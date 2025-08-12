use crate::stubs::shared::{PeerRtcMessage, RtcEvent};

use thava_types::{
    biject::message::PyMessage,
    rtc::{AllConnections, Channel, ConnectionState, PeerConnection, RtcMessage, SignalingChannel},
    uid::Uid,
    worker_machine::WorkerMachineId,
};

use anyhow::Result;
use tokio::sync::oneshot;
use tracing::info;

use core::fmt;
use std::marker::PhantomData;

use webrtc::{
    ice_transport::ice_candidate::{RTCIceCandidate, RTCIceCandidateInit},
    peer_connection::sdp::session_description::RTCSessionDescription,
};

/// Needed for `SignalingChannel` to send `PeerRtcMessage`
impl RtcMessage for PeerRtcMessage {
    fn new(id: Uid, event: i32, message: Vec<u8>) -> Self {
        Self {
            peer_id: id.into(),
            event,
            message,
        }
    }
}

/// Creates a new `PeerConnection` for a client,
/// adds a data channel (must be done first as the impolite peer),
/// and adds handlers to check states and handle local ICE candidates.
///
/// # Arguments
///
/// * `peer_id` - The id of the peer to connect to
/// * `signaling_channel` - The signaling channel to send and receive messages
/// * `connection_status_sender` - The sender to notify when the connection is established
pub async fn client_peer_connection(
    peer_id: &Uid,
    signaling_channel: &SignalingChannel<PeerRtcMessage>,
    connection_status_sender: oneshot::Sender<Result<()>>,
) -> Result<PeerConnection> {
    let mut peer_connection = PeerConnection::default().await?;
    peer_connection
        .create_data_channel(
            peer_id.clone(),
            signaling_channel.clone(),
            connection_status_sender,
        )
        .await?;
    peer_connection.start_state_change_handler(peer_id.clone(), signaling_channel.clone())?;
    peer_connection
        .start_ice_candidate_handler::<PeerRtcMessage>(peer_id.clone(), signaling_channel.clone())
        .await?;
    Ok(peer_connection)
}

/// Wrapper around the impolite state machine for ergonomic
/// matching for state transitions.
#[derive(Clone)]
pub enum PeerConnectionState {
    Offering(ImpolitePeerConnection<Offering>),
    Answered(ImpolitePeerConnection<Answered>),
    Connected(ImpolitePeerConnection<Connected>),
    Closed(ImpolitePeerConnection<Closed>),
}

/// Needed to store `PeerConnectionState` in `AllConnections`.
impl ConnectionState<WorkerMachineId> for PeerConnectionState {
    fn id(&self) -> WorkerMachineId {
        match self {
            PeerConnectionState::Offering(peer) => peer.peer_id.clone(),
            PeerConnectionState::Answered(peer) => peer.peer_id.clone(),
            PeerConnectionState::Connected(peer) => peer.peer_id.clone(),
            PeerConnectionState::Closed(peer) => peer.peer_id.clone(),
        }
    }
}

impl fmt::Debug for PeerConnectionState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PeerConnectionState::Offering(_) => write!(f, "Offering"),
            PeerConnectionState::Answered(_) => write!(f, "Answered"),
            PeerConnectionState::Connected(_) => write!(f, "Connected"),
            PeerConnectionState::Closed(_) => write!(f, "Closed"),
        }
    }
}

// Supported states for the impolite peer connection state machine.
#[derive(Clone)]
pub struct Offering;
#[derive(Clone)]
pub struct Answered;
#[derive(Clone)]
pub struct Connected;
#[derive(Clone)]
pub struct Closed;

