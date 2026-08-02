# 04. 디자인 패턴 (GoF)

> 추상화 레벨: ③ 컴포넌트 설계 · ④ 클래스 설계
> 책 대응: 2.4.2 디자인 패턴 (88쪽)

23개를 외우는 것이 목적이 아니다. **어떤 문제 상황에서 어떤 패턴이 답이 되는지**, 그리고 **언제 쓰지 말아야 하는지**를 판단할 수 있으면 된다.

---

## 0. 들어가기 전에

### 용어

| 용어 | 뜻 |
|---|---|
| **GoF** | Gang of Four. 『Design Patterns』(1994)를 쓴 네 저자를 부르는 말 |
| **패턴 (Pattern)** | 반복해서 나타나는 문제와, 그에 대해 검증된 해법의 짝 |
| **클라이언트 (Client)** | 그 패턴을 **사용하는 쪽** 코드 |
| **위임 (Delegation)** | 자기가 처리하지 않고 다른 객체에게 넘기는 것 |
| **합성 (Composition)** | 다른 객체를 필드로 가지고 그 기능을 쓰는 것 (상속과 대비) |
| **다형성 (Polymorphism)** | 같은 타입으로 다루지만 실제 동작은 구현체마다 다른 것 |
| **런타임 (Runtime)** | 프로그램 실행 중. 컴파일 시점과 대비 |

### 세 분류

| 분류 | 관심사 | 개수 |
|---|---|---|
| **생성 (Creational)** | 객체를 **어떻게 만드는가** | 5 |
| **구조 (Structural)** | 객체를 **어떻게 조합하는가** | 7 |
| **행위 (Behavioral)** | 객체가 **어떻게 협력하는가** | 11 |

### 중요한 전제

**Spring을 쓰면 상당수가 이미 프레임워크에 흡수되어 있다.** Singleton은 빈 스코프가, Factory는 컨테이너가, Proxy는 AOP가 대신한다. 그래서 "직접 구현할 패턴"과 "알아보기만 할 패턴"을 구분하는 게 실용적이다.

---

# 생성 패턴 (Creational)

## 1. Singleton (싱글턴)

> **목적**: 클래스의 인스턴스가 **하나만** 존재하도록 보장하고, 전역 접근점을 제공한다.

```java
// enum 방식 — 직렬화·리플렉션 공격에 안전하고 가장 간결하다
public enum ApprovalNumberGenerator {
    INSTANCE;

    private final AtomicLong sequence = new AtomicLong();

    public String generate() {
        return String.format("%08d", sequence.incrementAndGet() % 100_000_000);
    }
}

// 사용
String approvalNo = ApprovalNumberGenerator.INSTANCE.generate();
```

```java
// Spring에서는 그냥 빈으로 만든다 — 기본 스코프가 싱글턴이다
@Component
public class ApprovalNumberGenerator {
    private final AtomicLong sequence = new AtomicLong();
    public String generate() { ... }
}
```

**쓰지 말아야 할 때**: 상태를 가진 싱글턴은 **전역 변수와 같다**. 테스트 간 상태가 새고, 동시성 문제가 생긴다. Spring 빈으로 만들되 **상태를 두지 않는 것**이 안전하다.

**jun-bank**: 스프링이 대신하므로 직접 구현할 일이 거의 없다.

---

## 2. Factory Method (팩토리 메서드)

> **목적**: 객체 생성을 **서브클래스가 결정**하게 한다. 상위 클래스는 "만든다"만 알고 "무엇을 만드는지"는 모른다.

```java
// 정산 파일 파서 — 매입사마다 포맷이 다르다
public abstract class SettlementFileProcessor {

    /** 템플릿: 흐름은 여기서 고정 */
    public final SettlementResult process(Path file) {
        SettlementParser parser = createParser();      // ← 팩토리 메서드
        List<SettlementRecord> records = parser.parse(file);
        return reconcile(records);
    }

    protected abstract SettlementParser createParser();   // 서브클래스가 결정

    private SettlementResult reconcile(List<SettlementRecord> records) { ... }
}

public class CsvSettlementFileProcessor extends SettlementFileProcessor {
    @Override protected SettlementParser createParser() { return new CsvSettlementParser(); }
}

public class FixedWidthSettlementFileProcessor extends SettlementFileProcessor {
    @Override protected SettlementParser createParser() { return new FixedWidthSettlementParser(); }
}
```

**정적 팩토리 메서드와 혼동 주의**: `Money.of(1000)` 같은 것은 GoF의 Factory Method가 **아니다.** 그건 생성자 대신 쓰는 관용법(정적 팩토리)이다. GoF 패턴은 **서브클래스에 생성 책임을 위임**하는 것이 핵심이다.

**jun-bank**: 정산 파일 포맷이 여러 개가 되면 유용. 하나뿐이면 과하다.

---

## 3. Abstract Factory (추상 팩토리)

> **목적**: **서로 관련된 객체 묶음**을 일관되게 생성한다. 개별 객체가 아니라 **제품군(family)** 단위다.

```java
// 카드 브랜드마다 승인 전문·취소 전문 규격이 세트로 다르다
public interface CardNetworkFactory {
    AuthorizationMessageBuilder authorizationBuilder();
    ReversalMessageBuilder reversalBuilder();
}

public class VisaNetworkFactory implements CardNetworkFactory {
    public AuthorizationMessageBuilder authorizationBuilder() { return new VisaAuthBuilder(); }
    public ReversalMessageBuilder reversalBuilder() { return new VisaReversalBuilder(); }
}

public class MasterNetworkFactory implements CardNetworkFactory {
    public AuthorizationMessageBuilder authorizationBuilder() { return new MasterAuthBuilder(); }
    public ReversalMessageBuilder reversalBuilder() { return new MasterReversalBuilder(); }
}

// 클라이언트는 "어느 브랜드인지"만 고르면 세트가 일관되게 따라온다
public class NetworkMessageSender {
    private final CardNetworkFactory factory;

    public void sendAuthorization(Authorization auth) {
        var message = factory.authorizationBuilder().build(auth);   // Visa면 Visa끼리
        send(message);
    }
}
```

