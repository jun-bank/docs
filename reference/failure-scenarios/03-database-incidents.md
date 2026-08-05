# 03. 데이터베이스·트랜잭션 장애 사례 — 자료 기반 수집과 우리 프로젝트 대조

- 작성일: 2026-08-05
- 성격: **L0 리서치** — 구현의 입력이 되는 순간 실코드로 재확인한다
- 조사 대상: RDBMS(특히 MySQL/InnoDB) 운영에서 **실제로 발생한 사고**
- 대조 대상: `ADR-007`(W-1~W-4) · `ADR-009`(K-1~K-4) · `ADR-011`(lazy close) · `quality-attributes.md`(HA-1~HA-5) · `domain/aggregates/README.md`(E1~E5 · 락 순서) · `account.md` · `card.md`

> **MySQL 버전 표기 원칙**: 각 사례에 사고 당시 버전을 적고, 우리가 쓸 버전(**8.0/8.4 가정**)에서 그 동작이 어떻게 바뀌었는지를 따로 적는다.
> 확인 사실: **InnoDB 기본 격리 수준은 8.0 · 8.4 · 9.x 모두 `REPEATABLE READ`** 로 유지된다 ([MySQL 8.4 Reference Manual §17.7.2.1](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)).

---

## 1. 사례 목록

| # | 유형 | 사례 | 출처(회사/연도) | 우리 자리 | 막나? |
|---|---|---|---|---|---|
| **L1** | 락 경합 | 트리거 기반 온라인 스키마 변경이 테이블/DB 전체를 락다운 | GitHub, 2016 | HA-5 | ⚠️ 부분 |
| **L2** | 락 경합 | AUTO-INC 테이블 락 → 임포트 수 시간 지연 → 해제 후 **갭 락**으로 재발 | ideeli, 2013 (MySQL 5.1.34) | K-2 · E2 · 멱등 | ❌ **뚫림** |
| **L3** | 락 경합 | 중복 키 INSERT가 **S락**을 걸어 3세션 데드락 | MySQL 공식 문서 8.0 | E1 멱등 · 망취소 재시도 | ❌ **뚫림** |
| **L4** | 락 경합 | 단일 UPDATE의 락 획득 순서는 **실행 계획이 정한다** — 애플리케이션 락 순서가 무의미해지는 지점 | MySQL 8.0 문서 + 국내 정리 | README 락 순서 ①~⑤ | ❌ **뚫림** |
| **C1** | 커넥션 풀 | 컨슈머 스레드 16 vs 풀 10, **한 태스크가 커넥션 2개** 요구 → HikariCP 데드락 | 우아한형제들, 2020 | W-1 | ✅ **막음** |
| **C2** | 커넥션 풀 | 복제본용 무거운 쿼리가 **마스터로** 감 → ProxySQL 커넥션 풀 붕괴, 8시간 14분 | GitHub, 2020-02 | W-2 · W-4 · ADR-008 | ⚠️ 부분 |
| **C3** | 커넥션 풀 | 읽기 복제본 복구 실패 + PgBouncer 우회로 **커넥션 상한 초과**, 14시간 | OpenAI, 2023-02 | HA-4 | ⚠️ 부분 |
| **C4** | 커넥션 풀 | 풀을 **줄였더니** 응답시간 100ms → 2ms (50배) | Oracle RWP / HikariCP wiki | ADR-008 병렬도 | ❌ **뚫림** |
| **R1** | 복제 지연 | 43초 네트워크 단절 → 크로스리전 자동 페일오버 → **split-brain**, 24시간 11분, 954건 미복제 쓰기 | GitHub, 2018-10 | HA-1 · HA-3 · W-2 | ⚠️ 부분 |
| **R2** | 복제 지연 | 비동기 복제의 유실을 **lossless(semi-sync) replication + MHA** 로 막은 은행 사례 | 카카오뱅크, 2017 | HA-1 · W-2 | ✅ 참조 |
| **T1** | 롱 트랜잭션 | 940개 좀비 트랜잭션 → history list length **6,000,000** → SELECT 계속 느려짐 | Percona (⚠️ **연도 미확인**, MySQL 5.6 언급) | ADR-011 §5 대사 · ADR-008 | ❌ **뚫림** |
| **T2** | 롱 트랜잭션 | RR에서 미커밋 트랜잭션이 purge를 막아 undo 무한 증가 | Percona, 2014 | E3·E4 미수 스캔 | ⚠️ 부분 |
| **M1** | 마이그레이션 | 네이티브 `ALGORITHM=INPLACE`는 **복제본에서 논블로킹이 아니다** — 프라이머리 3시간이면 복제 지연 3시간 | PlanetScale, 2024 (MySQL 8.0) | HA-5 · K-1 | ⚠️ 부분 |
| **M2** | 마이그레이션 | 4단계 온라인 마이그레이션(이중 쓰기 → 읽기 전환 → 쓰기 전환 → 정리) = expand-contract | Stripe, 2017 | **HA-5** | ✅ 근거 |
| **O1** | ORM | RR에서 **lost update 198건/9,048 트랜잭션** — "ORM의 load→modify→save 패턴에서 MySQL이 커밋된 변경을 조용히 버린다" | Jepsen, 2023-12 (MySQL 8.0.34) | **E1 전부** · W-1 | ⚠️ 조건부 |
| **O2** | ORM | 애플리케이션 쿼리 패턴 변경이 마스터 부하를 급증시켜 4시간 23분 장애 | GitHub, 2020-02-27 | ADR-007 조회 전용 | ⚠️ 부분 |
| **I1** | 격리 수준 | RR 스냅샷은 **읽기만 보호하고 UPDATE는 보호하지 않는다** — 21건 대상이 31건으로 갱신 | Percona (⚠️ **연도 미확인**) | E3 회수 대상 선정 · PRE-2 | ❌ **뚫림** |
| **I2** | 격리 수준 | RR 갭 락 → RC로 내려 해소 (그러나 RC는 lost update를 못 막는다) | ideeli, 2013 / MySQL Bug #52663 | 격리 수준 미결정 | ❌ **미결정** |
| **A1** | 자동 증가 키 | `innodb_autoinc_lock_mode=0` 이 같은 테이블 INSERT를 전부 직렬화 | MySQL Bug #16979 / Percona, 2007 | 승인·전표 대량 INSERT | ✅ 8.0 기본값이 해결 |
| **A2** | 시퀀스 | JPA `GenerationType.AUTO` 가 ID 채번에 **커넥션을 추가로** 요구 → 풀 데드락 | 우아한형제들, 2020 | ID 전략 미결정 | ❌ **미결정** |

---

## 2. 사례별 상세

### 2.1 락 경합 · 데드락

#### L1. GitHub — 트리거 기반 온라인 스키마 변경이 프로덕션을 락다운시켰다 (2016)

> 출처: GitHub, **"gh-ost: GitHub's online schema migration tool for MySQL"**, 2016-08
> https://github.blog/news-insights/company-news/gh-ost-github-s-online-migration-tool-for-mysql/

**무슨 일이 있었나**

- `pt-online-schema-change`(트리거 기반)로 마이그레이션을 돌리면 *"near or complete lock downs in production, to the effect of rendering the table or the entire database inaccessible due to lock contention"* 이 발생했다.
- 원인: 트리거가 **모든 쿼리에 해석 코드 실행을 추가**하고, 그 오버헤드가 **쓰기 동시성에 비례해 증폭**된다. *"lock contention is directly related to write concurrency on the master."*
- 추가로 트리거 생성/삭제 시의 **메타데이터 락**이 *"stalls to the extent of many seconds to a minute while attempting to remove triggers from a busy table"* 을 만들었다.
- 결과: 일부 마이그레이션은 **"위험 작업"** 으로 분류되어 비피크 시간·주말에만 실행 가능했고, 일부는 **일관되게 MySQL 장애를 일으켰다**.
- 해결: 트리거를 버리고 **바이너리 로그 tailing** 으로 바꾼 gh-ost. 마스터는 *"a single connection that is sequentially writing to the ghost table"* 만 본다. 2016-07 프로덕션 투입.

| | |
|---|---|
| **우리 자리** | **HA-5**(expand-contract) · **K-1**(모든 자금 테이블에 계좌ID 컬럼) |
| **막고 있나** | ⚠️ **부분.** HA-5가 *"구/신 버전 동시 가동 가능"* 을 요구하지만, **DDL을 어떤 도구로 실행하는가는 아무 데도 정해져 있지 않다.** expand-contract는 "무엇을 바꾸는가"의 규율이고, L1은 "어떻게 바꾸는가"의 사고다 |
| **무엇이 막나** | HA-5의 스키마 규율 + ADR-009 K-1(계좌ID를 **지금** 넣어 나중 ALTER를 없앤다) |
| **재현 주입** | 승인 테이블에 400 TPS 쓰기를 걸어둔 채 `pt-online-schema-change`로 컬럼 추가 → 승인 p99가 3초(BR-01)를 넘는지 |

#### L2. ideeli — AUTO-INC 락을 풀었더니 갭 락이 나왔다 (2013, MySQL 5.1.34)

> 출처: Aaron Brown (ideeli), **"Diagnosing MySQL AUTO-INC and Gap Locks"**, ideeli tech blog / 2013
> http://blog.9minutesnooze.com/diagnosing-mysql-autoinc-gap-locks-ideeli-tech-blog/

**무슨 일이 있었나 — 두 단계 사고**

```
1단계) innodb_autoinc_lock_mode = 0 (traditional)
   SKU 임포트가 수 분 → 수 시간. 동시 임포트 12개 이상에서 악화
   SHOW ENGINE INNODB STATUS:
     TABLE LOCK table `db`.`table` trx id 4617 lock mode AUTO-INC waiting
   원인: 2009년 5.0 → 5.1.34 업그레이드 때 중복 PK 오류가 나서
         DBA 컨설턴트가 mode 0 으로 되돌려 놓았고 그대로 남아 있었다

2단계) mode 1 로 바꿨더니 — 갭 락
   정리(DELETE) 트랜잭션과 임포트(INSERT) 트랜잭션이 세컨더리 인덱스에서 충돌
     lock_mode X locks gap before rec insert intention waiting
   DELETE ... WHERE last_name LIKE 'D%'  가 갭을 잠그고
   INSERT actor(first_name,'Davis')      가 그 갭에 들어가려다 대기

해결) 두 트랜잭션 모두 READ COMMITTED 로 — 갭 락 소멸. 수 시간 → 수 분
```

