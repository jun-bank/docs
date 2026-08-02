# 01. SOLID 원칙

> 추상화 레벨: ④ 클래스 설계 (일부는 ③ 컴포넌트)
> 책 대응: 2.3.2 SOLID 원칙 (64~82쪽)

---

## 0. 들어가기 전에 — 용어부터

이 문서에서 반복해서 나오는 말들이다. 여기서 한 번 정리하고 시작한다.

| 용어 | 뜻 |
|---|---|
| **결합도 (Coupling)** | A를 바꿀 때 B도 바꿔야 하는 정도. 낮을수록 좋다 |
| **응집도 (Cohesion)** | 한 덩어리 안의 요소들이 서로 얼마나 관련 있는가. 높을수록 좋다 |
| **추상화 (Abstraction)** | 구체적인 것들의 공통점만 뽑아 이름 붙인 것. Java에서는 주로 인터페이스·추상 클래스 |
| **구현체 (Implementation)** | 추상화를 실제로 구현한 클래스 |
| **의존 (Dependency)** | A가 B를 사용하면 "A는 B에 의존한다"고 한다. B가 바뀌면 A가 영향받는다 |
| **계약 (Contract)** | 어떤 타입을 쓸 때 지켜지리라 기대하는 약속. 메서드 시그니처 + 사전조건 + 사후조건 + 불변식 |
| **사전조건 (Precondition)** | 메서드를 호출하기 전에 참이어야 하는 조건 (예: 인자가 null이 아니다) |
| **사후조건 (Postcondition)** | 메서드가 끝난 뒤 참이어야 하는 조건 (예: 반환값은 항상 0 이상) |
| **불변식 (Invariant)** | 객체가 살아 있는 동안 **항상** 참이어야 하는 조건 (예: 계좌 잔액은 음수가 아니다) |

SOLID는 로버트 마틴(Robert C. Martin)이 정리한 **객체지향 설계 5원칙**의 머리글자다. 목적은 하나다 — **변경에 강한 코드**. 요구사항은 반드시 바뀌는데, 바뀔 때 고쳐야 할 곳이 적고 예측 가능하도록 만드는 것이 전부다.

---

## S — 단일 책임 원칙 (SRP, Single Responsibility Principle)

### 정의

> **하나의 클래스는 변경되는 이유가 하나여야 한다.**

흔히 "한 클래스는 한 가지 일만 해야 한다"로 소개되는데, 이 표현은 오해를 부른다. "한 가지 일"의 크기가 사람마다 다르기 때문이다. 정확한 기준은 **변경 이유(reason to change)**다.

로버트 마틴은 나중에 이를 더 명확히 다시 썼다: **"하나의 모듈은 오직 하나의 액터(actor)에 대해서만 책임져야 한다."** 여기서 **액터**란 그 코드의 변경을 요구하는 이해관계자 집단이다 — 회계팀, 운영팀, 보안팀 같은.

### 왜 중요한가

한 클래스가 두 액터를 섬기면, **한쪽의 요구로 바꾼 코드가 다른 쪽을 망가뜨린다.** 서로 상관없는 두 팀이 같은 파일을 놓고 충돌하는 상황이 벌어진다.

### 나쁜 예

```java
// 이 클래스는 변경 이유가 셋이다
public class Payment {
    private Long amount;
    private PaymentStatus status;

    // ① 결제 규칙이 바뀌면 변경 — 액터: 결제 기획팀
    public boolean isApprovable(Long availableBalance) {
        return status == PaymentStatus.PENDING && amount <= availableBalance;
    }

    // ② DB 스키마가 바뀌면 변경 — 액터: 인프라팀
    public void save(Connection conn) throws SQLException {
        PreparedStatement ps = conn.prepareStatement(
            "INSERT INTO payment(amount, status) VALUES (?, ?)");
        ps.setLong(1, amount);
        ps.setString(2, status.name());
        ps.executeUpdate();
    }

    // ③ 리포트 양식이 바뀌면 변경 — 액터: 회계팀
    public String toReportRow() {
        return String.format("%,d원 | %s", amount, status.getLabel());
    }
}
```

