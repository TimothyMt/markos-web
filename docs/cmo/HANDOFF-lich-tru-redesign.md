# HANDOFF — Thiết kế lại sợi Trụ → Lịch (tầng ②→④)

> **Dành cho phiên thiết kế sau.** Đây là brief ngữ cảnh, KHÔNG phải lệnh thi công.
> Mục tiêu: phiên sau đọc file này là bắt được mạch ngay, không phải đào lại code.
> Người viết (phiên trước) đã điều tra xong wiring hiện trạng — chép lại ở đây để khỏi re-derive.
> Số dòng có `≈` là gợi ý, **đã trôi thì grep theo tên hàm** (mỏ neo bền hơn số dòng).

---

## 0. Vì sao có file này

Founder (bạn) quyết **thiết kế lại** khúc Trụ→Lịch ở phiên khác, thay vì vá chắp vá bây giờ.
Phiên trước đang gỡ nợ chất lượng Luồng C thì chạm phải chỗ này và thấy: đây không phải bug
đơn lẻ để "sửa nhanh", mà là **2 mô hình trụ chồng lên nhau + 1 mìn ở cách đánh key lịch**.
Đúng bài để dừng lại, thiết kế tử tế, chứ không vá tiếp.

---

## 1. Đang ở đâu trên trục 4 tầng

```
① Nghiên cứu (T1–T5) → ② Chiến lược (Đặt cược → Thông điệp/TRỤ) → ③ Sáng tạo (6 dạng · Ma trận) → ④ Phân phối (LỊCH)
```

Khúc cần thiết kế lại = **đuôi ②→④**, KHÔNG đụng ① (nghiên cứu đã xong, đứng ngoài).
- **②** đẻ ra **trụ** (`messaging.pillars`, mỗi trụ = 1 *territory/lãnh địa nói*).
- **③** biến trụ thành **Ma trận** (`content_matrix` = trụ × tầng phễu × kênh).
- **④** rải Ma trận (hoặc Nhịp nền) thành **Lịch** — mỗi ô lịch có 1 `key` để lưu bài đã gen.

---

## 2. Trạng thái Luồng C khi bàn giao

