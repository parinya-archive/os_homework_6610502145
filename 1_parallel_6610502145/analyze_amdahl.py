#!/usr/bin/env python3
"""
Amdahl's Law Analysis Tool
===========================
วิเคราะห์ผลการ benchmark เพื่อดึงค่า p (parallelizable fraction)
และสรุปข้อมูลสำหรับรายงาน

ใช้:
    python3 analyze_amdahl.py benchmark_results_YYYYMMDD_HHMMSS.csv [--advanced]

ตัวเลือก:
    --advanced   ใช้ nonlinear least-squares fitting หา p* ที่ดีที่สุด
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys


def analyze_amdahl_basic(csv_file):
    """
    วิเคราะห์พื้นฐาน: ถอด p_N รายจุด และคำนวณค่ากลาง

    จัดการกรณี sub-linear speedup (S < 1) ซึ่งแสดงว่า parallel version ช้ากว่า serial
    """
    print("\n" + "=" * 70)
    print("AMDAHL'S LAW ANALYSIS - BASIC MODE")
    print("=" * 70)

    df = pd.read_csv(csv_file)

    # กรอง N > 1 เพื่อคำนวณ p_N
    df_n = df[df["num_processes"] > 1].copy()

    N = df_n["num_processes"].to_numpy()
    S = df_n["speedup"].to_numpy()
    T = df_n["time_seconds"].to_numpy()
    T_serial = df.loc[df["num_processes"] == 1, "time_seconds"].iloc[0]

    # ถอด p_N รายจุด จากสูตร p_N = (1 - 1/S) / (1 - 1/N)
    # เฉพาะเมื่อ S > 0 (speedup valid)
    p_N = np.full_like(S, np.nan)
    for i, (n, s) in enumerate(zip(N, S)):
        if s > 0 and n > 1:
            p_N[i] = (1 - 1 / s) / (1 - 1 / n)

    df_n["p_N"] = p_N

    # ตรวจสอบ sub-linear
    is_sublinear = (S < 1).any()

    print(f"\n⚠️  DATA STATUS:")
    print(f"    Speedup range: {S.min():.3f} to {S.max():.3f}")
    if is_sublinear:
        print(f"    ❌ SUB-LINEAR SPEEDUP DETECTED!")
        print(f"       Parallel version is SLOWER than serial (S < 1)")
        print(f"       This indicates excessive MPI communication overhead")

    # คำนวณสถิติ (ใช้เฉพาะค่า p_N ที่ valid)
    p_valid = p_N[~np.isnan(p_N)]

    if len(p_valid) > 0:
        p_mean = np.mean(p_valid)
        p_median = np.median(p_valid)
        p_std = np.std(p_valid, ddof=1) if len(p_valid) > 1 else 0
        p_min = np.min(p_valid)
        p_max = np.max(p_valid)

        # สำหรับ sub-linear speedup, p อาจเป็นลบ (ไม่มีความหมาย)
        print(f"\n📊 ผลลัพธ์การวิเคราะห์:")
        print(f"   p_mean     = {p_mean:.4f}  (± {p_std:.4f})")
        print(f"   p_median   = {p_median:.4f}")
        print(f"   p_min      = {p_min:.4f}")
        print(f"   p_max      = {p_max:.4f}")

        if p_mean > 0:
            serial_frac = 1 - p_mean
            S_max = 1 / serial_frac if serial_frac > 0 else np.inf
            print(
                f"\n   Serial fraction (1-p) = {serial_frac:.4f} ({serial_frac * 100:.2f}%)"
            )
            print(f"   Parallel fraction (p) = {p_mean:.4f} ({p_mean * 100:.2f}%)")
            print(f"\n⚡ Amdahl's Law Ceiling:")
            print(f"   S_max ≈ 1/(1-p) ≈ {S_max:.2f}x")
        else:
            print(f"\n⚠️  Negative p values detected!")
            print(f"    This indicates parallel overhead > serial computation")
            print(f"    Model: T_parallel ≈ T_serial/S where S < 1")

    print(f"\n📈 ตารางรายละเอียด (N > 1):")
    print(
        df_n[
            ["num_processes", "time_seconds", "speedup", "efficiency", "p_N"]
        ].to_string(index=False)
    )

    return {
        "p_mean": p_mean if len(p_valid) > 0 else np.nan,
        "p_median": p_median if len(p_valid) > 0 else np.nan,
        "p_std": p_std if len(p_valid) > 0 else np.nan,
        "is_sublinear": is_sublinear,
        "df": df_n,
        "N": N,
        "S": S,
        "p_N": p_N,
    }


def analyze_amdahl_advanced(csv_file):
    """
    วิเคราะห์ขั้นสูง: ใช้ nonlinear least-squares fitting
    เพื่อหา p* ที่ฟิต S(N) ได้ดีที่สุด
    """
    try:
        from scipy.optimize import curve_fit
    except ImportError:
        print("❌ scipy ยังไม่ได้ติดตั้ง ให้ติดตั้ง: pip install scipy")
        return None

    print("\n" + "=" * 70)
    print("AMDAHL'S LAW ANALYSIS - ADVANCED MODE (FITTING)")
    print("=" * 70)

    df = pd.read_csv(csv_file)
    df_n = df[df["num_processes"] > 1].copy()

    N = df_n["num_processes"].to_numpy().astype(float)
    S_observed = df_n["speedup"].to_numpy()

    # ฟังก์ชัน Amdahl: S(N) = 1 / ((1-p) + p/N)
    def amdahl(N, p):
        return 1.0 / ((1 - p) + p / N)

    # Fit โดยเริ่มจากค่า initial guess p=0.5
    try:
        popt, pcov = curve_fit(
            amdahl, N, S_observed, p0=[0.5], bounds=(0, 1), maxfev=5000
        )
        p_optimal = popt[0]
        p_std_fit = np.sqrt(np.diag(pcov))[0]

        # คำนวณ prediction และ residuals
        S_predicted = amdahl(N, p_optimal)
        residuals = S_observed - S_predicted
        rmse = np.sqrt(np.mean(residuals**2))
        r_squared = 1 - (
            np.sum(residuals**2) / np.sum((S_observed - S_observed.mean()) ** 2)
        )

        print(f"\n🎯 Fitting Results:")
        print(f"   p*           = {p_optimal:.4f} ± {p_std_fit:.4f}")
        print(f"   Serial (1-p) = {1 - p_optimal:.4f}")
        print(f"   RMSE         = {rmse:.4f}")
        print(f"   R²           = {r_squared:.4f}")
        print(f"\n   S_max (theory) = {1 / (1 - p_optimal):.2f}x")

        # ตารางเปรียบเทียบ observed vs predicted
        df_n["speedup_predicted"] = S_predicted
        df_n["residual"] = residuals

        print(f"\n📊 Comparison (Observed vs Predicted):")
        print(
            df_n[
                ["num_processes", "speedup", "speedup_predicted", "residual"]
            ].to_string(index=False)
        )

        return {
            "p_optimal": p_optimal,
            "p_std": p_std_fit,
            "rmse": rmse,
            "r_squared": r_squared,
            "df": df_n,
        }

    except Exception as e:
        print(f"❌ Fitting failed: {e}")
        return None


def generate_summary(basic_result, advanced_result=None):
    """
    สรุปผลสำหรับรายงาน (summary for report)
    """
    print("\n" + "=" * 70)
    print("📋 SUMMARY FOR REPORT")
    print("=" * 70)

    is_sublinear = basic_result.get("is_sublinear", False)

    if is_sublinear:
        print(f"""
