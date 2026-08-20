# sia.haus 도메인 · 웹 보안 · 메일 인증

2026-08-20 점검 기록과 후속 작업입니다.

## 현재 구성

```
사이트       아임웹(Imweb) — 빌더가 호스팅
CDN          Amazon CloudFront (아임웹 소유, 직접 제어 불가)
오리진       Nginx (아임웹 소유)
DNS          Cloudflare (curt / liz.ns.cloudflare.com) — DNS-only, 프록시 미사용
인증서       Amazon 발급, SAN: sia.haus, *.sia.haus (2027-02-06 만료)
메일         카카오(다음) 도메인메일 — aspmx.daum.net
```

**제어 권한이 나뉘어 있다는 점이 이 문서의 전제입니다.**

| 계층 | 소유 | 우리가 바꿀 수 있나 |
|---|---|---|
| DNS 레코드 | Cloudflare 계정 | ✅ 가능 |
| 사이트 콘텐츠 · 도메인 연결 | 아임웹 관리자 | ✅ 가능 (아임웹이 허용하는 범위) |
| CDN · HTTP 응답 헤더 | 아임웹 | ❌ 불가 |

## 점검 결과

| 항목 | 상태 |
|---|---|
| 도메인 · DNS · CDN | 정상 |
| 웹 응답 | 200 (`sia.haus` → 301 → `www.sia.haus`) |
| TLS 인증서 | 유효 |
| SPF | 통과 |
| DMARC | 통과 (`p=none`) |
| DKIM | **미설정** |
| HTTPS 강제 | **미적용** — 평문 HTTP가 그대로 200 응답 |
| 보안 헤더 | **전무** — 6종 모두 없음 |

---

## 1. HTTPS 강제 — 아임웹 관리자에서

가장 중요하고, 가장 해결 가능성이 높은 항목입니다.

아임웹 관리자에서 **도메인 / SSL / 보안 접속** 계열 설정을 찾아 "HTTPS 접속 강제"에 해당하는
항목이 있는지 확인하세요. 아임웹은 연결 도메인에 무료 SSL을 제공하므로 인증서는 이미 발급된
상태입니다(위 인증서 정보 참고). 남은 건 평문 HTTP 요청을 HTTPS로 넘기는 설정뿐입니다.

해당 항목이 보이지 않으면 아임웹 고객지원에 이렇게 문의하세요:

> sia.haus 도메인을 사용 중입니다. 현재 http://sia.haus 로 접속하면 HTTPS로
> 리다이렉트되지 않고 평문으로 응답합니다. HTTPS 접속 강제(HTTP → HTTPS 301
> 리다이렉트) 설정 방법을 알려주시거나 적용해 주실 수 있을까요?

### 검증

```bash
curl -sSI http://sia.haus | head -3
```

`HTTP/1.1 301` 과 `Location: https://...` 가 보이면 적용된 것입니다.

---

## 2. 보안 헤더 — 아임웹에서는 불가능

응답 헤더는 CDN이나 오리진에서 붙이는데 둘 다 아임웹 소유입니다.
아임웹 관리 화면에서 임의의 HTTP 응답 헤더를 추가하는 기능은 제공되지 않습니다.

현재 빠진 헤더:

```
strict-transport-security
content-security-policy
x-content-type-options
x-frame-options
referrer-policy
permissions-policy
```

### 선택지 A — 그대로 둔다 (기본 권장)

정적인 소개 · 포트폴리오 사이트에서 이 헤더들이 막는 공격은 제한적입니다.
로그인이나 결제를 직접 처리하지 않는다면 실질 위험은 낮습니다.

다만 제안서를 받는 기관 · 대기업 보안팀이 도메인을 스캔하면 등급 F로 잡힙니다.
평가 항목에 보안 점검이 있는 입찰이라면 감점 요인이 될 수 있습니다.

### 선택지 B — Cloudflare 프록시를 켠다

DNS가 이미 Cloudflare에 있으므로, 프록시(주황 구름)를 켜면 아임웹을 건드리지 않고
헤더를 붙일 수 있습니다. **다만 트래픽 경로가 바뀌는 구조 변경입니다.**

```
현재:  방문자 → CloudFront(아임웹) → 오리진
변경:  방문자 → Cloudflare → CloudFront(아임웹) → 오리진
```