**Factory Method와의 차이**: Factory Method는 **객체 하나**, Abstract Factory는 **세트**. Visa 승인전문 + Master 취소전문이 섞이는 사고를 타입으로 막는 것이 목적이다.

**쓰지 말아야 할 때**: 제품군이 하나뿐일 때. 확장 축이 없는데 만들면 순수 오버헤드다.

---

## 4. Builder (빌더)

> **목적**: 복잡한 객체를 **단계적으로** 만든다. 특히 **선택적 파라미터가 많을 때**.

```java
public class Authorization {
    private final AuthorizationId id;
    private final CardId cardId;
    private final Money amount;
    private final MerchantId merchantId;
    private final String approvalNumber;
    private final LocalDateTime requestedAt;
    private final String idempotencyKey;

    private Authorization(Builder b) {
        this.id = b.id; this.cardId = b.cardId; this.amount = b.amount;
        this.merchantId = b.merchantId; this.approvalNumber = b.approvalNumber;
        this.requestedAt = b.requestedAt; this.idempotencyKey = b.idempotencyKey;
    }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private AuthorizationId id;
        private CardId cardId;
        private Money amount;
        private MerchantId merchantId;
        private String approvalNumber;
        private LocalDateTime requestedAt;
        private String idempotencyKey;

        public Builder cardId(CardId v)      { this.cardId = v; return this; }
        public Builder amount(Money v)       { this.amount = v; return this; }
        public Builder merchantId(MerchantId v) { this.merchantId = v; return this; }
        public Builder requestedAt(LocalDateTime v) { this.requestedAt = v; return this; }
        public Builder idempotencyKey(String v) { this.idempotencyKey = v; return this; }

        public Authorization build() {
            // 빌드 시점에 필수값·불변식을 한 번에 검증한다 ← 빌더의 진짜 가치
            Objects.requireNonNull(cardId, "카드 ID는 필수입니다");
            Objects.requireNonNull(amount, "금액은 필수입니다");
            if (amount.isNegative()) throw new IllegalArgumentException("금액은 음수일 수 없습니다");
            return new Authorization(this);
        }
    }
}

// 사용 — 인자 순서를 헷갈릴 일이 없다
Authorization auth = Authorization.builder()
    .cardId(cardId)
    .amount(Money.krw(50_000))
    .merchantId(merchantId)
    .requestedAt(now)
    .build();
```

**쓰지 말아야 할 때**: 필드가 3~4개 이하이고 전부 필수라면 생성자가 낫다. 빌더는 **필수값 누락을 컴파일 시점에 못 잡는다**는 단점이 있다.

**jun-bank**: `User.createBuilder()` 로 이미 쓰고 있다.

---

## 5. Prototype (프로토타입)

> **목적**: 기존 객체를 **복제**해서 새 객체를 만든다. 생성 비용이 크거나, 런타임 상태를 그대로 복사해야 할 때.

```java
public record SettlementConfig(
    String acquirerId, LocalTime cutOff, int retryCount, Duration timeout
) {
    /** 값 객체는 복제 대신 "일부만 바꾼 새 인스턴스"가 자연스럽다 */
    public SettlementConfig withCutOff(LocalTime newCutOff) {
        return new SettlementConfig(acquirerId, newCutOff, retryCount, timeout);
    }

    public SettlementConfig withRetryCount(int newRetryCount) {
        return new SettlementConfig(acquirerId, cutOff, newRetryCount, timeout);
    }
}

// 사용 — 기본 설정을 복제해 조금씩 다른 설정을 만든다
SettlementConfig base = new SettlementConfig("ACQ001", LocalTime.of(23, 0), 3, Duration.ofSeconds(5));
SettlementConfig weekend = base.withCutOff(LocalTime.of(20, 0));
```

**주의 — 얕은 복사 vs 깊은 복사**: `Cloneable`/`clone()`은 **얕은 복사**(내부 객체 참조를 공유)라 버그의 원천이다. Java에서는 **복사 생성자나 `with` 메서드**를 쓰는 편이 안전하다.

**jun-bank**: 값 객체를 불변으로 만들면 자연히 이 형태가 된다. 별도 패턴으로 의식할 일은 적다.

---

# 구조 패턴 (Structural)

## 6. Adapter (어댑터)

> **목적**: **호환되지 않는 인터페이스**를 클라이언트가 기대하는 형태로 변환한다.

```java
// 우리가 원하는 인터페이스 (포트 — 애플리케이션이 소유)
public interface CardNetworkPort {
    AuthorizationResponse requestAuthorization(AuthorizationRequest request);
}

// 외부 시스템이 제공하는 인터페이스 (우리가 못 바꾼다)
public interface AcquirerLegacyClient {
    String send(String iso8583Message) throws AcquirerException;
}

// 어댑터 — 둘 사이를 번역한다
@Component
@RequiredArgsConstructor
public class AcquirerNetworkAdapter implements CardNetworkPort {

    private final AcquirerLegacyClient legacyClient;
    private final Iso8583Codec codec;

    @Override
    public AuthorizationResponse requestAuthorization(AuthorizationRequest request) {
        String message = codec.encode(request);              // 우리 타입 → 외부 포맷
        try {
            String raw = legacyClient.send(message);
            return codec.decode(raw);                        // 외부 포맷 → 우리 타입
        } catch (AcquirerException e) {
            throw CardNetworkException.communicationFailure(e);   // 외부 예외 → 우리 예외
        }
    }
}
```

