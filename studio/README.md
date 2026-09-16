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
| 관리자 로그인이 있어야 무엇이든 가능 | `master` push 가 곧 배포 |

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

`data/site.json` 의 `licensing.launched` 가 `null` 입니다.

구독 라이선싱이 **실제로 운영 중이면 `true`** 로 바꾸세요. `null` 인 동안 `build.py` 는
안전한 쪽을 택합니다 — 정의문을 "작가 IP로 축적하고 있습니다" 로 쓰고, 라이선싱 FAQ 를
빼고, 빌드할 때마다 경고를 출력합니다. 없는 서비스를 정의문에 넣으면 첫 문의부터
어긋나기 때문에 모를 때 더 크게 주장하지 않습니다.

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

1. Vercel 프로젝트를 이 저장소에 연결 (Root Directory `studio`)
2. 프리뷰 URL 로 내용 확인 — **이 단계까지는 현재 사이트를 건드리지 않습니다**
3. 아임웹에 있는 기존 URL 목록을 확보해 `vercel.json` 에 301 `redirects` 작성
4. DNS 를 Vercel 로 전환
5. https 확인 후 HSTS `max-age` 상향

3번을 건너뛰면 **기존 검색 순위를 그대로 날립니다.** 옛 주소를 알아야 리다이렉트를
깝니다. `site:sia.haus` 검색 결과나 아임웹 관리자의 페이지 목록으로 확보하세요.
