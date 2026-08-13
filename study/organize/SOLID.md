# SOLID 원칙

이 문서는 SOLID 다섯 원칙을 **정의 → 왜 중요한가 → 나쁜 예 → 좋은 예 → 위반 신호** 순서로 정리한 것이다. 원칙마다 앞에 "먼저 알아야 할 것"을 두어 그 원칙을 읽는 데 필요한 개념을 그 자리에서 풀었고, 예제는 도메인 지식이 필요 없는 쉬운 것을 먼저 보인 뒤 같은 문제를 결제 도메인으로 다시 보이는 방식으로 두 번 나온다. 뒤쪽에는 원칙끼리 어떻게 돕고 어디서 충돌하는지, 그리고 공부하면서 스스로 답해본 다섯 개의 질문을 붙였다.

---

## SOLID 원칙에서 자주 나오는 용어

이 문서에서 반복해서 나오는 말들이다. 성격에 따라 세 묶음으로 나눠 정리하고 시작한다.

**요소들 사이의 관계를 보는 말**

1. **결합도(Coupling)**: A를 바꿀 때 B도 바꿔야 하는 정도. 낮을수록 좋다.
2. **응집도(Cohesion)**: 한 덩어리 안의 요소들이 서로 얼마나 관련 있는가. 높을수록 좋다.
3. **의존(Dependency)**: A가 B를 사용하면 "A는 B에 의존한다"고 한다. B가 바뀌면 A가 영향을 받는다.

**구조를 만드는 말**

4. **추상화(Abstraction)**: 구체적인 것들의 공통점만 뽑아 이름 붙인 것. Java에서는 주로 인터페이스, 추상 클래스.
5. **구현체(Implementation)**: 추상화를 실제로 구현한 클래스.

**약속을 적는 말**

6. **계약(Contract)**: 어떤 타입을 쓸 때 지켜지리라 기대하는 약속. 메서드 시그니처 + 사전조건 + 사후조건 + 불변식.
7. **사전조건(Precondition)**: 메서드를 호출하기 전에 참이어야 하는 조건. 예를 들면 인자가 null이 아니다.
8. **사후조건(Postcondition)**: 메서드가 끝난 뒤 참이어야 하는 조건. 예를 들면 반환값은 항상 0 이상이다.
9. **불변식(Invariant)**: 객체가 살아 있는 동안 항상 참이어야 하는 조건. 예를 들면 계좌 잔액은 음수가 아니다.

SOLID는 로버트 마틴(Robert C. Martin)이 정리한 객체지향 설계 5원칙의 머리글자이다. 목적은 하나다. **변경에 강한 코드.** 요구사항은 반드시 바뀌는데, 바뀔 때 고쳐야 할 곳이 적고 예측 가능하도록 하는 것이 전부이다.

---

## S — 단일 책임 원칙 (SRP, Single Responsibility Principle)

### 먼저 알아야 할 것

"클래스가 변경된다"는 말은 추상적인 표현이 아니라 **누군가 그 파일을 열어서 고친다**는 뜻이다. SRP는 그 "열어서 고치는 일"이 얼마나 자주, 서로 무관한 이유로 벌어지는지를 본다.

그리고 **액터(actor)** 라는 말이 계속 나온다. 액터는 코드 안에 없다. 코드 바깥에서 그 코드의 변경을 요구하는 사람이나 팀이다. 그래서 SRP는 코드만 읽어서는 판정할 수 없고, "이 메서드를 고쳐달라고 하는 사람이 누구인가"를 알아야 판정할 수 있다. 이 점이 응집도와 갈라지는 지점인데, 자세한 건 뒤의 5문항 1번에서 다룬다.

### 정의

> **하나의 클래스는 변경되는 이유가 하나여야 한다.**

흔히 "한 클래스는 한 가지 일만 해야 한다"로 소개되는데, 이 표현은 오해를 부른다. "한 가지 일"의 크기가 사람마다 다르기 때문이다. 정확한 기준은 **변경 이유(reason to change)** 이다.

로버트 마틴은 나중에 이를 더 명확히 다시 썼다. "하나의 모듈은 오직 하나의 액터(actor)에 대해서만 책임져야 한다." 여기서 액터란 그 코드의 변경을 요구하는 이해관계자 집단이다. 회계팀, 운영팀, 보안팀 같은.

### 왜 중요한가

한 클래스가 두 액터를 섬기면, 한쪽의 요구로 바꾼 코드가 다른 쪽을 망가뜨린다. 서로 상관없는 두 팀이 같은 파일을 놓고 충돌하는 상황이 벌어진다.

### 나쁜 예 — 먼저 간단한 것부터

마틴이 직접 든 예가 가장 알아보기 쉽다.

```java
public class Employee {
    public Money calculatePay()  { /* 급여 계산 */ }   // 요구하는 사람: CFO
    public String reportHours()  { /* 근무시간 보고 */ }  // 요구하는 사람: COO
    public void save()           { /* DB 저장 */ }     // 요구하는 사람: DBA
}
```

셋 다 직원 데이터를 쓰고, 셋 다 "직원에 관한 일"이다. 그런데 변경을 요구하는 사람은 셋이다. 여기서 `calculatePay()`와 `reportHours()`가 `regularHours()`라는 헬퍼를 공유한다고 하자. CFO의 요구로 그 헬퍼를 고치면, **아무도 요청하지 않은 COO의 리포트가 조용히 틀어진다.**

### 같은 문제, 결제 도메인에서

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

세 메서드는 서로 다른 이유로, 서로 다른 시점에 바뀐다. 그런데 같은 파일에 있으니 매번 이 파일을 건드리게 되고, 회계 리포트를 고치다가 결제 판단 로직을 실수로 깨트릴 수 있다.

### 좋은 예

액터별로 파일을 가른다.

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

이렇게 하면 회계 리포트를 바꿔도 도메인 파일에서의 변경이 일어나지 않는다.

### 위반 신호

- 클래스 이름에 "And"나 "Manager", "Util", "Helper"가 들어간다. (책임이 뭉뚱그려졌다는 신호)
- 한 클래스를 서로 다른 이유로 자주 커밋하게 된다. (git log를 보면 알 수 있다.)
- import 문에 성격이 다른 패키지가 섞여 있다. (도메인 + JDBC + HTTP)
- 테스트를 쓰려는데 필요 없는 것까지 준비해야 된다.

### 자주 하는 오해

