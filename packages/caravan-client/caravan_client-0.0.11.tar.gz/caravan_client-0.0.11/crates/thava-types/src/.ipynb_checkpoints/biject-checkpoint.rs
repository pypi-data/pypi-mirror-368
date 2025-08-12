use derive_more::{Deref, DerefMut};
use std::collections::HashMap;

use anyhow::Result;

use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;

use pyo3::types::{IntoPyDict, PyDict, PyList, PyListMethods, PyString, PyTuple};
use tracing::info;

use crate::uid::Uid;

/// The `torch` function to be run.
#[derive(Debug, Deref, Clone)]
struct RFunction(String);

/// The object (e.g. `Tensor`, `Module`) that will be operated on.
#[derive(Debug, Deref, Eq, Hash, PartialEq, Clone)]
struct RTorchObject(String);

/// The arguments for the `torch` function being run.
#[derive(Debug, Deref)]
struct RArgs(Py<PyTuple>);

/// The keyword arguments for the `torch` function being run.
#[derive(Debug, Deref)]
struct RKwargs(Py<PyDict>);

/// A full function request including all necessary metadata for
/// a `torch` function call.
#[derive(Debug)]
struct FunctionRequest {
    namespace: RTorchNamespace,
    function: RFunction,
    is_property: bool,
    object: Option<RTorchObject>,
    args: RArgs,
    kwargs: RKwargs,
}

/// Stores all `torch` objects that are created along with their ids.
#[derive(Debug, Deref, DerefMut)]
pub struct ObjectCache(HashMap<Uid, Py<PyAny>>);

/// Supported `torch` namespaces.
#[derive(Debug)]
enum RTorchNamespace {
    Torch { object: Option<TorchObject> },
    Cuda,
    Nn { object: Option<NnObject> },
    Optim { object: Option<OptimObject> },
}

/// Supported `torch` objects
#[derive(Debug)]
enum TorchObject {
    Tensor,
}

/// Supported `torch.nn` objects
#[derive(Debug)]
enum NnObject {
    Module,
    BCELoss,
}

/// Supported `torch.optim` objects
#[derive(Debug)]
enum OptimObject {
    Adam,
}

impl From<&str> for RTorchNamespace {
    fn from(namespace: &str) -> Self {
        match namespace {
            "torch" => RTorchNamespace::Torch { object: None },
            "torch.Tensor" => RTorchNamespace::Torch {
                object: Some(TorchObject::Tensor),
            },
            "torch.cuda" => RTorchNamespace::Cuda,
            "torch.nn" => RTorchNamespace::Nn { object: None },
            "torch.nn.Module" => RTorchNamespace::Nn {
                object: Some(NnObject::Module),
            },
            "torch.nn.BCELoss" => RTorchNamespace::Nn {
                object: Some(NnObject::BCELoss),
            },
            "torch.optim" => RTorchNamespace::Optim { object: None },
            "torch.optim.Adam" => RTorchNamespace::Optim {
                object: Some(OptimObject::Adam),
            },
            _ => panic!("Invalid namespace"),
        }
    }
}

impl From<RTorchNamespace> for &str {
    fn from(namespace: RTorchNamespace) -> Self {
        match namespace {
            RTorchNamespace::Torch {
                object: Some(TorchObject::Tensor),
            } => "torch.Tensor",
            RTorchNamespace::Torch { .. } => "torch",
            RTorchNamespace::Cuda => "torch.cuda",
            RTorchNamespace::Nn {
                object: Some(NnObject::Module),
            } => "torch.nn.Module",
            RTorchNamespace::Nn {
                object: Some(NnObject::BCELoss),
            } => "torch.nn.BCELoss",
            RTorchNamespace::Nn { object: None } => "torch.nn",
            RTorchNamespace::Optim {
                object: Some(OptimObject::Adam),
            } => "torch.optim.Adam",
            RTorchNamespace::Optim { object: None } => "torch.optim",
        }
    }
}

