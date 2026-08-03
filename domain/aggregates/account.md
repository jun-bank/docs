# 애그리게이트: 계좌

- 작성일: 2026-08-03
- 상태: 검토대기
- 소속 컨텍스트: **C1 뱅킹**
- 코드명: `Account`

---

## 1. 책임

> **고객의 자금을 보관하고, 지금 쓸 수 있는 금액(가용잔액)을 정확히 유지한다.**

계좌는 **자금의 현재 상태**를 소유한다. "무슨 일이 있었는가"는 원장(C5)이, "왜 묶여 있는가"는 승인(C3)이 안다.

**책임지지 않는 것**:
- 전표·회계 기록 → C5 원장
- 어느 승인이 얼마를 묶었는지 → C3 결제 (계좌는 **합계만** 안다)
- 카드별 한도 → C2 카드

---

## 2. 구성

### 애그리게이트 루트

| 이름 | 코드명 | 식별자 |
|---|---|---|
| 계좌 | `Account` | `AccountId` |

### 값 객체

| 이름 | 코드명 | 담는 값 | 자체 규칙 |
|---|---|---|---|
| 금액 | `Money` | 통화 + 최소단위 정수 | 부동소수 금지, 통화 불일치 연산 금지 (BR-07) |
| 계좌번호 | `AccountNumber` | 형식 검증된 번호 | 생성 시 형식 검증 |

### 상태 필드

| 필드 | 타입 | 뜻 |
|---|---|---|
| `balance` | `Money` | **계좌잔액** — 확정된 자금 |
| `holdTotal` | `Money` | **홀딩 합계** — 승인으로 점유된 금액의 총합 |
| `receivable` | `Money` | **미수** — 회수하지 못한 금액 (BR-20) |
| `receivableBlockLifted` | `boolean` | 운영자가 미수 차단을 해제했는가 (BR-45) |
| `dailyLimit` | `Money` | **계좌 1일 한도** — 이 계좌의 모든 카드 사용액 합계에 적용 (BR-44) |
| `dailyUsage` | `LimitUsage` | 계좌 단위 달력일 누적 사용액 (BR-44) |

> **홀딩을 목록이 아니라 합계로 든다.** 목록을 들면 계좌 애그리게이트가 승인 수만큼 커진다. 개별 홀딩의 존재는 승인(C3)이 소유한다 — 이중 해제는 승인 상태가 막는다.

### 다른 애그리게이트 참조

| 참조 대상 | 참조 방식 | 왜 참조하는가 |
|---|---|---|
| 회원 | `CustomerId` | 소유자 식별 (C7 인증이 소유) |

---

## 3. 불변식 (INV) ★

| # | 불변식 | 근거 | 위반 시 | 검증 위치 |
|---|---|---|---|---|
| **INV-1** | `balance ≥ 0` | BR-20 | 없는 돈이 나간 상태 | 모든 조작 후 |
| **INV-2** | `holdTotal ≥ 0` | — | 음수 점유는 무의미 | 모든 조작 후 |
| **INV-3** | `receivable ≥ 0` | BR-20 | 음수 미수는 무의미 | 모든 조작 후 |
| **INV-4** | **`balance > 0` 이면 `receivable = 0`** | BR-34 | 미수가 있는데 잔액이 남아 있음 = 상계가 안 됨 | 자금 유입 후 |
| **INV-5** | `receivable = 0` 이면 `receivableBlockLifted = false` | BR-45 | 미수가 없는데 차단 해제 플래그가 남음 | 상계 후 |
| **INV-6** | `dailyUsage.amount ≤ dailyLimit` | BR-44 | 계좌 한도 초과 | `useAccountLimit()` 후 |

### 불변식이 **아닌** 것 — 사전조건이다

