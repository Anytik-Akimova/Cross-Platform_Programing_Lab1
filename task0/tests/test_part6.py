import copy 

from xvm.vm import VM, parse_string

class MyIO:
    def __init__(self, in_buffer):
        self.in_buffer = copy.deepcopy(in_buffer)
        self.out_buffer = []
    
    def print_fn(self, obj):
        print(obj)
        self.out_buffer.append(obj)

    def input_fn(self, obj):
        a = self.in_buffer.pop(0)
        return a


# function foo(a, b):
#   c = a + b
#   d = b - a
#   return c * d
#
# $entrypoint$:
# a = input()
# b = input()
# c = foo(a, b)
# print(c)
TEST1_FOO = """\
STORE_VAR "b"
STORE_VAR "a"

LOAD_VAR "a"
LOAD_VAR "b"
ADD
STORE_VAR "c"

LOAD_VAR "a"
LOAD_VAR "b"
SUB
STORE_VAR "d"

LOAD_VAR "c"
LOAD_VAR "d"
MUL
RET
"""

TEST1_ENTRY = """\
INPUT_NUMBER
STORE_VAR "a"
INPUT_NUMBER
STORE_VAR "b"

LOAD_VAR "a"
LOAD_VAR "b"
LOAD_CONST "foo"
CALL

STORE_VAR "c"
LOAD_VAR "c"
PRINT
"""

def test1():
    code_foo = parse_string(TEST1_FOO)
    code_entry = parse_string(TEST1_ENTRY)
    code = {
        "foo": code_foo,
        "$entrypoint$": code_entry,
    }
    inp = [3, 5]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert io.out_buffer[0] == (3 + 5)*(5 - 3)
    assert variables["a"] == 3
    assert variables["b"] == 5
    assert "d" not in variables
    assert len(stack) == 0


# function fibonacci(n):
#    if n <= 0:
#        print("Incorrect input")
#        return -1
#    elif n == 1:
#        return 0
#    elif n == 2:
#        return 1
#    else:
#        return fibonacci(n-1) + fibonacci(n-2)
#
# $entrypoint$:
#     N = input()
#     FibNumber = fibonacci(N)
#     print(FibNumber)
TEST2_FIBONACCI = """\
STORE_VAR "n"

LABEL if
LOAD_CONST 0
LOAD_VAR "n"
GT
CJMP elif

LABEL elif
LOAD_CONST 1
LOAD_VAR "n"
NEQ
CJMP elif2

LOAD_CONST 0
RET

LABEL elif2
LOAD_CONST 2
LOAD_VAR "n"
NEQ
CJMP else

LOAD_CONST 1
RET

LABEL else

LABEL fibonacci(n-1)
LOAD_CONST 1
LOAD_VAR "n"
SUB
LOAD_CONST "fibonacci"
CALL

LABEL fibonacci(n-2)
LOAD_CONST 2
LOAD_VAR "n"
SUB
LOAD_CONST "fibonacci"
CALL

ADD
RET

LABEL after_if_unreachable
RET
"""

TEST2_ENTRY = """\
INPUT_NUMBER
STORE_VAR "N"
LOAD_VAR "N"
LOAD_CONST "fibonacci"
CALL

STORE_VAR "FibNumber"
LOAD_VAR "FibNumber"
PRINT
"""

def test2():
    code_fibonacci = parse_string(TEST2_FIBONACCI)
    code_entry = parse_string(TEST2_ENTRY)
    code = {
        "fibonacci": code_fibonacci,
        "$entrypoint$": code_entry,
    }
    inp = [11]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert io.out_buffer[0] == 55
    assert variables["FibNumber"] == 55
    assert "n" not in variables
    assert variables["N"] == 11
    assert len(stack) == 0