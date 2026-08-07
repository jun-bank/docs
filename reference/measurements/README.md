# 실측 근거 — 측정 방법과 재현 절차

이 폴더는 언어 학습 문서(`study/tech/languages/`)와 ADR-028이 인용하는 수치들이 **어떻게 측정됐는지**를 보존한다. 문서에는 결과(예: "고루틴 개당 약 2.6KB", "Go 기동 4.5ms vs JVM 78ms")만 있으면 검증할 수 없다 — 그 수치를 낸 실제 프로그램과 명령이 여기 있어서 누구든 다시 돌려볼 수 있다. 수치를 인용하는 문서는 이 폴더를 가리킨다.

## 측정 환경 (2026-08-07, 개발 머신)

측정은 홈랩 서버가 아니라 이 프로젝트의 개발 머신에서 이뤄졌다. 절대값보다 **배율**(예: JVM 기동이 Go의 약 17배)이 결정 근거이고, 배율은 환경이 달라도 크게 변하지 않는다. 홈랩 실측이 필요하면 같은 프로그램을 그 서버에서 돌리면 된다.

- Go: go1.24.5 linux/amd64
- JVM: OpenJDK 21.0.5 LTS (Temurin)
- 커널: Linux 7.0.0

## 측정 항목과 방법

**고루틴 메모리** (`go-runtime/goroutines_rss.go`) — 고루틴 10만 개를 띄워 대기시킨 뒤 OS가 보고하는 RSS(실사용 메모리)를 읽고 개수로 나눈다. 결과 ≈2.6KB/개. 이것이 "OS 스레드(수 MB)와 다르다"의 근거다. 재현: `go run goroutines_rss.go` 실행 후 해당 프로세스의 `/proc/<pid>/status`에서 `VmRSS`를 읽는다.

**GC 정지 시간** (`go-runtime/gc_pause.go`) — 약 20MB의 살아있는 포인터 데이터를 두고 3초간 할당을 반복시키며 `GODEBUG=gctrace=1`이 내보내는 STW(stop-the-world) 구간을 읽는다. 결과: 생존 힙 16.5MB에서 STW 중앙값 93.8µs. 작은 힙에서 Go GC가 사실상 무비용인 근거. 재현: `GODEBUG=gctrace=1 go run gc_pause.go`.

**기동 시간·바이너리 크기** (`go-runtime/hello.go`) — hello world를 컴파일해 바이트 수를 재고(`go build` 후 `stat`), 여러 번 실행해 프로세스 시작~종료 벽시계를 잰다. 동급 JVM 프로그램과 대조. 결과: 정적 바이너리 2,204,862B, 기동 Go 4.5ms vs JVM 78.2ms(약 17배). dispatcher가 SSH 호출마다 뜨는 프로세스라 이 배율이 곧 배포 소요라는 ADR-028 §4 논거의 실증. 재현: `go build -o hello hello.go && stat -c %s hello`, 기동은 `time ./hello` 반복.

**Kotlin 컬렉션 별칭 함정** (`kotlin-collections/Probe.java`) — Kotlin `listOf()`·`mutableListOf()`가 런타임에 어떤 Java 클래스가 되는지, Java 쪽에서 `set()`·`add()`가 통과하는지를 실행으로 확인한다. dev-conventions KO-2("읽기전용 인터페이스 뒤 객체가 외부 별칭으로 변경될 수 있다")의 실측판. 재현: `kotlin-stdlib` jar를 클래스패스에 두고 `javac Probe.java && java Probe`.

## 한계

이 수치들은 한 머신의 한 번 측정이다. 결정에 쓰는 것은 절대값이 아니라 배율·차수(order of magnitude)이며, 정밀 벤치마크(반복·분산·통계)가 필요한 판정은 `[구현 검증]`으로 이연한다 — 특히 홈랩 서버(허브 CPU 약함)에서의 실배포 소요는 첫 배포가 측정한다(cicd CDV-14).
