# 02. 클린 코드 — CLEAN 5속성

> 추상화 레벨: ③ 컴포넌트 설계 · ④ 클래스 설계
> 책 대응: 2.3.3 실천 방법 (82쪽)

**CLEAN** = **C**ohesive · **L**oosely Coupled · **E**ncapsulated · **A**ssertive · **N**onredundant

좋은 코드가 가져야 할 5가지 속성을 묶은 두문자어다. SOLID가 **"어떻게 설계할 것인가"의 원칙**이라면, CLEAN은 **"결과물이 어떤 성질을 가져야 하는가"의 속성**이다. 즉 SOLID는 수단, CLEAN은 상태에 가깝다.

---

## 0. 들어가기 전에 — 용어

| 용어 | 뜻 |
|---|---|
| **코드 냄새 (Code Smell)** | 버그는 아니지만 설계에 문제가 있음을 시사하는 징후 |
| **리팩토링 (Refactoring)** | 겉보기 동작을 바꾸지 않으면서 내부 구조를 개선하는 것 |
| **부수 효과 (Side Effect)** | 메서드가 반환값 말고 다른 것을 바꾸는 것 (필드 변경, 파일 쓰기 등) |
| **불변 객체 (Immutable Object)** | 생성 후 상태가 바뀌지 않는 객체. `record`, `final` 필드 |
| **방어적 복사 (Defensive Copy)** | 내부 컬렉션을 그대로 주지 않고 복사본을 주는 것 |
| **빈약한 도메인 모델 (Anemic Domain Model)** | 데이터만 있고 행위가 없는 도메인 객체. getter/setter 덩어리 |

---

## C — 응집성 (Cohesive)

### 정의

> **한 덩어리 안의 요소들이 하나의 목적을 향해 함께 작동하는 정도.**

높은 응집도란 "이 클래스에서 아무거나 하나 골라도 다른 것들과 명백히 관련 있다"는 상태다.

### 응집도의 등급 (낮은 것부터)

전통적으로 7단계로 분류한다. **아래로 갈수록 좋다.**

| 등급 | 뜻 | 예 |
|---|---|---|
| **우연적 (Coincidental)** | 아무 관련 없는 것들이 그냥 모여 있음 | `CommonUtils`, `Helper` |
| **논리적 (Logical)** | 비슷한 범주라서 모음. 실제 협력은 없음 | 모든 입력 검증을 한 클래스에 |
| **시간적 (Temporal)** | 같은 시점에 실행되어서 모음 | `initialize()` 안에 온갖 초기화 |
| **절차적 (Procedural)** | 정해진 순서로 실행되어서 모음 | |
| **통신적 (Communicational)** | 같은 데이터를 다뤄서 모음 | 같은 테이블을 읽고 쓰는 메서드들 |
| **순차적 (Sequential)** | 앞 출력이 뒤 입력이 됨 | |
| **기능적 (Functional)** ★ | 하나의 잘 정의된 작업만 수행 | **목표** |

### 나쁜 예 — 우연적 응집

```java
public class CommonUtils {
    public static String formatDate(LocalDate date) { ... }
    public static boolean isValidEmail(String email) { ... }
    public static Money calculateFee(Money amount) { ... }
    public static String maskCardNumber(String pan) { ... }
    public static byte[] compress(byte[] data) { ... }
}
```

이 다섯은 **서로 아무 관계가 없다.** "공통이라서" 모였을 뿐이다. 이런 클래스는 시간이 지나면 무한히 커지고, 모든 코드가 여기에 의존하게 되어 결합의 허브가 된다.

### 좋은 예 — 기능적 응집

```java
// 카드번호에 관한 모든 것이 한 곳에, 그리고 그것만
public record CardNumber(String value) {

    private static final Pattern PATTERN = Pattern.compile("\\d{16}");

    public CardNumber {
        if (value == null || !PATTERN.matcher(value).matches()) {
            throw CardException.invalidCardNumber(value);
        }
    }

    /** 화면 표시용 마스킹: 1234-****-****-5678 */
    public String masked() {
        return value.substring(0, 4) + "-****-****-" + value.substring(12);
    }

    /** 카드사 식별을 위한 앞 6자리 (BIN) */
    public String bin() {
        return value.substring(0, 6);
    }
}
```

### 감지 방법

