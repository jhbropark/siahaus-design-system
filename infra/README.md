# sia.haus 인프라 설정

웹 보안 설정(HTTPS 강제 · 보안 헤더)과 메일 인증(SPF/DKIM/DMARC) 관련 구성을 모아둡니다.

## 현재 구성

```
DNS         Cloudflare (curt / liz.ns.cloudflare.com) — DNS-only, 프록시 미사용
CDN         Amazon CloudFront
오리진      Nginx
인증서      Amazon 발급, SAN: sia.haus, *.sia.haus (2027-02-06 만료)
메일        카카오(다음) 도메인메일 — aspmx.daum.net
```

## 진단 결과 (2026-08-20)

| 항목 | 상태 |
|---|---|
| 도메인 · DNS · CDN | 정상 |
| 웹 응답 | 200 (`sia.haus` → 301 → `www.sia.haus`) |
| TLS 인증서 | 유효 |
| SPF | 통과 (`v=spf1 include:_spf.daum.net ~all`) |
| DMARC | 통과 (`v=DMARC1; p=none; rua=mailto:dmarc@sia.haus; fo=1`) |
| DKIM | **미설정** — 발신 메일에 서명 헤더 없음 |
| HTTPS 강제 | **미적용** — 평문 HTTP가 그대로 200 응답 |
| 보안 헤더 | **전무** — 6종 모두 없음 |

---

## 1. HTTPS 리다이렉트 + 보안 헤더

### 방법 A — CloudFront (권장)

CloudFront 배포를 직접 관리하는 경우입니다.

```bash
cd infra/cloudfront

# 변경 내용 미리보기 (아무것도 바꾸지 않음)
./apply.sh

# 실제 적용
./apply.sh --commit
```

스크립트가 하는 일:

1. 별칭에 `sia.haus`가 등록된 배포를 찾습니다
2. `siahaus-security-headers` 응답 헤더 정책을 생성합니다 (이미 있으면 재사용)
3. 현재 설정을 `cloudfront-config.backup.*.json`으로 백업합니다
4. 기본 동작과 모든 캐시 동작에 적용합니다
   - `ViewerProtocolPolicy` → `redirect-to-https`
   - `ResponseHeadersPolicyId` → 위 정책
5. 변경 diff를 출력한 뒤 업데이트합니다

전 엣지 전파에 5~15분 걸립니다.

#### 콘솔로 하는 경우

**HTTPS 리다이렉트** — CloudFront → 배포 선택 → Behaviors → 각 동작 편집
→ Viewer protocol policy → `Redirect HTTP to HTTPS`

**보안 헤더** — CloudFront → Policies → Response headers → Create
→ `response-headers-policy.json` 값대로 입력 → 각 Behavior에 연결

### 방법 B — 오리진 Nginx

CloudFront 콘솔에 접근할 수 없을 때 사용합니다.
`nginx/security-headers.conf`를 서버의 `/etc/nginx/snippets/`에 두고 server 블록에서 include 하세요.

HTTPS 리다이렉트는 별도로 추가합니다:

```nginx
server {
    listen 80;
    server_name sia.haus www.sia.haus;
    return 301 https://$host$request_uri;
}
```

> CloudFront가 앞단에 있으면 `X-Forwarded-Proto` 기준으로 판단해야 리다이렉트 루프가 나지 않습니다.
> 가능하면 방법 A를 쓰세요.

### 방법 C — 사이트 빌더를 쓰는 경우

CloudFront가 호스팅 업체 소유라 접근이 불가능할 수 있습니다.
그 경우 빌더 관리 화면의 "HTTPS 강제 / SSL 설정" 항목을 쓰거나, 업체에 요청해야 합니다.

---

## 2. 적용 후 검증

```bash
# 보안 헤더
curl -sSI https://sia.haus | grep -iE 'strict-transport|x-content-type|x-frame|referrer|permissions'

# HTTPS 리다이렉트 — 301 + Location: https:// 확인
curl -sSI http://sia.haus | head -3
```

외부 검사: https://securityheaders.com/?q=sia.haus

---

## 3. HSTS 단계적 강화

`max-age`를 처음부터 1년으로 걸면, 설정이 잘못됐을 때 브라우저가 캐시한 기간 내내 접속이 막힙니다.
반드시 단계적으로 올리세요.

| 단계 | 값 | 관찰 기간 |
|---|---|---|
| 1 | `max-age=300` (현재 설정) | 1일 |
| 2 | `max-age=86400` | 1주 |
| 3 | `max-age=31536000; includeSubDomains` | 상시 |

3단계의 `includeSubDomains`는 **모든 서브도메인에 HTTPS를 강제**합니다.
HTTPS를 지원하지 않는 서브도메인이 있으면 접속이 끊기니 먼저 확인하세요.

---

## 4. CSP는 아직 적용하지 않았습니다

사이트가 91개 스크립트 소스를 참조하고 있어, CSP를 바로 강제하면 페이지가 깨집니다.
`nginx/security-headers.conf` 하단에 Report-Only 시작 템플릿을 주석으로 남겨두었습니다.
위반 리포트를 수집해 허용 목록을 좁힌 뒤 강제로 전환하세요.

---

## 5. 남은 작업

- [ ] **DKIM** — 카카오 도메인메일 관리자에서 지원 여부 확인.
      지원하면 셀렉터·공개키를 받아 Cloudflare에 `<셀렉터>._domainkey` TXT 등록.
      미지원이면 DMARC는 `p=none`이 상한입니다 (전달된 메일에서 SPF가 깨지므로).
- [ ] **`dmarc@sia.haus` 수신 계정** — 없으면 집계 리포트가 전부 반송됩니다.
- [ ] **DMARC 정책 강화** — 리포트 2주 관찰 후 `p=quarantine` → `p=reject`.
      DKIM 설정이 선행되어야 합니다.
- [ ] **구조화 데이터** — 현재 `OnlineStore`로 선언되어 있습니다.
      미디어아트 스튜디오이므로 `Organization` 또는 `ProfessionalService`가 맞습니다.