**핵심 가치**: 외부 시스템의 형태가 **우리 도메인으로 새어 들어오지 않는다.** 헥사고날 아키텍처의 `infrastructure/` 계층이 통째로 이 패턴이다.

**jun-bank**: `UserRepositoryAdapter`, `AuthServiceAdapter` 가 정확히 이것.

---

## 7. Bridge (브리지)

> **목적**: **추상화와 구현을 분리**해서 둘이 **독립적으로** 확장되게 한다.

두 축이 각각 늘어나는데 상속으로 조합하면 클래스가 곱셈으로 폭발하는 상황을 푼다.

```java
// 문제: 알림 종류(승인/취소/정산) × 전송 수단(SMS/이메일/푸시) = 9개 클래스?

// 축 1: 전송 수단 (구현)
public interface NotificationSender {
    void send(String to, String title, String body);
}
public class SmsSender   implements NotificationSender { public void send(...) { ... } }
public class EmailSender implements NotificationSender { public void send(...) { ... } }
public class PushSender  implements NotificationSender { public void send(...) { ... } }

// 축 2: 알림 종류 (추상화) — 구현을 합성으로 들고 있다
public abstract class PaymentNotification {
    protected final NotificationSender sender;   // ← 다리(bridge)

    protected PaymentNotification(NotificationSender sender) { this.sender = sender; }

    public abstract void notify(Authorization auth);
}

public class ApprovalNotification extends PaymentNotification {
    public ApprovalNotification(NotificationSender sender) { super(sender); }

    @Override public void notify(Authorization auth) {
        sender.send(auth.cardholderContact(), "결제 승인",
            String.format("%s원이 승인되었습니다.", auth.amount()));
    }
}

// 조합은 런타임에 — 3 + 3 클래스로 9가지 조합이 나온다
new ApprovalNotification(new SmsSender()).notify(auth);
```

**Adapter와의 차이**: Adapter는 **이미 있는 것들을 사후에** 맞춘다. Bridge는 **처음부터 두 축이 따로 자랄 것을 예상**하고 설계한다.

---

## 8. Composite (컴포지트)

> **목적**: **개별 객체와 그 묶음을 똑같이** 다룰 수 있게 한다. 트리 구조에 쓴다.

```java
// 원장 전표: 단일 분개와 복합 전표를 같은 타입으로 다룬다
public interface LedgerEntry {
    Money debitTotal();
    Money creditTotal();
    default boolean isBalanced() { return debitTotal().equals(creditTotal()); }
}

// 잎(Leaf) — 단일 분개
public record SingleEntry(LedgerAccount account, EntryType type, Money amount)
        implements LedgerEntry {
    public Money debitTotal()  { return type == EntryType.DEBIT  ? amount : Money.zero(); }
    public Money creditTotal() { return type == EntryType.CREDIT ? amount : Money.zero(); }
}

// 가지(Composite) — 여러 분개를 묶은 전표
public record CompositeEntry(List<LedgerEntry> children) implements LedgerEntry {
    public Money debitTotal() {
        return children.stream().map(LedgerEntry::debitTotal).reduce(Money.zero(), Money::plus);
    }
    public Money creditTotal() {
        return children.stream().map(LedgerEntry::creditTotal).reduce(Money.zero(), Money::plus);
    }
}

// 클라이언트는 단일인지 복합인지 신경 쓰지 않는다
void post(LedgerEntry entry) {
    if (!entry.isBalanced()) throw LedgerException.notBalanced();   // 차변=대변 불변식
    repository.save(entry);
}
```

**jun-bank**: 복식부기 원장에 자연스럽게 맞는다. 전표 하나가 여러 분개로 이루어지고, "차변 합 = 대변 합"을 재귀적으로 검증할 수 있다.

---

## 9. Decorator (데코레이터)

> **목적**: 객체에 **기능을 동적으로 덧입힌다.** 상속 없이, 원본을 건드리지 않고.

```java
public interface AuthorizationHandler {
    AuthorizationResult handle(AuthorizeCommand command);
}

// 핵심 기능
public class CoreAuthorizationHandler implements AuthorizationHandler {
    public AuthorizationResult handle(AuthorizeCommand command) { /* 실제 승인 처리 */ }
}

// 데코레이터 공통 뼈대
public abstract class AuthorizationHandlerDecorator implements AuthorizationHandler {
    protected final AuthorizationHandler delegate;
    protected AuthorizationHandlerDecorator(AuthorizationHandler delegate) { this.delegate = delegate; }
}

// 기능 ① 로깅
public class LoggingHandler extends AuthorizationHandlerDecorator {
    public LoggingHandler(AuthorizationHandler d) { super(d); }
    public AuthorizationResult handle(AuthorizeCommand c) {
        log.info("승인 요청 시작: card={}, amount={}", c.cardId(), c.amount());
        AuthorizationResult result = delegate.handle(c);
        log.info("승인 요청 완료: result={}", result.status());
        return result;
    }
}

// 기능 ② 멱등성
public class IdempotentHandler extends AuthorizationHandlerDecorator {
    private final IdempotencyStore store;
    public IdempotentHandler(AuthorizationHandler d, IdempotencyStore s) { super(d); this.store = s; }
    public AuthorizationResult handle(AuthorizeCommand c) {
        return store.find(c.idempotencyKey())
            .orElseGet(() -> {
                AuthorizationResult r = delegate.handle(c);
                store.save(c.idempotencyKey(), r);
                return r;
            });
    }
}

// 조립 — 순서를 바꿔가며 조합할 수 있다
AuthorizationHandler handler =
    new LoggingHandler(
        new IdempotentHandler(
            new CoreAuthorizationHandler(), store));
```

