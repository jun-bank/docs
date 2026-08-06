# R4 — 소프트웨어 프로젝트 문서 "유형별" 작성 방법론 (딥 리서치)

> 조사 범위: jun-bank 워크플로우가 실제로 생산하는 문서 **유형** 6종. 개별 파일이 아니라 유형 단위.
> 조사 방법: WebSearch/WebFetch (2026-08). 각 절 = ⓐ 대표 방법론·원칙 / ⓑ 좋은 예·나쁜 예 / ⓒ [실무 의견]·논쟁 / ⓓ 출처.
> 주의: 본 문서는 L0 리서치 결과다. 여기서 도출된 규칙을 실제 템플릿에 반영할 때는 우리 문서 실물로 재확인해야 한다.

---

## 0. 전(全) 유형에 걸치는 상위 프레임 — Diátaxis

유형별 방법론을 논하기 전, "문서는 유형마다 다르게 써야 한다"는 주장 자체의 정본은 **Diátaxis**(Daniele Procida)다.
네 가지 사용자 니즈 → 네 가지 문서 형태로 분류한다.

| 형태 | 사용자 상태 | 축 |
|---|---|---|
| Tutorial (학습) | 초심자, 배우는 중 | 습득(acquisition) × 행동(action) |
| How-to guide (절차) | 이미 아는 사람이 일을 처리 중 | 적용(application) × 행동 |
| Reference (참조) | 사실을 조회 중 | 적용 × 인지(cognition) |
| Explanation (설명) | 이해를 넓히는 중 | 습득 × 인지 |

핵심 규칙 (how-to guide 기준, 우리 study/ 절차서·runbook에 직접 적용):
- **제목이 곧 목표**여야 한다. "How to integrate application performance monitoring" (○) vs "Application performance monitoring" (✗ — 무엇을 하는 글인지 안 보임).
- **순서(sequence)로 구성**한다. 실무적 필요 순서 + 독자의 사고 순서 둘 다 고려.
- **조건부 명령형(conditional imperative)** 을 쓴다: "If you want x, do y."
- **설명·역사·개념을 넣지 말라.** 필요하면 reference/explanation 문서로 링크. "Maintain focus on that goal."
- 독자를 **이미 유능한 사람**으로 가정한다(tutorial과의 결정적 차이).
- 피할 것: 도구 조작 나열(스위치 켜기·버튼 클릭), 사용성을 희생한 완전성, 설명으로의 이탈, 실제 문제는 분기하는데 선형 경로만 제시하는 것.
- Reference와의 차이: reference는 모든 옵션을 **빠짐없이**, how-to는 **불필요한 것을 일부러 뺀다**.

→ **우리 문서에의 함의**: "유스케이스 문서"와 "전문 규격서"는 reference 성격, "운영 절차서"와 "study 절차서"는 how-to 성격, "테스트 전략"은 explanation+reference 혼합이다. 한 파일에 두 형태를 섞으면 둘 다 나빠진다는 게 Diátaxis의 핵심 주장.

출처:
- https://diataxis.fr/
- https://diataxis.fr/start-here/
- https://diataxis.fr/how-to-guides/
- https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework

---

## 1. 유스케이스 문서

### ⓐ 대표 방법론 — Alistair Cockburn, *Writing Effective Use Cases* (2000)

정본. Jacobson이 유스케이스를 발명했다면 "어떻게 쓰는가"의 규범은 Cockburn이 세웠다. (Cockburn & Jacobson 공저 *Use Case Foundation* 문서도 있음.)

**(1) 목표 수준(goal level) — 3+2단계**

| 수준 | 표기 | 판별 기준 | 소요 |
|---|---|---|---|
| very high summary | 구름/`+`+ | 조직 전략 맥락 | — |
| **Summary** | 연/구름 `+` | 한 자리에서 못 끝냄. 여러 user-goal을 묶음 (예: "보험 계약 운용") | 수 시간~수개월 |
| **User goal** | 파도/바다 `!` 또는 표기 없음 | **Boss test**: 상사가 "그거 하느라 하루 보냈다"를 인정할 일인가. 한 자리(one sitting)에서 완료 | 분 단위 |
| **Subfunction** | 물고기 `-` | 단독 가치 없음, user-goal을 뒷받침 (예: "로그인", "금액 검증") | 초 단위 |
| too low | 조개 | 지나치게 세분 — 쓰지 말 것 | — |

작성 순서는 **middle-out**: user goal에서 시작 → 위로 summary → 아래로 subfunction.

**(2) 형식(precision level) — casual vs fully dressed**

- **Casual**: 본문이 한두 문단의 산문. 주 성공 시나리오와 대안/실패를 서술형으로 흘려 씀. 필드가 적음.
- **Fully dressed**: 필드 완비 + **번호 매긴 단계**. 확장이 주 시나리오에서 어디서 갈라지는지 번호로 고정되므로 대안 흐름 가독성이 좋다.
- 선택 기준(Larman의 반복형 요구공학 실무 수치): 첫 요구사항 워크숍에서 **전체 유스케이스의 약 10%(가장 중요·위험한 것)만 fully dressed**로 쓰고 나머지는 brief/casual. 폭 우선(breadth-first), 낮은 정밀도 → 높은 정밀도로 진행.
- Precision Level 2 = "use case brief" = 주 성공 시나리오만.

**fully dressed 템플릿 필드**: UC 식별자, 이름(능동 동사구), Primary Actor, Goal(Goal in Context), **Scope**, **Level**, Secondary Actors, Trigger, Preconditions, Stakeholders & Interests, **Main Success Scenario(MSS, 번호 단계)**, **Extensions**, Technology & Data Variations, Minimal Guarantee / Success Guarantee.

**(3) 단계(step) 작성 규칙 — 구체 규칙 수준**

- **주어-동사-목적어**의 단문. 각 단계마다 **행위자를 명시**한다("System validates…", "Customer provides…").
- **의도(intent)를 쓰고 동작(movements)을 쓰지 않는다.** "Customer provides address" (○) / "Customer clicks the Address tab and types…" (✗).
- 모든 단계는 **진행을 만들어야** 한다. 단계는 셋 중 하나여야 한다: ① 행위자 간 상호작용 ② 검증(validation) ③ 내부 상태 변경.
- **"check whether ~" 금지.** "System validates X"로 쓰고 실패는 **확장으로 뺀다**. 즉 `if`는 본문에 넣지 않는다 — 분기는 Extensions의 언어다.
- **MSS 이상적 길이 3~9단계.** 20단계 이상이면 유스케이스를 분해하라는 신호.

**(4) 확장(Extension) 작성 규칙 — 오류/확장 표를 읽기 좋게 쓰는 법**

- 번호 규칙: MSS 3단계의 확장 = **`3a`, `3b`**…, 그 하위 처리 단계 = **`3a1`, `3a2`**…. **`*a`** = "어느 단계에서든" 발생하는 조건(통신 두절, 세션 만료 등).
- **조건은 "탐지된 사실(detected fact)"로 적는다. 질문형 금지.**
  - ○ `3a. Invalid card number:`
  - ✗ `3a. Is the card valid?`
- 처리 단계는 조건 밑에 **들여쓰기**한다(조건 1줄 + 처리 n줄의 2단 구조가 표 가독성의 핵심).
- 각 확장은 반드시 셋 중 하나로 **끝난다**: ① MSS로 복귀(어느 단계로 rejoin하는지 명시) ② 별도의 성공 종료 ③ 실패 종료. — 끝을 안 적는 게 실무 최다 결함.
- **분량 역전이 정상**: fully dressed 예제에서 Extensions 절이 MSS보다 훨씬 길고 복잡하다. 확장이 텍스트의 대부분을 차지하는 게 정상이며, 성공·실패 양쪽 분기를 모두 담는다.

### ⓑ 좋은 예 / 나쁜 예

**나쁜 예 — Cockburn이 꼽는 흔한 오류**: UI를 설계함, 목표 수준을 잘못 잡음, primary actor 누락, stakeholder 이해관계 누락, 선언한 goal과 실제 steps가 어긋남.