- **메서드가 많으면 SRP 위반이다** → 아니다. 메서드가 20개여도 변경 이유가 하나면 SRP를 지킨 것이다.
- **클래스를 잘게 쪼갤수록 좋다** → 아니다. 함께 변하는 것을 억지로 나누면 응집도가 떨어지고 변경 시 여러 파일을 동시에 고쳐야 된다.

### 현장에서 만나는 상황

애플리케이션 서비스 하나가 저장, 외부 시스템 호출, 이벤트 발행을 모두 한다. 이게 SRP 위반인가?

**판단이 필요하다.** 애플리케이션 서비스의 역할이 원래 "유스케이스 오케스트레이션"이기 때문이다. 여러 협력자를 순서대로 부르는 것 자체는 그 서비스의 한 가지 일이다. 여기에 대고 기계적으로 SRP를 들이대면 서비스가 의미 없이 쪼개진다.

반면 **도메인 모델에 분산 트랜잭션 롤백용 필드가 끼어든 것**은 명확한 위반이다. 외부 호출이 실패했을 때 되돌리려고 이전 상태를 담아두는 필드 같은 것이 그렇다. 도메인 개념과 인프라 관심사가 한 클래스에 섞였고, 이 둘은 변경을 요구하는 사람이 다르다. 이 경우는 롤백 정보를 도메인 밖으로 빼는 것이 개선이다.

즉 같은 "여러 일을 한다"처럼 보여도, 액터가 하나면 위반이 아니고 액터가 둘이면 위반이다.

---

## O — 개방·폐쇄 원칙 (OCP, Open-Closed Principle)

### 먼저 알아야 할 것

여기서 말하는 **확장(open)** 과 **변경(closed)** 은 붙여 읽으면 모순처럼 보이지만 대상이 다르다. 확장은 새 코드를 **추가**하는 것이고, 변경은 이미 있는 코드를 **수정**하는 것이다. "확장에 열려 있고 변경에 닫혀 있다"는 말은 곧 **새 기능을 추가할 때 기존 파일을 열지 않는다**는 뜻이다.

그리고 OCP의 가장 단순한 형태는 다형성 그 자체다. 호출하는 쪽이 인터페이스 타입만 알고 있으면, 구현체가 몇 개로 늘어나든 호출부 코드는 그대로다.

뒤에 나오는 좋은 예에서 `List<FeePolicy>`를 주입받는 부분이 처음 보면 낯설 수 있다. 스프링은 같은 인터페이스를 구현한 빈이 여러 개 있으면 그것을 **리스트로 모아서 넣어준다.** 그래서 구현체 클래스를 하나 더 만들어 `@Component`만 붙이면, 주입받는 쪽은 한 줄도 안 고쳐도 새 구현체가 목록에 자동으로 들어온다.

### 정의

> **확장에는 열려 있고, 변경에는 닫혀 있어야 한다.**

### 왜 중요한가

기존 코드를 수정하면 이미 검증된 것이 깨질 위험이 생긴다. 반면 새 클래스를 추가하는 것은 기존 것을 건드리지 않으므로 안전하다. 테스트를 다시 돌릴 범위가 줄어든다.

### 나쁜 예 — 먼저 간단한 것부터

도형의 넓이를 구하는 코드다.

```java
public class AreaCalculator {
    public double area(Shape shape) {
        if (shape instanceof Circle c) {
            return Math.PI * c.radius() * c.radius();
        } else if (shape instanceof Rectangle r) {
            return r.width() * r.height();
        }
        throw new IllegalArgumentException("모르는 도형");
    }
}
```

삼각형을 추가하려면 이 파일을 연다. 도형이 늘어날 때마다 계속 연다. 고치면 이렇게 된다.

```java
public interface Shape {
    double area();
}

public record Circle(double radius) implements Shape {
    public double area() { return Math.PI * radius * radius; }
}

public record Rectangle(double width, double height) implements Shape {
    public double area() { return width * height; }
}
```

넓이를 구하는 방법을 각 도형이 스스로 안다. 삼각형은 파일 하나 추가로 끝나고 `AreaCalculator`는 아예 필요가 없어진다.

### 같은 문제, 결제 도메인에서

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

결제 수단이 하나 늘 때마다 이 클래스를 열어 `else if`를 추가한다. 변경에 닫혀 있지 않다.

