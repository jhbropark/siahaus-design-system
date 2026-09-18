# SIA.HAUS 스튜디오 사이트 — `www.sia.haus`

아임웹에서 옮겨오는 소개 사이트입니다. 구조는 `license/` 와 같습니다.

```
data/site.json  ──build.py──▶  index.html   (본문 · JSON-LD 전부 인라인)
                               llms.txt
                               sitemap.xml
```

```bash
python build.py            # 생성
python build.py --check    # 파일을 쓰지 않고 검증만
```

---

## 왜 아임웹에서 옮기는가

아임웹에서 **할 수 없던 것**이 여기서는 전부 기본값입니다.

| 아임웹에서 | 여기서 |
|---|---|
| `VideoObject` 오류를 못 고침 (아임웹이 자동 삽입) | 마크업 전체가 우리 것 |
| `robots.txt` 편집 불가 | 파일로 관리 |
| `llms.txt` 업로드 지원 불확실 | 빌드 산출물 |
| 보안 헤더 설정 불가 | `vercel.json` |
| FAQPage 를 넣어도 본문에 문답이 없으면 위반 | 문답이 본문에 실제로 렌더링됨 |
| 관리자 로그인이 있어야 무엇이든 가능 | `main` push 가 곧 배포 |

특히 마지막 줄이 이 이사의 실질적인 이유입니다.

## 설계 원칙

**빌드 시점에 정적 HTML 로 펼칩니다.** JSON 을 클라이언트에서 fetch 해 렌더링하면
봇이 받는 원본 HTML 이 껍데기만 남습니다. 이 사이트의 목적이 생성형 엔진에 인용되는
것이므로 그 방식은 쓸 수 없습니다. `build.py` 는 출력물에 **JSON-LD 외의 `<script>` 가
섞이면 빌드를 실패시킵니다.**

**읽는 사람에게 보이는 문자열은 전부 `data/` 에 있습니다.** `build.py` 에는 문구가
없습니다. 문구를 고칠 때 파이썬을 열 일이 없어야 합니다.

**JSON-LD 는 화면에 있는 내용만 옮겨 적습니다.** 화면에 없는 내용을 스키마로만
선언하면 구조화 데이터 위반이 되고, 생성형 엔진도 근거 없는 주장으로 취급해 인용하지
않습니다. `FAQPage` 를 실을 수 있는 것은 같은 문답이 본문에도 렌더링되기 때문입니다.

## 엔티티 연결

`Organization` 의 `@id` 는 **세 곳에서 글자까지 같아야** 하나의 엔티티로 합쳐집니다.

```
www.sia.haus/#organization  ──subOrganization──▶  varis.kr/#organization
                            ◀──parentOrganization──
```

| 파일 | 역할 |
|---|---|
| `studio/data/site.json` → `site.org_id` | 이 사이트가 선언하는 자기 `@id` |
| `academy-varis/build_jsonld.py` → `PARENT_ORG_ID` | varis.kr 이 부모로 가리키는 값 |

두 곳뿐입니다. 아임웹 시절 스니펫(`infra/geo/imweb-head-snippet.html`)에도 같은
`@id` 가 있었지만, 붙여넣을 곳이 없어져 2026-09-16 에 삭제했습니다.

**대표 도메인을 non-www 로 바꾸면 위를 함께 고칠 것.** 한쪽만 고치면 관계가 조용히
끊기고, 끊겨도 아무 오류가 나지 않아 눈치채기 어렵습니다.

## 확정이 필요한 값

`data/site.json` 의 `licensing.launched` 는 **`false`** 입니다 — 구독 라이선싱이
아직 출시 전임을 2026-09-16 에 확인했습니다.

그래서 정의문이 "작가 IP로 축적하고 있습니다" 로 끝나고 라이선싱 FAQ 가 빠집니다.
**출시하면 `true` 로 바꾸면** 정의문 뒷부분과 FAQ 가 함께 복구됩니다. 없는 서비스를
정의문에 넣으면 첫 문의부터 어긋나기 때문에, 모를 때 더 크게 주장하지 않습니다.

`license/` 사이트(구독 라이선싱 카탈로그)도 **출시 전에는 배포하지 마세요.**

그 밖에 값이 생기면 채울 곳:

| 항목 | 넣을 자리 |
|---|---|
| 대표 전화번호 | `site.telephone` 추가 후 `build_jsonld` 에 연결 |
| 사업자등록번호 | 공개 시 신뢰도 신호로 유효 |
| 인스타·유튜브·링크드인 | `site.same_as` 배열 |

## 실적 연도

