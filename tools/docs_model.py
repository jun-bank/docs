"""문서에서 정본 집합을 뽑는다. 손으로 쓴 목록을 신뢰하지 않는다."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGG  = ROOT / "domain" / "aggregates"

def _rows(md, header_pred):
    """표를 (헤더, [행]) 로 뽑는다."""
    out, cur, hdr = [], None, None
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):      # 구분선
                continue
            if hdr is None:
                if header_pred(cells): hdr, cur = cells, []
            else:
                cur.append(cells)
        elif hdr is not None and cur:
            out.append((hdr, cur)); hdr, cur = None, None
    if hdr is not None and cur: out.append((hdr, cur))
    return out

def aggregate_files():
    return sorted(p for p in AGG.glob("*.md") if p.name != "README.md")

def aggregate_index():
    """README 목록 표 → {코드명: (한글명, 파일)}  ※ 파일 목록과 대조된다"""
    md = (AGG / "README.md").read_text()
    idx = {}
    for hdr, rows in _rows(md, lambda c: c[:2] == ["애그리게이트", "컨텍스트"]):
        for r in rows:
            m = re.search(r"\*\*(.+?)\*\*\s*`(\w+)`", r[0])
            f = re.search(r"\((\S+?\.md)\)", r[3])
            if m and f: idx[m.group(2)] = (m.group(1), f.group(1))
    return idx

def operations(path):
    """§5 조작 표 → [코드명] (인자 제거)"""
    md = path.read_text()
    m = re.search(r"\n## \d+\. 조작.*?(?=\n## |\Z)", md, re.S)
    sec = m.group(0) if m else ""
    ops = []
    for hdr, rows in _rows(sec, lambda c: c[:2] == ["조작", "코드명"]):
        for r in rows:
            for m in re.finditer(r"`([a-zA-Z]\w*)\s*\(", r[1]):
                ops.append(m.group(1))
    return ops

def matrix():
    """변경 매트릭스 → (열 한글명, [(조작코드, {열: bool}, 경계)])"""
    md = (AGG / "README.md").read_text()
    tabs = _rows(md, lambda c: c[0] == "조작" and c[-1].strip("*") == "경계")
    if not tabs: return [], []
    hdr, rows = tabs[0]
    cols = [c.strip("* ") for c in hdr[1:-1]]
    out = []
    for r in rows:
        m = re.search(r"`(\w+)`", r[0])
        out.append((m.group(1) if m else r[0].strip("*` "),
                    {c: (v.strip() == "●") for c, v in zip(cols, r[1:-1])},
                    r[-1].strip("* ")))
    return cols, out

def boundaries():
    """트랜잭션 경계 표 → {E1: {참여자 코드명}}  — 기계 판독 가능한 칸에서만 읽는다"""
    md = (AGG / "README.md").read_text()
    b = {}
    for hdr, rows in _rows(md, lambda c: c[0] == "#" and "참여자" in " ".join(c)):
        pi = next(i for i, h in enumerate(hdr) if "참여자" in h)
        for r in rows:
            k = r[0].strip("* ")
            b[k] = set(re.findall(r"`(\w+)`", r[pi]))
    return b