도형과 다른 점이 하나 있다. 도형은 넓이 계산을 도형 자신이 가질 수 있었지만, 수수료율은 결제 수단이라는 enum이 가지기에 적절하지 않다. 정책이 바뀌는 주기가 다르고 정책마다 필요한 정보도 다르기 때문이다. 그래서 **정책을 별도 타입으로 뽑는다.**

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
    private final List<FeePolicy> policies;   // 스프링이 모든 구현체를 주입해준다

    public Money calculate(PaymentType type, Money amount) {
        return policies.stream()
            .filter(p -> p.supports(type))
            .findFirst()
            .orElseThrow(() -> new UnsupportedPaymentTypeException(type))
            .calculate(amount);
    }
}
```

이제 계좌이체 수수료를 추가하려면 새 클래스 하나만 만들면 된다. `FeeCalculator`는 열리지 않는다.

### 대가 — 공짜가 아니다

확장점을 만들면 간접 계층(indirection)이 하나 늘어난다. 코드를 따라가기 어려워지고, 파일 수가 늘고, "이 인터페이스의 구현체가 어디 있는지?"를 찾아야 한다.

핵심 판단은 이것이다. **확장이 실제로 일어날 축에서만 확장점을 연다.** 안 일어날 축에 미리 열어두면 그건 추측성 일반화(speculative generality)라는 안티패턴이다.

> 실무 감각: 두 번째 케이스가 생겼을 때 추상화한다. 첫 번째에 미리 하지 않는다. ("삼진 아웃 규칙" — 세 번째 중복에서 추상화하라는 경험칙도 널리 쓰인다.)

### 위반 신호

- 새 종류를 추가할 때마다 같은 파일의 `if/switch`를 찾아 고친다.
- 그 `switch`가 여러 곳에 흩어져 있다. (한 곳만 고치고 다른 곳을 빠트린다.)

### 현장에서 만나는 상황

확장점을 열지 말지는 "그 축이 실제로 늘어나는가"로 갈린다. 실무에서 이 판단이 갈리는 전형적인 경우는 이렇다.

**여는 게 맞는 축** — 결제 수단, 취소 유형(승인취소/부분취소/환불/망취소), 외부로 내보내는 파일 포맷, 알림 채널. 공통점은 **사업이 커지면 반드시 종류가 는다**는 것이다. 이미 두 종류 이상이고 세 번째가 예정돼 있다면 확실하다.

**열면 안 되는 축** — "나중에 DB를 바꿀지도 모르니까", "다른 회사에 팔게 될지도 모르니까" 같은 이유로 여는 확장점. 이런 건 대개 안 온다. 그리고 설령 오더라도 그때 필요한 축은 지금 상상한 축과 다를 확률이 높다.

판단이 애매하면 열지 않는 쪽이 낫다. 나중에 인터페이스를 뽑는 건 IDE가 해주는 기계적인 작업이지만, 잘못 열어둔 확장점을 걷어내는 건 그 위에 코드가 쌓인 뒤라 훨씬 비싸다.

---

## L — 리스코프 치환 원칙 (LSP, Liskov Substitution Principle)

### 먼저 알아야 할 것

**상속(`extends`)과 구현(`implements`)은 둘 다 하위 타입을 만든다.** LSP는 둘 모두에 적용된다. 상속만의 이야기가 아니다.

그리고 여기서 말하는 **계약은 문법이 아니라 약속이다.** 컴파일러는 메서드 이름과 파라미터 타입, 반환 타입만 검사한다. "이 메서드는 null을 안 넘겨야 한다", "결과는 항상 0 이상이다", "이 예외는 안 던진다" 같은 것은 검사하지 않는다. LSP가 다루는 것이 바로 컴파일러가 못 보는 이 영역이다. 그래서 컴파일은 통과하는데 프로그램은 틀리는 일이 생긴다.

마지막으로, LSP는 **호출자 관점에서 판정한다.** 자식 클래스만 놓고 보면 잘못된 게 없어 보여도, 부모 타입을 기대하고 짠 호출부에 넣었을 때 그 코드가 틀리게 되면 위반이다.

### 정의

> **하위 타입은 상위 타입을 대체할 수 있어야 한다.**

`Parent`를 쓰는 코드에 `Child`를 넣어도 프로그램이 여전히 올바르게 동작해야 한다. 바바라 리스코프(Barbara Liskov)가 정식화했다.

컴파일 되는 것과는 다른 의미이다. **컴파일은 되는데 의미가 깨지는 것**이 LSP 위반이다.

### 계약 관점의 정확한 규칙

하위 타입이 상위 타입을 대체하려면 네 가지를 지켜야 한다. 무엇에 대한 약속인지에 따라 묶으면 이렇게 된다.

```text
받는 것 ──── 사전조건을 강화하지 마라
               부모보다 더 까다로운 입력을 요구하면 안 된다

주는 것 ──┬─ 사후조건을 약화하지 마라
          │    부모보다 덜 보장하면 안 된다
          └─ 예외를 새로 던지지 마라
               부모가 던지지 않던 예외를 던지면 호출자가 대비할 수 없다

지키는 것 ─── 불변식을 유지하라
               부모가 지키던 조건을 깨면 안 된다
```

한 문장으로 줄이면 **입력은 부모보다 넓게 받고, 출력은 부모보다 좁게 준다**가 된다. 호출자 입장에서 생각하면 당연하다. 호출자는 부모의 약속만 알고 코드를 썼으니, 자식이 더 까다롭게 받거나 덜 보장하는 순간 그 코드가 틀린 코드가 된다.

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

수학적으로는 정사각형이 직사각형이지만, "너비와 높이를 독립적으로 바꿀 수 있다"는 계약 아래에서는 아니다. LSP는 **개념의 포함관계가 아니라 계약의 호환성**을 본다.

### 더 흔한 형태 — 부모에 없던 예외

실무에서 훨씬 자주 마주치는 건 위 사례보다 이쪽이다.

```java
public class Bird {
    public void fly() { /* 난다 */ }
}

public class Penguin extends Bird {
    @Override public void fly() {
        throw new UnsupportedOperationException("펭귄은 못 난다");
    }
}
```

생물학적으로 펭귄은 새가 맞다. 그런데 `Bird`라는 타입이 한 약속은 "난다"였고, 펭귄은 그걸 못 지킨다. 여기서도 **개념의 포함관계와 계약의 호환성이 어긋난다.**

### 같은 문제, 결제 도메인에서

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

펭귄과 똑같은 구조다. 부모에 없던 예외라 호출자가 대비할 수 없다.

그런데 이 `SettledTransaction` 하나가 어기는 것은 LSP만이 아니다. 원칙 세 개를 동시에 어긴다.

- **LSP 위반** — 부모에 없던 예외를 던진다.
- **ISP 위반** — `Transaction`이라는 상위 타입이 "취소 기능"까지 떠안아서, 취소가 불가능한 구현체가 안 쓰는 메서드를 강제로 받는다.
- **OCP 위반** — 새 거래 타입이 생길 때마다 호출부의 분기를 고쳐야 한다.

원인은 하나다. **"취소 가능성"이라는 축을 타입으로 분리하지 않은 것.** 세 원칙은 그 하나의 실수가 각각 다른 각도에서 드러난 모습이다. SOLID가 상호배타적인 다섯 칸이 아니라 서로 겹치는 다섯 개의 렌즈라는 게 여기서 드러난다.

### 좋은 예 — 능력을 타입으로 나눈다

```java
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

"할 수 있는 것"을 별도 인터페이스로 뽑았다. 취소할 수 없는 거래는 그 인터페이스를 아예 구현하지 않는다. 그러면 못 지킬 약속을 애초에 하지 않게 된다.

### 위반 신호

- 오버라이드한 메서드가 아무것도 안 하거나 예외를 던진다.
- 사용하는 쪽에 `instanceof`로 분기하는 코드가 늘어난다. (다형성이 깨졌다는 증거)
- 하위 클래스마다 다른 사용법 설명이 필요하다.

### instanceof는 왜 "다형성이 깨진 증거"인가

다형성의 값어치는 딱 하나다. **호출하는 쪽이 구체 타입을 몰라도 되고, 새 타입이 추가돼도 호출부가 안 바뀐다.**

```java
void process(Transaction tx) {
    tx.cancel();   // 어떤 구현체가 오든 이 줄은 그대로다
}
```

이 코드는 `Transaction` 구현체가 3개든 30개든 그대로이다. 호출부는 새 타입에 대해 닫혀 있다.

