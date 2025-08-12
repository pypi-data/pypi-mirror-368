from __future__ import annotations

from importlib import resources as impresources

import time
import csv
import io
import os
import copyreg
import builtins
import inspect
from enum import Enum
from collections import OrderedDict
from inspect import Signature, Parameter, BoundArguments
from dataclasses import dataclass
from abc import abstractmethod
import typing
from typing import Any, Optional, Union, NewType, Callable, Sequence, Literal
from types import ModuleType, MappingProxyType
import logging

from typeguard import check_type, TypeCheckError

import torch
import numpy

from . import robject
from .robject import (
    Return,
    ReturnType,
    RBuffer,
    RId,
    RObject,
    RFutureTensor,
    RTensor,
    RParameter,
    RemoteCallPayload,
    make_remote_call,
    standardize_device,
)

from .known import known_return_annotations, known_scripts

from torch.types import (
    _dtype,
    _complex,
    _bool,
    _int,
    _layout,
    SymInt,
    _size,
    _device,
    _qscheme,
    _float,
    Number,
)
from torch.return_types import (
    frexp,
    aminmax,
    min,
    max,
    median,
    nanmedian,
    mode,
    kthvalue,
    sort,
    topk,
    cummax,
    cummin,
    geqrf,
    histogram,
    histogramdd,
    lu_unpack,
    qr,
    slogdet,
    svd,
    triangular_solve,
)
from torch import dtype, memory_format, strided, qscheme
from torch import Tensor, Size, Generator
from torch._prims_common import DeviceLikeType
from torch._numpy._dtypes import DType
from torch.nn import Module
from torch.nn.common_types import _size_any_t
from torch.nn.utils.weight_norm import T_module
from torch.nn.utils.rnn import PackedSequence
from torch.jit.annotations import (
    BroadcastingList1,
    BroadcastingList2,
    BroadcastingList3,
)
from torch.serialization import MAP_LOCATION, MAP_PRIVATE, MAP_SHARED
from typing_extensions import TypeIs as _TypeIs

from jedi import Script
from jedi.api.classes import BaseSignature, Name, ParamName

logging.basicConfig(level=logging.WARNING)
logging.getLogger("parso.cache").setLevel(logging.WARNING)
logging.getLogger("parso.python.diff").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# torch type hints use ellipsis in all lowercase lol
class ellipsis: ...


@dataclass
class ParameterizedCall:
    is_remote: bool
    device: int  # Remote device where this Call will be routed
    to_device: int  # Remote device where the results of this Call will be routed
    returns: (
        Return | list[Return]
    )  # Return type of the function to infer RIds for RFutures


def parse_fn(full_fn_name: str) -> tuple[str, str]:
    """Returns namespace, fn_name by splitting at the last dot."""
    splits = full_fn_name.split(".")
    namespace = ".".join(splits[:-1])
    fn_name = splits[-1]
    return namespace, fn_name


def get_known_jedi_signatures(full_fn_name: str) -> list[BaseSignature]:
    known_script = known_scripts.get(full_fn_name)
    if not known_script:
        return []

    script_lines = known_script.splitlines()
    last_def_line_idx = None
    for i, line in reversed(list(enumerate(script_lines))):
        if line[:3] == "def":
            last_def_line_idx = i + 1
            break

    if last_def_line_idx is None:
        return []

    script = Script(known_script)
    inferences: list[Name] = script.infer(last_def_line_idx, 6)

    if inferences:
        signatures: list[BaseSignature] = inferences[0].get_signatures()
        return signatures

    return []


def get_jedi_signatures(
    full_fn_name: str, namespace: str, fn_name: str
) -> list[BaseSignature]:
    signatures: list[BaseSignature] = get_known_jedi_signatures(full_fn_name)
    if len(signatures) > 0:
        return signatures

    code = "import torch\n" + full_fn_name
    script = Script(code)
    # Skip the full namespace but add one char to put cursor on fn
    inferences: list[Name] = script.infer(2, len(namespace) + 1)
    if inferences:
        signatures: list[BaseSignature] = inferences[0].get_signatures()
        return signatures

    return []


