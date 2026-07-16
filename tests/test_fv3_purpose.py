"""Test FV3-2 — Mục đích chiến dịch (campaigns[].purpose 7 loại + migrate 4 enum goal cũ).

Chạy KHÔNG cần key LLM / DB: stub storage + llm_router, drive HÀM THẬT
(_norm_purpose, _KI_GOAL_TO_PURPOSE, save_key_idea(+purpose), derive_purposes).

Chốt đúng phạm vi brief FV3-2 (doc §3.1):
  ① _norm_purpose: nhận 7 loại hợp lệ · lạ → "" · không phân biệt hoa/thường.
  ② _KI_GOAL_TO_PURPOSE: awareness→branding · consideration→demand · conversion→conversion · retention→retention.
     (launch/winback/advocacy là loại MỚI — không có nguồn goal cũ.)
  ③ save_key_idea: purpose truyền thẳng → dùng · không truyền nhưng có goal → suy từ goal ·
     purpose mới (launch) không có goal → vẫn giữ launch · goal GIỮ NGUYÊN (peer, không đè).
  ④ derive_purposes: key_idea có goal chưa có purpose → suy · goal rỗng → để trống ·
     chạy lại → derived=0 (idempotent) · goal KHÔNG bị xoá.

Chạy:  python tests/test_fv3_purpose.py   (exit 0 = pass)
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

    # ---- ① _norm_purpose ----
    res += [
        ("① nhận đủ 7 loại hợp lệ",
         all(B._norm_purpose(p) == p for p in
             ("branding", "launch", "demand", "conversion", "retention", "winback", "advocacy"))),
        ("① loại lạ → ''", B._norm_purpose("awareness") == "" and B._norm_purpose("linh tinh") == ""),
        ("① không phân biệt hoa/thường + trim", B._norm_purpose("  BRANDING ") == "branding"),
    ]

    # ---- ② _KI_GOAL_TO_PURPOSE (map di trú 4 enum cũ) ----
    m = B._KI_GOAL_TO_PURPOSE
    res += [
        ("② awareness→branding", m.get("awareness") == "branding"),
        ("② consideration→demand", m.get("consideration") == "demand"),
        ("② conversion→conversion", m.get("conversion") == "conversion"),
        ("② retention→retention", m.get("retention") == "retention"),
        ("② map chỉ có 4 goal cũ (launch/winback/advocacy KHÔNG có nguồn)", set(m.keys()) == set(B._KI_GOALS)),
    ]

    # ---- ③ save_key_idea: purpose thẳng / suy từ goal / peer goal ----
    r1 = await B.save_key_idea(user_id=1, title="Đợt ra mắt serum", purpose="launch")
    r2 = await B.save_key_idea(user_id=1, title="Đợt phủ nhận biết", goal="awareness")   # không truyền purpose
    r3 = await B.save_key_idea(user_id=1, title="Đợt vừa goal vừa purpose",
                               goal="awareness", purpose="conversion")                    # purpose thắng
    res += [
        ("③ purpose truyền thẳng → dùng", r1["key_idea"].get("purpose") == "launch"),
        ("③ purpose mới (launch) không có goal → goal vẫn ''", r1["key_idea"].get("goal") == ""),
        ("③ không truyền purpose, có goal → suy (awareness→branding)",
         r2["key_idea"].get("purpose") == "branding"),
        ("③ goal GIỮ NGUYÊN khi suy purpose (peer)", r2["key_idea"].get("goal") == "awareness"),
        ("③ purpose truyền thẳng THẮNG suy-từ-goal", r3["key_idea"].get("purpose") == "conversion"),
    ]

    # ---- ④ derive_purposes: idempotent, không xoá goal ----
    _DB["intake_extra"]["key_ideas"] = [
        {"id": "k1", "title": "Đợt có goal", "goal": "conversion"},        # suy được → conversion
        {"id": "k2", "title": "Đợt goal rỗng", "goal": ""},                # không suy được → trống
        {"id": "k3", "title": "Đợt đã có purpose", "goal": "awareness", "purpose": "advocacy"},  # bỏ qua
    ]
    d1 = await B.derive_purposes(user_id=1)
    kis = {it["id"]: it for it in _DB["intake_extra"]["key_ideas"]}
    d2 = await B.derive_purposes(user_id=1)   # chạy lại
    res += [
        ("④ k1 goal=conversion → purpose=conversion", kis["k1"].get("purpose") == "conversion"),
        ("④ k1 goal KHÔNG bị xoá", kis["k1"].get("goal") == "conversion"),
        ("④ k2 goal rỗng → purpose để trống (không bịa)", not kis["k2"].get("purpose")),
        ("④ k3 đã có purpose → giữ nguyên (không đè)", kis["k3"].get("purpose") == "advocacy"),
        ("④ derive lần 1 = 1 (chỉ k1)", d1.get("derived") == 1),
        ("④ chạy lại → derived=0 (idempotent)", d2.get("derived") == 0),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-2 purpose:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
