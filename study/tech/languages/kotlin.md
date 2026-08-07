# Kotlin — 같은 JVM 위에서 기본값을 어디서 뒤집었나

> 학습 노트다. 결정의 근거가 될 수 없다(언어 결정의 정본: [`architecture/constraints.md`](../../../architecture/constraints.md) **C-05** · 코딩 규칙의 정본: [`dev-conventions.md`](../../../dev-conventions.md) §1).

공식 FAQ가 Kotlin의 값으로 먼저 내세우는 것은 분량이다 — "대략 40% 정도의 코드 줄 수 감소"([Kotlin FAQ](https://kotlinlang.org/docs/faq.html)). 그런데 줄 수는 언어를 고르는 이유가 되기 어렵다. 줄이는 방법은 많고 대부분 유지보수를 해친다. 이 프로젝트의 C-05 개정 기록에도 분량은 근거로 적혀 있지 않다.

이 문서가 따라가는 축은 다른 것이다: **무엇을 컴파일러가 거부하게 만들었는가.** null, 상태 분기의 누락, 금액과 날짜의 혼동, 컬렉션의 가변성 — 이것들은 Java에서 전부 "규율로 지키는 것"이고, Kotlin은 그중 일부를 "타입으로 지켜지는 것"으로 옮겼다. 옮긴 만큼 얻고, **옮기지 못한 경계에서 정확히 비용이 발생한다.** 그 경계가 이 문서의 절반이다. 인용은 Kotlin 2.x 기준 공식 문서와 KEEP(설계 제안서), 그리고 대조가 필요한 곳에서는 OpenJDK JEP를 쓴다. 이 프로젝트의 실측은 `jun-bank/common` 저장소의 첫 커밋(TL-1 스파이크)과 이 문서를 쓰며 직접 돌린 확인에서 가져왔다.

## 1. 공식 목록이 스스로 말하는 축

Kotlin 문서에는 Java와의 대조를 정면으로 적은 페이지가 있고, 거기 실린 "Kotlin에서 해소된 Java의 문제"는 일곱 줄이다 — "Null references are controlled by the type system · No raw types · Arrays in Kotlin are invariant · Kotlin has proper function types, as opposed to Java's SAM-conversions · Use-site variance without wildcards · Kotlin does not have checked exceptions · Separate interfaces for read-only and mutable collections"([Comparison to Java](https://kotlinlang.org/docs/comparison-to-java.html)).

읽어 보면 일곱 줄 중 여섯이 **타입 시스템을 손본 것**이고, 나머지 하나(검사 예외)는 반대로 타입 시스템이 하던 일을 **뺀** 것이다. "간결하다"는 이 목록에 없다. 같은 페이지가 반대 방향도 적는다 — Java에 있고 Kotlin에 없는 것으로 "Checked exceptions · Primitive types that are not classes · Static members … · Wildcard-types … · Records · package-private visibility modifier"를 나열한다. 이 두 목록을 나란히 놓으면 이 언어의 성격이 드러난다. Kotlin은 Java를 확장한 것이 아니라 **몇 개의 기본값을 반대로 정하고, 그 반대편에 있던 것을 버린** 언어다. 아래 각 절은 그 맞바꿈을 하나씩 본다.

## 2. null이 타입에 있다는 것 — 그리고 그 타입이 끝나는 자리

공식 정의는 짧다. "Kotlin explicitly supports nullability as part of its type system, meaning you can explicitly declare which variables or properties are allowed to be `null`. Also, when you declare non-null variables, the compiler enforces that these variables cannot hold a `null` value, preventing an NPE"([Null safety](https://kotlinlang.org/docs/null-safety.html)).

Java에도 `@Nullable`·`@NotNull`은 있다. 차이는 검사기의 유무가 아니라 **기본값이 어느 쪽인가**다. Java에서 어노테이션이 없는 참조는 nullable이 기본이고 판정은 선택적 도구가 하며, 그 도구를 끄면 규칙이 사라진다. Kotlin에서 `String`과 `String?`는 서로 다른 타입이고, 후자를 전자에 대입하는 코드는 존재할 수 없다. 규칙을 지키는 주체가 도구에서 언어로 옮겨 간 것이다.

`!!`는 그 규칙을 코드에서 명시적으로 취소하는 장치다. "The not-null assertion operator `!!` converts any value to a non-nullable type … if the value is `null`, the `!!` operator forces it to be treated as non-nullable, which results in an NPE"(같은 문서). 지금은 이렇게 담담하게 적혀 있지만, 이 연산자의 설계 의도를 가장 잘 드러낸 문장은 구판 문서에 있었다 — *"Thus, if you want an NPE, you can have it, but you have to ask for it explicitly and it won't appear out of the blue"*([Null safety, 2022-11-24 판](https://github.com/JetBrains/kotlin-web-site/blob/8c0ac89644a3/docs/topics/null-safety.md) — 현행 문서에서는 삭제된 표현이다). NPE는 "언제든 터질 수 있는 것"이 아니라 **누군가 명시적으로 요청해야 나오는 것**으로 재정의됐다는 뜻이다.

우리 규약 **KO-3**이 `!!`를 아예 금지한 이유가 여기 있다 — 요청 창구가 열려 있는 한 "타입이 보장한다"는 문장이 코드 어디서든 취소될 수 있다.

### 경계 — 플랫폼 타입

타입 시스템의 보장이 끝나는 자리는 Java 쪽 경계다. "Any reference in Java may be `null`, which makes Kotlin's requirements of strict null-safety impractical for objects coming from Java. Types of Java declarations are treated in Kotlin as non-denotable and called platform types"([Java interop](https://kotlinlang.org/docs/java-interop.html)). 이 타입은 **소스에 적을 수 없고**(non-denotable), 컴파일러가 오류 메시지에서만 `T!`로 표시한다.

중요한 것은 그 타입에 대해 컴파일러가 무엇을 하지 않는가다. "When you call methods on variables of platform types, Kotlin does not issue nullability errors at compile time, but the call may fail at runtime"(같은 문서). 즉 플랫폼 타입은 **검사가 유예된 구간**이고, 검사는 개발자가 타입을 적는 순간 일어난다 — "If you choose a non-nullable type, the compiler will emit an assertion upon assignment."

여기서 우리 규약 KO-3의 후반부가 나온다. *"플랫폼 타입(전문·파일 파싱·JDBC 경계)은 **경계에서 즉시 검증**해 non-null 도메인 타입으로 바꾼다."* 이것은 스타일 취향이 아니라 위 문장의 직접 귀결이다 — 플랫폼 타입을 그대로 안쪽으로 흘려보내면 assertion이 일어나는 지점이 뒤로 밀리고, NPE가 파싱 코드가 아니라 도메인 로직 한가운데서 터진다. 자바 쪽에 nullability 어노테이션이 붙어 있으면 이 유예 자체가 사라진다 — "Java types that have nullability annotations are represented not as platform types, but as actual nullable or non-nullable Kotlin types"(같은 문서. JetBrains·JSpecify·JSR-305·Lombok 등을 인식한다).

이 경로는 최근에 눈에 띄게 강해졌다. JSpecify(`org.jspecify.annotations`)에 대해서는 **Kotlin 2.1.0부터 위반이 경고가 아니라 오류**다 — "Starting from Kotlin 2.1.0, nullability mismatches are raised from warnings to errors by default"([What's new in Kotlin 2.1.0](https://kotlinlang.org/docs/whatsnew21.html)). 승격 경로도 문서화돼 있다: 1.6.0 경고 → 1.8.20 대상 확대 → 2.0.0 `@NonNull` 지원 → 2.1.0 strict 기본값([Compatibility guide for Kotlin 2.1](https://kotlinlang.org/docs/compatibility-guide-21.html)). 그리고 `@NullMarked`는 패키지·클래스 단위로 "이 범위는 기본이 non-null"을 선언한다. **Java 라이브러리가 JSpecify를 채택했다면 §2의 구멍은 그 라이브러리 표면에서 거의 사라진다** — 우리 스택에서는 이 항목이 그냥 좋은 소식이 아니라, 의존 라이브러리를 고를 때 볼 축 하나가 된다.

### 한계 — "타입에 있다"가 "자동으로 지켜진다"는 뜻은 아니다

공식 문서는 Kotlin에서 NPE가 나는 경로를 스스로 열거한다: 명시적 `throw NullPointerException()`, `!!`, 초기화 중 데이터 불일치(생성자에서 새는 `this`, 상위 생성자가 부르는 open 멤버), 그리고 Java 상호운용 — 특히 "Nullability issues with generic types. For example, a piece of Java code adding `null` into a Kotlin `MutableList<String>`"([Null safety](https://kotlinlang.org/docs/null-safety.html)).

이 프로젝트가 이미 같은 결론에 도달해 규약에 적어 두었다. KO-3의 비고는 이렇게 시작한다 — *"컴파일은 KO-3을 막지 못한다 — Kotlin은 domain·application 내부의 nullable 선언·`!!`·플랫폼 타입 전달을 전부 컴파일한다. non-null 시그니처는 그 시그니처를 지나는 경계 하나만 막는다."* 그래서 이 규칙의 주 강제 수단은 컴파일이 아니라 정적 검사와 경계 테스트다. **타입 시스템이 주는 것은 "한 경계에서의 거부"이고, 그 경계를 어디에 그을지는 여전히 설계가 정한다.**

## 3. sealed class와 when 완결성 — 상태를 늘리면 컴파일이 깨진다

`sealed`는 서브클래스의 집합을 컴파일 시점에 닫는 선언이다. "All direct subclasses of a sealed class are known at compile time. No other subclasses may appear outside the module and package within which the sealed class is defined"([Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html)). 집합이 닫히면 `when`이 모든 경우를 덮었는지 판정할 수 있고, 그러면 `else`가 필요 없어진다 — "if your subject is a `Boolean`, `enum class`, `sealed class`, or one of their nullable counterparts, you can cover all cases without an `else` branch"([Conditions and loops](https://kotlinlang.org/docs/control-flow.html)).

여기서 갈리는 것은 **언제 강제되는가**이고, Kotlin은 그 강제를 두 단계에 걸쳐 올렸다. 1.6은 경고를 냈다 — "Kotlin 1.6.0 reports warnings about non-exhaustive `when` statements with an enum, sealed, or Boolean subject … These warnings will become errors in future releases"([What's new in Kotlin 1.6.0](https://kotlinlang.org/docs/whatsnew16.html)). 그리고 1.7이 그 경고를 오류로 올렸다 — "Kotlin 1.7 will report an error about the `when` statement with an enum, sealed, or Boolean subject being non-exhaustive"([Compatibility guide for Kotlin 1.7](https://kotlinlang.org/docs/compatibility-guide-17.html)). **값을 쓰는 식(expression)만이 아니라 값을 버리는 문(statement)에서도** 분기 누락이 오류가 된 것이 이 변화의 내용이다. 상태 전이 코드는 대개 값을 반환하지 않는 문이므로, 이 승격이 없었다면 이 절의 이야기는 거의 성립하지 않는다.

> 주의: 현행 `control-flow.html`의 "If you use `when` as a statement, you don't need to cover all possible cases … However, no error occurs"는 subject가 enum·sealed·Boolean이 **아닌** 경우에만 맞는 서술이다(그 페이지의 예제는 subject가 `String`이다). 완결성 규칙의 정본으로는 위 compatibility guide를 본다.

이 항목이 이 프로젝트에 직결되는 이유는 상태 머신의 크기다. 승인 애그리게이트 하나만 해도 상태 8종에 전이 16건, 그리고 **금지 전이가 따로 22건**(F1~F22) 있다([`domain/state-machines/authorization.md`](../../../domain/state-machines/authorization.md)). 그 문서는 자기 핵심을 이렇게 적는다 — *"이 문서의 핵심은 §4 금지된 전이다. 허용 전이는 구현하면서 자연히 드러나지만, 금지는 명시하지 않으면 아무도 막지 않는다."*

상태를 sealed 계층(또는 enum)으로 표현하면, 상태가 하나 늘어날 때 **그 상태를 분기하는 모든 자리가 동시에 컴파일 오류가 된다.** 문서에 상태를 추가하고 코드 한 곳만 고치는 일이 구조적으로 불가능해진다는 뜻이고, 이것이 "문서에 적힌 전이표"와 "실제 코드"를 잇는, 사람 리뷰가 아닌 유일한 자동 장치다.

### 이 장치가 하지 않는 세 가지

첫째, **완결성 검사는 상태의 집합만 본다.** *"`AUTHORIZED`에서 `capture`가 허용되는가"*, *"`CAPTURED`에서 `reverse`는 F1이라 금지인가"* 는 전부 사람이 적은 조건이며 컴파일러의 시야 밖이다. sealed가 막는 것은 *"새 상태를 아무도 다루지 않는 것"* 까지다.

둘째, **`else`를 한 번 적으면 그 자리에서 검사가 영구히 꺼진다.** 새 상태는 오류를 내는 대신 조용히 `else`로 흘러들고, 그 순간 이 절의 이점은 없던 것이 된다. 실무에서 이 기능이 무력화되는 경로는 거의 전부 이것이다. 흥미롭게도 Java 쪽 명세가 같은 논거를 더 강한 문장으로 적어 두었다 — "if we code the `switch` to cover all the constants known at compile time, and omit the match-all clause, then we will find out about this change the next time we recompile … **A match-all clause risks sweeping exhaustiveness errors under the rug**"([JEP 441: Pattern Matching for switch](https://openjdk.org/jeps/441), Java 21). 두 언어가 독립적으로 같은 결론에 도달했다는 사실 자체가, 이것이 문법 취향이 아니라 유지보수의 문제라는 근거다.

셋째, subject가 sealed·enum·Boolean이 아니면 애초에 검사 대상이 아니다. 상태를 문자열이나 코드 값으로 들고 다니면 같은 코드가 아무 경고 없이 통과한다.

### Java 17+ sealed와의 실질 차이

같은 개념이지만 설계 결정이 몇 군데 갈린다. Java는 허용 서브클래스를 `permits` 절로 **적게** 하고, 각 서브클래스가 `final`·`sealed`·`non-sealed` 중 정확히 하나를 붙이도록 요구한다([JEP 409: Sealed Classes](https://openjdk.org/jeps/409), JDK 17). Kotlin은 그 목록을 적게 하지 않는다 — 설계 문서가 이유를 밝힌다: "Unlike Java, Kotlin does not require any kind of `permits` annotation even when subclasses are specified in another file, which honors Kotlin tradition of avoiding source-code repetition of information that could be inferred by the compiler"([KEEP-226 Sealed interfaces and sealed classes freedom](https://github.com/Kotlin/KEEP/blob/main/proposals/KEEP-0226-sealed-interface-freedom.md), Roman Elizarov).

실무에서 더 중요한 차이는 셋이다.

- **`non-sealed`가 Kotlin에는 없다.** Java는 봉인 계층에 "여기서부터는 열린다"는 탈출구를 문법으로 두었고, Kotlin에는 그 대응물이 없다(닫히지 않은 서브클래스를 두면 그 아래는 그냥 일반 상속이 된다).
- **런타임 안전망이 Java에만 있다.** 컴파일 이후 계층이 바뀌어 어떤 라벨도 맞지 않으면 Java는 `MatchException`을 던진다(JEP 441). Kotlin 쪽의 대응 규정은 **공식 문서·KEEP에서 확인하지 못했다.**
- **두 언어의 봉인 계층은 섞을 수 없다** — "Mixed sealed hierarchies between Java and Kotlin will not be supported. All subclasses of a sealed Kotlin class or interface must be defined in Kotlin"(KEEP-226).

한 가지는 Kotlin 쪽이 최근에 앞서 나갔다. 2.2.20이 도입하고 2.3.0에서 Stable이 된 **데이터 흐름 기반 완결성 검사**는 앞선 조건 검사와 조기 반환까지 추적해 불필요한 `else`를 지울 수 있게 한다 — "the compiler now tracks prior condition checks and early returns, so you can remove redundant `else` branches"([What's new in Kotlin 2.2.20](https://kotlinlang.org/docs/whatsnew2220.html)). `else`를 지울 수 있게 만드는 기능은 위의 둘째 함정을 줄인다는 점에서 단순한 편의가 아니다.

## 4. 값을 값으로 — data class와 value class

이 프로젝트의 공통 커널에는 값 타입이 둘 있고, 서로 다른 도구로 만들어져 있다. `Money`는 `data class`이고 `BusinessDate`는 `@JvmInline value class`다. 왜 갈렸는지가 이 절의 내용이다.

```kotlin
public data class Money(
    public val minorUnits: Long,
    public val currency: Currency,
) : Comparable<Money>

@JvmInline
public value class BusinessDate(public val value: LocalDate) : Comparable<BusinessDate>
```

(`jun-bank/common` — `common-kernel/src/main/kotlin/com/junbank/common/kernel/`)

### data class — 동등성을 컴파일러가 쓴다

"The compiler automatically derives the following members from all properties declared in the primary constructor: `equals()`/`hashCode()` pair · `toString()` … · `componentN()` functions … · `copy()` function"([Data classes](https://kotlinlang.org/docs/data-classes.html)). Java에서 IDE로 생성해 두고 필드를 추가할 때마다 갱신을 잊는 그 코드를 언어가 대신 쓴다.

값 타입에서 이것이 중요한 이유는 편의가 아니라 **정확성**이다. `Money(1000, Currency.KRW) == Money(1000, Currency.KRW)`가 참이어야 금액을 맵의 키로 쓰거나 단언에 쓸 수 있고, 그것을 손으로 쓰면 필드가 늘 때 조용히 어긋난다. 실제로 우리 `MoneyTest`의 단언은 전부 `assertEquals(krw(expectedQuotient), division.quotient)` 형태 — 생성된 `equals`에 기대고 있다.

함정이 셋 있다.

**첫째, 클래스 바디에 선언한 프로퍼티는 생성 코드에서 빠진다.** "The compiler only uses the properties defined inside the primary constructor for the automatically generated functions … two `Person` objects with the same name but different age values are considered equal since `equals()` only evaluates properties from the primary constructor"(같은 문서). 이것은 기능이자 함정이다 — 제외를 **의도할 때** 쓰는 장치지만, 의도 없이 바디에 필드를 하나 옮겨 놓으면 동등성 판정이 조용히 바뀐다.

**둘째, `copy()`는 얕은 복사다.** "The `copy()` function creates a shallow copy of the instance. In other words, it doesn't copy components recursively. As a result, references to other objects are shared"(같은 문서). 문서가 든 예제가 정확히 이 프로젝트의 위험 형태다 — `MutableList`를 든 data class를 `copy()`하면 원본과 사본이 같은 리스트를 공유한다. `data class` + `val`은 **깊은 불변을 주지 않는다**(§5와 같은 함정이다).

**셋째, private 생성자로 불변식을 지키는 값 타입은 `copy()`로 뚫린다.** 팩토리에서만 만들 수 있게 생성자를 닫아도 생성된 `copy()`는 public이라 `User.of("Alex", 1).copy(name = "")` 같은 우회가 성립한다. Kotlin은 이것을 고치는 중이고 2.0.20부터 경고를 낸다 — "In future Kotlin releases, we will introduce the behavior that the default visibility of the `copy()` function is the same as the constructor … Our migration plan starts with Kotlin 2.0.20, which issues warnings"([What's new in Kotlin 2.0.20](https://kotlinlang.org/docs/whatsnew2020.html)). 다만 **우리가 쓰는 2.4.x는 아직 경고 단계**이므로, 지금 그 우회를 막으려면 `@ConsistentCopyVisibility` 또는 `-Xconsistent-data-class-copy-visibility`를 명시적으로 켜야 한다(정본은 [KT-11914](https://youtrack.jetbrains.com/issue/KT-11914) — 오류 승격 시점은 JetBrains도 "not yet set in stone"이라고 적는다).

### value class — 타입만 얻고 래퍼는 안 만든다

`BusinessDate`가 `value class`인 이유는 그 타입의 KDoc이 직접 적고 있다. 이 시스템에는 영업일(BR-14 — 원장 귀속)과 달력일(BR-05 — 1일 한도의 "하루")이 **둘 다** 쓰이고, 둘이 같은 `LocalDate`를 쓰면 **컴파일러가 그 혼동을 잡아주지 않는다.** 감싸는 것 자체가 목적이다.

문제는 감싸는 비용이다. "it introduces runtime overhead due to additional heap allocations. Moreover, if the wrapped type is primitive, the performance hit is significant"([Inline value classes](https://kotlinlang.org/docs/inline-classes.html)). value class는 이 비용을 없앤다 — 런타임에는 대개 감싼 값 그 자체로 표현된다.

"대개"가 정확한 표현이다. 규칙이 한 줄로 적혀 있다 — "**As a rule of thumb, inline classes are boxed whenever they are used as another type.**" 문서가 드는 경우는 제네릭 타입 인자로 쓸 때, 인터페이스 타입으로 쓸 때, 그리고 **nullable로 쓸 때**(`Foo?`는 `Foo`와 다른 타입이다)다. 그러니까 `BusinessDate?`로 선언하거나, `List<BusinessDate>`에 담거나, `Comparable`을 받는 API에 넘기는 순간 힙 할당이 되살아난다. **"무비용 래퍼"는 조건부 문장이고, 그 조건은 코드가 어떻게 쓰이냐에 달려 있다.**

그리고 Java 쪽에서는 이 타입이 잘 보이지 않는다. 언박싱되면 시그니처가 겹치므로 컴파일러가 함수 이름에 해시를 붙인다 — "functions using inline classes are mangled by adding some stable hashcode to the function name"(같은 문서). 설계 문서는 이것이 부작용이 아니라 **의도**라고 적는다: "Now it will not possible to call this function from Java because `-` is an illegal symbol there … As these functions are accessible only from Kotlin, the problem about non-public primary constructors and `init` blocks becomes easier"([KEEP-0104 Inline classes](https://github.com/Kotlin/KEEP/blob/main/proposals/KEEP-0104-inline-classes.md), Stable since 1.5). 즉 **불변식을 Java 우회로 뚫지 못하게 만든 대가로 Java 상호운용을 끊은 것**이다. 열려면 `@JvmName`이나(개별) `@JvmExposeBoxed`·`-Xjvm-expose-boxed`를 써야 한다.

### Java record와의 자리

Java 16의 record는 다른 것을 강제한다 — "A record class is implicitly final, and cannot be abstract … The fields derived from the record components are final. This restriction embodies an immutable by default policy"([JEP 395: Records](https://openjdk.org/jeps/395)). Kotlin data class는 `var` 파라미터를 허용하므로 이 지점에서는 record가 더 엄격하다. 반대로 **record에는 `copy()`가 없다** — 파생 멤버 목록에 없고, JEP는 "복사"를 `new R(r1.c1(), r1.c2(), …)`처럼 손으로 재생성하는 것으로 설명한다.

JVM 21 프로젝트이므로 `@JvmRecord`(JVM 16 바이트코드 이상 필요)를 붙여 진짜 record로 만들 수도 있다. 다만 조건이 있다 — "The class cannot declare any mutable properties with backing fields"이고, **기존 클래스에 나중에 붙이면 바이너리 호환이 깨진다**("Applying `@JvmRecord` to an existing class is not a binary compatible change. It alters the naming convention of the class property accessors" — [Using Java records in Kotlin](https://kotlinlang.org/docs/jvm-records.html)). 버전으로 배포되는 공통 라이브러리(ADR-025 CL-1)에서는 이 한 줄이 결정적이다.

마지막으로 한 가지를 기록해 둘 만하다. Kotlin이 `@JvmInline`이라는 플랫폼 한정 어노테이션을 굳이 요구하는 이유를 설계 노트가 밝히고 있다 — JVM에 진짜 값 타입이 오면(Project Valhalla) 필드 여러 개짜리 value class도 효율적으로 표현할 수 있지만, "We cannot wait to make it stable until Valhalla becomes available in some unclear future. That was a motivation to require a `@JvmInline` annotation"([Design Notes on Kotlin Value Classes](https://github.com/Kotlin/KEEP/blob/main/notes/0001-value-classes.md), Roman Elizarov). 그 Valhalla는 [JEP 401 Value Objects](https://openjdk.org/jeps/401)로 **JDK 28 preview** 단계이므로, 우리 JVM 21에서는 "프로퍼티 하나" 제약이 앞으로도 한동안 유효하다.

## 5. 가변성을 이름에 적는다 — val/var와 읽기 전용 컬렉션

`val`이 보장하는 범위는 공식 정의가 정확히 한정한다 — "variables that are assigned a value only once … can't be reassigned a different value after initialization"([Basic syntax](https://kotlinlang.org/docs/basic-syntax.html)). **참조가 고정될 뿐 객체 내부는 고정되지 않는다.** 컬렉션 문서가 이것을 직접 적는다: "Note that a mutable collection doesn't have to be assigned to a `var`. Write operations with a mutable collection are still possible even if it is assigned to a `val`. The benefit of assigning mutable collections to `val` is that you protect the reference to the mutable collection from modification"([Collections overview](https://kotlinlang.org/docs/collections-overview.html)).

컬렉션 쪽의 설계는 §1 목록의 마지막 항목이다 — "Separate interfaces for read-only and mutable collections". Java와의 대조는 공식 마이그레이션 가이드가 잘 세워 놓았다. Java에서는 `Arrays.asList()`도 `Collections.unmodifiableList()`도 타입이 전부 `List`라서 "**You can't tell whether a collection is mutable by looking at its type**"이고 실패는 런타임 `UnsupportedOperationException`으로 온다. Kotlin에서는 `listOf(...)`에 `add`를 부르면 "Compilation error - Unresolved reference: add"다([Collections in Java and Kotlin](https://kotlinlang.org/docs/java-to-kotlin-collections-guide.html)). 실패 시점이 런타임에서 컴파일로 옮겨 온 것 — 이 언어가 반복해서 하는 그 이동이다.

### 읽기 전용은 불변이 아니다 — 그리고 공식 문서가 이 말을 흐린다

문제는 `List`가 **뷰**라는 사실이다. 입문 문서는 이것을 숨기지 않는다 — "you can **create a read-only view of a mutable list** by assigning it to a `List` … This is also called casting"([Kotlin tour: Collections](https://kotlinlang.org/docs/kotlin-tour-collections.html)). 뷰는 원본과 같은 객체이므로, 원본 참조를 들고 있는 쪽은 여전히 고칠 수 있고 그 변경은 뷰에도 보인다.

그런데 같은 공식 문서군에서 용어가 갈린다. 코딩 컨벤션은 이 인터페이스들을 "**immutable** collection interfaces"라고 부른다 — "Always use immutable collection interfaces (`Collection`, `List`, `Set`, `Map`) to declare collections which are not mutated"([Coding conventions](https://kotlinlang.org/docs/coding-conventions.html)). 이 문서를 먼저 읽은 사람이 "`List`를 반환하면 불변"이라고 결론 내리는 것은 자연스럽다. **함정의 절반은 용어에 있다.**

### 우리 스택에서 실제로 확인한 것

말로만 두면 실감이 안 나므로 이 프로젝트가 쓰는 조합(`kotlin-stdlib` 2.4.10 · Temurin JDK 21.0.5)에서 Java 쪽 호출자로 직접 확인했다.

| Kotlin에서 만든 것 | 런타임 클래스 | Java에서 `add()` | Java에서 `set()` |
|---|---|---|---|
| `listOf()` | `kotlin.collections.EmptyList` | 예외 | 예외 |
| `listOf("a")` | `java.util.Collections$SingletonList` | 예외 | 예외 |
| `listOf("a","b")` | `java.util.Arrays$ArrayList` | 예외 | **성공** |
| `mutableListOf(...)`를 `List` 타입으로 노출 | `java.util.ArrayList` | **성공** | **성공** |
| (대조) Java `List.of("a","b")` | `ImmutableCollections$List12` | 예외 | 예외 |

두 줄이 중요하다. **`listOf()`는 `List.of()`가 아니다** — 원소가 둘 이상이면 `Arrays.asList`로 내려가 원소 교체(`set`)가 통과한다. 그리고 **`List` 타입은 런타임 보증이 아니다** — 애그리게이트가 자기 `MutableList`를 `List`로 내주면 런타임 클래스는 그냥 `ArrayList`이고, Java 호출자에게는 아무것도 막히지 않는다. Kotlin 안에서도 `as MutableList` 캐스트 한 줄이면 같은 일이 된다.

이것이 규약 **KO-2**가 미리 적어 둔 내용의 실측판이다 — *"`List` 반환 타입은 불변을 보장하지 않는다. 읽기 전용 인터페이스 뒤의 객체가 외부 별칭으로 변경될 수 있다 … 컴파일이 막는 것은 '수신자가 `add`를 부르는 것'까지이고, 별칭 경로는 방어 복사·영속 컬렉션 + 변경 감지 테스트가 막는다."* 애그리게이트 불변식(INV-\*)이 "객체 안에서만 성립"하려면 밖에서 고쳐질 수 없어야 하는데, **타입 시스템이 주는 것은 그 절반뿐이다.**

진짜 불변 컬렉션이 필요하면 별도 의존성을 들여야 한다. `kotlinx.collections.immutable`은 stdlib가 아니고 좌표는 `org.jetbrains.kotlinx:kotlinx-collections-immutable`이며, 현재 버전은 0.5.1에 안정성 등급은 **Alpha**다 — "The feature set is still incomplete, and **breaking changes are expected**"([Stability of Kotlin components](https://kotlinlang.org/docs/components-stability.html)). "영속 컬렉션을 쓰면 된다"는 결론에는 이 비용이 함께 적혀야 한다.

## 6. 코루틴 — 스레드가 아니라 컴파일러 변환이다

코루틴을 "가벼운 스레드"로 설명하는 문장은 흔하지만, 실제로 무엇이 일어나는지는 설계 문서에 정확히 적혀 있다. `suspend`는 문법 설탕이 아니라 **JVM 시그니처를 바꾸는 컴파일 변환**이다 — "Suspending functions are implemented via Continuation-Passing-Style (CPS). Every suspending function and suspending lambda has an additional `Continuation` parameter that is implicitly passed to it when it is invoked"([KEEP-0164 Kotlin Coroutines](https://github.com/Kotlin/KEEP/blob/main/proposals/KEEP-0164-coroutines.md), Stable in 1.3). `suspend fun <T> CompletableFuture<T>.await(): T`로 쓴 함수의 실제 구현 시그니처는 `fun <T> CompletableFuture<T>.await(continuation: Continuation<T>): Any?`가 된다.

그 위에서 함수 본문은 상태 기계로 컴파일된다 — "a suspending function is compiled to a state machine, where states correspond to suspension points"(같은 문서). 중단 지점마다 번호가 붙고(`label`), **지역 변수는 스택이 아니라 그 익명 클래스의 필드로 승격**되며, 호출마다 상태 기계 객체가 하나 생겼다 사라진다. 중단 여부는 컴파일 시점이 아니라 런타임에 갈린다 — 중단하면 `COROUTINE_SUSPENDED`라는 표지 값을 돌려주고, 중단하지 않으면 결과를 그대로 반환한다. 설계 문서는 이 반환 타입이 "`COROUTINE_SUSPENDED`와 `T`의 합집합이며 Kotlin의 타입 시스템으로는 표현할 수 없다"고 스스로 적는다.

"가볍다"의 실체도 한 문장으로 정의돼 있다. "The running coroutine is always executed in some thread. However, a _suspended_ coroutine does not consume a thread and it is not bound to a thread in any way"(같은 문서 부록). 즉 **중단된 코루틴만 스레드를 놓는다.** 실행 중일 때는 언제나 진짜 스레드 위에 있다.

### 구조적 동시성 — 이 모델의 진짜 값

코루틴에서 가장 크게 갈리는 것은 성능이 아니라 **생명주기 관리**다. "coroutines form a tree hierarchy of parent and child tasks with linked lifecycles … A parent coroutine waits for its children to complete before it finishes. If the parent coroutine fails or gets canceled, all its child coroutines are recursively canceled too"([Coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html)). 새 코루틴은 `CoroutineScope` 안에서만 시작할 수 있으므로 "던져 놓고 잊는" 작업이 구조적으로 생기지 않는다 — `ExecutorService.submit()`과 갈리는 지점이 정확히 여기다.

예외 전파도 기본값이 강하다. "If a coroutine encounters an exception other than `CancellationException`, it cancels its parent with that exception. **This behaviour cannot be overridden** and is used to provide stable coroutines hierarchies for structured concurrency"([Coroutine exceptions handling](https://kotlinlang.org/docs/exception-handling.html), 강조는 원문 아님). 형제까지 함께 죽는 것이 기본이고, 벗어나려면 `try/catch`가 아니라 `SupervisorJob`으로 **구조 자체를 바꿔야** 한다.

### 한계 — 취소는 보장이 아니라 규약이다

"In Kotlin, coroutine cancellation is cooperative. Coroutines react to cancellation only when they cooperate by suspending or checking for cancellation explicitly"([Cancellation](https://kotlinlang.org/docs/coroutines-cancellation.html)). 중단점을 지나지 않는 코드는 취소해도 계속 돈다 — "If a coroutine doesn't suspend for a long time, it also doesn't stop when it's canceled." 계산 루프는 `yield()`·`isActive`·`ensureActive()`로 직접 협조해야 하고, `suspendCoroutine`으로 직접 감싼 어댑터는 취소에 아예 반응하지 않는다(같은 문서).

관측성 비용도 실재한다. `kotlinx.coroutines`는 비동기 예외의 스택 트레이스를 **사후에 재봉합**하는 기능을 따로 갖고 있는데, 문서가 그 대가를 적는다 — "The only downside of this approach is losing referential transparency of the exception." 게다가 복구가 항상 되지도 않는다: "If the exception class has class-specific fields not inherited from Throwable, the exception is not copied"([kotlinx.coroutines debugging](https://github.com/Kotlin/kotlinx.coroutines/blob/master/docs/topics/debugging.md)). 디버거에서는 변수가 사라지고("was optimized out"), 회피 옵션 `-Xdebug`는 "Never use this flag in production: `-Xdebug` can cause memory leaks"라고 못박혀 있다([Debug coroutines using IntelliJ IDEA](https://kotlinlang.org/docs/debug-coroutines-with-idea.html)).

### 가상 스레드와의 대비 — 같은 문제, 반대 해법

Java 21의 가상 스레드는 같은 문제(스레드 희소성)를 정반대로 푼다. JEP의 목표 첫 줄이 "Enable server applications written in the **simple thread-per-request style** to scale with near-optimal hardware utilization"이고, non-goal에는 "It is not a goal to change the basic concurrency model of Java"가 명시돼 있다. 비동기 스타일에 대한 비판도 직접적이다 — "They thus forsake the language's basic sequential composition operators, such as loops and try/catch blocks … Stack traces provide no usable context, debuggers cannot step through request-handling logic"([JEP 444: Virtual Threads](https://openjdk.org/jeps/444), Java 21). 해법은 런타임 쪽에 있다: "When code running in a virtual thread calls a blocking I/O operation in the `java.*` API, the runtime performs a non-blocking OS call and automatically suspends the virtual thread."

두 설계의 배치를 대조하면 성격이 분명해진다. Kotlin은 언어에 최소한만 넣고 나머지를 라이브러리에 남겼다 — "the compiler is only responsible for support of suspending functions, suspending lambdas, and the corresponding suspending function types … the rest is left to application libraries"(KEEP-0164). `launch`·`async`·`Dispatchers`는 언어가 아니라 `kotlinx.coroutines`다. 반대로 가상 스레드는 JDK 런타임에 들어갔고 코드는 그대로다. **JetBrains가 이 둘을 직접 비교한 공식 입장은 확인하지 못했다**(블로그·kotlinx.coroutines README·공식 문서에서 언급 0건).

### 이 프로젝트가 쓰지 않는 이유

Spring은 MVC(서블릿) 스택에서도 `suspend` 컨트롤러를 지원한다 — "Suspending function support in **Spring MVC and WebFlux** annotated `@Controller`"([Spring Framework — Coroutines](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html)). 그러므로 *"블로킹 스택이라 못 쓴다"* 는 근거는 성립하지 않는다. 실제 이유는 이익-비용 쪽이다.

이익이 서지 않는 첫째 이유는 블로킹 드라이버다. JDBC 호출은 코루틴이 흡수하지 못하고 결국 진짜 스레드를 점유해야 하므로 별도 풀로 격리된다 — `Dispatchers.IO`는 "designed for offloading blocking IO tasks to a shared pool of threads"이며 병렬도가 "the limit of 64 threads or the number of cores (whichever is larger)"로 제한된다([Dispatchers.IO API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html)). 즉 블로킹 스택에서 코루틴을 도입하면 *"코루틴 → `withContext(IO)` → 스레드 풀"* 이라는 우회 계층이 하나 늘 뿐이다. 반면 비용은 실재한다 — ThreadLocal 기반 인프라(MDC·trace)가 그대로 따라오지 않고(Spring 문서가 traceId 유실을 직접 인정한다), 앞 절의 스택 트레이스·디버깅 비용이 붙고, 의존성으로 `kotlinx-coroutines-reactor`가 따라온다.

정리하면 코루틴은 이 프로젝트에서 **요구가 아직 없는 도구**다(C-08 — 요구 → 계약 → 도구). 처리량 요구(QS-01)를 실제로 걸어 보고 스레드가 병목으로 실측될 때, JVM 21에서 먼저 검토할 대상은 코드 변경을 요구하지 않는 가상 스레드다. 코루틴이 그보다 나은 자리는 **구조적 동시성과 취소가 요구 자체인 경우**(여러 외부 호출을 묶어 하나라도 실패하면 전부 취소해야 하는 흐름)이며, 그때는 위 비용을 알고 지불하는 것이 된다.

## 7. 확장 함수와 수신자 람다 — DSL이 되는 이유, 그리고 정적 디스패치라는 천장

확장 함수의 정의에서 중요한 것은 무엇을 하지 않는가다. "Importantly, extensions don't modify the classes or interfaces they extend. When you define an extension, you don't add new members. You make new functions callable or new properties accessible using the same syntax"([Extensions](https://kotlinlang.org/docs/extensions.html)). 클래스를 열지 않고도 그 타입에 대한 어휘를 바깥에서 늘릴 수 있다는 것이 이 기능의 값이다 — 라이브러리 타입(`LocalDate`·`String`·`List`)에 우리 도메인의 말을 붙이는 자리가 여기다.

대가는 디스패치 규칙에 있다. "Extension functions are dispatched statically, meaning the compiler determines which function to call based on the receiver type at compile time … the compiler chooses the function based on the declared type, not the actual instance"(같은 문서). 확장은 다형적이지 않다 — 변수의 **선언 타입**이 무엇을 부를지 정한다. 그리고 이름이 겹치면 확장이 진다: "If a class has a member function and there's an extension function with the same receiver type, the same name, and compatible arguments, the member function takes precedence." 라이브러리가 나중에 같은 이름의 멤버를 추가하면 호출 대상이 조용히 바뀔 수 있다는 뜻이다.

### 수신자 람다 — DSL이 성립하는 지점

DSL을 만드는 것은 확장 함수가 아니라 **수신자 있는 함수 타입**이다. "By using well-named functions as builders in combination with function literals with receiver it is possible to create type-safe, statically-typed builders in Kotlin"([Type-safe builders](https://kotlinlang.org/docs/type-safe-builders.html)). `init: HTML.() -> Unit` 같은 타입은 "이 블록 안에서 `this`는 `HTML`이다"를 선언하고, 그래서 블록 안에서 부를 수 있는 이름이 타입으로 제한된다. 동적 언어의 빌더와 갈리는 지점이 정확히 여기다 — 오타는 런타임이 아니라 컴파일에서 걸린다.

같은 문서가 이 구조의 함정도 적는다. 중첩된 블록에서는 바깥 수신자의 멤버까지 전부 보이므로 `head { head { } }` 같은 무의미한 중첩이 성립한다. `@DslMarker`가 그것을 막는다 — "the Kotlin compiler knows which implicit receivers are part of the same DSL and allows to call members of the nearest receivers only." 바깥 수신자를 부르려면 `this@html.head { }`처럼 명시해야 한다.

### 우리 테스트가 실제로 읽히는 이유

이 프로젝트는 단언 DSL 라이브러리를 **넣지 않았다.** E2 §4.2가 도구 후보들을 도입 조건과 함께 보류했고(C-08 도구 최소주의), 확정된 것은 실행기(JUnit5) 하나뿐이다. 그런데도 첫 테스트 코드는 읽힌다 — 그 가독이 라이브러리가 아니라 언어 기본 기능에서 왔기 때문이다.

```kotlin
/** 한 줄이 곧 한 케이스다. 표를 문자열이 아니라 타입으로 넘기면 오타가 컴파일에서 걸린다. */
data class ComparisonCase(
    val label: String,
    val amount: Money,
    val limit: Money,
    val expectedSignum: Int,
) {
    override fun toString(): String = label
}

@ParameterizedTest
@MethodSource("comparisonCases")
fun `한도 경계 3점에서 비교 부호가 갈린다`(case: ComparisonCase) { /* ... */ }
```

(`jun-bank/common` — `common-kernel/src/test/kotlin/com/junbank/common/kernel/MoneyTest.kt`)

여기서 일하는 것은 백틱 함수 이름, data class, 그리고 연산자 오버로딩(`quotient * divisor + remainder`)이다. 셋 다 "Kotlin에 있고 Java에 없는 것" 목록의 항목이고([Comparison to Java](https://kotlinlang.org/docs/comparison-to-java.html)), 셋 다 의존성을 늘리지 않는다. **읽히는 테스트를 위해 DSL 라이브러리가 필요하다는 통념은 최소한 이 규모에서는 성립하지 않았다** — 이것이 도구를 늦게 넣는 규칙(C-08)이 실제로 버틴 한 사례다.

## 8. 검사 예외 폐지 — 무엇을 얻고 무엇을 떠넘겼나

같은 항목이 앞서 본 두 목록에 **동시에** 실려 있다. "Kotlin does not have checked exceptions"는 *"Kotlin에서 해소된 Java의 문제"* 에 들어 있고, "Checked exceptions"는 *"Java에 있고 Kotlin에 없는 것"* 에도 들어 있다([Comparison to Java](https://kotlinlang.org/docs/comparison-to-java.html)). 공식 문서가 이것을 개선이자 상실로 함께 적고 있다는 사실 자체가 이 논쟁의 상태를 잘 보여 준다.

찬성 쪽 근거로 문서가 드는 것은 한 줄뿐이다 — "Kotlin treats all exceptions as unchecked by default. Unchecked exceptions simplify the exception handling process: you can catch exceptions, but you don't need to explicitly handle or declare them"([Exceptions](https://kotlinlang.org/docs/exceptions.html)). 실무에서 이 결정이 지우는 것은 대개 두 가지다. 하나는 아무것도 하지 않는 `catch` 블록이고(검사 예외는 잡거나 선언하도록 강제하지만 **의미 있게 처리하도록** 강제하지는 못한다), 다른 하나는 람다·고차 함수와의 충돌이다 — 함수 타입에 예외 목록을 실을 방법이 없으면 검사 예외는 추상화를 통과하지 못한다.

반대 쪽 손실도 분명하다. 검사 예외는 **실패 경로를 시그니처에 적게 만드는 유일한 언어 장치**였고, 그것이 사라지면 "이 함수가 어떤 이유로 실패하는가"는 문서와 규율의 문제가 된다. 상호운용에서는 이 손실이 즉시 형태를 드러낸다 — Kotlin 함수는 기본적으로 `throws`를 선언하지 않으므로, Java 호출자가 그 예외를 잡으려 하면 컴파일되지 않는다. "You get an error message from the Java compiler, because `writeToFile()` does not declare `IOException`. To work around this problem, use the `@Throws` annotation in Kotlin"([Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html)).

이 프로젝트는 그 빈자리를 언어가 아니라 설계로 메운다. 규약 §3은 오류 코드 대장을 **유일 창구**로 두고, 수기 문자열을 금지하며, 판정 순서(K-1 · X-10)를 정본으로 고정한다. 즉 실패 경로의 전수성은 예외 타입 계층이 아니라 **오류 코드 모델과 그것을 검사하는 테스트**가 책임진다. 표준 라이브러리의 `Result`(`kotlin.Result` — [API 문서](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/), Kotlin 1.3부터 "a discriminated union that encapsulates a successful outcome with a value of type `T` or a failure with an arbitrary `Throwable`")와 `runCatching`도 같은 자리를 노리지만, 그것 역시 **컴파일러가 강제하지 않는 관용구**라는 점에서는 예외와 다르지 않다. 검사 예외의 대체물은 아직 언어 안에 없다.

## 9. Java 상호운용의 실제 — TL-1 스파이크가 실측한 것

FAQ의 "Kotlin is 100% interoperable with the Java programming language"([Kotlin FAQ](https://kotlinlang.org/docs/faq.html))는 사실이지만 **무마찰이라는 뜻은 아니다.** 마찰은 한 가지 형태로 반복된다 — Kotlin에 없는 개념(static 멤버, 필드, 오버로드, 검사 예외, open 클래스)을 Java 쪽 세계가 요구할 때, 그것을 어노테이션이나 컴파일러 플러그인으로 되돌려 주어야 한다.

가장 자주 부딪히는 것이 `static`이다. companion object의 멤버는 기본적으로 인스턴스 메서드이고, Java에서는 `C.Companion.callNonStatic()`으로만 닿는다. "Kotlin can also generate static methods for functions defined in named objects or companion objects if you annotate those functions as `@JvmStatic`. If you use this annotation, the compiler generates both a static method in the enclosing class of the object and an instance method in the object itself"([Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html)). 같은 문서가 나머지 되돌림도 하나씩 정의한다 — `@JvmField`(프로퍼티를 필드로), `@JvmOverloads`(기본값 파라미터마다 오버로드 생성), `@file:JvmName`(파일이 만드는 `AppKt` 클래스 이름 변경), 그리고 앞 절의 `@Throws`.

### 우리가 실제로 부딪힌 자리

이 마찰이 어느 정도인지를 이 프로젝트는 추측이 아니라 스파이크로 확인했다. `dev-conventions.md` **TL-1**은 JUnit5를 조건부 충족으로 남기면서 조건을 하나 달았다 — *"Kotlin에서의 파라미터 소스 구성은 미실증 · 첫 케이스 작성이 스파이크다."* JUnit5의 `@MethodSource`가 **정적** 팩토리를 요구하는데 Kotlin에는 `static`이 없기 때문이다.

결과는 세 형태 전부 성립이었다(`jun-bank/common` README — TL-1 파라미터 소스 스파이크).

| 형태 | 구성 | 쓰기 좋은 자리 |
|---|---|---|
| A | `@MethodSource` + `companion object` + `@JvmStatic` | 케이스가 타입 있는 data class여야 할 때 |
| B | `@CsvSource` | 스칼라만으로 표가 되는 자리. 값이 문자열 리터럴이라 타입 오타는 실행 시에 걸린다 |
| C | `@TestInstance(PER_CLASS)` + 비정적 `@MethodSource` | 케이스가 픽스처를 참조할 때. `@JvmStatic`도 `companion object`도 없다 |

그 판정문이 이 절의 결론이기도 하다 — *"`@JvmStatic`이 필요한 것은 형태 A뿐이고, 그마저 형태 C가 우회한다. 실행기를 바꿔야 할 이유가 아니라 형태를 고르는 문제였다."* 상호운용 마찰의 전형이 이렇다. 막히지 않지만 **한 번은 알아야 하고**, 모르면 "Kotlin에서는 이 도구가 안 된다"는 잘못된 결론에 도달한다.

### 어노테이션으로 안 되는 것 — final by default

한 가지 마찰은 어노테이션이 아니라 컴파일러 플러그인을 요구한다. "Kotlin has classes and their members `final` by default, which makes it inconvenient to use frameworks and libraries such as Spring AOP that require classes to be `open`"([All-open compiler plugin](https://kotlinlang.org/docs/all-open-plugin.html)). Spring(C-06)을 쓰는 이상 이 문제는 선택이 아니라 전제이며, 해법은 `kotlin-spring` 플러그인이다 — `@Component`·`@Async`·`@Transactional`·`@Cacheable`·`@SpringBootTest`가 붙은 클래스를 자동으로 열고, `@Component`의 메타 어노테이션 덕에 `@Configuration`·`@Service`·`@Repository`도 함께 열린다.

이것은 편의 기능이 아니라 **언어의 기본값과 프레임워크의 전제가 충돌하는 자리**다. 기억해 둘 것은 그 플러그인이 클래스를 여는 범위가 **어노테이션 목록으로 정해진다**는 점이다 — 목록 밖의 클래스는 여전히 final이므로, 프록시가 필요한데 목록에 없는 조합을 만들면 그 자리에서 막힌다.

반대 방향(Java를 Kotlin에서 호출하기)의 마찰은 훨씬 얕다. SAM 변환이 자동이고("Kotlin function literals can be automatically converted into implementations of Java interfaces with a single non-default method"), 게터·세터는 프로퍼티로 보이며, 컬렉션은 매핑 타입으로 들어온다. 남는 문제는 §2의 플랫폼 타입 하나다.

## 10. 비용 — 컴파일 시간·바이너리·학습

**컴파일 시간.** Kotlin 컴파일이 javac보다 느리다는 것은 널리 알려진 인식이지만, **JetBrains가 발표한 Kotlin 대 Java 컴파일 속도 비교 수치는 확인하지 못했다.** 공식 수치가 있는 것은 Kotlin 컴파일러 자신의 세대 간 비교다 — "The K2 compiler brings up to 94% compilation speed gains. For example, in the Anki-Android project, clean build times were reduced from 57.7 seconds in Kotlin 1.9.23 to 29.7 seconds in Kotlin 2.0.0"([K2 compiler migration guide](https://kotlinlang.org/docs/k2-compiler-migration-guide.html)). 증분 빌드의 초기화 단계는 최대 488%, 분석 단계는 최대 376% 빨라졌다고 같은 문서가 적는다(벤치마크 대상은 Anki-Android와 Exposed 두 오픈소스 프로젝트).

수치를 읽을 때 주의할 점이 둘이다. 하나는 이것이 **K1 대비**이지 Java 대비가 아니라는 것이고, 다른 하나는 clean build 수치와 incremental 수치가 자릿수부터 다르다는 것이다(29.7초 대 0.122초). 실제 개발 루프에서 체감되는 것은 후자이고, 그것을 지탱하는 장치는 기본으로 켜져 있다 — "The Kotlin Gradle plugin supports incremental compilation, which is enabled by default for Kotlin/JVM and Kotlin/JS projects"([Compilation and caches](https://kotlinlang.org/docs/gradle-compilation-and-caches.html)). 다만 ABI가 바뀌면 파급이 커진다 — "When a part of ABI changes, the Kotlin compiler recompiles all classes that depend on the changed class." 그리고 Kotlin 컴파일은 Gradle 데몬과 별도의 **Kotlin 데몬** JVM에서 돌아 메모리를 따로 먹는다(같은 문서).

**어노테이션 처리는 별도 항목이다.** 공식 문서가 kapt의 비용을 직접 적는다 — "It works by translating Kotlin source code into Java 'stubs' and then running the annotation processors on those stubs. However, this process is expensive, significantly increases build time, and loses some Kotlin-specific features in translation"([Migrate from kapt to KSP](https://kotlinlang.org/docs/ksp-kapt-migration.html)). 대안인 KSP는 "understands all Kotlin features and analyzes the source code directly, reducing build time"라고 같은 문서가 적는다. 실무적 함의는 단순하다 — **Java 어노테이션 프로세서에 의존하는 스택을 그대로 들고 오면 Kotlin의 빌드 비용이 가장 나빠진다.** 이 프로젝트는 ORM 선택(ADR-026 — Spring Data JDBC)과 도구 최소주의(C-08) 덕에 이 경로를 아직 밟지 않았다.

**바이너리 크기.** Kotlin으로 만든 산출물은 `kotlin-stdlib`를 런타임 의존으로 갖는다. 그 크기가 서버 배포에서 문제가 된 사례를 이 프로젝트 맥락에서 근거로 제시할 만한 **공식 수치는 확인하지 못했다** — Android 쪽 메서드 수 논의가 주된 출처인데, 우리 배포 형태(JVM 서버 3대, 컨테이너 없음)와 전제가 다르다. 이 항목은 비용으로 세우되 값은 비워 두는 것이 정직하다.

**학습 비용.** 가장 실질적인 지표는 앞서 본 목록의 반대쪽이다. "Kotlin에 있고 Java에 없는 것"에 21개 항목이 열거돼 있다 — 인라인 함수, 확장 함수, null 안전, 프로퍼티, 위임, 선언 지점 변성, 연산자 오버로딩, companion object, data class, 코루틴, 기본값 파라미터, 명명 인자, 중위 함수, explicit API 모드 등([Comparison to Java](https://kotlinlang.org/docs/comparison-to-java.html)). 이것이 학습 표면이고, 팀이 실제로 하는 일은 그중 **부분집합을 고르고 나머지를 안 쓰기로 합의하는 것**이다.

우리 규약이 정확히 그 작업을 했다. §1이 공식 스타일을 통째로 채택해 스타일 논쟁을 닫고(KO-1), 고유 규칙 다섯 건만 남겼다. 그리고 공통 라이브러리는 `explicitApi()`를 켠다 — *"공개 표면이 곧 세 배포의 계약이므로 무엇이 public인지 실수로 정해지면 안 된다"*(`jun-bank/common` README). 언어 기능이 많다는 것의 비용은 "배울 게 많다"가 아니라 **"팀마다 다른 Kotlin을 쓰게 된다"** 이고, 그 비용은 규약과 린트로만 줄어든다.

## 11. 정리 — 컴파일러가 막는 것과 우리가 막아야 하는 것

이 문서가 돌아본 기능들은 하나의 공통 형태를 갖는다. **각각은 특정한 경계 하나에서 코드를 거부한다** — non-null 타입은 그 시그니처를 지나는 대입에서, `when` 완결성은 sealed 타입을 분기하는 자리에서, value class는 그 타입을 요구하는 API에서, 읽기 전용 컬렉션 타입은 수신자가 변경 메서드를 부르는 지점에서. 그리고 각각은 그 경계 **바깥에서 정확히 무력하다**.

이 프로젝트의 규약이 그 사실을 이미 수치로 적고 있다. `dev-conventions.md` §1의 Kotlin 규칙은 여섯 건인데(KO-1~KO-6), **주 강제 수단이 「컴파일」인 것은 하나도 없다.** 불변 우선(KO-2)은 린트와 별칭 변경 감지 테스트가, null 안전(KO-3)은 정적 검사와 경계 테스트가, 값 타입 의무(KO-4)는 BR-07 정적 스캔이, 시간 주입(KO-5)은 금지 심볼 스캔이, import 창구(KO-6)는 아키텍처 테스트가 막는다. 컴파일이 **단독** 강제 수단인 규칙은 모듈 경계 쪽의 MO-2다 — `port/`를 별도 빌드 모듈로 빼서 다른 컨텍스트의 `domain/`을 컴파일 단계에서 참조할 수 없게 만든 것이며, 그것은 타입이 아니라 **모듈 그래프**가 하는 일이다.

이것을 "Kotlin이 기대만 못하다"로 읽으면 틀린 독해다. 규약이 저 배치에 도달할 수 있었던 것 자체가 언어가 제공한 것 덕분이다 — 무엇이 컴파일에 걸리고 무엇이 걸리지 않는지를 **한 줄로 판정할 수 있었기 때문에** 나머지를 린트·테스트·리뷰로 정확히 배분할 수 있었다. Java에서 같은 표를 만들면 대부분의 칸이 "리뷰"가 된다.

그래서 이 언어를 쓰는 실질은 이렇게 요약된다. Kotlin은 규칙을 대신 지켜 주지 않는다. **어느 규칙이 언어로 지켜질 수 있고 어느 규칙이 그럴 수 없는지를 분명하게 만들어 준다.** 후자를 무엇이 막을지 정하는 일은 여전히 남고, 그 배분을 적어 둔 것이 [`dev-conventions.md`](../../../dev-conventions.md) §1과 §7이다.
