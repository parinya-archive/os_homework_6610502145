import time
import sys
import threading
from module.ResourceManager import ResourceManager
from module.ProcThread import ProcThread


step_no = 0
step_lock = threading.Lock()


def step(msg: str) -> None:
    """Print step message with number and flush immediately"""
    global step_no
    with step_lock:
        step_no += 1
        print(f"[STEP {step_no:02d}] {msg}")
        sys.stdout.flush()


def deadlock_watcher(rm: ResourceManager, interval=1.0, auto_resolve=True):
    while True:
        time.sleep(interval)
        cyc = None
        with rm.lock:
            cyc = rm.detect_cycle()
            alive = [p for p, ok in rm.alive.items() if ok]
        if cyc and auto_resolve and alive:
            with rm.lock:
                victim = max(cyc, key=lambda p: sum(rm.alloc[p]))
                step(
                    f"[RESOLUTION] choose victim={victim} (max allocation={rm.alloc[victim]})"
                )
                rm.release_all_and_abort(victim)


def demo_avoidance_with_bankers():
    step("=== DEMO: Avoidance (Banker's Algorithm) ===")
    rm = ResourceManager(total=[1, 1], use_bankers=True)
    rm.add_process("P1", [1, 1])
    rm.add_process("P2", [1, 1])
    p1 = ProcThread("P1", rm, script=[[1, 0], [0, 1]], releases=[[1, 1]])
    p2 = ProcThread("P2", rm, script=[[0, 1], [1, 0]], releases=[[1, 1]])
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    step("=== END Avoidance Demo ===")


def demo_detection_and_resolution():
    step("=== DEMO: Detection + Resolution (WFG + abort) ===")
    rm = ResourceManager(total=[1, 1], use_bankers=False)
    rm.add_process("P1", [1, 1])
    rm.add_process("P2", [1, 1])
    p1 = ProcThread("P1", rm, script=[[1, 0], [0, 1]], releases=[[1, 1]])
    p2 = ProcThread("P2", rm, script=[[0, 1], [1, 0]], releases=[[1, 1]])
    watcher = threading.Thread(
        target=deadlock_watcher, args=(rm, 0.5, True), daemon=True, name="WFG-Watcher"
    )
    watcher.start()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    step("=== END Detection/Resolution Demo ===")
