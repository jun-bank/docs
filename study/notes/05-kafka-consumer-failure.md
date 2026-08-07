# 05. Kafka 소비 측 실패 처리 체계

> 놓쳤던 자리: 파이프라인 신뢰성 질문에서 **소비 측 실패**를 다루지 않았다.
> 발행 측만 설명하면 "메시지를 보냈다"까지만 보장하고, "처리됐다"는 보장하지 못한다.

---

## 1. 전제: Kafka는 왜 ACK를 "물어보지" 않는가

RabbitMQ 같은 푸시형 브로커와 헷갈리기 쉬운 지점.

| | 푸시형 (예: AMQP) | Kafka |
|---|---|---|
| 전달 | 브로커가 컨슈머에게 밀어줌 | **컨슈머가 당겨감(pull)** |
| 메시지 상태 | 브로커가 메시지별 ack/unack 추적 | 브로커는 **오프셋 숫자 하나**만 기억 |
| 소비 후 | ack 오면 삭제 | **삭제 안 함.** 보존 기간까지 그대로 |
| 재처리 | 재전송 요청 | **오프셋을 되돌리면 됨** |

핵심: **Kafka는 보존형 로그다.** 메시지는 소비돼도 사라지지 않고, 컨슈머는 "내가 어디까지 읽었다"는 **커서(오프셋)**만 관리한다.

→ 그래서 "받았는지 물어보는" 확인 모델이 필요 없다. 대신 **오프셋을 언제 커밋하느냐**가 모든 신뢰성 논의의 중심이 된다.

---

## 2. 재시도가 붙는 자리는 두 군데다

```
[발행 측]                    [브로커]              [소비 측]
비즈니스 TX ─▶ 아웃박스           로그              poll ─▶ 처리 ─▶ 오프셋 커밋
                  │                                        │
              릴레이 재발행                            실패 시:
              (ack 전 미완료 유지)                    재시도 토픽 → DLT
```

### ① 발행 측
- 아웃박스에 저장 (06번 문서 참고) → 릴레이가 재발행
- **ack를 받기 전까지 아웃박스 행을 "미완료"로 유지** → 릴레이가 죽어도 다음 릴레이가 이어서 발행
- `acks=all`, `enable.idempotence=true`, `retries` 설정
- 결과: **최소 1회 발행 보장** (중복은 발생 가능)

### ② 소비 측
- 처리 실패 → **오프셋을 커밋하지 않음** → 재조회 시 같은 메시지를 다시 받음
- 즉시 재시도로 안 되는 경우 → **백오프 재시도 토픽**
- 끝까지 실패 → **DLT(Dead Letter Topic)로 격리**

---

## 3. 오프셋 커밋 순서 함정 (핵심)

**"처리"와 "커밋" 사이의 순서가 실패 계열을 결정한다.**

### 케이스 A — 처리 전 커밋 (`enable.auto.commit=true`가 사실상 이것)
```
poll → 오프셋 커밋 → 처리 중 크래시
결과: 재시작 시 이미 커밋된 지점 이후부터 읽음 → 건너뜀 = 유실
```
자동 커밋은 백그라운드에서 주기적으로(`auto.commit.interval.ms`) 커밋하므로, **처리 완료와 무관하게 커밋될 수 있다.** → **at-most-once**

### 케이스 B — 처리 후 커밋
```
poll → 처리 완료 → 커밋 직전 크래시
결과: 재시작 시 같은 메시지를 다시 받음 → 중복 처리
```
→ **at-least-once**

### 결론
```java
props.put(ENABLE_AUTO_COMMIT_CONFIG, false);  // 필수
// 처리 완료 후 수동 커밋 (Spring Kafka: AckMode.MANUAL / RECORD / BATCH)
```

**"정확히 한 번"은 소비 측에서 공짜로 얻어지지 않는다.** 처리와 커밋이 서로 다른 시스템(외부 DB와 Kafka)에 걸쳐 있어 원자적으로 묶을 수 없기 때문이다. 그래서 **at-least-once + 멱등 소비**가 현실적 표준이다.

> Kafka 트랜잭션(`read-process-write`, `isolation.level=read_committed`)은 **Kafka→Kafka 경로에서만** exactly-once를 준다. 외부 DB에 쓰는 순간 그 보장은 깨진다.

---

## 4. 멱등 소비 = 인박스 패턴 (전제 조건)

at-least-once를 선택했다면 **중복 처리가 반드시 온다.** 이걸 흡수하는 게 인박스다.

```sql
CREATE TABLE processed_messages (
    message_id  VARCHAR(100) PRIMARY KEY,   -- 유니크 제약이 방어선
    consumer    VARCHAR(50)  NOT NULL,
    processed_at TIMESTAMP   NOT NULL DEFAULT now()
);
```

```java
@Transactional
public void handle(Event e) {
    try {
        inboxRepo.insert(e.messageId(), CONSUMER_NAME);  // 중복이면 여기서 예외
    } catch (DuplicateKeyException dup) {
        return;   // 이미 처리됨 → 조용히 스킵
    }
    businessLogic(e);   // 인박스 삽입과 같은 트랜잭션
}
```