def _nested_tensor_from_mask(
    t: Tensor, m: Tensor, mask_check: bool = True
) -> Tensor: ...


def get_signatures(
    full_fn_name: str, jedi_signatures: list[BaseSignature]
) -> list[Signature]:
    """Returns a list of `inspect` Signatures converted from Jedi Signatures."""
    return [to_signature(signature, full_fn_name) for signature in jedi_signatures]


def get_param_type(param: ParamName, full_fn_name: str) -> dict[str, Optional[Any]]:
    if param.name == "self" or param.name == "cls":
        namespace, fn = parse_fn(full_fn_name)
        return {"name": param.name, "kind": param.kind, "annotation": eval(namespace)}

    if param.name == "args":
        return {"name": param.name, "kind": inspect.Parameter.VAR_POSITIONAL}

    if param.name == "kwargs":
        return {"name": param.name, "kind": inspect.Parameter.VAR_KEYWORD}

    description: str = param.description
    colon_loc = description.find(":")
    equal_loc = description.find("=")

    if equal_loc >= 0 and colon_loc >= 0:
        try:
            param_name = description[6:colon_loc]
            annotation_str = description[colon_loc + 2 : equal_loc]
            default = eval(description[equal_loc + 1 :])

            if param_name[0] == "*":
                annotation_str = "Sequence[" + annotation_str + "]"

            annotation = eval(annotation_str)

            if default is ...:
                if annotation is Optional:
                    default = None
                else:
                    try:
                        default = eval(annotation_str + "()")
                    except TypeError:
                        logger.debug(f"default {annotation_str} could not evaluated")
                        default = None

            return {
                "name": param_name,
                "kind": param.kind,
                "annotation": annotation,
                "default": default,
            }
        except NameError as e:
            # TODO: this NameError occurs because we don't have something imported.
            # Solution is to recursively create a set of all objects, types,
            # or functions in the torch namespace

            logger.warning(f"something is not imported (case default given): {e}")
            ...
    elif colon_loc >= 0:
        try:
            param_name = description[6:colon_loc]
            param_kind = param.kind
            annotation_str = description[colon_loc + 2 :]
            if param_name[0] == "*":
                param_name = param_name[1:]
                annotation_str = "Sequence[" + annotation_str + "]"
                param_kind = Parameter.POSITIONAL_OR_KEYWORD
            annotation = eval(annotation_str)
            return {"name": param_name, "kind": param_kind, "annotation": annotation}
        except NameError as e:
            logger.debug(f"something is not imported (case default not given): {e}")
    return {"name": param.name, "kind": param.kind}


def unwrap_rtype(return_annotation: Any, signature: BaseSignature) -> Any:
    if return_annotation is type(None) or return_annotation is None:
        return Return(rtype=ReturnType.FUTURE)

    if type(return_annotation) is str:
        if return_annotation == "Self":
            robject_factory = eval(parse_fn(signature.full_name)[0])
            return Return(rtype=ReturnType.FUTURE, rfactory=robject_factory)
        else:
            return_annotation = eval(return_annotation)

    if return_annotation is type(None) or return_annotation is None:
        return Return(rtype=ReturnType.FUTURE)

    if type(return_annotation) in {
        typing.GenericAlias,
        typing._GenericAlias,
        typing._UnionGenericAlias,
    }:
        return_annotation = typing.get_args(return_annotation)

    # Have to check again based on some internal types being string
    if type(return_annotation) is str:
        return_annotation = eval(return_annotation)

    return_types = []
    if type(return_annotation) is tuple:
        if return_annotation[-1] == ...:
            return_type = unwrap_rtype(return_annotation[0], signature)
            if return_type.rtype == ReturnType.FUTURE:
                return Return(rtype=ReturnType.FUTURE, rfactory=tuple)
            else:
                return Return(rtype=ReturnType.BLOCKER)
        for rtype in return_annotation:
            if rtype is type(None):
                continue
            return_types.append(unwrap_rtype(rtype, signature))
    elif "torch" in str(return_annotation):
        original_annotation = return_annotation.__qualname__
        namespace, original_object = parse_fn(original_annotation)

        if hasattr(robject, "R" + original_object):
            rfactory = eval("R" + original_object)
        else:
            rfactory = eval(original_annotation)

        return Return(
            rtype=ReturnType.FUTURE,
            rfactory=rfactory,
        )
    else:
        return Return(rtype=ReturnType.BLOCKER)

    if len(return_types) == 1:
        return return_types[0]

    return return_types


