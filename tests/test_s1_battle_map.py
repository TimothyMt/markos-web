"""Test S1 — Bản đồ trận địa (battle_map / resources / principles).

Chạy KHÔNG cần key LLM / DB: stub storage.v2.profiles + tools.llm_router, drive HÀM THẬT
(gen_battle_map, save_battle_map, save_resources, save_principles).

⚠️ Vì sao có file này: bản S1 đầu tiên pass cả `py_compile` lẫn `import webapp.business`
nhưng CHẾT 100% lúc chạy (thiếu import datetime) — 2 cổng đó về cấu trúc không bắt được
tên chưa định nghĩa trong thân hàm. Test này gọi hàm THẬT, đó mới là cổng có răng.

Chốt các bất biến của brief S1 (docs/cmo/BRIEF-S1-ban-do-tran-dia.md §2/§5/§8):
  ① gen_battle_map chạy được, đẻ đủ 3 vai (core/growth/retain) + nhãn tệp là NGƯỜI THẬT.
  ② Guard chống-generic: LLM trả TÊN LOẠI ("bất tiện") làm nội dung vấn đề → BỊ VỨT;
     vấn đề cụ thể thì giữ (brief §9 — nhãn loại ≠ vấn đề).
  ③ id tệp ỔN ĐỊNH qua regen (hợp đồng persist cho S3 — mìn HANDOFF §4).
  ④ Human-override: người sửa → save đánh dấu edited_by_user (diff, không cần FE tự khai);
     id giữ nguyên qua ĐỔI TÊN; regen sau đó KHÔNG ghi đè thứ người đã sửa.
  ⑤ Người XOÁ được thật — tệp vắng mặt trong payload không bị hồi sinh.
  ⑥ LLM hỏng → degrade (degraded=True), KHÔNG crash, KHÔNG xoá vấn đề nào của người.
  ⑦ save_resources / save_principles chạy; expires vô hạn = None (KHÔNG phải "");
     created GIỮ ngày tạo gốc khi sửa mục cũ.

Chạy:  python tests/test_s1_battle_map.py   (exit 0 = pass)
"""
import sys, os, json, asyncio

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import webapp.business as biz
import storage.v2.profiles as profiles
import tools.llm_router as router

_DB = {"industry": "F&B",
       "intake_extra": {"wedge": "chủ quán ăn nhỏ tự đứng bếp",
                        "answers": {"objection": "khách hỏi giá xong im, không đặt"}}}

_RESEARCH = {"synthesis": "Khoảng trống: dân văn phòng quanh toà nhà chưa ai phục vụ bữa trưa nhanh.",
             "customer_insight": "Khách sợ tới nơi hết món. Nhiều người không biết quán ở hẻm nào."}

# LLM giả: cố tình nhét 1 vấn đề RÁC ("bất tiện" = tên loại) để test guard ②
_LLM_JSON = {"audiences": [
    {"role": "core", "label": "dân văn phòng quanh toà nhà, ăn trưa vội",
     "why": "bám wedge", "confidence": "high",
     "stages": {"awareness": [{"text": "không biết quán nằm hẻm nào, ngại tìm", "type": "unaware",
                               "source": "research", "confidence": "high", "why": "T3"}],
                "consideration": [{"text": "bất tiện", "type": "inconvenience", "source": "max",
                                   "confidence": "low", "why": "nhãn loại — phải bị vứt"}],
                "conversion": [{"text": "sợ tới nơi hết món, mất công đi", "type": "risk",
                                "source": "research", "confidence": "high", "why": "T3"}],
                "retention": []}},
    {"role": "growth", "label": "nhân viên toà nhà kế bên", "why": "segment gap", "confidence": "med",
     "stages": {"awareness": [], "consideration": [], "conversion": [], "retention": []}},
    {"role": "retain", "label": "khách quen đi ăn 2-3 lần/tuần", "why": "suy", "confidence": "low",
     "stages": {"awareness": [], "consideration": [], "conversion": [],
                "retention": [{"text": "ăn mãi một món thấy chán, quên quán", "type": "forget",
                               "source": "max", "confidence": "low", "why": "suy"}]}}]}

_FAIL_LLM = False


def _install_stubs():
    def _rt(o):                      # round-trip JSON = đúng đường thật (HTTP + DB), không chia sẻ tham chiếu
        return json.loads(json.dumps(o, ensure_ascii=False))

    async def _get_profile(uid):
        return _rt(_DB)

    async def _upsert(uid, **fields):
        _DB.update(_rt(fields))
        return _rt(_DB)

    async def _latest(uid, name):
        return _RESEARCH.get(name, "")

    async def _call(**kw):
        if _FAIL_LLM:
            raise RuntimeError("LLM down")
        return {"output": json.dumps(_LLM_JSON, ensure_ascii=False)}

    async def _ensure():
        return None

    async def _pick(x=None):
        return 1

    biz.available = lambda: True
    biz.ensure_client = _ensure
    biz.pick_user_id = _pick
    biz._latest_content = _latest
    profiles.get_profile = _get_profile
    profiles.upsert_profile = _upsert
    router.call = _call


