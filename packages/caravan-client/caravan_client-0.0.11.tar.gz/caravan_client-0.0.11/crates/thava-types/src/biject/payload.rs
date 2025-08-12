use crate::uid::Uid;

use derive_more::{Deref, DerefMut};
use std::collections::{HashMap, VecDeque};
use std::fmt::{Debug, Display};

use pyo3::exceptions::{PyAttributeError, PyBaseException, PyRuntimeError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyList, PyMapping, PyTuple};

use anyhow::Result;
use tracing::{info, instrument, warn};

/// A full function request including all necessary metadata for
/// a `torch` function call.
#[derive(Debug)]
pub struct FunctionRequest {
    pub full_fn_name: String,
    pub rids: VecDeque<Uid>,
    pub rdevice: i32,
    args: RArgs,
    kwargs: RKwargs,
    pub return_types: Vec<ReturnType>,
}

impl Display for FunctionRequest {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self.full_fn_name)
    }
}

impl FunctionRequest {
    fn resolve_fn<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let mut fn_pieces = self.full_fn_name.split(".");
        let mut module = match fn_pieces.next() {
            Some(module) => py.import(module)?,
            None => return Err(PyErr::new::<PyTypeError, _>("Invalid namespace")),
        }
        .into_any();

        for name in fn_pieces {
            module = module.getattr(name)?;
        }

        Ok(module)
    }

    fn to_json<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let fn_request_json = PyDict::new(py);

        fn_request_json.set_item("full_fn_name", &self.full_fn_name)?;
        fn_request_json.set_item("rdevice", self.rdevice)?;
        fn_request_json.set_item("args", self.args.bind(py))?;
        fn_request_json.set_item("kwargs", self.kwargs.bind(py))?;
        fn_request_json.set_item(
            "rids",
            self.rids
                .iter()
                .map(|id| (*id).into())
                .collect::<Vec<i64>>(),
        )?;
        fn_request_json.set_item(
            "return_types",
            self.return_types
                .iter()
                .map(|rtype| (*rtype).clone().into())
                .collect::<Vec<String>>(),
        )?;

        Ok(fn_request_json)
    }

    pub fn to_vec(&self) -> Result<Vec<u8>> {
        Ok(Python::with_gil(|py| {
            let fn_request_json = self.to_json(py)?;
            dumps(py, &fn_request_json)
        })?)
    }
}

impl Realize for FunctionRequest {
    fn recursive_realize<'py>(self, py: Python<'py>, object_cache: &ObjectCache) -> PyResult<Self>
    where
        Self: Sized,
    {
        Ok(FunctionRequest {
            full_fn_name: self.full_fn_name.clone(),
            rids: self.rids,
            rdevice: self.rdevice,
            args: self.args.recursive_realize(py, object_cache)?,
            kwargs: self.kwargs.recursive_realize(py, object_cache)?,
            return_types: self.return_types,
        })
    }
}

/// Stores all `torch` objects that are created along with their ids.
#[derive(Debug, Deref, DerefMut)]
pub struct ObjectCache(HashMap<Uid, Py<PyAny>>);

/// The arguments for the `torch` function being run.
#[derive(Debug, Deref)]
struct RArgs(Py<PyTuple>);

impl Realize for RArgs {
    #[instrument(skip_all)]
    fn recursive_realize<'py>(self, py: Python<'py>, object_cache: &ObjectCache) -> PyResult<Self>
    where
        Self: Sized,
    {
        let realized_args =
            recurse_realize_robjects(py, self.bind(py).clone().into_any(), object_cache)?;
        let realized_args: &Bound<'py, PyTuple> = realized_args.downcast()?;
        let realized_args: Py<PyTuple> = realized_args.clone().unbind();
        let realized_args = RArgs(realized_args);
        Ok(realized_args)
    }
}

/// The keyword arguments for the `torch` function being run.
#[derive(Debug, Deref)]
struct RKwargs(Py<PyDict>);

impl Realize for RKwargs {
    fn recursive_realize<'py>(self, py: Python<'py>, object_cache: &ObjectCache) -> PyResult<Self>
    where
        Self: Sized,
    {
        let realized_kwargs =
            recurse_realize_robjects(py, self.bind(py).clone().into_any(), object_cache)?;
        let realized_kwargs: &Bound<'py, PyDict> = realized_kwargs.downcast()?;
        let realized_kwargs: Py<PyDict> = realized_kwargs.into_py_dict(py)?.into();
        let realized_rkwargs = RKwargs(realized_kwargs);
        Ok(realized_rkwargs)
    }
}

