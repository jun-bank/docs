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
| UC-05 | [카드를 해지한다](UC-05-terminate-card.md) | 고객 | — | 초안 (계약 블록 후속) |
| UC-06 | [한도를 변경한다](UC-06-change-limit.md) | 고객 ∪ 운영자 담당자 | — | 초안 (계약 블록 후속) |
| UC-07 | [타행 이체로 입금받는다](UC-07-receive-deposit.md) | 입금원(시스템 — 고객 대리) | E3 | 초안 (계약 블록 후속) |
| UC-08 | [결제를 취소한다](UC-08-void-payment.md) | 매입사(시스템) | E1 | 초안 (계약 블록 후속) |
| UC-09 | [응답 유실 승인을 망취소한다](UC-09-network-cancel.md) | 매입사(시스템) | E1 / 예약 기록은 경계 없음 | 초안 (계약 블록 후속) |
| UC-10 | [매입 파일로 청산받는다](UC-10-capture-settlement-file.md) | 매입사(시스템) | E2 | 초안 (계약 블록 후속) |
| UC-11 | [취소 레코드로 환불을 확정한다](UC-11-refund-via-cancel-record.md) | 매입사(시스템 — 소지자 대리) | E4 | 초안 (계약 블록 후속) |
| UC-12 | [조사 대상을 보류/해제한다](UC-12-freeze-for-investigation.md) | 운영자 담당자 | — | 초안 (계약 블록 후속) |
| UC-13 | [미수 계좌의 승인 차단을 해제한다](UC-13-lift-receivable-block.md) | 운영자 2인 (BR-56 ②) | — | 초안 (계약 블록 후속) |
| UC-14 | [보류 격리 매입을 재처리로 승격한다](UC-14-promote-isolated-capture.md) | 운영자 2인 (BR-56 ③) | E2 | 초안 (계약 블록 후속) |
| UC-15 | [실패한 정산을 강제 재개한다](UC-15-resume-settlement.md) | 운영자 2인 (BR-56 ④ — R15) | — | 초안 (계약 블록 후속) |
| UC-16 | [원장 오기표를 역분개로 정정한다](UC-16-reverse-journal-entry.md) | 운영자 2인 (BR-56 ⑤ — R15) | — | 초안 (계약 블록 후속) |
| UC-17 | [불일치를 조사하고 처리한다](UC-17-investigate-discrepancy.md) | 운영자 담당자 | — | 초안 (계약 블록 후속) |
| UC-18 | [대사를 수동 실행한다](UC-18-run-reconciliation.md) | 운영자 담당자 (전사) | — | 초안 (계약 블록 후속) |
| UC-19 | [DLQ 이벤트를 재투입한다](UC-19-requeue-dlq.md) | 운영자 담당자 (전사) | — | 초안 (계약 블록 후속) |
| UC-20 | [감사 기록을 조회한다](UC-20-view-audit-records.md) | ★ AUDITOR(D-5 완전 분리) | 조회 | 초안 (계약 블록 후속) |

## 2. 엔드포인트 색인 ★ (BR-58 전수 시험의 입력 — 사람이 세면 빠진다)

