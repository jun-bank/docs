# 04. 시계열/관제 제품의 해상도 계층 설계

> 반론에 대한 답: **"다운샘플링 = 부정확"은 틀렸다.**
> 사전 집계는 **버킷 단위로는 정확한 집계**다. 잃는 것은 **버킷 내부의 디테일뿐**이고, 그 디테일이 필요한 경로는 애초에 따로 있다.

---

## 1. 문제 설정

관제 제품에서 충돌하는 두 요구:
- 최근 몇 분의 이상 징후는 **초 단위**로 봐야 한다
- 6개월 추이는 **한 화면**에 떠야 한다

원본 해상도로 6개월을 그리면 수억 포인트를 읽어 화면의 1000픽셀에 그린다. **어차피 화면에서 다운샘플링된다.** 그럴 거면 저장 시점에 하는 게 맞다.

---

## 2. 답변 1 — 조회 창에 비례한 해상도 (다중 해상도 계층)

```
조회 창          제공 해상도     저장 계층
─────────────────────────────────────────
~ 6시간          1초 (원본)      raw
~ 2일            10초            rollup_10s
~ 2주            1분             rollup_1m
~ 6개월          5분             rollup_5m
6개월 ~          1시간           rollup_1h
```

핵심 원칙:

1. **화면 픽셀 수를 넘는 포인트는 정보가 아니다.** 1000px 그래프에 100만 포인트를 보내는 건 낭비이자 렌더 지연.
2. **쿼리 라우터가 조회 창을 보고 계층을 자동 선택**한다. 사용자는 "해상도"를 고르지 않는다.
3. 각 계층은 TTL이 다르다. raw는 짧게, 상위 계층은 길게 → **저장 비용이 지수적으로 줄어든다.**
4. 계층 경계에서 그래프가 튀지 않도록, 경계를 넘는 조회는 한 계층으로 통일해서 읽는다.

---

## 3. 답변 2 — 롤업 버킷에 avg만 저장하지 않는다 (스파이크 보존의 핵심)

**"평균 내면 스파이크가 사라진다"는 지적은 avg만 저장할 때만 맞다.**

버킷마다 이렇게 저장한다:

| 필드 | 이유 |
|---|---|
| `min`, `max` | **스파이크 보존.** 1분 버킷의 max는 그 1분 안의 진짜 최댓값이다 — 근사가 아니다 |
| `sum`, `count` | 평균을 나중에 정확히 계산하기 위해 |
| `last` | 게이지형 지표의 현재 상태 |
| 히스토그램/스케치 | 분위수(p95, p99)를 위해 |

### 계층적 재집계(rollup of rollup)가 성립하는가 — 함수별 정리

| 함수 | 재집계 가능? | 방법 |
|---|---|---|
| `max` | ✅ 정확 | max of maxes |
| `min` | ✅ 정확 | min of mins |
| `sum` | ✅ 정확 | sum of sums |
| `count` | ✅ 정확 | sum of counts |
| `avg` | ⚠️ 조건부 | **sum/count로 계산해야 정확.** avg of avgs는 틀림 (버킷별 샘플 수가 다르면 가중치가 깨짐) |
| `p95`, `p99` | ❌ 불가 | **분위수는 평균낼 수 없다.** t-digest / HDR 히스토그램 같은 **머지 가능한 스케치**를 저장해야 함 |
| `distinct count` | ❌ 불가 | HyperLogLog 같은 스케치 필요 |

> 이 표가 "다운샘플링은 부정확"이라는 주장에 대한 정확한 반박이자, 동시에 **그 주장이 부분적으로 맞는 지점**(분위수, 고유 카운트)을 정확히 짚는다. 면접에서 이 구분을 하면 신뢰도가 크게 올라간다.

**대표적인 실무 사고**: 서버별 p99를 저장해두고 나중에 평균 내서 "전체 p99"라고 부르는 것. 수학적으로 무의미하다.

---

## 4. 답변 3 — 감지(알림)는 대시보드 경로에서 하지 않는다