**Proxy와의 차이**: Decorator는 **기능을 더하는 것**이 목적이고, Proxy는 **접근을 제어하는 것**이 목적이다. 구조는 거의 같고 의도가 다르다.

**주의**: 데코레이터를 많이 쌓으면 **스택 트레이스가 깊어지고 흐름을 따라가기 어렵다.** Spring AOP를 쓰면 같은 효과를 선언적으로 얻는다.

---

## 10. Facade (퍼사드)

> **목적**: 복잡한 하위 시스템에 **단순한 진입점 하나**를 제공한다.

```java
// 하위 시스템들
class CardValidator     { void validate(CardId id) { ... } }
class LimitChecker      { void check(CardId id, Money amount) { ... } }
class BalanceHolder     { void hold(AccountId id, Money amount) { ... } }
class LedgerPoster      { void post(Authorization auth) { ... } }
class FraudDetector     { void screen(AuthorizeCommand cmd) { ... } }

// 퍼사드 — 클라이언트는 이것 하나만 알면 된다
@Component
@RequiredArgsConstructor
public class PaymentAuthorizationFacade {

    private final CardValidator cardValidator;
    private final LimitChecker limitChecker;
    private final BalanceHolder balanceHolder;
    private final LedgerPoster ledgerPoster;
    private final FraudDetector fraudDetector;

    public AuthorizationResult authorize(AuthorizeCommand command) {
        fraudDetector.screen(command);
        cardValidator.validate(command.cardId());
        limitChecker.check(command.cardId(), command.amount());
        balanceHolder.hold(command.accountId(), command.amount());
        Authorization auth = Authorization.create(command.toSpec());
        ledgerPoster.post(auth);
        return AuthorizationResult.from(auth);
    }
}
```

**주의**: 퍼사드가 커지면 **God Object**가 된다. 퍼사드는 **조율만** 하고 판단은 하지 않아야 한다. 헥사고날의 애플리케이션 서비스가 사실상 이 역할이다.

---

## 11. Flyweight (플라이웨이트)

> **목적**: **같은 값을 가진 객체를 공유**해서 메모리를 아낀다.

```java
public final class Currency {
    private static final Map<String, Currency> CACHE = new ConcurrentHashMap<>();

    private final String code;
    private final int minorUnit;   // KRW=0, USD=2

    private Currency(String code, int minorUnit) { this.code = code; this.minorUnit = minorUnit; }

    /** 같은 코드면 항상 같은 인스턴스를 돌려준다 */
    public static Currency of(String code) {
        return CACHE.computeIfAbsent(code, c -> new Currency(c, minorUnitOf(c)));
    }

    private static int minorUnitOf(String code) {
        return "KRW".equals(code) || "JPY".equals(code) ? 0 : 2;
    }
}
```

**주의**: 공유하는 객체는 **반드시 불변**이어야 한다. 가변이면 한 곳에서 바꾼 게 전부에 반영되는 재앙이 된다. Java의 `Integer.valueOf()` 캐시(-128~127)가 대표적 사례다.

**jun-bank**: 통화 코드 정도. 요즘 환경에서 메모리 절약 목적으로 쓸 일은 드물다.

---

## 12. Proxy (프록시)

> **목적**: 실제 객체에 대한 **접근을 제어**한다. 지연 로딩, 권한 검사, 캐싱, 원격 호출.

```java
public interface LedgerQueryService {
    LedgerBalance balanceOf(AccountId accountId);
}

// 실제 구현 — 무겁다
public class LedgerQueryServiceImpl implements LedgerQueryService {
    public LedgerBalance balanceOf(AccountId id) { /* 전표 전부 집계 */ }
}

// 캐싱 프록시 — 접근을 가로채 제어한다
@RequiredArgsConstructor
public class CachingLedgerQueryProxy implements LedgerQueryService {
    private final LedgerQueryService target;
    private final Cache<AccountId, LedgerBalance> cache;

    @Override
    public LedgerBalance balanceOf(AccountId id) {
        return cache.get(id, () -> target.balanceOf(id));
    }
}
```

**대표 사례**:
- **JPA 지연 로딩**: `@ManyToOne(fetch = LAZY)` 로 얻는 객체가 프록시다
- **Spring AOP**: `@Transactional`, `@Cacheable` 은 전부 프록시로 구현된다
- **Feign**: 인터페이스만 선언하면 HTTP 호출 프록시를 만들어준다

**함정**: Spring AOP 프록시는 **자기 자신의 메서드를 내부 호출하면 적용되지 않는다.** 같은 클래스 안에서 `this.someTransactionalMethod()` 를 부르면 프록시를 거치지 않으므로 트랜잭션이 안 걸린다. 실무에서 매우 자주 만나는 함정이다.

---

# 행위 패턴 (Behavioral)

## 13. Chain of Responsibility (책임 연쇄)

> **목적**: 요청을 처리할 객체들을 **사슬로 연결**하고, 처리할 수 있는 객체가 나올 때까지 넘긴다.