def get_return_annotation(
    signature: BaseSignature, full_fn_name: str
) -> Return | list[Return]:
    # Known return annotations are needed for PyTorch functions that may have the return
    # type listed in the written documentation but not in the function signature itself.
    # For example, see `torch.broadcast_tensors` for PyTorch 2.7.
    known_return_annotation = known_return_annotations.get(full_fn_name)
    if known_return_annotation is not None:
        return known_return_annotation

    try:
        signature_type_hint = signature.get_type_hint()  # full signature line as a str
    except Exception as e:
        logger.debug(f"Could not get signature's type hint, blocking: {e}")
        return Return(rtype=ReturnType.BLOCKER)

    return_idx = signature_type_hint.find("->")
    if return_idx < 0:
        return Return(rtype=ReturnType.FUTURE)
    return_annotation_str = signature_type_hint[return_idx + 3 :]

    try:
        return unwrap_rtype(return_annotation_str, signature)

    except NameError as e:
        logger.warning(f"{e}, {signature.full_name}")
        return []


def to_signature(signature: BaseSignature, full_fn_name: str) -> Signature:
    parameters = []
    for param in signature.params:
        param: ParamName = param
        annotated_param: dict = get_param_type(param, full_fn_name)
        parameter = Parameter(**annotated_param)
        parameters.append(parameter)

    return_annotation = get_return_annotation(signature, full_fn_name)

    return Signature(parameters=parameters, return_annotation=return_annotation)


def typecheck_arguments(signature: Signature, bound_arguments: BoundArguments):
    typed_arguments: MappingProxyType[str, Parameter] = signature.parameters
    proposed_arguments: dict[str, Any] = bound_arguments.arguments

    for key, proposed_argument in proposed_arguments.items():
        typed_argument: Parameter | None = typed_arguments.get(key)

        if typed_argument is None:
            raise TypeError(f"arguments not bound correctly, {key} not found in types")

        argument_type = typed_argument.annotation

        if argument_type is Any:
            continue

        try:
            check_type(proposed_argument, argument_type)
        except TypeCheckError:
            if key == "self" and isinstance(proposed_argument, RFutureTensor):
                logger.warning("self is an RFuture, continuing type check")
                continue

            raise TypeError(
                f"type of {key}: {proposed_argument} is {type(proposed_argument)} "
                + f"which does not match type hint {argument_type}"
            )


def get_typechecked_arguments(
    full_fn_name: str,
    namespace: str,
    fn_name: str,
    signatures: list[Signature],
    *args,
    **kwargs,
) -> Optional[BoundArguments]:
    for signature in signatures:
        # print()
        # print(signature)
        try:
            bound_arguments: BoundArguments = signature.bind(*args, **kwargs)
            bound_arguments.apply_defaults()
            typecheck_arguments(signature, bound_arguments)
            return bound_arguments
        except TypeError as _e:
            # print(_e)
            # bind or typecheck failed
            continue
    return None


def is_cpu(device_arg: int) -> bool:
    return device_arg == -1


def is_robject(obj: Any) -> bool:
    return isinstance(obj, RObject) or (
        hasattr(obj, "rid") and isinstance(obj.rid, RId)
    )