⚠️  ผลการวิเคราะห์ Amdahl's Law - กรณี SUB-LINEAR SPEEDUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  ข้อเท็จจริงสำคัญ:
  • Speedup < 1.0 → Parallel version ช้ากว่า Sequential
  • ดังนั้น Amdahl's Law model ไม่เหมาะสำหรับกรณีนี้

🔍 สาเหตุ:
  1. MPI Communication Overhead ใหญ่เกินไป
     - Time to communicate > Time to compute

  2. Granularity ของปัญหาน้อยเกินไป
     - ปัญหาขนาดเล็ก ใช้ parallelization ไม่ได้ผล

  3. Static Load Balancing ไม่สมดุล
     - บางโปรเซส idle ขณะที่คนอื่นยังทำงาน

  4. MPI Library Initialization Overhead
     - การเริ่มต้น MPI ใช้เวลาเพิ่มเติม

📊 ข้อมูลจากการวัด:
  • Speedup min = {basic_result["S"].min():.3f}x
  • Speedup max = {basic_result["S"].max():.3f}x
  • ไม่มีประโยชน์จากการเพิ่ม processes

🎯 ข้อเสนอแนะ:
  1. เพิ่มขนาดปัญหา (problem size) ให้ใหญ่ขึ้น
  2. ลดจำนวน processes ที่ใช้ (อาจมีเพียง 2-4 เท่านั้นที่ดีที่สุด)
  3. ปรับปรุง Load Balancing (dynamic scheduling)
  4. ลดจำนวนครั้งของการ communicate/synchronize