**나쁜 예 — 실무 7대 실수 (Bridging the Gap)**:
1. **UI 세부 혼입** — "clicks the new account button". 문제는 두 가지: ① 버튼 이름이 실제 사용자 행위를 특정해주지 못해 오히려 **모호**해진다 ② 버튼/탭 이름이 바뀌면 유스케이스 대량 수정 → **유지보수 지옥**.
2. **시스템 응답 누락** — 사용자 단계만 있고 시스템이 무엇을 하는지 없다. 거의 모든 사용자 단계에 대응 시스템 행위를 적어라.
3. **기술 세부 혼입** — 데이터 요소·테이블·컴포넌트명·내부 트리거. 흐름이 끊기고 비즈니스 이해관계자·테스터가 못 읽는다. → 설계 문서/데이터 사전으로 분리.
4. **와이어프레임과 불일치** — 어느 쪽이 정본인지 모호해짐.
5. **대안/예외가 어디서 갈라지는지 불명** — 분기 지점과 복귀 지점을 반드시 기본 흐름 단계 번호로 지목.
6. **범위 밖 단계 포함** — 사전/사후조건 밖이거나 그 목표와 무관한 단계. 유스케이스를 쪼개라는 신호.
7. **용어 불일치** — "blog post / article / published content item"을 섞어 쓰면 개발팀이 서로 다른 개념으로 구현한다. → 용어집(glossary) 유지.

**좋은 예의 특징**: 읽힌다. Cockburn 본인의 기준 — "casual, readable use cases are still useful, whereas unreadable use cases won't get read." 즉 형식 완비보다 **가독성이 우선 기준**이다.

### ⓒ [실무 의견]·논쟁

- **[실무 의견]** *"fully dressed는 과하다" 진영*: Larman·Oracle 백서 계열은 10% 규칙(중요한 것만 fully dressed)을 제시. 전부 fully dressed로 쓰면 유지 비용이 가치를 넘는다.
- **[실무 의견]** *유스케이스 vs 유저스토리 논쟁*: 애자일 진영에서 유스케이스가 "무겁다"고 밀려났으나, Cockburn 진영 반론은 "유저스토리는 확장(예외 경로)을 담을 자리가 없다"는 것. 금융 도메인처럼 **예외 경로가 본질**인 영역에서는 확장 표가 유스케이스의 존재 이유다. → jun-bank처럼 오류/확장이 핵심인 도메인은 유스케이스 형식이 유리하다는 근거.
- **[실무 의견]** UI 세부 배제 원칙에 대한 반론: 와이어프레임이 있는 프로젝트에서는 유스케이스와 와이어프레임 중 **하나만 정본**이어야 하며, UI 흐름은 와이어프레임이 갖고 유스케이스는 의도만 갖는 분업이 실무 다수설.

### ⓓ 출처
- https://alistaircockburn.com/Use%20Case%20Foundation.pdf (Jacobson & Cockburn, Use-Case Foundation)
- https://www.ifi.uzh.ch/dam/jcr:00000000-25a0-3d08-0000-00000ce96422/weuc_extract.pdf (Writing Effective Use Cases 발췌)
- https://people.inf.elte.hu/molnarba/Informaciorendszerek_ELTE/Writing_effective_Use_cases_Cockburn.pdf (1999 초고 전문)
- https://kurzy.kpi.fei.tuke.sk/zsi/resources/CockburnBookDraft.pdf
- http://www.binaryphile.com/software-engineering/requirements/use-cases/2026/05/10/cockburn-use-cases-guide.html (규칙 요약 — 단계/확장 규칙 정리 우수)
- https://www.craiglarman.com/wiki/downloads/applying_uml/larman-ch6-applying-evolutionary-use-cases.pdf (Larman, 10% 규칙·precision level)
- https://www.oracle.com/technetwork/testcontent/gettingstartedwithusecasemodeling-133857.pdf
- https://www.ecs.csun.edu/~rlingard/COMP682/Lecture-12b%20Use%20Case%20Example.pdf (템플릿 + 3a/3a1 예시)
- https://www.bridging-the-gap.com/7-use-case-writing-mistakes/
- https://home.cs.colorado.edu/~kena/classes/6448/s05/lectures/lecture07-08.pdf
- https://www.modernanalyst.com/Careers/InterviewQuestions/tabid/128/ID/340/What-are-some-of-the-formats-used-for-writing-use-cases.aspx

---

## 2. 요구사항 문서 · 비즈니스 룰 문서

### ⓐ-1 대표 방법론 — Karl Wiegers, *Software Requirements* (3rd ed., Wiegers & Beatty)

**개별 요구사항 문장의 품질 특성 (6+)**: Correct(정확), Feasible(구현 가능), Necessary(필요 — 권한 있는 출처에서 유래), Prioritized(우선순위 부여), **Unambiguous(비모호)**, **Verifiable(검증 가능)**.
**요구사항 집합의 특성**: Complete, Consistent, Modifiable, Traceable.

정의 수준의 규칙:
- **Unambiguous**: "요구사항 문장의 독자는 오직 하나의 해석만 도출할 수 있어야 한다." 여러 독자가 읽어도 같은 해석에 도달해야 한다.
- **Verifiable**: "각 요구사항이 제대로 구현되었는지 확인할 **테스트나 검증 방법을 고안할 수 있는지** 확인하라." 고안이 불가능하면 그 문장은 요구사항이 아니다.

**금지어(주관적 형용사) 목록** — Wiegers가 명시적으로 나열:
`user-friendly, easy, simple, rapid, efficient, several, state-of-the-art, improved, maximize, minimize`

**작성 가이드라인**:
- 문장은 **짧게**, **능동태**로.
- 개발자 관점에서 다시 읽고 "이거 물어봐야 하나?" 싶으면 고쳐 쓴다.
- **개별적으로 테스트 가능**하게, **일관된 입도(granularity)** 로 쓴다.
- **접속사 금지 신호**: "and / or / and/or"가 보이면 요구사항 여러 개가 뭉쳐 있다는 뜻 — 쪼갠다.
- 같은 요구사항을 문서 여기저기에 **중복 서술하지 않는다**(수정 시 불일치 원천).
- 우선순위는 High/Medium/Low를 **고객 가치 × 비용 × 기술 위험**으로 판단.

### ⓐ-2 대표 방법론 — EARS (Easy Approach to Requirements Syntax)

Alistair Mavin 외, Rolls-Royce에서 제트엔진 제어 시스템의 감항 규정을 분석하며 개발. IEEE RE'09 발표. 자연어를 **살짝만 제약**해서(절 순서 고정 + 구조 키워드 어휘 한정) 모호성·막연함·불완전성을 줄인다.

일반형: **`WHILE <전제조건>, WHEN <트리거>, the <시스템명> SHALL <시스템 응답>`**

| # | 패턴 | 구문 | 예시 |
|---|---|---|---|
| 1 | **Ubiquitous** (항상) | `The <system> shall <response>` | "The mobile phone shall have a mass of less than XX grams" |
| 2 | **State-driven** (상태) | `While <precondition>, the <system> shall <response>` | "While there is no card in the ATM, the ATM shall display 'insert card to begin'" |
| 3 | **Event-driven** (사건) | `When <trigger>, the <system> shall <response>` | "When 'mute' is selected, the laptop shall suppress all audio output" |
| 4 | **Optional feature** (옵션) | `Where <feature is included>, the <system> shall <response>` | "Where the car has a sunroof, the car shall have a sunroof control panel" |
| 5 | **Unwanted behaviour** (원치 않는 동작) | `If <trigger>, then the <system> shall <response>` | "If an invalid credit card number is entered, then the website shall display 'please re-enter credit card details'" |
| 6 | **Complex** (복합) | `While <precondition>, When <trigger>, the <system> shall <response>` | "While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust" |

**구성 규칙**: 전제조건 0개 이상 / 트리거 0~1개 / **시스템명 정확히 1개** / 시스템 응답 1개 이상.
**성격**: 경량 — 교육 부담 최소, 전용 도구 불필요, 읽기 쉬움. 비영어권 작성자에게 특히 효과적이라고 저자가 주장. 안전 필수(safety-critical) 산업에서 채택.

