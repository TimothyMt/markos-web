"""Test FV3-7 — Lịch = brief NỘI DUNG + CỔNG CỨNG status (doc §5).

Stub storage + ÉP LLM, drive HÀM THẬT (save_calendar_post, gen_calendar_post, calendar_briefs_view,
_norm_post_status, _effective_post_status). Chốt đúng phạm vi brief FV3-7:
  ① save lưu 6 field brief + status; LƯU ĐƯỢC brief nháp KHI CHƯA có content.
  ② status lạ → 'draft'; 'approved' giữ nguyên.
  ③ merge mềm: lưu brief-only KHÔNG xoá content; lưu content-only KHÔNG xoá brief.
  ④ CỔNG CỨNG: gen bị CHẶN khi ô status='draft' hoặc không có brief / thiếu slot_key.
  ⑤ gen CHẠY khi status='approved' + brief 'nói gì' được bơm vào bài.
  ⑥ back-compat: entry CŨ có content, không status → coi như approved (Tạo lại không bị chặn oan).
  ⑦ calendar_briefs_view: map key→brief (+ has_content) cho FE.

Chạy:  python tests/test_fv3_calendar_brief.py   (exit 0 = pass)
"""
import sys, os, types, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _DB = {"intake_extra": {
        "messaging": {"core": "Da khỏe từ gốc",
                      "pillars": [{"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da"}],
                      "voice": {"do": ["chuyên gia", "đồng cảm"]}},
        "key_ideas": [{
            "id": "ki1", "title": "Đợt hành trình", "goal": "awareness",
            "funnel_map": {"offers": {"tofu": "Ebook miễn phí", "mofu": "Tư vấn 15p", "bofu": "Giảm 20%"}},
        }],
        "calendar_posts": {},
    }}

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "usp": "phác đồ chuẩn y khoa",
                    "target_customer": "nữ da nhạy cảm", "product_service": "dịch vụ chăm da",
                    "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None:
                _DB["intake_extra"] = intake_extra
            return True

    class _Campaigns:
        async def list_campaigns_v2(self, uid, limit=20): return []
        async def get_campaign(self, cid): return {}

    class _SkillRuns:
        async def insert_skill_run(self, uid, kind, content, model_used="test"):
            return {"id": 1, "content": content}
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
    return _DB, fake_R


_DB, _R = _install_stubs()
import webapp.business as B

B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
# ép _latest_content rỗng (bỏ tầng store thật — degrade path của gen)
async def _lc(uid, skill): return ""
B._latest_content = _lc

async def _call(**kw): return {"output": "Bài do LLM sinh (test)"}
_R.call = _call


async def _save(**kw):
    return await B.save_calendar_post(user_id=1, **kw)


def _posts():
    return _DB["intake_extra"].get("calendar_posts", {})


