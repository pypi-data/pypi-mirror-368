import threading
import time
import sys

class Spinner:
    def __init__(self, message="Loading..."):
        self.message = message
        self.stop_animation = threading.Event()
        self.animation_thread = threading.Thread(target=self._animate)

    def _animate(self):
        animation = "|/-\\"
        idx = 0
        while not self.stop_animation.is_set():
            sys.stdout.write(f"\r{self.message} {animation[idx % len(animation)]}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write("\r")
        sys.stdout.flush()

    def __enter__(self):
        self.animation_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.stop_animation.set()
        self.animation_thread.join()
