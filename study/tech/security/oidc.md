# OIDC와 claim·jti — "이 요청이 진짜 우리 파이프라인에서 왔나"를 증명하는 법

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 배포 신원 검증 정본: [`architecture/adr/ADR-027-deploy-orchestration.md`](../../../architecture/adr/ADR-027-deploy-orchestration.md) DO-11). 마지막 절의 우리 적용은 그 정본을 **인용**할 뿐 여기서 재판정하지 않는다.

이 문서는 OpenID Connect(OIDC)와 그 토큰 안의 claim, 그리고 jti를 개념부터 설명한다. 순서는 하나의 질문을 따라간다 — 배포 명령을 받는 쪽이 *"이 요청이 정말 우리 GitHub Actions 파이프라인에서 왔나"* 를 어떻게 기계적으로 증명하느냐다. HMAC 서명은 이 질문에 절반만 답하고, OIDC는 나머지 절반을 답하며, 그 답이 왜 하나의 값이 아니라 **여러 claim의 행렬**로만 성립하는지가 이 글의 골자다. 인용한 스펙 문장은 OpenID Connect Core 1.0·RFC 7519(JWT)·RFC 6749(OAuth 2.0)·GitHub 공식 문서 기준이다.

## 1. 문제 — 서명은 "키를 아는 자"까지만 증명한다

배포 API가 외부에서 요청을 받을 때 먼저 필요한 것은 진위 확인이다. 흔한 답이 HMAC 서명이다 — 요청 본문을 공유 비밀 키로 해시해 붙이고, 받는 쪽이 같은 키로 다시 계산해 맞춰 본다. 이것이 증명하는 것은 정확히 하나다: **이 요청을 만든 자가 그 비밀 키를 알고 있다.** 키가 새지 않는 한 위조는 불가능하다.

문제는 "키를 아는 자"가 우리가 알고 싶은 것보다 넓다는 데 있다. 같은 키를 여러 워크플로가 공유하면 어느 워크플로가 보냈는지 서명은 구분하지 못하고, 키가 한 번 유출되면 그 뒤의 모든 요청이 형식상 진짜가 된다. 우리가 실제로 던지고 싶은 질문은 *"키를 아는가"* 가 아니라 *"우리 저장소의, 우리 배포 워크플로가, 허용된 브랜치에서 실행되고 있는가"* 다. HMAC은 여기에 답할 수 없다 — 답하려면 **요청자가 자기 신원을 증명 가능한 형태로 실어 보내야** 하고, 그 신원을 발급하는 제3자가 있어야 한다. 그 제3자가 OIDC 발급자다.

이 프로젝트는 둘을 버리지 않고 **AND로 묶는다** — HMAC은 "위조되지 않았다"를, OIDC는 "누가 보냈다"를 각각 증명하고, 한쪽만으로는 배포를 열지 않는다(DO-11 · [`operations/cicd.md`](../../../operations/cicd.md) CD-4 ⑵).

## 2. OIDC — OAuth 2.0(인가) 위에 얹은 인증 계층

OIDC를 이해하려면 그 아래에 깔린 OAuth 2.0부터 갈라 봐야 한다. 둘은 자주 섞여 불리지만 답하는 질문이 다르다.

