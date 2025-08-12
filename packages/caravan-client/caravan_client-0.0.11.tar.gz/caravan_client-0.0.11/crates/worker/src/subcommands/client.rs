use crate::endpoints::worker_group_endpoint::WorkerGroupEndpoint;
use crate::subcommands::init::Email;
use anyhow::Result;
use tonic::Status;

pub async fn remove_clients(group_name: &str, emails: &[String]) -> Result<()> {
    let emails = emails
        .iter()
        .map(|email| match Email::new(email) {
            Ok(email) => Ok(email),
            Err(_) => Err(anyhow::anyhow!("Invalid email: {}", email)),
        })
        .collect::<Result<Vec<Email>>>()?;

    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    println!("Removing clients from group");

    match worker_group_endpoint
        .remove_clients_from_group(group_name, emails)
        .await
    {
        Ok(_) => {
            println!("Clients removed from group successfully");
        }
        Err(e) => {
            println!(
                "Error removing clients to group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}

pub async fn add_clients(group_name: &str, emails: &[String]) -> Result<()> {
    let emails = emails
        .iter()
        .map(|email| match Email::new(email) {
            Ok(email) => Ok(email),
            Err(_) => Err(anyhow::anyhow!("Invalid email: {}", email)),
        })
        .collect::<Result<Vec<Email>>>()?;

    let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;

    println!("Adding clients to group");

    match worker_group_endpoint
        .add_clients_to_group(group_name, emails)
        .await
    {
        Ok(response) => {
            response.keys.iter().for_each(|(email, key)| {
                println!("Client Email: {email}, Key: {key}");
            });
            println!("Clients added to group successfully");
        }
        Err(e) => {
            println!(
                "Error adding clients to group: {:?}",
                e.downcast::<Status>().unwrap().message()
            );
            println!("Please try again.");
        }
    }

    Ok(())
}