pub fn init_python() -> PyResult<()> {
    // Python::with_gil(|py| -> PyResult<()> {
    //     let signal = py.import_bound("signal")?;
    //     // Set SIGINT to have the default action
    //     signal
    //         .getattr("signal")?
    //         .call1((signal.getattr("SIGINT")?, signal.getattr("SIG_DFL")?))?;
    //     Ok(())
    // })?;

    Ok(())
}

pub fn init_object_cache() -> ObjectCache {
    ObjectCache(HashMap::new())
}

pub fn handle_bytes(bytes: &[u8], object_cache: &mut ObjectCache) -> Result<Vec<u8>> {
    info!("Received bytes");

    info!("Changes");
    let fn_req = unserialize_bytes(bytes)?;

    info!("Unserialized object: {:?}", fn_req);

    let result = Python::with_gil(|py| -> PyResult<Vec<u8>> {
        let fn_req = fn_req.into_bound(py);

        let fn_req = parse_fn_req(&fn_req).map_err(|e| {
            PyErr::new::<PyTypeError, _>(format!("Error parsing function request: {:?}", e))
        })?;

        info!("Parsed function request {:?}", fn_req);

        let result = call(py, object_cache, fn_req).map_err(|e| {
            PyErr::new::<PyTypeError, _>(format!("Error calling function: {:?}", e))
        })?;

        Ok(result)
    });

    Ok(result?)
}

fn unserialize_bytes(bytes: &[u8]) -> Result<Py<PyAny>> {
    info!("Unserializing bytes");
    let result = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
        let rtorch_code = include_str!("rtorch.py");
        let _ = PyModule::from_code_bound(py, rtorch_code, "rtorch.py", "rtorch")?;

        let dill = py.import_bound("dill")?;
        let loads = dill.getattr("loads")?;
        let obj = loads.call1((bytes,))?;

        Ok(obj.to_owned().unbind())
    });

    info!("Unserialized bytes");
    Ok(result?)
}

fn parse_fn_req(fn_req: &Bound<'_, PyAny>) -> Result<FunctionRequest> {
    let namespace = parse_namespace(fn_req)?;
    let function = parse_function(fn_req)?;
    let is_property = parse_is_property(fn_req)?;
    let object = parse_object(fn_req)?;
    let args = parse_args(fn_req)?;
    let kwargs = parse_kwargs(fn_req)?;

    Ok(FunctionRequest {
        namespace,
        function,
        is_property,
        object,
        args,
        kwargs,
    })
}

/// Parse the namespace from the function request
fn parse_namespace(fn_req: &Bound<'_, PyAny>) -> Result<RTorchNamespace> {
    info!("Parsing namespace");
    let namespace = fn_req
        .getattr("get")?
        .call1(("namespace",))?
        .extract::<String>()?;

    let object = fn_req
        .getattr("get")?
        .call1(("object",))?
        .extract::<Option<String>>()?;

    let full_namespace = match object {
        Some(object) => format!("{}.{}", namespace, object),
        None => namespace,
    };

    info!("Parsed namespace: {:?}", full_namespace);
    Ok(full_namespace.as_str().into())
}

/// Parse the function from the function request
fn parse_function(fn_req: &Bound<'_, PyAny>) -> Result<RFunction> {
    info!("Parsing function");
    let function = fn_req
        .getattr("get")?
        .call1(("function",))?
        .extract::<String>()?;

    info!("Parsed function: {:?}", function);
    Ok(RFunction(function))
}

/// Parse the is_property from the function request
fn parse_is_property(fn_req: &Bound<'_, PyAny>) -> Result<bool> {
    let is_property = fn_req
        .getattr("get")?
        .call1(("is_property",))?
        .extract::<bool>()?;

    Ok(is_property)
}

/// Parse the torch object (e.g. "Tensor") that we will be operating on from the function request
fn parse_object(fn_req: &Bound<'_, PyAny>) -> Result<Option<RTorchObject>> {
    let object = fn_req
        .getattr("get")?
        .call1(("object",))?
        .extract::<Option<String>>()?
        .map(|object_name| RTorchObject(object_name));

    Ok(object)
}

