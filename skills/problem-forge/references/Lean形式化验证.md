# Lean 4 形式化验证：答案核验第 ③ 级的执行手册

> **v2 更新（2026-11-06，优先于下文）**
> 本机已安装 Lean **4.35.0** 与 Mathlib 工程 `~/.dsh/lean-verify/mathlib-src`；插件 `lean-verify` 提供 `lean_env` / `lean_verify` / `lean_probe`。本预设 **v1.3 起**，数学/几何/算法/计算类题（含每道子题与变式）**强制**形式化验证，只认 `✅ 内核已验证`（退出码 0、无 `sorry`、公理干净），并须附 run 目录。
> 下文 §2–§8 的语法、模板、对账方法仍适用，但以下表述已被取代：①「本文所有代码都是未编译骨架」不再成立（`SKILL.md §2.6` 的模板已真实跑通，run 见 `examples/formal/VERIFICATION.md`）；②「无工具链可降级 NOT_ATTEMPTED」只适用于**不适用类**（纯尺规作图、实验设计、开放论述等，须逐题写理由）；③ 坐标化几何已纳入强制范围，纯尺规作图仍不适用。
> 一句话：**先自然语言解 → 再形式化 → 整组一次编译 → 对账 → 附机器证据**；做不了就停下求助，不许口头宣称已验证。

> 用途：为「题目拆解与变式设计师」补上答案核验的最强一级——把可代数化的中学/竞赛结论写成 Lean 4 定理并编译通过。
> 定位：核验三级中的 ③（① 自然语言严谨证明 + 第二解法 → ② Python/SymPy 机验 → ③ Lean 形式化）。③ 最强，也最贵、最易翻车；本文重点不是炫技，而是**怎么诚实做，以及做不了时怎么诚实说做不了**。
> 版本：v1（2026-11-05），v2 补丁（2026-11-06）。配合 `problem-forge/SKILL.md` §2.6（强制形式化）、§8（学科校验）、§8.0（伪证七类 P1–P7）、§9（质量门）使用。

> **⚠ 前置声明（读完再看代码）**
> 1. **本文所有 Lean 代码都是「未编译骨架」。** 写作时本机 `where.exe lean` / `where.exe lake` / `where.exe elan` 均无输出——没有工具链，**没有编译过任何一行**。任何代码块必须在本机跑通并贴出输出，才允许把状态写成 `VERIFIED`。
> 2. 语法与 tactic 名已对照 Mathlib 官方文档核对（§10-A）；**未核实项集中在 §10-B 逐条标注**。
> 3. **禁用四句话**：「已验证」「编译通过」「显然成立」「应该没问题」。状态只有 §3 的四个枚举值，没有第五个。

---
## §1 什么时候值得上 Lean

**判据：结论能否写成无歧义的命题。** Lean 证的是一个陈述，不是"一道题"。

| 适合（性价比高） | 典型形态 | 为什么划算 |
|---|---|---|
| 恒等式 / 因式分解 | `(x+y)^2 = x^2+2xy+y^2` | `ring` 一次闭环，毫秒级 |
| 不等式（多项式、有理式） | `x^2+1 ≥ 2x`、`a²+b² ≥ 2ab` | 喂平方非负提示即可 |
| 数论 / 整除 / 同余 | `3 ∣ n^3-n`、奇偶性 | `omega` + 分情形，逻辑无缝 |
| 组合恒等式 / 求和 | `2∑k = n(n-1)` | 归纳 + `ring`，专治漏边界项 |
| 可代数化的单调性、参数范围 | 二次函数在区间上单调、恒成立转最值 | 量化结构显式，方向错（P4）会被编译器抓住 |

