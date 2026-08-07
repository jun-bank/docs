# 백엔드 학습 노트 (전체 인덱스)

3개 세트로 구성되어 있다.

```
notes/
├── 00~08              단일 주제 심화 노트 (교정된 이해 기준)
├── axes/              개발 평가 축 7개 — 각각 독립 문서
└── server-design/     고가용성·확장성 서버 설계 — 12개 문서
```

---

## A. 단일 주제 노트 (00~08)

| # | 문서 | 한 줄 요약 |
|---|---|---|
| 00 | [개발 분야별 평가 축 (요약)](./00-engineering-axes.md) | 축 7개 압축 정리 → 상세는 `axes/` |
| 01 | [LSM 병합 모델](./01-lsm-merge-model.md) | 정렬은 쓰기 시점에 끝난다. 컴팩션은 머지 소트, 비용은 자원 경쟁 |
| 02 | [ClickHouse MergeTree](./02-clickhouse-mergetree.md) | INSERT = 파트 1개. Too many parts, async_insert, 키 설계 |
| 03 | [PostgreSQL RLS](./03-postgres-rls.md) | WHERE를 빼먹어도 DB가 거른다. 커넥션 풀·정책 비용 함정 |
| 04 | [시계열 해상도 계층](./04-timeseries-resolution-tiers.md) | 다운샘플링 ≠ 부정확. min/max/count 보존, 감지는 원본에서 |
| 05 | [Kafka 소비 측 실패 처리](./05-kafka-consumer-failure.md) | 오프셋 커밋 순서가 유실/중복을 결정. at-least-once + 멱등 소비 |
| 06 | [아웃박스 vs 발송 로그](./06-outbox-vs-dispatch-log.md) | 저장 시점이 닫는 실패 계열을 결정. 사건형 이벤트는 아웃박스 필수 |
| 07 | [실패 지점 되짚기 습관](./07-failure-point-checklist.md) | (절차) 답하기 전 5칸 중 어디인지 확정하고 시작 |
| 08 | [평가 축 확장판](./08-engineering-axes-deep.md) | 축 간 트레이드오프, 교차 번역, 경험 번역 템플릿 |

---

## B. [평가 축 개별 문서](./axes/) — 7개

각 축을 "무엇을 지키는 활동인가"로 정의하고, **자기 경험을 그 언어로 번역**하기 위한 세트.

| 축 | 지키는 것 |
|---|---|
| [Concurrency](./axes/concurrency.md) | 정확성 — 데이터가 조용히 틀리지 않게 |
| [Scalability](./axes/scalability.md) | 성장 여력 — 10배가 되면 뭐가 먼저 터지나 |
| [Availability](./axes/availability.md) | 연속성 — 일부가 죽어도 서비스는 산다 |
| [Performance](./axes/performance.md) | 속도 — p99가 체감 성능이다 |
| [System Design](./axes/system-design.md) | 변경 비용 — 되돌릴 수 있는가 |
| [Maintainability](./axes/maintainability.md) | 인수인계 가능성 — 6개월 뒤에 고칠 수 있나 |
| [UX](./axes/ux.md) | 사용 가능성 — 백엔드 p99도 UX다 |

---

## C. [고가용성 · 확장성 서버 설계](./server-design/) — 12개

**어떤 상황에서 어떤 설계와 기법이 있는가**의 카탈로그.

