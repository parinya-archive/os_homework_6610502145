from typing import *
import threading
import sys

# Local step function to avoid circular import
step_no = 0
step_lock = threading.Lock()


def step(msg: str) -> None:
    """Print step message with number and flush immediately"""
    global step_no
    with step_lock:
        step_no += 1
        print(f"[STEP {step_no:02d}] {msg}")
        sys.stdout.flush()


class ResourceManager:
    def __init__(self, total: List[int], use_bankers: bool):
        self.total = total[:]
        self.available = total[:]
        self.use_bankers = use_bankers
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)

        self.max: Dict[str, List[int]] = {}
        self.alloc: Dict[str, List[int]] = {}
        self.need: Dict[str, List[int]] = {}
        self.waiting_req: Dict[str, Optional[List[int]]] = {}
        self.alive: Dict[str, bool] = {}

    def _can_cover(self, a: List[int], b: List[int]) -> bool:
        return all(a[i] >= b[i] for i in range(len(a)))

    def _vec_add(self, a, b):
        return [a[i] + b[i] for i in range(len(a))]

    def _vec_sub(self, a, b):
        return [a[i] - b[i] for i in range(len(a))]

    def add_process(self, pid: str, max_claim: List[int]) -> None:
        with self.cv:
            self.max[pid] = max_claim[:]
            self.alloc[pid] = [0] * len(self.total)
            self.need[pid] = max_claim[:]
            self.waiting_req[pid] = None
            self.alive[pid] = True
            step(f"{pid} registered with MAX={max_claim}, TOTAL={self.total}")

    def request(self, pid: str, req: List[int]) -> None:
        with self.cv:
            step(f"{pid} REQUEST {req} (NEED={self.need[pid]}, AVAIL={self.available})")
            if not self._can_cover(self.need[pid], req):
                raise ValueError("Request exceeds NEED")

            while True:
                if not self.alive.get(pid, False):
                    raise RuntimeError(f"{pid} aborted; request cancelled")

                if not self._can_cover(self.available, req):
                    self.waiting_req[pid] = req[:]
                    step(f"{pid} WAIT (insufficient AVAIL), waiting...")
                    self.cv.wait(timeout=0.5)
                    continue

                if self.use_bankers and not self._is_safe_if_grant(pid, req):
                    self.waiting_req[pid] = req[:]
                    step(f"{pid} WAIT (unsafe by Banker's), waiting...")
                    self.cv.wait(timeout=0.5)
                    continue

                self.available = self._vec_sub(self.available, req)
                self.alloc[pid] = self._vec_add(self.alloc[pid], req)
                self.need[pid] = self._vec_sub(self.need[pid], req)
                self.waiting_req[pid] = None
                step(
                    f"{pid} GRANTED {req} -> ALLOC={self.alloc[pid]}, NEED={self.need[pid]}, AVAIL={self.available}"
                )
                self.cv.notify_all()
                return

    def release(self, pid: str, rel: List[int]) -> None:
        with self.cv:
            rel = [min(rel[i], self.alloc[pid][i]) for i in range(len(rel))]
            self.alloc[pid] = self._vec_sub(self.alloc[pid], rel)
            self.need[pid] = self._vec_add(self.need[pid], rel)
            self.available = self._vec_add(self.available, rel)
            step(
                f"{pid} RELEASE {rel} -> ALLOC={self.alloc[pid]}, NEED={self.need[pid]}, AVAIL={self.available}"
            )
            self.cv.notify_all()

    def release_all_and_abort(self, pid: str) -> None:
        with self.cv:
            if not self.alive.get(pid, False):
                return
            rel = self.alloc[pid][:]
            self.available = self._vec_add(self.available, rel)
            self.alloc[pid] = [0] * len(rel)
            self.need[pid] = self.max[pid][:]
            self.alive[pid] = False
            self.waiting_req[pid] = None
            step(f"{pid} ABORTED -> released {rel}, AVAIL={self.available}")
            self.cv.notify_all()

    # ----- Banker's safety check -----
    def _is_safe_if_grant(self, pid: str, req: List[int]) -> bool:
        work = self._vec_sub(self.available, req)
        alloc_sim = {p: v[:] for p, v in self.alloc.items()}
        need_sim = {p: v[:] for p, v in self.need.items()}
        alloc_sim[pid] = self._vec_add(alloc_sim[pid], req)
        need_sim[pid] = self._vec_sub(need_sim[pid], req)

        finish = {p: not self.alive[p] for p in alloc_sim.keys()}
        changed = True
        while changed:
            changed = False
            for p in alloc_sim.keys():
                if finish[p]:
                    continue
                if self._can_cover(work, need_sim[p]):
                    work = self._vec_add(work, alloc_sim[p])
                    finish[p] = True
                    changed = True

        safe = all(finish.values())
        step(f"[Banker] simulate grant to {pid}: SAFE={safe}")
        return safe

    # ----- Wait-for Graph detection -----
    def build_wait_for_graph(self) -> Dict[str, set[str]]:
        g: Dict[str, set[str]] = {
            p: set() for p in self.max.keys() if self.alive.get(p, False)
        }
        R = len(self.total)
        for p, req in self.waiting_req.items():
            if not self.alive.get(p, False) or req is None:
                continue
            for r in range(R):
                if req[r] > 0 and self.available[r] < req[r]:
                    for q, alloc_q in self.alloc.items():
                        if q != p and self.alive.get(q, False) and alloc_q[r] > 0:
                            g[p].add(q)
        return g

    def detect_cycle(self) -> Optional[List[str]]:
        g = self.build_wait_for_graph()
        seen, stack = set(), set()
        path: List[str] = []

        def dfs(u: str):
            seen.add(u)
            stack.add(u)
            path.append(u)
            for v in g[u]:
                if v not in seen:
                    cyc = dfs(v)
                    if cyc:
                        return cyc
                elif v in stack:
                    i = path.index(v)
                    return path[i:]
            stack.remove(u)
            path.pop()
            return None

        for s in list(g.keys()):
            if s not in seen:
                cyc = dfs(s)
                if cyc and len(cyc) > 1:
                    step(f"[DETECT] cycle found: {' -> '.join(cyc)}")
                    return cyc
        return None
