import itertools
import sys
import threading
import time


class Spinner:
    def __init__(self, message="Processing"):
        self.spinner = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        self.message = message
        self.running = False
        self.spinner_thread = None
        self.last_line = ""

    def _clear_line(self):
        # Clear the current line
        sys.stdout.write("\r")
        sys.stdout.write(" " * (len(self.last_line) + 2))
        sys.stdout.write("\r")
        sys.stdout.flush()

    def spin(self):
        while self.running:
            current = f"{next(self.spinner)} {self.message}"
            self._clear_line()
            sys.stdout.write(current)
            sys.stdout.flush()
            self.last_line = current
            time.sleep(0.1)

    def __enter__(self):
        if sys.stdout.isatty():  # Only show spinner in terminal
            self.running = True
            self.spinner_thread = threading.Thread(target=self.spin)
            self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        self._clear_line()
        # Move to new line for any following output
        sys.stdout.write("\n")