trait Realize {
    fn recursive_realize<'py>(self, py: Python<'py>, object_cache: &ObjectCache) -> PyResult<Self>
    where
        Self: Sized;
}

pub fn init_object_cache() -> ObjectCache {
    ObjectCache(HashMap::new())
}

#[instrument(skip_all)]
pub fn handle_bytes(bytes: &[u8], object_cache: &mut ObjectCache) -> Result<Vec<u8>> {
    let fn_request = match deserialize_bytes(bytes) {
        Ok(fn_request) => fn_request,
        Err(e) => {
            let e = Python::with_gil(|py| -> Result<Vec<u8>> {
                warn!("Deserialize error: {:?}", e);
                let e: PyErr = PyBaseException::new_err("Could not deserialize bytes");
                let e: &Bound<'_, PyBaseException> = e.value(py);
                dumps(py, e).map_err(|e| anyhow::anyhow!("Could not serialize error: {:?}", e))
            });
            return e;
        }
    };

    let result = Python::with_gil(|py| -> PyResult<Vec<u8>> {
        let fn_request = fn_request.into_bound(py);
        info!("fn_request: {fn_request:?}");

        let fn_request = parse_fn_request(&fn_request)
            .map_err(|e| PyTypeError::new_err(format!("Error parsing function request: {e}")))?;

        info!("parsed fn_request: {fn_request:?}");

        if fn_request.full_fn_name == "rdrop" {
            // explicitly ignore any exceptions here
            let _result = rdrop(py, &fn_request, object_cache);
            // rdrops are Future calls, don't return anything here
            return Ok(vec![]);
        }

        info!("Parsed function request {fn_request}");

        let mut fn_request = fn_request.recursive_realize(py, object_cache)?;

        let fn_result = call_fn(py, &fn_request)?;

        let result = recurse_to_robjects(
            py,
            fn_request.rdevice,
            fn_result,
            object_cache,
            &mut fn_request.rids,
        )?;

        // Explicitly don't return anything here
        if fn_request
            .return_types
            .iter()
            .any(|rtype| matches!(rtype, ReturnType::Future))
        {
            info!("future found, not returning anything");
            return Ok(vec![]);
        }

        let result_payload = dumps(py, &result)?;
        Ok(result_payload)
    });

    match result {
        Ok(result) => Ok(result),
        Err(e) => Python::with_gil(|py| -> Result<Vec<u8>> {
            let e: &Bound<'_, PyBaseException> = e.value(py);
            warn!("Python error encountered: {:?}", e);
            dumps(py, e).map_err(|e| anyhow::anyhow!("Could not serialize: {:?}", e))
        }),
    }
}

#[instrument(skip(bytes))]
fn deserialize_bytes(bytes: &[u8]) -> Result<Py<PyAny>> {
    let result = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
        let _rtorch_mod = py.import("rtorch")?;

        let pickle = py.import("pickle")?;
        let loads = pickle.getattr("loads")?;
        let obj = loads.call1((bytes,))?;

        Ok(obj.to_owned().unbind())
    });

    Ok(result?)
}

#[instrument(skip_all)]
pub fn parse_fn_request(fn_request: &Bound<'_, PyAny>) -> Result<FunctionRequest> {
    let full_fn_name: String = partial_parse_fn_request(fn_request, "full_fn_name")?;
    info!("parsing fn_request for {full_fn_name}");
    let rdevice: i32 = partial_parse_fn_request(fn_request, "rdevice")?;
    let args: RArgs = RArgs(partial_parse_fn_request(fn_request, "args")?);
    let kwargs: RKwargs = RKwargs(partial_parse_fn_request(fn_request, "kwargs")?);
    let rids: VecDeque<Uid> = partial_parse_fn_request::<Vec<i64>>(fn_request, "rids")
        .ok()
        .map(|v| v.iter().map(|i| (*i).into()).collect())
        .unwrap_or_default();
    let return_types: Vec<ReturnType> =
        partial_parse_fn_request::<Vec<String>>(fn_request, "return_types")?
            .iter()
            .map(From::from)
            .collect();

    Ok(FunctionRequest {
        full_fn_name,
        rdevice,
        rids,
        args,
        kwargs,
        return_types,
    })
}

