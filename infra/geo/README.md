# sia.haus GEO (Generative Engine Optimization)

생성형 엔진이 sia.haus 를 **읽고 · 인용하고 · 유입으로 연결**하도록 만드는 작업입니다.
2026-08-21 진단 기준.

## 저장소가 없다는 전제

sia.haus 는 아임웹(Imweb)으로 만든 사이트라 **소스 저장소가 없습니다.**
CDN(CloudFront)과 오리진(Nginx)이 모두 빌더 소유입니다. 따라서 이 폴더는 배포되는
코드가 아니라 **아임웹 관리자에 붙여넣을 자산과 그 근거**를 버전 관리하는 곳입니다.

| 파일 | 용도 |
|---|---|
| `imweb-head-snippet.html` | 아임웹 head 커스텀 HTML 에 붙여넣을 JSON-LD |
| `page-copy-draft.md` | 페이지 본문에 노출할 정의문 · FAQ 문안 |
| `llms.txt` | 루트 게시가 가능해지면 올릴 파일 |

---

## 진단 결과 (2026-08-21)

세 도메인 모두 이 작업 환경에서 egress 차단이라 `curl` 로 원본 HTML 을 직접 뜨지
못했습니다. 아래 **[크롤러]** 표시 항목은 서버에서 실제 사이트를 읽는 외부 도구의
결과이며, 1차 증거가 아닙니다. 배포 후 아래 "확인 절차"로 직접 검증하세요.

| # | 항목 | 단계 | 현황 |
|---|---|---|---|
| 1 | 렌더링 구조 | 읽기 | ✅ 서버 렌더링. 원본 HTML 에 본문 존재 [크롤러] |
| 2 | robots.txt AI 봇 | 읽기 | ⚠️ AI 크롤러 지시문 미검출 (차단은 아님, 기본 허용) |
| 3 | llms.txt | 읽기 | ⚠️ "존재"로 검출되나 soft-404 오탐 가능성 |
| 4 | Organization JSON-LD | 가져다쓰기 | ❌ 없음. `OnlineStore` 만 존재 (아임웹 자동 삽입 추정) |
| 5 | FAQ / FAQPage | 가져다쓰기 | ❌ 없음 |
| 6 | 본문 정의문 | 가져다쓰기 | 🔸 meta description 에만 존재. 화면 노출 확인 필요 |
| 7 | 엔티티 연결 | 가져다쓰기 | ❌ VARIS(varis.kr)와 스키마상 연결 없음 |
| 8 | HTTPS 강제 | 찾아가기 | ❌ 미적용 (`http://` → 301 → `http://www` → 200) |

