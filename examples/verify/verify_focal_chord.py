# -*- coding: utf-8 -*-
"""抛物线焦点弦 1/|AF|+1/|BF|=1 全量验算（数值 + 符号多项式恒等式）"""
from fractions import Fraction as Fr
import math

out = []
def say(s):
    out.append(s)

# ---------- 符号多项式工具（系数为 Fraction，升幂） ----------
def padd(a, b):
    n = max(len(a), len(b)); r = [Fr(0)] * n
    for i, c in enumerate(a): r[i] += c
    for i, c in enumerate(b): r[i] += c
    return r
def psub(a, b):
    return padd(a, [-c for c in b])
def pmul(a, b):
    r = [Fr(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r
def pscale(a, k):
    return [c * k for c in a]
def ptrim(a):
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a
def pstr(a):
    a = ptrim(list(a))
    return " + ".join(f"({c})k^{i}" if i else f"({c})" for i, c in enumerate(a) if c != 0) or "0"

def pdivmod(a, b):
    a = ptrim(list(a)); b = ptrim(list(b))
    q = [Fr(0)] * max(1, len(a) - len(b) + 1); r = list(a)
    while len(r) >= len(b) and any(r):
        d = len(r) - len(b); c = r[-1] / b[-1]
        q[d] += c
        for i, bc in enumerate(b): r[i + d] -= c * bc
        ptrim(r)
        if len(r) >= len(b) and r[-1] == 0: r.pop()
        if len(r) < len(b): break
        if all(x == 0 for x in r): break
    return q, ptrim(r)

say("=== A. 抛物线 y^2=4x：数值核验 1/|AF|+1/|BF| = 1 ===")
for k in [Fr(1), Fr(2), Fr(-3), Fr(1, 2), Fr(10), Fr(-1, 4)]:
    # 联立 y=k(x-1): k^2(x-1)^2 = 4x  =>  k^2 x^2 - (2k^2+4)x + k^2 = 0
    A = k * k; B = -(2 * k * k + 4); C = k * k
    disc = B * B - 4 * A * C
    assert disc > 0, "判别式必须为正（保证两个不同交点）"
    s = -B / A           # x1+x2
    p = C / A            # x1*x2
    x1 = (-B + Fr(math.isqrt(disc.numerator)) / math.isqrt(disc.denominator)) / (2 * A) if False else None
    # 用精确根：x = (2k^2+4 +- sqrt(disc)) / (2k^2)
    sq = Fr(math.sqrt(float(disc)))  # 仅用于展示
    # 焦半径 |AF| = x1 + 1 （定义：到准线 x=-1 的距离）
    val = Fr(1, 1) / (s / 2 + 1 - (Fr(0)))  # placeholder
    # 直接对两根分别算，避免近似：用 s,p 的对称式 1/(x1+1)+1/(x2+1)=(s+2)/(p+s+1)
    lhs = (s + 2) / (p + s + 1)
    say(f"  k={k}: 判别式={disc} (正), x1+x2={s}, x1*x2={p}, "
        f"(s+2)/(p+s+1)={lhs}, s==2+4/k^2? {s == 2 + 4 / (k * k)}")

say("")
say("=== A2. 焦半径 |AP|=x+1 与两点距离互验（数值）===")
for k in [Fr(1), Fr(2), Fr(-3)]:
    A = k * k; B = -(2 * k * k + 4); C = k * k
    disc = B * B - 4 * A * C
    sq = math.sqrt(float(disc))
    for sign in (1, -1):
        x = (float(-B) + sign * sq) / (2 * float(A))
        y = float(k) * (x - 1)
        on_curve = abs(y * y - 4 * x) < 1e-9
        d_two_point = math.hypot(x - 1, y)
        say(f"  k={k} 取 {sign:+d} 根: x={x:.6f}, y={y:.6f}, 在抛物线上={on_curve}, "
            f"两点距离={d_two_point:.6f}, x+1={x+1:.6f}, 差={abs(d_two_point-(x+1)):.2e}")

say("")
say("=== B. 垂直情形（斜率不存在）l: x=1 ===")
pts = [(1, 2), (1, -2)]
for (x, y) in pts:
    say(f"  A/B=({x},{y}) 在 y^2=4x 上: {y*y==4*x}, |PF|=两点距离={math.hypot(x-1,y):.6f}, x+1={x+1}")
say(f"  1/|AF|+1/|BF| = 1/2+1/2 = {Fr(1,2)+Fr(1,2)}")

say("")
say("=== C. k=0 退化检查（y=0 与 y^2=4x 的交点个数）===")
sols = [x for x in range(-5, 20) if 0 == 4 * x]
say(f"  y=0 代入得 0=4x => x=0，仅一个交点 (0,0)；F=(1,0) 不在抛物线上 => 不构成弦。交点数=1")

say("")
say("=== D. 台阶 1/2 的具体数值（worked example：k=1 与 P(4,4)）===")
say(f"  P(4,4): y^2=16=4*4 在抛物线上; |PF|=sqrt((4-1)^2+4^2)={math.hypot(3,4):.1f}; x+1={4+1}")
x1 = 3 + 2 * math.sqrt(2); x2 = 3 - 2 * math.sqrt(2)
y1 = x1 - 1; y2 = x2 - 1
say(f"  k=1: x1=3+2sqrt2={x1:.6f}, x2=3-2sqrt2={x2:.6f}, y1={y1:.6f}, y2={y2:.6f}")
say(f"    验 y1^2==4x1: {abs(y1*y1-4*x1):.2e}; y2^2==4x2: {abs(y2*y2-4*x2):.2e}")
say(f"    x1+x2={x1+x2:.6f} (=2+4/1=6? {abs(x1+x2-6):.2e}), x1*x2={x1*x2:.6f}")
d1 = math.hypot(x1 - 1, y1); d2 = math.hypot(x2 - 1, y2)
say(f"    |AF|={d1:.6f} (=4+2sqrt2 {4+2*math.sqrt(2):.6f}), |BF|={d2:.6f} (=4-2sqrt2 {4-2*math.sqrt(2):.6f})")
say(f"    1/|AF|+1/|BF|={1/d1+1/d2:.10f}")
say(f"  k=2: x^2-3x+1=0, 根=(3±sqrt5)/2={ (3+math.sqrt(5))/2:.6f},{(3-math.sqrt(5))/2:.6f}, 和={(3+math.sqrt(5))/2+(3-math.sqrt(5))/2}, 积={((3+math.sqrt(5))/2)*((3-math.sqrt(5))/2):.6f}")

say("")
say("=== E. 符号恒等式：(s+2) - (p+s+1) 在 s=2+4/k^2, p=1 下 ===")
k = [Fr(0), Fr(1)]
# s = (2k^2+4)/k^2 ; p = 1 = k^2/k^2 ; 通分后比较分子
two = [Fr(2)]; four = [Fr(4)]
num_s = padd(pscale(pmul(k, k), 2), four)          # 2k^2+4
den = pmul(k, k)                                    # k^2
num_p = list(den)                                   # k^2
lhs_num = padd(num_s, pscale(den, 2))               # s+2  的分子
rhs_num = padd(padd(num_p, num_s), den)             # p+s+1 的分子
diff = psub(lhs_num, rhs_num)
say(f"  s+2  分子 = {pstr(lhs_num)}；p+s+1 分子 = {pstr(rhs_num)}；差 = {pstr(diff)}")
say(f"  差为零多项式? {ptrim(diff)==[Fr(0)]}  => 分子恒等 => (s+2)/(p+s+1) = 1 对一切 k≠0")

say("")
say("=== F. 极坐标表征：rho = 2/(1-cos t) ===")
for t_deg in [30, 60, 90, 120, 225, 300]:
    t = math.radians(t_deg)
    r1 = 2 / (1 - math.cos(t))
    r2 = 2 / (1 - math.cos(t + math.pi))
    xs = [1 + r1 * math.cos(t), 1 + r2 * math.cos(t + math.pi)]
    ys = [r1 * math.sin(t), r2 * math.sin(t + math.pi)]
    on = all(abs(y * y - 4 * x) < 1e-9 for x, y in zip(xs, ys))
    say(f"  t={t_deg}°: rho={r1:.6f}, rho(t+pi)={r2:.6f}, 1/rho+1/rho'={1/r1+1/r2:.10f}, 两点在曲线上={on}")

say("")
say("=== G. 椭圆 x^2/4+y^2/3=1 的类比（变式 v1）===")
say("  方程 (3+4k^2)x^2 - 8k^2 x + (4k^2-12) = 0；s=8k^2/(3+4k^2), p=(4k^2-12)/(3+4k^2)")
ks = [Fr(1), Fr(2), Fr(-1, 2), Fr(5)]
for kkv in ks:
    k2 = kkv * kkv
    s = 8 * k2 / (3 + 4 * k2)
    p = (4 * k2 - 12) / (3 + 4 * k2)
    # |PF| = a - e*x = 2 - x/2 ; 1/|AF|+1/|BF| = 2/(4-x1)+2/(4-x2) = 2(8-s)/(16-4s+p)
    val = 2 * (8 - s) / (16 - 4 * s + p)
    say(f"  k={kkv}: s={s}, p={p}, 倒数和={val}, == 4/3? {val == Fr(4,3)}")
# 垂直：x=1
yd = math.sqrt(3 * (1 - 1 / 4))
say(f"  垂直 x=1: y=±{yd:.6f}, |AF|=|BF|={yd:.6f}, 倒数和={2/yd:.10f}, 4/3={4/3:.10f}")
# 符号核对：2(8-s) / (16-4s+p)，通分后应 = 4/3
k = [Fr(0), Fr(1)]
k2 = pmul(k, k)
three = [Fr(3)]
num_s = pscale(k2, 8)                       # 8k^2
den = padd(three, pscale(k2, 4))            # 3+4k^2
num_p = padd(pscale(k2, 4), [Fr(-12)])      # 4k^2-12
N1 = pscale(psub(pscale(den, 8), num_s), 2)                              # 比值分子：2(8-s) 通分后
D1 = psub(padd(pscale(den, 16), num_p), pscale(num_s, 4))                # 比值分母：16-4s+p 通分后
# 验 2(8-s)/(16-4s+p) = 4/3  <=>  3*N1 = 4*D1
diff = psub(pscale(N1, 3), pscale(D1, 4))
say(f"  3*N1 - 4*D1 = {pstr(diff)} => 恒等? {ptrim(diff)==[Fr(0)]}")
say("  => 椭圆情形倒数和恒为 4/3 = 2a/b^2（a=2,b=sqrt3）")

say("")
say("=== H. 变式 v4：弦长最值与存在性 ===")
for kkv in [Fr(1), Fr(2), Fr(1, 2), Fr(10)]:
    say(f"  k={kkv}: |AB|=x1+x2+2=4+4/k^2={4 + 4 / (kkv * kkv)}")
say(f"  垂直: |AB|=|AF|+|BF|=4；k→±∞ 时 4+4/k^2→4 => 最小值 4（通径）")
say(f"  |AB|=8 时 4+4/k^2=8 => k^2=1 => k=±1，存在")
say("")
say("=== I. 丙同学错解（分母漏 x1+x2）会产生什么 ===")
for kkv in [Fr(1), Fr(2)]:
    k2 = kkv * kkv
    s = 2 + 4 / k2
    wrong = (s + 2) / (1 + 1)      # 分母错写成 x1x2+1 = 2
    say(f"  k={kkv}: 正确值=1；错解值=(s+2)/(x1x2+1)={wrong} ≠ 1 => 会误判'题目条件不足'")
say("")
say("=== J. 台阶 6 结论：l 与抛物线有两个交点的条件 ===")
say("  k≠0 时 k^2x^2-(2k^2+4)x+k^2=0 判别式 = (2k^2+4)^2-4k^4 = 16k^2+16 > 0 恒成立")
for kkv in [Fr(1), Fr(3), Fr(-7, 2)]:
    k2 = kkv * kkv
    say(f"  k={kkv}: disc={16*k2+16} > 0")
print("\n".join(out))