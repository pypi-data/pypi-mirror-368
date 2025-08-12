use std::io::Read;
use std::process::Command;
use std::str;

use crate::config;
use crate::endpoints::worker_machine_endpoint::WorkerMachineEndpoint;
use crate::subcommands::init;
use thava_types::worker_machine::WorkerMachineStatus;

use thiserror::Error;
use tracing::info;

use async_trait::async_trait;

use nvml_wrapper::Nvml;
use once_cell::sync::Lazy;

use crate::subcommands::init::{DeviceStatuses, GpuId};
use std::collections::HashMap;

use anyhow::bail;

/// Time period in seconds to check GPU utilization and update remote status.
const GPU_MONITOR_TIME_PERIOD_SEC: u64 = 2;

/// Threshold for GPU utilization to determine if the worker machine is available or not.
const GPU_UTILIZATION_THRESHOLD: f64 = 40.0;

static NVML: Lazy<Nvml> = Lazy::new(|| match Nvml::init() {
    Ok(nvml) => nvml,
    Err(e) => Nvml::builder()
        .lib_path("libnvidia-ml.so.1".as_ref())
        .init()
        .expect("Failed to initialize NVML"),
});

/*
 * Adding type definitions here but can be moved to thava_types crate
*/

/// Represents the utilization of a GPU as a percentage.
#[derive(Copy, Clone, Debug, PartialEq, PartialOrd)]
struct GpuUtilization(f64);

/// Implementations for GpuUtilization
impl GpuUtilization {
    pub fn new(utilization: f64) -> GpuUtilization {
        GpuUtilization(utilization)
    }
}

impl From<GpuUtilization> for f64 {
    fn from(utilization: GpuUtilization) -> f64 {
        utilization.0
    }
}

impl From<f64> for GpuUtilization {
    fn from(utilization: f64) -> GpuUtilization {
        GpuUtilization::new(utilization)
    }
}

/// Error type for GPU monitoring.
#[derive(Debug, Error)]
pub enum GpuMonitoringError {
    #[error("Failed to get GPU utilization")]
    GetGpuUtilizationError,
    #[error("Failed to update remote GPU status")]
    UpdateRemoteGpuStatusError,
    #[error("Failed to get current remote GPU status")]
    GetRemoteGpuStatusError,
}

// Default implementation for a GpuMonitor
// #[derive(Default)]
// pub struct GpuMonitor;

// Implementation for Apple silicon Gpus
pub struct AppleGpuMonitor;

// Implementation for NVIDIA Gpus
pub struct NvidiaGpuMonitor;

// Trait to fetch GPU utilization, can be implemented depending on the platform
// Private
trait Utilization {
    /// Returns current GPU utilization of the system as a percentage.
    fn get_gpu_utilization() -> Result<GpuUtilization, GpuMonitoringError>;

    /// Returns current GPU utilization of all GPUs in the system as a vector of GpuUtilization.
    fn get_all_gpu_utilization() -> Result<HashMap<GpuId, GpuUtilization>, GpuMonitoringError> {
        Err(GpuMonitoringError::GetGpuUtilizationError)
    }
}

// Describes behavior of a GpuMonitor
#[async_trait]
trait Monitor: Utilization {
    /// Monitor the GPU utilization and update the remote database with the status.
    /// This function will run indefinitely in a separate thread.
    async fn monitor_gpu() -> Result<(), GpuMonitoringError> {
        let mut count = 0;
        loop {
            if count >= 5 {
                println!("Stopping GPU monitoring after 5 iterations");
                panic!();
            }
            // Get the current GPU utilization
            let device_utilizations = Self::get_all_gpu_utilization()?;

            // Update remote status if changed
            Self::update_remote_gpu_device_statuses(device_utilizations).await?;

            // Sleep for 2 seconds before checking again
            tokio::time::sleep(std::time::Duration::from_secs(GPU_MONITOR_TIME_PERIOD_SEC)).await;
            count += 1;
        }
    }

