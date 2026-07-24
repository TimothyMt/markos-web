"""Test S2 — Nước đi (gen_moves 2-call + commit_move).

Chạy KHÔNG cần key LLM / DB: stub storage.v2.profiles + tools.llm_router, drive HÀM THẬT
(gen_moves, commit_move). Router bị stub 2 nhánh (DRAFT / OPTIMIZE) để soi luồng 2-call thật.

⚠️ Vì sao có file này (giống S1): pass `import webapp.business` KHÔNG chứng minh hàm CHẠY —
tên chưa định nghĩa trong thân hàm / lệch seam chỉ nổ lúc gọi. Test này gọi hàm thật.

Chốt bất biến SPEC-chien-dich-4-tang §2/§8/§9 + design Gate 1:
  ① gen_moves chạy: seam bind vào audience_id + problem_id (id ổn định S1), trả nước đi có
     bậc (KHOÁ CỨNG) + thẻ + Xem-kỹ.
  ② Seam đứt phải NỔ: audience_id sai → error; problem_id sai → error (không im).
  ③ 2-call: OPTIMIZE hợp lệ → dùng bản Opus (optimized=True); OPTIMIZE hỏng → degrade về
     NHÁP Sonnet (optimized=False), KHÔNG crash; DRAFT hỏng hẳn → error.
  ④ Bản nháp được TRUYỀN vào call tối-ưu (không phải gen lại từ đầu).
  ⑤ Sanitize: nước đi thiếu tên / bậc-không-suy-được → BỊ VỨT (bậc là khoá cứng).
  ⑤b bac_spread<2 → note cảnh báo dồn 1 bậc.
  ⑥ "Nghĩ thêm": rethink ≠ rỗng → chèn hướng mới vào payload NHÁP.
  ⑦ commit_move: nước đi → big_idea(is_campaign) + mechanic + snapshot (chụp id+text+loại+giai đoạn).

Chạy:  python tests/test_s2_moves.py   (exit 0 = pass)
"""
import sys, os, json, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import webapp.business as biz
import storage.v2.profiles as profiles
import tools.llm_router as router

# battle_map giả (cấu trúc bám S1): 1 tệp core, 1 vấn đề có id ổn định
_DB = {"industry": "F&B", "intake_extra": {
    "wedge": "chủ quán ăn nhỏ tự đứng bếp",
    "messaging": {"core": "Bữa trưa nóng, nhanh, đúng giờ cho dân văn phòng", "pillars": [], "voice": {"do": [], "dont": []}},
    "resources": {"can_owner_on_camera": True, "can_shoot_video": True, "can_render_3d": False},
    "principles": [{"id": "prin_1", "text": "Không giảm giá sốc đại trà", "expires": None, "created": "2026-01-01T00:00:00+00:00"}],
    "battle_map": {"version": 1, "audiences": [
        {"id": "aud_core", "role": "core", "label": "dân văn phòng ăn trưa vội", "stages": {
            "awareness": {"applicable": True, "problems": [
                {"id": "prob_x", "text": "sợ tới nơi hết món, mất công đi", "type": "risk"}]},
            "consideration": {"applicable": True, "problems": []},
            "conversion": {"applicable": True, "problems": []},
            "retention": {"applicable": True, "problems": []}}}]},
}}

# NHÁP (Sonnet): 2 nước đi hợp lệ (2 bậc khác nhau) + 2 RÁC (thiếu tên / bậc bậy)
_DRAFT = {"luc_chan": "LO (sợ mất công) đang chặn hành động", "nuoc_di": [
    {"ten": "Mở nhận giữ món qua Zalo trước 11h", "bac": "1", "co_che": "khách nhắn món, quán giữ tới 12h30",
     "vi_du_mau": "'Nhắn 'Giữ cơm gà' — quán để phần, 12h30 tới lấy'", "dich_luc": "gỡ LO sợ hết món",
     "ai_nhung_tay": "chủ", "bao_lau": "một buổi", "doi_van_hanh": True, "gia_co": "gần như 0đ",
     "do_bang": "số tin giữ chỗ/ngày", "bang_chung": "med", "phanh": "", "phanh_loai": "", "nan_tu": "",
     "xem_ky": {"cac_buoc": ["Dán số Zalo tại quầy", "Ghi sổ giữ món"], "vi_sao_chon": "đánh thẳng lực LO",
                "da_nghi_roi_bo": "đã nghĩ tới ship nhưng vượt sức", "bang_chung_chi_tiet": "T3: khách sợ hết món",
                "chot_se_co": "1 việc dán số + 1 mẫu tin", "do_va_nguong_dung": "2 tuần <5 tin/ngày thì đổi"}},
    {"ten": "Bảng 'còn X suất' trước cửa", "bac": "phan_phoi", "co_che": "bảng cập nhật suất còn lại",
     "vi_du_mau": "'Còn 8 suất cơm sườn'", "dich_luc": "gỡ LO bằng tín hiệu còn hàng",
     "ai_nhung_tay": "nhân viên", "bao_lau": "vài ngày", "doi_van_hanh": False, "gia_co": "rẻ",
     "do_bang": "khách dừng lại đọc", "bang_chung": "low", "phanh": "", "phanh_loai": "", "nan_tu": "",
     "xem_ky": {"cac_buoc": ["Kẻ bảng"], "vi_sao_chon": "tín hiệu tại điểm bán", "da_nghi_roi_bo": "",
                "bang_chung_chi_tiet": "", "chot_se_co": "1 bảng", "do_va_nguong_dung": "1 tuần"}},
    {"ten": "", "bac": "1"},                    # RÁC: thiếu tên → vứt
    {"ten": "Ý mơ hồ", "bac": "zzz"},           # RÁC: bậc không suy được → vứt
]}

