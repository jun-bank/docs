# 03. PostgreSQL RLS (Row Level Security)

> 한 줄 정의: **`WHERE tenant_id = ?`를 빼먹은 쿼리도 DB가 대신 걸러준다.**
> 애플리케이션의 실수를 데이터베이스가 최종 방어하는 구조.

---

## 1. 왜 필요한가

멀티테넌시에서 테넌트 격리를 애플리케이션 코드에만 맡기면, **개발자가 조건 하나를 빠뜨리는 순간 다른 회사 데이터가 노출된다.** 코드 리뷰로 100% 막을 수 없다.

- 애플리케이션 레벨 방어: 실수 가능, 유출 시 **전체 테넌트** 노출 (최악의 사고 유형)
- DB 레벨 방어(RLS): 쿼리가 어떻게 생겼든 정책이 강제로 적용됨

---

## 2. 기본 사용법

```sql
-- 1) 테이블에 RLS 켜기 (이것만으로는 정책이 없어 아무것도 안 보임 = deny by default)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 2) 테이블 소유자에게도 적용 (이걸 빼면 소유자 계정은 정책을 우회한다)
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- 3) 정책 생성
CREATE POLICY tenant_isolation ON orders
  USING      (tenant_id = current_setting('app.tenant_id', true)::bigint)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::bigint);
```

### `USING` vs `WITH CHECK` — 자주 헷갈리는 지점
| 절 | 적용 대상 | 의미 |
|---|---|---|
| `USING` | SELECT, UPDATE, DELETE의 **읽는 행** | "이 행이 보이는가" |
| `WITH CHECK` | INSERT, UPDATE의 **쓰는 결과 행** | "이 행을 써도 되는가" |

**둘 중 하나만 걸면 구멍이 난다**: `USING`만 있으면 남의 테넌트 ID로 INSERT가 가능하고, UPDATE로 `tenant_id`를 남의 값으로 바꿔서 데이터를 넘겨줄 수도 있다.

### 요청마다 세션 변수 주입
```sql
SET LOCAL app.tenant_id = '42';   -- 트랜잭션 범위
```

---

## 3. 실무 함정 ① 커넥션 풀에서의 세션 변수 관리

**가장 위험한 부분.** 커넥션은 재사용되므로, **직전 요청의 tenant_id가 남아 있으면 그대로 다른 테넌트의 데이터가 보인다.**

| 방법 | 범위 | 안전성 |
|---|---|---|
| `SET app.tenant_id = ...` | **세션 전체** — 커넥션 반납 후에도 남음 | ❌ 위험 |
| `SET LOCAL app.tenant_id = ...` | **트랜잭션 종료 시 자동 복원** | ✅ 권장 |
| `set_config('app.tenant_id', v, true)` | 세 번째 인자 `true` = local | ✅ 권장 |

### 반드시 지킬 규칙
1. **`SET LOCAL`은 트랜잭션 안에서만 유효하다.** 트랜잭션 밖에서 실행하면 조용히 무시되고 경고만 뜬다 → **정책이 빈 값으로 평가되어 아무것도 안 보이거나(운 좋음), 설정 방식에 따라 잘못 보인다(운 나쁨).**
2. **PgBouncer transaction pooling과 반드시 같이 갈 것**: session pooling이 아닌 transaction pooling에서는 세션 레벨 `SET`이 커넥션 재사용 시 뒤섞인다. `SET LOCAL`만 쓰면 안전하다.
3. **커넥션 획득 시점에 자동 주입**: Spring이라면 `AbstractRoutingDataSource`나 `ConnectionPreparer`, 또는 트랜잭션 시작 리스너에서 강제로 주입. 개발자가 매번 호출하게 만들면 결국 빠뜨린다.
4. **`current_setting`의 두 번째 인자 `true`(missing_ok)**: 변수 미설정 시 예외 대신 NULL 반환. NULL과의 비교는 항상 false → 아무 행도 안 보임 = **fail-closed**. 이게 안전한 기본값이다. 반대로 `true`를 빼면 예외가 나서 원인을 빨리 찾을 수 있다. **정책상 fail-closed가 낫지만, 조용한 빈 결과는 디버깅이 어렵다** — 팀 규칙으로 정할 것.

### 우회 가능한 주체 (기억할 것)
- **슈퍼유저**와 `BYPASSRLS` 속성을 가진 롤은 RLS를 무시한다.
- `FORCE ROW LEVEL SECURITY`를 안 걸면 **테이블 소유자**도 무시한다.
- → **애플리케이션은 반드시 소유자가 아닌 전용 롤로 접속해야 한다.** 마이그레이션 계정과 런타임 계정을 분리.

---

## 4. 실무 함정 ② 정책 평가 비용

정책은 **모든 쿼리에 추가되는 조건(qual)**이다. 성능에 영향을 준다.

