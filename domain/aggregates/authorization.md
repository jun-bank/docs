# 애그리게이트: 승인

- 작성일: 2026-08-03
- 상태: 검토대기
- 소속 컨텍스트: **C3 결제**
- 코드명: `Authorization`

---

## 1. 책임

> **결제 한 건의 전 생애(승인 → 매입 → 취소·만료)를 추적하고, 각 시점에 허용되는 조작을 통제한다.**

승인은 **결제 라이프사이클의 정본**이다. 대사(BR-30)가 3자 비교를 하는 이유도 여기 있다 — 매입 전 승인은 원장에 없고 **승인 애그리게이트에만** 있다.

**책임지지 않는 것**:
- 계좌 잔액 · **홀딩 합계** — C1 뱅킹. 승인은 **자기 몫(`heldAmount`)만** 든다 — 합계는 계좌가, 건별 몫은 승인이 (BR-04 등식의 구성 요소)
- 한도 사용액 — **카드 한도는 C2 카드, 계좌 한도는 C1 뱅킹**(BR-44). 승인은 **두 층을 모두** 만족해야 성립한다
- **미수** — C1 뱅킹의 `Receivable`. 승인은 **참조만** 하며 회수·보류를 통제하지 않는다 (DC-001)
- 전표 — C5 원장

---

## 2. 구성

### 애그리게이트 루트

| 이름 | 코드명 | 식별자 |
|---|---|---|
| 승인 | `Authorization` | `AuthorizationId` |

### 값 객체

| 이름 | 코드명 | 담는 값 | 자체 규칙 |
|---|---|---|---|
| **상관 식별자** | `CorrelationId` | 매입사가 생성한 식별자 | **승인 성립 여부와 무관하게 존재** (BR-17 ①) |
| **승인번호** | `ApprovalNumber` | 발급사가 발번 | 승인 성립 시에만 존재 (BR-17 ②) |
| 금액 | `Money` | — | BR-07 |

### 상태 필드

| 필드 | 타입 | 뜻 |
|---|---|---|
| `correlationId` | `CorrelationId` | 매입사 생성 식별자 — **망취소 매칭의 유일 수단** |
| `approvalNumber` | `ApprovalNumber?` | 승인 성립 시 발번 |
| `amount` | `Money` | 승인 금액 |
| `status` | `AuthorizationStatus` | 상태 (§4) |
| `holdingFunds` | `boolean` | **이 승인이 홀딩을 잡고 있는가** |
| **`heldAmount`** | `Money` | **이 승인이 점유 중인 홀딩액.** 계좌 `holdTotal` 등식의 구성 요소 (BR-04 · INV-6) |
| **`settledBusinessDate`** | `BusinessDate?` | ★ **정산에 반영된 영업일** — `markSettled()` 시 확정, 이후 **불변**. 정산 합계 등식의 **부분집합을 고르는 키**다 (DC-002) |
| **`limitBasisDate`** | `BusinessDate` | ★ **이 승인이 소비한 한도 버킷** — 성립 시 확정, 이후 **불변**. `at`(원장 귀속 영업일)과 다른 개념이다 (DC-003) |
| **`limitContribution`** | `Money` | **이 승인이 그 기준일 한도에서 차지하는 몫.** 한도 등식의 구성 요소 (BR-05 · **카드 RC-1**) |
| `capturedAmount` | `Money?` | 매입된 금액 (null = 미매입) |
| `withdrawnAmount` | `Money` | 매입 시 즉시 출금된 금액 (BR-20). **매입 시점 확정 후 불변** — 감사 근거 |
| `returnedTotal` | `Money` | **고객에게 실제 반환한 누계.** 환불 산식의 결과이며 **그 시점 총 회수액**(`withdrawnAmount + 미수.recoveredAmount`)을 넘지 않는다 (**RC-1** — 승인 단독으로 검증 불가) |
| `cancelledAmount` | `Money` | **매입 전** 누적 취소액 (승인취소·부분취소). 환불은 포함하지 않는다 |
| `refundedTotal` | `Money` | **매입 후** 누적 환불액 — **매입액 기준**(반환액이 아니다). INV-7의 좌변 |
| `frozen` | `boolean` | 보류 여부 (BR-28) |
| `authorizedAt` | `Instant` | 승인 성립 시각 |
| `businessDate` | `BusinessDate` | 귀속 영업일 (BR-14) |