> 규칙: 신설 계약은 **같은 커밋으로 이 표에 등재**한다(02 양식 C-6).
> 시험 형식 = *"남의 식별자로 호출하면 거절되고, 응답이 '없음'과 구별되지 않는다"* (QS-08).
>
> ⚠️ **이 색인은 현재 전수가 아니다 (2026-08-06 루프 1 L1-15 — 명시 이월).** C7 인증의 **관리 API 표면 전체**(조직·운영자·권한·회원)는 애그리게이트·규칙 수준까지만 정해졌고 **UC·계약이 아직 없다.** BR-58 전수 시험은 **엔드포인트 목록을 입력으로 삼으므로**, 그 목록에 없는 표면은 **시험 대상에서 통째로 빠진다** — *"사람이 세면 빠진다"* 를 막으려고 만든 색인이 **미작성 표면 앞에서는 같은 한계를 갖는다.** 조직 조회의 형제 열거 차단(`org-unit.md` §5)처럼 **조건은 이미 정본에 있으나 시험할 표면이 없는** 상태다. C7 관리 API 패스에서 이 행을 실제 엔드포인트로 대체하는 것이 그 패스의 acceptance다.

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
| `POST /me/cards/{cardId}/termination` | UC-05 | 고객(본인) | ✅ · 운영자 경로 없음(BR-55 각주) |
| `PUT /me/cards/{cardId}/limits` | UC-06 | 고객(본인) | ✅ |
| `PUT /ops/cards/{cardId}/limits` | UC-06 | 운영자 담당자 | ✅ 스코프 밖 동일 |
| `PUT /me/accounts/{accountId}/daily-limit` | UC-06 | 고객(본인) | ✅ |
| `PUT /ops/accounts/{accountId}/daily-limit` | UC-06 | 운영자 담당자 | ✅ |
| 전문 `DEPOSIT-ADV` (K-2 확정) | UC-07 | 시스템(입금원 경로) | ✕ 시스템 채널(C-2) · 거절 형태 UC7-3 |
| 전문 `CANCEL-REQ/RES` (K-2 확정) | UC-08 | 시스템(매입사 경로) | ✕ 사유 구분(C-2 특칙) |
| 전문 `REVERSAL-REQ/RES` (K-2 확정) | UC-09 | 시스템(매입사 경로) | ✕ 〃 · 원승인 없음 = 예약(존재 비누설) |
| 파일 `CAPTURE-FILE` (K-2 확정) | UC-10·11 | 시스템(배치 — 예외 ②) | 해당 없음(응답 상대 없음 — 격리+불일치) |
| `POST·DELETE /ops/authorizations/{authorizationId}/freeze` | UC-12 | 담당자(개설 조직) | ✅ |
| `POST·DELETE /ops/receivables/{receivableId}/freeze` | UC-12 | 담당자(accountId 귀속) | ✅ |
| `POST /ops/accounts/{accountId}/receivable-block-lifts` | UC-13 | 담당자(=maker) — BR-56 ② | ✅ |
| `POST /ops/accounts/{accountId}/receivable-block-reimpositions` | UC-13 | 담당자 — 승인 절차 없음(안전 방향) | ✅ |
| `POST /ops/capture-batches/{fileId}/isolated-records/{recordId}/promotion` | UC-14 | 담당자(=maker) · 전사 — BR-56 ③ | △ 부재만 NOT_FOUND(축 없음 — BR-55 특칙) |
| (승인 요청 공통 계약 `POST /ops/approval-requests` — **①~⑤ 전부** 사용, 정본 = UC-02 §7 · ④⑤만 ★ 실행 엔드포인트 없음 — R15 지시 이벤트) | UC-02·13·14·15·16 | 담당자(=maker) | 대상별 (④ ✕ 영업일 / ⑤ ✅ 원전표 / ①②③ ✅) |
| ★ `GET /ops/approval-requests` (승인 대기·내 요청 목록 — BR-56 워크플로의 전제 조회. 리뷰 F-4가 발견한 누락) | UC-02 공통 | 담당자(내 요청) / 책임자(대기 목록) · 스코프 | ✅ |
| `POST /ops/discrepancies/{discrepancyId}/investigation` · `/resolution` | UC-17 | 운영자 담당자 | ✅ 유도 스코프(UC17-1 확정) |
| ★ `GET /ops/discrepancies` (목록 — UC-17 §3의 전제 조회. 리뷰 F-1이 발견한 누락) | UC-17 | 운영자 조회 이상 | ✅ 유도 스코프(UC17-1 확정) |
| `POST /ops/reconciliations` · `GET /ops/reconciliations/{runId}` | UC-18 | 담당자·전사 / 조회+ | ✕ 영업일 축 |
| `GET /ops/dlq` · `POST /ops/dlq/{outboxRecordId}/replay` | UC-19 | 조회+ / 담당자 · 전사 | ✕ · payload = 메타만(D-UC19 확정 — partition=계좌ID 노출은 명시) |
| `GET /ops/audit-records` · `/{recordId}` | UC-20 | ★ **AUDITOR** · grant 스코프 서브트리(축 없는 기록 = **루트 스코프만**) — 2026-08-06 C7 D-5 완전 분리(구 "책임자" 대체) | ✅ 목록·집계 포함(BR-58 전 형태) |
| ★ **C7 관리 API 전체 — 명시 이월** (2026-08-06 루프 1 **L1-15**): 조직(`OrgUnit.create`·`close`·**조회 표면** — 트리·형제 열거 차단) · 운영자(`register`·`suspend`·`resume`·`terminate`·`transfer`) · 권한(`RoleGrant.issue`·`revoke`·`recertify` — **BR-56 ⑥ 승인 요청의 인자 스키마 포함**) · 회원(`Member.*` — 해지 2단계) | **미작성** — 후속 패스 | 운영자(단계·스코프는 **BR-55 배정 표**가 이미 정본) | ⚠️ **이 행이 비어 있는 동안 BR-58 전수 시험의 입력이 불완전하다** — 아래 주 참조 |