```java
public interface AuthorizationRule {
    void check(AuthorizeContext ctx);   // 통과 못하면 예외
}

@Component @Order(1)
public class CardStatusRule implements AuthorizationRule {
    public void check(AuthorizeContext ctx) {
        if (!ctx.card().isUsable(ctx.requestedAt())) throw CardException.notUsable(ctx.card().id());
    }
}

@Component @Order(2)
public class DailyLimitRule implements AuthorizationRule {
    public void check(AuthorizeContext ctx) {
        if (ctx.todayTotal().plus(ctx.amount()).isGreaterThan(ctx.card().dailyLimit()))
            throw CardException.dailyLimitExceeded();
    }
}

@Component @Order(3)
public class AvailableBalanceRule implements AuthorizationRule {
    public void check(AuthorizeContext ctx) {
        if (ctx.amount().isGreaterThan(ctx.account().availableBalance()))
            throw AccountException.insufficientAvailableBalance();
    }
}

// 사슬 실행 — 규칙 추가는 클래스 하나 추가로 끝난다 (OCP)
@Service
@RequiredArgsConstructor
public class AuthorizationRuleChain {
    private final List<AuthorizationRule> rules;   // @Order 순서로 주입된다

    public void validate(AuthorizeContext ctx) {
        rules.forEach(rule -> rule.check(ctx));
    }
}
```

**대표 사례**: Spring Security의 **Filter Chain**, 서블릿 필터.

**jun-bank**: 승인 규칙은 계속 늘어난다(카드 상태, 한도, 잔액, 가맹점 제한, 이상거래). 이 패턴이 잘 맞는다.

---

## 14. Command (커맨드)

> **목적**: **요청 자체를 객체로 만든다.** 그러면 저장·큐잉·취소·재실행이 가능해진다.

```java
public interface LedgerCommand {
    void execute(LedgerContext ctx);
    LedgerCommand undo();          // 되돌리기 = 역분개
}

public record PostEntryCommand(LedgerAccount account, EntryType type, Money amount)
        implements LedgerCommand {

    @Override public void execute(LedgerContext ctx) {
        ctx.post(new SingleEntry(account, type, amount));
    }

    /** 원장은 append-only이므로 삭제가 아니라 반대 전표를 만든다 */
    @Override public LedgerCommand undo() {
        return new PostEntryCommand(account, type.reverse(), amount);
    }
}

// 커맨드를 모아 한 번에 실행하고, 실패 시 역순으로 되돌린다
public class LedgerTransactionScript {
    private final Deque<LedgerCommand> executed = new ArrayDeque<>();

    public void run(List<LedgerCommand> commands, LedgerContext ctx) {
        try {
            for (LedgerCommand c : commands) { c.execute(ctx); executed.push(c); }
        } catch (Exception e) {
            while (!executed.isEmpty()) executed.pop().undo().execute(ctx);   // 보상
            throw e;
        }
    }
}
```

**Saga와의 관계**: Saga의 **보상 트랜잭션**이 개념적으로 이 패턴이다. "실행"과 "되돌리기"를 짝으로 묶는 발상이 같다. (→ study/06)

---

## 15. Interpreter (인터프리터)

> **목적**: 어떤 **언어의 문법을 클래스로 표현**하고 해석한다.

```java
// 가맹점별 수수료 규칙을 식으로 표현: "amount * 0.025 + 100"
public interface FeeExpression {
    Money evaluate(FeeContext ctx);
}

public record AmountRef() implements FeeExpression {
    public Money evaluate(FeeContext ctx) { return ctx.amount(); }
}

public record Constant(Money value) implements FeeExpression {
    public Money evaluate(FeeContext ctx) { return value; }
}

public record Multiply(FeeExpression left, BigDecimal rate) implements FeeExpression {
    public Money evaluate(FeeContext ctx) { return left.evaluate(ctx).multiply(rate); }
}

public record Add(FeeExpression left, FeeExpression right) implements FeeExpression {
    public Money evaluate(FeeContext ctx) { return left.evaluate(ctx).plus(right.evaluate(ctx)); }
}

// amount * 0.025 + 100원
FeeExpression rule = new Add(
    new Multiply(new AmountRef(), new BigDecimal("0.025")),
    new Constant(Money.krw(100)));

Money fee = rule.evaluate(new FeeContext(Money.krw(50_000)));
```

**현실적 평가**: GoF 23개 중 **직접 구현할 일이 가장 드문 패턴**이다. 실무에서는 스크립트 엔진이나 룰 엔진을 쓴다. 다만 **수수료·한도 규칙을 데이터로 관리하고 싶을 때** 개념적으로 필요해진다.

---

## 16. Iterator (반복자)

> **목적**: 내부 구조를 노출하지 않고 **순회**하게 한다.

```java
// 대용량 정산 파일을 메모리에 다 올리지 않고 한 건씩 순회
public class SettlementFileIterator implements Iterator<SettlementRecord>, AutoCloseable {

    private final BufferedReader reader;
    private String nextLine;

    public SettlementFileIterator(Path file) throws IOException {
        this.reader = Files.newBufferedReader(file);
        this.nextLine = reader.readLine();
    }

    @Override public boolean hasNext() { return nextLine != null; }

    @Override public SettlementRecord next() {
        if (nextLine == null) throw new NoSuchElementException();
        SettlementRecord record = SettlementRecord.parse(nextLine);
        try { nextLine = reader.readLine(); } catch (IOException e) { throw new UncheckedIOException(e); }
        return record;
    }

    @Override public void close() throws IOException { reader.close(); }
}
```

**Java에서는 언어에 내장되어 있다**: `Iterable` 을 구현하면 향상된 for문이 동작하고, `Stream` 은 더 강력한 대안이다. **직접 구현할 일은 대용량 스트리밍 정도**다.

---

## 17. Mediator (중재자)

> **목적**: 객체들이 **서로 직접 참조하지 않고** 중재자를 통해 소통하게 한다. N:N 관계를 1:N으로 바꾼다.