### 주의점
1. **정책 표현식은 단순하게.** 정책 안에 서브쿼리(`tenant_id IN (SELECT ...)`)를 쓰면 행마다 평가되면서 성능이 급격히 나빠질 수 있다. 세션 변수 비교가 가장 싸다.
2. **`current_setting()`은 STABLE 함수**라 쿼리당 한 번 평가된다. 타입 캐스팅(`::bigint`)을 명시해야 인덱스를 제대로 탄다 — text와 bigint 비교로 남으면 인덱스를 못 쓸 수 있다.
3. **인덱스 설계**: `tenant_id`가 사실상 모든 쿼리의 필수 조건이 되므로, **복합 인덱스의 선두 컬럼**에 `tenant_id`를 넣는다. (`(tenant_id, created_at)` 등)
4. **leakproof 문제**: RLS가 걸린 테이블에서는 보안상 정책 조건이 다른 조건보다 먼저 평가되도록 플래너가 제약된다. `LEAKPROOF`가 아닌 함수를 쓴 조건은 뒤로 밀린다 → 예상보다 나쁜 실행 계획이 나올 수 있다. **RLS 적용 전후로 `EXPLAIN ANALYZE`를 비교하는 습관.**
5. 파티셔닝과 함께 쓰면 상성이 좋다: `tenant_id`가 정책 조건이자 파티션 키면 프루닝이 같이 먹는다.

---

## 5. 이중 방어선: ORM 레벨 (Hibernate)

RLS만 믿지 않고, 애플리케이션에서도 조건을 넣어 **성능(인덱스 활용)과 보안(계층 방어)을 동시에** 챙긴다.

### `@TenantId` (Hibernate 6+)
```java
@Entity
public class Order {
    @Id Long id;

    @TenantId
    private Long tenantId;   // 조회 시 자동 필터, 저장 시 자동 주입
}
```
`CurrentTenantIdentifierResolver`가 요청마다 현재 테넌트를 알려주면, Hibernate가 알아서 조건을 붙이고 채워 넣는다.

### `@Filter` (더 범용적, 조건을 직접 정의)
```java
@Entity
@FilterDef(name = "tenantFilter",
           parameters = @ParamDef(name = "tenantId", type = Long.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
public class Order { ... }
```
```java
session.enableFilter("tenantFilter").setParameter("tenantId", ctx.tenantId());
```

**`@Filter`의 한계 (반드시 알아둘 것)**
- **`session.get()` / `findById()`에는 적용되지 않는다.** (1차 캐시 조회는 필터를 안 탐)
- 네이티브 쿼리에는 적용되지 않는다.
- → 그래서 **RLS가 최종 방어선으로 여전히 필요하다.**

### 결론적 구조
```
요청 → 인터셉터에서 tenant_id 확정
      ├─ ORM 필터 (성능 + 1차 방어)
      └─ DB RLS   (최종 방어, 우회 불가)
```

---

## 6. 검증 체크리스트

- [ ] 애플리케이션 롤이 테이블 소유자가 아니고 `BYPASSRLS`가 없는가
- [ ] `FORCE ROW LEVEL SECURITY`가 걸려 있는가
- [ ] `USING`과 `WITH CHECK`가 **둘 다** 있는가
- [ ] `SET LOCAL`을 트랜잭션 안에서 쓰는가 (밖에서 쓰면 무시됨)
- [ ] 세션 변수 미설정 시 동작이 정의되어 있는가 (fail-closed 확인)
- [ ] **테스트**: 테넌트 A 컨텍스트로 B의 행 조회/수정/삭제/삽입 4종 모두 실패하는가
- [ ] RLS 적용 전후 주요 쿼리의 실행 계획이 나빠지지 않았는가

---

## 7. 면접용 한 문단 요약

> RLS는 테이블에 정책을 걸어, 애플리케이션이 조건을 빠뜨려도 DB가 행을 걸러주는 최종 방어선이다. 요청마다 `SET LOCAL`로 세션 변수에 tenant_id를 넣고 정책이 그걸 비교하는 구조인데, 함정이 두 개다. 하나는 커넥션 풀 — 세션 스코프 `SET`을 쓰면 커넥션 재사용 시 이전 테넌트 값이 남아 유출된다. 그래서 트랜잭션 스코프인 `SET LOCAL`을 쓰고, 커넥션 획득 시점에 자동 주입한다. 다른 하나는 성능 — 정책이 모든 쿼리의 조건으로 붙으므로 표현식을 단순하게 유지하고 tenant_id를 복합 인덱스 선두에 둔다. 그리고 RLS만 믿지 않고 Hibernate `@TenantId`/`@Filter`로 ORM 레벨 방어선을 하나 더 둔다. `@Filter`는 `findById`에 안 걸리기 때문에 둘 다 필요하다.
