# 애그리게이트: 매입 배치

- 작성일: 2026-08-03
- 상태: 검토대기
- 소속 컨텍스트: **C3 결제** (배치 경계)
- 코드명: `CaptureBatch`

---

## 1. 책임

> **매입 파일 한 건의 처리 진행 상태를 추적하고, 같은 레코드가 두 번 반영되지 않게 한다.**

배치가 중단·재개되는 것이 **정상 경로**다(S6). 그래서 "어디까지 처리했는가"를 애그리게이트가 소유한다.

---

## 2. 구성

| 필드 | 타입 | 뜻 |
|---|---|---|
| `fileId` | `SettlementFileId` | 파일 식별자 — **유일 키** |
| `businessDate` | `BusinessDate` | 이 파일이 귀속되는 영업일 (BR-14) |
| `status` | `BatchStatus` | 수신됨 / 처리중 / 중단됨 / 완료됨 |
| `totalRecords` | `int` | 파일의 전체 레코드 수 |
| `processedRecords` | `Set<CaptureRecordId>` | **처리 완료된 레코드 식별자** (BR-23) |
| `isolatedRecords` | `List<IsolatedRecord>` | 격리된 레코드 (BR-27·BR-32·BR-16 ③) |

> **레코드 식별자를 집합으로 든다.** 이것이 BR-23(파일 멱등)의 실체다. 재실행 시 이 집합에 있으면 건너뛴다.

---

## 3. 불변식

| # | 불변식 | 근거 | 위반 시 |
|---|---|---|---|
| **INV-1** | `fileId`는 유일하다 | BR-23 | 같은 파일이 두 번 처리 |
| **INV-2** | `processedRecords`에 같은 ID가 두 번 들어가지 않는다 | BR-23 | **이중 출금** |
| **INV-3** | `status = 완료됨` 이면 `\|processedRecords\| + \|isolatedRecords\| = totalRecords` | — | **부분 실패를 완료로 위장** |
| **INV-4** | `status = 완료됨` 이후 레코드가 추가되지 않는다 | — | 완료 후 변경 |

> ⚠️ **INV-3이 "에러 없이 돌았다 ≠ 완료"를 강제한다.** 건수로 판정하지 않으면 조용한 절단을 못 잡는다 (QS-09).

---

## 4. 조작

| 조작 | 코드명 | 사전조건 | 사후조건 | 이벤트 |
|---|---|---|---|---|
| **수신** | `receive(fileId, totalRecords, businessDate)` | INV-1 | 상태 = 수신됨 | `CaptureFileReceived` |
| **처리 시작** | `start()` | 상태 ∈ {수신됨, 중단됨} | 상태 = 처리중 | `CaptureBatchStarted` |
| **레코드 처리** | `markProcessed(recordId)` | 집합에 없음 (INV-2) | 집합에 추가 | — |
| **레코드 격리** | `isolate(recordId, reason)` | 집합에 없음 | 격리 목록에 추가 | `CaptureRecordIsolated` |
| **중단** | `interrupt(reason)` | 상태 = 처리중 | 상태 = 중단됨 | `CaptureBatchInterrupted` |
| **완료** | `complete()` | INV-3 | 상태 = 완료됨 | `CaptureBatchCompleted` |

### 재처리 (BR-23 · QS-09)

```
중단 → start() → 각 레코드에 대해
  if recordId ∈ processedRecords: 건너뛴다
  else: 처리 후 markProcessed()

완료 판정: |processed| + |isolated| = totalRecords    ← 건수로 검증 (INV-3)
```

### 취소 레코드 (BR-33)

파일에는 **매입 레코드와 취소 레코드가 섞여** 온다. 둘 다 `(fileId, recordId)` 멱등 대상이다(BR-33·HS8) — 적용하지 않으면 재처리 시 **환불이 두 번 반영**된다.

---

## 5. 격리 사유

| 사유 | 근거 | 불일치 유형 |
|---|---|---|
| 선행 승인 없음 | BR-27 | M2 미승인 매입 |
| 이미 매입된 승인 | BR-32 | M7 후속 매입 |
| 금액 초과 | BR-16 ③ | M4 금액 초과 매입 |

---

## 6. 경계 근거

| 질문 | 답 |
|---|---|
| **왜 이 범위인가** | 파일 멱등(INV-2)과 완료 판정(INV-3)이 **파일 한 건 안에서** 성립해야 한다 |
| **왜 더 크지 않은가** | 여러 파일을 묶으면 파일별 완료 판정을 못 한다 |
| **왜 더 작지 않은가** | `processedRecords`를 빼면 재실행 시 **중복 반영을 막을 수 없다** |
| **트랜잭션 단위인가** | **레코드 단위로 커밋**한다. 파일 전체를 한 트랜잭션으로 묶으면 대용량에서 락이 과도하고, 중단 시 진행분이 전부 사라진다 |

---

## 7. 미해결

| # | 의문 |
|---|---|
| **CB1** | `processedRecords`가 대용량일 때의 저장 방식 — 집합을 통째로 들면 메모리·직렬화 부담 (Phase 3 설계 사안) |
| **CB2** | 파일 자체가 손상되어 `totalRecords`를 못 읽으면? INV-3 판정 불가 |

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.0 | 2026-08-03 | 최초 작성 — 완료 판정을 건수로 강제(INV-3), 레코드 단위 커밋 |
