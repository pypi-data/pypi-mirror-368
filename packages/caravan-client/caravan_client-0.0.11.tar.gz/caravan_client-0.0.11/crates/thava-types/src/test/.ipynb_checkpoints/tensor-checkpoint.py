from dataclasses import dataclass
from typing import Optional
import dill
import caravancloud
import torch

torch_to = torch.Tensor.to

"""
Protocol for calling remote functions and getting the result:

Calling remote:
function = 
{
    "namespace": <namespace>,
    "function": <function_name>,
    "is_property": <is_property>,
    "object": Optional[<object>],
    "args": <args>,
    "kwargs": <kwargs>
}

<namespace> refers to the module where the function is defined.
<function_name> refers to the name of the function.
<is_property> is a boolean that indicates whether the function is a property.
<object> is the object in the namespace where the function is defined.
    If `None`, remote uses the namespace root.
    Otherwise, <object> is the object in the namespace where the function is defined.
<args> are the arguments passed to the function.
<kwargs> are the keyword arguments passed to the function.
"""

def torch_nontensor_bijection(fn):
    """Wraps a torch function to biject it to a worker."""
    func_name = str(fn.__name__)

    def wrapped(obj: Optional[str], is_property: bool, *args, **kwargs):
        device = None
        if "device" in kwargs:
            if kwargs["device"] != "cpu":
                device = kwargs["device"]

        # We check args even if device is None because we need
        # to check for RTensors in the args which would force
        # a remote call.
        args = list(args)

        args_rdevice = None


        # If the argument is an RTensor, replace it with its id
        for i in range(len(args)):
            if str(type(args[i])) == "<class 'rtorch.RTensor'>":
                curr_arg_rdevice = args[i].rdevice
                args[i] = args[i].id

                # Needed e.g. for zeros_like, which should use the same device as the give tensor
                if args_rdevice is None:
                    args_rdevice = curr_arg_rdevice
                else:
                    assert args_rdevice == curr_arg_rdevice, "All Tensor arguments must be on the same device"
        
        # Intended for a local function call
        if device is None and args_rdevice is None:
            return fn(*args, **kwargs)


        # Intended for a remote function call that transfers tensors across devices
        if device is not None and args_rdevice is not None and device != args_rdevice:
            # TODO: Implement device transfer of tensors
            raise NotImplementedError("Tensor transfers across devices not implemented")
        

        if device is None and args_rdevice is not None:
            device = args_rdevice

        args = tuple(args)

        function = {
            "namespace": "torch",
            "function": func_name,
            "is_property": is_property,
            "object": obj,
            "args": args,
            "kwargs": kwargs
        }

        function_dump = dill.dumps(function)

        return function_dump
    
    return wrapped

def torch_foreach_creation_bijection(fn):
    """Wraps a torch function to biject it to a worker."""
    func_name = str(fn.__name__)

    def wrapped(id: Optional[int], *args, **kwargs):
        device = None
        if "device" in kwargs:
            if kwargs["device"] != "cpu":
                device = kwargs["device"]

        original_args = args

        # We check args even if device is None because we need
        # to check for RTensors in the args which would force
        # a remote call.
        args = list(args)

        args_rdevice = None

        # If the argument is an RTensor, replace it with its id
        for i in range(len(args)):
            if isinstance(args[i], tuple):
                new_args = []
                for j in range(len(args[i])):
                    if isinstance(args[i][j], RTensor):
                        curr_arg_rdevice = args[i][j].rdevice
                        new_args.append(args[i][j].id)

                        # Needed e.g. for zeros_like, which should use the same device as the give tensor
                        if args_rdevice is None:
                            args_rdevice = curr_arg_rdevice
                        else:
                            assert args_rdevice == curr_arg_rdevice, "All Tensor arguments must be on the same device"
                args[i] = tuple(new_args)
        
        # Intended for a local function call
        if device is None and args_rdevice is None:
            return fn(*original_args, **kwargs)

        # Intended for a remote function call that transfers tensors across devices
        if device is not None and args_rdevice is not None and device != args_rdevice:
            # TODO: Implement device transfer of tensors
            raise NotImplementedError("Tensor transfers across devices not implemented")

        if device is None and args_rdevice is not None:
            device = args_rdevice

        args = tuple(args)


        function = {
            "namespace": "torch",
            "function": func_name,
            "is_property": False,
            "object": None,
            "args": args,
            "kwargs": kwargs
        }

        function_dump = dill.dumps(function)

        output = bytes(caravancloud.remote_call(function_dump, device))

        tensor_outs = dill.loads(output)

        tensors = []
        for tensor_pair in tensor_outs:
            id, tensor = tensor_pair
            tensor.__class__ = RTensor
            tensor.id = RId(id)
            tensor.rdevice = device
            tensors.append(tensor)

        return list(tensors)
    
    return wrapped

