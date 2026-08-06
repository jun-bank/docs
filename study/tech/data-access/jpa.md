# JPA와 Hibernate — 영속성 컨텍스트라는 아이디어와 그 청구서

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 데이터 접근 결정 정본: [`architecture/adr/ADR-026-data-access.md`](../../../architecture/adr/ADR-026-data-access.md)).

이 문서는 JPA(Jakarta Persistence)와 그 구현체 Hibernate를 개념부터 설명한다. 순서는 하나의 논리를 따른다 — 무엇이 문제였나, 그 문제를 어떤 아이디어로 풀었나, 그 아이디어가 필연적으로 만드는 비용은 무엇인가. 더티체킹·지연 로딩·N+1 같은 이름들은 각각의 기능이 아니라 **"영속성 컨텍스트"라는 하나의 결정에서 갈라져 나온 결과**로 읽는 것이 이해가 빠르다. 인용한 스펙 문장은 Jakarta Persistence 3.1, Hibernate 문장은 ORM 6.6 문서 기준이다.

## 1. 문제 — 객체 그래프와 테이블 행은 같은 모양이 아니다

메모리 위의 객체는 참조로 연결된 그래프이고, 관계형 DB는 값(외래키)으로 연결된 행의 집합이다. Martin Fowler는 이 둘을 "데이터의 서로 꽤 다른 두 표현(two quite different representations of data)"이라 부르며, 메모리 구조가 훨씬 자유롭기 때문에 사람들이 그쪽으로 프로그래밍하고 싶어 한다고 정리한다([OrmHate](https://martinfowler.com/bliki/OrmHate.html)). 두 표현 사이를 오가는 층을 따로 두자는 것이 Data Mapper 패턴이다 — "객체와 DB 사이에서 데이터를 옮기되 서로를, 그리고 매퍼 자신을 모르게 유지하는 매퍼들의 층"([P of EAA: Data Mapper](https://martinfowler.com/eaaCatalog/dataMapper.html)).

손으로 매핑하던 시절의 부담은 변환 코드 자체가 아니라 그 주변의 부기(bookkeeping)였다. 같은 행을 두 경로에서 읽으면 서로 다른 객체 두 개가 생겨 한쪽 수정이 다른 쪽에서 보이지 않았고, 무엇이 바뀌었는지를 개발자가 기억해 UPDATE 문을 골라 써야 했으며, 그 순서와 시점도 사람이 정해야 했다. 이 부기를 라이브러리가 대신 하려면 **트랜잭션 동안 어떤 객체를 읽고 무엇을 바꿨는지 기억하는 자리**가 필요하다.

## 2. 아이디어 — 트랜잭션 동안 "관리되는 객체 집합"을 하나 둔다

그 자리가 영속성 컨텍스트(persistence context)이고, 개념적으로는 두 고전 패턴의 결합이다. Identity Map은 "각 객체가 한 번만 로드되도록 로드된 객체를 맵에 담아 두고, 참조할 때 그 맵을 먼저 본다"([P of EAA](https://martinfowler.com/eaaCatalog/identityMap.html)). Unit of Work는 "비즈니스 트랜잭션의 영향을 받은 객체 목록을 유지하고 변경분 기록과 동시성 문제 해결을 조율한다"([P of EAA](https://martinfowler.com/eaaCatalog/unitOfWork.html)).

스펙의 정의도 같은 말을 한다. Jakarta Persistence는 §7.1에서 영속성 컨텍스트를 "어떤 영속 엔티티 식별자에 대해서도 엔티티 인스턴스가 오직 하나만 존재하는 엔티티 인스턴스들의 집합"으로 규정한다([Jakarta Persistence 3.1](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html)). Hibernate는 이 집합을 Session이 들고 있는 1차 캐시라고 부른다 — "Session은 JDBC Connection을 감싸며 애플리케이션 도메인 모델의 대체로 'repeatable read'인 영속성 컨텍스트(1차 캐시)를 유지한다"([Hibernate User Guide 2.1](https://docs.hibernate.org/orm/6.6/userguide/html_single/Hibernate_User_Guide.html)).

여기서 나오는 보장이 동일성 보장이다. 같은 트랜잭션 안에서 같은 행을 두 번 조회하면 같은 자바 객체가 돌아온다. 1차 캐시는 성능 기능이기 이전에 **"한 행 = 한 객체"라는 규칙을 지키기 위한 장치**이고, 뒤에 나오는 기능 대부분이 이 규칙 위에 서 있다.

## 3. 생명주기 — 관리 대상은 객체가 아니라 객체의 상태다

영속성 컨텍스트가 생기면 객체는 "그 집합 안에 있는가"에 따라 성질이 달라진다. 스펙은 네 상태를 정의한다(§3.2): new는 "new 연산자로 막 생성되어 아직 영속성 컨텍스트와 연결되지 않은" 상태, managed는 "영속성 컨텍스트와 연결된" 상태, detached는 "관리하던 영속성 컨텍스트가 닫혀 분리된" 상태, removed는 "DB에서 제거되도록 표시된" 상태다. Hibernate 입문 가이드는 이 흐름을 "persist()와 remove()는 엔티티 생명주기의 시작과 끝을 긋는 것으로 볼 수 있다"고 요약한다([Hibernate Introduction](https://docs.hibernate.org/orm/6.6/introduction/html_single/Hibernate_Introduction.html)).

```kotlin
@Entity
class AccountEntity(
    @Id val id: Long,
    var balance: Long,
)

val fresh = AccountEntity(id = 1, balance = 0)   // new — DB와 무관한 객체
em.persist(fresh)                                // managed — 이제 컨텍스트가 추적한다
val found = em.find(AccountEntity::class.java, 1) // managed — fresh와 같은 인스턴스다
```

실무에서 헷갈리는 지점은 대부분 이 상태 축에 있다. "왜 저장이 안 되지"는 대개 detached 객체를 고친 것이고, "왜 저장했는데 값이 다르지"는 managed 객체를 나중에 또 고친 것이다. 객체를 보고 판단할 수 없고 **그 객체가 지금 어떤 컨텍스트 안에 있는지를 알아야** 판단할 수 있다는 점이, JPA를 처음 배울 때 가장 낯선 부분이다.

## 4. 더티체킹 — save()를 부르지 않았는데 UPDATE가 나가는 이유

managed 상태 객체의 필드를 바꾸면 별도 호출 없이 UPDATE가 실행된다. 구현은 단순하다 — 컨텍스트가 로드 시점의 스냅샷을 갖고 있다가 커밋 직전에 현재 값과 비교해 달라진 컬럼을 찾는다. 스펙은 결과만 규정한다: "flush 시점에 영속성 제공자는 영속 엔티티에 대한 모든 변경을 DB에 적용한다"(§3.2.4).

```kotlin
@Transactional
fun withdraw(id: Long, amount: Long) {
    val account = em.find(AccountEntity::class.java, id)
    account.balance -= amount     // 저장 호출 없음
}                                 // 커밋 시점에 UPDATE account SET balance = ? WHERE id = ?
```

이것이 Unit of Work가 약속한 편의의 실체이고, 동시에 첫 번째 청구서다. 저장 코드가 사라지면 **"어디서 DB에 쓰는가"라는 질문에 코드가 답하지 못한다** — 답은 "managed 객체를 만진 모든 곳"이 된다. Spring Data JDBC 팀이 이 기능을 뺀 이유로 든 것도 정확히 그 점이다("dirty tracking... obscures the single point where persistence operations execute", [Introducing Spring Data JDBC](https://spring.io/blog/2018/09/17/introducing-spring-data-jdbc)).

## 5. flush — "언제 SQL이 나가는가"가 별도 개념이 된다

변경을 모아 두었다가 나중에 쓰기로 한 순간, "모아 둔 것을 실제로 내보내는 시점"이 개념으로 승격된다. 그것이 flush이고, JPA는 두 모드를 정의한다(§3.3.1): AUTO는 트랜잭션 중 필요 시점마다 동기화하고, COMMIT은 커밋 때만 동기화한다. Hibernate는 여기에 ALWAYS와 MANUAL을 더해 네 가지를 제공한다([Hibernate User Guide 7. Flushing](https://docs.hibernate.org/orm/6.6/userguide/html_single/Hibernate_User_Guide.html)).

기본값 AUTO의 핵심 규칙은 하나다 — 커밋할 때, 그리고 **쿼리를 실행하기 직전에** 밀린 변경을 먼저 내보낸다. 이유는 정합성이다. 방금 메모리에서 바꾼 값을 반영하지 않은 채 JPQL을 실행하면 같은 트랜잭션 안에서 자기 변경을 못 보는 결과가 나오기 때문이다. 대가는 SQL 실행 순서가 코드 줄 순서와 일치하지 않는다는 것이다 — 조회 한 줄이 앞선 여러 UPDATE를 촉발할 수 있다.

이 타이밍은 성능 문제가 아니라 동시성·잠금 문제로 나타날 때 더 아프다. 어떤 행에 언제 잠금이 걸리는지가 flush 시점에 달려 있는데, 그 시점을 결정하는 것은 개발자가 쓴 문장이 아니라 프레임워크의 규칙이기 때문이다. 잠금 순서가 불변식의 일부인 도메인에서는 이 간접성이 그대로 위험이 된다.

## 6. 지연 로딩 — 그래프를 다 읽지 않으려는 프록시

애그리게이트를 통째로 다루려면 연관 객체도 함께 있어야 하는데, 참조를 따라 전부 읽으면 주문 하나 조회에 DB 절반이 딸려 온다. 해법이 지연 로딩이다 — 연관 필드에 프록시를 심어 두고, 실제로 그 필드를 건드릴 때 SELECT를 실행한다(Hibernate 5.6 "Proxies and lazy fetching", [Introduction](https://docs.hibernate.org/orm/6.6/introduction/html_single/Hibernate_Introduction.html)).

```kotlin
@Entity
class OrderEntity(
    @Id val id: Long,
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    val lines: MutableList<OrderLineEntity> = mutableListOf(),
)
```

프록시는 살아 있는 컨텍스트를 전제하므로, 컨텍스트가 닫힌 뒤 그 필드를 만지면 `LazyInitializationException`("could not initialize proxy - no Session")이 난다. 흔한 회피책인 Open Session in View에 대해 Vlad Mihalcea는 "DB 관점에서 매우 비효율적이므로 엔터프라이즈 애플리케이션에서 절대 쓰지 말라"고 못박고, 정석은 필요한 연관을 쿼리에서 명시적으로 가져오는 것(JOIN FETCH)이나 DTO 프로젝션이라고 말한다([The best way to handle the LazyInitializationException](https://vladmihalcea.com/the-best-way-to-handle-the-lazyinitializationexception/)). [실무 의견]

## 7. 비용 ① N+1 — 반복문이 SQL을 낳는다

지연 로딩의 대가가 가장 자주 드러나는 형태가 N+1이다. 정의는 "데이터 접근 프레임워크가, 주 쿼리 실행 시 함께 가져올 수 있었던 데이터를 위해 N개의 추가 SQL을 실행하는" 상황이다([Vlad Mihalcea, N+1 query problem](https://vladmihalcea.com/n-plus-1-query-problem/)). 각 쿼리는 빨라서 슬로우 쿼리 로그에 걸리지 않고, 합계만 느려진다는 점이 이 결함의 성질을 말해 준다.

```kotlin
val orders = em.createQuery("select o from OrderEntity o", OrderEntity::class.java).resultList
orders.forEach { it.lines.size }   // 주문 한 건마다 SELECT — 총 1 + N회
```

고치는 방법은 "가져올 것을 쿼리에서 말한다"로 수렴한다 — JPQL의 `join fetch`, 엔티티 그래프, 배치 페치, 그리고 애초에 엔티티가 아니라 필요한 컬럼만 뽑는 DTO 프로젝션이다(Hibernate User Guide의 association fetching·batch fetching·join fetching 절). 여기서 드러나는 구조가 중요하다 — **자동 로딩이 만든 문제를 수동 지시로 되돌리는 것**이 정석 해법이고, 그 지시가 늘어날수록 "SQL을 안 쓰기 위해 도입한 도구로 SQL 계획을 짜는" 상태에 가까워진다.

## 8. 비용 ② 숨은 SQL — 실행 시점이 코드에 없다

앞의 세 절은 서로 다른 결함이 아니라 한 설계의 세 얼굴이다. 더티체킹은 쓰기 지점을 감추고, flush는 실행 시점을 감추며, 지연 로딩은 읽기 지점을 감춘다. 감춘 대가로 얻은 것은 진짜다 — 그래프 저장 코드와 부기가 사라진다. Fowler의 균형 잡힌 평가가 이 지점을 잘 요약한다: "ORM은 매핑 문제의 80~90%를 처리할 수 있지만, 마지막 덩어리는 관계형 DB를 정말 이해하는 누군가의 조심스러운 작업이 늘 필요하다"([OrmHate](https://martinfowler.com/bliki/OrmHate.html)).

문제는 나머지 10~20%가 균등하게 흩어져 있지 않다는 것이다. 그 구간은 대체로 동시성·잠금·조건부 갱신·대량 조회에 몰려 있고, 이 프로젝트의 쓰기 경로가 정확히 그 모양이다(정본: ADR-026 §1 — 멱등 판정·배포 창 락·fencing token·전표 원자성). 낙관적 잠금(`@Version`)처럼 JPA가 표준으로 제공하는 통제 수단도 있지만, "이 UPDATE가 이 조건에서만 성립해야 한다"를 표현하려면 결국 명시 쿼리로 내려가게 된다.

## 9. 정리 — JPA가 값을 내는 자리와 어긋나는 자리

JPA는 "객체 그래프를 통째로 다루고 싶다"는 요구에 맞춰 설계된 도구다. 그래프가 깊고, 화면·유스케이스마다 다른 부분을 오가며 고치고, 각 쓰기가 특별한 동시성 조건을 요구하지 않는 도메인에서 더티체킹과 지연 로딩은 실제로 코드를 크게 줄인다. 이때 감춰진 SQL은 비용이 아니라 목적이다.

반대로 쓰기 하나하나가 "이 조건이 참일 때만 이 행을 이렇게 바꾼다"인 도메인에서는 얻는 것이 적고 감춰진 축만 늘어난다. 이 프로젝트가 그 판단으로 Data JDBC를 골랐고 JPA는 도입 조건과 함께 잠갔다(정본: ADR-026 D1·D4 — 재판정은 그 문서에서 한다). 그다음 문서인 [`spring-data-jdbc.md`](spring-data-jdbc.md)는 같은 문제를 정반대 방향에서 푼 도구를 다루고, [`comparison.md`](comparison.md)가 둘을 축별로 비교한다.