/// Parse the args from the function request
fn parse_args(fn_req: &Bound<'_, PyAny>) -> Result<RArgs> {
    let args: Py<PyTuple> = fn_req
        .getattr("get")?
        .call1(("args",))?
        .downcast::<PyTuple>()
        .map_err(|_| PyErr::new::<PyTypeError, _>("Invalid args"))?
        .clone()
        .unbind();

    Ok(RArgs(args))
}

/// Parse the kwargs from the function request
fn parse_kwargs(fn_req: &Bound<'_, PyAny>) -> Result<RKwargs> {
    let kwargs: Py<PyDict> = fn_req
        .getattr("get")?
        .call1(("kwargs",))?
        .downcast::<PyDict>()
        .map_err(|_| PyErr::new::<PyTypeError, _>("Invalid kwargs"))?
        .clone()
        .unbind();

    Ok(RKwargs(kwargs))
}

/// Resolve a namespace to a Python object/module that can then have functions called on it
pub fn resolve_namespace<'a>(py: Python<'a>, namespace: &str) -> PyResult<Bound<'a, PyAny>> {
    let mut namespace = namespace.split(".");
    let mut module = match namespace.next() {
        Some(module) => py.import_bound(module)?,
        None => return Err(PyErr::new::<PyTypeError, _>("Invalid namespace")),
    }
    .into_any();

    while let Some(name) = namespace.next() {
        module = module.getattr(name)?;
    }

    Ok(module)
}

pub fn resolve_object<'a>(namespace: Bound<'a, PyAny>, object: &str) -> PyResult<Bound<'a, PyAny>> {
    let object = namespace.getattr(object)?;

    Ok(object)
}

/// Create an empty tensor
fn empty_tensor<'a>(py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let torch = py.import_bound("torch")?;
    let tensor = torch.getattr("empty")?;
    let tensor = tensor.call1((0,))?;

    Ok(tensor)
}

/// Create an empty module
fn empty_module<'a>(py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let torch = py.import_bound("torch")?;
    let module = torch.getattr("nn")?.getattr("Module")?;
    let module = module.call0()?;

    Ok(module)
}

/// Dump payload to bytes
fn dump(py: Python, payload: Bound<'_, PyAny>) -> Result<Vec<u8>> {
    let dill = py.import_bound("dill")?;
    let dumps = dill.getattr("dumps")?;
    let result = dumps.call1((payload,))?;

    Ok(result.extract::<Vec<u8>>()?)
}

fn dump_empty_payload(py: Python, payload: Bound<'_, PyAny>) -> Result<Vec<u8>> {
    dump(py, payload)
}

/// Create an id with empty tensor payload to return to client
fn empty_tensor_payload(py: Python, id: Uid) -> Result<Bound<'_, PyAny>> {
    let empty_tensor = empty_tensor(py)?;
    let id: i64 = id.into();
    let id = id.to_object(py).into_bound(py);
    let result_tuple = PyTuple::new_bound(py, &[id, empty_tensor]);

    let result = result_tuple.to_object(py).into_bound(py);

    Ok(result)
}

fn empty_module_payload(py: Python, id: Uid) -> Result<Bound<'_, PyAny>> {
    let empty_module = empty_module(py)?;
    let id: i64 = id.into();
    let id = id.to_object(py).into_bound(py);
    let result_tuple = PyTuple::new_bound(py, &[id, empty_module]);

    let result = result_tuple.to_object(py).into_bound(py);

    Ok(result)
}

fn empty_adam_payload(py: Python, id: Uid) -> Result<Bound<'_, PyAny>> {
    let adam_str = PyString::new_bound(py, "Adam").into_any();

    let id: i64 = id.into();
    let id = id.to_object(py).into_bound(py);
    let result_tuple = PyTuple::new_bound(py, &[id, adam_str]);

    let result = result_tuple.to_object(py).into_bound(py);

    Ok(result)
}

/// Fulfill a function request
fn call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    match &fn_req.namespace {
        RTorchNamespace::Torch {
            object: Some(TorchObject::Tensor),
        } => tensor_call(py, object_cache, fn_req),
        RTorchNamespace::Torch { object: None } => torch_call(py, object_cache, fn_req),
        RTorchNamespace::Cuda => cuda_call(py, object_cache, fn_req),
        RTorchNamespace::Nn {
            object: Some(NnObject::Module),
        } => module_call(py, object_cache, fn_req),
        RTorchNamespace::Nn {
            object: Some(NnObject::BCELoss),
        } => bceloss_call(py, object_cache, fn_req),
        RTorchNamespace::Optim {
            object: Some(OptimObject::Adam),
        } => adam_call(py, object_cache, fn_req),
        _ => unimplemented!(),
    }
}

