"""Chặn quota + gate truy cập tại ranh giới LLM (hook vào tools.llm_router).

- ensure_can_spend(uid): raise QuotaBlocked nếu chưa đăng nhập / chưa kích hoạt
  (status != 'active') / hết quota (token_used >= token_quota).
- record_usage(uid, tokens): cộng dồn users.token_used sau mỗi LLM call thành công.
- register_llm_hooks(): gắn pre/post hook vào llm_router (gọi 1 lần lúc khởi động).

user_id lấy từ contextvar business._current_uid — CÙNG nguồn với pick_user_id,
nên guard luôn bám đúng user của request đang chạy.
"""
import logging

logger = logging.getLogger(__name__)


class QuotaBlocked(Exception):
    """LLM bị chặn: chưa đăng nhập / chưa kích hoạt / hết quota."""
    def __init__(self, reason: str, code: str):
        super().__init__(reason)
        self.reason = reason
        self.code = code   # 'unauthenticated' | 'inactive' | 'quota_exceeded'


def _current_uid():
    try:
        from webapp.business import _current_uid as cv, _UNSET
        v = cv.get()
        return None if v is _UNSET else v      # _UNSET (nội bộ/test) → coi như chưa auth
    except Exception:
        return None


async def ensure_can_spend(uid) -> None:
    """Raise QuotaBlocked nếu user không được phép tốn token."""
    if uid in (None, "", "null"):
        raise QuotaBlocked("Bạn cần đăng nhập để dùng tính năng này.", "unauthenticated")
    from storage.v2 import users as users_mod, auth_identities
    ident = await auth_identities.get_by_user(int(uid))
    status = (ident or {}).get("status")
    if status != "active":
        raise QuotaBlocked(
            "Tài khoản đang chờ kích hoạt." if status in (None, "pending")
            else "Tài khoản đã bị khoá.",
            "inactive",
        )
    user = await users_mod.get_user(int(uid))
    if user is not None:
        quota = int(user.get("token_quota") or 0)
        used = int(user.get("token_used") or 0)
        if used >= quota:
            raise QuotaBlocked(
                "Bạn đã dùng hết hạn mức token. Liên hệ admin để nâng.",
                "quota_exceeded",
            )


async def record_usage(uid, tokens: int) -> None:
    """Cộng dồn token_used (best-effort; lỗi ghi không làm hỏng kết quả LLM)."""
    if uid in (None, "", "null") or not tokens or tokens <= 0:
        return
    from storage.v2 import users as users_mod
    try:
        await users_mod.add_token_usage(int(uid), int(tokens))
    except Exception as e:
        logger.warning("record_usage(%s,%s) failed: %s", uid, tokens, e)


# ── llm_router hooks ─────────────────────────────────────────────────────
async def _pre_hook(task_type, max_tokens):
    await ensure_can_spend(_current_uid())


async def _post_hook(result):
    toks = int(result.get("tokens_in") or 0) + int(result.get("tokens_out") or 0)
    await record_usage(_current_uid(), toks)


def register_llm_hooks() -> None:
    """Gắn quota + access gate vào llm_router.call (gọi lúc khởi động web app)."""
    from tools import llm_router
    llm_router.set_usage_hooks(pre=_pre_hook, post=_post_hook)
    logger.info("LLM usage hooks registered (quota + access gate).")
