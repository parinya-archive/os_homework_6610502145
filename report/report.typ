#import "function.typ": *
#import "graph.typ": *

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


เขียนโปรแกรมแยกตัวประกอบของจำนวนขนาดใหญ่ n (factorization) โดยใช้เครื่องมือคือ MPI4py


+ การเลือกใช้ algorithm ในงานการแยกตัวประกอบขนาด n ใช้ algorithm ของ #link("https://www.geeksforgeeks.org/dsa/pollards-rho-algorithm-prime-factorization/")[*Pollard's Rho Algorithm*]
  // intiilzie
  + start intiilze value $g(x) = x^2 + 1 (mod n)$ let value  c = 1
  + intiilze variable $x_0 = 2$\
    $x_i = g(x_(i-1))$

  // while d == 1
  + define value $"T" = x_0$ and $"H" = x_0$\
    $T arrow.l g("T")$\
    $H arrow.l g(g("T"))$\

  // check result
  + check $#math.text("gcd")(S - F, n) > 1$
    - $T = H arrow.r.double #math.text("gcd")(0, n) = n > 1$
    - $d = #math.text("gcd")(abs(T - H), n)$
    - if $d = 1$ loop ต่อ
    - if $1 lt d lt n$ find it $d$ is factor of n
    - if $d == n$ fail change parameter


  คำเตือน: algortihm นี้จะไม่หยุดถ้า n เป็นจำนวนเฉพาะดังนั้นเราจะตั้งค่า loop iterator ด้วย และล้มเหลวลองปรับ parameter

  Time Complexity: $O(sqrt(d) log(n))$

#header[Graph Visualization Example]

ตัวอย่างนี้ใช้ฟังก์ชัน `graph_chart` ที่สร้างไว้ในโปรเจ็กต์เพื่อวาดกราฟเส้นแสดงแนวโน้มเวลาประมวลผลจากข้อมูลสมมติ:

#let graph_data = (
  (0, 0),
  (2, 2),
  (3, 0),
  (4, 4),
  (5, 7),
  (6, 6),
  (7, 9),
  (8, 5),
  (9, 9),
  (10, 1),
)

#graph_chart(
  graph_data,
  size: (100%, 30%),
  caption: [กราฟตัวอย่างพร้อมคำอธิบาย],
  x_ticks: 5,
  y_ticks: 5,
  line_color: blue,
)

#header[Copy on Write]

ทำให้โปรแกรมแสดงให้เห็นถึงการทำงานของประบวนการ Copy on Write


#pagebreak()

#text(
  weight: "bold",
)[
  Reference:
]
+ Pollard's rho algorithm, *Wikipedia, The Free Encyclopedia*, 18 Apr. 2025. [Online]. Available: https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm. Accessed: Oct. 9, 2025.\
+ *Pollard’s Rho Algorithm for Prime Factorization*, *GeeksforGeeks*, 2024. [Online]. Available: https://www.geeksforgeeks.org/dsa/pollards-rho-algorithm-prime-factorization/. Accessed: Oct. 9, 2025.
