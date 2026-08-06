r"""API 레퍼런스를 정본에서 생성한다. 행을 손으로 쓰지 않는다 (gen_matrix 선례).

스파인 = usecases/README.md §2 엔드포인트 색인 (전수 정본).
보강   = 각 UC §7 계약 블록(`#### \`METHOD path\``)의 멱등·오류 표 행.
출력   = docs/api-reference.md — 수기 편집 금지(재생성으로만 갱신).
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
UC_DIR = ROOT / "usecases"

def index_rows():
    """색인 §2 표의 (인터페이스 셀, UC 셀, 주체 셀, L7 셀) 행들."""
    t = (UC_DIR / "README.md").read_text()
    s = t.index("## 2."); e = t.index("## 3.")
    rows = []
    for line in t[s:e].splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) >= 4 and cells[0] not in ("인터페이스", "엔드포인트"):
            rows.append(cells[:4])
    return rows

def uc_blocks():
    r"""UC 파일별 `#### \`METHOD path\`` 블록에서 멱등·오류 행을 추출."""
    out = {}  # (파일, 경로키) -> {"멱등": .., "오류": ..}
    for f in sorted(UC_DIR.glob("UC-*.md")):
        t = f.read_text()
        for m in re.finditer(r"^####\s+`((?:GET|POST|PUT|DELETE)[^`]+)`.*?(?=^####|^## |\Z)",
                             t, re.M | re.S):
            head = m.group(1)
            pm = re.match(r"(?:GET|POST|PUT|DELETE)\s+(\S+)", head)
            if not pm:
                continue
            path = pm.group(1).split("?")[0]
            block = m.group(0)
            entry = {}
            for key, label in (("멱등", "멱등"), ("오류", "오류 표")):
                rm = re.search(r"^\|\s*" + re.escape(label) + r"[^|]*\|\s*(.+?)\s*\|\s*$",
                               block, re.M)
                if rm:
                    entry[key] = rm.group(1)
            out.setdefault(path, {"file": f.name, **entry})
    return out

def first_sentence(s, limit=120):
    s = re.sub(r"\*\*|★|⚠️", "", s)
    return (s[:limit] + "…") if len(s) > limit else s

def build():
    idx = index_rows()
    blocks = uc_blocks()
    lines = [
        "# API 레퍼런스 (생성 문서 — 수기 편집 금지)",
        "",
        "> `tools/gen_api_reference.py`가 **usecases/README.md §2 색인**(스파인)과 **각 UC §7 계약 블록**에서 생성한다.",
        "> 의미의 정본은 각 UC §7이다 — 이 표는 조회 창구다. 갱신 = 재생성(검사가 drift를 잡는다).",
        "",
        "| 인터페이스 | UC | 주체 | L7/비고 | 멱등 (§7 발췌) |",
        "|---|---|---|---|---|",
    ]
    n_enriched = 0
    for iface, uc, subject, l7 in idx:
        pm = re.search(r"`(?:GET|POST|PUT|DELETE)[^`]*?(\S+?)`", iface)
        idem = ""
        if pm:
            path = pm.group(1).split("?")[0]
            b = blocks.get(path)
            if b and b.get("멱등"):
                idem = first_sentence(b["멱등"]); n_enriched += 1
        if not idem:
            idem = "(§7 참조)"
        lines.append(f"| {iface} | {uc} | {subject} | {l7} | {idem} |")
    lines += [
        "",
        f"> 행 {len(idx)}개 = 색인 §2 전수 · §7 멱등 발췌 {n_enriched}건 · 물리 규격 = [`interfaces/`](interfaces/README.md) · 이벤트 = 색인 §3 · 오류 코드 창구 = 색인 §5 코드 대장.",
    ]
    return "\n".join(lines) + "\n", len(idx)

if __name__ == "__main__":
    text, n = build()
    out = ROOT / "api-reference.md"
    if "--check" in sys.argv:
        cur = out.read_text() if out.exists() else ""
        if cur != text:
            print("api-reference.md drift — 재생성 필요", file=sys.stderr)
            sys.exit(1)
        print(f"api-reference 일치 ({n}행)")
    else:
        out.write_text(text)
        print(f"생성 완료: {out} ({n}행)")