`work.items` 의 `year` 는 **확인된 것만** 채워져 있습니다. 출처는
`infra/geo/llms.txt` 와 `project/readme.md` 이며, 그 두 곳에 연도가 없는 항목은
비워 뒀습니다. 화면에서는 연도 칸이 그냥 비고, `llms.txt` 에서도 빠집니다.
아는 연도가 있으면 채우시면 됩니다 — **추정해서 넣지 마세요.**

## 배포

Vercel 정적 배포. Root Directory 는 `studio` 입니다.

`vercel.json` 의 `Strict-Transport-Security` 가 **`max-age=300`(5분)** 인 것은
의도적입니다. 지금 `sia.haus` 는 HTTPS 강제가 안 걸려 있어, 긴 HSTS 를 먼저 걸면
전환 중 문제가 생겼을 때 브라우저가 몇 달간 http 로 못 돌아갑니다.
**도메인 전환이 끝나고 https 가 확실히 동작하는 것을 확인한 뒤** 올리세요
(varis.kr 은 `max-age=63072000`).

### 전환 순서

1. ~~Vercel 프로젝트를 이 저장소에 연결 (Root Directory `studio`)~~ ✅ 완료
2. ~~프리뷰 URL 로 내용 확인~~ ✅ 완료 — https://siahaus-design-system.vercel.app
3. 옛 URL → 새 주소 301 `redirects` 작성 ← **진행 중, 아래 참고**
4. DNS 를 Vercel 로 전환
5. https 확인 후 HSTS `max-age` 상향

3번을 건너뛰면 **기존 검색 순위를 그대로 날립니다.** 옛 주소를 알아야 리다이렉트를 깝니다.

### DNS — 전환 시 알아둘 것

`sia.haus` 의 네임서버는 **이미 Cloudflare** 입니다 (`liz.ns.cloudflare.com` ·
`curt.ns.cloudflare.com`). 아임웹은 호스팅만 하고 있으므로 **DNS 전환에 아임웹의
허락이 필요하지 않습니다.** Cloudflare 에서 레코드만 바꾸면 됩니다.

도메인 등록기관은 아임웹으로 보이며 Cloudflare Registrar 로 이전 예정입니다.
등록기관 이전은 DNS 를 건드리지 않아 사이트 동작과 무관하지만, **이전이 끝나기 전에
아임웹을 해지하면 도메인이 위험합니다.**

전환 후에는 아임웹 쪽 리다이렉트 문제(`sia.haus` → 302 → `http://www.sia.haus`)가
저절로 사라집니다. Vercel 이 apex→www 를 HTTPS 로 308 처리합니다.

## 리다이렉트 맵

`vercel.json` 의 `redirects` 에 있습니다. `statusCode: 301` 을 명시합니다 —
`permanent: true` 는 308 을 내보내는데, 301 이 검색엔진 문서에서 다루는 기준값입니다.

| 옛 주소 | 새 주소 | 확인 상태 |
|---|---|---|
| `/about` | `/` | ❓ 미확인 |
| `/contact` | `/#contact` | ❓ 미확인 |

**이 목록은 잠정입니다.** 아임웹 사이트를 이 작업 환경에서 읽을 수 없어
(egress 차단) 검색 인덱스와 대화 기록에서 모은 경로입니다. 존재하지 않는 경로에
대한 규칙은 그냥 발동하지 않으므로 해롭지는 않지만, **빠진 페이지는 전환과 동시에
검색에서 사라집니다.**

확정하려면 사이트에서 메뉴를 클릭해 주소를 직접 모아야 합니다.

`trailingSlash: false` 라 `/contact/` 는 `/contact` 로 정규화되므로 규칙 하나가
두 형태를 모두 덮습니다.

### 미결 — 프로젝트 상세 페이지

`/universe-cube` 같은 **프로젝트 상세 페이지가 옛 사이트에 있습니다.** 이 사이트는
단일 페이지라 대응할 곳이 없습니다. 일부러 리다이렉트를 넣지 않았습니다.

| 선택 | 결과 |
|---|---|
| 그대로 두기 (404) | 해당 페이지 색인·순위·내용 소실. 구글은 삭제된 콘텐츠에 404 를 선호합니다 |
| 이 사이트에 상세 페이지 추가 | 제작 필요. 아임웹에 **본문 내보내기가 없어** 손으로 옮겨야 합니다 |
| Behance 로 301 | 내용은 살지만 트래픽이 외부로 나갑니다 |

무관한 페이지로 리다이렉트하는 것(예: `/#work`)은 soft-404 로 취급돼 **하지 않는
편이 낫습니다.**
