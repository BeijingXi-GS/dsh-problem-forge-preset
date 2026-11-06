# -*- coding: utf-8 -*-
"""形态门实测 + 回填：学生版字数 / 每题说明行 / 元信息扫描 / A4 打印页数。

一次运行完成「测量 → 把数字与日志写回示例文件 → 写 check_student_sheet.log」。

用法（在仓库根目录）：python examples/verify/check_student_sheet.py
可选环境变量 EDGE_PATH 指定 msedge.exe；不设则自动探测常见安装位置
（找不到 Edge 时第 4 项页数记为 -1，其余检查照常进行）。
"""
import io, os, re, subprocess, tempfile, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MD = os.path.join(ROOT, "examples", "示例_学生版极简与主线表.md")
TEACHER = os.path.join(ROOT, "examples", "示例_物理_竖直圆轨道.md")
LOG = os.path.join(ROOT, "examples", "verify", "check_student_sheet.log")

EDGE = ""
for _cand in (os.environ.get("EDGE_PATH", ""),
              r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
              r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"):
    if not _cand:
        continue
    _cand = os.path.expandvars(_cand)
    if os.path.isfile(_cand):
        EDGE = _cand
        break

KEY = ["目标", "台阶", "知识点", "D1", "D2", "D3", "D4", "D5",
       "P1", "P2", "P3", "P4", "P5", "P6", "P7",
       "评分", "诊断", "教师", "主线", "验收", "回退", "变式", "考点", "难度", "解析", "答案"]

def read(p):
    return io.open(p, encoding="utf-8").read()

def nchars(t):
    return len(t.replace("\r", "").replace("\n", ""))

log = []
def out(s=""):
    log.append(s)
    print(s)

teacher = read(TEACHER)
md = read(MD)
m = re.search(r"<!-- STUDENT-BEGIN -->(.*?)<!-- STUDENT-END -->", md, re.S)
student = m.group(1)
t_chars, s_chars = nchars(teacher), nchars(student)
budget = t_chars / 3.0

out("[1] 字符数（去 CR/LF 的 Unicode 码点）")
out("    teacher = %d" % t_chars)
out("    student = %d" % s_chars)
out("    ratio   = %.2f%%  (1/3 预算 %.0f 字)" % (100.0 * s_chars / t_chars, budget))
out("    学生版占预算 %.1f%%" % (100.0 * s_chars / budget))

pre, blocks = student.split("### ")[0].strip(), re.split(r"^### ", student, flags=re.M)[1:]
out("[2] 逐题行数统计（题干行 / 作答区行 / 提示行 / 表格行 / 说明行）")
out("    使用说明: 1 段（位于方框开头，未计入每题）" if pre else "    使用说明: 缺失")
total_expl = 0
for b in blocks:
    lines = b.split("\n")
    title, body = lines[0].strip(), lines[1:]
    stem = ans = hint = tbl = expl = 0
    seen_ans = False
    for ln in body:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("作答区"):
            ans += 1; seen_ans = True
        elif s.startswith("提示"):
            hint += 1
        elif s.startswith("|"):
            tbl += 1
        elif s.startswith("**★"):
            stem += 1
        elif not seen_ans:
            stem += 1
        else:
            expl += 1
    total_expl += expl
    out("    %-4s 题干=%d 作答区=%d 提示=%d 表格=%d 说明=%d" % (title, stem, ans, hint, tbl, expl))
out("    题干外说明合计 = %d（规则上限：每题 ≤1）" % total_expl)

out("[3] 元信息扫描（学生版方框内，%d 个关键词）" % len(KEY))
nz = {k: student.count(k) for k in KEY if student.count(k)}
out("    命中: " + ("无" if not nz else str(nz)))
out("    全部为 0 = %s" % (not nz))

# A4 打印页数
def esc(s):
    s = html.escape(s)
    return re.sub(r"\$([^$]+)\$", r"\1", s)  # 版式测量：公式去 $ 按纯文本宽度近似

css = """
@page { size: A4; margin: 2cm; }
body { font-family: "SimSun",serif; font-size: 10.5pt; line-height: 1.6; }
h1 { font-size: 15pt; margin: 0 0 .4cm 0; }
h3 { font-size: 11.5pt; margin: .45cm 0 .2cm 0; }
p { margin: .12cm 0; }
table { border-collapse: collapse; margin: .15cm 0; }
td { border: 1px solid #000; padding: .06cm .5cm; text-align: center; }
.ans { height: 3.6cm; border-bottom: 1px solid #000;
       background: repeating-linear-gradient(to bottom, transparent 0, transparent .89cm, #000 .89cm, #000 .9cm); }
.hint { font-size: 9pt; border: 1px dashed #000; padding: .1cm .2cm; margin: .1cm 0; }
.usage { font-size: 9.5pt; }
"""
parts = ["<!doctype html><meta charset='utf-8'><style>%s</style><body><h1>练习单</h1>" % css]
if pre:
    parts.append("<p class='usage'>%s</p>" % esc(pre))
for b in blocks:
    lines = b.split("\n")
    parts.append("<h3>%s</h3>" % esc(lines[0].strip()))
    tbl_open = False
    for ln in lines[1:]:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("|"):
            if not tbl_open:
                parts.append("<table>"); tbl_open = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            parts.append("<tr>" + "".join("<td>%s</td>" % esc(c) for c in cells) + "</tr>")
            continue
        if tbl_open:
            parts.append("</table>"); tbl_open = False
        if s.startswith("作答区"):
            parts.append("<div class='ans'></div>")
        elif s.startswith("提示"):
            parts.append("<p class='hint'>%s</p>" % esc(s))
        else:
            parts.append("<p>%s</p>" % esc(s))
    if tbl_open:
        parts.append("</table>")
parts.append("</body>")

tmp = tempfile.mkdtemp(prefix="student_a4_")
hpath = os.path.join(tmp, "sheet.html")
ppath = os.path.join(tmp, "sheet.pdf")
io.open(hpath, "w", encoding="utf-8").write("\n".join(parts))
pages = -1
rc = -1
if EDGE:
    r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=" + ppath, "file:///" + hpath.replace("\\", "/")],
                       capture_output=True, timeout=120)
    rc = r.returncode
    if os.path.exists(ppath):
        data = open(ppath, "rb").read()
        pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