이제 `SettledTransaction`이 예외를 던지기 시작하면, 호출자는 저 한 줄을 더 이상 믿을 수 없다. 그래서 자기 방어를 하게 된다면,

```java
void process(Transaction tx) {
    if (tx instanceof SettledTransaction) return;
    if (tx instanceof RefundedTransaction) return;   // 나중에 또 하나 발견
    tx.cancel();
}
```

여기서 "어떤 거래가 취소 가능한가"라는 지식이 타입에서 빠져나와 호출부로 새어 나갔고, 원래는 각 클래스가 알아서 처리하던 것이 이제 호출부의 if 목록이 됐다. 그리고 이 목록은 호출부마다 하나씩 복제된다.

결정적인 문제는 컴파일러가 아무 도움도 못 준다는 것이다. 네 번째 취소 불가 타입을 추가해도 컴파일은 잘 되지만, 빠트린 분기는 운영 중에 `UnsupportedOperationException`으로 발견된다.

즉 `instanceof` 자체가 죄가 아니라 **`instanceof`는 증상이다.** 병은 "추상 타입을 통해 균일하게 다룰 수 없게 된 것"이며, 균일하게 다룰 수 없으니 호출자가 구체 타입을 캐물을 수밖에 없어진 것이다.

### 좋은 instanceof와 나쁜 instanceof를 어떻게 구별하는가

바로 위 좋은 예에도 `instanceof`가 있었다. 그럼 저건 왜 괜찮은가. 판별 기준은 하나로 줄일 수 있다. **새 타입을 추가했을 때 분기 개수가 늘어나는가.**

```text
                    나쁜 instanceof            좋은 instanceof
                    ─────────────────          ─────────────────
검사 대상            구체 클래스 이름            능력(capability) 인터페이스
분기 개수            타입 수만큼 늘어난다         1개로 고정
새 타입 추가 시       호출부를 고쳐야 한다         아무것도 안 고친다
빠트리면             런타임 예외                 컴파일 시점에 드러난다
```

`Cancellable` 검사는 거래 타입이 20개로 늘어도 분기가 하나다. 새 타입은 `implements Cancellable`을 붙이거나 안 붙이거나일 뿐, 호출부는 그대로다. 반면 `instanceof SettledTransaction`은 클래스 하나 늘 때마다 줄이 하나 는다.

### instanceof를 아예 없애는 방법

사실 `instanceof`도 없애는 방법이 있다.

```java
void cancel(Cancellable tx) {   // 못 취소하는 걸 넘기면 컴파일 에러
    tx.cancel();
}
```

위와 같이 못 취소하는 걸 넘기면 컴파일 에러가 나오도록 설계한다. 취소를 하려는 함수가 왜 `Transaction`을 받는가. 위와 같이 `Cancellable`을 받으면 된다. 그러면 검사할 일 자체가 없다.

그래도 검사가 필요한 순간은 있다. DB에서 `Transaction`으로 읽어오는 경계 지점 같은 곳이다. 그럴 땐 경계에서 한 번만 좁히고, 안쪽으로는 좁혀진 타입을 넘긴다.

```java
Transaction tx = repository.find(id);
if (tx instanceof Cancellable c) {
    cancelService.cancel(c);   // 이 안쪽에는 instanceof가 없다
} else {
    return Result.reject("정산 완료 거래는 취소할 수 없습니다");
}
```

위와 같이 실제 데이터가 들어오는 경계에서 검증하도록 하는 것이다. 핵심은 `instanceof`를 없애는 게 목적이 아니라, **도메인 지식이 호출부로 흩어지는 걸 막는 게 목적**이라는 것이다. 경계에서 한 번 확인하고 끝나면 흩어지지 않는다. 코드 전역에 퍼지기 시작하면 그때가 타입 설계를 다시 볼 신호다.

### 현장에서 만나는 상황

**상태에 따라 할 수 있는 일이 달라지는 도메인**에서 LSP가 가장 자주 깨진다. 거래(승인 → 매입 → 정산 → 취소), 주문(접수 → 배송중 → 완료), 문서(초안 → 검토 → 발행) 같은 것들이 전부 여기 해당한다.

이걸 상속으로 표현하면 거의 반드시 위반이 난다. 상위 타입에 모든 조작을 다 올려놓고 하위 타입에서 "이 상태에선 못 한다"고 예외를 던지게 되기 때문이다. 위의 `SettledTransaction`이 정확히 그 모양이다.

대안은 두 가지다. 하나는 **능력 인터페이스로 나누는 것**이고(위의 `Cancellable`), 다른 하나는 **State 패턴**으로 상태 객체가 자기가 할 수 있는 전이를 갖게 하는 것이다. 어느 쪽이든 공통점은 같다. **못 하는 일을 "예외를 던지는 메서드"로 표현하지 않고, 아예 타입에 없는 것으로 표현한다.**

---

## I — 인터페이스 분리 원칙 (ISP, Interface Segregation Principle)

### 먼저 알아야 할 것

여기서 **클라이언트(client)** 는 그 인터페이스를 **사용하는 쪽**이다. 구현하는 쪽이 아니다. 이걸 헷갈리면 원칙 자체가 반대로 읽힌다.

그리고 "의존한다"는 게 왜 비용인지 짚고 가야 한다. A가 B에 의존하면 **B가 바뀔 때 A도 다시 컴파일되고, 다시 배포되고, 다시 테스트된다.** 실제로 그 메서드를 안 썼어도 그렇다. 그래서 안 쓰는 메서드에 묶여 있는 것이 손해가 된다.

마지막으로 Java에서는 **한 클래스가 인터페이스를 여러 개 구현할 수 있다.** 이 사실이 ISP를 실용적으로 만든다. 인터페이스를 여러 개로 나눠도 구현 클래스까지 여러 개로 나눌 필요는 없다.

### 정의

> **클라이언트는 자신이 쓰지 않는 메서드에 의존하도록 강요받으면 안 된다.**

크고 뚱뚱한 인터페이스 하나보다, 역할별로 잘게 나뉜 인터페이스 여러 개가 낫다.

### 왜 중요한가

안 쓰는 메서드에 의존하면 그 메서드가 바뀔 때 나도 영향을 받는다. 재컴파일, 재배포, 재테스트가 따라온다. 또 구현체는 필요 없는 메서드까지 억지로 채워야 한다.

### 나쁜 예 — 먼저 간단한 것부터

