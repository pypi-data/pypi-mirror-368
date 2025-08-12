# -*- coding: utf-8 -*-
#
# Copyright (c) 2022~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import hashlib
import io
import os
import pathlib
from typing import Callable, Optional, Union


def get_gcid_piece_size(file_size: int) -> int:
    piece_size = 0x40000
    while file_size / piece_size > 0x200 and piece_size < 0x200000:
        piece_size = piece_size << 1
    return piece_size


ProgressCallbackType = Callable[[int, int], None]

def get_gcid_digest(fp: io.BufferedIOBase, fp_size: int, *,
        progress_callback: Optional[ProgressCallbackType]=None) -> bytes:
    '''
    Compute GCID from `fp`.
    '''

    if progress_callback is None:
        def progress_callback(_: object, __: object, /) -> None:
            pass

    # modified from https://binux.blog/2012/03/hash_algorithm_of_xunlei/

    h = hashlib.sha1()

    piece_size = get_gcid_piece_size(fp_size)

    buf = bytearray(piece_size)  # Reusable buffer to reduce allocations.
    buf_view = memoryview(buf)
    read_size_sum = 0
    while read_size := fp.readinto(buf):
        read_size_sum += read_size
        if read_size_sum > fp_size:
            raise ValueError('visit unexpected data.')
        h.update(hashlib.sha1(buf_view[:read_size]).digest())
        progress_callback(read_size_sum, fp_size)

    if fp_size != read_size_sum:
        raise ValueError('stream end too early.')

    return h.digest()


def get_file_gcid_digest(path: Union[str, pathlib.Path], *,
        progress_callback: Optional[ProgressCallbackType]=None) -> bytes:
    '''
    Compute GCID from file `path`.
    '''
    with open(path, 'rb') as fp:
        return get_gcid_digest(fp, os.path.getsize(path),
            progress_callback=progress_callback)


__all__ = [
    'get_gcid_piece_size',
    'get_gcid_digest',
    'get_file_gcid_digest'
]
