# 애그리게이트 명세

- 작성일: 2026-08-03
- 상태: **Phase 2 종료 후 Phase 3·4 반영** — 15종 (★ 2026-08-06 C7 명세로 조직·운영자·권한 부여·회원 4종 편입) (DC-001 미수 · R8 입금 수신 · ~~ADR-006 마감 스냅샷~~ **ADR-011·DC-005로 폐기 — 계좌가 영업일별 이동 행을 든다** — 구 표현: `closedBalance`를 직접 든다**). 인계: [`../handoff-to-phase3.md`](../handoff-to-phase3.md)
- 양식: `study/project-workflow/phase2/04-aggregate-format.md`
- ★ **2026-08-06 C7 리뷰 루프 1 반영 — L1-23**: 조작 대장의 경계 기호에 **`C7`**(C7 내부 원자 경계) 등재 · `OrgUnit.create`·`close`를 `—` → **`C7`** 로 정정(루트 `treeVersion` 갱신 + 부모 행 잠금) — 대장은 `tools/gen_matrix.py`에서 **재생성**했고 검사 ⑧이 이 토큰을 E와 같은 자격으로 읽는다. `operator.md` **OP1** · `role-grant.md` **RG1** 닫힘
- ★ **2026-08-06 R-06 기관 축 전파 일소**: §트랜잭션 경계 **E5** 서술의 정정 멱등 키 = `(기관, reversalId, 정정)` — `reversalId`는 **우리 채번**이라 기관 = **자행 고정**(입금 `depositId`는 입금원 채번이라 갈린다. `deposit-receipt.md` INV-1)
- 입력: `domain/event-storming.md` ⑦ · `domain/context-map.md` §4 데이터 소유권

---

## 목록

| 애그리게이트 | 컨텍스트 | 경계 | 문서 | 상태 |
|---|---|---|---|---|
| **계좌** `Account` | C1 뱅킹 | 실시간 | [account.md](account.md) | ✅ |
| **미수** `Receivable` | C1 뱅킹 | 실시간 · 배치 | [receivable.md](receivable.md) | ✅ **DC-001** |
| **입금 수신** `DepositReceipt` | C1 뱅킹 | 실시간 | [deposit-receipt.md](deposit-receipt.md) | ✅ **R8** |
| **카드** `Card` | C2 카드 | 실시간 | [card.md](card.md) | ✅ |
| **승인** `Authorization` | C3 결제 | 실시간 | [authorization.md](authorization.md) | ✅ |
| **취소 예약** `ReversalTombstone` | C3 결제 | 실시간 | [reversal-tombstone.md](reversal-tombstone.md) | ✅ |
| **멱등 레코드** `IdempotencyRecord` | C3 결제 | 실시간 | [idempotency-record.md](idempotency-record.md) | ✅ |
| **매입 배치** `CaptureBatch` | C3 결제 | 배치 | [capture-batch.md](capture-batch.md) | ✅ |
| **정산** `Settlement` | C4 정산 | 배치 | [settlement.md](settlement.md) | ✅ |
| **전표** `JournalEntry` | C5 원장 | 배치 | [journal-entry.md](journal-entry.md) | ✅ |
| **불일치** `Discrepancy` | C6 대사 | 배치 | [discrepancy.md](discrepancy.md) | ✅ |
| ★ **조직** `OrgUnit` | C7 인증 | 관리 | [org-unit.md](org-unit.md) | ✅ (2026-08-06 C7 명세) |
| ★ **운영자** `Operator` | C7 인증 | 관리 | [operator.md](operator.md) | ✅ 〃 |
| ★ **권한 부여** `RoleGrant` | C7 인증 | 관리 | [role-grant.md](role-grant.md) | ✅ 〃 |
| ★ **회원** `Member` | C7 인증 | 관리 | [member.md](member.md) | ✅ 〃 |

---

## 공통 규칙

### 참조는 ID로만 한다

