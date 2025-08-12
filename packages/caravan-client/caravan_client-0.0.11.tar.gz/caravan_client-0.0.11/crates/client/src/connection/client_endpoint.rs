use super::rtc::{ImpolitePeerConnection, PeerConnectionState};
use super::tokio_runtime;

use crate::stubs::client::client_service_client::ClientServiceClient;
use crate::stubs::client::GpuPair;
use crate::stubs::client::{QueueClientRequest, VerifyClientRequest};
use crate::stubs::shared::PeerRtcMessage;

use anyhow::Result;
use futures::Stream;
use pyo3::types::PyDict;
use thava_types::biject::message::PyMessage;
use thava_types::rtc::AllConnections;
use thava_types::worker_admin::{Email, Group, Key};
use thava_types::worker_machine::WorkerMachineId;

use thava_types::client::ClientId;

use pyo3::ffi::c_str;
use pyo3::prelude::*;

use tokio::sync::oneshot;

use tonic::service::interceptor::InterceptedService;
use tonic::service::Interceptor;
use tonic::transport::Channel;
use tonic::Request;

use tracing::{info, warn};

/// Verifies group access for a given email, sharing key, and group.
pub fn verify(email: Email, sharing_key: Key, group: Group) -> Result<(), anyhow::Error> {
    let tokio = tokio_runtime::tokio();

    pyo3_print("Verifying group access...");
    info!("Verifying group access");

    tokio.block_on(async move {
        let mut client = match ClientEndpoint::new().await {
            Ok(client) => client,
            Err(_) => {
                info!("Failed to connect to client endpoint");
                return Err(anyhow::anyhow!("Failed to connect to distributor"));
            }
        };

        match client.verify_group_access(email, sharing_key, group).await {
            Ok(true) => {
                info!("Group access verified");
                Ok(())
            }
            Ok(false) | Err(_) => {
                info!("Failed to verify group access");
                Err(anyhow::anyhow!("Failed to verify group access"))
            }
        }
    })
}

type QueueResult = Result<(
    Vec<(kanal::AsyncSender<PyMessage>, i64)>,
    kanal::AsyncReceiver<Vec<u8>>,
)>;

/// Queues a client with the distributor and returns a list of senders and a receiver.
/// The senders correspond to the GPUs in the caravan and the receiver is used to
/// universally receive messages from all GPUs.
pub fn queue(email: Email, sharing_key: Key, gpu_count: i64) -> QueueResult {
    let tokio = tokio_runtime::tokio();

    // TODO: Only flushes after all the print statements for some reason.
    pyo3_print("Setting up a new caravan of GPU(s)...");

    let (client_id, gpus) = tokio.block_on(async move {
        let mut client = ClientEndpoint::new().await?;

        info!("Queueing client");
        let queue_result = client.queue_client(email, sharing_key, gpu_count).await?;

        Ok::<(ClientId, Vec<GpuPair>), anyhow::Error>(queue_result)
    })?;

    pyo3_print("Received a caravan of GPU(s)!");
    pyo3_print("Connecting to each GPU in your caravan...");

    info!("Client ID: {:?}", client_id);

    let mut client_endpoint = tokio.block_on(async move {
        match ClientEndpoint::new_with_id(client_id).await {
            Ok(client) => {
                info!("Starting client");
                Ok(client)
            }
            Err(e) => Err(e),
        }
    })?;

    // Pass messages from Python to the correct polite peer (GPU)
    // The `py_receiver`s are embedded in each `ImpolitePeerConnection<Connected>`
    let mut py_senders: Vec<kanal::AsyncSender<PyMessage>> = Vec::new();
    let mut py_receivers: Vec<kanal::AsyncReceiver<PyMessage>> = Vec::new();
    gpus.iter().for_each(|_| {
        let (py_sender, py_receiver) = kanal::bounded_async(100);
        py_senders.push(py_sender);
        py_receivers.push(py_receiver);
    });

    // Used to relay messages from the polite peers back to Python.
    // The `worker_msg_sender` is embedded in each `ImpolitePeerConnection`
    let (worker_msg_sender, worker_msg_receiver) = kanal::bounded_async(100);

    // Used to indicate when all connections have been established
    let (connection_status_sender, connection_status_receiver) = oneshot::channel::<Result<()>>();

    let gpus_c = gpus.clone();

    // Internally spawns multiple perpetual tasks for all GPU connections
    tokio.spawn(async move {
        match client_endpoint
            .negotiate_all_peer_connections(
                gpus_c,
                py_receivers,
                worker_msg_sender,
                connection_status_sender,
            )
            .await
        {
            Ok(all_connections) => Ok(all_connections),
            Err(e) => Err(e),
        }
    });

    info!("Awaiting connection status");

    // All connections have been established, now client can continue with PyTorch as normal
    let connection_status = tokio.block_on(connection_status_receiver)?;

    println!("Connected to each GPU in your caravan!");

    info!("Connection status: {:?}", connection_status);

    info!("Established all connections");

    // Return to the caller a list of all senders they can pass messages to for
    // communication with the polite peer along with the GPU offset.
    // GPU offset is needed in situations where the first "local" GPU is mapped
    // to the `n`th GPU on the polite peer.
    let mut return_py_senders: Vec<(kanal::AsyncSender<PyMessage>, i64)> = Vec::new();
    for (i, py_sender) in py_senders.iter().enumerate() {
        return_py_senders.push((py_sender.clone(), gpus[i].gpu_offset));
    }

    Ok((return_py_senders, worker_msg_receiver))
}