설정 순서:

1. **SSL/TLS → Overview → `Full (strict)`**
   아임웹 인증서가 유효하므로 strict가 정상 동작합니다. 이걸 먼저 하지 않으면
   리다이렉트 루프가 납니다.
2. **DNS → `sia.haus`, `www` 레코드의 프록시 토글을 주황색으로**
3. **SSL/TLS → Edge Certificates → Always Use HTTPS 켜기**
   → 선택지 1의 HTTPS 강제도 여기서 해결됩니다.
4. **Rules → Transform Rules → Modify Response Header → 정적 헤더 추가**
   ```
   X-Content-Type-Options: nosniff
   X-Frame-Options: SAMEORIGIN
   Referrer-Policy: strict-origin-when-cross-origin
   Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
   ```
5. **SSL/TLS → Edge Certificates → HSTS** — 4번까지 정상 확인 후에만.
   `max-age`를 300초로 시작해 1일 → 1년으로 올립니다.

#### 감수해야 하는 것

- **아임웹이 공식 지원하지 않는 구성입니다.** 문제 발생 시 지원을 못 받을 수 있습니다.
- **방문자 IP가 Cloudflare IP로 보입니다** — 아임웹 방문자 통계가 왜곡될 수 있습니다.
- **캐시가 두 겹이 됩니다** — 사이트를 수정해도 반영이 늦어질 수 있습니다.
  (Cloudflare 캐시 purge로 해결)
- Cloudflare 무료 플랜의 Transform Rules 개수 제한을 확인하세요.

**진행하기 전에 아임웹 지원팀에 Cloudflare 프록시 사용 가능 여부를 먼저 문의하시길 권합니다.**

### CSP는 어느 쪽이든 보류

사이트가 스크립트 소스를 91개 참조하고 있어 검증 없이 강제하면 페이지가 깨집니다.
아임웹이 스크립트를 동적으로 주입하므로 허용 목록을 안정적으로 유지하기도 어렵습니다.

---

## 3. 구조화 데이터

현재 `OnlineStore`로 선언되어 있습니다. 미디어아트 스튜디오에는 맞지 않지만,
**아임웹이 쇼핑몰 기능을 기본 탑재하면서 자동으로 넣는 마크업일 가능성이 높습니다.**
관리 화면에 SEO / 스키마 설정 항목이 있는지 확인하고, 없으면 손댈 수 없는 부분입니다.

---

## 4. 메일 인증 — 완료 및 잔여

### 완료

```
SPF     v=spf1 include:_spf.daum.net ~all
DMARC   v=DMARC1; p=none; rua=mailto:dmarc@sia.haus; fo=1
```

Gmail 수신 테스트에서 확인:

```
Authentication-Results: mx.google.com;
       spf=pass ... smtp.mailfrom=sia@sia.haus;
       dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=sia.haus
```

### 남은 작업

- [ ] **DKIM** — 발신 메일에 `DKIM-Signature` 헤더가 없습니다.
      카카오 도메인메일 관리자에서 DKIM 지원 여부를 확인하고, 지원하면 셀렉터 · 공개키를
      받아 Cloudflare에 `<셀렉터>._domainkey` TXT로 등록하세요.
      미지원이면 DMARC는 `p=none`이 상한입니다 — 전달(forward)된 메일에서 SPF가 깨지는데
      이를 받쳐줄 서명이 없기 때문입니다.
- [ ] **`dmarc@sia.haus` 수신 계정** — 없으면 집계 리포트가 전부 반송됩니다.
      계정을 만들거나 `sia@sia.haus`의 별칭으로 등록하세요.
- [ ] **DMARC 강화** — DKIM 설정 후 리포트를 2주 관찰하고
      `p=quarantine; pct=25` → `pct=100` → `p=reject` 순으로 올립니다.

---

## 검증 명령 모음

```bash
# DNS
dig +short TXT _dmarc.sia.haus
dig +short TXT sia.haus
dig +short TXT <셀렉터>._domainkey.sia.haus

# 웹
curl -sSI http://sia.haus | head -3
curl -sSI https://sia.haus | grep -iE 'strict-transport|x-content-type|x-frame|referrer|permissions'
```

외부 검사: https://securityheaders.com/?q=sia.haus
