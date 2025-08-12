use super::stubs::worker_machine::WorkerMachine;

use crate::config::load_config;
use crate::connection::rtc::{PeerConnectionState, PolitePeerConnection};
use crate::endpoints::stubs::shared::{PeerRtcMessage, RtcEvent};
use crate::endpoints::stubs::worker_machine::worker_machine_service_client::WorkerMachineServiceClient;
use crate::endpoints::stubs::worker_machine::{
    CreateWorkerMachineRequest, GetWorkerMachineRequest, UpdateWorkerMachineRequest,
};
use crate::subcommands::init::{DeviceStatuses, Gpus, WorkerAdminId, WorkerMachineId};

use thava_types::biject::payload::{handle_bytes, ObjectCache};
use thava_types::client::ClientId;
use thava_types::rtc::AllConnections;
use thava_types::uid::Uid;
use thava_types::worker_machine::WorkerMachineStatus;

use anyhow::Result;
use thiserror::Error;

use tonic::service::interceptor::InterceptedService;
use tonic::service::Interceptor;
use tonic::transport::Channel;
use tonic::Request;

use futures::Stream;

use tracing::info;

#[derive(Error, Debug)]
pub enum WorkerMachineEndpointError {
    #[error("Failed to connect to the thava distributor.")]
    CreateWorkerMachineError,
}

pub struct WorkerMachineEndpoint<T>(pub WorkerMachineServiceClient<T>);

// Interceptor for every request to tell the distributor our id.
pub struct Authenticator {
    id: i64,
    admin_id: i64,
    auth_key: String,
}

impl Authenticator {
    pub fn from_config() -> Result<Self> {
        let config = load_config()?;
        Ok(Self {
            id: config.worker_machine.id.into(),
            admin_id: config.id.into(),
            auth_key: config.auth_key,
        })
    }
}

impl Interceptor for Authenticator {
    fn call(&mut self, mut request: Request<()>) -> Result<Request<()>, tonic::Status> {
        let metadata = request.metadata_mut();
        // info!("Bearer {:1} {:2}", self.id, self.auth_key);
        metadata.insert(
            "authentication",
            format!("Bearer {:1} {:2}", self.admin_id, self.auth_key)
                .parse()
                .unwrap(),
        );
        metadata.insert("machine_id", self.id.to_string().parse().unwrap());
        metadata.insert("admin_id", self.admin_id.to_string().parse().unwrap());

        Ok(request)
    }
}

impl WorkerMachineEndpoint<InterceptedService<Channel, Authenticator>> {
    /// Creates endpoint with authentication from the config file.
    pub async fn new_with_auth() -> Result<Self> {
        let channel = Channel::from_static("http://0.0.0.0:50051")
            .connect()
            .await?;

        let authenticator = Authenticator::from_config()?;

        let worker_machine_endpoint =
            WorkerMachineServiceClient::with_interceptor(channel, authenticator);
        Ok(Self(worker_machine_endpoint))
    }

    /// Sets up a continuous connection with the distributor over which all client connections will
    /// be negotiated.
    pub async fn negotiate_peer_connection(
        &mut self,
    ) -> Result<AllConnections<ClientId, PeerConnectionState>> {
        info!("Negotiating peer connection");
        let all_connections = AllConnections::default();
        let (d2w_sender, d2w_receiver) = kanal::bounded_async(100);

        info!("Worker machine sending request to distributor");

        let worker_to_distributor_stream = self
            .outbound_message_stream(all_connections.clone(), d2w_receiver)
            .await;

        let mut distributor_to_worker_stream = self
            .0
            .negotiate_peer_connection(Request::new(worker_to_distributor_stream))
            .await?
            .into_inner();

        info!("Worker machine got distributor response");

        while let Some(rtc_message) = distributor_to_worker_stream.message().await? {
            // info!("dist_to_worker: {:?}", rtc_message);
            d2w_sender.send(rtc_message).await?;
        }

        Ok(all_connections)
    }