세 메서드는 **서로 다른 이유로, 서로 다른 시점에** 바뀐다. 그런데 같은 파일에 있으니 매번 이 파일을 건드리게 되고, 회계 리포트를 고치다가 결제 판단 로직을 실수로 깨뜨릴 수 있다.

### 좋은 예

```java
// ① 결제 규칙 — 도메인
public class Payment {
    private final Money amount;
    private PaymentStatus status;

    public boolean isApprovable(Money availableBalance) {
        return status == PaymentStatus.PENDING && amount.isLessThanOrEqual(availableBalance);
    }
}

// ② 영속화 — 인프라
public class PaymentRepositoryAdapter implements PaymentRepository {
    private final PaymentJpaRepository jpaRepository;

    @Override
    public Payment save(Payment payment) {
        return PaymentMapper.toDomain(jpaRepository.save(PaymentMapper.toEntity(payment)));
    }
}

// ③ 표현 — 프레젠테이션
public class PaymentReportFormatter {
    public String toReportRow(Payment payment) {
        return String.format("%,d원 | %s",
            payment.getAmount().value(), payment.getStatus().getLabel());
    }
}
```

이제 회계 리포트를 바꿔도 도메인 파일은 열리지 않는다.

### 위반 신호

- 클래스 이름에 **"And"나 "Manager", "Util", "Helper"** 가 들어간다 (책임이 뭉뚱그려졌다는 신호)
- 한 클래스를 **서로 다른 이유로 자주 커밋**하게 된다 (git log를 보면 보인다)
- import 문에 **성격이 다른 패키지**가 섞여 있다 (도메인 + JDBC + HTTP)
- 테스트를 쓰려는데 **필요 없는 것까지 준비**해야 한다

### 자주 하는 오해

- ❌ "메서드가 많으면 SRP 위반이다" → 아니다. 메서드가 20개여도 **변경 이유가 하나면** SRP를 지킨 것이다
- ❌ "클래스를 잘게 쪼갤수록 좋다" → 아니다. 함께 변하는 것을 억지로 나누면 **응집도가 떨어지고** 변경 시 여러 파일을 동시에 고쳐야 한다

### jun-bank 연결점

`user-service`의 `CreateUserService`는 ① 사용자 저장 ② Auth Server 호출 ③ 이벤트 발행을 모두 한다. 이게 SRP 위반인지는 판단이 필요하다 — **애플리케이션 서비스의 역할이 원래 "유스케이스 오케스트레이션"** 이기 때문이다. (→ study/03)

반면 `User` 도메인 모델의 `previousStatus` 필드("Auth Server 호출 실패 시 롤백용")는 명확한 위반이다. **사용자 프로필이라는 도메인 개념**과 **분산 트랜잭션 복구**라는 인프라 관심사가 한 클래스에 섞였다.

---

## O — 개방·폐쇄 원칙 (OCP, Open-Closed Principle)

### 정의

> **확장에는 열려 있고, 변경에는 닫혀 있어야 한다.**

새 기능을 추가할 때 **기존 코드를 수정하지 않고 새 코드를 더하는 것만으로** 가능해야 한다는 뜻이다.

### 왜 중요한가

기존 코드를 수정하면 이미 검증된 것이 깨질 위험이 생긴다. 반면 새 클래스를 추가하는 것은 기존 것을 건드리지 않으므로 안전하다. **테스트를 다시 돌릴 범위가 줄어든다**는 것이 실질적 이득이다.

### 나쁜 예

```java
public class FeeCalculator {
    public Money calculate(PaymentType type, Money amount) {
        if (type == PaymentType.CREDIT_CARD) {
            return amount.multiply(0.025);
        } else if (type == PaymentType.DEBIT_CARD) {
            return amount.multiply(0.010);
        } else if (type == PaymentType.BANK_TRANSFER) {   // 새 결제수단이 생길 때마다
            return amount.multiply(0.005);                 // 이 파일을 연다
        }
        throw new IllegalArgumentException("지원하지 않는 결제수단: " + type);
    }
}
```

결제 수단이 하나 늘 때마다 이 클래스를 열어 `else if`를 추가한다. **변경에 닫혀 있지 않다.**

### 좋은 예

