from typing import Iterable, List, Sequence, TypeVar, overload, Protocol, runtime_checkable

__all__ = [
    "exc"
]

T = TypeVar("T")

# Anything that can be stringified
class _SupportsStr(Protocol):
    def __str__(self) -> str: ...

# Optional "has op" marker
@runtime_checkable
class _HasOp(Protocol):
    op: str

class _ExcludeList(List[T]):
    op: str = "NOT IN"

@overload
def exc(iterable: Iterable[T], /) -> _ExcludeList[T]: ...
@overload
def exc(*values: T) -> _ExcludeList[T]: ...

def exc(*args):
    """
    exc([1,2,3]) -> ExcludeList[int]
    exc(1,2,3)   -> ExcludeList[int]
    """
    if len(args) == 1 and not isinstance(args[0], (str, bytes)) and isinstance(args[0], Iterable):
        return _ExcludeList(args[0])  # type: ignore[arg-type]
    return _ExcludeList(args)         # type: ignore[arg-type]

def _join(vals: Sequence[_SupportsStr]) -> str:
    return ",".join(str(v) for v in vals)

def _inclause(value: Sequence[_SupportsStr], set_op: bool = False) -> str:
    clause = f"({_join(value)})"
    if set_op:
        op = value.op if isinstance(value, _HasOp) else "IN"
        return f"{op} {clause}"
    return clause

def _inclause_str(value: Sequence[_SupportsStr], set_op: bool = False) -> str:
    clause = "(" + ",".join(f"'{str(v)}'" for v in value) + ")"
    if set_op:
        op = value.op if isinstance(value, _HasOp) else "IN"
        return f"{op} {clause}"
    return clause
