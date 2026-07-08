# ROADMAP v2 — Marketing OS web (Max, AI CMO)

> **NGUỒN THẬT DUY NHẤT** cho "làm gì tiếp" (thay bản S-xx cũ → `roadmap-v1.archive.md`).
> Tổ chức theo **4 TẦNG sản phẩm**, hoàn thiện **từ trên xuống**. Cập nhật: **2026-07-08**.
>
> **Phân vai tài liệu (hết chồng chéo):**
> - `roadmap.md` (file này) = **làm gì tiếp** — trạng thái theo tầng, thứ tự ưu tiên.
> - `DECISIONS.md` = **vì sao** — nhật ký ADR (D-xxx), không xoá, chỉ tra cứu lý do.
> - `notes-todo.md` = **backlog bug lẻ** (N-xx) — mỗi mục đã map vào 1 tầng bên dưới; khi làm xong tick ở đây.
> - `product-journey-4-tang.md` = **khung sản phẩm** (bất biến) — 4 tầng + triết lý.
>
> **Ký hiệu:** ✅ xong & tin chạy · ✅? khai xong **cần VERIFY** (mâu thuẫn tài liệu / chưa test Railway) ·
> ⚠️ một phần · ⬜ chưa · ⏸️ cất theo Vision A · ✗ thiếu hẳn.

---

## North-star & phạm vi đợt này

**North-star:** Biến founder Việt (không có CMO) thành "có-CMO": đi 1 mạch
**Hồ sơ → Chiến lược → Nội dung → Lịch → Deliverable** — Max làm, founder duyệt/sửa. Web-owned.

**Luồng chủ đạo — VISION A** (founder chốt 2026-06-25):
```
Intake → Research T1-T3 → 🚪 GATE (chọn wedge + USP trên data thật, D-041)
  → ĐẶT CƯỢC 5 nhóm (Thị trường·Tệp·Định vị·Giá·Kênh)
  → T4 Synthesis + T5 Playbook (bám đặt cược) → 🏛️ Thông điệp
  → 6 dạng nội dung (bám Playbook ngầm) → Lịch 2-track (nền + đợt) → đo-học vòng lại.
```

**PHẠM VI ĐỢT NÀY (founder chốt 2026-07-08): chốt M0 + M1 CHẠY THẬT.**
- Verify pipeline thật trên Railway (sandbox không chạy LLM) — nợ nghiệm thu lớn nhất.
- KHÔNG mở auth/billing (D-002/D-014 vẫn nợ — để milestone sau, xem cuối file).
- Nguyên tắc "từ trên xuống": **hoàn thiện & test vững tầng ① trước khi dồn sức tầng dưới.**

---

## Bảng tổng — trạng thái 4 tầng

