import unittest
from unittest import mock # for mocking input()
import sys
import io
import ast
from pathlib import Path

from run import xvm_debug



UNIT_TEST_CODE = """
function "$entrypoint$"
LOAD_CONST 10
STORE_VAR "a"
LOAD_CONST 20
STORE_VAR "b"
BREAKPOINT
LOAD_VAR "a"
LOAD_VAR "b"
ADD
STORE_VAR "c"
"""


CALL_NEXT_TEST_CODE = """
function "add_ten"
LOAD_CONST 10
ADD
RET

function "$entrypoint$"
LOAD_CONST 5
LOAD_CONST "add_ten"
CALL                 
STORE_VAR "result"   
PRINT
"""




class TestDebugger(unittest.TestCase):

    def setUp(self):
        # create temporary file with test program
        self.test_program_path = Path("unittest_program.xvm")
        with open(self.test_program_path, "w", encoding="utf-8") as f:
            f.write(UNIT_TEST_CODE)
        
        self.mock_stdout = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.mock_stdout
        
    
    
    def CleanUp(self):            
        sys.stdout = self.original_stdout
        if self.test_program_path.exists():
            self.test_program_path.unlink()

    
    
    def run_debugger_with_commands(self, commands):
        input_str = "\n".join(commands)
        with mock.patch('sys.stdin', io.StringIO(input_str)):
            try:
                xvm_debug()
            except SystemExit: # to handle 'exit' command
                pass
            except EOFError: # to handle end of input
                pass
        
        output = self.mock_stdout.getvalue()

        print(f"================================= DEBUGGER OUTPUT from test {self._testMethodName} ================================= ", file=sys.stderr)
        print(output, file=sys.stderr)
        print(f"================================= THE END OF TEST {self._testMethodName} =================================\n\n\n\n", file=sys.stderr)
        sys.stderr.flush()

        return output

    
    def test_load_command(self):

        commands = [
            f"load {self.test_program_path}",
            "list",  
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        
        # 1) Success message
        self.assertIn("File loaded succesfully", output)
        
        # 2) Instruction pointer
        found_pointer_at_start = False
        for line in output.splitlines():
            if "->" in line and "0000:" in line:
                found_pointer_at_start = True
                break
        
        self.assertTrue(
            found_pointer_at_start, 
            "After loading, the instruction pointer should be at the first instruction"
        )


    def test_load_non_existent_file(self):
        non_existent_path = "this_file_does_not_exist_12345.xvm"
        
        commands = [
            f"load {non_existent_path}",
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        
        self.assertIn(f"File not found", output)
    
    
    def test_load_with_no_path(self):
        commands = [
            "load", 
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        self.assertIn(f"Usage: load <path>", output)



    def test_list_start_program_command(self):
        commands = [
            f"load {self.test_program_path}",
            "list",
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        self.assertIn("-> 0000:", output)
        self.assertNotIn("-0001:", output)



    def test_list_middle_program_command(self):
        commands = [
            f"load {self.test_program_path}",
            "step", 
            "step", 
            "step", 
            "list",  
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        self.assertIn("-> 0003:", output)
        self.assertIn("0002:", output) 
        self.assertIn("0004:", output)  




    def test_list_end_program_command(self):
        steps = ["step"] * 9
        
        commands = [f"load {self.test_program_path}"] + steps + ["list", "exit"]
        
        output = self.run_debugger_with_commands(commands)
        self.assertIn("0008:", output)
        self.assertNotIn("->", output, "The pointer should be at the end, no '->' expected")

    


    def test_run_norm_command(self):
        code_without_breakpoint = UNIT_TEST_CODE.replace("BREAKPOINT", "")
        test_path = Path("no_breakpoint_program.xvm")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(code_without_breakpoint)

        commands = [
            f"load {test_path}",
            "run",
            "memory", 
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        test_path.unlink()

        # 1) If the program ran to completion
        self.assertIn("End of program reached", output)
        # 2) Check final variable values
        self.assertIn("c = 30", output, "The variable 'c' should equal 30 after running the program")


    def test_run_without_program_command(self):
        commands = [
            "run",
            "exit"
        ]
        output = self.run_debugger_with_commands(commands)
    
        self.assertIn("No program loaded.", output)
        self.assertNotIn("Stopped at instruction", output)




    def test_run_memory_command(self):
        commands = [
            f"load {self.test_program_path}",
            "run",   
            "memory",
            "exit"
        ]
        output = self.run_debugger_with_commands(commands)
        self.assertIn("Stopped at instruction", output)
        self.assertIn("a = 10", output)
        self.assertIn("b = 20", output)
        self.assertNotIn("c =", output, "The variable 'c' should not be set yet")
    


    def test_step_jump_command(self):
        jmp_test_code = """
        function "$entrypoint$"
        LOAD_CONST 5
        JMP skip_target
        LOAD_CONST 999      
        LABEL skip_target
        STORE_VAR "a"      
        """
        test_path = Path("jmp_test_program.xvm")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(jmp_test_code)

        commands = [
            f"load {test_path}",
            "step", 
            "step",  # Doing step on JMP
            "list",  # Check where the pointer is
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        test_path.unlink()
        pointer_at_target = False
        for line in output.splitlines():
            if "->" in line and "STORE_VAR" in line and "'a'" in line:
                pointer_at_target = True
                break
        
        self.assertTrue(
            pointer_at_target,
            "After stepping over JMP, the instruction pointer should be at 'STORE_VAR \"a\"'"
        )


    def test_step_cjump_false(self):
        cjmp_test_code = """
        function "$entrypoint$"
        LOAD_CONST 0          
        CJMP jump_if_true
        LOAD_CONST 111      
        LABEL jump_if_true
        STORE_VAR "result"
        """
        test_path = Path("cjmp_false_test.xvm")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(cjmp_test_code)

        commands = [
            f"load {test_path}",
            "step",  
            "step",  
            "list",
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        test_path.unlink()

        pointer_continued_linearly = False
        for line in output.splitlines():
            if "->" in line and "LOAD_CONST" in line and "111" in line:
                pointer_continued_linearly = True
                break
        
        self.assertTrue(
            pointer_continued_linearly,
            "After CJMP with FALSE condition, the instruction pointer should continue linearly to 'LOAD_CONST 111'"
        )



    def test_step_cjump_true(self):
        cjmp_test_code = """
        function "$entrypoint$"
        LOAD_CONST 1         
        CJMP jump_if_true
        LOAD_CONST 111     
        LABEL jump_if_true
        STORE_VAR "result"    
        """
        test_path = Path("cjmp_true_test.xvm")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(cjmp_test_code)

        commands = [
            f"load {test_path}",
            "step",  
            "step", 
            "list",
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        test_path.unlink()

        pointer_jumped_correctly = False
        for line in output.splitlines():
            if "->" in line and "STORE_VAR" in line and "'result'" in line:
                pointer_jumped_correctly = True
                break
        
        self.assertTrue(
            pointer_jumped_correctly,
            "After stepping over CJMP with TRUE condition, the instruction pointer should be at 'STORE_VAR \"result\"'"
        )




    def test_next_command(self):
        test_path = Path("call_next_test.xvm")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(CALL_NEXT_TEST_CODE)

        commands = [
            f"load {test_path}",
            "step",  
            "step",  
            "next",  
            "list",  
            "exit"
        ]
        
        output = self.run_debugger_with_commands(commands)
        test_path.unlink() 

        
        pointer_at_correct_instruction = False
        for line in output.splitlines():
            if "->" in line and "STORE_VAR" in line and "'result'" in line:
                pointer_at_correct_instruction = True
                break
        
        self.assertTrue(
            pointer_at_correct_instruction, 
            "The instruction pointer should be at 'STORE_VAR \"result\"'      after 'next' command"
        )


    
    def test_exec_stack_command(self):
        commands = [
            "load debug_program1.txt",
            "exec LOAD_CONST 999",  
            "stack",               
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        self.assertIn("Executing: Op(OpCode.LOAD_CONST, 999)", output)
        
        parsed_stack = []
        in_stack_section = False
        for line in output.splitlines():
            print(f"TESTER PARSING LINE: '{line}' (in_stack_section={in_stack_section})")

            if not in_stack_section and "Stack (top is [0]):" in line:
                in_stack_section = True
                print("TESTER: Found stack header!") 

            if in_stack_section and line.strip().startswith('['):
                print(f"TESTER: Found stack item line: '{line}'")
                try:
                    val_str = line.split(']', 1)[1].strip()
                    parsed_stack.append(ast.literal_eval(val_str))
                    print(f"TESTER: Successfully parsed and added '{val_str}' to stack.")
                except Exception as e:
                    print(f"TESTER: FAILED to parse line '{line}'. Error: {e}")
        self.assertEqual(len(parsed_stack), 1, "Stack should have exactly one element")
        self.assertEqual(parsed_stack[0], 999, "Top of stack should be 999")

    
    
    def test_exec_failure_command(self): # testing that a failed 'exec' does not corrupt the current frame or variables
        
        commands = [
            f"load {self.test_program_path}",
            "step",  
            "step", 
            'exec LOAD_VAR "z"',
            "print a",
            "frame",
            "exit"
        ]

        output = self.run_debugger_with_commands(commands)
        self.assertIn("error", output, "Exec command should report a failure")
        self.assertIn("not defined", output, "Message should indicate 'z' is not defined")
        self.assertIn("a = 10", output, "Variable 'a' should still be accessible and equal to 10")
   


   