def torch_creation_bijection(fn):
    """Wraps a torch function to biject it to a worker."""
    func_name = str(fn.__name__)

    def wrapped(namespace: str, obj: Optional[str], is_property: bool, *args, **kwargs):
        device = None
        if "device" in kwargs:
            if kwargs["device"] != "cpu":
                device = kwargs["device"]


        # We check args even if device is None because we need
        # to check for RTensors in the args which would force
        # a remote call.
        args = list(args)

        args_rdevice = None

        # If the argument is an RTensor, replace it with its id
        for i in range(len(args)):
            if str(type(args[i])) == "<class 'rtorch.RTensor'>":
                curr_arg_rdevice = args[i].rdevice
                args[i] = args[i].id

                # Needed e.g. for zeros_like, which should use the same device as the give tensor
                if args_rdevice is None:
                    args_rdevice = curr_arg_rdevice
                else:
                    assert args_rdevice == curr_arg_rdevice, "All Tensor arguments must be on the same device"
        
        # Intended for a local function call
        if device is None and args_rdevice is None:
            return fn(*args, **kwargs)

        # Intended for a remote function call that transfers tensors across devices
        if device is not None and args_rdevice is not None and device != args_rdevice:
            # TODO: Implement device transfer of tensors
            raise NotImplementedError("Tensor transfers across devices not implemented")

        if device is None and args_rdevice is not None:
            device = args_rdevice


        args = tuple(args)

        function = {
            "namespace": namespace,
            "function": func_name,
            "is_property": is_property,
            "object": obj,
            "args": args,
            "kwargs": kwargs
        }


        function_dump = dill.dumps(function)

        # output = bytes(caravancloud.remote_call(function_dump, device))

        # id, tensor = dill.loads(output)

        # tensor.__class__ = RTensor
        # tensor.id = RId(id)
        # tensor.rdevice = device

        return function_dump
    
    return wrapped

def object_from_str(obj: Optional[str]):
    if obj is None:
        return None

    if obj == "Tensor":
        return RTensor
    elif obj == "Module":
        return RModule

def bytes_to_output(output, obj: Optional[str]):
    output = bytes(output)
    output = dill.loads(output)
    

    if isinstance(output, tuple):
        id, tensor = output

        tensor.__class__ = object_from_str(obj)
        tensor.id = RId(id)
        tensor.rdevice = 0

        return tensor
    
    return output

def bytes_to_out1(output):
    output = bytes(output)
    output = dill.loads(output)

    return output


@dataclass
class RId:
    id: int