    /// With a given GPU utilization, update the remote database with the status.
    async fn update_remote_gpu_device_statuses(
        device_utilizations: HashMap<GpuId, GpuUtilization>,
    ) -> Result<(), GpuMonitoringError> {
        // Figure out new status
        let mut new_statuses: DeviceStatuses =
            Self::evaluate_gpu_device_statuses(device_utilizations);

        // Only update if status has changed, check local
        let cached_device_statuses: DeviceStatuses = match Self::get_local_gpu_device_statuses() {
            Ok(status) => status,
            Err(_) => {
                return Err(GpuMonitoringError::GetRemoteGpuStatusError);
            }
        };

        // Only for testing purposes
        let _ = new_statuses
            .get_all_statuses()
            .iter_mut()
            .map(|(gpu_id, _)| {
                let cached_status = match cached_device_statuses.get(gpu_id) {
                    Some(status) => status,
                    None => {
                        info!("GPU {} not found in cached statuses", gpu_id);
                        return;
                    }
                };

                if *cached_status == WorkerMachineStatus::Unavailable {
                    info!(
                        "GPU {} status is Unavailable, setting to Available for testing",
                        gpu_id
                    );
                    new_statuses.set_status(gpu_id.clone(), WorkerMachineStatus::Available);
                } else {
                    info!(
                        "GPU {} status is Available, setting to Unavailable for testing",
                        gpu_id
                    );
                    new_statuses.set_status(gpu_id.clone(), WorkerMachineStatus::Unavailable);
                }
            });

        info!("Current remote status: {:?}", cached_device_statuses);
        if new_statuses != cached_device_statuses {
            info!(
                "New remote status for DB to be updated with: {:?}",
                new_statuses
            );
        }

        if new_statuses != cached_device_statuses {
            match Self::set_remote_gpu_device_statuses(new_statuses.clone()).await {
                Ok(_) => {
                    info!("Updated remote GPU status with status {:?}", new_statuses);
                }
                Err(_e) => {
                    info!(
                        "Error updating remote GPU status with status {:?}",
                        new_statuses
                    );
                    return Err(GpuMonitoringError::UpdateRemoteGpuStatusError);
                }
            }
        }

        Ok(())
    }

    async fn set_remote_gpu_device_statuses(device_statuses: DeviceStatuses) -> anyhow::Result<()> {
        // Update local config with new device statuses
        Self::set_local_gpu_device_statuses(device_statuses.clone())?;

        // Get local config to get worker machine id, gpu count and worker admin id
        let config = config::load_config()?;

        let id = config.worker_machine.id.clone();
        let gpus = config.worker_machine.gpus.clone();
        let worker_admin_id = init::WorkerAdminId::new(config.id);
        let status = config.worker_machine.status.clone();
        let device_statuses = config.worker_machine.device_statuses.clone();

        let mut worker_machine_endpoint = WorkerMachineEndpoint::new_with_auth().await?;

        // Update remote database with new status
        match worker_machine_endpoint
            .update_worker_machine(id, gpus, worker_admin_id, status, device_statuses)
            .await
        {
            Ok(_) => {}
            Err(e) => {
                return Err(e.into());
            }
        };

        Ok(())
    }

    /// Set remote and local config GPU status to the given status.
    async fn set_remote_gpu_status(
        device_index: u32,
        status: WorkerMachineStatus,
    ) -> anyhow::Result<()> {
        // Update local config with new status
        Self::set_local_gpu_status(device_index, status.clone())?;
        // Get local config to get worker machine id, gpu count and worker admin id
        let config = config::load_config()?;

        let id = config.worker_machine.id.clone();
        let gpus = config.worker_machine.gpus.clone();
        let worker_admin_id = init::WorkerAdminId::new(config.id);
        let status = config.worker_machine.status.clone();
        let device_statuses = config.worker_machine.device_statuses.clone(); // Map of device statuses

        let mut worker_machine_endpoint = WorkerMachineEndpoint::new_with_auth().await?;

        // Update remote database with new status
        match worker_machine_endpoint
            .update_worker_machine(id, gpus, worker_admin_id, status, device_statuses)
            .await
        {
            Ok(_) => {}
            Err(e) => {
                return Err(e.into());
            }
        };

        Ok(())
    }

