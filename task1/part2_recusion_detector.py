import ast
import inspect
import textwrap

#############################################
#############################################
# YOUR CODE BELOW
#############################################

# Implement `has_recursion`.

def has_recursion(func):
    #get function source code
    source = inspect.getsource(func)
    #remove irrelevant inddentation from nesting
    source = textwrap.dedent(source) 

    #create ast 
    tree = ast.parse(source)
    print(ast.dump(tree))

    func_name = func.__name__
    aliases = {func_name}  # track names that refer to the function

    # First pass: find aliases like `alias = func_name`
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Name) and node.value.id == func_name:
                # handle `a = func_name`
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        aliases.add(target.id)

    # Second pass: find any calls to aliases
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in aliases:
                return True  # recursion found

    return False
    #print(func.__name__)

#############################################

def test_simple():
    def func(i):
        if i > 0:
            func(i - 1)
    
    assert has_recursion(func)

    def func():
        return 5
    
    assert not has_recursion(func)

    def factorial(x):
        """This is a recursive function
        to find the factorial of an integer"""

        if x == 1:
            return 1
        else:
            return (x * factorial(x-1))

    assert has_recursion(factorial)
    print("test_simple passed")


def test_coupled():
    def func1(x):
        if x > 0:
            func2(x)
    
    def func2(x):
        if x > 0:
            func1(x)

    def func3(i):
        func1(i)

    assert has_recursion(func1)
    assert has_recursion(func2)
    assert not has_recursion(func3)
    print("test_coupled passed")


def test_big():
    def func1(i, j):
        if i > 0:
            func2(i-1, j)
        else:
            func6()
    
    def func2(i, j):
        if j > 0:
            func3(i, j-1)
        if i > 0:
            func4(i-1, j)

    def func3(i, j, run_func1=False):
        if j > 0:
            func2(i, j)

        if run_func1:
            func1(0, 0)
    
    def func4(i, j):
        if i == 0 and j == 0:
            func1(0, 0, run_func1=True)
        else:
            func5()
    
    def func5():
        """
        func6()
        """
        return

    def func6():
        func5()
    
    assert has_recursion(func1)
    assert has_recursion(func2)
    assert not has_recursion(func5)
    assert not has_recursion(func6)
    assert has_recursion(func3)
    assert has_recursion(func4)
    print("test_big passed")

# Unnecessary test for extra points!
def test_alias():
    def func1(x):
        function_alias = func1
        if x > 0:
            function_alias(x - 1)

    def func2(_):
        function_alias = func2
        return function_alias
    
    assert has_recursion(func1)
    assert not has_recursion(func2)
    print("test_alias passed")

test_simple()
test_coupled()
test_big()
test_alias()
