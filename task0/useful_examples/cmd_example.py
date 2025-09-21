import cmd

class MyShell(cmd.Cmd):
    intro = "Welcome to MyShell. Type help or ? to list commands."
    prompt = "myshell> "

    def __init__(self):
        super().__init__()
        self.stack = []

    # --- Explicit commands ---
    def do_exit(self, arg):
        """Exit the shell."""
        print("Exiting...")
        return True   # returning True exits cmdloop()

    def do_stack(self, arg):
        """Show current stack contents."""
        if self.stack:
            print("Stack:", self.stack)
        else:
            print("Stack is empty.")

    def do_push(self, arg):
        """Push an item onto the stack: PUSH <item>"""
        if not arg:
            print("Usage: push <item>")
        else:
            self.stack.append(arg)
            print(f"Pushed {arg!r}")

    def do_pop(self, arg):
        """Pop the last item off the stack."""
        if self.stack:
            item = self.stack.pop()
            print(f"Popped {item!r}")
        else:
            print("Stack is empty.")

    def do_my_stupid_cmd(self, arg):
        """A stupid command that does nothing."""
        print("This is a stupid command that does nothing.")

    # --- Default (catch-all) ---
    def default(self, line):
        """Called when no other command matches."""
        print(f"[default handler] You entered: {line!r}")

if __name__ == "__main__":
    MyShell().cmdloop()