fn partial_parse_fn_request<'py, T>(fn_request: &Bound<'py, PyAny>, partial_name: &str) -> Result<T>
where
    T: Debug + FromPyObject<'py>,
{
    let partial_piece = fn_request
        .getattr("get")?
        .call1((partial_name,))?
        .extract::<T>()?;

    Ok(partial_piece)
}

#[derive(Clone, Debug, PartialEq)]
pub enum ReturnType {
    Future,
    Blocker,
}

impl From<&String> for ReturnType {
    fn from(value: &String) -> Self {
        match value.as_str() {
            "future" => Self::Future,
            "blocker" => Self::Blocker,
            _ => Self::Blocker,
        }
    }
}

impl From<ReturnType> for String {
    fn from(value: ReturnType) -> Self {
        match value {
            ReturnType::Future => "future".to_string(),
            ReturnType::Blocker => "blocker".to_string(),
        }
    }
}

pub fn generate_future_rids(return_types: &Vec<ReturnType>) -> Vec<Uid> {
    return_types
        .iter()
        .filter(|rtype| **rtype == ReturnType::Future)
        .map(|_| Uid::new())
        .collect::<Vec<Uid>>()
}

fn is_robject<'py>(py: Python<'py>, object: &Bound<'py, PyAny>) -> PyResult<bool> {
    let rtorch_mod = py.import("rtorch")?;

    let is_robject_fn = rtorch_mod.getattr("is_robject")?;
    let is_robject = is_robject_fn.call1((object,))?.extract::<bool>()?;

    Ok(is_robject)
}

#[instrument(skip_all)]
fn get_rid<'py>(robject: &Bound<'py, PyAny>) -> PyResult<Uid> {
    let rid: Uid = robject
        .getattr("rid")?
        .getattr("id")?
        .extract::<i64>()?
        .into();
    Ok(rid)
}

#[instrument(skip_all)]
fn rdrop<'py>(
    py: Python<'py>,
    fn_request: &FunctionRequest,
    object_cache: &mut ObjectCache,
) -> PyResult<Vec<u8>> {
    if fn_request.full_fn_name != "rdrop" {
        return Err(PyAttributeError::new_err(
            "drop called without `rdrop` in request",
        ));
    }

    let args = fn_request.args.bind(py);
    if args.len() != 1 {
        return Err(PyAttributeError::new_err(
            "drop called with more than one argument, only self must be passed",
        ));
    }

    let robject = args.get_item(0)?;
    let rid = get_rid(&robject)?;

    let robject = object_cache.remove(&rid);
    match robject {
        Some(robject) => drop(robject),
        None => return Err(PyRuntimeError::new_err("could not find robject to drop")),
    }

    info!("dropped robject with rid {rid:?}");

    // pickle output for int 0
    Ok(vec![128, 4, 75, 0, 46])
}

