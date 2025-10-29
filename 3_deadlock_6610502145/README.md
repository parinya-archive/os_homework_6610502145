# Deadlock Demonstration Program

โปรแกรมสาธิตสภาวะ Deadlock ด้วย 3 วิธีการ: Classic, Avoidance, Detection & Resolution

## 📋 ภาพรวมโปรแกรม

โปรแกรมนี้สาธิตการเกิด Deadlock และวิธีการจัดการในระบบปฏิบัติการ โดยใช้ทรัพยากรจำลองแทนทรัพยากรจริง

### ⚙️ ส่วนประกอบของโปรแกรม

```
3_deadlock_6610502145/
├── deadlock.py              # Main program - Classic deadlock demo
├── module/
│   ├── ResourceManager.py   # Manages resources with Banker's Algorithm & Wait-for Graph
│   ├── ProcThread.py        # Process/Thread class for simulation
│   └── __init__.py
├── util/
│   ├── func.py              # Helper functions (demo_avoidance, demo_detection)
│   └── __init__.py
├── READMD.md                # This file
└── __init__.py
```

---

## 🎯 ทั้ง 3 โหมดการทำงาน

### 1️⃣ **Classic Mode** (Deadlock ธรรมชาติ)
- **วิธีการ**: ใช้ 2 threads และ 2 locks
- **ลักษณะการเกิด**: 
  - Thread T1 เก็บ Lock A แล้วรออย Lock B
  - Thread T2 เก็บ Lock B แล้วรออย Lock A
  - → Circular Wait → **DEADLOCK**
- **ผลลัพธ์**: Threads ค้างตลอด ไม่สามารถทำงานต่อได้
- **Coffman's Conditions ที่เกิด**:
  - ✅ Mutual Exclusion (locks มี mutual exclusion)
  - ✅ Hold and Wait (hold lock และ wait for another)
  - ✅ No Preemption (ไม่สามารถดึง lock)
  - ✅ Circular Wait (T1→B, T2→A)

### 2️⃣ **Avoidance Mode** (Banker's Algorithm)
- **วิธีการ**: ใช้ Banker's Algorithm เพื่อ**ป้องกันไว้ก่อน**
- **ลักษณะการทำงาน**:
  - Process ขอทรัพยากร
  - System จำลองการให้ทรัพยากร
  - ถ้าผลลัพธ์ unsafe → **ปฏิเสธ** request (WAIT)
  - ถ้า safe → **อนุมัติ** request
- **ผลลัพธ์**: ไม่มี deadlock เกิดขึ้น (ป้องกันไว้ก่อน)
- **ข้อดี**: 100% ปลอดภัย
- **ข้อจำกัด**: Conservative (อาจปฏิเสธ request ที่ปลอดภัย)

### 3️⃣ **Detection & Resolution Mode** (WFG + Victim Abort)
- **วิธีการ**: **อนุญาต** deadlock เกิดแล้ว**ตรวจจับ**และ**แก้**
- **ลักษณะการทำงาน**:
  1. Process ขอทรัพยากรได้ทั้งหมด
  2. Watcher thread สร้าง Wait-for Graph (WFG)
  3. ตรวจหาวงจร (cycle) ใน WFG
  4. ถ้าเจอ cycle → เลือก victim (ถือทรัพยากรมากสุด)
  5. ยุติ victim และปล่อยทรัพยากรทั้งหมด
  6. System คลายล็อก และ process อื่นดำเนินต่อ
- **ผลลัพธ์**: Deadlock เกิด ↔ ตรวจจับและแก้อัตโนมัติ
- **ข้อดี**: Allows progress มากกว่า Avoidance
- **ข้อจำกัด**: Resource ที่ victim ทำงานกลายเป็นหมาย

---

## 🚀 วิธีใช้

### ข้อกำหนด
```bash
Python 3.7+ (สำหรับ type hints และ threading)
```

### การรันโปรแกรม