→ **주목**: `If ~ then` 패턴이 **원치 않는 동작(오류·예외) 전용**으로 예약돼 있다. 정상 분기(`When`)와 오류 분기(`If`)를 키워드로 구분하는 것 — 우리 오류 코드/예외 규격 문장에 바로 쓸 수 있는 규칙.
→ 최근 동향: GitHub `spec-kit`에 EARS 통합 요청 이슈가 올라오는 등, LLM 기반 spec-driven development 도구권에서 EARS가 재조명되고 있음.

### ⓐ-3 비즈니스 룰 카탈로그 — Wiegers 분류 + Ronald Ross / RuleSpeak

**Wiegers의 비즈니스 룰 5분류**:

| 유형 | 정의 | 문서화 방식 |
|---|---|---|
| **Facts** (사실) | 어느 시점에 참인 업무 사실 | 단문. 예: "모든 컨테이너는 고유 바코드 식별자를 갖는다" |
| **Constraints** (제약) | 시스템/사용자의 행위를 제한 — 사내 정책 또는 법규 | 제약형 룰은 **역할-권한 매트릭스**로 적으면 간결 |
| **Action enablers** (행동 유발) | 특정 조건이 참이면 어떤 활동을 촉발 | if/then |
| **Inferences** (추론) | if/then 형태지만 then절이 **행동이 아니라 지식** | if/then |
| **Computations** (계산) | 산식 | 자연어로 쓰면 장황·혼란 → **수식 또는 규칙 표(decision table)** 로 |

핵심 원칙: **원자적 룰이 복합 룰보다 낫다** (하나의 복잡한 룰에 여러 룰을 합치지 말 것).
그리고 **비즈니스 룰 ≠ 요구사항**: 룰은 조직의 자산(시스템보다 오래 산다)이고, 요구사항은 그 룰을 시스템이 어떻게 강제하는가다 — 둘을 분리하고 **추적(traceability)** 으로 연결하는 것이 Wiegers 방식.

**Ronald G. Ross ("father of business rules")** — *The Business Rule Book*(1994), *Business Rule Concepts*(4th ed. 2013), *Principles of the Business Rule Approach*. Business Rules Manifesto의 저자이자 **RuleSpeak®** 공동 개발자.
- RuleSpeak = "비즈니스 룰을 간결하고 업무 친화적으로 표현하기 위한 **가이드라인 집합**"이며 엄격한 형식 언어가 아니라 **베스트 프랙티스**라고 스스로 규정.
- 목표 둘: ① 업무·IT 양측에 대한 표현의 명료성·일관성 ② 의사결정 기준과 조직 지식의 포착·표현·보존.
- 무료 실무자 키트 3종(다국어): **Basic RuleSpeak Do's & Don'ts (v2.2.5)**, **RuleSpeak Sentence Forms (v2.2.3)**, **RuleSpeak Tabulation of Lists (v1.0)**. ⚠️ 세부 문장형/키워드 목록은 이 PDF들을 받아야 확인 가능 — 본 리서치에서 원문 확보 실패(404). **[구현 검증] 대상**: RuleSpeak 정확한 키워드 세트(must/only/may 등)와 문장형은 원문 확인 후 인용할 것.
- Business Rules Manifesto의 정신: 룰은 **선언적(declarative)** 이어야 하고, 프로세스나 절차에 묻히지 않고 **독립적으로 관리**되어야 한다.

### ⓑ 좋은 예 / 나쁜 예

**나쁜 요구사항의 징후**(Wiegers 종합):
- 주관어 포함: "The system shall be user-friendly and respond rapidly."
- 접속사로 뭉침: "시스템은 A를 저장하고 B를 알림하며 C를 로깅해야 한다." → 3개로 분리.
- 검증 불가: "성능을 최대화해야 한다"(maximize).
- 출처 불명(Necessary 위반) — 누가 왜 요구했는지 추적 불가.
- 같은 요구사항이 여러 절에 반복 → 개정 시 불일치.

**좋은 비즈니스 룰의 징후**: 원자적, 선언적, 시스템 구현 방식을 언급하지 않음, 룰 ID로 요구사항에서 참조 가능, 계산·다중 조건은 표(decision table)로.

**좋은 요구사항 문장의 징후**: EARS 6패턴 중 하나에 딱 맞음, 시스템명이 하나, 테스트 케이스 이름이 문장에서 바로 나옴.

### ⓒ [실무 의견]·논쟁

- **[실무 의견]** *EARS는 과잉 형식주의인가*: 옹호측은 "훈련 30분, 도구 불필요"라며 비용 대비 효과를 주장. 비판측은 모든 문장을 `shall`로 강제하면 UI/UX·데이터 요구사항이 부자연스러워진다고 지적. 절충 실무는 **안전·계약·인터페이스 요구사항에만 EARS를 적용**하고 나머지는 자유서술.
- **[실무 의견]** *`shall` vs `must`*: EARS/항공우주 계열은 `shall`, 웹/IETF 계열은 RFC 2119의 `MUST`. 한 문서에서 **둘을 섞지 말 것**이 공통 조언.
- **[실무 의견]** *비즈니스 룰을 요구사항 문서에 인라인할 것인가, 별도 카탈로그로 뺄 것인가*: Wiegers/Ross는 **분리 + 추적** 주장(룰의 수명이 더 길다). 반론은 "카탈로그가 곧 아무도 안 읽는 유령 문서가 된다"는 것 — 분리하려면 **요구사항에서 룰 ID를 실제로 참조하는 관행**이 유지돼야 한다는 조건부 지지가 다수.
- **[실무 의견]** Wiegers의 "10 Requirements Traps" — 형식 규칙보다 **누가 요구사항을 소유하는가**가 실패 원인의 대부분이라는 관점. 문장 품질 규칙만으로는 안 된다는 유보.

### ⓓ 출처
- https://www.processimpact.com/articles/qualreqs.pdf (Wiegers, "Writing Quality Requirements", 1999 — 정본 아티클)
- https://www.cs.bgu.ac.il/~elhadad/se/requirements-wiegers-sd-may99.html (같은 글 HTML)
- https://www.oreilly.com/library/view/software-requirements-3rd/9780735679658/
- https://www.pearson.de/media/muster/ext/9780735679641.pdf (Software Requirements 3rd 발췌 PDF)
- https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md (책 요약 — 비즈니스 룰 5분류 상세)
- http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf (Wiegers, 10 Requirements Traps)
- https://medium.com/analysts-corner/identifying-and-documenting-business-rules-6e93978b1671 (Wiegers, 비즈니스 룰 식별·문서화)
- https://www.thebagirl.com/quality-criteria-for-requirements/
- https://alistairmavin.com/ears/ (EARS 공식 — 6패턴 정본)
- https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax
- https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20(EARS).pdf (Mavin & Wilkinson 원논문)
- https://www.iaria.org/conferences2013/filesICCGI13/ICCGI_2013_Tutorial_Terzakis.pdf (EARS 튜토리얼 v1.0)
- https://github.com/github/spec-kit/issues/1356 (EARS 통합 요청 — 최근 동향)
- https://www.rulespeak.com/en/ (RuleSpeak 공식)
- https://www.brcommunity.com/articles.php?id=b178 (Business Rules Manifesto 전문)
- https://www.brcommunity.com/articles.php?id=b128
- https://www.ronross.info/ , https://www.dataversity.net/contributors/ronald-g-ross-2/
- https://repository.immregistries.org/files/resources/58ffbcefe6977/aira_2017__4c__managing_business_rules__brsolutions__r__ross.pdf (Ross 강의자료)
- https://en.wikipedia.org/wiki/Business_rule

---

## 3. 테스트 전략 / 테스트 계획 문서

### ⓐ 대표 방법론

**(1) 전통·표준 계열 — IEEE 829 (Standard for Software Test Documentation)**

IEEE 829 test plan의 표준 목차(전 항목):
test plan identifier / introduction / **test items** / **features to be tested** / **features NOT to be tested** / approach / **item pass-fail criteria** / **suspension criteria and resumption requirements** / test deliverables / testing tasks / environmental needs / responsibilities / staffing and training needs / schedule / **risks and contingencies** / approvals.

IEEE 829-2008 기준으로 **전략(strategy)은 test plan의 하위 항목**이다.

