pub mod config;
pub mod connection;
pub mod endpoints;
pub mod gpu_monitoring;
pub mod subcommands;

use anyhow::Result;
use dotenv::dotenv;
use pyo3::prelude::*;
use std::env;
use tracing_subscriber::fmt::format::FmtSpan;

use crate::subcommands::{client, group, init, start};
use clap::{Args, Parser, Subcommand};

/// Caravan Worker
#[derive(Parser)]
#[command(version, about, long_about = None)]
struct App {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Register/login as worker admin and optionally register this device as a worker machine
    Init,
    /// Handle worker groups
    Group {
        #[command(subcommand)]
        group: Group,
    },
    /// Start the worker machine
    Start,

    /// Add or remove worker machines from a group
    Machine {
        /// Name of worker group
        #[arg(required = true, long, short)]
        group: Option<String>,
        /// Handle worker machines
        #[command(subcommand)]
        machine: Machine,
    },

    /// Add or remove clients from a group
    Client {
        #[command(subcommand)]
        operation: Client,
        /// Name of worker group
        #[arg(required = true, long, short)]
        group: Option<String>,
        /// List of client emails
        #[arg(required = true, long, short)]
        clients: Option<Vec<String>>,
    },
}

#[derive(Debug, Clone, Subcommand)]
enum Client {
    /// Add clients to group
    Add,
    /// Remove clients from group
    Remove,
}

#[derive(Debug, Clone, Subcommand)]
enum Group {
    /// Create a new worker group
    Create(Create),
    /// List all worker groups
    List,
    /// Delete a worker group
    Delete(Delete),
}

#[derive(Debug, Clone, Args)]
struct Create {
    /// Name of worker group
    name: String,
}

#[derive(Debug, Clone, Args)]
struct Delete {
    /// Name of worker group
    name: String,
}

#[derive(Debug, Clone, Subcommand)]
enum Machine {
    /// Add worker machine to group
    Add,
    /// Remove worker machine from group
    Remove,
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();

    let subscriber = tracing_subscriber::fmt()
        .compact()
        .with_file(true)
        .with_line_number(true)
        .with_target(false)
        .with_span_events(FmtSpan::ACTIVE)
        // .without_time()
        .finish();

    if let Ok(log_level) = env::var("LOG_LEVEL") {
        if log_level.to_lowercase() == "info" {
            tracing::subscriber::set_global_default(subscriber)?;
        }
    }

    Python::with_gil(|py| {
        let sys = py.import("sys")?;
        let path = sys.getattr("path")?;
        let site_packages = env::var("WVENV_SITE_PACKAGES")?;
        path.call_method1("append", (site_packages,))?;

        py.import("rtorch")?;
        Ok::<(), anyhow::Error>(())
    })?;

    /*
     * Parse command line arguments
     */
    let args = App::parse();

    /*
     * Execute the command depending on the arguments
     */
    match args.command {
        Command::Init => match init::init().await {
            Ok(_) => {}
            Err(e) => {
                eprintln!("{e}");
            }
        },
        Command::Start => match start::start().await {
            Ok(_) => {}
            Err(e) => {
                eprintln!("{e}");
            }
        },
        Command::Group { group } => match group {
            Group::Create(Create { name }) => {
                group::create(&name).await?;
            }
            Group::List => group::list::list().await?,
            Group::Delete(Delete { name }) => group::delete(&name).await?,
        },
        Command::Machine { group, machine } => match machine {
            Machine::Add => {
                if let Some(group) = group {
                    group::add_machine(&group).await?;
                } else {
                    eprintln!("Group name not provided");
                }
            }
            Machine::Remove => {
                if let Some(group) = group {
                    group::remove_machine(&group).await?;
                } else {
                    eprintln!("Group name not provided");
                }
            }
        },
        Command::Client {
            operation,
            group,
            clients,
        } => match operation {
            Client::Add => {
                if let Some(group) = group {
                    client::add_clients(&group, &(clients.unwrap())).await?;
                } else {
                    eprintln!("Group name not provided");
                }
            }
            Client::Remove => {
                if let Some(group) = group {
                    client::remove_clients(&group, &(clients.unwrap())).await?;
                } else {
                    eprintln!("Group name not provided");
                }
            }
        },
    }

    Ok(())
}