| | |
|---|---|
| **우리 자리** | **E2**(매입 배치 대량 INSERT + `Receivable.incur`) · **E3/E4**(미수 범위 스캔) · **K-2**(계좌ID 해시 파티션) |
| **막고 있나** | ❌ **뚫려 있다.** ① 격리 수준이 **어느 문서에도 결정돼 있지 않다** — MySQL 기본값 RR이면 갭 락이 켜져 있다 ② E2(매입 파일 배치, 새 미수 INSERT)와 E3(미수 FIFO 범위 스캔)이 **정확히 위 DELETE/INSERT 충돌과 같은 구조**다 |
| **무엇이 막나** | 지금은 **없다.** ADR-008 배치 파티션이 부하를 나누지만 갭 락은 파티션 안에서도 난다 |
| **재현 주입** | `SET GLOBAL innodb_print_all_deadlocks=ON`. 대사·매입 배치가 미수를 `WHERE accountId=? AND status='OPEN' FOR UPDATE` 로 범위 스캔하는 동안 E2/E5가 같은 계좌에 새 미수를 INSERT → `insert intention waiting` 발생 여부 |

#### L3. MySQL 공식 — 중복 키 INSERT가 S락을 걸어 데드락을 만든다 (MySQL 8.0)

> 출처: MySQL 8.0 Reference Manual **§17.7.3 Locks Set by Different SQL Statements in InnoDB**
> https://dev.mysql.com/doc/refman/8.0/en/innodb-locks-set.html

> *"If a duplicate-key error occurs, a shared lock on the duplicate index record is set. This use of a shared lock can result in deadlock should there be multiple sessions trying to insert the same row if another session already has an exclusive lock."*

```sql
CREATE TABLE t1 (i INT, PRIMARY KEY (i)) ENGINE = InnoDB;
-- 세션1: INSERT INTO t1 VALUES(1);   → X락 획득
-- 세션2: INSERT INTO t1 VALUES(1);   → 중복 오류 → S락 요청 (대기)
-- 세션3: INSERT INTO t1 VALUES(1);   → 중복 오류 → S락 요청 (대기)
-- 세션1: ROLLBACK;                    → 2·3이 S락 획득
--        2도 3도 X락으로 승격 불가 → DEADLOCK
```

또한 같은 문서:
- `INSERT ... ON DUPLICATE KEY UPDATE` 는 중복 시 **X락**을 건다 — 중복 PK면 index-record 락, **중복 유니크 키면 next-key 락**(즉 갭까지 잠근다).
- `UPDATE ... WHERE` 는 *"sets an exclusive next-key lock on every record the search encounters"* — **유니크 인덱스로 유니크 행을 찾을 때만** index-record 락으로 축소된다.

| | |
|---|---|
| **우리 자리** | ★ **E1의 `IdempotencyRecord.record`** · **E5의 `DepositReceipt.record`** · **E3의 `(depositId, 입금)` 수신 기록** |
| **막고 있나** | ❌ **뚫려 있다.** BR-01은 **망취소가 정상 경로**라고 명시했고(품질 속성 §0), 망취소·재시도는 **같은 `correlationId`로 여러 세션이 동시에 INSERT하는** 패턴이다. 이것이 위 3세션 시나리오 그 자체다 |
| **무엇이 막나** | 멱등 설계 자체는 **정확성**을 보장한다(HA-3). 막지 못하는 것은 **데드락으로 인한 실패율과 지연** — 그리고 BR-01 5초 타임아웃을 넘기면 **또 망취소가 온다**(양의 피드백) |
| **완화** | ① 멱등 레코드 키를 **PK**로 두면 next-key가 아닌 index-record 락 ② `INSERT ... ON DUPLICATE KEY UPDATE` 대신 **선조회 후 INSERT + 중복 예외를 멱등 히트로 해석** ③ 재시도 백오프 |
| **재현 주입** | 같은 `correlationId`로 동시 3~10 세션 승인 요청 → 데드락 로그·에러율·p99 측정 |

#### L4. 락 획득 순서는 애플리케이션이 정하지 못한다

> 출처: MySQL 8.0 Reference Manual **§17.7.5 How to Minimize and Handle Deadlocks**
> https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks-handling.html
> 보조: youngju.dev, **"데드락 진단과 예방 — 로그에서 두 쿼리를 특정하는 법"**, 2026-07-26
> https://www.youngju.dev/blog/database/2026-07-26-deadlock-debugging-prevention

MySQL 공식 권고는 우리 README와 **같은 방향**이다:

> *"When modifying multiple tables within a transaction, or different sets of rows in the same table, do those operations in a consistent order each time. Then transactions form well-defined queues and do not deadlock."*
> *"Always be prepared to re-issue a transaction if it fails due to deadlock. Deadlocks are not dangerous. Just try again."*
> *"Add well-chosen indexes ... so that your queries scan fewer index records and set fewer locks."*

**그러나 두 가지 단서가 있다:**

1. **단일 UPDATE/IN 절의 락 순서는 실행 계획이 정한다.** `UPDATE receivable SET ... WHERE id IN (a, b, c)` 는 `IN` 절에 적은 순서가 아니라 **인덱스 순서**로 잠근다. 정렬 순서를 강제하려면 `SELECT ... FOR UPDATE ... ORDER BY` 로 **먼저** 잠그거나, 애플리케이션이 키를 정렬해 **건별로** 잠가야 한다.
2. **조건 컬럼에 인덱스가 없으면 훑는 모든 레코드를 잠근다.**

| | |
|---|---|
| **우리 자리** | ★ **README 락 순서 ① 미수 → ② 승인 → ③ 계좌 → ④ 카드 → ⑤ 배치·멱등·정산** |
| **막고 있나** | ❌ **문서는 있으나 강제 장치가 없다.** §3.2에서 상세히 다룬다 |

---

### 2.2 커넥션 풀 고갈

#### C1. 우아한형제들 — 한 태스크가 커넥션 2개를 요구해 풀이 데드락 (2020)

> 출처: 우아한형제들 기술블로그, **"HikariCP Dead lock에서 벗어나기 (이론편/실전편)"**, 2020-02-06
> https://techblog.woowahan.com/2664/ · https://techblog.woowahan.com/2663/

**무슨 일이 있었나**

```
증상: HikariPool - Connection is not available, request timed out after 30000ms
      pool stats: total=10, active=10, idle=0, waiting=16

구조: Message Queue 컨슈머 스레드 16개  vs  HikariCP maximumPoolSize 10

기전: 한 태스크(메시지 1건 INSERT)가 동시에 커넥션 2개를 요구했다
      ① 루트 트랜잭션이 커넥션 #1 확보
      ② 서브 트랜잭션이 커넥션 #2 요청 → 풀에 없음 → 30초 대기
      ③ 타임아웃 → 서브 롤백 → 루트가 rollbackOnly → 전체 롤백
      ④ 그제서야 커넥션 반납 (이미 늦음)

왜 2개였나: JPA @GeneratedValue(strategy = GenerationType.AUTO)
           ID 채번을 위해 시퀀스 조회 커넥션이 추가로 필요했다

해결: 데드락 회피 가능한 풀 크기 적용 + SequenceGenerator에 pooled-lo optimizer
```

**필요 풀 크기 하한**: `스레드 수 × (한 태스크가 동시에 요구하는 최대 커넥션 수 − 1) + 1`

| | |
|---|---|
| **우리 자리** | **W-1**(E1~E5 안에서 ORM 외 DB 접근 금지) |
| **막고 있나** | ✅ **막는다 — 그리고 이것이 ADR-007의 가장 강한 부수 효과다.** W-1이 자금 경로에서 **두 번째 커넥션이 생길 경로 자체를 없앤다**: JDBC 직접 접근 없음 → 같은 영속성 컨텍스트 = 같은 커넥션 1개 |
| **무엇이 막나** | ADR-002 모듈 분리(자금 경로 모듈에 JDBC 타입 자체가 없음) + 아키텍처 테스트(JDBC 참조 0건) — *"쓸 수 없게 만드는"* 방식 |
| **⚠️ 남는 구멍** | **A2**: ID 채번 전략이 미결정이다. `GenerationType.AUTO`/`SEQUENCE`를 고르면 W-1을 지켜도 **채번이 별도 커넥션을 요구**해 같은 사고가 난다. `IDENTITY`(auto_increment)면 채번 커넥션은 없지만 **A1/L2의 AUTO-INC 경합**으로 간다. ★ **둘 중 하나를 고르는 결정이 아직 없다** |
| **재현 주입** | 풀 크기를 배치 병렬도보다 작게 설정 → E2 배치 실행 중 승인 경로가 `Connection is not available` 로 죽는지 |

#### C2. GitHub — 복제본용 쿼리가 마스터로 갔고, ProxySQL이 무너졌다 (2020-02)

> 출처: GitHub, **"February service disruptions post-incident analysis"**, 2020-03-26
> https://github.blog/2020-03-26-february-service-disruptions-post-incident-analysis/

| 시각(UTC) | 지속 | 무슨 일 |
|---|---|---|
| 02-19 15:17 | 52분 | *"The intent was to run this load against our read replica pool at a much lower frequency, but we inadvertently sent this traffic to the master."* → **커넥션 풀링을 담당하는 ProxySQL이 과부하**로 쿼리를 일관되게 수행 못 함 |
| 02-20 21:31 | 47분 | 마스터 승격 계획 작업 중 높은 부하로 ProxySQL 재실패 |
| 02-25 16:36 | **2시간 12분** | 활성 커넥션이 임계치 초과. ★ *"because of a system-level limit of 1048576, our process manager silently reduced our `LimitNOFILE` setting from 1073741824 to 65536"* — **설정이 조용히 축소돼 있었다** |
| 02-27 14:31 | **4시간 23분** | 애플리케이션 로직 변경이 쿼리 패턴을 바꿔 마스터 부하 급증 |
| **합계** | **8시간 14분** | 대응: 배포 3일 동결, 데이터 파티셔닝으로 mysql1 부하 20% 감축, 피처 플래그 도입 |