def get_matching_device(objs: list[RObject]) -> int:
    devices = set([obj.rdevice for obj in objs])

    if len(devices) == 0:
        raise AttributeError(
            "must provide at least one RObject to find a matching device"
        )

    if len(devices) > 1:
        raise AttributeError(
            f"cannot find a matching device as multiple devices exist: {devices}"
        )

    return standardize_device(devices.pop())


def has_robject(obj: Any) -> bool:
    """
    Checks if this obj contains an RObject by recursing
    through every child. Separate from `get_robjects`
    to allow for shortcut returns if one robject is found.
    """

    if is_robject(obj):
        return True
    if isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            if has_robject(item):
                return True
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if has_robject(value):
                return True
    elif hasattr(obj, "__dict__"):
        for attr_name, attr_value in obj.__dict__.items():
            if has_robject(attr_value):
                return True
    return False


def get_robjects(obj: Any) -> list[RObject]:
    """
    Gets all RObjects by recursing through every child in
    the given object. Inductive hypothesis is that all
    children of an RObject share the same device so we don't
    have to recurse through them.
    """

    if is_robject(obj):
        return [obj]

    robjects = []
    if isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            robjects.extend(get_robjects(item))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            robjects.extend(get_robjects(value))
    elif hasattr(obj, "__dict__"):
        for attr_name, attr_value in obj.__dict__.items():
            robjects.extend(get_robjects(attr_value))
    return robjects


all_returns = set([])


def biject_fn(
    full_fn_name: str, remote_call: Callable, gpu_offsets: list[int]
) -> Callable:
    original_fn: Callable = eval(full_fn_name)
    # TODO: should we raise Error if not Callable?
    namespace, fn_name = parse_fn(full_fn_name)

    jedi_signatures = get_jedi_signatures(full_fn_name, namespace, fn_name)
    signatures = get_signatures(full_fn_name, jedi_signatures)

    # print()
    # print(full_fn_name)
    # for js, s in zip(jedi_signatures, signatures):
    #     ds = js._get_docstring_signature()
    #     ds_arrow = ds.find("->")
    #     if ds_arrow >= 0:
    #         print(ds[ds_arrow + 3 :])

    #     print(s.return_annotation)
    #     if hasattr(s.return_annotation, "rfactory"):
    #         all_returns.add(s.return_annotation.rfactory)
    #     elif type(s.return_annotation) is list:
    #         all_returns.add(tuple(r.rfactory for r in s.return_annotation))
    #     else:
    #         print(s.return_annotation)
    #         pass

    # print()

    def bijected_fn(*args, **kwargs) -> Any:
        bound_arguments: Optional[BoundArguments] = get_typechecked_arguments(
            full_fn_name,
            namespace,
            fn_name,
            signatures,
            *args,
            **kwargs,
        )

        # print()
        # print(full_fn_name)

        signature = None
        if len(signatures) == 1:
            signature = signatures[0]

        parameterized_call = get_parameterized_call(
            bound_arguments, signature, gpu_offsets, *args, **kwargs
        )

        match parameterized_call:
            case ParameterizedCall(is_remote=False):
                return original_fn(*args, **kwargs)
            case ParameterizedCall(
                is_remote=True,
                device=device,
                to_device=to_device,
                returns=returns,
            ):
                return make_remote_call(
                    remote_call, full_fn_name, to_device, args, kwargs, device, returns
                )

    return bijected_fn


