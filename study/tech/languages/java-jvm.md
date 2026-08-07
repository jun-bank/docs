# JVM과 Java — "결정을 실행 시점까지 미룬다"는 선택과 그 청구서

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 언어 결정 정본: [`architecture/adr/ADR-028-language-selection.md`](../../../architecture/adr/ADR-028-language-selection.md)).

이 문서는 JVM(Java Virtual Machine)이 무엇을 풀려고 만들어졌고, 그 해법이 어떤 성질과 비용을 필연적으로 낳는지를 개념부터 설명한다. 순서는 하나의 논리를 따른다 — 무엇이 문제였나, 그 문제를 어떤 아이디어로 풀었나, 그 아이디어가 반드시 만드는 청구서는 무엇인가. 바이트코드·클래스로더·JIT·GC·메모리 모델은 각각의 기능이 아니라 **"컴파일 시점에 확정하지 않고 실행 시점까지 미룬다"는 하나의 결정에서 갈라져 나온 결과**로 읽는 것이 이해가 빠르다. 인용한 스펙 문장은 Java SE 21의 JVMS·JLS, HotSpot 동작은 OpenJDK 문서·JEP·소스 주석 기준이며, 수치는 각 출처가 밝힌 측정 조건에서만 유효하다.

## 1. 문제 — 모르는 기계 위에서, 사람이 메모리를 세지 않고 돌아야 한다

두 가지 문제가 동시에 있었다. 첫째, 배포 대상 기계의 CPU·OS를 컴파일 시점에 알 수 없다. 기계마다 다시 컴파일하면 "같은 프로그램"이라는 말이 흔들린다. 둘째, 사람이 해제 시점을 관리하는 메모리 모델은 해제 후 사용(use-after-free)과 이중 해제를 만드는데, 이 결함의 특징은 프로세스가 **죽지 않고 오염된 상태로 계속 도는 것**이다.

이 둘은 성격이 달라 보이지만 요구는 같다 — **프로그램과 실제 기계 사이에 판단할 수 있는 층을 하나 끼워 넣는 것**이다. 그 층이 있으면 명령어 번역도, 객체 수명 추적도 그 층이 대신할 수 있다.

## 2. 아이디어 — 기계를 하나 발명하고, 그 기계만 상대한다

JVM 스펙은 자신을 이렇게 규정한다. "The Java Virtual Machine is the cornerstone of the Java platform. It is the component of the technology responsible for its hardware- and operating system-independence, the small size of its compiled code, and its ability to protect users from malicious programs. The Java Virtual Machine is an abstract computing machine."([JVMS SE 21 §1.2](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-1.html))

주목할 문장은 그다음이다. "The Java Virtual Machine knows nothing of the Java programming language, only of a particular binary format, the class file format."(같은 절) 계약의 단위는 언어가 아니라 **`class` 파일 형식**이다. 그래서 Kotlin·Scala·Groovy가 같은 런타임 위에 설 수 있고, 이 프로젝트가 Java에서 Kotlin으로 언어를 바꾸면서도 생태계를 하나도 잃지 않는다(ADR-028 §3.2 — 판단 정본은 그쪽이다).

메모리 쪽도 같은 자리에 위임된다. "The heap is created on virtual machine start-up. Heap storage for objects is reclaimed by an automatic storage management system (known as a garbage collector); objects are never explicitly deallocated. The Java Virtual Machine assumes no particular type of automatic storage management system, and the storage management technique may be chosen according to the implementor's system requirements."([JVMS §2.5.3](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html))

마지막 문장이 중요하다 — 스펙은 **GC를 요구하되 어떤 GC인지는 정하지 않았다**. 그 빈칸이 뒤에 나오는 G1과 ZGC를 가능하게 한 자리다.

## 3. 클래스로더 — "언제 로드되는가"가 별도 개념이 된다

실행 시점까지 미루기로 한 순간, "무엇을 언제 읽어 들이는가"가 개념으로 승격된다. 스펙은 셋을 나눈다. "Loading is the process of finding the binary representation of a class or interface type with a particular name and creating a class or interface from that binary representation. Linking is the process of taking a class or interface and combining it into the run-time state of the Java Virtual Machine so that it can be executed. Initialization of a class or interface consists of executing the class or interface initialization method `<clinit>`."([JVMS §5](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-5.html))