| 不适合（别硬上） | 原因 |
|---|---|
| 纯几何作图（辅助线、尺规、轨迹） | Lean 里没有"图上看得见"；坐标化后证明量爆炸，收益低于 ① 级解析法核验 |
| 物理建模的**语义**（"恰好不脱离"到底翻译成什么） | Lean 只验证你写的方程，物理判断不在形式化范围内（见下） |
| 概率应用题 | 需先形式化样本空间与均匀性假设，成本远超题目价值 |
| 超大计算 / 依赖外部数据 | 形式化计算 ≠ 快速计算（用 ② 级 Python）；数据不可形式化，只能核验"给定数据下推理成立" |

**形式化鸿沟（最容易自欺的一条）**：

> **Lean 证明的是你写的 `theorem`；它不证明这个 `theorem` 忠实于原题。**

四类偏差必须逐条对账（§4-6）：① **漏假设**——原题有 $x>0$ 而你没写 `hx : 0 < x`，证的是更强命题（多半直接编译失败，算幸运）；② **多假设**——偷偷加"不妨设 $a\le b$"，编译通过但结论比原题弱，**最危险**；③ **语义漂移**——Lean 的 `/` 是全函数（`a/0 = 0`），中学"分母不能为 0"是定义域限制，Lean 里却是一条恒真等式；④ **空真**——假设互相矛盾时任何结论都成立，证完零信息，必须补非空性检查（§5.6）。

对冲只有两条：**写定理前列出"变量类型 / 假设表 / 结论"三列；证完后逐条对账并把对账表写进报告。** 没有对账表的 `VERIFIED` 一律按"陈述未核"处理，不算通过。

---
## §2 环境检测与安装

```powershell
# 注意：where 在 PowerShell 里是 Where-Object 的别名，必须写 where.exe
where.exe lean      # 期望 %USERPROFILE%\.elan\bin\lean.exe
where.exe lake
where.exe elan
lean --version      # 期望形如：Lean (version 4.x.y, commit ..., Release)
```
**坑**：写 `where lean` 不会报"找不到文件"，而是走 `Where-Object`，输出为空或一段无关对象——极易误判。统一用 `where.exe` 或 `Get-Command lean -ErrorAction SilentlyContinue`。判定：`lean` 与 `lake` 都有输出且 `--version` 打印版本号才算可用；**只有 `lean` 没有 `lake` 等于不能做 Mathlib 验证**（`import Mathlib` 靠 lake 注入依赖路径）。

安装（**必须先拿到用户同意**）：

```powershell
# 1) 装 elan（Lean 版本管理器，顺带装 lean + lake）；装完关掉重开终端（PATH 要刷新）
Invoke-WebRequest https://elan.lean-lang.org/elan-init.ps1 -OutFile elan-init.ps1
./elan-init.ps1 -y
# 2) 建项目（锁 lean-toolchain）→ 更新依赖 → 拉 Mathlib 预编译缓存（关键，跳过会退化为本地全量编译）
lake new problem math
cd problem
lake update
lake exe cache get
# 3) 编译单文件（项目根目录执行，lake env 负责注入 LEAN_PATH）
lake env lean Problem.lean
```
- 官方页现用写法是 `lake +v4.24.0 new my_project math`（`+vX.Y.Z` 只锁 `lake` 自身版本，不改项目的 Lean 版本）；不带版本号一般也行，但 `lake` 太老会报错。
- `lake exe cache get` **只对以 mathlib4 为依赖的项目有效**；报 `curl: (35) schannel ...` 是 Windows 杀软拦截，官方建议临时关杀软后跑 `lake exe cache get!`（感叹号强制重下）。清理位置：工具链 `~/.elan/toolchains`、缓存包 `~/.cache/mathlib`、项目依赖 `.lake/`。
- **体积与耗时（经验量级，版本间可差 2 倍）**：工具链 1–2 GB；Mathlib 源码+依赖 3–6 GB；预编译缓存下载 2–4 GB、解压后再占 2–3 GB；首次 `import Mathlib` 有缓存 5–30 s、**无缓存 30 分钟到数小时**；**磁盘预留 10 GB 以上**。

