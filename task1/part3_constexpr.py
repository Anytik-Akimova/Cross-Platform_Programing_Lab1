import math
import ast
import inspect
import textwrap

#############################################
#############################################
# YOUR CODE BELOW
#############################################

#helper func: check if node is const expr
def is_const_expr(node):
    #check if simply constants
    if isinstance(node, ast.Constant):
        return True
    #check if its actually an unary op
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)) and is_const_expr(node.operand):
        return True
    if isinstance(node, ast.BinOp) and is_const_expr(node.left) and is_const_expr(node.right):
        return True
    return False

#helper func: evaluate const expr as a separate tree
def eval_const_expr(node):
    expr = ast.Expression(body=node)
    ast.fix_missing_locations(expr)
    return eval(compile(expr, "<const-expr>", "eval"), {}, {})

# Implement `constexpr` and `eval_const_exprs`
def constexpr(func):
    def modified_function(*args, **kwargs):
        return func(*args, **kwargs)
    modified_function.is_marked_constexpr = True
    return modified_function


def eval_const_exprs(func):
    original = inspect.unwrap(func)

    #create the ast
    source = inspect.getsource(original)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    #create 'environment' (with closure and globals)
    #to access other functions
    cv = inspect.getclosurevars(original)
    env = dict(func.__globals__)
    env.update(cv.globals)
    env.update(cv.nonlocals)

    #find the target function and remove its decorators
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
            target_fn = node
            target_fn.decorator_list = []
            break

    #flag for multiple passes (nested functional expressions)
    changed = True

    #iterate
    while changed:
        changed = False
        for node in ast.walk(target_fn): 
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                func_name = node.func.id
                func_obj = env.get(func_name)
                #if not found in env
                if not func_obj:
                    continue
                if getattr(func_obj, "is_marked_constexpr", False):
                    if all(is_const_expr(arg) for arg in node.args):
                        values = [eval_const_expr(arg) for arg in node.args]
                        result = func_obj(*values)
                        node.__class__ = ast.Constant
                        node.value = result
                        #remove unneeded attributes of modified node
                        for attr in ('func', 'args', 'keywords'):
                            if hasattr(node, attr):
                                delattr(node, attr)
                        changed = True  

    #fix after manual modifications
    ast.fix_missing_locations(target_fn)

    #compile function as a module
    func_module = ast.Module(body=[target_fn], type_ignores=[])
    ast.fix_missing_locations(func_module)

    code = compile(func_module, " ", "exec")

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
test_advanced()