| Tầng | Khối chính | TT | Nợ mở (map notes/decisions) |
|---|---|---|---|
| ① Tâm lý / Nghiên cứu | Research T1-T3 web-owned (`research_web`) | ✅? | **Lô F chưa verify Railway (R-1)** · **N-12 (cắt output — CHƯA)** |
| ② Chiến lược | Gate wedge/USP · Synthesis T4 · Playbook T5 · Thông điệp · Đặt cược 5 nhóm | ✅ | N-07b · N-08 · **✗ Keyword/Demand** *(N-16 ✅)* |
| ③ Sáng tạo | 6 dạng nội dung · Occasion M1.1 · Retention M2.1 · Repurpose | ⚠️ | N-18 (trang #occasion rối) · N-17b (bài đọc playbook) |
| ④ Phân phối & Đo | Nhịp nền · Lịch 2-track M1.2 · Cảnh báo brand/đơn | ⚠️ | **✗ auto-pull đo-học (Lô I+)** · S-22 kéo-thả · ✗ A/B |
| ⑤ Nền tảng & UX (cross-cut) | Render output · Doc-reader · Trạng thái task | ⚠️ | **N-19 · N-04b · N-02** · D-042 *(N-01/05/06/09/10/13 ✅ · standalone đã khai tử D-047)* |

> ✅ **R-0 ĐÃ CHẠY (đối chiếu code, 2026-07-08).** Header notes-todo phần lớn ĐÚNG, trừ **N-12 khai xong
> nhưng CHƯA** + phát hiện **standalone lệch bản**. Chi tiết ở bảng "Kết quả R-0" ngay dưới.

### Kết quả R-0 — đối chiếu code (2026-07-08)
| Note | Verdict | Bằng chứng |
|---|---|---|
| N-01 repoint version | ✅ ĐÚNG-XONG | `business.py:584` re-stamp version, không đẻ row mới |
| N-05 bỏ tracked mock | ✅ | `app.js:885` gỡ khỏi competitor T1-T3 |
| N-06 timeout strategize | ✅ | `business.py:4081/4114` `wait_for(…,300)` + regen 240s; status qua SSE/toast |
| N-07 regen playbook | ⚠️ một phần | `regen_playbook` + timeout có (`business.py:4094`); **badge lệch-version chưa xác nhận** → N-07b mở |
| N-09 `####` trong bullet | ✅ | `app.js:192` strip bullet-prefix → `app.js:226` render heading |
| N-10 scroll reset | ✅ | `app.js:2278-2280` main+window+#view |
| N-11 tiếng Việt tự nhiên | ✅ | `business.py:1562` `_RW` luật TV chèn vào prompt web-owned |
| N-13 bảng cuộn ngang | ✅ | `app.js:211` + `380` bọc `.tbl-wrap` |
| N-14 patch fallback | ✅ | `business.py:3834` PATCH_ASK → `_revise_full_doc` |
| N-16 đặt cược sắc hơn | ✅ | `business.py:1621` OPS_BRIEF + SAVE + archetype + grounded (bỏ tier mini) |
| Lô F research web-owned | ✅ code / ⚠️ chưa verify | `research_web` `business.py:761` + `_RW_ANTIFAB` `:617`; **CẦN R-1 chạy thật** |
| **N-12 cắt output** | ❌ **CHƯA** (header khai nhầm) | `_calc_thinking_budget` **KHÔNG đổi**; research `mx=16000` → thinking `min(8000,40%)=6400` → output ~9600 vẫn cụt. Chỉ SWOT (`mx=22000`) an toàn |
| **N-19 `<br>` raw** | ❌ CHƯA | `inline()` `app.js:181` thiếu un-escape `&lt;br&gt;` |
| **N-04b JSON posmap trong `<p>`** | ❌ CHƯA (N-04 `<pre>` xong) | `enhancePosMaps` `app.js:364` chỉ quét `pre`, không quét `<p>` |
| N-02 UI bóp khi re-run | ❓ chưa verify được tĩnh | CSS/layout — cần soi bằng mắt trên Railway |
| Standalone lệch bản | ✅ ĐÃ XỬ (D-047) | Phát hiện lệch → **xoá hẳn** `dashboard-standalone.html` + `build_standalone.py`; FE về 1 nguồn |

---

## ① TẦNG TÂM LÝ / NGHIÊN CỨU — *hoàn thiện TRƯỚC*

**Đã có:** Research T1-T3 viết lại **WEB-OWNED** (`research_web`, Lô F / commit R-1 scrub trên nhánh này):
5 skill prompt khoá scope riêng (competitor không lấn ICP/JTBD — N-03; research kết bằng *so-what*, KHÔNG
xếp roadmap — N-03b/D-036) + chống bịa số (kèm nguồn / "(ước tính)"; thiếu data → "_chưa đủ dữ liệu công
khai_" — N-15) + soát số trần trước khi lưu. `_execute` bỏ pipeline `agents/`. Engine cũ D-035 (psychology
T2 cắt scope) / D-036 (research bỏ roadmap) cũng đã sửa prompt.

**Còn nợ (thứ tự):**
1. **🔴 R-1 — VERIFY Lô F trên Railway.** Đây là mục đích cả nhánh `feature/research-scrub`. Chạy thật 1
   business ngách → kiểm: competitor không độn ICP/JTBD, research không đẻ Quick-win/Medium/Long, số đều
   có nguồn/"(ước tính)", thiếu data ghi "_chưa đủ_". *(chặn mọi việc tầng dưới — garbage-in.)*
2. **🔴 N-12 — output research bị CẮT giữa câu** (R-0 xác nhận **CHƯA fix**). `_calc_thinking_budget` không
   đổi → 4 skill research `mx=16000` bị thinking ăn 40% (`min(8000,40%)=6400`) → chữ thấy ~9600 vẫn cụt.
   Fix: giảm cap dải 5K–20K (vd `min(4000,25%)`) HOẶC nâng research `mx≥20000`. Verify chung R-1.

*(✅ đã xong ở tầng này: N-11 tiếng Việt tự nhiên `business.py:1562` · N-14 patch fallback `business.py:3834`.)*

---

## ② TẦNG CHIẾN LƯỢC

**Đã có:** GATE 2-phase chọn wedge + USP trên data thật (D-041) · Đặt cược 5 nhóm (S-05) · Synthesis T4
mạch tích hợp cascade Playing-to-Win + USP/SAVE (D-038B) · Tactical Playbook T5 Segment→Phễu (D-031) hiện
tab riêng (D-038A) · 🏛️ Messaging House · SWOT+TOWS đúng tầng, hết cụt (D-037b) · TAM/SAM/SOM số thật (D-034#2).

**Còn nợ (thứ tự):**
1. **✗ Keyword / Demand (search intent)** — **gap DUY NHẤT còn thiếu ở tầng 2** (product-journey). Thêm 1
   bước demand/search-intent feed vào Strategy. *(tính năng mới, không phải bug.)*
2. **N-07b — badge Playbook khi Synthesis đổi.** R-0: `regen_playbook` + timeout ĐÃ có; còn thiếu **badge
   "Playbook theo chiến lược cũ"** khi fingerprint synthesis lệch (`_strategy_fp`). Verify regen chạy đúng khi "Chốt chiến lược".
3. **N-08 — chất lượng Playbook "hơi kém".** Rà: (a) prompt `_TAC_SYSTEM` chung chung? (b) upstream research
   mỏng → garbage-in. Làm SAU R-1 (research đủ trước rồi mới phán prompt).

*(✅ đã xong: N-16 đặt cược sắc hơn — `gen_bet_options` OPS_BRIEF + SAVE + archetype + grounded, `business.py:1621`.)*

---

## ③ TẦNG SÁNG TẠO

**Đã có:** 6 dạng nội dung (mỗi dạng tự mang vai trò phễu) · Gen bài hook×góc bám Playbook · Bản đồ phễu×kênh ·
Repurpose đa kênh/video/UGC · **M1.1 Occasion** (D-043/044: wizard chọn dịp→lever→brief SMART→lưu) ·
**M2.1 Retention/Winback** cẩm nang if-then (D-045).

**Còn nợ (thứ tự):**
1. **N-18 — redesign trang #occasion "Tuyến nội dung".** Trang còn RỐI (legacy: pillars vs tuyến vs
   branding-campaign vs occasion chồng chéo). Dựng lại thành 4 tuyến (Khai sáng/Tin cậy/Chuyển hoá/Lan toả)
   bám playbook ngầm → nối lịch. Bỏ/gộp khối legacy. *(slice ~S-20/S-21, việc lớn nhất còn lại của M1.)*
2. **N-17b — khâu sinh tuyến/bài phải ĐỌC CẢ Playbook** (không chỉ synthesis). Founder chốt Playbook = nền
   ngầm; bài tự kế thừa dù user không mở tab. Gắn với N-07b (playbook refresh).

---

## ④ TẦNG PHÂN PHỐI & ĐO

**Đã có:** Nhịp nền (6 dạng × tần suất) · **Lịch 2-track M1.2** (D-046: occasion window→tuần + always-on từ
pillars + gen bài slot thật) · Cảnh báo cân bằng brand/đơn 60-40 (Binet&Field).

**Còn nợ (thứ tự):**
1. **✗ Đóng vòng ĐO-HỌC (auto-pull) — MỎ VÀNG lớn nhất** (Lô I+, đã hoãn). Nền `content_feedback` + kết nối
   FB Ads/ads_snapshots ĐÃ CÓ; cần map FB post id ↔ skill_run content → tự gọi `content_feedback` → Max chấm
   → tối ưu bài kế. Đây là thứ biến Max thành **hệ-thống-sống**. *(để sau khi M0+M1 vững — cần map id.)*
2. **S-22 — lịch kéo-thả** (nền M-E đã có). Đổi ngày/ô kéo-thả.
3. **✗ A/B test · engagement monitoring · syndication** — làm sau auto-pull.

---

## ⑤ NỀN TẢNG & UX (cross-cutting — chạy song song mọi tầng)

> **R-0 (làm NGAY, trước khi lên lịch): đối chiếu code chốt thật-giả** cho N-01/02/04b/05/06/09/10/13/19 —
> `notes-todo` khai xong nhưng chưa chắc. Đọc `app.js`/`business.py` xác nhận từng cái rồi tick.

**Render output** (dùng chung `renderAIContent` — fix 1 lần áp mọi trang):
- ✅ **N-09** heading `####` lồng trong bullet — ĐÃ nâng thành heading (`app.js:192`).
- ✅ **N-13** bảng rộng — ĐÃ bọc `.tbl-wrap` cuộn ngang (`app.js:211/380`).
- ⬜ **N-19** `<br>` hiện raw trong ô bảng → un-escape `&lt;br&gt;` sau `esc()` (`inline()` `app.js:181`). *(còn mở)*
- ⬜ **N-04b** khối JSON pos-map KHÔNG fence → gom vào `<p>` lòi JSON thô. `enhancePosMaps` mới quét `<pre>`; thêm nhánh quét `<p>` match `{…"yTop"/"items"…}` → gỡ. *(còn mở)*

**Doc-reader UX:**
- ✅ **N-01** repoint version — ĐÃ đúng (`business.py:584`, không đẻ row mới).
- ⬜ **N-02** layout bị bóp khi re-run (panel version history) — **chưa verify được tĩnh, cần soi mắt trên Railway.**
- ✅ **N-10** cuộn lên đầu khi chuyển trang — ĐÃ reset main+window+#view (`app.js:2278`).

**Trạng thái task & dọn:**
- ✅ **N-06 (= S-40)** timeout strategize (`business.py:4081`) + status realtime SSE/toast — ĐÃ có.
- ✅ **N-05** bỏ section tracked mock ở T1-T3 — ĐÃ gỡ (`app.js:885`).
- ✅ **Standalone — ĐÃ KHAI TỬ (D-047, 2026-07-08):** xoá `dashboard-standalone.html` + `build_standalone.py`,
  gỡ luật mirror khỏi CLAUDE.md/.clinerules/docs. **FE = 1 nguồn duy nhất, sửa thẳng, không mirror.**
- ⬜ **D-042** dọn code chết (`SKILL_TO_TASK`, `swotCell`, mock `M.personas/pricingTiers/competitors`) — defer, có test chặn.

---

## Thứ tự thực thi đề xuất (top-down)

0. ✅ **R-0 XONG** (đối chiếu code 2026-07-08 — xem "Kết quả R-0" ở tầng ⑤).
1. **🔴 R-1** — verify Lô F research trên Railway (chạy thật 1 business ngách). *Chặn mọi việc tầng dưới.*
2. **Tầng ①** — **N-12 (cắt output — chưa fix)** cùng lượt R-1. Nghiệm thu research đủ-sâu.
3. **Tầng ⑤ render** — **N-19 + N-04b** (2 cái còn mở, nhanh; N-09/N-13 đã xong).
4. **Tầng ②** — **N-07b badge** → N-08 (chất lượng, sau khi research đủ).
5. **Tầng ③** — N-18 (redesign #occasion) + N-17b (bài đọc playbook). *Việc lớn nhất của M1.*
6. **N-02** (soi mắt trên Railway) — verify layout re-run.
7. **Tầng ④** — auto-pull đo-học (Lô I+) khi M0+M1 đã vững → S-22 kéo-thả.
8. *(ngoài đợt)* Keyword/Demand (②) · A/B (④) · **Auth + Billing (M4)**.

## ❓ Câu hỏi mở (chờ founder chốt)
- **N-12:** giảm cap `_calc_thinking_budget` (ảnh hưởng dải giữa toàn hệ) hay chỉ nâng `mx` của 4 skill research lên ≥20K (khoanh vùng, an toàn hơn)?

*(✅ Đã chốt: standalone khai tử — D-047.)*

## 🧪 Quy tắc TEST (founder chốt 2026-06-25)
- **Test theo slice, không dồn:** xong 1 slice → deploy Railway test ngay.
- Viết vài **test thuần Python** cho phần logic (như reconciliation/topics/occasion/retention/calendar) để
  bắt "sửa mới hỏng cũ" mà không cần chạy full app.
- Verify FE: `node --check web/app.js`; backend: `python -c "import webapp.business, webapp.api"`.

---

## Ngoài phạm vi đợt này (milestone sau — nhắc để không quên)
- **M4 Auth + RLS** (D-002/D-014 — nợ, ⚠️ **chặn cứng** việc public dữ liệu thật đa user).
- **M4 Billing** + gating gói Starter/Pro/Agency (D-011/D-013).
- Agency multi-client, tối ưu Ads chuyên sâu (luồng c), tự host LLM.
- Dọn tàn dư GitHub Pages / `bot/` (D-033/D-042).