- **클래스 이름으로 설명해 보기**: "이 클래스는 ○○을 한다"를 **접속사 없이** 말할 수 있는가?
- **필드 사용률 보기**: 메서드 A는 필드 1,2만 쓰고 메서드 B는 필드 3,4만 쓴다면 → **두 클래스로 나눌 신호**
- **테스트 준비 코드 보기**: 한 메서드를 테스트하려는데 관계없는 것까지 준비해야 한다면 응집도가 낮다

### jun-bank 연결점

`card-service` 안에 `card`(카드 발급·관리)와 `payment`(결제) 두 도메인이 함께 있다. 이 둘은 **함께 변하는가?** 카드 발급 규칙이 바뀔 때 결제 로직도 바뀌는가? 아니라면 응집도가 낮은 것이고, 서비스 분할의 근거가 된다.

---

## L — 느슨한 결합 (Loosely Coupled)

### 정의

> **A를 바꿀 때 B를 함께 바꿔야 하는 정도가 낮은 상태.**

결합 자체를 없앨 수는 없다. 협력하려면 어느 정도는 알아야 한다. 목표는 **"얼마나 아는가"를 최소화**하는 것이다.

### 결합의 등급 (나쁜 것부터)

| 등급 | 뜻 | 판정 |
|---|---|---|
| **내용 결합 (Content)** | 다른 모듈의 내부를 직접 건드림 | 금지 |
| **공통 결합 (Common)** | 전역 변수를 공유 | 금지 |
| **외부 결합 (External)** | 외부 포맷·프로토콜을 공유 | 최소화 |
| **제어 결합 (Control)** | 플래그를 넘겨 상대의 동작을 지시 | 피할 것 |
| **스탬프 결합 (Stamp)** | 필요 이상의 큰 구조체를 넘김 | 줄일 것 |
| **데이터 결합 (Data)** ★ | 필요한 값만 인자로 넘김 | **목표** |

### 나쁜 예 — 제어 결합

```java
// 호출자가 상대의 내부 동작을 지시한다
public void processPayment(Payment payment, boolean isRefund, boolean skipValidation) {
    if (!skipValidation) { validate(payment); }
    if (isRefund) {
        reverseLedger(payment);
    } else {
        postLedger(payment);
    }
}

// 호출부: 이게 무슨 뜻인지 읽을 수 없다
processPayment(payment, true, false);
```

**플래그 인자(boolean parameter)** 는 "이 메서드는 사실 두 가지 일을 한다"는 자백이다.

### 좋은 예

```java
public void postPayment(Payment payment) {
    validate(payment);
    postLedger(payment);
}

public void refundPayment(Payment payment) {
    validate(payment);
    reverseLedger(payment);
}

// 호출부가 스스로 설명된다
refundPayment(payment);
```

### 나쁜 예 — 스탬프 결합

```java
// 수수료 계산에 필요한 건 금액과 카드 종류뿐인데 주문 전체를 받는다
public Money calculateFee(Order order) {
    return order.getPayment().getAmount().multiply(rateOf(order.getCard().getType()));
}
```

`Order`의 구조가 바뀌면 이 메서드가 깨진다. 실제로 필요한 것은 두 개뿐인데.

```java
// 좋은 예 — 데이터 결합
public Money calculateFee(Money amount, CardType cardType) {
    return amount.multiply(rateOf(cardType));
}
```

### 결합을 줄이려다 오히려 복잡해지는 지점

**모든 결합을 없애려 하면 안 된다.** 흔한 과잉:

- 두 클래스 사이에 **이벤트 버스를 넣어** 직접 호출을 없앴는데, 이제 흐름을 따라갈 수 없다
- **인터페이스를 남발**해서 구현체가 하나뿐인 인터페이스가 수십 개 생겼다
- 서비스를 잘게 쪼개서 **네트워크 홉이 늘고** 디버깅이 불가능해졌다

> 판단 기준: **결합을 줄인 대가로 무엇을 잃었는가?** 흐름의 가시성을 잃었다면 대개 손해다.

### jun-bank 연결점

`user-service`가 `auth-server`를 **Feign 동기 호출**로 부른다. 이건 시간적 결합(temporal coupling)이다 — auth-server가 죽으면 회원가입이 안 된다. 이벤트로 바꾸면 결합은 줄지만 **결과적 일관성**을 감수해야 한다. **무엇을 잃고 무엇을 얻는지**가 이 판단의 핵심이다.

---

## E — 캡슐화 (Encapsulated)

### 정의

> **내부 표현을 감추고, 외부에는 의미 있는 조작만 노출하는 것.**

