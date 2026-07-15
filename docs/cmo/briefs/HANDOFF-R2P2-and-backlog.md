# HANDOFF — R2-P2 (dọn code) + backlog (bàn giao phiên khác)

> File tự chứa để 1 phiên MỚI (cold) làm được ngay. Trạng thái tại thời điểm viết: **R2-P1 đã merge vào `staging`**
> (PR #15, `45a529c`). Đọc kèm: `docs/cmo/briefs/R2-unify-strategy-input.md` (brief gốc) · `docs/cmo/WIRING.md` (luật mối nối).

## ⚙️ Luật vận hành (BẮT BUỘC — mọi task dưới)
- Nhánh dev riêng từ `staging` (đừng đụng thẳng `main`/`staging`). PR **base = `staging`**. **KHÔNG tự merge** — chờ user duyệt.
- **KHÔNG đổi schema DB** — mọi thứ nằm trong `intake_extra` (dict). **KHÔNG bịa số** trong output AI. **Đa ngành** — không hardcode ví dụ ngành.
- Verify offline (sandbox thiếu starlette + LLM key): `python3 -m py_compile webapp/business.py webapp/api.py` · `node --check web/app.js web/data.js` · chạy `tests/test_*.py` (mỗi file `python3 tests/x.py`, exit 0 = pass) · Playwright smoke (server `python3 -m http.server 8899 --directory web`; chromium `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`; playwright `/opt/node22/lib/node_modules/playwright`; fake `/api/bootstrap`→`{}` để `apiAvailable=true`).
- Commit message kết thúc bằng 2 dòng:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` / `Claude-Session: <link phiên của bạn>`. KHÔNG để model id trong commit/PR/code.

## Bối cảnh R2 (đã xong P1)
Tầng chiến lược từng có **2 bề mặt nhập trùng**: `bet_choices` (nuôi synthesis/playbook) + `spine` (nuôi `_spine_anchor` máy viết). P1 gộp UI thành **1 form** (`strategyForm` ở `web/app.js`), lưu **fan-out** ghi cả 2 store qua `save_strategy_input` (`webapp/business.py`) → downstream chưa đổi (tương thích ngược). P2 = dọn nợ do fan-out để lại.

---

## TASK R2-P2A — Xoá code Spine cũ đã CHẾT (rủi ro thấp, làm trước)
Sau P1b, các hàm/handler Spine rời KHÔNG còn được render/gọi. Xoá để đỡ rối. **GIỮ `spineState()`** (vẫn dùng bởi `strategyForm`).

**Xoá ở `web/app.js`:**
- `function spineBand()` (~L1870) — không còn render (đã gỡ khỏi dossier + strategy).
- `function spineCollapsible()` (~L1863) — không còn ai gọi (đã bỏ `_spineTop`).
- `function _spineSync()` (~L1812) — chỉ handler `spine-save` gọi.
- handler `if (act === 'spine-save')` (~L4048) + nút `data-act="spine-save"` (nằm trong `spineBand`, chết theo).

**Deprecate ở backend/api (chỉ dead FE gọi — xác nhận bằng grep trước khi xoá):**
- `save_spine` (`business.py` ~L470) + route `POST /api/biz/spine/save` (`api.py` ~L341/633) — FE chỉ gọi ở handler `spine-save` (đang xoá).
- `save_bet` (`business.py` ~L1901) + route `POST /api/biz/bet/save` (`api.py` ~L265/623) — `run-strategize-bet` đã chuyển sang `strategy-input/save`.
- **GIỮ**: `gen_bet_options` + `BET_CATEGORIES` + `bizBetCategories/bizBetOptions` (chips vẫn dùng trong `strategyForm` qua `betForm(['price'])`).

**Cách làm an toàn:** trước mỗi lần xoá, `grep -rn "<tên hàm>"` toàn repo (web/ + webapp/) xác nhận 0 caller khác. `node --check` + `py_compile` + Playwright smoke trang `#strategy` (form gộp render, lưu/lập chạy, 0 pageerror) + toàn bộ `tests/` PASS.

## TASK R2-P2B — (TUỲ CHỌN, lớn hơn) 1 nguồn thật, bỏ fan-out
Hiện `save_strategy_input` ghi CẢ `bet_choices` + `spine` (trùng dữ liệu tệp/định vị/giá). P2B = gom về **1 store** rồi rewire consumer.

**Consumer hiện tại (phải rewire nếu đổi store):**
- `bet_choices` đọc ở: synthesis `business.py` ~L3430 · playbook/khác ~L4716, ~L5016.
- `spine` đọc ở: `_spine_anchor` (`business.py` ~L3273), gọi tại ~L1158, ~L1505, ~L2088, ~L4297.
- biz_data expose: `bizSpine` (~L330) · `bizBetChoices` (~L348).

**Hướng gợi ý:** tạo `intake_extra.strategy` hợp nhất (market/channel/segment/positioning{alt,diff,statement,price_posture}/growth_focus/stage/objective/constraint). `save_strategy_input` chỉ ghi store này. Rewire synthesis/playbook + `_spine_anchor` đọc từ `strategy` (adapter đọc cả `bet_choices`/`spine` cũ để **migrate mềm** — không vỡ user cũ). Bỏ dần fan-out.
**Cân nhắc:** lợi ích chủ yếu là gọn code; rủi ro chạm synthesis/anchor (path lõi). Chỉ làm khi có thời gian + test kỹ. Nếu không, **P2A là đủ** để hết rối.

---

## BACKLOG khác (từ các phiên trước — ghi để không mất)
- **Auth (D-002):** `pick_user_id` đang TIN client `?user_id=` — chưa xác thực (lỗ bảo mật). Hướng đề xuất: Supabase Auth, **viết brief trước**. Không test được trong sandbox (cần deploy). Ưu tiên cao.
- **Engine prompts (D-035/036/037/038):** cần LLM key → chỉ soi/tinh trên staging, không sandbox.
- **Fast-path (time-to-first-post):** cho ra bài nháp từ dữ liệu tối thiểu → dụ hoàn thiện Nền. Đã hoãn (không phải chiến lược, là activation UX).
- **Placeholder Spine còn ví dụ cà phê** (trong `strategyForm`/`spineState` defaults) — đổi sang trung tính (đa ngành). Nhỏ, gộp lúc rảnh.

## Tham chiếu nhanh
- FE 1 nguồn: `web/app.js` (SPA) · `web/data.js` (nav) · `web/styles.css`. Backend: `webapp/business.py` (logic) · `webapp/api.py` (routes).
- Tests R2: `tests/test_r2_strategy_input.py` (fan-out). Pattern test: stub `storage.v2` + `tools.llm_router`, drive hàm thật.