# TỐI-ƯU (Opus): 2 nước đi sâu hơn (đánh dấu để test optimized=True)
_OPT = {"luc_chan": "LO (sợ mất công đi mà hết món) — không phải giá", "nuoc_di": [
    {"ten": "Giữ món Zalo + nhắn 'đã để phần'", "bac": "1", "co_che": "xác nhận 2 chiều tạo cam kết",
     "vi_du_mau": "'Đã để phần cơm gà cho anh, hẹn 12h30 nhé'", "dich_luc": "gỡ LO + tạo nếp quay lại",
     "ai_nhung_tay": "chủ", "bao_lau": "một buổi", "doi_van_hanh": True, "gia_co": "gần như 0đ",
     "do_bang": "tỉ lệ giữ-chỗ → tới lấy", "bang_chung": "med", "phanh": "", "phanh_loai": "", "nan_tu": "",
     "xem_ky": {"cac_buoc": ["Dán số", "Mẫu tin xác nhận"], "vi_sao_chon": "OPUS: thêm vòng xác nhận",
                "da_nghi_roi_bo": "", "bang_chung_chi_tiet": "", "chot_se_co": "việc + mẫu tin",
                "do_va_nguong_dung": "2 tuần"}},
    {"ten": "Gói ăn trưa cố định tuần", "bac": "chao_hang", "co_che": "đăng ký 5 bữa/tuần, giữ suất",
     "vi_du_mau": "'Gói 5 trưa: luôn có phần, khỏi lo hết'", "dich_luc": "gỡ LO bằng cam kết nguồn",
     "ai_nhung_tay": "chủ", "bao_lau": "vài tuần", "doi_van_hanh": True, "gia_co": "vài trăm nghìn/tuần",
     "do_bang": "số gói bán", "bang_chung": "low", "phanh": "⚠️ chỉ nên chốt nếu đủ nguyên liệu giữ suất đều",
     "phanh_loai": "resource", "nan_tu": "",
     "xem_ky": {"cac_buoc": ["Định giá gói"], "vi_sao_chon": "OPUS: chuyển LO thành nếp",
                "da_nghi_roi_bo": "", "bang_chung_chi_tiet": "", "chot_se_co": "1 gói", "do_va_nguong_dung": "3 tuần"}},
]}

_MODE = {"draft_fail": False, "optimize_fail": False}
_seen = {"draft_user": "", "opt_user": ""}


def _install_stubs():
    def _rt(o):
        return json.loads(json.dumps(o, ensure_ascii=False))

    async def _get_profile(uid):
        return _rt(_DB)

    async def _upsert(uid, **fields):
        _DB.update(_rt(fields))
        return _rt(_DB)

    async def _call(task_type=None, system="", user="", max_tokens=0, **kw):
        from tools.llm_router import TaskType
        if task_type == TaskType.CAMPAIGN_MOVES_DRAFT:
            if _MODE["draft_fail"]:
                raise router.AllProvidersFailedError("draft down")
            _seen["draft_user"] = user
            return {"output": json.dumps(_DRAFT, ensure_ascii=False)}
        if _MODE["optimize_fail"]:
            raise router.AllProvidersFailedError("optimize down")
        _seen["opt_user"] = user
        return {"output": json.dumps(_OPT, ensure_ascii=False)}

    async def _ensure():
        return None

    async def _pick(x=None):
        return 1

    biz.available = lambda: True
    biz.ensure_client = _ensure
    biz.pick_user_id = _pick
    profiles.get_profile = _get_profile
    profiles.upsert_profile = _upsert
    router.call = _call


_fails = []


def check(name, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else "   << " + str(extra)))
    if not cond:
        _fails.append(name)