| # | 문서 | 다루는 것 |
|---|---|---|
| 01 | [확장의 기본 원리](./server-design/01-scaling-principles.md) | 병목 이동, Little's Law, USL, 무상태화 |
| 02 | [요청 경로 계층별 설계](./server-design/02-request-path.md) | DNS/CDN/LB/게이트웨이, 헬스체크, graceful shutdown |
| 03 | [데이터 계층 확장](./server-design/03-data-layer.md) | 복제 지연, 파티셔닝, 샤딩, 리샤딩, CQRS |
| 04 | [캐시 설계](./server-design/04-caching.md) | 무효화, 스탬피드·관통·눈사태, 핫키 |
| 05 | [고가용성 토폴로지](./server-design/05-ha-topology.md) | 가용성 합성, failover, split-brain, 다중 AZ/리전 |
| 06 | [장애 격리와 복원력](./server-design/06-resilience.md) | 타임아웃, 재시도, 서킷 브레이커, 벌크헤드, 로드 셰딩 |
| 07 | [비동기 · 메시징](./server-design/07-async-messaging.md) | 큐 vs 로그, 백프레셔, 순서, 스케줄러 HA |
| 08 | [배포와 운영](./server-design/08-deployment-ops.md) | 무중단 배포, 마이그레이션, 롤백, 골든 시그널 |
| 09 | [용량 산정 · SLO](./server-design/09-capacity-slo.md) | 에러 버짓, 사이징, 부하 테스트, 오토스케일링 |
| **10** | **[상황별 플레이북](./server-design/10-playbook-by-symptom.md)** | **증상 → 진단 → 처방 (실전용)** |
| 11 | [안티패턴 모음](./server-design/11-antipatterns.md) | 하지 말아야 할 것 29가지 |

---

## 목적별 진입점

| 상황 | 어디부터 |
|---|---|
| **면접 준비 (구조 잡기)** | `axes/README.md` → 관심 축 개별 문서 |
| **면접 준비 (답변 연습)** | 각 문서 말미의 "면접에서 말하는 방식" |
| **설계 리뷰 / 신규 설계** | `server-design/README.md` → 01, 05, 06 |
| **지금 장애·성능 문제가 있음** | `server-design/10-playbook-by-symptom.md` |
| **뭘 하지 말아야 하나** | `server-design/11-antipatterns.md` |
| **절차 습관 교정** | `07-failure-point-checklist.md` |
| **특정 기술 (LSM/CH/RLS/Kafka)** | `01`~`06` |

---

## 문서 간 연결 지도

```
07 실패 지점 5칸 절차 ─────▶ 모든 파이프라인 논의의 프레임

01 LSM ──▶ 02 ClickHouse ──▶ 04 시계열 해상도 계층
                              (AggregatingMergeTree로 롤업)

06 아웃박스 ──▶ 05 Kafka 소비 측
   │              (아웃박스의 중복을 멱등 소비가 흡수)
   └──▶ server-design/03 데이터 계층, /07 비동기

axes/scalability  ──▶ server-design/01, 03, 04, 09
axes/availability ──▶ server-design/05, 06, 08
axes/concurrency  ──▶ 05, 06
전 축 실전        ──▶ server-design/10 플레이북
```

---

## 핵심 원칙 (전체 관통)

1. **확장은 병목을 없애는 게 아니라 옮기는 것이다** — 지금 병목이 어디인지 말할 수 있어야 한다
2. **타임아웃이 없으면 다른 모든 복원력 장치가 무의미하다**
3. **가용성은 의존성마다 곱셈으로 떨어진다** — 그래서 격리가 필수
4. **가용성을 가장 많이 깎는 건 고장이 아니라 변경이다** — 롤백 가능성이 곧 MTTR
5. **테스트하지 않은 복원력은 복원력이 아니다** — failover·백업 복원을 실제로 해본다
6. **저장 시점이 닫는 실패 계열을 결정한다** — 아웃박스 vs 발송 로그
7. **답변은 "다 좋게 만들었다"가 아니라 "무엇을 위해 무엇을 내줬다"의 형태여야 한다**

---

## 손으로 확인해볼 것

| 문서 | 실습 |
|---|---|
| 01 | db-engine-lab에 LSM 추가 → **병합 스레드 on/off에 따른 조회 p99 차이 측정** |
| 02 | 1행 INSERT 1000회 → `system.parts`로 파트 폭증 관찰 → `async_insert` 후 재측정 |
| 03 | 테넌트 A 컨텍스트에서 B 데이터에 대한 SELECT/INSERT/UPDATE/DELETE 4종이 모두 막히는지 |
| 05 | 컨슈머를 처리 중 강제 종료 → 자동 커밋 on/off로 유실 vs 중복이 갈리는지 재현 |
| server-design/04 | **캐시를 통째로 내린 상태에서 DB가 버티는지** 부하 테스트 |
| server-design/06 | 의존성에 지연 주입 → 타임아웃·서킷 브레이커가 실제로 동작하는지 |
| server-design/05 | DB failover 실행 → 앱이 자동 재연결하는지 |
