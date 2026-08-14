# 배포 인프라 여정 — 아이디어에서 실전까지

이 폴더는 jun-bank의 배포 인프라(infra·core·gateway 세 repo에 걸친 CI/CD 파이프라인)를 만든 과정을 세 각도에서 읽는 문서 모음이다. 각 repo의 `docs/devlog/`가 PR 단위의 세로 읽기(한 PR이 무엇을 왜 했나)라면, 이 폴더는 가로 읽기다 — 전체가 어떤 문제 순서로 자랐고(이 문서), 어떤 구조로 서 있으며([architecture.md](architecture.md)), 어떤 설계 패턴이 반복됐는가([patterns.md](patterns.md)).

읽는 순서는 이 문서(여정) → 아키텍처 → 패턴을 권한다. 여정이 "왜 이런 것들을 만들었나"의 맥락을 주고, 아키텍처가 그 결과물의 정적 구조를, 패턴이 그 구조를 관통하는 반복된 판단을 보여준다.

## 무엇을 만들었나 — 한 문단

main 브랜치에 머지하면 GitHub Actions가 이미지를 빌드해 GHCR에 digest로 올리고, 서명된 배포 요청(compose 정의를 동봉한 manifest)을 발행한다. 그 요청은 오라클 클라우드의 엣지를 거쳐 집 서버(.9)의 배포 agent에 닿고, agent는 두 겹의 관문(HMAC 서명, GitHub OIDC 신원)을 통과한 요청만, 배포 창 락 안에서, 검증된 compose 바이트로만 실행한다. core는 블루-그린 무중단 전환으로, gateway는 재기동 교체로 배포된다. 배포할 이미지는 digest로, 실행할 정의는 서명에 동봉된 내용으로 고정되어 있어 호스트에 놓인 파일이 몰래 실행되는 경로가 없다.

이 문장의 모든 절이 한때 비어 있던 칸이었고, 아래 여정이 그 칸들을 채운 순서다.

## 왜 이렇게 만들었나 — 설계 우선의 성격

jun-bank는 카드사+뱅킹 시스템을 만드는 학습·포트폴리오 프로젝트이면서, "혼자서도 팀처럼 도는" 개발 사이클을 연습하는 자리다. 그래서 인프라도 코드부터 짜지 않았다 — 결정은 ADR(아키텍처 결정 기록)이 먼저 내리고, 이슈와 마일스톤으로 작업을 쪼개고, PR이 이슈를 닫고, 그 과정을 로그와 검증 대장이 기록한다. 이 방식이 만든 특징이 devlog 곳곳에 보인다: 거의 모든 PR이 앞 PR의 리뷰가 남긴 잔여에서 태어나고, 리뷰가 실제로 설계를 뒤집으며, "닫지 못한 것"이 다음 이슈로 정직하게 넘어간다.

## 마일스톤 세 개의 이야기

### S0 — 기반: 기록의 계약부터

첫 코드는 Go 파일이 아니라 DDL이었다([infra pr-02](../../../../infra/docs/devlog/pr-02-layout-schema.md)). 배포 이력과 배포 창 락을 담는 DB 스키마를 먼저 세웠는데, 그 설계의 핵심은 "권한 단위를 테이블이 아니라 정의된 연산으로 둔다"는 것이다 — 어느 계정도 raw DML을 갖지 않고, 락은 저장 프로시저로만, 이력은 append-only로만 바뀐다. 같은 규칙을 DB GRANT와 Go 코드 두 계층에서 강제한 것이 이후 반복될 패턴의 시작이다.

### S1 — 수신 관문: 실행하지 않는 상태에서 거절부터

S1은 요청을 받되 아무것도 실행하지 않는 단계다. HTTP 골격([pr-07](../../../../infra/docs/devlog/pr-07-http-skeleton.md))이 미들웨어 체인의 자리를 만들고, 게이트 1(HMAC 서명·requestId 멱등 — [pr-08](../../../../infra/docs/devlog/pr-08-hmac-gate1.md))과 게이트 2(OIDC claim 행렬 — [pr-10](../../../../infra/docs/devlog/pr-10-oidc-gate2.md))가 그 자리를 채우며, 모드 조회의 fail-closed([pr-12](../../../../infra/docs/devlog/pr-12-mode-failclosed.md))가 "모르면 승인 쪽으로 닫는다"를 세웠다.