애그리게이트 간 참조는 **식별자만** 쓴다. 객체 참조를 두면 로딩 범위가 경계를 넘고, 남의 애그리게이트를 바꿀 수 있게 된다.

```java
private AccountId accountId;   // ✅
private Account account;       // ❌
```

### 트랜잭션 경계

**원칙**: 하나의 트랜잭션은 하나의 애그리게이트만 변경한다.

**의식적 예외 5건** — 근거는 `event-storming.md` ⑦ *한 요청이 여러 트랜잭션 경계를 넘지 않게 한다*.

| # | 무엇을 한 트랜잭션으로 | 참여자 (기계 판독) | **참여 조작** (기계 판독) | 왜 |
|---|---|---|---|---|
| **E1** | 승인의 **성립·해제·복원** — **계좌·카드·승인**(성립 시 멱등 포함, **예약 무효 시 취소 예약 소비**) | `Authorization` `Account` `Card` `IdempotencyRecord` `ReversalTombstone` | `Account.hold` `Account.releaseHold` `Account.restoreAccountLimit` `Account.useAccountLimit` `Authorization.authorize` `Authorization.createVoidedByTombstone` `Authorization.decline` `Authorization.expire` `Authorization.reverse` `Authorization.void` `Card.restoreLimit` `Card.useLimit` `IdempotencyRecord.record` `ReversalTombstone.consume` | 홀딩·한도·승인번호·멱등이 따로 커밋되면 초과 승인과 이중 처리가 난다. **해제·복원도 포함해야** `holdTotal`·`usage` 등식(BR-04·05)이 어긋나는 구간 없이 성립한다 — 망취소·승인취소·만료가 전부 여기 든다. ★ **예약 소비도 같은 커밋** — `createVoidedByTombstone`이 무효 승인을 만들고 예약을 안 지우면, 같은 예약이 **다음 승인도 무효로 만든다** |
| **E2** | 매입 레코드 반영 — **승인·계좌·카드·매입 배치·(부족 시) 미수** | `Authorization` `Account` `Card` `CaptureBatch` `Receivable` | `Account.capture` `Account.restoreAccountLimit` `Authorization.capture` `CaptureBatch.markProcessed` `CaptureBatch.promoteIsolated` `Card.restoreLimit` `Receivable.incur` | *격리에 있다 = 미반영, 처리에 있다 = 반영됨*이 성립하려면 **자금 이동과 집합 갱신이 같은 커밋**이어야 한다. 갈리면 그 사이의 프로세스 종료가 **이중 출금 창구**가 된다. **부족분의 `Receivable.incur(CAPTURE, 승인ID, …)`도 같은 커밋** — 빠지면 출금은 됐는데 채권이 없다. **카드도 참여자다** — 부분 매입의 한도 복원(BR-24)이 여기서 일어나므로 빠지면 `usage` 등식이 깨진다 |
| **E3** | 미수 회수 — **계좌 + 회수 대상 미수들 + 입금 수신** | `Account` `Receivable` `DepositReceipt` | `Account.deposit` `DepositReceipt.record` `Receivable.recover` | 회수 대상을 고르고(보류 제외) 그 합으로 회수액을 정한 뒤 각 미수를 갱신하는 것이 **한 커밋**이어야 한다. ★ **입금 수신 기록도 같은 커밋** — 반영 후 기록 전 종료 시 **재수신이 또 반영되어 잔액이 2배**가 된다 (BR-29). 갈리면 회수액과 실제 회수 합계가 어긋나 **환불 반환액이 틀어진다**(BR-34·43) |
| **E4** | 환불 — **승인 + 그 승인의 미수 + 계좌 + 반환액 회수 대상 미수들 + (매입 파일 경로면) 매입 배치** | `Authorization` `Account` `Receivable` `CaptureBatch` | `Account.refund` `Authorization.refund` `CaptureBatch.markProcessed` `Receivable.recover` `Receivable.writeOff` | 잔여 채무가 줄면 미수가 그만큼 **소멸**하고, 반환액이 **계좌로 입금**된다(BR-43 ①). 갈리면 ① *채무는 줄었는데 채권은 남은* 구간 ② **커밋 후 입금 전 종료 시 장부상 반환·실제 잔액 0** — 재시도는 INV-7이 막아 **고객 돈이 영구 증발** ③ 반환액이 회수할 **다른 미수가 빠지면** 그 금액이 잔액에도 없고 채권도 안 줄어 **증발**하거나, 재시도 시 **이중 회수**된다 ④ ★ **매입 파일의 취소 레코드로 들어온 환불이면 `markProcessed()`도 같은 커밋** — 환불 커밋 후 처리 표시 전에 종료되면 **같은 레코드가 재처리**된다. 부분 환불은 INV-7 상한 안에서 두 번 성공하므로 **고객에게 이중 반환**되고 정산 합계도 부푼다 |
| **E5** | 입금 정정 — **계좌 + 미수 + 입금 수신** | `Account` `Receivable` `DepositReceipt` | `Account.reverseDeposit` `DepositReceipt.record` `Receivable.incur` | 착오 입금을 되돌릴 때 잔액이 부족하면 부족분이 **채권**이 된다(BR-38·20). 갈리면 ① 계좌만 커밋 후 종료 시 **고객은 썼는데 채권이 0** ② 역순 실패 시 잔액이 남은 채 채권도 생겨 **이중 청구** ③ ★ **멱등이 없으면 같은 정정이 두 번 먹는다** — 부족분 미수의 `(origin, sourceRef)` 유일성은 **잔액이 부족할 때만** 작동한다. 잔액 20에 정정 10을 두 번 호출하면 둘 다 미수 없이 성공해 **20이 사라진다.** 소유자는 `DepositReceipt`이며 키는 ★ **`(기관, reversalId, 정정)`**(INV-1 · 2026-08-06 **R-06**) — 정정은 외부 전문이 아니라 **운영자의 역분개**이므로(BR-38) 멱등이 정정 지시에 걸리고, `reversalId`가 **우리 채번**이라 기관 = **자행 고정**이라 스코프가 자명하다(입금 `depositId`는 입금원 채번이라 갈린다) |