| # | 조건 | 왜 불변식이 아닌가 |
|---|---|---|
| **PRE-1** | `hold()` 시 `요청액 ≤ 가용잔액` | 가용잔액(= `balance − holdTotal`)이 **일시적으로 음수가 될 수 있다.** 입금 역분개(BR-38)로 잔액이 줄었는데 홀딩이 남아 있는 경우다. 이때 **신규 승인만 막으면 되고**, 기존 홀딩을 강제 해제할 이유는 없다 |
| **PRE-2** | `hold()` 시 `receivable = 0` 또는 `receivableBlockLifted = true` (BR-45) | 미수는 **정상적으로 존재할 수 있는 상태**다. 불변식으로 두면 미수가 생기는 순간 계좌가 무효가 된다 |
| **PRE-3** | `useAccountLimit()` 시 `dailyUsage + 요청액 ≤ dailyLimit` (BR-44) | 한도를 낮추면 기존 사용액이 새 한도를 넘을 수 있다 (BR-46). 그때 계좌가 무효가 되면 안 된다 |

> ⚠️ **"가용잔액 ≥ 0"을 불변식으로 두면 BR-38(입금 역분개)이 불가능해진다.** 잔액을 되돌리려는데 애그리게이트가 거부하기 때문이다. **불변식과 사전조건을 구분하지 않으면 정상 경로가 막힌다.**

---

## 4. 파생 값

| 이름 | 계산 | 근거 |
|---|---|---|
| **가용잔액** `availableBalance()` | `balance − holdTotal` | BR-04 |

> 저장하지 않고 **매번 계산**한다. 저장하면 세 값이 어긋날 수 있다.

---

## 5. 조작

| 조작 | 코드명 | 사전조건 | 사후조건 | 발행 이벤트 |
|---|---|---|---|---|
| **홀딩 점유** | `hold(amount)` | `amount ≤ availableBalance()` (PRE-1) | `holdTotal` 증가. `balance` 불변 | `HoldPlaced` |
| **홀딩 해제** | `releaseHold(amount)` | `amount ≤ holdTotal` | `holdTotal` 감소 | `HoldReleased` |
| **매입 출금** | `capture(captureAmount, heldAmount)` | `heldAmount ≤ holdTotal` | `holdTotal` **전액 해제**, `balance` 감소. 부족하면 `receivable` 증가 | `Withdrawn` 또는 `ReceivableIncurred` |
| **입금** | `deposit(amount)` | `amount > 0` | 미수 우선 상계 후 잔여분만 `balance` 증가 | `Deposited` · `ReceivableOffset` |
| **환불 입금** | `refund(amount)` | `amount > 0` | **입금과 동일하게 미수 우선 상계** (BR-34) | `Refunded` · `ReceivableOffset` |
| **계좌 한도 사용** | `useAccountLimit(amount, at)` | PRE-3 | `dailyUsage` 증가 (기준일 리셋 포함) | `AccountLimitUsed` |
| **계좌 한도 복원** | `restoreAccountLimit(amount, at)` | 같은 기준일 | `dailyUsage` 감소 | `AccountLimitRestored` |
| **미수 차단 해제** | `liftReceivableBlock(operator)` | `receivable > 0` | `receivableBlockLifted = true` | `ReceivableBlockLifted` |
| **입금 정정** | `reverseDeposit(amount)` | — | `balance` 감소. 부족분은 `receivable` | `DepositReversed` |

### 조작 상세 — `capture()` (BR-18 + BR-20)

```
입력: 매입액(captureAmount), 이 승인이 잡고 있던 홀딩액(heldAmount)

1) holdTotal -= heldAmount           ← 전액 해제 (부분 매입도 잔여분까지, BR-18)
2) if balance >= captureAmount:
       balance -= captureAmount
   else:
       receivable += (captureAmount - balance)
       balance = 0                    ← 음수가 되지 않는다 (INV-1)
```

> **홀딩 해제와 출금이 한 조작이다.** 나누면 그 사이에 가용잔액이 이중 차감된 상태가 노출된다.

### 조작 상세 — `deposit()` (BR-34)

```
1) if receivable > 0:
       상계액 = min(amount, receivable)
       receivable -= 상계액
       amount -= 상계액
2) balance += amount                 ← 남은 것만
```

> 입금액이 미수보다 적으면 **잔액은 늘지 않고 미수만 감소**한다 (INV-4).
> **`refund()`도 같은 절차를 쓴다** (BR-34) — 계좌로 들어오는 돈은 출처와 무관하게 채권 회수의 재원이다. 다만 상계 사실이 **조회에 표시**되어야 한다(BR-31 확장 대상).
> **미수가 전액 상계되면 `receivableBlockLifted`를 false로 되돌린다** (INV-5) — 차단이 자동 해제된다.

