> [보존] r5 리서치 원자료 — 2026-08-07 작성분 원문 무수정 이관. 규약 정본은 `docs/git-conventions.md`이며 이 파일은 근거 보관용이다.

# r5 — Git 협업 규약 정평 형식과 근거 (리서치 원자료)

- 작성: 2026-08-07 · 성격: **L0 리서치 근거 모음** (규약 정본 아님 — 정본 판정은 별도 작업)
- 방법: 명세 원문·공식 문서 직접 fetch 우선. 실무 의견은 **[실무 의견]** 표기. 주장마다 URL.
- ⚠️ 이 세션은 WebSearch 예산이 소진되어 **검색 없이 알려진 1차 출처를 직접 fetch**했다. 그 결과 *"업계에 무엇이 더 있나"*(발견형)는 약하고, *"정평 있는 원문이 무엇을 규정하나"*(확인형)는 강하다. 아래 「미확인 공백」 절이 그 한계를 명시한다.
- 우리 현재 세팅(실파일 확인 — `card-service/.github/` 등 리포별 동일):
  - 커밋: `docs/dev-conventions.md` **PR-7** — Conventional Commits `type(scope): 제목` + 빈 줄 + 본문, type ∈ `feat·fix·docs·refactor·test·chore·build`, **이모지 금지**
  - 흐름: **PR-8** — 마일스톤 → 이슈 → 이슈 기반 브랜치·MR
  - 이슈 템플릿: **yml form 4종**(기능 개발 / 버그 제보 / 리팩토링 / 성능 개선), 각 `title: "[Feature] "` 류 접두 + `labels: [feature|bug|refactor|performance]`, `config.yml` **없음**
  - PR 템플릿: `.github/PULL_REQUEST_TEMPLATE.md` — 3칸(요약 / 작업 내용 / 변경 유형)
  - 라벨: 리포 파일상 확인되는 것은 템플릿이 붙이는 **4종뿐**(feature·bug·refactor·performance). "12종"은 리포지토리 설정에만 존재하는 것으로 보이며 **파일로 관리되지 않는다**.

---

## 축 1 — 커밋 메시지 규약

### 1.1 Conventional Commits 1.0.0 (명세 원문)

출처: <https://www.conventionalcommits.org/en/v1.0.0/>

구조:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

규범 규칙 16개(원문 요지):

| # | 규칙 |
|---|---|
| 1 | 커밋은 **type 접두 필수** — 명사(`feat`, `fix` 등) + 선택 scope + 선택 `!` + **필수 종결 콜론+공백** |
| 2 | `feat` = 애플리케이션/라이브러리에 **새 기능 추가** 시 MUST |
| 3 | `fix` = **버그 수정** 시 MUST |
| 4 | scope는 **괄호로 감싼 명사** — 코드베이스의 한 구역. 예 `fix(parser):` |
| 5 | description은 콜론+공백 **직후** 위치, 변경의 짧은 요약 |
| 6 | body는 description **한 줄 띄고** 시작 |
| 7 | body는 자유 형식, 여러 문단 가능 |
| 8 | footer는 body 뒤 한 줄 띄고. 각 footer = `토큰` + (`:공백` 또는 `공백#`) + 값 |
| 9 | footer 토큰은 공백 대신 `-` 사용(`Acked-by`). **예외: `BREAKING CHANGE`** 는 공백 토큰 허용 |
| 10 | footer 값은 공백·개행 포함 가능. 다음 유효 토큰/구분자 쌍이 나오면 파싱 종료 |
| 11 | 파괴적 변경은 **type/scope 접두 또는 footer 항목**으로 MUST 표시 |
| 12 | footer 형태면 대문자 `BREAKING CHANGE:` + 공백 + 설명 |
| 13 | 접두 형태면 `:` **바로 앞에 `!`**. `!` 쓰면 footer의 `BREAKING CHANGE:` 생략 가능하고 description이 파괴적 변경 설명이 된다 |
| 14 | `feat`/`fix` 외 type **사용 가능**(예 `docs:`) — 명세는 목록을 고정하지 않는다 |
| 15 | 구성 단위는 **대소문자 비구분**으로 처리. 단 `BREAKING CHANGE`는 반드시 대문자 |
| 16 | `BREAKING-CHANGE`는 footer 토큰으로서 `BREAKING CHANGE`와 동의어 |

SemVer 연결(FAQ): `fix` → PATCH, `feat` → MINOR, `BREAKING CHANGE`(type 무관) → MAJOR.

> ★ 핵심: **명세는 type 목록도, 길이 제한(50/72/100)도 규정하지 않는다.** 그건 전부 Angular/commitlint 층에서 온다.

