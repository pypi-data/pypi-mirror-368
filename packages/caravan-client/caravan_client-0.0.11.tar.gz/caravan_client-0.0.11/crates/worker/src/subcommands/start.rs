use std::process::exit;

use super::super::endpoints::worker_machine_endpoint::WorkerMachineEndpoint;
use crate::gpu_monitoring;
use crate::gpu_monitoring::Activate;

use anyhow::Result;

use tracing::info;

#[cfg(target_os = "macos")]
type LocalGpuMonitor = gpu_monitoring::AppleGpuMonitor;

#[cfg(not(target_os = "macos"))]
type LocalGpuMonitor = gpu_monitoring::NvidiaGpuMonitor;

// Start the worker machine
pub async fn start() -> Result<()> {
    // If user kills application, deactivate appropriately
    ctrlc::set_handler(move || {
        let _ = tokio::runtime::Runtime::new()
            .unwrap()
            .block_on(LocalGpuMonitor::deactivate_monitor_gpu());
        exit(0);
    })
    .expect("Error setting Ctrl-C handler");

    // Start the GPU monitoring task
    // Runs gpu_monitoring::activate_monitor_gpu()
    let gpu_monitoring_task = tokio::spawn(LocalGpuMonitor::activate_monitor_gpu());

    // Register the worker machine as available and has two topics, one to subscribe to
    // and one to publish to.
    let mut worker_machine_endpoint = WorkerMachineEndpoint::new_with_auth().await?;

    let _all_connections = match worker_machine_endpoint.negotiate_peer_connection().await {
        Ok(all_connections) => all_connections,
        Err(e) => {
            info!("Error: {:?}", e);
            return Err(e);
        }
    };

    info!("All connections received");

    let _ = gpu_monitoring_task
        .await
        .expect("GPU monitoring task failed");

    Ok(())
}
