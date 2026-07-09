# Slice D1-F2 — Nối định vị (Spine + vault) vào Messaging House

> **Mục tiêu:** `gen_messaging` (Messaging House) kế thừa ĐÚNG định vị — Strategy Spine (alternative/differentiator/statement) + khung craft vault — thay vì chỉ `usp` thô. Trụ + giọng cùng một gốc với synthesis (F1). Siết seam **định vị → thông điệp** để mọi bài nội dung bám 1 lõi nhất quán.
> **Đọc trước:** `webapp/business.py` → `gen_messaging` (~dòng 3029), `_spine_anchor` (~2925), `_framework_anchor` (~2883, F1). `docs/cmo/briefs/D1-positioning.md` (F1) · `WIRING.md`.
> **Branch:** `feature/consolidate`.

## Bối cảnh (đọc kỹ — tránh làm sai chỗ)
- F1 đã grounded mục Định vị trong **synthesis** bằng vault. Grounding **DỪNG ở đó** — chưa chảy tới messaging.
- `gen_messaging` hiện: **KHÔNG gọi** `_spine_anchor`, **KHÔNG gọi** `_framework_anchor`; định vị vào prompt chỉ qua `usp = prof.get("usp")` (USP thô founder gõ) + `synth[:2200]` (có thể cắt mất mục Định vị).
- → Hở: trụ/giọng có thể lệch khỏi định vị Dunford mà synthesis vừa dựng.
- **Cả 2 helper đã tồn tại** (F1 + P0.2) → F2 KHÔNG viết logic mới, chỉ **chèn 2 anchor vào prompt** (đây là inject, không phải function mới).

## Phân tích mối nối (WIRING)
- **ĐỌC:** `spine` (producer = `save_spine`, ở `intake_extra.spine`) + vault cards (producer = knowledge-loop, `live` ✅) + `industry` (`prof.get("industry")`, đã có ở dòng ~3052) + `extra` (đã có ở ~3049). Mọi input ĐỀU sẵn trong scope `gen_messaging`.
- **GHI:** `intake_extra.messaging` — cấu trúc GIỮ NGUYÊN (`_norm_messaging`), KHÔNG đổi.
- **Derived-state?** KHÔNG.
- **Degrade:** `_spine_anchor(extra)` trả `""` nếu spine rỗng; `_framework_anchor(...)` trả `""` nếu vault rỗng/lỗi → prompt như cũ, KHÔNG vỡ.
- **Chống parrot:** `_framework_anchor` chỉ bơm Spec-gen (không exemplar — đã đảm bảo ở F1). `_spine_anchor` bơm dữ liệu user (an toàn).

## Function (1 commit) — chèn 2 anchor vào `user` của `gen_messaging`
Chỗ ráp `user` (~dòng 3078) hiện bắt đầu `f"# Ngành\n{industry} — {arche_label}\n# Sản phẩm..."`. Chèn spine + framework block NGAY SAU dòng ngành, TRƯỚC sản phẩm:
```python
        fw = _framework_anchor(industry=industry, goal_type="positioning")
        sp = _spine_anchor(extra)
        user = (f"# Ngành\n{industry} — {arche_label}\n"
                f"{sp}{fw}"
                f"# Sản phẩm/dịch vụ\n{product or '(chưa rõ)'}\n"
                f"# Khách mục tiêu\n{target or '(chưa rõ)'}\n# USP đã chốt\n{usp or '(chưa rõ)'}\n"
                ... # GIỮ NGUYÊN toàn bộ phần còn lại (bets/synth/tact/cust/steer)
        )
```
- **GIỮ dòng `# USP đã chốt`** (lời founder) — spine positioning BỔ SUNG, không thay thế.
- `sp`/`fw` tự mang tiêu đề block (`# CHIẾN LƯỢC NỀN…` / `# KHUNG ĐỊNH VỊ…`) + xuống dòng; nếu rỗng → chuỗi rỗng, prompt liền mạch như cũ.
- KHÔNG đụng nhánh `stage`/merge/`_norm_messaging` phía dưới.

## Verify (dán output thật vào commit)
```bash
python3 -c "import webapp.business, webapp.api"   # (api có thể thiếu starlette trong sandbox — nêu rõ nếu vậy)
py -m py_compile webapp/business.py && echo COMPILE_OK
py -c "import webapp.business as B; assert callable(B._spine_anchor) and callable(B._framework_anchor); print('anchors OK')"
```
- Không có key/DB thì KHÔNG chạy `gen_messaging` thật được — khai rõ "verify tĩnh; hành vi runtime chờ R-1".

## Self-review report (dán vào commit)
```
[D1-F2] nối Spine + vault vào gen_messaging — messaging kế thừa định vị Dunford, không chỉ USP thô
Đã check: compile/import OK · 2 anchor tồn tại · giữ USP line + cấu trúc messaging dict · degrade '' an toàn
Chưa chắc: token budget messaging (2600 pillars) có bị nén khi prompt dài thêm? → CHỐT SAU R-1, đừng sửa mù
```

## Mở — chốt SAU R-1 (đừng làm trong F2)
- Token budget `gen_messaging` (1400 core / 2600 pillars) nếu output nén khi input dày thêm → chỉ nâng khi R-1 cho thấy cụt.
- Trọng số nhấn định vị trong prompt (nếu CMO thấy trụ vẫn lệch).

## Không làm
- KHÔNG đổi cấu trúc `messaging` dict, KHÔNG bỏ dòng USP, KHÔNG đụng synthesis/playbook/`_norm_messaging`.
- KHÔNG sửa `brain/*` hay `brain.py`, KHÔNG viết logic mới (chỉ inject 2 anchor sẵn có).
- KHÔNG Write đè `business.py` (Edit chèn có mục tiêu). 1 function = 1 commit, push, **dừng chờ review**, KHÔNG tự merge.