링크는 다시 검증(verification)·준비(preparation)·해소(resolution)로 나뉘고, 스펙은 순서를 자유롭게 두되 두 가지는 못박는다 — "A class or interface is completely loaded before it is linked. A class or interface is completely verified and prepared before it is initialized."(§5.4) 검증이 여기 있다는 점이 §1의 두 번째 문제와 이어진다. 임의의 바이트 열이 아니라 **타입 안전성이 검사된 것만** 실행된다.

로드 자체는 위임 구조를 따른다. "The `ClassLoader` class uses a delegation model to search for classes and resources. Each instance of `ClassLoader` has an associated parent class loader. When requested to find a class or resource, a `ClassLoader` instance will usually delegate the search for the class or resource to its parent class loader before attempting to find the class or resource itself."([`java.lang.ClassLoader` javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ClassLoader.html))

부모에게 먼저 묻는다는 규칙 하나가 "애플리케이션 코드가 `java.lang.String`을 가짜로 바꿔치기할 수 없다"를 보장한다. 반대로 이 유연성의 청구서도 여기서 나온다 — 같은 이름의 클래스가 다른 로더에서 로드되면 **서로 다른 타입**이고, `ClassCastException`의 메시지가 "A cannot be cast to A"처럼 읽히는 상황이 그것이다. [실무 의견]

## 4. JIT ① — 미룬 덕에 더 많이 아는 컴파일러

바이트코드를 매번 해석하면 느리다. 그래서 HotSpot은 실행 중에 기계어로 컴파일한다. 컴파일러는 둘이다. C1은 "Fast, lightly optimizing bytecode compiler"이고, C2는 "Highly optimizing bytecode compiler, also known as 'opto'"로 "global value numbering, conditional constant type propagation, constant folding, global code motion, algebraic identities, method inlining (aggressive, optimistic, and/or multi-morphic), intrinsic replacement, loop transformations" 등을 수행한다([HotSpot Glossary](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html)).