class RTensor(torch.Tensor):

    rtensor_reshape = torch_creation_bijection(torch.Tensor.reshape)
    rtensor_repr = torch_nontensor_bijection(torch.Tensor.__repr__)
    rtensor_round = torch_creation_bijection(torch.Tensor.round)
    rtensor_float = torch_creation_bijection(torch.Tensor.float)
    rtensor_mean = torch_creation_bijection(torch.Tensor.mean)
    rtensor_add = torch_creation_bijection(torch.Tensor.__add__)
    rtensor_getitem = torch_creation_bijection(torch.Tensor.__getitem__)
    rtensor_is_sparse = torch_nontensor_bijection(torch.Tensor.is_sparse)
    rtensor_pow = torch_creation_bijection(torch.Tensor.__pow__)
    rtensor_mul = torch_creation_bijection(torch.Tensor.__mul__)
    rtensor_clone = torch_creation_bijection(torch.Tensor.clone)
    rtensor_sqrt = torch_creation_bijection(torch.Tensor.sqrt)
    rtensor_to = torch_creation_bijection(torch.Tensor.to)

    
    def reshape(*args, **kwargs):
        return RTensor.rtensor_reshape("torch", "Tensor", False, *args, **kwargs)
    
    def __repr__(*args, **kwargs):
        return RTensor.rtensor_repr("Tensor", False, *args, **kwargs)

    def round(*args, **kwargs):
        return RTensor.rtensor_round("torch", "Tensor", False, *args, **kwargs)

    def float(*args, **kwargs):
        ...
        # return RTensor.rtensor_float("Tensor", False, *args, **kwargs)

    def mean(*args, **kwargs):
        return RTensor.rtensor_mean("torch", "Tensor", False, *args, **kwargs)

    def __add__(*args, **kwargs):
        return RTensor.rtensor_add("torch", "Tensor", False, *args, **kwargs)

    def __getitem__(*args, **kwargs):
        return RTensor.rtensor_getitem("torch", "Tensor", False, *args, **kwargs)

    @property
    def shape(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.shape)(*args, **kwargs)

    @property
    def device(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.device)(*args, **kwargs)
    
    @property
    def grad(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.grad)(*args, **kwargs)

    def is_sparse(*args, **kwargs):
        return RTensor.rtensor_is_sparse("Tensor", False, *args, **kwargs)

    def mul_(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.mul_)(*args, **kwargs)

    def __pow__(*args, **kwargs):
        return RTensor.rtensor_pow("torch", "Tensor", False, *args, **kwargs)

    def __mul__(*args, **kwargs):
        return RTensor.rtensor_mul("torch", "Tensor", False, *args, **kwargs)

    def clone(*args, **kwargs):
        return RTensor.rtensor_clone("torch", "Tensor", False, *args, **kwargs)

    def addcmul_(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.addcmul_)(*args, **kwargs)

    def copy_(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.copy_)(*args, **kwargs)

    def sqrt(*args, **kwargs):
        return RTensor.rtensor_sqrt("torch", "Tensor", False, *args, **kwargs)

    def add_(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.add_)(*args, **kwargs)

    def addcdiv_(*args, **kwargs):
        ...
        # return torch_tensor_bijection(torch.Tensor.addcdiv_)(*args, **kwargs)

    def to(*args, **kwargs):
        return RTensor.rtensor_to("torch", "Tensor", False, *args, **kwargs)


rtorch_tensor = torch_creation_bijection(torch.tensor)
rtorch_zeros = torch_creation_bijection(torch.zeros)
rtorch_zeros_like = torch_creation_bijection(torch.zeros_like)
rtorch_view_as_real = torch_creation_bijection(torch.view_as_real)
rtorch_view_as_complex = torch_creation_bijection(torch.view_as_complex)
rtorch_is_complex = torch_nontensor_bijection(torch.is_complex)
rtorch_maximum = torch_creation_bijection(torch.maximum)
rtorch_foreach_add = torch_foreach_creation_bijection(torch._foreach_add)
rtorch_foreach_add_ = torch_foreach_creation_bijection(torch._foreach_add_)
rtorch_foreach_neg = torch_foreach_creation_bijection(torch._foreach_neg)
rtorch_foreach_lerp = torch_foreach_creation_bijection(torch._foreach_lerp)
rtorch_foreach_mul_ = torch_foreach_creation_bijection(torch._foreach_mul_)
rtorch_foreach_addcmul_ = torch_foreach_creation_bijection(torch._foreach_addcmul_)
rtorch_foreach_pow = torch_foreach_creation_bijection(torch._foreach_pow)
rtorch_foreach_sub_ = torch_foreach_creation_bijection(torch._foreach_sub_)
rtorch_foreach_div_ = torch_foreach_creation_bijection(torch._foreach_div_)
rtorch_foreach_reciprocal = torch_foreach_creation_bijection(torch._foreach_reciprocal)
rtorch_foreach_sqrt_ = torch_foreach_creation_bijection(torch._foreach_sqrt_)
rtorch_foreach_sqrt = torch_foreach_creation_bijection(torch._foreach_sqrt)
rtorch_foreach_maximum_ = torch_foreach_creation_bijection(torch._foreach_maximum_)
rtorch_foreach_addcdiv_ = torch_foreach_creation_bijection(torch._foreach_addcdiv_)