단순히 필드를 `private`으로 하는 게 아니다. **"어떻게 저장되어 있는가"를 밖에서 몰라도 되게 만드는 것**이 핵심이다.

### getter/setter를 열면 캡슐화가 깨지는가

**setter는 대체로 깨뜨린다. getter는 경우에 따라 다르다.**

setter가 위험한 이유: 객체가 **불변식을 지킬 기회를 잃는다.**

```java
// 나쁜 예 — 캡슐화 없음
public class Account {
    private Money balance;
    public Money getBalance() { return balance; }
    public void setBalance(Money balance) { this.balance = balance; }
}

// 호출부가 규칙을 직접 구현한다 — 여러 곳에 흩어지고, 하나만 빠뜨려도 데이터가 깨진다
Money newBalance = account.getBalance().minus(amount);
if (newBalance.isNegative()) throw new InsufficientBalanceException();
account.setBalance(newBalance);
```

```java
// 좋은 예 — 규칙이 객체 안에 있다
public class Account {
    private Money balance;
    private Money holdAmount;   // 승인으로 점유된 금액

    /** 가용잔액 = 원장잔액 − 홀딩 */
    public Money availableBalance() {
        return balance.minus(holdAmount);
    }

    /** 결제 승인을 위해 금액을 점유한다 */
    public void hold(Money amount) {
        if (amount.isGreaterThan(availableBalance())) {
            throw AccountException.insufficientAvailableBalance(availableBalance(), amount);
        }
        this.holdAmount = this.holdAmount.plus(amount);
    }

    /** 홀딩 해제 (승인취소·만료) */
    public void releaseHold(Money amount) {
        if (amount.isGreaterThan(holdAmount)) {
            throw AccountException.holdExceeded(holdAmount, amount);
        }
        this.holdAmount = this.holdAmount.minus(amount);
    }
}
```

이제 **"가용잔액을 넘겨 점유할 수 없다"는 불변식이 한 곳에서만 지켜진다.** 밖에서는 `balance`와 `holdAmount`가 어떻게 저장되는지 알 필요가 없다.

### getter가 위험해지는 경우 — 가변 객체 반환

```java
// 나쁜 예
public class Transfer {
    private final List<TransferStep> steps = new ArrayList<>();
    public List<TransferStep> getSteps() { return steps; }   // 내부 리스트를 그대로 준다
}

// 밖에서 마음대로 바꿀 수 있다
transfer.getSteps().clear();   // 캡슐화 붕괴
```

```java
// 좋은 예 — 방어적 복사 또는 불변 뷰
public List<TransferStep> getSteps() {
    return List.copyOf(steps);          // 불변 복사본
}
// 또는
public List<TransferStep> getSteps() {
    return Collections.unmodifiableList(steps);
}
```

### JPA와의 현실적 타협

JPA는 기본 생성자와 필드 접근을 요구한다. 그래서 흔히 이렇게 한다:

```java
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)   // JPA만 쓸 수 있게
@Getter                                              // 필요한 것만 열어도 된다
public class AccountEntity extends BaseEntity {
    // setter는 만들지 않는다
}
```

> **핵심 판단**: 도메인 모델과 JPA 엔티티를 **분리**하면 이 타협을 도메인까지 끌고 들어오지 않아도 된다. jun-bank는 이미 `domain/model`과 `infrastructure/persistence/entity`를 분리하고 `Mapper`로 변환하는 구조를 쓰고 있다.

### jun-bank 연결점

`User` 도메인 모델에 클래스 레벨 `@Getter`가 붙어 있다. 모든 필드가 노출된다는 뜻이다. 이게 필요한 노출인지, 관성인지 점검할 대상이다.

---

## A — 단정적 (Assertive)

### 정의

> **객체가 자기 데이터에 대한 판단을 스스로 내리는가, 아니면 남이 데이터를 꺼내가서 대신 판단하는가.**

"Assertive"는 "단호한, 자기주장이 있는"이라는 뜻이다. 객체가 수동적인 데이터 가방이 아니라 **행위의 주체**여야 한다는 속성이다.

### Tell, Don't Ask

이 속성을 실천하는 원칙이 **"묻지 말고 시켜라(Tell, Don't Ask)"** 다.

```java
// Ask — 물어보고 내가 판단한다 (비단정적)
if (card.getStatus() == CardStatus.ACTIVE
        && card.getExpiryDate().isAfter(LocalDate.now())
        && !card.isBlocked()) {
    approve();
}
```

