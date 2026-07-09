# CLAUDE.md — hướng dẫn cho AI coding agent

Marketing OS — **web app** ("Max", AI CMO) cho founder/SME Việt. KHÔNG phải Telegram bot.
Mọi nội dung hướng tới người dùng viết **tiếng Việt tự nhiên** (không dịch máy).

## Chạy & kiểm thử
```bash
pip install -r requirements.txt
python run_web.py            # → http://localhost:8000 (SQLite mặc định, KHÔNG cần Telegram)
```
- Lưu trữ: SQLite (`webapp/markos_web.db`) mặc định; Supabase nếu set `SUPABASE_URL`+`SUPABASE_SERVICE_KEY` (chạy `webapp/supabase_schema.sql`).
- LLM: cần ≥1 khoá `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GEMINI_API_KEY`.

## Frontend — 1 nguồn duy nhất (không còn standalone)
App chạy trên Railway, server phục vụ `web/` tĩnh (`web/index.html` load `app.js`/`styles.css`/`data.js` rời).
**KHÔNG còn `dashboard-standalone.html` / `build_standalone.py`** — đã khai tử (2026-07-08, theo D-033/D-042).
Sửa FE = sửa thẳng `web/app.js` · `web/styles.css` · `web/index.html`, **không phải mirror đi đâu cả**.

Kiểm sau khi sửa FE:
```bash
node --check web/app.js
```
Kiểm backend: `python3 -c "import webapp.business, webapp.api"`.

## Kiến trúc
- **Backend** `webapp/`: Starlette + uvicorn.
  - `api.py` — routes `/api/biz/*` (đăng ký ở `api_routes()`).
  - `business.py` — TOÀN BỘ logic nghiệp vụ (research, strategy, messaging, rhythm, calendar, gen bài…). File lớn; hàm `async def`, import nội bộ **lazy** (trong hàm).
  - `events.py` — SSE realtime (watcher 4s + Supabase Realtime).
  - `store*.py` — lớp lưu trữ SQLite/Supabase.
- **Frontend** `web/`: SPA thuần JS (hash-router trong `app.js`), không framework.
- **LLM** `tools/llm_router.py` — định tuyến đa nhà cung cấp theo `TaskType` (Gemini grounded / GPT-5 / Claude).
- **`agents/`** = thư viện PROMPT + logic AI dùng chung (KHÔNG phải bot). `business.py` tái dùng prompt bot (`agents.prompts`, `agents.operational_prompts`) qua import lazy/try-except — **đây là chủ ý để giữ chất lượng**, đừng thay bằng prompt tự chế mỏng.

## Quy ước dữ liệu (KHÔNG đổi schema DB)
- Dữ liệu người dùng nằm ở `profile.intake_extra` (dict) + bảng `campaigns_v2` + `skill_runs` (append-only, bản mới nhất thắng).
- Cấu hình mới → thêm key vào `intake_extra`, KHÔNG thêm cột/bảng.
- Ví dụ đã có trong `intake_extra`: `bet_choices`, `messaging` (cốt lõi+trụ+giọng+focus), `content_rhythm` (6 dạng × tần suất), `funnel_map`, `calendar_posts`.

## Mô hình sản phẩm — KHUNG CHỦ = 6 MIỀN CMO (D-049⑥)
Khung chính thức: **6 miền CMO** — D1 Positioning · D2 Pricing · D3 Channel/Budget · D4 Content · D5 Retention · D6 Measurement. Chi tiết + Strategy Spine: **`docs/cmo/00-PLAN.md`** (trục). Thứ tự: **Nghiên cứu (grounding) → Spine → 6 miền**.