**전략 vs 계획의 통상 구분**:
| | Test Strategy | Test Plan |
|---|---|---|
| 층위 | 조직/제품 수준 | 프로젝트 수준 |
| 성격 | 정적(static), 거의 안 바뀜 | 동적(dynamic), 프로젝트마다 다름 |
| 내용 | **무엇을·왜** — 목표, 테스트 레벨, 도구, 리스크 방법론 | **어떻게·누가·언제** — 범위, 접근, 자원, 일정 |

**(2) 맥락 주도 계열 — James Bach, Heuristic Test Strategy Model (HTSM) / Rapid Software Testing**

Bach의 정의(용어 재정의가 핵심 기여):
- **Test Plan** = "테스트 프로젝트를 이끄는 아이디어의 집합"
- **Test Strategy** = "테스트 **설계**를 이끄는 아이디어의 집합"
- **Test Logistics** = "전략을 수행하기 위해 자원을 배치하는 아이디어의 집합"
- ⇒ **Test Plan = Test Strategy + Test Logistics**
- 그리고 결정타: **"test plan 문서가 test plan을 담고 있다는 보장은 없다"** — 템플릿을 이해 없이 채우거나 상사를 만족시키려 쓴 문서는 실행 약속을 이행할 방법을 모른 채 쓰인 것.

**HTSM (v6.x) 구조** — 4대 guideword 영역:
1. **Project Environment** (프로젝트 요소 — 고객, 정보, 팀, 장비, 일정, 산출물)
2. **Product Elements** (제품 요소 — 구조, 기능, 데이터, 인터페이스, 플랫폼, 작업, 시간)
3. **Quality Criteria** (품질 기준 범주 — capability, reliability, usability, security, scalability, performance, installability, compatibility …)
4. **Test Techniques** (테스트 기법 — function, domain, stress, flow, scenario, claims, user, risk, automatic)
   → 이 넷이 상호작용해 **Perceived Quality(인지된 품질)** 를 만든다.

사용 지침: "casually 하게도, rigorously 하게도 쓸 수 있다. 어떤 소프트웨어에도 일반적으로 적용된다. **당신 조직 맥락에 맞게 수정하라.**" — 즉 HTSM은 템플릿이 아니라 **생각 누락 방지 체크리스트**다.

Bach의 문서화 철학: "나는 문서를 싫어하지 않는다. **낭비**를 싫어한다. 문서가 실제로 중요한 문제의 해법일 때 좋아하고, 단지 관리자의 강박일 때는 아니다." → 권장 형식은 **개요(outline), 매트릭스, 1페이지 참조 시트** 같은 미니멀 포맷.

**(3) 경량 실무 계열 — One Page Test Plan**

포함 항목: 대상 제품/기능 / **범위 in-out** / 리스크 / 가정 / 도구 / 환경 / 자원 / 추정.
논거 셋:
- **읽힘**: 바쁜 관리자는 긴 문서를 안 읽는다. 짧아야 실제로 검토된다.
- **효율**: 문서 작성 시간을 실제 테스트로 돌린다.
- **강제된 우선순위화**: 지면 제약이 "정말 필요한 것 vs 뺄 것"을 강제로 판단하게 만든다.
작성법: **의도한 독자에게 무엇이 필요한지 먼저 묻고** 그에 맞춰 항목을 고른다.
관련: Lisa Crispin & Janet Gregory *Agile Testing*의 one-page test plan 예시, Paul Carvalho의 극단판 **"0-Page Agile Test Plan"**(Agile 2012 — Collaborate–Design–Execute–Decide).

### ⓑ 좋은 예 / 나쁜 예

**담을 것 (합의되는 핵심)**
- **범위 밖(features NOT to be tested)** — IEEE 829가 명시 항목으로 둔 이유. 실무에서 가장 많이 빠지고 가장 많이 분쟁을 만든다.
- **리스크와 그에 대응하는 테스트** (리스크 기반 우선순위)
- **pass/fail 기준**과 **중단/재개 기준** — "언제 멈추는가"가 없으면 전략이 아니다.
- 환경·데이터 요건, 책임 주체.

**빼야 할 것**
- 테스트 케이스 목록(별도 산출물), 도구 사용법(reference로), 조직 소개·용어 설명 등 채움용 절.
- 템플릿에서 상속받았지만 이 프로젝트에 해당 없는 절 — Bach/Spolsky 양쪽이 공통으로 비판.

**나쁜 예의 징후**: 템플릿 목차가 전부 채워졌지만 "우리가 무엇을 안 할 것인가"가 없음 / 리스크 절이 일반론("일정 지연 가능") / 승인 서명란은 있는데 pass 기준이 없음 / 아무도 열어보지 않음(= 최종 판정 기준).

### ⓒ [실무 의견]·논쟁

- **[실무 의견]** *상세파 vs 1페이지파*: 규제 산업(금융·의료·항공)은 감사 대응 때문에 IEEE 829 계열의 상세 문서를 유지해야 한다는 현실적 반론이 강하다. 반대로 애자일 진영은 "waterfall 시대의 장문 테스트 계획에서 벗어나는 흐름"이라고 본다. **절충 다수설**: 조직 수준 test strategy는 안정적인 상세 문서로 1개, 프로젝트/스프린트 수준 test plan은 1페이지 living document.
- **[실무 의견]** *템플릿 유해론*: Bach — 템플릿을 이해 없이 채우면 문서는 있는데 계획은 없다. Spolsky도 사양서에 대해 동일 주장("Templates considered harmful") — 해당 없는 필수 절이 작성을 위축시키고 문서를 형식화한다.
- **[실무 의견]** *맥락 주도의 근본 입장*: "모든 실천의 가치는 맥락에 달렸다. 맥락 안의 좋은 실천은 있어도 **best practice는 없다**"(Kaner·Bach·Pettichord, *Lessons Learned in Software Testing*). 따라서 "표준 테스트 전략 문서 구조"라는 질문 자체를 거부하는 입장도 존재한다.
- **[실무 의견]** *두 문서가 정말 다 필요한가*: 소규모 팀에서는 strategy/plan 분리가 중복만 낳는다는 주장이 흔함. 분리의 실익은 "여러 프로젝트가 같은 전략을 공유할 때"뿐이라는 조건부 견해.

### ⓓ 출처
- https://web.cs.dal.ca/~arc/teaching/CS3130/Templates/TestingTemplates/Test%20Plan%20Templates/IEEEStandardTestPlans.doc (IEEE 829 원 템플릿)
- https://www.coleyconsulting.co.uk/testplan.htm
- https://www.professionalqa.com/ieee-standard-829
- https://reqtest.com/en/knowledgebase/how-to-write-a-test-plan-2/
- https://www.satisfice.com/download/heuristic-test-strategy-model (HTSM 정본)
- https://www.developsense.com/resource/htsm.pdf (HTSM v6.0 PDF)
- https://www.satisfice.com/download/building-a-context-driven-test-plan (How to Evolve a Context-Driven Test Plan — 7 tasks)
- https://www.satisfice.com/blog/archives/19 (Fighting Bad Test Documentation)
- https://www.satisfice.com/blog/archives/category/test-documentation
- https://www.thoughtworks.com/insights/blog/disruptive-testing-part-1-james-bach
- https://www.ministryoftesting.com/articles/the-one-page-test-plan
- https://www.agilealliance.org/wp-content/uploads/2016/01/Agile-2012-The-0-Page-Agile-Test-Plan-Paul-Carvalho.pdf
- https://cheesecakelabs.com/blog/heuristic-test-strategy/
- https://www.amazon.com/Lessons-Learned-Software-Testing-Context-Driven/dp/0471081124
- https://www.softwaretestinghelp.com/writing-test-strategy-document-template/

---

## 4. 운영 절차서 · Runbook / Playbook

### ⓐ 대표 방법론

**(1) Google SRE — playbook의 정본**

