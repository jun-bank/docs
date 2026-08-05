#!/usr/bin/env python3
"""문서 검산. 통과 = 종료 코드 0.

★ 이 스크립트가 잡은 결함 수 < 사람이 새로 잡은 결함 수 이면 검산이 형식적이라는 뜻이다.
  study/project-workflow/verification-by-construction.md §6 참조.
"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import docs_model as d
from gen_matrix import ASSIGN, NOTE, build

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

# ── ③-b 경계 참여 **조작** 목록 == ASSIGN (양방향) — 오배정·과잉 배정을 잡는다
declared_ops = {}
for hdr, rows in d._rows((d.AGG/"README.md").read_text(),
                         lambda c: c[0] == "#" and "참여 조작" in " ".join(c)):
    oi = next(i for i, h in enumerate(hdr) if "참여 조작" in h)
    for r in rows:
        declared_ops[r[0].strip("* ")] = set(re.findall(r"`([\w.]+)`", r[oi]))
if not declared_ops: bad("③", "경계 표에서 참여 조작 열을 읽지 못했다")
used_ops = {}
for k, b in ASSIGN.items():
    for e in b.split():
        if e.startswith("E"): used_ops.setdefault(e, set()).add(k)
for e in sorted(set(declared_ops) | set(used_ops)):
    dc, us = declared_ops.get(e, set()), used_ops.get(e, set())
    for o in sorted(dc - us): bad("③", f"{e} 참여 조작 {o} — 대장 배정에 {e}가 없다")
    for o in sorted(us - dc): bad("③", f"{e}를 단 조작 {o} — 경계 표 참여 조작에 없다 (과잉 배정?)")

# ── ⑪ `별도` 는 촉발 이벤트가 있어야 한다 (그것이 `—`와 다른 점이다)
EVENTS = set()
for p_ in sorted(d.AGG.glob("*.md")):
    for hdr, rows in d._rows(p_.read_text(), lambda c: any("이벤트" in h for h in c)):
        for r in rows: EVENTS |= set(re.findall(r"`([A-Z]\w+)`", " ".join(r)))
for k, b in ASSIGN.items():
    cited = {x for x in re.findall(r"`([A-Z]\w+)`", NOTE.get(k, "")) if x in EVENTS}
    if b.strip() == "별도" and not cited:
        bad("⑪", f"{k}가 `별도`인데 비고에 촉발 이벤트가 없다 — `—`(단일)와 구분되지 않는다")
    if b.strip() != "별도" and cited:
        bad("⑪", f"{k}는 촉발 이벤트({sorted(cited)})를 인용하는데 배정이 `{b}` 다 — `별도`여야 한다")

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
        m = re.search(r"배치 탐지 대상 (\d+)종.*?(\d+)종 전부", line)
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

# ── ⑬ ACL 소유 규칙 표가 **모든 경계**를 덮는가
#    R9 T1의 뿌리: 표가 E3·E4·E5만 덮어 E1·E2가 옛 규칙으로 남았다.
je = (d.AGG/"journal-entry.md").read_text()
owned = set(re.findall(r"\| \*\*(E[1-5]) ", je))
for e in sorted(set(decl) - owned):
    bad("⑬", f"ACL 소유 규칙 표에 {e} 행이 없다 — 그 경계의 이벤트가 판정 없이 남는다")

# ── ⑭ 등식 우변 필드 ↔ 전이 사후조건
#    RC 등식의 우변 필드를 바꾸는 전이가 그것을 사후조건에 적었는가.
#    "홀딩·한도를 건드리는데 구성 요소를 안 적음"이 세 라운드 연속 나왔다.
RHS = set()
for p_ in sorted(d.AGG.glob("*.md")):
    for n_, line in enumerate(body(p_).splitlines(), 1):
        if re.match(r"\| \*{0,2}RC-\d+", line):
            RHS |= {x for x in re.findall(r"`(\w+)`", line) if x[0].islower()}
RHS &= {"heldAmount", "limitContribution", "recoveredAmount", "outstanding"}
TOUCH = ("홀딩", "한도")
sm = ROOT/"domain/state-machines/authorization.md"
for hdr, rows in d._rows(body(sm), lambda c: "부수 효과" in c):
    fi = hdr.index("부수 효과")
    for r in rows:
        if fi >= len(r): continue
        eff = r[fi]
        if not any(t in eff for t in TOUCH): continue
        if "복원하지 않는다" in eff or "해제 없음" in eff or "재복원 없음" in eff: continue
        named = {x for x in re.findall(r"`(\w+)`", eff)}
        if not (named & RHS):
            bad("⑭", f"{sm.relative_to(ROOT)} {r[0]} — 홀딩·한도를 바꾸는데 "
                     f"등식 구성 요소({sorted(RHS)})를 사후조건에 안 적었다")

# ── ⑮ ACL ↔ 이벤트 payload ↔ 보조부
#    ACL이 쓰는 필드가 그 이벤트 payload에 있는가. 보조부 계정은 식별자를 싣는가.
PAYLOAD = {}
for p_ in sorted(d.AGG.glob("*.md")):
    for hdr, rows in d._rows(body(p_), lambda c: any("담는" in h for h in c)):
        ci = next(i for i, h in enumerate(hdr) if "담는" in h)
        for r in rows:
            ev = re.findall(r"`(\w+)`", r[1] if len(r) > 1 else "")
            if not ev: continue
            PAYLOAD.setdefault(ev[0], set()).update(re.findall(r"`(\w+)`", r[ci]) if ci < len(r) else [])
SUBLEDGER = ("고객예금", "미수금")
je = (d.AGG/"journal-entry.md").read_text()
for hdr, rows in d._rows(je, lambda c: c[:2] == ["상류 이벤트", "전표"]):
    for r in rows:
        ev = re.findall(r"`(\w+)`", r[0])
        if not ev or "기표 없음" in r[1] or "원장 아님" in r[1]: continue
        ev = ev[0]
        if ev not in PAYLOAD: bad("⑮", f"ACL이 번역하는 `{ev}` 의 발행 이벤트 정의를 못 찾았다"); continue
        for f in {x for x in re.findall(r"`(\w+)`", r[1]) if x[0].islower()}:
            if f not in PAYLOAD[ev]:
                bad("⑮", f"ACL의 `{ev}` 전표가 `{f}` 를 쓰는데 그 이벤트 payload에 없다")
        if any(a in r[1] for a in SUBLEDGER) and not (PAYLOAD[ev] & {"accountId", "subjectId"}):
            bad("⑮", f"`{ev}` 가 보조부 계정을 기표하는데 payload에 `accountId`가 없다 (INV-7)")

# ── ⑯ 배정 커버리지 — 독립 출처로 검사되는 비율
verified = set()
for p_ in TARGET:
    t = body(p_)
    for callee, op in set(re.findall(r"`([A-Z][a-zA-Z]*)\.([a-z][a-zA-Z]*)\(", t)):
        if f"{callee}.{op}" in ASSIGN: verified.add(f"{callee}.{op}")
e_assigned = {k for k, v in ASSIGN.items() if any(x.startswith("E") for x in v.split())}
cov = len(verified & e_assigned) * 100 // max(1, len(e_assigned))
COVERAGE_FLOOR = 15
if cov < COVERAGE_FLOOR:
    bad("⑯", f"배정 커버리지 {cov}% — 경계 배정 {len(e_assigned)}건 중 "
             f"독립 출처로 검사되는 것은 {len(verified & e_assigned)}건. 하한 {COVERAGE_FLOOR}%")

# ── ⑰ 불일치 유형 집합 == BR-09 정본 (건수를 파생 문서가 따로 선언하지 않는다)
brs_txt = BRS.read_text()
m = re.search(r"## BR-09\..*?(?=\n## BR-)", brs_txt, re.S)
canon_m = set(re.findall(r"^\| (M\d+) \|", m.group(0), re.M)) if m else set()
if len(canon_m) < 5: bad("⑰", f"BR-09 유형 표 파싱 실패 ({len(canon_m)})")
for p_ in sorted(ROOT.rglob("*.md")):
    if ".git" in p_.parts or "project-workflow" in str(p_) or "design-changes" in str(p_): continue
    for n, line in enumerate(body(p_).splitlines() if p_ in WIDE else p_.read_text().splitlines(), 1):
        if re.match(r"> \*\*v\d", line.strip()): continue      # 버전 주석은 옛 건수를 인용한다
        mm = re.search(r"유효 유형은? \*{0,2}(\d+)종", line) or (None if p_ == BRS else re.search(r"유형[^|\d]{0,6}(\d+)종", line))
        if mm and int(mm.group(1)) != len(canon_m):
            bad("⑰", f"{p_.relative_to(ROOT)}:{n} 불일치 유형 {mm.group(1)}종 선언 "
                     f"— BR-09 정본은 {len(canon_m)}종. 파생 문서는 건수를 적지 않는다")

# ── ⑱ ③ 의식적 예외는 세 칸이 전부 채워져야 한다 (04 §4)
#    "등재만 하고 정본·탐지가 비어 있다"가 R7 U7 · DC-002 였다.
for p_ in sorted(d.AGG.glob("*.md")):
    t = body(p_)
    for m in re.finditer(r"###[^\n]*의식적 예외.*?(?=\n### |\n## |\Z)", t, re.S):
        blk = m.group(0)
        cells = dict(re.findall(r"^\| \*\*(등식|정본|트랜잭션 경계|탐지)\*\* \| (.+?) \|\s*$", blk, re.M))
        for k in ("등식", "탐지"):
            if k not in cells: bad("⑱", f"{p_.relative_to(ROOT)} ③ 예외에 `{k}` 칸이 없다")
        for k, v in cells.items():
            if re.search(r"미정|미완|불충분|없다|⚠️", v):
                bad("⑱", f"{p_.relative_to(ROOT)} ③ 예외의 `{k}`가 미완이다 — "
                         f"세 칸이 채워지지 않으면 ③을 고를 수 없다 (04 §4)")

# ── ⑫ 열린 의문 색인 == 각 상태 머신 문서의 의문 ID (양방향)
SM = ROOT/"domain/state-machines"
docq = set()
for p_ in sorted(SM.glob("*.md")):
    if p_.name == "README.md": continue
    m = re.search(r"\n## \d+\. (?:미해결|의문).*?(?=\n## |\Z)", p_.read_text(), re.S)
    if not m: bad("⑫", f"{p_.relative_to(ROOT)} 의문 절이 없다"); continue
    docq |= set(re.findall(r"\| \*{0,2}([A-Z]{2,4}\d+)\*{0,2} \|", m.group(0)))
rm = (SM/"README.md").read_text()
sec = rm[rm.index("## 열린 의문"):] if "## 열린 의문" in rm else ""
idxq = set(re.findall(r"^\| \*\*([A-Z]{2,4}\d+)\*\*", sec, re.M))
for q in sorted(idxq - docq): bad("⑫", f"색인에만 있는 의문(유령): {q}")
for q in sorted(docq - idxq): bad("⑫", f"문서에만 있는 의문(누락): {q}")
m = re.search(r"## 열린 의문 \((\d+)건\)", rm)
if m and int(m.group(1)) != len(idxq):
    bad("⑫", f"열린 의문 선언 {m.group(1)}건 vs 실제 {len(idxq)}건")

if FAIL:
    print(f"실패 {len(FAIL)}건\n" + "\n".join("  " + x for x in FAIL)); sys.exit(1)
print(f"통과 — 애그리게이트 {len(idx)} · 조작 {len(canon)} · 경계 {len(decl)}")
