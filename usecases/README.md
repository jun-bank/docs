# 유스케이스 색인 (Phase 4)

- 양식: `study/project-workflow/phase4/01-usecase-format.md` · `02-feature-spec-format.md`
- 상태: **파일럿 4건 작성 + 듀얼 1패스 리뷰 반영 (2026-08-05)** — 정본 공백·판정 대기 목록은 `plans/2026-08-05/phase4-pilot/log.md` "정본 보고 목록"

## 1. 유스케이스 대장

| # | 이름 | 액터 | 경계 | 상태 |
|---|---|---|---|---|
| UC-01 | [카드 결제를 승인받는다](UC-01-authorize-payment.md) | 매입사(시스템 — 소지자 대리) | E1 | 검토대기 |
| UC-02 | [잘못 반영된 입금을 정정한다](UC-02-reverse-deposit.md) | 운영자 2인 (BR-56 ①) | E5 | 검토대기 |
| UC-03 | [내 잔액·거래를 조회한다](UC-03-view-balance-transactions.md) | 고객 | 조회 | 검토대기 |
| UC-04 | [카드 분실을 신고한다](UC-04-report-lost-card.md) | 고객 ∪ 운영자 담당자 | — (상태 전이) | 확정 |
| UC-05 | 카드를 해지한다 | 고객 | — | 작성중 |
| UC-06 | 한도를 변경한다 | 고객 ∪ 운영자 담당자 | — | 작성중 |
| UC-07 | 타행 이체로 입금받는다 | 입금원(시스템 — 고객 대리) | E3 | 작성중 |
| UC-08 | 결제를 취소한다 | 매입사(시스템) | E1 계열 | 작성중 |
| UC-09 | 응답 유실 승인을 망취소한다 | 매입사(시스템) | E1 계열 | 작성중 |
| UC-10 | 매입 파일로 청산받는다 | 매입사(시스템) | E2 | 작성중 |
| UC-11 | 취소 레코드로 환불을 확정한다 | 매입사(시스템 — 소지자 대리) | E4 | 작성중 |
| UC-12 | 조사 대상을 보류/해제한다 | 운영자 담당자 | — | 작성중 |
| UC-13 | 미수 계좌의 승인 차단을 해제한다 | 운영자 2인 (BR-56 ②) | — | 작성중 |
| UC-14 | 보류 격리 매입을 재처리로 승격한다 | 운영자 2인 (BR-56 ③) | E2 | 작성중 |
| UC-15 | 실패한 정산을 강제 재개한다 | 운영자 2인 (BR-56 ④ — R15) | — | 작성중 |
| UC-16 | 원장 오기표를 역분개로 정정한다 | 운영자 2인 (BR-56 ⑤ — R15) | — | 작성중 |
| UC-17 | 불일치를 조사하고 처리한다 | 운영자 담당자 | — | 작성중 |
| UC-18 | 대사를 수동 실행한다 | 운영자 담당자 (전사) | — | 작성중 |
| UC-19 | DLQ 이벤트를 재투입한다 | 운영자 담당자 (전사) | — | 작성중 |
| UC-20 | 감사 기록을 조회한다 | 운영자 책임자 | 조회 | 작성중 |

## 2. 엔드포인트 색인 ★ (BR-58 전수 시험의 입력 — 사람이 세면 빠진다)

> 규칙: 신설 계약은 **같은 커밋으로 이 표에 등재**한다(02 양식 C-6).
> 시험 형식 = *"남의 식별자로 호출하면 거절되고, 응답이 '없음'과 구별되지 않는다"* (QS-08).

| 인터페이스 | UC | 주체 | L7 대상 |
|---|---|---|---|
| 전문 `AUTH-REQ` | UC-01 | 시스템(매입사 경로) | ✕ — 사유 구분이 **BR-36·15 정본 특칙** (UC1-1 ✅ 닫힘 · C-2 채널 조항) |
| `POST /ops/approval-requests` ★ **BR-56 공통 계약 정본 = UC-02 §7** (U-7) | UC-02 | 운영자 담당자+ | ✅ 대상 부재·스코프 밖 동일 · 판정 순서 = 스코프 먼저 |
| `POST /ops/approval-requests/{id}/approve·reject` | UC-02 | 운영자 책임자 | ✅ (SELF_APPROVAL은 비노출 제외 — UC2-2) |
| `POST /ops/accounts/{accountId}/deposit-reversals` | UC-02 | 운영자 담당자(=maker) | ✅ 계좌 부재·스코프 밖 동일 |
| `GET /me/accounts/{accountId}/balance` | UC-03 | 고객(본인) | ✅ ★ QS-08 원형 |
| `GET /me/accounts/{accountId}/transactions` | UC-03 | 고객(본인) | ✅ 목록·페이징 포함 |
| `POST·DELETE /me/cards/{cardId}/suspension` | UC-04 | 고객(본인) | ✅ |
| `POST·DELETE /ops/cards/{cardId}/suspension` | UC-04 | 운영자 담당자 | ✅ 스코프 밖 동일 |

## 3. 이벤트 색인 ★ (리뷰 Q-6 — 이벤트도 전수 대상: 축·행위자·S-9)

