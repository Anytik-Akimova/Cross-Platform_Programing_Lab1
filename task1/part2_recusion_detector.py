import ast
import inspect
import textwrap

#############################################
#############################################
# YOUR CODE BELOW
#############################################

#helper func: get aliases in a tree
def find_aliases(tree, func_name):
    aliases = {func_name}  

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Name) and node.value.id == func_name:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        aliases.add(target.id)
    
    return aliases

#helper func: find func names in a tree 
def find_func(tree, aliases):
    called_funcs = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            #check for simple/aliased recursion
            if node.func.id in aliases:
                return True, called_funcs  
            #write any other funcs 
            else:
                called_funcs.add(node.func.id)
    
    return False, called_funcs

#helper func: recursively traverse sub-funcs
def traverse_funcs(func_name, called_funcs, visited_funcs, closure_vars, aliases):

    for cfunc in called_funcs:
        #if func was visited already, skip 
        if cfunc in visited_funcs:
            continue
        
        #add to visited funcs
        visited_funcs.add(cfunc)

        try:
            cfunc_obj = closure_vars[cfunc]
        except Exception as e:
            print(f"Internal funcs error")
        
        #get tree and locals 
        source = inspect.getsource(cfunc_obj)
        source = textwrap.dedent(source)
        tree = ast.parse(source)
        closure_vars_inner = inspect.getclosurevars(cfunc_obj).nonlocals

        #get new aliases, if any (of original function)
        aliases_internal = find_aliases(tree, func_name)
        aliases = aliases.union(aliases_internal)

        #traverse this tree 
        fl, called_funcs = find_func(tree, aliases)
        if fl == True:
            return True
                
        if called_funcs:
            fl = traverse_funcs(func_name, called_funcs, visited_funcs, closure_vars_inner, aliases)
            if fl == True:
                return True

    return False

# Implement `has_recursion`.
def has_recursion(func):
    #get function source code
    source = inspect.getsource(func)
    #remove irrelevant indentation from nesting
    source = textwrap.dedent(source) 

    #create ast 
    tree = ast.parse(source)

    #for mutual recursion
    closure_vars = inspect.getclosurevars(func).nonlocals

    #first, get all aliases
    func_name = func.__name__
    aliases = find_aliases(tree, func_name)

    #second, find calls to function/aliases
    fl, called_funcs = find_func(tree, aliases)
    if fl == True:
        return True
    
    #check any called funcs
    if called_funcs:
        fl = traverse_funcs(func_name, called_funcs, set(), closure_vars, aliases)
        if fl == True:
            return True

    return False

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
