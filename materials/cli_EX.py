import cmd
from xvm import VM
from xvm.vm import deserialize_code

class MyShell(cmd.Cmd):
    intro = "Welcome to MyShell. Type help or ? to list commands."
    prompt = "myshell> "

    def __init__(self):
        super().__init__()
        self.vm = VM()

    # --- Explicit commands ---
    def do_exit(self, arg):
        """Exit the shell."""
        print("Exiting...")
        return True   # returning True exits cmdloop()

    def do_stack(self, arg):
        """Show current stack contents."""
        print("Stack:", self.vm.stack)

    def do_memory(self, arg):
        """Show current memory contents."""
        print("Memory:", self.vm.variables)

    def do_exec(self, arg):
        """Exec OP_CODE <arg1> <arg2>..."""
        op = deserialize_code(arg)[0]
        self.vm.run_op(op)

    # --- Default (catch-all) ---
    def default(self, line):
        """Called when no other command matches."""
        print(f"[default handler] You entered: {line!r}")
    
def cmd_main():
    MyShell().cmdloop()

if __name__ == "__main__":
    cmd_main()