/// Tries to print in Python
/// WORKING BUT NOT FLUSHING EVERY TIME.
pub fn pyo3_print(message: &str) {
    match Python::with_gil(|py| {
        let locals = PyDict::new(py);
        locals.set_item("message", message)?;
        let command = c_str!("print(message)");
        py.run(command, None, Some(&locals))
    }) {
        Ok(()) => (),
        Err(e) => warn!("Error printing: {e}"),
    }
}

/// A client used to connect to the distributor and/or worker machines.
pub struct ClientEndpoint<T>(pub ClientServiceClient<T>);

/// Interceptor for every request to tell the distributor our id.
#[allow(dead_code)]
pub struct Authenticator {
    id: i64,
    group: String,
    email: String,
    sharing_key: String,
}

impl Authenticator {
    pub fn new(id: i64, group: String, email: String, sharing_key: String) -> Self {
        Self {
            id,
            group,
            email,
            sharing_key,
        }
    }
}

impl Interceptor for Authenticator {
    fn call(&mut self, mut request: Request<()>) -> Result<Request<()>, tonic::Status> {
        let metadata = request.metadata_mut();
        metadata.insert("id", self.id.to_string().parse().unwrap());

        Ok(request)
    }
}

impl ClientEndpoint<Channel> {
    /// Create a new client by connecting to the thava distributor.
    pub async fn new() -> Result<Self> {
        info!("Connecting to distributor");
        let channel = Channel::from_static("http://0.0.0.0:50051")
            .connect()
            .await?;

        let client = ClientServiceClient::new(channel);

        info!("Connected to distributor");

        Ok(Self(client))
    }

    /// Verifies that the given metadata corresponds to valid group access.
    pub async fn verify_group_access(
        &mut self,
        email: Email,
        sharing_key: Key,
        group: Group,
    ) -> Result<bool> {
        match self
            .0
            .verify_client(Request::new(VerifyClientRequest {
                email: email.into(),
                sharing_key: sharing_key.into(),
                group: group.into(),
            }))
            .await?
            .into_inner()
            .success
        {
            true => Ok(true),
            false => Err(anyhow::anyhow!("Failed to verify group access")),
        }
    }

    /// Queues this client and receives the workers assigned to this client after.
    pub async fn queue_client(
        &mut self,
        email: Email,
        sharing_key: Key,
        gpu_count: i64,
    ) -> Result<(ClientId, Vec<GpuPair>)> {
        let response = self
            .0
            .queue_client(Request::new(QueueClientRequest {
                email: email.into(),
                sharing_key: sharing_key.into(),
                gpu_count,
            }))
            .await?
            .into_inner();

        let client_id = response.client_id.into();
        let workers = response.workers;

        Ok((client_id, workers))
    }
}

impl ClientEndpoint<InterceptedService<Channel, Authenticator>> {
    /// Create a new client by connecting to the thava distributor.
    pub async fn new_with_id(client_id: ClientId) -> Result<Self> {
        // http:://[::1]:50051

        info!("Connecting to distributor");
        let channel = Channel::from_static("http://0.0.0.0:50051")
            // let channel = Channel::from_static("tcp://4.tcp.us-cal-1.ngrok.io:18543")
            .connect()
            .await?;

        // Temporary for testing deployment
        // let client =
        //     ClientServiceClient::connect("https://distributor-image-bejxcjmudq-uw.a.run.app")
        //         .await?;

        // TODO: need to replace the group/email/sharing_key so that we validate all future
        // distributor requests as well?
        let authenticator = Authenticator::new(
            client_id.into(),
            "group".to_string(),
            "email".to_string(),
            "sharing_key".to_string(),
        );

        let client_endpoint = ClientServiceClient::with_interceptor(channel, authenticator);

        info!("Connected to distributor");

        Ok(Self(client_endpoint))
    }

