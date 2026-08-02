# 06. 오케스트레이션 vs 코레오그래피

> 추상화 레벨: ① 아키텍처 설계
> 책 대응: 3.3.3 분산형 아키텍처의 대표적 설계 패턴 (118쪽)

여러 서비스에 걸친 하나의 업무 흐름을 **누가 조율하는가**의 문제다. jun-bank의 `transfer-service`는 이미 `SagaStatus`와 `OutboxEvent`를 갖고 있으므로, **이미 내려진 결정을 사후에 검토**하는 셈이다.

---

## 0. 용어 먼저

| 용어 | 뜻 |
|---|---|
| **분산 트랜잭션** | 여러 시스템(DB)에 걸친 하나의 논리적 작업 |
| **2PC (Two-Phase Commit)** | 조율자가 모든 참여자에게 "준비됐나?" 물은 뒤 전원 OK면 커밋시키는 프로토콜 |
| **ACID** | Atomicity(원자성)·Consistency(일관성)·Isolation(격리성)·Durability(지속성) |
| **Saga** | 긴 트랜잭션을 여러 로컬 트랜잭션으로 쪼개고, 실패 시 **보상**으로 되돌리는 패턴 |
| **보상 트랜잭션 (Compensating Transaction)** | 이미 커밋된 작업을 **의미적으로** 되돌리는 별도 트랜잭션 |
| **멱등성 (Idempotency)** | 같은 요청을 여러 번 처리해도 결과가 한 번 처리한 것과 같은 성질 |
| **Outbox 패턴** | 상태 변경과 이벤트 발행을 **같은 DB 트랜잭션**으로 묶어 유실을 막는 패턴 |
| **결과적 일관성** | 지금은 어긋나 있을 수 있으나 결국 같아지는 일관성 |

---

## 1. 왜 이 문제가 생기는가 — 2PC를 안 쓰는 이유

모놀리식에서는 이렇게 하면 끝난다.

```java
@Transactional
public void transfer(AccountId from, AccountId to, Money amount) {
    accountRepository.withdraw(from, amount);
    accountRepository.deposit(to, amount);
    ledgerRepository.post(from, to, amount);
}   // 하나라도 실패하면 전부 롤백. ACID가 공짜로 보장된다
```

서비스와 DB가 분리되면 이게 불가능하다. 이론적 해법인 **2PC**는 이렇게 동작한다:

```
조율자 → 참여자들: "준비됐나?" (Prepare)
참여자들 → 조율자: "예"           ← 이 시점부터 참여자는 락을 잡고 대기
조율자 → 참여자들: "커밋해"        (Commit)
```

**왜 마이크로서비스에서 안 쓰는가:**

1. **락을 오래 잡는다** — 준비~커밋 사이 내내 잠긴다. 처리량이 급락한다
2. **조율자가 단일 장애점** — "예" 응답 후 조율자가 죽으면 참여자는 **영원히 대기**(blocking)
3. **가용성이 곱해진다** — 참여자 각각 99.9%면 5개 참여 시 99.5%
4. **많은 시스템이 지원하지 않는다** — Kafka, 대부분의 NoSQL, 외부 API

> 결론: **분산 환경에서는 ACID를 포기하고 Saga를 쓴다.** "포기한다"는 표현이 정확하다 — 공짜 대체재가 아니라 **트레이드오프**다.

---

## 2. Saga 패턴

### 정의

> 긴 트랜잭션을 **여러 개의 로컬 트랜잭션**으로 쪼갠다. 각 로컬 트랜잭션은 즉시 커밋된다. 중간에 실패하면, 이미 커밋된 것들을 **보상 트랜잭션**으로 되돌린다.

```
정상:  T1 → T2 → T3 → T4  (완료)

실패:  T1 → T2 → T3 → ✗
       C1 ← C2 ← C3         (역순으로 보상)
```

### 핵심 성질 — ACID가 아니다

| ACID 속성 | Saga에서는 |
|---|---|
| **원자성 (A)** | ❌ 중간 상태가 **외부에 보인다**. T2까지 커밋된 상태를 다른 요청이 읽을 수 있다 |
| **일관성 (C)** | △ **결과적으로만** 일관 |
| **격리성 (I)** | ❌ **없다.** 이게 Saga의 가장 어려운 부분 |
| **지속성 (D)** | ✅ 각 로컬 트랜잭션은 커밋되므로 유지된다 |

