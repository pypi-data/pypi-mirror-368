use super::subcommands::init::{Email, Name, WorkerMachine};

use thava_types::uid::Uid;

use std::path::Path;

use anyhow::Result;

use serde::{Deserialize, Serialize};

use confy;

#[derive(Clone, Serialize, Deserialize)]
pub struct Config {
    pub id: Uid,
    pub name: Name,
    pub email: Email,
    pub auth_key: String,
    pub worker_machine: WorkerMachine,
}

impl Config {
    fn new(id: Uid, name: Name, email: Email, auth_key: String) -> Self {
        Config {
            id,
            name,
            email,
            auth_key,
            worker_machine: WorkerMachine::default(),
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Config {
            id: 0.into(),
            name: Name::new("<name>").unwrap(),
            email: Email::new("<email>@<domain>").unwrap(),
            auth_key: "".to_string(),
            worker_machine: WorkerMachine::default(),
        }
    }
}

/// Prompt the user for the configuration path and save the configuration to a file.
pub fn config_worker_admin(
    id: Uid,
    name: Name,
    email: Email,
    password_hash: String,
) -> Result<(Config, String)> {
    // The following snippet is for adding different config paths in the future.
    // You will have to add an environment variable to save this and read it when
    // implementing this.
    //
    // let default_path = confy::get_configuration_file_path(app_name, config_name)?
    //     .as_os_str()
    //     .to_str()
    //     .map(|s| s.to_string())
    //     .unwrap_or("".to_string());
    // let config_path = Text::new("Configuration path:")
    //     .with_default(&default_path)
    //     .prompt()?;
    // let mut config: Config = confy::load_path(&config_path)?;
    // config.name = name;
    // config.email = email;
    // confy::store_path(&config_path, config.clone())?;

    let config = Config::new(id, name, email, password_hash);

    store_config(config.clone())?;

    let config_path = config_path()?;

    Ok((config, config_path))
}

/// Stores worker admin config. Location defaults to ~/.config/thava/thava.toml
pub fn store_config(config: Config) -> Result<()> {
    let app_name = app_name();
    let config_name = config_name();
    confy::store(&app_name, config_name.as_str(), config)?;
    Ok(())
}

pub fn load_config() -> Result<Config> {
    if !check_config_exists()? {
        return Err(anyhow::anyhow!(
            "Config does not exist. Please run `caravan init` to create a new config."
        ));
    }
    let app_name = app_name();
    let config_name = config_name();
    let config = confy::load(&app_name, config_name.as_str())?;
    Ok(config)
}

pub fn config_path() -> Result<String> {
    let app_name = app_name();
    let config_name = config_name();
    let config_path = confy::get_configuration_file_path(&app_name, config_name.as_str())?
        .as_os_str()
        .to_str()
        .map(|s| s.to_string())
        .unwrap_or("".to_string());
    Ok(config_path)
}

pub fn app_name() -> String {
    "caravan".to_string()
}

pub fn config_name() -> String {
    "caravan".to_string()
}

pub fn check_config_exists() -> Result<bool> {
    let config_path = config_path()?;
    let config_exists = Path::new(&config_path).exists();
    Ok(config_exists)
}