### 다른 애그리게이트 참조

| 참조 대상 | 참조 방식 | 왜 참조하는가 |
|---|---|---|
| 카드 | `CardId` | 어느 카드의 결제인가 |
| 계좌 | `AccountId` | 어느 계좌에서 나가는가 |
| 가맹점 | `MerchantId` | 전문에 실려 온 값 (우리 고객 아님) |

---

## 3. 불변식 (INV) ★

| # | 불변식 | 근거 | 위반 시 | 검증 위치 |
|---|---|---|---|---|
| **INV-1** | `cancelledAmount ≤ amount` | BR-11 | 원결제보다 많이 환불 | 취소 조작 후 |
| **INV-7** | **`refundedTotal ≤ capturedAmount`** — 환불은 거래를 줄이는 것이므로 상한은 **매입액**이다 | BR-43 ① | **받지 않은 미수분까지 반환** — 잔액이 부풀고 미수는 남아 이후 입금을 또 상계한다 | `refund()` |
| **INV-8** | `withdrawnAmount`는 **불변**, `refundedTotal`·`returnedTotal`은 **단조 증가** | BR-43 ① | 상한이 스스로 커지거나 반환 이력이 사라진다 | `capture()` 후 · `refund()` 후 |
| **INV-9** | `cancelledAmount`와 `refundedTotal`은 **서로 섞이지 않는다** — 환불은 `cancelledAmount`를 올리지 않는다 | BR-16 ③ · BR-43 | 환불이 취소액에 들어가면 `capturedAmount ≤ amount − cancelledAmount`(INV-3)가 **매입 후에 사후 위반**된다 | `refund()` 후 |
| **INV-2** | **매입은 1회만** — `capturedAmount`가 한 번 설정되면 다시 바뀌지 않는다 | BR-16 ② | 이중 출금 | `capture()` |
| **INV-3** | `capturedAmount ≤ amount − cancelledAmount` | BR-16 ③ | **부분 취소된 만큼을 다시 매입** — 이중 청구 | `capture()` |
| **INV-4** | **매입 후에는 `holdingFunds = false`** | BR-18 | 가용잔액 이중 차감 | `capture()` 후 |
| **INV-5** | `status = 성립` 이면 `approvalNumber ≠ null` | BR-17 | 승인번호 없는 성립 승인 | 상태 전이 후 |
| **INV-6** | 종료 상태(**거절·무효·환불완료·정산완료**)에서는 상태 전이가 일어나지 않는다. **만료는 종료가 아니다** — 지연 매입(BR-19)과 만료 후 취소(BR-49)가 정상 경로다 | BR-19·49 | 죽은 거래의 부활 / 반대로 만료를 넣으면 **정상 경로가 차단** | 모든 전이 |

### 대사 불변식 — 승인 단독으로 검증 불가 ★

**미수를 함께 읽어야 참·거짓을 알 수 있다.** 양식 §4의 분류에 따라 INV와 분리한다.

| # | 명제 | 근거 | 위반 시 | 어디서 검증되나 |
|---|---|---|---|---|
| **RC-1** | **`returnedTotal ≤ withdrawnAmount + 미수.recoveredAmount`** (= 그 시점 총 회수액) | BR-43 ① | 실제로 받은 돈보다 많이 돌려준다. **상한을 `withdrawnAmount`로 고정하면 미수를 갚은 고객이 낸 만큼 못 받는다** — AU9가 기각한 모델이다 | **E4 커밋 안에서 검사** |
| **RC-2** | `refund()` 후 **회수액 ≤ 잔여 채무** (회수액 = `withdrawnAmount + 미수.recoveredAmount − returnedTotal`) | BR-43 ① | 초과 회수분이 남으면 **돌려줘야 할 돈을 안 돌려준 상태**다 | **E4 커밋 안에서 검사** |

