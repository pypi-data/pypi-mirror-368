use crate::pycaravan::init::Caravan;
use thava_types::rtorch::RemoteCall;

use tracing::info;

use pyo3::prelude::{pymodule, wrap_pyfunction, Bound, PyErr, PyModule, PyModuleMethods, PyResult};

/// Sets up tracing logs for the Python client
/// If the environment variable `CARAVANCLOUD_LOG` is set to 1, then logs will be enabled
fn setup_logs() -> PyResult<()> {
    let subscriber = tracing_subscriber::fmt()
        .compact()
        .with_file(true)
        .with_line_number(true)
        .with_target(false)
        .finish();

    if let Ok(should_log) = std::env::var("CARAVANCLOUD_LOG") {
        let should_log = should_log.parse::<i64>().unwrap();
        println!("should_log: {should_log}");
        if should_log == 1 {
            tracing::subscriber::set_global_default(subscriber)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(format!("{e}")))?;
            info!("Logging enabled");
        }
    }

    Ok(())
}

/// Full `caravancloud` module for client-side Python library (user-facing)
#[pymodule]
fn caravan(m: &Bound<'_, PyModule>) -> PyResult<()> {
    setup_logs()?;

    m.add_class::<Caravan>()?;
    m.add_class::<RemoteCall>()?;
    m.add_function(wrap_pyfunction!(crate::pycaravan::init::remote_call, m)?)?;
    Ok(())
}