> **전표는 네 예외 어디에도 없다.** BR-40이 원장 기표를 별도 논리 단위로 두었으므로, 위 트랜잭션이 커밋된 뒤 **유실되지 않는 경로**(Outbox 등)로 기표된다.
>
> **이 목록에 없는 것은 예외가 아니다.** 새 예외가 필요해 보이면 먼저 경계를 다시 본다.
>
> ⚠️ **예외가 늘어나는 것 자체가 신호다.** E3·E4는 DC-001에서 미수를 분리하며 생겼고, E1·E2도 참여자가 늘었다 — 분리로 **소유는 명확해졌지만 협력은 늘었다.**
>
> ★ **그 신호가 발화했다.** `reverseDeposit`이 다섯 번째(E5)를 요구했다. 경계를 다시 본 결과: **다섯 개는 전부 "자금이 움직이는 경로"이고, 자금 이동은 원래 여러 소유자를 건드린다.** 예외 수가 아니라 **참여자를 빠뜨리는 것**이 문제였고, 그것은 위 **변경 매트릭스**로 기계 검산한다. 여섯 번째가 필요해지면 그때 경계를 다시 본다.
>
> ⚠️ **E1의 확장은 만료 배치에 영향을 준다.** 대량 건을 처리하지만 **건별로 (승인·계좌·카드) 한 트랜잭션**이면 성립한다 — 배치 전체를 한 커밋으로 묶는 것이 아니다.

### 조작 대장 ★★ — 손으로 쓰지 않는다