복합기를 인터페이스 하나로 표현했다고 하자.

```java
public interface Machine {
    void print(Document d);
    void scan(Document d);
    void fax(Document d);
}

// 인쇄만 되는 구형 프린터
public class SimplePrinter implements Machine {
    public void print(Document d) { /* 인쇄 */ }
    public void scan(Document d)  { throw new UnsupportedOperationException(); }
    public void fax(Document d)   { throw new UnsupportedOperationException(); }
}
```

구현체가 필요 없는 메서드를 억지로 채웠다. 그리고 눈치챘겠지만 **여기서 LSP 위반도 같이 난다.** 부모에 없던 예외를 던지고 있기 때문이다. 뚱뚱한 인터페이스는 이렇게 두 원칙을 한꺼번에 무너뜨린다.

고치는 방향은 역할별로 나누는 것이다.

```java
public interface Printer { void print(Document d); }
public interface Scanner { void scan(Document d); }
public interface Fax     { void fax(Document d); }

public class SimplePrinter implements Printer { /* 인쇄만 */ }
public class OfficeMachine implements Printer, Scanner, Fax { /* 전부 */ }
```

### 같은 문제, 저장소 인터페이스에서

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
    private final UserRepository repository;   // findById 하나만 쓰는데
}
```

여기서는 예외를 던지는 문제는 없다. 대신 **의존의 범위가 문제다.** 조회만 하는 서비스가 `bulkUpdateStatus`의 시그니처가 바뀔 때마다 같이 재컴파일된다. 테스트에서 이 저장소를 가짜로 만들려면 안 쓰는 메서드 7개까지 채워야 한다.

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

구현 클래스 하나가 세 인터페이스를 모두 구현해도 된다. 중요한 건 **"누가 무엇에 의존하는가"** 지 파일 개수가 아니다.

```java
@Repository
public class UserRepositoryAdapter implements UserReader, UserWriter, UserSearcher {
    // 구현은 한 곳, 노출은 역할별로
}
```

### 위반 신호

- 인터페이스를 구현하는데 몸통이 비었거나 예외를 던지는 메서드가 생긴다.
- 테스트용 가짜 구현을 만들 때 안 쓰는 메서드를 잔뜩 채워야 한다.
- 인터페이스 이름이 `XxxService`, `XxxManager`처럼 역할이 아니라 대상만 가리킨다.

### 헥사고날 아키텍처와의 관계

포트(Port)를 설계할 때 ISP가 직접 적용된다. 포트는 "구현체가 제공할 수 있는 것"이 아니라 **"사용하는 쪽이 필요로 하는 것"** 으로 정의해야 한다. 이 방향이 뒤집히면 인터페이스가 구현을 그대로 베낀 껍데기가 된다.

### 현장에서 만나는 상황

외부 시스템을 붙일 때 이 실수가 가장 자주 나온다. 인증 서버든 결제 대행사든, 그쪽이 제공하는 API 목록을 그대로 인터페이스로 옮겨오는 것이다.

**점검 질문은 하나다.** 이 포트에 있는 오퍼레이션이 *우리 쪽이 필요로 해서* 있는가, 아니면 *저쪽이 제공해서* 있는가. 후자면 인터페이스가 상대방 SDK의 그림자일 뿐이고, 상대가 API를 바꿀 때마다 우리 도메인까지 흔들린다.

우리가 실제로 쓰는 게 "토큰 검증" 하나뿐이라면 포트에도 그 하나만 있으면 된다. 상대가 20개를 제공하는 것은 상대 사정이다.

---

## D — 의존관계 역전 원칙 (DIP, Dependency Inversion Principle)

### 먼저 알아야 할 것

여기서 말하는 **상위와 하위는 호출 순서가 아니다.** 상위 수준은 "무엇을 할 것인가"라는 정책(비즈니스 규칙)이고, 하위 수준은 "어떻게 할 것인가"라는 수단(DB, HTTP, 파일)이다. 비즈니스 로직이 DB를 호출하더라도 비즈니스가 상위다.

그리고 DIP를 이해하는 데 가장 큰 고비가 이것이다. **소스 코드의 의존 방향과 실행 시점의 호출 흐름은 반대일 수 있다.** 실행 시점에는 서비스가 어댑터를 호출하지만(안 → 밖), 소스 코드에서는 어댑터가 서비스 쪽 인터페이스를 참조한다(밖 → 안). DIP가 뒤집는 것은 **소스 코드의 의존 방향**이다.

마지막으로 "인터페이스를 누가 소유하는가"라는 표현이 계속 나오는데, 실무에서는 아주 구체적인 뜻이다. **그 인터페이스 파일이 어느 패키지·모듈에 들어 있는가.**

### 정의

> **상위 수준 모듈이 하위 수준 모듈에 의존해서는 안 된다. 둘 다 추상화에 의존해야 한다.**
> **추상화가 세부사항에 의존해서는 안 된다. 세부사항이 추상화에 의존해야 한다.**

### "역전"이 무엇을 뒤집는가

일반적인 흐름은 이렇다.

```text
[비즈니스 로직] ──의존──▶ [DB 코드]
```

비즈니스가 DB를 알고 있다. DB를 바꾸면 비즈니스 코드가 바뀐다. DIP를 적용하면 이렇게 된다.

```text
[비즈니스 로직] ──의존──▶ [인터페이스] ◀──구현── [DB 코드]
                          (비즈니스가 소유)
```

**화살표 방향이 뒤집혔다.** DB 코드가 비즈니스가 정의한 인터페이스를 구현하는 쪽이 되었다. 이게 "역전"의 뜻이다.

핵심은 **인터페이스를 누가 소유하는가**이다. 인터페이스가 도메인 패키지 안에 있어야 진짜 역전이다.

### 나쁜 예 — 먼저 간단한 것부터

스위치와 램프로 보면 짧게 끝난다.

```java
public class Switch {
    private final Lamp lamp = new Lamp();   // 램프를 직접 안다
    public void toggle() { lamp.turnOn(); }
}
```

이 스위치는 램프 전용이다. 선풍기에는 못 쓴다. 램프의 메서드 이름이 바뀌면 스위치도 고쳐야 한다.

```java
// 스위치 쪽이 소유하는 인터페이스 — "내가 필요한 건 켜고 끄는 것뿐이다"
public interface Switchable {
    void turnOn();
    void turnOff();
}

