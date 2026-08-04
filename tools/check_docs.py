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
WIDE   = TARGET + [ROOT/"product/01-business-rules.md", ROOT/"domain/context-map.md", ROOT/"domain/event-storming.md"]
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

# ── ⑧ 교차 호출 → 공유 경계 (배정의 정확성을 독립 출처로 검사한다)
#    문서가 스스로 "남의 조작을 부른다"고 적었으면, 그 둘은 같은 트랜잭션에 있어야 한다.
#    ASSIGN 은 사람 판단이므로 ASSIGN 끼리 비교해서는 오배정을 잡을 수 없다.
REAL = lambda b: {e for e in b.split() if e.startswith("E")}
owner_b = {}
for k, b in ASSIGN.items():
    owner_b.setdefault(k.split(".")[0], set()).update(REAL(b))
ko2code = {ko: c for c, (ko, f) in idx.items()}
for p in TARGET:
    stem = p.stem
    me = next((c for c, (ko, f) in idx.items() if f == stem + ".md"), None)
    if me is None: continue
    for n, line in enumerate(body(p).splitlines(), 1):
        for callee, op in set(re.findall(r"`([A-Z][a-zA-Z]*)\.([a-z][a-zA-Z]*)\(", line)):
            if callee == me or callee not in idx: continue
            key = f"{callee}.{op}"
            if key not in ASSIGN: bad("⑧", f"{p.relative_to(ROOT)}:{n} 없는 조작 호출: {key}"); continue
            if ASSIGN[key].strip() == "별도": continue   # 의도적 분리 (BR-40)
            shared = owner_b.get(me, set()) & REAL(ASSIGN[key])
            if not shared:
                bad("⑧", f"{p.relative_to(ROOT)}:{n} {me}가 {key}를 부르는데 "
                         f"공유 트랜잭션 경계가 없다 (호출자 {sorted(owner_b.get(me,set())) or '없음'} "
                         f"vs 피호출 {sorted(REAL(ASSIGN[key])) or '없음'})")

# ── ⑧-b 경계 주석 ⟨En⟩ — 산문에서도 경계를 기계 판독 가능하게
#     ⑧은 애그리게이트 단위라, 같은 애그리게이트의 다른 조작 배정은 검사되지 않는다(R8 K3).
#     조작 단위로 강제하려면 문서가 "이 절차는 En이다"를 기계가 읽을 수 있게 적어야 한다.
for p in TARGET:
    blocks, cur = [], []
    for line in body(p).splitlines():
        if line.strip(): cur.append(line)
        elif cur: blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    for blk in blocks:
        txt = "\n".join(blk)
        tags = set(re.findall(r"⟨(E\d)⟩", txt))
        if not tags: continue
        for callee, op in set(re.findall(r"`([A-Z][a-zA-Z]*)\.([a-z][a-zA-Z]*)\(", txt)):
            key = f"{callee}.{op}"
            if key not in ASSIGN: bad("⑧", f"{p.relative_to(ROOT)} ⟨{'/'.join(tags)}⟩ 없는 조작: {key}"); continue
            for t_ in tags:
                if t_ not in ASSIGN[key].split():
                    bad("⑧", f"{p.relative_to(ROOT)} ⟨{t_}⟩ 절차에 {key}가 있으나 "
                             f"그 조작의 배정은 `{ASSIGN[key]}` 다")

# ── ⑨ 불변식 참조 무결성 (폐기 심볼 하드코딩을 대신한다)
DEFINED = {}
for p in sorted(d.AGG.glob("*.md")):
    if p.name == "README.md": continue
    t = body(p)
    DEFINED[p.stem] = set(re.findall(r"\| \*{0,2}(INV-\d+|RC-\d+|POST-\d+|PRE-\d+)\*{0,2} \|", t))
stem_of = {ko: f[:-3] for c, (ko, f) in idx.items()}
for p in WIDE:
    for n, line in enumerate(body(p).splitlines(), 1):
        for ko, num in re.findall(r"(계좌|카드|승인|미수|배치|정산|전표|불일치|멱등|예약)\s*((?:INV|RC)-\d+)", line):
            tgt = stem_of.get(ko) or {"배치":"capture-batch","예약":"reversal-tombstone","멱등":"idempotency-record"}.get(ko)
            if tgt and tgt in DEFINED and num not in DEFINED[tgt]:
                bad("⑨", f"{p.relative_to(ROOT)}:{n} {ko} {num} — {tgt}.md에 정의가 없다")
        bare = re.findall(r"(?<![가-힣] )\b(INV-\d+|RC-\d+)\b", line)
        for num in set(bare):
            if re.search(rf"(계좌|카드|승인|미수|배치|정산|전표|불일치|멱등|예약)\s*{num}", line): continue
            m2 = re.search(rf"`([a-z-]+)\.md`[^|]{{0,20}}{num}", line)   # `journal-entry.md` INV-6
            if m2:
                if m2.group(1) in DEFINED and num not in DEFINED[m2.group(1)]:
                    bad("⑨", f"{p.relative_to(ROOT)}:{n} {m2.group(1)}.md {num} — 정의가 없다")
                continue
            if p.parent.name == "aggregates" and p.stem in DEFINED and num not in DEFINED[p.stem]:
                bad("⑨", f"{p.relative_to(ROOT)}:{n} {num} — 이 문서에 정의가 없다")

# ── ⑩ 종수 선언 vs 실제 파일 수
for d_, pat in ((d.AGG, "*.md"), (ROOT/"domain/state-machines", "*.md")):
    n_files = len([x for x in d_.glob(pat) if x.name != "README.md"])
    rm = d_/"README.md"
    m = re.search(r"상태:.*?(\d+)종", rm.read_text())
    if m and int(m.group(1)) != n_files:
        bad("⑩", f"{rm.relative_to(ROOT)} 헤더 {m.group(1)}종 vs 실제 파일 {n_files}개")

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
