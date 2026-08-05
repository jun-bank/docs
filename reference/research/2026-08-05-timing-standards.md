# 카드 결제 승인 — 응답시간·타임아웃·재시도 규약 기준치 리서치

- 작성일: 2026-08-05
- 조사 방법: WebSearch + 원문 WebFetch/PDF 추출 (Visa Business News PDF, Worldpay ISO 8583 Reference Guide V2.63 PDF 는 실제 다운로드 후 텍스트 추출하여 인용)
- 성격: **L0 리서치**. 여기의 수치는 구현 입력이 되는 순간 실제 계약서·연동규격으로 재확인해야 한다.

## 0. 근거 강도 범례

| 등급 | 의미 |
|---|---|
| **A (원문)** | 표준/규정/벤더 공식 문서의 원문을 직접 열어 인용 |
| **B (공식 2차)** | 벤더 공식 사이트지만 검색 스니펫 수준으로만 확인, 원문 전체 미열람 |
| **C (2차·업계)** | 블로그·업계 매체 등. 교차검증 안 됨 |
| **X** | **출처 없음 — 업계 통념** |

---

## 1. 승인 응답시간 규약

### 1.1 표준 자체가 값을 정하는가?

**정하지 않는다.** ISO 8583 은 *메시지 구조·데이터 요소·코드값*을 규정하는 표준이고(ISO 8583-1:2003 "Financial transaction card originated messages — Interchange message specifications — Part 1: Messages, data elements and code values"), 타임아웃 초 값은 표준 본문에 없다. 응답 대기시간은 **"사전 합의된 시간(pre-set time)"** 으로 각 네트워크·매입사·발급사 간 규약이 정한다.

