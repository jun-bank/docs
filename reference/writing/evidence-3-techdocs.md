# R3 — 기술 문서 작성 방법론 딥 리서치

조사일: 2026-08-06 · 방법: WebSearch/WebFetch 원출처 우선 · 표기: **[원출처]** = 1차 자료(저자·기관 공식), **[2차]** = 해설 기사, **[실무 의견]** = 블로그·HN 등 개인 견해
대상 문서군(jun-bank): ①참조 대장(BR 대장) ②유스케이스 계약 ③ADR 25건 ④절차서(운영·테스트 전략) ⑤워크플로우
진단 전제: "검증 최적화(고밀도 표·교차참조 과다)로 사람이 읽기 어렵다"

---

## 축 1 — Diátaxis (Daniele Procida)

### 1.1 4분류의 정확한 정의 [원출처]

| 유형 | 정의(원문) | 지향 |
|---|---|---|
| Tutorial | "an **experience** that takes place under the guidance of a tutor" / "a *practical activity*, in which the student learns by doing something meaningful, towards some achievable goal" | learning-oriented |
| How-to guide | "**directions** that guide the reader through a problem or towards a result" | goal-oriented |
| Reference | "technical descriptions of the machinery and how to operate it" / "propositional or theoretical knowledge that a user looks to in their work" | information-oriented |
| Explanation | "a discursive treatment of a subject, that permits reflection" | understanding-oriented |

출처: https://diataxis.fr/tutorials/ · https://diataxis.fr/how-to-guides/ · https://diataxis.fr/reference/ · https://diataxis.fr/explanation/

### 1.2 두 축(생성 원리) [원출처]

- **action / cognition**: "A skill or craft or practice contains both **action** (practical knowledge, knowing *how*) and **cognition** (theoretical knowledge, knowing *that*)."
- **acquisition / application**: 기술을 *습득 중*(study)인가, *적용 중*(work)인가.
- 교차 결과:

| | Action | Cognition |
|---|---|---|
| **Acquisition (study)** | Tutorial | Explanation |
| **Application (work)** | How-to guide | Reference |

- "There is simply no other territory to cover." (4분류가 완전집합이라는 주장)

출처: https://diataxis.fr/foundations/ · https://diataxis.fr/compass/

### 1.3 왜 섞으면 실패하나 [원출처 — 핵심]

