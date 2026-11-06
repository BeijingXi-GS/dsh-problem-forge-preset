# -*- coding: utf-8 -*-
"""竖直圆轨道临界问题：数值核对脚本（单位质量量纲，N/m 单位 m/s^2）"""
import math

print("=== 1. 原题：v_top=sqrt(gR), v0=sqrt(5gR) ===")
for R, g in [(1.0, 9.8), (0.5, 10.0), (2.0, 9.8), (1.0, 1.6)]:
    vtop = math.sqrt(g * R)
    v0 = math.sqrt(5 * g * R)
    e_lhs = 0.5 * v0 ** 2
    e_rhs = 0.5 * vtop ** 2 + g * 2 * R
    Nbot = v0 ** 2 / R + g
    Ntop = vtop ** 2 / R - g
    print("R=%.2f g=%.2f | v_top=%.6f v0=%.6f | 能量差=%.2e | N_b/m=%.6f (6g=%.4f) | N_t/m=%.2e | v0/v_top=%.6f"
          % (R, g, vtop, v0, e_lhs - e_rhs, Nbot, 6 * g, Ntop, v0 / vtop))

print("\n=== 2. 杆模型误读（v_top=0）对照 ===")
for R, g in [(1.0, 9.8)]:
    print("rod: v0=2*sqrt(gR)=%.6f；rope: %.6f；相对偏差=%.2f%%"
          % (2 * math.sqrt(g * R), math.sqrt(5 * g * R),
             100 * (math.sqrt(5) - 2) / math.sqrt(5)))

print("\n=== 3. 极限与缩放 ===")
print("R->0 : v0(R=1e-6,g=9.8)=%.3e" % math.sqrt(5 * 9.8 * 1e-6))
print("g->0 : v0(R=1,g=1e-6)=%.3e" % math.sqrt(5 * 1e-6 * 1))
print("v0/sqrt(gR) 恒为 sqrt5=%.10f（R、g 无关）" % math.sqrt(5))
print("R 加倍: v0 变大 sqrt2 倍 -> %.6f" % (math.sqrt(5 * 9.8 * 2) / math.sqrt(5 * 9.8 * 1)))

print("\n=== 4. v_top<sqrt(gR) 时提前脱离：脱离角与脱离后弹道最高点 ===")
def apex_above_bottom(k, g=9.8, R=1.0):
    # vtop^2 = k*g*R, 0<=k<1
    vtop2 = k * g * R
    c = (vtop2 + 2 * g * R) / (3 * g * R)      # cos(phi), phi 从最高点量
    if c >= 1:
        return None, None
    phi = math.acos(c)
    v2 = vtop2 + 2 * g * R * (1 - c)
    v = math.sqrt(v2)
    h_sep = R * (1 + c)                         # 脱离点离最低点高度
    rise = (v * math.sin(phi)) ** 2 / (2 * g)
    return math.degrees(phi), h_sep + rise

for k in [0.0, 0.2, 0.5, 0.8, 0.99]:
    ang, hmax = apex_above_bottom(k)
    print("v_top^2/gR=%.2f | 脱离角 phi=%.2f deg | 弹道最高点离底=%.4f R | 顶点高度=2R=2.0000 | 能否过顶=%s"
          % (k, ang, hmax, hmax >= 2.0))

print("\n=== 5. 最低点支持力 N/m 全程极值（v0^2 = 5gR 与 0.99*5gR）===")
def Nmin_over_m(v0sq, g=9.8, R=1.0):
    best = 1e9
    for i in range(0, 1801):
        th = math.radians(i / 10.0)
        v2 = v0sq - 2 * g * R * (1 - math.cos(th))
        N = v2 / R + g * math.cos(th) - 2 * g  # 用 theta 从最低点量：N/m = v^2/R + g*cos(theta) - 2g? 见校验
        best = min(best, N)
    return best
# 直接解析：N/m = v0^2/R - 2g + 3g*cos(theta)，theta 从最低点量
for f in [1.0, 1.01, 0.99]:
    v0sq = f * 5 * 9.8 * 1.0
    Nmin = v0sq / 1.0 - 2 * 9.8 + 3 * 9.8 * (-1)
    print("v0^2 = %.4f*5gR | N_min/m = %.6f (>=0 ? %s)" % (f, Nmin, Nmin >= -1e-9))

print("\n=== 6. N(h) 线性核对：N/m = v0^2/R + g - 3gh/R ===")
g, R = 9.8, 1.0
v0sq = 5 * g * R
for h in [0.0, 0.5, 1.0, 1.5, 2.0]:
    print("h=%.2f R | N/m=%.6f" % (h, v0sq / R + g - 3 * g * h / R))

print("\n=== 7. 变式答案核对 ===")
# O2: h0=2R, v0=sqrt(5g*h0/2)
h0 = 2.0
print("O2: v0=sqrt(5g*h0/2)=%.6f, 对照 sqrt(5gR)=%.6f" % (math.sqrt(5 * 9.8 * h0 / 2), math.sqrt(5 * 9.8 * 1.0)))
# O5: v0=sqrt(g r + 2 g H)
for r, H in [(1.0, 2.0), (0.8, 3.0)]:
    print("O5: r=%.2f H=%.2f -> v0=%.6f | 退化检验 H=2r -> %.6f"
          % (r, H, math.sqrt(9.8 * r + 2 * 9.8 * H), math.sqrt(9.8 * r + 4 * 9.8 * r)))
# O3: 下界
print("O3: 下界 sqrt(5gR)=%.6f；上界 +inf（N 随 v0 单调增）" % math.sqrt(5 * 9.8))