import fcntl
import time

class FileLock:
    def __init__(self, filename):
        self.filename = filename
        self.fd = None

    def __enter__(self):
        self.fd = open(self.filename, 'a+')
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self.fd
            except (IOError, BlockingIOError):
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_value, traceback):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        self.fd.close()
