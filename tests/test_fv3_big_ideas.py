"""Test FV3-1 — Tách Big Idea khỏi Chiến dịch (big_ideas[] + key_ideas[i].big_idea_id).

Chạy KHÔNG cần key LLM / DB: stub storage + llm_router, drive HÀM THẬT
(save_big_idea, save_key_idea(+big_idea_id), derive_big_ideas, biz_data).

Chốt đúng 4 mục brief FV3-1:
  ① save_big_idea: tạo mới (ok+id) · title trống → lỗi · update dedupe theo id (không tạo bản mới, đổi title).
     LƯU Ý: big_idea CHỈ có {id,title,angle,source_ref,season,created_at,updated_at} — KHÔNG status/window/funnel.
  ② save_key_idea(big_idea_id=<tồn tại>) → ghi FK · big_idea_id=<không tồn tại> → về "".
  ③ derive_big_ideas: 2 key_idea chưa gắn → 2 big idea + back-link · chạy lại → derived=0 (idempotent).
  ④ biz_data → bizBigIdeas phản ánh đúng số big idea.

Chạy:  python tests/test_fv3_big_ideas.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {
            "core": "Da khỏe từ gốc",
            "pillars": [
                {"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"},
                {"icon": "💬", "territory": "Chuyện nghề spa", "angle": "hậu trường"},
            ],
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
    async def _boot(**kw): return {"output": "{}"}
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

    # ---- ① save_big_idea: tạo mới, title trống lỗi ----
    r = await B.save_big_idea(user_id=1, title="Tết không cần hoàn hảo",
                              angle="bình an hơn hoàn hảo", source_ref="Chuyện nghề spa", season="Tết 2026")
    bi = r.get("big_idea", {})
    bid = bi.get("id")
    err = await B.save_big_idea(user_id=1, title="")
    res += [
        ("① tạo mới ok + có id", bool(r.get("ok")) and bool(bid)),
        ("① big_idea CHỈ field big-idea (không status/window/funnel)",
         set(bi.keys()) <= {"id", "title", "angle", "source_ref", "season", "created_at", "updated_at"}),
        ("① season giữ chữ tự do (không ép enum)", bi.get("season") == "Tết 2026"),
        ("① title trống → lỗi", "error" in err),
    ]

    # ---- ① update dedupe theo id ----
    r2 = await B.save_big_idea(user_id=1, id=bid, title="Tết không cần hoàn hảo (đã sửa)")
    bis = _DB["intake_extra"].get("big_ideas", [])
    res += [
        ("① update theo id KHÔNG tạo bản mới", len([i for i in bis if i["id"] == bid]) == 1),
        ("① update đổi được title", r2["big_idea"]["title"] == "Tết không cần hoàn hảo (đã sửa)"),
    ]

    # ---- ② save_key_idea với big_idea_id (FK) ----
    r3 = await B.save_key_idea(user_id=1, title="Chiến dịch branding Tết", big_idea_id=bid)
    r4 = await B.save_key_idea(user_id=1, title="Chiến dịch FK gãy", big_idea_id="khong-ton-tai")
    res += [
        ("② big_idea_id=<tồn tại> → ghi FK vào key_idea", r3["key_idea"].get("big_idea_id") == bid),
        ("② big_idea_id=<không tồn tại> → về rỗng", r4["key_idea"].get("big_idea_id") == ""),
    ]

    # ---- ③ derive_big_ideas: idempotent ----
    _DB["intake_extra"]["key_ideas"] = [
        {"id": "k1", "title": "Đợt hiểu da", "angle": "chống vẽ liệu trình", "source_ref": "Khoa học làn da"},
        {"id": "k2", "title": "Đợt xả kho", "angle": "ưu đãi thật", "source_ref": "Chuyện nghề spa"},
    ]
    n_before = len(_DB["intake_extra"].get("big_ideas", []))
    d1 = await B.derive_big_ideas(user_id=1)
    kis = _DB["intake_extra"].get("key_ideas", [])
    n_after = len(_DB["intake_extra"].get("big_ideas", []))
    d2 = await B.derive_big_ideas(user_id=1)   # chạy lại
    res += [
        ("③ derive 2 key_idea chưa gắn → 2 big idea mới", d1.get("derived") == 2 and n_after == n_before + 2),
        ("③ back-link cả 2 key_idea", bool(kis[0].get("big_idea_id")) and bool(kis[1].get("big_idea_id"))),
        ("③ chạy lại → derived=0 (idempotent)", d2.get("derived") == 0),
    ]

    # ---- ④ biz_data → bizBigIdeas ----
    bd = await B.biz_data(user_id=1)
    total = len(_DB["intake_extra"].get("big_ideas", []))
    res += [
        ("④ bizBigIdeas là list + đúng số", isinstance(bd.get("bizBigIdeas"), list) and len(bd["bizBigIdeas"]) == total),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("FV3-1 big-ideas:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