- Reference에 설명이 섞일 때: "This is bad for the reference, interrupted and obscured by digressions. But it's bad for the explanation too, because it's not allowed to develop appropriately and do its own work." (https://diataxis.fr/reference-explanation/)
- 전형적 실패: "Reference material that breaks off from describing the machinery in order to show how to do something, or a tutorial that interrupts its own lesson to digress into explanation are typical examples of confused, confusing documentation."
- Reference의 3규칙 [원출처, https://diataxis.fr/reference/]:
  1. **Structure the documentation around the code** — "The structure of the documentation should mirror the structure of the product."
  2. **Be austere** — "austere and uncompromising", "neutrality, objectivity, factuality". 레퍼런스는 *읽는* 것이 아니라 *조회하는(consult)* 것.
  3. **Describe, don't instruct** — "Neutral description is the key imperative of technical reference." 설명·지시·의견은 링크로 뺀다.
  - 일관성: "Standard patterns are what allow us to use reference material effectively." (식품 영양표시 라벨 비유 — 같은 자리에 같은 것이 있어야 한다)
  - 예시는 허용: "Examples are valuable ways of providing illustration that helps readers understand reference."
- Tutorial 금지사항: "A tutorial is not the place for explanation." + 선택지·대안 제거, 추상화 최소화, 정보 밀도 낮추기.
- How-to 금지사항: "no digression, explanation, teaching" / "practical usability is more helpful than completeness" / "Don't pollute your practical how-to guide with every possible thing".
- How-to 제목 규칙: "Choose titles that say exactly what a how-to guide shows." (좋음 "How to integrate application performance monitoring" / 나쁨 "Application performance monitoring")
- Explanation 규칙: 연결 짓기, 맥락·역사·제약 제공, **"Explanation can and must consider alternatives, counter-examples or multiple different approaches"**, 관점·의견 인정.

### 1.4 품질 이론 [원출처]

- **functional quality** = "accuracy, completeness, consistency, usefulness, precision and so on" — 객관 측정 가능, 서로 독립.
- **deep quality** = "feeling good to use, having flow, fitting to human needs, being beautiful, anticipating the user" — 주관적·상호의존적.
- 핵심: deep quality는 functional quality를 전제로만 성립. 우리 진단("검증엔 좋지만 읽기 어렵다")은 **functional은 높고 deep이 낮은 상태**로 정확히 매핑된다.
- 출처: https://diataxis.fr/quality/

### 1.5 적용 방법 — 점진적 [원출처]

- "every step in the right direction is worth publishing immediately"
- 대규모 재편 금지: "Diátaxis changes the structure of your documentation from the inside"
- 4단계 사이클: (1) Choose something (아무거나, 랜덤이어도 됨) (2) 기준으로 평가 (3) 개선 1개 결정 (4) 실행 후 종료.
- 출처: https://diataxis.fr/how-to-use-diataxis/

### 1.6 비판 [실무 의견]

- **분리하면 링크 지옥**: "This framework is helpful for *thinking* about content, but also results in a strange sidebar for your docs if you actually follow their advice." / "If you do separate them, you end up with a serious linking problem, where every page is useless in isolation." (HN dont__panic, https://news.ycombinator.com/item?id=33020045)
- **저자 반박(같은 스레드)**: 조종사 비유 — 엔진 비상시 조종사에게 필요한 건 처방적 절차이지 레퍼런스 데이터가 아니다. 섞이면 "at best unwelcome, at worst, deadly." (DanieleProcida)
- **용어가 서로 너무 가깝다**: "*Tutorial*, *how to guide* and *explanation* are all practically synonyms… you can't have different words that's supposed to help people gain understanding and then start off by confusing everyone." (HN, https://news.ycombinator.com/item?id=42325011)
- **교조화 경고 + 저자 완화**: "We do see people try to take it too far though and have literally only these four categories on their docs page, which never works well." / 저자: "you don't have to get it completely right, but most people would be better off moving more in that direction." 레퍼런스에 예시를 넣는 건 위반이 아니다.
- **타협안**: 카테고리는 분리하되 태그·택소노미로 교차 연결(HN makeitrain).
- 중립 평가: "attempting to segregate content into these discrete categories has had limited success" (I'd Rather Be Writing, https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework)

### 1.7 우리 문서 유형별 적용 후보

| 우리 문서 | Diátaxis 유형 | 적용 후보 |
|---|---|---|
| BR 대장 | **Reference** | austere·중립 서술 유지가 정답. 단 "왜 이 BR인가"(설명)·"이 BR을 어떻게 검증하나"(how-to)를 대장 안에 섞지 말고 링크로 분리. 대장 구조를 도메인 구조와 1:1 미러링. |
| 유스케이스 계약 | **Reference**(주) + 소량 Explanation 분리 | 계약 표는 조회용. 설계 근거·대안 논의는 별도 explanation 문서로 뽑아낸다. |
| ADR | **Explanation** | ADR은 본질적으로 explanation(대안·반례·관점 허용). 표로 압축하려는 유혹이 최대 위험. |
| 운영 절차서 | **How-to guide** | 완전성보다 실용성. 제목은 "무엇을 하는가"로. 설명·예외 카탈로그를 절차 안에 끼워넣지 않는다. |
| 테스트 전략 | **Explanation** | 전략은 왜/무엇을 우선하는가 — 서술형이 맞다. |
| 워크플로우 | **Tutorial**(신규자용) ∥ **How-to**(숙련자용) 분리 | 지금 한 문서가 둘을 겸하고 있다면 이게 "읽기 어려움"의 주범 후보. |

---

## 축 2 — 기업 스타일 가이드 & 커뮤니티 합의

### 2.1 Google developer documentation style guide [원출처]

**핵심 하이라이트** (https://developers.google.com/style/highlights)
- 2인칭("you"), 능동태, 현재시제, serial comma
- 제목·헤딩 **sentence case**
- "Put conditions before instructions, not after" ← 조건이 뒤에 오면 독자가 이미 실행한 뒤다
- 순서 있으면 번호 목록, 아니면 글머리표, 쌍 데이터는 description list
- "Don't pre-announce anything", "Use descriptive link text"

**표 규칙** (https://developers.google.com/style/tables) — *우리 문서 진단에 직결*
- 리스트를 쓸 때: "Each item is a single unit" 또는 "Each item is a pair of pieces of related data"
- **표를 쓸 때: "Each item is three or more pieces of related data"** ← 2열짜리는 표가 아니라 목록이어야 한다
- 표를 쓰지 말 것: 페이지 레이아웃, 코드 스니펫, 단일 열, "long one-dimensional lists in multiple columns", **번호 절차 안**
- 헤더: sentence case, 간결, 문장부호로 끝내지 말 것, **첫 행·첫 열만 헤더**
- 표는 완전한 문장으로 도입한다. 셀 병합(colspan/rowspan) 금지. 논리적 순서 또는 알파벳 정렬.

**목록 규칙** (https://developers.google.com/style/lists)
- 번호: "items where the sequence is significant, such as ordered steps, phases, or priorities"
- 글머리표: "items that's not a sequence"
- description list: 여러 용어에 주목시킬 때 / run-in heading: 개념 강조·공간 절약
- "Use the same syntax/structure for all list items in a given list" (병렬성)
- 항목 1개짜리 목록 금지. 중첩은 소문자·로마숫자.
- 도입 문장은 **완전한 문장**, 콜론 또는 마침표로 끝.

**헤딩 규칙** (https://developers.google.com/style/headings)
- sentence case. 페이지당 h1 1개, 고유.
- 태스크형 헤딩은 **원형동사로 시작** — "Create an instance" (not "Creating an instance")
- 레벨 건너뛰기 금지(h2 밑에만 h3). **빈 헤딩·연속 헤딩 금지** — "Make sure headings are followed by content."
- "Avoid using '-ing' verbs, numbers, and excessive punctuation in headings."

**교차참조/링크 규칙** (https://developers.google.com/style/cross-references) — *우리 진단 "교차참조 과다"에 직격*
- **"Each link creates a decision for the reader, adding cognitive load."**
- "Provide help in context rather than linking elsewhere" — 용어 정의·개념 설명·짧은 절차는 **링크 대신 그 자리에서 해결**
- "Generally, within a given page, don't provide duplicate links to the same destination." (예외: 특정 섹션 링크, 페이지가 매우 길어 링크가 멀리 떨어진 경우, 진입점이 여럿인 경우)
- 링크 텍스트: 짧고 고유하고 서술적, 중요한 단어를 앞에, 주변 문맥 없이도 의미가 통해야 함
- "Don't use phrases such as *this document*, *this article*, or *click here*."

**Technical Writing One (Google 공개 강좌)** [원출처]
- https://developers.google.com/tech-writing/one/short-sentences — "Focus each sentence on a single idea, thought, or concept. Just as statements in a program execute a single task, sentences should execute a single idea." / 긴 문장에 `or`·나열이 있으면 목록으로 변환하라는 신호 / filler = "textual junk food that consumes space without nourishing the reader" (예: "at this point in time"→"now", "is able to"→"can")
- https://developers.google.com/tech-writing/one/lists-and-tables — 글머리표는 "rearranging the items… the list's meaning does not change", 번호는 "the list's meaning changes" / 병렬성 4요소: **Grammar, Logical category, Capitalization, Punctuation** / "Consider starting all items in a numbered list with an imperative verb" / **lead-in 문장 규칙**: 모든 목록·표는 그것이 무엇인지 알려주는 문장으로 도입하고 **콜론**으로 끝낸다, 가능하면 "following"을 포함("The following list identifies key performance parameters:")

### 2.2 Microsoft Writing Style Guide [원출처]

- 철학: "crisp and clear", **"write for scanning first, reading second"**
- https://learn.microsoft.com/en-us/style-guide/scannable-content/
  - "Content on the first screen (also called *above the fold*) is the most likely to be read."
  - "Be brief, be bold, be clear" → "1. Use short, simple words. 2. Get to the point. 3. Then stop."
  - **문단 길이 수치 기준: "Three to seven lines is about the right length for a paragraph."**
  - "Lead with what's most important. Place important keywords near the beginning of headings, table entries, and paragraphs so they're easy to spot." (front-loading)
  - 긴 문서에는 내부 내비게이션(TOC + "Back to top")을 반드시 제공
  - 패턴 확립: "Apply the same sentence structures to similar information."
- 문장 길이: 쉼표가 몇 개 이상이면 복문 신호 — 쪼개라 (top-10 tips, https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice)
- 표 규칙 https://learn.microsoft.com/en-us/style-guide/scannable-content/tables — *우리 진단 직결*
  - **"Don't use a table just to present a list of items that are similar. Use a list instead."**
  - 표가 유용한 경우 4가지: 데이터/값, 단순 지시(액션↔단축키), 범주+예시, **두 개 이상의 속성을 가진 것들의 모음**
  - "Place information that identifies the contents of a row in the leftmost column."
  - "Make entries in a table parallel."
  - **빈 셀·em dash 금지 → "Not applicable" 또는 "None"**
  - **"Limit the number of columns and keep the text in each cell brief—ideally one line."** ← 고밀도 표에 대한 가장 직접적인 반대 규칙
  - 헤더는 구체적으로("Name" 대신 "Group"/"Employee"). 헤더+셀이 합쳐져 한 문장이 되게 구성하지 말 것(현지화 저해).
  - 표 도입 문장은 **완전한 문장 + 마침표**(Google은 콜론 — 두 가이드가 갈리는 지점)
  - 긴 표는 헤더 행 고정/반복.

### 2.3 Write the Docs 커뮤니티 합의 [원출처]

https://www.writethedocs.org/guide/writing/docs-principles/
- **ARID** — "Accept (some) Repetition In Documentation." DRY를 문서에 엄격히 적용하면 안 된다. 코드가 표현한 비즈니스 로직은 문서에서 **다시** 서술되어야 한다.
- **Skimmable** — "Structure content to help readers identify and skip over concepts which they already understand or are not relevant to their immediate questions."
- **Exemplary** — 예시·튜토리얼을 (일부) 포함하되 과적재 금지.
- **Consistent**, **Current** — "Consider incorrect documentation to be worse than missing documentation."
- **Nearby** — 문서는 코드 가까이.
- **Unique** — 별도 소스 간 내용 중복 제거(병렬 유지보수 방지). ※ ARID와 긴장 관계: *한 문서 안의 재진술은 허용, 여러 출처 간 중복은 금지*.
- **Discoverable / Addressable**(딥링크 가능) / **Cumulative**(선행 개념 먼저) / **Complete**(부분 커버리지 금지) / **Beautiful** / **Comprehensive**
- **Precursory** — "Begin documenting before you begin developing."

보조: The eight rules of good documentation (Adam Scott, O'Reilly, https://www.oreilly.com/content/the-eight-rules-of-good-documentation/) — inviting&clear / comprehensive / **skimmable** / examples / **useful repetition** / up-to-date / easy to contribute / easy to find

### 2.4 INNOQ "Principles of technical documentation" [2차, 아키텍처 문서 특화]

https://www.innoq.com/en/blog/2022/01/principles-of-technical-documentation/
- Req-1 Correct / Req-2 Current / Req-3 Understandable / Req-4 **Relevant (task-oriented)** / Req-5 **Referenceable** — "Use a consistent numbering schema for headings, diagrams and tables" / Req-6 Proper language — **"brief sentences (15–20 words average)"** (수치 기준) / Req-7 Maintainable — 불필요 디테일 생략·구체를 추상화 / Req-8 Easy to find / Req-9 Version controlled / Req-10 Proper tools / Req-11 Continuously updated(DoD 편입)

### 2.5 실측 근거 — 사람은 얼마나 읽는가 [원출처, NN/g]

- https://www.nngroup.com/articles/how-little-do-users-read/ — "users have time to read at most 28% of the words during an average visit", 현실 추정 **~20%**. 100단어 추가당 체류 +4.4초. **"users read half the information only on those pages with 111 words or less."**
- https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/ — F자 패턴(상단 가로 → 아래쪽 짧은 가로 → 좌측 세로). 실무 함의: "The first two paragraphs must state the most important information." / "Start subheads, paragraphs, and bullet points with information-carrying words that users will notice when scanning down the left side." / "Exhaustive reading is rare."
- 시사: **왼쪽 첫 단어가 정보를 담아야 한다** → 표의 첫 열, 목록 항목의 첫 단어, 헤딩의 첫 단어 설계가 가독성의 지렛대.

### 2.6 우리 문서 유형별 적용 후보

- **BR 대장 / 계약(표)**: MS "셀 텍스트는 이상적으로 한 줄", Google "3개 이상 관련 데이터일 때만 표" → 2열 표는 description list로 강등, 셀에 문단이 들어간 표는 표를 쪼개거나 본문으로 승격. 빈 셀은 "해당 없음"으로 명시(무음 누락 방지 — 검증 관점과도 합치).
- **전 문서**: lead-in 문장 규칙(모든 표·목록 앞에 "이 표는 X를 나타낸다" 한 줄) — 표만 던지는 현재 스타일의 최소 비용 개선.
- **교차참조**: "링크 하나 = 독자의 의사결정 하나" 원칙으로 링크 예산을 세우고, 용어 정의·짧은 절차는 인라인 해결. 동일 대상 중복 링크 제거.
- **헤딩**: 절차서·워크플로우는 원형동사 헤딩("계좌를 개설한다" 형태), 연속 헤딩(내용 없는 헤딩) 제거.
- **front-loading**: 각 문서 첫 화면에 결론/핵심을 배치, 각 섹션 첫 문장에 키워드.

---

## 축 3 — ADR 작성론

### 3.1 Nygard 원형 (2011) [원출처]

https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- 문제의식: **"Nobody ever reads large documents, either. Most developers have been on at least one project where the specification document was larger (in bytes) than the total source code size."** → bite-sized 문서가 최신성·소비 가능성 양쪽에서 유리하다.
- 템플릿:
  - **Title** — "short noun phrases. For example, 'ADR 1: Deployment on Ruby on Rails 3.0.10'"
  - **Status** — proposed / accepted / deprecated / superseded
  - **Context** — "describes the forces at play, including technological, political, social, and project local", **value-neutral** 사실 서술
  - **Decision** — "describes our response to these forces. It is stated in full sentences, with active voice. 'We will …'"
  - **Consequences** — "describes the resulting context, after applying the decision. **All consequences should be listed here, not just the 'positive' ones.**"
- 불변성/승계: "we will keep the old one around, but mark it as superseded. (It's still relevant to know that it *was* the decision, but is *no longer* the decision.)"

### 3.2 왜 맥락→결정→결과 순서인가 (해석)

- Context가 먼저인 이유: 결정은 **힘의 균형에 대한 응답**이므로, 힘을 모르면 결정을 평가할 수 없다. 미래의 독자가 "그 힘이 아직 유효한가"를 판정해 결정의 유효기간을 스스로 판단하게 한다.
- Consequences가 마지막인 이유: 결정 **이후의 맥락**(resulting context)이므로 다음 ADR의 Context 입력이 된다 — ADR 체인은 `Consequences(n) → Context(n+1)` 로 이어진다.
- 실무 확증: gRPC 사례 — "an architect chose gRPC for low latency. Years later, another architect refactored to messaging 'for decoupling,' not knowing about the latency requirement. Knowing the why would have prevented the mistake." (https://bool.dev/blog/detail/10-adr-antipatterns) [실무 의견]

### 3.3 나쁜 ADR — 안티패턴 카탈로그 [원출처급, Olaf Zimmermann]

https://ozimmer.ch/practices/2023/04/03/ADRCreation.html
- 주관성: **Fairy Tale**(얕은 정당화, 장점만) · **Sales Pitch**(마케팅 언어) · **Free Lunch Coupon**(어렵거나 장기적인 결과를 누락) · **Dummy Alternative**(들러리 대안)
- 시간축: **Sprint**(옵션 하나·단기 효과만) · **Tunnel Vision**(운영/유지보수 관점 누락) · **Maze**(주제와 내용 불일치, 지엽으로 탈선)
- 크기/내용: **Blueprint/Policy Disguise**(결정 일지가 아니라 권위적 요리책처럼 읽힘) · **Mega-ADR**(상세 설계·다이어그램·코드 스니펫으로 부푼 수 페이지) · **Novel/Epic**(SAD 전체를 ADR 하나에)
- 조작: **Magic Tricks**(거짓 긴급성, 문제-해결 불일치, 의심스러운 스코어링에 의한 유사 정밀도)
- 좋은 실천 7: 중요도로 선별 / 되돌리기 비싼 결정은 sprint 3 이전에 / 메타품질(관측성·적응성) 우선 / **"Be as objective as possible; no vendor bashing, no blaming and no sarcasm"** / **편집 품질 투자 — 길이를 감시하라(때로 슬라이드 1장이면 충분, 복잡하면 여러 페이지)** / 결정을 단계로 분할(단기 타협·중기 해법·장기 비전) / **확신 수준 공개**

보완: https://adr.github.io/ad-practices/ — Definition of Ready / architectural significance test / **"Normalise your criteria DOWN to the same level of abstraction"**(기준의 추상 수준을 통일) / Definition of Done 5요소(근거, 기준·대안, 이해관계자 합의, 문서화, 구현·리뷰 전략) / **결정 하나당 ADR 하나**

- 다른 두 안티패턴 [실무 의견]: **Groundhog Day**(왜인지 아무도 몰라 끝없이 재논의) · **Email-Driven Architecture**(결정이 메일 스레드에 묻힘). 실 저장소 관찰: "supersession links nobody updated, ADRs orphaned by authors who left two years ago, and entries marked 'Accepted' that the team quietly stopped following."

### 3.4 우리 ADR 25건 적용 후보

- **Mega-ADR / Blueprint 검사**: ADR에 상세 설계표·코드가 들어가 있으면 explanation(ADR)과 reference(설계 문서)의 혼입 — Diátaxis 진단과 동일 결론.
- **Consequences에 부정 결과가 있는가**를 25건 전수 점검(Fairy Tale / Free Lunch Coupon 스캔). 없으면 ADR이 아니라 홍보문.
- **Dummy Alternative 점검**: 대안이 형식적으로만 나열되고 기각 사유가 없는 건.
- **status 정합성 점검**: superseded 링크 미갱신, Accepted인데 실제로 안 지켜지는 건 → 대장과 실코드 대조.
- **확신 수준 필드 추가 검토**(ozimmer 실천 7) — 우리 하네스의 "load-bearing 가정" 개념과 자연스럽게 결합.
- **표 압축 금지**: ADR은 서술형이 정본. 25건을 한 장 요약표로 대체하려는 유혹은 Context 소실(=gRPC 사례)을 부른다. 대신 **인덱스 표(제목·상태·날짜·상위 결정) + 본문 서술** 이중 구조.

---

## 축 4 — 명세·계약 문서

### 4.1 RFC 2119 / 8174 [원출처]

https://www.rfc-editor.org/rfc/rfc2119
- MUST / REQUIRED / SHALL — "an absolute requirement of the specification"
- MUST NOT / SHALL NOT — "an absolute prohibition of the specification"
- SHOULD / RECOMMENDED — "there may exist valid reasons in particular circumstances to ignore a particular item, but **the full implications must be understood and carefully weighed** before choosing a different course"
- SHOULD NOT / NOT RECOMMENDED — 특정 상황에서 허용되거나 유용할 수 있으나 함의를 이해하고 신중히 판단해야 함
- MAY / OPTIONAL — "truly optional". 한 벤더가 넣고 다른 벤더가 빼도 무방.
- **절제 조항(가장 자주 무시되는 부분)**: 이 조동사들은 "must be used with care and sparingly"이며 "only be used where it is actually required for interoperation or to limit behavior which has potential for causing harm". 상호운용에 필요하지 않은데 특정 방법을 구현자에게 강요하는 데 쓰지 말 것.

**단점/보정 — RFC 8174** (https://www.rfc-editor.org/rfc/rfc8174)
- 원래 RFC 2119는 키워드가 "often capitalized"라고만 해서 소문자 must/should의 해석이 모호했다. RFC 8174은 **대문자 표기만** 규범적 의미를 갖는다고 확정.
- 실무 함의: 옵션과 의무를 혼동하면 "Two vendors can read the same sentence, build to opposite conclusions, and ship products that refuse to talk to each other." [2차, rfc-explained.com]
- 남용 문제: SHOULD의 과용은 실질적으로 "요구사항이 아님"을 뜻하게 되어 명세를 무력화. → 우리 계약 문서에서 SHOULD 사용 시 **"무시해도 되는 valid reason"을 함께 적지 않으면 SHOULD를 쓰지 않는다**는 규칙이 파생 가능.

### 4.2 API 레퍼런스 모범 — Stripe가 칭송받는 구체 이유 [2차, 티어다운]

https://writechoice.io/blog/best-api-documentation-stripe-teardown · https://www.moesif.com/blog/best-practices/api-product-management/the-stripe-developer-experience-and-docs-teardown/
1. **3열 레이아웃** — 좌: 내비, 중: 설명, 우: 실행 가능한 코드. 스크롤하면 우측 코드가 따라온다. 해결하는 문제는 미학이 아니라 **워크플로우**: 설명↔코드 왕복 스크롤 제거. "the right column is never empty—there is always something a developer can copy."
2. **레퍼런스와 가이드의 표면 분리** — "Treat your API reference and your getting-started guides as separate sections with separate navigation. Link between them liberally, but don't merge them." 병합하면 "too long for quick lookups and too fragmented for learning" — **Diátaxis의 reference/tutorial 분리와 정확히 같은 결론에 독립적으로 도달**.
3. **동작하는 예제** — 동일 연산을 cURL/Python/Ruby/Node/Go/Java/.NET/PHP로. 실제 값이며 테스트 환경에서 실행하면 진짜 응답이 온다. 로그인 상태면 **본인의 테스트 API 키가 자동 삽입**.
4. **행위 지향 헤딩** — "Every heading in Stripe's docs tells you what you're about to do. 'Create a customer.' 'Accept a payment.'" ("Customer creation overview" 같은 추상 헤딩 배제)
5. **인라인 정의** — "When Stripe introduces a concept like idempotency keys or payment intents, they define it in one sentence before using it… Right there, inline, the first time the term appears." ← Google의 "provide help in context rather than linking elsewhere"와 동일. **교차참조 과다 문제의 표준 해법**.
6. **에러 문서화** — 상태 코드가 아니라 (a) 사람이 읽는 설명 (b) 프로그램 처리용 `code` 필드 (c) 해당 문서로 직행하는 `doc_url`.

### 4.3 표 기반 명세의 한계론 (수집된 근거의 종합)

직접적인 "표 기반 명세 한계론" 단일 정전은 찾지 못했다. 대신 각 스타일 가이드가 **표의 적용 조건을 좁게 규정**하는 형태로 한계를 명시한다:
- Google: 표는 "three or more pieces of related data"일 때만. **번호 절차 안에 표 금지**, "long one-dimensional lists in multiple columns" 금지, 단일 열 금지, 셀 병합 금지.
- Microsoft: **"Don't use a table just to present a list of items that are similar."** / **"keep the text in each cell brief—ideally one line"** / 헤더+셀이 합쳐져 문장이 되게 하지 말 것.
- Diátaxis: 표는 reference의 형식이며, reference는 "boring and unmemorable"하고 **읽히는 게 아니라 조회된다**. 즉 *표에 담긴 것은 통독되지 않는다*는 것이 전제 — 서사가 필요한 내용(설계 근거, 결정)을 표에 담으면 그 내용은 사실상 전달되지 않는다.
- NN/g: 사용자는 페이지의 ~20%만 읽으며 좌측 세로 스캔이 지배적 → 표의 **첫 열**만 읽힐 가능성이 높다. 오른쪽 열에 든 핵심은 유실 위험.
- arc42는 반대 방향의 조언도 준다: **"Use tables instead of lengthy prose"**(Tips 4-2, 5-7, 7-7, 12-2, lean 태그) — 즉 표는 *긴 산문의 대체*로는 권장되나, *서사의 대체*로는 아니다. 두 조언의 경계 = **항목들이 동형(homogeneous)이고 각 셀이 짧을 때만 표**.
- [구현 검증] 우리 문서의 실제 표 중 "셀이 2줄 이상" 또는 "열이 5개 이상"인 비율은 실파일 계측 필요.

### 4.4 우리 문서 유형별 적용 후보

- **유스케이스 계약**: RFC 2119 조동사를 도입하되 **절제 조항까지 함께 도입**(상호운용/피해 방지에 필요한 곳만 MUST). 대문자 표기만 규범적임을 문서 서두에 명시(RFC 8174 방식 보일러플레이트).
- **계약 문서 구조**: Stripe식 "레퍼런스 표면 / 가이드 표면 분리 + 상호 링크". 계약 표 옆에 항상 **실행 가능한 예(샘플 요청·응답·경계값)**를 둔다.
- **에러/예외**: 코드만 나열하지 말고 (사람용 설명 / 프로그램용 코드 / 상세 문서 링크) 3요소.
- **용어**: 최초 등장 시 한 문장 인라인 정의 — 용어집 링크로 대체하지 않는다.
- **BR 대장**: 첫 열(가장 많이 읽히는 열)에 식별자가 아니라 **의미를 담는 이름**을 배치할지 재검토(F패턴 근거).

---

## 축 5 — Minimalism (John M. Carroll)

### 5.1 이론의 출발점 [원출처/2차]

- 실증 기원: IBM에서 Carroll(1984)이 워드프로세서 신규 사용자를 1:1로 대량 관찰한 실증 연구에서 출발. (https://www.stc.org/techcomm/2021/02/04/minimalism-heuristics-revisited-developing-a-practical-review-tool/)
- 대표 실험: **94쪽 매뉴얼을 25장의 카드로 대체**했더니 사용자가 **약 절반의 시간에** 과제를 학습. (https://www.instructionaldesign.org/theories/minimalism/)
- "The Minimal Manual"(1987–88)의 4특성: (1) brevity/conciseness (2) **focus on real tasks** (3) **support of error recognition and recovery** (4) **guided exploration**.
- 『The Nurnberg Funnel』(1990): 명시적 지시를 **극단적으로 줄이고** 사용자가 주로 탐색을 통해 학습하게 하는 접근을 재정식화. 제목 자체가 "깔때기로 지식을 부어 넣을 수 있다"는 환상에 대한 반어.

### 5.2 다섯 원칙 [원출처 요약]

1. "All learning tasks should be meaningful and self-contained activities"
2. "Learners should be given realistic projects as quickly as possible"
3. "Instruction should permit self-directed reasoning and improvising by increasing the number of active learning activities"
4. "Training materials and activities should provide for error recognition and recovery"
5. "There should be a close linkage between the training and actual system"

운용 휴리스틱 4: 즉시 의미 있는 과제 시작 / 수동적 학습 최소화(사용자가 빈틈을 채우게) / **오류 인식·복구 활동 포함** / 각 학습 활동은 자기완결적이고 **순서 독립적**

### 5.3 후속 실증과 한계 [2차/학술]

- van der Meij & Carroll(1995, 1998)이 휴리스틱으로 정식화. "The heuristics… are based on solid empirical research, and are intended as a tool for developing documentation."
- 한계 인정: "the abstract nature of the approach and its focus on software documentation has made it difficult to apply in industry settings; consequently, there is very little evidence on the suitability of minimalism for software documentation and no evidence at all for hardware documentation." (Vaasa 대학 논문, https://osuva.uwasa.fi/bitstreams/e96bd3f9-c878-49ae-9cc0-e5774f840bdf/download)
- → 미니멀리즘은 **학습 상황(튜토리얼)에서 강한 증거**, 레퍼런스·계약 문서에는 직접 이식되지 않는다. 우리 문서군에서는 워크플로우·온보딩 문서에 우선 적용.

### 5.4 우리 문서 유형별 적용 후보

- **워크플로우 / 온보딩**: "94쪽→25카드" 실험이 가장 직접적인 벤치마크. 현재 워크플로우 문서를 *실제 과제 단위 카드*로 재편하고, 각 카드는 **자기완결·순서 독립**.
- **운영 절차서**: **오류 인식·복구 절차를 1급 콘텐츠로 승격**("이 단계가 실패하면 어떻게 보이는가 / 어떻게 되돌리는가"). 지금 절차서가 정상 경로만 다룬다면 미니멀리즘 관점의 최대 결함.
- **전 문서**: "읽기 최소화" — 문서를 읽는 데 드는 시간을 비용으로 계상하고, 통독 전제를 버린다(NN/g 20% 실측과 결합).
- 주의: 미니멀리즘을 **BR 대장·계약에 적용하면 안 된다**(완전성이 계약의 본질). 유형별 분기가 필수.

---

## 축 6 — Information Mapping (Robert E. Horn, 1972)

### 6.1 구성 [2차 — 1차 자료는 유료/절판]

https://ivacheung.com/2012/11/introduction-to-information-mapping/ · https://medium.com/technical-writing-is-easy/information-mapping-in-technical-writing-5e772f7dc47c

**3 요소**: analysis → organization → presentation

**6 정보 유형** (거의 모든 기술·비즈니스 커뮤니케이션을 포괄한다는 주장):
| 유형 | 정의 |
|---|---|
| Procedure | "instructions on how to do something" |
| Process | "description of how something works" |
| Principle | "description of a standard or a convention" |
| Concept | "description of a new idea or object" |
| Structure | "description of an object's components" |
| Fact | "empirical information" |

**조직 원칙 6** (연구 기반): **chunking**(작고 다룰 수 있는 덩어리로) · **relevance**("limit each group or 'unit of information' to a single topic, purpose, or idea") · **labeling**("give each unit of information a meaningful name") · **consistency**(용어·형식·조직·표기의 일관) · **integrated graphics**(그래픽을 본문과 통합) · **accessible detail**(필요한 상세에 도달 가능하게)

**구조**: information block(단일 주제·**단일 정보 유형**; 문장·목록·표·그래픽 포함 가능) → information map(관련 block들만) → topic → document. 각 block은 **라벨을 좌측에 두고 시각적으로 분리**하여 스캔·재사용을 가능케 한다.

### 6.2 Diátaxis와의 관계 (분석)

- Horn의 "block = 단일 유형" 규칙은 Diátaxis의 "문서 = 단일 유형" 규칙의 **더 작은 입자 버전**이다. Diátaxis 저자도 compass를 "문장 수준부터 문서 수준까지" 적용하라고 한다("Do I think I am writing for *x* or *y*?" applied at different scales).
- 실무적 이점: 문서 전체를 4분류로 쪼개면 HN이 지적한 "링크 지옥"이 생기지만, **한 문서 안에서 블록 단위로 유형을 라벨링**하면 분리와 응집을 동시에 얻을 수 있다 → 우리 상황(교차참조 과다)에 대한 유력한 절충안.

### 6.3 우리 문서 유형별 적용 후보

- **모든 문서**: 섹션마다 정보 유형 라벨을 명시(예: `[사실]` `[절차]` `[원칙]` `[개념]`). 한 섹션에 두 유형이 섞이면 분리 신호.
- **BR 대장**: 각 BR = 하나의 block. 라벨(=BR 이름)이 좌측에서 스캔 가능해야 함(F패턴과 합치).
- **절차서**: Procedure와 Process를 분리 — "어떻게 하는가"와 "어떻게 동작하는가"가 한 문단에 섞이는 것이 절차서 가독성 저하의 전형.
- **accessible detail**: 상세는 삭제하지 말고 *접기/별도 블록/링크*로 계층화 — 검증 최적화를 잃지 않으면서 읽기 부담을 낮추는 유일한 합법 경로.

---

## 축 7 — docs-as-code 실무 / 문서 린트

### 7.1 Vale [원출처]

https://vale.sh/ · https://docs.vale.sh/
- 구조: **rule(YAML)** → **style(폴더)** → **.vale.ini(레포 루트)**. Markdown/AsciiDoc/reStructuredText/HTML을 마크업 문법을 무시하고 산문만 검사.
- **확장 지점(check 타입)** (https://docs.vale.sh/topics/styles.md):
  | 타입 | 검사 내용 |
  |---|---|
  | existence | 특정 정규식 패턴의 존재 |
  | substitution | 패턴을 지정 문자열로 치환(권장 표현 강제) |
  | occurrence | 패턴의 **출현 횟수** 상한/하한 |
  | repetition | 같은 패턴의 반복 회피 |
  | consistency | 둘 중 하나로 일관되게 사용(예: advisor/adviser) |
  | conditional | 조건부 존재 강제(예: 약어를 쓰면 앞에 정의가 있어야 함) |
  | capitalization | 지정 방식의 대소문자(sentence case/title case) |
  | metric | **가독성 등 커스텀 수식** 검사 |
  | spelling | Hunspell 사전 |
  | sequence | 품사 태깅 지원, 특정 순서 강제 |
  | script | Tengo 스크립트 커스텀 검사 |
  - *우리에게 중요한 두 가지*: **occurrence**로 문장 길이·단락당 링크 수 상한을 강제할 수 있고, **capitalization**으로 헤딩 sentence case를 강제할 수 있으며, **metric**으로 가독성 지표를 게이트화할 수 있다.
- 공식 스타일 패키지(errata-ai): **Google 스타일 규칙 파일 목록** (https://github.com/errata-ai/Google) — AMPM, Acronyms, Colons, Contractions, DateFormat, Ellipses, EmDash, Exclamation, FirstPerson, Gender, GenderBias, HeadingPunctuation, **Headings**(sentence case), Latin, LyHyphens, OptionalPlurals, Ordinal, OxfordComma, Parens, **Passive**, Periods, Quotes, Ranges, Semicolons, Slang, Spacing, Spelling, Units, We, WordList, Will 등. Microsoft 스타일 패키지도 동형으로 제공(Wordiness, Contractions, Passive 등).
- 추가 상용 스타일: Anthropomorphism, ExcessiveClaims, Jargon, Timeless(시간 종속 표현 금지) 등.

### 7.2 가독성을 리뷰 게이트로 거는 사례

- **Elastic**: 자체 스타일 가이드를 Vale 규칙으로 배포하고 문서 기여 절차에 편입 (https://github.com/elastic/vale-rules · https://www.elastic.co/docs/contribute-docs/vale-linter)
- **GitHub Action**: "The Vale action… runs Vale checks on pull requests that include documentation changes. The action reports any style issues found in **modified lines** in the form of a sticky comment. Issues are reported in the form of **errors, warnings, and suggestions**." → **변경 라인만 검사 + 3단계 심각도**가 실무 표준 패턴(전면 적용 시 노이즈 폭발 회피).
- **GitLab**: Vale를 문서 린터로 도입하는 이슈가 공개 트래킹 (https://gitlab.com/gitlab-org/gitlab/issues/38053)
- **Stoplight**: 도입 회고 — 자동 검사가 사람 리뷰어를 "내용"에 집중하게 해준다는 논지 (https://blog.stoplight.io/linting-the-stoplight-docs-with-vale)
- 커뮤니티 요약 [실무 의견]: "The same arguments for linting code apply to linting prose: catch consistency errors automatically, **free human reviewers to focus on substance**, lower the barrier to contribution." (https://tw-docs.com/docs/vale/vale-styleguides/)

### 7.3 우리 문서 유형별 적용 후보

- **가장 실행 가능한 즉효 조치**: `.vale.ini` + Google/Microsoft 스타일 패키지를 docs 레포에 도입하고 **변경 라인만, suggestion 심각도로 시작** → 점진 승격.
- **우리 진단에 맞춘 커스텀 규칙 후보**(Vale로 실제 강제 가능):
  - `occurrence`: 문장당 최대 단어 수(≈25), 단락당 최대 링크 수(예: 3), 표 셀 최대 길이는 script 필요
  - `capitalization`: 헤딩 sentence case
  - `existence`: "위 표 참조", "아래 참조", "해당 문서 참조" 같은 **비서술적 상호참조 문구** 금지
  - `conditional`: 약어/BR ID 최초 등장 시 정의가 선행하는지
  - `existence`: 소문자 must/should를 규범적으로 쓴 경우 경고(RFC 8174 대응)
- **문서 리뷰 게이트**: 우리 하네스의 "듀얼 1패스"에 **가독성 렌즈**를 추가 — 자동 린트가 잡는 것(형식)과 사람이 잡는 것(구조·유형 혼입)을 분리.

---

## 축 8 — 소프트웨어 아키텍처 문서화 (arc42 / C4)

### 8.1 arc42 [원출처]

https://arc42.org/overview/ · https://docs.arc42.org/
- 목적: "answers two questions in a pragmatic way: **what** should you document and communicate about your architecture, and **how**."
- 12 섹션(각 절 = 명확한 목적, 모든 하위 절은 선택적):
  1 Introduction & Goals / 2 Constraints / 3 Context & Scope / 4 Solution Strategy / 5 Building Block View(보통 가장 방대) / 6 Runtime View / 7 Deployment View / 8 Crosscutting Concepts / 9 Architectural Decisions / 10 Quality Requirements / 11 Risks & Technical Debt / 12 Glossary
- **"어느 층에 무엇을 얼마나" 원칙 — arc42 tips** (https://docs.arc42.org/keywords/):
  - Tip 4-1 "Explain the solution strategy as compact as possible (e.g. as list of keywords)!"
  - Tip 3-5 "Restrict the context to an overview, avoid too many details!"
  - Tip 1-16 "Describe only the **top 3–5 quality goals** in the introduction!" (상세 품질 요구는 섹션 10으로 이연 — Tip 1-18)
  - Tip 12-5 "Keep the glossary compact! Avoid trivia."
  - Tip 5-28 반복적으로 building block을 문서화하기보다 **개념(concept) 설명을 우선**하라
  - Tip 9-1 아키텍처적으로 유의미한 결정만 포함
  - lean 태그: "Use tables instead of lengthy prose" (4-2, 5-7, 7-7, 12-2), Tip 6-3 시나리오는 상세가 아닌 개략으로
  - **arc42 canvas**: 시스템 전체를 한 페이지로 — 초경량 옵션
- 핵심 설계 원리: **상세는 삭제가 아니라 이연(defer)**. 같은 정보를 상위 절에서 요약하고 하위 절에서 상세화하되, **중복 서술이 아니라 참조로 연결**.

### 8.2 C4 model (Simon Brown) [원출처/2차]

https://c4model.com/ · https://c4model.com/faq
- 4 추상 수준: Context → Container → Component → Code. 보조 다이어그램: System Landscape, Dynamic, Deployment.
- 핵심 은유: **"maps of your code"** — Google Maps처럼 줌 인/아웃. 각 다이어그램은 하나의 줌 레벨에서만 말한다.
- 오해 교정 [원출처 FAQ]: "The C4 model is just a way to describe a software system, from different levels of abstraction, and it implies nothing about the process of delivering software." → **4단계를 전부 그려야 하는 것이 아니다**. 또 "레벨별로 담당자를 나눈다"는 것은 의도된 사용 패턴이 아니다.
- 복잡도 대응: "don't be afraid to split that single complex diagram into a larger number of simpler diagrams, each with a specific focus around a business area, functional area, functional grouping, bounded context, use case, user interaction, feature set, etc."
- 보완 필요성 [원출처 FAQ]: "If you need to describe other aspects, feel free to supplement the C4 diagrams with UML diagrams, BPML diagrams, ArchiMate diagrams, entity relationship diagrams, etc." → **다이어그램만으로는 부족하며 서술로 보완**한다는 입장.

### 8.3 "문서는 짧을수록 읽힌다" — 주장과 반론

**찬성 측 근거**
- Nygard [원출처]: "Nobody ever reads large documents… the specification document was larger (in bytes) than the total source code size." → bite-sized 단위가 최신성·소비 가능성을 확보.
- NN/g [실측]: 평균 방문에서 최대 28%, 현실 ~20%만 읽힘. **111단어 이하 페이지에서만 절반이 읽힌다.**
- Microsoft [원출처]: "write for scanning first, reading second", 문단 3~7줄.
- Carroll [실증]: 94쪽 → 25카드로 학습 시간 절반.
- arc42 [원출처]: 요약·이연·compact 지시가 곳곳에.

**반론 / 조건부 반박**
- Write the Docs **Complete** 원칙 [원출처]: "Cover chosen concepts fully or not at all" — **부분 커버리지가 완전 미커버리지보다 나쁠 수 있다**(오도).
- Write the Docs **ARID** [원출처]: DRY를 문서에 엄격 적용하면 실패. 짧게 만들려는 압력이 필요한 재진술까지 제거한다.
- Diátaxis [원출처]: reference는 "boring and unmemorable"해도 **완전해야** 하며, 축약이 미덕이 아니다. 짧음은 튜토리얼·how-to의 미덕이지 reference의 미덕이 아니다. → **"짧을수록 좋다"는 문서 유형별로 참/거짓이 갈린다**.
- ozimmer [원출처]: ADR 길이는 "sometimes one slide suffices, complex issues may require several pages" — 길이는 **주제 복잡도의 함수**이지 상수가 아니다.
- INNOQ [2차]: Maintainable 원칙 = 불필요 상세 생략이지만, Correct/Comprehensive는 유지 — 짧게 만드는 방식은 **삭제가 아니라 추상화**여야 한다.
- HN [실무 의견] (https://news.ycombinator.com/item?id=41894814 계열 논의 요약, https://news.ycombinator.com/item?id=42325011): 읽히지 않는 진짜 원인은 길이가 아니라 ① **지식의 저주**(작성자는 너무 많이 알고 독자는 너무 적게 안다) ② **코드와 분리된 도구**에 문서가 살아서 ③ **오래됨**. 짧게 쓴다고 해결되지 않는다.

**종합 판정(우리 상황용)**: 길이가 아니라 **밀도(density)와 유형 혼입**이 문제다. 같은 정보량이라도 (a) 유형별로 분리하고 (b) 블록 라벨을 붙이고 (c) 상세를 이연하면 읽힌다. "짧게 쓰기"를 목표로 삼으면 BR 대장·계약의 완전성을 훼손한다.

### 8.4 우리 문서 유형별 적용 후보

- **문서 지도(문서 인덱스)**: C4의 "maps" 은유를 문서 자체에 적용 — 50편 위에 **줌 레벨 1장**(어떤 문서가 어떤 층인지)을 두면 교차참조 부담이 크게 준다.
- **arc42 매핑 점검**: 우리 50편이 arc42 12절 중 어디에 해당하는지 매핑해 **누락 층**과 **중복 층**을 찾는다. 특히 Solution Strategy(4)와 Crosscutting Concepts(8)이 없으면 독자는 개별 문서를 전부 읽어야만 전체를 구성할 수 있게 된다 — 교차참조 과다의 구조적 원인일 가능성.
- **상세 이연 규칙 도입**: "상위 문서는 top 3–5개만, 상세는 하위 문서에서" (arc42 Tip 1-16 방식)를 우리 문서 규약으로 성문화.

---

## 부록 A — 교차 확인된 합의(여러 출처가 독립적으로 같은 결론)

| 합의 | 출처 |
|---|---|
| 문서 유형(레퍼런스 vs 학습)을 물리적으로 분리하라 | Diátaxis(원출처) · Stripe 티어다운(실무 관찰) · Nygard(ADR을 별도 소형 문서로) |
| 용어·개념은 **최초 등장 시 인라인 한 문장 정의**, 링크로 대체하지 말라 | Google cross-references(원출처) · Stripe 티어다운 · Diátaxis tutorials("don't explain, link" — 단, 튜토리얼 한정) |
| 표는 **동형 항목 + 3개 이상 속성 + 짧은 셀**일 때만 | Google tables · Microsoft tables · (arc42는 "긴 산문 대신 표"를 권하나 lean 맥락 한정) |
| front-loading(중요한 것을 앞·왼쪽에) | Microsoft scannable content · NN/g F패턴 · Google headings |
| 병렬 구조(문법·범주·대소문자·구두점) | Google lists · Google tech writing one · Microsoft tables |
| 결과·결점을 반드시 함께 적어라 | Nygard Consequences("not just the positive ones") · ozimmer(Fairy Tale/Free Lunch 안티패턴) · Diátaxis explanation("must consider alternatives, counter-examples") |
| 문서 개선은 점진적으로, 전면 재편 금지 | Diátaxis how-to-use · Vale 실무(변경 라인만 검사) · arc42(선택적 절) |

## 부록 B — 상충 지점(그대로 채택하면 안 되는 것)

1. **표 도입 문장의 종결부호**: Google = 콜론 / Microsoft = 마침표. → 우리 규약에서 하나를 택해 성문화.
2. **ARID(재진술 허용) vs Unique(중복 금지)**: Write the Docs 내부에서도 긴장. 해석 = *한 문서 안의 재진술은 독자를 위해 허용, 여러 문서 간 동일 사실의 병렬 유지보수는 금지*.
3. **arc42 "표로 산문을 대체" vs Google/MS "표를 남용 말라"**: 경계는 항목의 동형성과 셀 길이.
4. **Minimalism(극단적 축약) vs 계약·대장의 완전성**: 문서 유형별로 적용/비적용을 명시적으로 갈라야 함.
5. **Diátaxis 엄격 분리 vs 링크 지옥**: Horn의 블록 단위 라벨링이 절충안.

## 부록 C — 미해결 / [구현 검증] 이연

- 우리 문서의 실제 표 밀도(열 수 분포, 셀 줄 수 분포), 문서당 교차참조 수, 문장 길이 분포 — 실파일 계측 필요.
- Vale 규칙의 한국어 문서 적용 가능성(품사 태깅·문장 분할이 영어 전제) — 실측 필요. 대안: 자체 script/metric 규칙 또는 형식(헤딩·링크·표 열수)만 검사.
- van der Meij & Carroll의 원 heuristics 전문(유료 논문) — 미확보, 요약본만 확보.
- Information Mapping 1차 자료(Horn, *Mapping Hypertext*) — 미확보, 2차 요약만.