부가(<https://www.conventionalcommits.org/en/about/>): 목적은 *"human and machine readable meaning"*. 채택처 Electron·Jenkins X·freeCodeCamp·yargs 등. 도구 50종+ (commitlint·gitlint·semantic-release·standard-version·git-cliff, Java 구현체 포함). Angular 가이드라인에서 파생.

**우리와의 차이**: PR-7의 type 7종은 **명세가 아니라 우리의 선택**이므로(규칙 14) 정당하지만, 근거를 "Conventional Commits가 정했다"로 적으면 틀린 귀속이 된다.

### 1.2 Angular 커밋 규약 (Conventional Commits의 원형)

출처: <https://raw.githubusercontent.com/angular/angular/main/contributing-docs/commit-message-guidelines.md>

- 형식: `<header>` / 빈 줄 / `<body>` / 빈 줄 / `<footer>`. header 필수.
- header: `<type>(<scope>): <short summary>`
- **type 8종**: `build`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `test` — ★ **`chore`가 없다.**
- scope = 영향받은 패키지(core·router·forms…). 문서 전용 변경은 scope 생략.
- summary: **명령형**("change" not "changed"), **소문자 시작**, **마침표 없음**.
- body: **`docs` type 외에는 필수**, 명령형·현재형, **최소 20자**, *왜*를 설명하고 이전/새 동작을 대비.
- footer: `BREAKING CHANGE: <요약>` + 빈 줄 + 설명·마이그레이션 지침 / `DEPRECATED: <대상>` + 빈 줄 + 대체 경로 / `Fixes #N`·`Closes #N`.
- revert: `revert: ` + 원래 header, 본문에 `This reverts commit <SHA>` + 사유.

**우리와의 차이**: 우리 type에 `chore`가 있고 `perf`·`ci`가 없다 — 그런데 **이슈 템플릿에는 「성능 개선」이 있어 축이 어긋난다**(이슈는 performance, 커밋은 chore).

### 1.3 commitlint config-conventional (사실상의 기계 강제 기본값)

출처: <https://raw.githubusercontent.com/conventional-changelog/commitlint/master/@commitlint/config-conventional/README.md>

- **type-enum 11종**: `build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test` (Angular 8종 + `chore`·`revert`·`style`)
- 에러 레벨 규칙: `type-enum`, `type-case`(소문자), `type-empty`, `subject-case`(sentence/start/pascal/upper-case 금지 = 소문자 계열 강제), `subject-empty`, `subject-full-stop`(마침표 금지), **`header-max-length` = 100**, `body-max-line-length` = 100, `footer-max-line-length` = 100
- 경고 레벨: `body-leading-blank`, `footer-leading-blank`

**우리와의 차이**: 우리 7종은 이 11종의 부분집합이라 **표준 도구로 그대로 강제 가능**(`type-enum` 오버라이드 1줄). PR-7이 기다리는 "도구 확정"은 사실상 이미 존재한다.

### 1.4 50/72 규칙의 원출처 — Tim Pope (2008)

출처: <https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>

- *"Capitalized, short (50 chars or less) summary"* → **50자 요약** + **빈 줄** + 72열 랩핑 본문 + 명령형.
- 근거: ⑴ `git log` 기본 pager에서 긴 줄이 화면 밖으로 흐른다 ⑵ `git format-patch`로 메일 전환 시 넷티켓 ⑶ 요약은 `--oneline`·`rebase`·`shortlog`·gitk·GitHub·reflog에서 **잘린 형태로 반복 노출**된다.
- 명령형 근거: **git이 스스로 만드는 메시지(merge/revert)가 명령형**이라 일관된다.

### 1.5 cbeams — "How to Write a Git Commit Message" (7 규칙)

출처: <https://cbea.ms/git-commit/>

1. 제목과 본문을 **빈 줄로 분리** — 첫 빈 줄까지가 git이 쓰는 title이다
2. **제목 50자 제한** — GitHub은 50자 초과 시 경고, **72자에서 잘라낸다**
3. 제목 **첫 글자 대문자**
4. 제목 **마침표 금지**
5. 제목 **명령형** — 테스트: *"If applied, this commit will ___"* 이 자연스럽게 읽혀야
6. 본문 **72자 랩핑** — git이 들여쓰기할 여백을 남겨 80자 안에 들어온다
7. 본문은 **what·why**를 설명, how는 코드가 설명한다

**우리와의 차이**: ⚠️ **규칙 3(대문자)과 commitlint `subject-case`(대문자 금지)는 정면 충돌**한다. Conventional Commits 계열을 택하면 cbeams 3번은 버려야 한다 — 두 출처를 함께 인용하면 규약이 자기모순이 된다.

### 1.6 Linus/Subsurface 스타일 (커널 계열)

출처: <https://raw.githubusercontent.com/torvalds/subsurface-for-dirk/master/README.md>

- 한 줄 header(**명령형**) + 빈 줄 + 본문, 본문 **74열 내외** 워드랩, 끝에 `Signed-off-by:`.
- 핵심 원칙: *"explain your solution and **why** you're doing what you're doing, as opposed to describing **what** you're doing"* — 리뷰어는 패치를 읽을 수 있지만 이유는 모른다.
- ★ 커널 계열은 **type 접두를 쓰지 않는다**(대신 서브시스템 접두 `net: ...`). Conventional Commits는 이 전통과 다른 계보다.

### 1.7 gitmoji (우리는 금지 — 반대 근거)

출처: <https://raw.githubusercontent.com/carloscuesta/gitmoji/master/README.md>

- 형식: `<intention> [scope?][:?] <message>` — intention = 이모지.
- 주장 근거: *"이모지만 봐도 커밋 의도를 식별"*.
- ★ **README 전체에 단점·한계·비판이 한 줄도 없다** — 채택 판단에 필요한 반대 근거를 스스로 제공하지 않는 홍보 문서다.
- 반대 근거로 쓸 수 있는 것(원문 대조에서 도출): ⑴ 이모지는 **grep·정렬·`--oneline` 폭**에서 type 문자열보다 열등하고 ⑵ Conventional Commits 규칙 1(type 접두 MUST)과 형식이 **양립하지 않는다**(gitmoji는 이모지가 첫 토큰) ⑶ commitlint `type-enum` 등 표준 파서가 그대로는 통과시키지 않는다.

**우리와의 차이**: 없음(이미 금지). 단 금지 근거를 취향이 아니라 **"기계 파싱 표준과 양립 불가"**로 적을 수 있다.

---

## 축 2 — 브랜치 모델

### 2.1 git-flow (nvie, 2010) + 저자 본인의 2020 경고

출처: <https://nvie.com/posts/a-successful-git-branching-model/>

| 브랜치 | 분기 | 병합 | 명명 |
|---|---|---|---|
| master | — | release·hotfix | 커밋 하나 = 프로덕션 릴리스 |
| develop | — | feature·release·hotfix | 다음 릴리스 통합 |
| feature | develop | develop | master/develop/`release-*`/`hotfix-*` 외 아무거나 |
| release | develop | develop **및** master | `release-*` |
| hotfix | master | develop **및** master(릴리스 진행 중이면 release로) | `hotfix-*` |

★ 저자 2020 주의문: 이 모델은 2010년 것이며, 지속적 배포 웹 앱에는 *"a much simpler workflow (like GitHub flow)"* 를 권한다. git-flow가 여전히 맞는 경우는 **명시적으로 버전이 매겨지는 소프트웨어**·**여러 버전을 동시에 지원**하는 경우. *"panaceas don't exist. Consider your own context."*

### 2.2 GitHub Flow (공식)

출처: <https://docs.github.com/en/get-started/using-github/github-flow>

1. 브랜치 생성 → 2. 변경 → 3. PR 생성 → 4. 리뷰 반영 → 5. 머지 → 6. **브랜치 삭제**
- 브랜치명: *"short, descriptive"* — 예 `increase-test-timeout`, `add-code-of-conduct`. ★ **접두 규칙(`feature/`)을 공식 문서는 요구하지 않는다.**
- 커밋: 하나의 논리적 변경만. 무관한 변경은 다른 브랜치로 — 되돌리기·추적이 쉬워진다.
- PR 본문: *"a summary of the changes and what problem they solve"*. 이슈는 **키워드로 링크**해 머지 시 자동 종료.
- 머지 후 브랜치 삭제 — 완료 신호 + 재사용 사고 방지. PR·커밋 히스토리는 남는다.

### 2.3 Trunk-Based Development (공식 사이트)

출처: <https://trunkbaseddevelopment.com/> · <https://trunkbaseddevelopment.com/short-lived-feature-branches/>

- 정의: *"developers collaborate on code in a single branch called 'trunk' and **resist any pressure to create other long-lived development branches**"*
- 두 변형: ⑴ **trunk 직접 커밋**(아주 작은 팀) ⑵ **단기 feature 브랜치**(큰 팀 — 리뷰·CI 목적)
- 구체 수치:
  - 브랜치 수명 *"a couple of days"* — **2일 초과 시 장수 브랜치가 될 위험**
  - 브랜치당 개발자 **1명**(페어면 2명)
  - **15명 이하 팀은 trunk 직접 커밋 가능**, 16명+ 에서 단기 브랜치가 더 생산적
- 릴리스 브랜치는 **just-in-time으로 잘라 하드닝 후 삭제**하거나, 처리량이 높으면 trunk에서 직접 릴리스 + fix-forward.
- 제약: **독립적으로 배포 가능한 커밋만** trunk에 착지 — 미완성 작업의 중간 머지 금지.

### 2.4 "git-flow는 해롭다" 계열 [실무 의견]

출처: <https://www.endoflineblog.com/gitflow-considered-harmful>

1. **읽을 수 없는 히스토리** — `--no-ff` 강제로 *"a giant ball of spaghetti"*
2. **master/develop 이중화가 잉여** — master 커밋이 곧 태그된 릴리스라면 develop이 이미 모든 정보를 갖는다. 남는 건 머지 커밋뿐
3. **복잡도 자체** — 잘못된 브랜치 머지·태그 누락·분기점 혼동이 유능한 개발자에게도 반복 발생 = 시스템 결함의 징후

대안("anti-gitflow"): 영구 브랜치 **1개**, 임시 feature 브랜치는 머지 후 삭제, **선형 히스토리 강제**, 릴리스/핫픽스는 태그 기반, master HEAD = 다음 릴리스 / 최신 태그 = 프로덕션.

### 2.5 Fowler — Patterns for Managing Source Code Branches

출처: <https://martinfowler.com/articles/branching-patterns.html>

- **Mainline** = 제품의 현재 상태를 나타내는 공유 코드라인.
- **Healthy Branch** = 매 커밋마다 자동 검사(빌드+테스트)를 돌려 결함이 없음을 보장 — self-testing code가 전제.
- **Integration Frequency**가 핵심 변수: 통합이 잦을수록 머지가 작고 위험이 낮다. *"Smaller integrations mean less work… but more importantly than less work, it's also less risk."*
- **feature 브랜치 수명 권고: "less than a day"**. CI의 표준은 *"everyone commits to the mainline every day"*.
- **Release Branch**: mainline에서 분기, **결함 수정만** 받고 새 기능은 안 받는다.
- 브랜치 전략은 **맥락 함수** — 간헐적 기여자가 있는 OSS와 전임 상업 팀은 근본적으로 다르다.

### 2.6 브랜치 이름의 하드 제약(git 자체)

출처: <https://git-scm.com/docs/git-check-ref-format>

금지: 컴포넌트가 `.`로 시작하거나 `.lock`으로 끝남 / `..` / ASCII 제어문자·공백·`~`·`^`·`:` / `?`·`*`·`[` / 선행·후행 `/`, 연속 `//` / 후행 `.` / `@{` / 단독 `@` / `\`.
★ **`foo`와 `foo/bar`는 공존 불가** — 브랜치 `feature`를 만들면 `feature/x`를 못 만든다(접두 스킴 채택 시 실질 제약).

### 2.7 1인·소규모에 대한 종합

원문들이 실제로 말하는 것만 모으면:
- nvie 본인: 지속 배포면 GitHub flow / **명시적 버전 관리 + 다중 버전 지원**이면 git-flow → 우리 `common` 라이브러리는 후자에 가깝고 서비스 리포는 전자에 가깝다
- trunkbased: **15명 이하 = trunk 직접 커밋 가능**, 단기 브랜치는 **리뷰·CI를 위해** 쓰는 것
- Fowler: 브랜치 수명 **1일 미만**
- endofline: 영구 브랜치 1개 + 선형 히스토리

**우리와의 차이**: PR-1(main 직접 금지 + 브랜치 우선) + PR-8(이슈 기반 브랜치)은 **trunkbased의 "단기 feature 브랜치" 변형과 정확히 일치**한다 — 다만 **수명 상한(2일/1일)과 `develop` 부재**를 규약에 명시적으로 적어야 git-flow로 미끄러지지 않는다.

---

## 축 3 — 이슈 템플릿

### 3.1 GitHub 공식 — md 템플릿 vs yml form

출처: <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository> · <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms> · <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema>

| | Markdown 템플릿 | Issue Form (yml) |
|---|---|---|
| 경로 | `.github/ISSUE_TEMPLATE/*.md` | `.github/ISSUE_TEMPLATE/*.yml` |
| 본질 | 본문 프리필 텍스트 — **사용자가 지울 수 있다** | 웹 폼 필드 — **`required: true` 강제 가능** |
| 필드 타입 | 없음 | `markdown`(제출 안 됨)·`input`·`textarea`·`dropdown`·`checkboxes`·`upload` |
| 필수 강제 | 불가 | 가능 — ⚠️ **`required`는 public 리포에서만 동작** |
| frontmatter | `title`·`labels`·`assignees`·`type` | 상동 + `projects` |

form 상위 키: `name`(필수·유일)·`description`(필수)·`body`(필수)·`assignees`·`labels`·`title`·`type`·`projects`.
- `labels`/`assignees`는 배열 또는 콤마 구분 문자열. **리포에 이미 존재하지 않는 라벨은 자동 추가되지 않는다.**
- `projects`는 `PROJECT-OWNER/PROJECT-NUMBER` 형식 + 쓰기 권한 필요.
- `textarea`는 `render:`로 코드블록 렌더 지정 가능(로그·스택트레이스에 유용). `dropdown`은 `multiple`·`default`(인덱스). `checkboxes`는 옵션별 `required`.
- 템플릿 **이름은 3자 초과**여야 선택 화면에 표시된다.
- 첨부 한도: 이미지 10MB / 문서·아카이브·텍스트 25MB / 비디오 100MB.

`config.yml`:
- `blank_issues_enabled: false` → 빈 이슈 생성 차단(쓰기 권한자만 보임)
- `contact_links:` → 질문·지원을 외부(Discussions·Stack Overflow)로 우회

### 3.2 유명 OSS 실제 템플릿 — 무엇을 강제하나

**Kubernetes** (<https://raw.githubusercontent.com/kubernetes/kubernetes/master/.github/ISSUE_TEMPLATE/bug-report.yaml>): textarea 10칸, **필수 4칸** = 무슨 일이 일어났나 / 무엇을 기대했나 / **최소·정확한 재현 방법** / **Kubernetes 버전**. 선택 6칸은 전부 **환경 정보**(클라우드·OS·설치도구·런타임·플러그인).

**Rust** (<https://raw.githubusercontent.com/rust-lang/rust/master/.github/ISSUE_TEMPLATE/bug_report.md>): md 템플릿. frontmatter `labels: C-bug`. 칸 = 코드 예시 / 기대 동작 / 실제 동작 / **Meta**(`rustc --version --verbose`, stable·beta·nightly 교차 확인, `RUST_BACKTRACE=1` 백트레이스).

**VS Code** (<https://raw.githubusercontent.com/microsoft/vscode/main/.github/ISSUE_TEMPLATE/config.yml>): `blank_issues_enabled: false` + contact_links로 질문을 Stack Overflow, 확장 개발을 Discussions로 라우팅.

★ 세 사례의 공통 축: **⑴ 재현 절차 ⑵ 기대 vs 실제 ⑶ 환경/버전** — 그리고 **질문은 이슈가 아니다**(VS Code는 아예 차단).

**우리와의 차이**:
- 우리 4종 폼에 **재현 절차·환경/버전 칸이 없다**(버그 템플릿 내용은 미확인이나 기능 템플릿은 개요/상세/테스트/참고 4칸). 은행 도메인이라 **재현 데이터·계좌 상태**가 결정적인데 강제 칸이 없다.
- `config.yml`이 **없어 빈 이슈가 허용**된다 → 템플릿을 우회할 수 있고, 라벨 자동 부여도 우회된다.
- `title: "[Feature] "` 접두는 **라벨과 정보가 중복**된다(라벨 `feature`가 이미 있다). GitHub 사례들은 제목 접두 대신 라벨/이슈 타입을 쓴다.
- 우리 리포는 **private일 가능성이 높은데 `required: true`는 public 전용** — 강제가 실제로 걸리지 않을 수 있다. ★ **[구현 검증] 필요**.

---

## 축 4 — PR/MR 템플릿·작성법

### 4.1 GitHub 공식

출처: <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository>

- 경로: 루트 `pull_request_template.md` / `docs/pull_request_template.md` / `.github/pull_request_template.md`
- **복수 템플릿**: 위 세 위치 중 하나에 `PULL_REQUEST_TEMPLATE/` 디렉터리 → `?template=NAME.md` 쿼리 파라미터로 선택
- ★ **PR에는 issue form(yml) 같은 구조화 폼이 없다** — 필수 칸 강제 불가. 강제하려면 CI(라벨/본문 검사)로 올려야 한다.
- 템플릿은 **기본 브랜치에 머지되어야** 적용된다.

이슈 연결 (<https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue>):
- 키워드 9종: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`
- 문법: `KEYWORD #N` / 타 리포 `KEYWORD OWNER/REPO#N`. 여러 이슈는 **각각 전체 문법**을 콤마로. 콜론·대문자 허용(`Closes: #10`, `CLOSES #10`)
- ★ **PR 본문 키워드는 PR이 기본 브랜치를 대상으로 할 때만 해석된다**
- 커밋 메시지의 키워드도 머지 시 이슈를 닫지만 **PR이 linked로 표시되지는 않는다**
- 수동 링크는 PR당 최대 10개, 키워드 링크는 **동일 리포 이슈만**

머지 방식 (<https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges>):
- **merge commit**: 모든 커밋 보존 + 명시적 머지 커밋
- **squash and merge**: 전 커밋을 **하나로 합침** — 기본 메시지는 저장소 설정과 커밋 수에 따라 PR 제목/본문/커밋 정보 중에서 조합. 관리자가 "Configuring commit squashing" 설정으로 기본값 지정 가능
- **rebase and merge**: 머지 커밋 없이 각 커밋을 base에 재생 → 선형 히스토리

### 4.2 Kubernetes PR 템플릿 (구조 사례)

출처: <https://raw.githubusercontent.com/kubernetes/kubernetes/master/.github/PULL_REQUEST_TEMPLATE.md>

칸: ⑴ **PR 종류**(`/kind bug|cleanup|documentation|feature|...` 봇 명령) ⑵ 무엇을/왜 ⑶ **관련 이슈**(`Fixes #`) ⑷ 리뷰어를 위한 특기사항 ⑸ **사용자 대면 변경 = 릴리스 노트 블록(없으면 `NONE` 명시)** ⑹ 추가 문서(KEP 등 — **브랜치가 아닌 커밋 고정 링크** 사용).

★ 배울 점 2개: **⑸ 릴리스 노트를 PR에서 수확**(축 7의 자동 릴리스 노트와 접속), **⑹ 영구 링크 강제**.

### 4.3 좋은 PR 설명 — Google eng-practices

출처: <https://google.github.io/eng-practices/review/developer/cl-descriptions.html>

- 첫 줄: **무엇을 하는지의 짧은 요약**, **명령형 완전 문장**, 뒤에 빈 줄. 예 *"Delete the RPC"* (not *"Deleting the RPC"*). 첫 줄은 히스토리에 남으므로 **CL을 안 봐도 이해되어야** 한다.
- 본문: 문제·**왜 이 접근인가**·한계·배경(버그 번호·벤치마크·설계 문서). 외부 링크는 **미래에 접근 불가할 수 있으므로 맥락을 본문에 포함**.
- 나쁜 예: *"Fix bug"*, *"Fix build"*, *"Add patch"*, *"Moving code from A to B"*
- ★ **제출 직전 설명을 다시 읽어 리뷰 중 변한 내용을 반영**하라 — 리뷰 과정에서 설명이 낡는다.

### 4.4 PR 크기 — 실증과 권고

**Google** (<https://google.github.io/eng-practices/review/developer/small-cls.html>):
- 수치: **~100줄 = 대체로 적정, ~1000줄 = 대체로 과대**. 단 *"한 파일 200줄은 괜찮을 수 있지만 50개 파일에 흩어진 200줄은 대체로 과대"* → **파일 확산이 줄 수만큼 중요**
- 이유 8가지: 빠른 리뷰(5분 단위는 내주기 쉽지만 30분 블록은 아니다) / 더 철저한 검토 / 버그 감소 / 재작업 낭비 감소 / 머지 충돌 감소 / 설계 개선 / 블로킹 감소 / **롤백 용이**
- 자기완결 기준: **한 가지만** 다룬다(기능 전체가 아니라 기능의 한 조각), 관련 테스트 포함, 제출 후에도 시스템이 정상 동작
- **예외 2가지만**: 파일 삭제(1줄로 계산), 신뢰할 수 있는 도구의 자동 리팩토링(리뷰어가 검증만)

**Cisco/SmartBear 실증 연구** (<https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/>) [실증]:
- **한 번에 200~400 LOC 이하** 리뷰
- **한 세션 60분 이하** — 이후 인지 성능 저하
- **검사 속도 500 LOC/시간 초과 시 결함 밀도가 유의하게 하락**
- 200~400 LOC를 60~90분에 보면 **결함 발견율 70~90%**
- 경량 리뷰는 정식 인스펙션 시간의 **20% 미만으로 같은 수의 버그**를 찾는다(정식 인스펙션은 200 LOC당 평균 9시간)

**우리와의 차이**: 우리 PR 템플릿 3칸에는 **⑴ 관련 이슈 링크 칸이 없고**(본문 예시에 `#42`가 묻혀 있을 뿐) ⑵ **테스트/검증 칸이 없으며** ⑶ **크기 상한 규칙이 없다**. PR-3의 안전선 ①~⑥은 규약 문서에만 있고 **PR 본문 체크리스트로 내려와 있지 않다** — 즉 리뷰 시점에 보이지 않는다. 또 "변경 유형" 칸의 값(`NEW FEATURE`/`FIX`/…)이 **커밋 type·이슈 라벨과 세 번째로 다른 어휘**다.

### 4.5 GitLab (MR 어휘를 쓴다면)

출처: <https://docs.gitlab.com/user/project/description_templates/>

- 경로: `.gitlab/issue_templates/*.md`, `.gitlab/merge_request_templates/*.md` — **기본 브랜치에 있어야** 한다
- 기본 템플릿 우선순위: 프로젝트 설정 > 상위 그룹 `Default.md` > 프로젝트 `Default.md`
- **GitHub의 issue form에 해당하는 구조화 폼이 없다**(마크다운만). 대신 **그룹/인스턴스 상속**, MR 변수 치환(`%{source_branch}`, `%{all_commits}`), 템플릿 내 **quick action** 임베드 가능

**우리와의 차이**: 우리는 GitHub 리포에 파일이 있는데 규약 문서는 "MR"이라고 부른다 — **어휘를 PR로 통일하거나 플랫폼을 명시**해야 한다.

---

## 축 5 — 라벨 체계

### 5.1 GitHub 기본 라벨 9종 (공식)

출처: <https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels>

`bug` / `documentation` / `duplicate` / `enhancement` / `good first issue` / `help wanted` / `invalid` / `question` / `wontfix`
- 신규 리포마다 자동 포함, 편집·삭제 가능. **조직 소유자는 조직 기본 라벨을 커스터마이즈**할 수 있다(→ 5개 리포 일괄 적용 수단).
- `good first issue`가 붙은 이슈는 리포의 contribute 페이지에 자동 노출.
- ★ **공식 문서는 기본 라벨의 색상 코드를 규정하지 않는다** — 색 관습은 표준이 아니라 관례다.

### 5.2 Kubernetes 다축 라벨 체계

출처: <https://www.kubernetes.dev/docs/guide/issue-triage/>

접두 축: `kind/` · `priority/` · `sig/` · `area/` · `triage/` · `lifecycle/`

priority 5단계(정의 포함):

| 라벨 | 의미 |
|---|---|
| `priority/critical-urgent` | 다음 릴리스 전까지 팀 리더가 **적극적으로 진행 중임을 보장할 책임** |
| `priority/important-soon` | 지금 또는 곧 인력을 배정, 이상적으로 다음 릴리스 |
| `priority/important-longterm` | 중요하나 여러 릴리스에 걸침, **릴리스를 막지 않음** |
| `priority/backlog` | 있으면 좋으나 인력 없음, 커뮤니티 기여 환영 |
| `priority/awaiting-more-evidence` | *"유용할 수 있으나 실제로 할 만한 근거가 아직 부족"* |

트리아지 워크플로: 신규 이슈에 `needs-triage` 자동 부여 → `/triage accepted`로 `triage/accepted` 전환 → 정보 부족은 `triage/needs-information` → **PR 없이 30일이면 소유자 접촉, 90일 무활동이면 `lifecycle/stale` 자동 부여**.

★ 배울 점: **priority는 "얼마나 급한가"가 아니라 "누가 무엇을 보장하는가"로 정의**되어 있다. 그래서 라벨이 실제로 작동한다.

### 5.3 접두 3축 스킴 [실무 의견]

출처: <https://medium.com/@dave_lunny/sane-github-labels-c5d2e6004b63>

- 3군: **Status** / **Type** / **Priority**. 라벨 이름에 `Status: ` 접두를 붙여 시각적으로 군을 구분 → 한눈에 상태·종류 파악.
- 규칙: **Status 라벨은 이슈당 하나만**.
- ⚠️ 저자 본인이 priority 라벨에 회의적 — 도입하면 *"모든 이슈가 critical이 된다"*.
- ★ 이 글은 **색 코딩 근거를 설명하지 않는다** — "색 체계 관습"에 정평 있는 원출처는 이번 조사에서 확인되지 않았다(아래 「미확인 공백」).

### 5.4 GitHub Issue Types (라벨의 대안 — 조직 기능)

출처: <https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization>

- 조직 전체에서 이슈를 분류하는 **1급 필드**. 기본 3종 **task / bug / feature**(편집·비활성·삭제 가능), **조직당 최대 25종**.
- 이슈 목록·이슈 본문에 표시, 필터·검색·프로젝트 뷰 기준으로 사용 가능.
- ★ 라벨과 달리 **조직 단위 단일 정의** → 리포 5개에 같은 type 축을 유지하는 문제를 라벨 동기화 없이 해결한다.

### 5.5 Conventional Comments (리뷰 코멘트 라벨 — 이슈 라벨과 다른 층)

출처: <https://conventionalcomments.org/>

형식: `<label> [decorations]: <subject>` + 빈 줄 + `[discussion]`

라벨 9종: `praise`(리뷰당 최소 1개 권장) · `nitpick`(사소·취향 — **본질상 non-blocking**) · `suggestion`(무엇을 왜 개선하는지 명확히) · `issue`(구체적 문제 — 가능하면 suggestion과 짝) · `todo`(작고 필요한 변경 — issue보다 가벼움) · `question`(관련성이 확실치 않은 우려) · `thought`(리뷰 중 떠오른 아이디어 — non-blocking) · `chore`(문서 링크를 동반한 단순 필수 작업) · `note`(항상 non-blocking, 짚고 넘어갈 것)

데코레이션: `(non-blocking)` / `(blocking)` / `(if-minor)`(사소하면 작성자가 바로 처리).

**우리와의 차이**:
- 우리 라벨은 **type 축 하나뿐**(feature·bug·refactor·performance)이고 **status·priority 축이 없다** — 1인 프로젝트에서 우선순위는 사실 마일스톤이 대신할 수 있으나, **status(진행/막힘/보류)는 대체제가 없다**.
- 라벨이 **파일로 관리되지 않는다**(리포 5개 = 수동 5회 동기화). 조직 기본 라벨 또는 라벨 동기화 액션이 필요.
- **PR-4(리뷰 렌즈: 구조·불변식 우선, 표기 지적 배제)와 Conventional Comments가 정확히 접속**한다 — `nitpick`/`note`를 non-blocking으로 강제하면 PR-4가 규칙에서 **형식**으로 내려간다.

---

## 축 6 — 마일스톤·프로젝트

### 6.1 마일스톤 (공식)

출처: <https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones>

- 용도: *"track progress on **groups of** issues or pull requests **in a repository**"* — ★ **리포 범위**다.
- 필드: 제목 · **마감일** · 설명(프로젝트 개요·관련 팀·예상 일정)
- 제공: 완료 퍼센트, 열림/닫힘 개수, 이슈·PR 목록, **드래그 우선순위 정렬**(열린 이슈 500개 초과 시 불가)

### 6.2 Projects (공식)

출처: <https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects>

- *"an adaptable **table, board, and roadmap**"* — 이슈·PR과 통합
- **필드 최대 50개**(내장 + 커스텀): date(출시일)·number(복잡도)·single select(우선순위 Low/Medium/High)·text·**iteration**(주 단위 계획, 휴지 기간 지원)
- 뷰 3종: 테이블(고밀도) / 칸반 보드 / 타임라인 로드맵. 각각 필터·정렬·그룹핑
- ★ **공식 문서는 마일스톤 vs Projects의 용도 구분을 명시하지 않는다.** 다만 커스텀 필드가 *"내장 메타데이터(assignee, milestone, labels 등)를 넘어서"* 확장한다고 적어, **마일스톤을 Projects의 한 필드로 취급**함을 드러낸다.

### 6.3 도출되는 구분 (원문 대조에서)

| | 마일스톤 | Projects |
|---|---|---|
| 범위 | **리포 1개** | **조직/여러 리포** |
| 축 | **하나**(무엇이 이 릴리스에 들어가나) + 마감일 | 다축(상태·우선순위·이터레이션·복잡도) |
| 진척 | 완료율 자동 | 뷰·필터로 구성 |
| 적합 | **릴리스 단위** | **스프린트/보드 단위** |

★ 멀티리포(우리 5개)에서 **마일스톤은 리포마다 따로 만들고 따로 닫아야 한다** — 리포를 가로지르는 단위는 Projects만 표현할 수 있다. 이것이 PR-8("리포별 마일스톤으로 규격화")의 실제 비용이다.

**우리와의 차이**: PR-8이 **마일스톤을 조정 단위로 삼는데, 5개 리포에 걸친 하나의 작업**(예: common 변경 → 3개 서비스 반영)은 마일스톤 5개로 쪼개진다. 이 경우 **Projects 1개 + 리포별 마일스톤**의 이중 구조가 필요한지 판정이 필요하다. [실무 의견 필요 — 아래 미확인 공백]

---

## 축 7 — 버전·태그·릴리스

### 7.1 SemVer 2.0.0 (명세 원문)

출처: <https://semver.org/>

| # | 규칙 |
|---|---|
| 1 | **공개 API를 선언**해야 한다 — 정확하고 포괄적으로 |
| 2 | `X.Y.Z` 음이 아닌 정수, 선행 0 금지, 수치적 증가(1.9.0 → 1.10.0 → 1.11.0) |
| 3 | **릴리스된 버전의 내용은 변경 불가** — 바꾸려면 새 버전 |
| 4 | **0.y.z = 초기 개발** — *"Anything MAY change at any time"*, API 불안정 |
| 5 | **1.0.0이 안정 공개 API를 정의**한다 |
| 6 | PATCH = 하위 호환 **버그 수정**만 |
| 7 | MINOR = 하위 호환 **기능 추가** 또는 **deprecated 표시**. PATCH를 0으로 |
| 8 | MAJOR = 공개 API의 **하위 비호환 변경**. MINOR·PATCH를 0으로 |
| 9 | pre-release = 하이픈 + 점 구분 식별자(`1.0.0-alpha.1`). 정식 버전보다 **낮은 우선순위** |
| 10 | build metadata = 플러스(`1.0.0+20130313144700`) — **우선순위 판정에서 무시** |
| 11 | 우선순위: major→minor→patch→pre-release 순 비교(build 제외). 숫자는 수치 비교, 영숫자는 사전식, **숫자 < 비숫자**, 식별자가 많은 쪽이 높다 |

### 7.2 git 태그 (공식 Pro Git)

출처: <https://git-scm.com/book/en/v2/Git-Basics-Tagging>

- **lightweight**: 커밋 체크섬만 담은 파일 = 단순 포인터. 메타데이터 없음
- **annotated**(`-a`): git 객체로 저장 — 태거 이름·이메일·날짜·메시지, **GPG 서명·검증 가능**
- ★ 공식 권고: *"It's generally recommended that you create **annotated** tags"* — 임시 태그가 필요할 때만 lightweight
- 태그는 `git push`로 **자동 전송되지 않는다** — `git push origin <tag>` / `--tags` / `--follow-tags`(annotated만)
- **`v` 접두**: 문서 예시가 일관되게 `v1.4` 등을 쓰지만 **공식적으로 강제되지는 않는다**(관례)

### 7.3 GitHub Releases

출처: <https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases> · <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes>

- 릴리스 = **git 태그 위에** 릴리스 노트와 바이너리를 얹은 배포 단위. **태그 생성일과 릴리스 생성일은 다를 수 있다**
- ZIP/tarball 자동 생성. 릴리스당 **에셋 1,000개**, 파일당 **2 GiB**
- **자동 릴리스 노트**: `.github/release.yml`
  - `changelog.exclude`(labels/authors) — 전체에서 제외
  - `changelog.categories[*]`: `title`(필수) · `labels`(필수) · 카테고리별 `exclude.labels`/`exclude.authors`
  - **`labels: ['*']`** = 앞선 카테고리에 안 걸린 나머지 전부(catch-all)
- ★ **PR 라벨이 릴리스 노트의 목차가 된다** — 라벨 체계(축 5)와 릴리스(축 7)가 여기서 물린다

### 7.4 Keep a Changelog 1.1.0

출처: <https://keepachangelog.com/en/1.1.0/>

원칙 7: 변경 로그는 **기계가 아니라 사람을 위한 것** / 모든 버전에 항목이 있어야 / 같은 유형끼리 묶어야 / 버전·섹션은 **링크 가능**해야 / 최신 버전이 위 / 각 버전의 **릴리스 날짜 표시** / SemVer 준수를 명시.

카테고리 6종: **Added** · **Changed** · **Deprecated** · **Removed** · **Fixed** · **Security**

형식: 맨 위 **Unreleased** 섹션 유지 / **ISO 8601 (YYYY-MM-DD)** — 지역 형식 금지 / 역시간순.

나쁜 관행 4: **커밋 로그 덤프**(*"they're full of noise"*) / **deprecation을 표시하지 않음** / **모호한 날짜 형식** / **일부만 기록**해 신뢰를 깨뜨림.

★ 주의: Keep a Changelog 카테고리 6종과 Conventional Commits type은 **일대일 대응이 아니다**(`refactor`·`test`·`chore`는 갈 곳이 없다) — 자동 생성기가 이들을 changelog에서 빼는 이유다.

### 7.5 버전 자동화 — semantic-release

출처: <https://raw.githubusercontent.com/semantic-release/semantic-release/master/README.md>

- 기본 규칙(Angular 규약): `fix(...)` → **PATCH** / `feat(...)` → **MINOR** / `BREAKING CHANGE:` footer → **MAJOR**
- 9단계: verify conditions → **get last release(git 태그에서)** → analyze commits → verify release → generate notes → **create git tag** → prepare → publish → notify
- 철학: *"releases are guaranteed to be unromantic and unsentimental"* — 버전 결정에서 사람의 감정을 제거하고 SemVer를 엄격히 따른다

### 7.6 버전 자동화 — release-please (릴리스 PR 모델)

출처: <https://raw.githubusercontent.com/googleapis/release-please/main/README.md> · <https://raw.githubusercontent.com/googleapis/release-please/main/docs/java.md>

- **연속 릴리스가 아니라 "릴리스 PR"** 을 유지한다: 기본 브랜치에 작업이 머지될 때마다 릴리스 PR이 갱신되고, **그 PR을 머지하는 순간** changelog 갱신·태그·GitHub 릴리스가 실행된다. 라벨로 생명주기 표시(`autorelease: pending` → `tagged` → `published`)
- 매핑: `fix:` → patch / `feat:` → minor / `feat!:` 등 `!` → major. 한 커밋에 여러 변경은 **footer로 추가 기재**
- ★ **JVM 지원**:
  - `maven` 전략 — 재귀적으로 모든 `pom.xml`의 `/project/version` 갱신(없으면 `/project/parent/version`), **릴리스 후 SNAPSHOT 버전을 별도 PR로 생성**(`autorelease: snapshot` 라벨, 태그·릴리스 없음)
  - `java` 전략 — **파일을 스스로 갱신하지 않는다**. `extra-files`로 버전 위치를 직접 지정해야 한다
  - ⚠️ **Gradle 전용 지원은 문서에 없다** → Gradle에서 쓰려면 `java` 전략 + `extra-files`(`gradle.properties` 등) 수동 구성
- **manifest 모드**: 한 리포에서 **여러 아티팩트를 각각의 버전·changelog로** 릴리스

### 7.7 Gradle/JVM 쪽 관습

**axion-release** (<https://axion-release-plugin.readthedocs.io/en/latest/>) — 태그가 버전의 단일 출처:
- git 태그에서 버전 도출(`project-0.1.0` → `0.1.0`), 기본 태그 접두는 **프로젝트명 기반**
- 커밋이 있거나 워킹트리가 더러우면 자동으로 **`-SNAPSHOT` 부착**(`0.1.1-SNAPSHOT`)
- `release` 태스크 = 태그 생성 + 버전 증가 / `markNextVersion -Prelease.version=1.0.0` = 다음 버전 수동 점프
- ★ **Conventional Commits를 읽지 않는다** — 태그 기반이지 커밋 기반이 아니다. 즉 "커밋 → 버전" 자동화를 원하면 release-please/semantic-release 계열, "태그 → 버전" 만 원하면 axion.

**GitHub Packages + Gradle** (<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-gradle-registry>):
- 리포지토리 URL: `https://maven.pkg.github.com/OWNER/REPOSITORY` — ★ **owner는 반드시 소문자**(대문자 미지원)
- 인증: PAT(classic) 또는 Actions의 `GITHUB_TOKEN`. `gpr.user`/`gpr.key` 프로퍼티 또는 `USERNAME`/`TOKEN` 환경변수
- 기본 매핑: 패키지 `com.example.test` → `OWNER/test` 리포
- **SNAPSHOT 지원됨**(Maven SNAPSHOT). 소비 측에서 스냅샷 활성화 필요
- 멀티 패키지는 subprojects에 maven-publish 적용

**우리와의 차이**:
- PR-7이 Conventional Commits를 쓰는데 **거기서 버전을 도출하는 장치가 없다** — 형식만 지키고 이득(자동 버전·changelog)은 아직 회수하지 않는 상태
- `common` 라이브러리가 GitHub Packages로 발행된다면 **owner 소문자·SNAPSHOT 정책·태그 접두(`v` vs `common-`)** 가 미결
- `chore`·`refactor`·`test`가 우리 type에 있는데 **changelog·릴리스 노트에서 어떻게 처리할지 규칙이 없다**

---

## 축 8 — 멀티리포에서 공통 라이브러리 소비

### 8.1 Gradle 버전 선언 형식

출처: <https://docs.gradle.org/current/userguide/dependency_versions.html>

- 형식 5종: **정확 버전**(`1.3`) / **Maven 범위**(`[1.0,)`, `[1.1, 2.0)`) / **접두 범위**(`1.+`, `1.3.+`) / **상태 기반**(`latest.integration`, `latest.release`) / **SNAPSHOT**(`1.0-SNAPSHOT`)
- rich version(강→약): **`strictly`**(가장 강함 — 불일치 버전 전부 배제, 다운그레이드 가능·다른 제약을 덮어씀, `!!` 축약) > **`require`**(하한 — 충돌 해결 시 상향 허용, **직접 의존의 기본값**) > **`prefer`**(가장 약함 — 다른 강한 지정이 없을 때만, 동적 버전 불가) + **`reject`**(특정 버전 배제)
- ★ 공식 경고: *"Using dynamic versions and changing modules can lead to **unreproducible builds**"* → **동적 버전을 쓸 거면 dependency locking을 함께** 써라

### 8.2 버전 카탈로그 (멀티리포 공유 수단)

출처: <https://docs.gradle.org/current/userguide/version_catalogs.html>

- `gradle/libs.versions.toml` — `[versions]` `[libraries]` `[bundles]` `[plugins]` 4절. 표준 위치는 **설정 없이 자동 인식**, 타입 안전 접근자 제공
- ★ **리포 간 공유 3방법**: ⑴ **`version-catalog` 플러그인**으로 카탈로그를 Maven 아티팩트로 발행 → 소비 측 `settings.gradle.kts`에서 `from("com.mycompany:catalog:1.0")` ⑵ `libs.versions.toml`을 공유 저장소에 두고 파일 참조 ⑶ settings 플러그인으로 프로그래밍적 선언 후 발행
- 카탈로그도 rich version(`strictly`/`prefer`/`require`) 지원, 임포트 시 특정 버전 오버라이드 가능

### 8.3 고정 vs 범위 — Renovate의 논거

출처: <https://docs.renovatebot.com/dependency-pinning/>

고정(pin) 찬성:
- **재현성** — *"you know exactly which version of each dependency is installed at any time"*
- **가시성** — 범위면 결함 버전이 자동 설치되지만, 고정이면 **PR로 와서 changelog를 읽고 테스트한 뒤 받는다**
- **롤백 용이** — 어느 의존성 변경이 문제인지 특정하고 커밋 단위로 되돌릴 수 있다

고정 반대:
- **노이즈 증가** — 업그레이드 PR이 잦아진다(automerge·스케줄·그룹핑으로 완화)
- **간접 의존성에는 무력** — 직접 의존만 고정되므로 통제감이 착시일 수 있다

권고 표:

| 대상 | 권고 |
|---|---|
| 앱(웹/Node) | **모든 의존성 고정** |
| 브라우저/양용 라이브러리 | dependencies는 **SemVer 범위**, devDependencies는 고정 |
| Node 전용 라이브러리 | 전부 고정 고려 |
| **모든 프로젝트** | **락 파일 사용** |

★ 우리 맥락으로 옮기면: **서비스 리포(=앱) → 고정**, **`common`이 다른 라이브러리를 쓸 때 → 범위**.

### 8.4 Dependabot

출처: <https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates> · <https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference>

- **`gradle`은 유효한 `package-ecosystem`**
- `schedule.interval`: `daily` · `weekly` · `monthly` · `quarterly` · `semiannually` · `yearly` · `cron`
- **`groups`**: 여러 업데이트를 **PR 하나로 묶는다**. `patterns`(와일드카드) · `update-types`(`patch`/`minor`/`major`) · `dependency-type`(development/production). 식별자는 문자로 시작·끝
- 새 릴리스에 대해 **기본 3일 쿨다운** 후 제안
- `versioning-strategy` 옵션이 존재하나 값 목록은 이번 fetch에서 회수되지 않음 — ★ **[구현 검증]**

**우리와의 차이**: `common` 소비 규약이 아직 없다. 리포 4개가 각자 버전을 적으면 **버전 드리프트가 규약 없이 발생**한다. 카탈로그 발행(8.2 ⑴)은 리포 5개 구조에 정확히 맞는 수단인데 현재 계획에 없다.

---

## 미확인 공백 (WebSearch 예산 소진으로 확인 못 한 것)

이 목록을 남기지 않으면 "조사했는데 없더라"와 "못 찾았다"가 구분되지 않는다.

1. **라벨 색 체계의 정평 있는 근거** — 공식 문서는 색을 규정하지 않고, dave_lunny 글도 색 근거를 설명하지 않는다. "색 관습"에 1차 출처가 있는지 미확인.
2. **PR 설명 품질 ↔ 리뷰 품질의 실증 연구** — Google 케이스 스터디 PDF(sback.it/publications/icse2018seip.pdf)는 fetch했으나 **PDF 파싱 실패**로 수치를 못 얻었다(중앙값 CL 크기·리뷰 지연·리뷰어 수). Rigby & Bird 계열도 미확인.
3. **1인 프로젝트의 마일스톤 vs Projects 실무 의견** — 1차 출처 부재. 축 6의 구분표는 **공식 문서 대조로 도출한 것**이지 인용이 아니다.
4. **Dependabot `versioning-strategy` 값 목록**(`auto`/`increase`/`widen`/`lockfile-only` 등으로 알려져 있으나 원문 미확인).
5. **Gradle 생태계의 Conventional Commits 기반 버전 자동화 관습** — release-please는 Gradle 전용 전략이 없고, axion은 커밋을 읽지 않는다. 둘을 잇는 정평 있는 관습이 존재하는지 미확인.
6. **"git-flow는 죽었다" 계열 중 endofline 외의 논쟁**(예: GitLab flow, ThoughtWorks Radar의 판정) 미수집.

---

## 부록 — 축 간 충돌 지점 (규약 작성 시 반드시 판정해야)

| 충돌 | A | B | 판정 필요 |
|---|---|---|---|
| 제목 대소문자 | cbeams 규칙 3(**대문자 시작**) | commitlint `subject-case`(**대문자 계열 금지**) | 둘 중 하나만 인용 가능 |
| 제목 길이 | Tim Pope/cbeams **50자** | commitlint `header-max-length` **100자** · Angular 100 | type(scope) 접두가 자리를 먹으므로 50은 사실상 불가 |
| type 목록 | Angular 8종(**chore 없음**) | commitlint 11종(**chore 있음**) | 우리 7종의 근거를 어디에 걸 것인가 |
| 유형 어휘 | 커밋 type(feat/fix/…) | 이슈 라벨(feature/bug/…) | + PR 템플릿의 `NEW FEATURE`/`FIX` — **어휘가 3벌**이다 |
| 브랜치 수명 | git-flow(기능 완성까지) | Fowler **1일 미만** · trunkbased **2일** | 이슈 단위 브랜치의 상한을 적을 것인가 |
| 필수 칸 강제 | issue form `required: true` | **public 리포에서만 동작** | 우리 리포 공개 여부에 종속 |
| 릴리스 노트 원천 | 커밋(semantic-release) | **PR 라벨**(GitHub `release.yml`) | 라벨 체계 설계가 여기에 종속된다 |