/// Recursively convert all RObjects to their original states
/// TODO: send a `has_robjects` boolean from Python to skip the double check.
fn recurse_realize_robjects<'py>(
    py: Python<'py>,
    object: Bound<'py, PyAny>,
    object_cache: &ObjectCache,
) -> PyResult<Bound<'py, PyAny>> {
    let rtorch_mod = py.import("rtorch")?;
    let robject_class = rtorch_mod.getattr("RObject")?;
    if object.is_instance(&robject_class)? {
        return from_robject(py, object, object_cache);
    }

    if object.is_instance_of::<PyTuple>() {
        let realized_tuple = object
            .try_iter()?
            .map(|e| {
                let e = e?;
                let r_e = recurse_realize_robjects(py, e, object_cache)?;
                Ok(r_e.clone())
            })
            .collect::<PyResult<Vec<Bound<'py, PyAny>>>>()?;

        info!("realized tuple");
        return Ok(PyTuple::new(py, realized_tuple)?.into_any());
    } else if object.is_instance_of::<PyList>() {
        let realized_list = object
            .try_iter()?
            .map(|e| {
                let e = e?;
                let r_e = recurse_realize_robjects(py, e, object_cache)?;
                Ok(r_e.clone())
            })
            .collect::<PyResult<Vec<Bound<'py, PyAny>>>>()?;

        info!("realized list");
        return Ok(PyList::new(py, realized_list)?.into_any());
    } else if object.is_instance_of::<PyDict>() {
        let realized_dict: &Bound<'py, PyDict> = object.downcast()?;
        for (k, v) in realized_dict.iter() {
            let v = recurse_realize_robjects(py, v, object_cache)?;
            realized_dict.set_item(k, v)?;
        }

        info!("realized dict");
    } else if object.hasattr("__dict__")? {
        let object_realized_dict: Bound<'py, PyMapping> =
            object.getattr("__dict__")?.downcast()?.clone();
        for pair in object_realized_dict.items()?.iter() {
            let k = pair.get_item(0)?;
            let v = pair.get_item(1)?;
            let v = recurse_realize_robjects(py, v, object_cache)?;
            match object.getattr("__dict__")?.set_item(&k, &v) {
                Ok(()) => continue,
                Err(e) => {
                    warn!(
                        "Error setting __dict__ k: {:?} to v {:?} due to {:?}",
                        k, v, e
                    );
                }
            }
        }

        info!("realized __dict__");
    }
    Ok(object)
}

/// Directly convert a Python RObject to the original object.
#[instrument(skip_all)]
fn from_robject<'py>(
    py: Python<'py>,
    object: Bound<'py, PyAny>,
    object_cache: &ObjectCache,
) -> PyResult<Bound<'py, PyAny>> {
    if !is_robject(py, &object)? {
        return Err(PyTypeError::new_err(format!(
            "object {object} is not an robject",
        )));
    }

    let rid = get_rid(&object)?;

    let original_object = object_cache
        .get(&rid)
        .ok_or(PyTypeError::new_err(format!(
            "robject with RId {rid} not found"
        )))?
        .bind(py);

    Ok(original_object.clone())
}

fn get_type<'py>(object: &Bound<'py, PyAny>) -> PyResult<String> {
    let object_type: String = object.get_type().fully_qualified_name()?.extract()?;
    Ok(object_type)
}

fn is_torch_object<'py>(object: &Bound<'py, PyAny>) -> PyResult<bool> {
    let object_type = &get_type(object)?;
    info!("object type: {object_type}");

    if object_type.len() < 5 {
        return Ok(false);
    }

    info!("object type first 5: {:?}", &object_type[0..5]);

    Ok(&object_type[0..5] == "torch")
}

fn get_torch_class<'py>(object: &Bound<'py, PyAny>) -> PyResult<String> {
    let object_type = &get_type(object)?;

    if !is_torch_object(object)? {
        return Err(PyTypeError::new_err(format!(
            "{object} cannot be parsed for RObject conversion: not a `torch` object",
        )));
    }

    let mut object_type_pieces = object_type.rsplit(".");
    match object_type_pieces.next() {
        Some(object) => Ok(object.into()),
        None => Err(PyTypeError::new_err(format!(
            "{object} cannot be parsed for RObject conversion"
        ))),
    }
}

