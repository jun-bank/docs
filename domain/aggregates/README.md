# 애그리게이트 명세

- 작성일: 2026-08-03
- 상태: 검토대기 — **10종 전부 작성** (DC-001로 미수 추가)
- 양식: `study/project-workflow/phase2/04-aggregate-format.md`
- 입력: `domain/event-storming.md` ⑦ · `domain/context-map.md` §4 데이터 소유권

---

## 목록

| 애그리게이트 | 컨텍스트 | 경계 | 문서 | 상태 |
|---|---|---|---|---|
| **계좌** `Account` | C1 뱅킹 | 실시간 | [account.md](account.md) | ✅ |
| **미수** `Receivable` | C1 뱅킹 | 실시간 · 배치 | [receivable.md](receivable.md) | ✅ **DC-001** |
| **카드** `Card` | C2 카드 | 실시간 | [card.md](card.md) | ✅ |
| **승인** `Authorization` | C3 결제 | 실시간 | [authorization.md](authorization.md) | ✅ |
| **취소 예약** `ReversalTombstone` | C3 결제 | 실시간 | [reversal-tombstone.md](reversal-tombstone.md) | ✅ |
| **멱등 레코드** `IdempotencyRecord` | C3 결제 | 실시간 | [idempotency-record.md](idempotency-record.md) | ✅ |
| **매입 배치** `CaptureBatch` | C3 결제 | 배치 | [capture-batch.md](capture-batch.md) | ✅ |
| **정산** `Settlement` | C4 정산 | 배치 | [settlement.md](settlement.md) | ✅ |
| **전표** `JournalEntry` | C5 원장 | 배치 | [journal-entry.md](journal-entry.md) | ✅ |
| **불일치** `Discrepancy` | C6 대사 | 배치 | [discrepancy.md](discrepancy.md) | ✅ |

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

| # | 무엇을 한 트랜잭션으로 | 참여자 (기계 판독) | 왜 |
|---|---|---|---|
| **E1** | 승인의 **성립·해제·복원** — **계좌·카드·승인**(성립 시 멱등 포함) | `Authorization` `Account` `Card` `IdempotencyRecord` `ReversalTombstone` | 홀딩·한도·승인번호·멱등이 따로 커밋되면 초과 승인과 이중 처리가 난다. **해제·복원도 포함해야** `holdTotal`·`usage` 등식(BR-04·05)이 어긋나는 구간 없이 성립한다 — 망취소·승인취소·만료가 전부 여기 든다 |
| **E2** | 매입 레코드 반영 — **승인·계좌·카드·매입 배치·(부족 시) 미수** | `Authorization` `Account` `Card` `CaptureBatch` `Receivable` | *격리에 있다 = 미반영, 처리에 있다 = 반영됨*이 성립하려면 **자금 이동과 집합 갱신이 같은 커밋**이어야 한다. 갈리면 그 사이의 프로세스 종료가 **이중 출금 창구**가 된다. **부족분의 `Receivable.incur(CAPTURE, 승인ID, …)`도 같은 커밋** — 빠지면 출금은 됐는데 채권이 없다. **카드도 참여자다** — 부분 매입의 한도 복원(BR-24)이 여기서 일어나므로 빠지면 `usage` 등식이 깨진다 |
| **E3** | 미수 회수 — **계좌 + 회수 대상 미수들** | `Account` `Receivable` | 회수 대상을 고르고(보류 제외) 그 합으로 회수액을 정한 뒤 각 미수를 갱신하는 것이 **한 커밋**이어야 한다. 갈리면 회수액과 실제 회수 합계가 어긋나 **환불 반환액이 틀어진다**(BR-34·43) |
| **E4** | 환불 — **승인 + 그 승인의 미수 + 계좌 + 반환액 회수 대상 미수들** | `Authorization` `Account` `Receivable` `CaptureBatch` | 잔여 채무가 줄면 미수가 그만큼 **소멸**하고, 반환액이 **계좌로 입금**된다(BR-43 ①). 갈리면 ① *채무는 줄었는데 채권은 남은* 구간 ② **커밋 후 입금 전 종료 시 장부상 반환·실제 잔액 0** — 재시도는 INV-7이 막아 **고객 돈이 영구 증발** ③ 반환액이 회수할 **다른 미수가 빠지면** 그 금액이 잔액에도 없고 채권도 안 줄어 **증발**하거나, 재시도 시 **이중 회수**된다 |
| **E5** | 입금 정정 — **계좌 + 미수** | `Account` `Receivable` `IdempotencyRecord` | 착오 입금을 되돌릴 때 잔액이 부족하면 부족분이 **채권**이 된다(BR-38·20). 갈리면 ① 계좌만 커밋 후 종료 시 **고객은 썼는데 채권이 0** ② 역순 실패 시 잔액이 남은 채 채권도 생겨 **이중 청구** |

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

