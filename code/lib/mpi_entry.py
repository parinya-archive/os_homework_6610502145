from __future__ import annotations
import sys, os

try:
    from mpi4py import MPI
except Exception as e:
    print(f"mpi4py import error: {e}", file=sys.stderr)
    raise SystemExit(2)

def ensure_project_on_path():
    # project root = one level up from this lib/ folder
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(lib_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def get_parallel_factorizer():
    ensure_project_on_path()
    # minimal: assume lib.PollardRho exists
    from lib.PollardRho import ParallelFactorizer
    return ParallelFactorizer

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        if MPI.COMM_WORLD.Get_rank() == 0:
            print("USAGE: python -m lib.mpi_entry <number>", file=sys.stderr)
        return 2

    n = int(argv[1])
    ParallelFactorizer = get_parallel_factorizer()

    comm = MPI.COMM_WORLD
    pf = ParallelFactorizer()

    # sync then measure compute-only time
    comm.Barrier()
    t0 = MPI.Wtime()
    factors = pf.parallel_factorize(n)
    t1 = MPI.Wtime()

    # only master prints parseable output
    rank = getattr(pf, "rank", comm.Get_rank())
    if rank == 0:
        print(f"FACTORS:{factors}")
        print(f"COMPUTE_TIME:{(t1 - t0):.6f}")

    return 0

if __name__ == "__main__":
    rc = main(sys.argv)
    sys.exit(rc)