_fails = []


def check(name, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else "   << " + str(extra)))
    if not cond:
        _fails.append(name)


def _all_texts(bm):
    return [p["text"] for a in bm["audiences"] for st in a["stages"].values() for p in st["problems"]]


async def main():
    global _FAIL_LLM
    _install_stubs()

    print("\n① gen_battle_map chạy thật")
    r = await biz.gen_battle_map(1)
    check("không trả error", "error" not in r, r.get("error"))
    bm = r.get("battle_map", {})
    auds = bm.get("audiences", [])
    check("đủ 3 vai", sorted(a["role"] for a in auds) == ["core", "growth", "retain"],
          [a["role"] for a in auds])
    core = next(a for a in auds if a["role"] == "core")
    check("nhãn tệp là người thật", core["label"] == "dân văn phòng quanh toà nhà, ăn trưa vội",
          core["label"])
    check("tệp core có confidence + why", bool(core["confidence"] and core["why"]))

    print("\n② Guard chống-generic (nhãn loại ≠ vấn đề)")
    texts = _all_texts(bm)
    check("vứt vấn đề rác 'bất tiện'", "bất tiện" not in texts, texts)
    check("giữ vấn đề cụ thể", "sợ tới nơi hết món, mất công đi" in texts, texts)

    print("\n③ id ổn định qua regen")
    ids1 = {a["role"]: a["id"] for a in auds}
    r2 = await biz.gen_battle_map(1)
    ids2 = {a["role"]: a["id"] for a in r2["battle_map"]["audiences"]}
    check("id không đổi", ids1 == ids2, (ids1, ids2))

    print("\n④ Human-override: người sửa thắng regen")
    bm2 = r2["battle_map"]
    c = next(a for a in bm2["audiences"] if a["role"] == "core")
    c["label"] = "TÊN DO NGƯỜI TỰ ĐẶT"
    c["stages"]["conversion"]["problems"][0]["text"] = "khách sợ hết món — người tự sửa"
    rs = await biz.save_battle_map(1, bm2)
    check("save không lỗi", "error" not in rs, rs.get("error"))
    sc = next(a for a in rs["battle_map"]["audiences"] if a["role"] == "core")
    check("tệp được đánh dấu edited_by_user", sc["edited_by_user"] is True)
    check("vấn đề được đánh dấu edited_by_user",
          sc["stages"]["conversion"]["problems"][0]["edited_by_user"] is True)
    check("id GIỮ NGUYÊN qua đổi tên", sc["id"] == ids1["core"], (sc["id"], ids1["core"]))

    r3 = await biz.gen_battle_map(1)
    c3 = next(a for a in r3["battle_map"]["audiences"] if a["role"] == "core")
    check("regen KHÔNG ghi đè tên người đặt", c3["label"] == "TÊN DO NGƯỜI TỰ ĐẶT", c3["label"])
    check("regen giữ vấn đề người sửa",
          "khách sợ hết món — người tự sửa" in [p["text"] for p in c3["stages"]["conversion"]["problems"]])

    print("\n⑤ Người xoá được thật")
    bm3 = r3["battle_map"]
    bm3["audiences"] = [a for a in bm3["audiences"] if a["role"] != "growth"]
    rs2 = await biz.save_battle_map(1, bm3)
    roles = [a["role"] for a in rs2["battle_map"]["audiences"]]
    check("tệp bị xoá không hồi sinh", "growth" not in roles, roles)

    print("\n⑥ LLM hỏng → degrade, không mất dữ liệu người")
    before = len(_all_texts(rs2["battle_map"]))
    _FAIL_LLM = True
    r4 = await biz.gen_battle_map(1)
    _FAIL_LLM = False
    check("không crash", "error" not in r4, r4.get("error"))
    check("báo degraded", r4.get("degraded") is True)
    check("không mất vấn đề nào", len(_all_texts(r4["battle_map"])) >= before,
          (before, len(_all_texts(r4["battle_map"]))))

    print("\n⑦ resources / principles")
    rr = await biz.save_resources(1, {"can_owner_on_camera": True, "can_shoot_video": False})
    check("resources ok", "error" not in rr, rr.get("error"))
    check("resources có updated", bool(rr["resources"].get("updated")))
    p1 = await biz.save_principles(1, [{"text": "không giảm giá đại trà"}])
    check("principles ok", "error" not in p1, p1.get("error"))
    check("expires vô hạn = None (không phải '')", p1["principles"][0]["expires"] is None,
          repr(p1["principles"][0]["expires"]))
    created1, pid = p1["principles"][0]["created"], p1["principles"][0]["id"]
    p2 = await biz.save_principles(1, [{"id": pid, "text": "không giảm giá đại trà (sửa)"}])
    check("created giữ ngày gốc", p2["principles"][0]["created"] == created1,
          (created1, p2["principles"][0]["created"]))

    print("\n" + ("=== S1: TẤT CẢ PASS ===" if not _fails
                  else "=== S1: FAIL %d mục: %s ===" % (len(_fails), ", ".join(_fails))))
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
