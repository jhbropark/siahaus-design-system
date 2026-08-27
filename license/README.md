# SIA.HAUS 라이선스 — 구독 라이선싱 MVP

미디어아트를 구독으로 빌려 쓰는 서비스의 카탈로그 페이지입니다.
공간 사업자가 **작품을 둘러보고 → 플랜을 비교하고 → 문의를 남기는** 흐름까지 완성돼 있습니다.

배포 대상: `license.sia.haus` (Vercel 정적 배포)

---

## 왜 이 구조인가

**내용을 빌드 시점에 정적 HTML 로 펼칩니다. JS 렌더링을 쓰지 않습니다.**

`data/site.json` 하나가 단일 진실 원천이고, `build.py` 가 이를 읽어
`index.html` · `llms.txt` · `sitemap.xml` 을 생성합니다.

```
data/site.json  ──build.py──▶  index.html   (본문 · JSON-LD 전부 인라인)
                               llms.txt
                               sitemap.xml
```

JSON 을 클라이언트에서 fetch 해 렌더링하면 봇이 받는 원본 HTML 이 껍데기만 남습니다.
이 사이트의 목적 자체가 생성형 엔진에 인용되는 것이라 그 방식은 쓸 수 없습니다.
현재 `index.html` 의 `<script>` 는 **JSON-LD 하나뿐이고 실행 스크립트는 0개**입니다.

## 로케일 — 한국어 · 영어

`data/` 의 파일 하나가 로케일 하나입니다.

| 파일 | 로케일 | 출력 | URL |
|---|---|---|---|
| `data/site.json` | ko | `index.html` · `llms.txt` | `https://license.sia.haus/` |
| `data/site.en.json` | en | `en/index.html` · `en/llms.txt` | `https://license.sia.haus/en/` |

`sitemap.xml` 은 루트에 하나만 두고 두 URL 을 `xhtml:link` 로 서로 연결합니다.
페이지끼리는 `hreflang` 으로 상호 참조하며 `x-default` 는 한국어 루트입니다.
내비게이션의 언어 전환 링크도 자동 생성됩니다.

### 읽는 사람에게 보이는 문자열은 전부 데이터에 있습니다

내비 라벨, 버튼, 스펙 제목, 메일 본문 초안, "확정 예정" 까지 **29종이 각 로케일의
`strings` 블록**에 있습니다. 템플릿에는 한국어가 남아 있지 않습니다.

처음 영어 빌드를 돌렸을 때 **영어 페이지가 한국어 가구를 쓰고 있었습니다** —
본문만 번역되고 내비와 버튼은 한국어였습니다. 그래서 전부 데이터로 뺐습니다.

### 영어는 미국식 철자로 씁니다

제품 이름이 `SIA.HAUS License` 입니다. **영국식으로 쓰면 명사가 `licence`, 동사가
`license` 라 한 페이지에 두 철자가 계속 나옵니다** — 브랜드명은 Licence 인데 본문은
"we license the work" 가 되는 식입니다.

그래서 `catalog` · `standardized` · `organization` 처럼 미국식으로 통일했습니다.
문구를 추가하실 때도 미국식으로 맞춰 주세요.

### 로케일을 더 추가하려면

1. `data/site.<코드>.json` 을 만들고 `site.locale` · `site.path` · `site.url` 을 채운다
2. `build.py` 상단 `DATA_FILES` 에 경로를 추가한다

hreflang · sitemap · 언어 전환은 자동으로 따라옵니다.

### 두 파일은 같은 사실을 담아야 합니다

작품 id, 플랜 id, 주소, 이메일은 **양쪽이 동일해야 합니다.** 문구만 다릅니다.
검증용 스니펫:

```bash
python3 -c "
import json
ko=json.load(open('data/site.json')); en=json.load(open('data/site.en.json'))
assert [w['id'] for w in ko['catalog']['works']]==[w['id'] for w in en['catalog']['works']]
assert [p['id'] for p in ko['plans']['items']]==[p['id'] for p in en['plans']['items']]
assert ko['site']['email']==en['site']['email']
print('사실 일치 OK')"
```

미확정 값은 **로케일별로 표시**됩니다(`[ko]` / `[en]`). 별개 파일이라 양쪽 다 채워야 합니다.

## 사용법

```bash
python3 build.py            # 생성
python3 build.py --check    # 파일을 쓰지 않고 검증만
```