async def main():
    _install_stubs()

    print("\n① gen_moves chạy thật — seam bind id, trả nước đi có bậc + Xem-kỹ")
    _MODE.update(draft_fail=False, optimize_fail=False)
    r = await biz.gen_moves(1, "aud_core", "prob_x")
    check("không error", "error" not in r, r.get("error"))
    mv = r.get("moves", [])
    check("có nước đi", len(mv) >= 1, len(mv))
    check("seam trả đúng stage/ids", r.get("stage") == "awareness" and r.get("problem_id") == "prob_x")
    check("mỗi nước đi có bậc slug hợp lệ", all(m["bac"] in biz._BAC_ENUM for m in mv))
    check("mỗi nước đi có id + bac_level", all(m["id"].startswith("move_") and m["bac_level"] in (1, 2, 3, 4, 5) for m in mv))
    check("có khối Xem-kỹ", all(isinstance(m.get("xem_ky"), dict) and "cac_buoc" in m["xem_ky"] for m in mv))
    check("luc_chan có nội dung", bool(r.get("luc_chan")))

    print("\n② Seam đứt phải NỔ (không im)")
    check("audience sai → error", "error" in await biz.gen_moves(1, "aud_NOPE", "prob_x"))
    check("problem sai → error", "error" in await biz.gen_moves(1, "aud_core", "prob_NOPE"))
    check("thiếu id → error", "error" in await biz.gen_moves(1, "", ""))

    print("\n③+④ 2-call: OPTIMIZE thắng, nháp được truyền vào tối-ưu")
    _MODE.update(draft_fail=False, optimize_fail=False)
    r = await biz.gen_moves(1, "aud_core", "prob_x")
    check("optimized=True khi Opus ra hợp lệ", r.get("optimized") is True, r.get("optimized"))
    check("dùng bản Opus (tên đặc trưng Opus)",
          any("Gói ăn trưa cố định tuần" == m["ten"] for m in r["moves"]), [m["ten"] for m in r["moves"]])
    check("nháp Sonnet ĐƯỢC truyền vào call tối-ưu",
          "BẢN NHÁP" in _seen["opt_user"] and "Mở nhận giữ món qua Zalo" in _seen["opt_user"])

    print("\n③b OPTIMIZE hỏng → degrade về NHÁP (không crash)")
    _MODE.update(draft_fail=False, optimize_fail=True)
    r = await biz.gen_moves(1, "aud_core", "prob_x")
    check("không error khi optimize hỏng", "error" not in r, r.get("error"))
    check("optimized=False", r.get("optimized") is False, r.get("optimized"))
    check("vẫn có nước đi từ NHÁP", any("Mở nhận giữ món qua Zalo trước 11h" == m["ten"] for m in r["moves"]),
          [m["ten"] for m in r.get("moves", [])])

    print("\n③c DRAFT hỏng hẳn → error")
    _MODE.update(draft_fail=True, optimize_fail=False)
    check("draft down → error", "error" in await biz.gen_moves(1, "aud_core", "prob_x"))

    print("\n⑤ Sanitize — rác bị vứt, ≥2 bậc")
    _MODE.update(draft_fail=False, optimize_fail=False)
    r = await biz.gen_moves(1, "aud_core", "prob_x")
    check("nước đi rác (thiếu tên/bậc bậy) bị vứt", all(m["ten"] and m["bac"] in biz._BAC_ENUM for m in r["moves"]))
    check("bac_spread≥2 → note rỗng", r.get("bac_spread") >= 2 and not r.get("note"), (r.get("bac_spread"), r.get("note")))

    print("\n⑥ Nghĩ thêm — rethink chèn vào payload nháp")
    await biz.gen_moves(1, "aud_core", "prob_x", rethink="khách bảo giá không phải vấn đề")
    check("rethink vào payload NHÁP", "NGHĨ THÊM" in _seen["draft_user"] and "giá không phải vấn đề" in _seen["draft_user"])

    print("\n⑦ commit_move — chốt thành chiến dịch + mechanic + snapshot")
    r = await biz.gen_moves(1, "aud_core", "prob_x")
    chosen = r["moves"][0]
    c = await biz.commit_move(1, "aud_core", "prob_x", chosen)
    check("commit không error", "error" not in c, c.get("error"))
    camp = c.get("campaign", {})
    check("is_campaign=True", camp.get("is_campaign") is True)
    check("mechanic = nước đi đã chọn", camp.get("mechanic", {}).get("ten") == chosen["ten"])
    snap = camp.get("snapshot", {})
    check("snapshot chụp đúng vấn đề",
          snap.get("problem_id") == "prob_x" and snap.get("stage") == "awareness"
          and snap.get("problem_text") == "sợ tới nơi hết món, mất công đi", snap)
    check("snapshot chụp tệp", snap.get("audience_id") == "aud_core" and snap.get("audience_role") == "core")
    check("chiến dịch DRAFT (chưa lịch)", camp.get("status") == "draft" and camp.get("grid") == [])
    bigs = _DB["intake_extra"].get("big_ideas", [])
    check("đã ghi vào big_ideas", any(b.get("id") == camp.get("id") for b in bigs), len(bigs))

    print("\n⑦b commit nước đi rác → error")
    check("move bậy → error", "error" in await biz.commit_move(1, "aud_core", "prob_x", {"ten": "", "bac": "zz"}))

    print("\n" + ("="*48))
    if _fails:
        print(f"❌ {len(_fails)} FAIL: {_fails}")
        sys.exit(1)
    print("✅ TẤT CẢ PASS")


if __name__ == "__main__":
    asyncio.run(main())