> **이 표는 `tools/gen_matrix.py` 가 생성한다.** 행은 각 애그리게이트 문서 §5 조작 표에서 오고,
> 사람이 판단하는 것은 **참여 경계 한 칸뿐**이다. 조작을 새로 만들면 **여기에 자동으로 나타나고**,
> 경계를 안 적으면 **`미배정`으로 떠서 생성이 실패한다.**
>
> ★ **이전 버전은 손으로 쓴 ● 격자였고, 그래서 58개 중 34개 조작이 통째로 빠져 있었다.**
> 격자는 *"빠진 것"* 을 보여주지 못한다 — 없는 행은 **빈 칸조차 만들지 않기** 때문이다.
> 같은 이유로 `freeze`·`capture`·`refund`·`expire`·`record`·`reverse`가 **애그리게이트마다 중복된 이름**인데
> 격자에는 소유자 없이 한 줄로 적혀 있었다.

**표기**: `E1`~`E5` = 그 경계 안에서 실행 · `—` = 자기 애그리게이트만 변경 · `조회` = 변경 없음
· `별도` = 커밋 뒤 유실되지 않는 경로로(BR-40)
· ★ **`C7`** = **C7 내부 원자 경계**(2026-08-06 확정) — 자금이 움직이지 않아 **E1~E5 표 밖**이지만 *"자기 애그리게이트만"* 도 아니다. `Operator.terminate`·`transfer`의 grant 회수, `RoleGrant.*`의 `authzVersion` 증가, `OrgUnit.create`·`close`의 **루트 `treeVersion` 갱신 + 부모 행 잠금**이 여기 든다. **검사 ⑧이 이 토큰을 E와 같은 자격으로 읽는다**(`check_docs.py` `REAL`) — 배정 오류가 기계로 잡힌다는 뜻이며, 그래서 `operator.md` **OP1**·`role-grant.md` **RG1**은 닫혔다(L1-23).

