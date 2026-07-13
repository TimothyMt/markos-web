"""Regression test B3 — sinh bài CHANNEL-AWARE (kênh quyết định định dạng) + 1 nguồn _FORMAT_SPECS.

Chạy KHÔNG cần key LLM / DB: stub llm_router (ghi lại system+max_tokens) + storage.v2, drive HÀM THẬT
gen_calendar_post + gen_derivative + _channel_to_format.

Chốt điều dễ vỡ:
  ① _channel_to_format: TikTok/Reels/Shorts→video · Zalo→short · Bài dài/landing→longform · FB/''→post.
  ② gen_calendar_post(channel='TikTok') → system mang khối VIDEO (shot/timing/caption/hashtag) + VẪN có anchor
     (giọng cốt lõi + TẦNG PHỄU); max_tokens=1500.
  ③ gen_calendar_post(channel='') → format 'post' (có "Gợi ý ảnh", KHÔNG shot list) = TƯƠNG THÍCH NGƯỢC.
  ④ gen_derivative(video, tier) → prompt mang khối video + GIỌNG thương hiệu (hết mỏng: chỉ ngành+USP+text).

Chạy:  python3 tests/test_b3_channel_format.py   (exit 0 = pass)
"""
import sys, os, types, asyncio, json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _install_stubs():
    _EXTRA = {"messaging": {"core": "Da khỏe từ gốc, không phụ thuộc liệu trình",
                            "pillars": [{"icon": "🔬", "territory": "Khoa học làn da", "angle": "cơ chế da",
                                         "proof": "máy soi 50x"}],
                            "voice": {"do": ["ấm áp, thật"], "dont": ["vẽ liệu trình"]}}}

    class _Profiles:
        async def get_profile(self, uid):
            return {"industry": "Spa - thẩm mỹ", "usp": "chuẩn y khoa", "product_service": "chăm sóc da",
                    "target_customer": "nữ 28-45", "intake_extra": _EXTRA}
        async def upsert_profile(self, uid, **kw): return {"ok": True}

    class _AnyAsync:
        def __getattr__(self, _):
            async def _f(*a, **k): return None
            return _f

    fake_v2 = types.ModuleType("storage.v2")
    fake_v2.profiles = _Profiles(); fake_v2.skill_runs = _AnyAsync(); fake_v2.campaigns_v2 = _AnyAsync()
    sys.modules["storage.v2"] = fake_v2
    sys.modules.setdefault("storage", types.ModuleType("storage"))
    fake_R = types.ModuleType("tools.llm_router")
    class TaskType: OPS_BRIEF = "b"; OPS_CONTENT_CREATIVE = "c"; OPS_CONTENT_BULK = "k"; INTAKE_JSON = "j"; CHANNEL_ADAPT = "ch"
    fake_R.TaskType = TaskType
    sys.modules.setdefault("tools", types.ModuleType("tools"))
    sys.modules["tools.llm_router"] = fake_R
    return _EXTRA


_install_stubs()
import webapp.business as B
B.available = lambda: True
async def _e(): return None
B.ensure_client = _e
async def _p(r=None): return 1
B.pick_user_id = _p
async def _lc(uid, name): return "Định vị: phòng khám da chuẩn y khoa." if name == "synthesis" else ""
B._latest_content = _lc

CAP = []
async def _call(task_type=None, system="", user="", max_tokens=0, **kw):
    CAP.append({"system": system, "user": user, "max_tokens": max_tokens})
    return {"output": "NỘI DUNG MẪU"}
sys.modules["tools.llm_router"].call = _call


async def _run():
    res = []

    # ---- ① mapper ----
    m = {ch: B._channel_to_format(ch) for ch in
         ["TikTok", "Reels 15s", "Shorts", "Zalo OA", "Bài dài FB", "Landing page", "Bài FB", ""]}
    res += [
        ("① video: TikTok/Reels/Shorts", m["TikTok"] == "video" and m["Reels 15s"] == "video" and m["Shorts"] == "video"),
        ("① short: Zalo", m["Zalo OA"] == "short"),
        ("① longform: Bài dài / landing", m["Bài dài FB"] == "longform" and m["Landing page"] == "longform"),
        ("① post: FB / rỗng (mặc định)", m["Bài FB"] == "post" and m[""] == "post"),
    ]

    # ---- ② channel='TikTok' → khối video + anchor + max_tokens 1500 ----
    CAP.clear()
    await B.gen_calendar_post(user_id=1, track="always", pillar="Khoa học làn da",
                              angle="Soi da 50x", track_role="khơi nhận biết", tier="tofu", channel="TikTok")
    c = CAP[-1]; sysp = c["system"]
    res += [
        ("② TikTok → khối VIDEO (shot/timing)", "KỊCH BẢN" in sysp and "shot" in sysp.lower() and "TIMING" in sysp),
        ("② TikTok → caption ≤125 + hashtag", "125" in sysp and "hashtag" in sysp.lower()),
        ("② VẪN có anchor: giọng cốt lõi", "Da khỏe từ gốc" in c["user"]),
        ("② VẪN có TẦNG PHỄU + kênh đăng", "TẦNG PHỄU" in c["user"] and "Kênh đăng: TikTok" in c["user"]),
        ("② max_tokens = 1500 (video)", c["max_tokens"] == 1500),
        ("② KHÔNG có 'Gợi ý ảnh' (không phải post)", "Gợi ý ảnh" not in sysp),
    ]

    # ---- ③ channel='' → format post (tương thích ngược) ----
    CAP.clear()
    await B.gen_calendar_post(user_id=1, track="always", pillar="Khoa học làn da", angle="X", tier="mofu")
    c0 = CAP[-1]
    res += [
        ("③ channel='' → post: có 'Gợi ý ảnh'", "Gợi ý ảnh" in c0["system"]),
        ("③ channel='' → KHÔNG shot list (không video)", "shot" not in c0["system"].lower()),
        ("③ channel='' → max_tokens 900 (post)", c0["max_tokens"] == 900),
    ]

    # ---- ④ gen_derivative(video, tier) → khối video + giọng thương hiệu ----
    CAP.clear()
    await B.gen_derivative(user_id=1, kind="video", source="Bài gốc: soi da 50x giúp hiểu da.",
                           pillar="Khoa học làn da", tier="tofu")
    d = CAP[-1]
    res += [
        ("④ derive video → khối video (shot/timing)", "shot" in d["system"].lower() and "TIMING" in d["system"]),
        ("④ derive → có GIỌNG thương hiệu (anchor)", "Da khỏe từ gốc" in d["user"]),
        ("④ derive → có tầng phễu + bài gốc", "TOFU" in d["user"] and "BÀI GỐC" in d["user"]),
        ("④ derive video max_tokens 1500", d["max_tokens"] == 1500),
    ]

    return res


def main():
    results = asyncio.run(_run())
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("B3 regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