> ⚠️ **INV로 적으면 안 된다.** 검증 위치에 *"승인 단독으로 검증 불가"* 라고 쓰면서 INV 표에 두는 것은 **"항상 참"이라 선언하고 아무도 검사하지 않는** 상태다 (양식 §4). E4가 승인·미수를 함께 잠그므로 **그 커밋 안에서는 검사할 수 있다.**

---

## 4. 상태

> 전이 규칙과 **금지 전이**는 별도 문서로 뺀다 → `domain/state-machines/authorization.md` (Phase 2-5)

| 상태 | 코드명 | 뜻 | 종료 |
|---|---|---|---|
| 요청됨 | `REQUESTED` | 검증 중 | ✕ |
| **성립** | `AUTHORIZED` | 승인번호 발번, 홀딩 점유 | ✕ |
| 거절됨 | `DECLINED` | 검증 실패 | **✓** |
| **무효** | `VOIDED` | 망취소 또는 승인취소로 무효화 | **✓** |
| **만료** | `EXPIRED` | 기한 내 미매입 (BR-03). **채무는 남는다** | ✕ ⚠️ |
| **매입됨** | `CAPTURED` | 확정 거래로 전환 | ✕ |
| 환불됨 | `REFUNDED` | 매입 후 전액 취소 | **✓** |
| 정산완료 | `SETTLED` | 순액 지급 확정 | **✓** ⚠️ |

> ⚠️ **`SETTLED` 이후 환불이 와도 이 승인은 바뀌지 않는다.** 환불은 **별도 차감 거래**로 다음 영업일 정산에 반영된다(BR-43). 종료 상태가 맞다.
>
> ⚠️ **만료는 종료 상태가 아니다.** BR-19에 따라 만료 후에도 매입이 도착할 수 있다(지연 매입). `EXPIRED → CAPTURED` 전이가 허용된다. **이것이 이 상태 머신에서 가장 반직관적인 부분이다.**

---

## 5. 조작

| 조작 | 코드명 | 사전조건 | 사후조건 | 발행 이벤트 |
|---|---|---|---|---|
| **성립** | `authorize(approvalNumber, at)` | 상태 = 요청됨, **유효한 취소 예약 없음**(존재 AND `at < expiresAt`) | 상태 = 성립, `holdingFunds = true` | `Authorized` |
| **예약 무효 생성** | `createVoidedByTombstone(at)` | **유효한 취소 예약 존재** | 상태 = 무효. **홀딩을 만들지 않고 한도도 쓰지 않는다** · 예약 소비 | `VoidedByTombstone` |
| **거절** | `decline(reason)` | 상태 = 요청됨 | 상태 = 거절됨, 사유 기록 (BR-36) | `Declined` |
| **망취소** | `reverse()` | 상태 ∈ {성립, **만료**} (멱등 — 이미 무효면 무시) | 상태 = 무효. `holdingFunds`가 참일 때만 홀딩·한도 복원 (BR-49) | `Reversed` |
| **승인취소** | `void(amount)` | 상태 ∈ {성립, **만료**}, **미매입**, INV-1 | 부분이면 `cancelledAmount` 증가, 전액이면 무효. 복원 조건은 `reverse()`와 동일 | `Voided` |
| **만료** | `expire(at)` | 상태 = 성립, **`frozen = false`** (BR-28) | 상태 = 만료, `holdingFunds = false` | `Expired` |
| **매입** | `capture(amount, at)` | INV-2·INV-3 (`amount ≤ 승인액 − 누적취소액`), 상태 ∈ {성립, 만료}, **`frozen = false`** (BR-50) | 상태 = 매입됨 · `holdingFunds = false` · `heldAmount = 0` · ★ **`at`의 영업일 = `limitBasisDate` 일 때만 한도 복원**(DC-003): 복원액 = `limitContribution` − min(매입액, `limitContribution`) 만큼 `Card.restoreLimit(복원액, limitBasisDate)` · `Account.restoreAccountLimit(복원액, limitBasisDate)` 호출 후 `limitContribution` 감액 (BR-24, E2). **기준일이 다르면 셋 다 불변** — 그 버킷은 이미 닫혔다(`usage`가 리셋됐다). 만료로 이미 복원됐으면 `limitContribution = 0`이라 복원액도 0 | `Captured` |
| **환불** | `refund(amount, receivable, recoverable)` | 상태 ∈ {**매입됨, 정산완료**}, **INV-7** | `refundedTotal` 증가 → 반환액·소멸액 파생 → **소멸 먼저, 그다음 계좌 입금(`recoverable`이 회수 대상)** → `returnedTotal` 증가. 잔여 채무 0이면 상태 = 환불됨. **승인·자기 미수·계좌·회수 대상 미수들이 한 커밋**(E4) | `Refunded` |
| **보류** | `freeze()` | 종료 상태 아님 | `frozen = true` | `Frozen` |
| **보류 해제** | `unfreeze()` | `frozen = true`. **종료 상태에서도 허용** — 보류 목록에서 내릴 유일한 경로다 | `frozen = false` | `Unfrozen` |
| **정산 확정** | `markSettled(businessDate)` | 상태 = 매입됨. **`frozen` 여부와 무관** (BR-28에 정산 제외가 없다) | 상태 = 정산완료 · ★ **`settledBusinessDate` 확정**(이후 불변 — 정산 등식의 부분집합 키, DC-002) | `Settled` |