| 조작 | 소유 | 참여 경계 | 비고 |
|---|---|---|---|
| `hold` | 계좌 `Account` | E1 |  |
| `releaseHold` | 계좌 `Account` | E1 |  |
| `capture` | 계좌 `Account` | E2 | 부족분 `Receivable.incur` 포함 |
| `deposit` | 계좌 `Account` | E3 |  |
| `refund` | 계좌 `Account` | E4 | 반환액 입금 — FIFO 회수 포함 |
| `useAccountLimit` | 계좌 `Account` | E1 |  |
| `restoreAccountLimit` | 계좌 `Account` | E1 E2 | E2 = 부분 매입 한도 복원 (BR-24) |
| `changeDailyLimit` | 계좌 `Account` | — |  |
| `liftReceivableBlock` | 계좌 `Account` | — |  |
| `reimposeReceivableBlock` | 계좌 `Account` | — |  |
| `reverseDeposit` | 계좌 `Account` | E5 | 부족분 채권 + 정정 멱등 |
| `incur` | 미수 `Receivable` | E2 E5 |  |
| `recover` | 미수 `Receivable` | E3 E4 | E4 = 반환액이 회수하는 다른 미수 |
| `writeOff` | 미수 `Receivable` | E4 |  |
| `freeze` | 미수 `Receivable` | — |  |
| `unfreeze` | 미수 `Receivable` | — |  |
| `find` | 입금 수신 `DepositReceipt` | 조회 |  |
| `record` | 입금 수신 `DepositReceipt` | E3 E5 | ★ 입금·정정을 한 번만 반영시킨다 (BR-29) |
| `assertSameRequest` | 입금 수신 `DepositReceipt` | 조회 |  |
| `expire` | 입금 수신 `DepositReceipt` | — |  |
| `assertUsable` | 카드 `Card` | 조회 |  |
| `useLimit` | 카드 `Card` | E1 |  |
| `restoreLimit` | 카드 `Card` | E1 E2 | E2 = 부분 매입 한도 복원 (BR-24) |
| `suspend` | 카드 `Card` | — |  |
| `resume` | 카드 `Card` | — |  |
| `terminate` | 카드 `Card` | — |  |
| `changeLimit` | 카드 `Card` | — |  |
| `authorize` | 승인 `Authorization` | E1 |  |
| `createVoidedByTombstone` | 승인 `Authorization` | E1 | 예약을 **소비**한다 |
| `decline` | 승인 `Authorization` | E1 |  |
| `reverse` | 승인 `Authorization` | E1 |  |
| `void` | 승인 `Authorization` | E1 |  |
| `expire` | 승인 `Authorization` | E1 |  |
| `capture` | 승인 `Authorization` | E2 |  |
| `refund` | 승인 `Authorization` | E4 | 소멸 먼저 → 계좌 입금 |
| `freeze` | 승인 `Authorization` | — |  |
| `unfreeze` | 승인 `Authorization` | — |  |
| `markSettled` | 승인 `Authorization` | 별도 | `SettlementCompleted` 수신 — 별도 논리 단위 (BR-40) |
| `record` | 취소 예약 `ReversalTombstone` | — |  |
| `consume` | 취소 예약 `ReversalTombstone` | E1 |  |
| `purge` | 취소 예약 `ReversalTombstone` | — |  |
| `expire` | 취소 예약 `ReversalTombstone` | — |  |
| `find` | 멱등 레코드 `IdempotencyRecord` | 조회 |  |
| `record` | 멱등 레코드 `IdempotencyRecord` | E1 |  |
| `assertSameRequest` | 멱등 레코드 `IdempotencyRecord` | 조회 |  |
| `expire` | 멱등 레코드 `IdempotencyRecord` | — |  |
| `receive` | 매입 배치 `CaptureBatch` | — |  |
| `start` | 매입 배치 `CaptureBatch` | — |  |
| `markProcessed` | 매입 배치 `CaptureBatch` | E2 E4 | E4 = 매입 파일의 **취소 레코드** |
| `isolate` | 매입 배치 `CaptureBatch` | — | 배치만 변경 — 불일치 적재는 Outbox (BR-40) |
| `interrupt` | 매입 배치 `CaptureBatch` | — |  |
| `complete` | 매입 배치 `CaptureBatch` | — |  |
| `reclassifyIsolated` | 매입 배치 `CaptureBatch` | — | 배치만 변경 — 불일치 적재는 Outbox (BR-50 재분류) |
| `promoteIsolated` | 매입 배치 `CaptureBatch` | E2 | ★ 재처리 경로의 멱등 — 자금 반영과 같은 커밋 |
| `close` | 정산 `Settlement` | — |  |
| `calculate` | 정산 `Settlement` | — |  |
| `fail` | 정산 `Settlement` | — |  |
| `retry` | 정산 `Settlement` | — |  |
| `escalate` | 정산 `Settlement` | — |  |
| `resumeByOperator` | 정산 `Settlement` | — |  |
| `post` | 전표 `JournalEntry` | 별도 | 상류 이벤트(`Deposited`·`Refunded` 등)를 ACL이 번역 — BR-40 |
| `reverse` | 전표 `JournalEntry` | 별도 | 오기표 정정 — `JournalPosted` 원전표를 뒤집는다 (BR-10·47) |
| `recordOrTouch` | 불일치 `Discrepancy` | 별도 | `DiscrepancyRecorded` — 탐지 배치·격리가 Outbox로 넘긴다 |
| `investigate` | 불일치 `Discrepancy` | — |  |
| `resolve` | 불일치 `Discrepancy` | — |  |
| `create` | 조직 `OrgUnit` | C7 |  |
| `close` | 조직 `OrgUnit` | C7 |  |
| `register` | 운영자 `Operator` | — |  |
| `suspend` | 운영자 `Operator` | C7 |  |
| `resume` | 운영자 `Operator` | C7 |  |
| `terminate` | 운영자 `Operator` | C7 | ★ 전 grant 회수 동반 — 〃 |
| `transfer` | 운영자 `Operator` | C7 | ★ grant 자동 회수 동반 — C7 내부 원자 갱신(자금 무이동, E 표 밖 의식적 예외) |
| `issue` | 권한 부여 `RoleGrant` | C7 | authzVersion 증가 동반 — 〃 |
| `revoke` | 권한 부여 `RoleGrant` | C7 | 〃 |
| `recertify` | 권한 부여 `RoleGrant` | C7 | 〃 |
| `register` | 회원 `Member` | — |  |
| `deactivate` | 회원 `Member` | — |  |
| `reactivate` | 회원 `Member` | — |  |
| `requestClose` | 회원 `Member` | — |  |
| `close` | 회원 `Member` | — |  |