**격리성이 없다는 것의 실제 의미**: 이체 중간에 출금은 됐고 입금은 안 된 상태에서 잔액을 조회하면 **돈이 사라진 것처럼 보인다.** 이걸 다루려면 별도 장치가 필요하다(아래 §5).

### Saga는 패턴, 오케스트레이션/코레오그래피는 구현 방식

```
Saga (패턴 — "쪼개고 보상한다")
 ├── 오케스트레이션 방식 (중앙 조율자가 순서를 안다)
 └── 코레오그래피 방식   (각자 이벤트를 듣고 스스로 결정한다)
```

---

## 3. 오케스트레이션 (Orchestration)

### 정의

**중앙 조율자(Orchestrator)** 가 각 서비스를 순서대로 호출하고, 실패 시 보상까지 지휘한다. 지휘자가 있는 오케스트라를 떠올리면 된다.

```
                  ┌──────────────────┐
      요청 ──────▶ │  결제 Saga 조율자  │
                  └──┬────┬────┬─────┘
            ① 한도확인 │    │    │
                     ▼    │    │
                 [카드서비스]│    │
            ② 잔액홀딩      ▼    │
                      [계좌서비스] │
            ③ 원장기록           ▼
                            [원장서비스]
```

### 코드

```java
@Service
@RequiredArgsConstructor
public class PaymentSagaOrchestrator {

    private final CardServicePort cardService;
    private final AccountServicePort accountService;
    private final LedgerServicePort ledgerService;
    private final SagaStateRepository sagaRepository;

    public AuthorizationResult execute(AuthorizeCommand command) {

        // Saga 상태를 먼저 저장한다 — 도중에 죽어도 복구할 수 있어야 하므로
        PaymentSaga saga = sagaRepository.save(PaymentSaga.start(command));

        try {
            // ① 카드 한도 점유
            LimitHoldId limitHold = cardService.holdLimit(command.cardId(), command.amount());
            saga.markStepCompleted(SagaStep.LIMIT_HELD, limitHold);
            sagaRepository.save(saga);

            // ② 계좌 잔액 홀딩
            BalanceHoldId balanceHold = accountService.hold(command.accountId(), command.amount());
            saga.markStepCompleted(SagaStep.BALANCE_HELD, balanceHold);
            sagaRepository.save(saga);

            // ③ 원장 기록
            LedgerEntryId entry = ledgerService.postHold(command.toLedgerSpec());
            saga.markStepCompleted(SagaStep.LEDGER_POSTED, entry);

            saga.complete();
            sagaRepository.save(saga);
            return AuthorizationResult.approved(saga.authorizationId());

        } catch (Exception e) {
            compensate(saga);                       // 보상
            sagaRepository.save(saga);
            throw PaymentException.authorizationFailed(e);
        }
    }

    /** 완료된 단계만 역순으로 되돌린다 */
    private void compensate(PaymentSaga saga) {
        saga.markCompensating();

        if (saga.isCompleted(SagaStep.LEDGER_POSTED)) {
            ledgerService.reverse(saga.ledgerEntryId());     // 역분개
        }
        if (saga.isCompleted(SagaStep.BALANCE_HELD)) {
            accountService.releaseHold(saga.balanceHoldId());
        }
        if (saga.isCompleted(SagaStep.LIMIT_HELD)) {
            cardService.releaseLimit(saga.limitHoldId());
        }

        saga.markCompensated();
    }
}
```

### 조율자를 어디에 두는가

| 방식 | 설명 | 평가 |
|---|---|---|
| **전용 서비스** | Saga만 담당하는 서비스를 만든다 | 관심사가 명확하나 서비스가 하나 는다 |
| **시작 서비스가 겸함** | 흐름을 시작한 서비스가 조율 | 가장 흔함. jun-bank의 `transfer-service`가 이 형태 |
| **워크플로 엔진** | Camunda, Temporal 등 외부 엔진 | 강력하나 학습·운영 비용 |

### 강점 / 약점

| 강점 | 약점 |
|---|---|
| **흐름이 코드 한 곳에 있다** — 읽으면 전체가 보인다 | 조율자가 **단일 장애점** |
| 상태 추적이 쉽다 (`SagaStatus` 하나만 보면 됨) | 조율자가 모든 참여자를 **알아야** 한다 → 결합 증가 |
| 보상 순서 제어가 명시적 | 흐름이 늘면 조율자가 **God Service**로 비대해짐 |
| 디버깅·테스트가 상대적으로 쉽다 | 참여자 추가 시 조율자를 수정 (OCP 위반 경향) |