```java
// 추상화 — 확장점
public interface FeePolicy {
    boolean supports(PaymentType type);
    Money calculate(Money amount);
}

// 구현체 — 새로 추가되는 부분
@Component
public class CreditCardFeePolicy implements FeePolicy {
    public boolean supports(PaymentType type) { return type == PaymentType.CREDIT_CARD; }
    public Money calculate(Money amount) { return amount.multiply(0.025); }
}

@Component
public class DebitCardFeePolicy implements FeePolicy {
    public boolean supports(PaymentType type) { return type == PaymentType.DEBIT_CARD; }
    public Money calculate(Money amount) { return amount.multiply(0.010); }
}

// 사용하는 쪽 — 더 이상 바뀌지 않는다
@Service
public class FeeCalculator {
    private final List<FeePolicy> policies;   // Spring이 모든 구현체를 주입해준다

    public Money calculate(PaymentType type, Money amount) {
        return policies.stream()
            .filter(p -> p.supports(type))
            .findFirst()
            .orElseThrow(() -> new UnsupportedPaymentTypeException(type))
            .calculate(amount);
    }
}
```

이제 계좌이체 수수료를 추가하려면 **새 클래스 하나만 만들면 된다.** `FeeCalculator`는 열지 않는다.

### 대가 — 공짜가 아니다

확장점을 만들면 **간접 계층(indirection)**이 하나 늘어난다. 코드를 따라가기 어려워지고, 파일 수가 늘고, "이 인터페이스의 구현체가 어디 있지?"를 찾아야 한다.

**핵심 판단**: 확장이 **실제로 일어날 축**에만 확장점을 연다. 안 일어날 축에 미리 열어두면 그건 **추측성 일반화(speculative generality)** 라는 안티패턴이다.

> 실무 감각: 두 번째 케이스가 생겼을 때 추상화한다. 첫 번째에 미리 하지 않는다. (**"삼진 아웃 규칙"** — 세 번째 중복에서 추상화하라는 경험칙도 널리 쓰인다)

### 위반 신호

- 새 종류를 추가할 때마다 **같은 파일의 `if/switch`를 찾아 고친다**
- 그 `switch`가 **여러 곳에 흩어져** 있다 (한 곳만 고치고 다른 곳을 빠뜨린다)

### jun-bank 연결점

- 결제 수단(체크/신용), 취소 유형(승인취소/부분취소/환불/망취소), 정산 파일 포맷 — 전부 **늘어날 축**이다
- 반면 "은행이 여러 개일 경우" 같은 건 안 늘어난다. 열지 않는다

---

## L — 리스코프 치환 원칙 (LSP, Liskov Substitution Principle)

### 정의

> **하위 타입은 상위 타입을 대체할 수 있어야 한다.**

`Parent`를 쓰는 코드에 `Child`를 넣어도 **프로그램이 여전히 올바르게 동작**해야 한다는 뜻이다. 바바라 리스코프(Barbara Liskov)가 정식화했다.

컴파일이 되는 것과는 다른 이야기다. **컴파일은 되는데 의미가 깨지는 것**이 LSP 위반이다.

### 계약 관점의 정확한 규칙

하위 타입이 상위 타입을 대체하려면:

| 규칙 | 뜻 |
|---|---|
| **사전조건을 강화하지 마라** | 부모보다 **더 까다로운 입력**을 요구하면 안 된다 |
| **사후조건을 약화하지 마라** | 부모보다 **덜 보장**하면 안 된다 |
| **불변식을 유지하라** | 부모가 지키던 조건을 깨면 안 된다 |
| **예외를 새로 던지지 마라** | 부모가 던지지 않던 예외를 던지면 호출자가 대비할 수 없다 |

### 나쁜 예 — 고전적인 정사각형/직사각형

```java
public class Rectangle {
    protected int width, height;
    public void setWidth(int w) { this.width = w; }
    public void setHeight(int h) { this.height = h; }
    public int area() { return width * height; }
}

public class Square extends Rectangle {
    @Override public void setWidth(int w)  { this.width = w; this.height = w; }
    @Override public void setHeight(int h) { this.width = h; this.height = h; }
}

// 사용하는 쪽
void test(Rectangle r) {
    r.setWidth(5);
    r.setHeight(4);
    assert r.area() == 20;   // Rectangle이면 통과, Square를 넣으면 16이 나와 실패
}
```

