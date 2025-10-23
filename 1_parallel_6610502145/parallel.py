import sys
import subprocess
import time
import csv
import os
import matplotlib.pyplot as plt

# ให้ fallback เป็นโฟลเดอร์ของไฟล์นี้ ถ้า PATH_CODE_DIR ไม่ถูกกำหนด
CODE_DIR = os.getenv("PATH_CODE_DIR") or os.path.dirname(os.path.abspath(__file__))
MPIEXEC = os.getenv("MPIEXEC", "mpiexec")


def run_for_cores(n, cores):
    # เรียกเป็นโมดูล lib.mpi_entry เพื่อให้ import เสถียร
    cmd = [
        MPIEXEC,
        "--bind-to",
        "core",
        "--map-by",
        "core",
        "-n",
        str(cores),
        sys.executable,
        "-m",
        "lib.mpi_entry",
        str(n),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=CODE_DIR, timeout=300
    )
    out = proc.stdout.strip()
    err = proc.stderr.strip()
    return proc.returncode, out, err


def parse_output(out):
    factors = None
    compute_time = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("FACTORS:"):
            factors = line.split("FACTORS:", 1)[1].strip()
        elif line.startswith("COMPUTE_TIME:"):
            try:
                compute_time = float(line.split("COMPUTE_TIME:", 1)[1].strip())
            except:
                compute_time = None
    return factors, compute_time


def main():
    if len(sys.argv) != 2:
        print("Usage: python factor.py <number>")
        sys.exit(1)

    n = int(sys.argv[1])
    print(f"Factorizing number: {n}")
    print("=" * 70)

    results = []  # (cores, factors, compute_time, returncode, stderr, wall_time)

    for num_cores in range(1, 9):  # Changed to run 1-8 cores
        t_start = time.time()
        try:
            rc, out, err = run_for_cores(n, num_cores)
        except subprocess.TimeoutExpired:
            wall = time.time() - t_start
            print(f"{num_cores} core(s): TIMEOUT | wall={wall:.4f}s")
            results.append((num_cores, None, None, -1, "timeout", wall))
            continue
        t_end = time.time()
        elapsed_wall = t_end - t_start

        if rc == 0:
            factors, compute_time = parse_output(out)
            print(
                f"{num_cores} core(s): {factors:30s} | compute_time={compute_time if compute_time is not None else 'N/A':>8} s | wall={elapsed_wall:.4f}s"
            )
            results.append((num_cores, factors, compute_time, rc, err, elapsed_wall))
        else:
            print(f"{num_cores} core(s): Error occurred | wall={elapsed_wall:.4f}s")
            if err:
                print(f"  stderr (tail): {err.splitlines()[-5:]}")
            results.append((num_cores, None, None, rc, err, elapsed_wall))

    # save CSV
    csv_path = os.path.join(CODE_DIR, "factor_timing.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["cores", "factors", "compute_time", "returncode", "stderr", "wall_time"]
        )
        for row in results:
            w.writerow(row)
    print(f"Saved CSV -> {csv_path}")

    # plot compute_time (only points with compute_time)
    cores_list = []
    times = []
    for cores, factors, compute_time, rc, err, wall in results:
        if compute_time is not None:
            cores_list.append(cores)
            times.append(compute_time)

    if cores_list:
        plt.figure()
        plt.plot(cores_list, times, marker="o")
        plt.xlabel("Number of MPI processes")
        plt.ylabel("Compute time (seconds)")
        plt.title(f"Scaling for n={n}")
        plt.grid(True)
        png_path = os.path.join(CODE_DIR, "factor_timing.png")
        plt.savefig(png_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot -> {png_path}")
    else:
        print("No compute_time values to plot (maybe errors).")


if __name__ == "__main__":
    main()
