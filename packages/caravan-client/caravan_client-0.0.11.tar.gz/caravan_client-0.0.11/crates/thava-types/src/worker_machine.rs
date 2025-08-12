use super::uid::Uid;
use super::worker_admin::WorkerAdminId;

use std::collections::{BTreeMap, HashMap};

use derive_more::{derive::Deref, Display};

use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash)]
pub struct WorkerMachineId(pub Uid);

impl WorkerMachineId {
    pub fn new() -> WorkerMachineId {
        WorkerMachineId(Uid::new())
    }
}

impl Default for WorkerMachineId {
    fn default() -> WorkerMachineId {
        WorkerMachineId::new()
    }
}

impl From<i64> for WorkerMachineId {
    fn from(id: i64) -> WorkerMachineId {
        WorkerMachineId(Uid::from(id))
    }
}

impl From<WorkerMachineId> for i64 {
    fn from(id: WorkerMachineId) -> i64 {
        id.0.into()
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash)]
pub struct GpuId(pub String);

impl GpuId {
    pub fn new(id: String) -> GpuId {
        GpuId(id)
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct GpuName(pub String);

impl GpuName {
    pub fn new(name: String) -> GpuName {
        GpuName(name)
    }
}

#[derive(Clone, Debug, Default, Deref, PartialEq, Eq, Serialize, Deserialize)]
pub struct Gpus(pub BTreeMap<GpuId, GpuName>);

impl Gpus {
    pub fn new() -> Gpus {
        Gpus(BTreeMap::new())
    }

    pub fn add_gpu(&mut self, id: GpuId, name: GpuName) {
        self.0.insert(id, name);
    }
}

impl From<HashMap<u32, String>> for Gpus {
    fn from(gpus: HashMap<u32, String>) -> Gpus {
        let mut gpus_map = BTreeMap::new();
        for (id, name) in gpus {
            gpus_map.insert(GpuId::new(id.to_string()), GpuName::new(name));
        }
        Gpus(gpus_map)
    }
}

impl From<Gpus> for HashMap<u32, String> {
    fn from(gpus: Gpus) -> HashMap<u32, String> {
        let mut gpus_map = HashMap::new();
        for (id, name) in gpus.0 {
            gpus_map.insert(id.0.parse().unwrap(), name.0);
        }
        gpus_map
    }
}

impl From<HashMap<String, String>> for Gpus {
    fn from(gpus: HashMap<String, String>) -> Gpus {
        let mut gpus_map = BTreeMap::new();
        for (id, name) in gpus {
            gpus_map.insert(GpuId::new(id), GpuName::new(name));
        }
        Gpus(gpus_map)
    }
}

impl From<Gpus> for HashMap<String, String> {
    fn from(gpus: Gpus) -> HashMap<String, String> {
        let mut gpus_map = HashMap::new();
        for (id, name) in gpus.0 {
            gpus_map.insert(id.0, name.0);
        }
        gpus_map
    }
}

#[derive(Clone, Debug, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Memory(pub f32);

impl Memory {
    pub fn new(memory: f32) -> Memory {
        Memory(memory)
    }
}

impl From<Memory> for f32 {
    fn from(memory: Memory) -> f32 {
        memory.0
    }
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Cores(pub u32);

impl Cores {
    pub fn new(cores: u32) -> Cores {
        Cores(cores)
    }
}

impl From<Cores> for u32 {
    fn from(cores: Cores) -> u32 {
        cores.0
    }
}

#[derive(
    Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Default,
)]
pub enum WorkerMachineStatus {
    #[display("Available")]
    Available,
    #[default]
    #[display("Unavailable")]
    Unavailable,
}

impl From<WorkerMachineStatus> for i32 {
    fn from(status: WorkerMachineStatus) -> i32 {
        match status {
            WorkerMachineStatus::Available => 0,
            WorkerMachineStatus::Unavailable => 1,
        }
    }
}

impl From<WorkerMachineStatus> for i64 {
    fn from(status: WorkerMachineStatus) -> i64 {
        match status {
            WorkerMachineStatus::Available => 0,
            WorkerMachineStatus::Unavailable => 1,
        }
    }
}

impl From<i32> for WorkerMachineStatus {
    fn from(status: i32) -> WorkerMachineStatus {
        match status {
            0 => WorkerMachineStatus::Available,
            1 => WorkerMachineStatus::Unavailable,
            _ => WorkerMachineStatus::Unavailable,
        }
    }
}

#[derive(Clone, Debug, Deref, PartialEq, Serialize, Deserialize)]
pub struct Topic(pub String);

impl From<Topic> for String {
    fn from(topic: Topic) -> String {
        topic.0
    }
}

impl From<String> for Topic {
    fn from(topic: String) -> Topic {
        Topic(topic)
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct WorkerMachine {
    pub id: WorkerMachineId,
    pub gpus: Gpus,
    pub admin_id: WorkerAdminId,
    pub status: WorkerMachineStatus,
    pub device_statuses: DeviceStatuses,
    pub cn_to_w: Topic,
    pub w_to_cn: Topic,
}

impl WorkerMachine {
    pub fn new(
        id: WorkerMachineId,
        gpus: Gpus,
        admin_id: WorkerAdminId,
        status: WorkerMachineStatus,
        device_statuses: DeviceStatuses,
    ) -> WorkerMachine {
        let cn_to_w = Topic(format!("cn_to_w{}", id.clone()).to_string());
        let w_to_cn = Topic(format!("w{}_to_cn", id.clone()).to_string());

        WorkerMachine {
            id,
            gpus,
            admin_id,
            status,
            device_statuses,
            cn_to_w,
            w_to_cn,
        }
    }
}

impl From<super::stubs::worker_machine::WorkerMachine> for WorkerMachine {
    fn from(machine: super::stubs::worker_machine::WorkerMachine) -> WorkerMachine {
        WorkerMachine {
            id: WorkerMachineId(machine.id.into()),
            gpus: machine.gpus.into(),
            admin_id: WorkerAdminId(machine.worker_admin_id.into()),
            status: machine.status.into(),
            device_statuses: machine.device_statuses.into(),
            cn_to_w: Topic(machine.cn_to_w),
            w_to_cn: Topic(machine.w_to_cn),
        }
    }
}

/// DeviceStatuses maps a GPU's ID to its availability status, a single map per worker machine
#[derive(Deref, Default, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DeviceStatuses(HashMap<GpuId, WorkerMachineStatus>);

impl DeviceStatuses {
    pub fn new(statuses: HashMap<GpuId, WorkerMachineStatus>) -> Self {
        DeviceStatuses(statuses)
    }

    pub fn set_status(&mut self, device_id: GpuId, status: WorkerMachineStatus) {
        self.0.insert(device_id, status);
    }

    pub fn get_status(&self, device_index: GpuId) -> Option<&WorkerMachineStatus> {
        self.0.get(&device_index)
    }

    pub fn get_all_statuses(&self) -> &HashMap<GpuId, WorkerMachineStatus> {
        &self.0
    }
}

impl From<DeviceStatuses> for HashMap<String, i32> {
    fn from(statuses: DeviceStatuses) -> HashMap<String, i32> {
        statuses
            .0
            .iter()
            .map(|(id, status)| (id.0.clone(), status.clone().into()))
            .collect()
    }
}

impl From<HashMap<String, i32>> for DeviceStatuses {
    fn from(statuses: HashMap<String, i32>) -> DeviceStatuses {
        let mut device_statuses = HashMap::new();
        for (id, status) in statuses {
            device_statuses.insert(GpuId::new(id), WorkerMachineStatus::from(status));
        }
        DeviceStatuses(device_statuses)
    }
}
