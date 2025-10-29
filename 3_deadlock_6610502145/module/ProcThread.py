import threading
import time
from .ResourceManager import ResourceManager, step


class ProcThread(threading.Thread):
    def __init__(self, pid: str, rm: ResourceManager, script, releases=None, delay=0.5):
        super().__init__(name=pid, daemon=False)
        self.pid, self.rm = pid, rm
        self.script = script
        self.releases = releases or []
        self.delay = delay

    def run(self):
        try:
            for req in self.script:
                self.rm.request(self.pid, req)
                time.sleep(self.delay)
            for rel in self.releases:
                self.rm.release(self.pid, rel)
                time.sleep(self.delay)
            step(f"{self.pid} FINISHED")
        except RuntimeError as e:
            step(f"{self.pid} STOP: {e}")
