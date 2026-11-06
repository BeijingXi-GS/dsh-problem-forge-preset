-- 未编译：未经 lake env lean 运行；本文件仅为 §2.6 降级骨架（NOT_ATTEMPTED）
-- 目标：只形式化临界速度的代数关系与「错解≠正解」的反例恒等式
-- 缺口（对账 §4-6）：「内侧轨道 ⇒ N ≥ 0」「临界在顶点」是物理判断，未形式化
import Mathlib

theorem circle_critical_speed
    (v0 vtop g R : ℝ) (hg : 0 < g) (hR : 0 < R)
    (hcrit : vtop ^ 2 = g * R)
    (hE : v0 ^ 2 = vtop ^ 2 + 4 * g * R) :
    v0 ^ 2 = 5 * g * R := by
  nlinarith

-- 错解的代数指纹：(2√(gR))² = 4gR ≠ 5gR
theorem wrong_model_square (g R : ℝ) (hg : 0 < g) (hR : 0 < R) :
    (2 * Real.sqrt (g * R)) ^ 2 = 4 * g * R := by
  rw [mul_pow]
  norm_num
  rw [Real.sq_sqrt (le_of_lt (mul_pos hg hR))]
  ring

-- 若装好 Lean：lake env lean ProblemB.lean
-- 再查 #print axioms circle_critical_speed（应 ⊆ [propext, Classical.choice, Quot.sound]）