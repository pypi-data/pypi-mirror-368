from .robject import Return, ReturnType, RTensor, RBuffer, RParameter

known_return_annotations = {
    "torch.functional.broadcast_tensors": Return(
        rtype=ReturnType.FUTURE, rfactory=list
    ),
    "torch._C.TensorBase.as_subclass": Return(
        rtype=ReturnType.FUTURE, rfactory=RTensor
    ),
    "torch.is_tensor": Return(rtype=ReturnType.BLOCKER),
    "torch.get_default_device": Return(rtype=ReturnType.BLOCKER),
    "torch.nn.Buffer.__new__": Return(rtype=ReturnType.FUTURE, rfactory=RBuffer),
    "torch.nn.Parameter.__new__": Return(rtype=ReturnType.FUTURE, rfactory=RParameter),
    "torch.Tensor.item": Return(rtype=ReturnType.BLOCKER),
    "torch.nn.Parameter.item": Return(rtype=ReturnType.BLOCKER),
}

known_scripts = {
    "torch._nested_tensor_from_mask": """
import torch

def _nested_tensor_from_mask(
    t: torch.Tensor, 
    m: torch.Tensor, 
    mask_check: bool = True
) -> torch.Tensor: ...""",
    "torch._transformer_encoder_layer_fwd": """
import torch

def _transformer_encoder_layer_fwd(
    src: torch.Tensor,
    embed_dim: int,
    num_heads: int,
    in_proj_weight: torch.Tensor,
    in_proj_bias: torch.Tensor,
    out_proj_weight: torch.Tensor,
    out_proj_bias: torch.Tensor,
    use_gelu: bool,
    norm_first: bool,
    norm_eps: float,
    norm1_weight: torch.Tensor,
    norm1_bias: torch.Tensor,
    norm2_weight: torch.Tensor,
    norm2_bias: torch.Tensor,
    linear1_weight: torch.Tensor,
    linear1_bias: torch.Tensor,
    linear2_weight: torch.Tensor,
    linear2_bias: torch.Tensor,
    merged_mask: Optional[torch.Tensor],
    mask_type: Optional[int],
) -> torch.Tensor:
    ...
""",
    "torch._native_multi_head_attention": """
import torch

def _native_multi_head_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    embed_dim: int,
    num_heads: int,
    in_proj_weight: torch.Tensor,
    in_proj_bias: torch.Tensor,
    out_proj_weight: torch.Tensor,
    out_proj_bias: torch.Tensor,
    key_padding_mask: Optional[torch.Tensor] = None,
    need_weights: bool = True,
    average_attn_weights: bool = True,
    mask_type: int = 1,
) -> tuple[torch.Tensor, Optional[torch.Tensor]]: ...""",
    "torch.nn.functional.max_pool1d": """
import torch
from torch.jit.annotations import BroadcastingList1
from typing import overload, Optional


@overload
def max_pool1d(
    input: torch.Tensor,
    kernel_size: BroadcastingList1[int],
    stride: Optional[BroadcastingList1[int]] = None,
    padding: BroadcastingList1[int] = 0,
    dilation: BroadcastingList1[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:  # noqa: D400
    ...

@overload
def max_pool1d(
    input: torch.Tensor,
    kernel_size: BroadcastingList1[int],
    stride: Optional[BroadcastingList1[int]] = None,
    padding: BroadcastingList1[int] = 0,
    dilation: BroadcastingList1[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> torch.Tensor:
    ...
""",
    "torch.nn.functional.max_pool2d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList2
from typing import overload, Optional


@overload
def max_pool2d(
    input: Tensor,
    kernel_size: BroadcastingList2[int],
    stride: Optional[BroadcastingList2[int]] = None,
    padding: BroadcastingList2[int] = 0,
    dilation: BroadcastingList2[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]:
    ...


@overload
def max_pool2d(
    input: Tensor,
    kernel_size: BroadcastingList2[int],
    stride: Optional[BroadcastingList2[int]] = None,
    padding: BroadcastingList2[int] = 0,
    dilation: BroadcastingList2[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> Tensor: ...
""",
    "torch.nn.functional.max_pool3d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList3
from typing import overload, Optional


@overload
def max_pool3d(
    input: Tensor,
    kernel_size: BroadcastingList3[int],
    stride: Optional[BroadcastingList3[int]] = None,
    padding: BroadcastingList3[int] = 0,
    dilation: BroadcastingList3[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]: ...


@overload
def max_pool3d(
    input: Tensor,
    kernel_size: BroadcastingList3[int],
    stride: Optional[BroadcastingList3[int]] = None,
    padding: BroadcastingList3[int] = 0,
    dilation: BroadcastingList3[int] = 1,
    ceil_mode: bool = False,
    return_indices: bool = False,
) -> Tensor: ...
    """,
    "torch.nn.functional.adaptive_max_pool1d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList1
from typing import overload


@overload
def adaptive_max_pool1d(
    input: Tensor,
    output_size: BroadcastingList1[int],
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]: ...


@overload
def adaptive_max_pool1d(
    input: Tensor,
    output_size: BroadcastingList1[int],
    return_indices: bool = False,
) -> Tensor: ...
""",
    "torch.nn.functional.adaptive_max_pool2d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList2
from typing import overload


@overload
def adaptive_max_pool2d(
    input: Tensor,
    output_size: BroadcastingList2[int],
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]: ...


def adaptive_max_pool2d(
    input: Tensor,
    output_size: BroadcastingList2[int],
    return_indices: bool = False,
) -> Tensor: ...
""",
    "torch.nn.functional.adaptive_max_pool3d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList3
from typing import overload


@overload
def adaptive_max_pool3d(
    input: Tensor,
    output_size: BroadcastingList3[int],
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]: ...


def adaptive_max_pool3d(
    input: Tensor,
    output_size: BroadcastingList3[int],
    return_indices: bool = False,
) -> Tensor: ...
""",
    "torch.nn.functional.fractional_max_pool2d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList3
from typing import overload


@overload
def adaptive_max_pool3d(
    input: Tensor,
    output_size: BroadcastingList3[int],
    return_indices: bool = False,
) -> tuple[Tensor, Tensor]: ...


def adaptive_max_pool3d(
    input: Tensor,
    output_size: BroadcastingList3[int],
    return_indices: bool = False,
) -> Tensor: ...
""",
    "torch.nn.functional.fractional_max_pool3d": """
from torch import Tensor
from torch.jit.annotations import BroadcastingList3
from typing import overload, Optional


@overload
def fractional_max_pool3d(
    input: Tensor,
    kernel_size: BroadcastingList3[int],
    output_size: Optional[BroadcastingList3[int]] = None,
    output_ratio: Optional[BroadcastingList3[float]] = None,
    return_indices: bool = False,
    _random_samples: Optional[Tensor] = None,
) -> tuple[Tensor, Tensor]: ...


@overload
def fractional_max_pool3d(
    input: Tensor,
    kernel_size: BroadcastingList3[int],
    output_size: Optional[BroadcastingList3[int]] = None,
    output_ratio: Optional[BroadcastingList3[float]] = None,
    return_indices: bool = False,
    _random_samples: Optional[Tensor] = None,
) -> Tensor: ...
""",
    "torch.nn.functional.threshold_": """
from torch import Tensor


def _threshold(
    input: Tensor,
    threshold: float,
    value: float,
    inplace: bool = False,
) -> Tensor: ...
""",
    "torch.Tensor.cfloat": """
import torch
from typing import Optional

def cfloat(self, memory_format: Optional[torch.memory_format]) -> torch.Tensor: ...
""",
    "torch.Tensor.cdouble": """
import torch
from typing import Optional

def cdouble(self, memory_format: Optional[torch.memory_format]) -> torch.Tensor: ...
""",
    "torch.Tensor.detach": """
import torch

def detach(self) -> Tensor: ...
""",
    "torch.Tensor.detach_": """
import torch

def detach_(self) -> Tensor: ...
""",
    "torch.nn.Parameter.cfloat": """
import torch
from typing import Optional

def cfloat(self, memory_format: Optional[torch.memory_format]) -> torch.Tensor: ...
""",
    "torch.nn.Parameter.cdouble": """
import torch
from typing import Optional

def cdouble(self, memory_format: Optional[torch.memory_format]) -> torch.Tensor: ...
""",
    "torch.nn.Parameter.detach": """
import torch

def detach(self) -> Tensor: ...
""",
    "torch.nn.Parameter.detach_": """
import torch

def detach_(self) -> Tensor: ...
""",
    "torch.unique": """
import torch
from typing import Optional

def unique(
    input: torch.Tensor, 
    return_inverse: bool = False, 
    return_counts: bool = False, 
    dim: Optional[int] = None
) -> tuple[torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]]:
    ...
""",
    "torch.unique_consecutive": """
import torch
from typing import Optional

def unique_consecutive(
    input: torch.Tensor, 
    return_inverse: bool = False, 
    return_counts: bool = False, 
    dim: Optional[int] = None
) -> tuple[torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]]:
    ...
""",
    "torch.atleast_1d": """
import torch
from typing import overload

@overload
def atleast_1d(tensor: torch.Tensor) -> torch.Tensor: ...
@overload
def atleast_1d(*tensors: torch.Tensor) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.atleast_2d": """
import torch
from typing import overload

@overload
def atleast_2d(tensor: torch.Tensor) -> torch.Tensor: ...
@overload
def atleast_2d(*tensors: torch.Tensor) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.atleast_3d": """
import torch
from typing import overload

@overload
def atleast_3d(tensor: torch.Tensor) -> torch.Tensor: ...
@overload
def atleast_3d(*tensors: torch.Tensor) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.block_diag": """
import torch

def block_diag(*tensors: torch.Tensor) -> torch.Tensor: ...
""",
    "torch.broadcast_tensors": """
import torch

def broadcast_tensors(*tensors: torch.Tensor) -> list[torch.Tensor]: ...
""",
    "torch.broadcast_shapes": """
import torch

def broadcast_shapes(*shapes) -> torch.Size: ...
""",
    "torch.chain_matmul": """
import torch

def chain_matmul(*matrices: torch.Tensor, out: torch.Tensor = None) -> torch.Tensor: ...
""",
    "torch.clip_grad_norm_": """
import torch
from typing import Optional, Iterable, Union

def clip_grad_norm_(
    parameters: Union[torch.Tensor, Iterable[torch.Tensor]],
    max_norm: float,
    norm_type: float = 2.0,
    error_if_nonfinite: bool = False,
    foreach: Optional[bool] = None,
) -> torch.Tensor: ...
""",
    "torch.clip_grad_value_": """
import torch
from typing import Optional, Iterable, Union

def clip_grad_value_(
    parameters: Union[torch.Tensor, Iterable[torch.Tensor]],
    clip_value: float,
    foreach: Optional[bool] = None,
) -> None: ...
""",
    "torch.Tensor.dim_order": """
import torch
from typing import Union

def dim_order(
    self, *, ambiguity_check: Union[bool, list[torch.memory_format]] = False
) -> tuple[int, ...]: ...
""",
    "torch.nn.Parameter.dim_order": """
import torch
from typing import Union

def dim_order(
    self, *, ambiguity_check: Union[bool, list[torch.memory_format]] = False
) -> tuple[int, ...]: ...
""",
    "torch.nn.functional.tanhshrink": """
import torch

def tanhshrink(input: torch.Tensor) -> torch.Tensor: ...
""",
    "torch.nn.functional.softsign": """
import torch

def softsign(input: torch.Tensor) -> torch.Tensor: ...
""",
    "torch.nn.functional.tanh": """
import torch

def tanh(input: torch.Tensor) -> torch.Tensor: ...
""",
    "torch.split": """
import torch
from typing import Union

def split(
    tensor: torch.Tensor,
    split_size_or_sections: Union[int, list[int]],
    dim: int = 0,
) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.Tensor.split": """
import torch
from typing import Union

def split(
    self,
    split_size_or_sections: Union[int, list[int]],
    dim: int = 0,
) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.nn.Parameter.split": """
import torch
from typing import Union

def split(
    self,
    split_size_or_sections: Union[int, list[int]],
    dim: int = 0,
) -> tuple[torch.Tensor, ...]: ...
""",
    "torch.unflatten": """
import torch
from typing import Union, Sequence

def unflatten(
    a: torch.Tensor,
    dim: int,
    sizes: Union[int, Sequence[int]]
) -> torch.Tensor: ...
""",
    "torch.Tensor.unflatten": """
import torch
from typing import Union, Sequence

def unflatten(
    self,
    dim: int,
    sizes: Union[int, Sequence[int]]
) -> torch.Tensor: ...
""",
    "torch.nn.Parameter.unflatten": """
import torch
from typing import Union, Sequence

def unflatten(
    self,
    dim: int,
    sizes: Union[int, Sequence[int]]
) -> torch.Tensor: ...
""",
    "torch.Tensor.backward": """
import torch
from typing import Optional, Sequence

def backward(
    self,
    gradient: Optional[torch.Tensor] = None,
    retain_graph: Optional[bool] = None,
    create_graph: bool = False,
    inputs: Optional[Sequence[torch.Tensor]] = None
) -> None: ...
""",
    "torch.nn.Parameter.backward": """
import torch
from typing import Optional, Sequence

def backward(
    self,
    gradient: Optional[torch.Tensor] = None,
    retain_graph: Optional[bool] = None,
    create_graph: bool = False,
    inputs: Optional[Sequence[torch.Tensor]] = None
) -> None: ...
""",
    "torch.cdist": """
import torch

def cdist(
    x1: torch.Tensor,
    x2: torch.Tensor,
    p: float = 2.0,
    compute_mode: str = "use_mm_for_euclid_dist_if_necessary"
) -> torch.Tensor: ...
""",
    "torch.tensordot": """
import torch
from typing import Optional, Union

def tensordot(
    a: torch.Tensor,
    b: torch.Tensor,
    dims: Union[int, tuple[list[int], list[int]], list[list[int]], torch.Tensor] = 2,
    out: Optional[torch.Tensor] = None
) -> torch.Tensor: ...
""",
    "torch.nn.utils.vector_to_parameters": """
import torch
from typing import Iterable

def vector_to_parameters(
    vec: torch.Tensor,
    parameters: Iterable[torch.Tensor]
) -> None: ...
""",
    "torch.nn.functional.interpolate": """
import torch
from typing import Optional

def interpolate(
    input: torch.Tensor,
    size: Optional[int] = None,
    scale_factor: Optional[list[float]] = None,
    mode: str = "nearest",
    align_corners: Optional[bool] = None,
    recompute_scale_factor: Optional[bool] = None,
    antialias: bool = False,
) -> torch.Tensor: ...
""",
    "torch.nn.functional.upsample": """
import torch
from typing import Optional, Union

def upsample(
    input: torch.Tensor,
    size: Optional[Union[int, tuple[int, ...]]] = None,
    scale_factor: Optional[Union[float, tuple[float, ...]]] = None,
    mode: str = "nearest",
    align_corners: Optional[bool] = None
) -> torch.Tensor: ...
""",
    "torch.nn.functional.upsample_nearest": """
import torch
from typing import Optional, Union

def upsample_nearest(
    input: torch.Tensor,
    size: Optional[Union[int, tuple[int, ...]]] = None,
    scale_factor: Optional[Union[float, tuple[float, ...]]] = None
) -> torch.Tensor: ...
""",
    "torch.nn.functional.upsample_bilinear": """
import torch
from typing import Optional, Union

def upsample_bilinear(
    input: torch.Tensor,
    size: Optional[Union[int, tuple[int, ...]]] = None,
    scale_factor: Optional[Union[float, tuple[float, ...]]] = None
) -> torch.Tensor: ...
""",
    "torch.Tensor.is_shared": """
import torch

def is_shared(self) -> bool: ...
""",
    "torch.Tensor.module_load": """
import torch

def module_load(
    self,
    other: torch.Tensor,
    assign: bool = False
) -> torch.Tensor: ...
""",
    "torch.Tensor.retain_grad": """
import torch

def retain_grad(self) -> None: ...
""",
    "torch.nn.Parameter.is_shared": """
import torch

def is_shared(self) -> bool: ...
""",
    "torch.nn.Parameter.module_load": """
import torch

def module_load(
    self,
    other: torch.Tensor,
    assign: bool = False
) -> torch.Tensor: ...
""",
    "torch.nn.Parameter.retain_grad": """
import torch

def retain_grad(self) -> None: ...
""",
    "torch.optim.Adam.step": """
import torch
from typing import Optional, Callable

def step(self, closure: Optional[Callable[[], torch.Tensor]] = None) -> Optional[torch.Tensor]: ...
""",
    "torch.optim.SGD.step": """
import torch
from typing import Optional, Callable

def step(self, closure: Optional[Callable[[], torch.Tensor]] = None) -> Optional[torch.Tensor]: ...
""",
}