| | |
|---|---|
| **우리 자리** | **W-2**(자금 판단은 쓰기 데이터소스) · **W-4**(표시용/판단용 분리) · **ADR-008**(배치 파티션 병렬도) |
| **막고 있나** | ⚠️ **부분.** W-2/W-4는 *"복제본이 판단에 새어 들어오는 것"* 을 막는다. GitHub 사고는 **반대 방향** — *"복제본용 부하가 마스터로 새어 들어왔다"*. **우리 문서에 그 방향을 막는 규칙이 없다** |
| **뚫린 자리** | ADR-007은 *"조회 전용 = 자유, 배치 = 자유"* 라고만 적었다. 조회·배치가 **쓰기 데이터소스를 쓰는 것을 금지하지 않는다.** ADR-008 파티션 수는 K-3에 따라 **설정값**이므로, 운영자가 병렬도를 올리면 승인 경로(QS-01)를 잡아먹는다 = ADR-007 되돌리기 조건 **R2** 그 자체 |
| **완화 후보** | ① 자금 경로 / 조회 / 배치 **커넥션 풀 3분리**(공유 상한이 아니라 별도 풀) ② 배치 병렬도 상한을 풀 크기에서 **역산**해 코드가 아닌 부팅 시 검증 ③ `LimitNOFILE` 류 **조용한 축소를 스모크에서 확인**(GitHub가 4개월 놓친 것) |
| **재현 주입** | 배치 병렬도 K-3을 단계적으로 올리며 승인 p99를 측정 → R2 발화 지점 찾기 |

#### C3. OpenAI — 복제본이 복구되지 않았고 풀러를 우회한 연결이 상한을 넘겼다 (2023-02-20)

> 출처: OpenAI Developer Community, **"Postmortem: Feb 20, 2023 OpenAI suffered a major DB outage"**, 2023
> https://community.openai.com/t/postmortem-feb-20-2023-openai-suffered-a-major-db-outage/73068

- 근본 원인: 클라우드 사업자의 **정기 유지보수** 후 **읽기 복제본이 복구 루프에서 빠져나오지 못했다**. 프라이머리는 hot standby로 페일오버했지만 **복제본에는 대응 페일오버가 없었다** → 용량 부족.
- 복구 중: *"previously unknown slow queries hogging the pools"* 가 PgBouncer 풀을 점유.
- 2차 장애(10:43–11:04): **새 복제본이 PgBouncer를 우회**해 붙어 **DB 커넥션 상한 초과**.
- 총 약 **14시간**(완성 트래픽 복구까지 ~9시간, 나머지 서비스 정상화까지 14시간).

| | |
|---|---|
| **우리 자리** | **HA-4**(세션·스티키 라우팅 비의존) · **D-05 부분 철회**(헬스체크·기본 지표는 포기 대상 아님) |
| **막고 있나** | ⚠️ **부분.** HA-4는 앱 인스턴스를 다룬다. **"복제본이 죽었을 때 조회 경로가 어디로 가는가"** 는 정해져 있지 않다. ADR-007은 *"조회 전용은 복제본 허용"* 이라고만 한다 |
| **핵심 교훈** | ★ **풀러를 우회하는 경로가 하나라도 있으면 상한 관리가 무너진다.** 우리 대응물은 W-1(ORM 외 접근 금지)인데, **그 강제 범위는 "자금 경로 모듈"뿐**이다. 배치·조회 모듈은 자유이므로 우회 경로가 남는다 |

#### C4. 풀을 줄이면 빨라진다 — Oracle Real-World Performance

> 출처: HikariCP Wiki **"About Pool Sizing"** / Oracle Real-World Performance group
> https://github.com/brettwooldridge/HikariCP/issues/1171 (문서 논의 스레드)

- 공식(고전): `connections = ((core_count * 2) + effective_spindle_count)`
  - 예: 4코어 + 디스크 1개 → **9**. NVMe/버퍼풀 히트 환경에서 `effective_spindle_count` 는 **사실상 0**.
- Oracle RWP 실측: 풀 크기를 **줄였더니 응답시간이 약 100ms → 약 2ms (약 50배)**.

| | |
|---|---|
| **우리 자리** | **ADR-008 배치 파티션 수(K-3)** · QS-01 400 TPS |
| **막고 있나** | ❌ **뚫려 있다.** *"파티션 수는 설정값이며 코드에 박지 않는다"*(K-3)는 **상한 근거가 없다.** 병렬도를 올리는 것이 처리 시간을 줄인다는 검증(ADR-009 §7)만 있고, **줄지 않는 지점 = DB 코어 수 기반 상한**은 어디에도 없다 |
| **재현 주입** | 파티션 수를 1→2→4→8→16 으로 올리며 배치 처리 시간과 **승인 p99**를 동시에 측정. 처리 시간이 더 안 줄고 p99만 오르는 지점이 상한 |

---

### 2.3 복제 지연

#### R1. GitHub — 43초 단절이 24시간 장애가 되었다 (2018-10-21)

> 출처: GitHub, **"October 21 post-incident analysis"**, 2018-10
> https://github.blog/news-insights/company-news/oct21-post-incident-analysis/

```
22:52 UTC  네트워크 유지보수로 US East 허브 ↔ 프라이머리 DC 간 43초 연결 상실
           → Orchestrator(Raft 기반)가 자동 페일오버, US West 복제본을 프라이머리로 승격
           → 양쪽 DC의 클러스터가 각각 상대에 없는 쓰기를 갖게 됨 (split-brain)

결과       East 에 약 40분 분량 미복제 쓰기. 한 바쁜 클러스터에서 954건이 서쪽으로 안 넘어감
           안전한 failback 불가 → 수동 조정 필요
총 24시간 11분 (10/21 22:52 ~ 10/22 23:03)

판단      "data integrity over site usability and time to recovery"
          — 데이터 무결성을 위해 서비스 저하를 감수했다
대책      크로스리전 승격 금지, 멀티리전 액티브-액티브, 카오스 엔지니어링
```

| | |
|---|---|
| **우리 자리** | **HA-1**(인스턴스 로컬 상태로 자금 판단 금지) · **HA-3**(모든 자금 경로 멱등) · **W-2** |
| **막고 있나** | ⚠️ **부분 — 그리고 우리 상충 판정이 GitHub와 같다.** `quality-attributes.md` §3: *"정합성 vs 가용성 → **정합성**, 개별 요청을 거절한다"*. GitHub의 판단(*"무결성 > 가용성"*)과 같은 방향 |
| **뚫린 자리** | ★ **split-brain에서 멱등이 깨진다.** 우리 멱등 키는 `correlationId`(**매입사가 생성**)이고 `IdempotencyRecord` 는 DB 유니크 제약으로 성립한다. **DB가 둘로 갈리면 같은 `correlationId`가 양쪽에 각각 기록되어 유니크 제약이 아무것도 막지 못한다** → 이중 승인. HA-3은 *"멱등이다"* 라고만 적고 **멱등의 근거가 단일 DB 유니크 제약이라는 사실**을 적지 않았다 |
| **지금은 왜 안 나나** | C-04(예산 0)로 **단일 인스턴스·단일 DB 운영**이기 때문이다. HA-1~HA-5는 *"구조가 다중화를 막지 않게"* 만 하고 있으므로, **다중화하는 순간 이 구멍이 열린다** |
| **재현 주입** | 지금은 재현 불가(단일 DB). ADR-004 R1(샤딩)·다중화 시점에 **필수 시험 항목**으로 이월 |

#### R2. 카카오뱅크 — 은행이 MySQL로 데이터 유실을 막은 방법 (2017)

> 출처: 바이라인네트워크, **"카카오뱅크는 어떻게 MySQL로 데이터 유실을 막았을까"**, 2017-10-17 (if(kakao)/DBA 성동찬 발표)
> https://byline.network/2017/10/17-6/

- 문제 인식: MySQL **비동기 복제**는 마스터가 죽으면 데이터를 잃을 수 있다 — 은행 채널계에 그대로 쓸 수 없다.
- 해법 ①: **Lossless replication** — 마스터 변경이 **실제 데이터 복제 전에 복제본의 릴레이 로그에 먼저 기록**된다. 마스터가 전송 전에 죽어도 **릴레이 로그로 동일 데이터를 재생성**할 수 있다.
- 해법 ②: **MHA(Master High Availability)** — 릴레이 로그로 빠르게 복구, 무손실 자동 페일오버.
- 핵심 문장: *"장애 시 데이터만 유실되지 않으면 마스터와 슬레이브가 정확히 일치할 필요는 없다."*

| | |
|---|---|
| **우리 자리** | **HA-1** · **W-2** · 가용성 2순위 |
| **막고 있나** | ✅ **참조 사례** — 우리 W-2(*"자금 판단 조회는 쓰기 데이터소스에서만"*)는 **복제 지연을 정합성에서 분리**하는 더 강한 선택이다. 카카오뱅크는 *"지연은 허용하되 유실은 막는다"*, 우리는 *"자금 판단은 지연을 아예 안 본다"* |
| **가져올 것** | ★ **우리는 "유실"을 안 다뤘다.** ADR-007은 복제 **지연**만 다루고, **마스터 장애 시 커밋된 자금 트랜잭션의 유실**은 어느 문서에도 없다. 은행이면 semi-sync는 선택이 아니라 요구다 |

---

### 2.4 롱 트랜잭션 · undo 증가

#### T1. Percona — 940개 좀비 트랜잭션이 SELECT를 계속 느리게 만들었다

> 출처: Percona, **"Chasing a Hung Transaction in MySQL: InnoDB History Length Strikes Back"** (⚠️ **게시 연도 미확인** — 본문이 MySQL **5.6**과 Amazon Aurora를 언급한다)
> https://www.percona.com/blog/chasing-a-hung-transaction-in-mysql-innodb-history-length-strikes-back/

