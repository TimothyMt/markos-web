"""Google OAuth (OpenID Connect) cho web self-serve — không cần Authlib.

Flow:
  1. GET /auth/google/login    → login():   lưu state CSRF vào session, redirect Google.
  2. User đồng ý → Google redirect /auth/google/callback?code&state.
  3. GET /auth/google/callback → callback(): verify state → đổi code lấy token →
     userinfo (sub,email,name) → auth_identities.find_or_create → set session['uid'].
  4. GET /auth/logout          → logout():  xoá session.

user_id LUÔN lấy từ session (cookie ký), KHÔNG bao giờ từ query param
(chống giả mạo / rò dữ liệu multi-tenant). Cần Supabase (biz layer) mới chạy thật.
"""
import logging
import secrets
from urllib.parse import urlencode

import httpx
from starlette.responses import RedirectResponse, HTMLResponse

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

logger = logging.getLogger(__name__)

_AUTH_ENDPOINT  = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_USERINFO       = "https://openidconnect.googleapis.com/v1/userinfo"
_SCOPES = "openid email profile"


def configured() -> bool:
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def _redirect_uri(request) -> str:
    """URI callback: ưu tiên env (khớp Google Console), fallback suy từ request."""
    if GOOGLE_REDIRECT_URI:
        return GOOGLE_REDIRECT_URI
    base = str(request.base_url).rstrip("/")
    return f"{base}/auth/google/callback"


async def login(request):
    """Khởi động OAuth: lưu state CSRF vào session, redirect sang Google."""
    if not configured():
        return HTMLResponse(
            "<h2>Chưa cấu hình đăng nhập Google</h2>"
            "<p>Thiếu GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET.</p>",
            status_code=503,
        )
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    nxt = request.query_params.get("next", "/")
    if nxt.startswith("/"):                       # chỉ path nội bộ (chống open-redirect)
        request.session["oauth_next"] = nxt
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  _redirect_uri(request),
        "response_type": "code",
        "scope":         _SCOPES,
        "state":         state,
        "access_type":   "online",
        "prompt":        "select_account",
    }
    return RedirectResponse(f"{_AUTH_ENDPOINT}?{urlencode(params)}")


async def callback(request):
    """Nhận code → đổi token → userinfo → find_or_create → set session['uid']."""
    if not configured():
        return HTMLResponse("Chưa cấu hình Google OAuth.", status_code=503)
    if request.query_params.get("error"):
        return HTMLResponse(
            f"<h2>Đăng nhập bị huỷ</h2><p>{request.query_params.get('error')}</p>",
            status_code=400,
        )
    code  = request.query_params.get("code")
    state = request.query_params.get("state")
    saved = request.session.pop("oauth_state", None)
    if not code or not state or state != saved:   # CSRF / state mismatch
        return HTMLResponse("<h2>State không hợp lệ</h2><p>Thử đăng nhập lại.</p>",
                            status_code=400)
    # 1) code → access_token → 2) userinfo (sub/email/name)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            tok = await client.post(_TOKEN_ENDPOINT, data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  _redirect_uri(request),
                "grant_type":    "authorization_code",
            })
            tok.raise_for_status()
            access_token = tok.json().get("access_token")
            if not access_token:
                raise ValueError("Google không trả access_token")
            ui = await client.get(
                _USERINFO, headers={"Authorization": f"Bearer {access_token}"})
            ui.raise_for_status()
            info = ui.json()
    except Exception as e:
        logger.warning("google callback exchange failed: %s", e)
        return HTMLResponse(f"<h2>Lỗi đăng nhập Google</h2><p>{e}</p>", status_code=502)

    sub = info.get("sub")
    if not sub:
        return HTMLResponse("Google không trả định danh (sub).", status_code=502)
    email = info.get("email")
    name  = info.get("name") or email

    # 3) find_or_create identity → user_id + status (cần Supabase client)
    from storage.v2 import auth_identities
    from webapp.business import ensure_client
    try:
        await ensure_client()
    except Exception as e:
        logger.warning("google callback ensure_client failed: %s", e)
        return HTMLResponse(
            "<h2>Hệ thống chưa sẵn sàng</h2><p>Thiếu kết nối dữ liệu.</p>",
            status_code=503)
    ident = await auth_identities.find_or_create("google", sub, email=email, name=name)
    if not ident or not ident.get("user_id"):
        return HTMLResponse("<h2>Không tạo được tài khoản</h2>", status_code=500)

    # 4) set session — mọi request sau đọc user_id TỪ ĐÂY (không phải query param)
    request.session["uid"]   = int(ident["user_id"])
    request.session["email"] = email
    nxt = request.session.pop("oauth_next", "/")
    return RedirectResponse(nxt or "/", status_code=303)


async def logout(request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
