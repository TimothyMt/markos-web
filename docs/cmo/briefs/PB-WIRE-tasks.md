# PB-WIRE — task cắt nhỏ cho Cline (companion của brief)

> Brief gốc (spec + quyết định đã chốt): [`playbook-artifact-wiring.md`](playbook-artifact-wiring.md).
> File này CẮT brief thành 6 task nhỏ (T1–T6) gộp 3 PR, để làm & review từng bước.
> Đọc brief gốc trước — file này KHÔNG lặp lại lý do/quyết định, chỉ là bảng thi công.

## Bất biến (nhắc lại — vi phạm = fail cổng)
- **KHÔNG đổi schema DB** → dữ liệu mới vào `intake_extra`.
- Playbook dừng ở **tầng ② (góc đánh)**, KHÔNG sinh hook/câu chữ chính thức.
- Mọi đường **degrade phải êm, KHÔNG crash, KHÔNG nút chết** (thiếu struct → hành vi cũ).
- 1 function = 1 commit. Push → mở PR (`base: staging`) bằng `gh pr create`, **KHÔNG tự merge**. Chờ Claude review PASS.

## Verify (máy Windows này)
- Dùng `python` — **KHÔNG phải `python3`** (Windows không có alias đó).
- Backend: `python -c "import webapp.business, webapp.api"`
- FE nếu đụng: `node --check web/app.js`
- Test: `test_playbook_struct` (viết ở T6).

---

## PR-A — Playbook producer: hạ độ cao + emit JSON (`webapp/business.py`)

### T1 — Hạ độ cao `_TAC_SYSTEM` (`business.py:3752`)
- Sửa luật **#3, #7, #8b**: mỗi mũi tactic xuống tới **góc đánh (territory) + kênh đích danh + khung test + KPI**.
  **Bỏ** ép "COPY MẪU (câu quote dùng ngay)" / "hook thật KHÔNG placeholder".
- Cho phép **1 ví dụ minh hoạ / Hướng**, bắt buộc **dán nhãn rõ**: "ví dụ cho dễ hình dung — KHÔNG phải bản chính thức" (option B).
- ⚠️ **Bug đã soi (hội đồng 2026-07-11):** bản working tree hiện tại luật **#7 còn sót** cụm
  *"(vẫn giữ **copy mẫu** + khung test + KPI)"* (`business.py:~3777`) — đá nhau với luật #3 mới.
  Sửa thành *"(vẫn giữ góc đánh + khung test + KPI)"*.
- **Thêm luật COMPLIANCE** (Q-C, chốt founder 2026-07-11 — soi từ output thật: playbook đề xuất
  "tài khoản seeding" + ảnh before-after da liễu không một chữ cảnh báo): *tactic phải hợp chính sách
  nền tảng (Meta/TikTok…) + pháp lý ngành nhạy cảm (y tế/mỹ phẩm/tài chính); seeding = khách thật
  hoặc có disclose, TUYỆT ĐỐI không dựng review giả; ngành nhạy cảm cẩn trọng ảnh before-after.*
- **Done:** grep prompt không còn chuỗi "copy mẫu"/"hook thật"; có luật compliance; markdown vẫn giữ chất người-đọc.

### T2 — Thêm block emit JSON vào `_TAC_SYSTEM` (cùng file)
- Cuối bài, yêu cầu model in **1 khối JSON `playbook_struct`** đúng schema Bước 0 của brief:
  `segments[] → {name, archetype, is_wedge, insight, tiers{tofu[],mofu[],bofu[]}}`,
  mỗi mũi = `{huong, territory, tows, channels[], test, cut, kpis[], example}`.
- **Field `insight` segment-level** (Q-B, chốt founder 2026-07-11): 1-2 câu nén từ 🧠 Insight cốt lõi —
  phần hồn của tệp (soi output thật: insight là đoạn hay nhất bài, schema cũ đánh rơi → downstream
  chỉ nhận territory khô, bài đúng góc nhưng trật tinh thần).
