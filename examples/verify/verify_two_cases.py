# -*- coding: utf-8 -*-
"""独立验算：案例A(抛物线焦弦) + 案例B(竖直圆轨道临界)。
无 sympy，用 Fraction 精确算术 + 高精度浮点。只打印结论行。"""
from fractions import Fraction as F
import math

print("=== 案例A ===")

def roots_from_k(k):
    # y=k(x-1), y^2=4x -> k^2 x^2 -(2k^2+4)x + k^2 = 0
    a, b, c = k*k, -(2*k*k+4), k*k
    d = b*b - 4*a*c
    if d < 0: return None
    r = math.sqrt(d)
    return ((-b-r)/(2*a), (-b+r)/(2*a))

# A1 斜率 k=3/4：判别式 16(k^2+1)=25 为完全平方 -> 有理根，可精确验算
k = F(3,4)
a, b, c = k*k, -(2*k*k+4), k*k
d = b*b-4*a*c
s = F(math.isqrt(d.numerator), 1) if d.numerator == math.isqrt(d.numerator)**2 and d.denominator==1 else None
sq = math.isqrt(d.numerator)
assert sq*sq == d.numerator and d.denominator == 1, d
x1 = (-b-sq)/(2*a); x2 = (-b+sq)/(2*a)
S = 1/(x1+1) + 1/(x2+1)
print("A1 k=3/4 精确: x1*x2=%s, x1+x2=%s, 1/(x1+1)+1/(x2+1)=%s" % (x1*x2, x1+x2, S))

# A2 数值扫描（含负斜率）
mx = 0.0
for kk in [-5,-3,-1.7,-0.5,0.3,0.9,1,2,4,10]:
    r = roots_from_k(kk); x1,x2 = r
    v = 1/(x1+1)+1/(x2+1)
    mx = max(mx, abs(v-1))
print("A2 斜率扫描 max|sum-1| = %.3e (k != 0)" % mx)

# A3 垂直弦 x=1: A(1,2),B(1,-2)
print("A3 垂直弦: |AF|=|BF|=2, sum=%.12f" % (1/2+1/2))

# A4 设 x=my+1: y^2-4my-4=0, y1y2=-4, sum=1
err = 0.0
for m in [-3,-1,0,0.5,2,6]:
    y1 = 2*m - math.sqrt(4*m*m+4); y2 = 2*m + math.sqrt(4*m*m+4)
    r1 = abs(y1)*math.sqrt(1+m*m); r2 = abs(y2)*math.sqrt(1+m*m)
    err = max(err, abs(1/r1+1/r2-1))
    assert abs(y1*y2+4) < 1e-12
print("A4 x=my+1 扫描 max|sum-1| = %.3e, y1*y2 = -4 恒成立" % err)

# A5 k=0 退化：y=0 代入 y^2=4x 只有 x=0 单点（切线，不是弦）
print("A5 k=0: y=0 与 y^2=4x 交点个数=1 -> 不构成弦，用户未排除")

# A6 反向对照：非焦弦不成立（说明恒等式由“过焦点”设计出来）
bad = 0
for m in [0, 1, 2]:
    # 过 (2,0) 的弦 x=my+2
    y1 = 2*m - math.sqrt(4*m*m+8); y2 = 2*m + math.sqrt(4*m*m+8)
    r1 = math.sqrt((m*y1+1)**2+y1*y1); r2 = math.sqrt((m*y2+1)**2+y2*y2)
    v = 1/r1+1/r2; bad += 1 if abs(v-1) > 1e-6 else 0
print("A6 非焦弦(x=my+2) 3 例全部 sum!=1: %s" % (bad == 3))

# A7 极坐标 r=2/(1-cosθ)：反向与正向两条射线倒数之和=1
e = 0.0
for deg in [10,45,80,120,160,200,300]:
    t = math.radians(deg)
    r1 = 2/(1-math.cos(t)); r2 = 2/(1+math.cos(t))
    e = max(e, abs(1/r1+1/r2-1))
print("A7 极坐标 r=2/(1-cosθ) max|sum-1| = %.3e" % e)

print()
print("=== 案例B ===")
g, R = 9.8, 1.0
v_top_c = math.sqrt(g*R)
v0_c = math.sqrt(5*g*R)
v0_wrong = 2*math.sqrt(g*R)
print("B1 临界 v_top=sqrt(gR)=%.6f m/s, v0=sqrt(5gR)=%.6f m/s" % (v_top_c, v0_c))
print("B2 错解 2sqrt(gR)=%.6f, 相对正解偏差=%.3f%% ; 平方比 4/5=%.3f" % (v0_wrong, abs(v0_wrong-v0_c)/v0_c*100, 4/5))

# B3 错解代入后的脱离角：N(φ)=m(v0^2/R-2g+3g cosφ), N=0
cosdet = (2*g - v0_wrong**2/R)/(3*g)
phi = math.degrees(math.acos(cosdet))
h = R*(1-cosdet); v2 = v0_wrong**2 - 2*g*R*(1-cosdet)
print("B3 v0=2sqrt(gR): 脱离于 cosφ=%.6f, φ=%.2f° (<180°, 未到顶), 高度=%.3fR, 该点 v=%.4f" % (cosdet, phi, h, math.sqrt(v2)))

# B4 正解 v0=sqrt(5gR): N(φ)/m = 3g(1+cosφ) >= 0, 仅顶为0
vals = [3*g*(1+math.cos(math.radians(d))) for d in range(0,181,5)]
print("B4 v0=sqrt(5gR): min_φ N/m=%.3e (φ=180°), 其余>0: %s" % (min(vals), all(v > -1e-12 for v in vals)))

# B5 反例：v_top^2=0.9gR -> 提前脱离，位置在顶前
for rt in [0.99, 0.9, 0.5]:
    v0sq = rt*g*R + 4*g*R
    cd = (2*g - v0sq/R)/(3*g)
    print("B5 v_top^2=%.2fgR -> 脱离 cosφ=%.4f, φ=%.2f°" % (rt, cd, math.degrees(math.acos(cd))))

# B6 能量闭环：v_top^2=gR -> v0^2=5gR；杆模型 v_top=0 -> v0^2=4gR
print("B6 能量: v0^2=v_top^2+4gR; 内轨临界 %s; 杆模型 %s" % (g*R+4*g*R, 0+4*g*R))