import subprocess
import time
import csv
from datetime import datetime

# ตัวเลขที่อยากหาตัวประกอบ
number = 2**56

# เตรียม list สำหรับเก็บผลลัพธ์
results = []

for nproc in range(1, 16):
    print(f"\n===== Running with {nproc} process(es) =====")
    start = time.time()
    subprocess.run(["mpirun", "-n", str(nproc), "python3", "parallel.py", str(number)])
    end = time.time()
    elapsed_time = end - start
    print(f"Time used: {elapsed_time:.3f} seconds")

    # เก็บผลลัพธ์
    results.append({"num_processes": nproc, "time_seconds": elapsed_time})

# บันทึกผลลัพธ์เป็น CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"benchmark_results_{timestamp}.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["num_processes", "time_seconds", "speedup", "efficiency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    # คำนวณ speedup และ efficiency
    baseline_time = results[0]["time_seconds"]

    for result in results:
        nproc = result["num_processes"]
        time_sec = result["time_seconds"]
        speedup = baseline_time / time_sec
        efficiency = speedup / nproc * 100

        writer.writerow(
            {
                "num_processes": nproc,
                "time_seconds": f"{time_sec:.3f}",
                "speedup": f"{speedup:.3f}",
                "efficiency": f"{efficiency:.2f}",
            }
        )

print(f"\n✓ Results saved to {csv_filename}")
print(f"✓ Run 'python3 plot_results.py {csv_filename}' to generate graphs")
