use crate::stubs::shared::RtcEvent;
use crate::uid::Uid;

use core::fmt::Debug;
use std::collections::HashMap;
use std::hash::Hash;
use std::sync::Arc;
use std::time::{Duration, Instant};

use anyhow::Result;

use bytes::Bytes;
use serde::{Deserialize, Serialize};
use tokio::sync::{oneshot, Mutex};

use tonic::async_trait;
use webrtc::api::interceptor_registry::register_default_interceptors;
use webrtc::api::media_engine::MediaEngine;
use webrtc::api::APIBuilder;
use webrtc::data_channel::data_channel_init::RTCDataChannelInit;
use webrtc::data_channel::data_channel_message::DataChannelMessage;
use webrtc::ice_transport::ice_candidate::RTCIceCandidateInit;
use webrtc::ice_transport::ice_server::RTCIceServer;
use webrtc::interceptor::registry::Registry;
use webrtc::peer_connection::configuration::RTCConfiguration;
use webrtc::peer_connection::peer_connection_state::RTCPeerConnectionState;
use webrtc::peer_connection::sdp::session_description::RTCSessionDescription;
use webrtc::{
    data_channel::RTCDataChannel, ice_transport::ice_candidate::RTCIceCandidate,
    peer_connection::RTCPeerConnection,
};

use tracing::{error, info};

/// Max WebRTC data channel send size is 64 KiB
const DATA_CHANNEL_CHUNK_SIZE: usize = 1024;
const DATA_CHANNEL_LOW_WATER_MARK: usize = DATA_CHANNEL_CHUNK_SIZE * 512;
const DATA_CHANNEL_HIGH_WATER_MARK: usize = DATA_CHANNEL_CHUNK_SIZE * 1024;

/// Generic over client/worker states (impolite vs polite peers)
/// since they use different ids. Gets `impl`ed for the
/// state machine objects in the client and worker.
///
/// All we need is the `id()` method for access in the `AllConnections`
pub trait ConnectionState<T>: Clone {
    fn id(&self) -> T;
}

/// Set of all operations we can perform on `AllConnections`,
/// generic of the particular state machine we are using.
pub enum ConnectionAction<T, PeerConnectionState>
where
    PeerConnectionState: ConnectionState<T>,
{
    AddConnection(PeerConnectionState),
    RemoveConnection(T),
    GetConnection(T, oneshot::Sender<Option<PeerConnectionState>>),
    SetConnection(T, PeerConnectionState),
}

/// Represents an API for managing all client connections.
/// This includes adding, removing, and getting peer connections.
/// Very cheap to clone since just an mpsc::Sender under the hood.
///
/// Note: can potentially be replaced with a `DashMap` as
/// a concurrent hashmap.
#[derive(Clone)]
pub struct AllConnections<T, PeerConnectionState>
where
    PeerConnectionState: ConnectionState<T>,
{
    sender: kanal::AsyncSender<ConnectionAction<T, PeerConnectionState>>,
}

impl<T, PeerConnectionState> Default for AllConnections<T, PeerConnectionState>
where
    T: Hash + Clone + Send + Sync + Eq + 'static + Debug,
    PeerConnectionState: ConnectionState<T> + Send + Sync + 'static,
{
    /// Creates `AllConnections` as an actor - all operations are matched against
    /// inside an async task to get around using a global lock.
    fn default() -> Self {
        // All operations will be sent over `connection_sender`
        let (connection_sender, connection_receiver) =
            kanal::bounded_async::<ConnectionAction<T, PeerConnectionState>>(100);

        tokio::spawn(async move {
            let mut connections = HashMap::new();

            while let Ok(connection) = connection_receiver.recv().await {
                match connection {
                    ConnectionAction::AddConnection(connection) => {
                        info!("Adding connection: {:?}", connection.id());
                        connections.insert(connection.id().clone(), connection);

                        info!("Connections: {:?}", connections.keys().collect::<Vec<_>>());
                    }
                    ConnectionAction::RemoveConnection(id) => {
                        connections.remove(&id);
                    }
                    // `sender` used to return a value back to the caller
                    ConnectionAction::GetConnection(id, sender) => {
                        if let Some(peer_connection) = connections.get(&id) {
                            // Ignore inside the `Err` because it sends our value back
                            if sender.send(Some(peer_connection.clone())).is_err() {
                                info!("Error setting peer connection for id: {:?}", id);
                            }
                        } else {
                            let _ = sender.send(None);
                        }
                    }
                    ConnectionAction::SetConnection(id, connection) => {
                        connections.insert(id, connection);
                    }
                }
            }
        });

        Self {
            sender: connection_sender,
        }
    }
}