### 조작 상세 — `capture()` 가 두 상태에서 허용되는 이유

```
AUTHORIZED → CAPTURED    정상 경로
EXPIRED    → CAPTURED    지연 매입 (BR-19) — 만료는 채무 소멸이 아니다
```

**둘 다 `holdingFunds`를 false로 만든다.** 만료 시 이미 false이므로 멱등하다.

> ⚠️ **단, 만료 후 취소가 먼저 도착했다면 상태가 `VOIDED`이므로 매입은 격리된다** (BR-49 · 충돌 C9). 만료된 승인의 결말은 **먼저 도착한 쪽이 정한다.**

### 조작 상세 — `refund()` 는 거래를 줄이고 반환액을 파생한다 (BR-43 ①)

```
입력: 환불액 = 거래를 얼마로 줄이는가 (매입액 기준) · 이 승인의 미수(없으면 null)

1) refundedTotal += 환불액                        INV-7: ≤ capturedAmount
2) 잔여 채무 = capturedAmount − refundedTotal
3) 미수회수 = (미수 ? 미수.recoveredAmount : 0)     ← 미수 없으면 0
   회수액   = withdrawnAmount + 미수회수 − returnedTotal
4) 반환액   = max(0, 회수액 − 잔여 채무)            ← 초과 회수분만
5) 미수 소멸액 = 미수 ? max(0, 미수.outstanding() − max(0, 잔여채무 − 회수액)) : 0
   if 소멸액 > 0 AND 미수.상태 = 미결:
       미수.writeOff(소멸액)                       ← ★ 반환액 입금보다 먼저
6) returnedTotal += 반환액                         RC-1: ≤ withdrawnAmount + 미수회수
   계좌.refund(반환액, recoverable)                  ← ★ 반환액 0이어도 **반드시 부른다**
                                                       recoverable 도 E4 참여자다
7) 잔여 채무 = 0 이면 상태 = 환불됨

> ★ **반환액이 0이어도 계좌를 부른다** (R10). 미수만 소멸한 환불에서 계좌를 건너뛰면
> 계좌 `INV-3`(*"미결 미수가 없으면 `receivableBlockLifted = false`"*)을 **재평가할 기회가 없다.**
> 마지막 미수가 소멸로 사라졌는데 차단 해제 플래그가 남아, BR-45의 자동 해제가 일어나지 않는다.
> `account.md`의 `refund()`도 이미 *"`amount = 0`도 정상"* 이라고 적고 있었다 — **부르는 쪽이 안 맞았다.**

── 1~7이 한 트랜잭션 (E4: 승인 + 자기 미수 + 계좌 + `recoverable` 미수들) ──
```

