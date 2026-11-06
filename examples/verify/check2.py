from fractions import Fraction as Fr
import math
# y1*y2 = -4 ?  and |AF|*|BF| = |AB| ?
for k in [1,2,-3,Fr(1,2)]:
    k=Fr(k); A=k*k; B=-(2*k*k+4); C=k*k
    d=B*B-4*A*C
    sq=Fr(math.sqrt(float(d))) if False else None
    s=-B/A; p=C/A
    # (y1*y2) = k^2*(x1-1)(x2-1) = k^2*(p - s + 1)
    yy = k*k*(p - s + 1)
    AFBF = (p + s + 1)
    AB = s + 2
    print(f"k={k}: x1x2={p}, x1+x2={s}, y1y2={yy} (==-4? {yy==-4}), |AF||BF|={AFBF}, |AB|={AB}, equal? {AFBF==AB}")
# 垂直
print("vertical: x1x2=1, |AF||BF|=4, |AB|=4 ->", 1==1, 2*2==4)