    ///. Set local config GPU status to the given status.
    fn set_local_gpu_status(device_index: u32, status: WorkerMachineStatus) -> anyhow::Result<()> {
        // Update local config with new status
        let mut config = config::load_config()?;

        config
            .worker_machine
            .device_statuses
            .set_status(GpuId::from(device_index), status);

        config::store_config(config)?;

        Ok(())
    }

    /// Get the current status of the remote GPU from local config file.
    fn get_local_gpu_status(device_index: u32) -> anyhow::Result<WorkerMachineStatus> {
        // Get current status from config
        let config = config::load_config()?;

        // Index into the device_statuses part of local config
        let statuses = config.worker_machine.device_statuses;

        // Check if the device index exists in the statuses
        if let Some(status) = statuses.get_status(GpuId::from(device_index)) {
            return Ok(status.clone());
        } else {
            // If the device index does not exist, return an error
            return Err(anyhow::anyhow!(
                "Device index {} does not exist in local config",
                device_index
            ));
        }
    }

    fn get_local_gpu_device_statuses() -> anyhow::Result<DeviceStatuses> {
        let config = config::load_config()?;
        let statuses = config.worker_machine.device_statuses;
        Ok(statuses)
    }

    fn set_local_gpu_device_statuses(device_statuses: DeviceStatuses) -> anyhow::Result<()> {
        // Update local config with new status
        let mut config = config::load_config()?;
        config.worker_machine.device_statuses = device_statuses;
        config::store_config(config)?;

        Ok(())
    }

    /// Check if, based on the current GPU utilization, the worker machine should be available or not.
    /// TODO: Can be customized to have different thresholds for availability.
    fn evaluate_gpu_status(utilization: GpuUtilization) -> WorkerMachineStatus {
        if f64::from(utilization) < GPU_UTILIZATION_THRESHOLD {
            WorkerMachineStatus::Available
        } else {
            WorkerMachineStatus::Unavailable
        }
    }

    fn evaluate_gpu_device_statuses(
        device_utilizations: HashMap<GpuId, GpuUtilization>,
    ) -> DeviceStatuses {
        let mut device_statuses = DeviceStatuses::default();

        for (gpu_id, utilization) in device_utilizations {
            let status = Self::evaluate_gpu_status(utilization);
            device_statuses.set_status(gpu_id, status);
        }

        device_statuses
    }
}

// Trait to activate the GPU monitoring
// Public for access by external crates, like worker/start.rs
#[async_trait]
pub trait Activate: Monitor {
    /// Activate GPU monitoring when the 'caravan start' process is started.
    async fn activate_monitor_gpu() -> anyhow::Result<()>;

    /// Deactivate GPU monitoring when the 'caravan start' process is killed.
    /// This will set the remote GPU status to Unavailable.
    /// (Only on Apple Silicon) Will deactivate the LaunchDaemon via `launchctl unload`.
    async fn deactivate_monitor_gpu() -> anyhow::Result<()>;
}

// Default GpuMonitor gets default Utilization trait (always returns Err if unimplemented) as Monitor is a supertrait
// impl Utilization for GpuMonitor {}

