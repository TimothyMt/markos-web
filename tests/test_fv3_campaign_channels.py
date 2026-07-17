"""Test FV3-4c — campaigns[].channels[] + validate ⊆ trần + gán kênh lạ về kênh chính đợt.

Stub storage + ÉP LLM (override tools.llm_router.call), drive HÀM THẬT.

Chốt đúng phạm vi brief FV3-4c (doc §3.3 Bước 3-4-6):
  ① _norm_channels: text/slug lỏng → slug chuẩn, dedupe, bỏ lạ.
  ② _ceiling_channel_slugs: bet_choices.channel → (rỗng) current_channels → (rỗng) top_channels[ngành].
  ③ save_key_idea(channels=...): lưu slug; partial-safe (channels=None → GIỮ kênh cũ).
  ④ save_campaign_channels: cập nhật kênh; kênh ngoài trần VẪN NHẬN + trả off=[kênh ngoài trần].
  ⑤ gen_funnel_map_for_idea: post kênh lạ → GÁN kênh chính đợt (channels[0]) + channel_guessed=True.
  ⑥ biz_data.bizChannelCeiling phản ánh trần.

Chạy:  python tests/test_fv3_campaign_channels.py   (exit 0 = pass)
"""
import sys, os, types, asyncio, json as _json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

# Nạp trước (khi `storage` còn là package THẬT) để degrade top_channels[ngành] chạy được sau khi stub storage.
# (Trong app thật storage là package nên nhánh này luôn chạy; chỉ stub rỗng của test mới chặn.)
import agents.campaign_scope_library  # noqa: E402,F401


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {"core": "Da khỏe từ gốc",
                      "pillars": [{"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"}]},
        "bet_choices": {"channel": ["đánh mạnh TikTok cho mẹ bỉm", "Zalo OA"]},   # trần ①
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
    fake_R.call = None
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return _DB, _PROF, fake_R


_DB, _PROF, _R = _install_stubs()
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

    # ---- ① _norm_channels ----
    res += [
        ("① text/slug lỏng → slug, dedupe, bỏ lạ",
         B._norm_channels(["TikTok", "tik tok", "Zalo OA", "bồ câu"]) == ["tiktok", "zalo_oa"]),
        ("① không phải list → []", B._norm_channels("tiktok") == []),
    ]

    # ---- ② _ceiling_channel_slugs ----
    ceil = B._ceiling_channel_slugs(_DB["intake_extra"], {**_PROF, "intake_extra": _DB["intake_extra"]})
    ceil_cur = B._ceiling_channel_slugs({}, {"current_channels": "Facebook, TikTok"})   # bet trống → current
    ceil_ind = B._ceiling_channel_slugs({}, {"industry": "Spa - thẩm mỹ"})              # trống hết → top_channels
    res += [
        ("② bet_choices.channel → trần [tiktok, zalo_oa]", ceil == ["tiktok", "zalo_oa"]),
        ("② bet trống → current_channels", ceil_cur == ["facebook", "tiktok"]),
        ("② trống hết → top_channels[ngành] (không rỗng)", isinstance(ceil_ind, list) and len(ceil_ind) > 0),
    ]

    # ---- ③ save_key_idea(channels) + partial-safe ----
    r1 = await B.save_key_idea(user_id=1, title="Đợt kênh", channels=["TikTok", "xxx", "Zalo OA"])
    kid = r1["key_idea"]["id"]
    await B.save_key_idea(user_id=1, id=kid, title="Đợt kênh (sửa tên)")   # KHÔNG gửi channels
    ki = next(i for i in _DB["intake_extra"]["key_ideas"] if i["id"] == kid)
    res += [
        ("③ lưu slug chuẩn, bỏ lạ", r1["key_idea"].get("channels") == ["tiktok", "zalo_oa"]),
        ("③ save lại không gửi channels → GIỮ kênh cũ (partial-safe)", ki.get("channels") == ["tiktok", "zalo_oa"]),
    ]

    # ---- ④ save_campaign_channels: ngoài trần vẫn nhận + off ----
    r4 = await B.save_campaign_channels(user_id=1, id=kid, channels=["Zalo OA", "Shopee"])
    res += [
        ("④ nhận cả kênh ngoài trần (shopee)", r4.get("channels") == ["zalo_oa", "shopee"]),
        ("④ trả off = kênh ngoài trần", r4.get("off") == ["shopee"]),
    ]

    # ---- ⑤ gen: post kênh lạ → gán kênh chính đợt + guessed ----
    _llm_returns({"ratio": "20/30/50", "offers": {}, "risks": [], "posts": [
        {"tier": "mofu", "channel": "Zalo OA", "format": "", "role": "nuôi"},
        {"tier": "bofu", "channel": "bồ câu đưa thư", "format": "", "role": "chốt"},
    ]})
    _DB["intake_extra"]["key_ideas"] = [{"id": "kg", "title": "Đợt gen", "purpose": "conversion",
                                         "channels": ["zalo_oa", "shopee"],
                                         "funnel_map": {"ratio": "", "posts": []}}]
    g = await B.gen_funnel_map_for_idea(user_id=1, id="kg")
    byrole = {p["role"]: p for p in g.get("funnel_map", {}).get("posts", [])}
    p_ok, p_guess = byrole.get("nuôi", {}), byrole.get("chốt", {})
    res += [
        ("⑤ kênh hợp lệ → slug đúng, không đoán", p_ok.get("channel") == "zalo_oa" and p_ok.get("channel_guessed") is False),
        ("⑤ kênh lạ → GÁN kênh chính đợt (channels[0]=zalo_oa)", p_guess.get("channel") == "zalo_oa"),
        ("⑤ kênh lạ → channel_guessed=True (giữ raw)",
         p_guess.get("channel_guessed") is True and p_guess.get("channel_raw") == "bồ câu đưa thư"),
    ]

    # ---- ⑥ biz_data.bizChannelCeiling ----
    _DB["intake_extra"]["bet_choices"] = {"channel": ["đánh mạnh TikTok cho mẹ bỉm", "Zalo OA"]}
    bd = await B.biz_data(user_id=1)
    res += [
        ("⑥ bizChannelCeiling = trần", bd.get("bizChannelCeiling") == ["tiktok", "zalo_oa"]),
    ]
    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-4c campaign-channels:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