| 조작 | 소유 | 참여 경계 | 비고 |
|---|---|---|---|
| `hold` | 계좌 `Account` | E1 |  |
| `releaseHold` | 계좌 `Account` | E1 |  |
| `capture` | 계좌 `Account` | E2 | 부족분 `Receivable.incur` 포함 |
| `deposit` | 계좌 `Account` | E3 |  |
| `refund` | 계좌 `Account` | E4 | 반환액 입금 — FIFO 회수 포함 |
| `useAccountLimit` | 계좌 `Account` | E1 |  |
| `restoreAccountLimit` | 계좌 `Account` | E1 |  |
| `liftReceivableBlock` | 계좌 `Account` | — |  |
| `reverseDeposit` | 계좌 `Account` | E5 | 부족분 채권 + 정정 멱등 |
| `incur` | 미수 `Receivable` | E2 E5 |  |
| `recover` | 미수 `Receivable` | E3 E4 | E4 = 반환액이 회수하는 다른 미수 |
| `writeOff` | 미수 `Receivable` | E4 |  |
| `freeze` | 미수 `Receivable` | — |  |
| `unfreeze` | 미수 `Receivable` | — |  |
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
| `markSettled` | 승인 `Authorization` | — |  |
| `record` | 취소 예약 `ReversalTombstone` | — |  |
| `consume` | 취소 예약 `ReversalTombstone` | E1 |  |
| `purge` | 취소 예약 `ReversalTombstone` | — |  |
| `expire` | 취소 예약 `ReversalTombstone` | — |  |
| `find` | 멱등 레코드 `IdempotencyRecord` | 조회 |  |
| `record` | 멱등 레코드 `IdempotencyRecord` | E1 E5 | E5 = 입금 정정 재호출 차단 |
| `assertSameRequest` | 멱등 레코드 `IdempotencyRecord` | 조회 |  |
| `expire` | 멱등 레코드 `IdempotencyRecord` | — |  |
| `receive` | 매입 배치 `CaptureBatch` | — |  |
| `start` | 매입 배치 `CaptureBatch` | — |  |
| `markProcessed` | 매입 배치 `CaptureBatch` | E2 E4 | E4 = 매입 파일의 **취소 레코드** |
| `isolate` | 매입 배치 `CaptureBatch` | 별도 | 불일치 적재는 Outbox (BR-40과 같은 이유) |
| `interrupt` | 매입 배치 `CaptureBatch` | — |  |
| `complete` | 매입 배치 `CaptureBatch` | — |  |
| `promoteIsolated` | 매입 배치 `CaptureBatch` | — |  |
| `close` | 정산 `Settlement` | — |  |
| `calculate` | 정산 `Settlement` | — |  |
| `fail` | 정산 `Settlement` | — |  |
| `retry` | 정산 `Settlement` | — |  |
| `escalate` | 정산 `Settlement` | — |  |
| `resumeByOperator` | 정산 `Settlement` | — |  |
| `post` | 전표 `JournalEntry` | 별도 | BR-40 — 원장은 별도 논리 단위 |
| `reverse` | 전표 `JournalEntry` | 별도 | BR-40 |
| `recordOrTouch` | 불일치 `Discrepancy` | 별도 | 탐지 배치·격리가 Outbox로 넘긴다 |
| `investigate` | 불일치 `Discrepancy` | — |  |
| `resolve` | 불일치 `Discrepancy` | — |  |

### 무엇이 검사되는가

`tools/check_docs.py` 가 확인한다:

| # | 검사 | 이것이 잡는 결함 |
|---|---|---|
| ① | 대장의 행 집합 **==** 각 문서 §5 조작 전집 (양방향 차집합 0) | 조작이 표에서 통째로 빠짐 |
| ② | 모든 **변경** 조작에 경계가 배정돼 있다 | 판정을 미룬 채 넘어감 |
| ③ | 각 경계의 **참여자 목록 == 그 경계가 붙은 행들의 소유 집합** | **참여자를 빠뜨림** — 네 라운드 연속 결함 |
| ④ | 대장이 참조하는 경계가 경계 표에 실재 | 없는 경계 참조 |
| ⑤ | 부수 효과 열의 `〃` · 폐기·이동된 심볼 | 복사가 만든 결함 · 재분류 잔재 |

> ★ **③이 핵심이다.** E4 참여자에 `CaptureBatch`를 적으면 **배치 조작 중 하나가 E4를 달아야만** 통과한다.
> 반대로 `markProcessed`에 E4를 달았는데 **E4 참여자에 배치가 없으면** 실패한다.
> **두 곳이 독립적으로 쓰이고 서로를 강제한다** — 한쪽만 고치는 실패가 여기서 막힌다.

### 락 순서 (교착 방지)

여러 애그리게이트를 잠그는 경계는 **항상 같은 순서**로 획득한다.

```
① 미수  — (incurredBusinessDate, receivableId) 전순서
② 승인  — authorizationId
③ 계좌  — accountId
④ 카드  — cardId
⑤ 배치·멱등·정산
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