> ★ **5단계가 6단계보다 먼저다.** 반환액도 계좌로 들어오는 자금이라 순서를 뒤집으면 **자기 미수가 회수 대상에 들어가** `recover()`가 잔여를 줄이고, 뒤이은 `writeOff(소멸액)`이 잔여 초과로 **거절**되어 환불 전체가 롤백된다 (BR-34 예외 ②).
>
> ★ **소멸액 0 · 미수 없음 · 미수 종결은 정상 경로다.** 조건 없이 `writeOff`를 부르면 두 번째 환불에서 이미 `CLOSED`인 미수에 `writeOff(0)`이 호출되어 **VF2로 거절**된다.
>
> ★ **반환액 입금이 같은 커밋이어야 한다.** 갈리면 커밋 후 입금 전 종료 시 **장부상 반환·실제 잔액 0**이 되고, 재시도는 INV-7(`refundedTotal + 요청액 ≤ capturedAmount`)이 막아 **고객 돈이 영구 증발**한다.

| 매입 10만 · 출금 7만 · 미수 3만 | `refundedTotal` | 잔여 채무 | 회수액 | 반환 | `returnedTotal` | 미수 잔여 |
|---|---|---|---|---|---|---|
| 매입 직후 | 0 | 10만 | 7만 | — | 0 | **3만** |
| 4만 환불 | 4만 | 6만 | 7만 | **1만** | 1만 | **0** (3만 소멸) |
| 6만 환불 | 10만 | 0 | 6만 | **6만** | **7만** | 0 |
| **고객이 미수 3만 상환 후 10만 환불** | 10만 | 0 | **10만** | **10만** | **10만** | 0 |

> ★ **회수액을 저장하지 않는다.** `withdrawnAmount`(불변) + `미수.recoveredAmount`(미수가 소유) − `returnedTotal`로 **매번 계산**한다. 승인이 회수액을 필드로 들면 그것이 **다시 합계 필드**가 되어 미수와 어긋난다 — DC-001이 없앤 구조다.
>
> ⚠️ **좌변(누계)이 없으면 상한이 있어도 소용없다.** `refundedTotal` 없이 요청액만 검사하면 나눠 환불로 그대로 넘어간다.
>
> ⚠️ **`cancelledAmount`로 겸용하면 안 된다.** 매입 후 환불이 `cancelledAmount`를 올리면 INV-3(`capturedAmount ≤ amount − cancelledAmount`)이 **이미 끝난 매입에 대해 사후 위반**된다 (INV-9).

### 조작 상세 — `void()` 와 `refund()` 의 분기 (BR-26)

| 원거래 상태 | 조작 | 원장 |
|---|---|---|
| 미매입 (성립·만료) | `void()` | **역분개 없음** — 확정 거래가 없다 |
| 매입됨 | `refund()` | **역분개 발생** |

> 이 분기가 BR-10(append-only)과 BR-08(전표 균형)의 적용 여부를 가른다.

---

## 6. 발행 이벤트

| 이벤트 | 코드명 | 담는 정보 | 구독자 |
|---|---|---|---|
| 승인 성립 | `Authorized` | 승인ID, 상관식별자, 승인번호, 금액, 영업일 | — (같은 트랜잭션) |
| 승인 거절 | `Declined` | 승인ID, 상관식별자, **거절 사유** | 운영자 |
| 망취소됨 | `Reversed` | 승인ID, 상관식별자 | — |
| 승인취소됨 | `Voided` | 승인ID, 취소액, 전액 여부 | — |
| 만료됨 | `Expired` | 승인ID, 시각 | — |
| **매입됨** | `Captured` | 승인ID, 매입액, 영업일 | ⚠️ **원장 아님** — 자금 이동 분개는 계좌 `Withdrawn`이 소유한다 (ACL 소유 규칙) · **C4 정산** |
| **환불됨** | `Refunded` | 승인ID, ★ **`accountId`**(보조부 기표 대상 — `journal-entry.md` INV-7), **`reductionAmount`(거래 축소액)** · **`writtenOffAmount`(자기 미수 소멸분)** · **`returnedAmount`(고객 반환액)** · **`recoveredAmount`(반환액 중 다른 미수 회수분)** · **`creditedAmount`(반환액 중 잔액 증가분)**, 영업일 | **C5 원장** · **C4 정산** |
| 보류/해제 | `Frozen` · `Unfrozen` | 승인ID, 운영자 | 운영자 |
| 정산 확정 | `Settled` | 승인ID, 정산일 | — |

