import math
import ast
import inspect
import textwrap

#############################################
#############################################
# YOUR CODE BELOW
#############################################

#helper functions
def is_const_expr(n):
    #check if simply constants
    if isinstance(n, ast.Constant):
        return True
    #check if its actually an unary op
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)) and isinstance(n.operand, ast.Constant):
        return True
    return False

def eval_const_expr(n):
    expr = ast.Expression(body=n)
    ast.fix_missing_locations(expr)
    return eval(compile(expr, "<const-expr>", "eval"), {}, {})

# Implement `constexpr` and `eval_const_exprs`
def constexpr(func):
    # keep your wrapper and the marker
    def modified_function(*args, **kwargs):
        return func(*args, **kwargs)
    modified_function.is_marked_constexpr = True
    return modified_function


def eval_const_exprs(func):
    original = inspect.unwrap(func)

    source = inspect.getsource(original)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    # ---- build env for folding (globals + closure) ----
    cv = inspect.getclosurevars(original)
    env = dict(func.__globals__)
    env.update(cv.globals)
    env.update(cv.nonlocals)

    # ---- find exactly the function we’re transforming and strip its decorators ----
    target_fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
            node.decorator_list = []             # prevent recursive @eval_const_exprs
            target_fn = node
            break

    if target_fn is None:
        # Fallback if getsource returned only the function (common case)
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef) and n.name == func.__name__:
                target_fn = n
                target_fn.decorator_list = []
                break

    # ---- fold constexpr calls using your existing logic ----
    # --- fold constexpr calls (multi-pass to catch nesting like f(g(...), 3)) ---
    changed = True
    while changed:
        changed = False
        for node in ast.walk(target_fn):  # target_fn is the function node you compiled
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                func_name = node.func.id
                func_obj = env.get(func_name)
                if not func_obj:
                    continue
                if getattr(func_obj, "is_marked_constexpr", False):
                    # use your constant check; below supports UnaryOp like -3
                    if all(is_const_expr(arg) for arg in node.args):
                        values = [eval_const_expr(arg) for arg in node.args]
                        result = func_obj(*values)
                        node.__class__ = ast.Constant
                        node.value = result
                        for attr in ('func', 'args', 'keywords'):
                            if hasattr(node, attr):
                                delattr(node, attr)
                        changed = True  # <-- triggers another pass


    ast.fix_missing_locations(target_fn)

    # ---- compile ONLY the single function we just transformed ----
    mini_mod = ast.Module(body=[target_fn], type_ignores=[])
    ast.fix_missing_locations(mini_mod)

    code = compile(mini_mod, " ", "exec")

    # Use globals + closure as the runtime globals of the recompiled function
    namespace = dict(func.__globals__)
    namespace.update(cv.globals)
    namespace.update(cv.nonlocals)

    exec(code, namespace, namespace)

    new_func = namespace[func.__name__]

    def modified_function(*args, **kwargs):
        return new_func(*args, **kwargs)

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

    print("test_simple passed")


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
    
    print("test_larger passed")


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

    print("test_multi passed")


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

    print("test_advanced passed")

test_simple()
test_larger()
test_multi()
#test_advanced()
