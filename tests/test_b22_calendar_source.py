"""Regression test B2.2 — Lịch (calendar_plan) đổi nguồn sang Layered (content_matrix + key_ideas).

Chạy KHÔNG cần key LLM / DB: stub storage.v2 + campaign_plan, drive HÀM THẬT calendar_plan
(+ _parse_cadence, _build_matrix_always, _build_keyidea_bands).

Chốt điều dễ vỡ:
  ① _parse_cadence: '2 bài/tuần' → nhiều slot/tuần · '1 bài/2 tuần' → cách tuần · '2 bài/tháng' →
     thưa · '' → [] (không lịch) · chuỗi lạ → nhịp thưa mặc định (KHÔNG ném).
  ② calendar_plan NỀN: có content_matrix → alwaysOn dựng từ cells (mang pillar/tier/track_role);
     ô không cadence KHÔNG lên lịch. Degrade: không content_matrix → về pillars cũ.
  ③ calendar_plan CHIẾN DỊCH: có key_ideas (window+funnel_map) → band track camp (campaignId=id,
     phase 'TOFU #k' duy nhất, mang sibling_group). Degrade: không key_ideas → campaigns_v2 cũ (cờ legacy).
  ④ Hợp đồng output GIỮ: alwaysOn/campaigns/orphans/weeks; thẻ đã duyệt (calendar_posts) round-trip
     (không rơi orphan) qua key ổn định oc|id|phase.

Chạy:  python3 tests/test_b22_calendar_source.py    (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs(extra):
    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa", "current_channels": "Facebook, TikTok", "intake_extra": extra}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            return True

    class _Campaigns:
        _rows = []
        async def list_campaigns_v2(self, uid, limit=30):
            return list(self._rows)

    class _AnyAsync:
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles()
    fake_v2.campaigns_v2 = _Campaigns()
    fake_v2.skill_runs = _AnyAsync()
    sys.modules["storage.v2"] = fake_v2
    sys.modules.setdefault("storage", types.ModuleType("storage"))
    fake_R = types.ModuleType("tools.llm_router")
    class TaskType: OPS_BRIEF = "ops_brief"
    fake_R.TaskType = TaskType
    async def _c(**kw): return {"output": "{}"}
    fake_R.call = _c
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return fake_v2


_EXTRA = {
    "horizon": "60",   # 9 tuần
    "messaging": {"core": "Da khỏe từ gốc", "pillars": [
        {"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"},
        {"icon": "💬", "territory": "Chuyện nghề spa", "angle": "hậu trường"}]},
    "content_matrix": {"cells": [
        {"pillar": "Khoa học làn da", "tier": "tofu", "role": "Khơi hiểu da", "platforms": ["Reels 15s"], "cadence": "2 bài/tuần"},
        {"pillar": "Chuyện nghề spa", "tier": "mofu", "role": "Nuôi tin cậy", "platforms": ["Bài FB"], "cadence": "1 bài/2 tuần"},
        {"pillar": "Khoa học làn da", "tier": "bofu", "role": "Chốt minh bạch", "platforms": [], "cadence": ""},  # không cadence → bỏ
    ]},
    "key_ideas": [{
        "id": "k1", "title": "Tháng hiểu da", "angle": "chống vẽ liệu trình", "goal": "awareness",
        "window_start": "2026-07-13", "window_end": "2026-08-09",   # ~4 tuần từ anchor
        "funnel_map": {"ratio": "65/25/10", "posts": [
            {"tier": "tofu", "channel": "Reels 15s", "role": "Soi da 50x", "pillar": "Khoa học làn da", "sibling_group": "s1"},
            {"tier": "tofu", "channel": "TikTok", "role": "Biến thể ngắn", "pillar": "Khoa học làn da", "sibling_group": "s1"},
            {"tier": "bofu", "channel": "Zalo OA", "role": "Ưu đãi có hạn", "pillar": "", "sibling_group": ""},
        ]}}],
}

fake_v2 = _install_stubs(_EXTRA)
import webapp.business as B
B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
async def _cp(uid): return {"pillars": []}   # không dùng pillars cũ khi có content_matrix
B.campaign_plan = _cp


async def _run():
    res = []

    # ---- ① _parse_cadence ----
    mw = 8
    res += [
        ("① '2 bài/tuần' → 2 slot/tuần", B._parse_cadence("2 bài/tuần", mw).count(1) == 2),
        ("① '1 bài/2 tuần' → cách tuần (1,3,5..)", B._parse_cadence("1 bài/2 tuần", mw) == [1, 3, 5, 7]),
        ("① '2 bài/tháng' → thưa (~mỗi 2 tuần)", len(B._parse_cadence("2 bài/tháng", mw)) <= 5 and 1 in B._parse_cadence("2 bài/tháng", mw)),
        ("① '' → [] (không lịch)", B._parse_cadence("", mw) == []),
        ("① chuỗi lạ → nhịp thưa mặc định (không ném)", len(B._parse_cadence("khi rảnh", mw)) >= 1),
    ]

    # ---- ② + ③ + ④ calendar_plan với Layered ----
    plan = await B.calendar_plan(user_id=1)
    always = plan.get("alwaysOn", [])
    camps = plan.get("campaigns", [])
    a_pillars = {s.get("pillar", "") for s in always}
    a_tiers = {s.get("tier") for s in always}
    res += [
        ("② output đủ khoá hợp đồng", all(k in plan for k in ("alwaysOn", "campaigns", "orphans", "weeks", "days"))),
        ("② NỀN từ content_matrix (slot mang tier)", bool(always) and a_tiers <= {"tofu", "mofu", "bofu"}),
        ("② ô 'tofu 2 bài/tuần' rải nhiều slot", sum(1 for s in always if s.get("tier") == "tofu") >= 4),
        ("② ô KHÔNG cadence (bofu) KHÔNG lên lịch", "bofu" not in a_tiers),
        ("② slot mang track_role (vai-trò-ô)", all(s.get("track_role") for s in always)),
        ("③ CHIẾN DỊCH từ key_ideas (1 band)", len(camps) == 1 and camps[0]["campaignId"] == "k1"),
        ("③ band mang name = title key_idea", camps[0]["name"] == "Tháng hiểu da"),
        ("③ post phase duy nhất 'TOFU #k'", any(p["phase"] == "TOFU #1" for p in camps[0]["posts"]) and any(p["phase"] == "TOFU #2" for p in camps[0]["posts"])),
        ("③ post mang sibling_group (repurpose)", any(p.get("sibling_group") == "s1" for p in camps[0]["posts"])),
        ("③ band KHÔNG cờ legacy (nguồn mới)", not camps[0].get("legacy")),
    ]

    # ---- ④ thẻ đã duyệt round-trip (không rơi orphan) ----
    ph = camps[0]["posts"][0]["phase"]                       # vd 'TOFU #1'
    _EXTRA["calendar_posts"] = {f"oc|k1|{ph}": {"content": "Bài đã duyệt", "approved": True,
        "track": "camp", "ref": {"campaignId": "k1", "phase": ph}, "place": {"week": 1, "day": 1, "phase": ph}}}
    plan2 = await B.calendar_plan(user_id=1)
    saved_post = next((p for p in plan2["campaigns"][0]["posts"] if p["phase"] == ph), {})
    res += [
        ("④ thẻ đã duyệt khớp lại band (saved=True)", saved_post.get("saved") is True),
        ("④ thẻ đã duyệt KHÔNG rơi orphan", not plan2.get("orphans")),
    ]
    _EXTRA.pop("calendar_posts", None)

    # ---- ② degrade: bỏ content_matrix → về pillars cũ (campaign_plan) ----
    _cm = _EXTRA.pop("content_matrix")
    async def _cp2(uid): return {"pillars": [{"name": "Trụ cũ", "id": "p1", "posts_per_week": 1, "angles": ["a"]}]}
    B.campaign_plan = _cp2
    plan3 = await B.calendar_plan(user_id=1)
    res.append(("② degrade không content_matrix → NỀN từ pillars cũ",
                bool(plan3.get("alwaysOn")) and any(s.get("pillar") == "Trụ cũ" for s in plan3["alwaysOn"])))
    _EXTRA["content_matrix"] = _cm
    B.campaign_plan = _cp

    # ---- ③ degrade: bỏ key_ideas → campaigns_v2 cũ (cờ legacy) ----
    _ki = _EXTRA.pop("key_ideas")
    fake_v2.campaigns_v2._rows = [{"id": "c9", "name": "Đợt cũ", "start_date": "2026-07-13",
                                   "end_date": "2026-07-26", "primary_goal": "đẩy đơn"}]
    plan4 = await B.calendar_plan(user_id=1)
    res.append(("③ degrade không key_ideas → campaigns_v2 cũ có cờ legacy",
                bool(plan4.get("campaigns")) and plan4["campaigns"][0].get("legacy") is True))
    _EXTRA["key_ideas"] = _ki
    fake_v2.campaigns_v2._rows = []

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("B2.2 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