수학적으로는 정사각형이 직사각형이지만, **"너비와 높이를 독립적으로 바꿀 수 있다"는 계약** 아래에서는 아니다. LSP는 **개념의 포함관계가 아니라 계약의 호환성**을 본다.

### 결제 도메인의 예

```java
// 나쁜 예
public class Transaction {
    public void cancel() { /* 취소 처리 */ }
}

public class SettledTransaction extends Transaction {
    @Override
    public void cancel() {
        throw new UnsupportedOperationException("정산 완료 거래는 취소할 수 없습니다");
        // ← 부모에 없던 예외. 호출자가 대비할 수 없다 = LSP 위반
    }
}
```

```java
// 좋은 예 — 능력을 타입으로 나눈다
public interface Transaction {
    TransactionId id();
    Money amount();
}

public interface Cancellable {
    void cancel();
}

public class AuthorizedTransaction implements Transaction, Cancellable { /* 취소 가능 */ }
public class SettledTransaction   implements Transaction { /* Cancellable을 구현하지 않는다 */ }

// 사용하는 쪽 — 타입으로 구분되므로 실행 시점에 터지지 않는다
void cancelIfPossible(Transaction tx) {
    if (tx instanceof Cancellable c) {
        c.cancel();
    }
}
```

### 위반 신호

- 오버라이드한 메서드가 **아무것도 안 하거나 예외를 던진다**
- 사용하는 쪽에 **`instanceof` 로 분기**하는 코드가 늘어난다 (다형성이 깨졌다는 증거)
- 하위 클래스마다 **다른 사용법 설명**이 필요하다

### jun-bank 연결점

거래 상태(승인/매입/정산/취소)마다 **허용되는 조작이 다르다.** 이걸 상속으로 표현하면 LSP 위반이 나기 쉽다. State 패턴(→ study/04) 또는 능력 인터페이스 분리가 대안이다.

---

## I — 인터페이스 분리 원칙 (ISP, Interface Segregation Principle)

### 정의

> **클라이언트는 자신이 쓰지 않는 메서드에 의존하도록 강요받으면 안 된다.**

크고 뚱뚱한 인터페이스 하나보다, **역할별로 잘게 나뉜 인터페이스 여러 개**가 낫다는 뜻이다.

### 왜 중요한가

안 쓰는 메서드에 의존하면 **그 메서드가 바뀔 때 나도 영향받는다.** 재컴파일, 재배포, 재테스트가 따라온다. 또 구현체는 필요 없는 메서드까지 억지로 채워야 한다.

### 나쁜 예

```java
public interface UserRepository {
    User save(User user);
    Optional<User> findById(UserId id);
    boolean existsByEmail(String email);
    List<User> search(UserSearchCondition condition);
    void delete(UserId id);
    long countByStatus(UserStatus status);
    List<User> findDormantUsers(LocalDate before);
    void bulkUpdateStatus(List<UserId> ids, UserStatus status);
}

// 조회만 필요한 곳도 이 8개 전부에 의존하게 된다
public class GetUserService {
    private final UserRepository repository;   // findById 하나만 쓰는데...
}
```

### 좋은 예

```java
public interface UserReader {
    Optional<User> findById(UserId id);
    boolean existsByEmail(String email);
}

public interface UserWriter {
    User save(User user);
    void delete(UserId id);
}

public interface UserSearcher {
    List<User> search(UserSearchCondition condition);
}

// 각자 필요한 것만 의존한다
public class GetUserService {
    private final UserReader userReader;
}

public class CreateUserService {
    private final UserReader userReader;   // 중복 검사용
    private final UserWriter userWriter;
}
```

구현 클래스 하나가 세 인터페이스를 모두 구현해도 된다. **중요한 건 "누가 무엇에 의존하는가"** 지 파일 개수가 아니다.

```java
@Repository
public class UserRepositoryAdapter implements UserReader, UserWriter, UserSearcher {
    // 구현은 한 곳, 노출은 역할별로
}
```

### 헥사고날 아키텍처와의 관계

