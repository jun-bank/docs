#!/usr/bin/env python3
"""변이 검사 — 과거에 실제로 났던 결함을 다시 주입하고, 검산이 잡는지 본다.

★ 통과하는 검산은 "결함이 없다"를 뜻하지 않는다. "이 검산이 아무것도 안 한다"일 수도 있다.
  R7 U1이 이것을 손으로 발견했다 — "R6가 잡은 치명 3건을 되돌려도 전부 통과한다".
"""
import subprocess, sys, shutil, tempfile, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (이름, 파일, 찾을 것, 바꿀 것, 원래 잡은 라운드)
MUT = [
 ("행 누락 — 조작을 대장에서 지운다", "tools/gen_matrix.py",
  '"Receivable.writeOff":"E4",', '', "R7 U5"),
 ("경계 참여자 누락 — E4에서 배치를 뺀다", "domain/aggregates/README.md",
  "`Authorization` `Account` `Receivable` `CaptureBatch`", "`Authorization` `Account` `Receivable`", "R7 U2"),
 ("배정 오류 — promoteIsolated를 단독으로", "tools/gen_matrix.py",
  '"CaptureBatch.promoteIsolated":"E2",', '"CaptureBatch.promoteIsolated":"—",', "R8 S1"),
 ("이동한 번호 잔재 — RC-1을 INV-10으로", "domain/aggregates/authorization.md",
  "(**RC-1** — 승인 단독으로 검증 불가)", "(INV-10)", "R7 U6"),
 ("없는 불변식 참조 — 카드 RC-1을 INV-5로", "domain/aggregates/authorization.md",
  "**카드 RC-1**", "카드 INV-5", "R8 K9"),
 ("집계 선언 불일치 — 10종을 9종으로", "product/01-business-rules.md",
  "→ **10종 전부 탐지", "→ **9종 전부 탐지", "R7 U8"),
 ("종수 선언 불일치 — 8종을 7종으로", "domain/state-machines/README.md",
  "**8종 작성**", "**7종 작성**", "R8 K13"),
 ("부수 효과 `〃` 주입", "domain/aggregates/receivable.md",
  None, None, "R1 C1"),
 ("기준소스의 없는 불변식 참조 — 계좌 RC-9", "product/01-business-rules.md",
  "**계좌 RC-1**", "계좌 RC-9", "R8 S17"),
 ("없는 규칙 참조 — BR-99", "domain/aggregates/account.md",
  "(BR-34)", "(BR-99)", "상시"),
]

def run(tree):
    r = subprocess.run([sys.executable, str(tree/"tools"/"check_docs.py")],
                       capture_output=True, text=True)
    return r.returncode, r.stdout

def main():
    base, ok = int(run(ROOT)[0]), 0
    if base != 0:
        print("기준 상태가 이미 실패한다 — 변이 검사 전에 고쳐라"); return 1
    for name, rel, old, new, origin in MUT:
        with tempfile.TemporaryDirectory() as td:
            tree = pathlib.Path(td)/"docs"
            shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            f = tree/rel; t = f.read_text()
            if old is None:                       # `〃` 주입 — 사후조건 칸
                lines = t.splitlines()
                for li, ln in enumerate(lines):
                    if ln.startswith("| **회수**"):
                        c = ln.split("|"); c[4] = " 〃 "; lines[li] = "|".join(c); break
                else: print(f"  ⚠️  {name} — 주입 지점 없음"); continue
                t = "\n".join(lines)
            else:
                if t.count(old) < 1:
                    print(f"  ⚠️  {name} — 변이 대상이 문서에 없다 ({old[:30]!r})"); continue
                t = t.replace(old, new, 1)
            f.write_text(t)
            if rel.startswith("tools/") and "regen" not in name:
                # 대장을 재생성한다 — 그래야 "재생성 필요"(①)가 아니라 의미 검사가 시험된다
                r = subprocess.run([sys.executable, "-c",
                    "import sys;sys.path.insert(0,'tools');from gen_matrix import build\n"
                    "new,_=build();p='domain/aggregates/README.md';s=open(p).read()\n"
                    "i=s.index('| 조작 | 소유 | 참여 경계 | 비고 |');j=s.index(chr(10)+chr(10)+'### 무엇이 검사되는가')\n"
                    "open(p,'w').write(s[:i]+new+s[j:])"], cwd=tree, capture_output=True, text=True)
            code, out = run(tree)
            caught = code != 0
            ok += caught
            print(f"  {'✅ 잡음' if caught else '❌ 통과시킴'}  {name}   ({origin})")
            if not caught: print(f"      → {out.strip()[:80]}")
    print(f"\n변이 {len(MUT)}건 중 {ok}건 검출  ({ok*100//len(MUT)}%)")
    return 0 if ok == len(MUT) else 1

sys.exit(main())