```java
// 중재자 — 각 참여자는 서로를 모른다
@Component
@RequiredArgsConstructor
public class SettlementMediator {

    private final SettlementFileReader fileReader;
    private final LedgerPoster ledgerPoster;
    private final ReconciliationChecker reconciler;
    private final NotificationSender notifier;

    public void runDailySettlement(LocalDate businessDate) {
        var records = fileReader.read(businessDate);
        var posted  = ledgerPoster.postAll(records);
        var result  = reconciler.check(businessDate, posted);
        if (result.hasMismatch()) {
            notifier.alertOperator(result);
        }
    }
}
```

**Facade와의 차이**: Facade는 **단방향**(클라이언트 → 하위 시스템)이고, Mediator는 **양방향**(참여자들이 서로 소통)이다.

**분산 시스템에서의 대응**: 이것이 **오케스트레이션**(중앙 조율자)이고, 중재자 없이 이벤트로 소통하는 것이 **코레오그래피**다. (→ study/06)

---

## 18. Memento (메멘토)

> **목적**: 객체의 **내부 상태를 캡슐화를 깨지 않고 저장**했다가 나중에 복원한다.

```java
public class TransferSaga {
    private SagaStatus status;
    private int currentStep;

    /** 스냅샷 — 내부 표현을 숨긴 채 상태만 담는다 */
    public record Snapshot(SagaStatus status, int currentStep) {}

    public Snapshot save() { return new Snapshot(status, currentStep); }

    public void restore(Snapshot snapshot) {
        this.status = snapshot.status();
        this.currentStep = snapshot.currentStep();
    }

    public void proceed() { currentStep++; }
}

// 사용 — 실패 시 이전 지점으로 되돌린다
TransferSaga.Snapshot checkpoint = saga.save();
try {
    saga.proceed();
} catch (Exception e) {
    saga.restore(checkpoint);
}
```

**주의**: 메멘토는 **메모리 상의 되돌리기**다. 분산 트랜잭션의 보상과는 다르다 — 이미 외부 시스템에 반영된 것은 메멘토로 되돌릴 수 없다.

**jun-bank 경고**: `User.previousStatus` 필드가 이 발상의 조잡한 형태다. 도메인 모델 안에 롤백용 필드를 두는 대신, 별도 스냅샷 객체로 분리하거나 **애초에 분산 트랜잭션 설계로 해결**하는 것이 맞다.

---

## 19. Observer (옵저버)

> **목적**: 어떤 객체의 상태가 바뀌면 **의존하는 객체들에게 자동으로 통보**한다.

```java
// 도메인 이벤트 (Observer 패턴의 현대적 형태)
public record AuthorizationApprovedEvent(
    AuthorizationId authorizationId, CardId cardId, Money amount, LocalDateTime occurredAt
) implements DomainEvent {}

// 발행 — 상태가 바뀐 쪽은 누가 듣는지 모른다
@Service
@RequiredArgsConstructor
public class AuthorizePaymentService {
    private final ApplicationEventPublisher publisher;

    @Transactional
    public AuthorizationResult authorize(AuthorizeCommand command) {
        Authorization auth = /* ... 승인 처리 ... */;
        publisher.publishEvent(new AuthorizationApprovedEvent(
            auth.id(), auth.cardId(), auth.amount(), auth.approvedAt()));
        return AuthorizationResult.from(auth);
    }
}

// 구독 — 듣는 쪽이 늘어도 발행 쪽 코드는 바뀌지 않는다 (OCP)
@Component
public class LedgerEventListener {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void on(AuthorizationApprovedEvent event) {
        ledgerService.postHoldEntry(event);
    }
}

@Component
public class NotificationEventListener {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void on(AuthorizationApprovedEvent event) {
        notificationService.notifyApproval(event);
    }
}
```

**`AFTER_COMMIT`이 중요한 이유**: 트랜잭션이 커밋되기 전에 이벤트를 처리하면, 롤백됐는데 알림이 나가는 사고가 생긴다.

**분산 환경의 한계**: 커밋 후 이벤트 발행은 **원자적이지 않다.** 커밋 성공 + 발행 실패 = 이벤트 유실. 이걸 막는 것이 **Outbox 패턴**이다. (품질 시나리오 QS-05)

**jun-bank**: 도메인 이벤트(`UserCreatedEvent` 등)로 이미 쓰고 있다.

---

## 20. State (상태)

> **목적**: 객체의 **상태에 따라 행동이 달라지는 것**을, 상태를 객체로 만들어 표현한다.

```java
// enum + 추상 메서드 — Java에서 가장 실용적인 State 구현
public enum AuthorizationStatus {

    PENDING {
        @Override public AuthorizationStatus approve() { return APPROVED; }
        @Override public AuthorizationStatus decline() { return DECLINED; }
    },
    APPROVED {
        @Override public AuthorizationStatus capture() { return CAPTURED; }
        @Override public AuthorizationStatus voidAuth() { return VOIDED; }
        @Override public AuthorizationStatus reverse() { return REVERSED; }
    },
    CAPTURED {
        @Override public AuthorizationStatus settle() { return SETTLED; }
        @Override public AuthorizationStatus refund() { return REFUNDED; }
    },
    SETTLED   { /* 종료 상태 — 아무 전이도 허용하지 않는다 */ },
    DECLINED  { },
    VOIDED    { },
    REVERSED  { },
    REFUNDED  { };

    // 기본은 전부 "허용하지 않음" — 허용되는 것만 각 상수가 오버라이드한다
    public AuthorizationStatus approve()  { throw illegal("승인"); }
    public AuthorizationStatus decline()  { throw illegal("거절"); }
    public AuthorizationStatus capture()  { throw illegal("매입"); }
    public AuthorizationStatus voidAuth() { throw illegal("승인취소"); }
    public AuthorizationStatus reverse()  { throw illegal("망취소"); }
    public AuthorizationStatus settle()   { throw illegal("정산"); }
    public AuthorizationStatus refund()   { throw illegal("환불"); }

    private IllegalStateTransitionException illegal(String operation) {
        return new IllegalStateTransitionException(this, operation);
    }
}

// 사용 — 잘못된 전이가 한 곳에서 막힌다
public class Authorization {
    private AuthorizationStatus status;

    public void capture() {
        this.status = status.capture();   // SETTLED 상태면 여기서 예외
    }
}
```

