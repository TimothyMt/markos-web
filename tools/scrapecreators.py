"""ScrapeCreators — client mỏng "đôi mắt" cho Max: lấy data THẬT từ social/ad-library.

1 KEY hệ thống (env `SCRAPECREATORS_API_KEY`, đúng pattern D-005) — không OAuth từng user.
Xem catalog đầy đủ + triết lý dùng: docs/web/references/scrapecreators-api.md.
Chi phí = credits theo lượt → gọi ON-DEMAND, cache mạnh ở tầng business (skill_runs).
"""
from __future__ import annotations

import os
import re

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


def tiktok_handle(handle_or_url: str) -> str:
    """Rút @handle từ URL TikTok hoặc trả về chính handle đã cho."""
    s = (handle_or_url or "").strip()
    m = re.search(r"@([\w.]+)", s)
    if m:
        return m.group(1)
    return s.lstrip("@").split("/")[0].split("?")[0]


async def fetch_tiktok_page(handle_or_url: str, want_videos: int = 8, with_transcript: bool = True) -> dict:
    """Kéo profile + N video (phân trang max_cursor) của 1 kênh TikTok.

    TikTok cho VIEW/SHARE/SAVE thật (FB không có) nhưng KHÔNG có ad-library công khai.
    `with_transcript`: gọi thêm transcript/video (1 credit/video) — chỉ có khi video có CC,
    brand video thường null → scripts đầy đủ cần ASR riêng (Whisper/Gemini) ở tầng trên.
    Trả {"profile", "videos", "transcripts": {aweme_id: text}, "handle"}.
    """
    import httpx

    handle = tiktok_handle(handle_or_url)
    headers = {"x-api-key": api_key()}
    async with httpx.AsyncClient(timeout=45.0, headers=headers) as c:
        profile = await _get(c, "/v1/tiktok/profile", {"handle": handle})

        videos: list = []
        cursor = None
        while len(videos) < want_videos:
            page = await _get(c, "/v3/tiktok/profile/videos", {"handle": handle, "max_cursor": cursor})
            batch = page.get("aweme_list") or []
            if not batch:
                break
            videos.extend(batch)
            if not page.get("has_more"):
                break
            cursor = page.get("max_cursor")
            if not cursor:
                break
        videos = videos[:want_videos]

        transcripts: dict = {}
        if with_transcript:
            for v in videos:
                aid = v.get("aweme_id")
                if not aid:
                    continue
                try:
                    tr = await _get(c, "/v1/tiktok/video/transcript",
                                    {"url": f"https://www.tiktok.com/@{handle}/video/{aid}"})
                    if tr.get("transcript"):
                        transcripts[aid] = tr["transcript"]
                except Exception:
                    pass

        return {"profile": profile, "videos": videos, "transcripts": transcripts, "handle": handle}