## 3. 이벤트 색인 ★ (리뷰 Q-6 — 이벤트도 전수 대상: 축·행위자·S-9)

| 이벤트 | UC | 행위자 판정 (AD-7) | 축 필드 | S-9 |
|---|---|---|---|---|
| `HoldPlaced` | UC-01 | 자금 — 비포함 ✓ | 불요(내부 이벤트 — 발행 안 됨) | 1 |
| `DepositReversed` | UC-02 | 자금 — 비포함 ✓ (감사 outbox가 나름) | ★ 확정(K-4): 기존 파티션 축(accountId) 유지 · `ownerId` 비포함 — 파티션 0인 이벤트만 각 블록 명시 | 1 |
| `CardSuspended` | UC-04 | **비포함 확정** ✓ (AD-7 ② 확장 — 주체 혼합, 2026-08-05 판정) | 〃 | 1 |
| `LimitChanged`(UC-06) · `Voided`·`Reversed`·tombstone 2종(UC-08·09) · 배치 **수명주기** 5종·`Captured`·`Withdrawn`(UC-10) · ★ `IsolatedRecordReclassified`(UC-14 — 시스템) · `Refunded`·`RefundCredited`(UC-11) · `Deposited`·`ReceivableRecovered`·`DepositConflict`(UC-07) · ★ `AccountDailyLimitChanged`(UC-06) | 각 UC | **비포함 확정**(자금/시스템/주체 혼합 — AD-7 ②) | 〃 | 1 |
| ★ `CardTerminated`(UC-05) → **비포함 확정**(AD-7 ② 확장 — 소지자 전용 비자금) · ★ `JournalReversed`(UC-16) → **포함 확정**(①·② 겹침의 ① 우선 — 발생 경로 운영자 전용) | UC-05·16 | 2026-08-06 확정 — 판정 대기 해소(ADR-017 v0.2) | 〃 | 1 |
| `DiscrepancyRecorded`·`DiscrepancyRedetected` (정본 discrepancy §5.1 — 발생 = UC-18 대사 · **UC-10 격리 즉시 적재** · **C8 M18(R16)**) | UC-18·10·(C8) | 비포함(시스템 적재) ✓ | 〃 | 1 |
| `ReceivableIncurred` (E2·E5 — C5 원장 구독) | UC-10·02 | 자금 — 비포함 ✓ | accountId | 1 |
| `ReceivableWrittenOff` (E4 — C5 원장 구독) | UC-11 | 자금 — 비포함 ✓ | accountId | 1 |
| `Frozen`·`Unfrozen`·`ReceivableFrozen/Unfrozen`(UC-12) · `ReceivableBlockLifted`(UC-13) · `IsolatedRecordPromoted`(UC-14) · `DiscrepancyInvestigating/Resolved`(UC-17) · `SettlementResumedByOperator`(UC-15) · ★ `ReceivableBlockReimposed`(UC-13) | 각 UC | **포함 ✓**(AD-7 ① 운영자 전용 — 정본 일치) | 〃 | 1 |
| ★ `SettlementResumeInstructed`·`JournalReversalInstructed` (C8→C4·C5 — 이름 확정 2026-08-06. payload = instructionId·approvalRequestId·인자·maker·checker·사유·approvedAt) | UC-15·16 | 포함(운영 — maker·checker 실림, AD-6 · AD-7 번역 입력 아님) | 없음(파티션 0) | 1 |