**1. Classic Mode - แสดง Deadlock ที่เกิดขึ้น**
```bash
python deadlock.py --mode classic
```
**คาดหวัง**:
```
[STEP 01] MODE: CLASSIC DEADLOCK DEMONSTRATION
[STEP 02] start program
...
[STEP XX] T1 trying to acquire Lock B
[STEP YY] T2 trying to acquire Lock A
...
[STEP ZZ] DEADLOCK CONFIRMED: threads still running (stuck waiting for locks)
```

**2. Avoid Mode - ป้องกัน Deadlock ด้วย Banker's Algorithm**
```bash
python deadlock.py --mode avoid
```
**คาดหวัง**:
```
[STEP 01] === DEMO: Avoidance (Banker's Algorithm) ===
[STEP 02] P1 registered with MAX=[1, 1], TOTAL=[1, 1]
[STEP 03] P2 registered with MAX=[1, 1], TOTAL=[1, 1]
[STEP 04] P1 REQUEST [1, 0]
[STEP 05] [Banker] simulate grant to P1: SAFE=True
[STEP 06] P1 GRANTED [1, 0]
[STEP 07] P2 REQUEST [0, 1]
[STEP 08] [Banker] simulate grant to P2: SAFE=False
[STEP 09] P2 WAIT (unsafe by Banker's)
...
[STEP XX] P1 FINISHED
[STEP YY] P2 GRANTED [0, 1]
[STEP ZZ] P2 FINISHED
```

**3. Detect Mode - ตรวจจับและแก้ Deadlock**
```bash
python deadlock.py --mode detect
```
**คาดหวัง**:
```
[STEP 01] === DEMO: Detection + Resolution (WFG + abort) ===
[STEP 02] P1 registered...
...
[STEP XX] [DETECT] cycle found: P1 -> P2 -> P1
[STEP YY] [RESOLUTION] choose victim=P2 (max allocation=[0, 1])
[STEP ZZ] P2 ABORTED -> released [0, 1]
[STEP AA] P1 FINISHED
```

---

## 📊 ตัวอย่างเอาต์พุท

### Classic Mode Output
```
[STEP 01] MODE: CLASSIC DEADLOCK DEMONSTRATION
[STEP 02] ============================================================
[STEP 03] Description: Two threads, each holding one lock and waiting for the other
[STEP 04] Expected: Deadlock will occur and threads will be stuck
[STEP 05] start program
[STEP 06] set traceback dump after 3 seconds (shows where threads are stuck)
[STEP 07] [MONITOR] No locks currently held
[STEP 08] start T1 and T2
[STEP 09] T1 starts
[STEP 10] T2 starts
[STEP 11] T1 trying to acquire Lock A
[STEP 12] T2 trying to acquire Lock B
[STEP 13] T1 acquired Lock A
[STEP 14] T2 acquired Lock B
[STEP 15] [MONITOR] Current locks held: Lock A=T1, Lock B=T2
[STEP 16] T1 waiting at Barrier (wait for T2 to reach same point)
[STEP 17] T2 waiting at Barrier (wait for T1 to reach same point)
[STEP 18] T1 trying to acquire Lock B (will block if T2 holds it)
[STEP 19] T2 trying to acquire Lock A (will block if T1 holds it)
[STEP 20] [MONITOR] Current locks held: Lock A=T1, Lock B=T2
[STEP 21] join with timeout 10 seconds (demonstrates deadlock - won't finish)
[STEP 22] checking thread status after join timeout
[STEP 23] T1 is_alive: True
[STEP 24] T2 is_alive: True
[STEP 25] DEADLOCK CONFIRMED: threads still running (stuck waiting for locks)
[STEP 26] ============================================================
```

---

## 🔍 ส่วนหลักของโค้ด

### 1. `deadlock.py`
- `classic_deadlock_demo()` - Classic mode implementation
- `main()` - Parse arguments และเลือก mode
- `t1()`, `t2()` - Two threads that create deadlock
- `acquire_lock()`, `release_lock()` - Helper functions

