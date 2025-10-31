import argparse
import csv
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

import plot_results

CASES = {
    "min": {
        "number": 2**40,
        "graph_dir": Path("min_graph"),
        "display": "2^40",
    },
    "max": {
        "number": 2**55,
        "graph_dir": Path("max_graph"),
        "display": "2^55",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run MPI factorization benchmarks and generate plots automatically."
    )
    parser.add_argument(
        "--case",
        choices=["all"] + list(CASES.keys()),
        default="all",
        help="Choose which dataset to benchmark (default: all).",
    )
    parser.add_argument(
        "--process-max",
        type=int,
        default=15,
        help="Highest number of processes to benchmark (>=1).",
    )
    return parser.parse_args()


def run_benchmark(number, process_range):
    results = []
    print(f"\nRunning benchmark for {number:,}")

    for nproc in process_range:
        print(f"\n===== Running with {nproc} process(es) =====")
        start = time.time()
        subprocess.run(
            [
                "mpirun",
                "-n",
                str(nproc),
                "python3",
                "parallel.py",
                str(number),
            ],
            check=True,
        )
        elapsed = time.time() - start
        print(f"Time used: {elapsed:.3f} seconds")
        results.append({"num_processes": nproc, "time_seconds": elapsed})

    return results


def write_csv(results, label):
    if not results:
        raise ValueError("No benchmark results to write.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_name = f"benchmark_results_{label}_{timestamp}.csv"
    baseline_time = results[0]["time_seconds"]

    with open(csv_name, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["num_processes", "time_seconds", "speedup", "efficiency"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            nproc = result["num_processes"]
            time_sec = result["time_seconds"]
            speedup = baseline_time / time_sec if time_sec else float("inf")
            efficiency = speedup / nproc * 100
            writer.writerow(
                {
                    "num_processes": nproc,
                    "time_seconds": f"{time_sec:.3f}",
                    "speedup": f"{speedup:.3f}",
                    "efficiency": f"{efficiency:.2f}",
                }
            )

    return Path(csv_name)


def clean_output_dir(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    for item in directory.iterdir():
        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)


def generate_plots(csv_path: Path, output_dir: Path):
    clean_output_dir(output_dir)
    df = plot_results.load_data(csv_path)

    plot_results.plot_execution_time(df, str(output_dir))
    plot_results.plot_speedup(df, str(output_dir))
    plot_results.plot_efficiency(df, str(output_dir))
    plot_results.plot_combined_metrics(df, str(output_dir))
    plot_results.plot_scalability(df, str(output_dir))
    plot_results.plot_comparative_analysis(df, str(output_dir))
    plot_results.generate_summary_report(df, str(output_dir))

    shutil.copy(csv_path, output_dir / csv_path.name)


def main():
    args = parse_args()

    if args.process_max < 1:
        raise ValueError("--process-max must be at least 1.")

    process_range = range(1, args.process_max + 1)
    if args.case == "all":
        cases_to_run = CASES.items()
    else:
        cases_to_run = [(args.case, CASES[args.case])]

    for label, config in cases_to_run:
        number = config["number"]
        graph_dir = config["graph_dir"]
        display = config["display"]

        print("\n" + "=" * 70)
        print(f"CASE: {label.upper()} ({display})")
        print("=" * 70)

        results = run_benchmark(number, process_range)
        csv_path = write_csv(results, label)
        generate_plots(csv_path, graph_dir)

        print(f"\n✓ CSV saved to {csv_path}")
        print(f"✓ Graphs exported to {graph_dir.resolve()}")

    print("\nAll requested benchmarks completed.")


if __name__ == "__main__":
    main()