```java
// Tell — 시킨다 (단정적)
if (card.isUsable()) {
    approve();
}

// Card 안에
public boolean isUsable() {
    return status == CardStatus.ACTIVE
        && expiryDate.isAfter(LocalDate.now())
        && !blocked;
}
```

**왜 중요한가**: 첫 번째 방식은 같은 조건식이 코드 여러 곳에 복사된다. 카드 사용 가능 조건이 하나 늘면 **모든 복사본을 찾아 고쳐야 한다.** 하나라도 빠뜨리면 버그다.

### 빈약한 도메인 모델 (Anemic Domain Model)

데이터만 있고 행위가 없는 도메인 객체를 말한다. 마틴 파울러(Martin Fowler)가 **안티패턴**으로 지목했다.

```java
// 빈약한 모델 — 사실상 DTO
public class Payment {
    private Long id;
    private Long amount;
    private String status;
    // getter/setter만 30줄
}

// 로직은 전부 서비스에
public class PaymentService {
    public void approve(Payment payment, Long availableBalance) {
        if (!"PENDING".equals(payment.getStatus())) throw ...;
        if (payment.getAmount() > availableBalance) throw ...;
        payment.setStatus("APPROVED");
    }
}
```

**무엇이 문제인가**: 규칙이 객체 밖에 있으므로 **누구든 규칙을 우회할 수 있다.** `payment.setStatus("APPROVED")`를 아무 데서나 호출하면 끝이다. 상태 전이 규칙이 강제되지 않는다.

### 다만 — 항상 나쁜가?

**아니다.** 다음 경우엔 빈약한 모델이 합리적이다:

- **CRUD만 하는 단순 영역** (설정값 관리 등) — 규칙이 없는데 억지로 만들 필요 없다
- **조회 전용 모델(Read Model)** — CQRS에서 조회 측은 데이터 그 자체가 목적이다
- **DTO·계약 객체** — 경계를 넘나드는 데이터 운반체는 원래 데이터 가방이 맞다

> 판단 기준: **지켜야 할 불변식이 있는가?** 있으면 객체 안에 넣는다. 없으면 억지로 만들지 않는다.

### jun-bank 연결점

`User`는 상태 전이 규칙을 스스로 가지고 있어 비교적 단정적이다. 반면 `CreateUserService`의 이메일 중복 검사는 서비스가 판단한다 — 이건 DB 조회가 필요해서 **불가피한 경우**에 해당한다. (→ study/03에서 다룬다)

---

## N — 비중복 (Nonredundant)

### 정의

> **같은 지식이 시스템 안에 두 번 이상 표현되지 않는 상태.**

### DRY와 같은 말인가?