impl<T, PeerConnectionState> AllConnections<T, PeerConnectionState>
where
    T: Hash + Clone + Send + Sync + Eq + 'static + Debug,
    PeerConnectionState: ConnectionState<T> + Send + Sync + 'static,
{
    /// Adds a new connection to the `AllConnections`.
    /// `msg_sender` is needed for the ICE candidate handler
    /// to send `RtcMessage`s back to the central message handler
    /// and be relayed back to the appropriate client.
    pub async fn add_connection<M>(&self, connection: PeerConnectionState) -> Result<()>
    where
        M: RtcMessage + Send + Sync + 'static,
    {
        self.sender
            .send(ConnectionAction::AddConnection(connection))
            .await?;
        Ok(())
    }

    /// Removes a connection based on the `id`.
    pub async fn remove_connection(&self, id: T) -> Result<()> {
        self.sender
            .send(ConnectionAction::RemoveConnection(id))
            .await?;
        Ok(())
    }

    /// Gets a connection based on the `id`.
    pub async fn get_connection(&self, id: &T) -> Option<PeerConnectionState> {
        info!("Getting peer connection for id: {:?}", id);

        // Needed to receive the connection from the main actor.
        let (sender, receiver) = oneshot::channel();
        self.sender
            .send(ConnectionAction::GetConnection(id.clone(), sender))
            .await
            .ok()?;
        receiver.await.ok()?
    }

    /// Sets a connection based on the `id`.
    pub async fn set_connection(&self, id: &T, connection: PeerConnectionState) -> Result<()> {
        self.sender
            .send(ConnectionAction::SetConnection(id.clone(), connection))
            .await?;
        Ok(())
    }
}

/// Represents messages to be sent over the signaling channel.
pub trait RtcMessage {
    fn new(id: Uid, event: i32, message: Vec<u8>) -> Self;
}

/// An abstraction for communication with the remote peer with
/// the signaling server. The internal sender is used for PeerConnection
/// handlers to send messages to the negotiation task. The external
/// sender will send messages to the remote peer, and the external
/// receiver will receive messages from the remote peer.
///
/// Note: the external sender's messages do NOT reach the external receiver,
/// but rather a separate receiver that will yield to the signaling server.
pub struct SignalingChannel<Message>
where
    Message: RtcMessage + Send + Sync + Clone + 'static,
{
    internal_sender: kanal::AsyncSender<Message>,
    external_sender: kanal::AsyncSender<Message>,
    external_receiver: kanal::AsyncReceiver<Message>,
}

impl<Message> Clone for SignalingChannel<Message>
where
    Message: RtcMessage + Send + Sync + Clone + 'static,
{
    fn clone(&self) -> Self {
        Self {
            internal_sender: self.internal_sender.clone(),
            external_sender: self.external_sender.clone(),
            external_receiver: self.external_receiver.clone(),
        }
    }
}

