"""Regression test B5 — #4 Hướng tăng trưởng trọng tâm (growth_focus).

Chạy KHÔNG cần key/DB: _spine_anchor + _validate_growth_focus là HÀM THUẦN (không load DB);
save_spine dùng stub storage.v2 (như test_b4).

Chốt điều dễ vỡ:
  ① enum: acquisition/conversion/retention/referral hợp lệ · junk/rỗng → ''.
  ② _spine_anchor bơm khối growth khi có focus (nhãn VN + "TRỌNG SỐ" + đòn bẩy kênh/đo).
  ③ bỏ trống + có stage → GỢI Ý từ stage (launch→acquisition), gắn nhãn "GỢI Ý" (soft).
  ④ bỏ trống + không stage → KHÔNG có dòng growth.
  ⑤ EVAL Test-3: anchor(focus=conversion) ≠ anchor(no focus) — bơm vào mà output đổi.
  ⑥ save_spine: persist growth_focus hợp lệ · junk → '' · giữ human value (không đè bằng máy đoán).

Chạy:  python3 tests/test_b5_growth_focus.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_DB = {"intake_extra": {}}


def _install():
    class _Profiles:
        async def get_profile(self, uid): return {"industry": "Spa", "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None: _DB["intake_extra"] = intake_extra
            return {"ok": True}
    class _AnyAsync:
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f
    fake = types.ModuleType("storage.v2")
    fake.profiles = _Profiles(); fake.campaigns_v2 = _AnyAsync(); fake.skill_runs = _AnyAsync()
    sys.modules["storage.v2"] = fake
    sys.modules.setdefault("storage", types.ModuleType("storage"))
    fr = types.ModuleType("tools.llm_router")
    class TT: OPS_BRIEF = "b"
    fr.TaskType = TT
    async def _c(**k): return {"output": "{}"}
    fr.call = _c
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fr


_install()
import webapp.business as B
B.available = lambda: True
async def _e(): return None
B.ensure_client = _e
async def _p(r=None): return 1
B.pick_user_id = _p


async def _run():
    res = []
    V = B._validate_growth_focus
    res += [
        ("① enum hợp lệ giữ nguyên", all(V(x) == x for x in ("acquisition", "conversion", "retention", "referral"))),
        ("① junk/rỗng → ''", V("khong-biet") == "" and V("") == "" and V(None) == "" and V("ACQUISITION") == "acquisition"),
    ]
    # ② có focus → khối growth đầy đủ
    a_conv = B._spine_anchor({"spine": {"stage": "growth", "growth_focus": "conversion"}})
    res += [
        ("② anchor focus=conversion có nhãn VN + TRỌNG SỐ + đòn bẩy",
         "Chốt đơn" in a_conv and "TRỌNG SỐ" in a_conv and "retargeting" in a_conv
         and "Hướng tăng trưởng trọng tâm kỳ này" in a_conv),
    ]
    # ③ bỏ trống + stage=launch → gợi ý acquisition, gắn "GỢI Ý"
    a_sug = B._spine_anchor({"spine": {"stage": "launch"}})
    res += [
        ("③ bỏ trống + launch → gợi ý Kéo khách mới, nhãn GỢI Ý (soft)",
         "Kéo khách mới" in a_sug and "GỢI Ý" in a_sug),
    ]
    # ④ bỏ trống + không stage → KHÔNG có dòng growth
    a_none = B._spine_anchor({"spine": {"audience": {"who": "dân VP"}}})
    res += [
        ("④ không focus + không stage → không có dòng Hướng tăng trưởng",
         "Hướng tăng trưởng" not in a_none),
    ]
    # ⑤ EVAL Test-3 — bơm focus → output ĐỔI
    a_base = B._spine_anchor({"spine": {"stage": "growth"}})
    a_ret = B._spine_anchor({"spine": {"stage": "growth", "growth_focus": "retention"}})
    res += [
        ("⑤ EVAL-3: anchor(retention) khác anchor(base) + khác anchor(conversion)",
         a_ret != a_base and a_ret != a_conv and "Giữ khách quay lại" in a_ret),
    ]
    # ⑥ save_spine persist + junk → '' + không đè máy đoán
    await B.save_spine(user_id=1, spine={"stage": "launch", "growth_focus": "referral"})
    sp = _DB["intake_extra"]["spine"]
    await B.save_spine(user_id=1, spine={"stage": "launch", "growth_focus": "loạn"})
    sp2 = _DB["intake_extra"]["spine"]
    res += [
        ("⑥ save persist growth_focus hợp lệ", sp.get("growth_focus") == "referral"),
        ("⑥ save junk → '' (không persist máy đoán)", sp2.get("growth_focus") == ""),
    ]
    # ⑦ Định giá đòn bẩy (price_posture) — enum + anchor reflect + save
    VP = B._validate_price_posture
    a_pp = B._spine_anchor({"spine": {"positioning": {"price_posture": "premium"}}})
    a_nopp = B._spine_anchor({"spine": {"positioning": {"statement": "x"}}})
    await B.save_spine(user_id=1, spine={"positioning": {"price_posture": "value"}})
    sp3 = _DB["intake_extra"]["spine"]
    await B.save_spine(user_id=1, spine={"positioning": {"price_posture": "loạn"}})
    sp4 = _DB["intake_extra"]["spine"]
    res += [
        ("⑦ price_posture enum hợp lệ / junk → ''",
         VP("premium") == "premium" and VP("PARITY") == "parity" and VP("x") == "" and VP("") == ""),
        ("⑦ anchor phản ánh đòn bẩy giá khi có (CAO CẤP) + vắng khi không",
         "Đòn bẩy giá" in a_pp and "CAO CẤP" in a_pp and "Đòn bẩy giá" not in a_nopp),
        ("⑦ save persist price_posture hợp lệ + junk → ''",
         sp3["positioning"].get("price_posture") == "value" and sp4["positioning"].get("price_posture") == ""),
    ]
    return res


def main():
    r = asyncio.run(_run()); ok = True
    for n, p in r:
        print(f"  {'✅' if p else '❌'} {n}"); ok = ok and p
    print("B5 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
