# Slice — Intake sắc hơn + USP validation (onliness / white-space)

> **Nguồn:** phiên soi R-1 thực nghiệm (drive AI intake trên Railway) + hội đồng thiết kế intake (2026-07-09). Chi tiết bằng chứng: chạy `/api/biz/intake` lộ câu nhồi-2-ý + giọng buộc tội + AI intake nông hơn form cứng.
> **Đọc trước:** `agents/discovery_prompts.py` (`MCKINSEY_INTERVIEW_SYSTEM`) · `agents/discovery.py` (`REQUIRED_FIELDS`, `_PROFILE_FIELDS`, `apply_discovery_to_profile`) · `webapp/business.py` `intake_turn` (~4015) + `strategize_web` `usp_rule` (~3627) + research T2 competitor prompt · `brain/frameworks/dunford-positioning.md`.
> **Branch:** làm trên nhánh tích hợp hiện hành (staging → feature branch mới nếu cần).

## Nguyên tắc CHỐT từ hội đồng (bất biến cho slice này)
1. **Chỉ HỎI cái founder-mới-biết + trả-lời-nổi.** Cái trừu tượng (JTBD, khác biệt, định vị) → **Max SUY rồi cho founder xác nhận**, KHÔNG hỏi trần.
2. **KHÔNG BAO GIỜ ép.** "Chưa biết" là câu trả lời hợp lệ → kích hoạt derive. (Prompt dòng 67 đã có — giữ.)
3. **1 câu = 1 ý.**
4. **Nháp → xác nhận** thay cho ô-trống: founder phản ứng với bản nháp giỏi gấp 10 lần tự sáng tạo.

---

## F1 — Sửa prompt intake: bỏ nhồi-2-ý + bỏ giọng buộc tội (RẺ, prompt-only)
**File:** `agents/discovery_prompts.py`, `MCKINSEY_INTERVIEW_SYSTEM`.
- **Xoá dòng 37** ("Một câu hỏi có thể gom 2 trường liên quan nếu tự nhiên…") — nó **mâu thuẫn** dòng 32 ("MỘT câu mỗi lượt") và là gốc gây câu nhồi (T1 nghề+giá, T3 thời gian+doanh thu).
- **Thêm 1 rule chống giọng buộc tội** (LLM tự chế khi gặp lặp — thực nghiệm thấy nó nói "app lỗi / sếp copy-paste", chạm tự ái): 
  > "Nếu sếp trả lời lặp/cụt/lệch: TUYỆT ĐỐI không đổ lỗi kỹ thuật hay nói sếp 'copy-paste/app lỗi'. Nhẹ nhàng hỏi lại bằng cách khác, hoặc cho phép bỏ qua trường đó ('cái này để em tự đề xuất sau cũng được')."
- **Verify:** không có key vẫn kiểm tĩnh được (đọc lại prompt); nếu có key → re-run drive intake, xác nhận không còn 2-ý/1-câu.

## F2 — Thêm 1 câu: competitive_alternative (founder biết + nuôi Dunford)
**Vì sao:** đây là xăng số 1 của D1-F1 (Dunford), *chỉ founder biết*, *trả lời nổi* nếu hỏi cụ thể — mà AI intake đang thiếu (form cứng có, AI intake không).
- **Prompt** (`discovery_prompts.py`): thêm field target + vào block JSON completion, phrasing ĐỜI THƯỜNG (không thuật ngữ):
  > *"Trước khi biết tới sếp, khách của sếp thường giải quyết chuyện này bằng cách nào — tự làm, mua ở đâu, hay dùng của ai?"*
  Đánh dấu **tùy** (hỏi nếu còn mạch; "chưa rõ" thì bỏ qua — theo nguyên tắc #2).
- **WIRING (seam — làm ĐÚNG chỗ):** `competitive_alternative` KHÔNG có cột DB → phải ghi vào **`intake_extra.answers.competitive_alternative`** (nơi form cứng ghi + research/strategize đọc qua `extra.get("answers")`, xem `business.py:948/3637/3814`). 
  - Trong `intake_turn` (~4015): sau khi có `discovery_input`, **tách `competitive_alternative` ra khỏi profile-fields** và merge vào `profile.intake_extra["answers"]` (đừng nhét vào cột user_business_profile — không có cột đó). Kiểm cách `intake_turn` hiện ghi `intake_extra` (nếu chưa ghi thì thêm đường ghi answers).
  - **Đừng** thêm vào DB schema. **Đừng** đổi `_PROFILE_FIELDS` nếu nó map thẳng sang cột.
- **Verify:** chạy drive intake → check profile 990xxx có `intake_extra.answers.competitive_alternative`.

## F3 — Competitor T2: onliness test + white-space (làm USP có kiểm định)
**Vì sao:** hiện T2 phân tích đối thủ chung chung; thiếu bước **đối chiếu USP/khác biệt founder ĐẦU-NHAU với từng đối thủ** → tìm chỗ trống chưa ai chiếm.
- **Grep** prompt skill `competitor` trong `research_web` (`business.py`) — đừng tin số dòng.
- Thêm vào prompt competitor 2 yêu cầu (block "so-what", không phá cấu trúc cũ):
  1. **Onliness test:** với USP/khác biệt founder khai (nếu có), soi từng đối thủ: *ai đã claim điều tương tự? Nếu đối thủ nói được y câu đó → khác biệt này KHÔNG phòng thủ được.*
  2. **White-space:** chỉ ra **khoảng trống định vị chưa ai đứng** trong ngành (bám đối thủ THẬT, có nguồn — theo luật chống bịa `_RW_ANTIFAB`).
- Giữ nguyên anti-fab (kèm nguồn / "(ước tính)").

## F4 — usp_stance='missing' đứng vào white-space (nhỏ)
**File:** `strategize_web` `usp_rule` (~3627-3632).
- Nhánh fallback (`missing`) hiện: "BẠN đề xuất định vị dựa trên research". **Bổ sung:** "…đề xuất USP **đứng vào KHOẢNG TRỐNG** mà research đối thủ (T2) tìm được (white-space), tránh điều đối thủ đã claim (onliness)."
- Đây là nối F3 → synthesis: định vị mới né chỗ đã đông, đứng chỗ trống.

## F5 — (GHI NỢ, KHÔNG làm trong slice này) Nháp → xác nhận UX
Cơ chế "Max nháp differentiation/JTBD/USP → founder gật/sửa" cần FE + backend → **slice riêng sau**. Ghi vào backlog. Hiện `usp_stance` + doc-editor đã cho founder sửa bản Max đề xuất (một phần); F5 làm nó thành bước có chủ đích.

---

## Verify chung (mỗi F 1 commit, chờ review)
```bash
python3 -c "import webapp.business, webapp.api"     # (api thiếu starlette trong sandbox = OK, nêu rõ)
py -m py_compile webapp/business.py
```
- F1/F2/F3 là prompt/wiring → nếu có key thì re-run drive intake + soi output; không key thì kiểm tĩnh + khai rõ "hành vi runtime chờ chạy thật".

## Không làm
- KHÔNG đổi schema DB (alternative → `intake_extra.answers`). KHÔNG ép trả lời. KHÔNG hỏi JTBD/differentiation trần (để derive). KHÔNG phá anti-fab research. KHÔNG làm F5 (nháp-xác-nhận) ở slice này.
- 1 function = 1 commit → push → chờ review. KHÔNG tự merge.
