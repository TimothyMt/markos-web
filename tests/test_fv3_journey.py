"""Test FV3-5 — funnel_map.journey[] (rào cản từ T3) + posts[].journey_stage (doc §4.1).

Stub storage + ÉP LLM trả journey + posts, drive HÀM THẬT (gen_funnel_map_for_idea) + helper thuần.

Chốt đúng phạm vi brief FV3-5:
  ① Helper chuẩn hoá stage: alias/substring → stage chuẩn; lạ → ''.
  ② Cắt journey theo archetype: impulse bỏ 'tìm hiểu'/'cân nhắc'; demand_gen/trust đủ 5.
  ③ _norm_journey: stage ngoài allowed bị bỏ · dedupe · thứ tự canonical.
  ④ SEAM: mỗi posts[] có journey_stage HỢP LỆ = 1 stage trong journey (LLM ghi lạ/thiếu → snap theo tier).
  ⑤ gen_funnel_map_for_idea ghi funnel_map.journey + journey_stage mỗi bài.

Chạy:  python tests/test_fv3_journey.py   (exit 0 = pass)
"""
import sys, os, types, asyncio, json as _json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {"core": "Da khỏe từ gốc",
                      "pillars": [{"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"}]},
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
        async def list_campaigns_v2(self, uid, limit=20): return []

    class _SkillRuns:
        async def list_skill_runs(self, uid, limit=30): return []

    class _Users:
        async def get_user(self, uid): return None

    class _Tracked:
        async def list_tracked_by_user(self, uid): return []

    class _BrandVoice:
        async def get_brand_voice(self, uid): return None

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles(); fake_v2.campaigns_v2 = _Campaigns()
    fake_v2.skill_runs = _SkillRuns(); fake_v2.users = _Users()
    sys.modules["storage.v2"] = fake_v2
    fake_storage = types.ModuleType("storage")
    fake_storage.tracked_competitors = _Tracked(); fake_storage.brand_voice = _BrandVoice()
    sys.modules["storage"] = fake_storage

    fake_R = types.ModuleType("tools.llm_router")
    class TaskType:
        OPS_BRIEF = "ops_brief"; OPS_CONTENT_CREATIVE = "ops_creative"; INTAKE_JSON = "intake_json"
    fake_R.TaskType = TaskType
    fake_R.call = None   # set per-test
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return _DB, fake_R


_DB, _R = _install_stubs()
import webapp.business as B

B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
async def _users(limit=50): return [{"id": 1}]
B.list_users = _users


def _llm_returns(payload):
    async def _call(**kw): return {"output": _json.dumps(payload)}
    _R.call = _call