**「需要用户同意」硬规则**：① 未安装时**不得擅自下载**，先说明下载什么、多大、多久、能否删除；② 用户拒绝或未回应 → 状态直接 `NOT_ATTEMPTED`，按 §9 降级，**不许**用"我推理了一遍等价于验证"糊过去；③ 只想试语法可提示官方在线编辑器 <https://live.lean-lang.org/>，但其**是否预载 Mathlib 未核**（§10-B），只能确认语法形态，不算 Mathlib 验证结果。

---
## §3 状态枚举（只用这四个词，没有第五个）

| 状态 | 判定条件（全部满足才可写） |
|---|---|
| `VERIFIED` | ① 编译退出码 0；② `sorry`/`admit` 计数为 0；③ `#print axioms <定理名>` 输出 ⊆ `[propext, Classical.choice, Quot.sound]`；④ §4-6 对账表通过 |
| `UNVERIFIED-SORRY` | 能编译（可能退出码 0）但存在 `sorry`/`admit`，或 `#print axioms` 出现 `sorryAx`；必须点名卡在哪一步、缺什么引理 |
| `FAILED` | 编译非 0 退出；必须贴**第一条**报错原文 + 行号 + 判断（类型错 / tactic 不适配 / 陈述写错） |
| `NOT_ATTEMPTED` | 无环境、题不适合（§1 右表）、用户拒绝安装、或超预算；必须写清属于哪一种 |

**每条记录必附五字段**（缺一项算没做）：文件路径 / 命令（如 `lake env lean Problem.lean`）/ Lean 版本（`lean --version` 首行原文）/ 输出摘要（≤3 行，成功写 `exit 0, no output`）/ sorry 计数。

- 计数命令（只抓字面，**不足以证明无 sorry**）：`(Select-String -Path Problem.lean -Pattern '\b(sorry|admit)\b' -AllMatches).Count`
- **真正的检查是 `#print axioms`**：`sorry` 只是 warning，退出码照样 0，但声明会依赖 `sorryAx`——这就是"编译通过 ≠ 证完了"。若用了 `native_decide`，还会多出 `Lean.ofReduceBool`（信任扩展公理，不属标准三公理），报告里**必须披露**。

---
## §4 标准流程（七步，不许跳）

1. **自然语言严谨证明**：纸上写全（取等条件、定义域、分类是否穷尽）。这是 ① 级，**不能用 Lean 代替思考**。
2. **抽取定理陈述**：变量与类型（`x y : ℝ` / `n : ℕ`）；假设表（每条对应原题哪句话）；结论（与原题所求等价吗）。
3. **写 `Problem.lean`**：单文件，顶部 `import`；每个结论一个**具名** `theorem`（便于 `#print axioms`），最终交付不用匿名 `example`。
4. **编译**：`lake env lean Problem.lean`，确认 `$LASTEXITCODE` 为 0。
5. **查 sorry**：字面 grep + `#print axioms` 双查；宁可多写几行把 sorry 显式暴露，也不要把 `sorry` 藏进辅助引理。
6. **与原题逐条对账**：

    | 对账项 | 原题 | Lean 定理 | 判定 |
    |---|---|---|---|
    | 变量域 | $x\in\mathbb{R}$ | `x : ℝ` | ✅ / ⚠ / ❌ |
    | 假设 1..k | 抄题面原文 | 每条 `h…` | 漏 / 多 / 等价 |
    | 结论 | 题面所求 | 结论式 | 等价 / 更强 / 更弱 |
    | 退化情形 | 端点、分母、n=0 | 是否被假设排除 | 已覆盖 / 缺失 |

   出现 ❌（更弱 / 漏假设 / 加假设）→ **不许**报 `VERIFIED`，先修陈述。
7. **报告**：按 §8 模板，附五字段 + 对账表摘要。