포트(Port)를 설계할 때 ISP가 직접 적용된다. **포트는 "구현체가 제공할 수 있는 것"이 아니라 "사용하는 쪽이 필요로 하는 것"으로 정의**해야 한다. 이 방향이 뒤집히면 인터페이스가 구현을 그대로 베낀 껍데기가 된다.

### jun-bank 연결점

`AuthServicePort`가 무엇을 노출하는지 점검 대상. `user-service`가 실제로 필요한 것만 있는가, 아니면 auth-server가 제공하는 것을 그대로 옮겼는가?

---

## D — 의존관계 역전 원칙 (DIP, Dependency Inversion Principle)

### 정의

> **상위 수준 모듈이 하위 수준 모듈에 의존해서는 안 된다. 둘 다 추상화에 의존해야 한다.**
> **추상화가 세부사항에 의존해서는 안 된다. 세부사항이 추상화에 의존해야 한다.**

여기서 **상위 수준(high-level)**은 비즈니스 정책(무엇을 할 것인가)이고, **하위 수준(low-level)**은 구체적 수단(어떻게 할 것인가 — DB, HTTP, 파일)이다.

### "역전"이 무엇을 뒤집는가

일반적인 흐름은 이렇다:

```
[비즈니스 로직] ──의존──▶ [DB 코드]
```

비즈니스가 DB를 알고 있다. DB를 바꾸면 비즈니스 코드가 바뀐다.

DIP를 적용하면:

```
[비즈니스 로직] ──의존──▶ [인터페이스] ◀──구현──  [DB 코드]
                          (비즈니스가 소유)
```

**화살표 방향이 뒤집혔다.** DB 코드가 비즈니스가 정의한 인터페이스를 구현하는 쪽이 되었다. 이게 "역전"의 뜻이다.

핵심은 **인터페이스를 누가 소유하는가**다. 인터페이스가 도메인 패키지 안에 있어야 진짜 역전이다.

### 나쁜 예

```java
package com.jun_bank.card.application;

import com.jun_bank.card.infrastructure.persistence.CardJpaRepository;  // ← 인프라를 import

@Service
public class AuthorizePaymentService {
    private final CardJpaRepository jpaRepository;   // JPA에 직접 의존

    public void authorize(...) {
        CardEntity entity = jpaRepository.findById(id).orElseThrow();
        // 도메인 로직이 JPA 엔티티를 직접 다룬다
    }
}
```

### 좋은 예

```java
// application/port/out/ — 애플리케이션이 소유하는 인터페이스
package com.jun_bank.card.application.port.out;

public interface CardRepository {
    Optional<Card> findById(CardId id);      // 도메인 타입만 사용
    Card save(Card card);
}

// application/service/ — 인프라를 전혀 모른다
package com.jun_bank.card.application.service;

@Service
@RequiredArgsConstructor
public class AuthorizePaymentService implements AuthorizePaymentUseCase {
    private final CardRepository cardRepository;   // 추상화에만 의존

    public AuthorizationResult authorize(AuthorizeCommand command) {
        Card card = cardRepository.findById(command.cardId())
            .orElseThrow(() -> CardException.notFound(command.cardId()));
        // 순수 도메인 로직
    }
}

// infrastructure/ — 여기가 위쪽 인터페이스를 구현한다 (의존 방향이 안쪽을 향한다)
package com.jun_bank.card.infrastructure.persistence;

@Repository
@RequiredArgsConstructor
public class CardRepositoryAdapter implements CardRepository {
    private final CardJpaRepository jpaRepository;
    private final CardMapper mapper;

    @Override
    public Optional<Card> findById(CardId id) {
        return jpaRepository.findById(id.value()).map(mapper::toDomain);
    }

    @Override
    public Card save(Card card) {
        return mapper.toDomain(jpaRepository.save(mapper.toEntity(card)));
    }
}
```

### DIP vs DI (의존성 주입) — 자주 혼동되는 지점

| | DIP | DI (Dependency Injection) |
|---|---|---|
| 성격 | **설계 원칙** | **구현 기법** |
| 관심 | 의존의 **방향** | 의존 객체를 **누가 넣어주는가** |
| 예 | 인터페이스를 도메인이 소유 | 생성자 주입, Spring `@Autowired` |