/// Fulfill a torch namespace function request
fn torch_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    info!("torch_call: start");

    match fn_req.function.0.as_str() {
        "tensor" | "zeros" | "zeros_like" | "view_as_real" | "view_as_complex" | "maximum" => {
            creation_op_call(py, object_cache, fn_req, false)
        }
        "is_complex" => torch_bool_call(py, object_cache, fn_req),
        "_foreach_add"
        | "_foreach_add_"
        | "_foreach_neg"
        | "_foreach_lerp_"
        | "_foreach_mul_"
        | "_foreach_addcmul_"
        | "_foreach_pow"
        | "_foreach_sub_"
        | "_foreach_div_"
        | "_foreach_reciprocal_"
        | "_foreach_sqrt_"
        | "_foreach_sqrt"
        | "_foreach_maximum_"
        | "_foreach_addcdiv_" => creation_op_call(py, object_cache, fn_req, true),
        _ => unimplemented!(),
    }
}

fn tensor_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let function = fn_req.function.0.as_str();

    match function {
        "reshape" | "__repr__" | "round" | "mean" | "__add__" | "__getitem__" | "is_sparse"
        | "__pow__" | "__mul__" | "clone" | "sqrt" | "to" | "backward" => {
            creation_op_call(py, object_cache, fn_req, false)
        }
        _ => unimplemented!(),
    }
}

fn module_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let function = fn_req.function.0.as_str();

    match function {
        "to" => module_creation_op_call(py, object_cache, fn_req),
        "_wrapped_call_impl" => creation_op_call(py, object_cache, fn_req, false),
        _ => unimplemented!(),
    }
}

fn bceloss_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let function = fn_req.function.0.as_str();

    match function {
        "_wrapped_call_impl" => creation_op_call(py, object_cache, fn_req, false),
        _ => unimplemented!(),
    }
}

fn adam_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let function = fn_req.function.0.as_str();

    match function {
        "__init__" => adam_creation_op_call(py, object_cache, fn_req),
        "step" => creation_op_call(py, object_cache, fn_req, false),
        "__repr__" => creation_op_call(py, object_cache, fn_req, false),
        "zero_grad" => creation_op_call(py, object_cache, fn_req, false),
        _ => unimplemented!(),
    }
}

fn convert_rid_to_robject<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    arg: Bound<'_, PyAny>,
) -> Result<Bound<'a, PyAny>> {
    let rtorch_code = include_str!("rtorch.py");

    let rtorch_mod = PyModule::from_code_bound(py, rtorch_code, "rtorch.py", "rtorch")?;

    let locals =
        &[("arg", arg.clone()), ("RId", rtorch_mod.getattr("RId")?)].into_py_dict_bound(py);

    info!(
        "RId type name: {}",
        rtorch_mod.getattr("RId")?.get_type().name()?
    );

    info!("Arg type name: {}", arg.get_type().name()?);

    let result = py
        .eval_bound("str(type(arg))", None, Some(locals))?
        //.eval_bound("isinstance(arg, RId)", None, Some(locals))?
        .extract::<String>()?;
    info!("Printing result of eval_bound: {:?}", result);

    if result != "<class 'rtorch.RId'>" {
        return Err(anyhow::anyhow!("Not an RId"));
    }

    info!("Is an RId, converting");
    let robject = match object_cache.get(&(arg.getattr("id")?.extract::<i64>()?.into())) {
        Some(robject) => robject,
        None => return Err(anyhow::anyhow!("Object not found")),
    };

    Ok(robject.to_object(py).into_bound(py))
}