- 근거: [ISO 8583-1:2003 (ISO Online Browsing Platform)](https://www.iso.org/obp/ui/#iso:std:iso:8583:-1:ed-1:v1:en) — 표준 제목·범위 자체가 메시지 명세임. **등급 A(범위 확인)** / 타임아웃 부재는 "규정하지 않음"의 확인이므로 등급 B.
- 보강: [Worldpay ISO 8583 Reference Guide V2.63 (2026-03)](https://docs.worldpay.com/assets/pdf/Worldpay_ISO_8583_Reference_Guide_V2.63.pdf) 의 Figure 3-3~3-5 는 타임아웃 시나리오를 **"within the specified time period"** 로만 서술하고 초 값을 본문에 두지 않는다 → 값은 구현체(매입사 플랫폼) 소관임을 재확인. **등급 A**

### 1.2 실제 구현체가 정하는 값

| 주체 | 값 | 대상 구간 | 출처 | 연도 | 등급 |
|---|---|---|---|---|---|
| Worldpay(Global Payments) | **최소 25초 권장**, 클라이언트 측 configurable | 가맹점 클라이언트 → 매입사 승인 플랫폼 (ISO 8583 over HTTPS) | [ISO 8583 Reference Guide V2.63, App. F.3](https://docs.worldpay.com/assets/pdf/Worldpay_ISO_8583_Reference_Guide_V2.63.pdf) — 원문: *"The client application should have configurable time-out value parameters. Worldpay recommends a timeout value of at least 25 seconds."* | 2026-03 | **A** |
| Worldpay | 단일 TCP 세션당 **미응답 요청 20건 초과 금지**, persistent connection 미허용 | 클라이언트 세션 관리 | 위와 동일 (App. F.3) | 2026-03 | **A** |
| Mastercard | **7초** — 초과 시 Mastercard 가 STIP 로 독자 승인 | Mastercard → Mastercard Processing(발급 프로세서) | [Mastercard Processing Debit APIs](https://developer.mastercard.com/mastercard-processing-debit/documentation/) | n/a | **B** |
| Mastercard | **40초** — Receive Network 무응답 판정 | Mastercard → 수신 네트워크 | [Mastercard Cross-Border Services — Timeouts](https://developer.mastercard.com/cross-border-services/documentation/response-error-codes/timeouts/) | n/a | **B** |
| Visa | STIP 는 "밀리초 단위"로 동작 — **공개된 수치 SLA 없음** | 발급사 무응답 시 VisaNet 대행 | [Visa — Smarter STIP](https://usa.visa.com/dam/VCOM/regional/na/us/about-visa/research/documents/smarter-stip.pdf), [Nilson Report](https://nilsonreport.com/articles/visa-adds-artificial-intelligence-to-stand-in-processing/) | 2024~ | **B** (질적 서술만) |
| 국내 VAN | **확인 실패** — KISVAN·NICE정보통신·한국결제네트웍스 모두 공개 자료에 "실시간·24×365" 라는 정성 표현만 있고 응답시간 규격 수치 없음 | 단말 ↔ VAN ↔ 카드사 | [NICE정보통신 VAN 서비스](https://www.nicevan.co.kr/korean/02_business/1.html), [KISVAN](https://www.kisvan.co.kr/sub01_02_01.html) | 2026 조회 | **X** |
| 업계 통념 | 단말 체감 1~3초, 전 구간 5초 이내 | 전체 승인 왕복 | 벤더 블로그([JA Technology](https://jatechnologysolutions.com/insights/iso-8583-how-payment-card-messages-work/)) 수준 | n/a | **C→X** |

> **국내 VAN/밴사 규약의 승인 응답시간 수치는 공개 자료로 확인되지 않았다.** VAN 연동규격서는 계약·NDA 기반 배포이며 웹에 없다. **출처 없음 — 업계 통념**으로 취급하고, 실제 값은 계약 시 규격서에서 받아야 한다.

---

## 2. 타임아웃 값 + 망취소 발송 시점

### 2.1 타임아웃 값

| 계층 | 값 | 출처 | 등급 |
|---|---|---|---|
| 가맹점 → 매입사 (국제, ISO 8583/HTTPS) | **≥ 25초** | Worldpay ISO 8583 Ref Guide V2.63 App. F.3 | **A** |
| 네트워크 → 발급 프로세서 | **7초** (Mastercard) | Mastercard Processing Debit APIs | **B** |
| 네트워크 → 수신 네트워크 | **40초** (Mastercard) | Mastercard Cross-Border Services Timeouts | **B** |
| 국내 PG(토스페이먼츠) 권장 | **Read Timeout 60초** — 원문: *"결제 처리와 관련된 API의 Read Timeout은 60초로 설정하면 돼요"* | [토스페이먼츠 개발자센터 — 타임아웃](https://docs.tosspayments.com/resources/glossary/timeout) | **A** |
| 국내 PG(나이스페이먼츠) 샘플 코드 | **Connection 3초 / Read 5초** (`setConnectTimeout(3000)`, `setReadTimeout(5000)`) | [NICEPAY 인증 결제 API 매뉴얼](https://developers.nicepay.co.kr/manual-auth.php) | **A**(문서상 존재) / 다만 **규약이 아니라 샘플 코드 값** — 근거 약함 |

> 국내 두 PG 가 3~5초와 60초로 12배 차이가 난다. 이는 "업계 표준값이 없다"는 증거로 읽어야 한다. 나이스 값은 샘플 코드, 토스 값은 문서상 권장값이라 **성격이 다르므로 직접 비교 불가**.

### 2.2 타임아웃 후 망취소(reversal) 발송 시점

- **국제 (Worldpay)**: 응답을 지정 시간 내 받지 못하면 **즉시 0420 reversal 을 발송**한다. 원문 Figure 3-3 시나리오: *"The intercept does not receive a response message within the specified time period. → The intercept sends a 0420 reversal request message."* **등급 A**
- **STIP 개입 시 (Figure 3-4)**: 네트워크가 대행 승인(0110) 후 발급사의 **지연 응답이 늦게 도착하면**, 그 지연 응답을 무효화하기 위해 네트워크가 0420 을 보낸다. 즉 reversal 은 "가맹점→네트워크" 방향만이 아니라 **양방향**으로 발생한다. **등급 A**
- **국내 (NICEPAY)**: *"승인 요청 후 기타오류(Network 지연 또는 가맹점 내부 처리오류) 발생시"* 망취소 요청. Connection timeout / Read timeout 각각에 대해 **인증 응답값을 참조해 즉시 망취소**하도록 안내. **등급 A**
- **국내 (KICC)**: *"응답 대기시간 초과(Read Timeout) 및 네트워크 오류로 응답을 받지 못한 경우… 반드시 망취소(Net-Cancel) API를 통해 상태를 확인"* — [KICC 개발자센터](https://docs.kicc.co.kr/docs/van-payment/simple/cancel/) **등급 B**

**결론: "타임아웃 발생 = 즉시 망취소"가 국내외 공통 규약이다. 지연 발송을 규정한 자료는 없다.**

---

## 3. 망취소(Reversal) 규약 — ISO 8583 0400/0420

### 3.1 메시지 종류

| MTI | 의미 | 성격 |
|---|---|---|
| 0400 | Reversal Request (Acquirer) | 요청-응답형 |
| 0401 | Reversal Request Repeat | 재전송 |
| 0410 | Reversal Request Response | |
| 0420 | Reversal Advice | 통보형(advice) |
| 0421 | Reversal Advice Repeat | **타임아웃 시 반복 전송** |
| 0430 | Reversal Advice Response (수신 확인) | |

- MTI 3번째 자리 `x x 2 x` = Advice, 4번째 자리 `x x x 1` = Repeat. 출처: [ISO 8583 — Wikipedia](https://en.wikipedia.org/wiki/ISO_8583), [Afferent Software](https://afferentsoftware.com/so-what-is-iso8583-anyway/) **등급 B**
- Worldpay 실무 구현은 **0420/0430 쌍**을 쓴다(Figure 3-3~3-5, 3-10, 3-11). 0400 계열은 이 가이드의 흐름도에 등장하지 않는다. **등급 A**

### 3.2 재시도 정책 — 표준이 정하는가?

**정하지 않는다.** 표준이 정하는 것은 "repeat 메시지가 존재한다"는 구조뿐이고, **횟수·간격은 구현체 소관**이다.

- 근거: *"If one of the intended recipients of the reversal advice message does not acknowledge receipt of the 0420 message, the originator **may** continue to send additional reversal advice repeat messages (0421) **until a response is received**"* — 조동사 `may` + 종료조건이 "응답 수신"뿐이고 횟수·간격이 없다. 출처: Wikipedia / Afferent Software **등급 B**
- 즉 **의미론은 store-and-forward + at-least-once 재전송**이며, 수신측이 **멱등하게 중복 reversal 을 흡수**해야 한다는 뜻이 된다.
- **재시도 횟수·간격의 구체 수치는 국내외 어느 공개 자료에서도 확인되지 않았다 → 출처 없음 — 업계 통념.**

### 3.3 TTL — 얼마나 오래 유효한가

| 대상 | 값 | 출처 | 등급 |
|---|---|---|---|
| **NICEPAY 망취소** | **1시간** — 원문: *"망취소 유효기간은 1시간으로, 요청 후 1시간 초과건은 망취소가 실패됩니다."* 또한 *"망취소는 승인 요청 및 응답 수신 처리에만 실패한 경우에 사용"*, *"orderId가 unique한 경우에만 정상 처리"* | [nicepay-manual/api/cancel.md](https://github.com/nicepayments/nicepay-manual/blob/main/api/cancel.md) | **A** |
| Visa — AFD(주유기) 선승인 | 승인 응답 수신 후 **2시간 이내** completion 또는 reversal 필수 | [Visa Business News, Article ID AI13522, 2023-10-19](https://corporate.visa.com/content/dam/VCOM/regional/na/us/support-legal/documents/authorization-framework-will-be-updated-to-simplify-authorization-processing-time-frames.pdf) 각주 2 | **A** |
| Visa — 미완료 거래 reversal | 완료되지 않을 것을 **인지한 시점부터 24시간 이내** 또는 승인 유효기간 만료 중 **빠른 쪽** | [Chargebacks911 — Visa Authorization Rules](https://chargebacks911.com/visa-authorization-rules/), [Walletto](https://walletto.eu/authorization-and-reversal-processing-requirements-for-merchants/) — **Visa Core Rules 원문 미확인** | **C** |
| Visa — 승인금액 초과분 | 최종금액보다 **15% 이상** 초과 승인 시 차액을 **24시간 이내** reversal | 위와 동일 | **C** |
| Mastercard — reversal 제출 기한 | 미국 CP **24시간**, CNP **72시간** / 유럽 **24시간** | [DPO Group blog](https://blog.dpogroup.com/mastercard-best-practices-managing-authorization-reversals/), Chargebacks911 — **Mastercard TPR 원문 다운로드 실패(차단)** | **C** |

> **중요한 구분**: 3.3 표의 Visa/Mastercard "24~72시간"은 **가맹점의 비즈니스 레벨 승인취소 의무**(주문 취소·금액 변경)이고, 2.2 의 "즉시 망취소"는 **통신 실패에 대한 기술적 reversal** 이다. **성격이 완전히 다르며 같은 타이머로 묶으면 안 된다.**

### 3.4 승인 유효기간 (참고 — 승인→매입 기한)

Visa 는 2024-04-13 부터 authorization validity 와 clearing 을 합쳐 단일 **authorization-to-clearing** 기간으로 통합했다. 출처: Visa Business News AI13522 (2023-10-19) **등급 A (PDF 원문 추출)**

| 거래 유형 | 최대 기간 |
|---|---|
| CNP (cardholder-initiated) | **10 캘린더일** |
| Estimated auth — 크루즈/숙박/렌터카 | **30 캘린더일** |
| Estimated auth — 기타 렌탈(항공기·자전거·보트·의류·장비·가구 등) | **10 캘린더일** |
| 그 외 모든 CP 거래 | **5 캘린더일** |
| 모든 MIT(할부·정기·선불·UCOF·환불) | **5 캘린더일** |

---

## 4. 멱등키 / 중복 전문 처리 — 얼마나 보관하는가

| 출처 | 보관 기간 | 원문 근거 | 등급 |
|---|---|---|---|
| **IETF** draft-ietf-httpapi-idempotency-key-header-07 (2025-10) | **수치 미규정** — 만료 정책은 **서버가 정의하고 문서에 공표해야 한다**고만 규정. *"The resource MAY require time based idempotency keys… the resource SHOULD define such expiration policy and publish it in the documentation."*, *"resources MUST publish an idempotency related specification, which MUST include expiration related policy if applicable."* | [IETF draft-07](https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-07.html) | **A** |
| **Stripe** | **24시간** — *"You can remove keys from the system automatically after they're at least 24 hours old"*, 프루닝 후 같은 키 재사용 시 **새 요청으로 처리**. 키 최대 255자. 파라미터가 다르면 에러 반환 | [Stripe API Reference — Idempotent requests](https://docs.stripe.com/api/idempotent_requests) | **A** |
| **NICEPAY** | 망취소 **1시간**, 중복 방지는 **orderId unique** 제약 | nicepay-manual/api/cancel.md | **A** |
| **ISO 8583 STAN(F11)/RRN(F37)** | **보관기간·중복탐지 윈도우 규정 없음.** F11 은 *"merchant-generated number that identifies the transaction… required field mirrored back in the response"* 로 식별자 정의만 있음. RRN 은 통상 처리일자 + STAN 조합 | Worldpay ISO 8583 Ref Guide V2.63 Field 011 정의 (원문 추출) / [Xflow](https://www.xflowpay.com/blog/rrn-retrieval-reference-number) | **A** / RRN 조합 설명은 **C** |
| **법정 보존 (한국)** | 전자금융거래법 제22조 ①: *"전자금융거래의 내용을 추적·검색하거나 그 내용에 오류가 발생할 경우에 이를 확인하거나 정정할 수 있는 기록을 생성하여 **5년의 범위 안에서 대통령령이 정하는 기간**동안 보존"*. 세부 기간은 시행령 제12조 | [전자금융거래법 제22조](https://www.law.go.kr/LSW//lsSideInfoP.do?lsiSeq=280277&joNo=0022&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR) | **B** (조문 인용은 검색 스니펫 기반, 시행령 제12조 각 호 원문은 **접근 차단으로 미확인**) |
| **가동기록 보존** | 전자금융감독규정 제13조 ⑨: 가동기록 **1년 이상** 보존 | [전자금융감독규정(제2025-4호)](https://ko.wikisource.org/wiki/전자금융감독규정_(제2025-4호)) | **B** |

> **핵심 발견**: 결제 도메인에 "멱등키는 N일 보관"이라는 **표준화된 관행은 없다**. 표준(IETF)은 명시적으로 "서버가 정하고 공표하라"고 위임한다. 실무 기준선은 **Stripe 24시간 / NICEPAY 1시간** 두 개가 공개 근거를 가진 유이한 값이다.
>
> 단, **멱등키 보관기간**과 **거래기록 법정 보존기간(5년)** 은 다른 것이다. 전자는 중복 요청 흡수용 단기 캐시, 후자는 감사·분쟁용 원장이다. 혼동하면 안 된다.

---

## 5. 정산 주기 (국내)

| 항목 | 값 | 출처 | 등급 |
|---|---|---|---|
| 신용판매대금 지급 기한 | 제12조 ①: **매출전표가 카드사에 접수된 날로부터 3영업일 이내** 지급 | [신용카드 가맹점 표준약관 (2024-04-20 시행) — 신한카드 게시본](https://www.shinhancard.com/pconts/html/helpdesk/terms/terms45/1186823_1199.html) | **A** |
| 매출전표 접수 기한 | 제9조 ①: 신용판매일로부터 **30일 이내** | 위와 동일 | **A** |
| 취소매출전표 제출 기한 | 제9조 ①: 작성일로부터 **3영업일 이내** | 위와 동일 | **A** |
| 지급예정일이 휴일인 경우 | **익영업일**에 지급 | 위와 동일 | **A** |
| 실무 체감 정산 | 대형 가맹점 D+1, 소규모 가맹점 D+2~D+3 | [리치페이 블로그](https://richpay.kr/column/card-sales-deposit-date/) 등 | **C** |
| **카드사 정산 마감 시각(cut-off time)** | **확인 실패** | — | **X — 출처 없음** |

> "D+2"는 **약관이 정한 값이 아니다.** 약관이 정하는 것은 *"매출전표 접수일 + 3영업일 이내"* 이고, D+n 은 매입 접수 시점이 언제 잡히느냐에 따라 결정되는 **결과값**이다. 설계 시 D+2 를 상수로 박으면 안 되고, **매입 접수 이벤트 기준 3영업일**을 모델로 삼아야 한다.
>
> **정산 마감 시각(예: 23:30 마감)은 공개 자료에서 찾지 못했다. 출처 없음 — 업계 통념.**

---

## 6. 가용성 SLA — 규제상 요구가 있는가

### 6.1 규제상 요구: **가동률(%) 수치 규제는 없다. RTO 규제는 있다.**

| 규정 | 내용 | 수치 | 출처 | 등급 |
|---|---|---|---|---|
| 전자금융감독규정 제23조 ⑨ | 핵심업무 **복구목표시간(RTO)** | **3시간 이내** (보험회사 핵심업무는 **24시간 이내**) | [전자금융감독규정(제2025-4호)](https://ko.wikisource.org/wiki/전자금융감독규정_(제2025-4호)), [IT위키 제23조](https://itwiki.kr/w/전자금융감독규정_제23조) | **B**(두 경로 교차 일치) |
| 전자금융감독규정 제23조 ⑧ | 재해복구센터를 **주전산센터와 일정거리 이상 떨어진 안전한 장소**에 구축·운용. 대상: 은행·산은·기은·농협은행·수협중앙회·투자매매/중개업자·증권금융·예탁결제원·거래소·**신용카드업자**·보험요율산출기관·저축은행중앙회·신협중앙회·보험회사 | 거리 수치 없음 | 위와 동일 | **B** |
| 전자금융감독규정 제23조 ① | 장애·재해·파업·테러 시에도 **업무가 중단되지 않도록** 업무지속성 확보방안 수립·준수 | 수치 없음 | 위와 동일 | **B** |
| 전자금융감독규정 제25조 | 정보처리시스템 **성능관리** — 사용 현황 및 추이 분석 **정기 실시** | **수치 없음** | 위와 동일 | **B** |
| 전자금융감독규정 제14조 ② | 모니터링시스템으로 시스템 자원 상태의 감시·경고·제어 | 수치 없음 | 위와 동일 | **B** |
| 금감원 「금융IT 안전성 강화를 위한 가이드라인」 (2023-11-08) | 전산자원 사용량 임계치를 **정상/주의/경계/심각 4단계**로 구분, 경계·심각 시 즉시 설비 증설 | **단계 구분만, % 수치는 공개 자료에서 미확인** | [KDI 경제정보센터 게시 보도자료](https://eiec.kdi.re.kr/policy/materialView.do?num=244509), [Kim&Chang 뉴스레터](https://www.kimchang.com/ko/insights/detail.kc?sch_section=4&idx=28401) | **B** |

### 6.2 실제 시중은행 공시 가용률

**확인 실패.** 금융위가 *"소비자가 금융회사별 보안 수준을 비교할 수 있도록 공시를 강화할 계획"* 이라고 밝힌 자료는 있으나, **개별 은행이 가동률(%)을 공시한 사례를 웹 검색으로 확인하지 못했다.**

→ **"국내 시중은행 가동률 99.9% 공시" 같은 수치는 출처 없음 — 업계 통념.** 근거 없이 인용하면 안 된다.

### 6.3 정리

- **규제는 "몇 %" 를 요구하지 않는다. "3시간 내 복구"를 요구한다.** 즉 한국 금융 규제의 가용성 축은 **가동률(uptime %)이 아니라 복구시간(RTO)** 이다.
- RTO 3시간을 연간 가용률로 환산하면 — **단일 재해 1회 기준** 3h/8760h ≈ 99.966% 에 해당하지만, **이는 규정이 명시한 값이 아니라 파생 계산이다.** 규정은 연간 누적 다운타임을 제한하지 않는다.

---

## 7. 이 프로젝트가 채택할 만한 값과 그 근거

> 원칙: **근거 등급 A/B 가 있는 값만 상수로 쓰고, X 등급은 상수가 아니라 "설정값 + 관측 후 조정" 으로 둔다.**

### 7.1 채택 권장

| 항목 | 권장값 | 근거 | 근거 강도 |
|---|---|---|---|
| 승인 요청 read timeout (대외 카드망/PG 방향) | **25~30초** (설정 가능하게) | Worldpay 가 ISO 8583 클라이언트에 **"at least 25 seconds"** 를 명시 (V2.63, 2026-03). 국제 카드망 실무의 유일한 공개 권장값 | **강함** |
| connect timeout | **3초** | NICEPAY 샘플 코드 `setConnectTimeout(3000)`. 연결 수립은 응답 처리와 무관하게 짧아야 함 | **약함** — 샘플 코드일 뿐 규약 아님. 단 "connect ≪ read" 라는 방향성은 타당 |
| 내부 서비스 간 승인 호출 timeout | **read timeout 의 60~70% 이하로 계층화** | 어떤 출처도 계층별 값을 주지 않음. 다만 Worldpay 의 "미응답 20건 초과 금지" 제약은 **상류 타임아웃이 하류보다 길면 큐가 쌓인다**는 것을 함의 | **약함 — 추론** |
| 타임아웃 발생 시 망취소 | **즉시 발송** (지연·배치 금지) | Worldpay Fig 3-3, NICEPAY, KICC 모두 "타임아웃 → 즉시 망취소". **국내외 일치하는 유일한 항목** | **강함** |
| 망취소 재시도 | **지수 백오프 + at-least-once, 수신측 멱등 흡수 전제** | ISO 8583 0421 의 종료조건이 "응답 수신"뿐 → 재전송은 무한정 가능한 구조. 횟수·간격 표준값은 **없음** | 구조는 **강함**, **구체 수치는 출처 없음 — 자체 결정 필요** |
| **망취소 유효기간(TTL)** | **1시간** | NICEPAY 가 명시적으로 1시간. 결제 도메인에서 공개 근거를 가진 **유일한 망취소 TTL** | **중간** — 단일 벤더 값이나 원문 명시 |
| **멱등키 보관 기간** | **24시간** | Stripe 원문 "at least 24 hours old" 후 삭제 가능. IETF 표준은 값을 위임하므로 **사실상 업계 레퍼런스가 Stripe 24시간** | **중간** — 표준 아님, 지배적 구현 관행 |
| 멱등키 정책 문서화 | **만료 정책을 API 문서에 반드시 공표** | IETF draft-07 의 **MUST** 요구사항 (*"resources MUST publish an idempotency related specification, which MUST include expiration related policy"*) | **강함** — 표준의 MUST |
| 멱등키 불일치 처리 | 같은 키 + 다른 파라미터 → **에러 반환** (조용히 통과 금지) | Stripe: *"compares incoming parameters to those of the original request and errors if they're not the same"* | **중간** |
| 거래기록 보존 | **5년** (감사·분쟁용 원장. 멱등키 캐시와 분리된 저장소) | 전자금융거래법 제22조 ① | **중간** — 시행령 제12조 각 호별 세부기간 미확인, **구현 전 반드시 시행령 원문 확인 필요** |
| 정산 모델 | **"매입 접수일 + 3영업일 이내" 를 도메인 규칙으로. D+2 를 상수화하지 말 것** | 신용카드 가맹점 표준약관 제12조 ① (2024-04-20 시행) | **강함** |
| 취소전표 처리 기한 | **3영업일** | 동 약관 제9조 ① | **강함** |
| 가용성 목표 | **RTO 3시간 이내** 를 1차 목표로 설계 (DR 구성 포함) | 전자금융감독규정 제23조 ⑨ — **규제 의무**. 신용카드업자는 제23조 ⑧ 재해복구센터 구축 대상 | **강함(규제)** |
| 가동률 SLA | **규제 근거 없음.** 내부 목표로만 설정하고 "규제 요구"라고 표기하지 말 것 | 규정에 % 수치 없음을 확인 | **강함(부재 확인)** |

### 7.2 채택하면 안 되는 값 / 주의

1. **"국제 카드사 승인 SLA 는 N초" 라고 쓰지 마라.** Visa 는 수치 SLA 를 공개하지 않는다. Mastercard 의 7초/40초는 **특정 제품 문서(Processing Debit / Cross-Border)** 의 값이지 범용 카드망 SLA 가 아니다.
2. **국내 VAN 승인 응답시간 규격은 확보하지 못했다.** 국내 연동을 전제로 설계한다면 이 값은 **미해결 리스크**다. 계약 시 규격서로 확인해야 하며, 그 전까지는 어떤 수치도 코드에 박으면 안 된다.
3. **Visa/Mastercard 의 "24시간 / 72시간 reversal" 을 기술 타임아웃 망취소와 같은 타이머로 다루지 마라.** 전자는 가맹점의 비즈니스 취소 의무, 후자는 통신 실패 복구다.
4. **"D+2 정산" 은 약관 근거가 없다.** 근거 있는 것은 "매출전표 접수일 + 3영업일 이내"뿐이다.
5. **"시중은행 가동률 99.9%" 는 출처를 찾지 못했다.** 인용 금지.
6. **정산 마감 시각(cut-off) 은 출처가 전혀 없다.** 설계에 필요하면 카드사/PG 에 직접 확인해야 한다.
7. **망취소 재시도 횟수·간격의 업계 표준값은 존재하지 않는다.** 자체 결정 사항이며, 결정 시 "이건 우리가 정한 값"이라고 문서에 남겨야 한다.

### 7.3 미해결 항목 (후속 조사 필요)

| 항목 | 왜 못 찾았나 | 확보 방법 |
|---|---|---|
| 국내 VAN 승인 응답시간·타임아웃 규격 | 연동규격서가 계약·NDA 배포, 웹에 없음 | VAN사 계약 시 규격서 수령 |
| 망취소 재시도 횟수·간격 | 표준·벤더 문서 모두 미규정 | 자체 정책 수립 + PG 확인 |
| 전자금융거래법 시행령 제12조 각 호별 보존기간 | LBOX 403 차단, 국가법령정보센터 원문 미열람 | law.go.kr 시행령 제12조 직접 확인 |
| 카드사 정산 마감 시각 | 공개 자료 없음 | 카드사/PG 직접 문의 |
| 국내 은행 가동률 공시 수치 | 공시 사례 확인 실패 | 각 은행 경영공시·금감원 공시자료 직접 조회 |
| Mastercard Transaction Processing Rules 원문의 reversal 기한 | PDF 다운로드 차단(505B 응답) | mastercard.us 에서 브라우저로 직접 수령 |
| 금감원 가이드라인 임계치 4단계의 실제 % | 보도자료에 수치 미포함 | 금감원 가이드라인 원문 입수 |

---

## 부록 — 원문 확인한 1차 자료 목록

| 자료 | 확인 방식 |
|---|---|
| Worldpay(Global Payments) ISO 8583 Reference Guide **V2.63 (2026-03)** | PDF 다운로드 → pdftotext 추출 → App. F.3 / Figure 3-3~3-5 / Field 011 원문 인용 |
| Visa Business News **Article ID AI13522 (2023-10-19)** — Authorization Framework Update | PDF 다운로드 → pdftotext 추출 → 시간표 전체 인용 |
| nicepay-manual `api/cancel.md` | GitHub 원문 |
| NICEPAY 인증 결제 API 매뉴얼 | 벤더 공식 문서 |
| 토스페이먼츠 개발자센터 — 타임아웃 | 벤더 공식 문서 |
| 신용카드 가맹점 표준약관 (2024-04-20 시행) | 신한카드 게시 원문 |
| 전자금융감독규정 (제2025-4호) | 위키문헌 + IT위키 교차 |
| IETF draft-ietf-httpapi-idempotency-key-header-07 (2025-10) | IETF 아카이브 |
| Stripe API Reference — Idempotent requests | 벤더 공식 문서 |