async def _run():
    res = []

    # ⓪ helper thuần
    res += [
        ("⓪ _norm_post_status lạ → 'draft'", B._norm_post_status("xyz") == "draft"),
        ("⓪ _norm_post_status 'approved' giữ", B._norm_post_status("Approved") == "approved"),
        ("⓪ _effective_post_status content-no-status → approved (back-compat)",
         B._effective_post_status({"content": "bài cũ"}) == "approved"),
        ("⓪ _effective_post_status rỗng → draft", B._effective_post_status({}) == "draft"),
    ]

    # ① LƯU brief NHÁP khi CHƯA có content (always track)
    k_aw = B._post_key("always", "rhy|educate|Khoa học làn da", "", "", 1, 2)
    r1 = await _save(track="always", pillar_id="rhy|educate|Khoa học làn da", week=1, day=2,
                     content="", journey_stage="cân nhắc", barrier_ref="sợ kích ứng",
                     content_brief="kể ca khách kích ứng 3 lần → soi da trước là bắt buộc",
                     material="ca khách thật — founder xác nhận", offer_ref="mofu", status="draft")
    e1 = _posts().get(k_aw, {})
    res += [
        ("① lưu được brief nháp (không content)", "error" not in r1 and bool(e1)),
        ("① content rỗng", e1.get("content") == ""),
        ("① journey_stage chuẩn hoá 'cân nhắc'", e1.get("journey_stage") == "cân nhắc"),
        ("① barrier_ref lưu", e1.get("barrier_ref") == "sợ kích ứng"),
        ("① content_brief lưu", "soi da trước" in (e1.get("content_brief") or "")),
        ("① material lưu", "founder xác nhận" in (e1.get("material") or "")),
        ("① offer_ref lưu", e1.get("offer_ref") == "mofu"),
        ("① status='draft'", e1.get("status") == "draft"),
    ]

    # ② status lạ → draft
    await _save(track="always", pillar_id="p2", week=1, day=3, content_brief="x", status="weird")
    res.append(("② status lạ → 'draft'",
                _posts().get(B._post_key("always", "p2", "", "", 1, 3), {}).get("status") == "draft"))

    # ③ merge mềm: DUYỆT brief (chỉ đổi status) KHÔNG xoá brief; rồi lưu CONTENT không xoá brief
    await _save(track="always", pillar_id="rhy|educate|Khoa học làn da", week=1, day=2, status="approved")
    e3a = _posts().get(k_aw, {})
    res += [
        ("③ duyệt → status approved", e3a.get("status") == "approved"),
        ("③ duyệt KHÔNG xoá content_brief", "soi da trước" in (e3a.get("content_brief") or "")),
        ("③ duyệt KHÔNG xoá barrier_ref", e3a.get("barrier_ref") == "sợ kích ứng"),
    ]
    await _save(track="always", pillar_id="rhy|educate|Khoa học làn da", week=1, day=2,
                content="Bài đã viết xong")
    e3b = _posts().get(k_aw, {})
    res += [
        ("③ lưu content giữ brief", "soi da trước" in (e3b.get("content_brief") or "")),
        ("③ lưu content giữ status approved", e3b.get("status") == "approved"),
        ("③ content set + approved(bool)=True",
         e3b.get("content") == "Bài đã viết xong" and e3b.get("approved") is True),
    ]

    # ④ CỔNG CỨNG — draft & không-brief bị chặn
    k_draft = B._post_key("always", "p2", "", "", 1, 3)   # status draft ở ②
    g_draft = await B.gen_calendar_post(user_id=1, track="always", pillar="Trụ", week=1, day=3, slot_key=k_draft)
    g_none = await B.gen_calendar_post(user_id=1, track="always", pillar="Trụ", week=9, day=9, slot_key="")
    _blocked = lambda g: "error" in g and any(w in g["error"].lower() for w in ["duyệt", "🔒", "brief"])
    res += [
        ("④ gen ô DRAFT bị chặn", _blocked(g_draft)),
        ("④ gen KHÔNG slot_key bị chặn", _blocked(g_none)),
    ]

    # ⑤ gen ô APPROVED chạy + bài bám brief 'nói gì'
    _seen = {}
    async def _capture(**kw):
        _seen.update(kw); return {"output": "BÀI OK"}
    _R.call = _capture
    g_ok = await B.gen_calendar_post(user_id=1, track="always", pillar="Khoa học làn da", week=1, day=2, slot_key=k_aw)
    _R.call = _call
    res += [
        ("⑤ gen ô APPROVED chạy (ok + content)", g_ok.get("ok") is True and bool(g_ok.get("content"))),
        ("⑤ brief 'nói gì' được bơm vào prompt", "soi da trước" in (_seen.get("user") or "")),
        ("⑤ có material → KHÔNG bật chốt chặn bịa", "TUYỆT ĐỐI không bịa" not in (_seen.get("user") or "")),
    ]

    # ⑥ back-compat: entry CŨ có content, KHÔNG status → approved → gen chạy
    _DB["intake_extra"]["calendar_posts"]["oc|ki1|BOFU #1"] = {
        "content": "bài cũ đã duyệt", "approved": True, "track": "camp",
        "ref": {"campaignId": "ki1", "phase": "BOFU #1"}, "place": {"phase": "BOFU #1"}}
    g_legacy = await B.gen_calendar_post(user_id=1, track="camp", campaign_id="ki1", phase="BOFU #1",
                                         tier="bofu", slot_key="oc|ki1|BOFU #1")
    res.append(("⑥ entry cũ (content, no status) → gen chạy", g_legacy.get("ok") is True))

    # ⑦ calendar_briefs_view
    view = B.calendar_briefs_view(_DB["intake_extra"])
    res += [
        ("⑦ view có key brief", k_aw in view),
        ("⑦ view.status hiệu lực = approved", view.get(k_aw, {}).get("status") == "approved"),
        ("⑦ view.has_content phản ánh content", view.get(k_aw, {}).get("has_content") is True),
        ("⑦ view chỉ chứa entry có nội dung/brief", all(v for v in view.values())),
    ]

    return res


def main():
    ok = True
    for name, passed in asyncio.run(_run()):
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-7 calendar-brief:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