async def _run():
    res = []

    # ---- ① _norm_journey_stage ----
    res += [
        ("① 'awareness' → nhận biết", B._norm_journey_stage("awareness") == "nhận biết"),
        ("① 'So sánh giá' (substring) → cân nhắc", B._norm_journey_stage("So sánh giá") == "cân nhắc"),
        ("① 'retention' → quay lại", B._norm_journey_stage("retention") == "quay lại"),
        ("① rác → ''", B._norm_journey_stage("linh tinh gì đó") == ""),
    ]

    # ---- ② cắt theo archetype ----
    imp = B._journey_stages_for_archetype("impulse")
    dg = B._journey_stages_for_archetype("demand_gen")
    res += [
        ("② impulse bỏ 'cân nhắc' + 'tìm hiểu'", "cân nhắc" not in imp and "tìm hiểu" not in imp),
        ("② impulse vẫn có nhận biết/mua/quay lại",
         all(s in imp for s in ("nhận biết", "mua", "quay lại"))),
        ("② demand_gen đủ 5 chặng", len(dg) == 5 and "cân nhắc" in dg),
        ("② archetype lạ → full 5", len(B._journey_stages_for_archetype("xyz")) == 5),
    ]

    # ---- ③ _norm_journey: bỏ stage ngoài allowed · dedupe · thứ tự canonical ----
    raw_j = [
        {"stage": "mua", "barrier": "sợ đắt", "content_role": "bảng giá minh bạch"},
        {"stage": "cân nhắc", "barrier": "sợ kích ứng", "content_role": "review da thật"},   # ngoài allowed impulse
        {"stage": "nhận biết", "barrier": "chưa biết brand", "content_role": "câu chuyện"},
        {"stage": "nhận biết", "barrier": "trùng", "content_role": "trùng"},                  # dup → bỏ
        {"stage": "linh tinh", "barrier": "x", "content_role": "y"},                          # lạ → bỏ
    ]
    nj = B._norm_journey(raw_j, B._journey_stages_for_archetype("impulse"))
    stages = [j["stage"] for j in nj]
    res += [
        ("③ 'cân nhắc' ngoài allowed impulse → bị bỏ", "cân nhắc" not in stages),
        ("③ dedupe: 'nhận biết' chỉ 1 lần", stages.count("nhận biết") == 1),
        ("③ stage lạ bị bỏ", "linh tinh" not in stages),
        ("③ thứ tự canonical (nhận biết trước mua)",
         stages.index("nhận biết") < stages.index("mua")),
        ("③ giữ barrier từ input", next((j["barrier"] for j in nj if j["stage"] == "mua"), "") == "sợ đắt"),
    ]

    # ---- ④ _snap_stage_to_journey (seam) ----
    js = ["nhận biết", "mua", "quay lại"]
    res += [
        ("④ stage hợp lệ trong journey → giữ", B._snap_stage_to_journey("mua", "bofu", js) == "mua"),
        ("④ stage lạ + tier bofu → snap vào 'mua'", B._snap_stage_to_journey("", "bofu", js) == "mua"),
        ("④ stage ngoài journey ('cân nhắc') → snap về stage có thật",
         B._snap_stage_to_journey("cân nhắc", "tofu", js) in js),
        ("④ journey rỗng → suy từ tier (vẫn có stage)", B._snap_stage_to_journey("", "tofu", []) == "nhận biết"),
    ]

    # ---- ⑤ gen_funnel_map_for_idea: journey + posts[].journey_stage ----
    _llm_returns({
        "ratio": "70/25/5", "offers": {}, "risks": [],
        "journey": [
            {"stage": "nhận biết", "trigger": "thấy quảng cáo", "barrier": "chưa biết tới",
             "content_role": "câu chuyện thương hiệu"},
            {"stage": "mua", "trigger": "có ưu đãi", "barrier": "sợ không hợp da",
             "content_role": "cam kết đổi trả"},
        ],
        "posts": [
            {"tier": "tofu", "channel": "TikTok", "format": "video 15s", "role": "khơi",
             "journey_stage": "nhận biết", "pillar": ""},
            {"tier": "bofu", "channel": "Facebook", "format": "bài viết", "role": "chốt",
             "journey_stage": "giai đoạn lạ", "pillar": ""},          # stage lạ → snap
            {"tier": "mofu", "channel": "Facebook", "format": "bài viết", "role": "nuôi",
             "pillar": ""},                                            # thiếu journey_stage → snap theo tier
        ],
    })
    _DB["intake_extra"]["key_ideas"] = [{"id": "kj", "title": "Đợt hành trình", "purpose": "branding",
                                         "channels": ["tiktok", "facebook"], "funnel_map": {"ratio": "", "posts": []}}]
    g = await B.gen_funnel_map_for_idea(user_id=1, id="kj")
    fm = g.get("funnel_map", {})
    jr = fm.get("journey", [])
    jstages = [j["stage"] for j in jr]
    posts = fm.get("posts", [])
    allowed = set(B._journey_stages_for_archetype(
        __import__("frameworks.industry_context", fromlist=["get_purchase_archetype"])
        .get_purchase_archetype("Spa - thẩm mỹ") or ""))
    res += [
        ("⑤ funnel_map.journey là list không rỗng", isinstance(jr, list) and len(jr) >= 1),
        ("⑤ mỗi chặng journey có stage+barrier+content_role",
         all({"stage", "barrier", "content_role"} <= set(j.keys()) for j in jr)),
        ("⑤ journey stage ⊆ allowed theo archetype ngành", all(s in allowed for s in jstages)),
        ("⑤ MỌI bài có journey_stage không rỗng", posts and all(p.get("journey_stage") for p in posts)),
        ("⑤ SEAM: journey_stage mỗi bài ∈ journey stages (khi journey có)",
         all(p["journey_stage"] in jstages for p in posts) if jstages else True),
        ("⑤ bài stage lạ được snap về stage hợp lệ",
         next((p["journey_stage"] for p in posts if p["role"] == "chốt"), None) in jstages),
        ("⑤ bài thiếu stage được snap (không rỗng)",
         bool(next((p["journey_stage"] for p in posts if p["role"] == "nuôi"), ""))),
    ]
    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-5 journey:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
