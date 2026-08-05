#!/usr/bin/env python3
"""변이 검사 — 과거에 실제로 났던 결함을 다시 주입하고, 검산이 잡는지 본다.

★ 통과하는 검산은 "결함이 없다"를 뜻하지 않는다. "이 검산이 아무것도 안 한다"일 수도 있다.
  R7 U1이 이것을 손으로 발견했다 — "R6가 잡은 치명 3건을 되돌려도 전부 통과한다".
"""
import subprocess, sys, shutil, tempfile, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (이름, 파일, 찾을 것, 바꿀 것, 원래 잡은 라운드)
MUT = [
 ("행 누락 — 조작을 대장에서 지운다", "tools/gen_matrix.py",
  '"Receivable.writeOff":"E4",', '', "R7 U5"),
 ("경계 참여자 누락 — E4에서 배치를 뺀다", "domain/aggregates/README.md",
  "`Authorization` `Account` `Receivable` `CaptureBatch`", "`Authorization` `Account` `Receivable`", "R7 U2"),
 ("배정 오류 — promoteIsolated를 단독으로", "tools/gen_matrix.py",
  '"CaptureBatch.promoteIsolated":"E2",', '"CaptureBatch.promoteIsolated":"—",', "R8 S1"),
 ("배정 오류 — isolate를 별도로", "tools/gen_matrix.py",
  '"CaptureBatch.isolate":"—",', '"CaptureBatch.isolate":"별도",', "R8 S12"),
 ("배정 오류 — markSettled를 단독으로", "tools/gen_matrix.py",
  '"Authorization.markSettled":"별도",', '"Authorization.markSettled":"—",', "R8 S13"),
 ("변경 조작을 `조회`로 위장", "tools/gen_matrix.py",
  '"Receivable.recover":"E3 E4",', '"Receivable.recover":"조회",', "R9 Opus"),
 ("과잉 배정 — recover에 없는 E2를 더한다", "tools/gen_matrix.py",
  '"Receivable.recover":"E3 E4",', '"Receivable.recover":"E2 E3 E4",', "R9 Opus"),
 ("이동한 번호 잔재 — RC-1을 INV-10으로", "domain/aggregates/authorization.md",
  "(**RC-1** — 승인 단독으로 검증 불가)", "(INV-10)", "R7 U6"),
 ("없는 불변식 참조 — 카드 RC-1을 INV-5로", "domain/aggregates/authorization.md",
  "**카드 RC-1**", "카드 INV-5", "R8 K9"),
 ("집계 선언 불일치 — 선언 수를 1 줄인다", "product/01-business-rules.md",
  "AUTO:count", None, "R7 U8"),
 ("종수 선언 불일치 — 9종을 8종으로", "domain/state-machines/README.md",
  "상태: **9종**", "상태: **8종**", "R8 K13"),
 ("부수 효과 `〃` 주입", "domain/aggregates/receivable.md",
  None, None, "R1 C1"),
 ("기준소스의 없는 불변식 참조 — 계좌 RC-9", "product/01-business-rules.md",
  "**계좌 RC-1**", "계좌 RC-9", "R8 S17"),
 ("등식 우변 필드를 전이에서 지운다", "domain/state-machines/authorization.md",
  "홀딩 해제(**`heldAmount` → 0**) · **카드·계좌 한도** 복원(**`limitContribution` → 0**)",
  "홀딩 해제 · **카드·계좌 한도** 복원", "R10 ⑭"),
 ("ACL이 쓰는 필드를 payload에서 지운다", "domain/aggregates/receivable.md",
  "| **미수 소멸** | `ReceivableWrittenOff` | `writeOff()` | 미수ID, **`accountId`**,",
  "| **미수 소멸** | `ReceivableWrittenOff` | `writeOff()` | 미수ID,", "R10 ⑮"),
 ("역방향 관계 R11을 지운다", "domain/context-map.md",
  "AUTO:delrow:| **R11** |", None, "Phase3 T1"),
 ("배포 단위 ADR에서 컨텍스트 하나를 뺀다", "architecture/adr/ADR-010-deployment-unit-final.md",
  "C6 대사", "대사", "Phase3 D8"),
 ("정산 ③ 정본을 다시 비운다", "domain/aggregates/settlement.md",
  "★ **승인 `capturedAmount` + `settledBusinessDate`** (C3 결제)", "**미정**", "DC-002"),
 ("파생 문서가 유형 건수를 따로 선언", "domain/glossary.md",
  "유형은 **BR-09 정본 표**가 소유한다", "유형 7종은 BR-09 참조 —", "R10"),
 ("열린 의문 유령 — 색인에 없는 ID 추가", "domain/state-machines/README.md",
  "| **RCS5** |", "| **XXS9** | 미수 | 유령 |\n| **RCS5** |", "R9 M4"),
 ("ACL 소유 규칙에서 E2 행 제거", "domain/aggregates/journal-entry.md",
  "AUTO:delrow:| **E2 매입**", None, "R9 T1"),
 ("없는 규칙 참조 — BR-99", "domain/aggregates/account.md",
  "(BR-34)", "(BR-99)", "상시"),
 ("★ 폐기된 필드 부활 (DC-006)", "domain/aggregates/account.md",
  "`AccountDailyMovement[]`", "`AccountDailyClose[]`", "㉓"),
 ("★ 대체된 ADR을 정본처럼 참조", "architecture/adr/ADR-002-module-structure.md",
  "★ **ADR-010**이 **실시간 코어**", "★ **ADR-004**가 **실시간 코어**", "㉒"),
 ("★ 규칙 ID 중복 정의", "architecture/adr/ADR-013-timeout-hierarchy.md",
  "| **T-13** |", "| **T-12** |", "㉔"),
 ("★ DC 반영 완료 주장 vs 본문", "design-changes/DC-006-daily-movement.md",
  "| **P-2** | `receivable.md` |", "| **P-2** | `card.md` |", "㉕"),
 ("★ 폐기된 개념어 부활 (마감 행)", "domain/aggregates/account.md",
  "영업일별 이동 행", "영업일별 마감 행", "㉖"),
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
            if old and old.startswith("AUTO:delrow:"):   # 접두사로 행을 지운다 (앵커가 낡지 않게)
                pre = old.split(":", 2)[2]
                lines = [l for l in t.splitlines() if not l.startswith(pre)]
                if len(lines) == len(t.splitlines()):
                    print(f"  ⚠️  {name} — 지울 행이 없다 ({pre!r})"); continue
                t = "\n".join(lines) + "\n"
            elif old == "AUTO:count":               # 선언 수를 문서에서 읽어 1 줄인다
                m = re.search(r"배치 탐지 대상 (\d+)종", t)
                if not m: print(f"  ⚠️  {name} — 선언을 못 찾음"); continue
                k = int(m.group(1))
                t = t.replace(f"→ **{k}종 전부 탐지", f"→ **{k-1}종 전부 탐지", 1)
            elif old is None:                     # `〃` 주입 — 사후조건 칸
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
