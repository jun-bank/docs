# Rust — 소유권 모델의 동작 방식과 그 보증의 대가

> 학습 노트다. 결정의 근거가 될 수 없다(이 프로젝트의 언어 제약 정본: [`architecture/constraints.md`](../../../architecture/constraints.md) C-05 · 저수준 도구 언어 판정 정본: [`operations/infrastructure.md`](../../../operations/infrastructure.md) §4).

이 문서는 Rust의 소유권 모델을 개념부터 설명하고, 그 모델이 무엇을 보증하며 그 보증에 얼마를 청구하는지까지 간다. 순서는 하나의 논리를 따른다 — 무엇이 문제였나, 그 문제를 어떤 아이디어로 풀었나, 그 아이디어가 필연적으로 만드는 비용은 무엇이고 어디서 그 비용이 회수되나. 차용 검사기·수명·`Send`/`Sync`·제로 코스트 추상은 각각의 기능이 아니라 **"값마다 소유자를 하나만 두고 그 사실을 컴파일러가 추적한다"는 하나의 결정에서 갈라져 나온 결과**로 읽는 것이 이해가 빠르다. 인용한 문장은 The Rust Programming Language(현행 판)·Rustonomicon·표준 라이브러리 문서 기준이고, 컴파일 오류 출력은 rustc 1.92.0에서 재현한 것이다.

## 0. 왜 이 언어가 생겼나 · 무엇을 지향하나

