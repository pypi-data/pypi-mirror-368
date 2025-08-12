use pyo3::{exceptions::PyTypeError, prelude::*};
use tracing::info;

use crate::biject::message::{create_pymessage, PyMessage};

/// The reason this remote call has to be wrapped in a struct is twofold:
/// 1. We want to be able to generically pass in remote calls to the biject function while
///    handling the async part consistently regardless of the remote_call implementation.
///    `__call__` allows us to add this functionality before calling `remote_call`.
/// 2. We are typically calling `biject` (a Python function) from Rust with a Rust function
///    pointer. To do this, we follow the PyO3 docs (as of Jul 25, 2025):
///    https://pyo3.rs/v0.25.1/function.html#calling-rust-functions-in-python which recommend
///    the option of using an enclosing struct with `__call__` implemented.
#[pyclass]
pub struct RemoteCall {
    pub remote_call: fn(PyMessage, i32) -> PyResult<Vec<u8>>,
}

#[pymethods]
impl RemoteCall {
    fn __call__(&self, fn_request: Py<PyAny>, device: i32) -> PyResult<Vec<u8>> {
        let message = create_pymessage(fn_request)
            .map_err(|e| PyTypeError::new_err(format!("Could not send function request: {e}")));

        let message = match message {
            Ok(message) => message,
            Err(e) => {
                info!("Problem with sending: {e:?}");
                PyMessage {
                    payload: vec![],
                    rids: vec![],
                }
            }
        };

        (self.remote_call)(message, device)
    }
}
