"""ScrapeCreators — client mỏng "đôi mắt" cho Max: lấy data THẬT từ social/ad-library.

1 KEY hệ thống (env `SCRAPECREATORS_API_KEY`, đúng pattern D-005) — không OAuth từng user.
Xem catalog đầy đủ + triết lý dùng: docs/web/references/scrapecreators-api.md.
Chi phí = credits theo lượt → gọi ON-DEMAND, cache mạnh ở tầng business (skill_runs).
"""
from __future__ import annotations

import os

BASE = "https://api.scrapecreators.com"


def api_key() -> str:
    return os.getenv("SCRAPECREATORS_API_KEY", "").strip()


def configured() -> bool:
    return bool(api_key())


async def _get(client, path: str, params: dict) -> dict:
    r = await client.get(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None})
    r.raise_for_status()
    return r.json()


async def fetch_facebook_page(url: str, want_posts: int = 8, want_ads: int = 12) -> dict:
    """Kéo profile + N bài organic (phân trang cursor) + ads đang chạy của 1 page FB.

    Trả {"profile": {...}, "posts": [...], "ads": [...]}. Raise nếu profile 404/lỗi key.
    """
    import httpx

    headers = {"x-api-key": api_key()}
    async with httpx.AsyncClient(timeout=45.0, headers=headers) as c:
        profile = await _get(c, "/v1/facebook/profile", {"url": url})

        posts: list = []
        cursor = None
        while len(posts) < want_posts:
            page = await _get(c, "/v1/facebook/profile/posts", {"url": url, "cursor": cursor})
            batch = page.get("posts") or []
            if not batch:
                break
            posts.extend(batch)
            cursor = page.get("cursor")
            if not cursor:
                break
        posts = posts[:want_posts]

        ads: list = []
        page_id = (profile.get("adLibrary") or {}).get("pageId")
        if page_id:
            try:
                res = await _get(c, "/v1/facebook/adLibrary/company/ads", {"pageId": page_id})
                ads = (res.get("results") or [])[:want_ads]
            except Exception:
                ads = []   # ad-library lỗi không nên chặn cả report

        return {"profile": profile, "posts": posts, "ads": ads}
