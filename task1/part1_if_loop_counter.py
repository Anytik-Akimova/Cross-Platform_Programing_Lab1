import ast
import inspect
import textwrap

#############################################
#############################################
# YOUR CODE BELOW
#############################################

# Implement `my_counter` counting ifs and loops
# NOTE: elif is also considered "if"

def my_counter(func):
    #get function source code
    source = inspect.getsource(func)
    #remove irrelevant inddentation from nesting
    source = textwrap.dedent(source) 

    #create ast 
    tree = ast.parse(source)

    #initialise counter
    num_loops = 0
    num_ifs = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            num_loops += 1
        elif isinstance(node, ast.If):
            num_ifs += 1
    
    def modified_function(*args, **kwargs):
        # run original func
        return func(*args, **kwargs)

    modified_function.num_loops = num_loops
    modified_function.num_ifs = num_ifs

    return modified_function

#############################################


def test_no_loops_ifs():
    @my_counter
    def func(a, b):
        return a + b
    assert func.num_loops == 0, func.num_loops
    assert func.num_ifs == 0, func.num_ifs

def test_ifs():
    @my_counter
    def func(a, b):
        if a > b:
            return a + b
        elif a == b:
            return 0
        else:
            return 1
    assert func.num_loops == 0, func.num_loops
    assert func.num_ifs == 2, func.num_ifs

def test_loops():
    @my_counter
    def func(a, b):
        for i in range(a):
            j = 0
            while j < b:
                j += 1
    assert func.num_loops == 2, func.num_loops
    assert func.num_ifs == 0, func.num_ifs

def test_if_loops():
    @my_counter
    def func(a, b):
        for i in range(a):
            if i < 3:
                j = 0
                var_if = 3
                while j < b:
                    "while i < b"
                    j += 1

    assert func.num_loops == 2, func.num_loops
    assert func.num_ifs == 1, func.num_ifs

def test_big():
    @my_counter
    def func(a, b):
        var = "while"
        if a ** b < 1.0:
            var2 = " if a ** b < 1.0:\n"
            for i in range(a):
                if i < 3:
                    j = 0
                    var = "for i in range(42):"
                    while j < b:
                        j += 1
                elif b == 16:
                    return
        elif a // b == 0:
            while True:
                """
                while True:
                    if i > 88:
                        break
                """
                for i in range(100):
                    if i > 88:
                        break
                break
        else:
            return -3303

    assert func.num_loops == 4, func.num_loops
    assert func.num_ifs == 5, func.num_ifs
