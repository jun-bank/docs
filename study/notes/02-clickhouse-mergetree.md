# 02. ClickHouse MergeTree 기초

> ES 세그먼트 실측 경험이 그대로 이식되는 영역. 개념 구조가 같아서 학습 비용 대비 효과가 가장 크다.

---

## 1. 대응 관계부터 잡기 (ES 경험의 이식)

| Elasticsearch | ClickHouse | 공통 성질 |
|---|---|---|
| 세그먼트(segment) | **파트(part)** | 불변, 백그라운드 병합 대상 |
| refresh로 세그먼트 생성 | INSERT 1회 = 파트 1개 | 소량 잦은 쓰기 = 파일 폭증 |
| 세그먼트 병합 | 파트 병합(merge) | I/O·CPU를 조회와 나눠 씀 |
| `_forcemerge` | `OPTIMIZE TABLE` | 수동 병합, 남발 금지 |
| 삭제 = tombstone | 삭제 = mutation(파트 재작성) | 제자리 수정 없음 |

**가장 중요한 한 문장**: `INSERT` 한 번이 **파트 하나**를 만든다. 행 1개짜리 INSERT를 1000번 하면 파트가 1000개 생긴다.

---

## 2. 파트 증식과 "Too many parts"

### 증상
```
DB::Exception: Too many parts (N). Merges are processing significantly slower than inserts.
```

이건 디스크가 꽉 찬 게 아니라 **인서트 속도가 병합 속도를 앞질렀다는 백프레셔 신호**다.

### 관련 설정 (버전별 기본값이 다르므로 실제 값은 서버에서 확인)
| 설정 | 의미 |
|---|---|
| `parts_to_delay_insert` | 이 수를 넘으면 인서트를 인위적으로 지연시킴 (1차 경고) |
| `parts_to_throw_insert` | 이 수를 넘으면 예외 발생 (2차 차단) |
| `max_parts_in_total` | 테이블 전체 파트 수 상한 |
| `background_pool_size` | 병합에 쓸 스레드 수 |

```sql
SELECT name, value FROM system.merge_tree_settings
WHERE name LIKE '%parts_to%';
```

### 원인 3가지와 처방

| 원인 | 처방 |
|---|---|
| 소량 인서트가 너무 잦음 | **배치로 묶기** (수만 행 단위) 또는 `async_insert` |
| **파티션이 너무 잘게 쪼개짐** | 파티션 키를 성기게 (일 단위 → 월 단위). *병합은 파티션 내부에서만 일어난다* |
| 병합 처리량 부족 | 디스크/CPU 증설, `background_pool_size` 조정 |

> **가장 흔한 진짜 원인은 과도한 파티셔닝이다.** 파티션 수 × 파트 수로 곱해지기 때문. 파티션 개수는 보통 수백~수천 이하를 목표로 잡는다.

---

## 3. 모니터링 쿼리 (실측 습관 이식)

```sql
-- 테이블별 파트 수 / 크기 (active 파트만)
SELECT database, table,
       count() AS parts,
       sum(rows) AS rows,
       formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY parts DESC;

-- 파티션별 파트 수 (과도한 파티셔닝 탐지)
SELECT table, partition, count() AS parts
FROM system.parts WHERE active
GROUP BY table, partition
ORDER BY parts DESC LIMIT 20;

-- 지금 돌고 있는 병합
SELECT table, elapsed, progress, num_parts,
       formatReadableSize(total_size_bytes_compressed) AS size,
       formatReadableSize(memory_usage) AS mem
FROM system.merges;

-- 병합 이력 (사후 분석용, part_log 활성화 필요)
SELECT event_time, table, event_type, rows, duration_ms
FROM system.part_log
WHERE event_type = 'MergeParts'
ORDER BY event_time DESC LIMIT 50;

-- 복제 지연 / 큐 적체 (ReplicatedMergeTree)
SELECT database, table, absolute_delay, queue_size, inserts_in_queue, merges_in_queue
FROM system.replicas;
```

> `system.parts`의 `active` 컬럼 주의: 병합 후에도 옛 파트 행이 한동안 남아 있다. `WHERE active`를 빼먹으면 파트 수가 부풀려 보인다.

---

## 4. 소량 인서트 대책: async_insert

애플리케이션에서 배치를 못 묶는 상황(여러 인스턴스가 각자 소량 전송)의 표준 해법. **서버 쪽에서 버퍼링해서 묶는다.**