이 단계에서 이 프로젝트의 검증 문화가 굳었다. 듀얼 리뷰(codex와 Opus 두 도구)가 세 번 실결함을 잡았는데 — 빈 requestId의 선점 붕괴, malformed nbf의 무음 통과, 단조 version의 fail-open — 전부 codex가 Opus의 누락을 보완했고 전부 "닫혀야 할 것이 열리는" 방향이었다. 리뷰어를 늘리는 것만으로는 부족하고 다른 방법(특히 실제로 실행해 보는 것)이 필요하다는 교훈이 여기서 나왔다.

### S2 — 실행: 부작용이 들어오다

S2는 실제로 배포하는 단계다. 배포 창 락 배선([pr-16](../../../../infra/docs/devlog/pr-16-window-lock.md))에서 그 교훈이 극적으로 확인됐다 — 같은 락 코드를 Opus는 "clean"으로, codex는 실 MySQL 익스플로잇으로 High 3건 실증으로, 정반대로 판정했다. 논증과 실행이 갈린 자리다.

이후 HTTP→오케스트레이션 배선([pr-18](../../../../infra/docs/devlog/pr-18-http-orchestration.md)), 실 dispatch([pr-22](../../../../infra/docs/devlog/pr-22-local-dispatch.md)), JWKS 실검증([pr-24](../../../../infra/docs/devlog/pr-24-jwks.md))을 거쳐 첫 실배포에 도달했는데, 거기서 false-UNKNOWN 사건([pr-25](../../../../infra/docs/devlog/pr-25-false-unknown.md))이 터졌다 — "통합에서 처음 실행되는 명령은 단위 테스트가 못 잡는다"는 것을 실증한 사건이다. 그다음 블루-그린 전환([pr-27](../../../../infra/docs/devlog/pr-27-blue-green.md)), repo별 allowlist([pr-29](../../../../infra/docs/devlog/pr-29-oidc-allowlist.md)), Outcome·identity 결박([pr-30](../../../../infra/docs/devlog/pr-30-outcome-identity.md))을 지나, 마지막으로 compose 동봉 실행 결박([pr-31](../../../../infra/docs/devlog/pr-31-compose-embed.md))이 S2를 완주시켰다.

### S3 — 분산: 다른 서버로 넓히다

S3은 .9 한 대에서 돌던 배포를 정산(.158)·원장(.164) 두 대로 넓힌 단계다. 로컬에는 없던 문제 — 원격 명령의 응답이 유실되면 무슨 일이 일어났는지 모른다 — 를 다뤄야 했고, 코드를 쓰기 전 두 번의 선검증이 "전송+자동 재개+fencing을 한 슬라이스에 담으면 서로 물린다"를 드러내 **세 조각으로 재슬라이스**했다([distributed-deploy-unknown](distributed-deploy-unknown.md)). 전송·실행자(최소·UNKNOWN=사람)→위성 fencing guard→자동 재개 순으로 각각 높음 리뷰를 거쳐 세운 뒤, 실서버 배선에서 그 계약들이 하나씩 fail-closed로 작동하는 걸 확인하며(lease 하한·workspace 배타성이 기동을 거부하며 배선을 지도했다) 양 위성 실배포를 완주했다 — "위성 배포 실행 불가"(CDT-1)로 오래 남아 있던 칸이 닫히고 배포 대상 넷이 전부 실동작한다([위성 여정](../../../../infra/docs/devlog/pr-34-38-satellite-transport.md)).

## 관통하는 하나의 문제 — fail-open

이 여정을 한 줄로 요약하면 "조용히 열리는 문을 하나씩 닫는 이야기"다. 리뷰가 잡은 결함의 압도적 다수가 fail-open이었다 — 모드를 모르면 dev로 열림, 시계 편차 0이 60초로 완화됨, stale 키로 무기한 검증, orphan이 틀린 이미지를 가림, 낡은 compose가 digest만 맞으면 통과. 이 프로젝트가 반복해서 택한 태도는 "값이 없으면 뜨지 않는 편이 맞다"이고, 그 태도가 어떤 구조로 코드에 나타났는지가 [patterns.md](patterns.md)의 주제다.

## 문서 지도

| 문서 | 무엇을 읽나 |
|---|---|
| 이 문서 | 전체 여정 — 문제 순서와 마일스톤 |
| [architecture.md](architecture.md) | 정적 구조 — 파이프라인 흐름·컴포넌트·신뢰 경계 |
| [patterns.md](patterns.md) | 반복된 설계 판단 — fail-closed·두 계층 강제·보증 계약 등 |

각 PR의 상세는 세 repo의 `docs/devlog/`에 있다 — [infra](../../../../infra/docs/devlog/README.md)(14편) · [core](../../../../core/docs/devlog/README.md)(2편) · [gateway](../../../../gateway/docs/devlog/README.md)(4편).
