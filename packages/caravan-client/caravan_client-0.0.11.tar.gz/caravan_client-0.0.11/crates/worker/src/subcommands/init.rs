use crate::endpoints::worker_admin_endpoint::WorkerAdminEndpoint;

use super::super::config;
use super::super::config::Config;
use super::super::endpoints::worker_machine_endpoint::WorkerMachineEndpoint;

use thava_types::uid::Uid;
use thava_types::worker_admin::WorkerAdmin;
use thava_types::worker_machine::WorkerMachineStatus;

use anyhow::{bail, Result};
use thiserror::Error;

use std::collections::{HashMap, HashSet};
use std::error;
use std::fmt;
use std::result;

use derive_more::{AsRef, Deref, Display};
use serde::{Deserialize, Serialize};

use nvml_wrapper::Nvml;

use inquire::validator::{StringValidator, Validation};
use inquire::Select;
use inquire::{Confirm, MultiSelect, Text};

use validator::ValidateEmail;

#[cfg(target_os = "macos")]
use objc2_metal::{MTLCopyAllDevices, MTLDevice};

#[derive(Display, Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash)]
pub struct GpuId(String);

impl GpuId {
    pub fn new(id: String) -> GpuId {
        GpuId(id)
    }
}

impl From<u32> for GpuId {
    fn from(id: u32) -> GpuId {
        GpuId(id.to_string())
    }
}

impl From<GpuId> for u32 {
    fn from(id: GpuId) -> u32 {
        id.0.parse().unwrap()
    }
}

impl From<GpuId> for String {
    fn from(id: GpuId) -> String {
        id.0
    }
}

#[derive(Display, Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct GpuName(String);

impl GpuName {
    pub fn new(name: String) -> GpuName {
        GpuName(name)
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, Default)]
pub struct Gpus(HashMap<GpuId, GpuName>);

impl Gpus {
    pub fn new(gpus: HashMap<GpuId, GpuName>) -> Gpus {
        Gpus(gpus)
    }

    #[cfg(target_os = "macos")]
    pub fn get_mac_gpus_vec() -> Vec<GpuName> {
        let mut gpus = Vec::new();

        let devices = MTLCopyAllDevices();

        for device in devices.iter() {
            let name = device.name();
            let gpu_name = GpuName::new(name.to_string());

            gpus.push(gpu_name);
        }
        gpus
    }

    #[cfg(target_os = "macos")]
    pub fn get_mac_gpus_statuses() -> DeviceStatuses {
        let mut statuses = HashMap::new();
        let devices = MTLCopyAllDevices();

        // TODO: If multiple GPU devices found on mac then find custom uuid for each device rather
        // than using the name as the ID.
        for (i, device) in devices.iter().enumerate() {
            let name = device.name();
            statuses.insert(GpuId(name.to_string()), WorkerMachineStatus::Unavailable);
        }

        DeviceStatuses::new(statuses)
    }
}

impl From<HashMap<u32, String>> for Gpus {
    fn from(gpus: HashMap<u32, String>) -> Self {
        let gpus = gpus
            .iter()
            .map(|(id, name)| (GpuId::new(id.to_string()), GpuName::new(name.clone())))
            .collect();
        Gpus(gpus)
    }
}

impl From<Vec<Gpu>> for Gpus {
    fn from(gpus: Vec<Gpu>) -> Self {
        let gpus = gpus
            .iter()
            .map(|gpu| (GpuId::new(gpu.0.to_string()), gpu.name().unwrap()))
            .collect();
        Gpus(gpus)
    }
}

impl From<Vec<GpuName>> for Gpus {
    fn from(gpus: Vec<GpuName>) -> Self {
        let gpus_map = gpus
            .into_iter()
            .enumerate()
            .map(|(i, name)| (GpuId::new(i.to_string()), name))
            .collect();
        Gpus(gpus_map)
    }
}

impl From<Gpus> for HashMap<u32, String> {
    fn from(val: Gpus) -> Self {
        val.0
            .iter()
            .map(|(id, name)| (id.0.parse().unwrap(), name.0.clone()))
            .collect()
    }
}

#[derive(Debug, Display, Error, Clone, Serialize, Deserialize, Default, Deref)]
pub struct WorkerMachineId(pub Uid);

impl WorkerMachineId {
    pub fn new(id: Uid) -> Self {
        WorkerMachineId(id)
    }
}