// Gets GPU utilization for Apple silicon
impl Utilization for AppleGpuMonitor {
    /// Returns current GPU utilization as a percentage.
    /// Only works on macOS with Apple Silicon GPUs.
    fn get_gpu_utilization() -> Result<GpuUtilization, GpuMonitoringError> {
        // Run the `powermetrics` command to get GPU utilization
        let output = match Command::new("sh")
            .arg("-c")
            .arg(r#"sudo powermetrics --samplers gpu_power -i 1000 -n 1 | grep "GPU HW active residency" | cut -d ':' -f 2 | sed 's/%//g' | awk '{print $1}'"#)
            .output()
        {
            Ok(output) => {
                output
            },
            Err(e) => {
                eprintln!("Failed to execute command: {}", e);
                return Err(GpuMonitoringError::GetGpuUtilizationError);
            }
        };

        // Convert the output to a string
        let output_str = match String::from_utf8(output.stdout) {
            Ok(output_str) => output_str.trim().to_string(),
            Err(e) => {
                eprintln!("Failed to convert output to string: {}", e);
                return Err(GpuMonitoringError::GetGpuUtilizationError);
            }
        };

        if output_str.is_empty() {
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }

        // Convert the output to a f64
        let output = match output_str.parse::<f64>() {
            Ok(output) => output,
            Err(e) => {
                eprintln!("Failed to parse get_gpu_util_output output to f64: {}", e);
                return Err(GpuMonitoringError::GetGpuUtilizationError);
            }
        };

        // Convert to GpuUtilization
        let output = GpuUtilization::from(output);

        println!("Current GPU Utilization: {:.2}%", f64::from(output)); // This is printing but not
                                                                        // info!() ...

        info!("Current GPU Utilization: {:.2}%", f64::from(output));

        Ok(output)
    }
}

fn get_nvidia_device_memory_util(device_index: u32) -> Result<f64, GpuMonitoringError> {
    let device = match NVML.device_by_index(device_index) {
        Ok(device) => device,
        Err(e) => {
            eprintln!("Failed to get device by index {}: {}", device_index, e);
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }
    };

    // Get the memory info
    let memory_info = match device.memory_info() {
        Ok(memory_info) => memory_info,
        Err(e) => {
            eprintln!("Failed to get memory info: {}", e);
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }
    };

    // Calculate memory utilization as a percentage
    let total_memory = memory_info.total;
    let used_memory = memory_info.used;
    let memory_utilization = (used_memory as f64 / total_memory as f64) * 100.0;

    Ok(memory_utilization)
}

fn get_nvidia_device_uuid(device_index: u32) -> Result<String, GpuMonitoringError> {
    let device = match NVML.device_by_index(device_index) {
        Ok(device) => device,
        Err(e) => {
            eprintln!("Failed to get device by index {}: {}", device_index, e);
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }
    };

    // Get the UUID of the device
    let uuid = match device.uuid() {
        Ok(uuid) => uuid,
        Err(e) => {
            eprintln!("Failed to get device UUID: {}", e);
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }
    };

    Ok(uuid)
}

/// Get the UUIDs of all GPUs on the machine
fn uuids() -> anyhow::Result<Vec<String>> {
    let devices = NVML.device_count()?;
    if devices == 0 {
        eprintln!("No NVIDIA GPUs found");
        return Err(GpuMonitoringError::GetGpuUtilizationError.into());
    }

    let mut uuids = Vec::new();
    for i in 0..devices {
        let device = NVML.device_by_index(i)?;
        let uuid = device.uuid()?;
        uuids.push(uuid);
    }
    Ok(uuids)
}

// Gets GPU utilization for NVIDIA GPUs
impl Utilization for NvidiaGpuMonitor {
    /// Returns current GPU utilization as a percentage, using NVML
    fn get_gpu_utilization() -> Result<GpuUtilization, GpuMonitoringError> {
        // Check if the system has NVIDIA GPUs
        if !has_nvidia_gpu() {
            eprintln!("No NVIDIA GPUs found");
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }

        let gpu_utilization = GpuUtilization::from(get_nvidia_device_memory_util(0)?);

        info!(
            "Current GPU Utilization: {:.2}%",
            f64::from(gpu_utilization)
        );

        Ok(gpu_utilization)
    }