---

## 6. 발행 이벤트

| 이벤트 | 코드명 | 언제 | 담는 정보 | 구독자 |
|---|---|---|---|---|
| 홀딩 점유됨 | `HoldPlaced` | `hold()` 성공 | 계좌ID, 금액 | — (같은 트랜잭션) |
| 홀딩 해제됨 | `HoldReleased` | `releaseHold()` | 계좌ID, 금액 | — |
| 출금됨 | `Withdrawn` | `capture()` | 계좌ID, 금액, 영업일 | **C5 원장** |
| 입금됨 | `Deposited` | `deposit()` | 계좌ID, 금액, 입금식별자, 영업일 | **C5 원장** |
| 미수 발생 | `ReceivableIncurred` | 잔액 부족 매입 | 계좌ID, 부족액 | **C5 원장** · 운영자 |
| 미수 상계됨 | `ReceivableOffset` | 입금 시 상계 | 계좌ID, 상계액 | **C5 원장** |
| 환불 입금됨 | `Refunded` | `refund()` | 계좌ID, 금액, 원거래 | **C5 원장** |
| 입금 정정됨 | `DepositReversed` | `reverseDeposit()` | 계좌ID, 금액, 사유 | **C5 원장** |

> 원장은 이 이벤트를 **전표 언어로 번역**한다 (컨텍스트 맵 R6, ACL).

---

## 7. 경계 근거

| 질문 | 답 |
|---|---|
| **왜 이 범위인가** | 가용잔액 판단(BR-04)이 `balance`와 `holdTotal`을 **함께** 요구한다. 미수는 잔액과 함께 움직인다(BR-34) |
| **왜 더 크지 않은가** | 카드 한도를 넣으면 **한 계좌에 카드가 여러 장(1:N)** 일 때 계좌가 카드별 한도를 떠안는다. 승인 상태를 넣으면 승인 수만큼 커진다 |
| **왜 더 작지 않은가** | `holdTotal`을 빼면 가용잔액을 계좌 안에서 판단할 수 없어 **불변식이 밖으로 샌다.** 미수를 빼면 BR-34 상계가 두 애그리게이트에 걸친다 |
| **트랜잭션 단위인가** | 원칙상 예. **단 승인 성립 시에는 카드·승인과 한 트랜잭션** (README 의식적 예외) |

---

## 8. 동시성

| 상황 | 처리 |
|---|---|
| 같은 계좌에 동시 승인 | **계좌 단위 낙관적 락**(버전) + 충돌 시 재시도. 카드가 여러 장이어도 경합은 계좌 단위 |
| 승인과 매입 배치의 경합 | 매입이 우선 확정(BR-26 C5), 취소는 매입취소로 강등 |
| 입금과 매입의 동시 도착 | 순서 무관 — `deposit()`과 `capture()`는 교환적이다 (둘 다 잔액 증감) |

> ⚠️ **`hold()`는 교환적이지 않다.** 읽고-판단하고-쓰는 사이에 다른 홀딩이 끼어들면 초과 승인이 난다. 반드시 낙관적 락 또는 직렬화가 필요하다 (QS-02).

---

## 9. 미해결

| # | 의문 | 영향 |
|---|---|---|
| ~~AC1~~ | 미수 계좌의 신규 승인 | **거절한다. 운영자가 계좌 단위로 차단 해제 가능. 전액 상계 시 자동 해제** → BR-45, PRE-2, INV-5 |
| ~~AC2~~ | 환불 입금의 미수 상계 | **상계한다.** 계좌로 들어오는 돈은 출처와 무관 → BR-34 확장 |

**(현재 미해결 없음)**

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.1 | 2026-08-03 | AC1·AC2 확정 반영 — 미수 차단(BR-45)·계좌 한도(BR-44)·환불 상계(BR-34 확장). 불변식 6종, 사전조건 3종, 조작 9종 |
| v1.0 | 2026-08-03 | 최초 작성 — 불변식 4종, 사전조건 1종(가용잔액을 불변식이 아닌 사전조건으로 구분), 조작 6종, 이벤트 8종 |
