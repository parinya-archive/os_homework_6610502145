# OS Report 2025

โค้ดและรายงานสำหรับวิชา Operating Systems ปีการศึกษา 2025 — เลือกทำ 2 หัวข้อ ได้แก่ parallel integer factorization และ deadlock handling. ที่นี่มีซอร์สโค้ด สคริปต์ทดลอง รายงานฉบับเต็ม และเอกสารประกอบการรันทั้งหมด

## Repository Layout
```
.
├── 1_parallel_6610502145/    # Parallel factorization with MPI + analytics scripts
├── 3_deadlock_6610502145/    # Deadlock classic/avoid/detect demo + visualizations
├── report/                   # Typst sources and final PDF report
├── README.md                 # ไฟล์นี้
└── LICENSE
```

## How to Run the Projects

### 1. Parallel Integer Factorization (`1_parallel_6610502145`)
- **Dependencies**: Python 3.10+, `mpi4py`, `numpy`, `pandas`, `matplotlib`, `seaborn`, และ OpenMPI หรือ MPICH
- **Setup**:
  ```bash
  cd 1_parallel_6610502145
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Factor a number with N ranks**:
  ```bash
  mpirun -n 4 python parallel.py 34343434
  ```
- **Benchmark (1–16 ranks) & collect CSV**:
  ```bash
  python benchmark.py
  ```
- **Generate performance charts & report**:
  ```bash
  python plot_results.py benchmark_results_YYYYMMDD_HHMMSS.csv
  ```
- รายละเอียดเชิงลึกและ troubleshooting อยู่ใน `1_parallel_6610502145/README.md`

### 3. Deadlock Demonstration (`3_deadlock_6610502145`)
- **Dependencies**: Python 3.9+ (ใช้มาตรฐานในไลบรารี `threading`, `dataclasses`, `itertools`, `matplotlib`)
- **Run classic two-lock deadlock**:
  ```bash
  cd 3_deadlock_6610502145
  python deadlock.py --mode classic
  ```
- **Run Banker's Algorithm avoidance demo**:
  ```bash
  python deadlock.py --mode avoid
  ```
- **Run wait-for graph detection & victim resolution**:
  ```bash
  python deadlock.py --mode detect
  ```
- **Build publication-quality figures**:
  ```bash
  python visualize.py
  ```
- รายละเอียดกระบวนการ, expected outputs, และคำอธิบายกราฟอยู่ใน `3_deadlock_6610502145/README.md`

## Report & Submission Assets
- รายงานฉบับเต็ม: `report/report.pdf` (จัดรูปด้วย Typst แหล่งที่มาอยู่ในไดเรกทอรีเดียวกัน)
- Copy-on-Write ไม่ได้เลือกทำ จึงไม่มีโฟลเดอร์ที่ 2 ตามข้อกำหนดการบ้าน
- โครงสร้างโฟลเดอร์ตามเทมเพลตส่งงานที่อาจารย์กำหนด พร้อม README หลัก 1 ไฟล์ตรงนี้

## Notes for Reviewers / TAs
- ตรวจสอบผลการทดลองได้จากไฟล์ CSV และกราฟในโฟลเดอร์ของแต่ละโปรเจกต์
- สคริปต์ benchmark และ visualization ไม่มี side effect ที่เป็นอันตรายต่อระบบ (ปฏิบัติตามหลัก DO NO HARM)
- หากรันบนระบบใหม่ ให้ติดตั้ง MPI (สำหรับหัวข้อ parallel) หรือ Python packages ตามคำแนะนำก่อนเท่านั้น

## Educational Use Disclaimer
ซอร์สโค้ดและเอกสารภายใน repository นี้จัดทำเพื่อการเรียนรู้ในรายวิชา Operating Systems เท่านั้น ไม่ได้ตั้งใจเผยแพร่เพื่อการใช้งานจริงในระบบผลิตหรือการใช้งานสาธารณะอื่นใด
