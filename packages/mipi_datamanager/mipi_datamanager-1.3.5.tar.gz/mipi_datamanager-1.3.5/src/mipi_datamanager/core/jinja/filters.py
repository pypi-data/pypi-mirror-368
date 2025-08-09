def inclause(value: list, set_op = False) -> str:
    clause = ",".join([str(v) for v in value])
    res = "(" + clause + ")"
    if set_op:
        op = getattr(value, "op", "IN")
        return op + " " + res
    return res

def inclause_str(value: list, set_op = False) -> str:
    _values = [f"'{v}'" for v in value]
    clause = ",".join(_values)
    res = "(" + clause + ")"
    if set_op:
        op = getattr(value, "op", "IN")
        return op + " " + res
    return res