/// The impolite peer connection state machine. Motivated by compile-time
/// guarantees and ergonomic state transitions.
///
/// * `peer_id` - id of the worker that we try to connect with
/// * `inner` - the actual `PeerConnection` itself
/// * `signaling_channel` - Channel with distributor to send and receive RTC messages
/// * `py_receiver` - `recv`s `PyMessage`s from Python, which should be relayed to the
///   polite peer through the `PeerConnection`
/// * `polite_msg_sender` - relays messages from polite peer to the impolite peer (who
///   we expect to be listening on the corresponding receiver)
#[derive(Clone)]
pub struct ImpolitePeerConnection<State> {
    peer_id: WorkerMachineId,
    inner: PeerConnection,
    signaling_channel: SignalingChannel<PeerRtcMessage>,
    py_receiver: kanal::AsyncReceiver<PyMessage>,
    polite_msg_sender: kanal::AsyncSender<Vec<u8>>,
    all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
    _state: PhantomData<fn() -> State>,
}

impl ImpolitePeerConnection<Offering> {
    /// Starts a new peer connection with the given peer id. Creates
    /// offer and sends it to the peer.
    pub async fn negotiate(
        peer_id: WorkerMachineId,
        external_sender: kanal::AsyncSender<PeerRtcMessage>,
        external_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
        connection_status_sender: oneshot::Sender<Result<()>>,
        py_receiver: kanal::AsyncReceiver<PyMessage>,
        polite_msg_sender: kanal::AsyncSender<Vec<u8>>,
    ) -> Result<()> {
        info!("Negotiating peer connection with peer_id: {:?}", peer_id);

        let (internal_sender, internal_receiver) = kanal::bounded_async(100);
        let signaling_channel =
            SignalingChannel::new(internal_sender, external_sender, external_receiver);

        let inner =
            client_peer_connection(&peer_id.0, &signaling_channel, connection_status_sender)
                .await?;
        let offer = inner.create_offer().await?;
        let offer_payload = serde_json::to_string(&offer)?;

        let message = PeerRtcMessage::new(
            peer_id.0.clone(),
            RtcEvent::Offer as i32,
            offer_payload.into(),
        );
        signaling_channel.internal_send(message).await?;

        let state = ImpolitePeerConnection {
            peer_id: peer_id.clone(),
            inner,
            signaling_channel: signaling_channel.clone(),
            py_receiver,
            polite_msg_sender,
            all_connections: all_connections.clone(),
            _state: PhantomData,
        };

        ImpolitePeerConnection::_negotiate(
            peer_id,
            state,
            signaling_channel,
            internal_receiver,
            all_connections,
        )
        .await?;

        Ok(())
    }

    async fn _negotiate(
        peer_id: WorkerMachineId,
        state: ImpolitePeerConnection<Offering>,
        signaling_channel: SignalingChannel<PeerRtcMessage>,
        internal_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
    ) -> Result<()> {
        let state = PeerConnectionState::Offering(state);

        all_connections
            .add_connection::<PeerRtcMessage>(state)
            .await?;

        let all_connections_c = all_connections.clone();
        let signaling_channel_c = signaling_channel.clone();
        let peer_id_c = peer_id.clone();

        tokio::spawn(async move {
            let mut signaling_channel = signaling_channel_c.clone();
            let peer_id = peer_id_c.clone();

            while let Ok(msg) = signaling_channel.recv().await {
                let all_connections = all_connections_c.clone();
                let worker_machine_id: WorkerMachineId = msg.peer_id.into();
                if worker_machine_id != peer_id {
                    continue;
                }

                let state = all_connections
                    .clone()
                    .get_connection(&worker_machine_id)
                    .await;

                if state.is_none() {
                    return Err(anyhow::anyhow!(
                        "State did not exist before receiving peer connection messages \
                        from worker_machine_id {worker_machine_id}."
                    ));
                }

                let state = state.unwrap();

                ImpolitePeerConnection::transition_external(msg, &peer_id, state, all_connections)
                    .await?;
            }

            Ok::<(), anyhow::Error>(())
        });

        let all_connections_c = all_connections.clone();
        let signaling_channel_c = signaling_channel.clone();
        let peer_id_c = peer_id.clone();
        tokio::spawn(async move {
            // Continuously handles messages coming from the signaling channel for state
            // transitions. This part is handled separately for transitions again because we might
            // receive messages from handlers as well, who are not authorized to make transitions
            // themselves (we need a mutable reference to the state).
            while let Ok(msg) = internal_receiver.recv().await {
                let all_connections = all_connections_c.clone();
                let signaling_channel = signaling_channel_c.clone();
                let peer_id = peer_id_c.clone();
                let worker_machine_id: WorkerMachineId = msg.peer_id.into();

                // This should never trigger since the internal sender/receiver are specific
                // to each peer connection state.
                if worker_machine_id != peer_id {
                    continue;
                }

                let state = all_connections.get_connection(&worker_machine_id).await;

                if state.is_none() {
                    return Err(anyhow::anyhow!(
                        "State did not exist before receiving peer connection messages \
                        from worker_machine_id {worker_machine_id}."
                    ));
                }

                let state = state.unwrap();

                ImpolitePeerConnection::transition_internal(
                    msg,
                    &peer_id,
                    state,
                    all_connections,
                    signaling_channel,
                )
                .await?;
            }

            Ok::<(), anyhow::Error>(())
        });

        Ok(())
    }