tensor = lambda *args, **kwargs: rtorch_tensor("torch", None, False, *args, **kwargs)
zeros = lambda *args, **kwargs: rtorch_zeros("torch", None, False, *args, **kwargs)
zeros_like = lambda *args, **kwargs: rtorch_zeros_like("torch", None, False, *args, **kwargs)
view_as_real = lambda *args, **kwargs: rtorch_view_as_real("torch", None, False, *args, **kwargs)
view_as_complex = lambda *args, **kwargs: rtorch_view_as_complex("torch", None, False, *args, **kwargs)
is_complex = lambda *args, **kwargs: rtorch_is_complex(None, False, *args, **kwargs)
maximum = lambda *args, **kwargs: rtorch_maximum("torch", None, False, *args, **kwargs)
_foreach_neg = lambda *args, **kwargs: rtorch_foreach_neg(None, *args, **kwargs)
_foreach_add = lambda *args, **kwargs: rtorch_foreach_add(None, *args, **kwargs)
_foreach_add_ = lambda *args, **kwargs: rtorch_foreach_add_(None, *args, **kwargs)
_foreach_lerp = lambda *args, **kwargs: rtorch_foreach_lerp(None, *args, **kwargs)
_foreach_mul_ = lambda *args, **kwargs: rtorch_foreach_mul_(None, *args, **kwargs)
_foreach_addcmul_ = lambda *args, **kwargs: rtorch_foreach_addcmul_(None, *args, **kwargs)
_foreach_pow = lambda *args, **kwargs: rtorch_foreach_pow(None, *args, **kwargs)
_foreach_sub_ = lambda *args, **kwargs: rtorch_foreach_sub_(None, *args, **kwargs)
_foreach_div_ = lambda *args, **kwargs: rtorch_foreach_div_(None, *args, **kwargs)
_foreach_reciprocal = lambda *args, **kwargs: rtorch_foreach_reciprocal(None, *args, **kwargs)
_foreach_sqrt_ = lambda *args, **kwargs: rtorch_foreach_sqrt_(None, *args, **kwargs)
_foreach_sqrt = lambda *args, **kwargs: rtorch_foreach_sqrt(None, *args, **kwargs)
_foreach_maximum_ = lambda *args, **kwargs: rtorch_foreach_maximum_(None, *args, **kwargs)
_foreach_addcdiv_ = lambda *args, **kwargs: rtorch_foreach_addcdiv_(None, *args, **kwargs)

rtensor_reshape = torch_creation_bijection(torch.Tensor.reshape)
rtensor_repr = torch_nontensor_bijection(torch.Tensor.__repr__)
rtensor_round = torch_creation_bijection(torch.Tensor.round)
rtensor_float = torch_creation_bijection(torch.Tensor.float)
rtensor_mean = torch_creation_bijection(torch.Tensor.mean)
rtensor_add = torch_creation_bijection(torch.Tensor.__add__)
rtensor_getitem = torch_creation_bijection(torch.Tensor.__getitem__)
rtensor_is_sparse = torch_nontensor_bijection(torch.Tensor.is_sparse)
rtensor_pow = torch_creation_bijection(torch.Tensor.__pow__)
rtensor_mul = torch_creation_bijection(torch.Tensor.__mul__)
rtensor_clone = torch_creation_bijection(torch.Tensor.clone)
rtensor_sqrt = torch_creation_bijection(torch.Tensor.sqrt)
rtensor_to = torch_creation_bijection(torch.Tensor.to)

repr = lambda *args, **kwargs: rtensor_repr("Tensor", False, *args, **kwargs)
add = lambda *args, **kwargs: rtensor_add("Tensor", False, *args, **kwargs)

rmodule_to = torch_creation_bijection(torch.nn.Module.to)

torch.nn.Module.to = lambda *args, **kwargs: rmodule_to("torch.nn", "Module", False, *args, **kwargs)