/// Recursively convert all torch objects to RObjects
fn recurse_to_robjects<'py>(
    py: Python<'py>,
    rdevice: i32,
    object: Bound<'py, PyAny>,
    object_cache: &mut ObjectCache,
    rids: &mut VecDeque<Uid>,
) -> PyResult<Bound<'py, PyAny>> {
    info!("rids: {rids:?}");
    // If `rdevice` is -1, we want to return the object directly
    if is_torch_object(&object)? && rdevice != -1 {
        info!("is torch object, converting to robject");

        return to_robject(py, rdevice, object, object_cache, rids.pop_front());
    }

    if object.is_instance_of::<PyTuple>() {
        let realized_tuple = object
            .try_iter()?
            .map(|e| {
                let e = e?;
                let r_e = recurse_to_robjects(py, rdevice, e, object_cache, rids)?;
                Ok(r_e.clone())
            })
            .collect::<PyResult<Vec<Bound<'py, PyAny>>>>()?;

        info!("to tuple");
        return Ok(PyTuple::new(py, realized_tuple)?.into_any());
    } else if object.is_instance_of::<PyList>() {
        let realized_list = object
            .try_iter()?
            .map(|e| {
                let e = e?;
                let r_e = recurse_to_robjects(py, rdevice, e, object_cache, rids)?;
                Ok(r_e.clone())
            })
            .collect::<PyResult<Vec<Bound<'py, PyAny>>>>()?;

        info!("to list");
        return Ok(PyList::new(py, realized_list)?.into_any());
    } else if object.is_instance_of::<PyDict>() {
        let realized_dict: &Bound<'py, PyDict> = object.downcast()?;
        for (k, v) in realized_dict.iter() {
            let v = recurse_to_robjects(py, rdevice, v, object_cache, rids)?;
            realized_dict.set_item(k, v)?;
        }

        info!("to dict");
    } else if object.hasattr("__dict__")? {
        let object_realized_dict: Bound<'py, PyMapping> =
            object.getattr("__dict__")?.downcast()?.clone();
        for pair in object_realized_dict.items()?.iter() {
            let k = pair.get_item(0)?;
            let v = pair.get_item(1)?;
            let v = recurse_to_robjects(py, rdevice, v, object_cache, rids)?;
            match object.getattr("__dict__")?.set_item(&k, &v) {
                Ok(()) => continue,
                Err(e) => {
                    warn!(
                        "Error setting __dict__ k: {:?} to v {:?} due to {:?}",
                        k, v, e
                    );
                }
            }
        }

        info!("to __dict__");
    }
    Ok(object)
}

/// Converts a torch object to the corresponding RObject remote reference
/// to be sent back to the client Python. The `rdevice`
/// field must be populated by client Python since it knows the
/// device mapping.
fn to_robject<'py>(
    py: Python<'py>,
    rdevice: i32,
    object: Bound<'py, PyAny>,
    object_cache: &mut ObjectCache,
    rid: Option<Uid>,
) -> PyResult<Bound<'py, PyAny>> {
    let torch_class = get_torch_class(&object)?;
    let rtorch_class = "R".to_owned() + &torch_class;
    info!("returning robject of type: {rtorch_class}");

    let rtorch_mod = py.import("rtorch")?;
    let rtorch_class = match rtorch_mod.getattr(&*rtorch_class) {
        Ok(class) => class,
        Err(e) => {
            warn!("{e:?}");
            return Ok(object);
        }
    };
    info!("resolved rtorch class: {:?}", rtorch_class);

    let id = match rid {
        Some(id) => {
            info!("found rid to use for assigning");
            id
        }
        None => Uid::new(),
    };

    object_cache.insert(id.clone(), object.clone().into());

    let robject = rtorch_class.call0()?;
    let rid: i64 = id.into();
    let rid = rtorch_mod.getattr("RId")?.call1((rid,))?;
    let robject = robject.call_method1("rnew", (rid, rdevice))?;

    Ok(robject)
}

fn dumps<'py>(py: Python<'py>, object: &Bound<'py, PyAny>) -> PyResult<Vec<u8>> {
    let pickle = py.import("pickle")?;
    let dumps = pickle.getattr("dumps")?;
    let object_payload = match dumps.call1((object,)) {
        Ok(payload) => payload,
        // We don't include _e in the error b/c it can trigger infinite recursion
        // while serializing.
        Err(_e) => {
            return Err(PyTypeError::new_err(
                "Could not serialize function request properly",
            ));
        }
    };

    let payload = object_payload.extract::<Vec<u8>>();

    payload
}

fn call_fn<'py>(py: Python<'py>, fn_request: &FunctionRequest) -> PyResult<Bound<'py, PyAny>> {
    let function = fn_request.resolve_fn(py)?;

    info!("function resolved: {:?}", function);

    let function_result = if function.is_callable() {
        info!("function is callable");
        function.call(fn_request.args.bind(py), Some(fn_request.kwargs.bind(py)))
    } else {
        info!("function not callable, getting property");
        let mut property_pieces = fn_request.full_fn_name.rsplit(".");
        match property_pieces.next() {
            Some(property_name) => fn_request.args.bind(py).get_item(0)?.getattr(property_name),
            None => Err(PyTypeError::new_err(format!(
                "could not retrieve property value for {:?}",
                fn_request.full_fn_name
            ))),
        }
    }?;

    info!("function result type: {:?}", function_result.get_type());

    Ok(function_result)
}
