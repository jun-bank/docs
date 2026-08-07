# Go 문법 — 우리 infra 코드를 읽는 데 필요한 만큼만

> 학습 노트다. Go 문법 전체 튜토리얼이 아니라, **이 저장소의 infra 코드에 실제로 나온 문법만** 골라 "이 줄이 무슨 일을 하는가"까지 설명한다. "Go를 왜 여기 쓰는가"는 다른 문서가 소유한다([`go.md`](go.md) — 런타임·GC·단일 바이너리, 그리고 언어 결정 정본 [`ADR-028`](../../../architecture/adr/ADR-028-language-selection.md)).

읽는 대상 코드는 네 파일이다: 게이트 1 검증기 [`internal/auth/auth.go`](../../../../infra/internal/auth/auth.go), HTTP 진입 미들웨어 [`internal/httpentry/httpentry.go`](../../../../infra/internal/httpentry/httpentry.go), 배포 스키마 관문 [`internal/store/store.go`](../../../../infra/internal/store/store.go), 단일 바이너리 진입점 [`cmd/agent/main.go`](../../../../infra/cmd/agent/main.go). 인용한 코드 줄은 전부 이 네 파일에서 그대로 복사한 것이고, 문법 근거는 Go 공식 명세([go.dev/ref/spec](https://go.dev/ref/spec))와 Effective Go([go.dev/doc/effective_go](https://go.dev/doc/effective_go))를 인라인으로 단다.

순서는 하나의 동선을 따른다. 파일을 여는 순간 보이는 뼈대(선언 키워드)에서 시작해, 타입과 메서드, 그다음 Go 초심자가 가장 헷갈리는 자리인 에러와 `nil`을 지나, 마지막으로 슬라이스·context·미들웨어·고루틴 같은 우리 코드의 실제 관용구로 내려간다. 헷갈리는 두 지점(`return nil`이 성공이라는 것, `jtiArg`가 NULL이 되는 것)은 5절에 모아 두었다.

## 1. 파일의 뼈대 — package·import·func·const·var·return

Go 파일은 전부 같은 골격으로 열린다. 맨 위 한 줄이 `package`이고, 그다음 `import` 블록, 그 아래로 `type`·`const`·`var`·`func` 선언이 온다. 우리 `auth.go`는 `package auth`로 시작하고, `main.go`는 실행 가능한 바이너리라서 `package main`이다 — 패키지 이름이 `main`이고 그 안에 `func main()`이 있으면 그것이 실행 진입점이다([spec: Program execution](https://go.dev/ref/spec#Program_execution)).

`import`는 이 파일이 쓰는 다른 패키지를 나열한다. 여러 개는 괄호로 묶는다.

```go
import (
	"crypto/hmac"
	"crypto/sha256"
	"errors"
	"os"
	"strings"
	"time"
)
```

Go는 여기 적은 패키지를 하나라도 코드에서 쓰지 않으면 **경고가 아니라 컴파일 오류**로 막는다(그 설계 이유는 [`go.md`](go.md) 1절의 빌드 위생). 예외가 하나 있는데, `main.go`의 이 줄이다.

```go
	_ "github.com/go-sql-driver/mysql"
```

이름 자리에 밑줄(`_`)을 둔 것은 "이 패키지를 이름으로는 안 쓰지만 로드는 하라"는 뜻이다 — MySQL 드라이버는 import되는 것만으로 `database/sql`에 자기를 등록하는 부작용을 낸다. 이런 부작용 목적의 import를 블랭크 import라 부른다([Effective Go: blank import](https://go.dev/doc/effective_go#blank_import)).

선언 키워드는 값의 성격에 따라 나뉜다. `const`는 컴파일 시점에 고정되는 상수이고, `var`는 변수이며, `func`는 함수다. 상수 하나는 이렇게 쓴다.

```go
const DefaultClockSkew = 60 * time.Second
```

여럿을 묶을 때는 `const ( ... )` 블록을 쓴다 — `store.go`의 락 보유자 종류가 그 예다.

```go
const (
	HolderNone        HolderKind = "NONE"
	HolderAgent       HolderKind = "AGENT"
	HolderBatchCutoff HolderKind = "BATCH_CUTOFF"
)
```

`var`도 같은 방식으로 묶는다. `auth.go`는 패키지 수준 에러 값들을 `var ( ... )`로 선언한다(`ErrNoKey` 등 — 에러가 값이라는 것은 4절에서 다룬다). 함수는 `func 이름(인자) 반환타입 { ... }` 꼴이고, 값을 돌려줄 때 `return`을 쓴다.

```go
func LoadConfig() (Config, error) {
```

반환 타입이 `(Config, error)`처럼 괄호로 둘인 것이 Go의 특징인데, 그 의미는 4절에서 본다.

## 2. type·struct·interface — 그리고 암묵 구현

`type`은 새 타입에 이름을 붙이는 키워드다. 우리 코드에서 세 가지 형태로 쓴다. 첫째는 여러 필드를 묶는 `struct`다.

```go
type Request struct {
	Method     string
	Path       string
	BodyDigest string
	...
}
```

`Request`는 서명이 덮는 필드들을 한 덩어리로 나른다. 각 필드는 `이름 타입` 꼴이고, 대문자로 시작하는 이름은 패키지 밖에서 보이는 공개 필드다(소문자는 비공개 — Go의 가시성 규칙은 이름의 첫 글자로 정해진다, [spec: Exported identifiers](https://go.dev/ref/spec#Exported_identifiers)).

둘째는 `interface`다. 인터페이스는 필드가 아니라 **메서드 목록**을 적는다 — "이런 메서드를 가진 것이면 무엇이든 이 타입으로 취급한다".

```go
type Verifier interface {
	Verify(req Request) (Decision, error)
}
```

셋째는 기존 타입에 이름만 새로 붙이는 형태다. 문자열이나 정수에 의미 있는 이름을 씌워 타입 안전을 얻는다.

```go
type role string
type HolderKind string
type FencingToken uint64
type ctxKey int
```

`role`은 속으로는 그냥 문자열이지만, `role`을 기대하는 자리에 아무 문자열이나 넣을 수 없게 해서 "역할" 개념을 타입으로 굳힌다. 함수 타입에도 이름을 붙일 수 있는데, `httpentry.go`의 미들웨어가 그 예다(8절에서 자세히).

```go
type middleware func(http.Handler) http.Handler
```

인터페이스에서 Go가 다른 언어와 갈리는 지점은 **구현을 명시적으로 선언하지 않는다**는 것이다. Java의 `implements`나 Kotlin의 `: Interface` 같은 표기가 없다. 어떤 타입이 인터페이스의 메서드를 전부 가지고 있으면, 그 사실만으로 자동으로 그 인터페이스를 만족한다([Effective Go: interfaces](https://go.dev/doc/effective_go#interfaces_and_types)). `store.go`의 `SQLStore`는 어디에도 "나는 LockStore다"라고 적지 않지만, `Acquire`·`Renew`·`Read` 같은 메서드를 다 가졌으므로 `LockStore`다.

이 암묵성에는 함정이 있다 — 메서드 하나를 오타 내면 컴파일러가 "이 타입은 그 인터페이스가 아니다"라고 조용히 판단할 뿐, 어디가 틀렸는지 알려주지 않는다. 그래서 우리 코드는 컴파일 시점에 이를 못박는 관용구를 쓴다.

```go
var (
	_ LockStore    = (*SQLStore)(nil)
	_ LedgerStore  = (*SQLStore)(nil)
	_ ModeStore    = (*SQLStore)(nil)
	_ HistoryStore = (*SQLStore)(nil)
)
```

이 네 줄은 실행에 아무 영향이 없다 — 값을 블랭크 식별자 `_`에 버린다. 역할은 오직 하나, "`*SQLStore`가 이 인터페이스를 만족하지 못하면 컴파일을 실패시켜라"이다. `(*SQLStore)(nil)`은 "SQLStore를 가리키는 포인터 타입의 nil 값"이고(포인터는 3·5절), 그것을 `LockStore` 자리에 대입해 보는 것으로 타입 검사를 강제한다. 인터페이스 만족을 코드로 증명하는 이 패턴은 표준 라이브러리도 쓰는 공인 관용구다([FAQ: guarantee a type satisfies an interface](https://go.dev/doc/faq#guarantee_satisfies_interface)).

우리 struct 어디에도 백틱 태그(예: `` `json:"..."` ``)가 없다는 점도 기록해 둘 만하다. 태그는 struct 필드에 붙여 JSON 직렬화나 ORM 매핑을 지시하는 문법인데([spec: Struct types](https://go.dev/ref/spec#Struct_types)), 우리 코드는 HTTP 헤더를 이름으로 직접 읽고 SQL을 자리표시자(`?`)로 직접 쓰기 때문에 태그가 필요한 자리가 없다. 문법이 없어서가 아니라 쓸 일이 없어서 안 보이는 것이다.

## 3. 메서드 리시버 — 값이냐 포인터냐

Go의 메서드는 클래스 안에 들어가지 않는다. 함수 이름 앞에 **리시버**라는 특별한 인자를 하나 더 달아 "이 함수는 이 타입에 붙는다"를 표현한다([spec: Method declarations](https://go.dev/ref/spec#Method_declarations)). `SystemClock`의 `Now`가 가장 단순한 예다.

```go
func (SystemClock) Now() time.Time { return time.Now() }
```

`func` 뒤 괄호 `(SystemClock)`이 리시버다 — "이 메서드는 `SystemClock` 값에 붙는다". 리시버에는 두 종류가 있고 우리 코드는 둘 다 쓴다. 값 리시버는 타입의 복사본을 받고, 포인터 리시버(`*T`)는 원본을 가리키는 포인터를 받는다.

```go
func (v *hmacVerifier) Verify(req Request) (Decision, error) {
```

여기 `(v *hmacVerifier)`는 포인터 리시버다. 검증기의 상태(키·시계)를 읽어야 하고, 복사 비용을 피하며, 무엇보다 우리는 이 값을 항상 포인터로 다루기 때문이다. 반대로 `httpentry.go`의 `rejectUnverified`는 값 리시버를 쓴다.

```go
func (d Deps) rejectUnverified(ctx context.Context, requestID, reason string) {
```

`Deps`는 인터페이스 몇 개를 담은 작은 묶음이라 복사해도 싸고, 이 메서드가 `Deps` 자체를 바꾸지 않으므로 값으로 받아도 무방하다. 값을 바꿔야 하거나 큰 구조체이면 포인터 리시버를, 작고 불변이면 값 리시버를 고르는 것이 관용이다([Effective Go: pointers vs. values](https://go.dev/doc/effective_go#pointers_vs_values)).

## 4. 에러는 예외가 아니라 값이다 — `if err != nil`과 `return nil`

여기가 다른 언어에서 온 사람이 가장 먼저 부딪히는 자리다. Go에는 `try/catch`가 없다. 실패할 수 있는 함수는 **마지막 반환값으로 `error`를 하나 더 돌려준다**([Effective Go: errors](https://go.dev/doc/effective_go#errors)). 그래서 함수 시그니처가 `(Config, error)`, `(Decision, error)`처럼 값 하나에 에러 하나가 붙는 꼴이 된다. 호출하는 쪽은 두 값을 한꺼번에 받는다.

```go
	dec, err := d.Verifier.Verify(areq)
	if err != nil {
		http.Error(w, "서명 검증 중 오류", http.StatusInternalServerError)
		return
	}
```

`dec, err :=`는 반환된 두 값을 두 변수에 나눠 받는다. 그다음 `if err != nil`이 Go 코드 전체에 깔린 관용구다 — "에러가 비어 있지 않으면(=실패했으면) 처리하라". 여기서 `nil`이 핵심이다. `error`는 인터페이스 타입이고, 그 인터페이스가 비어 있는 상태를 `nil`이라 한다. 그리고 Go의 규약은 **`nil` 에러 = 에러 없음 = 성공**이다.

이 규약을 정면으로 보여 주는 줄이 `store.go`의 `Reserve` 안에 있다 — 사용자가 헷갈렸다고 지목한 바로 그 코드다.

```go
	if err == nil {
		return nil // 신규 예약
	}
```

한 줄씩 풀면 이렇다. INSERT를 실행한 뒤 받은 `err`가 `nil`이면(`err == nil`), INSERT가 성공했다는 뜻이다. 그러면 `Reserve` 함수 자신도 성공을 알려야 하는데, 이 함수의 반환 타입은 `error` 하나뿐이라(`func (s *SQLStore) Reserve(...) error`), "성공"을 표현하는 방법이 곧 **`error` 자리에 `nil`을 돌려주는 것**이다. 즉 `return nil`은 "돌려줄 데이터가 없다"가 아니라 "**에러 없이 끝났다 = 성공했다**"는 신호다.

이것이 SQL의 `NULL`과 다른 지점이다. SQL `NULL`은 데이터 칸이 비었다는 뜻이지만, 여기 `nil`은 **에러 칸이 비었다**는 뜻이고 그 빈 상태가 곧 성공이다. 값의 부재가 아니라 실패의 부재다. 이 `return nil`을 받는 쪽(`httpentry.go`의 멱등 미들웨어)이 다시 `err == nil`로 성공을 읽어 흐름을 가른다.

```go
	switch {
	case err == nil:
		// 신규 예약 — 이력에 RESERVED를 남기고 하류로 진행한다.
```

에러를 값으로 다루면 좋은 점은 에러도 다른 값처럼 감싸고 검사할 수 있다는 것이다. `main.go`는 하위 에러를 `%w`로 감싸 맥락을 덧붙인다.

```go
		return fmt.Errorf("설정 로딩 실패: %w", err)
```

`%w`는 "이 에러를 원본을 잃지 않고 감싼다"는 동사다([Go blog: error wrapping](https://go.dev/blog/go1.13-errors)). 감싼 에러의 정체를 나중에 되묻는 두 함수가 `errors.Is`와 `errors.As`다. `errors.Is`는 "이 에러가 특정 에러값이냐"를 묻는다.

```go
	case errors.Is(err, store.ErrReplay):
```

`errors.As`는 "이 에러 사슬 안에 특정 **타입**의 에러가 있느냐, 있으면 그것을 꺼내 달라"를 묻는다. `httpentry.go`가 본문 크기 초과를 가려내는 자리가 그 예다.

```go
			var tooLarge *http.MaxBytesError
			if errors.As(err, &tooLarge) {
```

`var tooLarge *http.MaxBytesError`로 빈 포인터를 하나 만들고, `errors.As(err, &tooLarge)`가 에러 사슬에서 그 타입을 찾으면 `tooLarge`에 채워 넣으며 참을 돌려준다([pkg: errors.As](https://pkg.go.dev/errors#As)). `store.go`도 MySQL 드라이버의 구체 에러 타입을 이 방식으로 꺼내 중복 키 코드(1062)를 확인한다.

## 5. nil의 세 얼굴 — 성공이거나, 미설정이거나, 부재이거나

`nil`은 문맥에 따라 세 가지 다른 것을 뜻한다. 이 절은 그 셋을 나란히 놓아 4절의 `return nil`과 사용자가 지목한 `jtiArg`가 왜 둘 다 `nil`인데 뜻이 다른지를 못박는다. 세 얼굴 모두 뿌리는 하나다 — Go에서 포인터·인터페이스·슬라이스 같은 타입의 **제로값(초기화하지 않았을 때의 기본값)이 `nil`**이다([spec: The zero value](https://go.dev/ref/spec#The_zero_value)).

첫째 얼굴은 4절에서 본 **성공으로서의 nil**이다. `error` 반환 자리의 `nil`은 "실패가 없다"이고, 그래서 `return nil`이 성공을 뜻한다.

둘째 얼굴은 **미설정을 뜻하는 포인터 nil**이다. `auth.go`의 시계 스큐 설정이 그 예이고, 이것이 우리가 실제로 고친 버그의 핵심이었다.

```go
	Skew *time.Duration
```

`time.Duration`이 아니라 `*time.Duration`(포인터)으로 둔 데는 이유가 있다. 값 타입이면 "설정 안 함"과 "0으로 설정함"이 둘 다 `0`이라 구분되지 않는다. 포인터로 두면 **`nil`은 "운영자가 값을 안 줬다(미설정)", `nil`이 아닌 값은 "명시적으로 이만큼 주었다"**로 갈린다. 그 판정을 하는 자리가 이렇다.

```go
	skew := DefaultClockSkew
	if cfg.Skew != nil {
		skew = *cfg.Skew
	}
```

`cfg.Skew != nil`이면 운영자가 값을 준 것이므로 `*cfg.Skew`로 포인터가 가리키는 실제 값을 꺼내(`*`가 역참조다) 그대로 존중하고, `nil`이면 미설정이니 기본값(60초)으로 채운다. 반대로 값을 넣을 때는 `&`로 변수의 주소를 얻어 포인터를 만든다.

```go
	return Config{Key: []byte(key), Skew: &skew}, nil
```

`&skew`는 "`skew` 변수의 주소"이고, 그래서 `Skew` 필드(`*time.Duration`)에 들어간다. 포인터의 `nil`이 여기서는 데이터의 부재도 에러도 아닌, "설정이 안 됐다"는 상태 그 자체를 나른다.

셋째 얼굴은 **데이터의 부재로서의 nil**, 즉 SQL `NULL`이다. 사용자가 지목한 `store.go`의 `jtiArg`가 정확히 이 경우다.

```go
	var jtiArg any
	if jti != "" {
		jtiArg = jti
	}
	_, err := s.db.ExecContext(ctx,
		"INSERT INTO `deploy_request_ledger` (`request_id`, `jti`, `body_digest`) VALUES (?, ?, ?)",
		requestID, jtiArg, bodyDigest)
```

`var jtiArg any`는 `jtiArg`를 `any` 타입(= `interface{}`, 아무 값이나 담는 빈 인터페이스)으로 선언하고, 초기화하지 않았으니 제로값 `nil`로 시작한다. `jti` 문자열이 비어 있으면 `if` 블록에 안 들어가므로 `jtiArg`는 `nil`인 채로 남는다. 그 `nil`을 SQL 파라미터로 넘기면, `database/sql`이 **인터페이스 `nil`을 SQL `NULL`로 변환한다**([pkg: database/sql/driver Value](https://pkg.go.dev/database/sql/driver#Value) — 드라이버가 다뤄야 하는 값 목록에 `nil`이 들어 있고 그것이 NULL이다). 반대로 `jti`가 있으면 `jtiArg`에 문자열이 담겨 SQL 문자열 값으로 들어간다.

여기서 4절과의 대비가 분명해진다. `return nil`의 `nil`은 에러 인터페이스가 비어 성공을 뜻했지만, `jtiArg`의 `nil`은 **데이터 값이 없어 DB에 NULL로 기록**된다. 문법은 같은 `nil`이지만 하나는 "실패 없음", 하나는 "값 없음"이다. 그리고 이 NULL은 의도된 것이다 — 코드 주석이 밝히듯 UNIQUE 제약은 여러 NULL을 서로 충돌로 보지 않으므로, OIDC 이전 단계에서 여러 요청이 `jti` 없이 공존할 수 있다. 세 얼굴을 한 줄로 줄이면, `nil`은 "그 자리에 아무것도 없다"는 한 가지 문법이 문맥(에러 자리·포인터 자리·데이터 자리)에 따라 성공·미설정·부재로 읽히는 것이다.

## 6. 슬라이스와 []byte — 바이트 열을 다루는 법

Go에서 `[]T`는 슬라이스, 즉 길이가 변할 수 있는 `T`의 열이다([Effective Go: slices](https://go.dev/doc/effective_go#slices)). 우리 코드에서 가장 자주 보는 것이 `[]byte` — 원시 바이트 열이다. HMAC 키와 서명이 그 타입이다.

```go
	Signature  []byte
```

서명이나 키를 `string`이 아니라 `[]byte`로 두는 것은 암호 연산이 바이트 단위로 이뤄지고 내용이 임의 바이트일 수 있기 때문이다. 문자열과 바이트 열은 서로 변환할 수 있고, 우리 코드는 `[]byte(key)`처럼 문자열을 바이트 열로 바꾼다(5절 마지막 인용의 `[]byte(key)`가 그것이다).

본문 다이제스트를 만드는 `httpentry.go`가 슬라이스의 부분 표기까지 보여 준다.

```go
	sum := sha256.Sum256(body)
	return "sha256:" + hex.EncodeToString(sum[:])
```

`sha256.Sum256`은 고정 길이 배열 `[32]byte`를 돌려주는데, `hex.EncodeToString`은 슬라이스(`[]byte`)를 받는다. 그래서 `sum[:]`으로 배열 전체를 슬라이스로 바꿔 넘긴다 — `[:]`는 "처음부터 끝까지"를 뜻하는 슬라이스 표현식이다([spec: Slice expressions](https://go.dev/ref/spec#Slice_expressions)). 배열과 슬라이스가 다른 타입이라 이 한 글자짜리 변환이 필요하다.

## 7. context.Context — 첫 인자로 흐르는 취소와 값

`context.Context`는 요청 하나의 수명을 나타내는 값이다 — 취소 신호와 마감 시각, 그리고 요청 범위의 값을 실어 함수에서 함수로 흐른다([pkg: context](https://pkg.go.dev/context)). Go의 관용은 이것을 **함수의 첫 인자로 명시적으로 넘기는 것**이고, 우리 store 인터페이스가 그 규약을 그대로 따른다.

```go
	Reserve(ctx context.Context, requestID, jti, bodyDigest string) error
```

`ctx context.Context`가 언제나 맨 앞에 온다. 이렇게 하면 요청이 취소되거나 마감을 넘겼을 때 DB 호출까지 그 신호가 전달돼 중간에 멈출 수 있다(`ExecContext`·`QueryRowContext`가 `ctx`를 받는 이유다). context는 값을 나르기도 한다. `httpentry.go`는 게이트 1을 통과한 요청을 하류 미들웨어로 넘기려고 context에 실어 둔다.

```go
		ctx := context.WithValue(r.Context(), verifiedRequestKey, verifiedRequest{req: areq, jti: ""})
```

`r.Context()`로 요청의 현재 context를 얻고, `context.WithValue`로 검증된 요청을 얹은 새 context를 만든다. `main.go`는 context의 또 다른 쓰임인 취소·타임아웃을 보여 준다.

```go
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
```

`context.Background()`는 아무것도 실리지 않은 뿌리 context이고, `signal.NotifyContext`는 SIGINT/SIGTERM이 오면 취소되는 context를 만든다 — 그 취소가 우아한 종료의 방아쇠가 된다(9절).

## 8. http.Handler와 미들웨어 — 함수가 핸들러를 감싸 핸들러를 낸다

우리 HTTP 진입 층의 뼈대는 `http.Handler`라는 하나의 인터페이스와, 그것을 감싸는 미들웨어 패턴이다. `http.Handler`는 `ServeHTTP(ResponseWriter, *Request)` 메서드 하나를 가진 인터페이스이고, 미들웨어는 **핸들러를 받아 핸들러를 돌려주는 함수**다. 우리 코드는 그 형태에 이름을 붙였다.

```go
type middleware func(http.Handler) http.Handler
```

읽는 법은 "`http.Handler`를 입력받아 `http.Handler`를 출력하는 함수"다. 왜 이런 형태냐면, 이렇게 하면 각 미들웨어가 다음 핸들러를 감싸 요청 전후에 자기 일을 끼워 넣을 수 있기 때문이다([Go blog: middleware 패턴의 기반인 HandlerFunc](https://pkg.go.dev/net/http#HandlerFunc)). 본문 크기를 제한하는 미들웨어가 전형이다.

```go
func withBodyLimit(max int64) middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			r.Body = http.MaxBytesReader(w, r.Body, max)
			next.ServeHTTP(w, r)
		})
	}
}
```

세 겹으로 중첩된 이 구조를 안에서 밖으로 읽으면 이렇다. 가장 안쪽은 실제 일을 하는 함수(본문에 상한을 씌우고 `next.ServeHTTP`로 다음으로 넘김)다. `http.HandlerFunc(...)`는 그냥 함수를 `http.Handler`로 만들어 주는 어댑터다 — 함수 하나에 `ServeHTTP` 메서드를 붙여 인터페이스를 만족시킨다. 그리고 그 전체를 `func(next http.Handler) http.Handler`가 감싸, "다음 핸들러(`next`)를 받아 그것을 감싼 핸들러를 낸다"는 미들웨어 형태를 완성한다.

여러 미들웨어를 순서대로 두르는 것이 `chain`이다.

```go
func chain(h http.Handler, mws ...middleware) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}
```

`mws ...middleware`의 `...`는 가변 인자다 — 미들웨어를 몇 개든 받는다([spec: 가변 인자](https://go.dev/ref/spec#Passing_arguments_to_..._parameters)). 뒤에서부터 감싸는 것은 먼저 적은 미들웨어가 바깥(먼저 실행)이 되게 하려는 것이다. 실제 등록은 `NewHandler`에서 `mux.Handle("POST /deploy", chain(...))`로 이뤄진다 — `"POST /deploy"`라는 패턴 문자열은 Go 1.22+의 메서드별 라우팅이라, POST가 아닌 요청은 표준 라이브러리가 405로 자동 거절한다([Go 1.22 release notes: 라우팅 개선](https://go.dev/blog/routing-enhancements)).

## 9. 고루틴·채널·select·defer — 서버를 띄우고 우아하게 내린다

`main.go`의 서버 기동부는 Go의 동시성 원시들이 한자리에 모인 곳이다. `go` 키워드는 함수를 새 고루틴에서 동시에 실행시킨다([Effective Go: goroutines](https://go.dev/doc/effective_go#goroutines)).

```go
	go func() {
		fmt.Println("jun-bank deploy-agent · ROLE=main · listen:", cfg.ListenAddr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
			return
		}
		errCh <- nil
	}()
```

`go func(){ ... }()`는 익명 함수를 선언과 동시에 고루틴으로 띄운다. 서버의 `ListenAndServe`는 블로킹이라 별도 고루틴에 두어야 메인 흐름이 종료 신호를 기다릴 수 있다. 고루틴이 결과를 메인으로 돌려보내는 통로가 채널이다.

```go
	errCh := make(chan error, 1)
```

`make(chan error, 1)`은 `error`를 나르는, 버퍼 1짜리 채널을 만든다([Effective Go: channels](https://go.dev/doc/effective_go#channels)). 고루틴은 `errCh <- err`로 채널에 값을 보내고(화살표가 값이 가는 방향이다), 메인은 `<-errCh`로 받는다. 어느 쪽이 먼저 오는지 기다리는 것이 `select`다.

```go
	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return srv.Shutdown(shutdownCtx)
	}
```

`select`는 여러 채널 중 먼저 준비되는 쪽의 분기를 실행한다([spec: Select statements](https://go.dev/ref/spec#Select_statements)). 서버가 스스로 죽으면 `errCh`가 오고, 사용자가 SIGTERM을 보내면 7절의 `ctx.Done()`이 온다 — 후자면 10초 마감을 건 새 context로 `Shutdown`을 불러 진행 중인 요청을 마치게 한 뒤 내린다.

여기 두 번 나온 `defer`가 Go의 정리(cleanup) 관용구다. `defer`를 단 호출은 **그 함수가 반환하는 순간 실행된다** — 자원을 여는 코드 바로 옆에 닫는 코드를 둘 수 있게 해 준다([Effective Go: defer](https://go.dev/doc/effective_go#defer)).

```go
	defer stop()
```

`main.go`는 `signal.NotifyContext`가 돌려준 `stop`과 `context.WithTimeout`이 돌려준 `cancel`을 각각 `defer`로 걸어, 함수가 어떤 경로로 끝나든 신호 구독과 타이머가 반드시 해제되게 한다.

## 10. 읽다 걸리는 작은 문법 — := 대 =, switch, 블랭크, 타입 단언

앞 절들에 흩어져 나왔지만 따로 못박아 둘 값어치가 있는 문법을 모은다. 먼저 `:=`와 `=`의 차이다. `:=`는 **변수를 새로 선언하면서 동시에 값을 넣는다**(짧은 변수 선언, [spec](https://go.dev/ref/spec#Short_variable_declarations)). `=`는 **이미 있는 변수에 값을 다시 넣는다**(대입).

```go
	skew := DefaultClockSkew
	if raw := os.Getenv("AGENT_CLOCK_SKEW"); raw != "" {
		d, err := time.ParseDuration(raw)
		if err != nil || d < 0 {
			return Config{}, ErrBadSkew
		}
		skew = d
	}
```

`skew := ...`는 `skew`를 새로 만들고, 아래 `skew = d`는 그 이미 만든 `skew`에 새 값을 넣는다 — 여기서 `:=`를 다시 쓰면 안쪽 스코프에 다른 `skew`가 생겨 바깥 것이 안 바뀐다. `if raw := ...; raw != ""` 형태도 흔한데, `if` 조건 앞에 짧은 선언을 두어 `raw`를 그 `if` 블록 안에서만 살아 있게 한다.

`switch`는 우리 코드에서 두 모습으로 나온다. 값을 놓고 분기하는 형태는 `main.go`의 역할 판정이다.

```go
	switch role(raw) {
	case roleMain, roleAgent:
		return role(raw), nil
	case "":
		return "", errors.New("ROLE 미설정 ...")
	default:
		return "", fmt.Errorf("ROLE 미지원: %q ...", raw)
	}
```

조건 없는 `switch`(`switch {`)도 있는데, 이건 `if/else if` 사슬을 읽기 좋게 편 것이다 — 4절의 멱등 분기와 `store.go`의 다이제스트 3분기가 그 형태다. Go의 `case`는 자동으로 다음으로 흘러내리지 않아(fall-through 없음) `break`를 쓰지 않는다([Effective Go: switch](https://go.dev/doc/effective_go#switch)).

블랭크 식별자 `_`는 "이 값은 안 쓰니 버린다"는 표시로, 세 자리에서 봤다. 다중 반환에서 한쪽만 쓸 때(`_, err := s.db.ExecContext(...)` — 결과 행 수는 버리고 에러만), 에러를 의도적으로 무시할 때(`_ = d.History.AppendEvent(...)` — 기록 실패는 삼킨다는 결정), 그리고 2절의 컴파일타임 단언과 1절의 블랭크 import다([Effective Go: blank identifier](https://go.dev/doc/effective_go#blank)).

마지막은 타입 단언이다. `any`나 인터페이스 값에서 구체 타입을 꺼내는 문법으로, `httpentry.go`가 context에 실어 둔 값을 다시 꺼낼 때 쓴다.

```go
		v, ok := r.Context().Value(verifiedRequestKey).(verifiedRequest)
		if !ok {
			http.Error(w, "검증되지 않은 요청 (내부 순서 오류)", http.StatusInternalServerError)
			return
		}
```

`.(verifiedRequest)`가 "이 값이 `verifiedRequest` 타입이면 그것으로 꺼내라"는 타입 단언이다([spec: Type assertions](https://go.dev/ref/spec#Type_assertions)). 두 값 형태(`v, ok :=`)로 받으면 타입이 안 맞아도 패닉하지 않고 `ok`에 거짓이 온다 — 그래서 게이트 1을 거치지 않은 요청을 `if !ok`로 걸러 fail-closed로 막을 수 있다. `any` 타입 자체는 5절 `jtiArg`에서 봤듯 "아무 값이나 담는 빈 인터페이스"이고, 그렇게 담긴 값을 다시 구체 타입으로 되꺼내는 것이 이 타입 단언이다.
