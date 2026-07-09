# ROADMAP v2 — Marketing OS web (Max, AI CMO)

> **NGUỒN THẬT DUY NHẤT** cho "làm gì tiếp" (thay bản S-xx cũ → `roadmap-v1.archive.md`).
> Tổ chức theo **4 TẦNG sản phẩm**, hoàn thiện **từ trên xuống**. Cập nhật: **2026-07-08**.
>
> **Phân vai tài liệu (hết chồng chéo):**
> - `roadmap.md` (file này) = **làm gì tiếp** — trạng thái theo tầng, thứ tự ưu tiên.
> - `DECISIONS.md` = **vì sao** — nhật ký ADR (D-xxx), không xoá, chỉ tra cứu lý do.
> - `notes-todo.md` = **backlog bug lẻ** (N-xx) — mỗi mục đã map vào 1 tầng bên dưới; khi làm xong tick ở đây.
> - `docs/cmo/00-PLAN.md` = **khung chủ** (6 miền CMO + Strategy Spine) — nguồn khung chính thức.
> - `product-journey-4-tang.md` = **chi tiết triển khai D4 Content + lớp Nghiên cứu** (KHÔNG phải khung tổng).
>
> **Ký hiệu:** ✅ xong & tin chạy · ✅? khai xong **cần VERIFY** (mâu thuẫn tài liệu / chưa test Railway) ·
> ⚠️ một phần · ⬜ chưa · ⏸️ cất theo Vision A · ✗ thiếu hẳn.

> 🔀 **CHUYỂN KHUNG (D-049/D-050, 2026-07-09):** khung sản phẩm đã chốt **"6 miền CMO"** (`docs/cmo/00-PLAN.md`)
> làm **KHUNG CHỦ**, thay "4 tầng nội dung". 4 tầng (file này) = triển khai **D4 Content + chạm D6**;
> **bước Nghiên cứu KHÔNG mất** (thành lớp grounding nuôi Strategy Spine).
> **Đã HỢP NHẤT (D-050):** 2 luồng gộp về **1 cây duy nhất** (nhánh tích hợp `feature/consolidate`, sau merge = `main`)
> — file này nằm CÙNG `docs/cmo/`. Việc R-1 verify · N-xx · D-048 ScrapeCreators đã rã vào khung 6 miền.
> roadmap này = backlog thực thi **D4 Content + lớp Nghiên cứu-grounding** trong khung đó. Chi tiết 7 quyết định:
> `DECISIONS.md D-049` + `product-reconcile-2026-07-09.md`. ✅ Hợp nhất 2 nhánh đã thực thi (2026-07-09).

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
| ① Tâm lý / Nghiên cứu | Research T1-T3 web-owned (`research_web`) | ✅? | **Lô F chưa verify Railway (R-1)** *(N-12 ✅)* |
| ② Chiến lược | Gate wedge/USP · Synthesis T4 · Playbook T5 · Thông điệp · Đặt cược 5 nhóm | ✅ | N-08 (đánh giá, chờ R-1) · **✗ Keyword/Demand** *(N-07b/N-16 ✅)* |
| ③ Sáng tạo | 6 dạng nội dung · Occasion M1.1 · Retention M2.1 · Repurpose | ✅ | *(hết nợ bug — N-18/N-17b ✅; tinh chỉnh naming 4 tuyến tuỳ chọn)* |
| ④ Phân phối & Đo | Nhịp nền · Lịch 2-track M1.2 · Cảnh báo brand/đơn | ⚠️ | **✗ auto-pull đo-học (Lô I+)** · S-22 kéo-thả · ✗ A/B |
| ⑤ Nền tảng & UX (cross-cut) | Render output · Doc-reader · Trạng thái task | ⚠️ | **N-02** · D-042 *(N-01/05/06/09/10/13/19/04b ✅ · standalone khai tử D-047)* |

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
| N-12 cắt output | ✅ **ĐÃ XONG** *(R-0 đọc nhầm docstring)* | Code `llm_router.py:297` **đã** `min(4000,25%)` → research `mx=16000` thinking 4000 → output ~12000. Chỉ docstring lệch → đã sửa 2026-07-08 |
| N-19 `<br>` raw | ✅ **ĐÃ XONG** (2026-07-08) | `inline()` `app.js:182` un-escape `&lt;br&gt;`→`<br>`; test node pass |
| N-04b JSON posmap trong `<p>` | ✅ **ĐÃ XONG** (2026-07-08) | đoạn văn JSON pos-map không fence → route sang `<pre>` cho `enhancePosMaps` (render/gỡ); test node pass |
| N-07 / N-07b | ✅ **ĐÃ XONG** *(R-0 báo nhầm "badge chưa")* | cờ lệch `business.py:252` · ràng synth-id `:3539` · badge + nút regen `app.js:1083` · `regen_playbook` `:3546` |
| N-17b bài đọc playbook | ✅ **ĐÃ XONG** *(R-0 báo nhầm)* | sinh bài inject `tactical_playbook`+synthesis làm nền ngầm `business.py:2918-2926` |
| N-18 redesign #occasion | ✅ **PHẦN LỚN** *(R-0 báo nhầm "legacy rối")* | `app.js:1099` hub móng+spike (D-040), gỡ chồng chéo, tách nhịp/thông điệp ra 2 trang. Còn tinh chỉnh naming 4 tuyến = tuỳ chọn |

