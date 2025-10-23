#!/usr/bin/env python3
"""
Publication-quality visualization script for parallel processing benchmark results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sys import argv
import os

# ตั้งค่า style สำหรับกราฟแบบ publication-quality
plt.style.use("seaborn-v0_8-paper")
sns.set_palette("husl")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 13


def load_data(csv_file):
    """Load benchmark results from CSV file"""
    df = pd.read_csv(csv_file)
    return df


def plot_execution_time(df, output_dir):
    """Plot 1: Execution Time vs Number of Processes"""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Line plot with markers
    ax.plot(
        df["num_processes"],
        df["time_seconds"],
        marker="o",
        linewidth=2,
        markersize=8,
        color="#2E86AB",
        label="Execution Time",
    )

    # Fill area under curve
    ax.fill_between(df["num_processes"], df["time_seconds"], alpha=0.3, color="#2E86AB")

    ax.set_xlabel("Number of Processes", fontweight="bold")
    ax.set_ylabel("Execution Time (seconds)", fontweight="bold")
    ax.set_title("Execution Time vs Number of Processes", fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xticks(df["num_processes"])

    # Add value labels on points
    for i, (x, y) in enumerate(zip(df["num_processes"], df["time_seconds"])):
        ax.annotate(
            f"{y:.2f}s",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(f"{output_dir}/01_execution_time.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/01_execution_time.png")
    plt.close()


def plot_speedup(df, output_dir):
    """Plot 2: Speedup Analysis"""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Ideal speedup line
    ideal_speedup = df["num_processes"]
    ax.plot(
        df["num_processes"],
        ideal_speedup,
        linestyle="--",
        linewidth=2,
        color="gray",
        label="Ideal Speedup",
        alpha=0.7,
    )

    # Actual speedup
    ax.plot(
        df["num_processes"],
        df["speedup"],
        marker="s",
        linewidth=2.5,
        markersize=8,
        color="#A23B72",
        label="Actual Speedup",
    )

    ax.set_xlabel("Number of Processes", fontweight="bold")
    ax.set_ylabel("Speedup", fontweight="bold")
    ax.set_title("Speedup Analysis (Baseline: 1 Process)", fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xticks(df["num_processes"])
    ax.legend(loc="upper left")

    # Add value labels
    for i, (x, y) in enumerate(zip(df["num_processes"], df["speedup"])):
        ax.annotate(
            f"{y:.2f}x",
            (x, y),
            textcoords="offset points",
            xytext=(0, -15),
            ha="center",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(f"{output_dir}/02_speedup_analysis.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/02_speedup_analysis.png")
    plt.close()


def plot_efficiency(df, output_dir):
    """Plot 3: Parallel Efficiency"""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Efficiency bar chart with gradient colors
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df)))
    bars = ax.bar(
        df["num_processes"],
        df["efficiency"],
        color=colors,
        edgecolor="black",
        linewidth=1.2,
        alpha=0.8,
    )

    # Ideal efficiency line (100%)
    ax.axhline(
        y=100,
        color="green",
        linestyle="--",
        linewidth=2,
        label="Ideal Efficiency (100%)",
        alpha=0.7,
    )

    ax.set_xlabel("Number of Processes", fontweight="bold")
    ax.set_ylabel("Efficiency (%)", fontweight="bold")
    ax.set_title("Parallel Efficiency", fontweight="bold", pad=15)
    ax.set_xticks(df["num_processes"])
    ax.grid(True, alpha=0.3, linestyle="--", axis="y")
    ax.legend()

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, df["efficiency"])):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(f"{output_dir}/03_efficiency.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/03_efficiency.png")
    plt.close()


def plot_combined_metrics(df, output_dir):
    """Plot 4: Combined Metrics Dashboard"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        "Parallel Processing Performance Dashboard",
        fontsize=14,
        fontweight="bold",
        y=0.995,
    )

    # Subplot 1: Execution Time
    ax1 = axes[0, 0]
    ax1.plot(
        df["num_processes"],
        df["time_seconds"],
        marker="o",
        linewidth=2,
        markersize=7,
        color="#2E86AB",
    )
    ax1.fill_between(
        df["num_processes"], df["time_seconds"], alpha=0.3, color="#2E86AB"
    )
    ax1.set_xlabel("Number of Processes")
    ax1.set_ylabel("Time (seconds)")
    ax1.set_title("Execution Time", fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(df["num_processes"][::2])

    # Subplot 2: Speedup
    ax2 = axes[0, 1]
    ax2.plot(
        df["num_processes"],
        df["num_processes"],
        "--",
        color="gray",
        label="Ideal",
        alpha=0.7,
    )
    ax2.plot(
        df["num_processes"],
        df["speedup"],
        marker="s",
        linewidth=2,
        markersize=7,
        color="#A23B72",
        label="Actual",
    )
    ax2.set_xlabel("Number of Processes")
    ax2.set_ylabel("Speedup")
    ax2.set_title("Speedup Comparison", fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xticks(df["num_processes"][::2])

    # Subplot 3: Efficiency
    ax3 = axes[1, 0]
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df)))
    ax3.bar(
        df["num_processes"],
        df["efficiency"],
        color=colors,
        edgecolor="black",
        alpha=0.8,
    )
    ax3.axhline(y=100, color="green", linestyle="--", alpha=0.7)
    ax3.set_xlabel("Number of Processes")
    ax3.set_ylabel("Efficiency (%)")
    ax3.set_title("Parallel Efficiency", fontweight="bold")
    ax3.grid(True, alpha=0.3, axis="y")
    ax3.set_xticks(df["num_processes"][::2])

    # Subplot 4: Summary Table
    ax4 = axes[1, 1]
    ax4.axis("tight")
    ax4.axis("off")

    # Calculate statistics
    min_time = df["time_seconds"].min()
    max_time = df["time_seconds"].max()
    max_speedup = df["speedup"].max()
    avg_efficiency = df["efficiency"].mean()
    best_config = df.loc[df["time_seconds"].idxmin(), "num_processes"]

    summary_data = [
        ["Metric", "Value"],
        ["Min Time", f"{min_time:.3f}s"],
        ["Max Time", f"{max_time:.3f}s"],
        ["Max Speedup", f"{max_speedup:.2f}x"],
        ["Avg Efficiency", f"{avg_efficiency:.1f}%"],
        ["Best Config", f"{int(best_config)} processes"],
        ["Improvement", f"{((max_time / min_time - 1) * 100):.1f}%"],
    ]

    table = ax4.table(
        cellText=summary_data,
        cellLoc="left",
        colWidths=[0.6, 0.4],
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(2):
        table[(0, i)].set_facecolor("#4CAF50")
        table[(0, i)].set_text_props(weight="bold", color="white")

    # Style data rows
    for i in range(1, len(summary_data)):
        for j in range(2):
            table[(i, j)].set_facecolor("#f0f0f0" if i % 2 == 0 else "white")

    ax4.set_title("Performance Summary", fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/04_dashboard.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/04_dashboard.png")
    plt.close()


def plot_scalability(df, output_dir):
    """Plot 5: Scalability Analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Speedup with efficiency overlay
    ax1_twin = ax1.twinx()

    line1 = ax1.plot(
        df["num_processes"],
        df["speedup"],
        marker="o",
        linewidth=2.5,
        markersize=8,
        color="#FF6B6B",
        label="Speedup",
    )
    line2 = ax1_twin.plot(
        df["num_processes"],
        df["efficiency"],
        marker="s",
        linewidth=2.5,
        markersize=8,
        color="#4ECDC4",
        label="Efficiency",
        linestyle="--",
    )

    ax1.set_xlabel("Number of Processes", fontweight="bold")
    ax1.set_ylabel("Speedup", fontweight="bold", color="#FF6B6B")
    ax1_twin.set_ylabel("Efficiency (%)", fontweight="bold", color="#4ECDC4")
    ax1.set_title("Speedup vs Efficiency", fontweight="bold", pad=15)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(df["num_processes"][::2])

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")

    # Right: Time reduction percentage
    baseline = df["time_seconds"].iloc[0]
    time_reduction = (baseline - df["time_seconds"]) / baseline * 100

    colors_gradient = plt.cm.viridis(np.linspace(0, 1, len(df)))
    bars = ax2.barh(
        df["num_processes"].astype(str),
        time_reduction,
        color=colors_gradient,
        edgecolor="black",
        linewidth=1,
    )

    ax2.set_xlabel("Time Reduction (%)", fontweight="bold")
    ax2.set_ylabel("Number of Processes", fontweight="bold")
    ax2.set_title("Time Reduction vs Baseline", fontweight="bold", pad=15)
    ax2.grid(True, alpha=0.3, axis="x")

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, time_reduction)):
        width = bar.get_width()
        ax2.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            ha="left",
            va="center",
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
        )

    plt.tight_layout()
    plt.savefig(f"{output_dir}/05_scalability.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/05_scalability.png")
    plt.close()


def plot_comparative_analysis(df, output_dir):
    """Plot 6: Comparative Performance Analysis"""
    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # Main plot: Time vs Processes with multiple views
    ax_main = fig.add_subplot(gs[:, :2])

    # Primary axis: Time
    ax_main.plot(
        df["num_processes"],
        df["time_seconds"],
        marker="o",
        linewidth=3,
        markersize=10,
        color="#FF6B6B",
        label="Execution Time",
        zorder=3,
    )
    ax_main.fill_between(
        df["num_processes"], df["time_seconds"], alpha=0.2, color="#FF6B6B"
    )

    ax_main.set_xlabel("Number of Processes", fontweight="bold", fontsize=12)
    ax_main.set_ylabel(
        "Execution Time (seconds)", fontweight="bold", fontsize=12, color="#FF6B6B"
    )
    ax_main.set_title(
        "Comprehensive Performance Analysis", fontweight="bold", fontsize=13, pad=15
    )
    ax_main.grid(True, alpha=0.3, linestyle="--")
    ax_main.tick_params(axis="y", labelcolor="#FF6B6B")
    ax_main.set_xticks(df["num_processes"])

    # Find optimal point (minimum time)
    optimal_idx = df["time_seconds"].idxmin()
    optimal_procs = df.loc[optimal_idx, "num_processes"]
    optimal_time = df.loc[optimal_idx, "time_seconds"]

    ax_main.plot(
        optimal_procs,
        optimal_time,
        "g*",
        markersize=20,
        label="Optimal Configuration",
        zorder=5,
    )
    ax_main.annotate(
        "Optimal",
        (optimal_procs, optimal_time),
        xytext=(20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="arc3,rad=0", color="green", lw=2
        ),
    )

    ax_main.legend(loc="upper right", framealpha=0.9)

    # Small plot 1: Speedup gain
    ax1 = fig.add_subplot(gs[0, 2])
    speedup_gain = df["speedup"] - 1
    ax1.bar(
        df["num_processes"], speedup_gain, color="#95E1D3", edgecolor="black", alpha=0.8
    )
    ax1.set_ylabel("Speedup Gain", fontsize=9, fontweight="bold")
    ax1.set_title("Speedup Gain", fontsize=10, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.set_xticks(df["num_processes"][::3])

    # Small plot 2: Efficiency drop
    ax2 = fig.add_subplot(gs[1, 2])
    efficiency_drop = 100 - df["efficiency"]
    ax2.bar(
        df["num_processes"],
        efficiency_drop,
        color="#F38181",
        edgecolor="black",
        alpha=0.8,
    )
    ax2.set_xlabel("Processes", fontsize=9, fontweight="bold")
    ax2.set_ylabel("Efficiency Loss (%)", fontsize=9, fontweight="bold")
    ax2.set_title("Efficiency Loss", fontsize=10, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.set_xticks(df["num_processes"][::3])

    plt.savefig(f"{output_dir}/06_comparative_analysis.png", bbox_inches="tight")
    print(f"✓ Saved: {output_dir}/06_comparative_analysis.png")
    plt.close()


def generate_summary_report(df, output_dir):
    """Generate text summary report"""
    report_file = f"{output_dir}/performance_report.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("PARALLEL PROCESSING PERFORMANCE REPORT\n")
        f.write("=" * 70 + "\n\n")

        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total configurations tested: {len(df)}\n")
        f.write(
            f"Process range: {df['num_processes'].min()} - {df['num_processes'].max()}\n\n"
        )

        f.write("EXECUTION TIME\n")
        f.write("-" * 70 + "\n")
        f.write(f"Fastest time: {df['time_seconds'].min():.3f}s ")
        f.write(
            f"({int(df.loc[df['time_seconds'].idxmin(), 'num_processes'])} processes)\n"
        )
        f.write(f"Slowest time: {df['time_seconds'].max():.3f}s ")
        f.write(
            f"({int(df.loc[df['time_seconds'].idxmax(), 'num_processes'])} processes)\n"
        )
        f.write(f"Average time: {df['time_seconds'].mean():.3f}s\n\n")

        f.write("SPEEDUP ANALYSIS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Maximum speedup: {df['speedup'].max():.2f}x\n")
        f.write(f"Average speedup: {df['speedup'].mean():.2f}x\n\n")

        f.write("EFFICIENCY ANALYSIS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Best efficiency: {df['efficiency'].max():.2f}%\n")
        f.write(f"Worst efficiency: {df['efficiency'].min():.2f}%\n")
        f.write(f"Average efficiency: {df['efficiency'].mean():.2f}%\n\n")

        f.write("DETAILED RESULTS\n")
        f.write("-" * 70 + "\n")
        f.write(df.to_string(index=False))
        f.write("\n\n" + "=" * 70 + "\n")

    print(f"✓ Saved: {report_file}")


def main():
    if len(argv) < 2:
        print("Usage: python3 plot_results.py <csv_file>")
        print("Example: python3 plot_results.py benchmark_results_20250101_120000.csv")
        return

    csv_file = argv[1]

    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        return

    # Create output directory
    output_dir = "graphs"
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("GENERATING PUBLICATION-QUALITY GRAPHS")
    print("=" * 70 + "\n")

    # Load data
    df = load_data(csv_file)
    print(f"✓ Loaded data from {csv_file}")
    print(f"  - {len(df)} data points\n")

    # Generate all plots
    print("Generating graphs...\n")
    plot_execution_time(df, output_dir)
    plot_speedup(df, output_dir)
    plot_efficiency(df, output_dir)
    plot_combined_metrics(df, output_dir)
    plot_scalability(df, output_dir)
    plot_comparative_analysis(df, output_dir)

    # Generate summary report
    print("\nGenerating summary report...\n")
    generate_summary_report(df, output_dir)

    print("\n" + "=" * 70)
    print("✓ ALL GRAPHS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}/")
    print("\nGenerated files:")
    print("  1. 01_execution_time.png       - Execution time vs processes")
    print("  2. 02_speedup_analysis.png     - Speedup comparison with ideal")
    print("  3. 03_efficiency.png           - Parallel efficiency analysis")
    print("  4. 04_dashboard.png            - Complete performance dashboard")
    print("  5. 05_scalability.png          - Scalability analysis")
    print("  6. 06_comparative_analysis.png - Comprehensive comparison")
    print("  7. performance_report.txt      - Detailed text report")
    print("\n")


if __name__ == "__main__":
    main()
