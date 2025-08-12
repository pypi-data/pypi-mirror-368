import base64
from typing import Tuple


def dumps_user_data(serialized_context: bytes, serialized_secret_key: Tuple[bytes, bytes], serialized_homseq: bytes):
    return {
        'serialized_context': base64.b64encode(serialized_context).decode('utf-8'),
        'serialized_secret_key': [base64.b64encode(serialized_secret_key[0]).decode('utf-8'),
                                  base64.b64encode(serialized_secret_key[1]).decode('utf-8')],
        'serialized_homseq': base64.b64encode(serialized_homseq).decode('utf-8')
    }


def loads_user_data(user_data: dict) -> Tuple[bytes, Tuple[bytes, bytes], bytes]:
    serialized_context = base64.b64decode(user_data['serialized_context'])
    serialized_secret_key = (
        base64.b64decode(user_data['serialized_secret_key'][0]),
        base64.b64decode(user_data['serialized_secret_key'][1])
    )
    serialized_homseq = base64.b64decode(user_data['serialized_homseq'])
    return serialized_context, serialized_secret_key, serialized_homseq
