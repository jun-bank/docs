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
- 잔액·홀딩 금액 — C1 뱅킹 (승인은 **"내가 홀딩을 잡고 있는가"** 만 안다)
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
| `capturedAmount` | `Money?` | 매입된 금액 (null = 미매입) |
| `withdrawnAmount` | `Money` | 매입 시 즉시 출금된 금액 (BR-20). **매입 시점 확정 후 불변** — 감사 근거 |
| `returnedTotal` | `Money` | **고객에게 실제 반환한 누계.** 환불 산식의 결과이며 `withdrawnAmount`를 넘지 않는다 (INV-10) |
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
| **INV-10** | **`returnedTotal ≤ withdrawnAmount`** | BR-43 ① | 실제로 나간 돈보다 많이 돌려준다 | `refund()` 후 |
| **INV-11** | `refund()` 후 **회수액 ≤ 잔여 채무** (회수액 = `withdrawnAmount + 미수.recoveredAmount − returnedTotal`) | BR-43 ① | 초과 회수분이 남으면 **돌려줘야 할 돈을 안 돌려준 상태**다 | `refund()` 후 |
| **INV-2** | **매입은 1회만** — `capturedAmount`가 한 번 설정되면 다시 바뀌지 않는다 | BR-16 ② | 이중 출금 | `capture()` |
| **INV-3** | `capturedAmount ≤ amount − cancelledAmount` | BR-16 ③ | **부분 취소된 만큼을 다시 매입** — 이중 청구 | `capture()` |
| **INV-4** | **매입 후에는 `holdingFunds = false`** | BR-18 | 가용잔액 이중 차감 | `capture()` 후 |
| **INV-5** | `status = 성립` 이면 `approvalNumber ≠ null` | BR-17 | 승인번호 없는 성립 승인 | 상태 전이 후 |
| **INV-6** | 종료 상태(**거절·무효·환불완료·정산완료**)에서는 상태 전이가 일어나지 않는다. **만료는 종료가 아니다** — 지연 매입(BR-19)과 만료 후 취소(BR-49)가 정상 경로다 | BR-19·49 | 죽은 거래의 부활 / 반대로 만료를 넣으면 **정상 경로가 차단** | 모든 전이 |

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
| **매입** | `capture(amount, at)` | INV-2·INV-3 (`amount ≤ 승인액 − 누적취소액`), 상태 ∈ {성립, 만료}, **`frozen = false`** (BR-50) | 상태 = 매입됨, `holdingFunds = false` | `Captured` |
| **환불** | `refund(amount, receivable)` | 상태 = 매입됨, **INV-7** (`refundedTotal + amount ≤ capturedAmount`) | `refundedTotal` 증가 → **반환액·미수 소멸액 파생** → `returnedTotal` 증가 · `receivable.writeOff()` 호출 (E4). 잔여 채무 0이면 상태 = 환불됨 | `Refunded` |
| **보류** | `freeze()` | 종료 상태 아님 | `frozen = true` | `Frozen` |
| **보류 해제** | `unfreeze()` | `frozen = true`. **종료 상태에서도 허용** — 보류 목록에서 내릴 유일한 경로다 | `frozen = false` | `Unfrozen` |
| **정산 확정** | `markSettled()` | 상태 = 매입됨. **`frozen` 여부와 무관** (BR-28에 정산 제외가 없다) | 상태 = 정산완료 | `Settled` |

### 조작 상세 — `capture()` 가 두 상태에서 허용되는 이유

```
AUTHORIZED → CAPTURED    정상 경로
EXPIRED    → CAPTURED    지연 매입 (BR-19) — 만료는 채무 소멸이 아니다
```

**둘 다 `holdingFunds`를 false로 만든다.** 만료 시 이미 false이므로 멱등하다.

> ⚠️ **단, 만료 후 취소가 먼저 도착했다면 상태가 `VOIDED`이므로 매입은 격리된다** (BR-49 · 충돌 C9). 만료된 승인의 결말은 **먼저 도착한 쪽이 정한다.**

### 조작 상세 — `refund()` 는 거래를 줄이고 반환액을 파생한다 (BR-43 ①)

```
입력: 환불액 = 거래를 얼마로 줄이는가 (매입액 기준) · 이 승인의 미수(있으면)

1) refundedTotal += 환불액                        INV-7: ≤ capturedAmount
2) 잔여 채무 = capturedAmount − refundedTotal
3) 회수액   = withdrawnAmount + 미수.recoveredAmount − returnedTotal
4) 반환액   = max(0, 회수액 − 잔여 채무)            ← 초과 회수분만
5) returnedTotal += 반환액                         INV-10: ≤ withdrawnAmount
6) 미수 소멸액 = max(0, 미수.outstanding() − max(0, 잔여 채무 − 회수액))
   미수.writeOff(소멸액)                           ← E4 같은 커밋
7) 잔여 채무 = 0 이면 상태 = 환불됨
```

