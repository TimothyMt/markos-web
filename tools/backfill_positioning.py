#!/usr/bin/env python
"""One-off ops migration — backfill spine.positioning cho user cũ (có messaging, thiếu định vị).

Nối lại mối đứt Change A + chọn-đầu Q②: user qua flow cũ có `messaging` nhưng thiếu `spine.positioning`.
Đây là MẶT GỌI THẬT của backfill (Option 3 batch); read-path còn có lazy guard (_ensure_spine_positioning).

Chạy từ repo root:
    python tools/backfill_positioning.py --dry-run          # soi cả fleet, KHÔNG ghi
    python tools/backfill_positioning.py                    # quét & ghi cả fleet
    python tools/backfill_positioning.py --user 990555      # chỉ 1 user
    python tools/backfill_positioning.py --force            # ép suy lại (VẪN không đè source='user')

Supabase-only (cần SUPABASE_URL + SUPABASE_SERVICE_KEY trong .env). Idempotent, human-override an toàn.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # repo root → import webapp/* khi chạy từ tools/

for _s in (sys.stdout, sys.stderr):                               # Windows console cp1252 → ép UTF-8 (in tiếng Việt)
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


async def _run(args) -> dict:
    from webapp import business as biz
    if not biz.available():
        return {"error": "Chưa cấu hình Supabase (cần SUPABASE_URL + SUPABASE_SERVICE_KEY)."}
    if args.user is not None:
        return await biz.backfill_spine_positioning(args.user, dry_run=args.dry_run, force=args.force)
    return await biz.backfill_all_spine_positioning(dry_run=args.dry_run, force=args.force, limit=args.limit)


def main():
    ap = argparse.ArgumentParser(description="Backfill spine.positioning cho user cũ (thiếu định vị).")
    ap.add_argument("--dry-run", action="store_true", help="suy + trả kết quả, KHÔNG ghi DB")
    ap.add_argument("--force", action="store_true", help="ép suy lại cả bản đã derived (vẫn KHÔNG đè source='user')")
    ap.add_argument("--user", type=int, default=None, help="chỉ backfill 1 user_id (bỏ qua batch)")
    ap.add_argument("--limit", type=int, default=10000, help="trần số user quét trong batch")
    args = ap.parse_args()
    res = asyncio.run(_run(args))
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
