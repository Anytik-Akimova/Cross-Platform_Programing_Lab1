from pathlib import Path
import copy
from xvm.vm import VM, parse_string

DIR = Path(__file__).parent.resolve()

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


def test1():
    JSON_FULL_PATH = DIR / "test_part5_code.json"
    io = MyIO([])
    vm = VM(print_fn=io.print_fn, input_fn=io.input_fn)
    vm.run_code_from_json(str(JSON_FULL_PATH))
    assert io.out_buffer[0] == "Hello, World!"


def test2():
    JSON_1_PATH = DIR / "test_part5_code_p1.json"
    JSON_2_PATH = DIR / "test_part5_code_p2.json"

    io = MyIO([])
    vm = VM(print_fn=io.print_fn, input_fn=io.input_fn)
    vm.run_code_from_json(str(JSON_1_PATH))
    vm.dump_stack("my_stack_state.pkl")
    vm.dump_memory("my_memory_state.pkl")
    
    io = MyIO([])
    vm = VM(print_fn=io.print_fn, input_fn=io.input_fn)
    vm.load_stack("my_stack_state.pkl")
    vm.load_memory("my_memory_state.pkl")
    vm.run_code_from_json(str(JSON_2_PATH))
    assert io.out_buffer[0] == "Hello, World!"