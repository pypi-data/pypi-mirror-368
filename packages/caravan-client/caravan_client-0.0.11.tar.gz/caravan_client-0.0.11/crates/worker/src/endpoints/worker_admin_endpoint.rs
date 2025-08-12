use thava_types::stubs::worker_admin::worker_admin_service_client::WorkerAdminServiceClient;
use thava_types::stubs::worker_admin::{CreateWorkerAdminRequest, GetWorkerAdminByEmailRequest};

use crate::subcommands::init::{Email, Name, Password};

use argon2::password_hash::rand_core::OsRng;
use argon2::password_hash::SaltString;
use argon2::{Algorithm, Argon2, Params, PasswordHasher, Version};

use thava_types::uid::Uid;
use thava_types::worker_admin::WorkerAdmin;

use anyhow::Result;
use thiserror::Error;

use tonic::transport::Channel;
use tonic::Request;

#[derive(Error, Debug)]
pub enum WorkerAdminEndpointError {
    #[error("Failed to connect to the thava distributor.")]
    CreateWorkerAdminError,
    #[error("Failed to get worker admin.")]
    GetWorkerAdminError,
}

pub struct WorkerAdminEndpoint(WorkerAdminServiceClient<Channel>);

impl WorkerAdminEndpoint {
    /// Creates a new WorkerAdminEndpoint by connecting to the distributor
    pub async fn new() -> Result<Self> {
        // "https://distributor-image-bejxcjmudq-uw.a.run.app"
        match WorkerAdminServiceClient::connect("http://0.0.0.0:50051").await {
            Ok(client) => Ok(Self(client)),
            Err(_) => Err(WorkerAdminEndpointError::CreateWorkerAdminError.into()),
        }
    }

    pub async fn create_worker_admin(
        &mut self,
        name: Name,
        email: Email,
        password: Password,
    ) -> Result<(Uid, String)> {
        let hash_params = match Params::new(15000, 2, 1, None) {
            Ok(params) => params,
            Err(_) => return Err(WorkerAdminEndpointError::CreateWorkerAdminError.into()),
        };
        let hasher = Argon2::new(Algorithm::Argon2id, Version::V0x13, hash_params);

        let salt = SaltString::generate(&mut OsRng);

        let password_hash = match hasher.hash_password(password.as_bytes(), &salt) {
            Ok(hash) => hash.to_string(),
            Err(_) => return Err(WorkerAdminEndpointError::CreateWorkerAdminError.into()),
        };

        let id = self
            .0
            .create_worker_admin(Request::new(CreateWorkerAdminRequest {
                name: name.into(),
                email: email.into(),
                password: password_hash.clone(),
            }))
            .await?;

        Ok((id.into_inner().id.into(), password_hash))
    }

    pub async fn get_worker_admin_by_email(&mut self, email: Email) -> Result<Option<WorkerAdmin>> {
        let response = self
            .0
            .get_worker_admin_by_email(Request::new(GetWorkerAdminByEmailRequest {
                email: email.into(),
            }))
            .await?;

        let worker_admin = response
            .into_inner()
            .worker_admin
            .map(|worker_admin| worker_admin.into());

        Ok(worker_admin)
    }
}