값을 바꿀 때는 **`data/site.json` 만 고치고 다시 빌드**하세요.
`index.html` 을 직접 손대면 다음 빌드에서 덮어써집니다.

빌드는 끝날 때마다 **아직 채우지 않은 값의 개수와 경로를 출력**합니다.

```
⚠️  확정 필요 값 22개 — data/site.json 에서 채우세요
     · works.seoul-pulse.runtime
     · plans.single.price_monthly
     ...
```

## 가격은 별도 문의 — 정책입니다

`plans.pricing_mode` 가 `"quote"` 이면 세 플랜 모두 **"별도 문의"** 로 렌더링되고,
JSON-LD 의 `Offer` 에서 `priceSpecification` 이 **빠집니다.**

**이건 미확정 값이 아니라 결정된 정책이므로 빌드 경고에 잡히지 않습니다.**
화면에서도 미확정 표기(점선 밑줄)와 다르게 보입니다.

나중에 정가를 공개하기로 하면 각 플랜의 `price_monthly` 에 숫자를 넣으세요.
값이 있으면 `pricing_mode` 와 무관하게 금액이 우선 렌더링되고, JSON-LD 에도
`priceSpecification` 이 다시 들어갑니다.

## 해상도는 작품 속성이 아니라 납품 조건입니다

처음에는 작품마다 `resolution` 필드를 뒀으나 **제거했습니다.**

이 서비스는 "공간 규격에 맞춘 재출력"을 약속합니다. 그런데 작품 카드가
`3840×2160` 같은 고정 해상도를 표시하면 **그 약속과 정면으로 어긋납니다.**
공간 사업자가 자기 화면 규격과 다른 숫자를 보고 "우리 벽에는 안 맞는다" 고
판단할 이유가 없어야 합니다.

해상도는 카탈로그 도입부에 **서비스 수준 문구**로 한 번만 말합니다.

> 해상도는 공간의 화면 규격에 맞춰 재출력해 공급합니다.

작품별로 남긴 값은 **러닝타임**과 **원본 비율** 둘뿐입니다. 러닝타임은 루프 길이라
공간 운영 계획에 직접 쓰이고, 원본 비율은 재출력의 출발점이라 둘 다 실제 정보입니다.

## 값이 없는 스펙 행은 숨길 수 있습니다

`catalog.hide_unknown_specs` 가 `true` 이면 **값이 없는 스펙 행을 카드에서 아예 빼고**,
한 작품의 스펙이 전부 비어 있으면 `<dl>` 자체를 내보내지 않습니다.
카탈로그 도입부의 "각 카드에 표기했습니다" 문장도 표시할 스펙이 하나도 없으면 빠집니다.

`false` 로 두면 예전처럼 **"확정 예정"** 이 표시됩니다.

```jsonc
"catalog": { "hide_unknown_specs": true }
```

**숨겨도 빌드 경고에서는 사라지지 않습니다.** 화면에서 안 보이는 것과 값이 채워진 것은
다르고, 경고까지 조용해지면 그 값은 영영 안 채워집니다. 빌드는 숨긴 개수를 따로 알려줍니다.

```
스펙 행 10개는 값이 없어 화면에서 숨겼습니다 (hide_unknown_specs=true)

⚠️  확정 필요 값 11개 — data/site.json 에서 채우세요
```

값을 하나만 채워도 그 행만 나타납니다 — 전부 채울 때까지 기다릴 필요 없습니다.

## 지금 비어 있는 값 11개

`null` 인 항목은 화면에 **"확정 예정"** 으로 렌더링됩니다.
없는 값을 지어내는 대신 비어 있음을 드러내는 쪽을 택했습니다.

| 분류 | 개수 | 내용 |
|---|---|---|
| 작품 스펙 | 10 | 5개 작품 × 러닝타임 · 원본 비율 |
| 문의 폼 | 1 | Formspree ID |

이 10개는 **저장소 어디에도 없는 값입니다.** `project/uploads/` 의 73페이지 브리프를
전부 복호해 검색했지만 해상도 · 러닝타임 · 비율 관련 수치가 한 건도 없습니다
(포트폴리오 덱이라 프로젝트명 · 클라이언트 · 연도만 담겨 있습니다).

작품 원본 파일을 아는 사람이 채워야 합니다.

