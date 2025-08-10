#!/usr/bin/env python3

from klvm_rs.klvm_rs import run_serialized_chik_program


def run_klvm(fn, env=None):

    program = bytes.fromhex(open(fn, 'r').read())
    if env is not None:
        env = bytes.fromhex(open(env, 'r').read())
    else:
        env = bytes.fromhex("ff80")
    # constants from the main chik blockchain:
    # https://github.com/Chik-Network/chik-blockchain/blob/main/chik/consensus/default_constants.py
    max_cost = 11000000000
    cost_per_byte = 12000

    max_cost -= (len(program) + len(env)) * cost_per_byte
    return run_serialized_chik_program(
        program,
        env,
        max_cost,
        0,
    )


def count_tree_size(tree) -> int:
    stack = [tree]
    ret = 0
    while len(stack):
        i = stack.pop()
        if i.atom is not None:
            ret += len(i.atom)
        elif i.pair is not None:
            stack.append(i.pair[1])
            stack.append(i.pair[0])
        else:
            # this shouldn't happen
            assert False
    return ret

if __name__ == "__main__":
    import sys
    from time import time

    try:
        start = time()
        cost, result = run_klvm(sys.argv[1], sys.argv[2])
        duration = time() - start;
        print(f"cost: {cost}")
        print(f"execution time: {duration:.2f}s")
    except Exception as e:
        print("FAIL:", e.args[0])
        sys.exit(1)
    start = time()
    ret_size = count_tree_size(result)
    duration = time() - start;
    print(f"returned bytes: {ret_size}")
    print(f"parse return value time: {duration:.2f}s")
    sys.exit(0)
