# 배포 인프라의 설계 패턴 — 반복된 판단들

이 문서는 여러 PR에 걸쳐 반복해 나타난 설계 판단을 모은다. 여정([README.md](README.md))이 시간 순서, 아키텍처([architecture.md](architecture.md))가 정적 구조라면, 이 문서는 그 둘을 관통하는 "같은 생각의 반복"이다. 각 패턴은 이름·문제·해법·이 프로젝트에서의 실례로 적는다 — 다른 시스템을 만들 때도 옮겨 쓸 수 있는 모양으로.

## 패턴 1 — 모르면 닫는다 (fail-closed 기본값)

**문제.** 상태를 읽지 못하거나 값이 비었을 때, "일단 진행"이 곧 안전장치의 우회가 되는 자리가 있다.

**해법.** 판정 불가를 성공이 아니라 실패로 접는다. 특히 안전 게이트는 "모르면 열림"이 아니라 "모르면 닫힘"이어야 한다.

**실례.** 모드를 못 읽으면 dev(자동)가 아니라 operational(승인 필요)로 닫는다([pr-12](../../../../infra/docs/devlog/pr-12-mode-failclosed.md)). JWKS 키를 못 얻으면 전건 거절([pr-24](../../../../infra/docs/devlog/pr-24-jwks.md)). compose 세대 파일이 손상되면 "없음"이 아니라 "알 수 없음"으로 보고 폴백하지 않는다([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)). 이 프로젝트가 반복한 한 문장이 이 패턴을 요약한다 — "값이 없으면 뜨지 않는 편이 맞다."

## 패턴 2 — 같은 규칙을 두 계층에서 강제한다

**문제.** 한 계층의 규칙은 그 계층을 우회하는 경로가 생기면 무너진다.

**해법.** 중요한 불변식을 서로 독립적인 두 지점에서 강제한다 — 한쪽이 뚫려도 다른 쪽이 남게.

**실례.** 배포 스키마의 raw DML 금지를 DB GRANT(권한 부재)와 Go 코드(메서드 부재) 양쪽에서 막는다([pr-02](../../../../infra/docs/devlog/pr-02-layout-schema.md)). 모드 version의 단조성을 저장 프로시저 계산과 UNIQUE 제약 양쪽에서 강제한다([pr-12](../../../../infra/docs/devlog/pr-12-mode-failclosed.md)). lease 하한을 Go 오케스트레이션과 SQL 프로시저 양쪽에서 검증한다([pr-16](../../../../infra/docs/devlog/pr-16-window-lock.md)).

## 패턴 3 — 부재가 곧 강제다

**문제.** "하지 말라"를 규칙으로 적으면 그 규칙을 어기는 코드를 쓸 수 있다.

**해법.** 금지된 능력을 애초에 만들지 않는다. 금지 목록(deny-list)이 아니라 허용 집합(allow-list)으로 짠다.

**실례.** store가 일반 Exec/Query를 노출하지 않으니 raw DML을 쓸 방법이 없다([pr-02](../../../../infra/docs/devlog/pr-02-layout-schema.md)). subprocess env가 "COMPOSE_* 를 지우는" 코드 없이 애초에 상속하지 않는다 — 허용 집합(PATH + 주입값)이다([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)). 특권 실행이 열거된 명령만 argv로 돌려 raw shell을 만들 자리가 없다([pr-22](../../../../infra/docs/devlog/pr-22-local-dispatch.md)).

## 패턴 4 — 부작용 전에 선점한다

**문제.** 판정과 실행 사이의 창에서 재전송·경합·중복이 끼어든다.

**해법.** 되돌릴 수 없는 일을 하기 전에, 그 일을 할 권리를 원자적으로 확보한다.