    /// State transitions according to messages received from the polite peer.
    async fn transition_external(
        msg: PeerRtcMessage,
        peer_id: &WorkerMachineId,
        state: PeerConnectionState,
        all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
    ) -> Result<()> {
        let event = msg.event();
        info!("Received external event: {:?}", event);

        // Exhaustively match against all possible state transitions. We use our current
        // state and the event that we've just received and only allow method calls that
        // are defined for those states. We will typically pass messages using the
        // signaling channel within these transitions that will be sent back to the
        // distributor.
        match (&state, event) {
            (PeerConnectionState::Offering(current_state), RtcEvent::Answer) => {
                let answer_payload = String::from_utf8(msg.message.clone())?;
                let new_state = current_state.clone().to_answered(answer_payload).await?;

                all_connections
                    .set_connection(&peer_id, PeerConnectionState::Answered(new_state))
                    .await?;
            }
            // These are ICE candidates from the worker, so we can directly receive them.
            (PeerConnectionState::Answered(current_state), RtcEvent::IceCandidate) => {
                let ice_candidate_payload = String::from_utf8(msg.message.clone())?;

                current_state
                    .recv_ice_candidate(ice_candidate_payload)
                    .await?;
            }
            (PeerConnectionState::Connected(current_state), RtcEvent::IceCandidate) => {
                let ice_candidate_payload = String::from_utf8(msg.message.clone())?;

                current_state
                    .recv_ice_candidate(ice_candidate_payload)
                    .await?;
            }
            _ => {
                info!(
                    "Unhandled event and state combination: {:?} {:?}",
                    event, state
                );
            }
        }

        Ok(())
    }

    /// State transitions according to messages internally passed - e.g. IceCandidates
    /// that the impolite peer is generating itself. These may not necessarily always transition,
    /// in which case we catch and consume the event.
    async fn transition_internal(
        msg: PeerRtcMessage,
        peer_id: &WorkerMachineId,
        state: PeerConnectionState,
        all_connections: AllConnections<WorkerMachineId, PeerConnectionState>,
        signaling_channel: SignalingChannel<PeerRtcMessage>,
    ) -> Result<()> {
        let event = msg.event();
        info!("Received internal event: {event:?}");
        match (state, event) {
            // Received from ICE candidate handler before our answer, simply store.
            (PeerConnectionState::Offering(current_state), RtcEvent::IceCandidate) => {
                current_state
                    .add_pending_candidate(msg.message.clone())
                    .await?;
            }
            (PeerConnectionState::Offering(current_state), RtcEvent::Closed) => {
                let new_state = current_state.clone().to_closed().await?;
                let state = PeerConnectionState::Closed(new_state);

                all_connections.set_connection(&peer_id, state).await?;
            }
            (PeerConnectionState::Answered(current_state), RtcEvent::Connected) => {
                let new_state = current_state.clone().to_connected().await;
                let state = PeerConnectionState::Connected(new_state);

                all_connections.set_connection(&peer_id, state).await?;
            }
            (PeerConnectionState::Answered(current_state), RtcEvent::Closed) => {
                let new_state = current_state.clone().to_closed().await?;
                let state = PeerConnectionState::Closed(new_state);

                all_connections.set_connection(&peer_id, state).await?;
            }
            (PeerConnectionState::Connected(current_state), RtcEvent::Closed) => {
                let new_state = current_state.clone().to_closed().await?;
                let state = PeerConnectionState::Closed(new_state);

                all_connections.set_connection(&peer_id, state).await?;
            }

            // Messages yielded here include ICE candidates in the Answered or Connected
            // states.
            // TODO: define the states and raise an error if we are sending anything else
            // to follow opt-in yields rather than catch-all yield.
            _ => {
                info!("Sending out internal event: {event:?}");
                signaling_channel.send(msg).await?;
            }
        }
        Ok(())
    }

