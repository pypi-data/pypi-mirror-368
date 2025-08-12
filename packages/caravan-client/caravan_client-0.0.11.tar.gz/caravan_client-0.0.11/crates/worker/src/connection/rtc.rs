use crate::endpoints::stubs::shared::{PeerRtcMessage, RtcEvent};

use bytes::Bytes;
use thava_types::biject::payload::{self, ObjectCache};
use thava_types::client::ClientId;
use thava_types::rtc::{
    AllConnections, Channel, ConnectionState, PeerConnection, RtcMessage, SignalingChannel,
};
use thava_types::uid::Uid;
use tokio::time;

use anyhow::Result;
use core::fmt;
use std::{marker::PhantomData, time::Duration};

use tracing::info;
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

/// Creates a new `PeerConnection` for a worker as the polite peer,
/// and adds handlers to check states and handle local ICE candidates.
///
/// # Arguments
///
/// * `peer_id` - The id of the peer to connect to
/// * `signaling_channel` - The signaling channel to send and receive messages
pub async fn worker_peer_connection(
    peer_id: &Uid,
    signaling_channel: &SignalingChannel<PeerRtcMessage>,
) -> Result<PeerConnection> {
    let peer_connection = PeerConnection::default().await?;
    peer_connection.start_state_change_handler(peer_id.clone(), signaling_channel.clone())?;
    peer_connection
        .start_ice_candidate_handler::<PeerRtcMessage>(peer_id.clone(), signaling_channel.clone())
        .await?;
    peer_connection
        .clone()
        .start_data_channel_handler(peer_id.clone(), signaling_channel.clone())
        .await;
    Ok(peer_connection)
}

/// Wrapper around the impolite state machine for ergonomic
/// matching for state transitions.
#[derive(Clone)]
pub enum PeerConnectionState {
    Unoffered(PolitePeerConnection<Unoffered>),
    Offered(PolitePeerConnection<Offered>),
    Connected(PolitePeerConnection<Connected>),
    Closed(PolitePeerConnection<Closed>),
}

/// Needed to store `PeerConnectionState` in `AllConnections`.
impl ConnectionState<ClientId> for PeerConnectionState {
    fn id(&self) -> ClientId {
        match self {
            PeerConnectionState::Unoffered(peer) => peer.id.clone(),
            PeerConnectionState::Offered(peer) => peer.id.clone(),
            PeerConnectionState::Connected(peer) => peer.id.clone(),
            PeerConnectionState::Closed(peer) => peer.id.clone(),
        }
    }
}

impl fmt::Debug for PeerConnectionState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PeerConnectionState::Unoffered(_) => write!(f, "Unoffered"),
            PeerConnectionState::Offered(_) => write!(f, "Offered"),
            PeerConnectionState::Connected(_) => write!(f, "Connected"),
            PeerConnectionState::Closed(_) => write!(f, "Closed"),
        }
    }
}

// Supported states for the polite peer connection state machine.
#[derive(Clone)]
pub struct Unoffered;
#[derive(Clone)]
pub struct Offered;
#[derive(Clone)]
pub struct Connected;
#[derive(Clone)]
pub struct Closed;

type HandleTask = tokio::task::AbortHandle;

/// The polite peer connection state machine. Motivated by compile-time
/// guarantees and ergonomic state transitions.
///
/// * `peer_id` - id of the client that we try to connect with
/// * `inner` - the actual `PeerConnection` itself
/// * `signaling_channel` - Channel with distributor to send and receive RTC messages
#[derive(Clone)]
pub struct PolitePeerConnection<S> {
    id: ClientId,
    inner: PeerConnection,
    handle_fn: fn(&[u8], &mut ObjectCache) -> Result<Vec<u8>>,
    handle_task: Option<HandleTask>,
    signaling_channel: SignalingChannel<PeerRtcMessage>,
    all_connections: AllConnections<ClientId, PeerConnectionState>,
    _state: PhantomData<fn() -> S>,
}