**실례.** requestId·jti를 어떤 부작용도 있기 전에 원장에 INSERT로 선점한다 — UNIQUE 제약이 재전송을 INSERT 시점에 거부한다([pr-08](../../../../infra/docs/devlog/pr-08-hmac-gate1.md)). 배포 창 락을 "조회"가 아니라 "조건부 UPDATE 획득"으로 잡는다([pr-16](../../../../infra/docs/devlog/pr-16-window-lock.md)). repo↔target 결박을 멱등 선점 이전에 둬서, 권한 없는 요청이 requestId를 소모하지 못하게 한다([pr-29](../../../../infra/docs/devlog/pr-29-oidc-allowlist.md)).

## 패턴 5 — 보증되지 않으면 손대지 않는다

**문제.** 실패했을 때 "무엇이 어디까지 됐는지"를 모르면, 되돌리려는 행동이 오히려 라이브 상태를 망가뜨린다.

**해법.** 실패를 "미전환이 보증됨 / 실상태 불명"으로 나눈다. 불명이면 아무것도 정리하지 않고 사람을 부른다.

**실례.** 블루-그린 전환 실패를 게이트웨이의 보증 수준(ROLLED_BACK / INDETERMINATE / 409 소유권 상실)으로 3분기해, 보증 없는 실패에는 어느 슬롯도 내리지 않는다([pr-27](../../../../infra/docs/devlog/pr-27-blue-green.md)). 정리(down) 실패는 green이 남았을 수 있으니 UNKNOWN으로 락을 쥔 채 올린다([pr-22](../../../../infra/docs/devlog/pr-22-local-dispatch.md)). false-UNKNOWN 사건에서 fail-closed가 옳게 작동해 잘못된 "완료" 위장을 막은 것도 이 패턴의 실증이다([pr-25](../../../../infra/docs/devlog/pr-25-false-unknown.md)).

## 패턴 6 — 이름이 아니라 내용으로 고정한다

**문제.** 이름(태그·라벨·경로)은 재사용·변조·드리프트에 노출된다.

**해법.** 내용 주소(content-address)로 참조한다 — digest·해시. 그러면 "무엇이 실행되는가"가 이름이 아니라 바이트로 고정된다.

**실례.** 이미지를 태그가 아니라 digest로 pull·대조한다([pr-22](../../../../infra/docs/devlog/pr-22-local-dispatch.md)). compose를 이름표가 아니라 sha256으로 결박하고 검증된 바이트를 그대로 실행한다([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)). 저장소를 이름이 아니라 수치 ID로 매칭한다 — 이름은 재생성으로 재사용되지만 수치 ID는 아니다([pr-29](../../../../infra/docs/devlog/pr-29-oidc-allowlist.md)).

## 패턴 7 — 판정 소스를 하나로 둔다

**문제.** 같은 것을 두 곳에서 판정하면, 둘이 갈리는 순간 어느 쪽이 이겼는지가 침묵으로 결정된다.

**해법.** 검증·정규화·상태의 정본을 한 곳에만 둔다. 그 한 곳이 곧 계약이다.

**실례.** 서명 정규화가 `Canonicalize` 한 곳에만 있다 — CI와 agent가 같은 형태를 만들어야 하므로([pr-08](../../../../infra/docs/devlog/pr-08-hmac-gate1.md)). claim 대조를 라이브러리에 맡기지 않고 `checkClaims` 한 곳이 소유한다([pr-10](../../../../infra/docs/devlog/pr-10-oidc-gate2.md)). 라우트 상태의 정본이 SCG 라우트 한 곳이고, 조회 API도 그 스냅샷을 읽는다(사본을 따로 캐시하지 않음 — [gateway pr-02](../../../../gateway/docs/devlog/pr-02-dynamic-route.md)). JSON 필드 대소문자 무시 때문에 판정 소스가 둘로 갈리던 것을 최상위 키 정확 대조로 닫은 것도 이 패턴이다([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)).

## 패턴 8 — 닫지 못한 것을 소리내어 남긴다

**문제.** 방어선이 무언가를 못 막으면, 그 사실이 조용히 묻혀 "다 막았다"로 오인된다.

**해법.** 미완·한계·이연을 코드 주석·이슈·검증 대장에 명시한다. 무음 이연을 금지한다.

