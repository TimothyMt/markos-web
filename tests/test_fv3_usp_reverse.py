"""Test FV3-8 — USP thô → truy ngược Dunford (doc §1.1) + confidence/why persist qua save_strategy_input.

Stub storage + ÉP LLM, drive HÀM THẬT (gen_positioning_from_usp, save_strategy_input, _norm_pos_confidence).

Chốt đúng phạm vi brief FV3-8:
  ① gen_positioning_from_usp: alternative/differentiator/statement + confidence + why; KHÔNG persist.
  ② alternative KHÔNG BAO GIỜ rỗng (LLM để trống → tụt status quo Dunford).
  ③ differentiator bí → RỖNG (không bịa).
  ④ research MỎNG → confidence CAP 'low' (dù LLM khai 'high') — §1.2.
  ⑤ save_strategy_input: ghi spine.positioning.{confidence,source,why,updated}; source='user' (human-override);
     confidence 'low' → usp_stance='draft' (nhãn giả thuyết); 'high' → 'clear'.

Chạy:  python tests/test_fv3_usp_reverse.py   (exit 0 = pass)
"""
import sys, os, types, asyncio, json as _json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {}, "fields": {}}
    _RESEARCH = {"competitor": "", "customer_insight": ""}   # đổi per-test

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None:
                _DB["intake_extra"] = intake_extra
            _DB["fields"].update(kw)
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
    return _DB, _RESEARCH, fake_R


_DB, _RESEARCH, _R = _install_stubs()
import webapp.business as B

B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
async def _users(limit=50): return [{"id": 1}]
B.list_users = _users
# ép _latest_content trả research theo _RESEARCH (bỏ qua tầng store thật)
async def _lc(uid, skill): return _RESEARCH.get(skill, "")
B._latest_content = _lc


def _llm_returns(payload):
    async def _call(**kw): return {"output": _json.dumps(payload)}
    _R.call = _call


async def _run():
    res = []

    # ---- helper ----
    res += [
        ("⓪ _norm_pos_confidence lạ → 'low'", B._norm_pos_confidence("xyz") == "low"),
        ("⓪ giữ 'med'", B._norm_pos_confidence("med") == "med"),
    ]

    # ---- ① gen với research ĐỦ + LLM đầy đủ ----
    _RESEARCH["competitor"] = "Đối thủ A bán serum giá rẻ, đối thủ B spa cao cấp. " * 8
    _RESEARCH["customer_insight"] = "Khách sợ kích ứng, từng mua nhầm hàng trôi nổi. " * 8
    _llm_returns({"alternative": "Tự mua serum trôi nổi trên chợ mạng",
                  "differentiator": "Phác đồ chuẩn y khoa + soi da trước",
                  "statement": "Spa y khoa cho da nhạy cảm — an toàn trước, đẹp sau",
                  "confidence": "high",
                  "why": {"alternative": "T3 nói khách tự mua trôi nổi", "differentiator": "T2 không ai soi da",
                          "statement": "ghép alt+diff"}})
    g = await B.gen_positioning_from_usp(user_id=1, usp="chất lượng tốt, tận tâm")
    pr = g.get("proposal", {})
    res += [
        ("① trả proposal đủ 3 trường", bool(pr.get("alternative") and pr.get("differentiator") and pr.get("statement"))),
        ("① confidence giữ 'high' khi research đủ", g.get("confidence") == "high"),
        ("① why là dict có why-log", isinstance(g.get("why"), dict) and g["why"].get("alternative")),
        ("① KHÔNG persist (intake_extra chưa có spine)", "spine" not in _DB["intake_extra"]),
        ("① usp rỗng → lỗi", "error" in await B.gen_positioning_from_usp(user_id=1, usp="  ")),
    ]

    # ---- ② alternative rỗng → tụt status quo (không để trống) ----
    _llm_returns({"alternative": "", "differentiator": "X", "statement": "Y", "confidence": "med", "why": {}})
    g2 = await B.gen_positioning_from_usp(user_id=1, usp="usp thô")
    res += [("② LLM để alternative rỗng → Max tụt status quo (không rỗng)",
             bool(g2.get("proposal", {}).get("alternative")))]

    # ---- ③ differentiator bí → rỗng (không bịa) + ④ research mỏng → cap 'low' ----
    _RESEARCH["competitor"] = ""; _RESEARCH["customer_insight"] = ""     # mỏng
    _llm_returns({"alternative": "Khách chịu đựng", "differentiator": "", "statement": "Z",
                  "confidence": "high",   # LLM khai cao nhưng research mỏng → phải bị cap
                  "why": {}})
    g3 = await B.gen_positioning_from_usp(user_id=1, usp="usp thô")
    res += [
        ("③ differentiator bí → rỗng", g3.get("proposal", {}).get("differentiator") == ""),
        ("④ research mỏng → confidence cap 'low'", g3.get("confidence") == "low"),
        ("④ cờ thin=True", g3.get("thin") is True),
    ]

    # ---- ⑤ save_strategy_input: persist confidence/source/why + nhãn stance ----
    # ⑤a confidence low (user bấm qua) → stance 'draft' (giả thuyết)
    await B.save_strategy_input(user_id=1, payload={
        "segment": ["Da nhạy cảm"],
        "positioning": {"statement": "Spa y khoa da nhạy cảm", "alternative": "Tự mua trôi nổi",
                        "differentiator": "", "confidence": "low",
                        "why": {"alternative": "T3"}},
    })
    sp = _DB["intake_extra"].get("spine", {}).get("positioning", {})
    res += [
        ("⑤a spine.positioning.source='user' (human-override)", sp.get("source") == "user"),
        ("⑤a confidence lưu 'low'", sp.get("confidence") == "low"),
        ("⑤a có updated timestamp", isinstance(sp.get("updated"), (int, float)) and sp.get("updated")),
        ("⑤a why-log lưu lại", (sp.get("why") or {}).get("alternative") == "T3"),
        ("⑤a confidence thấp → usp_stance='draft' (nhãn giả thuyết)",
         _DB["fields"].get("usp_confidence") == "draft" and _DB["intake_extra"].get("usp_stance") == "draft"),
    ]
    # ⑤b confidence high (đã xác nhận) → stance 'clear'
    await B.save_strategy_input(user_id=1, payload={
        "segment": ["Da nhạy cảm"],
        "positioning": {"statement": "Spa y khoa da nhạy cảm", "alternative": "Tự mua", "confidence": "high"},
    })
    res += [
        ("⑤b confidence high → usp_stance='clear'",
         _DB["fields"].get("usp_confidence") == "clear" and _DB["intake_extra"].get("usp_stance") == "clear"),
        ("⑤b không kèm confidence → mặc định 'high' (user tự gõ)",
         (await _save_no_conf()) == "clear"),
    ]
    return res


async def _save_no_conf():
    await B.save_strategy_input(user_id=1, payload={
        "segment": ["X"], "positioning": {"statement": "Câu định vị tự gõ"}})
    return _DB["fields"].get("usp_confidence")


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-8 usp-reverse:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