/// Converts RId to tensors in place within the args PyTuple
fn rtensor_ids_to_robjects<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    args: &Bound<'_, PyTuple>,
) -> Result<Bound<'a, PyTuple>> {
    // Retrieve tensor from object cache
    let mut converted_args = Vec::<Py<PyAny>>::new();
    for i in 0..args.len() {
        info!("Attempting convert of arg {}", i);
        let arg = args.get_item(i)?;

        info!("Arg: {:?}", arg);

        let converted_arg = match convert_rid_to_robject(py, object_cache, arg.clone()) {
            Ok(converted_arg) => converted_arg,
            Err(e) => {
                info!("Error converting arg: {:?}", e);
                converted_args.push(arg.clone().into());
                continue;
            }
        };

        converted_args.push(converted_arg.unbind());
    }

    let converted_args = PyTuple::new_bound(py, &converted_args);

    Ok(converted_args)
}

/// Converts RIds to tensors in place within the TensorLists in the args PyTuple
fn foreach_rtensor_ids_to_tensors<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    args: &Bound<'_, PyTuple>,
) -> Result<Bound<'a, PyTuple>> {
    // Retrieve tensor from object cache
    let mut converted_args = Vec::<Py<PyAny>>::new();

    let rtorch_code = include_str!("rtorch.py");

    let rtorch_mod = PyModule::from_code_bound(py, rtorch_code, "rtorch.py", "rtorch")?;

    for i in 0..args.len() {
        info!("Attempting convert of arg {}", i);
        let arg = args.get_item(i)?;

        info!("Arg: {:?}", arg);

        info!("Type: {:?}", arg.get_type().name()?);

        if arg.get_type().name()? != "tuple" {
            info!("Not a tuple, skipping");
            converted_args.push(arg.unbind());
            continue;
        }

        let arg = arg
            .downcast::<PyTuple>()
            .map_err(|_| PyErr::new::<PyTypeError, _>("Invalid TensorList arg"))?;

        let mut rtensor_args = Vec::<Py<PyAny>>::new();
        for j in 0..arg.len() {
            let rtensor_arg = arg.get_item(j)?;

            let locals = &[
                ("arg", rtensor_arg.clone()),
                ("RId", rtorch_mod.getattr("RId")?),
            ]
            .into_py_dict_bound(py);

            let result = py
                .eval_bound("str(type(arg))", None, Some(locals))?
                .extract::<String>()?;
            info!("Printing result of eval_bound: {:?}", result);

            if result != "<class 'rtorch.RId'>" {
                info!("Not an RId, skipping");
                rtensor_args.push(rtensor_arg.unbind());
                continue;
            }

            info!("Is an RId, converting");
            let tensor =
                match object_cache.get(&(rtensor_arg.getattr("id")?.extract::<i64>()?.into())) {
                    Some(pyself) => pyself,
                    None => return Err(anyhow::anyhow!("Object not found")),
                };

            let tensor = tensor.to_object(py).into_bound(py);

            info!("Converted tensor: {:?}", tensor);

            rtensor_args.push(tensor.unbind());
        }

        let rtensor_args: Py<PyAny> = PyTuple::new_bound(py, &rtensor_args).into();

        info!("Converted rtensor_args: {:?}", &rtensor_args);

        converted_args.push(rtensor_args);
    }

    let converted_args = PyTuple::new_bound(py, &converted_args);

    info!("Final converted args: {:?}", converted_args);

    Ok(converted_args)
}

fn module_creation_op_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let namespace = resolve_namespace(py, fn_req.namespace.into())?;

    let resolved_fn = namespace.getattr(fn_req.function.as_str())?;

    let args = fn_req.args.clone_ref(py).into_bound(py);

    let kwargs = fn_req.kwargs.clone_ref(py).into_bound(py);

    let rmodule = match resolved_fn.call(args, Some(&kwargs)) {
        Ok(rmodule) => rmodule,
        Err(e) => {
            info!("torch_call: error calling function: {:?}", e);
            return Ok(Vec::new());
        }
    };
    let new_id = Uid::new();

    // Add tensor to object cache
    info!(
        "rmodule_call: inserting rmodule into object cache with id: {:?}",
        &new_id
    );
    object_cache.insert(new_id.clone(), rmodule.to_owned().unbind());
    info!("rmodule_call: inserted rmodule into object cache");

    // Return tuple of new_id and empty tensor to client
    info!("rmodule_call: returning empty tensor payload");
    dump_empty_payload(py, empty_module_payload(py, new_id)?)
}