### 무엇이 검사되는가

`tools/check_docs.py` 가 확인한다:

| # | 검사 | 이것이 잡는 결함 |
|---|---|---|
| ① | 대장의 행 집합 **==** 각 문서 §5 조작 전집 (양방향 차집합 0) | 조작이 표에서 통째로 빠짐 |
| ② | 모든 **변경** 조작에 경계가 배정돼 있다 | 판정을 미룬 채 넘어감 |
| ③ | 각 경계의 **참여자 목록 == 그 경계가 붙은 행들의 소유 집합** | **참여자를 빠뜨림** — 네 라운드 연속 결함 |
| ③-b | 각 경계의 **참여 조작 목록 == 그 경계를 단 조작 집합** (양방향) | **오배정·과잉 배정** — ③은 소유 애그리게이트만 봐서 같은 애그리게이트의 다른 조작을 못 봤다 (R9) |
| ⑪ | `별도`인 조작은 **촉발 이벤트를 인용**하고, 이벤트를 인용하는 조작은 `별도`다 | `별도`와 `—`가 구분되지 않던 것 — R8이 고친 배정 2건이 **되돌려도 통과**했다 (R9) |
| ⑫ | **열린 의문 색인 == 각 문서의 의문 ID** (양방향 + 선언 건수) | 유령 1건과 누락 1건이 **±1로 상쇄**돼 숫자만 맞았다 (R9) |
| ⑬ | **ACL 소유 규칙 표가 모든 경계를 덮는가** | 표가 E3·E4·E5만 덮어 `Captured`가 판정 없이 남아 **매입 이중 기표** (R9 T1의 뿌리) |
| ⑭ | **등식 우변 필드 ↔ 전이 사후조건** — 홀딩·한도를 바꾸는 전이가 `heldAmount`·`limitContribution`을 적었는가 | 세 라운드 연속 "구성 요소를 안 적음". 첫 실행에 **7건** |
| ⑮ | **ACL ↔ 이벤트 payload ↔ 보조부** — ACL이 쓰는 필드가 payload에 있는가, 보조부 계정은 `accountId`를 싣는가 | 첫 실행에 **7건** — R10 치명 5 재현 + 같은 유형 6건 |
| ⑯ | **배정 커버리지 하한** — 경계 배정 중 독립 출처로 검사되는 비율 | 표 대조는 *두 표를 함께 고치면* 통과한다. 지금 **19%**(26건 중 5건) |
| ⑰ | **불일치 유형 건수는 BR-09만 선언한다** | 용어사전이 **7종**이라 적은 채 남았다 — 정본은 13종 (R10) |
| ⑱ | **③ 의식적 예외의 등식·정본·탐지가 전부 채워져 있는가** | *"등재만 하고 정본·탐지가 비어 있다"* — R7 U7 · DC-002 |
| ⑲ | **컨텍스트 ↔ 배포 단위 커버리지** — 배포 ADR이 모든 컨텍스트를 배정했는가 | C7 인증이 **어디에도 배정되지 않았다** (Phase 3 D8) |
| ⑳ | **이벤트 구독자 ↔ 컨텍스트 관계** — 이벤트가 가는 방향이 관계 표에 있는가 | ★ **역방향 경로가 맵에 없어 치명 T1·T3** (DC-004). 만들자마자 `SettlementFailed`의 C4→C6 누락을 잡았다 |
| ㉑ | **미확정 수치 표 ↔ 규칙 본문** — 본문이 확정됐는데 표에 남아 있지 않은가 | ★ **본문만 고치고 요약표를 안 고치는 형태** — 장애 사례 리서치가 이것을 **Knight Capital의 뿌리**로 지목했다 |
| ④ | 대장이 참조하는 경계가 경계 표에 실재 | 없는 경계 참조 |
| ⑤ | 부수 효과 열의 `〃` · 폐기·이동된 심볼 | 복사가 만든 결함 · 재분류 잔재 |