public class Switch {
    private final Switchable device;        // 램프든 선풍기든 상관없다
    public Switch(Switchable device) { this.device = device; }
    public void toggle() { device.turnOn(); }
}

public class Lamp implements Switchable { /* 램프가 스위치의 계약을 따른다 */ }
```

주목할 점은 `Switchable`이 **스위치 쪽에 있다**는 것이다. 램프가 그것을 구현한다. 스위치가 램프를 알던 관계가, 램프가 스위치의 요구를 따르는 관계로 뒤집혔다.

### 같은 문제, 애플리케이션 코드에서

```java
package com.example.card.application;

import com.example.card.infrastructure.persistence.CardJpaRepository;  // ← 인프라를 import

@Service
public class AuthorizePaymentService {
    private final CardJpaRepository jpaRepository;   // JPA에 직접 의존

    public void authorize(...) {
        CardEntity entity = jpaRepository.findById(id).orElseThrow();
        // 도메인 로직이 JPA 엔티티를 직접 다룬다
    }
}
```

램프를 직접 들고 있는 스위치와 같은 모양이다. JPA를 걷어내면 이 서비스도 같이 무너진다.

### 좋은 예

```java
// application/port/out/ — 애플리케이션이 소유하는 인터페이스
package com.example.card.application.port.out;

public interface CardRepository {
    Optional<Card> findById(CardId id);      // 도메인 타입만 사용
    Card save(Card card);
}

// application/service/ — 인프라를 전혀 모른다
package com.example.card.application.service;

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
package com.example.card.infrastructure.persistence;

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

`CardRepository`가 `application/port/out/`에 있다는 게 핵심이다. 이 파일을 `infrastructure/`로 옮기는 순간 역전은 사라진다. 인터페이스가 있느냐가 아니라 **어디에 있느냐**가 DIP를 결정한다.

### DIP vs DI(의존성 주입) — 자주 혼동되는 지점

둘은 층위가 다르다. 나란히 놓으면 이렇다.

```text
              DIP                          DI (Dependency Injection)
              ───────────────────────      ─────────────────────────────
성격          설계 원칙                     구현 기법
관심          의존의 방향                   의존 객체를 누가 넣어주는가
예            인터페이스를 도메인이 소유      생성자 주입, 스프링 @Autowired
```

**DI를 써도 DIP를 어길 수 있다.** 생성자로 `CardJpaRepository`를 주입받으면 DI는 했지만 DIP는 어긴 것이다. 여전히 구체 클래스에 의존하고 있으니까.

### 위반 신호

- 도메인·애플리케이션 패키지에서 `javax.persistence`, `org.springframework.jdbc`, `feign` 같은 걸 import 한다.
- 인터페이스가 인프라 패키지 안에 있다.
- 인터페이스 메서드 시그니처에 엔티티, DTO 같은 인프라 타입이 등장한다.

### 현장에서 만나는 상황

포트와 어댑터 구조를 잡아놓고도 DIP가 새는 자리가 있다. **포트의 시그니처다.**

패키지 위치는 제대로 잡았는데 메서드가 이렇게 생겼다면 역전은 이름뿐이다.

```java
public interface CardRepository {
    Optional<CardEntity> findById(Long id);   // 엔티티와 원시 타입이 새어나왔다
}
```

`CardEntity`는 JPA 어노테이션이 붙은 인프라 타입이다. 이게 포트 시그니처에 있으면 애플리케이션이 결국 JPA를 아는 셈이고, 저장 기술을 바꾸는 순간 도메인까지 따라 바뀐다.

**점검 방법은 간단하다.** 포트 인터페이스 파일을 열어서 import 목록을 본다. 도메인 타입 말고 다른 게 있으면 새고 있는 것이다.

---

## 원칙 간의 관계와 충돌

### 서로 돕는 관계

다섯 원칙은 따로 노는 규칙이 아니라 한 방향으로 이어진다. 앞의 원칙이 뒤의 원칙을 싸게 만들어준다.

```text
SRP  책임이 하나면 ─────┐
                       ├──▶  계약이 작고 명확해진다
ISP  경계를 얇게 유지 ───┘             │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                   LSP 지키기 쉽다           DIP 적용이 싸다
                   약속이 적으면              포트가 좁으면
                   깨트릴 것도 적다            구현·가짜 구현이 싸다
                                                  │
                                                  ▼
                                          경계가 생긴다
                                                  │
                                                  ▼
                                          OCP 가능해진다
                                          새 구현체 추가로 확장
```

### 충돌하는 지점

같은 방향으로만 가지는 않는다. 네 군데에서 부딪힌다.

**SRP ↔ 응집도**
잘게 나눌수록 SRP는 지켜지지만 함께 변하는 것이 흩어진다.
→ 함께 변하는 것은 함께 둔다. SRP의 기준은 "변경 이유"지 "크기"가 아니다.

**OCP ↔ 단순함**
확장점을 열수록 간접 계층이 늘어 읽기 어려워진다.
→ 실제로 확장되는 축에만 연다.

**ISP ↔ 파일 수**
인터페이스를 나눌수록 파일이 는다.
→ 구현은 한 클래스로 합쳐도 된다. 의존 방향이 중요하지 파일 수가 아니다.

**DIP ↔ 생산성**
모든 것에 포트를 만들면 보일러플레이트가 폭증한다.
→ 경계를 넘는 것(DB, 외부 API, 메시징)에만 적용하고, 내부 협력 객체까지 하지 않는다.

---

## 스스로 고민해볼 포인트

### 1. SRP의 "단일 책임"과 응집도는 같은 말인가

**아니다. 결정적 차이는 "코드만 보고 판단할 수 있느냐"에 있다.**

응집도는 모듈 내부 요소들이 서로 얼마나 관련 있는지를 본다. 코드를 읽으면 판단할 수 있는 내재적 성질이다. 같은 데이터를 쓰는가, 같은 목적에 기여하는가.

SRP는 "변경을 요청하는 사람이 누구인가"를 본다. 마틴이 나중에 명확히 한 표현은 "하나의 액터(actor)에 대해서만 책임진다"이다. 이건 코드의 성질이 아니라 **코드와 조직의 관계**이다. 코드만 읽어서는 알 수 없다.

앞의 SRP 절에서 본 `Employee`가 정확히 그 예다. `calculatePay()`, `reportHours()`, `save()` 셋 다 직원 데이터를 쓰고, 셋 다 "직원에 관한 일"이다. 고전적 응집도 척도로는 높다. 그런데 변경을 요구하는 사람은 각각 CFO, COO, DBA로 셋이다.