- 정의: **playbook(= runbook)** 은 "자동 알람에 어떻게 대응하는가"를 설명하는, **알람과 함께 만들어지는** 상위 수준 가이드. "**알람을 만들 때마다 대응 playbook 항목도 같이 만든다**"가 원칙.
- **효과 수치**: 사전에 베스트 프랙티스를 playbook에 기록해두면 "winging it"(즉흥 대응) 대비 **MTTR 약 3배 개선**. — 이 수치가 runbook 논의의 표준 인용값.
- **항목 구조**: severity(심각도) / impact(영향) / metric(지표) / background(배경) / **mitigation**(완화) / **discovery**(진단·디버깅 제안). 각 playbook은 **트리거(보통 모니터링 알람)로 시작**한다.
- **유지보수**: playbook 세부는 **프로덕션이 변하는 속도와 같은 속도로 낡는다**. 일 단위 릴리스면 매일 갱신이 필요할 수도. 규칙: **해당 알람이 울렸을 때 on-call이 최신 정보로 playbook을 갱신한다**(알람 발생 = 갱신 트리거로 삼는 피드백 루프).
- **팀 합의 원칙**: playbook이 제각각 불어나지 않도록, "우리 playbook이 반드시 가져야 할 **최소한의 구조화된 항목**"을 팀이 먼저 정하라.
- **탈출구**: playbook 항목을 무한히 늘리지 말고 "새로 얻은 프로덕션 지식을 **자동화나 모니터링 콘솔로 전환**할 기회"를 찾으라 — 문서화의 종착지는 자동화.
- 참고: on-call learning checklist는 **절차·진단 단계를 담지 않는다**. 대신 전문가 연락처, 유용한 문서 위치, 파고들 질문을 열거하는 "비교적 미래에 안 낡는(future-proof)" 문서로 만든다. → **잘 낡는 것(절차)과 안 낡는 것(색인·질문)을 다른 문서로 분리**하라는 설계 지침.

**(2) PagerDuty / Limoncelli — runbook의 형태**

Tom Limoncelli(*The Practice of System and Network Administration*) 기준, 좋은 runbook의 **7개 절**:
1. Service Overview
2. Service Build Information
3. Software Deployment Instructions
4. Common Task Procedures
5. **Pager Playbook** (모니터링 알람 ↔ 대응)
6. Disaster Recovery Plans
7. Service Level Agreements

PagerDuty 실무 원칙:
- **명료·단순**: 불필요한 세부 제거, 쉬운 문서 언어. "합의된 최선의 해법"을 명확히 제시.
- **근거 기반**: 과거 인시던트 리포트와 포스트모템을 훑어 실제로 가장 효율적이었던 해결 경로를 문서화. 전문가가 best practice로 인정하는 것을 적는다.
- **일관성**: 모든 애플리케이션의 runbook을 **같은 구조**로. 조직 차원에서 정리 방식을 합의하지 않으면 runbook 간 단계 중복이 생긴다.
- **테스트**: runbook은 **격리 실행으로 테스트**한다(자동화 플랫폼의 test 버튼). 현장 검증(field test) 후 배포.
- **runbook vs playbook 구분**(PagerDuty 용법): runbook = 특정 작업의 상세 절차, playbook = 더 큰 사건에 대한 총괄 대응(여러 runbook과 여러 담당자를 포함하는 전체 워크플로). ⚠️ Google SRE는 두 용어를 동의어로 쓴다 — **용어가 조직마다 반대로 쓰이므로 문서 첫머리에 정의를 박아야 한다.**

**(3) 절차 문장 규칙 (SOP/technical writing 정본)**

- **명령형(imperative) 능동태**로 쓴다. "**Click Save**" (○) / "The user should click Save" (✗).
- **한 단계 = 한 행위(atomic)**. 두 행위가 필요하면 두 단계로 쪼갠다. 항상 함께 수행되는 경우에만 합친다.
- 각 단계는 **행위 동사로 시작**: Open, Verify, Record, Notify…
- **순차 번호**, 하위 단계는 1.1 / 1.2.
- **판단 분기는 단계 안에 묻지 말고 별도 경로로 분기**시킨다.
- **중요한 단계 끝에는 기대 결과 / 품질 확인(검증 지점)을 적는다.** ← runbook의 "검증 지점" 요구와 정확히 일치.
- 수동태 금지(주의를 핵심에서 흩뜨린다), 전문용어 최소화.

### ⓑ 좋은 예 / 나쁜 예

**좋은 runbook**
- 트리거(알람명)로 시작하고, 심각도·영향으로 **즉시 판단**할 재료를 위에 준다.
- 명령형 원자 단계 + 각 단계의 기대 출력 + 실패 시 분기.
- 복사-실행 가능한 명령(정확한 커맨드), 그러나 **파괴적 명령 앞에는 확인 지점**.
- 마지막에 "이걸로 해결 안 되면 → 에스컬레이션 대상/링크".

**나쁜 runbook**
- 산문으로 흐르는 설명, "적절히 조치한다" 류의 판단 위임 문장.
- 낡음 — 명령/경로/대시보드 링크가 죽어 있음(SRE가 지목한 최대 실패 모드).
- 조직 내 runbook마다 구조가 달라 인시던트 중 탐색 비용이 큼.
- 알람은 있는데 대응 항목이 없음(SRE 원칙 위반).

### ⓒ [실무 의견]·논쟁

- **[논쟁 — SRE 내부]** *일반형 vs 단계별*: Google 내부에서도 갈린다.
  - **일반형 지지**: "RPC Errors High" 전체에 항목 **하나**만 두고 아키텍처 다이어그램을 곁들인다. 이유 — 느리게 낡고, 훈련된 엔지니어에게 유연성을 준다.
  - **단계별 지지**: step-by-step playbook이 **사람 간 편차를 줄이고 MTTR을 낮춘다**.
  - → 실무 결론: **낡는 속도 × 대응자 숙련도**의 함수. 자주 바뀌는 시스템·숙련팀 → 일반형. 안정적 시스템·교대 인원 다양 → 단계별.
- **[실무 의견 — 반(反)runbook]** Charity Majors: "우리가 가는 곳엔 runbook이 없다(there's no runbooks where we're going)". 논거 — **같은 것이 반복해서 깨지지 않는다**(고치니까). 그래서 runbook에 쓴 시간은 대체로 낭비이며, 현대 분산 시스템에서는 매번 새로운 문제를 만나므로 미리 훈련될 수 없다. 대안은 **관측 가능성(observability)** 으로 시스템을 그 자리에서 이해하는 능력. *Observability Engineering*은 "빠르게 낡는 runbook"을 나쁜 디버깅 습관으로 명시.
- **[절충 다수설]** runbook의 가치는 **반복성**에 비례한다. 반복되는 정형 작업(배포·롤백·배치 재수행·계정 잠금 해제)은 runbook이 압도적으로 유리하고, 신규·비정형 장애는 observability + 에스컬레이션 경로가 답이다. **두 종류를 한 문서에 섞지 말 것.**
- **[실무 의견]** runbook의 종착지는 문서가 아니라 **자동화**(SRE 원문의 입장이기도 함). 단계별 playbook이 완성되면 그것은 스크립트로 만들 수 있다는 신호다.

### ⓓ 출처
- https://sre.google/workbook/on-call/ (SRE Workbook, On-Call — playbook 원칙 정본)
- https://sre.google/sre-book/table-of-contents/
- https://sre.google/sre-book/accelerating-sre-on-call/ (on-call learning checklist)
- https://sre.google/sre-book/introduction/
- https://www.pagerduty.com/resources/automation/learn/what-is-a-runbook/ (Limoncelli 7절 포함)
- https://docs.firehydrant.com/docs/runbook-best-practices
- https://www.nobl9.com/it-incident-management/runbook-example
- https://www.techtarget.com/searchitoperations/tip/An-introduction-to-SRE-documentation-best-practices
- https://charity.spicytakes.org/ (Charity Majors)
- https://www.infoq.com/articles/charity-majors-observability-failure
- https://www.goodreads.com/book/show/59039072-observability-engineering
- https://pressbooks.senecapolytechnic.ca/technicalwriting/chapter/standard-operating-procedures-sops/ (SOP 작성 규칙)
- https://extension.psu.edu/standard-operating-procedures-a-writing-guide
- https://www.instructionalsolutions.com/blog/procedure-writing
- https://courses.lumenlearning.com/suny-esc-technicalwriting/chapter/standard-operating-policies-procedures/
- https://www.thefdagroup.com/blog/a-basic-guide-to-writing-effective-standard-operating-procedures-sops

---

## 5. 인터페이스 / 전문(電文) 규격서

### ⓐ 대표 방법론

**(1) ICD (Interface Control Document) — 시스템공학 정본**

