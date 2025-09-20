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


# print(1.0)
# print(2)
# a = input()
# b = input()
# print(a - b)
TEST1 = """\
LOAD_CONST 1.0
PRINT
LOAD_CONST 2
PRINT
INPUT_NUMBER
STORE_VAR "a"
INPUT_NUMBER
STORE_VAR "b"
LOAD_VAR "b"
LOAD_VAR "a"
SUB
PRINT
"""

def test1():
    code = parse_string(TEST1)
    inp = [8.0, 5.0]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert isinstance(io.out_buffer[0], float)
    assert isinstance(io.out_buffer[1], int)
    assert isinstance(io.out_buffer[2], float)
    assert len(stack) == 0
    assert int(sum(io.out_buffer)) == 6, io.out_buffer


# print("Hello, World!")
TEST2 = """\
INPUT_STRING
PRINT
"""

def test2():
    code = parse_string(TEST2)
    inp = ["Hello, World!"]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert io.out_buffer[0] == inp[0], io.out_buffer
    assert len(stack) == 0