**생긴 계기.** Rust는 2006년 모질라에서 일하던 프로그래머 Graydon Hoare의 개인 프로젝트로 시작했다. 널리 인용되는 계기는 사소하다 — 밴쿠버의 자기 아파트에 돌아왔더니 엘리베이터가 소프트웨어가 죽어 멈춰 서 있었고, "이런 기반 소프트웨어가 왜 아직도 이렇게 잘 죽는가"가 출발점이었다([How Rust went from a side project to the world's most-loved programming language](https://www.technologyreview.com/2023/02/14/1067869/rust-worlds-fastest-growing-programming-language/), MIT Technology Review, 2023). 문제의 배경은 이 문서 §1이 수치로 보이는 것 — C/C++로 쓰인 브라우저·커널 같은 대형 시스템에서 메모리 안전 결함이 심각한 취약점의 지배적 계급이라는 사실이었다. 2009년 모질라가 이 프로젝트를 공식 후원하기 시작한 이유가 정확히 그 자리에 있었다 — 차세대 브라우저 엔진을 안전하게 짤 언어가 필요했고, "가비지 컬렉터를 얹지 않고도 안전하게"가 처음부터 조건이었다(같은 글).

**간략한 흐름.** 언어의 지향을 이해하는 데 필요한 이정표만 시간순으로 든다(완전한 연표가 아니라 관련된 것만이다).

- **2006** — Graydon Hoare가 개인 프로젝트로 착수([MIT Technology Review](https://www.technologyreview.com/2023/02/14/1067869/rust-worlds-fastest-growing-programming-language/), 2023).
- **2009** — 모질라가 공식 후원을 시작 — 브라우저 엔진용 안전 언어라는 목적이 이때 붙는다(같은 글).
- **2015-05-15** — 1.0 릴리스. 이때부터 하위 호환 안정성 보증(stable)이 시작된다([Announcing Rust 1.0](https://blog.rust-lang.org/2015/05/15/Rust-1.0.html), 2015 — 이 날짜는 10주년 릴리스 노트가 "정확히 Rust 1.0의 10주년"이라 적어 재확인된다, [Rust 1.87.0](https://blog.rust-lang.org/2025/05/15/Rust-1.87.0/)).
- **2016** — 모질라가 Rust로 만든 브라우저 엔진 Servo를 공개([MIT Technology Review](https://www.technologyreview.com/2023/02/14/1067869/rust-worlds-fastest-growing-programming-language/), 2023). 지향이 대형 시스템에서 실제로 값을 낸 자리이고, §8에서 다룰 Quantum CSS(Stylo)가 이 계열이다.
- **2018년 말** — 2018 에디션(1.31)에서 비렉시컬 수명(NLL)이 안정화된다 — §3에서 볼 RFC 2094가 이때 기본 동작이 된다(2015 에디션까지 확장은 1.36, 완전 기본화는 2022년, [NLL by default](https://blog.rust-lang.org/2022/08/05/nll-by-default.html)).
- **2021-02-08** — Rust Foundation 설립. 2020년 모질라 정리해고 뒤, AWS·구글·화웨이·마이크로소프트·모질라가 함께 세워 언어의 관리 주체가 특정 회사에서 독립 재단으로 옮겨간다([Mozilla Welcomes the Rust Foundation](https://blog.mozilla.org/en/mozilla/mozilla-welcomes-the-rust-foundation/), 2021).

**지향점.** Rust가 내건 것은 네 가지로 요약된다. 첫째, GC 없는 메모리 안전 — §1이 말하는 "런타임에 아무것도 두지 않고 컴파일 타임 검사만으로 같은 보증"이다. 둘째, 데이터 레이스를 실행이 아니라 컴파일에서 막는 것(§5). 셋째, 제로 코스트 추상 — 안전과 고수준 표현을 런타임 비용 없이 얻는 것(§6). 넷째, 이 셋을 묶은 표어가 공식 Book 16장의 제목 그대로 "두려움 없는 동시성(Fearless Concurrency)"이다([Book ch.16](https://doc.rust-lang.org/book/ch16-00-concurrency.html)) — 동시성 코드를 "돌려 보고 레이스를 디버깅한다"가 아니라 "컴파일되면 레이스가 없다"로 바꾸겠다는 목표다.

**세 언어군의 자리 — 그리고 그 대가.** 이 지향들은 안전을 한 축이 아니라 두 축(메모리 안전 · 데이터 레이스 없음)으로 보고, 각 언어가 그 두 축을 어디서 사느냐로 갈린다 — C++는 어느 축도 언어가 보장하지 않고 개발자 규율에 맡기며(비안전이 사양), Go·JVM·C#은 런타임 GC로 메모리 안전 축을 사되 데이터 레이스 축은 여전히 프로그래머에게 열어 두고, Rust는 두 축을 다 컴파일 타임에 잠근다. 그래서 Rust는 C++에 대한 반작용이다 — 같은 무런타임 제어를 유지하되 그 제어를 안전하게 만든다. 이 대비의 정밀판이 §9이고, 각 언어가 안전을 어느 통화로 지불하는지가 그 절의 요점이다.

공짜는 아니다. GC 언어가 안전을 런타임 자원(메모리·CPU·정지)으로 내는 자리에서, Rust는 같은 안전을 사람의 시간 — 소유권·수명을 배우는 학습 곡선과 매 빌드의 컴파일 시간 — 으로 낸다. 이 청구서가 §7이고, 학습 곡선과 컴파일 시간은 결함이 아니라 "GC 없는 안전"이라는 지향의 필연적 대가다. 이 문서 전체가 그 하나의 교환 — 무엇을 보증하고 그 보증을 어느 통화로 지불하는가 — 을 절마다 되짚는다.

## 1. 문제 — 두 가지 해법을 동시에 거부한다

메모리 안전 결함은 대규모 C/C++ 코드베이스의 지배적 취약점 계급이다. 미국·영국·호주 등 7개국 보안 기관이 공동 발표한 문서가 네 측정을 한자리에 모아 놓았다 — "마이크로소프트 CVE의 약 70%가 메모리 안전 취약점이고(2006~2018년 CVE 기준), 구글 Chromium 프로젝트에서 식별된 취약점의 약 70%가 메모리 안전 취약점이며, Mozilla 취약점 분석에서 치명·고위험 버그 34건 중 32건이 메모리 안전 취약점이었고, 구글 Project Zero 분석에서 2021년 제로데이의 67%가 메모리 안전 취약점이었다"([The Case for Memory Safe Roadmaps](http://web.archive.org/web/2024id_/https://media.defense.gov/2023/Dec/06/2003352724/-1/-1/0/THE-CASE-FOR-MEMORY-SAFE-ROADMAPS-TLP-CLEAR.PDF), CISA·NSA·FBI 외, 2023).

이 수치를 인용할 때 붙는 한정어가 중요하다. 백악관 ONCD 보고서의 표현은 "엄격한 코드 리뷰와 다른 예방·탐지 통제에도 불구하고, **메모리 비안전 언어에서** 패치되고 CVE가 배정된 보안 취약점의 **최대** 70%가 메모리 안전 문제 때문"이다([Back to the Building Blocks](https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/02/Final-ONCD-Technical-Report.pdf), 2024). Chromium의 수치도 전체 버그가 아니라 "2015년 이후 Stable 채널의 고위험·치명 보안 버그 912건" 기준이며, 그중 절반이 use-after-free다([Chromium Memory safety](https://www.chromium.org/Home/chromium-security/memory-safety/)). 즉 "모든 소프트웨어 취약점의 70%"가 아니라 **"메모리 비안전 언어로 쓰인 대규모 코드베이스에서 심각한 취약점의 약 70%"**가 정확한 진술이다.

마이크로소프트가 이 통계를 발표하며 덧붙인 한 문장이 문제의 성격을 말해 준다 — "이것은 집중적인 코드 리뷰, 교육, 정적 분석을 포함한 완화책들에도 **불구하고** 그렇다"([We need a safer systems programming language](http://web.archive.org/web/2019id_/https://msrc-blog.microsoft.com/2019/07/18/we-need-a-safer-systems-programming-language/), MSRC, 2019). 규율과 도구를 더 투입해서 해결되는 문제가 아니었다는 뜻이다.

이 문제의 기존 해법은 하나였다. 런타임에 가비지 컬렉터를 두고 메모리 해제 시점을 사람에게서 빼앗는 것 — Java, Go, C#이 그렇게 했고 실제로 성공했다. Rust는 이 해법을 거부한다. 커널·드라이버·임베디드·지연 민감 서비스처럼 런타임을 얹을 수 없거나 얹기 싫은 자리가 남기 때문이다. 그래서 Rust의 질문은 이렇게 좁혀진다 — **런타임에 아무것도 두지 않고, 컴파일 타임의 검사만으로 같은 보증을 낼 수 있는가.**

## 2. 소유권 — 값마다 소유자를 하나만 둔다

그 검사를 가능하게 하는 최소 규칙이 소유권이고, 공식 문서가 세 줄로 규정한다 — "Rust의 각 값은 소유자를 갖는다. 한 번에 오직 하나의 소유자만 있을 수 있다. 소유자가 스코프를 벗어나면 값은 버려진다(dropped)"([The Rust Programming Language ch.4.1](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)). 세 번째 줄이 해제 시점을 결정한다. 스코프 끝에서 컴파일러가 `drop` 호출을 삽입하므로, 해제는 자동이되 **그 시점이 컴파일 타임에 확정된다** — GC처럼 런타임이 결정하지 않는다.

두 번째 줄이 double free를 막는다. Book의 설명이 직접적이다 — "`s2`와 `s1`이 스코프를 벗어날 때 둘 다 같은 메모리를 해제하려 할 것이다. 이것이 double free 오류이고 메모리 안전 버그 중 하나다. (…) 메모리 안전을 보장하기 위해, `let s2 = s1;` 다음부터 Rust는 `s1`을 더 이상 유효하지 않은 것으로 간주한다." 대입은 복사가 아니라 **이동(move)** 이고, 이동하고 나면 원래 이름은 죽는다.

```rust
let s1 = String::from("hello");
let s2 = s1;            // 이동 — s1은 여기서 무효가 된다
println!("{s1}");       // 컴파일 거부
```

```
error[E0382]: borrow of moved value: `s1`
  |
2 |     let s1 = String::from("hello");
  |         -- move occurs because `s1` has type `String`, which does not implement the `Copy` trait
3 |     let s2 = s1;
  |              -- value moved here
4 |     println!("{s1}, world!");
  |                ^^ value borrowed here after move
```

여기서 이미 이 설계의 성질이 드러난다. 런타임 검사가 아니라 **타입 검사**다. `s1`이 무효라는 사실은 실행해 봐야 아는 것이 아니라 컴파일러가 소유권 이동을 추적해서 아는 것이고, 그래서 비용이 실행 시점에 남지 않는다. 대신 비용은 다른 곳으로 옮겨간다 — 값을 여러 곳에서 쓰고 싶을 때마다 "누가 소유자인가"를 사람이 결정해야 한다.

## 3. 차용 — 별칭과 변경을 동시에 주지 않는다

소유권만으로는 쓸 수 있는 프로그램이 너무 적다. 함수에 값을 넘길 때마다 소유권이 넘어가면 돌려받는 코드를 계속 써야 한다. 그래서 소유권을 넘기지 않고 참조만 빌려주는 장치가 차용이고, 여기에 규칙 두 줄이 붙는다 — "어느 시점에든 하나의 가변 참조 **또는** 임의 개수의 불변 참조를 가질 수 있다. 참조는 항상 유효해야 한다"([Book ch.4.2](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)).

첫 줄이 이 언어의 중심 규칙이다. 별칭(aliasing)과 변경(mutation)을 동시에 허용하지 않는다는 뜻이며, 이것 하나가 뒤에 나오는 보증 대부분의 뿌리다. 왜 이 조합이 위험한지는 Book이 데이터 레이스의 세 조건으로 설명한다 — "둘 이상의 포인터가 같은 데이터에 동시에 접근한다 · 그중 최소 하나가 쓰기에 쓰인다 · 접근을 동기화하는 장치가 없다". 차용 규칙은 앞의 두 조건을 **단일 스레드에서도** 금지한다.

무엇이 거부되는지 두 실례로 본다. 가변 참조를 두 개 만들면 E0499다.

```rust
let mut s = String::from("hello");
let r1 = &mut s;
let r2 = &mut s;
println!("{r1}, {r2}");
```

```
error[E0499]: cannot borrow `s` as mutable more than once at a time
  |
3 |     let r1 = &mut s;
  |              ------ first mutable borrow occurs here
4 |     let r2 = &mut s;
  |              ^^^^^^ second mutable borrow occurs here
5 |     println!("{r1}, {r2}");
  |                -- first borrow later used here
```

불변 참조가 살아 있는 동안 가변 참조를 만들면 E0502다.

```rust
let mut s = String::from("hello");
let r1 = &s;
let r3 = &mut s;
println!("{r1}, {r3}");
```

```
error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable
  |
3 |     let r1 = &s;
  |              -- immutable borrow occurs here
5 |     let r3 = &mut s;
  |              ^^^^^^ mutable borrow occurs here
6 |     println!("{r1}, {r3}");
  |                -- immutable borrow later used here
```

이 규칙이 처음에 답답한 이유는 규칙 자체가 아니라 **범위**였다. 초기 Rust는 참조의 수명을 렉시컬 스코프로 계산해서, 참조를 변수에 담는 순간 그 수명이 블록 끝까지 늘어났다. RFC 2094(Non-Lexical Lifetimes)가 이것을 제어 흐름 그래프 기반으로 바꿨다 — "새 제안에서 참조의 수명은 그 참조가 이후에 사용될 수 있는 함수 구간에만 걸친다"([RFC 2094](https://github.com/rust-lang/rfcs/blob/master/text/2094-nll.md)). 아래 코드는 NLL 이전에는 거부됐고 지금은 통과한다.

```rust
let mut data = vec!['a', 'b', 'c'];
let slice = &mut data[..];
capitalize(slice);
data.push('d');     // NLL 이전: E0502. 현재: 통과 — slice가 더 이상 쓰이지 않는다
```

다만 RFC가 다룬 세 사례가 전부 해결된 것은 아니다. 함수 경계를 넘는 조건부 제어 흐름(RFC의 problem case #3 — `match map.get_mut(&key)`의 `None` 갈래에서 같은 맵에 삽입하고 참조를 반환하는 형태)은 rustc 1.92에서도 여전히 E0499로 거부된다. 그 사례는 후속 작업인 Polonius의 대상이고 아직 stable에 없다. **차용 검사기는 "안전한 프로그램을 전부 통과시킨다"가 아니라 "안전하지 않은 프로그램을 전부 막는다"를 보증한다** — 방향이 한쪽이며, 그 비대칭이 뒤의 §7에서 비용으로 돌아온다.

## 4. 수명 — 참조는 대상보다 오래 살 수 없다

차용 규칙의 둘째 줄("참조는 항상 유효해야 한다")을 강제하는 장치가 수명이다. Book의 정의는 "수명은 우리가 이미 써 온 또 다른 종류의 제네릭이다. 타입이 원하는 동작을 갖도록 보장하는 대신, 수명은 **참조가 우리에게 필요한 기간만큼 유효하도록** 보장한다"이다([Book ch.10.3](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)). 대부분의 수명은 추론되고, 참조들의 수명 관계가 여러 가지로 해석될 수 있을 때만 사람이 적는다.

이 검사가 잡는 것이 dangling reference다.

```rust
let r;
{
    let x = 5;
    r = &x;
}
println!("r: {r}");
```

```
error[E0597]: `x` does not live long enough
  |
4 |         let x = 5;
  |             - binding `x` declared here
5 |         r = &x;
  |             ^^ borrowed value does not live long enough
6 |     }
  |     - `x` dropped here while still borrowed
7 |     println!("r: {r}");
  |                   - borrow later used here
```

C에서 이 코드는 컴파일되고 실행되며 대체로 그럴듯한 값을 출력하다가 언젠가 다른 곳에서 터진다. Rust에서는 링크 단계에 가지도 못한다. **use-after-free를 런타임에 탐지하는 것이 아니라 그런 프로그램이 존재할 수 없게 만드는 것** — 이것이 앞의 §1이 말한 "런타임에 아무것도 두지 않는다"의 실체다.

수명이 헷갈리는 지점은 용어에 있다. RFC 2094가 이것을 명시적으로 갈라 놓았다 — 참조의 **수명(lifetime)** 은 "그 참조가 사용되는 기간"이고, 값의 **스코프(scope)** 는 "그 값이 해제되기 전까지의 기간"이다. 검사기가 하는 일은 이 둘의 포함 관계 확인이고, 에러 메시지의 "does not live long enough"는 정확히 그 관계가 깨졌다는 말이다.

## 5. Send와 Sync — 데이터 레이스가 타입 오류가 되는 원리

여기가 소유권 모델이 가장 크게 값을 내는 자리다. 앞의 세 절은 전부 단일 스레드 이야기였는데, 그 규칙들이 스레드 경계에 그대로 적용되면 데이터 레이스가 사라진다. 필요한 추가 장치는 마커 트레이트 두 개뿐이다.

표준 라이브러리의 정의는 짧다. `Send`는 "스레드 경계를 넘어 이전될 수 있는 타입"이고([std::marker::Send](https://doc.rust-lang.org/std/marker/trait.Send.html)), `Sync`는 "스레드 간에 참조를 공유해도 안전한 타입"이다([std::marker::Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html)). 둘의 관계는 한 줄로 정의된다 — "정확한 정의는 이렇다: 타입 `T`가 `Sync`인 것은 `&T`가 `Send`인 것과 필요충분이다. 다시 말해 `&T` 참조를 스레드 간에 넘길 때 (데이터 레이스를 포함한) 미정의 동작 가능성이 없다는 뜻이다."

핵심은 이것이 **자동 트레이트**라는 점이다. Rustonomicon의 설명이 정확하다 — "`Send`와 `Sync`는 자동으로 파생되는 트레이트이기도 하다. 다른 모든 트레이트와 달리, 어떤 타입이 전부 `Send`이거나 `Sync`인 타입들로만 구성되어 있다면 그 타입도 `Send`이거나 `Sync`다"([Rustonomicon: Send and Sync](https://doc.rust-lang.org/nomicon/send-and-sync.html)). 즉 개발자가 스레드 안전성을 선언하는 것이 아니라, **구성 요소로부터 컴파일러가 계산한다.** 안전하지 않은 조각 하나가 들어가면 그것을 담은 구조체 전체가 자동으로 스레드 간 이동 불가가 된다.

실제로 거부되는 장면이 이 원리를 가장 잘 보여 준다. `Rc<T>`는 참조 카운트를 원자적으로 갱신하지 않으므로 `!Send`다.

```rust
let counter = Rc::new(5);
thread::spawn(move || {
    println!("{}", counter);
});
```

```
error[E0277]: `Rc<i32>` cannot be sent between threads safely
  |
  = help: within `{closure@...}`, the trait `Send` is not implemented for `Rc<i32>`
note: required by a bound in `spawn`
```

`RefCell<T>`는 동기화 없이 내부 가변성을 제공하므로 `!Sync`이고, `Arc`로 감싸도 통과하지 못한다.

```rust
let data = Arc::new(RefCell::new(0));
let d = Arc::clone(&data);
thread::spawn(move || { *d.borrow_mut() += 1; });
```

```
error[E0277]: `RefCell<i32>` cannot be shared between threads safely
  |
  = help: the trait `Sync` is not implemented for `RefCell<i32>`
  = note: if you want to do aliasing and mutation between multiple threads, use `std::sync::RwLock` instead
  = note: required for `Arc<RefCell<i32>>` to implement `Send`
```

마지막 `note` 한 줄이 규칙의 실전 구현이다. `RefCell`이 `Sync`가 아니어서 `Arc<RefCell<i32>>`가 `Send`가 아니게 되고, 그래서 `spawn`의 경계 조건에 걸린다 — "`&T`가 `Send`인 것은 `T`가 `Sync`인 것과 필요충분"이라는 정의가 에러 메시지로 그대로 나온 것이다. 그리고 컴파일러는 대안까지 알려 준다(`RwLock`을 쓰라).

주장의 범위는 정확히 봐야 한다. Book은 "소유권과 타입 검사를 활용해서, **많은** 동시성 오류가 런타임 오류가 아니라 컴파일 타임 오류가 된다"고 쓴다 — "모든"이 아니다([Book ch.16](https://doc.rust-lang.org/book/ch16-00-concurrency.html)). 못 막는 것을 Book이 직접 밝힌다 — "`Mutex<T>`를 쓸 때 Rust가 모든 종류의 논리 오류로부터 당신을 보호해 주지는 못한다. (…) `Mutex<T>`에는 **데드락**을 만들 위험이 따른다"(ch.16.3). 정리하면 **데이터 레이스(위 3조건의 정확한 정의)와 use-after-free·double free·dangling reference는 컴파일 타임에 막고, 데드락·참조 순환으로 인한 누수·순서 의존 논리 버그는 막지 못한다.**

경계도 하나 있다. `unsafe`는 이 검사들을 끄지 않는다 — "`unsafe`가 차용 검사기를 끄거나 Rust의 다른 안전성 검사를 비활성화하지 않는다는 점을 이해하는 것이 중요하다. unsafe 코드에서 참조를 쓰면 그것도 여전히 검사된다"([Book ch.20.1](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html)). `unsafe`가 여는 것은 원시 포인터 역참조·unsafe 함수 호출·가변 static 접근·unsafe 트레이트 구현·union 필드 접근 다섯 가지뿐이고, 나머지 규칙은 그대로다. 그래서 안전성 주장의 정확한 형태는 "Rust 프로그램은 안전하다"가 아니라 Rustonomicon이 쓴 대로 **"Safe Rust만 쓴다면 dangling pointer도, use-after-free도, 다른 어떤 미정의 동작도 겪지 않는다"**([Meet Safe and Unsafe](https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html))이며, `unsafe` 블록은 그 보증의 책임을 사람이 인수하는 표시다.

## 6. 제로 코스트 추상 — 무엇이 0이고 무엇이 0이 아닌가

앞 절들의 검사가 전부 컴파일 타임이라면, 남는 질문은 "그래서 실행 시점에는 정말 아무것도 안 남는가"다. 이 주장의 이름이 제로 코스트 추상이고, 출처는 Rust가 아니라 C++다. Book이 Stroustrup의 원칙을 그대로 인용한다 — "일반적으로 C++ 구현은 제로 오버헤드 원칙을 따른다: **쓰지 않는 것에는 비용을 내지 않는다. 그리고 나아가, 쓰는 것은 직접 손으로 짜도 그보다 나을 수 없다**"([Book ch.13.4](https://doc.rust-lang.org/book/ch13-04-performance.html)).

Book은 이 주장을 측정으로 뒷받침한다. 같은 검색 작업을 명시적 `for` 루프로 쓴 판과 반복자 체인으로 쓴 판을 벤치마크한 결과다.

```
test bench_search_for  ... bench:  19,620,300 ns/iter (+/- 915,700)
test bench_search_iter ... bench:  19,234,900 ns/iter (+/- 657,200)
```

고수준 추상 쪽이 오히려 근소하게 빨랐다. 결론 문장은 "반복자는 고수준 추상임에도, 당신이 저수준 코드를 직접 쓴 것과 대략 같은 코드로 컴파일된다. 반복자는 Rust의 제로 코스트 추상 중 하나이며, 이는 그 추상을 쓰는 것이 **추가적인 런타임 오버헤드를 부과하지 않는다**는 뜻이다"이고, 더 강한 주장도 붙는다 — "**많은 경우** 반복자를 쓴 Rust 코드는 손으로 쓸 어셈블리와 같은 것으로 컴파일된다. 루프 언롤링이나 배열 접근의 경계 검사 제거 같은 최적화가 적용되어 결과 코드가 극도로 효율적이 된다."

여기서 두 가지를 정확히 읽어야 한다. 첫째, **"많은 경우"는 하나가 아니라 전부가 아니라는 말이다.** 마지막 문장이 경계 검사 제거를 최적화의 성과로 꼽는다는 것은, 뒤집으면 최적화가 걷어내지 못한 자리에는 경계 검사가 남는다는 뜻이다. 둘째, 이 성질을 만드는 기계장치가 공짜가 아니다.

그 기계장치가 단형화(monomorphization)다. 제네릭을 타입마다 별도 기계어로 펼치기 때문에 가상 호출도 박싱도 없고, 그래서 런타임 비용이 0이 된다. 그런데 §7에서 볼 컴파일 시간 항목의 첫 번째 원인이 정확히 이것이다 — "Rust는 각 제네릭 인스턴스화를 자기만의 기계어로 번역하는데, 이는 **코드 비대(code bloat)를 만들고 컴파일 시간을 늘린다**"([The Rust Compilation Model Calamity](https://www.pingcap.com/blog/rust-compilation-model-calamity/)). 즉 **"제로 코스트"는 비용이 사라졌다는 뜻이 아니라 비용이 실행 시점에서 컴파일 시점과 바이너리 크기로 옮겨갔다는 뜻이다.** 이 문서 전체를 관통하는 형태가 여기서도 반복된다.

0이 아닌 자리도 몇 곳 분명하다. 트레이트 객체(`dyn Trait`)를 쓰면 동적 디스패치가 일어나므로 단형화의 이점이 사라지는데, 이것은 결함이 아니라 선택 사항이다 — 원칙의 앞 절("쓰지 않는 것에는 비용을 내지 않는다")대로 쓰겠다고 적었을 때만 낸다. 비동기도 마찬가지다. `async fn`이 만드는 상태 기계는 자기 참조 구조이므로 `Pin`이라는 별도 개념을 끌고 들어오고([std::pin](https://doc.rust-lang.org/std/pin/)), 이 복잡도는 런타임 비용은 아니지만 **인지 비용**으로 청구된다. 정리하면 제로 코스트 추상의 정확한 형태는 이렇다 — **런타임 비용은 실제로 0에 가깝고, 그 대가는 컴파일 시간·바이너리 크기·언어 복잡도로 전가된다.**

## 7. 청구서 — 학습 곡선·설계 반복·컴파일 시간

앞의 보증들은 공짜가 아니다. 대가는 세 자리에 청구되고, 세 항목의 성격이 서로 다르다 — 하나는 시간이 지나면 줄고, 하나는 설계할 때마다 다시 나오며, 하나는 매일 나온다.

**학습 곡선.** 가장 강한 근거는 설문이 아니라 대조 실험이다. Coblenz 등은 소유권을 GC로 우회하는 `Bronze` 수집기를 만들어 학생 428명을 무작위 배정했는데, 복잡한 별칭이 필요한 과제에서 GC를 쓴 집단은 약 4시간, Rust 소유권을 쓴 집단은 약 12시간이 걸렸다 — 약 3배다. 논문의 결론은 "소유권·차용·수명이 사용자가 Rust에서 겪는 어려움의 주된 원인이었다"이다([Garbage Collection Makes Rust Easier to Use, ICSE 2022](https://arxiv.org/abs/2110.01098)). 자기보고가 아니라 통제된 시험이라는 점에서 반박하기 어려운 수치다.

무엇이 특히 어려운지도 측정되어 있다. Stack Overflow 질문 15,509건과 Rust 프로그래머 101명을 조사한 연구에서, 컴파일러 에러를 "항상" 이해했다는 응답이 소유권 규칙 위반은 39.6%인 데 비해 **수명 규칙 위반은 10.0%**였다([Learning and Programming Challenges of Rust, ICSE 2022](https://songlh.github.io/paper/survey.pdf)). 진짜 벽은 소유권이 아니라 수명이라는 뜻이고, 이는 §4에서 본 "수명과 스코프는 다른 것"이라는 구분이 실제로 잘 안 잡힌다는 이야기와 같다. 같은 논문이 통념 하나는 반박한다 — 안전 규칙 위반의 **91.8%가 safe 코드로 수정된다.** "결국 `unsafe`로 도망치게 된다"는 것은 데이터가 지지하지 않는다.

**설계 반복 비용.** 소유권은 코드 스타일이 아니라 **자료구조 설계를 제약한다.** 연결 리스트를 다루는 유명한 튜토리얼이 이 성질을 그대로 보여 준다 — 첫 시도는 `recursive type has infinite size`로 막히고, 책은 `Box` → `Rc` → `Arc` → 원시 포인터 `unsafe` 순으로 올라가며 소유권 우회 도구를 차례로 동원한다([Learn Rust With Entirely Too Many Linked Lists](https://rust-unofficial.github.io/too-many-lists/)). 그래프처럼 순환 참조가 본질인 구조에서는 Rust 언어팀 리드 Niko Matsakis가 직접 인덱스 기반 표현을 권한다 — "인덱스는 복잡한 자료구조를 표현하는 간결하고 편리한 방법인 경우가 많고, 멀티스레드 코드나 소유권과 잘 어울린다"([Modeling graphs in Rust using vector indices](https://smallcultfollowing.com/babysteps/blog/2015/04/06/modeling-graphs-in-rust-using-vector-indices/)).

이 비용이 특별한 이유는 **되돌리기 어려운 자리에 걸린다**는 점이다. 다른 언어에서 "일단 참조로 연결해 두고 나중에 정리한다"가 되는 것이, 여기서는 소유 구조를 먼저 정해야 컴파일이 되고, 그 결정이 틀리면 자료구조를 다시 짜야 한다. 자기 참조 구조체가 극단적 사례다 — 값이 이동하면 자기 자신을 가리키던 포인터가 옛 주소를 가리켜 무효가 되는데, Rust는 "값이 이동했다는 사실을 그 값에게 알려 주지 않기" 때문에 `Pin`이라는 별도 장치가 필요하다([std::pin](https://doc.rust-lang.org/std/pin/)). 그리고 이건 특수한 사정이 아니다 — 같은 문서가 밝히듯 "그런 자기 참조 타입의 핵심 예가 `async fn`의 `Future`를 구현하기 위해 컴파일러가 생성하는 상태 기계"이므로, 비동기를 쓰는 순간 누구나 간접적으로 이 문제에 닿는다.

**컴파일 시간.** 이건 Rust 팀 스스로 인정하는 항목이다. 3,700명 넘게 응답한 공식 컴파일러 성능 설문의 결론이 직설적이다 — "많은 사람이 그렇게 운이 좋지는 않다는 것이 분명하며, Rust의 빌드 성능이 그들의 생산성을 제약한다"([Rust compiler performance survey 2025](https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/)). 같은 설문에서 응답자의 **55%가 재빌드에 10초 넘게 기다린다**고 답했고, 더 무거운 사실은 이것이다 — **"Rust를 더 이상 쓰지 않는다고 답한 응답자의 약 45%가 그만둔 이유 중 하나로 긴 컴파일 시간을 들었다."**

느린 이유는 구조적이다. Rust 공동 창시자 중 한 명인 Brian Anderson이 정리한 목록이 정확하다 — 제네릭 인스턴스마다 별도 기계어를 만드는 단형화(monomorphization), 대량의 LLVM IR을 생성해 옵티마이저에게 지워 달라고 맡기는 관행, 크레이트 단위 코드 생성, trait coherence가 만드는 병렬화 제약이다. 그의 요약은 "Rust 프로그래밍 언어는 느린 컴파일 시간을 갖도록 설계되었다"이고, TiKV에서 전체 재빌드가 개발 모드 15분·릴리스 모드 30분 걸린 사례도 함께 적혀 있다([The Rust Compilation Model Calamity](https://www.pingcap.com/blog/rust-compilation-model-calamity/)).

개선은 진행 중이지만 자릿수가 바뀌지는 않았다. 병렬 프론트엔드는 `-Z threads=8`에서 최대 50% 단축이 나오지만 기본값이 아니고 데드락을 포함한 알려진 버그가 있으며 메모리 사용이 최대 35%까지 는다. 그리고 같은 글에 뼈아픈 자기 진단이 있다 — "이 시점에서 컴파일러는 이미 크게 최적화되어 있어 새로운 개선을 찾기 어렵다. **남아 있는 손쉬운 열매가 없다**"([Faster compilation with the parallel front-end](https://blog.rust-lang.org/2023/11/09/parallel-rustc/)). Cranelift 백엔드는 클린 빌드 총 컴파일 시간을 약 5% 줄이지만 "대부분의 대형 프로젝트가 한두 개의 미지원 기능에 걸려 쓸 수 없다"([2025H2 Cranelift 목표](https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html)).

**균형을 위한 반대 방향.** 이 청구서가 곧 "쓰지 말라"는 결론은 아니다. 공식 설문에서 "Rust가 도입 비용만큼의 값을 했다"는 응답이 64%(2023), "조직이 앞으로도 Rust를 쓸 것 같다"가 77%다([2023 Annual Rust Survey](https://blog.rust-lang.org/2024/02/19/2023-Rust-Annual-Survey-2023-results/)). 자기평가 "생산적" 비율은 42%(2022) → 47%(2023) → 53%(2024)로 꾸준히 올라간다([2024 State of Rust Survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/)). 구글은 "다른 어떤 언어에 비해서도 Rust에 생산성 페널티가 있다는 데이터를 보지 못했다"고 보고했고, 램프업 분포는 2개월 이내에 기여할 자신이 있다는 응답이 2/3 초과, 타 언어만큼 생산적이 되기까지는 2개월 이내 1/3·4개월 이내 50% 초과다([Rust fact vs. fiction](https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html)). 안드로이드에서는 하류 이득까지 실측됐다 — 중·대규모 변경의 롤백률이 C++ 대비 약 4배 낮고 코드 리뷰 시간이 약 25% 짧다([Rust in Android: move fast and fix things](https://blog.google/security/rust-in-android-move-fast-fix-things/)).

그래서 청구서의 정확한 형태는 "Rust는 비싸다"가 아니다. **초기에 크고 시간이 지나면 줄어드는 비용(학습)과, 설계할 때마다 다시 나오는 비용(자료구조), 그리고 매일 균일하게 나오는 비용(컴파일)이 섞여 있다.** 마지막 항목만 개선 속도가 느리다.

## 8. 회수되는 자리 — 런타임을 못 얹는 곳, 공유 상태를 병렬화하는 곳, 정지가 곧 위반인 곳

§7의 청구서를 내고도 남는 곳이 있다. 회수 조건은 셋이고, 셋 다 **"GC 언어를 쓰면 된다"가 답이 되지 않는다**는 공통점이 있다. 이 조건을 알아 두면 §10에서 우리 경우를 판정하기가 쉬워진다.

**조건 ① 런타임을 얹을 수 없다.** 커널이 대표다. 리눅스 커널의 Rust 코드는 표준 라이브러리를 링크하지 않고 `core`만 쓰며 `#![no_std]`가 강제된다([Linux kernel: Rust general information](https://docs.kernel.org/rust/general-information.html)). GC는 애초에 선택지가 아니고, 그렇다고 C를 계속 쓰면 §1의 CVE 계급을 계속 낸다. 이 자리에서 Rust는 "더 나은 선택지"가 아니라 **비어 있던 칸을 채우는 유일한 후보**다. 커널이 안전성을 관리하는 방식도 참고할 만하다 — `unsafe`를 드라이버에 흩뿌리지 않고 "커널 C API와의 모든 직접 상호작용을 신중히 리뷰되고 문서화된 추상으로 캡슐화"해서 한곳에 모으고, 잎 모듈인 드라이버는 그 안전한 추상만 쓴다. 임베디드도 같은 논리다 — 상주 런타임을 얹을 메모리가 없는 곳에서 메모리 안전을 얻는 방법이 정적 검사밖에 없다.

**조건 ② 공유 상태를 병렬화하는 것이 목표다.** 여기가 §5가 값을 내는 자리다. Mozilla가 Firefox의 CSS 스타일 계산 엔진을 Rust로 다시 쓴 이유가 정확히 이것이었고, 설명 문장이 짧고 분명하다 — "**Rust에서는 데이터 레이스가 없다는 것을 정적으로 검증할 수 있다. 컴파일러가 그렇게 하도록 두지 않는다**"([Inside a super fast CSS engine: Quantum CSS](https://hacks.mozilla.org/2017/08/inside-a-super-fast-css-engine-quantum-css-aka-stylo/)). 이 성질이 있으면 병렬화가 "해 보고 나중에 레이스를 디버깅한다"가 아니라 "컴파일되면 레이스가 없다"가 된다. 스타일 계산처럼 수많은 노드를 코어 수만큼 나눠 처리하는 작업에서 같은 글은 코어 수에 가까운 선형 가속을 목표로 제시한다(단, 그 배수는 측정치가 아니라 병렬화 목표로 제시된 값이다). **핵심은 속도가 아니라 시도 가능성이다** — 공유 가변 상태 위 병렬화는 다른 언어에서도 가능하지만, 정확성을 사후 테스트로만 확인할 수 있어서 손대기를 포기하게 되는 종류의 작업이다.

**조건 ③ GC 정지가 지연 목표를 직접 깬다.** Discord의 사례가 이 조건의 교과서다. Go로 쓴 서비스에서 "대략 **2분마다** 지연과 CPU 스파이크"가 났고, 원인은 힙이 자라지 않아도 "Go가 최소 2분마다 가비지 컬렉션을 강제로 돌리는" 데 있었다 — 수집기가 LRU 캐시 전체를 훑어 참조가 없는지 확인해야 했기 때문이다. 중요한 것은 **튜닝으로 해결되지 않았다**는 점이다 — "GC 퍼센트를 어떻게 설정해도 아무것도 바뀌지 않았다", 할당 속도가 충분히 빠르지 않아 주기를 당길 수도 없었고, 캐시를 줄이면 DB 부하가 올라 "99번째 백분위 지연이 더 나빠졌다". Rust로 옮긴 결과는 "**지연, CPU, 메모리 모든 성능 지표에서 Go를 이겼다**"였다([Why Discord is switching from Go to Rust](https://discord.com/blog/why-discord-is-switching-from-go-to-rust)).

세 사례 모두 자기 보고라는 점은 감안해야 하고, Discord 자신이 글 말미에 선을 그어 둔다 — "**분명히 해 두자면, 우리는 그냥 그러고 싶다는 이유로 모든 것을 Rust로 다시 써야 한다고 생각하지 않는다.**"

이 세 조건이 공유하는 형태가 있다. 어느 경우에도 대안이 "조금 느린 다른 언어"가 아니었다 — 커널·임베디드는 후보 자체가 없었고, 스타일 엔진은 병렬화를 포기하는 것이 대안이었으며, Discord는 튜닝 손잡이를 다 돌려 본 뒤였다. **§7의 청구서는 이렇게 대안이 막힌 자리에서만 상대적으로 싸 보인다.**

뒤집으면 회수되지 않는 조건도 그대로 나온다. 병목이 계산이 아니라 **대기**인 곳 — 네트워크 왕복과 DB 응답을 기다리는 I/O 바운드 서비스 — 에서는 실행 속도를 몇 배 올려도 총 지연이 거의 그대로다. GC 정지가 있어도 그것이 삼키는 시간이 지연 예산에 비해 무시할 만한 곳도 마찬가지다. 그리고 동시성이 스레드 사이 공유 메모리가 아니라 **DB 트랜잭션과 잠금**에 있는 곳에서는, §5가 컴파일 타임에 제거해 주는 결함 계급이 애초에 잘 나타나지 않는다.

회수 실패가 실제로 관측된 사례도 있다. Prisma는 ORM의 쿼리 엔진을 Rust에서 TypeScript로 **되돌렸는데**, 이유가 성능이 아니라 경계 비용이었다 — "쿼리 엔진에 기여하려면 Rust와 TypeScript 숙련을 겸해야 해서 커뮤니티 참여 기회가 줄어든다", "운영체제와 OpenSSL 라이브러리 버전마다 각자의 바이너리가 필요해 배포가 복잡해지고 개발이 느려진다", "현대 자바스크립트 런타임·서버리스·엣지 환경이 큰 Rust 바이너리와 늘 호환되지는 않는다"([From Rust to TypeScript](https://www.prisma.io/blog/from-rust-to-typescript-a-new-chapter-for-prisma-orm)). 되돌린 뒤 번들이 약 14 MB에서 1.6 MB로 줄고 일부 조회가 3배가량 빨라졌다고 보고했지만, 같은 글이 그 개선을 언어가 아니라 **언어 간 직렬화 오버헤드가 사라진 덕**으로 돌린다. 그래서 교훈은 *"TypeScript가 Rust보다 빠르다"* 가 아니라 **이질 언어 경계를 하나 세우는 비용이 그 언어의 이점을 삼킬 수 있다**는 것이고, 이 축은 §10에서 우리 경우에 그대로 걸린다.

## 9. 세 계급의 안전성 — 비용이 어디에 놓이는가

Rust를 다른 언어와 비교할 때 흔한 실수가 "안전한가 아닌가"를 한 축으로 보는 것이다. 축은 둘이고, 둘을 갈라야 각 언어가 무엇을 주고 무엇을 안 주는지가 보인다 — **메모리 안전**과 **데이터 레이스 없음**이다. GC는 첫째 축만 준다.

**C++ — 비안전이 사양이다.** 표준의 미정의 동작 정의는 "이 문서가 아무 요구사항도 부과하지 않는 동작"이고, 잘 정의된 프로그램에서 구현에 따라 달라질 뿐인 미명세 동작(unspecified behavior)과 명확히 구분된다([C++ 표준 초안 [defns.undefined]](https://timsong-cpp.github.io/cppwp/n4950/intro.defs)). 해제된 포인터 역참조, 범위 밖 접근, 데이터 레이스가 모두 이 계급에 들어간다. 즉 안전성 비용은 **전적으로 개발자 규율에 놓인다.**

도구로 메꾸는 것에는 성질상의 한계가 있다. AddressSanitizer는 힙·스택·전역의 범위 밖 접근, use-after-free, use-after-return, use-after-scope, double free를 잡지만, 스스로 밝히듯 "컴파일러 계측 모듈과 **런타임 라이브러리**로 구성"되고 "일반적인 슬로다운은 **2배**"다([AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)). 실행된 경로에서 실제로 발생한 것만 잡는 탐지이지 증명이 아니고, 2배 비용 때문에 상시 운영에 켤 수도 없다.

**Go·JVM — GC가 첫째 축을 준다. 둘째 축은 주지 않는다.** 이 부분이 가장 자주 오해된다. Go 메모리 모델은 데이터 레이스를 "`sync/atomic`의 원자적 접근이 아닌 한, 같은 메모리 위치에 대한 읽기나 쓰기와 동시에 일어나는 쓰기"로 정의하고, 대응을 프로그래머에게 넘긴다 — "여러 고루틴이 동시에 접근하는 데이터를 수정하는 프로그램은 그 접근을 직렬화해야 한다"([The Go Memory Model](https://go.dev/ref/mem)). 컴파일 오류가 아니다. Java도 같다. JLS는 "happens-before 관계로 순서가 정해지지 않은 충돌하는 두 접근을 포함하면 데이터 레이스를 포함한다고 말한다"(§17.4.5)고 정의하고, 그 결과를 "**잘못 동기화된 프로그램은 놀라운 동작을 보일 수 있다**", "코드에 데이터 레이스가 있으면 직관에 반하는 결과가 종종 가능하다"로 서술한다([JLS ch.17](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)).

다만 C++와의 차이는 실재한다. Go·Java의 레이스는 미정의 동작이 아니라 **정의된 범위 안의 이상한 값**이다 — 메모리가 깨지거나 임의 코드가 실행되지는 않는다. 그 대신 이 언어들이 제공하는 것은 탐지 도구이고, 그 도구도 런타임이다. Go의 race detector 공식 문서가 두 한계를 그대로 적는다 — "전형적인 프로그램에서 메모리 사용이 **5~10배**, 실행 시간이 **2~20배** 늘 수 있다", 그리고 "race detector는 런타임에 일어난 레이스만 찾으므로 실행되지 않은 코드 경로의 레이스는 찾지 못한다"([Data Race Detector](https://go.dev/doc/articles/race_detector)).

GC 자체의 비용도 감춰지지 않는다. Go의 공식 GC 가이드가 이것을 구조적 교환으로 못박는다 — "높은 수준에서 GOGC는 GC CPU와 메모리 사이의 교환을 결정한다", 그리고 "핵심은 이것이다: **GOGC를 두 배로 하면 힙 메모리 오버헤드가 두 배가 되고 GC CPU 비용은 대략 절반이 된다**"([A Guide to the Go GC](https://go.dev/doc/gc-guide)). 즉 GC를 쓰는 대가는 "가끔 멈춘다"가 아니라 **메모리와 CPU 사이의 상시 교환**이며, 어느 쪽으로 돌리든 하나는 낸다. 현대 수집기들이 정지 시간을 힙 크기에 비례하지 않게 만든 것은 사실이지만, 그것은 이 교환을 없앤 것이 아니라 정지 축을 개선한 것이다.

**Rust — 두 축을 컴파일 타임에 준다.** §2~§4가 첫째 축이고 §5가 둘째 축이다. Book의 표현대로 "소유권과 타입 검사를 활용해서 많은 동시성 오류가 런타임 오류가 아니라 컴파일 타임 오류가 된다". 비용은 런타임에 없는 대신 §7의 세 항목으로 옮겨가 있다.

아래 표는 앞 문단들에서 확인한 사실을 한 칸에 한 값으로 요약한 것이다. 근거는 위 서술에 있고 표는 기억을 되살리는 용도다.

| 축 | C++ | Go · JVM | Rust |
|---|---|---|---|
| 메모리 안전 보장 주체 | 없음(개발자 규율) | 런타임 GC | 컴파일러 |
| 해제 시점 결정 | 개발자 | 런타임 | 컴파일 타임 |
| use-after-free | 미정의 동작 | 구조적으로 불가 | 컴파일 거부 |
| 데이터 레이스의 지위 | 미정의 동작 | 정의되나 값이 어긋남 | 컴파일 거부 |
| 데이터 레이스 대응 수단 | 런타임 탐지기 | 런타임 탐지기 | 타입 검사 |
| 탐지기 오버헤드 | 약 2배(ASan) | 실행 2~20배(Go) | 해당 없음 |
| 상시 런타임 비용 | 없음 | 메모리·CPU 교환 | 없음 |
| 주된 비용의 위치 | 운영 중 사고 | 실행 자원 | 학습·설계·빌드 |
| 막지 못하는 것 | 대부분 | 데이터 레이스·데드락 | 데드락·논리 레이스 |

표의 마지막 줄이 이 절의 요점이다. **어느 쪽도 데드락과 논리적 순서 버그는 막지 못한다.** 세 언어의 차이는 "안전한가"가 아니라 **같은 안전을 사는 값을 어느 통화로 지불하는가**이며, C++는 운영 사고로, Go·JVM은 실행 자원으로, Rust는 사람의 시간으로 낸다.

## 10. 우리 릴레이에서는 왜 회수되지 않는가

이 절은 이 프로젝트의 기존 판정을 옮긴 것이다 — 정본은 [`constraints.md`](../../../architecture/constraints.md) C-05와 [`infrastructure.md`](../../../operations/infrastructure.md) §4이고, 여기서 재판정하지 않는다. 먼저 용어를 맞춰 둔다. 이 프로젝트의 이름은 "릴레이"이고, 하는 일은 코어 트랜잭션이 사실 갱신과 같은 커밋으로 `outbox`에 넣은 이벤트를 폴링해서 수신 배포에 전달하고 완료 표시하는 것이다. 브로커는 없다(정본: ADR-021 ET-1).

**첫째, 병목이 Rust가 이기는 축에 없다.** §8의 회수 사례들은 전부 CPU·GC 정지·메모리가 병목인 자리였다. 릴레이의 일은 DB 폴링 → 네트워크 호출 → 상태 전이이고, 이 프로젝트가 스스로 지목한 병목은 두 개다 — "**inbox API 호출이 릴레이 처리량의 병목이 된다**"(정본: ADR-021 R5)와 "outbox 폴링이 코어 DB 부하를 유의미하게 올린다"(정본: ADR-005 R1). 둘 다 언어를 바꿔서 줄어드는 항목이 아니다. 계산이 아니라 대기가 비용인 워크로드에서 실행 속도를 몇 배 올려도 총 지연은 거의 그대로다.

**둘째, 지연 보증이 릴레이에 걸려 있지 않다.** Discord가 Rust로 옮긴 이유는 GC 정지가 사용자 지연 목표를 직접 깼기 때문인데, 이 프로젝트에서 p99 3초 같은 응답 목표가 걸린 곳은 매입사 전문 수신부터 응답 송신까지의 **동기 승인 경로**이지 릴레이가 아니다(정본: QS-01·QS-02). 릴레이에 걸린 유일한 시한은 대사 배치 완료 1시간인데, 그 문서 자신이 "1시간은 [미검증] 자체 목표"이며 마감 기준 여유가 10시간이라고 적는다(정본: QS-04). 그리고 릴레이가 느려질 때의 결과가 무엇인지도 이미 정해져 있다 — 서킷이 열리면 "전달 중단, outbox에 쌓임(유실 없음)"이다(정본: ADR-013 §2.2). **밀리초가 아니라 시간 단위의 여유가 있고, 늦어짐이 장애가 아니라 적체로 흡수되는 구조다.**

**셋째, 이 프로젝트의 동시성은 스레드 동시성이 아니다.** §5가 보여 준 Rust의 최대 강점은 공유 메모리 위 스레드 경합을 타입으로 잡는 것인데, 이 프로젝트가 다루는 동시성은 전부 DB 층에 있다 — 자금·한도 애그리게이트의 버전 필드 기반 낙관적 락, 경로별 격리 수준, 조건부 UPDATE와 행 잠금이다(정본: ADR-012). 불변식을 지키는 주체가 컴파일러가 아니라 DB이고, 그 방어선은 언어를 바꿔도 그대로 남는다. **Rust가 컴파일 타임에 제거해 주는 결함 계급이 이 코드베이스에는 거의 나타나지 않는다.**

**넷째, 회수해야 할 비용이 측정된 적이 없다.** 릴레이 처리량은 여전히 [미검증]로 열려 있다. 이 프로젝트는 이 상황에 적용할 규칙을 이미 갖고 있다 — 타임아웃 초기값 아홉 개 중 여섯이 미검증이라고 밝히며 "그때까지 이 값을 근거로 다른 결정을 하지 않는다"고 못박은 것과 같은 원칙이다(정본: ADR-013 §4). 측정되지 않은 병목을 근거로 언어를 바꾸는 것은 그 원칙의 정반대다.

**다섯째, 이 프로젝트는 실제로 같은 판단을 한 번 내렸고 Rust가 졌다.** 호스트 상주 저수준 도구의 언어를 고를 때 Kotlin/JVM·Go·Rust를 여섯 축으로 대조했고, Rust 열의 판정은 이랬다 — 상주 메모리 "가장 가볍다", 스택 단일성 "학습·빌드 시간이 가장 크다", 호스트 조작 친화 "지원되지만 생태계가 얇다", 이 프로젝트에서의 실증 "미실증", 되돌림 비용 "높다"(정본: infrastructure.md §4). 결과는 Go였다. **상주 메모리라는 Rust의 최강 축이 실제로 걸린 자리 — CPU·RAM 여유가 가장 적은 허브 호스트 — 에서조차 다른 축들이 이겼다.**

그리고 릴레이는 애초에 그 대조표의 대상도 아니다. 같은 절 머리말이 "대상은 애플리케이션이 아니다. 은행 배포 본체는 Kotlin/JVM으로 이미 고정돼 있고(C-05) 그것은 이 절의 대상이 아니다"라고 적고, 판정의 경계도 "Go는 인프라 층에만 산다 — 은행 도메인은 Kotlin/JVM 불변이다"로 못박혀 있다. 릴레이 러너는 공통 라이브러리의 `messaging-infra` 모듈이 소유하므로(정본: ADR-025 CL-3), 다른 언어로 옮기면 그 공통 라이브러리 전체를 못 쓰게 되는 비용이 추가로 붙는다.

이 판단을 우리만 한 것이 아니라는 외부 근거도 있다. 구글은 C++와 Go 양쪽에서 Rust로 재작성한 경험을 나란히 보고했는데, 두 수치가 크게 갈린다 — C++ 대비로는 "모든 사례에서 Rust로 서비스를 구축하고 유지·갱신하는 데 드는 노력이 **2배 넘게 줄었다**", 그런데 Go 대비로는 "**Go에서 Rust로 시스템을 재작성했을 때, 같은 규모의 팀이 같은 시간을 들여 만든다는 것을 발견했다**"([Lars Bergstrom, Rust Nation UK 2024](https://www.theregister.com/2024/03/31/rust_google_c/)). 생산성 손실이 없다는 뜻이지 생산성 이득도 없다는 뜻이며, 이득으로 함께 보고된 것은 메모리 사용 감소와 결함률 감소다. **즉 Rust의 큰 승리는 "C++를 쓸 수밖에 없던 자리"에서 나오고, 이미 메모리 안전한 언어를 쓰는 자리에서는 §8의 좁은 조건에 걸릴 때만 나온다.** 이 프로젝트의 본체는 후자이며 그 조건에 걸리지 않는다. 다만 이 수치는 통제 실험이 아니라 발표자의 자기 보고이고 표본·산출법이 공개되어 있지 않으므로, 방향의 근거로만 쓰는 것이 맞다.

정리하면 결론은 "Rust가 이 일에 부족하다"가 아니다. **Rust가 비싸게 사 오는 보증이 이 자리에서는 이미 다른 층이 더 싸게 제공하고 있다** — 메모리 안전은 JVM이 주고, 자금 불변식은 DB 제약과 조건부 UPDATE가 지키며, 지연 여유는 설계상 시간 단위로 확보되어 있다. 여기에 언어를 하나 더 들이면 도구 최소주의(정본: C-08 — "도구 하나 = 운영 대상 하나")가 명시한 비용만 늘어난다. 뒤집어 말하면 **재판정 신호도 분명하다** — 릴레이 처리량이 실측되어 CPU나 GC 정지가 병목으로 확인되거나, 릴레이에 초 단위가 아닌 지연 목표가 새로 걸리는 순간이다. 그 전까지는 회수될 비용이 없다.

## 11. Rust를 배우려면 무엇을 보라 — 원 출처 경로

순서를 하나 권한다. 먼저 [The Rust Programming Language](https://doc.rust-lang.org/book/)의 4장(소유권·차용)과 10.3절(수명), 16장(동시성)만 읽는다. 이 세 곳이 이 문서 §2~§5의 전부이고, 공식 Book은 예제를 실제로 컴파일해 볼 수 있게 쓰여 있어서 에러 메시지를 눈으로 보는 것이 설명을 읽는 것보다 빠르다. 20.1절(Unsafe Rust)까지 보면 보증의 경계가 어디인지가 잡힌다.

그다음이 경계와 원리다. [Rustonomicon](https://doc.rust-lang.org/nomicon/)의 "Meet Safe and Unsafe"와 "Send and Sync" 두 절은 짧고, `Send`/`Sync`가 왜 `unsafe` 트레이트이며 자동 파생이 무엇을 의미하는지를 Book보다 정확하게 설명한다. 표준 라이브러리의 [Send](https://doc.rust-lang.org/std/marker/trait.Send.html)·[Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html) 문서는 각각 한 페이지이므로 함께 읽는 편이 좋다. 차용 검사기가 왜 지금의 모양이 되었는지는 [RFC 2094(NLL)](https://github.com/rust-lang/rfcs/blob/master/text/2094-nll.md)의 도입부와 세 problem case가 정본이다 — 그중 셋째는 아직 해결되지 않았다는 점을 확인하면서 읽으면 검사기의 현재 한계까지 함께 잡힌다.

손으로 부딪혀 보고 싶으면 [Learn Rust With Entirely Too Many Linked Lists](https://rust-unofficial.github.io/too-many-lists/)가 가장 효율이 좋다. 연결 리스트 하나를 만들며 `Box`부터 `unsafe` 포인터까지 올라가는 구성이라, 소유권이 자료구조 설계를 어떻게 제약하는지를 설명이 아니라 컴파일 오류로 배우게 된다.

마지막은 균형 자료다. 비용 쪽은 [Rust 컴파일러 성능 설문 2025](https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/)와 [The Rust Compilation Model Calamity](https://www.pingcap.com/blog/rust-compilation-model-calamity/)가 자기비판으로서 가장 정직하고, 효용 쪽은 구글의 [Rust fact vs. fiction](https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html)과 안드로이드 보고([Rust in Android](https://blog.google/security/rust-in-android-move-fast-fix-things/))가 실측 수치를 가진 몇 안 되는 출처다. 학습 난이도를 수치로 확인하고 싶으면 [Bronze GC 무작위 대조 시험](https://arxiv.org/abs/2110.01098)과 [Learning and Programming Challenges of Rust](https://songlh.github.io/paper/survey.pdf) 두 논문이면 충분하다.

실습 제안 하나로 마친다. 같은 작은 프로그램 — 여러 스레드가 하나의 카운터를 올리는 코드 — 을 Go와 Rust로 각각 쓰고, Go 쪽은 뮤텍스를 일부러 빼고 `go run -race`로 돌려 보고, Rust 쪽은 `Arc` 없이 컴파일해 보면 이 문서 §5와 §9가 십 분 만에 몸으로 이해된다. 한쪽은 실행해야 알고, 다른 쪽은 실행할 수조차 없다는 것이 두 설계의 차이 전부다.

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.1 | 2026-08-09 | §0 **왜 이 언어가 생겼나·무엇을 지향하나** 신설 — 2006 Graydon Hoare 개인 프로젝트→2009 모질라 후원의 계기, 이정표 6개(2006·2009·2015·2016·2018·2021)를 시간순으로, 지향점 4가지(GC 없는 메모리 안전·데이터 레이스 컴파일 차단·제로 코스트·두려움 없는 동시성), 안전 두 축의 세 언어군 대비와 GC 대비를 §7·§9의 지향 대가로 명시 연결. 기존 §1~§11 본문·수치·출처는 그대로 보존 |