정의: 프로젝트에서 생성된 **모든 인터페이스 정보**(도면·다이어그램·표·서술)의 기록. 목적은 인터페이스 정보를 **통제하고 이력을 남기는 것**.

**필드당 문서화해야 할 속성**(HHS EPLC Interface Control Practices Guide 계열의 표준 목록):
- 이름 / 식별자(project-unique identifier)
- 우선순위
- **타이밍·빈도·볼륨·순서(sequencing)**
- **가능한 값의 범위 또는 열거(enumeration)**
- 보안·프라이버시 제약
- **크기와 형식(문자열 길이 등)**
- 송신자와 수신자(sources and recipients)
- 기술명(technical name)
- **측정 단위**

**핵심 규칙 2가지**:
- 프로토콜이 여러 인코딩(바이너리/JSON/Protobuf)을 허용하면 **ICD는 하나의 정본 인코딩(canonical encoding)으로 못 박고**, 수용할 **모든 메시지 변형에 대해 예시를 제공**해야 한다.
- **모든 ICD가 같은 필드 구성을 쓰라** — 그래야 통합 담당자의 스크립트와 테스트 하네스가 자동 파싱할 수 있다.

**권장 절 구성(실무 ICD)**: 표지(발행일·작성자) / **개정 이력 표**(날짜·리비전·작성자·변경 설명) / 목차·표 목차·그림 목차 / 서명 페이지 / **Scope(무엇을 다루고 무엇을 제외하는가)** / 문서 개요 / 네트워크(물리 연결·프로토콜) / 시각 동기화 / **메시지 정의**.
중요: **"ICD는 보통 요구사항을 담지 않는다."** 아키텍처 결정은 설계 문서로, ICD는 저수준 통신 사양에 집중.

**메시지/필드 표의 열(column) 설계**:
- 저수준(바이트 기반): **필드명 / 데이터 타입(별도 데이터 타입 표 참조) / 바이트 수 / 설명(min·max 값 포함)**
- 고수준(JSON 등): **필드명 / 데이터 타입 / 필수·선택 / 기대 동작 설명**

**헤더 규약**: 모든 메시지에 고정 헤더 — **Message ID**(페이로드 종류 + 전체 메시지 크기 결정) / **ICD 버전 번호** / 시퀀스 번호(권장) / 발신 주체(하드웨어 vs 소프트웨어) / 전송 모드.
**엔디안**: 반드시 명시하고 **바이트 순서 다이어그램을 그려라**(모호성 제거).
**버저닝**: 개정 이력 표 + **모든 메시지 봉투에 ICD 버전을 실어** 수신자가 해석 방식을 고를 수 있게 한다.

**흔한 실수**: ICD를 설계 문서와 혼동 / 에러 처리·복구 시나리오 누락 / 연결 경로와 **연결 해제 시나리오** 미문서화 / 연결·에러 경로 시퀀스 다이어그램 부재 / 데이터 타입 크기와 비트 연산에 대한 암묵적 이해 가정 / JSON 필드의 선택 여부 미표기.

**(2) 금융권 전범 — ISO 8583 / NACHA ACH**

**ISO 8583** (카드 거래 전문 표준)의 문서 스타일:
- 메시지 구성 순서를 **먼저 못 박는다**: message header → **MTI(Message Type Indicator)** → 하나 이상의 **bitmap** → bitmap 순서대로의 data elements.
- **primary bitmap 8바이트**: 비트 n = 필드 n의 존재 여부(1~64). secondary bitmap이 있으면 65~128.
- **각 data element마다 의미와 포맷을 고정 표기.** 포맷 코드 관습: `n`(numeric), `a`(alphabetic), `an`(alphanumeric), `ans`(alphanumeric+special), 고정길이는 숫자(`n6`), 가변길이는 `LL`/`LLL` 접두(`LLVAR`/`LLLVAR`).
- 수신 시스템은 **bitmap → 존재 필드 식별 → 필드 포맷 표 → 값 추출**의 순서로 파싱한다. 즉 **문서 구조가 파서 구현 순서와 1:1로 대응**하도록 쓰여 있다. ← 전문 규격서 설계의 핵심 교훈.

**NACHA ACH 파일 포맷**(고정길이 파일 명세의 전범):
- **94문자 고정폭 ASCII**, 중첩(enveloped) 구조.
- 구조: File Header → (Batch Header → Entry Detail [→ Addenda] → Batch Control)* → File Control.
- 각 레코드 타입마다 **"이 레코드는 무엇을 지정하는가"를 한 문단으로 먼저 서술**한 뒤 필드 표를 붙인다. 예: "File Header Record는 물리적 파일 특성을 지정하고 직전 출발지·목적지를 식별한다. 또한 날짜·시각·파일 식별자를 포함한다."
- **필수/선택을 레코드 단위로 명시**("모든 레코드와 필드는 필수, 단 record 7 Addenda는 선택").
- **Control 레코드에 합계·해시 총계·건수·블록 수**를 두어 파일 무결성을 자체 검증하게 한다. ← 규격서가 **검증 수단을 포맷 안에 내장**한 사례.
- 은행마다 같은 표준을 자기 고객용 가이드로 재발행하며(위 출처들), 이때 필드 표 형식이 사실상 업계 표준 스타일이 되었다.

**(3) 규범 언어 — RFC 2119 / BCP 14 (+ RFC 8174)**

- **MUST** = 절대 요구, 예외 없음 / **SHOULD** = 정당한 이유가 있을 때만 무시 가능 / **MAY** = 진짜 선택. 단 MAY로 구현한 쪽과 안 한 쪽이 **상호운용 가능해야 한다**(양방향).
- **RFC 8174**의 추가 규칙: **대문자로 쓴 것만 규범적(binding)** 이다. 소문자 "should"는 비공식 안내.
- RFC 2119 자체의 지침: 이 키워드들은 "**신중하고 아껴서(with care and sparingly)**" 써야 하며, **상호운용성에 진짜 필요하거나 유해한 동작을 막을 때만** 등장해야 한다.
- 문서 앞부분에 "본 문서의 키워드는 RFC 2119(BCP 14)에 따라 해석한다"는 문구를 넣는 것이 관례.
- OASIS 등 다른 표준화 기구도 동등한 키워드 가이드라인을 별도 발행.

### ⓑ 좋은 예 / 나쁜 예

**좋은 전문 규격서의 특징**
- **파싱 순서 = 문서 순서**(ISO 8583 교훈). 독자가 위에서 아래로 읽으면 파서가 만들어진다.
- 필드 표에 **오프셋/길이/타입/필수여부/값 범위·열거/단위**가 전부 있고, 열 구성이 모든 표에서 동일.
- **정본 인코딩 1개**로 고정 + 모든 변형에 **완전한 예시 전문(sample message)** 첨부.
- 에러 코드가 별도 표로 있고, 각 코드마다 **의미 + 송신자가 취할 행동**이 있다.
- **버전과 개정 이력**이 문서 상단에 있고, 메시지 자체에도 버전 필드가 있다.
- 무결성 검증 수단(합계·해시·건수)이 포맷에 포함.

**나쁜 예의 징후**
- 필드 길이는 있는데 **패딩 규칙(좌/우, 공백/0)** 이 없다 — 고정길이 전문에서 최다 사고 원인.
- 인코딩(EUC-KR/UTF-8)과 **길이 단위(바이트 vs 문자)** 를 명시하지 않음.
- 엔디안·부호 표현·소수점 위치(implied decimal) 미정의.
- 예시 전문이 없거나, 있는데 필드 표와 불일치.
- 선택 필드의 "미사용 시 무엇을 채우는가"가 없음.
- 정상 흐름만 있고 **에러 응답·타임아웃·재전송·중복 처리(idempotency)** 규정이 없음.

### ⓒ [실무 의견]·논쟁