---

## 7. 경계 근거

| 질문 | 답 |
|---|---|
| **왜 이 범위인가** | 취소 한도(INV-1)·매입 1회(INV-2)·홀딩 점유 상태(INV-4)가 **한 결제 건 안에서** 성립해야 한다 |
| **왜 더 크지 않은가** | 홀딩·한도의 **합계**를 들면 계좌·카드와 중복 소유가 된다. **자기 몫**(`heldAmount`·`limitContribution`)은 중복이 아니라 **등식의 구성 요소**이며, 그것이 없으면 계좌·카드의 ③ 등식을 계산할 수 없다 (DC-001) |
| **왜 더 작지 않은가** | `capturedAmount`를 빼면 INV-2(매입 1회)를 지킬 수 없고, `cancelledAmount`를 빼면 INV-1을 지킬 수 없다. **둘 다 지금 이중 출금·초과 환불을 막는 유일한 장치다** |
| **트랜잭션 단위인가** | 원칙상 예. **승인 성립은 계좌·카드와**(E1), **환불은 그 승인의 미수와**(E4) 한 트랜잭션 |
| **합계 필드는 없는가** | 없다 — 모든 금액 필드가 **자기 거래 한 건**의 값이다 (양식 §4) |

---

## 8. 동시성

| 상황 | 처리 |
|---|---|
| **같은 상관 식별자로 중복 승인 요청** | 멱등 레코드가 막는다 (BR-02) — 승인 애그리게이트에 도달하지 않음 |
| **망취소 중복 수신** | `reverse()`가 멱등 — 이미 무효면 무시 (BR-13) |
| **망취소 선도착** | **유효한** 취소 예약이 `authorize()`의 사전조건을 막는다 (BR-22). 만료된 예약은 없는 것으로 본다 |
| **취소와 매입 동시 도착** | **매입 선행 확정**, 취소를 매입취소로 강등 (BR-26 · 충돌 C5) |
| 만료 배치와 매입의 경합 | 둘 다 `holdingFunds = false`로 수렴 — 순서 무관 |
| **만료 후 취소와 매입의 경합** | **먼저 도착한 쪽이 결말을 정한다** (BR-49 · 충돌 C9) |
| **보류 전환과 매입의 경합** | 보류 전환이 이 애그리게이트의 락을 잡는다 — 둘 중 하나만 성공 (BR-50) |

---

## 9. 미해결

| # | 의문 | 영향 |
|---|---|---|
| ~~AU1~~ | 부분 취소 후 매입 가능액 | **`승인액 − 누적취소액`이다** → INV-3 수정, BR-16 ③ 수정 |
| ~~AU2~~ | 정산 완료 후 환불 | **원거래를 되돌리지 않는다.** 별도 배치로 접수해 **다음 영업일 정산의 차감분**으로 처리 → BR-43 |

| ~~AU3~~ | 만료 상태의 취소 | **무효화 + 채무 소멸** → BR-49 |
| ~~AU4~~ | 보류 중 매입 도착 | **격리 후 해제 시 재처리** → BR-50 |
| ~~AU5~~ | 무효 승인 매입의 불일치 유형 | **M8 신설** → BR-51 |
| ~~AU9~~ | 부분 환불 시 자기 미수 | **환불은 거래 금액 기준. 미수는 산식의 파생값으로 자동 소멸** → BR-43 ① 재작성 |
| ~~AU10~~ | 이미 상계된 미수 뒤의 환불 | **미수가 회수액을 소유**하고 승인은 매번 계산 → DC-001 |

