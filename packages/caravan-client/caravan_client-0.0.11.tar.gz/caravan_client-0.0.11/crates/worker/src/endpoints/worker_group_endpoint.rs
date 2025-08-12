use crate::subcommands::init::Email;
use crate::subcommands::init::WorkerMachineId;

use super::stubs::worker_group::worker_group_service_client::WorkerGroupServiceClient;
use super::stubs::worker_group::RemoveClientsFromGroupResponse;
use super::stubs::worker_group::{
    AddClientsToGroupRequest, AddClientsToGroupResponse, AddWorkerMachineRequest,
    CreateWorkerGroupRequest, CreateWorkerGroupResponse, DeleteWorkerGroupRequest,
    GetAllWorkerGroupsRequest, RemoveClientsFromGroupRequest, RemoveWorkerMachineRequest,
};
use super::worker_machine_endpoint::{Authenticator, WorkerMachineEndpoint};

use anyhow::Result;

use thava_types::uid::Uid;
use thava_types::worker_group::{SharingKey, WorkerGroup, WorkerGroupId, WorkerGroupName};
use tonic::service::interceptor::InterceptedService;
use tonic::transport::Channel;
use tonic::Request;

pub struct WorkerGroupEndpoint<T>(WorkerGroupServiceClient<T>);

impl WorkerGroupEndpoint<InterceptedService<Channel, Authenticator>> {
    pub async fn new_with_auth() -> Result<Self> {
        let channel = Channel::from_static("http://0.0.0.0:50051")
            .connect()
            .await?;

        let authenticator = Authenticator::from_config()?;

        let worker_group_endpoint =
            WorkerGroupServiceClient::with_interceptor(channel, authenticator);
        Ok(Self(worker_group_endpoint))
    }

    pub async fn create_group(&mut self, name: &str) -> Result<CreateWorkerGroupResponse> {
        let request = Request::new(CreateWorkerGroupRequest {
            name: name.to_string(),
        });

        let response = self.0.create_worker_group(request).await?.into_inner();

        Ok(response)
    }

    pub async fn add_clients_to_group(
        &mut self,
        group_name: &str,
        emails: Vec<Email>,
    ) -> Result<AddClientsToGroupResponse> {
        let emails: Vec<String> = emails.into_iter().map(|email| email.into()).collect();

        let request = Request::new(AddClientsToGroupRequest {
            group: group_name.to_string(),
            emails: emails.clone(),
        });

        let response = self.0.add_clients_to_group(request).await?.into_inner();

        Ok(response)
    }

    pub async fn remove_clients_from_group(
        &mut self,
        group_name: &str,
        emails: Vec<Email>,
    ) -> Result<RemoveClientsFromGroupResponse> {
        let emails: Vec<String> = emails.into_iter().map(|email| email.into()).collect();

        let request = Request::new(RemoveClientsFromGroupRequest {
            group: group_name.to_string(),
            emails: emails.clone(),
        });

        // TODO: This is one way, the other way is in add_clients_to_group
        match self.0.remove_clients_from_group(request).await {
            Ok(response) => Ok(response.into_inner()),
            Err(e) => Err(e.into()),
        }
    }

    pub async fn list_groups(&mut self) -> Result<Vec<WorkerGroup>> {
        let request = Request::new(GetAllWorkerGroupsRequest {});

        let response = self.0.get_all_worker_groups(request).await?.into_inner();

        let worker_groups_protos = response.worker_groups;

        let mut worker_groups = vec![];
        for group in worker_groups_protos.iter() {
            worker_groups.push(self.group_from_proto(group.clone()).await?);
        }

        Ok(worker_groups)
    }

    pub async fn delete_group(&mut self, name: &str) -> Result<()> {
        let request = Request::new(DeleteWorkerGroupRequest {
            name: name.to_string(),
        });

        self.0.delete_worker_group(request).await?;

        Ok(())
    }

    pub async fn add_worker_machine(&mut self, group_name: &str, machine_id: i64) -> Result<()> {
        let request = Request::new(AddWorkerMachineRequest {
            worker_machine_id: machine_id,
            worker_group_name: group_name.to_string(),
        });

        self.0.add_worker_machine(request).await?;

        Ok(())
    }

    pub async fn remove_worker_machine(&mut self, group_name: &str, machine_id: i64) -> Result<()> {
        let request = Request::new(RemoveWorkerMachineRequest {
            worker_machine_id: machine_id,
            worker_group_name: group_name.to_string(),
        });

        self.0.remove_worker_machine(request).await?;

        Ok(())
    }

    async fn group_from_proto(
        &self,
        group: super::stubs::worker_group::WorkerGroup,
    ) -> Result<WorkerGroup> {
        let mut worker_machine_endpoint = WorkerMachineEndpoint::new_with_auth().await?;

        let clients = group
            .clients
            .into_iter()
            .map(|(email, key)| (thava_types::worker_admin::Email(email), SharingKey(key)))
            .collect();

        let mut machines = vec![];
        for machine_id in group.machines {
            let machine_id = Uid::from(machine_id);
            let machine = worker_machine_endpoint
                .get_worker_machine(WorkerMachineId(machine_id))
                .await?;
            let machine = thava_types::worker_machine::WorkerMachine {
                id: thava_types::worker_machine::WorkerMachineId(machine.id.into()),
                gpus: machine.gpus.into(),
                admin_id: machine.worker_admin_id.into(),
                status: machine.status.into(),
                device_statuses: machine.device_statuses.into(),
                cn_to_w: machine.cn_to_w.into(),
                w_to_cn: machine.w_to_cn.into(),
            };
            machines.push(machine);
        }

        machines.sort_by_key(|machine| machine.id.clone());

        Ok(WorkerGroup {
            id: WorkerGroupId(Uid::from(group.id)),
            name: WorkerGroupName(group.name),
            clients,
            machines,
        })
    }
}
