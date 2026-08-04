"""조작 대장을 문서에서 생성한다. 행을 손으로 쓰지 않는다."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import docs_model as d

# 경계 배정 — 여기만 사람이 판단한다. 행 자체는 문서에서 온다.
# 배정되지 않은 변경 조작은 생성 시 오류로 드러난다(빈 칸 = 결함).
ASSIGN = {
 "Account.hold":"E1","Account.releaseHold":"E1","Account.useAccountLimit":"E1",
 "Account.restoreAccountLimit":"E1","Account.capture":"E2","Account.deposit":"E3",
 "Account.refund":"E4","Account.reverseDeposit":"E5","Account.liftReceivableBlock":"—",
 "Receivable.incur":"E2 E5","Receivable.recover":"E3 E4","Receivable.writeOff":"E4",
 "Receivable.freeze":"—","Receivable.unfreeze":"—",
 "Card.assertUsable":"조회","Card.useLimit":"E1","Card.restoreLimit":"E1 E2",
 "Card.suspend":"—","Card.resume":"—","Card.terminate":"—","Card.changeLimit":"—",
 "Authorization.authorize":"E1","Authorization.createVoidedByTombstone":"E1",
 "Authorization.decline":"E1","Authorization.reverse":"E1","Authorization.void":"E1",
 "Authorization.expire":"E1","Authorization.capture":"E2","Authorization.refund":"E4",
 "Authorization.freeze":"—","Authorization.unfreeze":"—","Authorization.markSettled":"별도",
 "ReversalTombstone.record":"—","ReversalTombstone.consume":"E1",
 "ReversalTombstone.purge":"—","ReversalTombstone.expire":"—",
 "IdempotencyRecord.find":"조회","IdempotencyRecord.record":"E1 E5",
 "IdempotencyRecord.assertSameRequest":"조회","IdempotencyRecord.expire":"—",
 "CaptureBatch.receive":"—","CaptureBatch.start":"—","CaptureBatch.markProcessed":"E2 E4",
 "CaptureBatch.isolate":"—","CaptureBatch.interrupt":"—","CaptureBatch.complete":"—",
 "CaptureBatch.promoteIsolated":"E2",
 "Settlement.close":"—","Settlement.calculate":"—","Settlement.fail":"—",
 "Settlement.retry":"—","Settlement.escalate":"—","Settlement.resumeByOperator":"—",
 "JournalEntry.post":"별도","JournalEntry.reverse":"별도",
 "Discrepancy.recordOrTouch":"별도","Discrepancy.investigate":"—","Discrepancy.resolve":"—",
}
NOTE = {
 "Account.capture":"부족분 `Receivable.incur` 포함",
 "Account.refund":"반환액 입금 — FIFO 회수 포함",
 "Account.reverseDeposit":"부족분 채권 + 정정 멱등",
 "Card.restoreLimit":"E2 = 부분 매입 한도 복원 (BR-24)",
 "Authorization.createVoidedByTombstone":"예약을 **소비**한다",
 "Authorization.refund":"소멸 먼저 → 계좌 입금",
 "CaptureBatch.markProcessed":"E4 = 매입 파일의 **취소 레코드**",
 "Receivable.recover":"E4 = 반환액이 회수하는 다른 미수",
 "IdempotencyRecord.record":"E5 = 입금 정정 재호출 차단",
 "CaptureBatch.isolate":"배치만 변경 — 불일치 적재는 Outbox (BR-40)",
 "CaptureBatch.promoteIsolated":"★ 재처리 경로의 멱등 — 자금 반영과 같은 커밋",
 "Authorization.markSettled":"정산 완료 후 별도 논리 단위 (BR-40)",
 "JournalEntry.post":"BR-40 — 원장은 별도 논리 단위",
 "JournalEntry.reverse":"BR-40",
 "Discrepancy.recordOrTouch":"탐지 배치·격리가 Outbox로 넘긴다",
}

def build():
    idx = d.aggregate_index()
    lines = ["| 조작 | 소유 | 참여 경계 | 비고 |", "|---|---|---|---|"]
    missing = []
    for code, (ko, f) in idx.items():
        for op in d.operations(d.AGG / f):
            key = f"{code}.{op}"
            b = ASSIGN.get(key)
            if b is None: missing.append(key); b = "**미배정**"
            lines.append(f"| `{op}` | {ko} `{code}` | {b} | {NOTE.get(key,'')} |")
    if missing:
        sys.stderr.write("미배정 조작:\n  " + "\n  ".join(missing) + "\n")
    return "\n".join(lines), missing

if __name__ == "__main__":
    t, m = build(); print(t); sys.exit(1 if m else 0)