impl<Message> SignalingChannel<Message>
where
    Message: RtcMessage + Send + Sync + Clone + 'static,
{
    pub fn new(
        internal_sender: kanal::AsyncSender<Message>,
        external_sender: kanal::AsyncSender<Message>,
        external_receiver: kanal::AsyncReceiver<Message>,
    ) -> Self {
        Self {
            internal_sender,
            external_sender,
            external_receiver,
        }
    }

    pub async fn internal_send(&self, message: Message) -> Result<()> {
        self.internal_sender.send(message).await?;
        Ok(())
    }

    pub async fn send(&self, message: Message) -> Result<()> {
        if self.external_sender.send(message).await.is_err() {
            error!("Could not send external message");
        };
        Ok(())
    }

    pub async fn recv(&mut self) -> Result<Message> {
        let message = self.external_receiver.recv().await?;
        Ok(message)
    }
}

#[async_trait]
pub trait Channel {
    async fn send(&self, data: Vec<u8>, rids: Option<Vec<Uid>>) -> Result<()>;
    async fn recv(&mut self) -> Result<Vec<u8>>;
}

#[derive(Serialize, Deserialize)]
pub struct DataChunk {
    data: Vec<u8>,
    is_last: bool,
}

impl From<DataChunk> for Bytes {
    fn from(data_chunk: DataChunk) -> Self {
        let mut data = data_chunk.data;
        data.insert(0, data_chunk.is_last.into());
        Bytes::from(data)
    }
}

impl From<Bytes> for DataChunk {
    fn from(data: Bytes) -> Self {
        let mut data = data.to_vec();
        let is_last = data.remove(0) != 0;

        DataChunk { data, is_last }
    }
}

/// Represents a data channel for sending and receiving data.
/// Offers a more idiomatic API than the underlying `RTCDataChannel`
/// object.
///
/// This implementation was chosen over the lower level
/// detach API for more control (may want to switch in the future
/// since it offers `AsyncRead` and `AsyncWrite` implementations).
///
/// Uses actor model for interacting with the `RTCDataChannel`.
/// When creating, the `DataChannel` is empty (i.e. cannot send or receive)
/// and an `RTCDataChannel` must be added via `add_data_channel`.
/// Can be cloned (semi) cheaply (at the cost of `resubscribe`s)
/// and will still refer to the same underlying `RTCDataChannel`.
///
/// Sends and receives data as `Vec<u8>` for simplicity.
pub struct DataChannel {
    /// Sends message from `RTCDataChannel` to be `recv`
    in_sender: kanal::AsyncSender<DataChannelMessage>,
    /// Receives messages from `RTCDataChannel` to be given to user
    in_receiver: kanal::AsyncReceiver<DataChannelMessage>,
    /// Sends message from user to `RTCDataChannel`
    out_sender: kanal::AsyncSender<DataChannelMessage>,
    /// Receives message from user to be sent to `RTCDataChannel`
    out_receiver: kanal::AsyncReceiver<DataChannelMessage>,
    /// Receives `buffered_amount_low` callback messages
    buffer_event_receiver: kanal::AsyncReceiver<()>,
    /// Interface with data channel through actions
    action_sender: kanal::AsyncSender<DataChannelAction>,
    /// Used to add the internal `RTCDataChannel`
    data_channel_sender: kanal::AsyncSender<Arc<RTCDataChannel>>,
}

enum DataChannelAction {
    GetBufferedAmount(oneshot::Sender<usize>),
}

impl Clone for DataChannel {
    fn clone(&self) -> Self {
        Self {
            in_sender: self.in_sender.clone(),
            in_receiver: self.in_receiver.clone(),
            out_sender: self.out_sender.clone(),
            out_receiver: self.out_receiver.clone(),
            buffer_event_receiver: self.buffer_event_receiver.clone(),
            action_sender: self.action_sender.clone(),
            data_channel_sender: self.data_channel_sender.clone(),
        }
    }
}