**DI를 써도 DIP를 어길 수 있다.** 생성자로 `CardJpaRepository`를 주입받으면 DI는 했지만 DIP는 어긴 것이다 — 여전히 구체 클래스에 의존하고 있으니까.

### 위반 신호

- 도메인·애플리케이션 패키지에서 `javax.persistence`, `org.springframework.jdbc`, `feign` 같은 걸 **import** 한다
- 인터페이스가 **인프라 패키지 안에** 있다
- 인터페이스 메서드 시그니처에 **엔티티·DTO 같은 인프라 타입**이 등장한다

### jun-bank 연결점

현재 구조는 `application/port/out/`에 인터페이스를 두고 `infrastructure/`에서 구현하는 형태로 **DIP를 지키고 있다.** 다만 점검할 것: 포트 메서드가 도메인 타입만 쓰는가, 아니면 엔티티가 새어나오는가.

---

## 원칙 간의 관계와 충돌

### 서로 돕는 관계

```
DIP ──▶ 경계를 만든다 ──▶ OCP 가능해진다 ──▶ 확장이 안전해진다
 ▲                              │
 │                              ▼
ISP ──▶ 경계를 얇게 유지 ──▶ LSP 지키기 쉬워진다
                               │
SRP ──▶ 책임이 하나면 ─────────┘  대체 가능성이 자연히 확보된다
```

### 충돌하는 지점

| 충돌 | 상황 | 판단 |
|---|---|---|
| **SRP ↔ 응집도** | 잘게 나눌수록 SRP는 지켜지지만 함께 변하는 것이 흩어진다 | **함께 변하는 것은 함께 둔다.** SRP의 기준은 "변경 이유"지 "크기"가 아니다 |
| **OCP ↔ 단순함** | 확장점을 열수록 간접 계층이 늘어 읽기 어려워진다 | **실제로 확장되는 축에만** 연다 |
| **ISP ↔ 파일 수** | 인터페이스를 나눌수록 파일이 는다 | 구현은 한 클래스로 합쳐도 된다. **의존 방향이 중요하지 파일 수가 아니다** |
| **DIP ↔ 생산성** | 모든 것에 포트를 만들면 보일러플레이트가 폭증 | **경계를 넘는 것**(DB·외부 API·메시징)에만 적용. 내부 협력 객체까지 하지 않는다 |

---

## 스스로 답할 질문

1. SRP의 "단일 책임"과 응집도는 같은 말인가?
   - 힌트: SRP는 **변경 이유**를 보고, 응집도는 **요소 간 관련성**을 본다. 대체로 함께 가지만 같지 않다
2. OCP를 지키려고 만든 추상화가 한 번도 확장되지 않았다면 그건 지킨 것인가 낭비인가?
3. DIP를 지키면 자동으로 테스트하기 쉬워지는가? 그 인과는 무엇인가?
   - 힌트: 인터페이스가 있으면 가짜 구현(Mock/Stub)을 끼울 수 있다
4. 5개 원칙 중 서로 충돌하는 경우가 있는가? 무엇을 우선하는가?
5. 이 원칙들이 클래스 레벨을 넘어 **모듈·아키텍처 레벨**에도 적용되는가?
   - 힌트: SRP → 바운디드 컨텍스트, DIP → 헥사고날, ISP → API 계약 설계, OCP → 플러그인 아키텍처

---

## jun-bank 적용 검토 (공부 후 채운다)

| 원칙 | 점검 대상 | 판단 |
|---|---|---|
| SRP | `User` 도메인 모델에 `previousStatus`(분산 트랜잭션 롤백용) 필드가 있는 것 | |
| SRP | `CreateUserService`가 저장·외부호출·이벤트발행을 모두 수행하는 것 | |
| LSP | 거래 상태별로 허용 조작이 다른 구조를 어떻게 표현할 것인가 | |
| ISP | `AuthServicePort`가 노출하는 오퍼레이션 범위 | |
| DIP | 포트 메서드에 인프라 타입이 새어나오지 않는가 | |
| OCP | 결제 수단·취소 유형·정산 파일 포맷의 확장점 설계 | |
| OCP | 서비스마다 복붙된 `global/` 설정 클래스들 | |

---

## 참고

- (공부하며 채운다)