---

## 4. 코레오그래피 (Choreography)

### 정의

중앙 조율자가 없다. 각 서비스가 **이벤트를 듣고 스스로 다음 행동을 결정**한다. 안무를 익힌 무용수들이 지휘자 없이 함께 춤추는 모습에서 온 이름이다.

```
[카드서비스] ──LimitHeld──▶ [계좌서비스] ──BalanceHeld──▶ [원장서비스]
                                                             │
                                                        LedgerPosted
                                                             │
                                                             ▼
                                                       [알림서비스]
```

### 코드

```java
// ① 카드 서비스 — 시작. 다음에 무슨 일이 일어날지 모른다
@Service
@RequiredArgsConstructor
public class CardLimitService {

    @Transactional
    public void holdLimit(AuthorizeCommand command) {
        Card card = cardRepository.findById(command.cardId()).orElseThrow();
        card.holdLimit(command.amount());
        cardRepository.save(card);

        outbox.append(new LimitHeldEvent(          // Outbox — 같은 트랜잭션에 기록
            command.authorizationId(), command.accountId(), command.amount()));
    }
}

// ② 계좌 서비스 — LimitHeld를 듣고 자기 일을 한다
@Component
@RequiredArgsConstructor
public class AccountEventHandler {

    @KafkaListener(topics = "payment.limit-held")
    @Transactional
    public void on(LimitHeldEvent event) {
        // 멱등성 — 같은 이벤트가 두 번 와도 한 번만 처리 (Kafka는 at-least-once)
        if (processedEventStore.exists(event.eventId())) return;

        try {
            Account account = accountRepository.findById(event.accountId()).orElseThrow();
            account.hold(event.amount());
            accountRepository.save(account);

            outbox.append(new BalanceHeldEvent(event.authorizationId(), event.amount()));
        } catch (InsufficientBalanceException e) {
            // 실패도 이벤트로 알린다 — 보상은 각자가 알아서 한다
            outbox.append(new BalanceHoldFailedEvent(event.authorizationId(), e.getMessage()));
        }
        processedEventStore.save(event.eventId());
    }
}

// ③ 카드 서비스 — 실패 이벤트를 듣고 스스로 보상한다
@Component
@RequiredArgsConstructor
public class CardCompensationHandler {

    @KafkaListener(topics = "payment.balance-hold-failed")
    @Transactional
    public void on(BalanceHoldFailedEvent event) {
        Card card = cardRepository.findByAuthorizationId(event.authorizationId()).orElseThrow();
        card.releaseLimit(event.authorizationId());     // 보상
        cardRepository.save(card);
    }
}
```

**주목할 점**: 어느 클래스에도 **"승인은 한도확인 → 잔액홀딩 → 원장기록 순서로 진행된다"는 문장이 없다.** 흐름은 이벤트 연결로만 존재한다. 이게 코레오그래피의 본질이자 최대 약점이다.

### 강점 / 약점

| 강점 | 약점 |
|---|---|
| **결합도가 매우 낮다** — 서로를 모른다 | **전체 흐름이 어디에도 없다** |
| 참여자 추가가 기존 코드를 안 건드림 | 장애 추적이 극도로 어렵다 |
| 단일 장애점 없음 | **순환 의존** 위험 (A→B→C→A) |
| 확장성이 좋다 | "지금 어디까지 갔나"를 알기 어렵다 |
| | 보상 로직이 여러 서비스에 흩어짐 |

---

## 5. 비교

| 축 | 오케스트레이션 | 코레오그래피 |
|---|---|---|
| **결합도** | 높음 (조율자가 전부 안다) | **낮음** |
| **흐름 가시성** | **높음** (코드 한 곳) | 낮음 (흩어짐) |
| **장애 추적** | **쉬움** (Saga 상태 조회) | 어려움 (분산 추적 필수) |
| **변경 시 파급** | 조율자 수정 필요 | 관련 서비스만 |
| **순환 의존 위험** | 없음 | **있음** |
| **단일 장애점** | **있음** (조율자) | 없음 |
| **테스트 난이도** | 낮음 | 높음 |
| **참여자 추가** | 조율자 수정 | **구독만 추가** |
| **적합한 흐름 길이** | **긴 흐름 (3단계 이상)** | 짧은 흐름 (1~2단계) |

### 실무 판단 기준

> **흐름을 사람이 설명해야 하면 오케스트레이션, 알림처럼 흘려보내면 되면 코레오그래피.**