def biject_property(
    namespace: str,
    property_names: list[str],
    remote_call: Callable,
    gpu_offsets: list[int],
) -> tuple[Callable, Callable]:
    """
    Properties need to be bijected through their getattribute and setattr
    functions. We return the bijected versions of these two functions.
    """
    object_namespace, object_class = parse_fn(namespace)
    remote_object_class = eval("R" + object_class)

    original_setattr_name = namespace + ".__setattr__"
    original_setattr = eval(original_setattr_name)

    remote_setattr = biject_fn(original_setattr_name, remote_call, gpu_offsets)

    def bijected_setattr(obj: Any, name: str, value: Any):
        """
        setattr is alias for __setattr__ and is called whenever `obj.<prop> = <val>`
        is found. It is only enabled for attributes we care about (e.g. Tensor.grad).
        """
        if isinstance(obj, remote_object_class):
            for property_name in property_names:  # should be set
                if name == property_name:
                    # print(f"remote setattr: {name}")
                    remote_setattr(obj, name, value)
        # print(f"local setattr: {name}")
        original_setattr(obj, name, value)

    original_getattribute_name = namespace + ".__getattribute__"
    original_getattribute = eval(original_getattribute_name)

    remote_getattribute = biject_fn(
        original_getattribute_name, remote_call, gpu_offsets
    )

    def bijected_getattribute(obj: Any, name: str) -> Any:
        for property_name in property_names:
            if name == property_name and isinstance(obj, remote_object_class):
                # print(f"remote getattr: {name}")
                return remote_getattribute(obj, name)
        # print(f"local getattr: {name}")
        return original_getattribute(obj, name)

    return bijected_setattr, bijected_getattribute