impl Default for DataChannel {
    /// Creates a new empty `DataChannel` and sets up listening channels.
    fn default() -> Self {
        // When `send` called, sends from `in_sender` to `in_receiver` which
        // will send to the `RTCDataChannel`
        let (in_sender, in_receiver) = kanal::bounded_async::<DataChannelMessage>(10000);

        // When a message is received from the `RTCDataChannel`, `out_sender`
        // sends it again, which is received by `out_receiver` and relayed on `recv`
        let (out_sender, out_receiver) = kanal::bounded_async::<DataChannelMessage>(10000);

        // When WebRTC `bufferedamountlow` events are triggered, send a message across this
        // channel.
        let (buffer_event_sender, buffer_event_receiver) = kanal::bounded_async::<()>(10000);

        // Interface with the data channel (e.g. getters/setters)
        let (action_sender, action_receiver) = kanal::bounded_async::<DataChannelAction>(10000);

        // When the user is ready to submit an `RTCDataChannel`, they will
        // send using `add_data_channel` which sends using `data_channel_sender`
        // to `data_channel_receiver` which sets handlers up (ONCE).
        let (data_channel_sender, data_channel_receiver) =
            kanal::bounded_async::<Arc<RTCDataChannel>>(1000);

        let in_sender_c = in_sender.clone();
        let out_receiver_c = out_receiver.clone();

        // Handles the `add_data_channel` method, where we will receive a single
        // `RTCDataChannel` that will serve for all future `send` and `recv`s
        tokio::spawn(async move {
            let in_sender = in_sender_c.clone();
            let out_receiver = out_receiver_c.clone();

            // Once an `RTCDataChannel` is created, set up handlers for relaying
            // messages FROM and TO the channel.
            if let Ok(data_channel) = data_channel_receiver.recv().await {
                data_channel
                    .set_buffered_amount_low_threshold(DATA_CHANNEL_LOW_WATER_MARK)
                    .await;
                info!(
                    "Data channel buffered amount set to: {:?}",
                    data_channel.buffered_amount_low_threshold().await
                );

                // FROM THE CHANNEL: When a message is received on the data channel, send it to our
                // `in_receiver` so external callers can receive it.
                let in_sender = in_sender.clone();
                data_channel.on_message(Box::new(move |msg| {
                    let in_sender = in_sender.clone();
                    Box::pin(async move {
                        in_sender
                            .send(msg)
                            .await
                            .expect("failed to send data channel message");
                    })
                }));

                // TO THE CHANNEL: When a message is received on the `out_receiver`,
                // send it to the data channel.
                let out_receiver = out_receiver.clone();
                let data_channel_c = data_channel.clone();
                tokio::spawn(async move {
                    let data_channel = data_channel_c.clone();
                    while let Ok(msg) = out_receiver.recv().await {
                        data_channel
                            .send(&msg.data)
                            .await
                            .expect("failed to send data channel message");
                    }
                });

                // BUFFERED AMOUNT EVENTS: When the amount of data being sent is queueing in
                // the data channel buffer, events will trigger when this amount dips below the
                // threshold.
                data_channel
                    .on_buffered_amount_low(Box::new(move || {
                        info!("received bufferedamountlow");
                        let buffer_event_sender = buffer_event_sender.clone();
                        Box::pin(async move {
                            buffer_event_sender
                                .send(())
                                .await
                                .expect("failed to send buffered amount event");
                        })
                    }))
                    .await;

                // ACTIONS
                tokio::spawn(async move {
                    while let Ok(action_message) = action_receiver.recv().await {
                        match action_message {
                            DataChannelAction::GetBufferedAmount(response_sender) => {
                                response_sender
                                    .send(data_channel.buffered_amount().await)
                                    .expect("Could not send buffered amount");
                            }
                        }
                    }
                });
            }
        });

        Self {
            in_sender,
            in_receiver,
            out_sender,
            out_receiver,
            buffer_event_receiver,
            action_sender,
            data_channel_sender,
        }
    }
}

impl DataChannel {
    /// Adds an `RTCDataChannel` that can now be communicated with
    /// using the `send` and `recv` API.
    pub async fn add_data_channel(&self, data_channel: Arc<RTCDataChannel>) -> Result<()> {
        self.data_channel_sender
            .send(data_channel)
            .await
            .map_err(|_| anyhow::anyhow!("failed to send data channel to data channel receiver"))?;
        Ok(())
    }

