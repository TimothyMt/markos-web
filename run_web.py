"""
Standalone web dashboard server — KHÔNG cần Telegram token.

Chạy:  python run_web.py
Mở:    http://localhost:8000

Mặc định lưu vào SQLite (webapp/markos_web.db). Nếu set SUPABASE_URL +
SUPABASE_SERVICE_KEY (chạy webapp/supabase_schema.sql trước) thì tự dùng Supabase.
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from webapp.api import api_routes, full_state
from webapp import store, events
from services import google_oauth
from config import SESSION_SECRET

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
WEB_DIR = Path(__file__).resolve().parent / "web"


@asynccontextmanager
async def lifespan(app: Starlette):
    backend = store.configure()
    await store.init()
    from webapp.quota import register_llm_hooks
    register_llm_hooks()                      # quota + access gate tại ranh giới LLM
    logging.info("Web dashboard ready (store=%s).", backend)
    # SSE: watcher (luôn chạy) + Supabase Realtime (nếu có)
    asyncio.create_task(events.watcher(full_state))
    asyncio.create_task(events.realtime_listener(full_state))
    yield


class UidContextMiddleware:
    """Pure-ASGI middleware: bơm user_id từ session vào contextvar business._current_uid.

    Đặt BÊN TRONG SessionMiddleware (sau nó trong list) để đọc được scope['session'].
    Pure-ASGI (không BaseHTTPMiddleware) để contextvar propagate đúng sang endpoint.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            from webapp.business import set_current_uid
            sess = scope.get("session") or {}
            set_current_uid(sess.get("uid"))
        await self.app(scope, receive, send)


async def oauth_fb_callback(request):
    """FB OAuth callback cho web standalone (không có bot → notify bị bỏ qua)."""
    try:
        from services.fb_oauth import handle_callback
        return await handle_callback(request, None)
    except Exception as e:
        logging.warning("oauth_fb_callback failed: %s", e)
        return HTMLResponse(f"<h2>Lỗi kết nối</h2><p>{e}</p>", status_code=500)


if not SESSION_SECRET:
    logging.warning(
        "SESSION_SECRET chưa set → dùng key dev tạm (cookie GIẢ MẠO được). "
        "Production BẮT BUỘC set SESSION_SECRET."
    )
_session_secret = SESSION_SECRET or "dev-insecure-secret-change-me"

app = Starlette(
    routes=api_routes() + [
        Route("/oauth/fb/callback", oauth_fb_callback, methods=["GET"]),
        Route("/auth/google/login", google_oauth.login, methods=["GET"]),
        Route("/auth/google/callback", google_oauth.callback, methods=["GET"]),
        Route("/auth/logout", google_oauth.logout, methods=["GET", "POST"]),
        Mount("/", app=StaticFiles(directory=str(WEB_DIR), html=True), name="web"),
    ],
    middleware=[
        Middleware(
            SessionMiddleware,
            secret_key=_session_secret,
            same_site="lax",          # cho phép cookie sau redirect OAuth top-level
            max_age=14 * 24 * 3600,   # 14 ngày
            https_only=False,         # Railway kết thúc TLS ở proxy; bật True nếu serve HTTPS trực tiếp
        ),
        Middleware(UidContextMiddleware),   # đọc session['uid'] → contextvar (sau Session)
    ],
    lifespan=lifespan,
)


def main():
    port = int(os.environ.get("PORT", "8000"))
    print(f"\n  Marketing OS web dashboard → http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