> ⚠️ **Đính chính R-0 (2026-07-08, sau khi founder chất vấn):** bản R-0 đầu đọc comment/docstring nên
> báo NHẦM 4 mục trên là "mở/một phần" trong khi đã xong. Re-audit bằng đọc implementation → **backlog
> N-xx thực chất đã sạch**, chỉ còn N-02 (cần soi mắt Railway) + N-08 (chờ R-1). Phần còn lại của roadmap
> là TÍNH NĂNG mới (Keyword/Demand, auto-pull đo-học), không phải bug.
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
*(✅ đã xong ở tầng này: N-11 tiếng Việt `business.py:1562` · N-14 patch fallback `business.py:3834` ·
N-12 thinking budget `llm_router.py:297` `min(4000,25%)` → output ~12000, hết cụt (R-0 báo nhầm là chưa —
thực ra code đã sửa, chỉ docstring lệch; đã sửa docstring 2026-07-08).)*

---

## ② TẦNG CHIẾN LƯỢC

**Đã có:** GATE 2-phase chọn wedge + USP trên data thật (D-041) · Đặt cược 5 nhóm (S-05) · Synthesis T4
mạch tích hợp cascade Playing-to-Win + USP/SAVE (D-038B) · Tactical Playbook T5 Segment→Phễu (D-031) hiện
tab riêng (D-038A) · 🏛️ Messaging House · SWOT+TOWS đúng tầng, hết cụt (D-037b) · TAM/SAM/SOM số thật (D-034#2).

**Còn nợ (thứ tự):**
1. **✗ Bản đồ Cầu & Sự chú ý (đa nguồn)** — mở rộng "Keyword/Demand (search intent)" mà product-journey ghi.
   Ở VN cầu sống trên social > Google → không chỉ search; gồm 4 bề mặt: Google · TikTok · FB Ad Library
   (đối thủ) · Comment/review. **Nguồn data thật = ScrapeCreators** (1 key, đã tra full endpoint →
   `references/scrapecreators-api.md`). Kiến trúc: ScrapeCreators (mắt) → LLM (não) → bám SỐ THẬT, bớt
   "(ước tính)". v1 = TikTok + FB Ad Library; v2 = Google volume (DataForSEO). 📝 **spec `slices/S2-demand-map.md` + D-048** (2026-07-08, chờ founder chốt 4 câu hỏi mở: độ sâu v1 · cap credit · comment v1/v1.1 · đếm credit).
   - **Đồng thời nâng grounding T1-T3:** audit đã map chỗ "khát" data đối thủ → endpoint (xem
     `references/scrapecreators-api.md` §4). Competitor (T1) là nơi tiêu thụ chính — bơm kết quả vào block
     "DỮ LIỆU GROUNDED" của prompt (không phải sửa prompt). Market/customer/pricing hưởng lợi thêm.
2. **N-08 — chất lượng Playbook "hơi kém".** Rà: (a) prompt `_TAC_SYSTEM` chung chung? (b) upstream research
   mỏng → garbage-in. Làm SAU R-1 (research đủ trước rồi mới phán prompt). *(đánh giá, không phải bug binary.)*
   → (a) **đã vá cứng** trong prompt (`_TAC_SYSTEM` rule 8b nói thẳng N-08: cấm placeholder, kênh đích danh,
   ngưỡng test so sánh được). → (b) **ScrapeCreators grounding (mục 1) trực tiếp trị**: research dày → playbook bớt mỏng.
3. **🆕 N-20 (nghi, chờ R-1) — token budget Synthesis=3200/Playbook=4000 có vẻ BÓP** (research dùng 16-22K).
   Synthesis→Gemini Pro (thinking ăn vào output) chỉ ~2.240 token cho 8 mục. **Nghi gốc thật của N-08 độc lập
   với research.** Soi mắt khi R-1; nếu cụt/nén → fix rẻ nâng max_tokens (3200→6000 / 4000→7000). ĐỪNG sửa mù.

*(✅ đã xong: N-16 đặt cược sắc (`business.py:1621`) · **N-07/N-07b** badge+regen Playbook đầy đủ (`business.py:252/3539`, `app.js:1083`).)*

---

## ③ TẦNG SÁNG TẠO

**Đã có:** 6 dạng nội dung (mỗi dạng tự mang vai trò phễu) · Gen bài hook×góc bám Playbook · Bản đồ phễu×kênh ·
Repurpose đa kênh/video/UGC · **M1.1 Occasion** (D-043/044: wizard chọn dịp→lever→brief SMART→lưu) ·
**M2.1 Retention/Winback** cẩm nang if-then (D-045).

**Còn nợ:** — ✅ tầng này **HẾT NỢ BUG** (N-18, N-17b đã xử, xem dưới).
- *(tuỳ chọn, không gấp)* tinh chỉnh trang #occasion cho khớp hẳn naming 4 tuyến (Khai sáng/Tin cậy/Chuyển
  hoá/Lan toả) nếu muốn — hiện đã là hub móng+spike gọn (D-040), không còn "rối legacy".