**Formspree ID 가 없는 동안에는** 문의 섹션이 폼 대신 **항목이 채워진 메일 링크**로
렌더링됩니다. 지금 배포해도 문의를 받을 수 있습니다.
ID 를 넣으면 자동으로 폼으로 바뀝니다.

## 이미지

작품 이미지는 **톤 자리표시자**(CSS 그라디언트)입니다.
디자인 시스템 readme 의 방침과 같습니다 — 실제 작품 스틸로 교체하세요.

교체 시 `data/site.json` 의 각 작품에 `image` 필드를 추가하고 `build.py` 의
`work-visual` 렌더링을 `<img>` 로 바꾸면 됩니다. alt 는 작품명 + 종류로 채우세요.

## 검증

```bash
python3 build.py --check
```

빌드 자체가 생성된 JSON-LD 를 파싱해 확인합니다. 실패하면 빌드가 멈춥니다.

배포 후:

```bash
# 정의문이 JS 실행 전 원본 HTML 에 있는가 — 이 사이트의 존재 이유
curl -s https://license.sia.haus/ | grep -o '구독 방식으로 빌려 쓰는 서비스'

# 구조화 데이터 타입
curl -s https://license.sia.haus/ | grep -oE '"@type": *"[^"]+"' | sort -u

# GEO 파일 3종
for f in robots.txt sitemap.xml llms.txt; do
  printf "%-14s " "$f"; curl -s -o /dev/null -w "%{http_code}\n" "https://license.sia.haus/$f"
done
```

구조화 데이터: https://validator.schema.org/ 에 `https://license.sia.haus/` 입력.
`WebSite` · `Service` · `ItemList` · `FAQPage` 가 잡혀야 합니다.

## 서비스 범위는 전 세계입니다

`site.area_served` 가 `"Worldwide"` 이고 JSON-LD 의 `Service.areaServed` 로 나갑니다.

처음에는 `{"@type":"Country","name":"KR"}` 이었는데, **그러면 생성형 엔진이 해외 문의에
"한국 내 서비스"라고 답합니다.** 밀라노 디자인위크·베니스 비엔날레 실적이 있는
스튜디오에는 맞지 않는 선언이었습니다.

특정 국가로 좁히려면 이 값을 바꾸세요. 문자열, 또는 `Country` 객체 배열도 됩니다.

## 엔티티 연결

`Service` 와 `WebSite` 가 `https://www.sia.haus/#organization` 을 참조합니다.
sia.haus 본체의 Organization 스키마(`infra/geo/imweb-head-snippet.html`)를 붙여넣어야
이 참조가 성립합니다. **본체 적용이 선행되어야 합니다.**

```
license.sia.haus/#service ──provider──▶ www.sia.haus/#organization
                                              │
                                        subOrganization
                                              ▼
                                        varis.kr/#organization
```

## 배포

```bash
cd license
vercel deploy --prod --yes
```

`vercel.json` 이 보안 헤더 5종을 붙입니다. 아임웹인 sia.haus 본체와 달리
이쪽은 Vercel 이라 헤더를 직접 설정할 수 있어, 본체에서 포기했던 항목을 여기서는 켭니다.
HSTS 는 `max-age=300` 으로 시작합니다 — 정상 확인 후 단계적으로 올리세요.

## 아직 정해지지 않은 것 — 코드보다 먼저

| 항목 | 왜 중요한가 |
|---|---|
| **라이선스 약관** | 상영 범위(단일 공간/체인), 재배포 금지, 크레딧 표기 의무, 계약 종료 후 파일 파기 |
| **자산 전달 방식** | 다운로드 링크 · 물리 매체 · 현장 설치 중 무엇인지에 따라 운영 부담이 완전히 달라집니다 |
| **작품별 권리 상태** | 커미션 작품은 발주처와 권리가 나뉘어 있을 수 있습니다. **카탈로그에 올리기 전에 작품별로 확인이 필요합니다** |
| **재출력 범위** | "공간 규격에 맞춘 재출력"의 실제 작업량 — 단순 리사이즈인지 재렌더링인지 |

특히 **작품별 권리 상태**는 법적 위험이 있는 항목입니다.
그랜드 조선·김창열 아틀리에처럼 발주처가 명확한 작품은 재라이선싱 가능 여부를
계약서로 확인한 뒤 카탈로그에 올리세요.
