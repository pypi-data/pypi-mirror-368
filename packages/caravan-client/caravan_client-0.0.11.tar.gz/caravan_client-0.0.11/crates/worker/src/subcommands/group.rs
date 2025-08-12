pub mod list;

use crate::config;
use crate::endpoints::worker_group_endpoint::WorkerGroupEndpoint;

use anyhow::Result;
use tonic::Status;

pub async fn create(name: &str) -> Result<()> {
    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    match worker_group_endpoint.create_group(name).await {
        Ok(_) => {
            println!("Worker group \"{name}\" created successfully");
        }
        Err(e) => {
            println!(
                "Error creating worker group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}

pub async fn delete(name: &str) -> Result<()> {
    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    match worker_group_endpoint.delete_group(name).await {
        Ok(_) => {
            println!("Worker group deleted successfully");
        }
        Err(e) => {
            println!(
                "Error deleting worker group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}

pub async fn add_machine(group_name: &str) -> Result<()> {
    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    let config = config::load_config()?;
    let machine_id = config.worker_machine.id;

    match worker_group_endpoint
        .add_worker_machine(group_name, machine_id.into())
        .await
    {
        Ok(_) => {
            println!("Worker machine added to group successfully");
        }
        Err(e) => {
            println!(
                "Error adding worker machine to group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}

pub async fn remove_machine(group_name: &str) -> Result<()> {
    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    let config = config::load_config()?;
    let machine_id = config.worker_machine.id;

    match worker_group_endpoint
        .remove_worker_machine(group_name, machine_id.into())
        .await
    {
        Ok(_) => {
            println!("Worker machine removed from group successfully");
        }
        Err(e) => {
            println!(
                "Error removing worker machine from group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}
