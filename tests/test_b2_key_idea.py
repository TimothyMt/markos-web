"""Regression test B2 — CHAIN-V2 T4+T5 (Key Idea theo đợt + funnel map per idea).

Chạy KHÔNG cần key LLM / DB: stub llm_router + storage.v2, drive HÀM THẬT
(suggest_key_ideas, save_key_idea, gen_funnel_map_for_idea).

Chốt các điều dễ vỡ:
  ① save_key_idea: append + gen id, dedupe theo id (update giữ funnel_map cũ),
     window rỗng → draft / đủ window → active, goal chuẩn hoá về enum.
  ② gen_funnel_map_for_idea: validate lọc tier rác + post thiếu khoá; posts KHÔNG rỗng;
     ratio UỐN theo goal (conversion → khung nặng-đáy vào prompt + ra ratio khi LLM bỏ trống;
     goal='' → lưới cuối 60/30/10); degrade: LLM ra rác hết → dựng tối thiểu từ messaging pillars.
  ③ suggest_key_ideas degrade: KHÔNG playbook_struct → seed từ messaging.pillars, vẫn ra ideas.

Chạy:  python3 tests/test_b2_key_idea.py    (exit 0 = pass)
LƯU Ý: chỉ chứng minh PLUMBING (validate/degrade/ratio-hint tới tay model). Model có xoay
       góc đánh hợp lý / phân bổ tỉnh táo không → soi output thật trên staging.
"""
import sys, os, types, asyncio, json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {
            "core": "Da khỏe từ gốc, không phụ thuộc liệu trình",
            "pillars": [
                {"icon": "🔬", "territory": "Khoa học làn da", "angle": "giải thích cơ chế da", "proof": "máy soi 50x"},
                {"icon": "💬", "territory": "Chuyện nghề spa", "angle": "kể hậu trường", "proof": ""},
            ],
            "voice": {"do": ["ấm áp, thật"], "dont": ["nói phét"]},
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

    class _AnyAsync:
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles()
    fake_v2.skill_runs = _AnyAsync()
    sys.modules["storage.v2"] = fake_v2
    sys.modules.setdefault("storage", types.ModuleType("storage"))

    fake_R = types.ModuleType("tools.llm_router")
    class TaskType:
        OPS_BRIEF = "ops_brief"; OPS_CONTENT_CREATIVE = "ops_creative"; INTAKE_JSON = "intake_json"
    fake_R.TaskType = TaskType
    async def _boot(**kw): return {"output": "{}"}
    fake_R.call = _boot
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return _DB, fake_R


_DB, R = _install_stubs()
import webapp.business as B

B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
async def _latest(uid, name): return "Chiến lược: phòng khám da chuẩn y khoa." if name == "synthesis" else ""
B._latest_content = _latest

CAPTURED = []
_MODE = {"funnel": "good"}   # 'good' | 'garbage'
async def _fake_call(task_type=None, system="", user="", max_tokens=0, **kw):
    CAPTURED.append({"system": system, "user": user})
    if "DANH SÁCH BÀI DỰ KIẾN" in system:          # ③ gen_funnel_map_for_idea
        if _MODE["funnel"] == "garbage":
            return {"output": json.dumps({"ratio": "", "posts": [
                {"tier": "XXX", "channel": "FB", "role": "rác tier"},          # tier rác → bỏ
                {"tier": "tofu", "channel": "", "role": "thiếu kênh"},         # thiếu channel → bỏ
            ]})}
        return {"output": json.dumps({"ratio": "", "posts": [
            {"tier": "tofu", "channel": "Reels 15s", "role": "khơi nhận biết", "note": ""},
            {"tier": "MOFU", "channel": "Bài dài FB", "role": "nuôi cân nhắc"},   # tier HOA → chuẩn hoá lower
            {"tier": "bofu", "channel": "", "role": "thiếu kênh → bỏ"},          # thiếu channel → bỏ
            {"tier": "zzz", "channel": "X", "role": "tier rác → bỏ"},            # tier rác → bỏ
        ]})}
    # ① suggest_key_ideas
    return {"output": json.dumps({"ideas": [
        {"title": "Tháng hiểu da", "angle": "chống vẽ liệu trình", "source_ref": "Khoa học làn da", "goal": "awareness"},
        {"title": "Xả kho cuối năm", "angle": "ưu đãi thật", "source_ref": "Chuyện nghề spa", "goal": "conversion"},
    ]})}
R.call = _fake_call


async def _run():
    res = []

    # ---- ① save_key_idea: tạo mới, id sinh, funnel_map rỗng, window rỗng → draft ----
    r = await B.save_key_idea(user_id=1, title="Tháng hiểu da", angle="chống vẽ liệu trình",
                              source="max", source_ref="Khoa học làn da", goal="awareness")
    ki = r.get("key_idea", {})
    kid = ki.get("id")
    res += [
        ("① save tạo mới ok + có id", bool(r.get("ok")) and bool(kid)),
        ("① funnel_map khởi tạo rỗng", ki.get("funnel_map") == {"ratio": "", "posts": []}),
        ("① window rỗng → status draft", ki.get("status") == "draft"),
        ("① goal hợp lệ giữ nguyên", ki.get("goal") == "awareness"),
    ]

    # ---- ① goal rác → '' ; đủ window → active ----
    r2 = await B.save_key_idea(user_id=1, title="Đợt có hạn", goal="bậy bạ",
                               window_start="2026-08-01", window_end="2026-08-15")
    res += [
        ("① goal rác → rỗng", r2["key_idea"]["goal"] == ""),
        ("① đủ window → status active", r2["key_idea"]["status"] == "active"),
    ]

    # ---- ① dedupe theo id: update meta GIỮ funnel_map cũ ----
    _DB["intake_extra"]["key_ideas"][0]["funnel_map"] = {"ratio": "65/25/10", "posts": [{"tier": "tofu", "channel": "FB", "role": "x", "note": ""}]}
    r3 = await B.save_key_idea(user_id=1, id=kid, title="Tháng hiểu da (đã sửa)")
    ideas = _DB["intake_extra"]["key_ideas"]
    res += [
        ("① update theo id KHÔNG tạo bản mới", len([i for i in ideas if i["id"] == kid]) == 1),
        ("① update giữ funnel_map cũ", r3["key_idea"]["funnel_map"]["ratio"] == "65/25/10"),
        ("① update đổi được title", r3["key_idea"]["title"] == "Tháng hiểu da (đã sửa)"),
    ]

    # ---- ② gen_funnel_map_for_idea: validate lọc rác, tier chuẩn enum, posts không rỗng ----
    # set goal=conversion cho key idea kid để soi ratio-by-goal
    for i in ideas:
        if i["id"] == kid:
            i["goal"] = "conversion"
    _MODE["funnel"] = "good"; CAPTURED.clear()
    g = await B.gen_funnel_map_for_idea(user_id=1, id=kid)
    fm = g.get("funnel_map", {})
    posts = fm.get("posts", [])
    tiers = {p["tier"] for p in posts}
    up = CAPTURED[-1]["user"]
    res += [
        ("② gen ok", bool(g.get("ok"))),
        ("② lọc tier rác + post thiếu khoá (còn 2/4)", len(posts) == 2),
        ("② tier chuẩn về enum lowercase", tiers <= set(B._KI_TIERS) and "mofu" in tiers),
        ("② mọi post đủ tier+channel+role", all(p["tier"] and p["channel"] and p["role"] for p in posts)),
        ("② goal=conversion → khung nặng-đáy 20/30/50 vào prompt", "20/30/50" in up),
        ("② LLM bỏ trống ratio → lấy khung theo goal (20/30/50)", fm.get("ratio") == "20/30/50"),
    ]

    # ---- ② ratio goal='' → lưới cuối 60/30/10 trong prompt ----
    r4 = await B.save_key_idea(user_id=1, title="Ý không mục tiêu")     # goal ''
    CAPTURED.clear()
    await B.gen_funnel_map_for_idea(user_id=1, id=r4["key_idea"]["id"])
    res.append(("② goal rỗng → prompt nhắc lưới cuối 60/30/10", "60/30/10" in CAPTURED[-1]["user"]))

    # ---- ② degrade: LLM ra rác hết → dựng tối thiểu từ messaging pillars (KHÔNG cụt) ----
    _MODE["funnel"] = "garbage"
    gd = await B.gen_funnel_map_for_idea(user_id=1, id=kid)
    res += [
        ("② degrade posts KHÔNG rỗng (từ pillars)", bool(gd.get("ok")) and len(gd["funnel_map"]["posts"]) >= 1),
        ("② degrade post hợp lệ tier tofu", all(p["tier"] == "tofu" for p in gd["funnel_map"]["posts"])),
    ]

    # ---- ③ suggest degrade: KHÔNG playbook_struct → seed messaging.pillars ----
    assert "playbook_struct" not in _DB["intake_extra"]
    s = await B.suggest_key_ideas(user_id=1)
    ideas_s = s.get("ideas", [])
    res += [
        ("③ suggest ra ideas dù thiếu playbook_struct", len(ideas_s) == 2),
        ("③ ideas chuẩn hoá source=max + goal enum", all(i["source"] == "max" for i in ideas_s)
         and ideas_s[1]["goal"] == "conversion"),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("B2 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