out("[4] A4 打印页数（Edge headless：A4、边距 2cm、10.5pt、每题 4 行作答区 3.6cm）")
out("    pages = %d  (edge rc=%d)%s" % (pages, rc, "" if EDGE else "  [未找到 Edge：设 EDGE_PATH 后重跑]"))
out("    口径：Markdown→A4 HTML，公式去 $ 后按纯文本宽度近似，误差 ±5%")

nlines = len(md.split("\n")) - (1 if md.endswith("\n") else 0)
out("[5] 文件总行数 = %d（上限 200）" % nlines)

# 回填（数字 + 日志块）
new_block = "```text\n" + "\n".join(log) + "\n```"
new = re.sub(r"```text\n.*?\n```", lambda _: new_block, md, count=1, flags=re.S)
new = re.sub(r"学生版 \d+ 字；\d+/14901 = [\d.]+%（占预算 [\d.]+%）",
             "学生版 %d 字；%d/14901 = %.2f%%（占预算 %.1f%%）" %
             (s_chars, s_chars, 100.0 * s_chars / t_chars, 100.0 * s_chars / budget), new)
new = re.sub(r"只有 \d+ 字（占预算 [\d.]+%，门允许写到它的 [\d.]+ 倍）",
             "只有 %d 字（占预算 %.1f%%，门允许写到它的 %.1f 倍）" %
             (s_chars, 100.0 * s_chars / budget, budget / s_chars), new)
new = re.sub(r"\d+ 字加每题 4 行作答区已排到 \d+ 页",
             "%d 字加每题 4 行作答区已排到 %d 页" % (s_chars, pages), new)
new = re.sub(r"打出 \*\*\d+ 页\*\*", "打出 **%d 页**" % pages, new)
new = re.sub(r"实测 5 题 \+ 2 选做按 4 行作答区排是 \d+ 页",
             "实测 5 题 + 2 选做按 4 行作答区排是 %d 页" % pages, new)

if new != md:
    io.open(MD, "w", encoding="utf-8").write(new)
    print("[patched] md updated")
io.open(LOG, "w", encoding="utf-8").write("\n".join(log) + "\n")
print("[ok] log ->", LOG)