---
## §5 Lean 4 + Mathlib 模板（未编译骨架，可直接改）

> 风险等级：**低**＝语法与 tactic 稳定；**中**＝API 名可能随版本微调；**高**＝很可能要按本地 Mathlib 现场调。改前先 `#check` / `exact?` / Loogle (<https://loogle.lean-lang.org/>) 确认符号存在。

**5.1 恒等式 / 代数（风险：低）**

```lean
import Mathlib

theorem expand_sq (x y : ℝ) : (x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2 := by
  ring   -- 完全平方一步闭环；纯数值恒等式（如 (3:ℚ)/4 + 1/4 = 1）改用 norm_num
-- ring 只认交换半环等式；√ / log / sin / abs 会被当原子，直接放弃
```
**5.2 不等式（风险：低-中）**

```lean
import Mathlib

-- 给 nlinarith 一个"平方非负"提示即可闭环
theorem sq_add_one_ge (x : ℝ) : x ^ 2 + 1 ≥ 2 * x := by
  nlinarith [sq_nonneg (x - 1)]

-- 均值不等式：假设必须写全，否则命题为假；名字别用 amgm（Mathlib 已有，会撞名报错）
theorem sq_add_sq_ge_two_mul (a b : ℝ) (ha : 0 < a) (hb : 0 < b) : a ^ 2 + b ^ 2 ≥ 2 * a * b := by
  nlinarith [sq_nonneg (a - b)]
-- nlinarith 不会自己想到 (x-1)^2 ≥ 0，必须喂提示；喂错会直接失败，不会"蒙对"
-- 取等条件是证明副产物，别塞进定理——要写就另立 ∃ x, … 命题
```
**5.3 数论 / 整除（风险：高，务必现场调）**

```lean
import Mathlib

-- 最稳的最小骨架：直接给见证，ring 收尾
theorem dvd_sq_self (n : ℕ) : n ∣ n ^ 2 := ⟨n, by ring⟩

-- 高频结论 3 ∣ n³ − n：先记住 n³ − n = (n−1)·n·(n+1)，三个连续整数必有一个被 3 整除
theorem three_dvd_cube_sub (n : ℕ) : 3 ∣ n ^ 3 - n := by
  omega   -- ⚠ 常见教程写法。omega 只做线性算术，n^3 是非线性项，此写法很可能不通过。
          -- 走通路线：① 分情形 n % 3 ∈ {0,1,2}（Nat.dvd_of_mod_eq_zero / Nat.dvd_sub）；
          -- ② 先 push_cast 到 ℤ，在 ℤ 上用 ring 把差写成乘积。两条路都需现场核对 API。
-- ℕ 减法截断：n - 1 在 n=0 时变 0；通用题优先在 ℤ/ℚ 上陈述，或加 (hn : 0 < n)
-- 有限验证 ≠ 全称证明(P2)：example (n : Fin 1000) : 3 ∣ (n:ℕ)^3 - (n:ℕ) := by decide
--   只说明前 1000 个成立，报告须标"有限范围机验"，不得计入 §8.0 的 P2 通过
```
**5.4 函数单调 / 导数（风险：中—高，Mathlib 变动最剧烈）**

```lean
import Mathlib

-- 单调性优先 MonotoneOn + 区间，避免"全局单调"这类假命题
theorem sq_mono_on_nonneg : MonotoneOn (fun x : ℝ => x ^ 2) (Set.Ici 0) := by
  intro x hx y hy hxy
  nlinarith [hx, hy, hxy]

-- 导数：接口名随版本变动最大，先 #check 再写；以下仅形态示意，未核
-- theorem d_sq (x : ℝ) : HasDerivAt (fun y : ℝ => y ^ 2) (2 * x) x := by
--   simpa using hasDerivAt_pow 2 x
-- 中学"求导判单调"在 Lean 里非必须：能直接作差证不等式就别求导（nlinarith 比 deriv 稳）
```
**5.5 组合恒等式 / 求和（风险：中）**：用 `induction` + `ring`，优先在 `ℚ` 上陈述以绕开 ℕ 除法（`2·∑_{k<n} k = n(n−1)`）。归纳一跑，$n$ 的任意性就是真任意，正好克制 P2（"只验证前几项"）。

**5.6 物理建模示例：只验证代数，不验证物理语义（风险：低）**

```lean
import Mathlib

-- 情境：光滑竖直圆轨道，物块从最低点以 v0 出发。
-- 物理语义（"机械能守恒""恰好不脱离"）不在 Lean 范围内，只能写成假设！
theorem loop_v0 (v0 vtop g R : ℝ) (hg : 0 < g) (hR : 0 < R)
    (hE : v0 ^ 2 = vtop ^ 2 + 4 * g * R)   -- 假设 1：能量守恒（物理判断，未形式化）
    (hN : vtop ^ 2 = g * R) :              -- 假设 2：最高点支持力恰为 0（物理判断，未形式化）
    v0 ^ 2 = 5 * g * R := by linarith

-- 非空性检查：确认两条假设不互相矛盾，否则定理空真、零信息量
theorem loop_v0_nonvacuous :
    ∃ v0 vtop g R : ℝ, 0 < g ∧ 0 < R ∧ v0 ^ 2 = vtop ^ 2 + 4 * g * R ∧ vtop ^ 2 = g * R := by
  refine ⟨3, 2, 1, 4, by norm_num, by norm_num, by norm_num, by norm_num⟩
```
**随代码必写三句**：① Lean 证的是"由能量守恒与临界条件可推出 $v_0^2=5gR$"这个**代数推论**；② 它**不验证**"恰好不脱离 ⇔ N=0"这个物理翻译；③ 量纲、极限（$R\to0$）仍按 SKILL.md §8 物理清单人工做。缺这三句＝把 §1 的鸿沟藏起来。

---
## §6 tactic 速查（一句话：什么时候用 + 前提/坑）

| tactic | 什么时候用 | 前提 / 坑 |
|---|---|---|
| `ring` | 交换半环里的**等式**（展开、配方、因式分解核对） | 只认等式；`√`/`log`/`abs` 是原子，证不了 |
| `ring_nf` | 把式子化成**规范形**（不闭环，可作中间步），或"环推理藏在子项里"导致 `ring` 失败 | 不保证闭环；`P (x+x+x)` → `P (x*3)` 这类改写最顺手 |
| `linarith` | **线性**不等式与等式 | 只看线性组合；非线性项被当原子，报 `failed` |
| `nlinarith` | 多项式不等式（含 `^2`、`^3`） | **必须喂提示** `[sq_nonneg (x-1)]`；项多时慢，注意心跳超时 |
| `field_simp` | 含分式，先"去分母" | **需要分母非零**；Lean 除法全函数（`a/0=0`），中学的"无意义"不报错，只会让你证出**错的命题** |
| `norm_num` | 具体数字的算式、数值等式/不等式 | 只管可判定数值；别拿它证含变量的命题 |
| `omega` | `ℕ`/`ℤ` 上的**线性**算术、取模、整除的线性部分 | **线性**！`n^3` 必失败；ℕ 减法截断它自己会处理 |
| `positivity` | 证 `0 < …` / `0 ≤ …`（平方、绝对值、指数） | 只做结构递归；自定义函数需先展开 |
| `simp` | 通用化简、代入引理 | 可能循环或化简过头，用 `simp only [...]` 收窄；失败 ≠ 命题假 |
| `gcongr` | 不等式链里"逐项比较"（两边同乘正数、同加同减） | 非负条件要自动或附注补齐 |
| `induction` / `rcases` | 归纳、分情形（`n % 3` 三分类） | 归纳写 `with \| zero => … \| succ k ih => …`；`rcases` 拆 `∨`/`∃` |
| `have` / `calc` | 拆中间结论 / 写可读的等号不等式链 | `have h : … := by …` 是可读性关键，别把一切塞给一个 tactic |
| `norm_cast` / `push_cast` | `ℕ`/`ℤ`/`ℚ`/`ℝ` 间转换 | 类型不匹配的头号解药；配合 `ring`/`omega` 收尾 |
| `decide` / `native_decide` | 有限范围可判定命题 | **只证有限个**（P2 风险）；`native_decide` 引入 `Lean.ofReduceBool`，须披露 |

---
## §7 常见坑（按踩到频率排）

1. **类型不匹配**：`(2:ℕ)/4 = 0` 而 `(2:ℚ)/4 = 1/2`；`n - 1` 在 ℕ 上到 0 就停。**规矩**：恒等式/不等式默认在 `ℝ`/`ℚ` 陈述，确需整除/同余才用 `ℕ`，报告写明类型选择理由。
2. **分母为 0 与全函数除法**：Lean 里 `1/0 = 0`，"$\frac{1}{x-1}$ 的定义域"**不在陈述里**——必须自己加 `(hx : x ≠ 1)`，否则证的是另一道题。
3. **`nlinarith` 缺提示**：报 `nlinarith failed to find a contradiction`，九成是没喂 `sq_nonneg` / `mul_self_nonneg` / `h : 0 ≤ x`。
4. **ℕ 上 `ring` 遇减法**：截断减法不是环运算；先 `push_cast` 到 ℤ/ℚ，或加 `0 < n`。
5. **Mathlib 版本 API 变动**：`deriv`、`HasDerivAt`、部分 `Nat.dvd_*` 改过名；`deprecated` 只是警告，被删的名字直接编译失败。**写代码前先 `#check`，不要凭记忆写 API。**
6. **`import Mathlib` 编译慢**：没跑 `lake exe cache get` 时首次几十分钟起；省时间就窄导入（`import Mathlib.Tactic` + `import Mathlib.Data.Real.Basic`）。
7. **sorry 藏在引理里**：主 `theorem` 干净、辅助 `lemma` 藏 `sorry` 也能"编译通过"。**只能靠 `#print axioms <主语名>` 兜底**（显示 `sorryAx`），grep 抓不到跨文件引用。
8. **空真 / 矛盾假设**：假设互相矛盾时定理平凡成立，交付前必须补 §5.6 那样的非空性检查。

---
## §8 报告模板（Agent 直接套）

**A. 没上 Lean（最常见）**

```
形式化验证｜状态：NOT_ATTEMPTED（本机无 Lean）
原因：本机无 Lean 4 工具链（where.exe lean / lake / elan 均无输出），且未获用户安装授权。
      （若因题目不适合，改写为：结论含几何作图/物理语义判断，不满足 §1 判据。）
已做替代验证：① 自然语言严谨证明 + 独立第二解法（见教师版 §…）；② Python/SymPy 符号核对（见 §…）
可编译骨架：<路径>/Problem.lean（未经验证，风险等级：中）
已核边界：Lean 证的是我写的定理，未核其忠实于原题（无对账表）
下一步：用户同意安装 Lean（约 10 GB 磁盘 / 20–60 分钟）后可升级为 VERIFIED
```
**B. 成功**
```
形式化验证｜状态：VERIFIED
文件路径：题目工坊/<题简称>/lean/Problem.lean    命令：lake env lean Problem.lean
Lean 版本：<lean --version 首行原文>    输出摘要：exit 0，无 error；#print axioms ⊆ [propext, Classical.choice, Quot.sound]
sorry 计数：0（字面 grep 0；#print axioms 无 sorryAx）
陈述对账：变量域 ✅ / 假设 3 条全部来自题面 ✅ / 结论等价 ✅ / 退化情形（n=0）已由 hn 排除 ✅
已知边界：Lean 只验证了代数推论，未验证"物理情境 → 方程"的翻译语义。
```
**C. 有 sorry 或报错**

```
形式化验证｜状态：UNVERIFIED-SORRY（或 FAILED）
文件路径：…    命令：…    Lean 版本：…
输出摘要：第 12 行 error: application type mismatch …（或 sorry 位于第 18 行分情形）
sorry 计数：1（在 lemma aux_mod 内；原因：n % 3 = 2 分支未找到合适的 Nat.dvd 引理）
处置：已按 §9 用 SymPy 数值核对 + 第二解法兜底；不声称该结论已形式化验证。
```
**禁语**：状态行不许出现"基本验证通过""逻辑上已证""编译器应该能过"。要么有退出码，要么写没做。

---
## §9 降级策略（没有 Lean 时怎么诚实交付）

1. **顺序不可逆**：① → ② → ③。**① 永远要做**，Lean 不是免做 ① 的借口。
2. **必须显式写"未形式化验证"**：在交付物"学科校验"一节加一行——`形式化验证：NOT_ATTEMPTED（原因：…），已用 SymPy 符号展开 + 第二解法替代核对`。
3. **替代手段强度排序**（用来解释"这条答案到底多可信"）：SymPy 符号恒等（强）> 高精度数值抽样（强但非证明）> 特殊值/端点代入（弱）> 直觉与"看得出"（**不算验证**）。
4. **绝对不能做三件事**：把"我推理了一遍没发现问题"写成"已验证"；用有限取值核对冒充全称证明（P2）；把 §5 的未编译骨架当成"已经跑过"贴进报告。
5. 拒绝安装时的收尾话术：`该结论已用自然语言证明 + SymPy 符号核对；如需机器级零假设验证，可在具备 Lean 4 + Mathlib 的环境下用 §5 骨架升级为 VERIFIED。`

---
## §10 来源与核对状态

**A 级（本次真实抓取成功，可引用）**

- 《Lean projects》：`lake new … math` / `lake update` / `lake exe cache get[!]` / Windows 杀软与工具链损坏排错 — <https://leanprover-community.github.io/install/project.html>
- 《Did you prove it?》：`#print axioms` 白名单 `[propext, Classical.choice, Quot.sound]`、`sorryAx` 判定、"独立 .lean 文件不算验证" — <https://leanprover-community.github.io/did_you_prove_it.html>
- Mathlib tactics 总表（tactic 名与存在性核对，并确认 `Mathlib.Tactic` 窄导入口存在）— <https://leanprover-community.github.io/mathlib4_docs/tactics.html>、<https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic.html>
- `ring` / `ring_nf` 模块页（`ring` 在 ℕ 上的示例、`ring_nf` 的"非终结化简"语义）— <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/Ring/RingNF.html>

**B 级（未核实，用时标注不确定性，不要当权威引用）**

- `elan-init.ps1` 的 `-y` 参数：URL 已确认可达（HEAD 返回 200），脚本体因内容类型限制未抓取；首次安装以脚本自报 usage 为准。
- 所有 Lean 代码的**可编译性**：全部未编译。`sq_nonneg`、`Nat.dvd_of_mod_eq_zero`、`Nat.dvd_sub`、`hasDerivAt_pow` 等名字按常见用法写出，`import Mathlib` 下大概率存在但**未逐一 `#check`**。
- 体积/耗时：经验量级，不同 Mathlib 版本可差 2 倍；`live.lean-lang.org` 是否预载 Mathlib 未核；`native_decide` 引入 `Lean.ofReduceBool` 按社区通行说法记录，未在本机复核。

**30 秒速查**：`where.exe` 三连查环境 → 没装先问用户 → 写定理前列「变量/假设/结论」→ 跑完看「退出码 + sorry 计数 + `#print axioms`」→ 证完交对账表 → 必写一句「Lean 证的是我写的定理，不证它忠实于原题」。
