use pyo3::exceptions::{PyException, PyTypeError};
use pyo3::prelude::*;

use serde_pickle::SerOptions;
use thava_types::biject::message::PyMessage;
use tokio::runtime::Runtime;
use tracing::info;

use std::sync::OnceLock;

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

use pyo3::class::basic::CompareOp;
use pyo3::types::PyString;

use client::connection::client_endpoint;
use thava_types::rtorch::RemoteCall;
use thava_types::worker_admin::{Email, Group, Key};

// Senders to worker machines and i64 for the device index mapping
static PY_SENDERS: OnceLock<Vec<(kanal::AsyncSender<PyMessage>, i64)>> = OnceLock::new();
static MSG_RECEIVER: OnceLock<kanal::AsyncReceiver<Vec<u8>>> = OnceLock::new();

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
    m.add_function(wrap_pyfunction!(remote_call, m)?)?;
    Ok(())
}

#[pyclass]
pub struct Caravan {
    email: String,
    group: String,
    key: String,
    gpu_count: u32,
}

#[pymethods]
impl Caravan {
    #[new]
    fn new() -> Self {
        Caravan {
            email: String::from(""),
            group: String::from(""),
            key: String::from(""),
            gpu_count: 0,
        }
    }

    // Return a string that Python could use to recreate the Caravan
    fn __repr__(slf: &Bound<'_, Self>) -> PyResult<String> {
        let class_name: Bound<'_, PyString> = slf.get_type().qualname()?;
        Ok(format!("{class_name}()"))
    }

    // Return an informal representation string of Caravan
    fn __str__(&self) -> String {
        format!(
            "Caravan\nEmail: {}\nGroup: {}\nKey: {}\nGPU Count: {}",
            self.email, self.group, self.key, self.gpu_count
        )
    }

    // #[pyclass(frozen, eq, hash)]
    // #[derive(PartialEq, Hash)]

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.email.hash(&mut hasher);
        self.group.hash(&mut hasher);
        self.key.hash(&mut hasher);
        self.gpu_count.hash(&mut hasher);
        hasher.finish()
    }

    // Truthyness
    fn __bool__(&self) -> bool {
        self.gpu_count != 0
    }

    // #[pyclass(eq, ord)]
    // #[derive(PartialEq, PartialOrd)]
    // Comparing Caravan objects done based off gpu_count
    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyResult<bool> {
        Ok(op.matches(self.gpu_count.cmp(&other.gpu_count)))
    }

    fn set_email(&mut self, user_email: String) {
        self.email = user_email;
    }

    fn set_group(&mut self, user_group: String) {
        self.group = user_group;
    }

    fn set_key(&mut self, user_key: String) {
        self.key = user_key;
    }

    fn set_gpu_count(&mut self, user_gpu_count: u32) {
        self.gpu_count = user_gpu_count;
    }

    /// Set Caravan email for access
    pub fn email<'a>(
        mut slf: PyRefMut<'a, Self>,
        user_email: String,
    ) -> PyResult<PyRefMut<'a, Self>> {
        slf.set_email(user_email);
        Ok(slf)
    }

    /// Set Caravan public/private group name
    pub fn group<'a>(
        mut slf: PyRefMut<'a, Self>,
        user_group: String,
    ) -> PyResult<PyRefMut<'a, Self>> {
        slf.set_group(user_group);
        Ok(slf)
    }

    /// Set Caravan sharing key to access a public/private group
    pub fn key<'a>(mut slf: PyRefMut<'a, Self>, user_key: String) -> PyResult<PyRefMut<'a, Self>> {
        slf.set_key(user_key);
        Ok(slf)
    }

    /// Request a specific number of GPUs for the Caravan
    pub fn gpu_count<'a>(
        mut slf: PyRefMut<'a, Self>,
        user_gpu_count: u32,
    ) -> PyResult<PyRefMut<'a, Self>> {
        slf.set_gpu_count(user_gpu_count);
        Ok(slf)
    }

    /// Using the provided options, build a Caravan of GPUs
    pub fn build<'a>(slf: PyRefMut<'a, Self>) -> PyResult<()> {
        // Check if either all or none of the email, group, and key are provided
        let is_email_empty = slf.email.is_empty();
        let is_group_empty = slf.group.is_empty();
        let is_key_empty = slf.key.is_empty();

        let all = !(is_email_empty || is_group_empty || is_key_empty);
        let none = is_email_empty && is_group_empty && is_key_empty;

        if !(all || none) {
            return Err(PyException::new_err(
                "Please provide an email, group, and key to build a Caravan.",
            ));
        }

        // if all {
        match client_endpoint::verify(
            Email::new(slf.email.clone()),
            Key::new(slf.key.clone()),
            Group::new(slf.group.clone()),
        ) {
            Ok(()) => {}
            Err(_) => {
                return Err(PyException::new_err(
                    "Group access verification failed. Please check your sharing key.",
                ))
            }
        };
        //}

        let (py_senders, msg_receiver) = match client_endpoint::queue(
            Email::new(slf.email.clone()),
            Key::new(slf.key.clone()),
            slf.gpu_count as i64,
        ) {
            Ok(py_senders) => {
                println!("Built Caravan!");
                py_senders
            }
            Err(_) => {
                return Err(PyException::new_err(
                    "Worker machines are currently busy. Please try again later.",
                ))
            }
        };

        PY_SENDERS.get_or_init(|| py_senders);
        MSG_RECEIVER.get_or_init(|| msg_receiver);

        Python::with_gil(|py| {
            let rtorch_mod = py.import("rtorch")?;

            let remote_call = RemoteCall { remote_call };
            let gpu_offsets: Vec<i64> = PY_SENDERS
                .get_or_init(|| vec![])
                .iter()
                .map(|(_sender, gpu_offset)| gpu_offset.clone())
                .collect();

            rtorch_mod
                .getattr("patch")?
                .call1((remote_call, gpu_offsets))?;

            Ok::<(), pyo3::PyErr>(())
        })?;

        Ok(())
    }
}

