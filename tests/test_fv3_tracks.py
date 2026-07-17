"""Test FV3-6 — tracks[].alias: biệt danh lát cắt (trụ × dạng) (doc §4.2).

Stub storage, drive HÀM THẬT (save_track_alias, tracks_view, track_alias, track_default_name, biz_data.bizTracks).

Chốt đúng phạm vi brief FV3-6:
  ① track_default_name: tên máy ghép 'Trụ × Dạng-label'; dạng lạ → chỉ trụ.
  ② tracks_view: liệt kê trụ × DẠNG ĐANG BẬT (content_rhythm) — mỗi lát có default/alias/display.
  ③ save_track_alias: đặt biệt danh → display=alias; upsert theo (pillar,dang); alias rỗng → gỡ về tên máy.
  ④ dạng lạ → lỗi; trụ rỗng → lỗi. KHÔNG đụng trục (chỉ overlay tên).
  ⑤ biz_data.bizTracks phản ánh biệt danh.

Chạy:  python tests/test_fv3_tracks.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {"core": "Da khỏe từ gốc", "pillars": [
            {"icon": "🔬", "territory": "Da nhạy cảm", "angle": "cơ chế da"},
            {"icon": "🌿", "territory": "Thành phần lành", "angle": "nguồn gốc"},
        ]},
        # chỉ bật 2 dạng → lát cắt = 2 trụ × 2 dạng = 4
        "content_rhythm": {"story": {"on": True, "freq": 1.0}, "review": {"on": True, "freq": 1.0},
                           "sell": {"on": False, "freq": 1.0}},
    }}

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "intake_extra": _DB["intake_extra"]}
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
    extra = _DB["intake_extra"]

    # ---- ① track_default_name ----
    res += [
        ("① tên máy 'Trụ × Dạng-label'",
         B.track_default_name("Da nhạy cảm", "review") == "Da nhạy cảm × " + B.CONTENT_DANG["review"][1]),
        ("① dạng lạ → chỉ trụ", B.track_default_name("Da nhạy cảm", "xyz") == "Da nhạy cảm"),
    ]

    # ---- ② tracks_view: trụ × dạng ĐANG BẬT ----
    view = B.tracks_view(extra)
    keys = {(t["pillar"], t["dang"]) for t in view}
    res += [
        ("② 2 trụ × 2 dạng bật = 4 lát", len(view) == 4),
        ("② chỉ dạng BẬT (story/review), không có 'sell' (tắt)",
         all(t["dang"] in ("story", "review") for t in view) and ("Da nhạy cảm", "story") in keys),
        ("② display mặc định = tên máy khi chưa đặt alias",
         all(t["display_name"] == t["default_name"] and not t["alias"] for t in view)),
        ("② mỗi lát có icon + dang_label", all(t.get("icon") and t.get("dang_label") for t in view)),
    ]

    # ---- ③ save_track_alias: đặt biệt danh ----
    r = await B.save_track_alias(user_id=1, pillar="Da nhạy cảm", dang="review", alias="Chuyện da thật của khách")
    al = B.track_alias(_DB["intake_extra"], "Da nhạy cảm", "review")
    v2 = {(t["pillar"], t["dang"]): t for t in B.tracks_view(_DB["intake_extra"])}
    tgt = v2.get(("Da nhạy cảm", "review"), {})
    res += [
        ("③ đặt alias ok", r.get("ok") is True and r.get("alias") == "Chuyện da thật của khách"),
        ("③ track_alias đọc lại đúng", al == "Chuyện da thật của khách"),
        ("③ view display = alias sau khi đặt", tgt.get("display_name") == "Chuyện da thật của khách" and tgt.get("alias")),
        ("③ lát khác KHÔNG bị đụng (vẫn tên máy)",
         v2.get(("Thành phần lành", "story"), {}).get("display_name") == B.track_default_name("Thành phần lành", "story")),
    ]

    # ---- ③b upsert: đổi alias cùng (pillar,dang) không nhân đôi ----
    await B.save_track_alias(user_id=1, pillar="Da nhạy cảm", dang="review", alias="Da thật")
    raw = [t for t in _DB["intake_extra"].get("tracks", [])
           if t.get("pillar") == "Da nhạy cảm" and t.get("dang") == "review"]
    res += [("③b upsert: chỉ 1 bản ghi (pillar,dang)", len(raw) == 1 and raw[0]["alias"] == "Da thật")]

    # ---- ③c alias rỗng → gỡ về tên máy ----
    await B.save_track_alias(user_id=1, pillar="Da nhạy cảm", dang="review", alias="  ")
    res += [
        ("③c alias rỗng → xoá bản ghi", B.track_alias(_DB["intake_extra"], "Da nhạy cảm", "review") == ""),
        ("③c gỡ xong không còn track cho lát đó",
         not [t for t in _DB["intake_extra"].get("tracks", [])
              if t.get("pillar") == "Da nhạy cảm" and t.get("dang") == "review"]),
    ]

    # ---- ④ guard: dạng lạ / trụ rỗng → lỗi ----
    bad1 = await B.save_track_alias(user_id=1, pillar="Da nhạy cảm", dang="khùng", alias="x")
    bad2 = await B.save_track_alias(user_id=1, pillar="", dang="review", alias="x")
    res += [
        ("④ dạng lạ → lỗi", "error" in bad1),
        ("④ trụ rỗng → lỗi", "error" in bad2),
    ]

    # ---- ⑤ biz_data.bizTracks ----
    await B.save_track_alias(user_id=1, pillar="Thành phần lành", dang="story", alias="Kể chuyện nguyên liệu")
    bd = await B.biz_data(user_id=1)
    bt = bd.get("bizTracks")
    got = next((t for t in (bt or []) if t["pillar"] == "Thành phần lành" and t["dang"] == "story"), {})
    res += [
        ("⑤ bizTracks là list", isinstance(bt, list) and len(bt) == 4),
        ("⑤ bizTracks phản ánh biệt danh vừa đặt", got.get("display_name") == "Kể chuyện nguyên liệu"),
    ]
    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-6 tracks-alias:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