둘을 함께 쓰는 것이 티어드 컴파일이다. "Without tiered compilation, a server VM uses the interpreter to collect profiling information about methods that is sent to the compiler. With tiered compilation, the server VM also uses the client compiler to generate compiled versions of methods that collect profiling information about themselves. ... Tiered compilation is enabled by default for the server VM."([Java HotSpot VM Performance Enhancements](https://docs.oracle.com/en/java/javase/21/vm/java-hotspot-virtual-machine-performance-enhancements.html))

단계는 다섯이고, HotSpot 소스 주석이 그대로 나열한다.

```
level 0 - interpreter (Profiling is tracked by a MethodData object, or MDO in short)
level 1 - C1 with full optimization (no profiling)
level 2 - C1 with invocation and backedge counters
level 3 - C1 with full profiling (level 2 + All other MDO profiling information)
level 4 - C2 with full profile guided optimization
```
([`compilationPolicy.hpp`](https://github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilationPolicy.hpp))

여기서 설계 의도가 드러난다. 같은 주석이 "level 2 is generally faster than level 3 by about 30%, therefore we would want to minimize the time a method spends at level 3"라고 적는다 — **프로파일링은 공짜가 아니고**, 정책의 상당 부분이 "C2에 넘길 만큼의 프로파일만 모으고 빨리 빠져나오기"에 쓰인다. 트리비얼한 메서드는 아예 "compiled at level 1 instead of 4"로 끝난다.

즉 JIT의 이점은 "나중에 컴파일해서"가 아니라 **컴파일할 때 실제 실행 통계를 알고 있어서**다. 어느 분기가 실제로 잡히는지, 어느 호출 지점이 사실상 단형(monomorphic)인지는 정적 컴파일러가 알 수 없고, 이것이 인라이닝의 질을 좌우한다.

## 5. JIT ② 탈최적화 — 틀려도 되게 만들어 두고 공격적으로 추측한다

프로파일에 근거한 추측은 언젠가 깨진다. 새 서브클래스가 로드되면 단형 가정이 무너지고, 지금까지 null이 없던 필드에 null이 들어온다. 그래서 되돌리는 장치가 짝으로 필요하다.

- **deoptimization**: "The process of converting an compiled (or more optimized) stack frame into an interpreted (or less optimized) stack frame. Also describes the discarding of an nmethod whose dependencies (or other assumptions) have been broken. Deoptimized nmethods are typically recompiled to adapt to changing application behavior."
- **uncommon trap**: "When code generated by C2 reverts back to the interpreter for further execution. C2 typically compiles for the common case, allowing it to focus on optimization of frequently executed paths."
- **on-stack replacement (OSR)**: 루프를 도는 중인 인터프리터 프레임을 컴파일된 프레임으로 갈아 끼우는 것 — "A rough inverse to deoptimization."

(모두 [HotSpot Glossary](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html))

이 되돌림 장치가 JVM 성능의 핵심 비대칭이다. **되돌릴 수 있으니 틀릴 수 있는 최적화를 해도 된다.** 정적 컴파일러는 모든 가능한 서브클래스를 고려해야 하지만, JIT는 "지금까지 이 호출 지점은 한 종류만 봤다"에 걸고 인라이닝한 뒤, 가정이 깨지면 프레임을 인터프리터로 되돌린다. OpenJDK 자신의 표현으로는 "It can speculatively optimize native code, assuming a particular frequent path of execution, and revert to interpreting bytecode when it observes that the assumption no longer holds. ... By these and related techniques, the JVM can achieve higher peak performance than is possible with traditional static approaches."([JEP 483](https://openjdk.org/jeps/483))

## 6. 그래서 얼마나 빠른가 — "네이티브 몇 배"의 정직한 형태

이 질문은 조건 없이는 답이 없다. 정직한 형태는 셋으로 쪼개는 것이다.

**① 정점 성능(peak)**: 충분히 오래 돈 뒤의 뜨거운 경로는 §5의 이유로 정적 컴파일과 같은 급에 들어간다. 공개 실측 중 조건이 명시된 것은 Benchmarks Game이다. 25.03 회차의 Java 대 C++(g++) 비교에서, 손으로 벡터 명령을 쓴 항목(사이트가 `*`로 표시)을 뺀 각 문제의 최속 구현끼리 CPU 초를 비교하면 이렇다([Java vs C++ g++](https://benchmarksgame-team.pages.debian.net/benchmarksgame/fastest/javavm-gpp.html)).

| 문제 | C++ g++ | Java | 배수 |
|---|---|---|---|
| spectral-norm | 5.34 | 5.51 | 1.03 |
| fannkuch-redux | 30.73 | 40.12 | 1.31 |
| n-body | 5.17 | 6.94 | 1.34 |
| mandelbrot | 9.31 | 16.15 | 1.73 |

"1~2배 안"이라는 통념은 **이 조건에서는** 유지된다. 조건을 세 가지 밝혀 둔다. ⑴ 이 프로그램들은 수 초~수십 초를 도는 계산 커널이라 워밍업이 이미 끝난 구간만 잰다 — 즉 JIT에 가장 유리한 형태다. ⑵ `*` 표시된 수작업 벡터화 C++ 구현까지 넣으면 격차는 크게 벌어진다(mandelbrot에서 3.46초, 약 4.7배). ⑶ 사이트 자신이 "How the programs are written matters! Always look at the source code."라고 못박는다 — 이것은 언어의 순위표가 아니라 특정 구현들의 측정치다([측정 방법](https://benchmarksgame-team.pages.debian.net/benchmarksgame/how-programs-are-measured.html)). 서버 워크로드에 그대로 옮길 수 있는 배수가 아니라는 뜻이고, 애초에 이 프로젝트의 지배 항은 CPU가 아니다(§12).

**② 워밍업(warmup)**: 그 정점에 도달하기까지의 구간. OpenJDK는 이를 "warmup time, i.e., the time required for the HotSpot JVM to optimize an application's code for peak performance"로 정의한다([JEP 483](https://openjdk.org/jeps/483)). 이 구간이 존재한다는 사실 자체가 비용이다(§11).

**③ AOT와의 대조**: 같은 자바 코드를 JIT로 돌린 것과 GraalVM Native Image로 AOT 컴파일한 것을 나란히 잰 자료가 같은 회차에 있다([Java vs Java naot](https://benchmarksgame-team.pages.debian.net/benchmarksgame/fastest/java.html)). CPU 초는 AOT가 조금 앞서고(fannkuch-redux 34.41 대 40.12, n-body 6.01 대 6.94, spectral-norm 5.35 대 5.51), **상주 메모리는 AOT가 약 1/3**(n-body 20MB 대 61MB), 빌드 시간은 AOT가 두 자릿수 배로 길다(같은 표의 `make` 열: 약 145초 대 1.7초).

여기서 성급한 결론을 내면 안 된다. 이 프로그램들은 클래스 수가 적고 동적 디스패치가 거의 없는 계산 커널이라 **§5가 말한 JIT의 무기(실행 프로파일 기반 추측)가 쓰일 자리가 없다.** 그 무기가 필요한 쪽에서는 반대 방향의 증거가 나온다 — GraalVM 자신이 처리량을 올리려면 프로파일을 되돌려 넣으라고 안내한다. "Consider using Profile-Guided Optimization (PGO) to optimize your application for improved throughput. These optimizations allow the Graal compiler to leverage profiling information, **similar to when it is running as a JIT compiler**, when AOT-compiling your application."([GraalVM Native Image: Optimizations and Performance](https://www.graalvm.org/latest/reference-manual/native-image/optimizations-and-performance/), 강조 추가. PGO는 Oracle GraalVM 기능이고 Community Edition에는 없다.) AOT가 JIT의 처리량에 근접하려면 JIT가 공짜로 갖고 있던 것을 별도 단계로 만들어 넣어야 한다는 뜻이다.

정리하면 축은 성능이 아니라 **프로세스 수명**이다. 짧게 뜨고 죽는 것에는 AOT가, 오래 도는 큰 동적 코드베이스에는 JIT가 유리하다 — 그리고 이 구도가 §11·§12의 결론을 그대로 예고한다.

## 7. GC ① 세대 가설과 G1 — 젊어서 죽는 객체를 노린다

GC 전략의 출발점은 관찰 하나다. "The weak generational hypothesis states that young objects tend to die young, while old objects tend to stick around. Thus collecting young objects requires fewer resources and yields more memory, while collecting old objects requires more resources and yields less memory."([JEP 439](https://openjdk.org/jeps/439))

이 가설이 참이면 힙 전체를 매번 훑을 이유가 없다. 세대별 수집은 그래서 "objects expected to be referenced for different lengths of time"을 다른 영역에 두고 영역마다 다른 알고리즘을 쓰는 기법이다([HotSpot Glossary](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html)).

기본 컬렉터인 G1이 이것을 구현하는 방식은 영역(region) 분할이다. "G1 partitions the heap into a set of equally sized heap regions, each a contiguous range of virtual memory. A region is the unit of memory allocation and memory reclamation." 회수는 복사로 한다 — "G1 reclaims space mostly by using evacuation: live objects found within selected memory areas to collect are copied into new memory areas, compacting them in the process." 그리고 그 복사는 멈춘 상태에서 한다 — "G1 performs garbage collections and space reclamation in stop-the-world pauses."([Oracle GC Tuning Guide: G1](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html))

여기서 G1의 성격이 나온다. G1은 일시정지를 **없애는** 것이 아니라 **예측 가능한 상한 안에 넣는** 컬렉터다. 목표는 설정값이고 소프트 목표다 — "Sets a target for the maximum GC pause time (in milliseconds). This is a soft goal, and the JVM will make its best effort to achieve it. ... By default, for G1 the maximum pause time target is 200 milliseconds."([`java` 명령 레퍼런스, `-XX:MaxGCPauseMillis`](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html))

기본값 200ms라는 숫자를 이 프로젝트 맥락에 놓으면 성격이 보인다 — 승인 응답 p99 목표가 3초인 시스템(BR-01)에서 200ms는 예산의 한 자리를 차지하지만 치명적이지는 않고, 목표가 수십 ms인 시스템이라면 G1은 처음부터 틀린 선택이다.

## 8. GC ② ZGC — 일시정지를 힙 크기에서 떼어낸 방법

G1의 한계는 "살아 있는 객체를 멈춘 채로 복사한다"에 있다. 힙이 커지면 옮길 것도 늘고 일시정지도 늘어난다. ZGC는 **복사 자체를 애플리케이션과 동시에** 하는 쪽으로 문제를 옮겼다.

핵심 장치가 컬러 포인터와 로드 배리어다. "A core design principle/choice in ZGC is the use of load barriers in combination with colored object pointers (i.e., colored oops). This is what enables ZGC to do concurrent operations, such as object relocation, while Java application threads are running. From a Java thread's perspective, the act of loading a reference field in a Java object is subject to a load barrier. In addition to an object address, a colored object pointer contains information used by the load barrier to determine if some action needs to be taken before allowing a Java thread to use the pointer. For example, the object might have been relocated, in which case the load barrier will detect the situation and take appropriate action."([JEP 333](https://openjdk.org/jeps/333))

그 결과가 일시정지와 힙 크기의 분리다. "Stop-the-world phases are limited to root scanning, so GC pause times do not increase with the size of the heap or the live set."(같은 문서) 대신 청구서는 처리량으로 간다 — JEP 333의 목표 자체가 "No more than 15% application throughput reduction compared to using G1"이었다. 배리어는 참조를 읽을 때마다 실행되는 코드이므로, **일시정지를 산 값은 상시 오버헤드**다.

세대화는 나중에 얹혔다. JDK 21의 [JEP 439](https://openjdk.org/jeps/439)가 Generational ZGC를 도입하면서 스토어 배리어를 추가해 세대 간 참조(remembered set)와 마킹을 담당하게 했고, 로드 배리어의 책임을 줄여 더 최적화했다. 이후 [JEP 474](https://openjdk.org/jeps/474)(JDK 23)가 세대 모드를 기본값으로 바꾸고 [JEP 490](https://openjdk.org/jeps/490)(JDK 24)이 비세대 모드를 제거했다. 즉 지금 `-XX:+UseZGC`는 세대별 ZGC다.

실측 대조는 JEP 333이 SPECjbb 2015, 128G 힙, composite 모드에서 보고한 값이 가장 구체적이다.

| | 평균 | 99.9 백분위 | 최대 |
|---|---|---|---|
| ZGC | 1.091ms | 1.663ms | 1.681ms |
| G1 | 156.806ms | 543.846ms | 543.846ms |

처리량(max-jOPS)은 ZGC 100%를 기준으로 G1이 91.2%, 지연 민감 지표(critical-jOPS)는 ZGC 76.1% 대 G1 54.7%였다. 이 수치는 **128G 힙이라는 조건에서의 값**이고, 힙이 작으면 격차는 줄어든다(G1 일시정지가 힙에 비례하는 반면 ZGC는 그렇지 않다는 것이 이 표의 요지다).

"서브 ms"라는 표현의 근거는 JEP 439의 목표 조항과 서술이다 — "Pause times should not exceed 1 millisecond", 그리고 "ZGC's pause times are consistently measured in microseconds; by contrast the pause times of the default garbage collector, G1, range from milliseconds to seconds." `java` 레퍼런스의 표현은 조금 더 보수적이다 — "This is a low latency garbage collector, providing max pause times of a few milliseconds, at some throughput cost. Pause times are independent of what heap size is used. Supports heap sizes from 8MB to 16TB."

## 9. 메모리 모델 — happens-before, "동시성이 맞다"를 말할 수 있게 하는 규칙

JIT와 CPU가 재배치를 한다는 사실은 §5에서 이미 나왔다. 그러면 다른 스레드가 내 쓰기를 언제 보는지를 어떻게 아는가. 이 물음에 답이 없으면 동시성 코드의 "정확하다"는 말이 정의되지 않는다.

재배치의 출처는 하나가 아니다. "There are a number of potential sources of reordering, such as the compiler, the JIT, and the cache. The compiler, runtime, and hardware are supposed to conspire to create the illusion of as-if-serial semantics, which means that in a single-threaded program, the program should not be able to observe the effects of reorderings. However, reorderings can come into play in incorrectly synchronized multithreaded programs."([JSR-133 FAQ](https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html))

자바의 답이 happens-before다. "Two actions can be ordered by a *happens-before* relationship. If one action *happens-before* another, then the first is visible to and ordered before the second."([JLS SE 21 §17.4.5](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)) 관계를 만드는 규칙은 프로그램 순서와 전이성, 그리고 synchronizes-with에서 온다(§17.4.4).

| 만드는 것 | 스펙 문장 |
|---|---|
| 락 | "An unlock action on monitor *m* synchronizes-with all subsequent lock actions on *m*" |
| volatile | "A write to a volatile variable *v* synchronizes-with all subsequent reads of *v* by any thread" |
| 스레드 시작 | "An action that starts a thread synchronizes-with the first action in the thread it starts." |
| 스레드 종료 | "The final action in a thread `T1` synchronizes-with any action in another thread `T2` that detects that `T1` has terminated." |

그 위에 데이터 경합과 보증이 정의된다. "When a program contains two conflicting accesses that are not ordered by a happens-before relationship, it is said to contain a *data race*." 그리고 "If a program is correctly synchronized, then all executions of the program will appear to be sequentially consistent."(§17.4.5)

이 보증의 값어치를 스펙 자신이 설명한다 — "This is an extremely strong guarantee for programmers. Programmers do not need to reason about reorderings to determine that their code contains data races. Therefore they do not need to reason about reorderings when determining whether their code is correctly synchronized."(같은 절) **경합만 없애면 재배치를 머릿속에서 지워도 된다**는 것이 JMM이 개발자에게 판 물건이다.

주의할 함정 하나는 FAQ가 못박는다. "It is important for both threads to synchronize on the same monitor in order to set up the happens-before relationship properly. It is not the case that everything visible to thread A when it synchronizes on object X becomes visible to thread B after it synchronizes on object Y."([JSR-133 FAQ](https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html)) 동기화는 "어딘가 락을 걸었다"가 아니라 **같은 모니터로 짝을 맞췄다**일 때만 성립한다.

```kotlin
class BalanceCache {
    @Volatile private var snapshot: Balance? = null   // volatile 쓰기 = 모니터 해제와 같은 메모리 효과

    fun publish(b: Balance) { snapshot = b }          // 이 쓰기 이전의 모든 쓰기가
    fun read(): Balance? = snapshot                   // 이 읽기 이후에 보인다
}
```

비용도 실재한다. LMAX가 2.4GHz 코어에서 64비트 카운터를 5억 번 증가시킨 실험(단위 ms)은 이렇게 나왔다 — 단일 스레드 300, 락을 건 단일 스레드 10,000, 락 경합 두 스레드 224,000, CAS 단일 스레드 5,700, volatile 쓰기 4,700([LMAX Disruptor 기술 문서 Table 1](https://lmax-exchange.github.io/disruptor/disruptor.html)). 순서 보장은 공짜가 아니고, **경합이 붙는 순간 두 자릿수 배로 뛴다**는 것이 이 표의 요점이다.

## 10. 관측 — 새벽 3시에 열어볼 수 있는가

JVM의 실무 강점 중 절반은 성능이 아니라 이것이다. 프로세스가 살아 있는 채로 내부를 꺼낼 수 있고, 그 도구가 JDK에 기본 포함된다.

```bash
jcmd <pid> Thread.print -l          # 전체 스레드 스택 + java.util.concurrent 락 (Impact: Medium)
jcmd <pid> GC.heap_dump dump.hprof  # HPROF 힙 덤프 (Impact: High — 기본적으로 full GC를 요청한다)
jcmd <pid> JFR.start                # Flight Recorder 시작 (Impact: Low)
jcmd <pid> JFR.dump filename=r.jfr
```
([jcmd 레퍼런스](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html) — Impact 등급은 그 문서의 표기다)

셋의 성격이 다르다는 점이 중요하다.

- **스레드 덤프**는 "지금 이 순간 누가 어디서 멈춰 있나"의 스냅샷이다. 락 대기와 데드락(§9의 실패가 실제로 드러나는 자리)을 여기서 본다.
- **힙 덤프**는 "무엇이 메모리를 붙잡고 있나"의 스냅샷이다. Impact가 High이고 full GC를 유발하므로 **운영 중 아무 때나 뜨는 도구가 아니다.** 대신 사고 순간을 자동으로 잡는 방법이 있다 — `-XX:+HeapDumpOnOutOfMemoryError`("Enables the dumping of the Java heap to a file ... when a `java.lang.OutOfMemoryError` exception is thrown. ... By default, this option is disabled")와 `-XX:HeapDumpPath`([`java` 레퍼런스](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html)).
- **JFR**은 앞의 둘과 범주가 다르다. 스냅샷이 아니라 **사고 직전까지의 이벤트 기록**이다. JEP의 표현으로 "Events are stored in a single file that can be attached to bug reports and examined by support engineers, allowing after-the-fact analysis of issues in the period leading up to a problem."([JEP 328](https://openjdk.org/jeps/328))

JFR을 상시 켤 수 있는가가 실무의 갈림길인데, JEP 328의 성공 기준이 그 답이다 — "At most 1% performance overhead out-of-the-box on SPECjbb2015" / "No measurable performance overhead when not enabled". 다만 같은 문서의 비목표에 "Enable data collection by default"가 있으므로 **명시적으로 켜야 한다**(`-XX:StartFlightRecording`). 이 프로젝트처럼 관측 스택을 나중으로 미룬 시스템에서(ADR-023) JVM 기본 도구가 갖는 값은 여기에 있다 — 외부 도구 없이도 사후 분석의 최소선이 런타임에 들어 있다. [실무 의견]

## 11. 비용의 정직한 목록 — 기동·상주 메모리·워밍업·튜닝 표면

JEP 483이 이 청구서를 스스로 요약한다. "All this dynamism comes at a price, however, which must be paid every time an application starts."

**기동.** JVM은 시작할 때 "scans hundreds of JAR files on disk and reads and parses thousands of class files into memory", 로드·링크·검증·해소를 하고, 정적 초기화자를 실행한다. 프레임워크가 있으면 더 늘어난다 — "if the application uses a framework, e.g., the Spring Framework, then the framework's startup-time discovery of `@Bean`, `@Configuration`, and related annotations will trigger yet more work." 구체적 수치로, Spring PetClinic 3.2.0은 기동에 약 21,000개 클래스를 로드·링크하며 JDK 23에서 4.486초가 걸렸다(같은 JEP의 AOT 캐시 사용 시 JDK 24에서 2.604초, 캐시 크기 130MB).

**워밍업.** §6의 ②다. 정점 성능에 도달하기 전 구간이 존재하며, 이를 줄이려는 것이 [JEP 515](https://openjdk.org/jeps/515)(AOT 메서드 프로파일)와 [Project CRaC](https://openjdk.org/projects/crac/)(체크포인트/복원)의 동기다. JEP 515의 예시는 짧은 프로그램에서 90ms → 73ms(19% 개선)였다 — **짧은 프로그램에서는 개선폭도 짧다**는 점까지 그 문서가 밝히고 있다.

**상주 메모리.** 힙만이 아니다. 기본값들을 모아 보면 성격이 드러난다([`java` 레퍼런스](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html)).

| 항목 | 기본값 | 성격 |
|---|---|---|
| 힙 최대 (`-XX:MaxRAMPercentage`) | 가용 메모리의 25% | 컨테이너 메모리 한도와 따로 논다 — 명시 설정이 사실상 필수 |
| 코드 캐시 (`-XX:ReservedCodeCacheSize`) | 240MB (티어드 끄면 48MB) | JIT 산출물이 사는 곳 — 힙 밖 |
| 메타스페이스 (`-XX:MaxMetaspaceSize`) | 제한 없음 | 클래스 메타데이터 — 네이티브 메모리 |
| 스레드 스택 (`-Xss`) | Linux/x64 1024KB | 스레드 수 × 이 값이 그대로 상주 비용 |

"JVM 메모리 = 힙"이라고 생각하면 컨테이너에서 OOM Killer에게 죽는다. 코드 캐시·메타스페이스·스레드 스택은 전부 힙 밖이고, 기본 힙이 가용 메모리의 25%인 것도 그래서다. [실무 의견] 규모 감각으로는 §6의 벤치마크가 그대로 쓸 만하다 — 같은 계산을 하는 n-body에서 C++ 구현이 약 2.5MB를 쓸 때 JVM 구현은 약 61MB를 썼다. **하는 일이 작아도 런타임은 작아지지 않는다**는 것이 이 비용의 성질이다.

**튜닝 표면.** 위 표 자체가 비용이다. `java` 레퍼런스의 `-XX` 옵션 수는 사람이 다 아는 규모가 아니고, 이는 "기본값으로 잘 도는데 한계에 부딪히면 알아야 할 것이 갑자기 많아진다"는 형태로 청구된다.

이 넷을 합치면 JVM이 **틀리는 자리**가 정확히 보인다 — 호출마다 새로 뜨는 짧은 프로세스, 메모리가 귀한 다수의 작은 데몬, 배포처에 런타임을 깔기 어려운 환경. 이 프로젝트가 인프라 도구를 Go로 간 근거가 그것이다(판단 정본: ADR-028 L-2).

## 12. [실무 의견] 은행이 JVM에 수렴한 자리, 그리고 어긋나는 자리

이하는 공개 1차 출처로 전부 뒷받침되지 않는 해석이다. 위 절들과 구분해서 읽어야 한다.

**수렴의 이유는 "빨라서"가 아니다.** 은행 코어의 지배 항은 CPU가 아니라 DB 왕복과 락 대기다(이 프로젝트 기준: ADR-013의 시간 예산). 그러면 언어 선택의 축은 성능이 아니라 **실패 모드**로 옮겨간다. 은행에서 최악은 크래시가 아니라 **틀린 값으로 조용히 계속 도는 것**인데, §1에서 본 메모리 비안전 언어의 결함이 만드는 것이 정확히 그 계급이다. GC 언어에는 이 계급 자체가 없다.

**두 번째 이유는 앞 절 그대로다.** 터졌을 때 열어볼 수 있는가(§10). 25년치의 JDBC·트랜잭션·커넥션 풀·TLS 스택이 이 도메인에서 두들겨 맞으며 실패 모드가 문서화되어 있다는 것이, 새 런타임의 이론적 우월함보다 실무에서 자주 이긴다. "안정적"의 정직한 번역은 **"터지는 방식이 예측 가능하고 열어볼 도구가 있다"**에 가깝다.

**세 번째는 GC 반론이 실제로 소멸했다는 점이다.** "JVM은 GC 때문에 금융에 못 쓴다"는 오래된 반론인데, §8의 수치가 그 반론의 전제(수백 ms 일시정지)를 무너뜨린다. 다만 소멸한 것은 **반론**이지 **비용**이 아니다. ZGC는 일시정지를 처리량으로 샀고(JEP 333의 15% 목표), 저지연을 진지하게 추구하는 금융 코드는 여전히 GC를 회피하는 설계를 한다 — LMAX Disruptor가 링 버퍼를 기동 시 전부 선할당하는 이유가 그것이다. "All memory for the ring buffer is pre-allocated on start up. ... This pre-allocation of entries eliminates issues in languages that support garbage collection, since the entries will be re-used and live for the duration of the Disruptor instance."([LMAX Disruptor](https://lmax-exchange.github.io/disruptor/disruptor.html)) 금융 거래소를 JVM 위에 짓되 **할당을 안 하는 방식으로** 짓는다는 것 — 이것이 실무의 실제 형태다.

**어긋나는 자리는 §11이 이미 열거했다.** 그리고 그 경계는 은행 시스템 안에도 있다. 코어는 한 번 떠서 몇 주를 도니 기동·워밍업이 상각되지만, 배포·감시 도구는 호출마다 뜨므로 같은 성질이 그대로 손해가 된다. 하나의 시스템 안에서도 층마다 답이 다르다는 것이 요점이다.

## 13. 정리 — 하나의 결정에서 갈라져 나온 것들

이 문서가 다룬 것들은 서로 다른 기능이 아니라 §2의 한 결정이 만든 결과다. 바이트코드는 기계를 실행 시점에 정하려고, 클래스로더는 무엇을 읽을지를 실행 시점에 정하려고, JIT는 어떻게 최적화할지를 실행 시점에 정하려고, GC는 언제 해제할지를 실행 시점에 정하려고 있다. 청구서도 같은 뿌리에서 나온다 — 실행 시점에 정하려면 **실행 시점에 그 판단을 할 런타임이 상주해야 하고**(메모리), **판단할 정보를 모을 시간이 필요하며**(워밍업), **판단 자체가 매번 처음부터 시작한다**(기동).

그래서 JVM이 값을 내는 조건은 한 문장으로 줄어든다 — **오래 살아서 그 판단 비용을 상각할 수 있는가.** 은행 코어는 그 조건을 만족하고, 배포 스크립트는 만족하지 않는다.

이 프로젝트가 그 판단으로 서비스 레이어를 Kotlin/JVM으로, 인프라 레이어를 Go로 갈랐다(정본: [ADR-028](../../../architecture/adr/ADR-028-language-selection.md) — 재판정은 그 문서에서 한다). 같은 디렉토리의 다음 문서들이 각 언어를 같은 축으로 다룬다.
