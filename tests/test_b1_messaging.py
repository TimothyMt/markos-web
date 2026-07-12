"""Regression test B1 — T3 Thông điệp (back-end).

Chạy KHÔNG cần key LLM / DB: stub llm_router + storage.v2, drive HÀM THẬT
(gen_messaging, gen_calendar_post) và bắt prompt gửi model.

Chốt 2 điều dễ vỡ khi ai đó sửa messaging về sau:
  (a) prompt dựng trụ mang đủ luật (2 cửa · đào proof · 5 hạng · hygiene fact)
      VÀ context thật (synthesis/tactical/insight) chảy vào để model có đồ đào proof;
      pipeline không tự bịa proof (trụ rỗng giữ rỗng qua _norm_messaging).
  (b) máy viết ĐỌC proof để vặn giọng: trụ có proof → giọng khẳng định + lồng bằng
      chứng; trụ rỗng proof → 'CẤM claim'. (Đây là bug gốc: anchor từng bỏ proof+angle.)

Chạy:  python3 tests/test_b1_messaging.py    (exit 0 = pass)
LƯU Ý: test chỉ chứng minh PLUMBING (đồ tới tay model, không rò/không bịa trong ống).
       Việc model có TUÂN THỦ không (chọn đúng hạng proof, thật sự nhịn claim) phải
       soi bài thật trên staging — nằm ngoài phạm vi unit test này.
"""
import sys, os, types, asyncio, json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    """Thay LLM + storage bằng in-memory để chạy offline."""
    _DB = {"intake_extra": {}}

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "usp": "chuẩn y khoa, không xâm lấn",
                    "product_service": "chăm sóc da công nghệ cao",
                    "target_customer": "nữ 28-45 văn phòng",
                    "intake_extra": _DB["intake_extra"]}
        async def upsert_profile(self, uid, intake_extra=None, **kw):
            if intake_extra is not None:
                _DB["intake_extra"] = intake_extra
            return True

    class _AnyAsync:            # nuốt mọi bước lưu (skill_runs...) → async no-op
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles()
    fake_v2.skill_runs = _AnyAsync()
    sys.modules["storage.v2"] = fake_v2
    sys.modules.setdefault("storage", types.ModuleType("storage"))
    sess = types.ModuleType("storage.session"); sess._client = object()
    async def _init_pool(): return None
    sess.init_pool = _init_pool
    sys.modules["storage.session"] = sess

    # llm_router thật cần `anthropic` (không có offline) → fake cả module
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

# ---- stub các cổng I/O của business ----
B.available = lambda: True
async def _ensure(): return None
B.ensure_client = _ensure
async def _pick(req=None): return 1
B.pick_user_id = _pick
_CTX = {
    "synthesis": "Định vị: phòng khám da chuẩn y khoa. Sai lầm ngành: spa chạy theo liệu trình đắt tiền.",
    "tactical_playbook": "Bằng chứng vận hành: máy soi da 50x, lưu ảnh trước/sau 200+ khách. Bác sĩ da liễu trực tiếp.",
    "customer_insight": "Khách sợ bị vẽ liệu trình, muốn hiểu tình trạng da mình trước khi chi tiền.",
}
async def _latest(uid, name): return _CTX.get(name, "")
B._latest_content = _latest

CAPTURED = []
async def _fake_call(task_type=None, system="", user="", max_tokens=0, **kw):
    CAPTURED.append({"system": system, "user": user})
    if '"pillars"' in system:      # bước dựng trụ → 1 trụ đào được proof + 1 trụ rỗng proof
        return {"output": json.dumps({
            "pillars": [
                {"icon": "🔬", "territory": "Khoa học làn da", "angle": "giải thích cơ chế da yếu",
                 "proof": "máy soi da 50x + ảnh trước/sau 200 khách"},
                {"icon": "💬", "territory": "Chuyện nghề spa", "angle": "kể hậu trường thật", "proof": ""},
            ],
            "voice": {"do": ["ấm áp, thật"], "dont": ["vẽ liệu trình", "nói phét"]}})}
    return {"output": json.dumps({"core": "Da khỏe từ gốc, không phụ thuộc liệu trình",
                                  "taglines": ["Hiểu da trước khi chi tiền"]})}
R.call = _fake_call


async def _run():
    results = []

    # ---- (a) dựng trụ: luật + context + không bịa proof ----
    r = await B.gen_messaging(user_id=1, stage="pillars",
                              core="Da khỏe từ gốc, không phụ thuộc liệu trình")
    sysp, usrp = CAPTURED[-1]["system"], CAPTURED[-1]["user"]
    pillars = r.get("messaging", {}).get("pillars", [])
    results += [
        ("(a) system có luật 2 CỬA", "2 CỬA" in sysp),
        ("(a) system có TỰ ĐÀO PROOF", "TỰ ĐÀO PROOF" in sysp),
        ("(a) system có 5 HẠNG", "5 HẠNG" in sysp),
        ("(a) system có luật HYGIENE FACT", "HYGIENE FACT" in sysp),
        ("(a) user có nguyên liệu proof (tactical)", "máy soi da 50x" in usrp),
        ("(a) user có customer insight", "vẽ liệu trình" in usrp),
        ("(a) proof trụ 1 giữ nguyên, trụ 2 rỗng (không bịa)",
         bool(r.get("ok")) and len(pillars) == 2 and pillars[0]["proof"] and pillars[1]["proof"] == ""),
    ]

    # ---- (b) máy viết đọc proof để vặn giọng ----
    CAPTURED.clear()
    await B.gen_calendar_post(user_id=1, track="always", pillar="Chuyện nghề spa")
    wp = CAPTURED[-1]["system"] + "\n" + CAPTURED[-1]["user"]
    results += [
        ("(b) trụ CÓ proof → giọng KHẲNG ĐỊNH + lồng bằng chứng",
         "CÓ BẰNG CHỨNG: máy soi da 50x" in wp and "giọng KHẲNG ĐỊNH" in wp),
        ("(b) trụ RỖNG proof → CẤM claim",
         "CHƯA CÓ bằng chứng" in wp and "CẤM claim" in wp),
        ("(b) anchor mang cả angle (góc nói)", "giải thích cơ chế da yếu" in wp),
    ]
    return results


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("B1 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
