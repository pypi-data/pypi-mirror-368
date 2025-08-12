import ctypes
import torch
from lattica_query.serialization import generic_pb2

_ser_dtype_map = {
    torch.int32: generic_pb2.DataType.INT32,
    torch.int64: generic_pb2.DataType.INT64,
    torch.float32: generic_pb2.DataType.FLOAT,
    torch.float64: generic_pb2.DataType.DOUBLE,
    torch.complex64: generic_pb2.DataType.COMPLEX_FLOAT,
    torch.complex128: generic_pb2.DataType.COMPLEX_DOUBLE,
    torch.bool: generic_pb2.DataType.BOOL
}

_deser_dtype_map = {
    generic_pb2.DataType.INT32: torch.int32,
    generic_pb2.DataType.INT64: torch.int64,
    generic_pb2.DataType.FLOAT: torch.float32,
    generic_pb2.DataType.DOUBLE: torch.float64,
    generic_pb2.DataType.COMPLEX_FLOAT: torch.complex64,
    generic_pb2.DataType.COMPLEX_DOUBLE: torch.complex128,
    generic_pb2.DataType.BOOL: torch.bool
}

def ser_tensor(tensor, tensor_proto=None):
    if tensor_proto is None:
        tensor_proto = generic_pb2.TensorHolder()

    tensor = tensor.contiguous()
    tensor_proto.dtype = _ser_dtype_map[tensor.dtype]
    tensor_proto.sizes.extend(tensor.shape)
    tensor_proto.strides.extend(tensor.stride())
    tensor_proto.data = bytes((ctypes.c_char * tensor.nbytes).from_address(
        tensor.storage().untyped().data_ptr()
    ))
    return tensor_proto


def deser_tensor(tensor_proto, as_str=False):
    if as_str:
        proto = generic_pb2.TensorHolder()
        proto.ParseFromString(tensor_proto)
    else:
        proto = tensor_proto

    if proto.data == b'':
        return None
    dtype = _deser_dtype_map[proto.dtype]
    sizes = list(proto.sizes)
    strides = list(proto.strides)
    tensor = torch.frombuffer(
        proto.data, dtype=dtype).reshape(sizes).as_strided(sizes, strides)

    return tensor