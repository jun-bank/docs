# 유스케이스 색인 (Phase 4)

- 양식: `study/project-workflow/phase4/01-usecase-format.md` · `02-feature-spec-format.md`
- 상태: **파일럿 4건 작성 + 듀얼 1패스 리뷰 반영 (2026-08-05)** — 정본 공백·판정 대기 목록은 `plans/2026-08-05/phase4-pilot/log.md` "정본 보고 목록"

## 1. 유스케이스 대장

| # | 이름 | 액터 | 경계 | 상태 |
|---|---|---|---|---|
| UC-01 | [카드 결제를 승인받는다](UC-01-authorize-payment.md) | 매입사(시스템 — 소지자 대리) | E1 | 검토대기 |
| UC-02 | [잘못 반영된 입금을 정정한다](UC-02-reverse-deposit.md) | 운영자 2인 (BR-56 ①) | E5 | 검토대기 |
| UC-03 | [내 잔액·거래를 조회한다](UC-03-view-balance-transactions.md) | 고객 | 조회 | 검토대기 |
| UC-04 | [카드 분실을 신고한다](UC-04-report-lost-card.md) | 고객 ∪ 운영자 담당자 | — (상태 전이) | 검토대기 |

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

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v0.3 | 2026-08-05 | **듀얼 1패스 반영** — 이벤트 색인 신설(Q-6) · BR-56 공통 계약 정본 위치 표시(U-7) · 상태줄 정합(F-5) · ★ v0.1 이력의 "UC-01 등재"는 그 시점 사실이고 v0.2 갱신(UC-02~04·엔드포인트 7행)이 이력 없이 지나갔다(F-7) — 이 행이 그 정정이다 |
| v0.2 | 2026-08-05 | (이력 누락분 소급 — F-7) UC-02~04 등재 · 엔드포인트 7행 추가 |
| v0.1 | 2026-08-05 | 색인 신설 — UC-01 등재. 엔드포인트 색인이 QS-08 전수 시험의 입력임을 명시 |
