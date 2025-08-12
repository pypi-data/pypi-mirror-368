use std::collections::HashMap;

use derive_more::derive::Display;
use serde::{Deserialize, Serialize};

use crate::{uid::Uid, worker_admin::Email, worker_machine::WorkerMachine};

#[derive(
    Clone, Debug, Display, Default, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash,
)]
pub struct WorkerGroupId(pub Uid);

impl WorkerGroupId {
    pub fn new() -> WorkerGroupId {
        WorkerGroupId(Uid::new())
    }
}

#[derive(Clone, Debug, Display, Default)]
pub struct WorkerGroupName(pub String);

impl WorkerGroupName {
    pub fn new(name: &str) -> WorkerGroupName {
        WorkerGroupName(name.to_string())
    }
}

#[derive(Clone, Debug, Display, Default)]
pub struct SharingKey(pub String);

#[derive(Clone, Debug, Default)]
pub struct WorkerGroup {
    pub id: WorkerGroupId,
    pub name: WorkerGroupName,
    pub clients: HashMap<Email, SharingKey>,
    pub machines: Vec<WorkerMachine>,
}

impl WorkerGroup {
    pub fn new(name: WorkerGroupName) -> WorkerGroup {
        WorkerGroup {
            id: WorkerGroupId::default(),
            name,
            clients: HashMap::new(),
            machines: Vec::new(),
        }
    }
}