## 4. 도출표 ★ (전수성의 근거 — 조작 **65** · 운영자 규칙 · SM 전이 → 판정)

> 집계 이력: 62(2026-08-05) → **65**(2026-08-06 정본 판정 반영 — `changeDailyLimit`·`reimposeReceivableBlock`·`reclassifyIsolated` 신설. 리뷰 M-01이 헤더 미갱신을 잡았다)

> 판정 = **기존 UC** / **신규 UC**(아래 대장에 추가) / **운영 절차**(U-2 — 액터의 목표가 아닌 순수 배치·자동 경로) / **내부**(다른 UC의 단계로만 존재).
> 원천: `domain/aggregates/README.md` 조작 대장 · BR 운영자 조작 · 상태 머신 9종. **빈 칸 = 결함.**

| 조작(군) | 판정 |
|---|---|
| 계좌 `hold`·`releaseHold`·`useAccountLimit`·`restoreAccountLimit` | 내부 — UC-01 승인의 단계 |
| 계좌 `capture` · 승인 `capture` · 배치 `receive`~`complete` | **UC-10** 매입 파일 청산 (E2) |
| 계좌 `deposit` · 미수 `recover` · 입금수신 `find`·`record`·`assertSameRequest` | **UC-07** 타행 입금 (E3) |
| 계좌 `refund` · 승인 `refund` · 미수 `writeOff` | **UC-11** 환불 확정 (E4) |
| 계좌 `reverseDeposit` · 입금수신(정정) | 기존 **UC-02** |
| 계좌 `liftReceivableBlock` · ★ `reimposeReceivableBlock` | **UC-13** 승인 차단 해제·재부과 (해제 = BR-56 ② / 재부과 = 담당자 단독 — BR-45, UC13-1 확정) |
| 미수 `incur` | 내부 — UC-10·02의 부족분 단계 |
| 미수 `freeze`·`unfreeze` · 승인 `freeze`·`unfreeze` | **UC-12** 조사 보류/해제 (BR-28) |
| 입금수신·멱등·취소예약 `expire`·`purge` | 운영 절차 — 정리 배치 (액터 목표 아님) |
| 카드 `assertUsable`·`useLimit`·`restoreLimit` | 내부 — UC-01·08·10의 단계 |
| 카드 `suspend`·`resume` | 기존 **UC-04** |
| 카드 `terminate` | **UC-05** 카드 해지 (소지자·불가역) |
| 카드 `changeLimit` · 계좌 ★ `changeDailyLimit` | **UC-06** 한도 변경 (소지자∪담당자 — BR-46, UC6-1 확정) |
| 승인 `authorize`·`decline`·`createVoidedByTombstone` · 멱등 `find`·`record` | 기존 **UC-01** |
| 승인 `void`(전액·부분) | **UC-08** 결제 취소 (실시간 전문 — BR-26·11) |
| 승인 `reverse` · 취소예약 `record`·`consume` | **UC-09** 망취소 (BR-13·22) |
| 승인 `expire` | 운영 절차 — 만료 배치 (BR-03) |
| 승인 `markSettled` · 정산 `close`·`calculate`·`fail`·`retry`·`escalate` | 운영 절차 — 정산·커트오프 (BR-52) |
| 정산 `resumeByOperator` | **UC-15** 정산 강제 재개 (BR-56 ④ — R15) |
| 배치 `promoteIsolated` | **UC-14** 격리 재처리 승격 (BR-56 ③) |
| 배치 `isolate` | ★ 내부 — **UC-10의 단계 6**(격리는 매입 반영의 일부다 — 리뷰 F-5 정정: 처음 감시 배치로 오판) |
| 배치 ★ `reclassifyIsolated` | 내부 — 시스템(승인 종료 이벤트 트리거, B9 — UC-14 §4-F·UC14-2 확정. 액터 목표 아님) |
| 배치 `interrupt` | 운영 절차 — 감시 배치 (시스템, BR-54 예외 ②) |
| 전표 `post` | 운영 절차 — 원장 ACL (이벤트 수신) |
| 전표 `reverse` | **UC-16** 원장 역분개 (BR-56 ⑤ — R15) |
| 불일치 `recordOrTouch` | 내부 — 대사·격리·M18의 적재 단계 |
| 불일치 `investigate`·`resolve` | **UC-17** 불일치 조사·처리 (BR-48) |
| BR-42 대사 수동 실행 | **UC-18** (담당자 — 전사 스코프) |
| M17 DLQ 재투입 (ADR-014) | **UC-19** (담당자 — 전사 스코프) |
| BR-57 감사 기록 조회 (AD-5) | **UC-20** (★ AUDITOR — 2026-08-06 D-5) |
| ApprovalRequest `request`·`approve`·`reject`·`consume` | 내부 — BR-56 조작 UC들의 공통 단계 (정본 = UC-02 §7 · U-7) · `expire` = 운영 절차(예외 ⑨) |
| 대사 3자 비교·anchor 생성·릴레이·커트오프 드레인·통지(BR-53) | 운영 절차 — 액터의 목표가 아니다 (U-2) |
| ★ **조회 표면 (4번째 원천 — 리뷰 F-4 정정: 조작·전이 3원천은 조회를 구조적으로 못 잡는다)** | 고객 조회 = **UC-03**(BR-31·58) · 감사 조회 = **UC-20**(BR-57) · 불일치 목록 = **UC-17의 단계**(`GET /ops/discrepancies`) · 승인 대기/내 요청 목록 = **UC-02 공통 계약의 단계**(`GET /ops/approval-requests` — BR-56 워크플로 전제) · DLQ 목록 = UC-19 · 정산 상태 = UC-18. 조회 UC의 전수성은 **엔드포인트 색인**이 담보한다(도출표의 한계 명시 — 가정 1 부분 반증. ⚠️ 순환 위험 — **교차 검증(색인 ↔ 시나리오 전제 조회 대조)은 계약 전수 패스의 acceptance**) |