- **[실무 의견]** *표 vs 산문*: 인터페이스 규격서는 표가 정본이어야 하며 산문은 표를 대체할 수 없다는 것이 거의 합의. 다만 **각 레코드/메시지마다 한 문단의 목적 서술을 표 앞에 두는** NACHA 스타일이 가독성에 유리하다는 실무 지지가 강하다(표만 있으면 "왜"를 알 수 없다).
- **[실무 의견]** *ICD에 요구사항을 넣을 것인가*: 넣지 말라는 게 시스템공학 정론(ICD는 "무엇을 주고받는가"만). 반론 — 요구사항 번호를 참조하면 추적성이 좋아진다. 단 참조하는 순간 **요구사항이 바뀔 때마다 ICD를 갱신해야 하는 결합**이 생긴다는 비용을 명시적으로 인정하는 것이 조건.
- **[실무 의견]** *예시(sample) 분량 논쟁*: 모든 변형에 예시를 넣으면 문서가 비대해지고 낡는다 vs 예시 없는 규격서는 반드시 오해된다. 절충 — **예시를 문서에 인라인하지 말고 테스트 픽스처 파일로 두고 문서에서 링크**하되, 픽스처가 CI로 검증되게 한다(문서와 코드의 동기화 문제를 자동화로 해결).
- **[실무 의견]** RFC 2119 키워드 남용 비판: 모든 문장을 MUST로 쓰면 진짜 중요한 MUST가 묻힌다. RFC 2119 원문 자체가 "sparingly"를 명시한 이유.

### ⓓ 출처
- https://en.wikipedia.org/wiki/Interface_control_document
- https://www.hhs.gov/sites/default/files/ocio/eplc/EPLC%20Archive%20Documents/31-Interface%20Control/eplc_interface_control_practices_guide.pdf (HHS EPLC Interface Control Practices Guide)
- https://medium.com/@david.barrineau_14226/how-to-write-an-interface-control-document-icd-56282eeffffe (필드 표 열 설계·헤더·엔디안·흔한 실수)
- https://soho.nascom.nasa.gov/publications/soho-documents/ICD/icd.pdf (NASA SOHO ICD 실물 예)
- https://www.voa.va.gov/DocumentView.aspx?DocumentID=78 (ICD 템플릿)
- https://beefed.ai/en/interface-control-documents-templates
- https://www.ibm.com/docs/SSMKHH_9.0.0/com.ibm.etools.mft.samples.iso8583.doc/doc/background.htm (ISO 8583 구조)
- https://medium.com/@bayram.serkan/explaining-iso-8583-messages-7def9bbc5b3c
- https://www.linkedin.com/pulse/understand-bitmap-field-format-iso-8583-message-sandeep-devhare
- https://www.hancockwhitney.com/hubfs/Treasury%20Services%20Resource%20Library%20Files/ACH%20Services/NACHA-FORMAT.pdf (NACHA 94자 고정폭 명세 실물)
- https://www.treasurysoftware.com/ach/how-do-i-create-an-ach-nacha-file-detailed-file-format.aspx
- https://independent-bank.com/_/kcms-doc/174/59908/20201006_NACHA_FileLayoutGuide_Final.pdf
- https://dam.bancofcal.com/m/5ec324636794be06/original/UG32-NACHA-File-Format-Specifications.pdf
- https://secureinstantpayments.com/sip/help/interface_specs/external/NACHA_format.pdf
- https://www.rfc-editor.org/rfc/rfc2119.html (RFC 2119 원문)
- https://www.rfc-editor.org/info/rfc2119/
- https://www.oasis-open.org/policies-guidelines/keyword-guidelines/
- https://mtsknn.fi/blog/rfc-2119-in-a-nutshell/

---

## 6. 프로세스 / 워크플로우 문서 (study/ 절차서 류)

### ⓐ 대표 방법론

**(1) 절차 문장 규칙** — §4 SOP 규칙과 동일 정본을 공유한다(명령형·원자 단계·번호·분기 분리·기대 결과). 여기서는 프로세스 문서 고유 이슈만 다룬다.

**(2) 순서도 vs 산문 vs 매트릭스 — 무엇을 언제 쓰는가**

| 표현 | 담는 것 | 못 담는 것 |
|---|---|---|
| **번호 매긴 절차(산문)** | 정확한 행위·명령·검증 지점 | 병렬성, 전체 조망 |
| **Swimlane / BPMN 다이어그램** | **시간 흐름 + 역할별 책임 이동** | 정확한 명령, 상담/통보 관계 |
| **RACI 매트릭스** | 산출물별 **정적 책임 배분**(R/A/C/I) | 순서·시간 |

핵심 통찰: **RACI와 swimlane은 경쟁이 아니라 상보**다.
- RACI = "시간 축이 없는 정적 매트릭스, 산출물마다 누가 어떤 역할인가".
- Swimlane = "그 소유권이 따라가는 **순서**를 보여준다".
- BPMN 다이어그램은 "누가 무엇을 하는가"는 보여주지만 **자문(Consulted)·통보(Informed) 관계는 다이어그램에 안 보인다** — 이 결정적 정보가 RACI에서만 표현된다. 그래서 강한 프로세스 문서는 **둘을 함께** 쓴다.
- BPMN의 장점: 표준 기호로 기술·비기술 독자를 잇고 자동화 가능한 수준의 상세를 담는다. 단점: 학습 비용.

**(3) 체크리스트 설계론 — Atul Gawande, *The Checklist Manifesto* (+ Daniel Boorman/Boeing)**

구체 규칙 수준:
- **두 유형 중 하나를 반드시 선택하라.**
  - **DO-CONFIRM**: 팀원이 기억과 경험으로 각자 일을 수행한 뒤, **멈춰서 체크리스트로 확인**한다.
  - **READ-DO**: 읽으면서 하나씩 수행하고 체크한다(요리 레시피형).
- **Pause point(정지점)를 명시적으로 정의하라.** 언제 이 체크리스트를 꺼내는가. (경고등이 켜질 때처럼 자명한 순간이면 생략 가능.)
- **길이: 5~9개 항목**(작업 기억의 한계)이 rule of thumb.
- **한 정지점에서 60~90초를 넘기면** 체크리스트가 다른 일에 방해가 되기 시작한다 → 사람들이 지름길을 타고 단계가 누락된다.
- **"killer items"에 집중**: 빠뜨리면 가장 위험한데도 자주 간과되는 항목만.
- **표현은 단순하고 정확하게**, 그 **직군의 언어**를 쓴다.
- **겉모습도 단순하게**: 한 페이지에 맞추고, 불필요한 색을 쓰지 말고, 대문자·소문자를 섞어 쓴다(전부 대문자 금지 — 가독성).
- **반드시 실세계에서 테스트하라.** "첫 초안은 언제나 무너진다. 어떻게 무너지는지 관찰하고 고치고 다시 테스트하기를 일관되게 작동할 때까지 반복하라."

**(4) Diátaxis how-to 규칙** — §0 참조. 프로세스 문서는 how-to이므로 **설명을 넣지 말고 링크로 빼라**, **조건부 명령형**, **제목이 목표**.

**(5) 사양·프로세스 문서의 반(反)템플릿 입장 — Joel Spolsky**

*Painless Functional Specifications* 4부의 규칙:
1. **재미있게 써라(Be funny).** 지루한 문서는 읽히지 않고, 나중에 "그런 얘기 들은 적 없다"는 분쟁을 낳는다. "the user" 대신 "Miss Piggy" 같은 구체적 등장인물을 쓰라.
2. **사양 쓰기는 "뇌가 실행할 코드"를 쓰는 것**이다. 사람 뇌는 랜덤 액세스가 아니라 **서사(narrative)와 맥락**으로 작동한다 → **큰 그림 먼저, 세부 나중**. 추상적 정의보다 구체적 이야기.
3. **가능한 한 단순하게 써라.** 짧은 문장, 일상어. "utilize" → "use". 벽 같은 텍스트는 불릿으로 쪼개고, 스크린샷을 넣고, 여백을 넉넉히.
4. **여러 번 다시 읽고 고쳐라.** 즉시 이해되지 않는 문장은 다시 쓴다.
5. **템플릿은 유해하다(Templates considered harmful).** 표준 템플릿은 ① 해당 기능과 무관한 필수 절을 강요하고 ② 작성 자체를 위압적으로 만들어 사람들이 사양을 안 쓰게 만든다. 사양은 정형 양식이 아니라 **에세이처럼 맞춤 문서**여야 한다.