> 아임웹이 자동으로 넣는 노드는 `OnlineStore` 뿐이 아닙니다 —
> [아임웹이 넣는 마크업은 우리가 못 고친다](#아임웹이-넣는-마크업은-우리가-못-고친다-2026-09-04) 참고.

**읽기 단계는 통과했고, 가져다쓰기가 통째로 비어 있습니다.** 아임웹이 서버에서
HTML 을 렌더링하므로 봇이 본문을 못 읽는 문제는 없습니다. 문제는 읽은 내용에
"이 회사가 무엇인가"를 기계가 확정할 근거가 없다는 것입니다.

### 3번 항목에 대한 주의

외부 크롤러가 `/llms.txt` 를 "존재"로 보고했지만 **믿지 마세요.** 많은 빌더가 없는
경로에도 200 과 HTML 을 돌려줍니다(soft 404). 아래로 직접 확인하세요.

```bash
curl -sI https://sia.haus/llms.txt | head -1        # 200 이어도
curl -s  https://sia.haus/llms.txt | head -c 200    # HTML 이 나오면 없는 것
```

---

## 전략 — 왜 이 순서인가

아임웹에서 할 수 있는 것과 없는 것이 갈립니다. **할 수 있는 것부터, 효과 큰 순으로.**

| 순위 | 작업 | 단계 | 실현성 |
|---|---|---|---|
| 🔴 1 | 본문 정의문 노출 | 가져다쓰기 | ⭕ 페이지 편집 |
| 🔴 2 | Organization + WebSite JSON-LD | 가져다쓰기 | ⭕ head 삽입 |
| 🟠 3 | FAQ 본문 + FAQPage JSON-LD | 가져다쓰기 | ⭕ 페이지 편집 + head |
| 🟠 4 | HTTPS 강제 + canonical www 확정 | 찾아가기 | ⭕ 아임웹 설정 — 아래 참고 |
| 🟡 5 | llms.txt 게시 | 읽기 | ❓ 루트 파일 업로드 지원 여부 |
| ⬜ 6 | robots.txt 수정 | 읽기 | ❌ 어려움 — 단, **차단 상태가 아니라 급하지 않음** |

### 5·6번을 뒤로 미루는 이유

`llms.txt` 는 **표준이 아니라 관행**입니다. 크롤러가 읽는다는 보장이 없습니다.
`robots.txt` 도 AI 봇 지시문이 없을 뿐 차단된 상태가 아니라, 기본값이 허용입니다.

**둘 다 없어도 인용은 됩니다. 화면에 인용할 문장이 없으면 둘 다 있어도 인용되지
않습니다.** 그래서 1~3번이 먼저입니다.

### canonical 은 www 로 확정 (2026-08-21)

현재 `sia.haus` → 301 → `www.sia.haus` 로 가고 있어 **www 를 정본으로 유지**합니다.
스니펫의 모든 URL 이 `https://www.sia.haus/` 기준입니다.

**HTTPS 강제 설정과 한 번에 처리하세요.** 지금은 리다이렉트가 `http://sia.haus` →
`http://www.sia.haus` 로 끝나 평문에 머무릅니다. 목표 형태는 이것입니다.

```
http://sia.haus       ─┐
http://www.sia.haus   ─┼─▶  https://www.sia.haus/   (301, 한 번에)
https://sia.haus      ─┘
```

리다이렉트를 두 번 태우면(평문 www 를 거쳐 https 로) 체인이 길어지고 첫 구간이
평문으로 남습니다. 아임웹 설정에서 **HTTPS 강제와 www 통일이 한 단계로 처리되는지**
확인하고, 나뉘어 있으면 둘 다 켜세요.

확인:

```bash
curl -sI http://sia.haus      | grep -iE '^(HTTP|location)'
curl -sI http://www.sia.haus  | grep -iE '^(HTTP|location)'
curl -sI https://sia.haus     | grep -iE '^(HTTP|location)'
```

세 경우 모두 최종 도착지가 `https://www.sia.haus/` 여야 합니다.

### 엔티티 연결 — 두 도메인을 하나의 주체로

Organization 스키마에 `subOrganization` 으로 varis.kr 을 연결했습니다.

```
https://www.sia.haus/#organization  ──subOrganization──▶  https://varis.kr/#organization
```

varis.kr 에는 이미 `EducationalOrganization` 이 `@id: https://varis.kr/#organization`
로 선언돼 있어 참조가 성립합니다. 두 사이트가 별개 브랜드로 흩어지지 않고 하나의
엔티티 그래프로 묶이면, 한쪽에서 쌓은 신뢰가 다른 쪽 질의에도 작동합니다.

> **varis.kr 쪽에 상호 참조를 추가하면 더 강해집니다.**
> `build_jsonld.py` 의 `ORGANIZATION` 에 아래를 넣고 다시 실행하세요.
> ```python
> "parentOrganization": {"@id": "https://www.sia.haus/#organization"}
> ```
> 단방향도 유효하지만 양방향이 확실합니다.

---

## 적용 절차

**순서를 지켜야 합니다. FAQPage 를 먼저 넣으면 위반입니다.**

1. **`page-copy-draft.md` 의 정의문**을 아임웹 페이지 본문에 노출
2. **FAQ 문답 5개**를 페이지 하단에 노출 (문안 그대로)
3. 아임웹 관리자 → 사이트 설정 → 고급 설정 → **head 커스텀 HTML** 에
   `imweb-head-snippet.html` 붙여넣기
4. 2번을 마쳤으면 스니펫 안의 **FAQPage 주석 해제**
5. 아임웹 SEO 설정에서 title 60자 / description 155자 / OG 이미지 확인
6. 루트 파일 업로드가 가능하면 `llms.txt` 게시

---

## 확인 절차 (배포 후)

```bash
# 1. 정의문이 JS 실행 전 원본 HTML 에 있는가 — GEO 의 핵심
curl -s https://www.sia.haus/ | grep -o '수직통합형'

# 2. JSON-LD 가 실제로 주입됐는가
curl -s https://www.sia.haus/ | grep -c 'application/ld+json'

# 3. 스키마 타입 확인
curl -s https://www.sia.haus/ | grep -oE '"@type": *"[^"]+"' | sort -u

# 4. llms.txt 가 진짜인가 (HTML 이 나오면 soft-404)
curl -s https://sia.haus/llms.txt | head -c 200

# 5. HTTPS 강제 여부
curl -sI http://sia.haus | head -3
```

구조화 데이터 검증: https://validator.schema.org/ 에 `https://www.sia.haus/` 입력.
`Organization` · `WebSite` (그리고 4단계 후 `FAQPage`) 가 잡혀야 합니다.

---

---

## 아임웹이 넣는 마크업은 우리가 못 고친다 (2026-09-04)

Search Console 이 sia.haus 의 `VideoObject` 구조화 데이터에서 **심각한 문제 2건**을
보고했습니다.

| 오류 | 의미 |
|---|---|
| `uploadDate` 입력란이 누락되었습니다 | 영상 게시일이 없음 — 필수 속성 |
| `name` 입력란이 누락되었습니다 | 영상 제목이 없음 — 필수 속성 |

### 무엇을 잃는가 — 색인이 아니라 리치 결과다

"심각한 문제"라는 문구 때문에 페이지가 검색에서 빠진 것으로 읽히지만 그렇지 않습니다.

| 잃는 것 | 유지되는 것 |
|---|---|
| 동영상 리치 결과 (썸네일·재생시간 노출) | 페이지 색인 |
| 동영상 검색 탭 노출 | 일반 검색 순위 |
| | 기존 트래픽 |

구조화 데이터가 **무효**해서 그 항목이 리치 결과 후보에서 빠지는 것이지, 페이지가
평가절하되는 것이 아닙니다. 긴급 장애가 아니라 **못 받고 있는 노출**입니다.

### 이 폴더의 스니펫으로는 못 고친다

진단 때 발견한 `OnlineStore` 노드와 같은 출처 — **아임웹이 자동으로 삽입하는
마크업**으로 보입니다. `imweb-head-snippet.html` 은 `Organization` 과 `WebSite`
노드를 **추가**할 뿐이고, 아임웹이 넣는 노드를 수정하거나 제거할 수 없습니다.
head 커스텀 HTML 은 문서에 태그를 덧붙이는 자리이지 기존 노드를 편집하는
자리가 아닙니다.

즉 이 문제는 **적용 절차와 별개 트랙**입니다. 스니펫 적용을 미룰 이유도, 스니펫을
적용했다고 해결될 일도 아닙니다.

### 대응 절차

1. **Search Console → 동영상 페이지 보고서**에서 영향받은 URL 목록을 확인합니다.
   전체 페이지인지 특정 동영상 블록이 있는 페이지들뿐인지가 갈림길입니다.
2. 그중 한 URL 을 [Rich Results Test](https://search.google.com/test/rich-results)
   에 넣고 `VideoObject` 노드의 **원본 JSON-LD 를 직접 봅니다.**
3. 본 내용에 따라 갈립니다.

| 관찰 | 원인 | 대응 |
|---|---|---|
| `name` 이 빈 문자열 | 아임웹 동영상 블록의 제목 칸이 비어 있음 | **관리자에서 제목을 채우면 해결** |
| `name` 키 자체가 없음 | 아임웹이 아예 안 넣음 | 아임웹 문의 |
| `uploadDate` 키가 없음 | 아임웹이 게시일을 매핑하지 않음 — 플랫폼 버그 쪽 | 아임웹 문의 |

`name` 은 사용자가 채울 수 있는 값일 가능성이 있지만, `uploadDate` 는 관리자
화면에 입력란이 없는 것이 보통이라 **빌더가 고쳐야 합니다.**

### 아임웹 문의 문안

> 사이트(sia.haus)의 동영상 블록에서 자동 생성되는 `VideoObject` 구조화 데이터에
> 필수 속성 `uploadDate` 와 `name` 이 누락되어, Google Search Console 에서 심각한
> 오류로 보고되고 동영상 리치 결과가 노출되지 않습니다. 동영상 블록이 출력하는
> JSON-LD 에 두 속성을 포함해 주실 수 있는지, 또는 관리자에서 채울 수 있는
> 입력란이 있는지 확인 부탁드립니다.

### sia.haus 의 Search Console 계정이 다르다

이 작업 환경에 연결된 Search Console 계정에는 `sc-domain:varis.kr` 만 있습니다.
**sia.haus 속성은 다른 구글 계정에 등록되어 있어** 여기서 조회·검증할 수 없습니다.
sitemap 제출이나 URL 검사도 마찬가지이니, sia.haus 관련 Search Console 작업은
해당 계정으로 직접 하시거나 이 계정을 소유자로 추가해야 합니다.

## GEO 인용 모니터링 — 질문 셋 (실행 전, 리스트업만)

ChatGPT · Perplexity · Gemini 에 **월 1회** 던지고 sia.haus 인용 여부를 기록합니다.
브랜드명을 넣지 않은 3~5번에서 잡히는지가 실제 성과입니다.

| # | 질문 | 확인 대상 |
|---|---|---|
| 1 | SIA.HAUS는 어떤 회사인가요? | 정의문이 그대로 인용되는가 |
| 2 | SIA.HAUS와 일반 영상 제작사의 차이가 뭔가요? | 수직통합 문장 인용 여부 |
| 3 | 미디어 파사드 제작할 수 있는 국내 스튜디오 추천해 줘 | 브랜드명 없이 등장하는가 |
| 4 | 건물 외벽 미디어아트를 구독처럼 빌려 쓸 수 있나요? | IP 라이선싱 문장이 잡히는가 |
| 5 | 몰입형 전시 기획부터 운영까지 맡길 수 있는 곳 있어? | 파이프라인 문장이 잡히는가 |

기록 항목: 날짜 / 엔진 / 인용 여부 / 인용된 문장 / 링크 노출 여부.

**인용되지 않을 때 llms.txt 부터 의심하지 마세요.** 대부분 화면 본문에 인용할
문장이 없어서입니다.

---

## 구독 라이선싱 제품 — `license/`

정의문이 말하는 구독 라이선싱의 실제 페이지는 [`../../license/`](../../license/) 에
만들어져 있습니다 (`license.sia.haus`, Vercel 정적 배포).

**본체 스키마 적용이 선행되어야 합니다.** `license.sia.haus` 의 `Service` 가
`https://www.sia.haus/#organization` 을 참조하는데, 이 폴더의 스니펫을 아임웹에
붙여넣기 전까지는 그 대상이 존재하지 않습니다.

```
license.sia.haus/#service ──provider──▶ www.sia.haus/#organization  ← 아임웹 head
                                              │
                                        subOrganization
                                              ▼
                                        varis.kr/#organization      ← 이미 존재
```

> **정의문의 "라이선싱합니다" 는 license.sia.haus 가 배포된 시점부터 참입니다.**
> 그 전에 본체에 정의문을 올리면 없는 서비스를 설명하게 됩니다.
> 순서는 ① license 배포 → ② 본체 정의문·스키마 적용 입니다.

## 확정이 필요한 값

`page-copy-draft.md` 3번 표를 보세요. 가장 중요한 것은 **구독 라이선싱 출시 여부**입니다.
아직 출시 전이라면 정의문 뒷부분과 FAQ 3번을 빼야 합니다.