> 세 결정의 선택지·기각 이유는 `domain/state-machines/authorization.md` §8.

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.9 | 2026-08-04 | **DC-001 단계 12** — **INV-10·INV-11을 대사 불변식 RC-1·RC-2로 이동**(검증 위치에 "승인 단독 검증 불가"라 써 놓고 INV에 뒀다 — P1 재발) · `refund()`에 `recoverable` 인자 추가(E4 참여자) · `capture()`에 **부분 매입의 `limitContribution` 감액** 명시(BR-24 — T8에 한도 복원이 한 글자도 없었다) |
| v1.8 | 2026-08-04 | **DC-001 단계 10** — `heldAmount`·`limitContribution` 신설(계좌·카드 ③ 등식의 구성 요소. 없으면 등식 계산 불가) · **INV-10 상한 정정**(`withdrawnAmount` → `+ 미수.recoveredAmount` — 옛 상한은 AU9가 기각한 모델이었다) · `refund()` 절차에 **소멸 선행·조건부 호출·계좌 입금 포함**(E4) · 검산표 4행 정정 |
| v1.7 | 2026-08-04 | **DC-001 단계 3** — `recoveredAmount` **제거**(미수가 소유). `returnedTotal` 신설 + INV-10 재정의 · INV-11 신설 · `recoverReceivable()` 제거 · `refund()`가 **미수를 인자로 받아 `writeOff()` 호출**(E4). 회수액을 **저장하지 않고 매번 계산** — 저장하면 그것이 다시 합계 필드가 되어 미수와 어긋난다 |
| v1.6 | 2026-08-04 | **AU9·AU10 확정 — 환불 모델 교체.** 환불액을 "반환액"에서 **"거래 축소액"** 으로 재정의하고 반환액을 파생 계산으로 바꿨다. `receivableAmount` → **`recoveredAmount`**(회수 총액, 상환 배분으로 증가·반환으로 감소) · INV-7 상한을 `capturedAmount`로 · INV-10 신설 · `recoverReceivable()` 신설. 미수 소멸이 **별도 조작에서 산식의 파생**이 되어 계좌 합계 침범 위험이 사라졌다 |
| v1.5 | 2026-08-04 | 재점검 반영 — **`refundedTotal` 필드 신설**(INV-7의 좌변이 없어 나눠 환불하면 상한이 무의미했다) · INV-9 신설(환불이 `cancelledAmount`를 오염시키면 INV-3이 사후 위반) |
| v1.4 | 2026-08-04 | post-fix 반영 — ★ **INV-7의 기준을 불변값 `withdrawnAmount`로 교체**. `capturedAmount − receivableAmount`로 두면 환불 시 미수 차감이 상한을 키워 **나눠 환불하면 실제 출금액을 초과**한다. INV-8(두 금액 필드 불변) 신설, 부분 환불 미수 처리를 AU9로 등재 |
| v1.3 | 2026-08-04 | 듀얼 리뷰 반영 — **INV-6에서 만료 제외·거절 추가**(만료를 종료로 두면 BR-19·49가 런타임에서 차단된다) · **INV-7 환불 상한** 신설 + `receivableAmount` 필드(BR-43 ①) · `createVoidedByTombstone()` 분리(`authorize()`가 상반된 사후 상태 둘을 갖던 계약 모호성 해소) · `markSettled()`는 보류와 무관 · `unfreeze()`는 종료 상태에서도 허용 |
| v1.2 | 2026-08-03 | 상태 머신(Phase 2-5) 결과 반영 — `reverse()`·`void()` 사전조건에 만료 추가(BR-49), `capture()`에 `frozen = false` 추가(BR-50), 동시성 2행 추가 |
| v1.1 | 2026-08-03 | AU1·AU2 확정 반영 — INV-3을 `승인액 − 누적취소액`으로 수정, 정산 완료 후 환불은 별도 차감 거래(BR-43) |
| v1.0 | 2026-08-03 | 최초 작성 — 불변식 6종, 상태 8종, 조작 10종, 이벤트 9종. 만료가 종료 상태가 아니라는 점(EXPIRED → CAPTURED 허용)과 그 근거 명시 |