거의 같지만 **DRY의 정의가 더 정확하다.** DRY(Don't Repeat Yourself)의 원문은 이렇다:

> "모든 지식은 시스템 내에서 **단일하고 모호하지 않은, 권위 있는 표현**을 가져야 한다."

주목할 점: **"코드"가 아니라 "지식"**이다. 겉모양이 같은 코드가 두 개 있어도, **표현하는 지식이 다르면 중복이 아니다.**

### 우연한 중복 vs 진짜 중복

```java
// A: 카드 결제 수수료
public Money calculateCardFee(Money amount) {
    return amount.multiply(new BigDecimal("0.025"));
}

// B: 정산 수수료
public Money calculateSettlementFee(Money amount) {
    return amount.multiply(new BigDecimal("0.025"));
}
```

코드가 똑같다. 합쳐야 할까?

**아니다.** 이 둘은 **우연히 같은 값**일 뿐 서로 다른 지식이다. 카드 수수료가 3%로 오르면 정산 수수료는 그대로여야 한다. 합쳐두면 하나를 바꿀 때 다른 하나가 딸려 바뀐다 — **더 위험한 버그**다.

> 판단 기준: **"이 둘은 항상 함께 바뀌는가?"** 함께 바뀌면 중복이고, 따로 바뀌면 우연이다.

### 진짜 중복의 예

```java
// 세 곳에 흩어진 "가용잔액" 계산 — 같은 지식의 중복
// AccountService
Money available = account.getBalance().minus(account.getHoldAmount());
// AuthorizationService
Money available = account.getBalance().minus(account.getHoldAmount());
// BalanceQueryService
Money available = account.getBalance().minus(account.getHoldAmount());
```

"가용잔액이란 무엇인가"는 **하나의 지식**이다. 지급정지액을 빼는 규칙이 추가되면 세 곳을 다 고쳐야 하고, 하나만 빠뜨리면 조회 화면과 승인 판단이 어긋난다.

```java
// 지식을 한 곳으로
public class Account {
    public Money availableBalance() {
        return balance.minus(holdAmount).minus(suspendedAmount);
    }
}
```

### 의도적 중복이 정당한 경우 — 서비스 경계

마이크로서비스에서는 **중복이 오히려 권장**되는 경우가 있다.

```java
// account-service 의 Money
public record Money(long amount, Currency currency) { ... }

// ledger-service 의 Money
public record Money(long amount, Currency currency) { ... }
```

이걸 공유 라이브러리로 합치면:
- **장점**: 중복 제거, 정의 일치
- **단점**: 두 서비스가 **같은 라이브러리 버전에 묶인다.** 한쪽 요구로 `Money`를 바꾸면 다른 쪽도 재배포해야 한다 → **독립 배포라는 마이크로서비스의 핵심 이점이 사라진다**

> 이것이 **N(비중복) ↔ L(느슨한 결합) 의 정면 충돌**이다. 정답은 상황마다 다르다.

### jun-bank 연결점

`Money`가 account / card / payment / ledger / transaction / transfer **6곳에 복붙**되어 있다. 이게

- **N 위반**인가 (같은 지식의 중복) — 그렇다면 common-lib로 옮긴다
- **L을 지키기 위한 정당한 중복**인가 — 그렇다면 그대로 둔다

**이 질문의 답이 곧 ADR이다.** → `drafts/architecture/decisions/` (ADR-0005 예정)

판단 재료:
- 6개의 `Money`가 **실제로 같은가?** 정밀도·통화·반올림 규칙이 서비스마다 달라야 할 이유가 있는가?
- `common-lib`은 이미 **외부 Maven 저장소로 배포**되고 있다 (제약 TC-3). 버전을 올릴 때마다 6개 서비스를 반영해야 하는 비용은 얼마인가?

---

## 5속성 간의 긴장 관계

| 긴장 | 내용 | 판단 |
|---|---|---|
| **N ↔ L** | 중복을 없애려 공유하면 결합이 생긴다 | **서비스 경계를 넘는 공유는 신중히.** 경계 안에서는 N 우선 |
| **C ↔ N** | 응집을 위해 함께 두면 다른 곳과 중복될 수 있다 | 함께 변하는 것이 더 중요 → C 우선 |
| **E ↔ 편의성** | 캡슐화하면 매번 메서드를 만들어야 한다 | **불변식이 있으면 E 우선**, 없으면 완화 가능 |
| **A ↔ 계층 분리** | 도메인에 로직을 넣으려는데 인프라가 필요하다 | 도메인 서비스 또는 애플리케이션 계층으로 (→ study/03) |

---

## 스스로 답할 질문

1. 5개 속성 중 서로 **긴장 관계**에 있는 쌍은? (위 표를 보기 전에 스스로 답해 보기)
2. `Money`가 6개 서비스에 복붙된 것은 **N 위반**인가, **L을 지키기 위한 정당한 중복**인가?
   → 이 답이 `drafts/architecture/decisions/` 의 ADR로 이어진다
3. "Assertive"와 SOLID의 SRP는 어떻게 다른가?
   - 힌트: SRP는 **책임의 개수**, Assertive는 **책임의 위치**
4. 캡슐화가 잘 된 코드는 테스트하기 쉬운가 어려운가? 왜인가?
   - 힌트: 내부 상태를 확인할 수 없다 vs 의미 있는 조작만 검증하면 된다
5. 이 5속성은 어느 추상화 레벨까지 올라가는가? **서비스 레벨**에도 적용되는가?
   - 힌트: 응집도 → 바운디드 컨텍스트, 결합도 → 서비스 간 통신, 캡슐화 → API 경계

---

## jun-bank 적용 검토 (공부 후 채운다)

| 속성 | 점검 대상 | 판단 |
|---|---|---|
| C | `card-service` 안에 `card`와 `payment` 두 도메인이 함께 있는 것 | |
| L | 서비스 간 Feign 동기 호출 (`user-service` → `auth-server`) | |
| E | `User` 도메인 모델의 클래스 레벨 `@Getter` | |
| A | 도메인 모델이 상태 전이 규칙을 스스로 판단하는가 | |
| N | `Money` 6벌 | |
| N | `global/` 설정 클래스 전 서비스 복붙 | |

---

## 참고

- (공부하며 채운다)