## 5. 계약 공통 규약 ★ (정본 — 2026-08-06 사용자 합의 4묶음. 02 양식 C-1~6 위에 얹힌다)

### K-1 오류·멱등
- **판정 순서 고정**: ① **자기 속성 전부**(단계 + 전사 스코프 보유(P-6) = `FORBIDDEN_LEVEL` — 대상 조회 전) → ② **스코프·존재**(`NOT_FOUND` — 부재·타인·스코프 밖 **동일 형태**, L7) **+ 대상 유효성**(★ 고유 코드 — 예: `INVALID_BUSINESS_DATE`. NOT_FOUND로 접지 않는다 — 재점검 정정) → ③ 상태·인자 (UC-02 확정 순서의 전 계약 적용).
- ★ **시스템 채널(전문·파일)은 `X-10`이 정본이다**(`interfaces/README.md` — **① 인자 형식 → ② 멱등 단락 → ③ 대상 존재 → ④ 상태**. 채널 인가 `FORBIDDEN_LEVEL`은 전문 처리 이전의 ACL 판정이라 ① 앞에 선다): **재수신이 대상 조회보다 앞서야** 최초 결과 재반환이 성립하기 때문이다 — 위 사람 채널 순서는 **그대로 두고**(변경 없음) 채널로 갈린다.
- **코드 3계층**: ⑴ 공통 4종 `FORBIDDEN_LEVEL`·`NOT_FOUND`·`INVALID_STATE`·`ARG_MISMATCH` ⑵ **SM 금지 표의 응답 열이 정본**인 코드(CF·AF·BF·F·RF — 계약이 재발명하지 않는다) ⑶ 조작 고유 코드는 신설 최소화.
- ★ **CDS3 일반화**: 사람 채널의 **상태 전이 재요청은 전부 명시 거절**(`ALREADY_*` — 무음 무시는 상태 오인을 만든다). 단 **PUT 값 교체는 자연 멱등**(동일값 재요청 = 성공 — 응답이 현재값을 보여줘 오인이 없다). *(o-OQ5 판정 포함 — `changeLimit`·`changeDailyLimit` 동일값 = 성공)*
- **시스템 채널 재수신 = 최초 결과 재반환**(멱등 키 = 채널 유일 식별자: 승인 전문 = 멱등 레코드 · 입금 = 입금 수신 · 파일 = `(fileId, recordId)` · R15 지시 = 지시 ID).

