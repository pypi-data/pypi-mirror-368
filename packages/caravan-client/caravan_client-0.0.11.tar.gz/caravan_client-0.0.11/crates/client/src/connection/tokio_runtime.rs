use anyhow::Result;

use pyo3::exceptions::PyException;

use tokio::runtime::Runtime;

use pyo3::prelude::*;

use std::sync::OnceLock;

pub fn tokio() -> &'static Runtime {
    static TOKIO: OnceLock<Runtime> = OnceLock::new();
    TOKIO.get_or_init(|| Runtime::new().unwrap())
}

async fn send_messages() -> Result<()> {
    // let mut client = Client::new().await?;
    // client.start_client().await?;
    Ok(())
}

#[pyfunction]
pub fn start() -> PyResult<()> {
    match tokio().block_on(send_messages()) {
        Ok(_) => {}
        Err(e) => {
            return Err(PyException::new_err(format!("Failed to start client: {e}")));
        }
    }
    Ok(())
}
