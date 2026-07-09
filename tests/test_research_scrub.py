"""R-3: eval harness cho R-1 (_scrub_research) — bắt "sửa mới hỏng cũ" mà KHÔNG cần chạy full app / LLM.

Chạy: python -m pytest tests/test_research_scrub.py -v
Hoặc: python tests/test_research_scrub.py   (self-runner, không cần pytest)

Phủ 4 trường hợp:
  1. BAD  — research có mục roadmap "Strategic Implications" + số trần → phải GỠ roadmap + cảnh báo số.
  2. GOOD — số đã gắn nguồn/(ước tính), không roadmap → giữ NGUYÊN, không warn.
  3. SWOT — TOWS + "Cơ hội" là hợp lệ → TUYỆT ĐỐI không bị gỡ nhầm.
  4. NON-RESEARCH — skill ngoài research → không đụng tới dù có roadmap.
  5. MID   — roadmap ở GIỮA bài → gỡ đúng đoạn, giữ section sau nó.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.business import _scrub_research


BAD_MARKET = """# Nghiên cứu thị trường

## 1. Quy mô thị trường
Thị trường đạt 500 triệu USD năm 2025 theo [VECOM](https://vecom.vn/report).
Tăng trưởng 12% mỗi năm.
Có 99% người dùng smartphone.
Khoảng 3 triệu khách tiềm năng.

## 6. Strategic Implications
### 🟢 Quick wins
- Chạy ads ngay
### 🟡 Medium term
- Xây thương hiệu
### 🔴 Risks
- Đối thủ lớn
"""

GOOD_MARKET = """# Nghiên cứu thị trường

## 1. Quy mô
Thị trường 500 triệu USD ([VECOM](https://vecom.vn)); tăng ~12% (ước tính).

## 2. Kết luận
So-what: nên tập trung phân khúc cao cấp."""

SWOT_TOWS = """# SWOT

## Điểm mạnh
- Chất lượng cao

## Cơ hội
- Thị trường đang lớn

## Ma trận TOWS
### Chiến lược SO (Điểm mạnh × Cơ hội)
- Tận dụng chất lượng để chiếm thị phần
### Chiến lược WT (Điểm yếu × Thách thức)
- Giảm rủi ro"""

NON_RESEARCH = """# Synthesis

## Lộ trình 90 ngày
### Ngắn hạn
- Chạy ngay"""

MID_ROADMAP = """# Customer Insight

## ICP
Phụ nữ 25-40.

## Quick wins
- Làm ngay

## JTBD
Khách muốn tiết kiệm thời gian."""


def test_bad_market_strips_roadmap_and_flags_numbers():
    cleaned, warns = _scrub_research(BAD_MARKET, "market_research")
    # roadmap bị gỡ
    assert "Strategic Implications" not in cleaned
    assert "Quick wins" not in cleaned
    assert "Medium term" not in cleaned
    # nội dung research thật GIỮ nguyên
    assert "Quy mô thị trường" in cleaned
    assert "[VECOM](https://vecom.vn/report)" in cleaned
    # có cả 2 cảnh báo
    assert any("lộ trình" in w or "roadmap" in w for w in warns), warns
    assert any("chưa gắn nguồn" in w for w in warns), warns


def test_good_market_unchanged_no_warn():
    cleaned, warns = _scrub_research(GOOD_MARKET, "market_research")
    assert cleaned == GOOD_MARKET.strip()
    assert warns == []


def test_swot_tows_not_stripped():
    cleaned, warns = _scrub_research(SWOT_TOWS, "swot")
    assert "Ma trận TOWS" in cleaned
    assert "Chiến lược SO" in cleaned
    assert "Chiến lược WT" in cleaned
    assert "Cơ hội" in cleaned
    assert not any("lộ trình" in w or "roadmap" in w for w in warns), warns


def test_non_research_skill_untouched():
    cleaned, warns = _scrub_research(NON_RESEARCH, "synthesis")
    assert cleaned == NON_RESEARCH          # trả NGUYÊN (kể cả whitespace)
    assert "Lộ trình 90 ngày" in cleaned
    assert warns == []


def test_mid_roadmap_removed_keeps_following_section():
    cleaned, warns = _scrub_research(MID_ROADMAP, "customer_insight")
    assert "ICP" in cleaned
    assert "JTBD" in cleaned                 # section SAU roadmap được giữ
    assert "Quick wins" not in cleaned
    assert "Làm ngay" not in cleaned


def test_empty_content_safe():
    assert _scrub_research("", "market_research") == ("", [])


if __name__ == "__main__":
    # Self-runner (không cần pytest)
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)