- 결제 승인처럼 **결과를 즉시 알려줘야 하고 실패 시 정확히 되돌려야 하는 흐름** → 오케스트레이션
- "결제됐으니 포인트 적립하고 알림 보내라"처럼 **부수적이고 순서가 중요하지 않은 흐름** → 코레오그래피

**한 시스템 안에서 섞어도 된다.** 오히려 그게 정상이다.

---

## 6. Saga의 어려운 부분들

### 6.1 보상이 불가능한 작업

**이미 되돌릴 수 없는 것들이 있다.**

| 작업 | 보상 가능? | 대응 |
|---|---|---|
| DB 레코드 삽입 | ✅ 삭제 또는 역분개 | |
| 잔액 차감 | ✅ 환입 | |
| **이메일·SMS 발송** | ❌ | 취소 안내를 **추가 발송** |
| **외부 카드사 승인** | △ | 취소 전문(망취소) 전송 — **상대가 받아줘야 함** |
| **현금 출금** | ❌ | 애초에 마지막 단계로 배치 |

**설계 원칙**: **되돌릴 수 없는 작업은 Saga의 마지막에 둔다.** 그러면 그 앞이 다 성공한 뒤에만 실행되므로 보상할 일이 없다.

### 6.2 피벗 트랜잭션 (Pivot Transaction)

Saga를 세 구간으로 나누는 개념이다.

```
[보상 가능 트랜잭션들] → [피벗] → [재시도 가능 트랜잭션들]
     실패하면 되돌림       분기점      실패하면 성공할 때까지 재시도
```

- **피벗 이전**: 실패하면 전체 보상
- **피벗**: 이 지점을 넘으면 **되돌리지 않는다.** 결정의 순간
- **피벗 이후**: 실패해도 보상하지 않고 **성공할 때까지 재시도**한다

결제에서는 **"승인 확정"이 피벗**이다. 승인이 확정된 뒤 알림 발송이 실패했다고 승인을 취소하지 않는다 — 알림을 재시도할 뿐이다.

### 6.3 격리성 부재에 대한 대응

Saga에는 격리성이 없어 **중간 상태가 다른 요청에 보인다.** 대표적 대응책:

| 기법 | 설명 |
|---|---|
| **시맨틱 락 (Semantic Lock)** | 처리 중임을 나타내는 상태를 둔다 (예: `PENDING`). 다른 요청이 보고 판단 |
| **교환적 업데이트** | 순서에 무관한 연산만 쓴다 (절대값 설정 ❌, 증감 ⭕) |
| **비관적 뷰** | 조회 시 **최악을 가정**해 보여준다 (홀딩된 금액을 이미 나간 것으로 표시) |
| **값 재확인** | 커밋 직전에 읽은 값이 그대로인지 다시 확인 |

**jun-bank의 홀딩(Hold) 개념이 정확히 시맨틱 락 + 비관적 뷰다.** 승인만 되고 매입은 안 된 금액을 가용잔액에서 미리 빼서 보여주는 것.

### 6.4 Outbox 패턴 — 이벤트 유실 막기

**문제**: DB 커밋과 이벤트 발행은 서로 다른 시스템이라 원자적이지 않다.

```java
@Transactional
public void hold(...) {
    accountRepository.save(account);      // ① DB 커밋 성공
    kafkaTemplate.send("balance.held", event);   // ② 여기서 브로커가 죽으면? → 이벤트 영구 유실
}
```

**해법**: 이벤트를 **같은 DB의 테이블에 저장**한다. 그러면 하나의 로컬 트랜잭션에 묶인다.

```java
@Transactional
public void hold(AuthorizeCommand command) {
    Account account = accountRepository.findById(command.accountId()).orElseThrow();
    account.hold(command.amount());
    accountRepository.save(account);                        // ① 상태 변경

    outboxRepository.save(OutboxEvent.of(                   // ② 이벤트도 같은 DB, 같은 트랜잭션
        "balance.held", new BalanceHeldEvent(...)));
}   // ①②가 함께 커밋되거나 함께 롤백된다

// 별도 프로세스가 outbox를 읽어 발행한다
@Scheduled(fixedDelay = 1000)
@Transactional
public void publishOutbox() {
    List<OutboxEvent> pending = outboxRepository.findPending(100);
    for (OutboxEvent event : pending) {
        kafkaTemplate.send(event.topic(), event.payload());
        event.markPublished();       // 실패하면 다음 주기에 재시도된다
    }
}
```

