#!/usr/bin/env bash
# sia.haus — CloudFront에 HTTPS 리다이렉트 + 보안 헤더 적용
#
# 사용법:
#   ./apply.sh                 # 변경 내용만 출력 (dry-run, 기본값)
#   ./apply.sh --commit        # 실제 적용
#
# 요구사항: aws CLI v2, jq, CloudFront 수정 권한

set -euo pipefail

DOMAIN="${DOMAIN:-sia.haus}"
POLICY_NAME="siahaus-security-headers"
POLICY_FILE="$(dirname "$0")/response-headers-policy.json"
WORKDIR="$(mktemp -d)"
COMMIT=false
[[ "${1:-}" == "--commit" ]] && COMMIT=true

trap 'rm -rf "$WORKDIR"' EXIT

log() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# ── 1. 배포 찾기 ────────────────────────────────────────────────
log "1. $DOMAIN 을 서비스하는 CloudFront 배포 검색"
DIST_ID="$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Aliases.Items && contains(Aliases.Items, '$DOMAIN')].Id | [0]" \
  --output text)"

if [[ -z "$DIST_ID" || "$DIST_ID" == "None" ]]; then
  echo "오류: 별칭(Alternate domain name)에 $DOMAIN 이 등록된 배포를 찾지 못했습니다." >&2
  echo "      다음으로 직접 확인하세요: aws cloudfront list-distributions \\" >&2
  echo "        --query \"DistributionList.Items[].{Id:Id,Aliases:Aliases.Items}\"" >&2
  exit 1
fi
echo "   배포 ID: $DIST_ID"

# ── 2. 응답 헤더 정책 생성 (없으면) ──────────────────────────────
log "2. 응답 헤더 정책 '$POLICY_NAME' 확인/생성"
POLICY_ID="$(aws cloudfront list-response-headers-policies --type custom \
  --query "ResponseHeadersPolicyList.Items[?ResponseHeadersPolicy.ResponseHeadersPolicyConfig.Name=='$POLICY_NAME'].ResponseHeadersPolicy.Id | [0]" \
  --output text 2>/dev/null || echo "None")"

if [[ -z "$POLICY_ID" || "$POLICY_ID" == "None" ]]; then
  if $COMMIT; then
    POLICY_ID="$(aws cloudfront create-response-headers-policy \
      --response-headers-policy-config "file://$POLICY_FILE" \
      --query 'ResponseHeadersPolicy.Id' --output text)"
    echo "   생성됨: $POLICY_ID"
  else
    echo "   [dry-run] 정책이 없어 새로 생성 예정 (파일: $POLICY_FILE)"
    POLICY_ID="<생성-예정>"
  fi
else
  echo "   기존 정책 재사용: $POLICY_ID"
fi

# ── 3. 배포 설정 가져오기 ──────────────────────────────────────
log "3. 현재 배포 설정 조회"
aws cloudfront get-distribution-config --id "$DIST_ID" > "$WORKDIR/dist.json"
ETAG="$(jq -r '.ETag' "$WORKDIR/dist.json")"
jq '.DistributionConfig' "$WORKDIR/dist.json" > "$WORKDIR/config.json"
cp "$WORKDIR/config.json" "./cloudfront-config.backup.$(date +%Y%m%d%H%M%S).json"
echo "   ETag: $ETAG"
echo "   백업: ./cloudfront-config.backup.*.json"
echo "   현재 ViewerProtocolPolicy: $(jq -r '.DefaultCacheBehavior.ViewerProtocolPolicy' "$WORKDIR/config.json")"
echo "   현재 ResponseHeadersPolicyId: $(jq -r '.DefaultCacheBehavior.ResponseHeadersPolicyId // "(없음)"' "$WORKDIR/config.json")"

# ── 4. 설정 패치 ──────────────────────────────────────────────
log "4. 변경 사항 계산 — 기본 동작 + 모든 캐시 동작에 적용"
jq --arg pid "$POLICY_ID" '
  .DefaultCacheBehavior.ViewerProtocolPolicy = "redirect-to-https"
  | .DefaultCacheBehavior.ResponseHeadersPolicyId = $pid
  | if (.CacheBehaviors.Quantity // 0) > 0 then
      .CacheBehaviors.Items |= map(
        .ViewerProtocolPolicy = "redirect-to-https"
        | .ResponseHeadersPolicyId = $pid
      )
    else . end
' "$WORKDIR/config.json" > "$WORKDIR/config-new.json"

diff <(jq -S . "$WORKDIR/config.json") <(jq -S . "$WORKDIR/config-new.json") || true

# ── 5. 적용 ───────────────────────────────────────────────────
if ! $COMMIT; then
  log "dry-run 종료 — 실제 적용하려면 ./apply.sh --commit"
  exit 0
fi

log "5. 배포 업데이트"
aws cloudfront update-distribution \
  --id "$DIST_ID" \
  --distribution-config "file://$WORKDIR/config-new.json" \
  --if-match "$ETAG" \
  --query 'Distribution.Status' --output text

log "완료 — 전 엣지 전파까지 5~15분 소요됩니다."
echo "검증:  curl -sSI https://$DOMAIN | grep -iE 'strict-transport|x-content-type|x-frame|referrer|permissions'"
echo "리다이렉트: curl -sSI http://$DOMAIN | head -3"
