"""Regression test R2-P1a — save_strategy_input FAN-OUT: 1 payload → CẢ bet_choices + spine.

Chạy KHÔNG cần key/DB: stub storage.v2, drive HÀM THẬT save_strategy_input + _spine_anchor.

Chốt điều dễ vỡ:
  ① FAN-OUT: 1 lần lưu → _DB có CẢ bet_choices lẫn spine (atomic, 1 upsert).
  ② DEDUPE ô chung: segment → bet.segment + spine.audience.who · statement → bet.positioning + spine.positioning.statement ·
     price_posture → bet.price (nhãn ngắn) + spine.positioning.price_posture.
  ③ map/validate: price_posture enum · growth_focus enum · objective số ép qua _parse_vn_number.
  ④ compat cũ: wedge (từ tệp) + usp (từ định vị) vẫn set → synthesis/hiển thị cũ không vỡ.
  ⑤ DOWNSTREAM đọc như cũ: _spine_anchor(spine vừa ghi) ra khối có định vị + hướng tăng trưởng + đòn bẩy giá.

Chạy:  python3 tests/test_r2_strategy_input.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_DB = {"intake_extra": {}}
_UPSERTS = {"n": 0}


def _install():
    class _Profiles:
        async def get_profile(self, uid): return {"industry": "Spa", "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            _UPSERTS["n"] += 1
            if intake_extra is not None: _DB["intake_extra"] = intake_extra
            _DB.setdefault("fields", {}).update(kw)
            return {"ok": True}
    fake = types.ModuleType("storage.v2")
    fake.profiles = _Profiles()
    sys.modules["storage.v2"] = fake
    sys.modules.setdefault("storage", types.ModuleType("storage"))


_install()
import webapp.business as B
B.available = lambda: True
async def _e(): return None
B.ensure_client = _e
async def _p(r=None): return 1
B.pick_user_id = _p


async def _run():
    res = []
    payload = {
        "market": ["Chưa ai làm phác đồ cho da nhạy cảm"],
        "segment": ["Dân văn phòng da nhạy cảm", "Mẹ bỉm"],
        "channel": ["TikTok", "Zalo"],
        "positioning": {"alternative": "tự mua serum trôi nổi", "differentiator": "phác đồ chuẩn y khoa",
                        "statement": "Phục hồi da chuẩn y khoa, đồng hành 1:1"},
        "price_posture": "premium",
        "stage": "growth", "growth_focus": "conversion",
        "objective": {"outcome": "Tăng đơn gói phục hồi", "metric": "đơn",
                      "target": {"value": "1.200", "unit": "đơn", "period": "quý"},
                      "baseline": {"value": "800", "unit": "đơn", "period": "quý"}, "deadline": "2026-12-31"},
        "audience": {"pain": "da kích ứng, mua nhầm", "where": "TikTok, phòng khám da liễu"},
        "constraint": {"people": "Founder + 1 content", "budget": "20 triệu/tháng", "capacity": "8 bài/tháng"},
    }
    _UPSERTS["n"] = 0
    r = await B.save_strategy_input(user_id=1, payload=payload)
    ie = _DB["intake_extra"]
    bet, spine = ie.get("bet_choices", {}), ie.get("spine", {})
    res += [
        ("① fan-out: _DB có CẢ bet_choices + spine", bool(bet) and bool(spine)),
        ("① atomic: đúng 1 upsert", _UPSERTS["n"] == 1),
        ("② dedupe tệp: segment → bet.segment + spine.audience.who",
         bet.get("segment") == ["Dân văn phòng da nhạy cảm", "Mẹ bỉm"]
         and spine["audience"]["who"] == "Dân văn phòng da nhạy cảm · Mẹ bỉm"),
        ("② dedupe định vị: statement → bet.positioning + spine.positioning.statement",
         bet.get("positioning") == ["Phục hồi da chuẩn y khoa, đồng hành 1:1"]
         and spine["positioning"]["statement"] == "Phục hồi da chuẩn y khoa, đồng hành 1:1"),
        ("② dedupe giá: price_posture → bet.price nhãn ngắn + spine.price_posture",
         bet.get("price") == ["Cao cấp"] and spine["positioning"]["price_posture"] == "premium"),
        ("② giữ alt/diff riêng của spine",
         spine["positioning"]["alternative"] == "tự mua serum trôi nổi"
         and spine["positioning"]["differentiator"] == "phác đồ chuẩn y khoa"),
        ("③ enum + số: growth_focus/stage hợp lệ, target ép số 1200",
         spine["growth_focus"] == "conversion" and spine["stage"] == "growth"
         and spine["objective"]["target"]["value"] == 1200),
        ("③ market/channel giữ nguyên (bet-only)",
         bet.get("market") == ["Chưa ai làm phác đồ cho da nhạy cảm"] and bet.get("channel") == ["TikTok", "Zalo"]),
        ("④ compat: wedge từ tệp + usp từ định vị",
         ie.get("wedge") == "Dân văn phòng da nhạy cảm · Mẹ bỉm"
         and _DB.get("fields", {}).get("usp") == "Phục hồi da chuẩn y khoa, đồng hành 1:1"),
    ]
    # ⑤ downstream: _spine_anchor đọc spine vừa ghi (KHÔNG đổi hàm) → có định vị + hướng tăng trưởng + giá
    anchor = B._spine_anchor(ie)
    res.append(("⑤ _spine_anchor đọc spine mới: có định vị + hướng tăng trưởng + đòn bẩy giá",
                "Định vị" in anchor and "Chốt đơn" in anchor and "Đòn bẩy giá" in anchor and "CAO CẤP" in anchor))
    # rác → enum ''
    await B.save_strategy_input(user_id=1, payload={"price_posture": "loạn", "growth_focus": "xyz", "segment": []})
    sp2 = _DB["intake_extra"]["spine"]
    res.append(("③ rác → enum '' (price/growth)",
                sp2["positioning"]["price_posture"] == "" and sp2["growth_focus"] == ""))
    return res


def main():
    r = asyncio.run(_run()); ok = True
    for n, p in r:
        print(f"  {'✅' if p else '❌'} {n}"); ok = ok and p
    print("R2-P1a regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