**대가**: 발행이 **최소 한 번(at-least-once)** 보장이므로 **중복 발행이 가능하다.** 따라서 **소비 측이 반드시 멱등해야 한다.**

> 이 대가는 피할 수 없다. "정확히 한 번(exactly-once)"은 분산 환경에서 매우 비싸거나 불가능하다. **at-least-once + 멱등 소비**가 실무의 정답이다.

### 6.5 멱등성 — 어느 쪽에서 더 중요한가

**둘 다 똑같이 중요하다.** 다만 이유가 다르다.

- **오케스트레이션**: 조율자가 재시도할 때 참여자가 중복 처리하면 안 된다
- **코레오그래피**: 브로커가 이벤트를 중복 전달할 수 있다 (at-least-once)

```java
// 멱등성 구현의 기본형
@Transactional
public AuthorizationResult authorize(AuthorizeCommand command) {
    // 1) 이미 처리했으면 최초 결과를 그대로 반환한다 — 재처리하지 않는다
    Optional<AuthorizationResult> previous = idempotencyStore.find(command.idempotencyKey());
    if (previous.isPresent()) return previous.get();

    AuthorizationResult result = doAuthorize(command);

    // 2) 결과를 키와 함께 저장 (같은 트랜잭션에)
    idempotencyStore.save(command.idempotencyKey(), result);
    return result;
}
```

**주의점**:
- 멱등키에 **유니크 제약**을 걸어야 동시 요청에서도 안전하다
- **저장과 처리가 같은 트랜잭션**이어야 한다
- 멱등키의 **보관 기간** 정책이 필요하다 (영원히 둘 수 없다)

---

## 7. 스스로 답할 질문

1. 둘 중 하나를 **시스템 전체에 통일**해야 하는가, 흐름마다 달라도 되는가?
2. 코레오그래피에서 "지금 이 결제가 어디까지 갔는지"를 어떻게 아는가?
   - 힌트: 상태를 모으는 별도 구독자(프로세스 매니저)를 두거나, 분산 추적에 의존
3. 오케스트레이션의 조율자가 **God Service**가 되는 것을 어떻게 막는가?
   - 힌트: 조율자는 **순서만** 알고 **판단은 하지 않는다**
4. **이벤트를 발행했는데 아무도 안 듣는 상황**을 코레오그래피에서 어떻게 감지하는가?
5. 멱등성은 둘 중 어느 쪽에서 더 중요한가? 아니면 똑같이 중요한가?
6. Outbox 패턴은 둘 중 어느 쪽에 필요한가?
   - 힌트: 이벤트를 쓰는 모든 곳
7. Saga에 격리성이 없다면, **이체 중간에 잔액을 조회한 사용자**에게 무엇을 보여줘야 하는가?
8. **at-least-once + 멱등 소비**와 **exactly-once**는 결과적으로 같은가? 다르다면 어디가 다른가?

---

## 8. jun-bank 적용 검토 (공부 후 채운다)

| 흐름 | 참여 서비스 | 현재 방식 | 판단 |
|---|---|---|---|
| 회원가입 | user → auth | **동기 Feign (트랜잭션 내부)** | |
| 계좌 이체 | transfer → account × 2 → ledger | `SagaStatus`·`OutboxEvent` 존재 | |
| **결제 승인** | card → account → ledger | **미구현** | |
| **망취소** | 매입사 → card → account → ledger | **미구현** | |
| **매입·정산** | 배치 → transaction → ledger | **미구현** | |
| 회원 탈퇴 | user → 전 서비스 | `user.deleted` 이벤트 (코레오그래피) | |

### 지금 확인된 문제

1. **회원가입과 계좌 이체가 서로 다른 방식을 쓴다.** 의도된 것인가, 그때그때 결정한 결과인가?
2. **회원가입은 `@Transactional` 안에서 Feign 동기 호출을 한다.** 이건 Saga도 2PC도 아니다 —
   - DB 커넥션을 쥔 채 네트워크를 기다린다
   - auth 성공 후 로컬 커밋이 실패하면 **고아 AuthUser**가 남는다
   - 멱등키가 없어 재시도 시 중복 생성된다
3. **Outbox가 `transfer-service`에만 있다.** `user-service`는 try-catch로 삼키고 자체 재시도 테이블을 쓴다 → 품질 시나리오 **QS-05를 통과하지 못한다**

> 이 세 가지가 `architecture/03-transaction-design.md`에서 통일해야 할 대상이다.

---

## 참고

- (공부하며 채운다)
