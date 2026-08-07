# 개발 평가 축 (개별 문서)

> 각 축을 **"무엇을 지키는 활동인가"**로 정의하고, 자기 경험을 그 언어로 번역하기 위한 세트.

---

## 문서 목록

| 축 | 문서 | 지키는 것 | 실패하면 |
|---|---|---|---|
| **Concurrency** | [concurrency.md](./concurrency.md) | 정확성 | 데이터가 조용히 틀린다 |
| **Scalability** | [scalability.md](./scalability.md) | 성장 여력 | 트래픽이 늘면 못 버틴다 |
| **Availability** | [availability.md](./availability.md) | 연속성 | 일부 고장이 전체 중단이 된다 |
| **Performance** | [performance.md](./performance.md) | 속도 | 느리다 (동작은 한다) |
| **System Design** | [system-design.md](./system-design.md) | 변경 비용 | 기능 추가가 갈수록 비싸진다 |
| **Maintainability** | [maintainability.md](./maintainability.md) | 인수인계 가능성 | 아무도 못 고친다 |
| **UX** | [ux.md](./ux.md) | 사용 가능성 | 동작은 하는데 쓰기 싫다 |

**종합·트레이드오프**: [`../08-engineering-axes-deep.md`](../08-engineering-axes-deep.md)

---

## 먼저 정리할 혼동 3가지

### ① Concurrency ≠ Performance
동시성은 "빠른가"가 아니라 **"틀리지 않는가"**다.
락을 걸면 오히려 느려진다. 성능을 위해 락을 푸는 게 아니라, **정확성을 위해 성능을 내주는** 것.

### ② Scalability ≠ Performance
요청 1건이 10ms인 건 성능. 요청이 10배 와도 10ms인 건 확장성.
**단일 요청이 아무리 빨라도 수평 확장이 막혀 있으면 확장성은 0이다.**

### ③ Availability ≠ Scalability
레플리카 3대는 둘 다에 기여하지만 목적이 다르다.
확장성은 **부하 분산**, 가용성은 **대체 가능성**. 부하가 없어도 가용성을 위해 레플리카가 필요하다.

---

## 축 사이의 트레이드오프

**축은 독립적이지 않다. 하나를 올리면 다른 게 내려간다.**

| 충돌 | 내용 |
|---|---|
| Concurrency ↔ Performance | 락은 정확성을 사고 처리량을 판다 |
| Consistency ↔ Availability | 분단 시 정합성을 지키면 요청을 거절해야 한다 (CAP) |
| Scalability ↔ Consistency | 복제·샤딩은 최종적 일관성을 부른다 |
| Performance ↔ Maintainability | 캐시·비정규화는 복잡도를 늘린다 |
| Availability ↔ 비용 | 9 하나에 비용 한 자릿수 |
| System Design ↔ 개발 속도 | 미리 쪼개면 오버엔지니어링, 안 쪼개면 나중에 비쌈 |
| UX ↔ Consistency | 낙관적 업데이트는 잠깐 거짓말을 한다 |

> **좋은 답변**: "A를 위해 B를 얼마만큼 내줬고, 그 판단 근거는 C였습니다."
> **나쁜 답변**: "성능도 좋고 확장성도 좋고 유지보수도 좋게 만들었습니다."

---

## 경계는 깔끔하지 않다 (교차 번역)

면접에서 "그건 제 영역이 아니라서요"로 선을 긋기보다, 각 축을 자기 도메인 언어로 번역하는 게 훨씬 강하다.

| 축 | 백엔드 버전 | 프론트 버전 |
|---|---|---|
| Concurrency | 행 락, 격리 수준, 멱등성 키 | 응답 경쟁 상태, 요청 취소, 중복 제출 |
| Availability | 이중화, failover, 서킷 브레이커 | CDN, 오프라인 캐시, API 실패 시 폴백 UI |
| Scalability | 샤딩, 복제 | 가상 스크롤, 페이지네이션, 점진적 로딩 |
| **UX** | **p99 지연, 에러 응답 설계, 멱등성** | 인터랙션 반응성 |
| Maintainability | 계층 분리, 관측성 | 컴포넌트 경계, 디자인 토큰 |

**특히 기억할 두 가지**
- **백엔드 p99는 그대로 UX다**
- **프론트에도 동시성이 있다**

---

## 자기 경험 번역 템플릿

> **[상황]** 어떤 규모/제약에서
> **[축]** 어떤 축의 문제였고
> **[선택]** 무엇을 골랐고
> **[대가]** 무엇을 내줬고
> **[측정]** 어떻게 확인했는가

### 자기 점검 매트릭스
프로젝트별로 채워보고, **빈칸이 곧 다음 공부 주제이자 예상 질문**이다.

| 축 | 내 사례 | 측정한 수치 | 내준 대가 |
|---|---|---|---|
| Concurrency | | | |
| Scalability | | | |
| Availability | | | |
| Performance | | | |
| System Design | | | |
| Maintainability | | | |
| UX | | | |

> **모든 칸을 채운 시스템은 없다.** 안 한 것을 "안 했다"가 아니라 **"이런 이유로 안 했다"**로 말할 수 있으면 그게 더 좋은 답이다.

---

## 심화로 가는 길

| 축 | 심화 문서 |
|---|---|
| Scalability | `../server-design/01, 03, 04, 09` |
| Availability | `../server-design/05, 06, 08` |
| Concurrency | `../05-kafka-consumer-failure.md`, `../06-outbox-vs-dispatch-log.md` |
| 전 축 실전 | `../server-design/10-playbook-by-symptom.md` |
