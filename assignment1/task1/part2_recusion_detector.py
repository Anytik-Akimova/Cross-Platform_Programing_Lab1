#############################################
#############################################
# YOUR CODE BELOW
#############################################

# Implement `has_recursion`.

def has_recursion(func):
    print(func.__name__)
    return True

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