fn adam_creation_op_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    let namespace = resolve_namespace(py, fn_req.namespace.into())?;

    let args = fn_req.args.clone_ref(py).into_bound(py);

    let kwargs = fn_req.kwargs.clone_ref(py).into_bound(py);

    let rmodule = match convert_rid_to_robject(py, object_cache, args.get_item(0)?) {
        Ok(rmodule) => rmodule,
        Err(e) => {
            info!("torch_call: error converting rmodule: {:?}", e);
            return Ok(Vec::new());
        }
    };

    let params = rmodule.getattr("parameters")?.call0()?;

    let mut remaining_args = args
        .get_slice(1, args.len() - 1)
        .extract::<Vec<Py<PyAny>>>()?;

    remaining_args.insert(0, params.into());

    let args = PyTuple::new_bound(py, &remaining_args);

    let rmodule = match namespace.call(args, Some(&kwargs)) {
        Ok(rmodule) => rmodule,
        Err(e) => {
            info!("torch_call: error calling function: {:?}", e);
            return Ok(Vec::new());
        }
    };
    let new_id = Uid::new();

    // Add tensor to object cache
    info!(
        "rmodule_call: inserting rmodule into object cache with id: {:?}",
        &new_id
    );
    object_cache.insert(new_id.clone(), rmodule.to_owned().unbind());
    info!("rmodule_call: inserted rmodule into object cache");

    // Return tuple of new_id and empty tensor to client
    info!("rmodule_call: returning empty tensor payload");
    dump_empty_payload(py, empty_adam_payload(py, new_id)?)
}

fn creation_op_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
    is_foreach: bool,
) -> Result<Vec<u8>> {
    info!("torch_call: creation: {:?}", fn_req.function);

    info!("torch_call: resolving namespace");
    let namespace = resolve_namespace(py, fn_req.namespace.into())?;
    info!("torch_call: resolved namespace: {:?}", namespace);

    let resolved_fn = namespace.getattr(fn_req.function.as_str())?;

    // Clone ref needed b/c otherwise args and kwargs are consumed
    info!("torch_call: calling {:?}", fn_req.function);
    let args = fn_req.args.clone_ref(py).into_bound(py);

    info!("torch_call: args: {:?}", args);

    info!("torch_call: foreach: {}", is_foreach);
    let args = if is_foreach {
        foreach_rtensor_ids_to_tensors(py, object_cache, &args)?
    } else {
        rtensor_ids_to_robjects(py, object_cache, &args)?
    };

    let kwargs = fn_req.kwargs.clone_ref(py).into_bound(py);
    info!("torch_call: kwargs: {:?}", kwargs);

    let robjects = match resolved_fn.call(args, Some(&kwargs)) {
        Ok(robjects) => robjects,
        Err(e) => {
            info!("torch_call: error calling function: {:?}", e);
            return Ok(Vec::new());
        }
    };
    info!("torch_call: called function, result: {:?}", robjects);

    // TODO: make this pretty
    info!("robjects type: {:?}", robjects.get_type().name()?);

    match robjects.get_type().name()?.to_string().as_str() {
        "tuple" => {
            let mut payloads = Vec::<Bound<'_, PyAny>>::new();
            for i in 0..robjects.len()? {
                let tensor = robjects.get_item(i)?;
                let new_id = Uid::new();

                // Add tensor to object cache
                info!(
                    "torch_call: inserting robject into object cache with id: {:?}",
                    &new_id
                );
                object_cache.insert(new_id.clone(), tensor.to_owned().unbind());
                info!("torch_call: inserted robject into object cache");

                // Return tuple of new_id and empty tensor to client
                payloads.push(empty_tensor_payload(py, new_id)?);
            }

            let result = PyTuple::new_bound(py, &payloads)
                .to_object(py)
                .into_bound(py);
            let result = dump(py, result)?;

            Ok(result)
        }
        "Tensor" | "Module" => {
            let new_id = Uid::new();

            // Add tensor to object cache
            info!(
                "torch_call: inserting robject into object cache with id: {:?}",
                &new_id
            );
            object_cache.insert(new_id.clone(), robjects.to_owned().unbind());
            info!("torch_call: inserted tensor into object cache");

            // Return tuple of new_id and empty tensor to client
            info!("torch_call: returning empty tensor payload");
            dump_empty_payload(py, empty_tensor_payload(py, new_id)?)
        }
        _ => {
            info!("torch_call: output is not an robject, returning output as is");

            dump(py, robjects)
        }
    }
}