이때 문제가 발생하는 부분은 `calculatePay`와 `reportHours`가 `regularHours()`라는 헬퍼를 공유한다고 하자. CFO가 급여 규정 변경을 요청해서 그 헬퍼를 고치면, **아무도 요청하지 않은 COO의 리포트가 조용히 틀어지며, 이는 응집도가 높아서 생긴 사고다.**

방향도 다르다. 응집도는 무엇을 함께 둘지를 말하고, SRP는 무엇을 갈라놓을지를 말한다. 대체로 같이 가지만 어긋나는 지점이 정확히 사고가 나는 지점이다.

이때 SRP를 "한 가지 일만 한다"로 읽으면 메서드 하나짜리 클래스 수백 개가 나온다. 마틴이 직접 그 해석을 부인했다. 축은 **작업의 크기가 아니라 변경의 출처**이다.

### 2. OCP를 지키려고 만든 추상화가 한 번도 확장되지 않았다면 그건 지킨 것인가 낭비인가

**대체로 낭비다.** 그리고 "지킨 것 아니면 낭비"라는 이분법 자체가 틀렸다. 둘 다일 수 있다.

핵심은 비대칭이다.

추상화를 **안 만들었다가 나중에 필요해지면** — 인터페이스 추출은 IDE가 해주는 기계적 작업이고, 무엇보다 이 시점엔 변화 축을 실제로 알고 있다.

추상화를 **잘못 만들었다가 다른 축이 필요해지면** — 틀린 추상화와 싸워야 하고, 그 사이 코드가 그 위에 쌓여 있다. 산디 메츠의 말을 보면 "중복이 잘못된 추상화보다 훨씬 싸다."

그리고 경험적으로, 두 번째 사례를 보기 전에 만든 추상화는 대개 엉뚱한 축에 걸려 있다. "DB를 갈아탈지도 모르니 리포지토리 인터페이스"를 만들었는데, 실제로 온 요구는 "정산 규칙이 하나 더 생겼다"였다. 그 인터페이스는 아무런 도움이 안 되고 결국 기존 코드를 고친다. 낭비인 데다가 OCP를 지켜주지도 못한다.

여기서 한술 더 뜨면, 쓰이지 않는 추상화는 비용이 0이 아니라 **음수다.** 읽는 사람에게 "여기가 확장점이다"라고 거짓말을 하기 때문이다.

그럼에도 사전에 추상화가 정당한 경우가 있다.

- 두 번째 구현이 이미 확정된 경우 (로드맵, 계약에 있다)
- 나중에 넣기 비싼 경계 — 공개 API, 저장된 스키마, 발행되는 이벤트, 팀 간 경계. 판단 기준은 **가역성**이다.
- 지금 당장 대가를 받는 경우 — 테스트 (3번에서 이어진다.)

그래서 이때 OCP를 "미리 확장에 대비하라"가 아닌 **"두 번째 변형이 실제로 왔을 때, 수정이 아니라 추가로 흡수하라"** 로 읽는 게 맞다. 예언이 아니라 대응하는 구조의 작업이 필요하다.

### 3. DIP를 지키면 자동으로 테스트하기 쉬워지는가, 그 인과는 무엇인가

**아니다.** "인터페이스가 있으면 Mock을 끼울 수 있다"는 설명은 인과가 잘못됐다.

인터페이스가 있더라도

```java
class TransferService {
    private final AccountRepository repo = new PostgresAccountRepository();  // ← 여기
}
```

이와 같은 초기화 구조이면 타입 수준에서는 DIP를 지킨 것처럼 보이는데, 테스트는 아무것도 못 바꾼다.

실제 인과를 보면 이렇다.

```text
DIP → 의존을 추상으로 선언 → 인터페이스는 new 할 수 없다
    → 밖에서 주입받을 수밖에 없다 → 그 주입 지점이 seam(마이클 페더스)
    → 테스트가 거기서 갈아끼운다
```

인과가 사는 곳은 가운데다. 테스트 용이성을 주는 건 인터페이스의 존재가 아니라 **주입(DI)** 이다. 인터페이스 없이 주입만 해도 테스트는 되고, 인터페이스만 있고 내부에서 `new`를 하면 테스트는 안 된다.

그리고 더 중요한 두 번째 이유가 있다. DIP의 진짜 테스트 이득은 mock을 끼울 수 있는 게 아니라, **추상화를 도메인이 필요로 하는 모양으로 정의하게 강제한다**는 것이다. 마틴이 말한 "역전"의 핵심은 인터페이스를 호출하는 쪽이 소유한다는 데 의미를 가진다.

제대로 역전했다면 포트는 이렇게 생긴다.

```java
interface PaymentGateway {
    AuthResult authorize(Money amount, Card card);
}
```

메서드 하나, 가짜 구현은 10줄이며, 테스트는 도메인 언어로 단언한다.

잘못 역전하면 — 벤더 SDK 모양을 그대로 인터페이스로 뜨면 — 메서드 14개에 벤더 DTO가 시그니처에 박힌다. mock은 만들 수 있다. 그런데 테스트는 벤더 세부사항을 외우게 되고, SDK 업데이트마다 깨지고, 결과가 아니라 호출 순서를 검증하게 된다. **mockable하지만 testable하지 않은 상태이다.** 이런 테스트는 시스템이 망가져도 통과하고, 동작이 안 변한 리팩토링에는 실패한다.

그래서 실무적으로 리포지토리 같은 건 mock 프레임워크보다 손으로 쓴 in-memory Fake를 추천한다. 포트가 좁으면 Fake는 싸고, 상태 기반이라 실제 계약을 검증한다.

그리고 여기서 2번과 이어지는 지점이 있다. **DIP 인터페이스는 투기적 추상화가 아니다.** 첫날부터 구현체가 둘이다. 진짜와 Fake, 이미 값을 치르게 되는 것이다.

### 4. 5개 원칙 중 서로 충돌하는 경우가 있는가, 무엇을 우선하는가

충돌한다. 가장 날카롭게 충돌하는 건 **LSP ↔ OCP**이다.

OCP는 "하위 타입을 추가해서 확장하라"고 밀고, LSP는 "하위 타입이 할 수 있는 걸 제한한다". 즉 부모의 계약이 강할수록 유효한 하위 타입은 줄어든다. 확장성을 늘리려고 계약을 약화시키면 형식적으로 LSP를 지키지만, 추상화가 보장하는 게 없어져서 부담이 전부 호출자에게 간다.

