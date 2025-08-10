from __future__ import annotations
from typing import Optional

from .klvm_storage import KLVMStorage


def at(obj: KLVMStorage, position: str) -> Optional[KLVMStorage]:
    """
    Take a string of `f` and `r` characters and follow that path.

    Example:

    ```
    p1 = Program.to([10, 20, 30, [15, 17], 40, 50])
    assert Program.to(17) == at(p1, "rrrfrf")
    ```

    Returns `None` if an atom is hit at some intermediate node.

    ```
    p1 = Program.to(10)
    assert None == at(p1, "rr")
    ```

    """
    v = obj
    for c in position.lower():
        pair = v.pair
        if pair is None:
            return None
        if c == "f":
            v = pair[0]
        elif c == "r":
            v = pair[1]
        else:
            raise ValueError(
                f"`at` got illegal character `{c}`. Only `f` & `r` allowed"
            )
    return v
