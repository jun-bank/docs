#!/usr/bin/env python3
"""문서 검산. 통과 = 종료 코드 0.

★ 이 스크립트가 잡은 결함 수 < 사람이 새로 잡은 결함 수 이면 검산이 형식적이라는 뜻이다.
  study/project-workflow/verification-by-construction.md §6 참조.
"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import docs_model as d
from gen_matrix import ASSIGN, build

ROOT = d.ROOT
FAIL = []
def bad(rule, msg): FAIL.append(f"[{rule}] {msg}")

# ── ① 대장 행 == 조작 전집 (양방향)
idx = d.aggregate_index()
canon = {f"{c}.{op}" for c, (ko, f) in idx.items() for op in d.operations(d.AGG / f)}
assigned = set(ASSIGN)
for k in sorted(canon - assigned): bad("①", f"문서에 있으나 대장에 없음: {k}")
for k in sorted(assigned - canon): bad("①", f"대장에 있으나 문서에 없음: {k}")

# 목록 표 == 실제 파일
files = {p.name for p in d.aggregate_files()}
listed = {f for _, f in idx.values()}
for f in sorted(files - listed): bad("①", f"파일이 있으나 목록에 없음: {f}")
for f in sorted(listed - files): bad("①", f"목록에 있으나 파일이 없음: {f}")

# 생성된 대장이 README에 실제로 반영돼 있는가 (생성물과 문서가 갈리는 것을 막는다)
table, missing = build()
readme = (d.AGG / "README.md").read_text()
for k in missing: bad("②", f"경계 미배정: {k}")
if table not in readme:
    bad("①", "README의 조작 대장이 gen_matrix.py 생성 결과와 다르다 — 재생성 필요")

# ── ③④ 경계 참여자 == 그 경계가 붙은 행들의 소유
decl = d.boundaries()
if not decl: bad("④", "경계 표에서 참여자 열을 읽지 못했다")
used = {}
for k, b in ASSIGN.items():
    owner = k.split(".")[0]
    for e in b.split():
        if e.startswith("E"): used.setdefault(e, set()).add(owner)
for e in sorted(set(decl) | set(used)):
    if e not in decl: bad("④", f"대장이 참조하는 경계 {e}가 경계 표에 없다"); continue
    if e not in used: bad("③", f"경계 {e}에 배정된 조작이 하나도 없다"); continue
    for a in sorted(decl[e] - used[e]): bad("③", f"{e} 참여자 {a} — 그 경계를 단 조작이 없다")
    for a in sorted(used[e] - decl[e]): bad("③", f"{e}에 {a} 조작이 있으나 참여자 목록에 없다")

# ── ⑤ 부수 효과·사후조건 열의 `〃` (조작·전이 표에서만 — 여기서만 결함이 된다)
TARGET = sorted(d.AGG.glob("*.md")) + sorted((ROOT/"domain/state-machines").glob("*.md"))
def body(p):
    t = p.read_text()
    return t.split("\n## 변경 이력")[0]          # 이력은 옛 번호를 인용해야 한다
for p in TARGET:
    rel = p.relative_to(ROOT)
    for hdr, rows in d._rows(body(p), lambda c: any(h in ("사후조건","부수 효과") for h in c)):
        cols = [i for i,h in enumerate(hdr) if h in ("사후조건","부수 효과")]
        for r in rows:
            for i in cols:
                if i < len(r) and "〃" in r[i]:
                    bad("⑤", f"{rel} {r[0][:24]} — 부수 효과에 `〃`")

# ── ⑤ 이동·폐기된 심볼 (정본 문서 본문에서만 — 이력·변천 문서는 인용해야 한다)
DEAD = {"INV-10": "RC-1로 이동", "INV-11": "RC-2로 이동",
        "receivableTotal": "DC-001에서 제거", "recoverReceivable": "DC-001에서 제거"}
for p in TARGET:
    for n, line in enumerate(body(p).splitlines(), 1):
        for sym, why in DEAD.items():
            if re.search(rf"\b{sym}\b", line):
                bad("⑤", f"{p.relative_to(ROOT)}:{n} 폐기 심볼 {sym} ({why})")

# ── ⑥ 손으로 쓴 집계 수치
for p in sorted(ROOT.rglob("*.md")):
    if ".git" in p.parts or "project-workflow" in str(p): continue
    for n, line in enumerate(p.read_text().splitlines(), 1):
        m = re.search(r"유효 유형 (\d+)종.*?(\d+)종 전부", line)
        if m and m.group(1) != m.group(2):
            bad("⑥", f"{p.relative_to(ROOT)}:{n} 선언 불일치 {m.group(1)}종 vs {m.group(2)}종")

# ── ⑦ 없는 규칙 참조
BRS = ROOT/"product/01-business-rules.md"
brs = set(re.findall(r"^## (BR-\d+)\.", BRS.read_text(), re.M))
if len(brs) < 10: bad("⑦", f"규칙 목록 파싱 실패 ({len(brs)}건)")
for p in sorted(ROOT.rglob("*.md")):
    if ".git" in p.parts or p == BRS or "project-workflow" in str(p): continue
    for n, line in enumerate(p.read_text().splitlines(), 1):
        for r in set(re.findall(r"BR-\d+", line)):
            if r not in brs: bad("⑦", f"{p.relative_to(ROOT)}:{n} 없는 규칙 참조: {r}")

if FAIL:
    print(f"실패 {len(FAIL)}건\n" + "\n".join("  " + x for x in FAIL)); sys.exit(1)
print(f"통과 — 애그리게이트 {len(idx)} · 조작 {len(canon)} · 경계 {len(decl)}")
