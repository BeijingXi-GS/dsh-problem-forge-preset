# 示例：Lean 形式化验证报告（v1.3）

## 环境

- Lean 4.35.0（managed）
- Mathlib 工程：`~/.dsh/lean-verify/mathlib-src`
- 工具：`lean_verify`（lean-verify 插件）

## 机器证据

| 项 | 值 |
|---|---|
| run 目录 | `~/.dsh/lean-verify/runs\2026-11-06T08-53-37-864Z-forge-v13-example` |
| 退出码 | 0 |
| 判定 | ✅ 内核已验证 |
| 公理 | `propext`, `Classical.choice`, `Quot.sound` |
| `sorry` / `admit` | 0 |
| 自定义 `axiom` | 0 |

## 逐条对账

| 条目 | theorem / example | 判定 | 假设对账 | 结论对账 |
|---|---|---|---|---|
| 基题第 1 步 | `(x+y)^2 = x^2+2xy+y^2` | ✅ | 无额外假设 | 完全平方展开 |
| 基题第 2 步 | `x^2+y^2 = (x+y)^2-2xy` | ✅ | 无额外假设 | 移项恒等 |
| 基题 | `x+y=5 ∧ xy=6 → x^2+y^2=13` | ✅ | `h1`↔「x+y=5」；`h2`↔「xy=6」 | ↔ 所求 13 |
| A 类 | `a+b=5 ∧ ab=6 → a²+b²=13` | ✅ | 换字母，命题同构 | ↔ 同基题 |
| B 类 | `x+y=5 ∧ xy=6 → x³+y³=35` | ✅ | 同基题假设 | ↔ 三次幂所求 35 |
| C 类 | `¬ ∃ x y, x+y=5 ∧ xy=7` | ✅ | 同形假设 | ↔ 「无实数解，默认公式 11 不成立」 |
| 算法 | `sumTo_correct` | ✅ | 无 | ↔ 前 n 项和公式 |

## 陈述对账说明

- Lean 证的是上表 theorem，不自动证明它忠实于原题；本表逐条给出「假设 ↔ 题面」「结论 ↔ 所求」。
- C 类另有一条 `x²+y²=11` 在矛盾假设下成立（空真），仅用于说明「不能拿空真命题当答案」，不作为解题依据。
- 未覆盖：无（本题组全部可形式化）。

## 备注

- 复现命令：`lean_verify code=<Problem.lean> projectDir="~/.dsh/lean-verify/mathlib-src" label=forge-v13-example`
- Mathlib 首次 `import` 约 1–3 分钟；整组一次编译。