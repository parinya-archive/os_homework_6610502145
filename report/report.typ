#import "function.typ": *

#set page(
  paper: "a4",
  numbering: "1",
  header: align(right)[
    #text("Parinya Aobaun 6610502145", size: 10pt)
  ],
)

#set text(
  size: 12pt,
  font: "Liberation Sans",
)

#topic[OS report 2025]
#header[Intro to Parallel Programming]

*Algorithm Exlanation*\
ใช้ Algorithm แยกตัวประกอบของ $n$ แบบลองไปเรื่อยๆตั้งแต่ $1$ ถึง $sqrt(n)$\
หลักการที่ใช้ของ parallel คือการแบ่งจำนวนเป็น chunk แล้วให้แค่ละ process รันในส่วนของตัวเอง\
*Pseudo-code*
```
- Input: n, process
- แบ่งช่วง $[2, sqrt(n)]$ ออกเป็นจำนวน process ช่วง
- ไล่เช็คหาว่า n หารในช่วงตัวเองและบันทึกตัวที่
- ให้ "MPI.Gather" รวมกันแล้วจัดรูปผลเป็นชุดของตัวประกอบ
```
*Implementation notes*
- *Libraries*: python 3.13.9, mpi4py
- *I/O*: อ่าน n จาก argument ของไฟล์บันทึกเวลาและหน่วยความจำ
- *Correctness*: cross-check เทียบ version sequenctial ตอน process = 1
*Experiment setup*
- *Hardware*: 13th Gen Intel(R) Core(TM) i5-13500H, RAM 15 GiB
- *OS & Runtime*: Fedora Linux 42 (Workstation Edition) x86_64
- *Parameters*: n หลายขนาด และจำนวน process ตั้งแต่ 1 ถึง 15

*Performance Analysis*\
#h(2em) การวัดผลที่ใช้เวลาจำนวน processes เทียบกับจำนวนวินาทีและ speed up เมื่อเทียบกับ 1 process และวัด efficiency ต่อ 1 core\
ตาม Amdahl's Law สูตรคือ $S = 1 / ((1- p) + P/N)$\
โดยที่
- $S$ คือ speed up
- $N$ คือ จำนวน process
- $p$ คือ จำนวน task ที่ parallel ได้
- $1-p$ คือ จำนวน task ที่ serquencial

*Result*
เป้าหมาย: หาว่า program มีส่วนของ parallel part และ sequential part เท่าไร
จากความสัมพันธ์ $S(N) = 1/((1-p) + p/N)$ จะหา $p$\
+ หาค่า baseline $T(1)$
  โดยดูจากค่า csv ตรงที่ $T(1)$
+ จัดรูปสมการให้หาค่า $p_(n)$
  + จาก $S(N) = 1/ ((1-p) + P/N)$
  + $1/S(N) = 1-p(1 - 1/N) bb(arrow) p = (1-1/(S(N)))/(1-1/N)$
+ หาค่า $p_(n)$ สำหรับ $n = 1, 2, 3, 4,...$
$
  p_(n) = (1-1/(S(N)))/(1-1/N)
$
+ รวมค่า $p_(N)$ เพื่อค่า $p$ ที่กลางที่สุด
  วิธีคือเอาค่าเฉลี่ยของ median ของ $p_(N)$ ด้วย $p_(N) = (1-1/S(N))/ 1-1/N$

*Summary*
จากการคำนวณพบว่า parallelizable = 72.43% และส่วนของ serial = 27.57 % โดยใช้



#figure(
  image("../1_parallel_6610502145/min_graph/01_execution_time.png", width: 80%),
  caption: [speed up เมื่อเลขน้อย],
)
#figure(
  image("../1_parallel_6610502145/max_graph/01_execution_time.png", width: 80%),
  caption: [speed up เมื่อเลขน้อย],
)

*Analysis*
- Speed up เพิ่มขึ้นตามจำนวน process แต่เริ่มชะลอเมื่อเกินขนาด X เพราะ overhead (คอขวดตรง communication และ sync)
- Efficience ต่อ core ลดลงเมื่อ process มากขึ้นตาม *Amdahl's Law*: $S = 1 / ((1- p) + P/N)$


#pagebreak()
#header[deadlock]\
#h(2em) เป็นการจำลอง deadlock โดยมี 3 แนวทางคือ
  + Avodiance (Banker's),
  + Detection (Wait-for Graph),
  + Resolution (find process and abort)


*Simulated Resource*
- total: เวกเตอร์ของทรัพยากรแต่ละชนิดทั้งหมด
- available: เวกเตอร์ของทรัพยากรที่ยังว่างอยู่
- max[pid]: เวกเตอร์ความต้องการสูงสุด each process
- alloc[pid]: เวกเตอร์ของทรัพยากรที่ยังจัดสรรค์อยู่
- need[pid]: max[pid] - alloc[pid]
- alive[pid]: สถานะว่า process ว่ายังมีชีวิตอยู่หรือ abort ไปแล้ว
- waiting_req[pid]: คำขอปัจจุบันในการสร้าง WFG

*Coffman's Deadlock Conditions*
ใน deadlock.py สร้าง thread $T_1$ และ $T_2$ และล็อค A/B:
- Mutual Exclusion: Lock A/B เขาถึงทีละ thread
- Hold and wait: $T_1$ ถือ A แล้วรอ B ในตอนนั้นเอง $T_2$ ถือ B แล้วรอ A
- No preemption: ล็อคไม่ถูกยึดคืนอัตโนมัติ
- Circular wait: $T_1 arrow A "wait" B$, $T_2 arrow B "wait" A$ เป็นวงจร

*Deadlock Avoidance using Banker's Algorithm*
ในโค้ด python เมื่อ ResourceManager(use_bankers=True)
1. request(pid, req) ถ้าจะลองทำให้ update available alloc need ชั่วคราว
2. เรียก is_safe_state() หา safe sequence:
  - work = available.copy()
  - finish[pid] = False by default
  - วนหา process ที่ need[pid] $lt.eq$ work แล้วก็ทำจนจบแล้ว finish[pid] = True
  - ถ้าทำจน finish ทุกโปรเซส = True ก็คือ safe ไม่งั้น unsafe
3. ระบบนี้ไม่เข้าสู้ unsafe state เสี่ไม่มี deadlock แน่นอน

*Deadlock Detectoin using Wait-for Graph*
เมื่อ ResourceManager(use_bankers=False) และมีคำขอที่รอ:
- build_wait_for_graph() ส่วน wait for graph
  โหนด = process, edge = p รอ q
- detect_cycle(wait for graph) ใช้ 2 color problem ตรวจวงวรแล้วพบว่า deadlock เกิดขึ้นแล้ว

*Deadlock Resolution using Victim Selection and abort*
เมื่อพบ cycle:
  - เลือก victim แล้วแต่นโยบายเช่น
    1. ถือทรัพยากรเยอะ
    2. อยู่นาน
  - release_all_and_abort(vicim) คืนทรัพยากรทั้งหมดของเหยื่อโดยการ alive[victim]=False, ล้าง waiting_req
  - ปลุกตัว tread อื่นแล้วดำเนินการต่อ

#pagebreak()
#text(
  weight: "bold",
)[
  Reference:
]
+ https://mpi4py.readthedocs.io/en/stable/