자바 `Collection.add()`가 정확히 이 실패다. 불변 컬렉션을 받아들이려고 "`UnsupportedOperationException`을 던질 수 있다"로 계약을 약화시켰다. 명세상 LSP 위반이 아니다. 그런데 모든 호출자가 이론상 그 예외를 처리해야 하고, 실제로는 아무것도 안 한다. 잘 알려진 단점이다.

즉 **계약의 강도는 제로섬 다이얼이다.** 한쪽엔 "구현할 수 있는 타입의 수", 다른 쪽엔 "호출자가 받는 보장". 자동 해결책은 없고, 어느 쪽이 이 도메인에서 더 비싼지를 정해야 한다.

다른 충돌들도 있다. ISP를 밀면 개념이 파편화되고(`Readable`/`Writable`/`Closable`로 흩어져 "파일"이 어디에도 없다), SRP를 밀면 로직이 수백 개 클래스에 흩어져 산탄총 수술이 된다.

그렇다면 우선순위를 어떻게 정하면 좋을까.

```text
1순위   LSP         정확성의 문제 — 흥정 대상이 아니다
2순위   SRP         변경이 어디에 떨어지는지 정한다 (액터 축으로)
3순위   DIP         경계에서만 — DB, 외부 API, 메시징
4순위   ISP · OCP   증거가 나온 뒤에 적용한다
```

**LSP가 무조건 1순위다.** 다섯 개 중 유일하게 비용이 아니라 정확성의 문제이기 때문이다. 나머지 넷은 "변경 비용"을 거래하는 원칙이고 이는 서로 흥정, 즉 트레이드오프에 따라 달라질 수 있다. 하지만 LSP 위반은 흥정 대상이 아닌 그냥 버그다. 게다가 그 위에 쌓인 모든 추상화를 조용히 오염시킨다.

충돌을 푸는 메타 원칙은 **가역성**이다. 두 원칙이 부딪히면 틀렸을 때 되돌리기 싼 쪽을 고른다. 추상화는 나중에 넣기 쉽고 걷어내기 어렵다. 클래스는 나중에 쪼개기 쉽고, 이미 API, 스키마, 이벤트로 새어나간 분리를 합치기는 어렵다. 기본값은 단순한 쪽, 예외는 옮기기 비싼 경계다.

그리고 SOLID 자체가 목적이 아니다. 목적은 **변경 비용을 낮추는 것**이지, 원칙을 적용했더니 실제로 발생하는 변경이 더 비싸졌다면 잘못 적용된 것이다.

### 5. 이 원칙들이 클래스 레벨을 넘어 모듈, 아키텍처 레벨에도 적용되는가

**적용되며, 오히려 거기서 더 중요하다.** 클래스 레벨 실수는 리팩토링이지만, 서비스 경계 실수는 분산 트랜잭션 + 데이터 마이그레이션 + 팀 간 협상이다.

다섯 개가 그대로 한 층 위로 올라간다.

```text
클래스 레벨                모듈 · 아키텍처 레벨
──────────                ────────────────────
SRP  ──────────────▶   바운디드 컨텍스트 · 서비스 경계
OCP  ──────────────▶   플러그인 아키텍처 · 이벤트 기반 확장
LSP  ──────────────▶   API 버전 · 메시지 스키마 호환
ISP  ──────────────▶   API 계약 설계 · BFF
DIP  ──────────────▶   헥사고날 · 포트와 어댑터
```

**SRP → 바운디드 컨텍스트**

액터 논리가 그대로 올라간다. 경계는 기술 레이어가 아니라 "누가 변경을 요청하는가"를 따라야 한다. "UI 서비스 / 로직 서비스 / DB 서비스"로 쪼갠 마이크로서비스가 실패하는 이유가 정확히 이거다. 업무 변경 하나가 셋을 다 건드린다. 콘웨이 법칙은 이 원칙의 조직판이다.

**LSP → 서비스 계약**

이게 제일 저평가되어 있는데, LSP는 상속이 아니라 **대체 가능한 계약 전부에 적용된다.** API 버전, 메시지 스키마, 같은 포트 뒤의 다른 결제사. v1이 받아주던 필드를 v2가 거부하면 사전조건 강화이고, 모든 클라이언트가 깨진다. Avro, Protobuf의 하위 호환 규칙은 리스코프의 사전/사후조건 규칙을 기계화한 것이다.

**OCP → 플러그인 아키텍처**

새 소비자가 "결제 정산됨" 이벤트를 구독해도 발행하는 쪽은 바뀌지 않는다. 컴포넌트 의존 화살표가 안정적인 쪽을 향하게 두고, 확장은 말단에 플러그인을 붙이는 식으로 흡수한다. 클래스 레벨에서 `else if`를 지웠던 것과 같은 일을 서비스 레벨에서 하는 것이다.

**ISP → API 계약 설계**

클라이언트가 거대한 API 전체에 의존하게 만들지 않는다. BFF(Backend for Frontend), GraphQL의 필드 선택, 소비자 주도 계약 테스트(Pact)가 전부 네트워크 경계에서의 ISP다. 모든 서비스가 물고 있는 공용 라이브러리도 모듈 규모의 뚱뚱한 인터페이스다. 한 번 바뀌면 전부 재배포해야 한다.

**DIP → 헥사고날**

도메인이 포트를 정의하고 인프라가 구현한다. 소스 의존은 안쪽을 향하고 런타임 호출은 바깥으로 흐른다.

그리고 스케일이 올라가면서 생기는 결정적인 차이가 하나 있다. 클래스 레벨의 SOLID는 아무도 강제하지 않는 관습이지만, **모듈 레벨에서는 빌드 의존성으로 강제할 수 있다.** 도메인 모듈의 빌드 파일에 인프라 의존성이 아예 없으면 DIP 위반은 컨벤션 위반이 아니라 컴파일 에러가 된다. 규율이 아니라 구조로 막는 것이라 훨씬 강하다.

다만 4번의 가역성 원칙이 여기서 더 세게 작용한다. 되돌리기 싼 부분은 증거가 나올 때까지 기다리되, 저장된 스키마나 발행되는 이벤트, 공개 API처럼 되돌리기 비싼 부분은 미리 값을 치르는 게 맞다.
