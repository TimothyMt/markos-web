"""Regression test B2.1 — Layered: MA TRẬN NỘI DUNG (trụ×phễu×nền tảng) + ĐỢT NHẤN.

Chạy KHÔNG cần key LLM / DB: stub llm_router + storage.v2, drive HÀM THẬT
(gen_content_matrix, save_key_idea +focus_*, gen_funnel_map_for_idea +pillar/sibling_group).

Chốt các điều dễ vỡ:
  ① gen_content_matrix: validate lọc tier rác + ô thiếu role; pillar khớp trụ messaging (lạ → trụ đầu);
     platforms rỗng → điền kênh đang dùng; degrade KHÔNG playbook_struct → vẫn ra cells từ pillars (KHÔNG cụt).
  ② save_key_idea đợt nhấn: focus_tier rác → ''; focus_pillars không-list → []; hợp lệ giữ nguyên;
     update meta GIỮ funnel_map cũ (KHÔNG hồi quy B2).
  ③ gen_funnel_map_for_idea: posts mang pillar (khớp lỏng, lạ → '') + sibling_group; TƯƠNG THÍCH NGƯỢC
     (bài model thiếu 2 trục → điền '' KHÔNG vỡ); focus_tier set → prompt DỒN tầng đó; content_matrix nạp làm nền.

Chạy:  python3 tests/test_b21_layered_matrix.py    (exit 0 = pass)
LƯU Ý: chỉ chứng minh PLUMBING (validate/degrade/toạ-độ ma trận tới tay model). Model có tổ chức ma trận
       gọn / repurpose đúng nền tảng theo ngành không → soi output thật trên staging.
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
_MODE = {"matrix": "good", "funnel": "good"}
async def _fake_call(task_type=None, system="", user="", max_tokens=0, **kw):
    CAPTURED.append({"system": system, "user": user})
    if "MA TRẬN NỘI DUNG THƯỜNG TRỰC" in system:          # ① gen_content_matrix
        if _MODE["matrix"] == "garbage":
            return {"output": json.dumps({"cells": [
                {"pillar": "Khoa học làn da", "tier": "ZZZ", "role": "tier rác", "platforms": ["FB"]},   # tier rác → bỏ
                {"pillar": "Chuyện nghề spa", "tier": "tofu", "role": "", "platforms": ["FB"]},          # thiếu role → bỏ
            ]})}
        return {"output": json.dumps({"cells": [
            {"pillar": "Khoa học làn da", "tier": "TOFU", "role": "khơi hiểu da", "platforms": ["Reels 15s"], "cadence": "1 bài/tuần"},  # tier HOA → chuẩn hoá
            {"pillar": "trụ lạ hoắc", "tier": "mofu", "role": "nuôi cân nhắc", "platforms": []},          # trụ lạ → về trụ đầu; platforms rỗng → điền
            {"pillar": "Chuyện nghề spa", "tier": "bad", "role": "bỏ", "platforms": ["X"]},               # tier rác → bỏ
        ]})}
    if "DANH SÁCH BÀI DỰ KIẾN" in system:                 # ③ gen_funnel_map_for_idea
        return {"output": json.dumps({"ratio": "", "posts": [
            {"tier": "tofu", "channel": "Reels 15s", "role": "khơi nhận biết", "pillar": "Khoa học làn da", "sibling_group": "s1"},
            {"tier": "tofu", "channel": "Bài FB", "role": "biến thể repurpose", "pillar": "khoa học", "sibling_group": "s1"},  # pillar khớp lỏng
            {"tier": "mofu", "channel": "Bài dài FB", "role": "nuôi cân nhắc"},   # THIẾU pillar+sibling_group → điền '' (tương thích ngược)
            {"tier": "bofu", "channel": "Landing", "role": "chốt", "pillar": "trụ ma", "sibling_group": ""},  # pillar lạ → ''
        ]})}
    return {"output": json.dumps({"ideas": []})}
R.call = _fake_call


async def _run():
    res = []

    # ---- ① gen_content_matrix: validate + khớp trụ + platforms fallback ----
    _MODE["matrix"] = "good"; CAPTURED.clear()
    m = await B.gen_content_matrix(user_id=1)
    cm = m.get("content_matrix", {})
    cells = cm.get("cells", [])
    tiers = {c["tier"] for c in cells}
    pills = {c["pillar"] for c in cells}
    res += [
        ("① gen ok", bool(m.get("ok"))),
        ("① lọc tier rác + ô thiếu role (còn 2/3)", len(cells) == 2),
        ("① tier chuẩn enum lowercase", tiers <= set(B._KI_TIERS) and "tofu" in tiers),
        ("① mọi ô đủ pillar+tier+role+platforms", all(c["pillar"] and c["tier"] and c["role"] and c["platforms"] for c in cells)),
        ("① trụ lạ khớp về trụ đã biết (không đẻ trụ ngoài Thông điệp)", pills <= {"Khoa học làn da", "Chuyện nghề spa"}),
        ("① platforms rỗng → điền kênh đang dùng (Facebook)", any(c["platforms"] == ["Facebook"] for c in cells)),
        ("① lưu content_matrix vào intake_extra", "content_matrix" in _DB["intake_extra"]),
    ]

    # ---- ① degrade: LLM ra rác hết → dựng tối thiểu 1 ô/trụ ở tofu (KHÔNG cụt) ----
    _MODE["matrix"] = "garbage"
    md = await B.gen_content_matrix(user_id=1)
    cd = md.get("content_matrix", {}).get("cells", [])
    res += [
        ("① degrade cells KHÔNG rỗng (từ pillars)", bool(md.get("ok")) and len(cd) >= 1),
        ("① degrade ô hợp lệ tier tofu", all(c["tier"] == "tofu" for c in cd)),
    ]

    # ---- ② save_key_idea đợt nhấn: focus_tier/focus_pillars chuẩn hoá ----
    r = await B.save_key_idea(user_id=1, title="Đợt hiểu da", goal="awareness",
                              focus_tier="MOFU", focus_pillars=["Khoa học làn da", "  "])
    ki = r.get("key_idea", {})
    kid = ki.get("id")
    r2 = await B.save_key_idea(user_id=1, title="Ý nhấn rác", focus_tier="xxx", focus_pillars="không-phải-list")
    res += [
        ("② focus_tier hợp lệ chuẩn hoá lowercase", ki.get("focus_tier") == "mofu"),
        ("② focus_pillars lọc rỗng", ki.get("focus_pillars") == ["Khoa học làn da"]),
        ("② focus_tier rác → ''", r2["key_idea"]["focus_tier"] == ""),
        ("② focus_pillars không-list → []", r2["key_idea"]["focus_pillars"] == []),
    ]

    # update meta GIỮ funnel_map cũ (không hồi quy B2)
    for it in _DB["intake_extra"]["key_ideas"]:
        if it["id"] == kid:
            it["funnel_map"] = {"ratio": "65/25/10", "posts": [{"tier": "tofu", "channel": "FB", "role": "x", "note": ""}]}
    r3 = await B.save_key_idea(user_id=1, id=kid, title="Đợt hiểu da (sửa)", focus_tier="bofu")
    res += [
        ("② update GIỮ funnel_map cũ", r3["key_idea"]["funnel_map"]["ratio"] == "65/25/10"),
        ("② update đổi được focus_tier", r3["key_idea"]["focus_tier"] == "bofu"),
    ]

    # ---- ③ gen_funnel_map_for_idea: pillar + sibling_group + tương thích ngược + focus bias ----
    _MODE["funnel"] = "good"; CAPTURED.clear()
    g = await B.gen_funnel_map_for_idea(user_id=1, id=kid)
    fm = g.get("funnel_map", {})
    posts = fm.get("posts", [])
    up = CAPTURED[-1]["user"]
    by_role = {p["role"]: p for p in posts}
    res += [
        ("③ gen ok", bool(g.get("ok"))),
        ("③ mọi post có khoá pillar+sibling_group", all("pillar" in p and "sibling_group" in p for p in posts)),
        ("③ pillar khớp chính xác giữ nguyên", by_role.get("khơi nhận biết", {}).get("pillar") == "Khoa học làn da"),
        ("③ pillar khớp LỎNG ('khoa học'→trụ đầy đủ)", by_role.get("biến thể repurpose", {}).get("pillar") == "Khoa học làn da"),
        ("③ sibling_group repurpose giữ (s1)", by_role.get("khơi nhận biết", {}).get("sibling_group") == "s1"),
        ("③ TƯƠNG THÍCH NGƯỢC: post thiếu 2 trục → pillar='' sibling=''",
         by_role.get("nuôi cân nhắc", {}).get("pillar") == "" and by_role.get("nuôi cân nhắc", {}).get("sibling_group") == ""),
        ("③ pillar lạ hẳn → '' (không đẻ trụ ngoài Thông điệp)", by_role.get("chốt", {}).get("pillar") == ""),
        ("③ khoá cũ tier/channel/role còn nguyên (B2)", all(p["tier"] and p["channel"] and p["role"] for p in posts)),
        ("③ focus_tier=bofu → prompt DỒN tầng BOFU", "DỒN tầng BOFU" in up),
        ("③ content_matrix nạp vào prompt làm nền", "Ma trận nội dung nền" in up),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("B2.1 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
