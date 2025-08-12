use crate::{
    biject::payload::{generate_future_rids, parse_fn_request},
    uid::Uid,
};
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;

use anyhow::Result;
use tracing::{info, instrument};

#[derive(Clone)]
#[pyclass]
pub struct PyMessage {
    pub payload: Vec<u8>,
    pub rids: Vec<Uid>,
}

#[instrument(skip_all)]
pub fn create_pymessage(fn_request: Py<PyAny>) -> Result<PyMessage> {
    let mut fn_request = Python::with_gil(|py| {
        let fn_request = fn_request.bind(py);
        parse_fn_request(&fn_request)
            .map_err(|e| PyTypeError::new_err(format!("Error parsing function request: {e}")))
    })?;

    let rids = generate_future_rids(&fn_request.return_types);
    fn_request.rids = rids.clone().into();

    info!("fn_request: {:?}", fn_request);

    let payload = fn_request
        .to_vec()
        .map_err(|e| PyTypeError::new_err(format!("Could not serialize function request: {e}")))?;

    let message = PyMessage { payload, rids };

    Ok(message)
}