```
증상   SELECT 가 점점 느려지고 재시작해야만 회복
지표   InnoDB history list length = 6,000,000 이상, 계속 증가
발견   information_schema.innodb_trx + performance_schema.events_statements_history
       → ACTIVE 상태로 766,000초(약 8.8일) 방치된 트랜잭션 940개
       프로세스 리스트에서는 "Sleep" 으로 보였다 (락과 undo는 계속 쥔 채)
원인   REPEATABLE READ 에서 미커밋 트랜잭션이 있으면
       InnoDB 는 다른 트랜잭션의 undo 레코드를 purge 하지 못한다
       → 행 버전이 계속 쌓이고 SELECT 가 버전 체인을 더 길게 훑는다
해결   940개 커넥션 kill → history list length 6,000,000 → 793
비고   5.6 에서는 RC 로 내리면 해소됐으나 Amazon Aurora 에서는 안 됐다
```

> 함께: Percona, **"InnoDB transaction history often hides dangerous 'debt'"**, 2014-10-17
> https://www.percona.com/blog/2014/10/17/innodb-transaction-history-often-hides-dangerous-debt/

| | |
|---|---|
| **우리 자리** | ★ **ADR-011 §1 표** — *"M9·M10·M11은 커트오프 불필요 — **코어 안, 한 읽기 트랜잭션**"* |
| **막고 있나** | ❌ **뚫려 있다. 그리고 ADR-011이 스스로와 충돌한다.** |
| **모순 지점** | ADR-011 §2에서 **안 C(전 계좌를 한 읽기 트랜잭션으로)** 를 *"long transaction · 파티션 병렬 불가"* 로 **기각**했다. 그런데 §1 표는 M9·M10·M11을 *"코어 안, **한 읽기 트랜잭션**"* 이라고 적어 **기각한 안 C를 대사 경로에 다시 들여놨다.** 계좌 수 × 승인 수 전체를 훑는 RR 읽기 트랜잭션은 정확히 T1의 6,000,000 시나리오다 |
| **왜 위험한가** | 대사는 **매 영업일** 돈다(BR-41). 매일 밤 수십 분짜리 RR 읽기 트랜잭션이 열리면 그동안 **승인 경로의 undo purge가 멈춘다** → 다음 날 승인 SELECT가 느려진다 → BR-01 3초 초과 → 망취소 증가 → **정합성 사고 입구**(품질 속성 §0의 인과 사슬 그대로) |
| **완화 후보** | ① 대사를 **계좌 파티션 단위 짧은 트랜잭션 N개**로 (K-4가 이미 *"파티션 완료 후 단일 단계"* 를 말한다 — 파티션 안이 짧아야 한다) ② `SET TRANSACTION ISOLATION LEVEL READ COMMITTED` 로 대사 읽기 ③ ★ **`history list length` 를 QS-04 탐지 지표에 넣는다** |
| **재현 주입** | 대사 배치를 돌리는 동안 `SHOW ENGINE INNODB STATUS` 의 `History list length` 를 1초 간격 샘플링. 배치 종료 후 원복되는가, 승인 p99가 그동안 오르는가 |

#### T2. Percona — RR에서 트랜잭션 이력이 감추는 '빚' (2014)

- history list length가 커지면 **SELECT가 이전 행 버전을 점점 더 많이 스캔**해야 하고, 성능이 재시작 전까지 계속 떨어진다.
- undo 공간은 **트랜잭션 크기에 따라 무한히 커질 수 있다**.

| | |
|---|---|
| **우리 자리** | **E3**(미수 FIFO 범위 스캔) · **E4**(자기 미수 + 회수 대상 미수 전순서 선점) |
| **막고 있나** | ⚠️ **부분.** E3·E4는 **한 계좌** 범위이므로 짧다. 위험한 것은 T1의 대사 배치 쪽 |

---

### 2.5 마이그레이션 사고

#### M1. PlanetScale — 네이티브 온라인 DDL은 복제본에서 논블로킹이 아니다 (2024, MySQL 8.0)

> 출처: PlanetScale, **"The State of Online Schema Migrations in MySQL"**, 2024
> https://planetscale.com/blog/state-of-online-schema-migrations-in-mysql

**`ALGORITHM=INPLACE` 의 실제 문제**

| 문제 | 내용 |
|---|---|
| **복제 정지** | *"On replica servers, the operation is NOT non-blocking"* — 프라이머리에서 3시간 걸리면 **복제본은 3시간 뒤처진다** |
| 자원 점유 | *"resource greedy ... can and will impact performance on busy servers"* |
| 디스크 | 원본 테이블 크기만큼 추가 필요 |
| **중단 불가** | *"The only way to abort is to kill the query aggressively"* — 그 후 비싼 정리 작업 |

**`ALGORITHM=INSTANT` 의 한계** (임의 위치 `ADD/DROP COLUMN` 은 **MySQL 8.0.29** 부터)

- 메타데이터 변경만: **타입 변경(int→bigint) 불가 · 인덱스 추가 불가 · PK 변경 불가 · FK 불가 · 문자셋 변경 불가**
- `DROP COLUMN` 은 **백업 없이 되돌릴 수 없다** — 내장 revert 없음
- 결론: *"Third-party solutions remain the way to go for the foreseeable future"* (gh-ost / Vitess VReplication / spirit)

| | |
|---|---|
| **우리 자리** | **HA-5**(expand-contract) · **K-1**(자금 테이블에 계좌ID 컬럼) · **ADR-011 Q-1**(계좌에 `lastClosedBusinessDate`·`closedBalance` 신설) |
| **막고 있나** | ⚠️ **부분 — 그러나 K-1의 판단은 이 사례가 정확히 뒷받침한다.** ADR-009 §5: *"모든 자금 테이블이 계좌ID를 갖고 있어야 한다 — 없으면 파티션 불가"*, K-1 주석: *"지금 안 하면 나중에 못 하는 것"*. **INSTANT DDL은 컬럼 추가는 되지만 그 컬럼을 선행 키로 하는 인덱스 추가는 안 된다.** 즉 나중에 K-1을 하려면 **INPLACE 전면 리빌드 = 복제본 정지** |
| **✅ 잘 막고 있는 자리** | ADR-011 Q-1의 신설 필드가 **둘 다 nullable**(`BusinessDate?` · `Money?`)이다. expand 단계가 안전하고, **R2**(*"`lastClosedBusinessDate < 대상 영업일`이면 `balance`를 쓴다"*)가 **NULL/구값을 읽는 구버전 앱과의 동시 가동을 이미 처리**한다 — 이것이 교과서적인 expand-contract다 |
| **⚠️ 남는 것** | contract 단계(NOT NULL 승격·구 컬럼 제거)를 **누가 언제 하는가**가 없다. M1의 *"DROP COLUMN은 되돌릴 수 없다"* 가 여기에 걸린다 |
| **재현 주입** | 승인 400 TPS 중 승인 테이블에 `ALTER TABLE ... ADD INDEX` (INPLACE) → 복제 지연 시간과 승인 p99 |

#### M2. Stripe — 4단계 온라인 마이그레이션 = expand-contract (2017)

> 출처: Stripe, **"Online migrations at scale"**, 2017-02-02
> https://stripe.com/blog/online-migrations

```
① 이중 쓰기  — 기존 테이블과 새 테이블에 동시에 쓴다 (동기 유지)
② 읽기 전환  — 코드베이스의 모든 읽기 경로를 새 테이블로
③ 쓰기 전환  — 모든 쓰기 경로를 새 테이블로만
④ 정리       — 구 데이터 모델 의존 데이터 제거

+ 백필: 두 저장소가 동일해지도록 누락분을 채운다.
  ★ 프로덕션 DB에 비싼 쿼리를 돌리는 대신 Hadoop/MapReduce 로 오프라인 병렬 처리
```

| | |
|---|---|
| **우리 자리** | ★ **HA-5** — *"스키마 변경은 expand-contract(구/신 버전 동시 가동 가능)"* |
| **막고 있나** | ✅ **HA-5의 근거로 그대로 쓸 수 있다.** HA-5는 한 줄짜리 원칙이고, Stripe 4단계가 **그 원칙의 실행 절차**다 |
| **가져올 것** | ★ **백필을 프로덕션 DB에서 돌리지 않는다**는 규칙. 우리 문맥으로 옮기면 **K-1의 계좌ID 백필을 승인 경로와 같은 DB에서 대량 UPDATE로 하면 안 된다**(T1·T2의 롱 트랜잭션으로 직행). 청크 + 커밋 분할 + 스로틀 |

---

### 2.6 ORM 관련 사고

#### O1. Jepsen — MySQL 8.0.34의 REPEATABLE READ는 ORM 패턴을 조용히 깬다 (2023-12)

> 출처: Jepsen, **"MySQL 8.0.34"**, 2023-12
> https://jepsen.io/analyses/mysql-8.0.34

**단일 노드 정상 상태에서 관측된 이상 현상**

| 이상 | 관측 |
|---|---|
| **G2-item** (write-write / read-write 순환) | 정상 단일 노드에서 **40초에 214건** |
| **G-single** (read skew) | 60초 테스트에서 **244건** — *"one transaction can both fail to observe but also overwrite another"* |
| **Lost update** | **9,048 트랜잭션 중 198건** (그중 순환으로 검출된 것은 47건뿐) |
| **내부 비일관성** | 9,048 중 **126건** — 한 트랜잭션 안에서 유령 값을 읽음 |
| **비단조 읽기** | 동시 쓰기의 **부분 효과**를 관측 — 스냅샷 의미 위반 |
| SERIALIZABLE (AWS RDS 다중 노드) | `replica_preserve_commit_order=OFF` 기본값 탓으로 추정되는 G2-item·G-single |

★ **핵심 문장**:
> *"The common ORM pattern in which a program starts a transaction, loads an object into memory, manipulates it, saves it back to the database, then commits, may find that MySQL silently discards those committed changes."*

**권고**: ① 안전이 중요한 연산은 **SERIALIZABLE** ② READ COMMITTED에서 개별 읽기를 **`SELECT ... FOR UPDATE`** 로 강화 ③ read-modify-write는 **명시적 애플리케이션 락**

