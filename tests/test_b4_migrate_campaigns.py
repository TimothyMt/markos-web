"""Regression test B4 — migrate campaigns_v2 CŨ → key_ideas (chiến dịch Layered).

Chạy KHÔNG cần key/DB: stub storage.v2, drive HÀM THẬT migrate_campaigns_to_key_ideas.

Chốt điều dễ vỡ:
  ① map field: name→title · offer_lever/summary→angle · start/end→window · primary_goal→goal enum ·
     có window → status active, thiếu → draft · source='migrated' + migrated_from=cid.
  ② IDEMPOTENT: chạy lần 2 KHÔNG nhân đôi (dedupe theo migrated_from).
  ③ ADDITIVE: giữ nguyên key_ideas có sẵn + KHÔNG xoá campaigns_v2 (list vẫn nguyên).
  ④ bỏ campaign thiếu tên (skipped), goal lạ → ''.

Chạy:  python3 tests/test_b4_migrate_campaigns.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_DB = {"intake_extra": {"key_ideas": [
    {"id": "kept1", "title": "Ý có sẵn", "source": "user", "funnel_map": {"ratio": "", "posts": []}}]}}
_CAMPS = [
    {"id": "c1", "name": "Sale hè", "primary_goal": "conversion", "offer_lever": "giảm 30%",
     "start_date": "2026-07-01", "end_date": "2026-07-15"},
    {"id": "c2", "name": "Phủ nhận biết Q3", "primary_goal": "brand", "summary": "phủ tệp mới",
     "start_date": "", "end_date": ""},
    {"id": "c3", "name": "", "primary_goal": "x"},                       # thiếu tên → skip
    {"id": "c4", "name": "Đợt lạ", "primary_goal": "khong-biet"},        # goal lạ → ''
]


def _install():
    class _Profiles:
        async def get_profile(self, uid): return {"industry": "Spa", "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None: _DB["intake_extra"] = intake_extra
            return True
    class _Camps:
        async def list_campaigns_v2(self, uid, limit=50): return list(_CAMPS)   # KHÔNG xoá
    class _AnyAsync:
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f
    fake = types.ModuleType("storage.v2")
    fake.profiles = _Profiles(); fake.campaigns_v2 = _Camps(); fake.skill_runs = _AnyAsync()
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
    r1 = await B.migrate_campaigns_to_key_ideas(user_id=1)
    ideas = _DB["intake_extra"]["key_ideas"]
    mig = [k for k in ideas if k.get("source") == "migrated"]
    by_from = {k["migrated_from"]: k for k in mig}
    res += [
        ("① nhập 3/4 (bỏ campaign thiếu tên)", r1.get("migrated") == 3 and r1.get("skipped") == 1),
        ("① giữ ý có sẵn (additive)", any(k["id"] == "kept1" for k in ideas)),
        ("① c1: name→title, offer→angle, goal conversion, window→active",
         by_from["c1"]["title"] == "Sale hè" and by_from["c1"]["angle"] == "giảm 30%"
         and by_from["c1"]["goal"] == "conversion" and by_from["c1"]["status"] == "active"),
        ("① c2: brand→awareness, thiếu window → draft, summary→angle",
         by_from["c2"]["goal"] == "awareness" and by_from["c2"]["status"] == "draft"
         and by_from["c2"]["angle"] == "phủ tệp mới"),
        ("① c4: goal lạ → ''", by_from["c4"]["goal"] == ""),
        ("① mọi bản nhập có funnel_map rỗng + source=migrated", all(k["funnel_map"] == {"ratio": "", "posts": []} for k in mig)),
    ]
    # ② idempotent — chạy lại KHÔNG nhân đôi
    r2 = await B.migrate_campaigns_to_key_ideas(user_id=1)
    ideas2 = _DB["intake_extra"]["key_ideas"]
    res += [
        ("② lần 2: migrated=0 (idempotent)", r2.get("migrated") == 0 and r2.get("skipped") == 4),
        ("② KHÔNG nhân đôi (vẫn 3 bản migrated)", len([k for k in ideas2 if k.get("source") == "migrated"]) == 3),
    ]
    # ③ campaigns_v2 KHÔNG bị xoá
    from storage.v2 import campaigns_v2
    still = await campaigns_v2.list_campaigns_v2(1)
    res.append(("③ campaigns_v2 cũ còn nguyên (không xoá)", len(still) == 4))
    return res


def main():
    r = asyncio.run(_run()); ok = True
    for n, p in r:
        print(f"  {'✅' if p else '❌'} {n}"); ok = ok and p
    print("B4 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
