# API 레퍼런스 (생성 문서 — 수기 편집 금지)

> `tools/gen_api_reference.py`가 **usecases/README.md §2 색인**(스파인)과 **각 UC §7 계약 블록**에서 생성한다.
> 의미의 정본은 각 UC §7이다 — 이 표는 조회 창구다. 갱신 = 재생성(검사가 drift를 잡는다).

| 인터페이스 | UC | 주체 | L7/비고 | 멱등 (§7 발췌) |
|---|---|---|---|---|
| 전문 `AUTH-REQ` | UC-01 | 시스템(매입사 경로) | ✕ — 사유 구분이 **BR-36·15 정본 특칙** (UC1-1 ✅ 닫힘 · C-2 채널 조항) | (§7 참조) |
| `POST /ops/approval-requests` ★ **BR-56 공통 계약 정본 = UC-02 §7** (U-7) | UC-02 | 운영자 담당자+ | ✅ 대상 부재·스코프 밖 동일 · 판정 순서 = 스코프 먼저 | 비멱등 — 중복 요청은 각각 `PENDING`으로 남고 방치 통지(BR-53 계열)가 잡는다. *(리뷰 확인 요청 — 멱등 필요?)* |
| `POST /ops/approval-requests/{id}/approve·reject` | UC-02 | 운영자 책임자 | ✅ (SELF_APPROVAL은 비노출 제외 — UC2-2) | (§7 참조) |
| `POST /ops/accounts/{accountId}/deposit-reversals` | UC-02 | 운영자 담당자(=maker) | ✅ 계좌 부재·스코프 밖 동일 |  `(기관, reversalId, 정정)` — DepositReceipt INV-1(2026-08-06 R-06: 채널 키의 유일성 스코프는 발신 기관이다).  `reversalId`는 우리가 채번하므로(운영자 지시… |
| `GET /me/accounts/{accountId}/balance` | UC-03 | 고객(본인) | ✅ ★ QS-08 원형 | 조회 — 자연 멱등 |
| `GET /me/accounts/{accountId}/transactions` | UC-03 | 고객(본인) | ✅ 목록·페이징 포함 | 조회 — 자연 멱등 (커서 = offset 아님 — backlog 조회 기준) |
| `POST·DELETE /me/cards/{cardId}/suspension` | UC-04 | 고객(본인) | ✅ | 비멱등 — 재신고는 명시 거절(CF9. 거절이 멱등 경계 역할) |
| `POST·DELETE /ops/cards/{cardId}/suspension` | UC-04 | 운영자 담당자 | ✅ 스코프 밖 동일 | (§7 참조) |
| `POST /me/cards/{cardId}/termination` | UC-05 | 고객(본인) | ✅ · 운영자 경로 없음(BR-55 각주) | 비멱등 — 상태 전이가 멱등 경계. 재요청은 명시 거절 `ALREADY_TERMINATED`(CF8 · K-1: 사람 채널의 상태 전이 재요청은 무음 무시 금지 — 무시하면 요청자가 상태를 오인한다). UC-04 정… |
| `PUT /me/cards/{cardId}/limits` | UC-06 | 고객(본인) | ✅ |  PUT 값 교체 = 자연 멱등 — 동일 값 재요청은 성공(K-1 · o-OQ5 판정). 상태 전이가 아니므로 `ALREADY_*` 계열이 없다(UC-04·UC-05와 갈리는 지점). 승인과의 경합은 카드 단위 낙관… |
| `PUT /ops/cards/{cardId}/limits` | UC-06 | 운영자 담당자 | ✅ 스코프 밖 동일 | (§7 참조) |
| `PUT /me/accounts/{accountId}/daily-limit` | UC-06 | 고객(본인) | ✅ | PUT 값 교체 = 자연 멱등(K-1 — 동일 값 재요청 = 성공). 승인과의 경합은 계좌 단위 낙관적 락(§4-I) |
| `PUT /ops/accounts/{accountId}/daily-limit` | UC-06 | 운영자 담당자 | ✅ | (§7 참조) |
| 전문 `DEPOSIT-ADV` (K-2 확정) | UC-07 | 시스템(입금원 경로) | ✕ 시스템 채널(C-2) · 거절 형태 UC7-3 | (§7 참조) |
| 전문 `CANCEL-REQ/RES` (K-2 확정) | UC-08 | 시스템(매입사 경로) | ✕ 사유 구분(C-2 특칙) | (§7 참조) |
| 전문 `REVERSAL-REQ/RES` (K-2 확정) | UC-09 | 시스템(매입사 경로) | ✕ 〃 · 원승인 없음 = 예약(존재 비누설) | (§7 참조) |
| 파일 `CAPTURE-FILE` (K-2 확정) | UC-10·11 | 시스템(배치 — 예외 ②) | 해당 없음(응답 상대 없음 — 격리+불일치) | (§7 참조) |
| `POST·DELETE /ops/authorizations/{authorizationId}/freeze` | UC-12 | 담당자(개설 조직) | ✅ | 비멱등 — 재보류는 명시 거절(`ALREADY_FROZEN`). 플래그 전이가 멱등 경계이고 그 거절이 경계를 드러낸다(K-1 CDS3) |
| `POST·DELETE /ops/receivables/{receivableId}/freeze` | UC-12 | 담당자(accountId 귀속) | ✅ | 비멱등 — 재보류는 명시 거절(`ALREADY_FROZEN` — 승인 보류와 동일. K-1 CDS3) |
| `POST /ops/accounts/{accountId}/receivable-block-lifts` | UC-13 | 담당자(=maker) — BR-56 ② | ✅ | 비멱등 —  승인 요청 1건 = 1회 소비(INV-2)가 실질 멱등 경계다: 같은 승인 요청 ID로 재실행하면 `CONSUMED` 종료 상태라 AF5로 거절된다. 계좌 플래그 자체의 재요청도 명시 거절(`ALREAD… |
| `POST /ops/accounts/{accountId}/receivable-block-reimpositions` | UC-13 | 담당자 — 승인 절차 없음(안전 방향) | ✅ | 비멱등 — 재요청은 명시 거절(`ALREADY_BLOCKED`). 거절이 멱등 경계다(K-1 CDS3) |
| `POST /ops/capture-batches/{institution}/{fileId}/isolated-records/{recordId}/promotion` | UC-14 | 담당자(=maker) · 전사 — BR-56 ③ | △ 부재만 NOT_FOUND(축 없음 — BR-55 특칙. ★ 경로에 기관 — R-06 키 `(기관, fileId)` 귀결) | (§7 참조) |
| (승인 요청 공통 계약 `POST /ops/approval-requests` — **①~⑤ 전부** 사용, 정본 = UC-02 §7 · ④⑤만 ★ 실행 엔드포인트 없음 — R15 지시 이벤트) | UC-02·13·14·15·16 | 담당자(=maker) | 대상별 (④ ✕ 영업일 / ⑤ ✅ 원전표 / ①②③ ✅) | 비멱등 — 중복 요청은 각각 `PENDING`으로 남고 방치 통지(BR-53 계열)가 잡는다. *(리뷰 확인 요청 — 멱등 필요?)* |
| ★ `GET /ops/approval-requests` (승인 대기·내 요청 목록 — BR-56 워크플로의 전제 조회. 리뷰 F-4가 발견한 누락) | UC-02 공통 | 담당자(내 요청) / 책임자(대기 목록) · 스코프 | ✅ | 비멱등 — 중복 요청은 각각 `PENDING`으로 남고 방치 통지(BR-53 계열)가 잡는다. *(리뷰 확인 요청 — 멱등 필요?)* |
| `POST /ops/discrepancies/{discrepancyId}/investigation` · `/resolution` | UC-17 | 운영자 담당자 | ✅ 유도 스코프(UC17-1 확정) | 비멱등 — 재호출은 명시 거절(DF4).  거절이 멱등 경계다 |
| ★ `GET /ops/discrepancies` (목록 — UC-17 §3의 전제 조회. 리뷰 F-1이 발견한 누락) | UC-17 | 운영자 조회 이상 | ✅ 유도 스코프(UC17-1 확정) | 조회 — 자연 멱등. 커서는 전순서 키이므로 재호출이 같은 창을 준다(offset 아님) |
| `POST /ops/reconciliations` · `GET /ops/reconciliations/{runId}` | UC-18 | 담당자·전사 / 조회+ | ✕ 영업일 축 |  같은 영업일 재실행은 정상 동작이고 멱등이다(§4-B — `lastDetectedOn`이 그 영업일이면 `detectionCount`가 오르지 않는다: BR-48 · INV-2. *발견 횟수 ≈ 미해결 영업일 수*… |
| `GET /ops/dlq` · `POST /ops/dlq/{outboxRecordId}/replay` | UC-19 | 조회+ / 담당자 · 전사 | ✕ · payload = 메타만(D-UC19 확정 — partition=계좌ID 노출은 명시) | 조회 — 자연 멱등 (커서 = offset 아님) |
| `GET /ops/audit-records` · `/{recordId}` | UC-20 | ★ **AUDITOR** · grant 스코프 서브트리(축 없는 기록 = **루트 스코프만**) — 2026-08-06 C7 D-5 완전 분리(구 "책임자" 대체) | ✅ 목록·집계 포함(BR-58 전 형태) | 조회 — 자연 멱등 (커서 = offset 아님).  기록 적재 쪽의 멱등은 `sourceRef` = 조회 요청 식별자(AD-3) — 같은 요청이 두 번 적재되지 않는다 |
| ★ **C7 관리 API 전체 — 명시 이월** (2026-08-06 루프 1 **L1-15**): 조직(`OrgUnit.create`·`close`·**조회 표면** — 트리·형제 열거 차단) · 운영자(`register`·`suspend`·`resume`·`terminate`·`transfer`) · 권한(`RoleGrant.issue`·`revoke`·`recertify` — **BR-56 ⑥ 승인 요청의 인자 스키마 포함**) · 회원(`Member.*` — 해지 2단계) | **미작성** — 후속 패스 | 운영자(단계·스코프는 **BR-55 배정 표**가 이미 정본) | ⚠️ **이 행이 비어 있는 동안 BR-58 전수 시험의 입력이 불완전하다** — 아래 주 참조 | (§7 참조) |

> 행 30개 = 색인 §2 전수 · §7 멱등 발췌 19건 · 물리 규격 = [`interfaces/`](interfaces/README.md) · 이벤트 = 색인 §3 · 오류 코드 창구 = 색인 §5 코드 대장.
