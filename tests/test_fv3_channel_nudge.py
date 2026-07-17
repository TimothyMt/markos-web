"""Test FV3-4d — nudge kênh lệch chiến lược + bơm ngược lên trần (doc §3.3 Bước 5).

Stub storage, drive HÀM THẬT (detect_channel_drift, promote_channel_to_strategy, biz_data.bizChannelDrift).

Chốt đúng phạm vi brief FV3-4d:
  ① detect_channel_drift: kênh ngoài trần ở ≥2 đợt → lệch · ở 1 đợt → bỏ qua (không nhắc phép thử) ·
     ranked theo số đợt · trần rỗng → [].
  ② promote_channel_to_strategy: thêm kênh vào trần (bet_choices.channel) → hết lệch · idempotent (added=False).
  ③ biz_data.bizChannelDrift phản ánh kênh lệch.

Chạy:  python tests/test_fv3_channel_nudge.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
import agents.campaign_scope_library  # noqa: E402,F401  (nạp trước khi stub storage — xem test 4c)


def _install_stubs():
    _DB = {"intake_extra": {
        "bet_choices": {"channel": ["đánh mạnh TikTok", "Zalo OA"]},   # trần ① = tiktok, zalo_oa
        "key_ideas": [
            {"id": "k1", "title": "Đợt A", "channels": ["tiktok", "instagram"]},   # instagram off (1)
            {"id": "k2", "title": "Đợt B", "channels": ["zalo_oa", "instagram"]},  # instagram off (2) → lệch
            {"id": "k3", "title": "Đợt C", "channels": ["shopee"]},                # shopee off (1) → chưa đủ
            {"id": "k4", "title": "Đợt D", "channels": ["tiktok"]},                # trong trần
        ],
    }}
    _PROF = {"industry": "Spa - thẩm mỹ", "current_channels": "Facebook, TikTok"}

    class _Profiles:
        async def get_profile(self, uid):
            return {**_PROF, "intake_extra": _DB["intake_extra"]}
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
    return _DB, _PROF


_DB, _PROF = _install_stubs()
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
    prof = {**_PROF, "intake_extra": _DB["intake_extra"]}

    # ---- ① detect_channel_drift ----
    drift = B.detect_channel_drift(_DB["intake_extra"], prof)
    slugs = [d["slug"] for d in drift]
    inst = next((d for d in drift if d["slug"] == "instagram"), {})
    res += [
        ("① instagram (2 đợt ngoài trần) → lệch", "instagram" in slugs),
        ("① shopee (1 đợt) → KHÔNG nhắc (dưới ngưỡng)", "shopee" not in slugs),
        ("① đếm đúng số đợt + label", inst.get("count") == 2 and inst.get("label") == "Instagram"),
        ("① tiktok/zalo (trong trần) → không lệch", "tiktok" not in slugs and "zalo_oa" not in slugs),
    ]
    # trần rỗng → [] (guard)
    _orig = B._ceiling_channel_slugs
    B._ceiling_channel_slugs = lambda e, p: []
    empty = B.detect_channel_drift(_DB["intake_extra"], prof)
    B._ceiling_channel_slugs = _orig
    res += [("① trần rỗng → [] (không nhắc khi chưa có chiến lược)", empty == [])]

    # ---- ② promote_channel_to_strategy ----
    r = await B.promote_channel_to_strategy(user_id=1, slug="instagram")
    ceil2 = set(B._ceiling_channel_slugs(_DB["intake_extra"], {**_PROF, "intake_extra": _DB["intake_extra"]}))
    drift2 = [d["slug"] for d in B.detect_channel_drift(_DB["intake_extra"], {**_PROF, "intake_extra": _DB["intake_extra"]})]
    r_again = await B.promote_channel_to_strategy(user_id=1, slug="instagram")
    r_bad = await B.promote_channel_to_strategy(user_id=1, slug="bồ câu")
    res += [
        ("② bơm ngược → instagram vào trần", r.get("added") is True and "instagram" in ceil2),
        ("② sau bơm → instagram hết lệch", "instagram" not in drift2),
        ("② idempotent: bơm lại → added=False", r_again.get("added") is False),
        ("② slug lạ → lỗi", "error" in r_bad),
    ]

    # ---- ③ biz_data.bizChannelDrift ----
    # reset lại đợt để instagram lệch trở lại (đã promote ở trên) — dùng bet_choices gốc
    _DB["intake_extra"]["bet_choices"] = {"channel": ["đánh mạnh TikTok", "Zalo OA"]}
    bd = await B.biz_data(user_id=1)
    res += [
        ("③ bizChannelDrift là list", isinstance(bd.get("bizChannelDrift"), list)),
        ("③ bizChannelDrift bắt instagram lệch lại", "instagram" in [d["slug"] for d in bd.get("bizChannelDrift", [])]),
    ]
    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-4d channel-nudge:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
