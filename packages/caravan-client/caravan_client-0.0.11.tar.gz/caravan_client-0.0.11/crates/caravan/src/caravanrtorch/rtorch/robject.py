from __future__ import annotations

from functools import partial
import logging
from abc import abstractmethod
import pickle
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Callable

import torch
from torch._prims_common import DeviceLikeType

logging.basicConfig(level=logging.WARNING)
logging.getLogger("parso.cache").setLevel(logging.WARNING)
logging.getLogger("parso.python.diff").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class RId:
    id: int


class ReturnType(Enum):
    FUTURE = "future"
    BLOCKER = "blocker"


@dataclass
class Return:
    """
    Represents a PyTorch function's return type as a FUTURE or a BLOCKER. If the
    return type is a FUTURE, we optionally provide the object constructor such that
    all future methods and functions resolve correctly. We need to have the RFuture
    object emulate the
    """

    rtype: ReturnType
    rfactory: Optional[str] = None

    def __str__(self) -> str:
        return f"{str(self.rtype.value).capitalize()}({self.rfactory})"

    def __repr__(self) -> str:
        return f"{str(self.rtype.value).capitalize()}({self.rfactory})"


@dataclass
class RemoteCallPayload:
    full_fn_name: str
    rids: list[RId]
    rdevice: int
    args: tuple
    kwargs: dict
    return_types: list[str]

    def dumps(self) -> bytes:
        payload = {
            "full_fn_name": self.full_fn_name,
            "rids": self.rids,
            "rdevice": self.rdevice,
            "args": self.args,
            "kwargs": self.kwargs,
            "return_types": self.return_types,
        }

        bytes_payload = bytes(pickle.dumps(payload))
        return bytes_payload

    def get(self, key: str) -> Any:
        return getattr(self, key)

    def loads(payload: bytes) -> RemoteCallPayload:
        """
        Load a `RemoteCallPayload` from the byte serialization. Note that this is NOT
        meant for a remote call result, but to deserialize any payload serialized
        using `RemoteCallPayload.dumps`.
        """
        payload: dict = pickle.loads(payload)
        return RemoteCallPayload(
            full_fn_name=payload["full_fn_name"],
            rids=payload["rids"],
            rdevice=payload["rdevice"],
            args=payload["args"],
            kwargs=payload["kwargs"],
            return_types=payload["return_types"],
        )


@abstractmethod
def remote_call(payload: RemoteCallPayload, device: int) -> bytes: ...


def make_remote_call(
    remote_call: Callable[[RemoteCallPayload, int], bytes],
    full_fn_name: str,
    to_device: int,
    args: tuple,
    kwargs: dict,
    device: int,
    returns: Return | list[Return],
) -> bytes | None:
    """
    Assuming here that a list of Return will be all Futures for now,
    based on manual check of all torch.csv functions.
    """
    logger.info(
        f"name: {full_fn_name}, to_device: {to_device}, "
        f"device: {device}, returns: {returns}"
    )

    return_types = []

    if isinstance(returns, Return):
        return_types.append(returns.rtype.value)
    else:
        for return_ in returns:
            return_types.append(return_.rtype.value)

    # logger.info(f"parsed return types {return_types}")

    # `rids` is empty here since it gets populated for `RFuture` before being sent
    # by `remote_call`.
    remote_call_payload = RemoteCallPayload(
        full_fn_name=full_fn_name,
        rids=[],
        rdevice=to_device,
        args=args,
        kwargs=kwargs,
        return_types=return_types,
    )

    # if len(args) > 0:
    #     logger.info(
    #         f"parsed return types {remote_call_payload.full_fn_name}, {type(remote_call_payload.args[0])}"
    #     )

    remote_call_result_payload = remote_call(remote_call_payload, device)

    if full_fn_name == "rdrop":
        logger.info("rdrop returning early")
        return

    # logger.info("got result")
    result_bytes = bytes(remote_call_result_payload)
    result = pickle.loads(result_bytes)
    if result is None:
        return None

    if isinstance(returns, Return):
        # logger.info(f"single return type, rid: {result}")
        if returns.rtype == ReturnType.FUTURE:
            # get first and only rid from list
            result = result[0]
        return process_remote_result_for_return(result, returns, to_device)
    else:
        rids: list[int] = result
        # logger.info(f"multiple return types, iterating through rids: {rids}")
        results = []
        for rid, return_ in zip(rids, returns):
            if return_.rtype == ReturnType.FUTURE:
                results.append(
                    process_remote_result_for_return(rid, return_, to_device)
                )

        return results


def process_remote_result_for_return(
    result: Any, return_: Return, to_device: int
) -> Any:
    match return_:
        case Return(rtype=ReturnType.BLOCKER, rfactory=_rfactory):
            # TODO: we are passing in a "device" and a "to_device", where
            # device means where we route the call, and to_device means where
            # the device will put any RObject. But does this just mean cpu?
            if isinstance(result, RObject):
                logger.debug(f"result: {result.rdevice}")  # TODO: temporary

            # If error received, raise the Exception
            if isinstance(result, BaseException):
                raise result

            return result

        case Return(rtype=ReturnType.FUTURE, rfactory=rfactory):
            match str(rfactory):
                case "<class 'rtorch.robject.RTensor'>":
                    return RFutureTensor.rnew(RId(result), rdevice=to_device)
                case "<class 'rtorch.robject.RParameter'>":
                    return RFutureParameter.rnew(RId(result), rdevice=to_device)
                case "None":
                    return RFuture.rnew(RId(result), rdevice=to_device)
                case other:
                    raise NotImplementedError(f"not implemented yet {other}")