| 이벤트 | UC | 행위자 판정 (AD-7) | 축 필드 | S-9 |
|---|---|---|---|---|
| `HoldPlaced` | UC-01 | 자금 — 비포함 ✓ | 불요(내부 이벤트 — 발행 안 됨) | [미정 — 전수 시] |
| `DepositReversed` | UC-02 | 자금 — 비포함 ✓ (감사 outbox가 나름) | Phase 4 전수 시 (IS-5) | [미정] |
| `CardSuspended` | UC-04 | **비포함 확정** ✓ (AD-7 ② 확장 — 주체 혼합, 2026-08-05 판정) | 〃 | [미정] |

## 4. 도출표 ★ (전수성의 근거 — 조작 62 · 운영자 규칙 · SM 전이 → 판정)

> 판정 = **기존 UC** / **신규 UC**(아래 대장에 추가) / **운영 절차**(U-2 — 액터의 목표가 아닌 순수 배치·자동 경로) / **내부**(다른 UC의 단계로만 존재).
> 원천: `domain/aggregates/README.md` 조작 대장 · BR 운영자 조작 · 상태 머신 9종. **빈 칸 = 결함.**

| 조작(군) | 판정 |
|---|---|
| 계좌 `hold`·`releaseHold`·`useAccountLimit`·`restoreAccountLimit` | 내부 — UC-01 승인의 단계 |
| 계좌 `capture` · 승인 `capture` · 배치 `receive`~`complete` | **UC-10** 매입 파일 청산 (E2) |
| 계좌 `deposit` · 미수 `recover` · 입금수신 `find`·`record`·`assertSameRequest` | **UC-07** 타행 입금 (E3) |
| 계좌 `refund` · 승인 `refund` · 미수 `writeOff` | **UC-11** 환불 확정 (E4) |
| 계좌 `reverseDeposit` · 입금수신(정정) | 기존 **UC-02** |
| 계좌 `liftReceivableBlock` | **UC-13** 승인 차단 해제 (BR-56 ②) |
| 미수 `incur` | 내부 — UC-10·02의 부족분 단계 |
| 미수 `freeze`·`unfreeze` · 승인 `freeze`·`unfreeze` | **UC-12** 조사 보류/해제 (BR-28) |
| 입금수신·멱등·취소예약 `expire`·`purge` | 운영 절차 — 정리 배치 (액터 목표 아님) |
| 카드 `assertUsable`·`useLimit`·`restoreLimit` | 내부 — UC-01·08·10의 단계 |
| 카드 `suspend`·`resume` | 기존 **UC-04** |
| 카드 `terminate` | **UC-05** 카드 해지 (소지자·불가역) |
| 카드 `changeLimit` · 계좌 한도 변경 | **UC-06** 한도 변경 (소지자∪담당자 — BR-46) |
| 승인 `authorize`·`decline`·`createVoidedByTombstone` · 멱등 `find`·`record` | 기존 **UC-01** |
| 승인 `void`(전액·부분) | **UC-08** 결제 취소 (실시간 전문 — BR-26·11) |
| 승인 `reverse` · 취소예약 `record`·`consume` | **UC-09** 망취소 (BR-13·22) |
| 승인 `expire` | 운영 절차 — 만료 배치 (BR-03) |
| 승인 `markSettled` · 정산 `close`·`calculate`·`fail`·`retry`·`escalate` | 운영 절차 — 정산·커트오프 (BR-52) |
| 정산 `resumeByOperator` | **UC-15** 정산 강제 재개 (BR-56 ④ — R15) |
| 배치 `promoteIsolated` | **UC-14** 격리 재처리 승격 (BR-56 ③) |
| 배치 `isolate`·`interrupt` | 운영 절차 — 감시 배치 (시스템, BR-54 예외 ②) |
| 전표 `post` | 운영 절차 — 원장 ACL (이벤트 수신) |
| 전표 `reverse` | **UC-16** 원장 역분개 (BR-56 ⑤ — R15) |
| 불일치 `recordOrTouch` | 내부 — 대사·격리·M18의 적재 단계 |
| 불일치 `investigate`·`resolve` | **UC-17** 불일치 조사·처리 (BR-48) |
| BR-42 대사 수동 실행 | **UC-18** (담당자 — 전사 스코프) |
| M17 DLQ 재투입 (ADR-014) | **UC-19** (담당자 — 전사 스코프) |
| BR-57 감사 기록 조회 (AD-5) | **UC-20** (책임자) |
| ApprovalRequest `request`·`approve`·`reject`·`consume` | 내부 — BR-56 조작 UC들의 공통 단계 (정본 = UC-02 §7 · U-7) · `expire` = 운영 절차(예외 ⑨) |
| 대사 3자 비교·anchor 생성·릴레이·커트오프 드레인·통지(BR-53) | 운영 절차 — 액터의 목표가 아니다 (U-2) |

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v0.3 | 2026-08-05 | **듀얼 1패스 반영** — 이벤트 색인 신설(Q-6) · BR-56 공통 계약 정본 위치 표시(U-7) · 상태줄 정합(F-5) · ★ v0.1 이력의 "UC-01 등재"는 그 시점 사실이고 v0.2 갱신(UC-02~04·엔드포인트 7행)이 이력 없이 지나갔다(F-7) — 이 행이 그 정정이다 |
| v0.2 | 2026-08-05 | (이력 누락분 소급 — F-7) UC-02~04 등재 · 엔드포인트 7행 추가 |
| v0.1 | 2026-08-05 | 색인 신설 — UC-01 등재. 엔드포인트 색인이 QS-08 전수 시험의 입력임을 명시 |