fn tokio() -> &'static Runtime {
    static TOKIO: OnceLock<Runtime> = OnceLock::new();
    TOKIO.get_or_init(|| Runtime::new().unwrap())
}

fn py_sender(idx: i32) -> (kanal::AsyncSender<PyMessage>, i64) {
    PY_SENDERS.get().unwrap()[idx as usize].clone()
}

fn msg_receiver() -> kanal::AsyncReceiver<Vec<u8>> {
    MSG_RECEIVER.get().unwrap().clone()
}

/// Call a remote `torch` function.
/// msg should be a serialized function message, device is the index of the
/// "local" abstracted device that the client has, which is mapped to the actual device
/// index on the worker machine using GPU offsets.
#[pyfunction]
pub fn remote_call(message: PyMessage, device: i32) -> PyResult<Vec<u8>> {
    info!("Remote call");
    let (sender, gpu_offset) = py_sender(device);
    info!("Corrected device index: {}", gpu_offset);

    let returns_future = !message.rids.is_empty();
    let rids = message.rids.clone();

    let send_task = async move {
        let rids = message.rids.clone();
        match sender.send(message).await {
            Ok(_) => {
                info!("sent message for rids: {rids:?}")
            }
            Err(_) => return Err(PyException::new_err("Failed to send message")),
        }
        Ok(())
    };

    let receive_task = async move {
        let msg_receiver = msg_receiver();
        msg_receiver
            .recv()
            .await
            .map_err(|e| PyException::new_err(format!("No response {e:?}")))
    };

    if returns_future {
        // Assume if rids not empty that all return types are futures, so return serialized list
        // of rids.
        info!("future found, returning with rids immediately");
        tokio().block_on(send_task)?;

        return serde_pickle::to_vec(&rids, SerOptions::default())
            .map_err(|_e| PyTypeError::new_err("could not serialize rids"));
    } else {
        let send_and_receive_task = async move {
            send_task.await?;
            receive_task.await
        };
        tokio().block_on(send_and_receive_task)
    }
}