    fn create_message(data: &[u8], is_last: bool) -> DataChannelMessage {
        let data = DataChunk {
            data: data.to_vec(),
            is_last,
        };
        DataChannelMessage {
            is_string: false,
            data: Bytes::from(data),
        }
    }

    pub async fn buffered_amount(&self) -> Result<usize> {
        let (response_sender, response_receiver) = oneshot::channel();
        self.action_sender
            .send(DataChannelAction::GetBufferedAmount(response_sender))
            .await?;
        Ok(response_receiver.await?)
    }
}

#[async_trait]
impl Channel for DataChannel {
    /// Sends data over the data channel. Must chunk data to accommodate SCTP data size limits
    /// used in WebRTC under the hood.
    async fn send(&self, data: Vec<u8>, rids: Option<Vec<Uid>>) -> Result<()> {
        let instant = Instant::now();
        let mut errors = vec![];
        let mut sent_sizes = vec![];

        let mut chunks = data.chunks(DATA_CHANNEL_CHUNK_SIZE).peekable();

        while let Some(chunk) = chunks.next() {
            while self.buffered_amount().await? >= DATA_CHANNEL_HIGH_WATER_MARK {
                match self.buffer_event_receiver.recv().await {
                    Ok(()) => {}
                    Err(e) => error!("Error receiving buffer event: {e:?}"),
                }
            }

            let message = DataChannel::create_message(chunk, chunks.peek().is_none());
            match self.out_sender.send(message).await {
                Ok(size) => sent_sizes.push(size),
                Err(e) => errors.push(e),
            }
        }

        if !errors.is_empty() {
            error!(
                "Number of errors while sending message of size {}: {}",
                data.len(),
                errors.len()
            );
        }

        let duration = instant.elapsed();

        // TODO: see when things are being sent here. Should somehow be sent serially?
        info!(
            "Sent {} messages successfully in {duration:?} for rids: {rids:?}",
            sent_sizes.len()
        );

        Ok(())
    }

    /// Receives data from the data channel. Must reconstruct from chunk data: see
    /// `DataChannel::send`
    async fn recv(&mut self) -> Result<Vec<u8>> {
        let instant = Instant::now();
        let mut data = Vec::with_capacity(64_000);
        let mut num_chunks = 0;
        let mut durations = vec![];
        let mut last_chunk_time = Instant::now();
        while let Ok(message) = self.in_receiver.recv().await {
            let chunk_arrival_time = Instant::now();
            let _time_since_last = chunk_arrival_time.duration_since(last_chunk_time);
            let instant = Instant::now();
            let data_chunk: DataChunk = message.data.into();
            data.extend(data_chunk.data);
            num_chunks += 1;
            if data_chunk.is_last {
                break;
            }
            let duration = instant.elapsed();
            durations.push(duration);
            // info!("Chunk {num_chunks} arrived after {time_since_last:?}");
            last_chunk_time = chunk_arrival_time;
        }

        let duration = instant.elapsed();

        info!(
            "Recv {num_chunks} chunks for message of size: {} in {duration:?}",
            data.len()
        );

        let total_duration: Duration = durations.iter().sum();

        info!("Total duration: {total_duration:?}");

        Ok(data)
    }
}

/// Represents a peer connection with a remote peer.
#[derive(Clone)]
pub struct PeerConnection {
    pub rtc_connection: Arc<RTCPeerConnection>,
    pub data_channel: DataChannel,
    pub pending_candidates: Arc<Mutex<Vec<RTCIceCandidateInit>>>, // Local candidates that have not been sent to the remote peer yet
}