""")
    else:
        p_mean = basic_result.get("p_mean", 0)
        serial_frac = 1 - p_mean
        S_max = 1 / serial_frac if serial_frac > 0 else np.inf

        print(f"""
ผลการวิเคราะห์ Amdahl's Law จากข้อมูลการวัดจริง
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ค่าที่ได้จากการคำนวณ:
  • สัดส่วนงาน parallelizable (p) ≈ {p_mean:.4f} ({p_mean * 100:.2f}%)
  • สัดส่วนงาน serial (1-p) ≈ {serial_frac:.4f} ({serial_frac * 100:.2f}%)

ทำนายเพดาน speedup:
  • S_max ≈ 1/(1-p) ≈ {S_max:.2f}x

ข้อสังเกต:
  • ค่า speedup ที่วัดได้มี saturation เร็วกว่าที่ทำนายจาก Amdahl
  • สาเหตุ: Overhead ในการ gather ผล, static load balancing ที่ไม่สมดุล
""")

    if advanced_result:
        p_opt = advanced_result["p_optimal"]
        rmse = advanced_result["rmse"]
        r2 = advanced_result["r_squared"]

        print(f"""
ผลจากการ Fitting (Amdahl Model):
  • p* (optimal) = {p_opt:.4f}
  • RMSE = {rmse:.4f}
  • R² = {r2:.4f}

อภิปราย:
  • ค่า RMSE ที่สูง บ่งชี้ว่า Amdahl model โดยลำพัง ไม่สามารถอธิบายการทำงาน
  • ปัจจัยอื่น เช่น communication overhead หรือ load imbalance มีบทบาท
""")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nตัวอย่าง:")
        print("  python3 analyze_amdahl.py benchmark_results_20251029_143212.csv")
        print(
            "  python3 analyze_amdahl.py benchmark_results_20251029_143212.csv --advanced"
        )
        sys.exit(1)

    csv_file = sys.argv[1]
    advanced_mode = "--advanced" in sys.argv

    if not Path(csv_file).exists():
        print(f"❌ ไฟล์ {csv_file} ไม่พบ")
        sys.exit(1)

    # วิเคราะห์พื้นฐาน
    basic_result = analyze_amdahl_basic(csv_file)

    # วิเคราะห์ขั้นสูง (ถ้าขอ)
    advanced_result = None
    if advanced_mode:
        advanced_result = analyze_amdahl_advanced(csv_file)

    # สรุปสำหรับรายงาน
    generate_summary(basic_result, advanced_result)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