**신설 코드 대장** (2026-08-06 U-2 — K-1 ⑶의 유일 창구. 여기 없는 코드는 계약이 쓸 수 없다):
`ALREADY_FROZEN`·`ALREADY_UNFROZEN`(보류 재요청 — 승인·미수 공통) · `ALREADY_LIFTED`·`ALREADY_BLOCKED`(차단 해제/재부과) · `ALREADY_PROMOTED`(승격 API 재지시 — BF8 무음은 배치 재개 전용) · `ALREADY_APPROVED/REJECTED/CONSUMED/EXPIRED`(승인요청 종료 재호출 — 구 INVALID_STATE 대체) · `ALREADY_RUNNING`(대사 진행 중 + 진행 runId) · `ALREADY_DELIVERED`·`ALREADY_RESOLVED`(DLQ 종료 재투입) · `NOT_MAKER`(A4 — 승인요청을 본 뒤 판정) · `DUPLICATE_INSTRUCTION`(④⑤ 지시 ID 요청 단계 유일) · `NO_RECEIVABLE`(미결 미수 부재) · `EXCEEDS_CANCELABLE`(누적취소 초과 — 시스템 채널 사유 구분) · `AUTH_NOT_FOUND`·`ACCOUNT_NOT_FOUND`(시스템 채널 대상 부재 — 기관 채널이라 사유 구분, L7 비적용) · ★ `VOIDED_BY_RESERVATION`(취소 예약 소비로 무효 성립 — UC-01 §4-B의 응답, 승인도 거절도 아닌 제3형태의 명시. 2026-08-06 규격서 보고 4) · ★ 승인 거절의 카드 사유 3분 = **SM 응답 열 재사용**(`CARD_SUSPENDED`(CF4)·`CARD_EXPIRED`(CF6)·`CARD_TERMINATED`(CF3) — `DECLINED_CARD` 단일 상수 대체, BR-15 구분 요구. 신설 아님) · `INVALID_BUSINESS_DATE`·`DRAIN_INCOMPLETE`(대사 실행 전제)

**선례 승계 코드** (신설 아님 — 파일럿 UC-01~03·SM 응답 열이 출처. 리뷰 F9 보완 — 대장 창구를 완성한다): 공통 4종 · `INVALID_OPERATION`·`NO_APPROVAL`·`NO_ORIGINAL`·`EXCEEDS_ORIGINAL`·`DUPLICATE`·`SELF_APPROVAL`·`IDEMPOTENCY_CONFLICT`·`INVALID_CURSOR` · **SM 응답 열 전부**(CF·BF·F·RF·SF·DF·VF — 예: `AUTH_ALREADY_CAPTURED`(F1)는 실시간 취소의 CAPTURED 거절에도 재사용한다. 2026-08-06 리뷰 통합 — `AUTH_CAPTURED` 신설안 철회)