    /// Stores local ICE candidates until in the `Answered` state.
    pub async fn add_pending_candidate(&self, candidate_payload: Vec<u8>) -> Result<()> {
        info!("Adding pending candidate");
        let candidate_payload: String = String::from_utf8(candidate_payload)?;
        let candidate: RTCIceCandidateInit = RTCIceCandidateInit {
            candidate: candidate_payload,
            ..Default::default()
        };
        self.inner.pending_candidates.lock().await.push(candidate);
        Ok(())
    }

    /// Receives an answer from the peer and transitions to the `Answered` state.
    /// Sends all pending ICE candidates.
    pub async fn to_answered(
        self,
        answer_payload: String,
    ) -> Result<ImpolitePeerConnection<Answered>> {
        info!("offering to answered");
        let answer: RTCSessionDescription = serde_json::from_str(&answer_payload)?;
        self.inner
            .rtc_connection
            .set_remote_description(answer)
            .await?;

        let answered: ImpolitePeerConnection<Answered> = ImpolitePeerConnection {
            peer_id: self.peer_id,
            inner: self.inner,
            signaling_channel: self.signaling_channel,
            py_receiver: self.py_receiver,
            polite_msg_sender: self.polite_msg_sender,
            all_connections: self.all_connections,
            _state: PhantomData,
        };

        info!("answered; sending all pending candidates");

        answered.send_all_pending_candidates().await?;

        Ok(answered)
    }

    pub async fn close<T>(
        state: ImpolitePeerConnection<T>,
    ) -> Result<ImpolitePeerConnection<Closed>> {
        state.inner.rtc_connection.close().await?;
        state
            .all_connections
            .remove_connection(state.peer_id.clone())
            .await?;
        Ok(ImpolitePeerConnection {
            peer_id: state.peer_id,
            inner: state.inner,
            signaling_channel: state.signaling_channel,
            py_receiver: state.py_receiver,
            polite_msg_sender: state.polite_msg_sender,
            all_connections: state.all_connections,
            _state: PhantomData,
        })
    }

    /// Closes the connection and transitions to the `Closed` state.
    pub async fn to_closed(self) -> Result<ImpolitePeerConnection<Closed>> {
        info!("offering to closed");
        ImpolitePeerConnection::close(self).await
    }
}

impl ImpolitePeerConnection<Answered> {
    /// Sends all pending ICE candidates.
    pub async fn send_all_pending_candidates(&self) -> Result<()> {
        info!("Sending all pending candidates");
        let mut pending_candidates = self.inner.pending_candidates.lock().await;
        for candidate in pending_candidates.iter() {
            self.send_ice_candidate_str(&candidate.candidate).await?;
        }
        pending_candidates.clear();
        Ok(())
    }

    /// Sends an ICE candidate that is already in string format.
    pub async fn send_ice_candidate_str(&self, candidate_payload: &str) -> Result<()> {
        info!("Sending ice candidate");
        let message = PeerRtcMessage::new(
            self.peer_id.0.clone(),
            RtcEvent::IceCandidate as i32,
            candidate_payload.into(),
        );
        self.signaling_channel.internal_send(message).await?;
        Ok(())
    }

