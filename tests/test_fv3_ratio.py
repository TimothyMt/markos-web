"""Test FV3-3 — Tỉ lệ phễu derived từ purpose + ratio_source override (human wins).

Chạy KHÔNG cần key LLM / DB: stub storage + llm_router, drive HÀM THẬT
(_norm_ratio, _purpose_ratio_hint, save_funnel_ratio, gen_funnel_map_for_idea, biz_data.bizPurposes).

Chốt đúng phạm vi brief FV3-3 (doc §3.2):
  ① _norm_ratio: '60/30/10' giữ · '6/3/1' scale→100 · tổng≠100 scale · rác → ''.
  ② _purpose_ratio_hint: purpose hợp lệ → bảng + why · purpose rỗng nhưng có goal → _GOAL_RATIO (no why) ·
     cả hai rỗng → _DEFAULT_RATIO.
  ③ save_funnel_ratio: ratio hợp lệ → ghi + ratio_source='user' · rác → lỗi · chưa có funnel_map → tạo tối thiểu.
  ④ gen_funnel_map_for_idea: purpose (chưa khoá) → ratio suy-từ-purpose + source='derived' ·
     ĐÃ ratio_source='user' → GIỮ ratio người dùng, source vẫn 'user' (Max KHÔNG đè — WIRING §2).
  ⑤ biz_data.bizPurposes: 7 mục, mỗi mục có key/label/ratio/why.

Chạy:  python tests/test_fv3_ratio.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {
            "core": "Da khỏe từ gốc",
            "pillars": [{"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"}],
        },
    }}

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "current_channels": "Facebook, TikTok",
                    "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None:
                _DB["intake_extra"] = intake_extra
            return True

    class _Campaigns:
        async def list_campaigns_v2(self, uid, limit=20):
            return []

    class _SkillRuns:
        async def list_skill_runs(self, uid, limit=30):
            return []

    class _Users:
        async def get_user(self, uid):
            return None

    class _Tracked:
        async def list_tracked_by_user(self, uid):
            return []

    class _BrandVoice:
        async def get_brand_voice(self, uid):
            return None

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles()
    fake_v2.campaigns_v2 = _Campaigns()
    fake_v2.skill_runs = _SkillRuns()
    fake_v2.users = _Users()
    sys.modules["storage.v2"] = fake_v2
    fake_storage = types.ModuleType("storage")
    fake_storage.tracked_competitors = _Tracked()
    fake_storage.brand_voice = _BrandVoice()
    sys.modules["storage"] = fake_storage

    fake_R = types.ModuleType("tools.llm_router")
    class TaskType:
        OPS_BRIEF = "ops_brief"; OPS_CONTENT_CREATIVE = "ops_creative"; INTAKE_JSON = "intake_json"
    fake_R.TaskType = TaskType
    async def _boot(**kw): return {"output": "{}"}   # LLM rỗng → gen degrade từ pillars
    fake_R.call = _boot
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return _DB


_DB = _install_stubs()
import webapp.business as B

B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
async def _users(limit=50): return [{"id": 1}]
B.list_users = _users


async def _run():
    res = []

    # ---- ① _norm_ratio ----
    res += [
        ("① '60/30/10' giữ nguyên", B._norm_ratio("60/30/10") == "60/30/10"),
        ("① '6/3/1' scale → tổng 100", B._norm_ratio("6/3/1") == "60/30/10"),
        ("① tổng≠100 scale về 100", sum(int(x) for x in B._norm_ratio("50/30/30").split("/")) == 100),
        ("① rác/thiếu số → ''", B._norm_ratio("nhiều/ít") == "" and B._norm_ratio("60/40") == ""),
    ]

    # ---- ② _purpose_ratio_hint ----
    rp, wp = B._purpose_ratio_hint("branding")
    rg, wg = B._purpose_ratio_hint("", "conversion")     # purpose rỗng → goal cũ
    rd, wd = B._purpose_ratio_hint("", "")               # cả hai rỗng → default
    res += [
        ("② purpose=branding → bảng '70/25/5' + có why", rp == "70/25/5" and bool(wp)),
        ("② purpose rỗng, goal=conversion → _GOAL_RATIO (no why)", rg == B._GOAL_RATIO["conversion"] and wg == ""),
        ("② cả hai rỗng → _DEFAULT_RATIO", rd == B._DEFAULT_RATIO),
    ]

    # ---- ③ save_funnel_ratio ----
    _DB["intake_extra"]["key_ideas"] = [{"id": "kx", "title": "Đợt test ratio", "purpose": "conversion"}]
    ok = await B.save_funnel_ratio(user_id=1, id="kx", ratio="10/20/70")
    bad = await B.save_funnel_ratio(user_id=1, id="kx", ratio="linh tinh")
    kx = next(i for i in _DB["intake_extra"]["key_ideas"] if i["id"] == "kx")
    res += [
        ("③ ratio hợp lệ → ghi + source='user'",
         ok.get("ok") and kx["funnel_map"]["ratio"] == "10/20/70" and kx["funnel_map"]["ratio_source"] == "user"),
        ("③ ratio rác → lỗi (không ghi đè)", "error" in bad and kx["funnel_map"]["ratio"] == "10/20/70"),
        ("③ tạo funnel_map tối thiểu có posts[]", isinstance(kx["funnel_map"].get("posts"), list)),
    ]

    # ---- ④ gen_funnel_map_for_idea: derived vs user-lock ----
    # (a) purpose, CHƯA khoá → source='derived', ratio suy-từ-purpose (LLM rỗng → dùng khung)
    _DB["intake_extra"]["key_ideas"] = [{"id": "kd", "title": "Đợt chốt đơn", "purpose": "conversion",
                                         "funnel_map": {"ratio": "", "posts": []}}]
    gd = await B.gen_funnel_map_for_idea(user_id=1, id="kd")
    fmd = gd.get("funnel_map", {})
    # (b) ĐÃ ratio_source='user' → giữ ratio người dùng, không đè
    _DB["intake_extra"]["key_ideas"] = [{"id": "ku", "title": "Đợt user chốt tay", "purpose": "conversion",
                                         "funnel_map": {"ratio": "33/33/34", "ratio_source": "user", "posts": []}}]
    gu = await B.gen_funnel_map_for_idea(user_id=1, id="ku")
    fmu = gu.get("funnel_map", {})
    res += [
        ("④a chưa khoá → source='derived'", fmd.get("ratio_source") == "derived"),
        ("④a ratio suy-từ-purpose=conversion (20/30/50)", fmd.get("ratio") == "20/30/50"),
        ("④b user-lock → GIỮ ratio '33/33/34' (Max không đè)", fmu.get("ratio") == "33/33/34"),
        ("④b user-lock → source vẫn 'user'", fmu.get("ratio_source") == "user"),
    ]

    # ---- ⑤ biz_data.bizPurposes ----
    bd = await B.biz_data(user_id=1)
    bp = bd.get("bizPurposes")
    res += [
        ("⑤ bizPurposes 7 mục", isinstance(bp, list) and len(bp) == 7),
        ("⑤ mỗi mục có key/label/ratio/why",
         all(isinstance(x, dict) and {"key", "label", "ratio", "why"} <= set(x.keys()) for x in (bp or []))),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-3 ratio:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