impl PolitePeerConnection<Unoffered> {
    /// Starts a new peer connection with the given peer id. Sends ping
    /// to distributor every 30 seconds.
    pub async fn negotiate(
        msg: PeerRtcMessage,
        peer_id: ClientId,
        external_sender: kanal::AsyncSender<PeerRtcMessage>,
        external_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        all_connections: AllConnections<ClientId, PeerConnectionState>,
        handle_fn: fn(&[u8], &mut ObjectCache) -> Result<Vec<u8>>,
    ) -> Result<()> {
        info!("init to unoffered");

        let (internal_sender, internal_receiver) = kanal::bounded_async(100);
        let signaling_channel =
            SignalingChannel::new(internal_sender, external_sender, external_receiver);

        let peer_connection = worker_peer_connection(&peer_id, &signaling_channel).await?;

        // TODO: make constant
        let mut interval = time::interval(Duration::from_secs(30));
        let signaling_channel_c = signaling_channel.clone();
        let peer_id_c = peer_id.clone();
        tokio::spawn(async move {
            loop {
                interval.tick().await;
                info!("sending ping for client {}", &peer_id_c);
                let ping_message = PeerRtcMessage {
                    peer_id: peer_id_c.clone().into(),
                    event: RtcEvent::Ping.into(),
                    message: vec![],
                };

                signaling_channel_c
                    .clone()
                    .internal_send(ping_message)
                    .await?;
            }

            #[allow(unreachable_code)]
            Ok::<(), anyhow::Error>(())
        });

        let state = PolitePeerConnection {
            id: peer_id.clone(),
            inner: peer_connection,
            handle_fn,
            handle_task: None,
            signaling_channel: signaling_channel.clone(),
            all_connections: all_connections.clone(),
            _state: PhantomData,
        };

        PolitePeerConnection::_negotiate(
            msg,
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
        msg: PeerRtcMessage,
        peer_id: ClientId,
        state: PolitePeerConnection<Unoffered>,
        signaling_channel: SignalingChannel<PeerRtcMessage>,
        internal_receiver: kanal::AsyncReceiver<PeerRtcMessage>,
        all_connections: AllConnections<ClientId, PeerConnectionState>,
    ) -> Result<()> {
        let state = PeerConnectionState::Unoffered(state);

        all_connections
            .add_connection::<PeerRtcMessage>(state.clone())
            .await?;

        let all_connections_c = all_connections.clone();
        let signaling_channel_c = signaling_channel.clone();
        let peer_id_c = peer_id.clone();

        PolitePeerConnection::transition_external(msg, &peer_id, state, all_connections.clone())
            .await?;

        tokio::spawn(async move {
            let all_connections = all_connections_c.clone();
            let mut signaling_channel = signaling_channel_c.clone();
            let peer_id = peer_id_c.clone();

            while let Ok(msg) = signaling_channel.recv().await {
                let all_connections = all_connections.clone();
                let client_id: ClientId = msg.peer_id.into();
                if client_id != peer_id {
                    continue;
                }

                let state = all_connections.clone().get_connection(&client_id).await;

                if state.is_none() {
                    return Err(anyhow::anyhow!(
                        "State did not exist before receiving peer connection messages \
                        from client_id {client_id}."
                    ));
                }

                let state = state.unwrap();

                PolitePeerConnection::transition_external(msg, &peer_id, state, all_connections)
                    .await?;
            }

            Ok::<(), anyhow::Error>(())
        });

        tokio::spawn(async move {
            let all_connections_c = all_connections.clone();
            let signaling_channel_c = signaling_channel.clone();
            while let Ok(msg) = internal_receiver.recv().await {
                let all_connections = all_connections_c.clone();
                let signaling_channel = signaling_channel_c.clone();
                let client_id: ClientId = msg.peer_id.into();
                if client_id != peer_id {
                    continue;
                }

                let state = all_connections.clone().get_connection(&client_id).await;

                if state.is_none() {
                    return Err(anyhow::anyhow!(
                        "State did not exist before receiving peer connection messages \
                        from client_id {client_id}."
                    ));
                }

                let state = state.unwrap();

                PolitePeerConnection::transition_internal(
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

    async fn transition_external(
        msg: PeerRtcMessage,
        peer_id: &ClientId,
        state: PeerConnectionState,
        all_connections: AllConnections<ClientId, PeerConnectionState>,
    ) -> Result<()> {
        let event = msg.event();
        info!("received external event: {:?}", event);
        // Check for state transition conditions such that we have compile-time guarantees
        // of transition correctness. Transitions will send messages to the signaling
        // channel.
        match (&state, event) {
            (PeerConnectionState::Unoffered(current_state), RtcEvent::Offer) => {
                let offer_payload = String::from_utf8(msg.message.clone())?;
                let new_state = current_state.clone().to_offered(&offer_payload).await?;
                let state = PeerConnectionState::Offered(new_state);

                all_connections.set_connection(&peer_id, state).await?;
            }
            (PeerConnectionState::Offered(current_state), RtcEvent::IceCandidate) => {
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
                    "Unhandled state and event combination: {:?} {:?}",
                    state, event
                );
            }
        }

        Ok(())
    }
    async fn transition_internal(
        msg: PeerRtcMessage,
        peer_id: &ClientId,
        state: PeerConnectionState,
        all_connections: AllConnections<ClientId, PeerConnectionState>,
        signaling_channel: SignalingChannel<PeerRtcMessage>,
    ) -> Result<()> {
        let event = msg.event();
        info!("received internal event: {:?}", event);
        match (&state, event) {
            // If local ICE candidates are somehow generated before an offer is received,
            // store them in a pending list.
            (PeerConnectionState::Unoffered(current_state), RtcEvent::IceCandidate) => {
                if let Err(e) = current_state
                    .add_pending_candidate(msg.message.clone())
                    .await
                {
                    info!("Error adding pending candidate: {:?}", e);
                }
            }
            (PeerConnectionState::Unoffered(current_state), RtcEvent::Closed) => {
                let new_state = current_state
                    .clone()
                    .to_closed()
                    .await
                    .expect("Failed to close connection");
                let state = PeerConnectionState::Closed(new_state);
                all_connections
                    .set_connection(&peer_id, state)
                    .await
                    .expect("Failed to set connection");
            }
            // If data channel opens, intercept and transition to connected state.
            (PeerConnectionState::Offered(current_state), RtcEvent::Connected) => {
                let new_state = current_state
                    .clone()
                    .to_connected()
                    .await
                    .expect("Failed to transition to connected");
                let state = PeerConnectionState::Connected(new_state);
                all_connections
                    .set_connection(&peer_id, state)
                    .await
                    .expect("Failed to set connection");
            }
            (PeerConnectionState::Offered(current_state), RtcEvent::Closed) => {
                let new_state = current_state
                    .clone()
                    .to_closed()
                    .await
                    .expect("Failed to close connection");
                let state = PeerConnectionState::Closed(new_state);
                all_connections
                    .set_connection(&peer_id, state)
                    .await
                    .expect("Failed to set connection");
            }
            (PeerConnectionState::Connected(current_state), RtcEvent::Closed) => {
                let new_state = current_state
                    .clone()
                    .to_closed()
                    .await
                    .expect("Failed to close connection");
                let state = PeerConnectionState::Closed(new_state);
                all_connections
                    .set_connection(&peer_id, state)
                    .await
                    .expect("Failed to set connection");
            }
            // otherwise, yield the message
            // Messages yielded here include ICE candidates in the Offered or Connected
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

    /// Stores local ICE candidates until in the `Offered` state.
    pub async fn add_pending_candidate(&self, candidate_payload: Vec<u8>) -> Result<()> {
        info!("adding pending candidate");
        let candidate_payload: String = String::from_utf8(candidate_payload)?;
        let candidate: RTCIceCandidateInit = RTCIceCandidateInit {
            candidate: candidate_payload,
            ..Default::default()
        };
        self.inner.pending_candidates.lock().await.push(candidate);
        Ok(())
    }

    /// Receives an offer from the peer and transitions to the `Offered` state.
    /// Sends all pending ICE candidates.
    pub async fn to_offered(self, offer: &str) -> Result<PolitePeerConnection<Offered>> {
        info!("unoffered to offered");
        let offer: RTCSessionDescription = serde_json::from_str(offer)?;
        self.inner
            .rtc_connection
            .set_remote_description(offer)
            .await?;

        let answer = self.inner.rtc_connection.create_answer(None).await?;
        self.inner
            .rtc_connection
            .set_local_description(answer.clone())
            .await?;

        let answer = serde_json::to_string(&answer)?;

        self.signaling_channel
            .internal_send(PeerRtcMessage {
                peer_id: self.id.clone().into(),
                event: RtcEvent::Answer as i32,
                message: answer.into(),
            })
            .await?;

        let offered: PolitePeerConnection<Offered> = PolitePeerConnection {
            id: self.id,
            inner: self.inner,
            handle_fn: self.handle_fn,
            handle_task: self.handle_task,
            signaling_channel: self.signaling_channel,
            all_connections: self.all_connections,
            _state: PhantomData,
        };

        offered.send_all_pending_candidates().await?;

        Ok(offered)
    }

    pub async fn close<T>(state: PolitePeerConnection<T>) -> Result<PolitePeerConnection<Closed>> {
        state.inner.rtc_connection.close().await?;
        state
            .all_connections
            .remove_connection(state.id.clone())
            .await?;
        Ok(PolitePeerConnection {
            id: state.id,
            inner: state.inner,
            handle_fn: state.handle_fn,
            handle_task: state.handle_task,
            signaling_channel: state.signaling_channel,
            all_connections: state.all_connections,
            _state: PhantomData,
        })
    }

    /// Closes the connection and transitions to the `Closed` state.
    pub async fn to_closed(self) -> Result<PolitePeerConnection<Closed>> {
        info!("unoffered to closed");
        PolitePeerConnection::close(self).await
    }
}

impl PolitePeerConnection<Offered> {
    /// Sends all pending ICE candidates.
    pub async fn send_all_pending_candidates(&self) -> Result<()> {
        info!("sending all pending candidates");
        let mut pending_candidates = self.inner.pending_candidates.lock().await;
        for candidate in pending_candidates.iter() {
            self.send_ice_candidate_str(&candidate.candidate).await?;
        }
        pending_candidates.clear();
        Ok(())
    }

    /// Sends an ICE candidate that is already in string format.
    pub async fn send_ice_candidate_str(&self, candidate_payload: &str) -> Result<()> {
        info!("sending ice candidate");
        let message = PeerRtcMessage::new(
            self.id.0.clone(),
            RtcEvent::IceCandidate as i32,
            candidate_payload.into(),
        );
        self.signaling_channel.internal_send(message).await?;
        Ok(())
    }

    /// Sends an ICE candidate.
    pub async fn send_ice_candidate(&self, candidate: RTCIceCandidate) -> Result<()> {
        info!("sending ice candidate");
        let candidate_payload = candidate.to_json()?.candidate;
        let message = PeerRtcMessage::new(
            self.id.0.clone(),
            RtcEvent::IceCandidate as i32,
            candidate_payload.into(),
        );
        self.signaling_channel.internal_send(message).await?;
        Ok(())
    }

    /// Receives an ICE candidate and adds it to the peer connection.
    pub async fn recv_ice_candidate(&self, candidate_payload: String) -> Result<()> {
        info!("receiving ice candidate");
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
    /// Starts `rtorch` bijection on the worker end.
    pub async fn to_connected(self) -> Result<PolitePeerConnection<Connected>> {
        info!("offered to connected");
        let new_state = PolitePeerConnection {
            id: self.id,
            inner: self.inner.clone(),
            handle_fn: self.handle_fn,
            handle_task: self.handle_task,
            signaling_channel: self.signaling_channel,
            all_connections: self.all_connections,
            _state: PhantomData,
        };

        let new_state = new_state.start_rtorch().await?;

        Ok(new_state)
    }

    /// Closes the connection and transitions to the `Closed` state.
    pub async fn to_closed(self) -> Result<PolitePeerConnection<Closed>> {
        info!("offered to closed");
        PolitePeerConnection::close(self).await
    }
}

impl PolitePeerConnection<Connected> {
    /// Starts the `rtorch` bijection for a new connection.
    pub async fn start_rtorch(self) -> Result<PolitePeerConnection<Connected>> {
        let data_channel = self.inner.data_channel.clone();
        let handle_fn = self.handle_fn.clone();

        // maps ids to torch objects
        let mut object_cache = payload::init_object_cache();

        // `DataChannel` message handler - every incoming message
        // from the impolite peer gets handled, and the response is
        // sent back over the channel.
        let handle_task = tokio::spawn(async move {
            let mut data_channel = data_channel.clone();
            while let Ok(message) = data_channel.recv().await {
                info!("received message");
                let result: Bytes = (handle_fn)(&message, &mut object_cache)?.into();

                // If FUTURE, we return an empty vec, so we don't send anything back.
                if result.is_empty() {
                    info!("empty result due to future, not sending");
                    continue;
                }

                // If BLOCKER, we simply relay whatever result to the client.
                info!("nonempty result, sending back across data channel");
                data_channel.send(result.to_vec(), None).await?;
            }

            info!("data channel receiver closed");
            Ok::<(), anyhow::Error>(())
        });

        Ok(PolitePeerConnection {
            id: self.id,
            inner: self.inner.clone(),
            handle_fn: self.handle_fn,
            handle_task: Some(handle_task.abort_handle()),
            signaling_channel: self.signaling_channel,
            all_connections: self.all_connections,
            _state: PhantomData,
        })
    }

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
            self.id.0.clone(),
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
    pub async fn to_closed(self) -> Result<PolitePeerConnection<Closed>> {
        info!("connected to closed");

        if let Some(ref handle_task) = self.handle_task {
            info!("aborting handle fn");
            handle_task.abort();
        }

        PolitePeerConnection::close(self).await
    }
}

impl PolitePeerConnection<Closed> {
    /// Changes nothing; included for idempotency.
    pub async fn to_closed(self) -> Result<PolitePeerConnection<Closed>> {
        info!("closed to closed");
        PolitePeerConnection::close(self).await
    }
}