class RObject:
    rid: RId
    rdevice: torch.device

    def rnew(self, rid: RId, rdevice: DeviceLikeType | None = None):
        self.rid = rid
        if rdevice is not None:
            if rdevice == -1:
                self.rdevice = torch.device("cpu")
            else:
                self.rdevice = torch.device(rdevice)
        else:
            self.rdevice = None
        return self

    @classmethod
    def cls_rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        instance = cls()
        return instance.rnew(rid, rdevice)

    def __repr__(self):
        if not hasattr(self, "rdevice"):
            return f"RObject[{self.rid}, None]"
        return f"RObject[{self.rid}, {self.rdevice}]"

    # def __del__(self):
    #     if not hasattr(self, "rid"):
    #         return

    #     rdevice = standardize_device(self.rdevice)

    #     try:
    #         make_remote_call(
    #             remote_call=remote_call,
    #             full_fn_name="rdrop",
    #             to_device=-1,
    #             args=(self,),
    #             kwargs={},
    #             device=rdevice,
    #             returns=[Return(rtype=ReturnType.BLOCKER)],
    #         )
    #     except Exception as e:
    #         logger.error(f"could not drop object: {e}")


def standardize_device(device: DeviceLikeType) -> int:
    device = torch.device(device)  # idempotent
    if device.index is None:
        return -1
    else:
        return device.index


class RFuture(RObject):
    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        instance = cls()
        return RObject.rnew(instance, rid, rdevice)

    def __reduce_ex__(self, protocol):
        """
        See `RTensor.__reduce_ex__`
        """
        return (RObject.cls_rnew, (self.rid, self.rdevice))

    def __iter__(self):
        raise NotImplementedError(
            "TODO: block on iteration, RFuture must resolve first"
        )


class RTensor(torch.Tensor, RObject):
    def __reduce_ex__(self, protocol):
        """
        Overrides serialization using `pickle`. Note that `Tensor`
        overrides the serialization process already using `__reduce_ex__`,
        which means we cannot use `__reduce__` as we normally would.
        Additionally, Tensor is based in a new-style C class (e.g. TensorBase),
        which means we cannot make an `__init__` or `__new__` method as
        information for reconstruction using `__new__` gets stored in the
        serialization. To my knowledge (Tejas) as of May 30, this minimizes
        the number of bytes for an `RTensor`, storing only the rid and the
        rdevice.
        """
        return (self.rnew, (self.rid, self.rdevice))

    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None) -> RTensor:
        rtensor = cls()
        return super().rnew(rtensor, rid, rdevice)


class RFutureTensor(RTensor):
    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        instance = cls()
        return RObject.rnew(instance, rid, rdevice)

    def __reduce_ex__(self, protocol):
        """
        See `RTensor.__reduce_ex__`
        """
        return (RObject.cls_rnew, (self.rid, self.rdevice))

    def __iter__(self):
        raise NotImplementedError(
            "TODO: block on iteration, RFuture must resolve first"
        )

    def __del__(self):
        if not hasattr(self, "rid"):
            return

        rdevice = standardize_device(self.rdevice)

        try:
            make_remote_call(
                remote_call=remote_call,
                full_fn_name="rdrop",
                to_device=-1,
                args=(self,),
                kwargs={},
                device=rdevice,
                returns=Return(rtype=ReturnType.FUTURE),
            )
        except Exception as e:
            logger.error(f"could not drop object: {e}")


class RParameter(torch.nn.Parameter, RObject):
    def __reduce_ex__(self, protocol):
        """
        See `RTensor.__reduce_ex__`
        """
        return (self.rnew, (self.rid, self.rdevice))

    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        rparameter = cls()
        return super().rnew(rparameter, rid, rdevice)


class RFutureParameter(RParameter):
    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        instance = cls()
        return RObject.rnew(instance, rid, rdevice)

    def __reduce_ex__(self, protocol):
        """
        See `RTensor.__reduce_ex__`
        """
        return (RObject.cls_rnew, (self.rid, self.rdevice))

    def __iter__(self):
        raise NotImplementedError(
            "TODO: block on iteration, RFuture must resolve first"
        )

    def __del__(self):
        if not hasattr(self, "rid"):
            return

        rdevice = standardize_device(self.rdevice)

        try:
            make_remote_call(
                remote_call=remote_call,
                full_fn_name="rdrop",
                to_device=-1,
                args=(self,),
                kwargs={},
                device=rdevice,
                returns=Return(rtype=ReturnType.FUTURE),
            )
        except Exception as e:
            logger.error(f"could not drop object: {e}")


class RBuffer(torch.nn.Buffer, RObject):
    def __reduce_ex__(self, protocol):
        """
        See `RTensor.__reduce_ex__`
        """
        return (self.rnew, (self.rid, self.rdevice))

    @classmethod
    def rnew(cls, rid: RId, rdevice: DeviceLikeType | None = None):
        rbuffer = cls()
        return super().rnew(rbuffer, rid, rdevice)
