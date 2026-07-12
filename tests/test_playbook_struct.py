"""Regression test PR-A — playbook_struct (schema emit + validate 2 mức).

Chạy offline (không key/DB): kiểm hằng prompt `_TAC_SYSTEM` + hàm thuần
`_validate_playbook_struct`. Bao Q-A/Q-B/Q-C (chốt hội đồng 2026-07-11):
  Q-A cut TƯƠNG ĐỐI (bỏ ví dụ số tuyệt đối bịa)
  Q-B insight segment-level (phần hồn của tệp)
  Q-C compliance (chính sách nền tảng + seeding thật/disclose)
+ validate: NGHIÊM với wedge, LỎNG với tệp phụ, insight KHÔNG bắt buộc (degrade).

Chạy:  python3 tests/test_playbook_struct.py   (exit 0 = pass)
"""
import sys, os, json, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import webapp.business as B


def _wedge_huong():
    return {"huong": "h", "territory": "lãnh địa X", "tows": "SO1",
            "channels": ["Reels 15s"], "test": "3 biến thể", "cut": "thắng ≥1.5× thua",
            "kpis": ["view"], "example": ""}


def _valid_struct(insight=True):
    seg = {"name": "Mẹ bỉm", "archetype": "impulse", "is_wedge": True,
           "tiers": {"tofu": [_wedge_huong()], "mofu": [_wedge_huong()], "bofu": [_wedge_huong()]}}
    if insight:
        seg["insight"] = "sợ chọn sai sữa cho con"
    return {"segments": [seg]}


def run():
    R = []
    s = B._TAC_SYSTEM

    # ---- Q-A: cut tương đối, không còn ví dụ số tuyệt đối bịa ----
    R.append(("Q-A ví dụ cut dạng tương đối", "biến thể thắng ≥1.5×" in s))
    R.append(("Q-A luật nhãn số tuyệt đối", "ngưỡng giả định" in s))
    R.append(("Q-A đã bỏ ví dụ 'Watch-through>30%' bịa", "Watch-through>30%" not in s))

    # ---- Q-B: insight segment-level ----
    R.append(("Q-B insight trong schema JSON", '"insight": ""' in s))
    R.append(("Q-B mô tả insight (phần hồn)", "phần HỒN" in s))

    # ---- Q-C: compliance ----
    R.append(("Q-C có luật COMPLIANCE", "COMPLIANCE" in s))
    R.append(("Q-C cấm review giả", "review giả" in s))

    # ---- JSON mẫu trong prompt vẫn parse + có insight ----
    i = s.rfind("{\n", 0, s.index('  "segments": ['))
    block = s[i:s.index("- `segments`")].rstrip().rstrip('"').rstrip()
    try:
        d = json.loads(block)
        seg = d["segments"][0]
        R.append(("JSON mẫu parse được", True))
        R.append(("JSON mẫu segment có insight", "insight" in seg))
        R.append(("JSON mẫu cut đã đổi tương đối", seg["tiers"]["tofu"][0]["cut"].startswith("sau 7 ngày")))
    except Exception as e:
        R.append((f"JSON mẫu parse ({e})", False))

    # ---- validate 2 mức ----
    R.append(("validate: struct wedge đủ khoá → PASS", B._validate_playbook_struct(_valid_struct(True)) is True))
    R.append(("validate: THIẾU insight vẫn PASS (degrade)", B._validate_playbook_struct(_valid_struct(False)) is True))
    # wedge thiếu 1 tầng → FAIL (nghiêm)
    bad = _valid_struct(True); bad["segments"][0]["tiers"]["bofu"] = []
    R.append(("validate: wedge thiếu tầng → FAIL", B._validate_playbook_struct(bad) is False))
    # tệp phụ (is_wedge False) thiếu tầng → vẫn PASS (lỏng)
    aux = {"segments": [{"name": "phụ", "archetype": "x", "is_wedge": False, "tiers": {"tofu": [], "mofu": [], "bofu": []}}]}
    R.append(("validate: tệp phụ thiếu tầng → PASS (lỏng)", B._validate_playbook_struct(aux) is True))
    R.append(("validate: không phải dict → FAIL", B._validate_playbook_struct("x") is False))

    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok = ok and passed
    print("playbook_struct regression:", "✅ PASS" if ok else "❌ FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