    /// Negotiate all peer connections with the distributor. Spawns perpetual tasks
    /// for all connections.
    pub async fn negotiate_all_peer_connections(
        &mut self,
        gpu_pairs: Vec<GpuPair>,
        py_receivers: Vec<kanal::AsyncReceiver<PyMessage>>,
        worker_msg_sender: kanal::AsyncSender<Vec<u8>>,
        connection_status_sender: oneshot::Sender<Result<()>>,
    ) -> Result<AllConnections<WorkerMachineId, PeerConnectionState>> {
        let all_connections = AllConnections::default();
        let (d2c_sender, d2c_receiver) = kanal::bounded_async(100);

        let client_to_distributor_stream = ClientEndpoint::outbound_message_stream(
            gpu_pairs,
            all_connections.clone(),
            d2c_receiver,
            py_receivers,
            connection_status_sender,
            worker_msg_sender,
        )
        .await;

        // let client_to_distributor_stream = async_stream::stream! {};

        let mut distributor_to_client_stream = self
            .0
            .negotiate_peer_connection(Request::new(client_to_distributor_stream))
            .await?
            .into_inner();

        while let Some(rtc_message) = distributor_to_client_stream.message().await? {
            d2c_sender.send(rtc_message).await?;
        }

        Ok(all_connections)
    }

    /// Handles all incoming RTC messages and sends return RTC messages
    /// through the stream.
    ///
    /// * `gpu_pairs` - All allocated `GPUPair`s for this client.
    /// * `all_connections` - `AllConnections` object for mapping worker ids to `PeerConnection`s via
    ///   the `PeerConnectionState`.
    /// * `signaling_channel`: A communication method between `PeerConnectionState`s and this
    ///   outbound message stream.
    /// * `c2d_receiver` - The receiver for the signaling channel to handle messages from the
    ///   `PeerConnectionState`.
    /// * `py_receivers` - A list of receivers listening for messages from Python to send to the
    ///   correct peer connection.
    /// * `worker_msg_sender` - Relay messages from the worker machines to Python.
    pub async fn outbound_message_stream(
        gpu_pairs: Vec<GpuPair>,
        all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
        d2c_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        py_receivers: Vec<kanal::AsyncReceiver<PyMessage>>,
        connection_status_sender: oneshot::Sender<Result<()>>,
        worker_msg_sender: kanal::AsyncSender<Vec<u8>>,
    ) -> impl Stream<Item = PeerRtcMessage> + 'static {
        let (c2d_sender, c2d_receiver) = kanal::bounded_async(100);
        let mut all_connection_status_receivers = Vec::new();

        // Create a peer connection for each GPU
        for (i, gpu_pair) in gpu_pairs.iter().enumerate() {
            let (worker_connection_status_sender, worker_connection_status_receiver) =
                oneshot::channel::<Result<()>>();
            all_connection_status_receivers.push(worker_connection_status_receiver);

            // Manages the full negotiation process, just needs the signaling server to be running.
            ImpolitePeerConnection::negotiate(
                gpu_pair.worker_machine_id.into(),
                c2d_sender.clone(),
                d2c_receiver.clone(),
                all_connections.clone(),
                worker_connection_status_sender,
                py_receivers[i].clone(),
                worker_msg_sender.clone(),
            )
            .await
            .expect("Failed to create impolite peer connection");
        }

        // Once all connections are established, sends connection status as connected
        // back to the client (this blocks the interpreter until all are connected).
        tokio::spawn(async move {
            for worker_connection_status_receiver in all_connection_status_receivers {
                let _ = worker_connection_status_receiver
                    .await
                    .expect("failed to receive connection status");
            }

            connection_status_sender
                .send(Ok(()))
                .expect("failed to send connection status");
        });

        // The return stream to the distributor is fully dependent on the state machine and the
        // messages that the signaling channel sends.
        async_stream::stream!({
            while let Ok(message) = c2d_receiver.recv().await {
                yield message;
            }
        })
    }
}