**가장 중요한 구조적 분리.**

```
                    ┌─▶ [알림 평가]  ← 원본 스트림에서 즉시 평가
수집 → 원본 스트림 ─┤
                    └─▶ [저장/롤업] ─▶ [대시보드 조회]
```

| | 감지 경로 | 조회 경로 |
|---|---|---|
| 입력 | 원본 스트림 (풀 해상도) | 롤업된 저장소 |
| 요구 | 낮은 지연, 놓치지 않기 | 넓은 범위, 빠른 렌더 |
| 지연 허용 | 초 단위 | 수 초~분 |
| 정확도 | 원본 그대로 | 버킷 단위로 정확 |

즉, **"다운샘플링해서 스파이크를 놓치면 어쩌냐"는 질문은 경로를 혼동한 것이다.** 스파이크 감지는 대시보드가 하는 일이 아니다. 대시보드는 사후에 "그때 무슨 일이 있었나"를 보여주는 도구고, 그 용도로는 버킷의 max로 충분하다. 그리고 원본이 필요하면 **해당 구간만 raw 계층에서 드릴다운**하면 된다.

> 이 구조가 있으면 다음 문장이 성립한다: **"롤업은 감지 정확도와 무관하다. 감지는 원본에서 하기 때문이다."**

---

## 5. 구현 형태

### ClickHouse (02번 문서와 연결)
```sql
-- 롤업 대상 테이블
CREATE TABLE metrics_1m (
    bucket    DateTime,
    metric    LowCardinality(String),
    cnt       AggregateFunction(count),
    sum_v     AggregateFunction(sum, Float64),
    min_v     AggregateFunction(min, Float64),
    max_v     AggregateFunction(max, Float64),
    q         AggregateFunction(quantilesTDigest(0.95, 0.99), Float64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (metric, bucket);

-- 원본 → 롤업 자동 반영
CREATE MATERIALIZED VIEW metrics_1m_mv TO metrics_1m AS
SELECT toStartOfMinute(ts) AS bucket, metric,
       countState()  AS cnt,
       sumState(value) AS sum_v,
       minState(value) AS min_v,
       maxState(value) AS max_v,
       quantilesTDigestState(0.95, 0.99)(value) AS q
FROM metrics_raw
GROUP BY bucket, metric;

-- 조회 (계층적 재집계도 State를 그대로 머지하면 정확)
SELECT bucket, maxMerge(max_v) AS mx,
       sumMerge(sum_v) / countMerge(cnt) AS avg_v,
       quantilesTDigestMerge(0.95, 0.99)(q) AS quantiles
FROM metrics_1m GROUP BY bucket;
```

`quantilesTDigestState`가 위 3절의 "머지 가능한 스케치"에 해당한다.

### 다른 스택
- **Prometheus**: recording rule로 사전 집계, 장기 보관은 Thanos/Cortex의 downsampling (5m/1h 계층을 count/sum/min/max/counter로 저장 — 위와 같은 원리)
- **VictoriaMetrics**: `-downsampling.period` 설정
- **TimescaleDB**: continuous aggregate + 계층적 continuous aggregate
- **InfluxDB**: continuous query / task

---

## 6. 면접용 한 문단 요약

> 다운샘플링이 부정확하다는 건 avg만 저장할 때 얘기다. 버킷에 min·max·sum·count를 함께 저장하면 max는 그 구간의 진짜 최댓값이라 스파이크가 보존되고, avg도 sum/count로 정확히 복원된다. 다만 분위수와 고유 카운트는 평균낼 수 없어서 t-digest나 HLL 같은 머지 가능한 스케치를 저장해야 한다. 그리고 구조적으로 더 중요한 건, 알림 평가를 대시보드 경로가 아니라 원본 스트림에서 한다는 점이다. 감지는 원본에서, 조회는 조회 창에 비례한 해상도 계층에서. 그래서 롤업은 감지 정확도와 무관하고, 잃는 건 버킷 내부 디테일뿐인데 그건 필요할 때 raw 계층으로 드릴다운하면 된다.