    fn get_all_gpu_utilization() -> Result<HashMap<GpuId, GpuUtilization>, GpuMonitoringError> {
        let device_count = match NVML.device_count() {
            Ok(count) => count,
            Err(e) => {
                eprintln!("Failed to get device count: {}", e);
                return Err(GpuMonitoringError::GetGpuUtilizationError);
            }
        };

        if device_count == 0 {
            eprintln!("No NVIDIA GPUs found");
            return Err(GpuMonitoringError::GetGpuUtilizationError);
        }

        // Get map of GPU utilization percentages
        let mut gpu_utilizations = HashMap::new();
        for i in 0..device_count {
            let uuid = get_nvidia_device_uuid(i)?;
            let device_memory_util = get_nvidia_device_memory_util(i)?;

            info!(
                "Current GPU {} memory utilization: {:.2}%",
                uuid, device_memory_util
            );

            println!(
                "Current GPU {} memory utilization: {:.2}%",
                uuid, device_memory_util
            );

            gpu_utilizations.insert(GpuId::new(uuid), GpuUtilization::from(device_memory_util));
        }
        return Ok(gpu_utilizations);
    }
}

// Default GpuMonitor gets all the platform-agnostic trait Monitor
// #[async_trait]
// impl Monitor for GpuMonitor {}

// Must be implemented b/c Activate is a supertrait of Monitor
#[async_trait]
impl Monitor for AppleGpuMonitor {}

// Must be implemented b/c Activate is a supertrait of Monitor
#[async_trait]
impl Monitor for NvidiaGpuMonitor {}

// Activates and deactivates GPU monitoring for Apple silicon
#[async_trait]
impl Activate for AppleGpuMonitor {
    async fn activate_monitor_gpu() -> anyhow::Result<()> {
        // Only for Apple Silicon
        info!("Activating GPU monitoring for Apple Silicon");
        load_launch_daemon()?;

        Ok(())
    }

    async fn deactivate_monitor_gpu() -> anyhow::Result<()> {
        // Only for Apple Silicon
        info!("Unloading GPU monitoring LaunchDaemon for Apple Silicon");
        unload_launch_daemon()?;
        cleanup_launch_daemon_fd()?;

        // Set remote GPU status to Unavailable, for all machines
        info!("Deactivating GPU monitoring for Apple Silicon");

        let mut unavailable_statuses = HashMap::new();
        for uuid in uuids().unwrap() {
            unavailable_statuses.insert(GpuId::new(uuid), WorkerMachineStatus::Unavailable);
        }

        Self::set_remote_gpu_device_statuses(DeviceStatuses::new(unavailable_statuses)).await?;

        Ok(())
    }
}

// Activates and deactivates GPU monitoring for NVIDIA GPUs
#[async_trait]
impl Activate for NvidiaGpuMonitor {
    async fn activate_monitor_gpu() -> anyhow::Result<()> {
        // For non-Apple Silicon, no need to load LaunchDaemon
        info!("Activating GPU monitoring for NVIDIA GPU");
        Self::monitor_gpu().await?;
        Ok(())
    }

    async fn deactivate_monitor_gpu() -> anyhow::Result<()> {
        info!("Deactivating GPU monitoring for NVIDIA GPU");
        // Set remote GPU status to Unavailable, for all machines

        let mut unavailable_statuses = HashMap::new();
        for uuid in uuids().unwrap() {
            unavailable_statuses.insert(GpuId::new(uuid), WorkerMachineStatus::Unavailable);
        }

        Self::set_remote_gpu_device_statuses(DeviceStatuses::new(unavailable_statuses)).await?;

        Ok(())
    }
}

/// Load the GPU monitoring LaunchDaemon for Apple Silicon.
fn load_launch_daemon() -> anyhow::Result<()> {
    let launch_daemon_path = "/Library/LaunchDaemons/cloud.thecaravan.gpu-monitoring.plist";

    // Load the LaunchDaemon
    let output = match Command::new("launchctl")
        .arg("load")
        .arg(launch_daemon_path)
        .output()
    {
        Ok(output) => output,
        Err(e) => {
            eprintln!("Failed to execute command: {}", e);
            return Err(e.into());
        }
    };

    if !output.status.success() {
        return Err(anyhow::anyhow!("Failed to load LaunchDaemon"));
    }

    Ok(())
}

/// Unload the GPU monitoring LaunchDaemon for Apple Silicon.
fn unload_launch_daemon() -> anyhow::Result<()> {
    let launch_daemon_path = "/Library/LaunchDaemons/cloud.thecaravan.gpu-monitoring.plist";

    // Unload the LaunchDaemon
    let output = Command::new("launchctl")
        .arg("unload")
        .arg(launch_daemon_path)
        .output()?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("Failed to unload LaunchDaemon"));
    }

    Ok(())
}

