"""
KrillinAI / KlicStudio client — extract transcript + metadata từ video.

Repo gốc: https://github.com/krillinai/KlicStudio
KrillinAI là tool video localization/transcription dùng Whisper + LLM segmentation.

Pattern em chọn:
1. Nếu KRILLIN_BINARY env var trỏ tới binary → subprocess CLI mode (best quality, có VAD + segmentation)
2. Nếu không có → fallback Whisper API qua openai SDK (đã có sẵn trong requirements)
3. Nếu cả 2 fail → cho user paste transcript trực tiếp (skill vẫn chạy được)

Trả về dict:
  {
    "transcript": "full text concat",
    "segments": [{"start": float, "end": float, "text": str}, ...],
    "duration_seconds": float,
    "language": "vi" | "en" | ...,
    "source": "krillin" | "whisper_api" | "user_paste",
    "video_url": str (original input nếu là URL),
  }
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

KRILLIN_BINARY = os.getenv("KRILLIN_BINARY", "")  # vd: /usr/local/bin/krillin
KRILLIN_TIMEOUT_SECONDS = int(os.getenv("KRILLIN_TIMEOUT", "300"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Max file size cho Whisper API: 25MB
WHISPER_MAX_BYTES = 25 * 1024 * 1024
# Gemini inline bytes ~20MB — trên ngưỡng này cần Files API (bỏ qua để giữ đơn giản).
GEMINI_INLINE_MAX_BYTES = 18 * 1024 * 1024

_BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

URL_REGEX = re.compile(r"^https?://", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────

async def extract_transcript(
    source: str,
    language_hint: Optional[str] = None,
) -> dict:
    """Extract transcript từ video URL hoặc local file path.

    Args:
        source: URL (YouTube/TikTok/...) hoặc local file path
        language_hint: "vi" / "en" — Whisper sẽ dùng làm prior

    Returns:
        dict với keys: transcript, segments, duration_seconds, language, source, video_url
    """
    is_url = bool(URL_REGEX.match(source))

    # Path 1: KrillinAI CLI (preferred — handles YouTube/TikTok download + transcript)
    if KRILLIN_BINARY and shutil.which(KRILLIN_BINARY):
        try:
            result = await _run_krillin(source, language_hint)
            result["video_url"] = source if is_url else ""
            result.setdefault("local_video_path", "" if is_url else source)
            return result
        except Exception as e:
            logger.warning(f"krillin CLI failed, falling back to whisper: {e}")

    # Path 2/3: tải file 1 lần → thử Whisper (chính, có timestamp) → Gemini (dự phòng).
    if OPENAI_API_KEY or GEMINI_API_KEY:
        local_path = await _ensure_local_file(source) if is_url else source
        errors: list[str] = []
        if OPENAI_API_KEY:
            try:
                result = await _run_whisper_api(local_path, language_hint)
                result["video_url"] = source if is_url else ""
                result["local_video_path"] = local_path
                return result
            except Exception as e:
                logger.warning(f"whisper API failed: {e}")
                errors.append(f"whisper: {type(e).__name__}: {str(e)[:120]}")
        if GEMINI_API_KEY:
            try:
                result = await _run_gemini_transcribe(local_path, language_hint)
                result["video_url"] = source if is_url else ""
                result["local_video_path"] = local_path
                return result
            except Exception as e:
                logger.warning(f"gemini transcribe failed: {e}")
                errors.append(f"gemini: {type(e).__name__}: {str(e)[:120]}")
        raise RuntimeError("ASR engine đều fail: " + " | ".join(errors))

    raise RuntimeError(
        "Không có engine transcript khả dụng. Setup 1 trong 3:\n"
        "- KRILLIN_BINARY env var trỏ tới binary KrillinAI (https://github.com/krillinai/KlicStudio)\n"
        "- OPENAI_API_KEY env var (Whisper — có timestamp)\n"
        "- GEMINI_API_KEY env var (Gemini đọc thẳng video — dự phòng)"
    )


def is_available() -> bool:
    """Skill chỉ chạy được nếu có ít nhất 1 engine."""
    return bool(
        (KRILLIN_BINARY and shutil.which(KRILLIN_BINARY))
        or OPENAI_API_KEY or GEMINI_API_KEY
    )


def availability_report() -> str:
    """Trả về thông tin debug để user biết engine nào đang active."""
    krillin_ok = bool(KRILLIN_BINARY and shutil.which(KRILLIN_BINARY))
    lines = []
    lines.append(f"- KrillinAI binary: {'✅ ' + KRILLIN_BINARY if krillin_ok else '❌ chưa setup'}")
    lines.append(f"- Whisper (OpenAI, có timestamp): {'✅' if OPENAI_API_KEY else '❌ thiếu OPENAI_API_KEY'}")
    lines.append(f"- Gemini (dự phòng): {'✅' if GEMINI_API_KEY else '❌ thiếu GEMINI_API_KEY'}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# KrillinAI CLI
# ─────────────────────────────────────────────────────────────────

async def _run_krillin(source: str, language_hint: Optional[str]) -> dict:
    """Chạy KrillinAI binary, parse stdout JSON.

    Giả định convention KrillinAI có flag --transcript-only --json --input <src>.
    Nếu binary thật khác CLI shape, cần adapt hàm này (tham khảo docs upstream).
    """
    cmd = [
        KRILLIN_BINARY,
        "--transcript-only",
        "--json",
        "--input", source,
    ]
    if language_hint:
        cmd.extend(["--language", language_hint])

    logger.info(f"krillin cmd: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=KRILLIN_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"krillin timeout sau {KRILLIN_TIMEOUT_SECONDS}s")

    if proc.returncode != 0:
        raise RuntimeError(f"krillin exit {proc.returncode}: {stderr.decode()[:500]}")

    data = json.loads(stdout.decode())
    segments = data.get("segments", [])
    return {
        "transcript": data.get("transcript") or " ".join(s.get("text", "") for s in segments),
        "segments": segments,
        "duration_seconds": float(data.get("duration", 0)),
        "language": data.get("language") or language_hint or "vi",
        "source": "krillin",
    }


# ─────────────────────────────────────────────────────────────────
# Whisper API fallback (OpenAI SDK)
# ─────────────────────────────────────────────────────────────────

async def _run_whisper_api(local_path: str, language_hint: Optional[str]) -> dict:
    """Whisper-1 qua HTTP multipart TRỰC TIẾP. Trả segments có timestamps.

    KHÔNG dùng openai SDK ở đây: SDK dựng `httpx.AsyncClient(proxies=...)` — với httpx>=0.28
    (bỏ tham số `proxies`) sẽ `TypeError` ngay lúc khởi tạo, chết cả ASR dù key đúng. Gọi REST
    thẳng bằng httpx né hẳn phụ thuộc phiên bản đó.
    """
    file_size = os.path.getsize(local_path)
    if file_size > WHISPER_MAX_BYTES:
        raise RuntimeError(
            f"File {file_size / 1024 / 1024:.1f}MB vượt giới hạn Whisper API (25MB). "
            "Cần compress audio hoặc dùng KrillinAI binary cho file lớn."
        )

    with open(local_path, "rb") as f:
        files = {"file": (os.path.basename(local_path) or "audio.mp4", f, "application/octet-stream")}
        data = {
            "model": "whisper-1",
            "language": language_hint or "vi",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "segment",
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files=files,
                data=data,
            )
    resp.raise_for_status()
    d = resp.json()
    segments = [
        {"start": float(s.get("start", 0)), "end": float(s.get("end", 0)), "text": s.get("text", "")}
        for s in (d.get("segments") or [])
    ]
    return {
        "transcript": (d.get("text") or "").strip(),
        "segments": segments,
        "duration_seconds": float(d.get("duration") or 0),
        "language": d.get("language") or language_hint or "vi",
        "source": "whisper_api",
    }


async def _run_gemini_transcribe(local_path: str, language_hint: Optional[str]) -> dict:
    """Fallback ASR — Gemini 2.5 Flash đọc THẲNG file video/audio → lời thoại (không timestamp).

    Dùng khi thiếu OPENAI_API_KEY hoặc Whisper lỗi. Inline bytes nên giới hạn ~18MB.
    """
    file_size = os.path.getsize(local_path)
    if file_size > GEMINI_INLINE_MAX_BYTES:
        raise RuntimeError(
            f"File {file_size / 1024 / 1024:.1f}MB vượt ngưỡng inline Gemini (~18MB) — "
            "cần Files API (chưa nối) hoặc dùng Whisper."
        )
    from google import genai
    from google.genai import types

    ext = Path(local_path).suffix.lower().lstrip(".")
    mime = {"mp4": "video/mp4", "mov": "video/quicktime", "webm": "video/webm",
            "m4a": "audio/mp4", "mp3": "audio/mpeg", "wav": "audio/wav"}.get(ext, "video/mp4")
    with open(local_path, "rb") as f:
        blob = f.read()

    client = genai.Client(api_key=GEMINI_API_KEY)
    resp = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=blob, mime_type=mime),
            ("Ghi lại TOÀN BỘ lời thoại (tiếng Việt) trong video/audio này. "
             "Chỉ trả về text lời thoại, KHÔNG mô tả hình ảnh, KHÔNG thêm lời dẫn."),
        ],
    )
    txt = (resp.text or "").strip()
    if not txt:
        raise RuntimeError("Gemini transcribe trả rỗng (video không có lời thoại?)")
    return {
        "transcript": txt,
        "segments": [],
        "duration_seconds": 0.0,
        "language": language_hint or "vi",
        "source": "gemini",
    }


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

async def _ensure_local_file(url: str) -> str:
    """Tải audio/video remote về file tạm. Whisper/Gemini nhận mp3/mp4/m4a/wav/webm.

    Ưu tiên **yt-dlp**: bền với CDN social (TikTok/FB) — tự lo cookie/redirect/watermark và
    LẤY URL MỚI từ trang xem, tránh `play_addr` ký-tạm đã hết hạn (httpx GET trần → 403).
    Fallback **httpx** GET thẳng khi yt-dlp không có (chỉ hợp URL media trực tiếp).
    """
    try:
        import yt_dlp  # noqa: F401
        has_ytdlp = True
    except ImportError:
        has_ytdlp = False

    if has_ytdlp:
        try:
            return await asyncio.to_thread(_download_ytdlp, url)
        except Exception as e:
            logger.warning(f"yt-dlp tải fail ({type(e).__name__}: {str(e)[:140]}) → thử httpx trực tiếp")

    return await _download_httpx(url)


def _download_ytdlp(url: str) -> str:
    """Sync (chạy trong thread) — yt-dlp tải mp4 progressive về thư mục tạm, trả path file lớn nhất."""
    import yt_dlp

    tmp_dir = tempfile.mkdtemp(prefix="krillin_")
    opts = {
        "outtmpl": os.path.join(tmp_dir, "media.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # file đơn (progressive) để KHỎI cần ffmpeg merge; mp4 ưu tiên.
        "format": "best[ext=mp4]/mp4/best",
        "http_headers": {"User-Agent": _BROWSER_UA, "Referer": "https://www.tiktok.com/"},
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
    if not os.path.exists(path):
        cands = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)]
        cands = [f for f in cands if os.path.isfile(f)]
        if not cands:
            raise RuntimeError("yt-dlp không tạo ra file media")
        path = max(cands, key=os.path.getsize)
    logger.info(f"yt-dlp downloaded {url} → {path} ({os.path.getsize(path)} bytes)")
    return path


async def _download_httpx(url: str) -> str:
    """Fallback — GET thẳng URL media (chỉ dùng khi yt-dlp vắng; TikTok CDN hay 403)."""
    suffix = Path(url.split("?")[0]).suffix or ".mp4"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="krillin_")
    os.close(fd)
    dl_headers = {"User-Agent": _BROWSER_UA, "Referer": "https://www.tiktok.com/"}
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True, headers=dl_headers) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(tmp_path, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                    f.write(chunk)
    logger.info(f"httpx downloaded {url} → {tmp_path} ({os.path.getsize(tmp_path)} bytes)")
    return tmp_path


def format_transcript_for_prompt(extract: dict, max_chars: int = 8000) -> str:
    """Format extract dict thành text block đẹp inject vào prompt Claude."""
    src = extract.get("source", "unknown")
    dur = extract.get("duration_seconds", 0)
    lang = extract.get("language", "?")
    segments = extract.get("segments") or []

    header = (
        f"**Transcript engine:** {src} | "
        f"**Độ dài video:** {dur:.1f}s | "
        f"**Ngôn ngữ:** {lang}"
    )

    # Prefer timestamped segments — giúp Claude reason về pacing/hook timing
    if segments:
        lines = []
        for s in segments:
            ts = f"[{s.get('start', 0):.1f}s → {s.get('end', 0):.1f}s]"
            lines.append(f"{ts} {s.get('text', '').strip()}")
        body = "\n".join(lines)
    else:
        body = extract.get("transcript", "")

    if len(body) > max_chars:
        body = body[:max_chars] + f"\n\n... (truncated, tổng {len(body)} chars)"

    return f"{header}\n\n```\n{body}\n```"