impl PeerConnection {
    /// Reasonable defaults come from the `webrtc` crate
    /// data channel examples. Data channel is not explicitly
    /// created here to be generic across the client and worker.
    pub async fn default() -> Result<Self> {
        let config = RTCConfiguration {
            ice_servers: vec![RTCIceServer {
                urls: vec!["stun:stun.l.google.com:19302".to_owned()],
                ..Default::default()
            }],
            ..Default::default()
        };

        let mut media_engine = MediaEngine::default();
        media_engine.register_default_codecs()?;
        let mut registry = Registry::new();
        registry = register_default_interceptors(registry, &mut media_engine)?;

        let api = APIBuilder::new()
            .with_media_engine(media_engine)
            .with_interceptor_registry(registry)
            .build();

        let rtc_connection = Arc::new(api.new_peer_connection(config).await?);

        let peer_connection = PeerConnection {
            rtc_connection,
            data_channel: DataChannel::default(),
            pending_candidates: Arc::new(Mutex::new(Vec::new())),
        };

        Ok(peer_connection)
    }

    /// Creates a data channel with open and message listeners.
    /// Must be created before creating an offer as part of WebRTC protocol.
    ///
    /// # Arguments
    /// * `peer_id` - The ID of the remote peer
    /// * `signaling_channel` - The signaling channel to send messages to the remote peer
    /// * `connection_status_sender` - A oneshot sender to send the result of the connection
    ///   attempt back to the caller; used to signal the data channel is open
    pub async fn create_data_channel<Message>(
        &mut self,
        peer_id: Uid,
        signaling_channel: SignalingChannel<Message>,
        connection_status_sender: oneshot::Sender<Result<()>>,
    ) -> Result<()>
    where
        Message: RtcMessage + Send + Sync + Clone + 'static,
    {
        let options = Some(RTCDataChannelInit {
            ordered: Some(true),
            max_retransmits: Some(0u16),
            ..Default::default()
        });

        let data_channel = self
            .rtc_connection
            .create_data_channel("data", options)
            .await?;

        data_channel.clone().on_open(Box::new(move || {
            info!("data channel opened");
            let message = Message::new(peer_id, RtcEvent::Connected as i32, vec![]);

            // Send the connection status back to the caller
            let _ = connection_status_sender.send(Ok(()));

            Box::pin(async move {
                // The signaling channel receiver handles the state transition to `Connected`
                signaling_channel
                    .internal_send(message)
                    .await
                    .expect("failed to send connected message");
            })
        }));

        // Need to add the `RTCDataChannel` here so that `send` and `recv` work.
        self.data_channel.add_data_channel(data_channel).await?;

        Ok(())
    }

    /// Creates an offer to send to the remote peer.
    pub async fn create_offer(&self) -> Result<RTCSessionDescription> {
        let offer = self.rtc_connection.create_offer(None).await?;
        self.rtc_connection
            .set_local_description(offer.clone())
            .await?;
        Ok(offer)
    }

    /// Starts a state change handler which can be used
    /// for fault tolerance and other state transitions.
    pub fn start_state_change_handler<Message>(
        &self,
        peer_id: Uid,
        signaling_channel: SignalingChannel<Message>,
    ) -> Result<()>
    where
        Message: RtcMessage + Send + Sync + Clone + 'static,
    {
        self.rtc_connection
            .on_peer_connection_state_change(Box::new(move |s: RTCPeerConnectionState| match s {
                RTCPeerConnectionState::Failed => {
                    let message = Message::new(peer_id.clone(), RtcEvent::Closed as i32, vec![]);
                    let signaling_channel = signaling_channel.clone();

                    Box::pin(async move {
                        info!("peer connection failed; sending closed message");
                        // The signaling channel receiver handles the state transition to `Closed`
                        signaling_channel
                            .internal_send(message)
                            .await
                            .expect("failed to send closed message");
                    })
                }

                // We do not handle the `Connected` state here; rather we handle it when the
                // data channel is opened
                _ => Box::pin(async {}),
            }));
        Ok(())
    }

