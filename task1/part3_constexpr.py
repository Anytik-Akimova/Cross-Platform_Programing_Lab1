import math

#############################################
#############################################
# YOUR CODE BELOW
#############################################

# Implement `constexpr` and `eval_const_exprs`

def constexpr(func):
    
    def modified_function(*args, **kwargs):
        # run original func
        return func(*args, **kwargs)

    return modified_function


def eval_const_exprs(func):
    
    def modified_function(*args, **kwargs):
        # run original func
        return func(*args, **kwargs)

    return modified_function

#############################################


# Execution Marker is only used for instrumentation
# and tests, do not consider it as a state change. In
# other words, it does not make a pure function "not pure".
class ExecutionMarker:
    def __init__(self):
        self.counter = 0
    def mark(self):
        self.counter += 1
    def reset(self):
        self.counter = 0


def test_simple():
    _m = ExecutionMarker()

    @constexpr
    def f(a, b):
        _m.mark()
        return a + b

    @eval_const_exprs
    def my_function(a):
        return f(3, 6) + f(a, 3)

    _m.reset()
    result = my_function(8)
    assert result == 3+6 + 8+3, f"Res {result}"
    assert _m.counter == 1, _m.counter


def test_larger():
    _m = ExecutionMarker()

    @constexpr
    def f(a, b):
        _m.mark()
        return int(math.exp(b + a))

    @constexpr
    def g(a, b):
        _m.mark()
        return a - b

    @eval_const_exprs
    def my_function(a):
        result = f(-3, 3)
        result = result + f(a, 8)
        return g(result, 2) + g(333, 330)

    _m.reset()
    res = my_function(-8)
    assert res == 3, res
    assert _m.counter == 2, _m.counter


def test_multi():
    _m = ExecutionMarker()

    @constexpr
    def f(a, b):
        _m.mark()
        return int(math.exp(a + b))

    @constexpr
    def g(a, b):
        _m.mark()
        return a - b

    @eval_const_exprs
    def my_function(a):
        result = f(g(0, 3), 3) + g(3, a)
        return result

    _m.reset()
    out = my_function(3)
    assert out == 1, out
    assert _m.counter == 1, _m.counter


# Extra points.
def test_advanced():
    _m = ExecutionMarker()

    @constexpr
    def f(a, b):
        _m.mark()
        return int(math.exp(a + b))

    @eval_const_exprs
    def my_function(a):
        result = f(3 - 3, 0) + f(3, a)
        return result

    _m.reset()
    res = my_function(-3)
    assert res == 2, res
    assert _m.counter == 1, _m.counter