| | |
|---|---|
| **우리 자리** | ★★ **E1 전부** · **W-1**(자금 경로는 ORM 단일 경로) · `account.md` §8 · `card.md` §8 |
| **왜 치명적인가** | E1은 **정확히 이 패턴**이다: `Account` 로드 → `hold()` 로 `holdTotal` 증가 → 저장 → 커밋. `Card.useLimit()` 도, `Account.useAccountLimit()` 도 같다. **lost update 하나가 곧 초과 승인**이다 |
| **막고 있나** | ⚠️ **조건부로 막는다 — 그리고 그 조건이 ADR에 없다.** `account.md` §8이 *"계좌 단위 **낙관적 락**(버전) + 충돌 시 재시도"*, `card.md` §8이 *"카드 단위 낙관적 락"* 을 적었다. 낙관적 락은 `UPDATE ... SET version=v+1 WHERE id=? AND version=v` 이므로 **행 조건부 갱신**이고, lost update를 실제로 막는다 |
| **★ 뚫린 자리** | 낙관적 락이 **애그리게이트 문서 §8(동시성)에만 있고 ADR-007 규칙(W-1~W-4)에는 없다.** ADR-007은 *"ORM 단일 경로"* 만 강제한다. **ORM 단일 경로는 flush 타이밍은 막지만 lost update는 못 막는다** — 오히려 Jepsen이 지목한 그 패턴을 **의무화**한다. W-5(낙관적 락 필수)가 없다 |
| **★ 두 번째 구멍** | ADR-007 §4 *"무엇이 이것을 강제하나"* 의 세 수단(모듈 분리 · 아키텍처 테스트 · 데이터소스 분리)은 **전부 "JDBC를 못 쓰게" 만드는 것**이고, **버전 컬럼 누락을 잡는 수단은 하나도 없다**. `@Version` 을 안 붙인 애그리게이트가 하나 있으면 그 자리에서 초과 승인이 난다 — 그리고 그것은 **컴파일도 아키텍처 테스트도 통과한다** |
| **세 번째** | `account.md` PRE-2(*"미결 미수 없음"*)는 **존재 여부 조회**다. RR의 비잠금 읽기는 **갭 락을 안 걸어 팬텀을 막지 못한다.** E2/E5가 동시에 그 계좌에 미수를 만들면 **미수 있는 계좌에 승인이 성립**한다. 이 위반은 M9·M10·M11 어느 등식에도 안 걸린다(합계 등식이 아니라 **존재 술어**이므로) → **탐지 없이 남는다** |
| **재현 주입** | ① `@Version` 을 일부러 제거하고 같은 계좌 동시 승인 → 초과 승인 건수 ② 격리 수준을 RR/RC로 바꿔가며 같은 시험 ③ PRE-2 팬텀: 승인 트랜잭션이 미수 존재 조회를 마친 시점에 다른 세션이 미수 INSERT 후 커밋 → 승인이 통과하는지 |

#### O2. GitHub — 쿼리 패턴 변경이 4시간 23분 장애를 만들었다 (2020-02-27)

> 출처: 위 C2와 같은 포스트모템

- *"application logic changes to database query patterns rapidly increased load on the master of the mysql1 database cluster"* → 클러스터 전체가 느려져 **의존 서비스 전부의 가용성**에 영향, **4시간 23분**.
- 대응: 배포 3일 동결 + **피처 플래그**로 문제 로직을 런타임에 끌 수 있게.

> ★ N+1은 개별 사례로 강한 1차 출처를 찾지 못했다(§5 참조). O2가 **"코드 변경이 DB 부하를 배수로 늘린다"** 는 같은 계열의 검증된 사례다.

| | |
|---|---|
| **우리 자리** | **ADR-007** 조회 전용 경로(*"자유 — 성능에 맞는 수단"*) · **W-3**(조회 전용은 읽기 전용 명시 + 자금 경로와 분리) |
| **막고 있나** | ⚠️ **부분.** W-3이 트랜잭션을 분리하지만 **자원은 분리하지 않는다**. 조회 API가 N+1을 만들면 같은 DB를 공유하는 자금 경로가 죽는다 |
| **가져올 것** | ★ **피처 플래그** — 우리 문서 어디에도 *"나쁜 코드를 배포 없이 끄는 수단"* 이 없다. HA-2(단일 실행 보장)·복구가능성 5순위와 같은 층위의 요구다 |

---

### 2.7 격리 수준 오해

#### I1. Percona — RR의 스냅샷은 읽기만 보호하고 UPDATE는 보호하지 않는다

> 출처: Percona, **"What if … MySQL's Repeatable Reads Cause You to Lose Money?"** (⚠️ **게시 연도 미확인** — 본문에서 확인하지 못했다)
> https://www.percona.com/blog/what-if-mysqls-repeatable-reads-cause-you-to-lose-money/

```
설정   bonus=1 AND active=1 인 고객 21명, 예상 할인 비용 약 $242 (매출 $2,416.23의 10%)

세션1  START TRANSACTION;  (REPEATABLE READ)
       SELECT * FROM customer WHERE bonus=1 AND active=1;   → 21건 (스냅샷)
세션2  UPDATE customer SET active=1 WHERE ... ;             → 휴면 10명 활성화, COMMIT
세션1  UPDATE customer SET ... WHERE bonus=1 AND active=1;  → ★ 31건 갱신

결과   예상 $242 → 실제 약 $375
이유   "스냅샷은 읽기를 보호하지만 UPDATE 절은 현재 테이블 상태에 매칭된다"

해법   SELECT ... FOR SHARE  또는  SELECT ... FOR UPDATE  로 대상을 먼저 잠근다
       (또는 RC + 애플리케이션 로직)
```

| | |
|---|---|
| **우리 자리** | ★★ **E3 `deposit()`** · **E4 `refund()`** — `account.md` §5 조작 상세 |
| **왜 정확히 같은 구조인가** | `account.md` 는 *"**대상을 먼저 정하고 합을 낸다**"* 를 핵심으로 적었다: ① 회수 가능액 = Σ `recoverable[i].outstanding()` ② 회수액 = min(유입액, 회수 가능액) ③ FIFO 배분 ④ 잔여만 `balance` 증가. **①과 ③ 사이에 다른 경로가 그 미수를 바꾸면 RC-2(배분 합계 = 회수액)가 깨진다** |
| **막고 있나** | ⚠️ **문서는 인식하고 있으나 장치가 반쪽이다.** `account.md` §8: *"회수 대상 조회와 회수의 경합 → 한 트랜잭션(E3). 조회 후 커밋 전에 다른 경로가 그 미수를 회수하면 **미수 단위 락**에서 하나만 성공"*. **"미수 단위 락"이 낙관적 락인지 `SELECT ... FOR UPDATE` 인지 적혀 있지 않다** |
| **★ 결정적 차이** | 낙관적 락이면 **기존 미수의 변경**은 잡지만 **새로 생긴 미수**(E2/E5의 `Receivable.incur`)는 못 잡는다 = **팬텀**. RR에서 비잠금 `SELECT`는 갭 락을 안 걸므로, ①에서 안 보였던 미수가 커밋 시점에는 존재한다. FIFO 순서(`incurredBusinessDate`)상 **앞에 끼어드는** 미수면 회수 순서 자체가 틀린다 → BR-34 위반 → **환불 반환액이 틀어진다**(E3 근거란이 예고한 바로 그 결과) |
| **막는 법** | `SELECT ... FROM receivable WHERE accountId=? AND status=OPEN ORDER BY incurredBusinessDate, receivableId **FOR UPDATE**` — RR에서 이 범위 잠금이 **next-key 락으로 갭까지 잠가** 팬텀을 막는다. ★ **즉 우리는 RR의 갭 락이 필요하다** — I2와 정면으로 부딪힌다 |
| **재현 주입** | E3 트랜잭션이 회수 대상을 조회한 뒤 커밋 전에, 다른 세션이 같은 계좌에 **더 이른 `incurredBusinessDate`** 미수를 INSERT+커밋 → RC-2 배분 합계와 FIFO 순서가 유지되는지 |

#### I2. RR 갭 락 vs RC lost update — 어느 쪽으로 가도 대가가 있다

> 출처: L2(ideeli, 2013) · MySQL Bug **#52663** *"Lost update incrementing column value under READ COMMITTED isolation level"* https://bugs.mysql.com/bug.php?id=52663
> · Jepsen MySQL 8.0.34 (O1)

