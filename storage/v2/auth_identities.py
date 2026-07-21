"""
Auth identities — định danh đăng nhập ngoài (Google OAuth) ↔ user_id nội bộ.

Self-serve web: user đăng nhập Google → 'sub' ổn định → tra/khởi tạo user_id.
Default-deny: identity mới có status='pending' + users.token_quota=0; admin phải
kích hoạt (status='active' + set quota) mới dùng được Max.

Hai gate TÁCH BẠCH:
  - status  = quyền TRUY CẬP (pending/active/blocked) — admin bật/tắt.
  - token_quota (bảng users) = NGÂN SÁCH token — chặn quota cứng mỗi LLM call.
Tách ra để phân biệt "chờ duyệt" vs "đã duyệt nhưng hết token".
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from storage.v2._client import get_client

logger = logging.getLogger(__name__)
TABLE = "auth_identities"


async def get_by_external(provider: str, external_id: str) -> Optional[dict]:
    """Tra identity theo (provider, external_id). None nếu chưa có / lỗi."""
    client = get_client()
    if client is None:
        return None
    try:
        resp = (
            await client.table(TABLE)
            .select("*")
            .eq("provider", provider)
            .eq("external_id", external_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.warning("get_by_external(%s,%s) failed: %s", provider, external_id, e)
        return None


async def get_by_user(user_id: int) -> Optional[dict]:
    """Tra identity theo user_id (check status khi vào app)."""
    client = get_client()
    if client is None:
        return None
    try:
        resp = (
            await client.table(TABLE)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.warning("get_by_user(%d) failed: %s", user_id, e)
        return None


async def find_or_create(
    provider: str,
    external_id: str,
    email: Optional[str] = None,
    name: Optional[str] = None,
) -> Optional[dict]:
    """Tìm identity; nếu chưa có → tạo user_id mới (quota=0) + identity 'pending'.

    Trả identity dict (có user_id, status). None nếu lỗi / không có client.
    """
    client = get_client()
    if client is None:
        return None
    # 1) Đã tồn tại → trả luôn (kể cả pending/blocked, caller đọc status).
    found = await get_by_external(provider, external_id)
    if found:
        return found
    # 2) Tạo user mới — user_id do sequence (DEFAULT) cấp; quota=0 = default-deny.
    try:
        u = (
            await client.table("users")
            .insert({"name": name, "plan": "web", "token_quota": 0})
            .execute()
        )
        new_uid = u.data[0]["user_id"] if u.data else None
        if new_uid is None:
            logger.error("find_or_create: users insert không trả user_id")
            return None
    except Exception as e:
        logger.warning("find_or_create users insert failed: %s", e)
        return None
    # 3) Tạo identity (default-deny 'pending').
    try:
        resp = (
            await client.table(TABLE)
            .insert({
                "provider": provider,
                "external_id": external_id,
                "user_id": new_uid,
                "email": email,
                "name": name,
                "status": "pending",
            })
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        # Đua 2 request cùng sub → UNIQUE(provider,external_id) vỡ. Tra lại identity
        # đã tạo bởi request kia; user vừa insert thành orphan quota=0 (vô hại).
        logger.warning("find_or_create identity insert failed (%s) → re-fetch", e)
        return await get_by_external(provider, external_id)


async def set_status(user_id: int, status: str) -> bool:
    """Admin: đổi trạng thái truy cập (active / blocked / pending)."""
    client = get_client()
    if client is None:
        return False
    try:
        await (
            client.table(TABLE)
            .update({"status": status,
                     "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("user_id", user_id)
            .execute()
        )
        return True
    except Exception as e:
        logger.warning("set_status(%d,%s) failed: %s", user_id, status, e)
        return False


async def list_identities(limit: int = 100) -> list:
    """Admin dashboard: liệt kê identity (mới nhất trước)."""
    client = get_client()
    if client is None:
        return []
    try:
        resp = (
            await client.table(TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        logger.warning("list_identities failed: %s", e)
        return []