    /// Sends an ICE candidate.
    pub async fn send_ice_candidate(&self, candidate: RTCIceCandidate) -> Result<()> {
        info!("Sending ice candidate");
        let candidate_payload = candidate.to_json()?.candidate;
        let message = PeerRtcMessage::new(
            self.peer_id.0.clone(),
            RtcEvent::IceCandidate as i32,
            candidate_payload.into(),
        );
        self.signaling_channel.internal_send(message).await?;
        Ok(())
    }

    /// Receives an ICE candidate and adds it to the peer connection.
    pub async fn recv_ice_candidate(&self, candidate_payload: String) -> Result<()> {
        info!("Receiving ice candidate");
        let candidate: RTCIceCandidateInit = RTCIceCandidateInit {
            candidate: candidate_payload,
            ..Default::default()
        };
        self.inner
            .rtc_connection
            .add_ice_candidate(candidate)
            .await?;
        Ok(())
    }

    /// Transitions to the `Connected` state.
    pub async fn to_connected(self) -> ImpolitePeerConnection<Connected> {
        info!("answered to connected");

        let py_receiver = self.py_receiver.clone();
        let polite_msg_sender = self.polite_msg_sender.clone();

        // Relayer async task: all messages from Python are received
        // on the `py_receiver` and sent to the peer through the `DataChannel`.
        // The very next message from the `DataChannel` is then sent to the
        // impolite peer using the `polite_msg_sender`
        let data_channel = self.inner.data_channel.clone();
        tokio::spawn(async move {
            info!("Waiting for message");
            let mut data_channel = data_channel.clone();
            while let Ok(msg) = py_receiver.recv().await {
                info!("data channel now starting to send for rids: {:?}", msg.rids);
                data_channel
                    .send(msg.payload, Some(msg.rids.clone()))
                    .await
                    .expect("Failed to relay message to polite peer.");

                // If rids is empty, it's a blocking call, so we are receiving a result from the
                // remote worker.
                if msg.rids.is_empty() {
                    let polite_response = data_channel.recv().await.unwrap();
                    info!("Response from polite peer: {:?}", polite_response.len());
                    polite_msg_sender
                        .send(polite_response.to_vec())
                        .await
                        .expect("Failed to relay message to python.");
                }
            }
        });

        ImpolitePeerConnection {
            peer_id: self.peer_id,
            inner: self.inner.clone(),
            signaling_channel: self.signaling_channel,
            py_receiver: self.py_receiver,
            polite_msg_sender: self.polite_msg_sender,
            all_connections: self.all_connections,
            _state: PhantomData,
        }
    }

    /// Closes the connection and transitions to the `Closed` state.
    pub async fn to_closed(self) -> Result<ImpolitePeerConnection<Closed>> {
        info!("answered to closed");
        ImpolitePeerConnection::close(self).await
    }
}

impl ImpolitePeerConnection<Connected> {
    /// Sends data to the peer.
    pub async fn send_data(&self, data: Vec<u8>) -> Result<()> {
        self.inner.data_channel.send(data, None).await?;
        Ok(())
    }

    /// Receives data from the peer.
    pub async fn recv_data(&mut self) -> Result<Vec<u8>> {
        self.inner.data_channel.recv().await
    }

    /// Sends an ICE candidate.
    pub async fn send_ice_candidate(&self, candidate: RTCIceCandidate) -> Result<()> {
        let candidate_payload = serde_json::to_string(&candidate)?;
        let message = PeerRtcMessage::new(
            self.peer_id.0.clone(),
            RtcEvent::IceCandidate as i32,
            candidate_payload.into(),
        );
        self.signaling_channel.internal_send(message).await?;
        Ok(())
    }

    /// Receives an ICE candidate and adds it to the peer connection.
    pub async fn recv_ice_candidate(&self, candidate_payload: String) -> Result<()> {
        let candidate: RTCIceCandidateInit = RTCIceCandidateInit {
            candidate: candidate_payload,
            ..Default::default()
        };
        self.inner
            .rtc_connection
            .add_ice_candidate(candidate)
            .await?;
        Ok(())
    }