### 2. `module/ResourceManager.py`
- `request()` - Request resource (with Banker's check if enabled)
- `release()` - Release resource
- `_is_safe_if_grant()` - Banker's Algorithm safety check
- `build_wait_for_graph()` - Build WFG for detection
- `detect_cycle()` - Find cycle in WFG using DFS

### 3. `module/ProcThread.py`
- Process/Thread wrapper ที่ใช้ ResourceManager
- `run()` - Execute script of requests and releases

### 4. `util/func.py`
- `demo_avoidance_with_bankers()` - Run Avoidance demo
- `demo_detection_and_resolution()` - Run Detection demo
- `deadlock_watcher()` - Monitor thread for cycle detection

---

## 💡 Coffman's Conditions vs ทั้ง 3 วิธี

| Coffman's Condition | Classic | Avoidance | Detection |
|---|---|---|---|
| Mutual Exclusion | ✅ เกิด | ✅ เกิด | ✅ เกิด |
| Hold and Wait | ✅ เกิด | ❌ ไม่เกิด | ✅ เกิด |
| No Preemption | ✅ เกิด | ✅ เกิด | ❌ มี preemption (abort) |
| Circular Wait | ✅ เกิด | ❌ ป้องกัน | ✅ เกิดแล้วตรวจจับ |
| **ผล** | 💥 DEADLOCK | 🛡️ ป้องกัน | 🔧 แก้ไข |

---

## 📈 การเปรียบเทียบ 3 วิธี

```
Classic Mode (ธรรมชาติ):
  ✅ เห็นการเกิด deadlock จริงๆ
  ✅ ง่ายเข้าใจ
  ❌ ต้องรอ timeout

Avoidance (ป้องกัน):
  ✅ ไม่มี deadlock
  ✅ ปลอดภัย 100%
  ❌ Conservative (อาจเฉพาะอายอย)

Detection (ตรวจจับ):
  ✅ Allow more progress
  ✅ ระบบสามารถ recover
  ❌ ต้องยุติ victim
```

---

## 🛠️ Architecture

### Data Flow

```
deadlock.py (main)
    ↓
[--mode classic] → classic_deadlock_demo() → [2 Threads + 2 Locks]
[--mode avoid]   → demo_avoidance_with_bankers() → ResourceManager (Banker's ON)
[--mode detect]  → demo_detection_and_resolution() → ResourceManager (Banker's OFF) + Watcher

ResourceManager
    ├── Banker's Algorithm (_is_safe_if_grant)
    ├── Wait-for Graph (build_wait_for_graph)
    ├── Cycle Detection (detect_cycle)
    └── Resource Allocation
```

---

## 🧪 Test Scenarios

### Scenario 1: Classic Deadlock
```
Process: T1 acquire(A) → wait(B)
Process: T2 acquire(B) → wait(A)
Result: DEADLOCK ← Circular Wait
```

### Scenario 2: Banker's Avoidance
```
P1 need=[1,1], alloc=[0,0]  request=[1,0] → GRANT (safe)
P2 need=[1,1], alloc=[0,0]  request=[0,1] → WAIT (unsafe)
P1 finish & release          P2 request=[0,1] → GRANT
Result: NO DEADLOCK ← Prevented by Banker's
```

### Scenario 3: Detection & Resolution
```
P1, P2 both requesting (deadlock will occur)
Watcher detects cycle P1→P2→P1
Choose victim P2 (max allocation)
P2 aborted, resources released
Result: SYSTEM RECOVERS ← Detected & Resolved
```

---

## 📝 Output Interpretation

- `[STEP XX]` - Step number for tracking execution
- `[MONITOR]` - Lock status monitoring
- `[Banker]` - Banker's Algorithm safety check result
- `[DETECT]` - Deadlock cycle detection
- `[RESOLUTION]` - Victim selection and abort

---

## 🎓 Learning Outcomes

เมื่อรันโปรแกรมนี้ คุณจะเข้าใจ:

1. ✅ Deadlock คืออะไรและเกิดได้ยังไง
2. ✅ Coffman's 4 Conditions ที่ทำให้เกิด deadlock
3. ✅ วิธี **Avoidance** ด้วย Banker's Algorithm
4. ✅ วิธี **Detection** ด้วย Wait-for Graph
5. ✅ วิธี **Resolution** ด้วยการ abort victim
6. ✅ Trade-offs ระหว่างแต่ละวิธี

---

## 📊 Publication-Quality Visualizations

โปรแกรมนี้มาพร้อมสคริปต์สร้างกราฟคุณภาพสูง **7 รูป** สำหรับการนำเสนอและรายงาน:

### ✨ สร้างกราฟ

```bash
python visualize.py
```

**ผลลัพธ์**: สร้าง 7 รูปในรูปแบบ PNG และ PDF ที่ `figures/` directory

### 📈 รูปที่สร้างขึ้น

#### 1️⃣ **Coffman's Conditions**
- แสดง **4 เงื่อนไข** ของ Coffman ที่ทำให้เกิด Deadlock
- ใช้สีและหัวข้อที่ชัดเจน
- เหมาะสำหรับการบรรยาย

#### 2️⃣ **Classic Deadlock Sequence**
- แสดง **timeline** ของการเกิด deadlock
- ลูกศรแสดงการไหลของ threads
- ส่วนวงกลมแสดง circular wait

#### 3️⃣ **Wait-For Graph Detection**
- **3 scenarios**: ไม่มี cycle | Simple cycle | Complex cycle
- ใช้ DFS detection
- แสดงทั้งกรณี safe และ deadlock

#### 4️⃣ **Banker's Algorithm Flow**
- ขั้นตอนการทำงานของ Banker's Algorithm
- Flowchart แบบชัดเจน
- แสดง SAFE/UNSAFE checks และ decision paths

#### 5️⃣ **Three Approaches Comparison**
- **ตารางเปรียบเทียบ** 3 วิธี
- **Timeline graphs** สำหรับแต่ละวิธี
- Description ของแต่ละวิธี

#### 6️⃣ **Resource Allocation States**
- **Unsafe State** - ที่มีความเสี่ยง
- **Safe State** - ที่ปลอดภัย
- ตัวอย่างเชิงปริมาณของทรัพยากร

#### 7️⃣ **Detection & Resolution Flow**
- **8 ขั้นตอน** ของการตรวจจับและแก้ไข
- Flowchart แบบลำดับ
- ตั้งแต่ deadlock เกิด → recovery

### 🎨 คุณลักษณะของกราฟ

- ✅ **Publication-Quality**: DPI 300
- ✅ **Dual Format**: PNG (สำหรับการแสดง) + PDF (สำหรับพิมพ์)
- ✅ **Color-Coded**: ใช้สีที่สอดคล้องกัน
- ✅ **High Contrast**: อ่านง่าย
- ✅ **Professional Layout**: เหมาะสำหรับนำเสนอในการประชุมวิชาการ

### 📁 Output Files

```
figures/
├── 01_coffmans_conditions.{png,pdf}
├── 02_classic_deadlock_sequence.{png,pdf}
├── 03_wait_for_graph.{png,pdf}
├── 04_bankers_algorithm_flow.{png,pdf}
├── 05_three_approaches_comparison.{png,pdf}
├── 06_resource_allocation_states.{png,pdf}
└── 07_detection_resolution_flow.{png,pdf}
```

### 🖼️ ตัวอย่างการใช้งาน

**สำหรับรายงาน Word/PowerPoint:**
```
คัดลอก PNG files ได้โดยตรง
ความละเอียด 300 dpi เหมาะสำหรับพิมพ์
```

**สำหรับการพิมพ์หนังสือ/วารสาร:**
```
ใช้ PDF files ที่ resolution 300 dpi
ขนาด 14x10 นิ้ว สำหรับขนาดหน้า A4
```

**สำหรับการนำเสนอในการประชุมวิชาการ:**
```
ใช้ PNG files ที่ resolution สูง
ขนาดใหญ่พอสำหรับจอ projector
```

---

## 📚 Reference

- Coffman, E. G.; Elphick, M. J.; Shoshani, A. (1971). "System Deadlock Detection and Resolution"
- Banker's Algorithm - Edsger Dijkstra (1964)
- Wait-for Graph - Standard OS resource allocation technique

---

**โปรแกรมโดย**: นิสิต ID: 6610502145  
**วิชา**: Operating Systems  
**ปีการศึกษา**: 2024