> ★ **③이 핵심이다.** E4 참여자에 `CaptureBatch`를 적으면 **배치 조작 중 하나가 E4를 달아야만** 통과한다.
> 반대로 `markProcessed`에 E4를 달았는데 **E4 참여자에 배치가 없으면** 실패한다.
> **두 곳이 독립적으로 쓰이고 서로를 강제한다** — 한쪽만 고치는 실패가 여기서 막힌다.

### 락 순서 (교착 방지)

> ★ **`AccountDailyMovement` 행은 계좌와 같은 자리에서 잠근다**(DC-005) — 계좌를 잡을 때 그날 행도 같이 잡는다. 별도 순서를 만들지 않는다.

여러 애그리게이트를 잠그는 경계는 **항상 같은 순서**로 획득한다.

```
① 미수  — (incurredBusinessDate, receivableId) 전순서
② 승인  — authorizationId
③ 계좌  — accountId
④ 카드  — cardId
⑤ 배치·멱등·정산·★승인요청(C8 `consume` — BR-56 ①~③이 실행 트랜잭션에 참여한다. 자금 무이동이라 E 표 밖 — 의식적 예외)
```

> **미수를 먼저 잠근다.** E3(계좌+미수들)와 E4(승인+미수들+계좌)가 **미수에서 만나므로**, 미수를 나중에 잡으면 두 경로가 서로를 기다린다. FIFO 정렬 키가 락 순서 키를 겸한다.
>
> ⚠️ **E4는 자기 미수와 회수 대상 미수를 함께 전순서로 선점**한다. 자기 미수만 먼저 잠그면 그 키가 뒤일 때 순서가 깨진다.

### 불변식과 사전조건의 구분

| | 뜻 | 언제 검사 |
|---|---|---|
| **불변식 (INV)** | 애그리게이트가 살아 있는 동안 **항상** 참 | 모든 조작 후 |
| **사전조건 (PRE)** | 특정 조작을 **호출하기 전에** 참이어야 함 | 그 조작 진입 시 |

**둘을 혼동하면 정상 경로가 막힌다.** 예: "가용잔액 ≥ 0"을 불변식으로 두면 입금 역분개(BR-38)가 불가능해진다 — 아래 `account.md` INV/PRE 구분 참조.

### 도메인 이벤트

이벤트는 **애그리게이트가 만들고 애플리케이션이 발행한다**. 이벤트명은 과거형이며 용어사전을 따른다.

### 부수 효과를 `〃`로 적지 않는다

전이·조작 표의 부수 효과 열에서 **앞 행과 같다는 뜻의 `〃`를 쓰지 않는다.** 이 프로젝트에서 `〃`가 **세 라운드 연속으로 결함을 만들었다**:

| 라운드 | 무엇을 복사했나 | 결과 |
|---|---|---|
| 1차 | 승인 T9가 T8의 "홀딩 전액 해제" | 만료로 이미 풀린 홀딩을 또 해제 → **초과 승인** (치명) |
| 3차 | 승인 T11이 T10의 "대응 미수 소멸" | 부분 환불이 미수를 전액 소멸 → **채권 손실** |

> **조건이 한 줄 다르면 부수 효과도 다르다.** 길어지더라도 매번 풀어 쓴다.

### 시간을 주입받는다

`LocalDateTime.now()`를 애그리게이트 안에서 호출하지 않는다. 시각은 인자로 받는다 — 그래야 만료·귀속일 판단을 테스트할 수 있다.