    /// Closes the connection and transitions to the `Closed` state.
    pub async fn to_closed(self) -> Result<ImpolitePeerConnection<Closed>> {
        info!("connected to closed");
        ImpolitePeerConnection::close(self).await
    }
}

impl ImpolitePeerConnection<Closed> {
    /// Changes nothing; included for idempotency.
    pub async fn to_closed(self) -> Result<ImpolitePeerConnection<Closed>> {
        info!("closed to closed");
        ImpolitePeerConnection::close(self).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use thava_types::biject::payload::{handle_bytes, ObjectCache};
    use worker::connection::rtc::PolitePeerConnection;
    use worker::endpoints::stubs::shared;

    use std::time::{Duration, Instant};
    use tokio::time::timeout;
    use tracing::error;

    struct SignalingServer {
        impolite_sender: kanal::AsyncSender<PeerRtcMessage>,
        impolite_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        polite_sender: kanal::AsyncSender<shared::PeerRtcMessage>,
        polite_receiver: kanal::AsyncReceiver<shared::PeerRtcMessage>,
    }

    fn log() -> tracing::subscriber::DefaultGuard {
        let subscriber = tracing_subscriber::fmt()
            .compact()
            .with_file(true)
            .with_line_number(true)
            .with_target(false)
            .finish();

        tracing::subscriber::set_default(subscriber)
    }

    async fn signaling_server() -> Result<SignalingServer> {
        let (impolite_sender, impolite_receiver) = kanal::bounded_async::<PeerRtcMessage>(100);
        let (polite_sender, polite_receiver) = kanal::bounded_async::<shared::PeerRtcMessage>(100);

        let (im_to_pol_sender, im_to_pol_receiver) =
            kanal::bounded_async::<shared::PeerRtcMessage>(100);
        let (pol_to_im_sender, pol_to_im_receiver) = kanal::bounded_async::<PeerRtcMessage>(100);

        // Relays from impolite to polite
        tokio::spawn(async move {
            while let Ok(msg) = impolite_receiver.recv().await {
                let msg: shared::PeerRtcMessage = shared::PeerRtcMessage {
                    peer_id: msg.peer_id.into(),
                    event: msg.event.into(),
                    message: msg.message,
                };
                im_to_pol_sender.send(msg).await.unwrap();
            }
        });

        // Relays from polite to impolite
        tokio::spawn(async move {
            while let Ok(msg) = polite_receiver.recv().await {
                let msg: PeerRtcMessage = PeerRtcMessage {
                    peer_id: msg.peer_id.into(),
                    event: msg.event.into(),
                    message: msg.message,
                };
                pol_to_im_sender.send(msg).await.unwrap();
            }
        });

        Ok(SignalingServer {
            impolite_sender,
            impolite_receiver: pol_to_im_receiver,
            polite_sender,
            polite_receiver: im_to_pol_receiver,
        })
    }

    #[tokio::test]
    async fn test_negotiation() -> Result<()> {
        let _default_guard = log();
        let signaling_server = signaling_server().await?;

        let (connection_status_sender, connection_status_receiver) = oneshot::channel();
        let (_py_sender, py_receiver) = kanal::bounded_async(100);
        let (polite_msg_sender, _polite_msg_receiver) = kanal::bounded_async(100);

        let impolite_all_connections = AllConnections::default();
        let polite_all_connections = AllConnections::default();

        tokio::spawn(async move {
            while let Ok(msg) = signaling_server.polite_receiver.recv().await {
                let peer_id = msg.peer_id.into();
                let event = msg.event();
                info!("received event: {:?}", event);

                // If the peer connection doesn't exist and the event is an offer,
                // create a new peer connection and add to AllConnections.
                if polite_all_connections
                    .get_connection(&peer_id)
                    .await
                    .is_none()
                    && event == shared::RtcEvent::Offer
                {
                    info!("creating new peer connection for peer_id: {:?}", peer_id);
                    PolitePeerConnection::negotiate(
                        msg,
                        peer_id,
                        signaling_server.polite_sender.clone(),
                        signaling_server.polite_receiver.clone(),
                        polite_all_connections.clone(),
                        handle_bytes as fn(&[u8], &mut ObjectCache) -> Result<Vec<u8>>,
                    )
                    .await?;
                }
            }

            Ok::<(), anyhow::Error>(())
        });

        ImpolitePeerConnection::negotiate(
            0.into(),
            signaling_server.impolite_sender,
            signaling_server.impolite_receiver,
            impolite_all_connections,
            connection_status_sender,
            py_receiver,
            polite_msg_sender,
        )
        .await?;

        if let Err(_) = timeout(Duration::from_secs(5), connection_status_receiver).await {
            panic!("Could not establish peer connection in time.");
        };

        Ok(())
    }

    fn echo(bytes: &[u8], _object_cache: &mut ObjectCache) -> Result<Vec<u8>> {
        Ok(bytes.to_vec())
    }

    #[tokio::test]
    async fn test_streaming() -> Result<()> {
        let _default_guard = log();
        let signaling_server = signaling_server().await?;

        let (connection_status_sender, connection_status_receiver) = oneshot::channel();
        let (py_sender, py_receiver) = kanal::bounded_async(100);
        let (polite_msg_sender, polite_msg_receiver) = kanal::bounded_async(100);

        let impolite_all_connections = AllConnections::default();
        let polite_all_connections = AllConnections::default();

        tokio::spawn(async move {
            while let Ok(msg) = signaling_server.polite_receiver.recv().await {
                let peer_id = msg.peer_id.into();
                let event = msg.event();
                info!("received event: {:?}", event);

                // If the peer connection doesn't exist and the event is an offer,
                // create a new peer connection and add to AllConnections.
                if polite_all_connections
                    .get_connection(&peer_id)
                    .await
                    .is_none()
                    && event == shared::RtcEvent::Offer
                {
                    info!("creating new peer connection for peer_id: {:?}", peer_id);
                    PolitePeerConnection::negotiate(
                        msg,
                        peer_id,
                        signaling_server.polite_sender.clone(),
                        signaling_server.polite_receiver.clone(),
                        polite_all_connections.clone(),
                        echo as fn(&[u8], &mut ObjectCache) -> Result<Vec<u8>>,
                    )
                    .await?;
                }
            }

            Ok::<(), anyhow::Error>(())
        });

        ImpolitePeerConnection::negotiate(
            0.into(),
            signaling_server.impolite_sender,
            signaling_server.impolite_receiver,
            impolite_all_connections,
            connection_status_sender,
            py_receiver,
            polite_msg_sender,
        )
        .await?;

        if let Err(_) = timeout(Duration::from_secs(5), connection_status_receiver).await {
            panic!("Could not establish peer connection in time.");
        };

        let small_payload = vec![1, 2, 3];

        let message = PyMessage {
            payload: small_payload.clone(),
            rids: vec![],
        };

        match py_sender.send(message).await {
            Ok(()) => info!("sent message",),
            Err(_) => error!("error sending message"),
        }

        if let Ok(response) = polite_msg_receiver.recv().await {
            assert_eq!(response, small_payload);
        }

        // let large_payload = vec![0u8; 30_000_000];
        let large_payload = vec![0u8; 100000489];
        info!("Large payload len: {}", (&large_payload).len());

        let message = PyMessage {
            payload: large_payload.clone(),
            rids: vec![],
        };

        let instant = Instant::now();
        match py_sender.send(message).await {
            Ok(()) => info!("sent message"),
            Err(_) => error!("error sending message"),
        }

        if let Ok(response) = polite_msg_receiver.recv().await {
            info!("received something");
            assert_eq!(response, large_payload);
        }

        let duration = instant.elapsed();

        info!(
            "Time to send and receive {} bytes: {:?}",
            large_payload.len(),
            duration
        );

        Ok(())
    }
}