| Nợ | Việc | Trạng thái |
|----|------|-----------|
| **C1** | Trang "Giọng & Tính cách" trùng ④ Thông điệp | ✅ **XONG** — khai tử, merge staging (PR #42) |
| **C2** | Mô hình trụ + key lịch (file này) | ⏸ **Gác để thiết kế lại** |
| **C3** | Rải bài lịch dày hơn (`distribute_grid_posts`) | ⏳ Chưa làm — xem §6 |

C2 và C3 **chồng địa bàn** (cùng đụng builder lịch), nên hợp lý gộp vào **một** phiên thiết kế.

---

## 3. Wiring THẬT của sợi Trụ → Lịch (đã điều tra, tin được)

### 3a. Mô hình trụ đang SỐNG = `messaging.pillars` (territory-based)
- Shape: `{icon, territory, angle, proof}` — chuẩn hoá ở `_norm_messaging` (business.py ≈3620).
- Producer: ② Thông điệp (web sinh thật). Đây là **nguồn trụ duy nhất còn sống**.
- Tiêu thụ:
  - `gen_content_matrix` (business.py:5341) đọc `messaging.pillars` (≈5361–5372) làm trụ cho Ma trận.
  - `tracks_view` (business.py:1807) đọc `messaging.pillars` territory.
  - `_build_rhythm_always` (business.py:2831) xoay vòng `messaging.pillars` territory.

### 3b. Mô hình trụ CHẾT (bãi legacy) = `campaign_plan.pillars` / `pillars_locked` / `_pillar_id`
- `save_pillars` (business.py:573) → ghi `intake_extra.pillars_locked` (shape `{id,name,role,funnel,cadence,...}`).
- `campaign_plan` (business.py:1161) → suy trụ từ Synthesis+Tactical, dùng `pillars_locked` nếu có.
- `_pillar_id` (business.py:2789) → `pid = p.id if p.id else "n_"+slug(p.name)[:12]` (đọc id/name, **không** territory).
- **UI chốt-trụ ĐÃ CHẾT**: `app.js` có handler `lock-pillars`(4758)/`unlock-pillars`(4770)/`regen-pillars`(4778)
  + đọc `.pillar-chk:checked`(4760) + 1 dòng CSS(styles.css:1241) — **NHƯNG không có renderer nào đẻ ra `.pillar-chk`**.
  Query luôn rỗng → handler chết lâm sàng.
- `_pillar_id` **không builder lịch sống nào gọi** — chỉ dùng cho `_normalize_saved` (migrate cũ) + degrade fallback.

> ⚠️ Nhãn nợ cũ ghi "bridge 2 mô hình trụ" đã **lỗi thời**: sau redesign B2 chỉ còn 1 model sống (3a)
> + 1 bãi rác (3b). Không cần "bridge" — cần **quyết dọn bãi tới đâu**.

### 3c. Builder lịch — degrade 3 tầng nguồn NỀN
`content_matrix` (B2.1) → `content_rhythm` → `pillars` (business.py ≈3241, nhánh chọn ≈3350–3365):
- Có `content_matrix` (≥1 ô) → `_build_matrix_always` (2923).
- Không, có `content_rhythm` (≥1 dạng bật) → `_build_rhythm_always` (2831).
- Không cả hai → fallback pillars cũ (degrade).

---

## 4. MÌN THẬT — "bài đã lưu biến mất" (khác nhãn cũ)

**Cơ chế** (đã đọc tận key):
- `_build_rhythm_always` (business.py:2862): `pid = f"rhy|{d['key']}|{terr}"` với `terr` = **territory chữ thô**
  → key ô lịch = `aw|rhy|<dạng>|<territory>|<w>|<d>`.
- `_build_matrix_always` (business.py:2939): `pid = "mx|"+slug(pillar)[:14]+"|"+tier`
  → key = `aw|mx|<slug(tên trụ)>|<tier>|<w>|<d>`.
- Bài đã gen lưu theo key này; render lịch dò lại bằng `idx_always.get((pid,w,d))` (2873 / 2955).

**Hậu quả**: Founder đổi tên/territory 1 trụ ở ② Thông điệp **SAU KHI** đã lưu bài lịch
→ builder sinh key mới (theo tên mới) → `idx_always` không khớp key cũ → **bài đã sửa mất khỏi UI**
(dữ liệu vẫn còn trong DB, chỉ mồ côi không hiện).

**Xếp loại**: edge-case *sửa-sau-khi-dựng*. **KHÔNG chặn launch** (đa số user không đổi tên trụ sau khi rải).
Nhưng là **nợ thiết kế thật** — key persist không nên bám chữ đổi-được.

**Hướng vá gợi ý** (để phiên thiết kế cân): cấp **id ổn định cho mỗi `messaging.pillar`** (giữ nguyên qua edit tên),
key lịch bám id thay vì territory-text, + **migrate mềm** key cũ (đọc được cả 2 dạng trong 1 thời gian).
→ Đụng `calendar_posts` đã lưu ⇒ **bắt buộc test Lớp 2 (data thật)** trước khi tin. Lớp 2 hiện đang gác.

---

## 5. Dọn bãi legacy (làm được ngay, KHÔNG đụng data lưu)

Nếu phiên thiết kế muốn thu gọn mặt bằng trước khi xây:
- **An toàn xoá**: UI chốt-trụ chết ở `app.js` — 3 handler `lock/unlock/regen-pillars` + reader `.pillar-chk`(4760)
  + CSS `.pillar-chk`(styles.css:1241). Không render → xoá không ảnh hưởng runtime.
- **Cân nhắc (không bắt buộc)**: route `/api/biz/pillars-lock` + `save_pillars` + đọc `pillars_locked` trong `campaign_plan`.
  Giữ lại nếu muốn chừa đường tương lai; xoá nếu quyết Model 3b chết hẳn.
- **GIỮ**: `_normalize_saved` + degrade fallback (còn cần cho bài cũ đã lưu).

---

## 6. C3 — rải bài lịch dày hơn (`distribute_grid_posts`, business.py:3071)

Nợ song song, cùng địa bàn ④. Yêu cầu (từ spec đã chốt, xem memory `calendar-post-distribution-logic`):
rải theo **window + lưới tầng×kênh → ngày** theo **trình tự phễu + neo cao điểm + nhịp + không dồn cục + delta**
(đừng rải bừa/đều tăm tắp). Phiên thiết kế nên xem C3 **cùng lúc** với việc đánh key ở §4 —
vì rải dày hơn = nhiều ô hơn = nhiều key hơn, quyết định key ổn định ở đây trả cổ tức luôn.

---

## 7. Ràng buộc BẤT DI (đọc kỹ trước khi thiết kế)

1. **KHÔNG đổi schema DB.** Mọi cấu hình mới → thêm key vào `intake_extra` (dict). Trụ id ổn định cũng phải sống trong `messaging.pillars` item, không thêm cột/bảng.
2. **Key lịch = hợp đồng persist.** Đổi format key = phải có **migration đọc-được-cả-2** + test data thật (Lớp 2). Không "đổi cứng rồi mong bài cũ tự khớp".
3. **Cổng kiểm mối nối** (`docs/cmo/WIRING.md`): mọi key đọc/ghi phải có producer + khớp tên/slug/kiểu 2 đầu + có đường degrade. Trụ-id là *derived-state mới* → nếu tự sinh phải kèm quy tắc ổn định (đừng để regen đổi id).
4. **Giữ chất lượng prompt bot** — `gen_content_matrix` tái dùng prompt agents; đừng thay bằng prompt tự chế mỏng.
5. Verify: `node --check web/app.js` + `python -c "import webapp.business, webapp.api"`. FE 1 nguồn (`web/app.js`), không mirror.

---

## 8. Câu hỏi mở cho phiên thiết kế (chốt trước khi code)

1. **Trụ-id**: sinh thế nào để ổn định qua edit tên? (uuid lúc tạo trụ? hash nội dung ban đầu? counter?) — phải sống được khi user regen Thông điệp.
2. **Model 3b**: xoá hẳn hay chừa? Nếu xoá → dọn luôn route + save_pillars ở §5.
3. **Migration key**: đọc-cả-2 trong bao lâu? Có backfill key cũ → id mới không, hay chỉ đọc lỏng?
4. **C3 + key**: thiết kế rải dày (§6) và key ổn định (§4) chung một nhịp hay tách?
5. **Nhịp vs Ma trận**: 2 builder (`_build_rhythm_always` vs `_build_matrix_always`) đánh key khác nhau (`rhy|territory` vs `mx|slug`) — có thống nhất một sơ đồ key không?

---

## 9. Mỏ neo tra cứu nhanh (grep theo tên, số dòng chỉ gợi ý)

| Thứ | Nơi | ≈dòng |
|-----|-----|-------|
| Chuẩn hoá messaging (nguồn trụ sống) | `webapp/business.py` `_norm_messaging` | 3620 |
| Ma trận từ trụ | `gen_content_matrix` | 5341 |
| Builder lịch NỀN (nhịp) — key `rhy\|territory` | `_build_rhythm_always` | 2831 (key 2862) |
| Builder lịch NỀN (ma trận) — key `mx\|slug` | `_build_matrix_always` | 2923 (key 2939) |
| Nhánh chọn nguồn NỀN (degrade 3 tầng) | (calendar builder) | 3350–3365 |
| Rải bài (C3) | `distribute_grid_posts` | 3071 |
| Bãi legacy — id trụ cũ | `_pillar_id` | 2789 |
| Bãi legacy — chốt trụ | `save_pillars` | 573 |
| Bãi legacy — campaign_plan | `campaign_plan` | 1161 |
| UI chốt-trụ CHẾT | `web/app.js` lock/unlock/regen-pillars | 4758–4785 |

---

*Ghi bởi phiên gỡ-nợ-C, 2026-07-23. Liên quan: `docs/cmo/LAUNCH-READINESS.md` (§ Luồng C), `docs/cmo/WIRING.md` (Hiến pháp mối nối), memory `calendar-post-distribution-logic` / `messaging-pillars-positioning-quality-debt` / `sanxuat-redesign-flow-wiring`.*
