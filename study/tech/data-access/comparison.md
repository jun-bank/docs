# JPA vs Spring Data JDBC — 축별 비교와 이 프로젝트의 선택

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 데이터 접근 결정 정본: [`architecture/adr/ADR-026-data-access.md`](../../../architecture/adr/ADR-026-data-access.md)).

이 문서는 두 도구를 다섯 축(SQL 가시성·동시성 통제·학습 곡선·생태계·적합 도메인)으로 비교하고, 마지막에 값 비교표 하나로 요약한다. 비교의 결론을 먼저 말하면 이렇다 — **어느 쪽이 우수한지가 아니라 "쓰기 경로가 그래프 저장이냐 상태 전이냐"가 선택을 가른다.** 개념 설명은 [`jpa.md`](jpa.md)와 [`spring-data-jdbc.md`](spring-data-jdbc.md)에 있고, 여기서는 그 개념들이 실제 선택에서 어떻게 부딪히는지만 다룬다. 마지막 두 절은 이 프로젝트의 결정 요지(정본 인용)와 JPA를 따로 공부할 때의 원 출처 경로다.

## 1. 두 도구는 같은 문제를 풀지 않는다

JPA는 "객체 그래프와 테이블의 불일치"를 푸는 도구다. 영속성 컨텍스트가 트랜잭션 동안 객체를 추적하고, 더티체킹이 변경분을 찾아내고, 지연 로딩이 그래프를 필요한 만큼만 읽는다. 이 세 기능은 서로를 전제하므로 따로 떼어 평가할 수 없고, 셋을 합쳐 얻는 것은 "저장 코드를 쓰지 않는 상태"다.