fn torch_bool_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    info!("torch_call: bool call: {:?}", fn_req.function);

    info!("torch_call: resolving namespace");
    let namespace = resolve_namespace(py, fn_req.namespace.into())?;
    info!("torch_call: resolved namespace: {:?}", namespace);

    let tensor = namespace.getattr(fn_req.function.as_str())?;

    // Clone ref needed b/c otherwise args and kwargs are consumed
    info!("torch_call: calling {:?}", fn_req.function);

    let args = fn_req.args.clone_ref(py).into_bound(py);
    info!("torch_call: args: {:?}", args);

    let args = rtensor_ids_to_robjects(py, object_cache, &args)?;

    let args = rtensor_ids_to_robjects(py, object_cache, &args)?;

    let kwargs = fn_req.kwargs.clone_ref(py).into_bound(py);
    info!("torch_call: kwargs: {:?}", kwargs);

    let result = match tensor.call(args, Some(&kwargs)) {
        Ok(result) => result,
        Err(e) => {
            info!("torch_call: error calling function: {:?}", e);
            return Ok(Vec::new());
        }
    };
    info!("torch_call: called function, result: {:?}", tensor);

    let result = dump(py, result)?;

    Ok(result)
}

fn cuda_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    Ok(Vec::new())
}

fn nn_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    Ok(Vec::new())
}

fn optim_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    info!("torch_call: optim: {:?}", fn_req.function);

    match fn_req.function.0.as_str() {
        "Adam" => creation_op_call(py, object_cache, fn_req, false),
        _ => unimplemented!(),
    }
}

fn optim_adam_call<'a>(
    py: Python<'a>,
    object_cache: &mut ObjectCache,
    fn_req: FunctionRequest,
) -> Result<Vec<u8>> {
    info!("torch_call: optim_adam: {:?}", fn_req.function);

    match fn_req.function.0.as_str() {
        "zero_grad" => creation_op_call(py, object_cache, fn_req, false),
        "step" => creation_op_call(py, object_cache, fn_req, false),
        _ => unimplemented!(),
    }
}

#[cfg(test)]
mod tensor {
    use pyo3::types::PyList;

    use super::*;

    trait Repr {
        fn rrepr(&self, object_cache: &mut ObjectCache) -> Result<String>;
    }

