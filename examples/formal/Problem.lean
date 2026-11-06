-- Lean 4.35.0 + Mathlib（工程：~/.dsh/lean-verify/mathlib-src）
-- 运行：lean_verify projectDir=... label=forge-v13-example
-- 判定：✅ 内核已验证（退出码 0；公理 propext, Classical.choice, Quot.sound）
-- run 目录：~/.dsh/lean-verify/runs\2026-11-06T08-53-37-864Z-forge-v13-example

import Mathlib

/-- 基题第 1 步：完全平方展开 -/
example (x y : ℝ) : (x + y)^2 = x^2 + 2*x*y + y^2 := by ring

/-- 基题第 2 步：移项得 x²+y² = (x+y)² - 2xy -/
example (x y : ℝ) : x^2 + y^2 = (x + y)^2 - 2*x*y := by ring

/-- 基题：x+y=5, xy=6 ⇒ x²+y²=13 -/
example (x y : ℝ) (h1 : x + y = 5) (h2 : x * y = 6) : x^2 + y^2 = 13 := by
  nlinarith

/-- A 类 同质异述：换字母/换说法，本质同一命题 -/
example (a b : ℝ) (h1 : a + b = 5) (h2 : a * b = 6) : a^2 + b^2 = 13 := by
  nlinarith

/-- B 类 同质增条件（增思维深度）：三次幂需要恒等式 -/
example (x y : ℝ) (h1 : x + y = 5) (h2 : x * y = 6) : x^3 + y^3 = 35 := by
  have key : x^3 + y^3 = (x + y)^3 - 3 * (x * y) * (x + y) := by ring
  rw [key, h1, h2]
  norm_num

/-- C 类 形似神异：同样给和与积，但无实数解；默认套公式会算出 11 -/
example : ¬ ∃ x y : ℝ, x + y = 5 ∧ x * y = 7 := by
  rintro ⟨x, y, h1, h2⟩
  nlinarith [sq_nonneg (x - y)]

/-- 说明「空真」：假设本身矛盾时，任何结论都成立；不能把这条当答案依据 -/
example (x y : ℝ) (h1 : x + y = 5) (h2 : x * y = 7) : x^2 + y^2 = 11 := by
  nlinarith [sq_nonneg (x - y)]

/-- 算法题：前 n 项和 -/
def sumTo : Nat → Nat
  | 0 => 0
  | n + 1 => (n + 1) + sumTo n

theorem sumTo_correct (n : Nat) : 2 * sumTo n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ k ih =>
      simp [sumTo]
      nlinarith