**왜 `if/switch`보다 나은가**: 상태 전이 규칙이 **한 곳에 모인다.** `if (status == APPROVED || status == PENDING)` 같은 조건이 코드 곳곳에 복사되는 것을 막는다. 상태가 추가되면 컴파일러가 빠진 곳을 알려준다.

**jun-bank**: 결제 라이프사이클(승인→매입→정산, 각종 취소)에 정확히 맞는다. **가장 중요한 패턴 중 하나.**

---

## 21. Strategy (전략)

> **목적**: **알고리즘군을 캡슐화**하고 런타임에 교체 가능하게 한다.

```java
public interface SettlementStrategy {
    boolean supports(AcquirerId acquirerId);
    SettlementResult settle(List<CaptureRecord> records);
}

@Component
public class DailySettlementStrategy implements SettlementStrategy {
    public boolean supports(AcquirerId id) { return id.settlementCycle() == Cycle.DAILY; }
    public SettlementResult settle(List<CaptureRecord> records) { /* D+1 일괄 */ }
}

@Component
public class WeeklySettlementStrategy implements SettlementStrategy {
    public boolean supports(AcquirerId id) { return id.settlementCycle() == Cycle.WEEKLY; }
    public SettlementResult settle(List<CaptureRecord> records) { /* 주간 합산 */ }
}

@Service
@RequiredArgsConstructor
public class SettlementService {
    private final List<SettlementStrategy> strategies;

    public SettlementResult settle(AcquirerId acquirerId, List<CaptureRecord> records) {
        return strategies.stream()
            .filter(s -> s.supports(acquirerId))
            .findFirst()
            .orElseThrow(() -> SettlementException.noStrategy(acquirerId))
            .settle(records);
    }
}
```

**State와의 차이**: 구조가 거의 같다. 차이는 **누가 바꾸는가**다.
- **Strategy**: **클라이언트가** 알고리즘을 고른다. 전략끼리 서로 모른다
- **State**: **객체 스스로** 상태를 바꾼다. 상태끼리 다음 상태를 안다

**OCP의 대표적 실현 수단**이다. (study/01의 `FeePolicy` 예제가 바로 이것)

---

## 22. Template Method (템플릿 메서드)

> **목적**: 알고리즘의 **뼈대는 상위 클래스에 고정**하고, 일부 단계만 서브클래스가 채운다.

```java
public abstract class BatchJob {

    /** final — 흐름은 바꿀 수 없다 */
    public final BatchResult run(LocalDate businessDate) {
        BatchContext ctx = prepare(businessDate);
        validate(ctx);                                  // 훅(hook) — 선택적 재정의
        BatchResult result = execute(ctx);              // 필수 구현
        report(result);
        return result;
    }

    protected abstract BatchContext prepare(LocalDate businessDate);
    protected abstract BatchResult execute(BatchContext ctx);

    /** 기본 동작을 제공하되 필요하면 덮어쓸 수 있다 */
    protected void validate(BatchContext ctx) { }

    private void report(BatchResult result) {
        log.info("배치 완료: 처리 {}건, 실패 {}건", result.successCount(), result.failureCount());
    }
}

public class CaptureBatchJob extends BatchJob {
    @Override protected BatchContext prepare(LocalDate d) { return BatchContext.of(fileReader.read(d)); }
    @Override protected BatchResult execute(BatchContext ctx) { /* 매입 반영 */ }
    @Override protected void validate(BatchContext ctx) {
        if (ctx.records().isEmpty()) throw BatchException.emptyFile();
    }
}
```

**Strategy와의 차이**: Template Method는 **상속**으로, Strategy는 **합성**으로 변형을 만든다. 상속은 컴파일 시점에 고정되고 합성은 런타임에 교체 가능하다. **일반적으로 Strategy가 더 유연하다.**

**주의**: 상위 클래스가 하위를 호출하는 **역전된 제어 흐름(할리우드 원칙 — "먼저 연락하지 마세요, 저희가 연락드립니다")** 이라 디버깅이 어려울 수 있다.

---

## 23. Visitor (비지터)

> **목적**: 객체 구조를 **바꾸지 않고 새로운 연산을 추가**한다.

```java
public interface LedgerEntryVisitor<R> {
    R visitSingle(SingleEntry entry);
    R visitComposite(CompositeEntry entry);
}

public interface LedgerEntry {
    <R> R accept(LedgerEntryVisitor<R> visitor);
}

public record SingleEntry(LedgerAccount account, EntryType type, Money amount) implements LedgerEntry {
    public <R> R accept(LedgerEntryVisitor<R> v) { return v.visitSingle(this); }
}

public record CompositeEntry(List<LedgerEntry> children) implements LedgerEntry {
    public <R> R accept(LedgerEntryVisitor<R> v) { return v.visitComposite(this); }
}

// 연산 ① 잔액 집계
public class BalanceVisitor implements LedgerEntryVisitor<Money> {
    public Money visitSingle(SingleEntry e) {
        return e.type() == EntryType.DEBIT ? e.amount() : e.amount().negate();
    }
    public Money visitComposite(CompositeEntry e) {
        return e.children().stream().map(c -> c.accept(this)).reduce(Money.zero(), Money::plus);
    }
}

// 연산 ② 감사 리포트 — 기존 클래스를 건드리지 않고 추가된다
public class AuditReportVisitor implements LedgerEntryVisitor<String> { ... }
```