또한: **에러 케이스는 누군가 결정을 내려야 하는 지점**이다("비밀번호 분실 시 정책"). 결정하지 않으면 코드를 쓸 수 없다 → **사양은 그 결정을 기록하는 것**이다. 초판에 미결(open issue)이 남는 것은 정상이며, **미결로 표시하고 대안을 논의**하되 프로그래머가 착수하기 전까지 전부 없애야 한다.

### ⓑ 좋은 예 / 나쁜 예

**좋은 프로세스 문서**
- 제목이 달성할 목표(동사구).
- 단계가 명령형 원자 단위 + 각 단계의 기대 결과.
- 분기가 조건부 명령형("~이면 ~하라")으로 명시되고, 어디로 복귀하는지 표시.
- 역할이 나오면 RACI나 최소한 "누가"가 각 단계에 붙어 있다.
- **미결 사항이 미결로 표시**되어 있다(감춰져 있지 않다).
- 체크리스트 부분은 5~9항목, 정지점 명시, 유형(DO-CONFIRM/READ-DO) 선언.

**나쁜 프로세스 문서**
- 절차와 설명과 배경이 한 문서에 섞여 있어 급할 때 못 쓴다(Diátaxis 위반).
- 30항목짜리 체크리스트 — 사람들이 형식적으로 전부 체크하고 실제로는 안 본다.
- 템플릿의 빈 절이 "N/A"로 가득함.
- 수동태·"적절히 처리한다" 류의 책임 회피 문장.
- 순서도만 있고 정확한 명령이 없거나, 산문만 있고 병렬·역할이 안 보임.

### ⓒ [실무 의견]·논쟁

- **[실무 의견]** *템플릿 유해론 vs 일관성*: Spolsky/Bach는 템플릿을 비판하지만, 운영 문서(runbook)에서는 PagerDuty·SRE가 **일관된 구조**를 강하게 요구한다. 갈라지는 지점 — **탐색 비용이 지배적인 문서(인시던트 중 읽는 것)는 템플릿이 옳고, 사고를 요하는 문서(사양·전략)는 템플릿이 해롭다.** 이것이 두 진영을 화해시키는 실무 정리.
- **[실무 의견]** *체크리스트는 몇 개까지?* Gawande의 5~9는 항공/수술처럼 **긴장 상태에서 구두로 수행**하는 맥락의 수치다. 문서로 읽으며 수행하는 개발 체크리스트(예: 릴리스 전 점검)는 더 길어도 된다는 반론이 있으나, 그 경우 **"killer items 서브셋"을 따로 표시**하라는 절충이 흔하다.
- **[실무 의견]** *READ-DO의 함정*: 숙련자에게 READ-DO를 강요하면 형식적 체크로 전락한다. 숙련도가 높은 팀일수록 DO-CONFIRM이 맞고, 신규 인원이 섞인 온콜 교대에서는 READ-DO가 맞다 — 이는 §4의 "일반형 vs 단계별 playbook" 논쟁과 같은 축이다.
- **[실무 의견]** *RACI 무용론*: RACI 매트릭스를 만들어도 실제로 참조되지 않는다는 비판이 흔하다. 유효한 조건은 "Accountable이 항목당 정확히 1명"과 "실제 분쟁 시 이 문서를 편다"는 관행 두 가지.

### ⓓ 출처
- https://diataxis.fr/how-to-guides/
- https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/
- https://www.joelonsoftware.com/2000/10/03/painless-functional-specifications-part-2-whats-a-spec/
- https://www.joelonsoftware.com/2000/10/04/painless-functional-specifications-part-3-but-how/
- https://www.joelonsoftware.com/2000/10/15/painless-functional-specifications-part-4-tips/ (5규칙 + 템플릿 유해론)
- https://blog.beeminder.com/speclist/ (Spec-List — 후속 실무 변형)
- https://ba-copilot.com/raci-matrix
- https://www.engineeringmanagement.info/2017/05/why-use-both-raci-matrix-with-swim-lane.html
- https://en.wikipedia.org/wiki/Swimlane
- https://www.visual-paradigm.com/tutorials/how-to-generate-raci-chart-from-bpmn.jsp
- https://insight7.io/6-process-mapping-methodologies-compared-and-explained/
- https://www.shortform.com/blog/checklist-checklist/ ("Checklist for Checklists" 20단계 요약)
- https://grahammann.net/book-notes/the-checklist-manifesto-atul-gawande
- https://joelhooks.com/the-checklist-manifesto/
- https://sive.rs/book/ChecklistManifesto
- https://www.mickmel.com/highlights-from-the-checklist-manifesto-by-atul-gawande/
- https://www.instructionalsolutions.com/blog/procedure-writing

---

## 7. 유형 간 교차 원칙 (종합)

리서치 전체에서 **여러 유형에 반복 등장한** 규칙만 뽑는다. 이것이 우리 문서 규약의 후보다.

1. **한 문서 = 한 형태.** 절차·참조·설명을 섞지 않는다 (Diátaxis / Cockburn의 "기술 세부를 설계 문서로" / ICD의 "요구사항을 담지 않는다"가 모두 같은 규칙).
2. **분기는 본문이 아니라 전용 구조에 담는다.** Cockburn의 Extensions, EARS의 `If~then`, SOP의 "판단 분기를 별도 경로로", Diátaxis의 조건부 명령형 — 네 방법론이 독립적으로 같은 결론.
3. **끝나는 곳을 적어라.** 확장은 복귀/성공/실패로 끝나야 하고, 테스트 계획은 pass/중단 기준이 있어야 하고, runbook은 에스컬레이션으로 끝나야 한다.
4. **주관어·수동태·접속사 뭉침 금지.** (Wiegers 금지어 목록, SOP 능동 명령형, "and/or는 요구사항 분리 신호".)
5. **모든 표는 열 구성이 같아야 한다.** ICD의 "같은 필드를 모든 ICD에" — 자동 파싱/스크립트화 가능성이 이유.
6. **낡음(staleness)을 설계 변수로 다뤄라.** SRE의 "알람이 울릴 때 갱신", 낡는 것(절차)과 안 낡는 것(색인·질문)을 분리, 예시는 CI로 검증되는 픽스처로.
7. **길이 제약은 품질 도구다.** 1페이지 테스트 계획의 "강제된 우선순위화", 체크리스트 5~9항목, MSS 3~9단계 — 셋 다 "지면 제약이 사고를 강제한다"는 같은 논리.
8. **템플릿의 양면성.** 탐색 비용이 지배적인 문서 → 템플릿 필수(runbook). 사고가 지배적인 문서 → 템플릿 유해(사양·전략).
9. **읽히지 않는 문서는 실패다.** Cockburn("unreadable use cases won't get read"), Bach("낭비를 싫어한다"), 1페이지 테스트 계획, Spolsky("재미있게 써라") — 네 저자가 동일 판정 기준을 제시.

---

## 8. 미확인 / [구현 검증] 이연 항목

- **RuleSpeak 정확한 문장형과 키워드 세트** — 공식 PDF(Basic Do's & Don'ts v2.2.5, Sentence Forms v2.2.3) 원문 확보 실패(URL 404). rulespeak.com에서 직접 다운로드해 확인 필요.
- **Cockburn 원서의 "use case quality checklist" 원문 항목** — 2차 출처(binaryphile 요약, ecs.csun.edu 템플릿)로 규칙은 확보했으나, 원서 체크리스트의 정확한 항목 수·문구는 미확인.
- **HTSM 4대 영역의 하위 guideword 전체 목록** — PDF 원문(developsense.com/resource/htsm.pdf) 미파싱. 영역명까지만 확인.
- **HHS EPLC Interface Control Practices Guide 원문** — 403으로 직접 확인 실패, 2차 인용으로 필드 속성 목록 확보.
- **"MTTR 3배 개선"의 원 측정 근거** — Google SRE 원문의 서술은 확인했으나 측정 방법·표본은 원문에 상세하지 않음. 인용 시 "Google SRE의 주장"으로 표기할 것.
- Wiegers 비즈니스 룰 5분류의 **원서 원문 예시** — 2차 출처(BookDigests, Medium 도입부)로 확인. 원서 3판 해당 장 확인 시 예시 보강 가능.

> 조사 제약: 본 세션의 WebSearch 예산(200회) 소진으로 일부 후속 검색을 수행하지 못함. 위 항목은 WebFetch 또는 다음 세션에서 보완 가능.