**중요한 두 가지**
1. **인박스 삽입과 비즈니스 로직이 같은 트랜잭션**이어야 한다. 아니면 "인박스만 기록되고 처리는 안 됨" 상태가 생긴다.
2. **`message_id`는 생산자가 만든 안정적 ID**여야 한다. Kafka 오프셋은 재발행 시 달라지므로 부적합하다.

**대안**: 비즈니스 로직 자체를 멱등하게 설계 (`UPDATE ... SET status='PAID' WHERE id=? AND status='PENDING'`, upsert 등). 별도 테이블 없이 가능하면 이쪽이 더 낫다.

---

## 5. 재시도 계층 설계

### 실패 종류부터 나눈다 (이걸 안 나누면 설계가 틀어진다)

| 종류 | 예시 | 대응 |
|---|---|---|
| **일시적(transient)** | DB 커넥션 끊김, 타임아웃, 429 | 재시도 O |
| **영구적(permanent)** | 역직렬화 실패, 스키마 불일치, 검증 오류 | **재시도 무의미 → 즉시 DLT** |

**Poison pill**: 영구 실패 메시지를 무한 재시도하면 **파티션 전체가 그 메시지에서 멈춘다.** 뒤의 정상 메시지가 전부 밀린다. 실패 종류 구분이 필수인 이유.

### 블로킹 재시도 vs 논블로킹 재시도

**블로킹**: 같은 스레드에서 sleep 후 재시도
- 장점: **순서 보존**
- 단점: 파티션 전체 정지. `max.poll.interval.ms`(기본 5분)를 넘기면 **컨슈머가 죽은 걸로 판단되어 리밸런싱** → 더 큰 사고

**논블로킹(재시도 토픽)**: 실패 메시지를 별도 토픽으로 넘기고 원본 오프셋은 커밋
```
main-topic ─실패─▶ retry-1s ─실패─▶ retry-10s ─실패─▶ retry-1m ─실패─▶ DLT
```
- 장점: 메인 파티션이 안 막힘
- **단점: 해당 키의 순서가 깨진다** ← 반드시 언급해야 할 트레이드오프

> 순서가 중요한 도메인(상태 전이)이면 논블로킹 재시도를 쓸 수 없다. 대신 짧은 블로킹 재시도 후 바로 DLT로 보내고 알림을 띄운다.

### Spring Kafka 예시
```java
@RetryableTopic(
    attempts = "4",
    backoff = @Backoff(delay = 1000, multiplier = 3.0),
    dltStrategy = DltStrategy.FAIL_ON_ERROR,
    exclude = { DeserializationException.class, ValidationException.class }  // 영구 실패는 즉시 DLT
)
@KafkaListener(topics = "orders")
public void consume(OrderEvent e) { ... }

@DltHandler
public void dlt(OrderEvent e, @Header(KafkaHeaders.ORIGINAL_TOPIC) String topic) {
    alertService.notify(...);   // DLT는 쌓아두는 곳이 아니라 알림 대상
}
```

### DLT 운영 (자주 빠뜨리는 부분)
- **DLT 유입 건수에 알림을 건다.** 안 그러면 조용히 유실된 것과 같다
- 원본 토픽/오프셋/예외 스택을 **헤더에 보존**
- **재처리(replay) 수단**을 미리 만들어 둔다. DLT는 종착지가 아니라 대기소다

---

## 6. 리밸런싱 관련 함정

- **`max.poll.records`가 크고 처리가 느리면** `max.poll.interval.ms`를 넘겨 컨슈머가 그룹에서 쫓겨난다 → 리밸런싱 → 커밋 못한 메시지 재처리 → 또 느림 → 무한 반복
  - 처방: `max.poll.records` 축소, 처리 시간 단축, `max.poll.interval.ms` 상향 중 택
- **리밸런싱 중 커밋 유실**: `ConsumerRebalanceListener.onPartitionsRevoked`에서 커밋
- **정적 멤버십(`group.instance.id`)**: 배포로 인한 불필요한 리밸런싱 억제

---

## 7. 면접용 한 문단 요약

> Kafka는 pull 기반 보존 로그라 브로커가 메시지별 ack를 추적하지 않고, 컨슈머가 오프셋만 관리한다. 그래서 신뢰성의 중심은 커밋 시점이다. 자동 커밋은 처리 완료와 무관하게 커밋돼서 크래시 시 건너뜀 유실이 나고, 처리 후 커밋으로 바꾸면 커밋 직전 크래시 시 중복이 난다. 외부 DB에 쓰는 이상 처리와 커밋을 원자적으로 묶을 수 없으니 at-least-once를 택하고, 대신 인박스 테이블의 유니크 제약이나 멱등한 비즈니스 로직으로 중복을 흡수한다. 재시도는 실패를 일시적/영구적으로 먼저 나눠서 영구 실패는 바로 DLT로 보내고 — 안 그러면 poison pill이 파티션을 막는다 — 일시적 실패만 백오프 재시도 토픽에 태운다. 다만 재시도 토픽은 키 순서를 깨뜨리므로, 순서가 중요한 도메인에서는 쓸 수 없다.