| 격리 수준 | 얻는 것 | 잃는 것 |
|---|---|---|
| **RR** (MySQL 기본, 8.0/8.4/9.x 동일) | 갭·넥스트키 락으로 **팬텀 방지** → I1 방어 | 갭 락 데드락(L2) · **lost update는 여전히 발생**(Jepsen 198건) · undo purge 지연(T1) |
| **RC** | 갭 락 없음 → L2·T1 완화 | **팬텀 노출**(I1 재발) · lost update(Bug #52663) · MySQL 문서상 *"each consistent read reads its own fresh snapshot"* |

★ **어느 쪽도 read-modify-write를 안전하게 만들지 않는다.** 두 경우 모두 **명시적 잠금(낙관적 락 또는 `FOR UPDATE`)이 필수**다.

| | |
|---|---|
| **우리 자리** | **전 경로** — 그런데 **격리 수준을 정한 문서가 없다** |
| **막고 있나** | ❌ **미결정.** ADR-007은 *"어디서 읽는가"* 를 정했고 *"어떤 격리로 읽는가"* 를 정하지 않았다. 기본값 RR이 그대로 적용된다 |
| **필요한 결정** | 경로별로 다르게: 자금 경로 E1~E5 = **RR + 명시적 잠금**(I1 방어에 갭 락이 필요) / 대사·배치 읽기 = **RC**(T1 방어) / 조회 전용 = **RC** |

---

### 2.8 자동 증가 키 · 시퀀스 병목

#### A1. AUTO-INC 테이블 락 — `innodb_autoinc_lock_mode`

> 출처: MySQL Bug **#16979** *"AUTO_INC lock in InnoDB works a table level lock"* https://bugs.mysql.com/bug.php?id=16979
> · Percona, **"InnoDB auto-inc scalability fixed"**, 2007-09-26 https://www.percona.com/blog/2007/09/26/innodb-auto-inc-scalability-fixed/
> · MySQL 8.0/9.1 Reference Manual **§17.6.1.6 AUTO_INCREMENT Handling in InnoDB** https://dev.mysql.com/doc/refman/9.1/en/innodb-auto-increment-handling.html

| 모드 | 동작 | 결과 |
|---|---|---|
| **0** traditional | 모든 INSERT류가 **문장 종료까지 테이블 레벨 AUTO-INC 락** | ★ 같은 테이블 INSERT **전부 직렬화** — L2의 1단계 |
| **1** consecutive | 벌크 INSERT만 테이블 락, 한 번에 하나 | 문장 기반 복제에서 연속 ID 필요 시 |
| **2** interleaved | AUTO-INC 테이블 락 **없음**, 동시 실행 | 가장 빠르고 확장성 높음. **MySQL 8.0 기본값**(행 기반 복제와 함께) |

| | |
|---|---|
| **우리 자리** | 승인·전표·미수 테이블의 대량 INSERT (400 TPS + 매입 배치) |
| **막고 있나** | ✅ **MySQL 8.0 기본값(mode 2)이 해결한다.** 단 ideeli가 그랬듯 **과거 사고 때문에 mode 0으로 되돌려 놓고 잊는 것**이 실제 위험이다 |
| **재현 주입** | `innodb_autoinc_lock_mode` 를 0으로 내리고 매입 배치 병렬 실행 → 처리 시간이 직렬 수준으로 붕괴하는지 (부팅 시 이 변수를 assert 하는 근거를 만든다) |

#### A2. JPA 시퀀스 채번이 커넥션을 하나 더 먹는다

> 출처: 우아한형제들 HikariCP 장애 (C1). *"@GeneratedValue(strategy = GenerationType.AUTO) ... ID 생성을 위해 추가적인 Connection이 필요"* → 후속 조치로 **SequenceGenerator에 Pooled-lo optimizer 적용**

| | |
|---|---|
| **우리 자리** | 전 애그리게이트의 ID 전략 — **어느 문서에도 결정이 없다** |
| **막고 있나** | ❌ **미결정.** 선택지가 서로 다른 사고로 이어진다 |

| 전략 | 위험 | 우리 문맥 |
|---|---|---|
| `IDENTITY` (auto_increment) | A1 경합(8.0 기본값이 완화) · **INSERT 전 ID를 모른다** | K-1/K-2가 **계좌ID 해시로 파티션 판정**을 요구한다. 계좌ID가 DB 채번이면 **저장 전에 파티션을 못 정한다** |
| `SEQUENCE` | **C1 풀 데드락**(채번 커넥션) — pooled-lo로 완화 | W-1(ORM 단일 경로)을 지켜도 채번은 별도 커넥션 |
| **애플리케이션 채번**(UUID/ULID/스노플레이크) | 랜덤 UUID면 **클러스터드 인덱스 단편화**와 버퍼풀 히트 저하 | ★ **K-1·K-2와 가장 잘 맞는다** — ID가 앱에 있으므로 파티션 판정이 저장 전에 가능하고, HA-3 멱등에도 유리 |

---

## 3. ★ 우리가 뚫려 있는 것

> 순서는 **자금 사고로 이어지는 거리**순이다.

### 3.1 낙관적 락이 ADR 규칙이 아니다 — W-5가 없다 (O1)

```
ADR-007 W-1  "E1~E5 안에서 ORM 외의 DB 접근을 하지 않는다"
             ↓
             Jepsen이 지목한 load → modify → save → commit 패턴을 의무화한다
             그 패턴은 MySQL 8.0.34 RR에서 lost update 198건/9,048 트랜잭션

방어 장치     account.md §8 "계좌 단위 낙관적 락(버전) + 충돌 시 재시도"
              card.md §8    "카드 단위 낙관적 락"
              → 애그리게이트 문서에만 있다. ADR 규칙에 없다.
              → ADR-007 §4의 강제 수단 3종은 전부 "JDBC를 못 쓰게" 만드는 것이고
                 버전 컬럼 누락을 잡는 수단은 하나도 없다
```

**왜 이것이 1순위인가**: `@Version` 누락은 **컴파일도 아키텍처 테스트도 통과하고**, 승인 성공률도 안 떨어지고, 부하가 낮을 땐 재현도 안 된다. 그리고 발현 형태가 **초과 승인**이다 — Phase 2가 열 라운드에 걸쳐 막은 바로 그 사고.

**제안**: `W-5 — E1~E5가 변경하는 모든 애그리게이트는 낙관적 락 버전을 갖는다`. 강제 수단은 ADR-007 §4와 같은 층위여야 한다 — **아키텍처 테스트가 "E1~E5 참여자 목록의 모든 애그리게이트에 버전 필드가 있는지"를 조작 대장에서 읽어 검사**한다(대장은 이미 기계 판독이다).

### 3.2 락 순서 ①~⑤ 를 DB가 그 순서로 잠그지 않는다 (L4 · L2)

README는 락 순서를 **① 미수 → ② 승인 → ③ 계좌 → ④ 카드 → ⑤ 배치·멱등·정산** 으로 못 박았다. 방향은 MySQL 공식 권고와 같다. **문제는 세 가지다.**

**(a) 낙관적 락이면 락 순서는 개발자가 정하지 못한다.**

낙관적 락에서 실제 행 잠금은 **커밋 시점 flush의 UPDATE 순서**에 발생한다. 그 순서는 Hibernate `ActionQueue` 가 정하고(대략 insert → update → delete, 같은 타입 안에서는 삽입 순서), **문서화된 계약이 아니다.** 즉 README의 ①~⑤ 는 *"코드에서 도메인 메서드를 부르는 순서"* 를 규율할 뿐 **DB 락 순서를 규율하지 못한다.**

> ★ 이것을 강제하려면 **경계 진입 시 `SELECT ... FOR UPDATE` 를 ①~⑤ 순서로 명시 획득**해야 한다. 그러면 락 순서는 지켜지지만 **비관적 락으로 바뀌어** 승인 경로 처리량이 달라진다. **둘 중 하나를 고르는 결정이 없다.**

**(b) E2·E5가 락 순서를 구조적으로 위반한다.**

```
E2 = 승인 · 계좌 · 카드 · 매입배치 · (부족 시) 미수
락 순서상 미수는 ① 이다. 그런데 —

Account.capture():
   1) holdTotal -= heldAmount
   2) balance >= captureAmount 인가?     ← ★ 계좌(③)를 읽어야 안다
   3) 부족하면 Receivable.incur(...)      ← 그제서야 미수(①)를 건드린다

즉 "미수를 잡을지 여부"가 계좌 락을 쥔 뒤에야 결정된다 → ③ 다음에 ①
E5(reverseDeposit)도 동일: 잔액 감액 후 부족분을 Receivable.incur
```

E2/E5의 `incur` 는 **INSERT**이므로 기존 행 락이 아니라 **insert intention 갭 락**을 만든다. 그리고 E3/E4는 같은 계좌의 미수를 **FIFO 범위 스캔**한다 → RR이면 next-key 락. **L2(ideeli)의 DELETE/INSERT 갭 충돌과 동일한 구조**다.

**(c) 미수 다건 잠금이 정렬 순서로 안 잡힌다.**

README: *"FIFO 정렬 키가 락 순서 키를 겸한다"*, *"E4는 자기 미수와 회수 대상 미수를 함께 전순서로 선점한다"*. 전순서는 `(incurredBusinessDate, receivableId)` 인데 **PK는 `receivableId`** 다.

- `UPDATE receivable ... WHERE receivableId IN (...)` → **PK 순서**로 잠근다
- E3의 FIFO 처리 → `(incurredBusinessDate, receivableId)` 순서를 의도

**두 순서가 다르면 E3과 E4가 서로 다른 순서로 같은 미수 집합을 잠근다 → 데드락.** 강제하려면 `(incurredBusinessDate, receivableId)` 복합 인덱스로 `ORDER BY ... FOR UPDATE` 하거나 **건별로 정렬 순서대로 N번 잠가야** 한다.

### 3.3 격리 수준이 결정되지 않았다 (I1 · I2 · L2 · T1)

기본값 RR이 그대로 적용되면 **네 사례가 동시에 걸린다**. 그리고 우리가 원하는 방향이 **경로마다 반대다**:

| 경로 | 원하는 것 | 왜 |
|---|---|---|
| **E3·E4 미수 회수** | **RR + `FOR UPDATE`** (갭 락 필요) | I1 — 팬텀 미수가 FIFO 순서와 RC-2를 깬다 |
| **E2 매입 배치 / E5** | **RC** (갭 락 방해) | L2 — 대량 INSERT가 범위 락과 충돌 |
| **대사 배치 읽기** | **RC** | T1 — RR 롱 읽기가 undo purge를 막는다 |
| **E1 승인** | 어느 쪽이든 **명시적 잠금 필수** | O1 — 두 격리 모두 lost update를 안 막는다 |

★ **"기본값이니까"로 남겨두면 가장 비싼 조합(RR + 잠금 없음)이 된다.**

### 3.4 대사 배치가 롱 트랜잭션이다 — ADR-011이 스스로와 충돌한다 (T1)

```
ADR-011 §2   안 C(전 계좌를 한 읽기 트랜잭션으로)를
             "long transaction · 파티션 병렬 불가" 로 기각

ADR-011 §1   그런데 M9·M10·M11 을 "코어 안, 한 읽기 트랜잭션" 이라고 적었다
             M15(정산 합계)도 "코어 안"

→ 기각한 안 C가 대사 경로로 되돌아왔다
→ RR 롱 읽기 트랜잭션이 undo purge 를 막는다 (Percona: HLL 6,000,000)
→ 다음 날 승인 SELECT 가 느려진다 → BR-01 3초 초과 → 망취소 증가
→ 망취소는 품질 속성 §0이 지목한 "정합성 사고의 최대 입구"
```

**막는 법**: 대사를 **계좌 파티션 단위 짧은 트랜잭션 N개**로 쪼갠다(K-4가 이미 *"파티션 완료 후 단일 단계"* 를 요구하므로 파티션 안이 짧으면 된다) + 대사 읽기를 **RC**로 + **`History list length` 를 QS-04 탐지 지표에 편입**.

### 3.5 중복 키 INSERT 데드락 — 망취소가 정상 경로인데 (L3)

BR-01은 망취소를 **정상 경로**로 규정했다. 망취소·재시도는 **같은 키로 여러 세션이 동시에 INSERT** 하는 패턴이고, MySQL 8.0 공식 문서가 그 패턴에서 **S락 승격 실패로 데드락**이 난다고 명시한다.

**양의 피드백이 위험하다**: 데드락 → 재시도 → 지연 → BR-01 5초 초과 → **매입사가 또 망취소** → 세션 증가 → 데드락 증가.

**막는 법**: 멱등 키를 **PK**로(유니크 세컨더리 인덱스면 next-key 락) · `INSERT ... ON DUPLICATE KEY UPDATE` 대신 **INSERT 시도 → 중복 예외를 멱등 히트로 해석** · 지수 백오프.

### 3.6 커넥션 풀·자원 분리 규칙이 없다 (C2 · C3 · C4)

- ADR-007은 조회·배치를 *"자유"* 로 두었고, **어느 풀을 쓰는가**를 정하지 않았다.
- ADR-009 K-3(*"파티션 수는 설정값"*)에 **상한 근거가 없다**. C4(풀을 줄이면 50배 빨라진다)가 상한이 존재함을 보여준다.
- GitHub는 이 조합으로 8시간 14분을 잃었고, ADR-007 되돌리기 조건 **R2**(*"조회 부하가 쓰기 경로를 침해"*)가 정확히 이 상황이다 — **R2가 발화하는 것을 감지할 지표가 없다.**

### 3.7 멱등의 근거가 단일 DB 유니크 제약이라는 사실이 안 적혀 있다 (R1)

HA-3은 *"모든 자금 경로가 멱등이다"* 라고만 적는다. 실제 멱등 장치는 `IdempotencyRecord`·`DepositReceipt`·`promoteIsolated` 이고, **셋 다 DB 유니크 제약에 의존**한다. GitHub 2018처럼 **DB가 split-brain되면 유니크 제약이 아무것도 막지 못한다.**

지금은 단일 DB라 발현하지 않는다. 그러나 HA-5와 같은 성격이다 — **다중화하는 순간 열리고, 그때는 못 고친다.**

### 3.8 스키마 변경의 **실행 방법**이 없다 (L1 · M1 · M2)

HA-5는 *"무엇을 바꾸는가"*(expand-contract)만 정하고 *"어떻게 바꾸는가"*를 정하지 않았다. 네이티브 INPLACE는 **복제본에서 논블로킹이 아니고**(M1), 트리거 기반 OSC는 **DB 전체를 락다운시킬 수 있다**(L1). K-1의 계좌ID 백필을 프로덕션에서 대량 UPDATE로 돌리면 **3.4의 롱 트랜잭션**으로 직행한다(M2가 오프라인 백필을 쓴 이유).

### 3.9 ✅ 반대로, 잘 막고 있는 것

| # | 무엇 | 무엇이 막나 |
|---|---|---|
| ① | **HikariCP 커넥션 2개 데드락(C1)** | **W-1** — 자금 경로에 JDBC 접근 수단 자체가 없으므로 두 번째 커넥션이 생길 수 없다. 모듈 분리(컴파일) + 아키텍처 테스트 + 데이터소스 분리 |
| ② | **복제 지연으로 인한 초과 승인(R1·C2 방향)** | **W-2 + HA-1** — 자금 판단이 복제본을 아예 안 본다. *"복제 지연이 정합성에 닿지 않는다"* |
| ③ | **flush 타이밍(ORM/JDBC 혼용)** | **W-1** — 혼용을 금지하면 발생할 수 없다. 규약이 아니라 구조 |
| ④ | **lazy close의 expand 안전성(M1)** | **ADR-011 Q-1 + R2** — 신설 필드 둘 다 nullable, *"`lastClosedBusinessDate < 대상 영업일`이면 `balance`를 쓴다"* 가 구/신 동시 가동을 이미 처리. **교과서적 expand-contract** |
| ⑤ | **나중에 못 하는 스키마 결정(M1)** | **K-1** — *"지금 안 하면 나중에 못 한다"*. INSTANT DDL로는 컬럼 추가만 되고 **선행 키 인덱스 추가는 INPLACE 전면 리빌드**라는 사실이 이 판단을 뒷받침한다 |
| ⑥ | **롱 트랜잭션(안 C)의 정면 기각** | **ADR-011 §2** — *"long transaction · 파티션 병렬 불가"* 로 기각한 판단 자체는 옳다(§3.4는 그 판단이 §1에서 새어 들어온 것을 지적하는 것) |
| ⑦ | **AUTO-INC 직렬화(A1)** | MySQL 8.0 기본 `innodb_autoinc_lock_mode=2` |
| ⑧ | **정합성 vs 가용성 상충 판정** | GitHub 2018의 *"data integrity over site usability"* 와 **같은 결론**을 이미 내렸다 |

---

## 4. 실험 시나리오 (Phase 5 주입 목록)

> 각 시험은 **주입 → 관측 지표 → 통과 기준** 을 갖는다. 통과 기준은 기존 ADR 검증 표와 연결한다.

| # | 대상 | 주입 | 관측 | 통과 기준 |
|---|---|---|---|---|
| **X-1** | §3.1 낙관적 락 | 계좌/카드에서 `@Version` 제거 · 같은 계좌 동시 승인 200 세션 | 초과 승인 건수 · RC-1/RC-3 등식 | ★ **버전 있으면 0건, 없으면 >0건이 나와야 한다.** 둘 다 0이면 시험이 무의미(부하 부족) — ADR-007 §6 *"동시 승인 시험"* 을 이렇게 구체화 |
| **X-2** | §3.1 팬텀(PRE-2) | 승인이 *"미결 미수 없음"* 조회를 마친 뒤 커밋 전에, 다른 세션이 같은 계좌에 미수 INSERT+커밋 | 승인 성립 여부 | 승인이 **거절**되거나, 성립한다면 **그 위반을 탐지하는 장치**를 지목할 수 있어야 한다 (현재는 M9~M11 어디에도 안 걸린다) |
| **X-3** | §3.2 락 순서 | E2(매입 배치, 미수 INSERT) ∥ E3(입금, 미수 FIFO 범위 스캔) 을 같은 계좌에 동시 | `innodb_print_all_deadlocks=ON` 로그 · `insert intention waiting` | 데드락 0건. 발생하면 **락 순서 ①~⑤ 가 DB 수준에서 안 지켜진다는 증거** |
| **X-4** | §3.2(c) 정렬 | E3(FIFO 순)과 E4(회수 대상 다건)를 같은 미수 집합에 동시 | 데드락 · 잠금 순서 | `SHOW ENGINE INNODB STATUS` 의 두 트랜잭션이 **같은 순서**로 미수를 잠갔는가 |
| **X-5** | §3.3 격리 | 격리 수준을 RR / RC 로 바꿔가며 X-1·X-3·X-6 을 반복 | 각 시험 결과의 차이 | 경로별 격리 수준 결정의 **실측 근거**를 만든다 |
| **X-6** | §3.4 롱 트랜잭션 | 대사 배치(M9·M10·M11·M15) 실행 중 승인 400 TPS 유지 | `History list length` 1초 샘플 · 승인 p99 · undo 테이블스페이스 크기 | HLL이 배치 종료 후 **원복**되고, 배치 중 승인 p99가 **BR-01 3초 이내** |
| **X-7** | §3.5 멱등 데드락 | 같은 `correlationId` 로 동시 3 / 10 / 50 세션 승인 | 데드락 건수 · 에러율 · p99 | 데드락 0건 또는 **재시도로 100% 흡수**되고 p99 3초 이내 |
| **X-8** | §3.6 풀 분리 | 배치 병렬도(K-3)를 1→2→4→8→16 상향, 승인 400 TPS 병행 | 배치 처리 시간 · 승인 p99 · 풀 대기 | ★ **처리 시간이 더 안 줄고 p99만 오르는 지점 = K-3 상한.** 이 값을 문서화 (ADR-009 §7 *"파티션 수를 늘리면 처리 시간이 준다"* 를 **상한까지** 확장) |
| **X-9** | §3.6 조용한 축소 | 부팅 시 `LimitNOFILE` · `max_connections` · `innodb_autoinc_lock_mode` · `transaction_isolation` 실측값을 로그로 남기고 기대값과 대조 | assert 실패 | GitHub가 4개월 놓친 *"프로세스 매니저가 조용히 65536으로 줄였다"* 를 **부팅 스모크에서** 잡는다 |
| **X-10** | §3.8 DDL | 승인 400 TPS 중 승인 테이블에 `ALTER TABLE ... ADD INDEX`(INPLACE) | 복제 지연 · 승인 p99 · 메타데이터 락 대기 | 복제 지연이 마이그레이션 시간만큼 늘어나는지 실측 → **도구 선택(gh-ost 등)의 근거** |
| **X-11** | ADR-007 §6 | 복제 지연을 인위적으로 크게(예: 60초) 주입 | 승인 판단 결과 | ADR-007 검증표 그대로 — **지연을 키워도 결과 불변** |
| **X-12** | §3.7 멱등 근거 | (다중화 시점으로 이월) DB를 분리한 상태에서 같은 `correlationId` 를 양쪽에 전송 | 이중 승인 | 지금은 재현 불가. **ADR-004 R1 착수 시 필수 항목**으로 등재 |

---

## 5. 못 찾은 것 / 출처 없음

### 5.1 1차 출처를 찾지 못한 것 — 본문에서 사례로 쓰지 않았다

| 찾으려 한 것 | 상태 |
|---|---|
| **국내 기업의 공개 DB 포스트모템** (토스·카카오·네이버·라인·쿠팡·당근의 *장애 보고서*) | ❌ 국내 기업 블로그는 **기법 공유**는 많으나 GitHub 형식의 **포스트모템 공개가 거의 없다.** 확보한 국내 1차 출처는 우아한형제들 HikariCP(C1)·카카오뱅크 복제(R2)·토스 코어뱅킹(아래) 3건 |
| **N+1이 단독으로 일으킨 실장애의 회사 공개 포스트모템** | ❌ 검색 결과는 전부 **교육용 블로그/미디엄 글**이었고 회사명·날짜·영향 시간이 있는 1차 출처가 없었다. **본문에서는 O2(GitHub 2020-02-27, 쿼리 패턴 변경 → 4시간 23분)로 대체**했다 |
| **당근 테크 블로그 "MySQL Gap Lock (두번째 이야기)"** (Sunguck Lee) | ⚠️ URL은 확인했으나 **Medium이 본문을 반환하지 않아 내용을 인용하지 못했다.** https://medium.com/daangn/mysql-gap-lock-두번째-이야기-49727c005084 — 갭 락 국내 사례로 후속 확인 필요 |
| **if(kakao) / DEVIEW / Percona Live 의 DB 장애 세션** | ⚠️ if(kakao) dev 2022는 **데이터센터 화재** 대응이 주제로, DB 락/트랜잭션 사고가 아니다. DEVIEW·Percona Live에서 조건에 맞는 세션을 특정하지 못했다 |
| **Shopify의 DB 장애 포스트모템** | ❌ 검색으로 확보하지 못했다 |
| **MySQL 9.0+ 에서 기본 격리 수준 변경 여부** | ✅ **변경 없음을 확인** — 8.0·8.4·9.x 모두 `REPEATABLE READ` 기본 |
| **Percona 글 2건의 게시 연도** (T1 · I1) | ⚠️ 본문에서 게시일을 확인하지 못했다. 표와 상세에 **연도 미확인**으로 명시했다 |
| **ideeli 사고의 정확한 발생 연도** | ⚠️ 글은 MySQL **5.1.34**(2009년 업그레이드 언급) 기준이다. 본문의 "2013"은 블로그 게시 시점 추정이며 **확정 아님** |

### 5.2 확보했으나 본문 사례 번호를 주지 않은 참고

| 출처 | 왜 |
|---|---|
| 토스, **"은행 최초 코어뱅킹 MSA 전환기 (feat. 지금 이자 받기)"**, SLASH 23 https://toss.tech/article/slash23-corebanking | **장애 사례가 아니라 성공 사례**다. 다만 우리와 구조가 같아 §5.3에 별도로 적는다 |
| 우아한형제들, **"Aurora MySQL를 운영하면서 알면 좋을 것 같은 미세한 팁"**, 2019 https://techblog.woowahan.com/2653/ | 페일오버 후 **캐시 워밍**이 동작하지 않으면 *"굉장히 바쁜 DB였다면 전체 응답시간이 떨어져 장애로 이어질 수 있는"* 상황을 다룬다. 구체적 사고 서술이 아니라 운영 팁 |
| 우아한형제들, **"MySQL을 이용한 분산락으로 여러 서버에 걸친 동시성 관리"** https://techblog.woowahan.com/2631/ | **HA-2**(배치·스케줄러 단일 실행 보장)의 구현 참고. 사고 사례는 아니다 |
| youngju.dev, **"커넥션 풀 크기, 크게 잡으면 손해인 이유"** / **"데드락 진단과 예방"**, 2026-07-26 | 개인 블로그. C4·L4의 **보조** 근거로만 썼고 1차 출처(HikariCP wiki·MySQL 문서)를 병기했다 |

### 5.3 ★ 토스 코어뱅킹 — 우리와 가장 가까운 국내 사례 (장애가 아니라 대조군)

> 출처: 토스, **"은행 최초 코어뱅킹 MSA 전환기 (feat. 지금 이자 받기)"**, SLASH 23 (2023)
> https://toss.tech/article/slash23-corebanking

- **계좌 단위 현재 잔액 데이터에 대해서만** 고유하게 **Row Locking** — *"데드락과 성능 저하를 방지"*
- 트랜잭션2가 트랜잭션1 완료까지 **대기**하되 **합리적 타임아웃**으로 고객이 락을 인지하지 못하게
- **온라인 검증**(기존 코어뱅킹 vs 새 MSA 결과 실시간 비교) + **배치 대량 검증** 병행, 불일치 시 알람
- 결과: 170배 성능 개선

| 우리와 비교 | |
|---|---|
| **같은 것** | 계좌 잔액이 직렬화 지점 · 트랜잭션 경계를 계좌로 좁힘 · **사후 대사로 정합성 검증**(우리 BR-41 · M9~M15) |
| **다른 것** | ★ 토스는 **비관적 Row Lock + 타임아웃**, 우리는 **낙관적 락 + 재시도**(`account.md` §8). **Jepsen(O1) 관점에서 둘 다 유효하지만 실패 모드가 다르다** — 비관적은 대기/타임아웃, 낙관적은 재시도 폭풍. §3.2(a)에서 지적한 *"락 순서를 강제하려면 비관적으로 가야 한다"* 와 이어진다 |
| **가져올 것** | **이중 검증**(온라인 비교 + 배치 비교). 우리 M9~M15는 배치 비교만 있다 |

---

## 부록. 출처 일람

**공식 문서 (MySQL 8.0 / 8.4 / 9.x)**
- [§17.7.3 Locks Set by Different SQL Statements in InnoDB (8.0)](https://dev.mysql.com/doc/refman/8.0/en/innodb-locks-set.html)
- [§17.7.5 How to Minimize and Handle Deadlocks (8.0)](https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks-handling.html)
- [§17.7.2.1 Transaction Isolation Levels (8.4)](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [§17.6.1.6 AUTO_INCREMENT Handling in InnoDB (9.1)](https://dev.mysql.com/doc/refman/9.1/en/innodb-auto-increment-handling.html)
- [§10.11.4 Metadata Locking (8.0)](https://dev.mysql.com/doc/refman/8.0/en/metadata-locking.html)
- [MySQL Bug #16979 — AUTO_INC lock works as table level lock](https://bugs.mysql.com/bug.php?id=16979)
- [MySQL Bug #52663 — Lost update under READ COMMITTED](https://bugs.mysql.com/bug.php?id=52663)

**포스트모템 · 기업 기술 블로그**
- [GitHub — October 21 post-incident analysis (2018)](https://github.blog/news-insights/company-news/oct21-post-incident-analysis/)
- [GitHub — February service disruptions post-incident analysis (2020)](https://github.blog/2020-03-26-february-service-disruptions-post-incident-analysis/)
- [GitHub — gh-ost: GitHub's online schema migration tool for MySQL (2016)](https://github.blog/news-insights/company-news/gh-ost-github-s-online-migration-tool-for-mysql/)
- [OpenAI — Postmortem: Feb 20, 2023 DB outage](https://community.openai.com/t/postmortem-feb-20-2023-openai-suffered-a-major-db-outage/73068)
- [Stripe — Online migrations at scale (2017)](https://stripe.com/blog/online-migrations)
- [우아한형제들 — HikariCP Dead lock에서 벗어나기 (이론편) (2020)](https://techblog.woowahan.com/2664/)
- [우아한형제들 — HikariCP Dead lock에서 벗어나기 (실전편) (2020)](https://techblog.woowahan.com/2663/)
- [우아한형제들 — Aurora MySQL를 운영하면서 알면 좋을 것 같은 미세한 팁 (2019)](https://techblog.woowahan.com/2653/)
- [우아한형제들 — MySQL을 이용한 분산락으로 여러 서버에 걸친 동시성 관리](https://techblog.woowahan.com/2631/)
- [바이라인네트워크 — 카카오뱅크는 어떻게 MySQL로 데이터 유실을 막았을까 (2017)](https://byline.network/2017/10/17-6/)
- [토스 — 은행 최초 코어뱅킹 MSA 전환기 (SLASH 23)](https://toss.tech/article/slash23-corebanking)
- [ideeli — Diagnosing MySQL AUTO-INC and Gap Locks (2013)](http://blog.9minutesnooze.com/diagnosing-mysql-autoinc-gap-locks-ideeli-tech-blog/)

**분석 · 벤더**
- [Jepsen — MySQL 8.0.34 (2023-12)](https://jepsen.io/analyses/mysql-8.0.34)
- [Percona — Chasing a Hung Transaction in MySQL: InnoDB History Length Strikes Back](https://www.percona.com/blog/chasing-a-hung-transaction-in-mysql-innodb-history-length-strikes-back/)
- [Percona — Innodb transaction history often hides dangerous 'debt' (2014)](https://www.percona.com/blog/2014/10/17/innodb-transaction-history-often-hides-dangerous-debt/)
- [Percona — What if … MySQL's Repeatable Reads Cause You to Lose Money?](https://www.percona.com/blog/what-if-mysqls-repeatable-reads-cause-you-to-lose-money/)
- [Percona — InnoDB auto-inc scalability fixed (2007)](https://www.percona.com/blog/2007/09/26/innodb-auto-inc-scalability-fixed/)
- [Percona — InnoDB Gap Locks](https://www.percona.com/blog/innodbs-gap-locks/)
- [PlanetScale — The State of Online Schema Migrations in MySQL (2024)](https://planetscale.com/blog/state-of-online-schema-migrations-in-mysql)
- [HikariCP — About Pool Sizing (문서 논의 스레드)](https://github.com/brettwooldridge/HikariCP/issues/1171)
- [youngju.dev — 데드락 진단과 예방 (2026)](https://www.youngju.dev/blog/database/2026-07-26-deadlock-debugging-prevention)
- [youngju.dev — 커넥션 풀 크기, 크게 잡으면 손해인 이유 (2026)](https://www.youngju.dev/blog/database/2026-07-26-connection-pool-sizing)

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v0.1 | 2026-08-05 | 최초 작성 — 8개 유형 20개 사례를 1차 출처로 수집하고 E1~E5 · W-1~W-4 · K-1~K-4 · HA-1~HA-5에 대조. ★ 뚫린 자리 8건 식별(그중 **W-5 낙관적 락 규칙 부재**, **락 순서의 DB 수준 미강제**, **격리 수준 미결정**, **ADR-011 §1↔§2 롱 트랜잭션 자기모순**이 자금 사고에 가장 가깝다). 잘 막고 있는 자리 8건도 함께 기록 — 특히 **W-1이 우아한형제들 HikariCP 사고를 구조적으로 막는다**는 것이 ADR-007의 예상 밖 이득 |