impl From<WorkerMachineId> for i64 {
    fn from(id: WorkerMachineId) -> i64 {
        id.0.into()
    }
}

#[derive(Debug, Display, Error, Clone, Serialize, Deserialize, Default, Deref)]
pub struct WorkerAdminId(Uid);

impl WorkerAdminId {
    pub fn new(id: Uid) -> Self {
        WorkerAdminId(id)
    }
}

impl From<WorkerAdminId> for i64 {
    fn from(id: WorkerAdminId) -> i64 {
        id.0.into()
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

    pub fn get_all_statuses(&self) -> HashMap<GpuId, WorkerMachineStatus> {
        self.0.clone()
    }
}

impl fmt::Display for DeviceStatuses {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{{ {} }}",
            self.0
                .iter()
                .map(|(id, status)| format!("{}: {}", id.0, status))
                .collect::<Vec<String>>()
                .join(", ")
        )
    }
}

impl From<Gpus> for DeviceStatuses {
    fn from(gpus: Gpus) -> DeviceStatuses {
        let mut statuses = HashMap::new();
        // Default status for each GPU is Unavailable
        let nvml = Gpu::nvml().expect("Failed to initialize NVML");
        let device_count = nvml.device_count().expect("Failed to get device count");

        // Hashmap of gpu names to count
        let mut selected_gpu_names: HashMap<String, u32> = HashMap::new();
        for gpu_name in gpus.0.values() {
            *selected_gpu_names.entry(gpu_name.0.clone()).or_insert(0) += 1;
        }

        for i in 0..device_count {
            let device = nvml
                .device_by_index(i)
                .expect("Failed to get device by index");
            let name = device.name().expect("Failed to get device name");
            let uuid = device.uuid().expect("Failed to get UUID");

            if selected_gpu_names.contains_key(&name) {
                statuses.insert(
                    GpuId::new(uuid),
                    WorkerMachineStatus::Unavailable, // Default status
                );
                // Decrement the count for this GPU name
                if let Some(count) = selected_gpu_names.get_mut(&name) {
                    *count -= 1;
                    // If count reaches zero, remove the entry
                    if *count == 0 {
                        selected_gpu_names.remove(&name);
                    }
                }
            }
        }

        DeviceStatuses(statuses)
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

#[derive(Clone, Serialize, Deserialize, Default)]
pub struct WorkerMachine {
    pub id: WorkerMachineId,
    pub gpus: Gpus,
    pub admin_id: WorkerAdminId,
    pub status: WorkerMachineStatus,

    // Maps device index to available/unavailable status
    pub device_statuses: DeviceStatuses,
}

impl WorkerMachine {
    pub fn new(
        id: WorkerMachineId,
        gpus: Gpus,
        admin_id: WorkerAdminId,
        status: WorkerMachineStatus,
    ) -> Self {
        WorkerMachine {
            id,
            gpus: gpus.clone(),
            admin_id,
            status,
            #[cfg(not(target_os = "macos"))]
            device_statuses: DeviceStatuses::from(gpus.clone()),
            #[cfg(target_os = "macos")]
            device_statuses: DeviceStatuses::new(HashMap::new()),
        }
    }
}

// The following types are defined here on purpose even though
// similar types are defined in thava_types. This decision
// was made to avoid unnecessary newtypes to avoid the orphan
// rule when implementing StringValidator and other external traits
// for the CLI tool.

/// User name.
#[derive(Debug, Display, Clone, Serialize, Deserialize, AsRef)]
pub struct Name(String);

#[derive(Debug, Error, Clone)]
#[error("Name cannot be empty. Please try again.")]
pub struct NameError;

impl From<Name> for String {
    fn from(name: Name) -> String {
        name.0
    }
}

/// User email.
#[derive(Debug, Display, Clone, Serialize, Deserialize)]
pub struct Email(String);

impl From<Email> for String {
    fn from(email: Email) -> String {
        email.0
    }
}

#[derive(Debug, Error, Clone)]
#[error("Invalid email. Please try again.")]
pub struct EmailError;

#[derive(Debug, Error, Clone, Display, Deref)]
pub struct Password(String);

#[derive(Debug, Error, Clone)]
pub enum PasswordError {
    #[error("Password cannot be empty. Please try again.")]
    Empty,
}

/// GPU handle.
#[derive(Debug, Clone, Serialize, Deserialize, Hash, Eq, PartialEq)]
pub struct Gpu(u32);

#[derive(Debug, Error, Clone)]
pub enum GpuError {
    #[error("NVIDIA initialization failed.")]
    NvmlInit,
    #[error("Invalid GPU selection. Please try again.")]
    Invalid,
    #[error("No GPUs found. Please make sure you have a compatible GPU installed.")]
    NotFound,
}

impl Name {
    /// Create a new Name instance with the specified name. Returns error if empty.
    pub fn new(name: &str) -> Result<Self> {
        if name.is_empty() {
            bail!(NameError);
        }
        Ok(Name(name.to_string()))
    }
}

impl Email {
    /// Create a new Email instance with the specified email. Returns error if invalid.
    pub fn new(email: &str) -> Result<Self> {
        if ValidateEmail::validate_email(&email) {
            Ok(Email(email.to_string()))
        } else {
            bail!(EmailError);
        }
    }
}

impl Password {
    /// Create a new Password instance with the specified password. Returns error if invalid.
    pub fn new(password: &str) -> Result<Self> {
        if password.is_empty() {
            bail!(PasswordError::Empty);
        }
        Ok(Password(password.to_string()))
    }
}

impl Gpu {
    fn new(handle: u32) -> Result<Self> {
        Ok(Gpu(handle))
    }

    /// Get the UUIDs of all GPUs on the machine
    pub fn uuids() -> Result<Vec<String>> {
        let nvml = Gpu::nvml()?;
        let devices = nvml.device_count()?;
        if devices == 0 {
            bail!(GpuError::NotFound);
        }

        let mut uuids = Vec::new();
        for i in 0..devices {
            let device = nvml.device_by_index(i)?;
            let uuid = device.uuid()?;
            uuids.push(uuid);
        }
        Ok(uuids)
    }

    /// Get the name of the GPU.
    fn name(&self) -> Result<GpuName> {
        let nvml = Gpu::nvml()?;
        let device = match nvml.device_by_index(self.0) {
            Ok(device) => device,
            Err(_) => bail!(GpuError::Invalid),
        };
        let name = match device.name() {
            Ok(name) => GpuName(name),
            Err(_) => bail!(GpuError::Invalid),
        };
        Ok(name)
    }

    /// Get a list of available GPU handles.
    fn handles() -> Result<Vec<Gpu>> {
        let nvml = Gpu::nvml()?;
        let gpus = nvml.device_count();
        if gpus.is_err() {
            bail!(GpuError::Invalid);
        }
        let gpus = gpus?;
        if gpus == 0 {
            bail!(GpuError::NotFound);
        }

        Ok((0..gpus)
            .collect::<Vec<u32>>()
            .iter()
            .map(|&handle| Gpu::new(handle).unwrap())
            .collect())
    }

    /// Get a list of available GPU names.
    fn names() -> Result<Vec<GpuName>> {
        let gpus = Gpu::handles()?;
        let names = gpus
            .iter()
            .map(|gpu| gpu.name())
            .collect::<Result<Vec<GpuName>>>();
        match names {
            Ok(names) => Ok(names),
            Err(_) => bail!(GpuError::Invalid),
        }
    }

    /// Initialize the NVIDIA Management Library.
    fn nvml() -> Result<Nvml> {
        let mut nvml = Nvml::init();
        // If the default path fails, try WSL default path. See #51 in nvml-wrapper.
        if nvml.is_err() {
            nvml = Nvml::builder()
                .lib_path("libnvidia-ml.so.1".as_ref())
                .init();
        }
        match nvml {
            Ok(nvml) => Ok(nvml),
            Err(_) => bail!(GpuError::NvmlInit),
        }
    }
}

/// Display the GPU handle and name.
impl fmt::Display for Gpu {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{} - {}", self.0, self.name().unwrap())
    }
}

// Validation traits for user input
#[derive(Clone)]
struct NameValidator;
impl StringValidator for NameValidator {
    fn validate(
        &self,
        value: &str,
    ) -> result::Result<Validation, Box<dyn error::Error + Send + Sync>> {
        let name = Name::new(value);
        match name {
            Ok(_) => Ok(Validation::Valid),
            Err(e) => Ok(Validation::Invalid(e.to_string().into())),
        }
    }
}

#[derive(Clone)]
struct EmailValidator;
impl StringValidator for EmailValidator {
    fn validate(
        &self,
        value: &str,
    ) -> result::Result<Validation, Box<dyn error::Error + Send + Sync>> {
        let email = Email::new(value);
        let email = match email {
            Ok(email) => email,
            Err(e) => return Ok(Validation::Invalid(e.to_string().into())),
        };

        let worker_admin: Result<Option<WorkerAdmin>> = futures::executor::block_on(async move {
            let mut worker_admin_endpoint = WorkerAdminEndpoint::new().await?;
            let worker_admin = worker_admin_endpoint
                .get_worker_admin_by_email(email)
                .await?;
            Ok(worker_admin)
        });

        match worker_admin {
            Ok(Some(_)) => Ok(Validation::Invalid("Email already in use.".into())),
            Ok(None) => Ok(Validation::Valid),
            Err(e) => Ok(Validation::Invalid(e.to_string().into())),
        }
    }
}

#[derive(Clone)]
struct PasswordValidator;
impl StringValidator for PasswordValidator {
    fn validate(
        &self,
        value: &str,
    ) -> result::Result<Validation, Box<dyn error::Error + Send + Sync>> {
        let password = Password::new(value);
        match password {
            Ok(_) => Ok(Validation::Valid),
            Err(e) => Ok(Validation::Invalid(e.to_string().into())),
        }
    }
}

/// Prompt the user for their name
fn name() -> Result<Name> {
    let name = Text::new("Name:").with_validator(NameValidator).prompt();
    match name {
        Ok(name) => Ok(Name::new(&name)?),
        Err(_) => {
            bail!(NameError)
        }
    }
}

/// Prompt the user for their email
fn email() -> Result<Email> {
    let email = Text::new("Email:").with_validator(EmailValidator).prompt();
    match email {
        Ok(email) => Ok(Email::new(&email)?),
        Err(_) => bail!(EmailError),
    }
}

/// Prompt the user for a password
fn password() -> Result<Password> {
    let password = inquire::Password::new("Password:")
        .with_display_mode(inquire::PasswordDisplayMode::Masked)
        .with_validator(PasswordValidator)
        .prompt();
    match password {
        Ok(password) => Ok(Password::new(&password)?),
        Err(_) => bail!(PasswordError::Empty),
    }
}

/// Prompt the user to select GPUs from available devices
fn get_selected_gpus() -> Result<Vec<String>> {
    #[cfg(not(target_os = "macos"))]
    let names = Gpu::names()?;

    #[cfg(target_os = "macos")]
    let names = Gpus::get_mac_gpus_vec();

    let names_with_index_prefix: Vec<String> = names
        .iter()
        .enumerate()
        .map(|(i, gpu)| format!("{} - {}", i, gpu.0))
        .collect();

    let selected_gpus = MultiSelect::new("Select GPUs:", names_with_index_prefix)
        .with_all_selected_by_default()
        .prompt()?;

    // Take the part of the string after the dash with the GPU name
    let selected_gpus: Vec<String> = selected_gpus
        .iter()
        .map(|gpu| String::from(gpu.split(" - ").nth(1).unwrap()))
        .collect();

    Ok(selected_gpus)
}

#[derive(Display)]
enum InitOption {
    #[display(fmt = "Register/Login as a different worker admin")]
    RegisterWorkerAdmin,
    #[display(fmt = "Modify/register your device as a worker machine")]
    RegisterWorkerMachine,
    #[display(fmt = "Exit")]
    Exit,
}

async fn check_distributor_exists() -> Result<()> {
    match WorkerAdminEndpoint::new().await {
        Ok(_) => Ok(()),
        Err(e) => Err(e),
    }
}

fn is_worker_admin_logged_in() -> Result<InitOption> {
    if config::check_config_exists()? {
        let existing_config = config::load_config()?;
        let email = existing_config.email.clone();
        let name = existing_config.name.clone();
        println!("You are currently logged in as {name} with the email: {email}.");

        let options = vec![
            InitOption::RegisterWorkerAdmin,
            InitOption::RegisterWorkerMachine,
            InitOption::Exit,
        ];
        let continue_option = Select::new("Select an option to continue:", options).prompt()?;
        return Ok(continue_option);
    }
    Ok(InitOption::RegisterWorkerAdmin)
}

/// Initialize as a thava worker admin, prompting the user for their name and email
/// and saving the configuration to a file.
async fn init_worker_admin() -> Result<Config> {
    println!("Let's register you as a worker admin!");
    let mut worker_admin_endpoint = WorkerAdminEndpoint::new().await?;

    println!("\nEnter personal information:");

    let name = name()?;
    let email = email()?;

    let password = password()?;

    let (uid, password_hash) = worker_admin_endpoint
        .create_worker_admin(name.clone(), email.clone(), password)
        .await?;

    let (config, config_path) = config::config_worker_admin(uid, name, email, password_hash)?;

    println!(
        "\nThank you! You are now registered as a worker admin, \
        with configuration saved to {config_path}."
    );
    Ok(config)
}

/// Initialize as a thava worker, prompting the user for compute limits
async fn init_worker_machine(mut config: Config) -> Result<Config> {
    println!("\nChoose compute limits:");

    let gpus = get_selected_gpus()?;

    {
        println!(
            "\nThank you for registering your device as a Caravan worker! \
            You can start work by running `caravan start`."
        );
        println!();
        println!("GPUs:");

        gpus.iter().for_each(|gpu| {
            println!("{gpu}");
        });
    }

    let gpus = Gpus::new(
        gpus.into_iter()
            .enumerate()
            .map(|(i, name)| (GpuId::new(i.to_string()), GpuName::new(name)))
            .collect(),
    );

    #[cfg(not(target_os = "macos"))]
    let device_statuses = DeviceStatuses::from(gpus.clone());

    #[cfg(target_os = "macos")]
    let device_statuses = Gpus::get_mac_gpus_statuses();

    let worker_admin_id = WorkerAdminId::new(config.id.clone());
    let worker_machine_status = WorkerMachineStatus::Unavailable;

    let mut worker_machine_client = WorkerMachineEndpoint::new_with_auth().await?;
    let worker_machine_id = worker_machine_client
        .create_worker_machine(
            gpus.clone(),
            worker_admin_id.clone(),
            worker_machine_status.clone(),
            device_statuses.clone(),
        )
        .await?;

    config.worker_machine = WorkerMachine::new(
        WorkerMachineId::new(worker_machine_id),
        gpus,
        worker_admin_id,
        worker_machine_status,
    );

    config::store_config(config.clone())?;

    Ok(config)
}

/// Initializes the user as a worker admin and optionally the device as a worker.
pub async fn init() -> Result<Config> {
    // If distributor is not online, user cannot register anything.
    check_distributor_exists().await?;

    println!("Welcome to Caravan!\n");

    // If config exists, user can log in again or add a worker machine.
    let mut worker_admin_config = match is_worker_admin_logged_in()? {
        InitOption::RegisterWorkerAdmin => init_worker_admin().await?,
        InitOption::RegisterWorkerMachine => {
            let config = config::load_config()?;
            return init_worker_machine(config).await;
        }
        InitOption::Exit => return Err(anyhow::anyhow!("Initialization cancelled.")),
    };

    // let mut worker_admin_config = init_worker_admin().await?;

    println!();

    let should_init_worker =
        Confirm::new("Would you like to register your device as a worker as well?")
            .with_default(true)
            .prompt()?;
    if !should_init_worker {
        return Ok(worker_admin_config);
    }

    // TODO: Currently the worker is first saved then worker is saved in the
    // same config again. Should change to building config and saving it once.
    worker_admin_config = init_worker_machine(worker_admin_config).await?;

    Ok(worker_admin_config)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_name() {
        let empty_name = Name::new("");
        assert!(empty_name.is_err());

        let valid_name = Name::new("test");
        assert!(valid_name.is_ok());
    }

    #[test]
    fn test_email() {
        let empty_email = Email::new("");
        assert!(empty_email.is_err());

        let no_at_email = Email::new("test");
        assert!(no_at_email.is_err());

        let no_domain_email = Email::new("test@");
        assert!(no_domain_email.is_err());

        let valid_email = Email::new("name@domain");
        assert!(valid_email.is_ok());
    }

    #[test]
    fn test_gpus() {
        let gpus = Gpu::handles();
        assert!(gpus.is_ok());

        let names = Gpu::names();
        assert!(names.is_ok());
    }
}
