"""Regression test B6 — 3 artifact lấy từ khoá: Risk & Contingency + Offer theo tầng (A+B).
(% tỉ trọng pillar = B6-C, test riêng trong cùng file khi làm C.)

Chạy KHÔNG cần key/DB: stub storage.v2 + tools.llm_router (ghi lại prompt + trả JSON điều khiển).

Chốt điều dễ vỡ:
  ① _norm_risks: enum mức (low→thấp, rác→''), cắt, cap 6, bỏ rỗng · _norm_offers: chỉ giữ tier hợp lệ.
  ② gen_funnel_map_for_idea: prompt CÓ schema offers+risks · parse → funnel_map.offers + idea.risks (chuẩn hoá).
  ③ save_key_idea(risks=…): human override chuẩn hoá · risks=None → KHÔNG đụng risks cũ.
  ④ gen_calendar_post camp: bơm OFFER tầng của đợt vào prompt (anchor B).

Chạy:  python3 tests/test_b6_course_artifacts.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_DB = {"intake_extra": {"key_ideas": [
    {"id": "k1", "title": "Đợt phủ nhận biết", "angle": "góc X", "goal": "awareness",
     "window_start": "2026-08-01", "window_end": "2026-08-20", "status": "active",
     "focus_tier": "", "focus_pillars": [], "funnel_map": {"ratio": "", "posts": []},
     "risks": [{"risk": "cũ", "likelihood": "cao", "impact": "cao", "backup": "cũ B"}]}]}}
_CALLS = []


def _install():
    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa", "current_channels": "Facebook, TikTok",
                    "intake_extra": _DB["intake_extra"]}
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
    class TT: OPS_BRIEF = "b"; OPS_CONTENT_CREATIVE = "c"
    fr.TaskType = TT
    async def _c(**k):
        _CALLS.append(k)
        sysp = k.get("system", "")
        if "DANH SÁCH BÀI" in sysp:   # gen_funnel_map_for_idea
            return {"output": '{"ratio":"65/25/10",'
                    '"offers":{"tofu":"Xem clip mẹo da khô","mofu":"Đặt tư vấn 1:1 miễn phí","bofu":"Giảm 15% gói phục hồi"},'
                    '"risks":[{"risk":"CPL cao hơn target","likelihood":"trung bình","impact":"cao","backup":"chuyển sang TikTok organic"},'
                    '{"risk":"creative không convert","likelihood":"LOW","impact":"med","backup":"đổi UGC thật"},'
                    '{"risk":"","backup":""}],'
                    '"posts":[{"tier":"tofu","channel":"Reels 15s","role":"khơi tò mò","pillar":"","sibling_group":"","note":""}]}'}
        return {"output": "Bài mẫu."}   # gen_calendar_post
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
async def _lc(uid, name): return ""
B._latest_content = _lc


async def _run():
    res = []
    NR, NO, NL = B._norm_risks, B._norm_offers, B._norm_risk_level
    # ① pure
    r = NR([{"risk": "a", "likelihood": "low", "impact": "HIGH", "backup": "b"},
            {"risk": "", "backup": ""},                          # rỗng → bỏ
            {"risk": "c", "likelihood": "xyz", "impact": "", "backup": "d"}] + [{"risk": f"x{i}", "backup": "y"} for i in range(8)])
    res += [
        ("① _norm_risks: enum low→thấp/HIGH→cao, rỗng bỏ, rác→''",
         r[0]["likelihood"] == "thấp" and r[0]["impact"] == "cao" and r[1]["risk"] == "c" and r[1]["likelihood"] == ""),
        ("① _norm_risks cap 6", len(r) == 6),
        ("① _norm_offers giữ tier hợp lệ, bỏ rác",
         NO({"tofu": "A", "mofu": "", "bofu": "B", "xxx": "z"}) == {"tofu": "A", "bofu": "B"}),
        ("① _norm_risk_level", NL("medium") == "trung bình" and NL("cao") == "cao" and NL("?") == ""),
    ]
    # ② gen_funnel_map_for_idea
    _CALLS.clear()
    out = await B.gen_funnel_map_for_idea(user_id=1, id="k1")
    idea = _DB["intake_extra"]["key_ideas"][0]
    sysp = _CALLS[0]["system"] if _CALLS else ""
    res += [
        ("② prompt gen CÓ schema offers+risks", '"offers"' in sysp and '"risks"' in sysp),
        ("② parse → funnel_map.offers 3 tầng", idea["funnel_map"].get("offers") == {"tofu": "Xem clip mẹo da khô", "mofu": "Đặt tư vấn 1:1 miễn phí", "bofu": "Giảm 15% gói phục hồi"}),
        ("② parse → idea.risks chuẩn hoá (2 hợp lệ, rỗng bị bỏ, LOW/med→thấp/trung bình)",
         len(idea["risks"]) == 2 and idea["risks"][1]["likelihood"] == "thấp" and idea["risks"][1]["impact"] == "trung bình"),
    ]
    # ③ save_key_idea risks override + None không đụng
    await B.save_key_idea(user_id=1, id="k1", title="Đợt phủ nhận biết",
                          risks=[{"risk": "R", "likelihood": "cao", "impact": "thấp", "backup": "P"}, {"risk": "", "backup": ""}])
    idea = _DB["intake_extra"]["key_ideas"][0]
    res.append(("③ save risks override chuẩn hoá (rỗng bị bỏ)", len(idea["risks"]) == 1 and idea["risks"][0]["risk"] == "R"))
    await B.save_key_idea(user_id=1, id="k1", title="Đợt phủ nhận biết", goal="conversion")   # risks=None
    idea = _DB["intake_extra"]["key_ideas"][0]
    res.append(("③ save risks=None KHÔNG xoá risks cũ", len(idea["risks"]) == 1 and idea["goal"] == "conversion"))
    # ④ gen_calendar_post camp bơm offer tầng
    _CALLS.clear()
    await B.gen_calendar_post(user_id=1, track="camp", campaign_id="k1", tier="mofu")
    userp = next((c["user"] for c in _CALLS if "user" in c), "")
    res.append(("④ calendar_post camp bơm OFFER tầng MOFU vào prompt",
                "OFFER" in userp and "Đặt tư vấn 1:1 miễn phí" in userp))
    return res


def main():
    r = asyncio.run(_run()); ok = True
    for n, p in r:
        print(f"  {'✅' if p else '❌'} {n}"); ok = ok and p
    print("B6 (A+B) regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
