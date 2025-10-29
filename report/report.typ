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
#h(2em) เป็นการจำลอง deadlock ด้วย coffman's Condition โดยใช้ python\
โดยจะจำลองโดยการมีมากกว่า 2 thread จับจองทรัพยากรพร้อมกัน ตรวจจับโดยการใช้ wait for graph และจับเวลา

#pagebreak()
#text(
  weight: "bold",
)[
  Reference:
]
+ https://mpi4py.readthedocs.io/en/stable/
