import lattica_fhe_core as fhe_core

def generate_key(
    serialized_homseq: bytes,
    serialized_context: bytes,
) -> tuple[tuple[bytes, bytes], bytes]:
    return fhe_core.generate_key(serialized_homseq, serialized_context)


def enc(
    serialized_context: bytes,
    serialized_sk: tuple[bytes, bytes],
    serialized_pt: bytes,
    pack_for_transmission: bool = False,
    n_axis_external: int = None,
) -> bytes:
    return fhe_core.enc(
        serialized_context,
        serialized_sk[0],
        serialized_pt,
        pack_for_transmission,
        n_axis_external,
    )


def dec(
    serialized_context: bytes,
    serialized_sk: tuple[bytes, bytes],
    serialized_ct: bytes,
    as_complex: bool = False,
) -> bytes:
    return fhe_core.dec(serialized_context, serialized_sk[1], serialized_ct, as_complex)


def apply_client_block(
    serialized_block: bytes, 
    serialized_context: bytes, 
    serialized_pt: bytes
) -> bytes:
    return fhe_core.apply_client_block(
        serialized_block, serialized_context, serialized_pt
    )
