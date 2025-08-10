from typing import List, Optional, Tuple

from .klvm_storage import KLVMStorage

def run_serialized_chik_program(
    program: bytes, environment: bytes, max_cost: int, flags: int
) -> Tuple[int, KLVMStorage]: ...
def deserialize_as_tree(
    blob: bytes, calculate_tree_hashes: bool
) -> Tuple[List[Tuple[int, int, int]], Optional[List[bytes]]]: ...
def serialized_length(blob: bytes) -> int: ...

NO_NEG_DIV: int
NO_UNKNOWN_OPS: int
LIMIT_HEAP: int
MEMPOOL_MODE: int

class LazyNode(KLVMStorage):
    atom: Optional[bytes]

    @property
    def pair(self) -> Optional[Tuple[KLVMStorage, KLVMStorage]]: ...