**OAuth 2.0은 인가(authorization)의 프레임워크다.** RFC 6749는 자신을 "제3자 애플리케이션이 HTTP 서비스에 제한적으로 접근할 수 있게 하는 프레임워크"로 규정한다([RFC 6749 Abstract](https://www.rfc-editor.org/rfc/rfc6749)). 핵심 산출물은 access token이고, 그것이 답하는 것은 *"이 앱이 무엇을 할 수 있는가"* 다 — 예를 들어 "이 앱이 당신의 사진에 읽기 접근을 해도 되는가". OAuth는 **접근 권한을 위임**하는 도구이지, 상대가 *누구인지*를 표준화된 형태로 알려 주도록 설계되지 않았다.

**OIDC는 그 위에 인증(authentication) 계층을 얹는다.** OpenID Connect Core 1.0은 스스로를 "OAuth 2.0 프로토콜 위의 단순한 신원 계층(a simple identity layer on top of the OAuth 2.0 protocol)"이라 정의한다([OIDC Core 1.0 Abstract](https://openid.net/specs/openid-connect-core-1_0.html)). 여기서 추가되는 산출물이 **ID 토큰**이고, 그것이 답하는 것은 *"요청 주체가 누구인가"* 다. 인가가 "무엇을 해도 되나"라면 인증은 "너는 누구냐"이고, OIDC는 후자를 표준화한다.

우리 맥락에서 GitHub Actions는 인가를 위임받으려는 게 아니라 **자기 신원을 증명**하려는 것이다. 그래서 우리가 쓰는 것은 OAuth의 access token이 아니라 OIDC의 **ID 토큰**이고, 그 안의 claim이 "어느 저장소·어느 워크플로"인지를 말해 준다. 이 토큰은 발급자(issuer)가 서명해서 내주며, 발급자는 GitHub의 경우 `https://token.actions.githubusercontent.com`라는 고정된 URL이다(§7).

## 3. JWT — claim은 서명된 payload의 키-값이다

ID 토큰의 물리적 형식은 JWT(JSON Web Token)다. JWT는 점(`.`)으로 이어진 세 부분이다 — `header.payload.signature`. 각 부분은 base64url로 인코딩된 JSON(서명은 바이트열)이고, 겉보기엔 암호문 같지만 **header와 payload는 암호화가 아니라 인코딩일 뿐이라 누구나 디코딩해 읽을 수 있다.** JWT가 지키는 것은 기밀성이 아니라 무결성이다 — 서명이 "이 내용이 발급 후 바뀌지 않았고 그 발급자가 서명했다"를 보장한다.

```
[header]    eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9      = {"alg":"RS256","typ":"JWT"}
[payload]  .eyJpc3MiOiJodHRwczovL3Rva2VuLi4uIn0       = {"iss":"https://token...","sub":"repo:...", ...}
[sig]      .NHVaYe26MbtOYhSKkoKYdFVomg4i8ZJd...       = payload를 발급자 키로 서명한 값
```

여기서 **claim이란 payload 안의 키-값 한 쌍**이다. `iss`(발급자)·`sub`(주체)·`aud`(수신자)·`exp`(만료) 같은 이름들은 각각 하나의 claim이고, RFC 7519가 등록 claim(registered claim)으로 이름과 의미를 표준화해 둔 것들이다([RFC 7519 §4.1](https://www.rfc-editor.org/rfc/rfc7519#section-4.1)). GitHub은 여기에 `repository`·`ref` 같은 자기 도메인의 claim을 더 얹는다(§7).

검증의 출발점은 딱 하나다 — **먼저 서명을 확인한다.** 서명이 발급자의 공개 키로 검증되지 않으면 payload의 어떤 값도 신뢰할 수 없다. 서명이 통과한 다음에야 payload의 claim들을 하나씩 따져 볼 수 있고, 다음 절이 그 "하나씩"이 왜 여러 칸의 표가 되는지를 다룬다.

## 4. claim 검증이 "행렬"인 이유 — 한 칸이 하나의 침입 경로를 닫는다

서명이 유효한 토큰은 "발급자가 진짜로 발급했다"까지만 말한다. 그런데 그 발급자(`token.actions.githubusercontent.com`)는 **GitHub의 모든 저장소, 모든 워크플로에** 토큰을 발급한다. 즉 서명만 보면 *아무 저장소의 아무 워크플로*가 발급받은 토큰도 형식상 유효하다. 그래서 "우리 것인가"는 서명 하나가 아니라 payload의 여러 claim을 **각각** 대조해야 성립하고, 그 대조가 표(행렬)의 모양을 띤다. 각 claim이 무엇을 증명하고 빠지면 무엇이 뚫리는지가 그 표를 읽는 방식이다.

- **`iss`(발급자)** — 토큰을 서명한 주체. 발급자를 하나로 고정하지 않으면 다른 신뢰 도메인이 발급한 유효 토큰을 받게 된다. OIDC Core는 ID 토큰 검증 규칙에서 "`iss`가 반드시 예상 발급자와 일치해야 한다"고 못박는다([OIDC Core §3.1.3.7](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)).
- **`aud`(수신자)** — 이 토큰이 향하는 대상. **우리 배포 API 전용 audience**를 요구하고 플랫폼 기본값을 쓰지 않는 것이 핵심이다. 기본 audience를 그대로 받으면 다른 목적으로 발급된 토큰이 배포에 재사용될 수 있다. OIDC Core도 검증 시 "`aud`에 자신이 포함돼 있어야 하고, 신뢰하지 않는 audience가 있으면 거절해야 한다"고 규정한다(§3.1.3.7).
- **저장소 — `repository` + `repository_id`** — 어느 저장소가 발급받았나. 이름만 보면 안 되고 **수치 ID를 함께** 본다. 이름은 저장소 이전·삭제 후 재생성으로 재사용될 수 있지만 수치 ID는 재사용되지 않기 때문이다(§5·§7).
- **`ref`·`ref_type`** — 어느 브랜치·태그에서 실행됐나. 배포 가능한 ref를 허용목록으로 좁히지 않으면 임의의 브랜치나 태그에서 돌린 워크플로가 배포를 발행할 수 있다(기본은 기본 브랜치 하나).
- **`job_workflow_ref`(워크플로)** — 어느 워크플로 파일이 이 잡을 정의했나. 이걸 배포 워크플로 하나로 고정하지 않으면, **같은 저장소의 다른 워크플로**(예: 테스트용·문서용)가 토큰을 받아 배포를 열 수 있다.
- **`exp`·`nbf`·`iat`(시간)** — 유효 창과 발급 시각. 만료·아직 유효하지 않음·시각 skew를 검사하지 않으면 오래된 토큰이 계속 유효하다. 이 축은 다음에 다룰 재전송 방어(jti)와 짝을 이룬다.

빠진 칸 하나가 곧 하나의 우회로다 — 서명은 유효한데 `aud`를 안 보면 재사용이, `job_workflow_ref`를 안 보면 이웃 워크플로가, `repository_id`를 안 보면 이름 재사용이 뚫린다. 그래서 검증은 "이 중 몇 개"가 아니라 **전 칸 AND**이고, 한 칸이라도 어긋나면 적용하지 않고 거절을 기록한다(DO-11).

## 5. sub 문자열 대조가 위험한 이유 — 합성 문자열은 형식이 바뀌면 조용히 무너진다

앞의 claim들을 한 줄로 요약해 담은 것처럼 보이는 값이 `sub`(subject)다. GitHub Actions의 `sub`는 예컨대 이런 모양이다:

```
sub = "repo:octo-org/octo-repo:environment:prod"
sub = "repo:my-org/my-repo:ref:refs/heads/main"
```

한눈에 저장소·ref·environment가 다 들어 있어 보이니, "이 문자열이 우리 것과 같은가"로 검증하고 싶어진다. 이것이 함정이고, 우리 DO-11이 명시적으로 금지하는 지점이다. 이유는 두 가지다.

첫째, **`sub`는 여러 조각을 이어 붙인 합성 문자열이라 형식이 조용히 바뀐다.** 위 두 예를 보면 어떤 토큰은 `:environment:prod`로, 어떤 토큰은 `:ref:refs/heads/main`으로 끝난다 — 무엇을 트리거했느냐에 따라 꼬리가 달라진다. 정확한 전체 문자열 매칭은 형식이 바뀌면 우리 것도 조용히 거절해 버리고(가용성 사고), 그걸 피하려 **프리픽스 매칭**(`repo:my-org/my-repo:*`)으로 느슨하게 풀면 이번엔 그 저장소의 *아무 브랜치·아무 environment·pull request*까지 와일드카드에 걸려 통과한다(보안 사고). 어느 쪽으로 새든 **조용히** 새는 게 핵심이다 — 문자열 하나가 여러 축을 뭉쳐 담고 있어서, 한 축의 형식 변화가 다른 축의 판정을 무너뜨린다.

둘째, GitHub은 최근 `sub`의 형식 자체를 바꾸고 있다. 공식 문서에 따르면 **2026년 7월 15일 이후 생성된 저장소는 소유자·저장소의 수치 ID를 포함하는 불변(immutable) 형식**을 쓴다([GitHub OIDC 문서](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)). 즉 `sub`의 문면은 시간에 따라 움직이는 대상이다. 움직이는 문자열을 통째로 대조하는 코드는 그 변화를 만나는 순간 깨진다.

바른 길은 §4의 결론과 같다 — **`sub`를 대조 대상이 아니라 파생값으로 보고, 그 안에 뭉쳐 있는 구성 요소(`repository_id`·`ref`·`job_workflow_ref` 등)를 각각 별도 claim으로 검증한다.** 각 축을 따로 보면 한 축의 형식이 바뀌어도 판정이 조용히 무너지지 않는다(DO-11 각주: *"`sub`는 대조 대상이 아니라 파생값이다"*).

## 6. jti — 진위를 통과한 토큰의 재전송을 막는 축

여기까지의 검증을 다 통과한 토큰도 아직 막지 못한 공격이 하나 있다 — **재전송(replay)**이다. 유효한 토큰을 중간에서 가로채거나 로그에서 주워, 만료 전에 **그대로 다시** 보내는 것이다. 서명도 claim도 전부 진짜이므로 §4·§5의 어떤 칸도 이걸 잡지 못한다. 진위 검증과 재전송 방어는 다른 축이다.

그 다른 축을 담당하는 claim이 `jti`(JWT ID)다. RFC 7519는 이를 "JWT의 고유 식별자"로 정의하며, 값은 **다른 토큰에 우연히 같은 값이 배정될 확률이 무시할 만하도록** 발급되어야 하고, 명시적으로 "`jti` claim은 JWT가 재전송되는 것을 막는 데 쓸 수 있다"고 적는다([RFC 7519 §4.1.7](https://www.rfc-editor.org/rfc/rfc7519#section-4.1.7)). 다만 스펙이 주는 것은 *고유한 이름표*까지이고, "한 번만 쓰이게 하는" 것은 받는 쪽의 몫이다 — 받는 쪽이 **부작용을 일으키기 전에 그 `jti`를 내구적으로 선점**해 두고, 이미 본 `jti`가 다시 오면 거절하는 일회성 소비를 구현해야 비로소 재전송이 막힌다.

이 구조는 이 프로젝트에 이미 있는 축과 정확히 같다. 시스템 채널로 같은 요청이 두 번 오면 두 번 실행하지 않고 최초 결과를 재반환하는 멱등 규약(`usecases/README.md` K-1)이 그것이고, 배포 채널은 요청의 `requestId`와 토큰의 `jti`를 **부작용 전에 함께 선점**함으로써 같은 규약을 적용한다(DO-10 ⑶ · DO-11). *"토큰 재사용 = 재전송"* 이라는 한 문장이 시간 claim(`exp`)과 `jti`를 한 묶음으로 묶는 이유다 — `exp`는 창을 좁히고, `jti`는 그 창 안의 중복을 없앤다.

## 7. GitHub Actions가 주는 claim — 이름이 아니라 수치 ID까지 온다

앞 절들의 claim이 우리 상상이 아니라 실제로 토큰에 온다는 것을 GitHub 공식 문서로 확인해 두면, §8의 우리 행렬이 무엇 위에 서는지가 분명해진다. GitHub Actions OIDC ID 토큰의 발급자는 `https://token.actions.githubusercontent.com` 하나이고, payload에는 다음 claim들이 실린다([GitHub OIDC 문서](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)):

- **표준(등록) claim**: `iss`·`sub`·`aud`·`exp`·`nbf`·`iat`·`jti` — 앞의 절들이 다룬 그대로.
- **저장소 신원**: `repository`(이름)·`repository_id`(**수치 ID**)·`repository_owner`·`repository_owner_id`·`repository_visibility`. 이름과 수치 ID가 **둘 다** 온다는 점이 §5의 "이름 재사용" 방어를 실제로 가능하게 한다.
- **실행 맥락**: `ref`·`ref_type`·`sha`·`workflow`·`job_workflow_ref`·`event_name`·`head_ref`·`base_ref`·`run_id`·`run_number`·`run_attempt`.
- **행위자·환경**: `actor`·`actor_id`·`environment`·`runner_environment`.

여기서 우리 검증에 쓰이는 것은 이 전부가 아니라 §8이 고른 칸들이다 — claim이 많다는 것과 그중 무엇을 신뢰 판정에 태우느냐는 별개다. 특히 `environment` claim은 존재하지만, 그것이 운영 승인의 증거로 실제로 서는지는 다음 절이 짚는 별도의 문제다.

## 8. 우리 적용 — DO-11 행렬과 아직 서지 않은 운영 승인 결박

이 프로젝트는 위의 개념을 배포 신원 검증에 그대로 적용한다. 정본은 ADR-027 DO-11의 **claim 검증 행렬**이고(아래는 그 인용이다 — 재판정하지 않는다), 형태는 §4~§6이 설명한 그대로다: `iss`는 하나로 고정, `aud`는 우리 전용, 저장소는 `repository` + **`repository_id` 수치 ID**, `ref`는 허용목록, `job_workflow_ref`는 배포 워크플로 하나, `exp`·`nbf`·`iat`는 유효 창, `jti`는 부작용 전 선점. **`sub` 문자열은 대조하지 않는다.** HMAC과 OIDC는 AND이며, 한 칸이라도 불일치면 적용하지 않고 거절을 기록한다(DO-11 · RL-8 무예외).

다만 한 칸은 아직 서지 않았다. 운영 모드 배포를 사람의 승인 뒤에만 열려면, *"승인 뒤에만 발급되는 증거"*(보호된 environment의 secret 또는 그 environment로 발급된 토큰)가 요청에 결박되어 있어야 한다. 문제는 **그 결박이 GitHub 플랫폼에서 실제로 서는지를 문서만으로는 판정할 수 없다**는 것이다 — 구체적으로 **비공개 저장소에서 environment 보호 규칙·승인 게이트가 요금제상 걸리는가**가 확인되지 않았다. 그래서 이 항목은 `[구현 검증]`으로 이연되어 중앙 대장에 등재돼 있고(IV-37 · ADR-027 §7 잔여-5), **판정 전까지 "운영 승인"은 기계가 보증하는 값이 아니라 「자기 신고」로 읽으며 그 사실을 배포 이력에 남긴다.** [구현 검증]

정리하면 우리 검증이 지금 기계적으로 보증하는 경계는 *"우리 저장소의, 우리 배포 워크플로가, 허용된 ref에서, 재전송 없이 보냈는가"* 까지다 — §1이 던진 질문에 대한 답이 여기까지 왔다. 그 위에 "사람이 승인했는가"를 얹는 마지막 칸은 개념이 아니라 플랫폼 요금제의 문제로 남아 있고, 그 한계를 감추지 않고 이력에 적어 두는 것이 현재의 정직한 상태다(같은 축의 긴급 권한 결박은 ADR-024 §2.4 · CDV-20이 대칭으로 다룬다).
