"""Test AUTH self-serve (Google OAuth + session + default-deny + quota).

Bảo vệ 4 tính chất bảo mật CỐT LÕI của auth — chạy KHÔNG cần Supabase/Google:
  ① FLIP: pick_user_id BỎ QUA user_id do client gửi; chỉ tin session (contextvar).
  ② Middleware→contextvar→pick: request có session → uid đúng; ẩn danh → None.
  ③ Quota/access gate: LLM bị CHẶN ở pre-hook TRƯỚC khi gọi provider khi chưa auth.
  ④ Admin guard: /api/admin/* → 403 với ẩn danh/không-admin, 200 với admin.

Chạy:  python tests/test_auth.py   (exit 0 = pass)
"""
import os
import sys
import asyncio

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ["ADMIN_EMAILS"] = "admin@x.com"          # set TRƯỚC khi import config/api
os.environ.pop("WEB_DEFAULT_USER_ID", None)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def test_flip_ignores_client_user_id():
    """① pick_user_id chỉ tin session; user_id client gửi là INERT."""
    from webapp import business

    async def _t():
        business.set_current_uid(None)
        assert await business.pick_user_id(999) is None      # client gửi 999, no session
        business.set_current_uid(123)
        assert await business.pick_user_id(999) == 123        # session thắng
        business.set_current_uid(None)
        assert await business.pick_user_id("null") is None
    asyncio.run(_t())
    print("① FLIP OK — client-supplied user_id inert")


def test_middleware_sets_contextvar():
    """② Middleware bơm session['uid'] → contextvar → pick_user_id thấy đúng."""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import JSONResponse, PlainTextResponse
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.testclient import TestClient
    from run_web import UidContextMiddleware
    from webapp import business

    async def set_uid(request):
        request.session["uid"] = 777
        return PlainTextResponse("ok")

    async def read_uid(request):
        return JSONResponse({"pick": await business.pick_user_id(999)})

    app = Starlette(
        routes=[Route("/set", set_uid), Route("/read", read_uid)],
        middleware=[Middleware(SessionMiddleware, secret_key="k"),
                    Middleware(UidContextMiddleware)])
    c = TestClient(app)
    c.get("/set")
    assert c.get("/read").json() == {"pick": 777}             # session → uid đúng
    assert TestClient(app).get("/read").json() == {"pick": None}   # ẩn danh → None
    print("② MIDDLEWARE→CONTEXTVAR→pick OK")


def test_quota_gate_blocks_unauthenticated_llm():
    """③ LLM bị chặn ở pre-hook (trước provider) khi chưa đăng nhập."""
    from webapp import business, quota
    from tools import llm_router
    quota.register_llm_hooks()
    tt = list(llm_router.TaskType)[0]

    async def _t():
        business.set_current_uid(None)
        try:
            await llm_router.call(tt, system="x", user="y", max_tokens=10)
            assert False, "LLM KHÔNG bị chặn"
        except quota.QuotaBlocked as e:
            assert e.code == "unauthenticated"
    try:
        asyncio.run(_t())
    finally:
        llm_router.set_usage_hooks(None, None)   # gỡ hook, tránh nhiễm test khác
    print("③ QUOTA/ACCESS GATE OK — chặn LLM ẩn danh trước khi tốn tiền")


def test_admin_guard():
    """④ /api/admin/* — 403 ẩn danh/không-admin, 200 admin."""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import PlainTextResponse
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.testclient import TestClient
    from webapp import api

    async def set_session(request):
        request.session["email"] = request.query_params.get("email", "")
        return PlainTextResponse("ok")

    app = Starlette(
        routes=[Route("/setsession", set_session),
                Route("/api/admin/users", api.admin_users, methods=["GET"]),
                Route("/api/admin/access", api.admin_access, methods=["POST"])],
        middleware=[Middleware(SessionMiddleware, secret_key="k")])

    anon = TestClient(app)
    assert anon.get("/api/admin/users").status_code == 403
    assert anon.post("/api/admin/access", json={"user_id": 1, "status": "active"}).status_code == 403
    bob = TestClient(app); bob.get("/setsession?email=bob@x.com")
    assert bob.get("/api/admin/users").status_code == 403
    adm = TestClient(app); adm.get("/setsession?email=admin@x.com")
    assert adm.get("/api/admin/users").status_code == 200
    print("④ ADMIN GUARD OK — anon/non-admin=403, admin=200")


if __name__ == "__main__":
    test_flip_ignores_client_user_id()
    test_middleware_sets_contextvar()
    test_quota_gate_blocks_unauthenticated_llm()
    test_admin_guard()
    print("\nALL AUTH TESTS PASSED")