**실례.** dispatch의 orphan 완전 방어를 못 하면서 "무음 이연 아님"과 함께 이슈 #21로 분리했다([pr-22](../../../../infra/docs/devlog/pr-22-local-dispatch.md)). identity 결박이 못 닫는 축(엉뚱한 서비스를 가리키는 오설정)을 주석에 적고 #19가 닫는다고 남겼다([pr-30](../../../../infra/docs/devlog/pr-30-outcome-identity.md)). JWKS 재페치 창의 kid 거절이 fail-open이 아니라 가용성 대가임을 주석으로 구분했다([pr-24](../../../../infra/docs/devlog/pr-24-jwks.md)). 구현 접촉에서만 판정 가능한 수치는 `[구현 검증]` 태그로 중앙 대장에 등재한다.

## 패턴 9 — 그린이 안전을 뜻하지 않는다 (검증의 검증)

**문제.** 테스트가 통과하고 배포가 완료돼도, 그 판정 자체가 공허하거나 위장일 수 있다.

**해법.** 테스트가 실제로 무엇을 잡는지 확인한다 — 결함을 먼저 재현(red-first)하고, 방어를 되돌려 테스트가 붉어지는지 본다(뮤테이션). "무엇이 깨지면 이 테스트가 붉어지는가"에 답하지 못하는 단언은 공허하다.

**실례.** 락 보안 3건을 미수정 스키마에서 프로브로 재현 통과시켜(RED 증거) 실재를 증명한 뒤 회귀 테스트로 바꿨다([pr-16](../../../../infra/docs/devlog/pr-16-window-lock.md)). compose 동봉의 방어선 14종을 뮤테이션으로 전부 붉어지게 확인했다([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)). 선언한 실패모드를 통과시키던 공허 단언(`dispatch > 2` 같은)을 뮤테이션으로 실제 검증하도록 교체했다([pr-29](../../../../infra/docs/devlog/pr-29-oidc-allowlist.md)). CI 테스트에서 Gradle의 UP-TO-DATE 캐시 통과를 `--rerun-tasks`로 배제한 것도 같은 경계다([gateway pr-05](../../../../gateway/docs/devlog/pr-05-ci-test.md)).

## 패턴 10 — 리뷰는 다른 방법을 겹친다

**문제.** 같은 코드를 여러 명이 같은 방식으로 봐도, 한 방식이 놓치는 것은 다 놓친다.

**해법.** 서로 다른 방법을 겹친다 — 논증과 실행, 구현을 본 리뷰와 안 본 리뷰(blind), 도구 A와 도구 B.

**실례.** 배포 창 락에서 Opus는 SQL 의미를 논증해 clean으로 읽었고 codex는 실 MySQL로 익스플로잇해 High 3건을 실증했다 — 정반대 판정이 갈린 이유가 방법의 차이였다([pr-16](../../../../infra/docs/devlog/pr-16-window-lock.md)). 여러 PR에서 codex가 Opus의 누락을 단독으로 보완했다(빈 requestId·malformed nbf). 구현을 열람하지 않고 불변식만 보고 테스트를 설계하는 blind 워커가 명세 공백을 되돌려줬다([pr-29](../../../../infra/docs/devlog/pr-29-oidc-allowlist.md)·[pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md)). 이 프로젝트의 결론 — 리뷰어를 늘리는 것보다 방법을 겹치는 것이 결함을 잡는다.

## 이 패턴들이 함께 그리는 태도

열 가지가 결국 한 방향을 가리킨다: **안전한 실패를 위험한 성공보다 낫게 여긴다.** 모르면 닫고(1), 우회로를 없애고(2·3), 되돌릴 수 없는 일 앞에 선점하고(4), 보증 없이 손대지 않고(5), 이름 대신 내용으로 고정하고(6), 판정을 한 곳에 두고(7), 못 막은 것을 소리내어 남기고(8), 검증 자체를 의심하고(9), 방법을 겹쳐 본다(10). 뱅킹 시스템의 인프라라는 성격 — 조용한 실패가 자금·신뢰에 직결되는 도메인 — 이 이 태도를 정당화한다.
