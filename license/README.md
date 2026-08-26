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

## 지금 비어 있는 값 22개

`null` 인 항목은 화면에 **"확정 예정"** 으로 렌더링되고, JSON-LD 의 가격 필드에서는
아예 빠집니다. 없는 값을 지어내는 대신 비어 있음을 드러내는 쪽을 택했습니다.

| 분류 | 개수 | 내용 |
|---|---|---|
| 작품 스펙 | 15 | 5개 작품 × 러닝타임 · 해상도 · 비율 |
| 플랜 | 6 | 3개 플랜 × 월 구독료 · 계약 기간 |
| 문의 폼 | 1 | Formspree ID |

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