### K-2 명명
- 경로 접두 = **주체 채널**(`/me` 고객 본인 · `/ops` 운영자 · 전문/파일 = 채널 규격명). 조작 = **명사 자원**(`POST …/suspension` — 동사 금지), 해제 = **DELETE 동일 자원**, 값 교체 = `PUT`, 조회 = `GET`.
- **전문·파일 이름 확정**: `AUTH-REQ/RES` · `CANCEL-REQ/RES` · `REVERSAL-REQ/RES` · `DEPOSIT-ADV`★**/RES**(응답 — 2026-08-06 규격서 작성 중 확장: 동기 응답 전문이 UC-07 계약에 있는데 이름이 없었다) · `CAPTURE-FILE` (색인 [미정] 해제).
- 이벤트 = 과거분사 사실명(기존 관행).

### K-3 S-9 스키마 버전
- 전 이벤트 payload에 **`schemaVersion: 1`**. ★ **의미 필드 추가 = 새 이벤트 타입**(S-6a — 버전 올림 아님). 버전은 비의미 변경(표현·검증 강화)용으로만.

### K-4 축·감사 스코프 (2026-08-06 보정 — U-2 판정 A-2·3·B-11·A-6·B-5)
- 이벤트 축 = **기존 파티션 축(accountId) 유지**. ★ **이벤트 payload에 `ownerId`를 얹지 않는다(전면 비포함)** — IS-1 6종은 **저장 모델** 대상이다(초안 문면 "이벤트에만"은 오독이었다 — 사용자 보정): 자금 이벤트 = 원장 언어(IS-5) · 내부 이벤트 = 구독자 없음 · 운영 이벤트 = 스코프는 소비 시점 판정. 테넌트 축은 형태만(IS-7 — 필드 예약 안 함).
- 감사 AD-8 스코프 칸 = ★ **판정에 실제 쓰인 스코프 값**(운영자 = 조직 축 값 · 고객 = 소유 · ★ **시스템 채널 = 대상의 소유 축**(IS-2 형태) · **축 없는 대상(예약·파일·배치·감사 자신(AD-5 재귀 차단 유도)) = 없음(null) + 대상 식별자**) — 재현 가능성 기준, 혼재 해소. ★ **null·전사 스코프 감사 행의 조회 자격 = ★ 루트 스코프 `AUDITOR`만**(2026-08-06 **C7 D-5 전환** — L1-25. 구 표기 *"전사 스코프 책임자만"*(D-UC20 ㉠)을 **대체**한다: 감사 열람은 **AUDITOR 전용**이 되어 책임자는 어떤 스코프에서도 열람하지 못한다. 조건 구조 — *null은 전사보다 좁을 수 없다* — 는 그대로이고 **주체만 갈렸다**. 정본 = UC-20 §7 · ADR-017 AD-5·AD-8).

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v0.14 | 2026-08-06 | **재점검 정정 — 항목 2**: K-1 판정 순서 항에 ★ **시스템 채널(전문·파일) = X-10 정본** 분기 1문 추가(① 인자 형식 → ② 멱등 단락 → ③ 대상 존재 → ④ 상태 — 재수신이 대상 조회보다 앞선다). **사람 채널 순서는 불변** |
| v0.13 | 2026-08-06 | **C7 리뷰 루프 1 반영 — L1-15·25**: 엔드포인트 색인에 ★ **C7 관리 API 이월 행** + **색인이 현재 전수가 아니라는 명시**(BR-58 전수 시험 입력의 공백 — L1-15) · **K-4의 null·전사 감사 행 조회 자격을 AUDITOR로 전환**(구 "전사 스코프 책임자만"을 D-5가 대체 — L1-25) |
| v0.13 | 2026-08-06 | K-2에 `DEPOSIT-ADV/RES` 확장 · 코드 대장 +1(`VOIDED_BY_RESERVATION` — 예약 소비 거절, BR-22 사유 구분) · SM 카드 3코드(CF3·4·6)를 승인 거절 사유 구분에 재사용 명시(DECLINED_CARD 3분 — BR-15) |
| v0.12 | 2026-08-06 | **리뷰 반영(듀얼 1패스)** — 선례 승계 코드 절(F9·F3: AUTH_CAPTURED 철회 → F1 재사용) · K-1 순서 재기술(F10) · K-4 null 조회 자격(F1) · 색인: UC-19 행 확정·축 열 확정·B-12 본표 병합(F4·F5·OQ8) |
| v0.11 | 2026-08-06 | U-2b — UC17-1 유도 스코프 확정 반영(색인 2행) · `INVALID_CURSOR` 코드 대장 등재 |
| v0.10 | 2026-08-06 | **U-2 판정 통합** — K-4 보정(이벤트 ownerId 전면 비포함 — 사용자)·시스템/축없음 감사 스코프 · **신설 코드 대장**(K-1 창구) · R15 지시 이벤트 이름 확정 · S-9 열 일괄 1 · 이벤트 색인 +2(ReceivableIncurred·WrittenOff — B-12) |
| v0.9 | 2026-08-06 | ★ **계약 공통 규약 §5 신설**(K-1~4 — 사용자 합의 4묶음: 오류·멱등(CDS3 일반화 + PUT 자연 멱등 = o-OQ5 판정) · 명명(전문 이름 확정) · S-9(schemaVersion 1·새 타입 원칙) · 축·감사 스코프) + 색인 [미정] 4행 해제 |
| v0.8 | 2026-08-06 | **정본 판정 반영 ③** — 행위자 판정 2종 확정(CardTerminated 비포함·JournalReversed 포함) 색인 반영 |
| v0.7 | 2026-08-06 | **정본 판정 반영 ②** — M19 신설(UC10-1)·자동 재분류(UC14-2) 착지: 도출표 +1행(`reclassifyIsolated` 내부) |
| v0.6 | 2026-08-06 | **정본 판정 반영 ①** — 계좌 조작 2신설 착지(UC6-1·UC13-1 확정): 엔드포인트 +1(재부과)·이벤트 색인 2행·도출표 2행 갱신 |
| v0.5 | 2026-08-05 | **듀얼 1패스 반영** — ★ UC-17 엔드포인트 2행 누락 복구 + 목록 조회 2건 신설(불일치 목록·승인 대기 — F-1·F-4) · 도출표에 **조회 표면(4번째 원천)** 추가·isolate 판정 정정(F-4·F-5) · 이벤트 색인 판정 대기 분리·누락 3행(F-6) · UC-06 주체별 행 분리(F-10) · 승인 요청 공통 행 ①~⑤ 정정(OQ1) |
| v0.4 | 2026-08-05 | **전수 통합 (U-3)** — 대장 16행 확정·엔드포인트 15행·이벤트 3묶음 행 추가(워커 4군 packet 통합 — 같은 커밋 등재 C-6). 전문·파일 인터페이스 명칭은 전부 [미정 — 계약 전수에서 일괄] |
| v0.3 | 2026-08-05 | **듀얼 1패스 반영** — 이벤트 색인 신설(Q-6) · BR-56 공통 계약 정본 위치 표시(U-7) · 상태줄 정합(F-5) · ★ v0.1 이력의 "UC-01 등재"는 그 시점 사실이고 v0.2 갱신(UC-02~04·엔드포인트 7행)이 이력 없이 지나갔다(F-7) — 이 행이 그 정정이다 |
| v0.2 | 2026-08-05 | (이력 누락분 소급 — F-7) UC-02~04 등재 · 엔드포인트 7행 추가 |
| v0.1 | 2026-08-05 | 색인 신설 — UC-01 등재. 엔드포인트 색인이 QS-08 전수 시험의 입력임을 명시 |