- **Example `cut` trong schema đổi sang TƯƠNG ĐỐI** (Q-A, chốt founder 2026-07-11): vd
  `"cut": "sau 7 ngày, biến thể thắng ≥1.5× CTR biến thể thua"`. Kèm mô tả: *ngưỡng go/kill ưu tiên
  dạng SO SÁNH; số tuyệt đối bắt buộc dán nhãn "ngưỡng giả định — chỉnh theo baseline thật"*
  (soi output thật: model tự bịa "Watch-through>30%", "Open rate>40%" không baseline — example cũ
  còn dạy nó bịa thêm).
- **JSON in COMPACT (minified, không pretty-print, không fence)** — tiết kiệm token + khó đứt đuôi
  (chốt founder 2026-07-11). Schema mẫu trong prompt vẫn được viết pretty cho model đọc,
  nhưng kèm lệnh "IN RA dạng nén 1 dòng".
- Thêm luật ưu tiên: **khối JSON là BẮT BUỘC** — nếu sắp hết chỗ, RÚT GỌN markdown,
  **TUYỆT ĐỐI không cắt/bỏ khối JSON** (thứ nằm cuối output chết đầu tiên khi cạn token).
- Thêm định nghĩa chặn hook-trá-hình vào mô tả `territory`: *territory = mệnh đề MÔ TẢ lãnh địa/góc
  (nói VỀ nội dung), KHÔNG phải câu nói VỚI khách hàng* (chốt founder 2026-07-11).
- **Done:** gen thử playbook → cuối output có khối JSON nén parse được; territory không phải câu hook.

### T3 — Parse + lưu `playbook_struct` trong `_gen_playbook` (`business.py:3794`)
- **Tăng `max_tokens` router_call trong `_gen_playbook` 4000 → 10000** (chốt founder 2026-07-11 —
  chống JSON đứt đuôi; giữ nguyên luật "rút gọn markdown" để bài không phình vô tội vạ).
- Sau khi có `tactical` (dòng ~3851): tách khối JSON khỏi markdown, lưu `extra["playbook_struct"]`.
  Markdown vẫn `insert_skill_run("tactical_playbook", …)` như cũ.