*(✅ đã xong: **N-18** trang #occasion đã redesign móng+spike, gỡ chồng chéo (`app.js:1099`, D-040) ·
**N-17b** sinh bài đọc CẢ `tactical_playbook`+synthesis làm nền ngầm (`business.py:2918`).)*

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

> ✅ **R-0 XONG (2 vòng, 2026-07-08):** vòng 1 sơ sài (đọc comment → báo nhầm N-12/07b/17b/18); vòng 2
> re-audit đọc implementation → đính chính. Kết luận: **N-xx gần như sạch**, chỉ N-02 + N-08 còn lại.

**Render output** (dùng chung `renderAIContent` — fix 1 lần áp mọi trang) — ✅ **HẾT NỢ:**
- ✅ **N-09** heading `####` lồng trong bullet — nâng thành heading (`app.js:192`).
- ✅ **N-13** bảng rộng — bọc `.tbl-wrap` cuộn ngang (`app.js:211/380`).
- ✅ **N-19** `<br>` raw trong ô bảng — un-escape `&lt;br&gt;`→`<br>` (`inline()` `app.js:182`, 2026-07-08).
- ✅ **N-04b** JSON pos-map không fence — route sang `<pre>` cho `enhancePosMaps` xử (`app.js`, 2026-07-08).

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

> **CHỐT (2026-07-08 sau re-audit):** backlog **N-xx bug đã sạch**. Việc còn lại KHÔNG phải "vá nợ" nữa
> mà là **verify + tính năng mới**. Đừng đi fix lại N-01…N-19 (đã xong hết trừ N-02/N-08).

1. **🔴 R-1** — verify Lô F research trên Railway (chạy thật 1 business ngách). **← việc kế tiếp, THỦ CÔNG (founder bấm nút), tôi không chạy LLM trong sandbox được.**
2. **N-02** — soi mắt layout re-run trên Railway (song song R-1). N-08 — đánh giá chất lượng Playbook SAU khi R-1 cho thấy research đủ.
3. **Tính năng tầng ②** — Keyword / Demand (search intent) — gap thật còn thiếu.
4. **Tính năng tầng ④** — auto-pull đo-học (Lô I+) khi M0+M1 vững → S-22 kéo-thả.
5. *(ngoài đợt)* A/B test (④) · **Auth + Billing (M4)**.

## ❓ Câu hỏi mở (chờ founder chốt)
*(Trống — standalone đã chốt khai tử D-047; N-12 đã xong.)*

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
