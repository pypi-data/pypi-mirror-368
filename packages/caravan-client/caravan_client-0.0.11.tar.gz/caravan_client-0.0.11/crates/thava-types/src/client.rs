use crate::uid::Uid;

use serde::{Deserialize, Serialize};

use derive_more::{derive::Deref, Display};

#[derive(Debug, Display, Deref, Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Default)]
pub struct ClientId(pub Uid);

impl ClientId {
    pub fn new() -> Self {
        ClientId(Uid::new())
    }
}

impl From<i64> for ClientId {
    fn from(id: i64) -> ClientId {
        ClientId(Uid::from(id))
    }
}

impl From<ClientId> for i64 {
    fn from(id: ClientId) -> i64 {
        id.0.into()
    }
}

impl From<Uid> for ClientId {
    fn from(id: Uid) -> Self {
        ClientId(id)
    }
}

impl From<ClientId> for Uid {
    fn from(id: ClientId) -> Uid {
        id.0
    }
}