    impl Repr for Bound<'_, PyAny> {
        fn rrepr(&self, object_cache: &mut ObjectCache) -> Result<String> {
            let repr_args = PyTuple::new_bound(self.py(), &[self.clone()]);
            let repr_kwargs = PyDict::new_bound(self.py());
            let result_repr =
                torch_call_bijected(self.py(), "repr", &repr_args, &repr_kwargs, object_cache)?
                    .extract::<String>()?;

            Ok(result_repr)
        }
    }

    fn init_logs() {
        let subscriber = tracing_subscriber::fmt()
            .compact()
            .with_file(true)
            .with_line_number(true)
            .with_target(false)
            // .without_time()
            .finish();
        if let Ok(should_log) = std::env::var("CARAVANCLOUD_LOG") {
            if should_log == "1" {
                let _ = tracing::subscriber::set_global_default(subscriber);
            }
        }
    }

    fn torch_call_bijected<'a>(
        py: Python<'a>,
        function: &str,
        args: &Bound<'a, PyTuple>,
        kwargs: &Bound<'a, PyDict>,
        object_cache: &mut ObjectCache,
    ) -> Result<Bound<'a, PyAny>> {
        let rtorch_test = include_str!("test/tensor.py");
        let test_mod = PyModule::from_code_bound(py, rtorch_test, "rtorch.py", "rtorch")?;

        let resolved_function = test_mod.getattr(function)?;

        // Get the object name from the function name
        let function_parts = function.split(".").into_iter().collect::<Vec<&str>>();
        let object = if function_parts.len() >= 2 {
            function_parts
                .get(function_parts.len() - 2)
                .map(|&x| x.to_string())
        } else {
            Some("Tensor".into())
        };

        info!("Object: {:?}", object);

        let result = resolved_function
            .call(args, Some(kwargs))?
            .extract::<Vec<u8>>()?;
        let result = handle_bytes(&result, object_cache)?;

        let result = match object {
            Some(object) => test_mod
                .getattr("bytes_to_output")?
                .call1((result, object))?,
            None => test_mod
                .getattr("bytes_to_output")?
                .call1((result, "torch"))?,
        };

        Ok(result.into())
    }

    #[test]
    fn tensor() {
        init_logs();

        let mut object_cache = init_object_cache();

        Python::with_gil(|py| -> PyResult<()> {
            let tensor_kwargs = PyDict::new_bound(py);
            tensor_kwargs.set_item("device", 0)?;
            let tensor_data = PyList::new_bound(py, &[1, 2, 3]);
            let tensor_args = PyTuple::new_bound(py, &[tensor_data]);

            // Expected tensor output
            let torch_mod = py.import_bound("torch")?;
            let expected_tensor = torch_mod
                .getattr("tensor")?
                .call(&tensor_args, Some(&tensor_kwargs))?;
            let expected_repr = expected_tensor.getattr("__repr__")?.call0()?.to_string();

            // Bijected tensor output
            let tensor_result = torch_call_bijected(
                py,
                "tensor",
                &tensor_args,
                &tensor_kwargs,
                &mut object_cache,
            )
            .unwrap()
            .rrepr(&mut object_cache)
            .unwrap();

            assert_eq!(tensor_result, expected_repr);

            Ok(())
        })
        .unwrap();
    }

    #[test]
    fn add() {
        init_logs();

        let mut object_cache = init_object_cache();

        Python::with_gil(|py| -> PyResult<()> {
            let tensor_kwargs = PyDict::new_bound(py);
            tensor_kwargs.set_item("device", 0)?;
            let tensor_data = PyList::new_bound(py, &[1, 2, 3]);
            let tensor_args = PyTuple::new_bound(py, &[tensor_data]);

            let tensor2_data = PyList::new_bound(py, &[4, 5, 6]);
            let tensor2_args = PyTuple::new_bound(py, &[tensor2_data]);

            // Expected tensor output
            let torch_mod = py.import_bound("torch")?;
            let expected_tensor1 = torch_mod
                .getattr("tensor")?
                .call(&tensor_args, Some(&tensor_kwargs))?;
            let expected_tensor2 = torch_mod
                .getattr("tensor")?
                .call(&tensor2_args, Some(&tensor_kwargs))?;
            let expected_tensor = expected_tensor1
                .getattr("__add__")?
                .call1((expected_tensor2,))?;
            let expected_repr = expected_tensor.getattr("__repr__")?.call0()?.to_string();

            // Bijected tensor output
            let tensor1_result = torch_call_bijected(
                py,
                "tensor",
                &tensor_args,
                &tensor_kwargs,
                &mut object_cache,
            )
            .unwrap();

            let tensor2_result = torch_call_bijected(
                py,
                "tensor",
                &tensor2_args,
                &tensor_kwargs,
                &mut object_cache,
            )
            .unwrap();

            let add_args = PyTuple::new_bound(py, &[tensor1_result, tensor2_result]);
            let add_kwargs = PyDict::new_bound(py);
            let tensor_result =
                torch_call_bijected(py, "add", &add_args, &add_kwargs, &mut object_cache)
                    .unwrap()
                    .rrepr(&mut object_cache)
                    .unwrap();

            info!("Expected: {:?}", expected_repr);
            info!("Result: {:?}", tensor_result);

            assert_eq!(tensor_result, expected_repr);

            Ok(())
        })
        .unwrap();
    }
}
