import threading
import time
import faulthandler
import sys

# show step for debug
step_no = 0
step_lock = threading.Lock()


def step(msg: str) -> None:
    """Print step message with number and flush immediately"""
    global step_no
    with step_lock:
        step_no += 1
        print(f"[STEP {step_no:02d}] {msg}")
        sys.stdout.flush()


# resource for deadlock
lock_a = threading.Lock()
lock_b = threading.Lock()

# track lock ownership for real-time debugging
lock_owner = {}
owner_lock = threading.Lock()

barrier = threading.Barrier(2)


def acquire_lock(lock, name, thread_name):
    """Acquire lock and track ownership"""
    step(f"{thread_name} trying to acquire {name}")
    lock.acquire()
    with owner_lock:
        lock_owner[name] = thread_name
    step(f"{thread_name} acquired {name}")


def release_lock(lock, name, thread_name):
    """Release lock and update tracking"""
    lock.release()
    with owner_lock:
        if name in lock_owner:
            del lock_owner[name]
    step(f"{thread_name} released {name}")


# Simulation thread 1
def t1():
    step("T1 starts")
    # thread1 acquires lock A first
    acquire_lock(lock_a, "Lock A", "T1")

    step("T1 waiting at Barrier (wait for T2 to reach same point)")
    barrier.wait()

    step("T1 trying to acquire Lock B (will block if T2 holds it)")
    acquire_lock(lock_b, "Lock B", "T1")
    step("T1 acquired Lock B (this line won't execute in deadlock)")
    release_lock(lock_b, "Lock B", "T1")
    release_lock(lock_a, "Lock A", "T1")
    step("T1 finished")


def t2() -> None:
    step("T2 starts")
    # thread2 acquires lock B first
    acquire_lock(lock_b, "Lock B", "T2")

    step("T2 waiting at Barrier (wait for T1 to reach same point)")
    barrier.wait()

    step("T2 trying to acquire Lock A (will block if T1 holds it)")
    acquire_lock(lock_a, "Lock A", "T2")  # deadlock happens here
    step("T2 acquired Lock A (this line won't execute in deadlock)")

    release_lock(lock_a, "Lock A", "T2")
    release_lock(lock_b, "Lock B", "T2")
    step("T2 finished")


def monitor_locks(duration=15):
    """Real-time monitor thread that displays lock status every 1 second"""
    end_time = time.time() + duration
    while time.time() < end_time:
        time.sleep(1)
        with owner_lock:
            if lock_owner:
                owners = ", ".join([f"{k}={v}" for k, v in lock_owner.items()])
                step(f"[MONITOR] Current locks held: {owners}")
            else:
                step("[MONITOR] No locks currently held")


def main():
    step("start program")
    faulthandler.enable()
    step("set traceback dump after 3 seconds (shows where threads are stuck)")
    faulthandler.dump_traceback_later(3, repeat=False)

    # Start monitor thread
    monitor_th = threading.Thread(target=monitor_locks, daemon=True, name="Monitor")
    monitor_th.start()

    t1_th = threading.Thread(target=t1, name="T1")
    t2_th = threading.Thread(target=t2, name="T2")

    step("start T1 and T2")
    t1_th.start()
    t2_th.start()

    step("join with timeout 10 seconds (demonstrates deadlock - won't finish)")
    t1_th.join(timeout=10)
    t2_th.join(timeout=10)

    step("checking thread status after join timeout")
    step(f"T1 is_alive: {t1_th.is_alive()}")
    step(f"T2 is_alive: {t2_th.is_alive()}")

    if t1_th.is_alive() or t2_th.is_alive():
        step("DEADLOCK CONFIRMED: threads still running (stuck waiting for locks)")
    else:
        step("Both threads finished successfully")


if __name__ == "__main__":
    main()
