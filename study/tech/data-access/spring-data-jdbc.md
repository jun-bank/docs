# Spring Data JDBC — 애그리게이트 경계를 저장 경계로 삼는 도구

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 데이터 접근 결정 정본: [`architecture/adr/ADR-026-data-access.md`](../../../architecture/adr/ADR-026-data-access.md)).

이 문서는 Spring Data JDBC를 설계 철학부터 설명한다. 이 도구는 "JPA에서 기능을 뺀 가벼운 버전"이 아니라 **뺀 것 자체가 설계 목표인 도구**여서, 기능 목록을 먼저 보면 오히려 이해가 안 된다. 순서는 무엇에 대한 반작용인지, 그 반작용을 지탱하는 경계 개념(애그리게이트)이 무엇인지, 실제 코드가 어떻게 생겼는지, 그 대가로 무엇을 직접 써야 하는지다. 인용은 Spring Data Relational 공식 레퍼런스와 저자 Jens Schauder의 spring.io 블로그 원문 기준이다.

## 1. 출발점 — JPA의 세 가지를 의도적으로 뺀다

Schauder는 도입 글에서 목적을 한 문장으로 밝힌다: "Spring Data JDBC의 아이디어는 JPA의 복잡성에 굴복하지 않으면서 관계형 DB에 접근하는 것"이다([Introducing Spring Data JDBC](https://spring.io/blog/2018/09/17/introducing-spring-data-jdbc)). 뺀 것은 세 가지 — 예상치 못한 비싼 쿼리나 예외를 유발하는 지연 로딩, 같은 엔티티의 여러 버전 비교를 어렵게 만드는 캐싱, 영속 연산이 일어나는 단일 지점을 흐리는 더티 트래킹이다. 세션과 엔티티 프록시라는 개념 자체도 없앴다.

공식 레퍼런스의 "Why Spring Data JDBC?"는 같은 내용을 사용자 관점의 두 문장으로 요약한다. "엔티티를 로드하면 SQL이 실행된다. 그것이 끝나면 완전히 로드된 엔티티를 갖는다. 지연 로딩도 캐싱도 없다." 그리고 "엔티티를 저장하면 저장된다. 저장하지 않으면 저장되지 않는다. 더티 트래킹도 세션도 없다"([Why Spring Data JDBC?](https://docs.spring.io/spring-data/relational/reference/jdbc/why.html)).

이 선택의 대가는 명확하다. 편의를 잃는 대신 얻는 것은 **"SQL은 리포지토리 메서드를 호출할 때, 오직 그때만 실행된다"**는 성질이고([Introducing Spring Data JDBC](https://spring.io/blog/2018/09/17/introducing-spring-data-jdbc)), 그래서 코드를 읽는 것과 DB에 무슨 일이 일어나는지 아는 것이 같은 일이 된다. jpa.md에서 본 세 가지 청구서(숨은 쓰기 지점·flush 타이밍·숨은 읽기)가 한꺼번에 사라지는 대신, 뒤에 나올 §8의 비용이 생긴다.

## 2. 경계 — 애그리게이트가 곧 저장 단위다

기능을 뺀 자리를 무엇으로 지탱하는가가 이 도구의 본론이고, 답은 DDD의 애그리게이트다. Fowler의 정의는 "단일 단위로 다룰 수 있는 도메인 객체들의 묶음"이며, 핵심은 두 문장이다 — "애그리게이트는 데이터 저장 전송의 기본 단위다. 로드하거나 저장할 때 애그리게이트 전체를 요청한다"와 "트랜잭션은 애그리게이트 경계를 넘지 않아야 한다"([DDD_Aggregate](https://martinfowler.com/bliki/DDD_Aggregate.html)). Vaughn Vernon은 여기에 설계 규칙을 더한다 — 진짜 불변식을 일관성 경계 안에 모델링할 것, 애그리게이트를 작게 유지할 것, 다른 애그리게이트는 식별자로 참조할 것, 애그리게이트 간 갱신은 최종 일관성으로 처리할 것([Effective Aggregate Design Part I](https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_1.pdf)).

Spring Data JDBC는 이 개념을 문서가 아니라 런타임 규칙으로 채택했다. 레퍼런스는 애그리게이트를 "그것에 대한 원자적 변경들 사이에 일관성이 보장되는 엔티티들의 묶음"으로 정의하고, "각 애그리게이트는 정확히 하나의 애그리게이트 루트를 가지며, 애그리게이트는 그 루트의 메서드를 통해서만 조작된다"고 못박는다. 저장 측 규칙은 더 직접적이다 — "애그리게이트 루트로부터 도달 가능한 모든 엔티티는 그 애그리게이트 루트의 일부로 간주된다"([Domain-Driven Design and Relational Databases](https://docs.spring.io/spring-data/relational/reference/jdbc/domain-driven-design.html)).

그래서 이 도구에서 "무엇을 하나의 클래스 그래프로 묶을 것인가"는 매핑 취향이 아니라 트랜잭션 설계다. 도달 가능성이 곧 저장 범위이므로, 애그리게이트를 크게 잡으면 매번 그만큼을 통째로 쓰게 되고, 작게 잡으면 그 경계 밖의 일관성은 다른 수단으로 지켜야 한다. 리포지토리는 애그리게이트 루트마다 하나 둔다.

## 3. 참조는 두 종류 — 안쪽은 객체, 바깥쪽은 식별자

경계 규칙이 코드에 나타나는 형태는 참조의 이분법이다. Schauder는 "애그리게이트 루트에서 비-transient 참조를 따라 도달할 수 있는 모든 것은 애그리게이트의 일부"라고 정의한 뒤, DDD 원칙을 적용해 결론을 낸다 — "여러 애그리게이트가 같은 엔티티를 참조한다면 그 엔티티는 그것들을 참조하는 애그리게이트의 일부일 수 없다." 따라서 "모든 Many-to-One과 Many-to-Many 관계는 id를 참조하는 것만으로 모델링되어야 한다"([Spring Data JDBC, References, and Aggregates](https://spring.io/blog/2018/09/24/spring-data-jdbc-references-and-aggregates)).

```kotlin
// 애그리게이트 루트 — 내부 엔티티는 객체로 들고 있다
data class Order(
    @Id val id: Long? = null,
    val status: String,
    val lines: Set<OrderLine> = emptySet(),   // order_line 테이블, Order와 함께 저장·삭제된다
    val cardId: Long,                          // 다른 애그리게이트 — 식별자만 (객체 참조 금지)
)

data class OrderLine(val sku: String, val quantity: Int)

interface OrderRepository : CrudRepository<Order, Long>
```

이 규칙의 결과는 삭제 동작에서 가장 선명하다. 애그리게이트를 지우면 도달 가능한 것들이 함께 지워지고, id로만 참조된 것은 남는다. 애그리게이트 간 참조에 대해 레퍼런스가 붙이는 단서도 같은 맥락이다 — "애그리게이트를 가로지르는 참조는 항상 일관적임이 보장되지 않는다. 결국에는 일관되어짐이 보장될 뿐이다"([Domain-Driven Design and Relational Databases](https://docs.spring.io/spring-data/relational/reference/jdbc/domain-driven-design.html)).

## 4. 사용 모습 ① 저장 — save()가 전부이고, 그 안은 delete 후 insert다

쓰기 API는 하나다. `save()`를 부르면 애그리게이트 전체가 DB에 반영되고, 부르지 않으면 아무 일도 일어나지 않는다. 레퍼런스가 밝히는 내부 동작은 다음과 같다 — 새 애그리게이트면 "루트에 대한 insert 후, 직접·간접으로 참조된 모든 엔티티에 대한 insert"가 실행되고, 기존 애그리게이트면 "참조된 엔티티들이 전부 삭제되고, 루트가 update되고, 참조된 엔티티들이 다시 insert된다"([Persisting Entities](https://docs.spring.io/spring-data/relational/reference/jdbc/entity-persistence.html)).

```kotlin
@Transactional
fun addLine(orderId: Long, line: OrderLine) {
    val order = orders.findById(orderId).orElseThrow()
    orders.save(order.copy(lines = order.lines + line))   // 이 호출에서만 SQL이 나간다
}
```

이 구현은 문서가 스스로 인정하는 낭비를 동반한다. "참조된 엔티티 중 실제로 바뀐 것이 몇 개뿐이라면 삭제 후 삽입은 낭비다. 개선될 수 있고 아마 개선되겠지만 한계가 있다 — Spring Data JDBC는 애그리게이트의 이전 상태를 알지 못한다"(같은 문서). 이전 상태를 기억하지 않기로 한 결정(세션·캐시 없음)의 직접적인 대가이고, **애그리게이트를 작게 잡으라는 Vernon의 규칙이 여기서는 성능 규칙이 된다.**

새 것인지 기존 것인지의 판정은 `@Id` 속성으로 한다. 식별자가 비어 있으면 새 애그리게이트로 보므로, Kotlin에서는 위 예시처럼 `val id: Long? = null`을 두는 형태가 기본이다. 레퍼런스는 제약 하나를 덧붙인다 — "엔티티를 저장한 뒤에는 그 엔티티가 더 이상 새 것이어서는 안 된다".

## 5. 사용 모습 ② 조건부 상태 전이 — 쿼리를 직접 쓴다

애그리게이트 통째 저장으로 표현되지 않는 쓰기가 있다. "점유자가 없을 때만 내 식별자로 바꾼다", "이미 처리했으면 다시 처리하지 않는다" 같은 조건부 전이는 읽고-판단하고-저장하는 사이에 경쟁이 끼어들 수 있어, 단일 UPDATE 문의 WHERE 절로 표현해야 원자성이 성립한다. Spring Data JDBC에서는 `@Query`에 `@Modifying`을 붙여 쓰고, 반환 타입은 `void`·`int`(영향 행 수)·`boolean`(갱신 여부) 중 고른다([Query Methods](https://docs.spring.io/spring-data/relational/reference/jdbc/query-methods.html)).

```kotlin
interface CaptureBatchRepository : CrudRepository<CaptureBatchRow, Long> {

    @Modifying
    @Query("""
        UPDATE capture_batch SET owner = :owner, leased_until = :until
        WHERE id = :id AND (owner IS NULL OR leased_until < :now)
    """)
    fun acquireLease(id: Long, owner: String, until: Instant, now: Instant): Boolean
}
```

메서드 이름으로 쿼리를 파생하는 기능도 있지만 범위가 좁다 — 애그리게이트 루트에 직접 있는 단순 속성에 한정되고, 조인이 필요한 조회나 update·delete는 파생되지 않는다(같은 문서). 즉 이 도구에서 이름 기반 파생은 편의 기능이고, **쓰기의 본체는 사람이 쓴 SQL이 맡는다.** 조건부 UPDATE가 코드에 그대로 보이는 것이 이 프로젝트에서는 요구사항이었다(정본: ADR-026 D1).

`@Modifying` 쿼리에는 단서가 하나 붙는다. 엔티티 콜백과 생명주기 이벤트를 건너뛰므로 감사(auditing) 애노테이션이 자동 갱신되지 않는다(같은 문서) — 명시 쿼리로 내려간 경로에서는 그런 부가 기능도 함께 내려놓는다고 이해하면 된다.

## 6. 사용 모습 ③ 조회 — 애그리게이트를 재구성하지 않는다

목록·집계·커서 조회는 애그리게이트를 통째로 읽어 화면 모양으로 접는 방식과 맞지 않는다. 필요한 것은 여러 테이블에서 몇 개 컬럼만 뽑은 평평한 행이지 도메인 객체가 아니기 때문이다. Spring Data JDBC는 이 층을 자기가 대신 해 주려 하지 않으므로, 조회는 `JdbcClient`(Spring Framework 6.1부터의 통합 클라이언트)나 `JdbcTemplate`으로 직접 쓴다([Spring Framework — JDBC core](https://docs.spring.io/spring-framework/reference/data-access/jdbc/core.html)).

```kotlin
data class OrderSummary(val id: Long, val status: String, val lineCount: Int)

fun page(afterId: Long, size: Int): List<OrderSummary> =
    jdbcClient.sql("""
        SELECT o.id, o.status, count(l.order) AS line_count
        FROM "order" o LEFT JOIN order_line l ON l.order = o.id
        WHERE o.id > :afterId GROUP BY o.id, o.status ORDER BY o.id LIMIT :size
    """)
        .param("afterId", afterId).param("size", size)
        .query(OrderSummary::class.java).list()
```

이 분리는 JPA 진영에서도 최종적으로 권장되는 형태와 같다 — 앞 문서에서 본 DTO 프로젝션이 그것이다. 차이는 시점이다. JPA에서는 성능 문제가 드러난 뒤 엔티티 조회에서 프로젝션으로 내려가지만, 여기서는 조회가 처음부터 별도 층이다(이 프로젝트의 결정도 같다 — 정본: ADR-026 D2).

## 7. 동시성 — 낙관적 잠금은 있고, 그 이상은 SQL로 쓴다

애그리게이트 단위 저장에도 경쟁은 있다. 읽어서 고친 뒤 저장하는 사이에 다른 트랜잭션이 같은 애그리게이트를 바꿨다면 마지막 쓰기가 앞의 변경을 덮는다. Spring Data JDBC는 숫자형 `@Version` 속성으로 이를 막는다 — "애그리게이트 루트에 대한 update 문은 DB에 저장된 버전이 실제로 변하지 않았음을 검사하는 where 절을 포함하고", 그렇지 않으면 `OptimisticLockingFailureException`이 발생하며, 버전 값은 엔티티와 DB 양쪽에서 증가한다([Persisting Entities](https://docs.spring.io/spring-data/relational/reference/jdbc/entity-persistence.html)).

비관적 잠금(`SELECT ... FOR UPDATE`)이나 fencing token 검사처럼 조건이 더 구체적인 통제는 프레임워크 기능이 아니라 명시 쿼리로 쓴다. 이것이 이 도구의 일관된 태도다 — **동시성 통제를 프레임워크가 추상화하지 않고 SQL 표면에 남겨 둔다.** 통제 수단이 적은 것이 아니라, 통제가 코드에 드러나 있어야 리뷰와 실험(잠금 실험 같은)이 가능하다는 쪽에 선 것이다.

## 8. 한계 — 무엇을 직접 써야 하는지 알고 고른다

첫째, 깊은 객체 그래프의 자동 영속이 필요하면 이 도구는 맞지 않는다. 애그리게이트가 커질수록 매번 delete 후 insert하는 비용과 매핑 코드가 함께 늘고, 그 지점이 바로 JPA가 값을 내기 시작하는 지점이다(이 프로젝트는 그 상황을 JPA 도입 조건으로 잠가 두었다 — 정본: ADR-026 D4).

둘째, 매핑 커스터마이징 여지가 작다. 레퍼런스가 직접 말한다 — "엔티티를 테이블에 매핑하는 단순한 모델이 있다. 아마 꽤 단순한 경우에만 통할 것이다. 마음에 들지 않으면 자신의 전략을 코딩해야 한다. Spring Data JDBC는 애노테이션으로 전략을 커스터마이징하는 지원을 아주 제한적으로만 제공한다"([Why Spring Data JDBC?](https://docs.spring.io/spring-data/relational/reference/jdbc/why.html)).

셋째, 조회 모델과 그 매핑 코드는 전부 직접 쓴다(§6). 넷째, 애그리게이트 간 참조를 id로만 두므로 여러 애그리게이트를 걸친 일관성은 도구가 아니라 설계로 지켜야 한다 — 트랜잭션 경계를 어디에 그을지, 어디를 최종 일관성으로 둘지를 사람이 정해야 한다. [실무 의견] 자료·튜토리얼·스택오버플로 축적량이 JPA에 비해 훨씬 적어서, 낯선 문제를 만났을 때 검색으로 해결되는 비율이 낮다는 점도 실제로는 비용이다.

## 9. 정리 — 규칙이 적고, 그 규칙이 도메인 개념과 같다

Spring Data JDBC를 한 문장으로 줄이면 "애그리게이트 경계를 저장 경계로 삼고, 그 밖의 모든 것은 명시 SQL로 남긴 도구"다. 배울 개념은 세 개뿐이다 — 애그리게이트 루트, `save()`가 하는 일, 그리고 나머지는 직접 쓴다는 것. 감춰진 동작이 없으므로 코드를 읽으면 SQL이 보이고, 그 대신 편의는 없다.

이 성질이 어떤 도메인에서 유리하고 어떤 도메인에서 불리한지, 그리고 이 프로젝트가 왜 이 쪽을 골랐는지는 [`comparison.md`](comparison.md)에서 축별로 비교한다. JPA 쪽 개념이 아직 흐리면 [`jpa.md`](jpa.md)를 먼저 읽는 편이 낫다 — 이 도구의 설계는 그쪽 개념을 알아야 "왜 뺐는가"가 읽힌다.