    /// Starts an ICE candidate handler which will generate
    /// local ICE candidates that can be sent to the remote peer.
    pub async fn start_ice_candidate_handler<Message>(
        &self,
        peer_id: Uid,
        signaling_channel: SignalingChannel<Message>,
    ) -> Result<()>
    where
        Message: RtcMessage + Send + Sync + Clone + 'static,
    {
        self.rtc_connection
            .on_ice_candidate(Box::new(move |c: Option<RTCIceCandidate>| {
                let signaling_channel_c = signaling_channel.clone();
                if let Some(candidate) = c {
                    let candidate_payload = candidate
                        .to_json()
                        .expect("Candidate was not JSON parseable")
                        .candidate;

                    let message = Message::new(
                        peer_id.clone(),
                        RtcEvent::IceCandidate as i32,
                        candidate_payload.into(),
                    );

                    return Box::pin(async move {
                        // Relay ICE candidates to the remote peer
                        if let Err(e) = signaling_channel_c.internal_send(message).await {
                            error!("Failed to send internally: {e}");
                        }
                    });
                }
                Box::pin(async {})
            }));
        Ok(())
    }

    /// Starts a data channel handler which will replace the
    /// data channel when a new one is opened. Consumes
    /// self but this is okay since `PeerConnection`
    /// is cheap to clone.
    pub async fn start_data_channel_handler<Message>(
        self,
        peer_id: Uid,
        signaling_channel: SignalingChannel<Message>,
    ) where
        Message: RtcMessage + Send + Sync + Clone + 'static,
    {
        let self_data_channel = self.data_channel.clone();
        self.rtc_connection
            .on_data_channel(Box::new(move |d: Arc<RTCDataChannel>| {
                let data_channel = d.clone();

                let message = Message::new(peer_id.clone(), RtcEvent::Connected as i32, vec![]);
                let signaling_channel = signaling_channel.clone();

                let self_data_channel = self_data_channel.clone();
                Box::pin(async move {
                    self_data_channel
                        .add_data_channel(data_channel)
                        .await
                        .expect("failed to add data channel");
                    info!("data channel open; replaced data channel");

                    // The signaling channel receiver handles the state transition to `Connected`
                    signaling_channel
                        .clone()
                        .internal_send(message)
                        .await
                        .expect("failed to send connected message");
                })
            }));
    }
}

/// Used by the distributor to send messages through PubSub.
#[derive(Debug, Clone)]
pub enum Event {
    Offer,
    Answer,
    AcceptAnswer,
    RemoteIceCandidate,
    LocalIceCandidate,
    Blank,
}

impl From<&str> for Event {
    fn from(event: &str) -> Self {
        match event {
            "OFFER" => Event::Offer,
            "ANSWER" => Event::Answer,
            "ACCEPT_ANSWER" => Event::AcceptAnswer,
            "ICE_CANDIDATE" => Event::RemoteIceCandidate,
            "LOCAL_ICE_CANDIDATE" => Event::LocalIceCandidate,
            _ => Event::Blank,
        }
    }
}

impl From<Event> for String {
    fn from(event: Event) -> Self {
        match event {
            Event::Offer => "OFFER".into(),
            Event::Answer => "ANSWER".into(),
            Event::AcceptAnswer => "ACCEPT_ANSWER".into(),
            Event::RemoteIceCandidate => "ICE_CANDIDATE".into(),
            Event::LocalIceCandidate => "LOCAL_ICE_CANDIDATE".into(),
            Event::Blank => "".into(),
        }
    }
}

impl From<i32> for Event {
    fn from(event: i32) -> Self {
        match event {
            0 => Event::Offer,
            1 => Event::Answer,
            2 => Event::AcceptAnswer,
            3 => Event::RemoteIceCandidate,
            4 => Event::LocalIceCandidate,
            _ => Event::Blank,
        }
    }
}

impl From<Event> for i32 {
    fn from(event: Event) -> Self {
        match event {
            Event::Offer => 0,
            Event::Answer => 1,
            Event::AcceptAnswer => 2,
            Event::RemoteIceCandidate => 3,
            Event::LocalIceCandidate => 4,
            Event::Blank => 5,
        }
    }
}
