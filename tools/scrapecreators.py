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


def video_play_url(v: dict) -> str | None:
    """Rút URL media tải được (MP4) từ 1 aweme TikTok — để ASR/tải khi cần lời thoại.

    TikTok/ScrapeCreators đặt URL ở nhiều nhánh khác nhau (`video.play_addr.url_list`,
    `download_addr`, biến thể camelCase, hoặc phẳng) → thử lần lượt, trả URL http đầu tiên.
    URL CDN có thể cần header trình duyệt/hết hạn nhanh → tầng tải phải phòng thủ.
    """
    if not isinstance(v, dict):
        return None
    vid = v.get("video") or {}
    candidates: list = []
    for key in ("play_addr", "download_addr", "play_addr_h264", "play_addr_bytevc1",
                "playAddr", "downloadAddr"):
        node = vid.get(key)
        if isinstance(node, dict):
            candidates.extend(node.get("url_list") or node.get("urlList") or [])
        elif isinstance(node, str):
            candidates.append(node)
    for key in ("playAddr", "downloadAddr", "play_url", "download_url", "url"):
        val = v.get(key) or vid.get(key)
        if isinstance(val, str):
            candidates.append(val)
    for u in candidates:
        if isinstance(u, str) and u.startswith("http"):
            return u
    return None


def _vtt_to_text(s: str) -> str:
    """WEBVTT/SRT → text thuần: bỏ header, dòng timestamp `-->`, số thứ tự, NOTE/STYLE; khử lặp.

    Transcript CC của ScrapeCreators trả dạng WEBVTT thô (có `00:00:00.040 --> ...`), lại hay là
    bản auto-dịch tiếng Anh — ở đây chỉ dọn markup để hiển thị được; ngôn ngữ sai thì cần ASR.
    """
    if not s or ("WEBVTT" not in s and "-->" not in s):
        return (s or "").strip()
    out: list = []
    for line in s.splitlines():
        t = line.strip()
        if not t or t == "WEBVTT" or "-->" in t or t.isdigit():
            continue
        if t.upper().startswith(("NOTE", "STYLE", "REGION")):
            continue
        if not out or out[-1] != t:   # khử dòng lặp liên tiếp (VTT hay lặp)
            out.append(t)
    return " ".join(out).strip()


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
                    clean = _vtt_to_text(tr.get("transcript") or "")
                    if clean:
                        transcripts[aid] = clean
                except Exception:
                    pass

        return {"profile": profile, "videos": videos, "transcripts": transcripts, "handle": handle}
