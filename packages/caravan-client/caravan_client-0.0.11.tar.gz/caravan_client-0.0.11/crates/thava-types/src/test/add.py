from typing import Optional
from dataclasses import dataclass

import dill

import torch

"""
Protocol for calling remote functions and getting the result:

Calling remote:
function = 
{
    "namespace": <namespace>,
    "function": <function_name>,
    "is_property": <is_property>,
    "self": Optional[<self>],
    "args": <args>,
    "kwargs": <kwargs>
}

<namespace> refers to the module where the function is defined.
<function_name> refers to the name of the function.
<is_property> is a boolean that indicates whether the function is a property.
<self> is the object that the function is called on.
    If `None`, remote creates an object and returns the id.
    Otherwise, <self> is the remote id of the object.
<args> are the arguments passed to the function.
<kwargs> are the keyword arguments passed to the function.
"""

@dataclass
class RTensorId:
    id: int

class RTensor(torch.Tensor):
    id: RTensorId

    def __init__(self, id: RTensorId):
        self.id = id

def torch_bijection(fn_name):
    """Wraps a torch function to biject it to a worker."""
    func_name = str(fn_name)

    def wrapped(id: Optional[int], *args, **kwargs):
        args = list(args)

        # If the argument is an RTensor, replace it with its id
        for i in range(len(args)):
            if isinstance(args[i], RTensor):
                args[i] = args[i].id

        args = tuple(args)
        print(args)

        function = {
            "namespace": "torch",
            "function": func_name,
            "is_property": False,
            "self": None,
            "args": args,
            "kwargs": kwargs
        }

        function_dump = dill.dumps(function)
        
        # Save dump for test
        with open(f'dump/{fn_name}.pkl', 'wb') as f:
            f.write(function_dump)
            print(f"Dumped {fn_name} to {f.name}")
    
    return wrapped

if __name__ == "__main__":
    torch.tensor = lambda *args, **kwargs: torch_bijection("tensor")(None, *args, **kwargs)

    a = torch.tensor([1, 2, 3])
    b = torch.tensor([2, 3, 4])

    c = a + b