// Clean up file descriptors opened by LaunchDaemon (Not sure if this is necessary)
fn cleanup_launch_daemon_fd() -> anyhow::Result<()> {
    std::fs::remove_file("/tmp/cloud.thecaravan.gpu-monitoring.log")?;
    std::fs::remove_file("/tmp/cloud.thecaravan.gpu-monitoring.err")?;
    Ok(())
}

/// Checks for NVIDIA GPU (Windows/Linux)
fn has_nvidia_gpu() -> bool {
    Command::new("nvidia-smi")
        .arg("--query-gpu=name")
        .arg("--format=csv,noheader")
        .output()
        .is_ok()
}

/// Checks for Apple Silicon GPU
fn has_apple_gpu() -> bool {
    std::env::consts::ARCH == "aarch64" && std::env::consts::OS == "macos"
}

/*
 * TESTING TIP:

 * println!() calls in test functions will only show up if the test fails
 * Include a panic!() at the end of the test function so test "always fails" and to get stdout
 * printed
*/

/// Panic if the TEST_LOG environment variable is set to 1.
/// Used if you want your println!() debug calls to show up in tests even if they pass.
fn panic_on_env_var() {
    if std::env::var("TEST_LOG").is_ok() && std::env::var("TEST_LOG").unwrap() == "1" {
        panic!();
    }
}

/// Tests for GPU monitoring and utilization functions.
#[cfg(test)]
mod tests {
    use super::*;

    type LocalGpuMonitor = NvidiaGpuMonitor;

    /// Test for activating the GPU utilization monitoring.
    #[tokio::test]
    async fn test_activate_monitor_gpu() {
        let _ = LocalGpuMonitor::activate_monitor_gpu().await;

        panic_on_env_var();
    }

    // Test for monitoring
    #[tokio::test]
    async fn test_monitor_gpu() {
        let _ = LocalGpuMonitor::monitor_gpu().await;
    }

    #[test]
    fn test_gpu_utilization() {
        let utilization = GpuUtilization::new(50.0);
        assert_eq!(f64::from(utilization), 50.0);
    }

    #[test]
    fn test_evaluate_gpu_status() {
        let low_utilization = GpuUtilization::new(10.0);
        let high_utilization = GpuUtilization::new(80.0);

        assert_eq!(
            LocalGpuMonitor::evaluate_gpu_status(low_utilization),
            WorkerMachineStatus::Available
        );
        assert_eq!(
            LocalGpuMonitor::evaluate_gpu_status(high_utilization),
            WorkerMachineStatus::Unavailable
        );
    }

    /// Test setting and getting remote GPU status
    #[tokio::test]
    async fn test_set_remote_gpu_status() {
        // Example status to set
        let status = WorkerMachineStatus::Unavailable;
        let ex_device_index = 0; // Example device index
                                 // Check that the set function doesn't error
        assert!(
            LocalGpuMonitor::set_remote_gpu_status(ex_device_index, status.clone())
                .await
                .is_ok()
        );

        // Check that the set function actually set the correct value in the remote DB
        let remote_status = get_remote_gpu_status().await.unwrap();
        assert_eq!(remote_status, status);
    }

