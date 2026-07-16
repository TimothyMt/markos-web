"""Test FV3-4b — Tách posts[].channel (slug) khỏi posts[].format trong gen_funnel_map_for_idea.

Stub storage + ÉP LLM trả posts cụ thể (override tools.llm_router.call), drive HÀM THẬT.

Chốt đúng phạm vi brief FV3-4b (doc §3.3 Bước 2):
  ① channel LLM → slug chuẩn ('Reels 15s' → instagram); giữ channel_raw; format tách riêng.
  ② format LLM để trống + kênh có slug → gợi ý format đầu của kênh (không khoá cứng).
  ③ kênh LẠ (channel_slug='') → channel='', channel_guessed=True, giữ channel_raw (để #4c gán).
  ④ biz_data.bizChannels: 12 kênh, mỗi kênh slug/label/tiers/formats.

Chạy:  python tests/test_fv3_post_channel.py   (exit 0 = pass)
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

    # LLM trả 3 bài: kênh chuẩn-lỏng · format trống · kênh lạ
    _llm_returns({"ratio": "20/30/50", "offers": {}, "risks": [], "posts": [
        {"tier": "tofu", "channel": "Reels 15s", "format": "video 15s", "role": "khơi tò mò", "pillar": ""},
        {"tier": "mofu", "channel": "Zalo OA", "format": "", "role": "nuôi", "pillar": ""},
        {"tier": "bofu", "channel": "bồ câu đưa thư", "format": "thư tay", "role": "chốt", "pillar": ""},
    ]})
    _DB["intake_extra"]["key_ideas"] = [{"id": "kb", "title": "Đợt tách kênh", "purpose": "conversion",
                                         "funnel_map": {"ratio": "", "posts": []}}]
    g = await B.gen_funnel_map_for_idea(user_id=1, id="kb")
    posts = {p["role"]: p for p in g.get("funnel_map", {}).get("posts", [])}
    p_reel, p_zalo, p_bird = posts.get("khơi tò mò", {}), posts.get("nuôi", {}), posts.get("chốt", {})

    res += [
        ("① 'Reels 15s' → channel slug=instagram", p_reel.get("channel") == "instagram"),
        ("① giữ channel_raw gốc", p_reel.get("channel_raw") == "Reels 15s"),
        ("① format tách riêng giữ nguyên", p_reel.get("format") == "video 15s"),
        ("① không đoán (channel_guessed False)", p_reel.get("channel_guessed") is False),
        ("② 'Zalo OA' → slug=zalo_oa", p_zalo.get("channel") == "zalo_oa"),
        ("② format trống + có slug → gợi ý format đầu của kênh",
         bool(p_zalo.get("format")) and p_zalo.get("format") in B.CHANNELS["zalo_oa"]["formats"]),
        ("③ kênh lạ → channel='' ", p_bird.get("channel") == ""),
        ("③ kênh lạ → channel_guessed=True", p_bird.get("channel_guessed") is True),
        ("③ kênh lạ vẫn giữ channel_raw (để #4c gán)", p_bird.get("channel_raw") == "bồ câu đưa thư"),
    ]

    # ---- ④ biz_data.bizChannels ----
    bd = await B.biz_data(user_id=1)
    bc = bd.get("bizChannels")
    res += [
        ("④ bizChannels 12 kênh", isinstance(bc, list) and len(bc) == 12),
        ("④ mỗi kênh có slug/label/tiers/formats",
         all(isinstance(x, dict) and {"slug", "label", "tiers", "formats"} <= set(x.keys()) for x in (bc or []))),
    ]
    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-4b post-channel:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