    /// Creates an outbound RtcMessage stream to be sent to the distributor.
    /// Can be treated as a state machine that translates incoming RtcMessages
    /// into outbound RtcMessages according to the WebRTC protocol.
    ///
    /// # Arguments
    ///
    /// * `all_connections` - A reference to AllConnections
    ///   (approximation of cheap, cloneable concurrent HashMap)
    /// * `signaling_channel` - Signaling channel used to create every
    ///   PolitePeerConnection, also a communication method between `PeerConnectionState`s
    ///   and this outbound message stream.
    /// * `d2w_receiver` - Receiver for messages from the distributor
    /// * `w2d_receiver` - Receiver for messages from the signaling channel
    pub async fn outbound_message_stream(
        &self,
        all_connections: AllConnections<ClientId, PeerConnectionState>,
        d2w_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
    ) -> impl Stream<Item = PeerRtcMessage> {
        let all_connections_c = all_connections.clone();
        let (w2d_sender, w2d_receiver) = kanal::bounded_async(100);

        // Receive messages from the distributor, handle them, and send new messages
        // back to the distributor through the state machine.
        tokio::spawn(async move {
            let all_connections = all_connections_c;
            while let Ok(msg) = d2w_receiver.recv().await {
                let peer_id = ClientId::from(msg.peer_id);
                let event = msg.event();
                info!("received event: {:?}", event);

                // If the peer connection doesn't exist and the event is an offer,
                // create a new peer connection and add to AllConnections.
                if all_connections.get_connection(&peer_id).await.is_none()
                    && event == RtcEvent::Offer
                {
                    info!("creating new peer connection for peer_id: {:?}", peer_id);
                    PolitePeerConnection::negotiate(
                        msg,
                        peer_id.0.into(),
                        w2d_sender.clone(),
                        d2w_receiver.clone(),
                        all_connections.clone(),
                        handle_bytes as fn(&[u8], &mut ObjectCache) -> Result<Vec<u8>>,
                    )
                    .await?;
                }
            }

            Ok::<(), anyhow::Error>(())
        });

        // Stream of PeerRtcMessages to be sent to the distributor.
        // Receive messages from the signaling channel, handle them, and send new messages.
        async_stream::stream!({
            // Send a blank message to the distributor to signal that the worker machine is ready.
            let blank = PeerRtcMessage {
                peer_id: 0,
                event: 0,
                message: Vec::new(),
            };

            yield blank;

            // Receive from signaling channel, intercept messages in specific
            // states, and relay messages to the distributor.
            while let Ok(msg) = w2d_receiver.recv().await {
                yield msg;
            }
        })
    }

    /// Creates a new worker machine with the given parameters.
    pub async fn create_worker_machine(
        &mut self,
        gpus: Gpus,
        worker_admin_id: WorkerAdminId,
        status: WorkerMachineStatus,
        device_statuses: DeviceStatuses,
    ) -> Result<Uid> {
        let response = self
            .0
            .create_worker_machine(Request::new(CreateWorkerMachineRequest {
                gpus: gpus.into(),
                status: status.into(),
                device_statuses: device_statuses.into(),
                worker_admin_id: worker_admin_id.into(),
            }))
            .await?;

        Ok(response.into_inner().id.into())
    }

    /// Updates the worker machine with the given parameters.
    pub async fn update_worker_machine(
        &mut self,
        id: WorkerMachineId,
        gpus: Gpus,
        worker_admin_id: WorkerAdminId,
        status: WorkerMachineStatus,
        statuses: DeviceStatuses,
    ) -> Result<()> {
        self.0
            .update_worker_machine(Request::new(UpdateWorkerMachineRequest {
                worker_machine_id: id.into(),
                gpus: gpus.into(),
                worker_admin_id: worker_admin_id.into(),
                status: status.into(),
                device_statuses: statuses.into(),
            }))
            .await?;

        Ok(())
    }

    /// Gets the worker machine for the given worker machine id.
    pub async fn get_worker_machine(&mut self, id: WorkerMachineId) -> Result<WorkerMachine> {
        info!("Getting worker machine");
        let request = Request::new(GetWorkerMachineRequest { id: id.into() });
        let response = self.0.get_worker_machine(request).await?;

        let worker_machine = match response.into_inner().worker_machine {
            Some(worker_machine) => worker_machine,
            None => return Err(anyhow::anyhow!("Worker machine not found")),
        };

        Ok(worker_machine)
    }
}

impl WorkerMachineEndpoint<Channel> {
    /// Creates a new WorkerMachineClient by connecting to the distributor
    pub async fn new() -> Result<Self> {
        match WorkerMachineServiceClient::connect(
            //"https://distributor-image-bejxcjmudq-uw.a.run.app",
            "http://0.0.0.0:50051",
        )
        .await
        {
            Ok(client) => Ok(Self(client)),
            Err(_) => Err(WorkerMachineEndpointError::CreateWorkerMachineError.into()),
        }
    }
}
