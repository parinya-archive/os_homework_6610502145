"""
Deadlock Visualization - Publication-Quality Graphs
Generates high-quality figures for the deadlock demonstration program
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import seaborn as sns
from typing import Tuple, List

# Set style for publication-quality figures
sns.set_style("whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["lines.linewidth"] = 2
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 11


def run_deadlock_demo(mode: str, project_root: Path, timeout: int) -> str:
    """
    Run a single deadlock demonstration mode with a timeout safeguard.

    Returns:
        str: "completed" if the demo finishes within the timeout, otherwise "timeout".
    """
    cmd = [sys.executable, str(project_root / "deadlock.py"), "--mode", mode]

    start_time = datetime.now()
    status = "unknown"
    return_code = None
    duration = 0.0

    print(f"▶ Running deadlock demo '{mode}' (timeout={timeout}s)")

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.stdout:
            print(result.stdout)
        status = "completed"
        return_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        captured = getattr(exc, "output", None) or getattr(exc, "stdout", None) or ""
        if isinstance(captured, bytes):
            captured = captured.decode("utf-8", errors="replace")
        if captured:
            print(captured)
        print(f"[WARNING] Demo exceeded {timeout} seconds and was terminated.")
        status = "timeout"
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

    if status == "completed":
        print(
            f"  ✓ Mode '{mode}' completed in {duration:.2f}s "
            f"(return code {return_code})"
        )
    else:
        print(f"  ⚠ Mode '{mode}' timed out after {timeout}s")

    return status


def run_deadlock_demos(project_root: Path) -> List[Tuple[str, str]]:
    """Run all deadlock demos with sensible timeout safeguards."""
    print("\n" + "=" * 60)
    print("Executing deadlock demonstrations with automatic timeouts")
    print("=" * 60)

    timeout_map = {"classic": 8, "avoid": 20, "detect": 20}
    results: List[Tuple[str, str]] = []

    for mode in ("classic", "avoid", "detect"):
        status = run_deadlock_demo(mode, project_root, timeout_map[mode])
        results.append((mode, status))

    print("-" * 60)
    for mode, status in results:
        if status == "completed":
            print(f"✓ {mode:8s} : completed")
        else:
            print(f"! {mode:8s} : timed out (expected for classic deadlock demo)")
    print("=" * 60 + "\n")

    return results


def create_coffmans_conditions_diagram():
    """Create a diagram showing Coffman's 4 Conditions"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(
        "Coffman's Four Necessary and Sufficient Conditions for Deadlock",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    conditions = [
        {
            "title": "1. Mutual Exclusion",
            "description": "Resources cannot be shared\nonly one process at a time",
            "color": "#FF6B6B",
        },
        {
            "title": "2. Hold and Wait",
            "description": "Process holds resources while\nwaiting for others",
            "color": "#FFA500",
        },
        {
            "title": "3. No Preemption",
            "description": "Resources cannot be forcefully\ntaken from processes",
            "color": "#4ECDC4",
        },
        {
            "title": "4. Circular Wait",
            "description": "Circular chain of processes\neach waiting for next",
            "color": "#95E1D3",
        },
    ]

    for idx, (ax, cond) in enumerate(zip(axes.flat, conditions)):
        # Create rounded rectangle background
        rect = FancyBboxPatch(
            (0.05, 0.1),
            0.9,
            0.8,
            boxstyle="round,pad=0.05",
            edgecolor="black",
            facecolor=cond["color"],
            alpha=0.3,
            linewidth=2.5,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # Add title
        ax.text(
            0.5,
            0.75,
            cond["title"],
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            transform=ax.transAxes,
        )

        # Add description
        ax.text(
            0.5,
            0.40,
            cond["description"],
            ha="center",
            va="center",
            fontsize=11,
            transform=ax.transAxes,
            wrap=True,
        )

        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    plt.tight_layout()
    return fig


def create_classic_deadlock_sequence():
    """Create sequence diagram showing classic deadlock scenario"""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Timeline
    time_steps = np.arange(0, 10, 1)

    # Thread positions
    t1_y = 7
    t2_y = 4
    lock_a_y = 2
    lock_b_y = 0.5

    # Draw threads
    ax.text(
        -0.5, t1_y, "Thread T1", ha="right", va="center", fontsize=12, fontweight="bold"
    )
    ax.text(
        -0.5, t2_y, "Thread T2", ha="right", va="center", fontsize=12, fontweight="bold"
    )
    ax.text(
        -0.5,
        lock_a_y,
        "Lock A",
        ha="right",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        -0.5,
        lock_b_y,
        "Lock B",
        ha="right",
        va="center",
        fontsize=11,
        fontweight="bold",
    )

    # Timeline line for threads
    ax.plot([0, 9], [t1_y, t1_y], "k--", alpha=0.3, linewidth=1)
    ax.plot([0, 9], [t2_y, t2_y], "k--", alpha=0.3, linewidth=1)

    # T1 acquires Lock A (step 1)
    ax.arrow(
        1,
        t1_y,
        0.5,
        lock_a_y - t1_y + 0.3,
        head_width=0.15,
        head_length=0.2,
        fc="#FF6B6B",
        ec="#FF6B6B",
        linewidth=2.5,
    )
    ax.text(
        0.7,
        (t1_y + lock_a_y) / 2 - 0.5,
        "acquire(A)",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="#FF6B6B", alpha=0.7),
    )

    # T2 acquires Lock B (step 1)
    ax.arrow(
        1,
        t2_y,
        0.5,
        lock_b_y - t2_y - 0.3,
        head_width=0.15,
        head_length=0.2,
        fc="#4ECDC4",
        ec="#4ECDC4",
        linewidth=2.5,
    )
    ax.text(
        0.7,
        (t2_y + lock_b_y) / 2 + 0.5,
        "acquire(B)",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="#4ECDC4", alpha=0.7),
    )

    # Barrier sync (step 2-3)
    ax.plot([2, 2], [t1_y - 0.3, t2_y + 0.3], "g-", linewidth=3, alpha=0.5)
    ax.text(
        2,
        5.5,
        "Barrier\nSync",
        ha="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
    )

    # T1 waits for Lock B (step 3)
    ax.arrow(
        3.5,
        t1_y,
        0.5,
        lock_b_y - t1_y + 0.2,
        head_width=0.15,
        head_length=0.2,
        fc="#FF6B6B",
        ec="#FF6B6B",
        linewidth=2.5,
        linestyle="dashed",
        alpha=0.6,
    )
    ax.text(
        3.2,
        (t1_y + lock_b_y) / 2,
        "wait(B)\nBLOCKED",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="#FFB6B6", alpha=0.7),
    )

    # T2 waits for Lock A (step 3)
    ax.arrow(
        3.5,
        t2_y,
        0.5,
        lock_a_y - t2_y - 0.2,
        head_width=0.15,
        head_length=0.2,
        fc="#4ECDC4",
        ec="#4ECDC4",
        linewidth=2.5,
        linestyle="dashed",
        alpha=0.6,
    )
    ax.text(
        3.2,
        (t2_y + lock_a_y) / 2,
        "wait(A)\nBLOCKED",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="#9EDBDA", alpha=0.7),
    )

    # Circular Wait - show cycle
    circle_theta = np.linspace(0, 2 * np.pi, 100)
    circle_x = 6.5 + 1.5 * np.cos(circle_theta)
    circle_y = 4 + 2 * np.sin(circle_theta)
    ax.plot(circle_x, circle_y, "r--", linewidth=2.5, alpha=0.7)
    ax.text(
        6.5,
        4,
        "DEADLOCK",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        bbox=dict(
            boxstyle="round",
            facecolor="#FFE5E5",
            alpha=0.9,
            edgecolor="red",
            linewidth=2,
        ),
    )

    # Step labels
    steps = [
        "Step 1:\nT1 acq(A)\nT2 acq(B)",
        "Step 2:\nBarrier\nSync",
        "Step 3:\nT1 wait(B)\nT2 wait(A)\nDEADLOCK",
    ]
    for i, step in enumerate(steps):
        ax.text(
            1 + i * 2.5,
            -1.5,
            step,
            ha="center",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
        )

    ax.set_xlim(-2, 9)
    ax.set_ylim(-2.5, 8.5)
    ax.axis("off")

    plt.title(
        "Classic Deadlock Scenario: Circular Wait",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    return fig


def create_wait_for_graph():
    """Create Wait-For Graph visualization"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Wait-For Graph (WFG) - Deadlock Detection", fontsize=14, fontweight="bold"
    )

    # Scenario 1: No Deadlock
    ax = axes[0]
    ax.set_title("Scenario 1: No Cycle\n(No Deadlock)", fontsize=12, fontweight="bold")

    # Nodes
    nodes = {"P1": (0.3, 0.7), "P2": (0.7, 0.7), "P3": (0.5, 0.3)}
    for node, (x, y) in nodes.items():
        circle = plt.Circle((x, y), 0.08, color="#4ECDC4", ec="black", linewidth=2)
        ax.add_patch(circle)
        ax.text(
            x,
            y,
            node,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white",
        )

    # Edges: P1 → P2, P2 → P3 (no cycle)
    ax.annotate(
        "",
        xy=(0.63, 0.7),
        xytext=(0.37, 0.7),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#2C3E50"),
    )
    ax.annotate(
        "",
        xy=(0.58, 0.42),
        xytext=(0.52, 0.58),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#2C3E50"),
    )

    ax.text(0.5, 0.75, "P1 → P2", ha="center", fontsize=10)
    ax.text(0.65, 0.5, "P2 → P3", ha="center", fontsize=10, rotation=-45)

    # Status
    ax.text(
        0.5,
        0.05,
        "No Cycle = Safe",
        ha="center",
        fontsize=11,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.8),
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Scenario 2: Simple Cycle
    ax = axes[1]
    ax.set_title("Scenario 2: Simple Cycle\n(Deadlock)", fontsize=12, fontweight="bold")

    nodes = {"P1": (0.2, 0.5), "P2": (0.8, 0.5)}
    for node, (x, y) in nodes.items():
        circle = plt.Circle((x, y), 0.08, color="#FF6B6B", ec="black", linewidth=2)
        ax.add_patch(circle)
        ax.text(
            x,
            y,
            node,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white",
        )

    # Edges: P1 → P2 → P1 (cycle)
    ax.annotate(
        "",
        xy=(0.72, 0.55),
        xytext=(0.28, 0.55),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )
    ax.annotate(
        "",
        xy=(0.28, 0.45),
        xytext=(0.72, 0.45),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )

    ax.text(0.5, 0.6, "P1 → P2", ha="center", fontsize=10)
    ax.text(0.5, 0.35, "P2 → P1", ha="center", fontsize=10)

    # Status
    ax.text(
        0.5,
        0.05,
        "Cycle Found = DEADLOCK!",
        ha="center",
        fontsize=11,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#FFB6B6", alpha=0.8),
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Scenario 3: Complex Cycle
    ax = axes[2]
    ax.set_title(
        "Scenario 3: Complex Cycle\n(Deadlock)", fontsize=12, fontweight="bold"
    )

    nodes = {"P1": (0.5, 0.8), "P2": (0.8, 0.5), "P3": (0.5, 0.2), "P4": (0.2, 0.5)}
    colors = {"P1": "#FF6B6B", "P2": "#FF6B6B", "P3": "#FF6B6B", "P4": "#FF6B6B"}
    for node, (x, y) in nodes.items():
        circle = plt.Circle((x, y), 0.07, color=colors[node], ec="black", linewidth=2)
        ax.add_patch(circle)
        ax.text(
            x,
            y,
            node,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
        )

    # Edges forming cycle: P1→P2→P3→P4→P1
    ax.annotate(
        "",
        xy=(0.75, 0.65),
        xytext=(0.55, 0.75),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )
    ax.annotate(
        "",
        xy=(0.65, 0.25),
        xytext=(0.75, 0.45),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )
    ax.annotate(
        "",
        xy=(0.25, 0.45),
        xytext=(0.45, 0.25),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )
    ax.annotate(
        "",
        xy=(0.55, 0.75),
        xytext=(0.25, 0.55),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="#E74C3C"),
    )

    # Status
    ax.text(
        0.5,
        0.05,
        "Cycle: P1→P2→P3→P4→P1",
        ha="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#FFB6B6", alpha=0.8),
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    return fig


def create_bankers_algorithm_flow():
    """Create Banker's Algorithm flow diagram"""
    fig, ax = plt.subplots(figsize=(12, 14))

    # Define boxes
    boxes = [
        {"y": 0.95, "label": "Process Requests Resources", "color": "#3498DB"},
        {"y": 0.85, "label": "Check: Available ≥ Request?", "color": "#F39C12"},
        {"y": 0.72, "label": "Simulate Grant\n(Pretend to give)", "color": "#9B59B6"},
        {"y": 0.60, "label": "Is Safe State?", "color": "#F39C12"},
        {"y": 0.47, "label": "YES", "color": "#27AE60"},
        {"y": 0.35, "label": "GRANT Request\n(Actually give)", "color": "#27AE60"},
        {"y": 0.20, "label": "Process Proceeds", "color": "#1ABC9C"},
    ]

    # Draw boxes and connections
    for i, box in enumerate(boxes):
        y = box["y"]
        width = 0.6
        height = 0.08

        rect = FancyBboxPatch(
            (0.2, y - height / 2),
            width,
            height,
            boxstyle="round,pad=0.01",
            edgecolor="black",
            facecolor=box["color"],
            alpha=0.8,
            linewidth=2.5,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        ax.text(
            0.5,
            y,
            box["label"],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white",
            transform=ax.transAxes,
        )

        # Draw arrow to next box
        if i < len(boxes) - 1:
            next_y = boxes[i + 1]["y"]
            ax.annotate(
                "",
                xy=(0.5, next_y + 0.04),
                xytext=(0.5, y - 0.04),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", lw=2, color="black"),
            )

    # Draw NO path
    ax.text(
        0.15,
        0.85,
        "NO",
        ha="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#E74C3C", alpha=0.8),
        transform=ax.transAxes,
    )
    ax.annotate(
        "",
        xy=(0.15, 0.25),
        xytext=(0.15, 0.87),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="->", lw=2, color="#E74C3C", linestyle="dashed"),
    )

    ax.text(
        0.15,
        0.60,
        "NO",
        ha="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#E74C3C", alpha=0.8),
        transform=ax.transAxes,
    )
    ax.annotate(
        "",
        xy=(0.15, 0.35),
        xytext=(0.15, 0.54),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="->", lw=2, color="#E74C3C", linestyle="dashed"),
    )

    # WAIT box
    ax.text(
        0.15,
        0.25,
        "WAIT\n(Retry Later)",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#F39C12", alpha=0.8),
        transform=ax.transAxes,
    )

    # Title
    ax.text(
        0.5,
        1.02,
        "Banker's Algorithm Flow",
        ha="center",
        fontsize=16,
        fontweight="bold",
        transform=ax.transAxes,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    return fig


def create_three_approaches_comparison():
    """Create comprehensive comparison of 3 approaches"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

    fig.suptitle(
        "Deadlock Handling: Three Approaches Compared", fontsize=16, fontweight="bold"
    )

    # Comparison table
    ax = fig.add_subplot(gs[0, :])
    ax.axis("tight")
    ax.axis("off")

    table_data = [
        ["Aspect", "Classic", "Avoidance", "Detection"],
        ["Deadlock Occurs", "YES", "NO", "YES"],
        ["Detection Time", "N/A", "N/A", "Real-time"],
        ["Coffman Conditions", "All 4 Present", "3 of 4", "All 4 Present"],
        ["Performance", "Low", "Medium", "Medium"],
        ["Safety", "Unsafe", "Safe", "Recoverable"],
        ["Use Case", "Study/Demo", "Real Systems", "Monitoring"],
    ]

    table = ax.table(
        cellText=table_data,
        cellLoc="center",
        loc="center",
        colWidths=[0.2, 0.25, 0.25, 0.25],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)

    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor("#2C3E50")
        table[(0, i)].set_text_props(weight="bold", color="white")

    # Style rows
    colors = ["#FF6B6B", "#4ECDC4", "#95E1D3"]
    for i in range(1, len(table_data)):
        for j in range(4):
            if j == 0:
                table[(i, j)].set_facecolor("#ECF0F1")
                table[(i, j)].set_text_props(weight="bold")
            else:
                table[(i, j)].set_facecolor(colors[j - 1])
                table[(i, j)].set_alpha(0.3)

    # Timeline visualization
    ax = fig.add_subplot(gs[1, 0])
    ax.set_title("Classic: Timeline", fontsize=12, fontweight="bold")
    ax.barh([0], [8], color="#FF6B6B", alpha=0.7, height=0.5, label="Running")
    ax.barh(
        [0], [2], left=[8], color="#E74C3C", alpha=0.9, height=0.5, label="Deadlock"
    )
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("Time", fontsize=10)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_yticks([])

    ax = fig.add_subplot(gs[1, 1])
    ax.set_title("Avoidance: Timeline", fontsize=12, fontweight="bold")
    ax.barh([0], [10], color="#4ECDC4", alpha=0.7, height=0.5, label="Safe Execution")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("Time", fontsize=10)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_yticks([])

    ax = fig.add_subplot(gs[1, 2])
    ax.set_title("Detection: Timeline", fontsize=12, fontweight="bold")
    ax.barh([0], [4], color="#95E1D3", alpha=0.7, height=0.5, label="Running")
    ax.barh(
        [0], [2], left=[4], color="#E74C3C", alpha=0.7, height=0.5, label="Deadlock"
    )
    ax.barh(
        [0], [4], left=[6], color="#27AE60", alpha=0.7, height=0.5, label="Recovered"
    )
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("Time", fontsize=10)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_yticks([])

    # Method descriptions
    approaches = [
        ("CLASSIC\n(No Prevention)", "#FF6B6B"),
        ("AVOIDANCE\n(Banker's)", "#4ECDC4"),
        ("DETECTION\n(WFG)", "#95E1D3"),
    ]

    for idx, (name, color) in enumerate(approaches):
        ax = fig.add_subplot(gs[2, idx])
        ax.text(
            0.5,
            0.5,
            name,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round", facecolor=color, alpha=0.5),
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    return fig


def create_resource_allocation_diagram():
    """Create resource allocation state diagram"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Resource Allocation States", fontsize=14, fontweight="bold")

    # Left: Unsafe State
    ax = axes[0]
    ax.set_title(
        "Unsafe State → Deadlock Risk", fontsize=12, fontweight="bold", color="#E74C3C"
    )

    states_unsafe = [
        {"y": 0.85, "text": "Total: CPU:10, Memory:20GB", "color": "#3498DB"},
        {
            "y": 0.70,
            "text": "P1: Allocated CPU:5 Mem:8GB\nNeed: CPU:5 Mem:12GB",
            "color": "#E74C3C",
        },
        {
            "y": 0.50,
            "text": "P2: Allocated CPU:5 Mem:8GB\nNeed: CPU:5 Mem:12GB",
            "color": "#E74C3C",
        },
        {
            "y": 0.30,
            "text": "Available: CPU:0 Mem:4GB\nCANNOT satisfy BOTH",
            "color": "#F39C12",
        },
    ]

    for state in states_unsafe:
        rect = FancyBboxPatch(
            (0.05, state["y"] - 0.07),
            0.9,
            0.12,
            boxstyle="round,pad=0.01",
            edgecolor="black",
            facecolor=state["color"],
            alpha=0.6,
            linewidth=2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(
            0.5,
            state["y"],
            state["text"],
            ha="center",
            va="center",
            fontsize=10,
            transform=ax.transAxes,
            fontweight="bold",
        )

    ax.text(
        0.5,
        0.10,
        "UNSAFE STATE - Will lead to DEADLOCK",
        ha="center",
        fontsize=11,
        fontweight="bold",
        transform=ax.transAxes,
        bbox=dict(boxstyle="round", facecolor="#FFB6B6", alpha=0.8),
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Right: Safe State
    ax = axes[1]
    ax.set_title(
        "Safe State → Deadlock Free", fontsize=12, fontweight="bold", color="#27AE60"
    )

    states_safe = [
        {"y": 0.85, "text": "Total: CPU:10, Memory:20GB", "color": "#3498DB"},
        {
            "y": 0.70,
            "text": "P1: Allocated CPU:3 Mem:5GB\nNeed: CPU:2 Mem:7GB",
            "color": "#27AE60",
        },
        {
            "y": 0.50,
            "text": "P2: Allocated CPU:2 Mem:3GB\nNeed: CPU:3 Mem:5GB",
            "color": "#27AE60",
        },
        {
            "y": 0.30,
            "text": "Available: CPU:5 Mem:12GB\nCAN satisfy sequence",
            "color": "#27AE60",
        },
    ]

    for state in states_safe:
        rect = FancyBboxPatch(
            (0.05, state["y"] - 0.07),
            0.9,
            0.12,
            boxstyle="round,pad=0.01",
            edgecolor="black",
            facecolor=state["color"],
            alpha=0.6,
            linewidth=2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(
            0.5,
            state["y"],
            state["text"],
            ha="center",
            va="center",
            fontsize=10,
            transform=ax.transAxes,
            fontweight="bold",
        )

    ax.text(
        0.5,
        0.10,
        "SAFE STATE - All processes can complete",
        ha="center",
        fontsize=11,
        fontweight="bold",
        transform=ax.transAxes,
        bbox=dict(boxstyle="round", facecolor="#B6FFB6", alpha=0.8),
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    return fig


def create_detection_resolution_flow():
    """Create detection and resolution workflow"""
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.set_title(
        "Deadlock Detection & Resolution Workflow",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Define workflow steps
    steps = [
        {
            "y": 0.95,
            "text": "1. Normal Operation\nProcesses requesting resources",
            "color": "#3498DB",
        },
        {
            "y": 0.82,
            "text": "2. Deadlock Occurs\nCircular wait detected",
            "color": "#E74C3C",
        },
        {
            "y": 0.69,
            "text": "3. Build Wait-for Graph\nCreate graph of waiting chains",
            "color": "#F39C12",
        },
        {
            "y": 0.56,
            "text": "4. Cycle Detection (DFS)\nSearch for cycles in WFG",
            "color": "#F39C12",
        },
        {"y": 0.43, "text": "5. Cycle Found!\nDeadlock confirmed", "color": "#E74C3C"},
        {
            "y": 0.30,
            "text": "6. Select Victim\nChoose process with max allocation",
            "color": "#9B59B6",
        },
        {
            "y": 0.17,
            "text": "7. Abort & Release\nKill victim, free all resources",
            "color": "#E67E22",
        },
        {
            "y": 0.04,
            "text": "8. Recovery\nSystem resumes (processes retry)",
            "color": "#27AE60",
        },
    ]

    for i, step in enumerate(steps):
        # Draw box
        rect = FancyBboxPatch(
            (0.1, step["y"] - 0.05),
            0.8,
            0.09,
            boxstyle="round,pad=0.01",
            edgecolor="black",
            facecolor=step["color"],
            alpha=0.7,
            linewidth=2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # Add text
        ax.text(
            0.5,
            step["y"],
            step["text"],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            transform=ax.transAxes,
            color="white",
        )

        # Draw arrow
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(0.5, steps[i + 1]["y"] + 0.045),
                xytext=(0.5, step["y"] - 0.045),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", lw=2.5, color="black"),
            )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    return fig


def generate_visualizations(figures_dir: Path) -> List[Tuple[str, str]]:
    """Generate and save all publication-quality visualizations."""
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("Generating publication-quality visualizations")
    print("=" * 60 + "\n")

    figure_specs = [
        (
            "01_coffmans_conditions",
            create_coffmans_conditions_diagram(),
            "Coffman's Conditions",
        ),
        (
            "02_classic_deadlock_sequence",
            create_classic_deadlock_sequence(),
            "Classic Deadlock Sequence",
        ),
        ("03_wait_for_graph", create_wait_for_graph(), "Wait-For Graph"),
        (
            "04_bankers_algorithm_flow",
            create_bankers_algorithm_flow(),
            "Banker's Algorithm Flow",
        ),
        (
            "05_three_approaches_comparison",
            create_three_approaches_comparison(),
            "Three Approaches Comparison",
        ),
        (
            "06_resource_allocation_states",
            create_resource_allocation_diagram(),
            "Resource Allocation States",
        ),
        (
            "07_detection_resolution_flow",
            create_detection_resolution_flow(),
            "Detection & Resolution Flow",
        ),
    ]

    saved: List[Tuple[str, str]] = []
    for filename, fig, title in figure_specs:
        print(f"📊 Creating {title}...")
        png_path = figures_dir / f"{filename}.png"
        fig.savefig(png_path, bbox_inches="tight", dpi=300)
        print(f"✓ Saved: {png_path}")
        plt.close(fig)
        saved.append((filename, title))

    print("\n" + "=" * 60)
    print("✓ All visualizations generated successfully!")
    print(f"✓ Output directory: {figures_dir}")
    print("=" * 60 + "\n")

    print("Generated files:")
    for i, (filename, _) in enumerate(saved, 1):
        print(f"  {i}. {filename}.png")
    print("\n")

    return saved


def main():
    """Run deadlock demos with timeouts and generate visualizations."""
    project_root = Path(__file__).resolve().parent
    figures_dir = project_root / "graph"

    figures_dir.mkdir(parents=True, exist_ok=True)

    run_deadlock_demos(project_root)
    generate_visualizations(figures_dir)

    print("Artifacts available at:")
    print(f"  - Graph images: {figures_dir}")


if __name__ == "__main__":
    main()