Spring Data JDBC는 "애그리게이트를 통째로 저장·로드한다"는 DDD 규칙을 그대로 구현한 도구다. 저장 단위가 애그리게이트로 고정되어 있으니 추적할 것이 없고, 그래서 세션·캐시·더티 트래킹이 필요 없다 — "엔티티를 저장하면 저장된다. 저장하지 않으면 저장되지 않는다"([Why Spring Data JDBC?](https://docs.spring.io/spring-data/relational/reference/jdbc/why.html)). 대신 애그리게이트로 표현되지 않는 쓰기와 모든 조회는 사람이 SQL로 쓴다.

그래서 비교의 첫 질문은 기능 비교가 아니다. 내 도메인의 쓰기가 "그래프를 고쳐 저장하는 일"에 가까운가, "조건이 참일 때만 행을 바꾸는 일"에 가까운가 — 이 질문의 답이 아래 다섯 축의 값을 대부분 결정한다.

## 2. SQL 가시성 — 언제 무엇이 실행되는지 코드가 답하는가

JPA에서 SQL의 실행 시점은 코드 줄과 어긋난다. 필드 대입이 커밋 시점의 UPDATE가 되고(더티체킹), 조회 한 줄이 밀린 변경들을 먼저 밀어내며(AUTO flush), 연관 필드 접근이 SELECT를 낳는다(지연 로딩). 이 간접성은 결함이 아니라 설계 목표였고, 잘 맞는 도메인에서는 그만큼의 코드를 지워 준다.

Spring Data JDBC에서는 그 관계가 1:1이다 — "SQL 문은 리포지토리 메서드를 호출할 때, 오직 그때만 실행된다"([Introducing Spring Data JDBC](https://spring.io/blog/2018/09/17/introducing-spring-data-jdbc)). 얻는 것은 실행 순서를 코드로 재구성할 수 있다는 성질이고, 이것은 성능보다 재현성과 리뷰 가능성 쪽에서 값을 낸다. 잠금 실험처럼 "어느 순간에 어떤 문장이 나갔는가"가 곧 검증 대상인 작업에서는 이 축이 결정적이다.

가시성의 대가는 분량이다. 조회 SQL과 행-객체 매핑을 전부 손으로 쓰므로 코드량이 늘고, 스키마가 바뀌면 고칠 자리가 여러 곳이다. 반대로 JPA는 그 분량을 줄이는 대신, 문제가 생겼을 때 "왜 이 쿼리가 여기서 나갔는가"를 프레임워크 규칙으로 되짚어야 한다.

## 3. 동시성 통제 — 낙관적 잠금은 둘 다, 조건부 UPDATE는 결이 다르다

버전 컬럼 기반 낙관적 잠금은 양쪽 모두 표준 기능이다. JPA는 `@Version`을, Spring Data JDBC도 숫자형 `@Version` 속성을 지원해 update의 where 절로 버전 불변을 검사하고 실패 시 `OptimisticLockingFailureException`을 던진다([Persisting Entities](https://docs.spring.io/spring-data/relational/reference/jdbc/entity-persistence.html)). 이 축만 보면 차이가 없다.

차이는 그 밖의 통제에서 나온다. "점유자가 없을 때만 획득", "토큰이 최대값 미만이면 거부" 같은 조건부 전이는 조건을 UPDATE의 where 절에 넣어 영향 행 수로 성패를 판정해야 원자적이다. Spring Data JDBC에서는 이것이 자연스러운 사용법이고(`@Modifying` + `@Query`), JPA에서도 같은 방식이 가능하지만 그 순간 영속성 컨텍스트 밖으로 나가게 되어 도구의 장점이 소멸한다 — 벌크 쿼리는 컨텍스트에 반영되지 않으므로 컨텍스트와 DB가 어긋나지 않도록 개발자가 따로 신경 써야 한다.

한 가지는 분명히 해 둘 필요가 있다. **동시성 안전은 어느 프레임워크도 주지 않는다** — 제약·행 잠금·조건부 갱신 같은 DB 수준 장치가 최종 방어선이고, 프레임워크는 그것을 편하게 부르거나 가려 놓거나 할 뿐이다. 이 프로젝트가 방어선을 컴파일·테스트·DB 세 층으로 못박은 것도 같은 인식이다(정본: ADR-026 D3).

## 4. 학습 곡선 — 진입은 JPA가 쉽고, 숙달은 JPA가 훨씬 비싸다

처음 며칠은 JPA가 압도적으로 편하다. 엔티티에 애노테이션 몇 개를 붙이면 CRUD가 돌고, 연관을 객체 참조로 그냥 쓸 수 있으며, 스키마 자동 생성으로 DB 설계를 미룰 수도 있다. 반대로 Spring Data JDBC는 시작부터 테이블을 만들고 조회 SQL을 써야 하므로 첫 화면까지의 거리가 멀다.

그 관계는 몇 주 안에 뒤집힌다. JPA에서 실제로 배워야 하는 것은 애노테이션이 아니라 영속성 컨텍스트의 동작 모델 — 생명주기 네 상태, flush 모드와 쿼리 전 flush, 프록시와 초기화 시점, 페치 전략, 벌크 연산과 컨텍스트의 불일치, 2차 캐시 — 이고, 이 모델을 모르면 증상만 보고는 원인을 짚을 수 없다. Spring Data JDBC 쪽에서 배울 모델은 애그리게이트 경계와 `save()`의 동작, 그리고 SQL 자체다.

[실무 의견] 그래서 두 도구의 난이도는 "무엇을 이미 아는가"에 달려 있다. SQL과 트랜잭션·잠금을 아는 사람에게 Spring Data JDBC는 거의 배울 것이 없고, 반대로 JPA는 SQL을 몰라도 시작할 수 있게 해 주지만 결국 SQL과 프레임워크 모델을 둘 다 알아야 하는 지점으로 데려간다. 학습 목적이라면 어느 쪽을 먼저 하든 SQL을 건너뛸 수는 없다는 것이 실무의 공통된 조언이다.

## 5. 생태계 — 실무 표준은 여전히 JPA다

[실무 의견] 자바 백엔드 채용과 기존 코드베이스의 절대 다수가 Spring Data JPA를 쓴다. 그 결과 축적된 자료·튜토리얼·질문답변·튜닝 노하우의 양이 Spring Data JDBC와 비교가 되지 않고, QueryDSL 같은 주변 도구, 팀 내에 경험자가 있을 확률, 낯선 문제를 검색으로 해결할 확률이 모두 JPA 쪽에서 높다. 도구 선택은 기술적 적합성만의 문제가 아니므로 이 축은 실제로 무게가 있다.

반대 방향의 사실도 있다. Spring Data JDBC는 별도 라이브러리가 아니라 Spring Data 계열의 일부여서 새 의존을 추가하지 않고, 개념이 적어 팀에 새로 들어온 사람에게 설명할 것도 적다. 학습 자산 측면에서는 두 축이 충돌한다 — 프로젝트에서 안 쓰는 기술의 실무 경험은 쌓이지 않는다.

[불확실] 두 도구의 실제 채택 비율을 이 문서에서 수치로 확인하지는 않았다. 위 진술은 공개 통계가 아니라 통용되는 관찰에 기댄 것이므로, 수치가 필요한 자리에서는 별도 근거를 찾아야 한다.

## 6. 적합 도메인 — 쓰기 경로의 모양이 가른다

JPA가 유리한 곳은 그래프가 깊고 편집이 잦은 도메인이다. 여러 화면이 같은 애그리게이트의 다른 부분을 오가며 고치고, 각 쓰기에 특별한 동시성 조건이 없으며, 조회도 대체로 도메인 객체 모양이면 더티체킹과 지연 로딩이 코드를 크게 줄인다. 사내 업무 시스템·CMS·설정 관리처럼 "폼을 열어 고치고 저장한다"가 주된 흐름인 곳이 전형이다.

Spring Data JDBC가 유리한 곳은 쓰기가 상태 전이인 도메인이다. 금융 원장, 재고 차감, 예약 좌석, 잡 스케줄러처럼 "조건이 참일 때만 바뀐다"와 "무엇이 언제 실행되는가"가 불변식의 일부인 경우, 감춰진 실행 시점은 곧 검증 불가능한 구간이 된다. 조회가 목록·집계·커서 중심이어서 애초에 애그리게이트 재구성이 필요 없는 시스템도 여기에 속한다.

경계에 있는 경우가 물론 많다. 그럴 때 유용한 판정 질문은 "이 시스템의 어려운 부분이 매핑인가, 동시성인가"다 — 매핑이 어려우면 JPA가 그 80~90%를 가져가 주고([OrmHate](https://martinfowler.com/bliki/OrmHate.html)), 동시성이 어려우면 JPA가 가져가 주는 부분이 없으면서 축만 하나 늘어난다.

## 7. 값 비교표

아래 표는 앞의 다섯 축에서 확인한 사실을 한 칸에 한 값으로 요약한 것이다. 판단의 근거는 앞 절들에 있고, 표는 기억을 되살리는 용도다.

| 축 | JPA (Hibernate) | Spring Data JDBC |
|---|---|---|
| SQL 실행 시점 | flush 규칙이 결정 | 리포지토리 호출 시점 |
| 변경 저장 | 더티체킹 자동 | 명시 `save()` |
| 저장 단위 | 엔티티 단위 + 캐스케이드 | 애그리게이트 통째 |
| 기존 애그리게이트 갱신 | 바뀐 컬럼만 UPDATE | 참조 엔티티 삭제 후 재삽입 |
| 연관 로딩 | 지연 로딩(프록시) | 없음, 항상 완전 로드 |
| 1차 캐시·동일성 보장 | 있음 | 없음 |
| 낙관적 잠금 | `@Version` | `@Version` |
| 조건부 UPDATE | 가능하나 컨텍스트 밖 | 기본 사용법(`@Modifying`) |
| 조회 전용 모델 | 선택(DTO 프로젝션) | 필수(JdbcClient·JdbcTemplate) |
| 스키마 자동 생성 | 지원 | 없음 |
| 배울 핵심 개념 | 컨텍스트·생명주기·flush·페치 | 애그리게이트 경계·`save()` |

## 8. 우리 프로젝트는 왜 Data JDBC인가 — ADR-026 요지

이 절은 [`ADR-026`](../../../architecture/adr/ADR-026-data-access.md)의 요지를 옮긴 것이다 — 정본은 그 문서이고, 여기서 재판정하지 않는다. 맥락은 §1의 한 문장으로 요약된다: 이 도메인의 쓰기는 "객체 그래프 저장"이 아니라 "조건부 상태 전이"이며, 멱등 판정·배포 창 락·fencing token·전표의 한 커밋 원자성이 모두 조건부 UPDATE와 행 잠금으로 표현되고 "언제 어떤 SQL이 실행되는가"가 불변식의 일부다. 게다가 도메인 엔티티와 영속 엔티티를 분리했기 때문에(정본: ADR-002) 더티체킹을 쓸 수 없어, JPA를 골라도 사실상 Data JDBC의 사용 패턴이 되면서 무거운 런타임만 얹게 된다.

결정은 네 가지다. 쓰기는 Spring Data JDBC로 애그리게이트 단위 영속과 명시 `save()`를 쓰고 조건부 전이는 `@Modifying` 명시 쿼리로 한다(D1). 조회는 처음부터 명시 쿼리(JdbcClient/JdbcTemplate)와 조회 전용 모델로 간다 — "성능 문제가 생기면 내려간다"가 아니라 시작부터 그 층이다(D2). 무결성·안정성의 방어선은 컴파일(값 타입)·테스트(계약·불변식)·DB(제약·조건부 UPDATE·행 잠금) 세 층이며 영속성 프레임워크가 아니다(D3). JPA는 불도입하되 도입 조건과 함께 잠근다 — 복잡한 객체 그래프의 자동 영속이 실증적으로 필요해질 때(2회 이상 실측) 전면 교체가 아니라 해당 애그리게이트의 adapter만 교체한다(D4).

감수한 대가도 그 문서가 명시한다. 조회 전용 모델과 매핑 코드를 직접 쓰는 초기 비용, JPA 생태계의 편의(스키마 자동 생성 등)를 안 쓰는 것 — 스키마는 어차피 Flyway가 정본이다 —, 그리고 실무 표준 JPA 경험이 이 프로젝트 밖으로 미뤄진다는 학습 축의 손실이다. **이 문서 시리즈가 존재하는 이유가 마지막 항목이다.**

## 9. JPA를 배우려면 무엇을 보라 — 원 출처 경로

순서를 하나 권한다. 먼저 패턴 정의로 개념의 뿌리를 잡는다 — [Unit of Work](https://martinfowler.com/eaaCatalog/unitOfWork.html), [Identity Map](https://martinfowler.com/eaaCatalog/identityMap.html), [Data Mapper](https://martinfowler.com/eaaCatalog/dataMapper.html) 세 페이지는 각각 몇 문단이고, 영속성 컨텍스트가 무엇의 구현인지를 알고 나면 나머지가 훨씬 빨리 읽힌다. 균형을 위해 [OrmHate](https://martinfowler.com/bliki/OrmHate.html)를 함께 읽으면 ORM 비판을 어디까지 받아들일지 기준이 선다.

그다음이 스펙과 구현 문서다. [Jakarta Persistence 3.1 스펙](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html)에서 §3(엔티티 생명주기·flush 모드)과 §7(영속성 컨텍스트)만 읽어도 용어의 정확한 정의가 잡히고, 스펙 문장은 짧아서 실제로 읽을 만하다. 구현 쪽은 [Hibernate Introduction 가이드](https://docs.hibernate.org/orm/6.6/introduction/html_single/Hibernate_Introduction.html)를 통독한 뒤, [Hibernate User Guide](https://docs.hibernate.org/orm/6.6/userguide/html_single/Hibernate_User_Guide.html)에서 flushing·proxies and lazy fetching·entity graphs·association fetching·batch fetching·join fetching 절을 집중해 보는 것이 효율이 좋다.

[실무 의견] 마지막은 성능·함정 영역이고, 여기서는 Vlad Mihalcea의 글이 사실상 표준 참고 자료다 — [N+1 query problem](https://vladmihalcea.com/n-plus-1-query-problem/)과 [LazyInitializationException 다루기](https://vladmihalcea.com/the-best-way-to-handle-the-lazyinitializationexception/)가 출발점으로 적당하고, 같은 저자의 책 『High-Performance Java Persistence』가 깊이 있는 후속이다. 대조군으로 Spring Data JDBC 쪽 원문 두 편([Introducing Spring Data JDBC](https://spring.io/blog/2018/09/17/introducing-spring-data-jdbc), [References and Aggregates](https://spring.io/blog/2018/09/24/spring-data-jdbc-references-and-aggregates))과 DDD 애그리게이트 원문([Fowler](https://martinfowler.com/bliki/DDD_Aggregate.html), [Vernon](https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_1.pdf))을 함께 두면, JPA의 기능들을 "무엇을 위해 감췄는가"라는 질문과 함께 읽게 된다.

실습 제안 하나로 마친다. 같은 작은 도메인(주문과 주문 항목)을 두 도구로 각각 구현하고 SQL 로그를 켜서 비교해 보면, 이 문서 전체가 두 시간 만에 몸으로 이해된다 — 특히 항목 하나를 추가할 때 JPA는 INSERT 한 줄, Spring Data JDBC는 DELETE 후 재삽입이 나가는 장면이 두 설계의 차이를 그대로 보여 준다.