```sql
SET async_insert = 1;
SET wait_for_async_insert = 1;   -- 버퍼 플러시까지 대기 (내구성 ↑, 레이턴시 ↑)
-- SET wait_for_async_insert = 0; -- 즉시 반환 (처리량 ↑, 유실 창 존재)
SET async_insert_max_data_size = 10000000;  -- 버퍼 크기
SET async_insert_busy_timeout_ms = 1000;    -- 최대 대기 시간
```

**트레이드오프가 핵심**: `wait_for_async_insert = 0`이면 클라이언트가 성공 응답을 받은 뒤 서버가 죽으면 **유실된다**. 이건 06번 문서(아웃박스 vs 발송 로그)의 "유실 창" 이야기와 정확히 같은 구조의 선택이다.

대안: `Buffer` 테이블 엔진 (메모리 버퍼 → 주기적 플러시. 서버 크래시 시 유실).

---

## 5. 쿼리 비용을 결정하는 두 개의 키

이게 MergeTree 설계의 90%다.

```sql
CREATE TABLE events (
    ts        DateTime,
    tenant_id UInt32,
    metric    LowCardinality(String),
    value     Float64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)          -- 파티션 키
ORDER BY (tenant_id, metric, ts)   -- 정렬 키 (= 기본 키)
TTL ts + INTERVAL 90 DAY;
```

### ORDER BY (정렬 키)
- 파트 내부의 **물리적 정렬 순서**이자 **희소 인덱스(sparse primary index)**의 기준.
- ClickHouse는 행 단위 인덱스가 아니라 `index_granularity`(기본 8192행)마다 한 개의 마크만 저장한다. → 인덱스가 작아서 메모리에 상주한다.
- **원칙**: 카디널리티 낮은 컬럼 → 높은 컬럼 순. 그리고 **거의 모든 쿼리에 들어가는 필터 컬럼을 맨 앞에.**
- 정렬 키 접두사(prefix)로 필터링해야 그래뉼 스킵이 된다. `WHERE metric = 'x'`만 있고 `tenant_id` 조건이 없으면 위 예시에서는 스킵이 잘 안 된다.
- 압축률에도 직결된다. 비슷한 값이 인접하면 압축이 훨씬 잘 된다.

### PARTITION BY (파티션 키)
- 목적은 인덱싱이 **아니다.** 목적은 (1) 파티션 프루닝 (2) `DROP PARTITION` / TTL로 대량 삭제를 O(1)로 만들기.
- **병합은 파티션 경계를 넘지 않는다** → 파티션을 잘게 쪼개면 파트가 곱하기로 늘어난다.
- 실무 기본값: **월 단위(`toYYYYMM`)**. 일 단위는 보관 기간이 짧고 일 단위 삭제가 필수일 때만.

### 확인 방법
```sql
EXPLAIN indexes = 1
SELECT ... FROM events WHERE ...;
-- 읽은 파트 수 / 그래뉼 수를 보고 프루닝이 먹었는지 확인
```

---

## 6. 알아두면 좋은 변형 엔진

| 엔진 | 용도 | 함정 |
|---|---|---|
| `ReplacingMergeTree` | 최신 버전만 남기는 upsert 흉내 | **병합 시점에만** 중복 제거됨 → 조회 시 `FINAL` 또는 집계로 보정 필요 |
| `SummingMergeTree` | 같은 키의 숫자 컬럼 합산 | 위와 동일. 즉시 반영 아님 |
| `AggregatingMergeTree` | 사전 집계 상태 저장 (`*State`/`*Merge`) | 04번 롤업 설계의 표준 구현체 |
| `ReplicatedMergeTree` | Keeper 기반 복제 | 01번 문서의 fetch 설정 참고 |

> `ReplacingMergeTree`를 "중복 없는 테이블"로 오해하는 게 가장 흔한 사고. **최종적 일관성**이지 즉시 유일성 보장이 아니다.

---

## 7. 면접용 한 문단 요약

> MergeTree는 INSERT마다 불변 파트를 만들고 백그라운드로 병합한다. 구조가 Lucene 세그먼트와 같아서, 소량 잦은 인서트가 파트를 폭증시켜 "Too many parts"로 인서트를 막는 백프레셔가 걸린다. 그래서 배치 인서트나 async_insert로 묶고, 파티션 키는 병합이 파티션을 넘지 않는다는 점 때문에 성기게 잡는다. 쿼리 비용은 ORDER BY 키가 결정하는데, 희소 인덱스라 정렬 키 접두사로 필터링해야 그래뉼 스킵이 먹는다. 운영에서는 system.parts로 파티션별 파트 수를, system.merges와 part_log로 병합 처리량을 본다.
