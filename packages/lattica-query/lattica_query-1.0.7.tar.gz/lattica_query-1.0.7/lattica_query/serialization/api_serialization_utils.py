from lattica_query.serialization import serialization_utils


def load_proto_tensor(data: bytes) -> 'Tensor':
    return serialization_utils.deser_tensor(data, as_str=True)


def dumps_proto_tensor(data: 'Tensor') -> bytes:
    return serialization_utils.ser_tensor(data).SerializeToString()