**트레이드오프가 명확하다**:
- ✅ **연산 추가는 쉽다** (새 Visitor 클래스만)
- ❌ **타입 추가는 어렵다** (모든 Visitor를 고쳐야 함)

따라서 **타입은 안정적이고 연산이 자주 늘어나는 구조**에만 쓴다. 반대 상황이면 오히려 해롭다.

**Java의 대안**: 자바 17+ 의 **sealed interface + 패턴 매칭 switch** 가 훨씬 간결하다.

```java
public sealed interface LedgerEntry permits SingleEntry, CompositeEntry {}

Money balance = switch (entry) {
    case SingleEntry e    -> e.type() == EntryType.DEBIT ? e.amount() : e.amount().negate();
    case CompositeEntry e -> e.children().stream().map(this::balanceOf).reduce(Money.zero(), Money::plus);
};
```
컴파일러가 **모든 케이스를 다뤘는지 검사**해주므로 Visitor의 장점을 얻으면서 코드가 짧다. jun-bank는 Java 21이므로 이쪽을 우선 검토한다.

---

# 정리

## 헷갈리는 쌍 구분표

| 쌍 | 구조 | 차이 |
|---|---|---|
| **Adapter ↔ Bridge** | 유사 | Adapter는 **사후에** 맞춤. Bridge는 **사전에** 두 축을 분리 |
| **Adapter ↔ Facade** | 다름 | Adapter는 **인터페이스 변환**. Facade는 **단순화** |
| **Decorator ↔ Proxy** | 동일 | Decorator는 **기능 추가**. Proxy는 **접근 제어** |
| **Strategy ↔ State** | 동일 | Strategy는 **클라이언트가** 교체. State는 **스스로** 전이 |
| **Strategy ↔ Template Method** | 다름 | Strategy는 **합성**. Template Method는 **상속** |
| **Factory Method ↔ Abstract Factory** | 다름 | 전자는 **객체 하나**. 후자는 **제품군 세트** |
| **Facade ↔ Mediator** | 유사 | Facade는 **단방향**. Mediator는 **양방향** |
| **Composite ↔ Decorator** | 유사 | Composite는 **여러 자식**. Decorator는 **자식 하나** |

## Spring이 대신 해주는 것

| 패턴 | Spring에서 |
|---|---|
| Singleton | 기본 빈 스코프 |
| Factory / Abstract Factory | `ApplicationContext`, `@Configuration` |
| Proxy | AOP (`@Transactional`, `@Cacheable`), Feign |
| Observer | `ApplicationEventPublisher`, `@EventListener` |
| Chain of Responsibility | Security Filter Chain, `HandlerInterceptor` |
| Template Method | `JdbcTemplate`, `RestTemplate` 등 `*Template` 전부 |
| Strategy | `List<Interface>` 주입 후 선택 |

## jun-bank에서 실제로 쓸 만한 것

| 우선순위 | 패턴 | 적용처 |
|---|---|---|
| **높음** | **State** | 결제 라이프사이클 상태 전이 (승인→매입→정산, 각종 취소) |
| **높음** | **Strategy** | 수수료 정책, 정산 주기, 취소 유형별 처리 |
| **높음** | **Adapter** | 헥사고날 인프라 계층 전체 |
| **높음** | **Chain of Responsibility** | 승인 규칙 체인 |
| 중간 | **Composite** | 복식부기 전표 구조 |
| 중간 | **Command** | 원장 전표 실행/역분개, Saga 보상 |
| 중간 | **Observer** | 도메인 이벤트 |
| 중간 | **Builder** | 복잡한 애그리게이트 생성 |
| 낮음 | Facade, Template Method | 애플리케이션 서비스·배치에 자연히 나타남 |
| **낮음** | Flyweight, Interpreter, Memento, Prototype, Visitor | 개념만 |

---

## 스스로 답할 질문

1. 패턴을 **먼저 알고 적용**하는 것과 리팩토링하다 **결과적으로 도달**하는 것 — 어느 쪽이 맞는가?
2. Spring이 이미 대신 해주는 패턴은 무엇인가? DI가 Factory/Singleton을 어떻게 흡수했는가?
3. **패턴 과용의 냄새**는 무엇인가? 이름만 패턴이고 실속이 없는 경우를 어떻게 알아채는가?
   - 힌트: 구현체가 하나뿐인 인터페이스, 한 번도 교체되지 않은 Strategy
4. State 패턴과 `enum + switch` 는 언제 갈리는가? 결제 상태 전이에는 무엇이 맞는가?
5. 상속 기반 패턴이 많은데 **합성 우선(composition over inheritance)** 원칙과 충돌하지 않는가?
6. Java 21의 sealed interface + 패턴 매칭이 어떤 GoF 패턴들을 대체하는가?

## 정리 방식 (권고)

23개를 순서대로 훑는 대신, **먼저 문제를 적고 패턴을 붙이는 방향**으로 채운다.

```
문제: 결제 상태가 승인→매입→정산으로 전이하며 각 상태에서 허용되는 조작이 다르다
  → 후보 패턴: State / Strategy / enum+switch
  → 선택과 근거:
  → 선택하지 않은 것과 이유:
```

---

## 참고

- (공부하며 채운다)