**"4 tầng nội dung" = cách triển khai D4 Content + lớp Nghiên cứu-grounding** (KHÔNG phải toàn bộ sản phẩm):
① Nghiên cứu (T1-T5) → ② Chiến lược (Đặt cược → Synthesis+Playbook → 🏛️ Thông điệp) →
③ Sáng tạo (6 dạng nội dung · 🎛️ Nhịp nền) → ④ Phân phối & Đo (Lịch: nền móng + đợt spike).
Chi tiết 4 tầng: `docs/web/product-journey-4-tang.md`. Mọi bài **tự bám Thông điệp** (cốt lõi+giọng) để nhất quán.

## Khi thêm route/tính năng
1. `business.py`: viết hàm `async def` (lazy import deps).
2. `api.py`: thêm handler + `Route(...)` trong `api_routes()`.
3. `business.py biz_data()`: expose dữ liệu ra key `bizXxx` cho FE.
4. FE `app.js`: render + handler trong `handleAction()` (sửa thẳng, 1 nguồn — không mirror).
5. **Cổng kiểm mối nối** (xem dưới) rồi verify (mục trên) rồi commit.

## ⚠️ Cổng kiểm mối nối (seam check) — LUẬT cho MỌI function
Lỗi nguy hiểm nhất = **mối nối**: function *tiêu thụ* một khoá mà **không ai sản xuất** ra, hoặc lệch tên/slug/kiểu → **im tới runtime mới nổ**. Trước khi PASS bất kỳ function nào (code hoặc brief), qua Hiến pháp ở **`docs/cmo/WIRING.md`**:
1. Mọi khoá function đọc/ghi có **producer** + dòng trong sổ hợp đồng WIRING; khớp **tên/slug/enum/kiểu** 2 đầu; **tới được** lúc runtime; có **đường degrade** nếu input thiếu/thô.
2. Nếu function **TỰ SUY trạng thái user** (phân loại ngành, stage, funnel…) → **luật derived-state**: bắt buộc lưu `confidence`+`updated`+`why-log` + cổng review + **human-override** (con người thắng). Không đoán liều, đóng băng khi dao động.
3. **Không dồn phân tích trước** — Hiến pháp (bất biến) chốt 1 lần; phân tích mối nối **từng function làm JIT tại brief-time** (mục "Phân tích mối nối" trong brief).
- Đụng `brain/` → chạy `py brain/_check.py` (linter synapse, exit 1 = đứt).

## Tài liệu thiết kế AI CMO (đọc khi làm slice CMO / brain / function mới)
`docs/cmo/00-PLAN.md` (kiến trúc 2 tầng×6 miền + nguyên tắc) · `STRATEGY-FRAMEWORK.md` (khung 6 lựa chọn chiến lược — xương phân tích đa ngành, grounded Playing-to-Win/STP/Dunford/STDC/AARRR) · `WORKFLOW.md` (build loop, 4 vai review + 4 luật vận hành) · `EVAL.md` (chuẩn đánh giá field/tính năng) · `KNOWLEDGE.md` (vault/bộ não brain/) · `WIRING.md` (Hiến pháp mối nối + sổ hợp đồng) · `briefs/00-INDEX.md` (thứ tự slice + luật mỗi function).

## Không làm
- Không thêm phụ thuộc Telegram / không đụng `bot/` (đã tách khỏi repo này).
- Không đổi schema DB. Không bịa số liệu trong output AI (prompt đã cấm — giữ nguyên).

## Git workflow (Cline code, Claude Code review, user merge)
`main` có branch protection: bắt buộc PR + ≥1 approval, không cho push thẳng/force-push.

1. Mọi task code mới → tạo branch riêng từ `main` (vd `feature/xxx`). KHÔNG bao giờ commit/push thẳng vào `main`.
2. Cline code + push branch đó, mở PR bằng `gh pr create` — KHÔNG tự merge (không có quyền, và không được merge dù có quyền).
3. Claude Code review PR (diff, logic, an toàn) trước khi merge.
4. Sau khi Claude Code duyệt → merge vào nhánh trung gian (staging/dev) để user test.
5. User test xong, tự quyết định merge nhánh đó vào `main`.