def map_device_to_offset(
    device_arg: int,
    bound_arguments: Optional[BoundArguments],
    gpu_offsets: list[int],
    *args,
    **kwargs,
) -> tuple[tuple[Any], dict[str, Any]]:
    if device_arg >= len(gpu_offsets):
        raise RuntimeError(
            "CUDA error: invalid device ordinal "
            "(have you allocated enough Caravan GPUs?)"
        )

    if not bound_arguments:
        return args, kwargs

    for i, (param_name, param) in enumerate(
        bound_arguments.signature.parameters.items()
    ):
        if i >= len(args) or param.kind in (
            inspect.Parameter.VAR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            break

        try:
            _arg = bound_arguments.arguments[param_name]
        except KeyError:
            # end of positional arguments
            break
        else:
            if param_name == "device" and device_arg != -1:
                args = list(args)
                args[i] = gpu_offsets[device_arg]
                args = tuple(args)

    if kwargs.get("device") and device_arg != -1:
        kwargs["device"] = gpu_offsets[device_arg]

    return args, kwargs


def get_parameterized_call(
    bound_arguments: Optional[BoundArguments],
    signature: Optional[Signature],
    gpu_offsets: list[int],
    *args,
    **kwargs,
) -> ParameterizedCall:
    # If we cannot typecheck the arguments against the derived function signature,
    # we should just assume that the device argument is not provided.
    # In this instance, we will simply check for the RObject conditions, in which case
    # a remote call will be tried and a remote error can be returned if the function
    # does not resolve remotely.
    if bound_arguments is None:
        # print("bound args are None")
        device_arg = None

        if signature is not None:
            returns = signature.return_annotation
        else:
            returns = None
    else:
        # print("bound args are not None")
        device_arg: DeviceLikeType = bound_arguments.arguments.get("device")
        returns = bound_arguments.signature.return_annotation
        # print(bound_arguments.signature)

    has_device = device_arg is not None
    if has_device:
        device_arg: int = standardize_device(device_arg)
        if device_arg != -1:
            args, kwargs = map_device_to_offset(
                device_arg, bound_arguments, gpu_offsets, *args, **kwargs
            )

    robjects: list[RObject] = []
    for arg in args:
        robjects.extend(get_robjects(arg))
    for key, value in kwargs.items():
        robjects.extend(get_robjects(value))

    has_robjects = False
    if len(robjects) > 0:
        has_robjects = True

    if has_device:
        if is_cpu(device_arg) and has_robjects:
            logger.debug(
                "called with cpu AND with robjects => route call to device matches"
            )

            matched_device: int = get_matching_device(robjects)
            return ParameterizedCall(
                is_remote=True,
                device=matched_device,
                to_device=-1,
                returns=Return(rtype=ReturnType.BLOCKER),
            )
        elif is_cpu(device_arg):
            logger.debug(
                "called with cpu AND with no robjects => call original function"
            )

            return ParameterizedCall(
                is_remote=False,
                device=device_arg,
                to_device=-1,
                returns=Return(rtype=ReturnType.BLOCKER),
            )
        elif has_robjects:
            logger.debug(
                "called with rdevice AND with robjects => route call if device matches"
            )

            matched_device: int = get_matching_device(robjects)
            if matched_device != device_arg:
                # TODO: need to support moving objects between devices
                raise AttributeError(
                    f"matched device {matched_device} from arg RObjects does not match "
                    + f"device arg {device_arg}"
                )
            # TODO: this has matched_device for device and to_device, ideally
            # the above case gets resolved and these will not be the same.
            return ParameterizedCall(
                is_remote=True,
                device=matched_device,
                to_device=matched_device,
                returns=returns,
            )
        else:
            logger.debug("called with rdevice AND with no robjects => route call")
            return ParameterizedCall(
                is_remote=True,
                device=device_arg,
                to_device=device_arg,
                returns=returns,
            )

    if has_robjects:
        logger.debug(
            "called without rdevice AND with robjects => route call if device matches"
        )
        matched_device: int = get_matching_device(robjects)
        return ParameterizedCall(
            is_remote=True,
            device=matched_device,
            to_device=matched_device,
            returns=returns,
        )

    logger.debug(
        "called without rdevice AND without robjects => call original function"
    )
    return ParameterizedCall(
        is_remote=False,
        device=device_arg,
        to_device=device_arg,
        returns=Return(rtype=ReturnType.BLOCKER),
    )


def recurse_module_dir(module_name: str):
    # TODO: recurse through submodules, use type(submodule)
    module = eval(module_name)
    found_types = set()
    for module_dir in dir(module):
        full_submodule_name = str(module_name) + "." + str(module_dir)
        full_submodule = eval(full_submodule_name)

        if callable(eval(full_submodule_name)):
            logger.debug(full_submodule_name)
            logger.debug(type(full_submodule))
            found_types.add(type(full_submodule))

    logger.debug(found_types)


def get_object_dir(obj: str, exceptions: list[str]) -> list[str]:
    resolved_obj = eval(obj)

    subobjs = []
    for subobj in dir(resolved_obj):
        full_fn_name = obj + "." + subobj
        if callable(eval(full_fn_name)):
            if not any([exception in subobj for exception in exceptions]):
                subobjs.append(full_fn_name)

    return subobjs


def patch(
    _remote_call: Callable[[RemoteCallPayload, int], bytes], _gpu_offsets: list[int]
):
    from . import bijections

    global remote_call
    remote_call = _remote_call
    robject.remote_call = _remote_call

    # Needed so that module.to() will swap parameter data instead of assigning
    torch.__future__.set_overwrite_module_params_on_conversion(True)
    torch._has_compatible_shallow_copy_type = lambda tensor, other: True

    # TODO: need to package the csv correctly
    apply_list = []
    biject_file = impresources.files(bijections) / "torch.csv"
    with biject_file.open("r") as f:
        biject_reader = csv.reader(f)
        for row in biject_reader:
            apply_list.extend(row)

    properties: dict[str, list[str]] = {}

    for full_fn_name in apply_list:
        try:
            namespace, fn_name = parse_fn(full_fn_name)
            if callable(eval(full_fn_name)):
                bijected_fn = biject_fn(full_fn_name, _remote_call, _gpu_offsets)
                setattr(eval(namespace), fn_name, bijected_fn)
            else:
                property_name = fn_name
                namespace_properties = properties.setdefault(namespace, [])
                namespace_properties.append(property_name)
        except Exception as e:
            logging.error(f"Could not biject {full_fn_name}: {e}")
            raise e

    for namespace, property_names in properties.items():
        try:
            bijected_setattr, bijected_getattr = biject_property(
                namespace, property_names, _remote_call, _gpu_offsets
            )

            setattr(eval(namespace), "__setattr__", bijected_setattr)
            setattr(eval(namespace), "__getattribute__", bijected_getattr)
        except Exception as e:
            logging.error(f"Could not biject {namespace}, {property_name}: {e}")

    # print(all_returns)
    # print("done patching!")
