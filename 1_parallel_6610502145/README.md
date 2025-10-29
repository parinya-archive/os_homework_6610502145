# Parallel Integer Factorization with MPI

โปรเจคนี้ใช้หาตัวประกอบของจำนวนเต็มขนาดใหญ่โดยใช้ parallel processing ผ่าน MPI (Message Passing Interface)

## Prerequisites

- Python 3.x
- MPI implementation (OpenMPI หรือ MPICH)
- ติดตั้ง MPI libraries:
  ```bash
  # Fedora/RHEL
  sudo dnf install openmpi openmpi-devel

  # Ubuntu/Debian
  sudo apt-get install openmpi-bin libopenmpi-dev
  ```

## Installation

### 1. Install Python dependencies

```bash
pip3 install -r requirements.txt --user
```

หรือใช้ virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### วิธีที่ 1: รันหาตัวประกอบแบบระบุจำนวน processes

```bash
mpirun -n <num_processes> python3 parallel.py <number>
```

**ตัวอย่าง:**
```bash
# รันด้วย 4 processes
mpirun -n 4 python3 parallel.py 34343434

# รันด้วย 8 processes
mpirun -n 8 python3 parallel.py 123456789
```

### วิธีที่ 2: รัน Benchmark (ทดสอบ 1-4096 processes)

รันและบันทึกผลลัพธ์เป็น CSV:

```bash
python3 benchmark.py
```

**Output:**
- แสดงเวลาที่ใช้สำหรับแต่ละจำนวน processes (1-16)
- บันทึกผลลัพธ์เป็น `benchmark_results_YYYYMMDD_HHMMSS.csv`
- คำนวณ speedup และ efficiency อัตโนมัติ

### วิธีที่ 3: สร้างกราฟวิเคราะห์ประสิทธิภาพ

หลังจากรัน benchmark แล้ว สร้างกราฟแบบ publication-quality:

```bash
python3 plot_results.py benchmark_results_YYYYMMDD_HHMMSS.csv
```

**Output:**
- สร้างโฟลเดอร์ `graphs/` พร้อมกราฟ 6 แบบ:
  1. `01_execution_time.png` - เวลาประมวลผล vs จำนวน processes
  2. `02_speedup_analysis.png` - การเปรียบเทียบ speedup
  3. `03_efficiency.png` - ประสิทธิภาพ parallel
  4. `04_dashboard.png` - Dashboard รวมทุกตัวชี้วัด
  5. `05_scalability.png` - วิเคราะห์ scalability
  6. `06_comparative_analysis.png` - วิเคราะห์เชิงเปรียบเทียบ
  7. `performance_report.txt` - รายงานสถิติแบบข้อความ

## Example Workflow

```bash
# 1. รัน benchmark
python3 benchmark.py

# 2. สร้างกราฟ (ใช้ไฟล์ CSV ที่ได้จากขั้นตอนที่ 1)
python3 plot_results.py benchmark_results_20251023_190107.csv

# 3. ดูผลลัพธ์
ls -lh graphs/
cat graphs/performance_report.txt
```

## Quick Test

ทดสอบว่าโปรแกรมทำงานได้:

```bash
# ทดสอบหาตัวประกอบของ 100 ด้วย 2 processes
mpirun -n 2 python3 parallel.py 100

# ผลลัพธ์ที่ได้: [2, 4, 5, 10, 20, 25, 50]
```

## Project Structure

```
1_parallel_6610502145/
├── parallel.py          # โปรแกรมหลักสำหรับหาตัวประกอบแบบ parallel
├── benchmark.py         # สคริปต์ทดสอบประสิทธิภาพ 1-16 processes
├── plot_results.py      # สคริปต์สร้างกราฟวิเคราะห์
├── requirements.txt     # Python dependencies
├── README.md           # เอกสารนี้
└── graphs/             # โฟลเดอร์เก็บกราฟ (สร้างอัตโนมัติ)
```

## Performance Metrics

โปรแกรมคำนวณตัวชี้วัดต่อไปนี้:

- **Execution Time**: เวลาที่ใช้ในการประมวลผล
- **Speedup**: S(n) = T(1) / T(n) เทียบกับการรัน 1 process
- **Efficiency**: E(n) = S(n) / n × 100%
- **Time Reduction**: เปอร์เซ็นต์การลดเวลาเทียบกับ baseline

## Troubleshooting

**ปัญหา: `ModuleNotFoundError: No module named 'mpi4py'`**
```bash
pip3 install mpi4py --user
```

**ปัญหา: `ModuleNotFoundError: No module named 'seaborn'`**
```bash
pip3 install seaborn matplotlib pandas --user
```

**ปัญหา: `mpirun: command not found`**
- ติดตั้ง OpenMPI ตาม Prerequisites ด้านบน