- ⚠️ **Repo CHƯA có helper tách JSON khỏi đuôi markdown** (các chỗ hiện có — funnel_map, tracks… —
  đều là output JSON-thuần strip fence). Tự viết extractor: tìm khối `{…}` **cân bằng ngoặc** cuối bài;
  tolerate cả trường hợp model lỡ bọc ```` ```json ```` dù đã cấm.
- **Validate 2 mức** (chốt founder 2026-07-11): **NGHIÊM với segment wedge** (`is_wedge=true`: đủ 3 tầng,
  mỗi Hướng đủ khoá bắt buộc) — **LỎNG với tệp phụ** (thiếu tầng/khoá → giữ phần có, không vứt cả struct).
- **Làm sạch markdown ≠ validate struct** (chốt founder 2026-07-11): strip best-effort khối JSON-đuôi
  khỏi markdown TRƯỚC khi lưu **kể cả khi parse fail** — user không bao giờ thấy JSON thô trên UI.
- **Versioned theo `playbook_synth_id`** (đã set ở dòng ~3858) — regen playbook → regen struct cùng id.
- **Degrade:** parse fail/thiếu → KHÔNG lưu struct, KHÔNG crash; **`logger.warning` khi parse fail**
  (đo được tỉ lệ rụng — degrade êm nhưng không được degrade MÙ).
- **Done:** chạy strategy → `intake_extra.playbook_struct` có, khớp `playbook_synth_id`;
  `bizPlaybookStale` (`business.py:317`) vẫn đúng; markdown lưu ra KHÔNG chứa JSON thô.

---

## PR-B — Nối góc đánh xuống sản xuất bài (`webapp/business.py`)

> ⛔ **TẠM DỪNG (founder chốt 2026-07-11) — KHÔNG code T4/T5 dưới đây.**
> Kiến trúc mới `CHAIN-V2-KIENTRUC.md` thay mối nối này: bài sinh từ THẺ calendar, thẻ sinh từ
> funnel-map-của-key-idea vốn đã mang góc đánh. PR-A (T1–T3) vẫn giữ nguyên giá trị.

### T4 — Helper map slot → (tier, is_wedge) ⚠️ SEAM KHÓ — HỎI nếu mơ hồ
- `gen_calendar_post` (`business.py:3142`, gọi từ `api.py:186`) **không nhận tầng phễu tường minh**.
  Gần nhất: `track_role` (Khai sáng/Tin cậy/Chuyển hoá/Lan toả) · `phase` · `objective` · `funnel_map`.
- Viết helper thuần: `(track_role/phase/objective, playbook_struct) → Hướng khớp theo TẦNG PHỄU + wedge`.
  **Match theo TẦNG PHỄU + wedge, KHÔNG theo tên Hướng** (tên trôi mỗi lần gen).
- Ứng viên map: Khai sáng≈tofu · Tin cậy≈mofu · Chuyển hoá≈bofu · Lan toả≈tofu/cross.
- **Nếu cách suy tầng phễu không chắc → DỪNG, hỏi founder** (brief cho phép), ĐỪNG đoán liều.

### T5 — Bơm góc đánh vào `gen_calendar_post` (quanh `strat_anchor` dòng ~3230)
- Dùng helper T4: đọc `playbook_struct` → chèn **`territory + channels + huong` của Hướng khớp
  + `insight` (segment-level, Q-B)** vào prompt như *"góc đánh tham chiếu — bám góc này + tinh thần
  insight này, TỰ viết câu chữ bằng giọng Thông điệp"*.
- 🔴 **KHÔNG** chèn `example` làm hook. Hook vẫn do model viết mới, bám `_messaging_anchor_from`.
- **Degrade:** thiếu struct → giữ nguyên hành vi cũ (khối `strat_anchor` hiện tại).
- **Done:** slot TOFU tệp wedge → payload/log CÓ `territory+channels`, KHÔNG có `example`;
  playbook cũ (không struct) → chạy như cũ, không lỗi.

---

## PR-C — Khoá cut/KPI cho D6 + nghiệm thu

### T6 — Đảm bảo `cut/kpis` truy được + test
- Xác nhận `cut`+`kpis` đọc lại được bằng khoá từ `playbook_struct`.
  *(Vòng đo thật/UI = slice D6 riêng — NON-GOAL ở đây, chỉ đảm bảo khoá tồn tại.)*
- Viết `test_playbook_struct`:
  1. parse struct đủ segment × 3 tầng, có `territory/channels/cut/kpis`;
  2. thiếu struct → `gen_calendar_post` không lỗi (degrade);
  3. `cut/kpis` truy được bằng khoá.
- Chạy: `python -c "import webapp.business, webapp.api"` + `test_playbook_struct` pass.

---

## Acceptance (map thẳng brief gốc)
- [ ] `intake_extra.playbook_struct` parse ra; segment wedge đủ 3 tầng, có `insight` +
      `territory/channels/cut/kpis` (tệp phụ cho phép thiếu — validate 2 mức). *(T3)*
- [ ] Markdown lưu ra KHÔNG chứa JSON thô, kể cả khi parse fail; parse fail có `logger.warning`. *(T3)*
- [ ] Markdown playbook KHÔNG còn "Copy mẫu (dùng ngay)" làm chuẩn; `example` (nếu có) kèm nhãn "ví dụ minh hoạ". *(T1)*
- [ ] `gen_calendar_post` slot TOFU tệp wedge → prompt CÓ `territory+channels`, KHÔNG chèn `example` làm hook. *(T5)*
- [ ] Thiếu struct (playbook cũ) → calendar vẫn chạy, không lỗi. *(T3, T5)*
- [ ] `cut+kpis` truy được bằng khoá (test đọc lại). *(T6)*
- [ ] Import backend pass; `test_playbook_struct` pass. *(T6)*

## Thứ tự
T1 → T2 → T3 (PR-A) → T4 → T5 (PR-B) → T6 (PR-C). Mỗi PR chờ cổng review PASS mới sang PR sau.