| 매입 10만 · 출금 7만 · 미수 3만 | `refundedTotal` | 잔여 채무 | 회수액 | 반환 | `returnedTotal` | 미수 잔여 |
|---|---|---|---|---|---|---|
| 매입 직후 | 0 | 10만 | 7만 | — | 0 | **3만** |
| 4만 환불 | 4만 | 6만 | 7만 | **1만** | 1만 | **0** (3만 소멸) |
| 6만 환불 | 10만 | 0 | 6만 | **6만** | **7만** | 0 |
| **고객이 미수 3만 상환 후 10만 환불** | 10만 | 0 | **10만** | **10만** | 7만 | 0 |

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
| **매입됨** | `Captured` | 승인ID, 매입액, 영업일 | **C5 원장** · **C4 정산** |
| **환불됨** | `Refunded` | 승인ID, 환불액, 영업일 | **C5 원장** · **C4 정산** |
| 보류/해제 | `Frozen` · `Unfrozen` | 승인ID, 운영자 | 운영자 |
| 정산 확정 | `Settled` | 승인ID, 정산일 | — |

---

## 7. 경계 근거

| 질문 | 답 |
|---|---|
| **왜 이 범위인가** | 취소 한도(INV-1)·매입 1회(INV-2)·홀딩 점유 상태(INV-4)가 **한 결제 건 안에서** 성립해야 한다 |
| **왜 더 크지 않은가** | 홀딩 **금액**을 들면 계좌와 중복 소유가 된다. 한도 사용액을 들면 카드와 중복 |
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
| v1.7 | 2026-08-04 | **DC-001 단계 3** — `recoveredAmount` **제거**(미수가 소유). `returnedTotal` 신설 + INV-10 재정의 · INV-11 신설 · `recoverReceivable()` 제거 · `refund()`가 **미수를 인자로 받아 `writeOff()` 호출**(E4). 회수액을 **저장하지 않고 매번 계산** — 저장하면 그것이 다시 합계 필드가 되어 미수와 어긋난다 |
| v1.6 | 2026-08-04 | **AU9·AU10 확정 — 환불 모델 교체.** 환불액을 "반환액"에서 **"거래 축소액"** 으로 재정의하고 반환액을 파생 계산으로 바꿨다. `receivableAmount` → **`recoveredAmount`**(회수 총액, 상환 배분으로 증가·반환으로 감소) · INV-7 상한을 `capturedAmount`로 · INV-10 신설 · `recoverReceivable()` 신설. 미수 소멸이 **별도 조작에서 산식의 파생**이 되어 계좌 합계 침범 위험이 사라졌다 |
| v1.5 | 2026-08-04 | 재점검 반영 — **`refundedTotal` 필드 신설**(INV-7의 좌변이 없어 나눠 환불하면 상한이 무의미했다) · INV-9 신설(환불이 `cancelledAmount`를 오염시키면 INV-3이 사후 위반) |
| v1.4 | 2026-08-04 | post-fix 반영 — ★ **INV-7의 기준을 불변값 `withdrawnAmount`로 교체**. `capturedAmount − receivableAmount`로 두면 환불 시 미수 차감이 상한을 키워 **나눠 환불하면 실제 출금액을 초과**한다. INV-8(두 금액 필드 불변) 신설, 부분 환불 미수 처리를 AU9로 등재 |
| v1.3 | 2026-08-04 | 듀얼 리뷰 반영 — **INV-6에서 만료 제외·거절 추가**(만료를 종료로 두면 BR-19·49가 런타임에서 차단된다) · **INV-7 환불 상한** 신설 + `receivableAmount` 필드(BR-43 ①) · `createVoidedByTombstone()` 분리(`authorize()`가 상반된 사후 상태 둘을 갖던 계약 모호성 해소) · `markSettled()`는 보류와 무관 · `unfreeze()`는 종료 상태에서도 허용 |
| v1.2 | 2026-08-03 | 상태 머신(Phase 2-5) 결과 반영 — `reverse()`·`void()` 사전조건에 만료 추가(BR-49), `capture()`에 `frozen = false` 추가(BR-50), 동시성 2행 추가 |
| v1.1 | 2026-08-03 | AU1·AU2 확정 반영 — INV-3을 `승인액 − 누적취소액`으로 수정, 정산 완료 후 환불은 별도 차감 거래(BR-43) |
| v1.0 | 2026-08-03 | 최초 작성 — 불변식 6종, 상태 8종, 조작 10종, 이벤트 9종. 만료가 종료 상태가 아니라는 점(EXPIRED → CAPTURED 허용)과 그 근거 명시 |