    // Helper function to get worker's status from remote DB
    async fn get_remote_gpu_status() -> anyhow::Result<WorkerMachineStatus> {
        let worker_id = get_worker_id()?;

        // Get remote status to check if it was set correctly
        let mut worker_machine_endpoint = WorkerMachineEndpoint::new_with_auth().await.unwrap();

        let remote_worker = match worker_machine_endpoint.get_worker_machine(worker_id).await {
            Ok(worker) => worker,
            Err(e) => {
                return Err(e.into());
            }
        };

        Ok(remote_worker.status.into())
    }

    // Helper function to get worker id from local config
    fn get_worker_id() -> anyhow::Result<init::WorkerMachineId> {
        let config = config::load_config()?;
        Ok(config.worker_machine.id)
    }

    /// Test for updating local config file with new GPU status.
    #[test]
    fn test_set_local_gpu_status() {
        // Example status to set
        let status = WorkerMachineStatus::Available;
        let ex_device_index = 0; // Example device index
                                 // Check that the set function doesn't error
        assert!(LocalGpuMonitor::set_local_gpu_status(ex_device_index, status.clone()).is_ok());

        // Check that the set function actually set the correct value in the config file
        let config = config::load_config().unwrap();
        assert_eq!(config.worker_machine.status, status);
    }

    /// Test for getting current GPU status from local config file.
    #[test]
    fn test_get_local_gpu_status() {
        // Example device index to get status for
        let ex_device_index = 0; // Example device index
        let call_status = LocalGpuMonitor::get_local_gpu_status(ex_device_index);
        assert!(call_status.is_ok());

        let status = call_status.unwrap();
        println!("Current GPU status: {:?}", status);

        panic_on_env_var();
    }

    /// Confirm current machine has NVIDIA GPU
    #[test]
    fn test_has_nvidia_gpu() {
        assert!(has_nvidia_gpu());
    }

    /// Confirm current machine has Apple Silicon GPU
    #[test]
    fn test_has_apple_gpu() {
        assert!(has_apple_gpu());
    }

    /// Test for getting current GPU utilization on NVIDIA GPU
    #[test]
    fn test_get_nvidia_gpu_utilization() {
        println!("Running test_get_nvidia_gpu_utilization");
        let utilization = match NvidiaGpuMonitor::get_gpu_utilization() {
            Ok(utilization) => utilization,
            Err(e) => {
                println!("Error on PANIC: {:?}", e);
                panic!();
            }
        };
        println!("GPU utilization: {:.2}%", f64::from(utilization));

        panic!();

        assert!(f64::from(utilization) >= 0.0);
        assert!(f64::from(utilization) <= 100.0);
    }

    /// Test for getting current GPU utilization on Apple Silicon
    #[test]
    fn test_get_apple_gpu_utilization() {
        println!("Running test_get_apple_gpu_utilization");
        let utilization = match AppleGpuMonitor::get_gpu_utilization() {
            Ok(utilization) => utilization,
            Err(e) => {
                println!("Error on PANIC: {:?}", e);
                panic!();
            }
        };
        println!("GPU utilization: {:.2}%", f64::from(utilization));
        info!("GPU utilization: {:.2}%", f64::from(utilization));

        assert!(f64::from(utilization) >= 0.0);
        assert!(f64::from(utilization) <= 100.0);

        panic!();
    }

    /// Test for getting all GPU utilization on NVIDIA GPUs
    #[test]
    fn test_get_all_nvidia_gpu_utilization() {
        println!("Running test_get_all_nvidia_gpu_utilization");
        let gpu_utilizations = match NvidiaGpuMonitor::get_all_gpu_utilization() {
            Ok(utilizations) => utilizations,
            Err(e) => {
                println!("Error on PANIC: {:?}", e);
                panic!();
            }
        };

        for (uuid, utilization) in gpu_utilizations.iter() {
            println!(
                "GPU {} memory utilization: {:.2}%",
                uuid,
                f64::from(*utilization)
            );
        }

        assert!(!gpu_utilizations.is_empty());
        for utilization in gpu_utilizations.values() {
            assert!(f64::from(*utilization) >= 0.0);
            assert!(f64::from(*utilization) <= 100.0);
        }

        panic!();
    }
}
