# BRIEF FV3-1 — Tách Big Idea khỏi Chiến dịch (1 big idea → N chiến dịch)

> Đọc trước: `CLAUDE.md` · `AGENTS.md` · `docs/cmo/WIRING.md` · `docs/cmo/FLOW-V3-research-to-calendar.md` §2 & §6.
> Đây là **việc #1** của Flow V3. Slice này **ADDITIVE + IDEMPOTENT + KHÔNG phá lịch đang chạy**.
> Nhánh: cắt từ `staging`, tên `feature/fv3-big-ideas`. PR base = `staging`. **Không tự merge.**

## Mục tiêu (WHY — không phải HOW)
Hôm nay `intake_extra.key_ideas[]` gộp làm một: mỗi phần tử vừa là **big idea** (title/angle/source_ref)
vừa là **chiến dịch** (window/goal/funnel_map/focus_*). Vì gộp 1:1, **không chạy được 1 big idea qua nhiều
chiến dịch** (vd big idea "Tết không cần hoàn hảo" → 1 chiến dịch branding ToFu trên TikTok + 1 chiến dịch
chốt đơn BoFu trên Zalo → hôm nay founder phải nhân bản, 2 bản trôi khác nhau).

Slice này **thêm 1 tầng big idea đứng trên** các chiến dịch, và **liên kết** chiến dịch về big idea của nó.

## Quyết định thiết kế đã chốt (đừng lật lại — hỏi nếu chưa rõ)
- **KHÔNG đổi tên khoá `key_ideas`.** Nó tiếp tục là **mảng CHIẾN DỊCH** (đã mang đủ field chiến dịch).
  Đổi tên khoá = migration rủi ro + đụng mọi consumer cho 0 giá trị người dùng. Coi `key_ideas` = "campaigns"
  về mặt khái niệm; **không** rename storage.
- **Thêm mới:** `intake_extra.big_ideas[]` (tầng trên) + `key_ideas[i].big_idea_id` (FK mềm trỏ ngược lên).
- **`big_idea_id` rỗng = chiến dịch trần** — hợp lệ, degrade OK. KHÔNG bắt buộc mọi chiến dịch phải có big idea.
- **KHÔNG xoá gì.** Không đụng `funnel_map`, `focus_*`, `campaigns_v2`. Additive thuần (tiền lệ:
  `migrate_campaigns_to_key_ideas`).

## Hình dữ liệu (trong `profile.intake_extra` — KHÔNG đổi schema DB)
```
big_ideas[] = [{
  id:         "<slug-time>",       # sinh như save_key_idea sinh id
  title:      str<=140,            # ý lớn 1 câu
  angle:      str<=220,            # góc / thế đối lập (tuỳ chọn)
  source_ref: str<=160,            # lãnh địa/trụ gốc (tuỳ chọn)
  season:     str<=60,             # mùa/kỳ (tuỳ chọn, tự do — vd "Tết 2026")
  created_at, updated_at: float
}]

key_ideas[i].big_idea_id = "<id của big_ideas>" | ""   # THÊM field, mặc định ""
```

## Việc phải làm (tự quyết cách, tự tìm vị trí — đừng tin số dòng)

### Backend `webapp/business.py`
1. **`save_big_idea(user_id, id="", title, angle="", source_ref="", season="")`** — tạo/sửa 1 big idea.
   Append/update `intake_extra.big_ideas` dedupe theo id (mẫu y hệt `save_key_idea`). Title trống → lỗi.
   Trả `{"ok": True, "big_idea": {...}}`.
2. **`save_key_idea(...)`**: thêm tham số `big_idea_id: str = ""`. Validate: nếu truyền và **khác rỗng** thì
   phải trỏ tới 1 big idea **tồn tại** (không thì bỏ qua = "", đừng tạo FK gãy). Ghi vào meta của key_idea.
   Giữ nguyên toàn bộ hành vi cũ (dedupe id, giữ funnel_map khi update…).
3. **`derive_big_ideas(user_id)`** — migration ADDITIVE + IDEMPOTENT: với mỗi `key_ideas[i]` **chưa có**
   `big_idea_id`, mint 1 big idea từ `title`/`angle`/`source_ref` của nó rồi back-link. Chạy lại lần 2 =
   0 thay đổi (idempotent: bỏ qua key_idea đã có `big_idea_id`). KHÔNG gộp trùng ở lần này (1 chiến dịch cũ →
   1 big idea; user gộp tay sau). Trả `{"ok": True, "derived": n, "skipped": m}`.
4. **`biz_data()`**: expose `out["bizBigIdeas"] = intake_extra.big_ideas or []` (mẫu y hệt `bizKeyIdeas`).

### Route `webapp/api.py`
5. Thêm 3 route trong `api_routes()`, đặt cạnh cụm key-idea hiện có:
   `/api/biz/big-idea/save` · `/api/biz/big-ideas/derive` (+ nếu cần cho FE). Handler mỏng như các handler cạnh.

### Frontend `web/app.js` (Edit chèn có mục tiêu — KHÔNG Write đè)
6. `bizBigIdeas` → helper `biList()` (mẫu `kiList()`).
7. Tab **⚡ Chiến dịch** (`mxSpikeInner`): **nhóm** các chiến dịch theo `big_idea_id`. Mỗi nhóm hiện
   **1 header big idea** (title + angle) rồi liệt kê các `kiCardHTML` con. Chiến dịch `big_idea_id=""` gom
   nhóm "Chưa gắn ý lớn" (hoặc hiện phẳng như cũ). Composer `＋ Chiến dịch mới`: thêm ô **chọn big idea**
   (dropdown từ `biList()` + lựa chọn "＋ ý lớn mới" mở ô nhập nhanh).
8. Giữ nguyên `kiCardHTML`, `kiFunnelHTML`, `kiPostHTML` — chỉ đổi tầng bao ngoài (grouping). Đừng phá render bài.

### Calendar — CHỈ ĐỌC, đừng phá
9. `_build_keyidea_bands` + `calendar_plan` lặp `key_ideas` **phẳng** để rải lịch. Sau slice này **vẫn chạy
   y nguyên** vì key_idea còn đủ field (title/angle/window/funnel_map). **KHÔNG cần đụng** — chỉ verify test
   lịch còn xanh. (Band name = key_idea.title vẫn đúng; big idea chỉ là tầng gom ở FE Chiến dịch.)

## ⚠️ Phân tích mối nối (WIRING — làm rồi mới code)
Sổ hợp đồng khoá slice này đụng:

| Khoá | Producer (ghi) | Consumer (đọc) | Khớp? |
|---|---|---|---|
| `big_ideas[]` | `save_big_idea`, `derive_big_ideas` | `biz_data`→`bizBigIdeas`; FE `biList` | tên/kiểu 2 đầu |
| `key_ideas[i].big_idea_id` | `save_key_idea`(+param), `derive_big_ideas` | FE grouping `mxSpikeInner` | FK mềm; rỗng = trần |
| `bizBigIdeas` | `biz_data` | FE `biList` | mẫu `bizKeyIdeas` đã có |

**Luật FK mềm:** `big_idea_id` trỏ big idea **không tồn tại** → FE coi như "" (nhóm chưa gắn), KHÔNG rớt chiến dịch.
Producer `save_key_idea` **không** ghi FK gãy (validate tồn tại trước khi ghi).
**Đây KHÔNG phải derived-state** (con người chốt big idea + gắn FK), nên không cần confidence/why-log.
`derive_big_ideas` là migration một chiều từ dữ liệu người dùng, idempotent — không đoán trạng thái.

## Degrade
- Chưa có big idea nào → tab Chiến dịch hiện phẳng như hôm nay (nhóm "chưa gắn"). Không màn trống lạ.
- `derive_big_ideas` chạy trên profile 0 key_idea → `{derived:0, skipped:0}`, không lỗi.

## Verify (bắt buộc trước commit — dán kết quả vào commit body)
```
python -m py_compile webapp/business.py webapp/api.py
node --check web/app.js
python tests/test_b2_key_idea.py           # còn xanh — save_key_idea không regress
python tests/test_b21_layered_matrix.py    # còn xanh
python tests/test_b22_calendar_source.py   # còn xanh — LỊCH KHÔNG GÃY (quan trọng nhất)
```
**Thêm test mới** `tests/test_fv3_big_ideas.py` (mẫu các test B2, có `_DB` mock):
- `save_big_idea`: tạo mới sinh id; update dedupe theo id; title trống → lỗi.
- `save_key_idea(big_idea_id=<tồn tại>)` → ghi FK; `big_idea_id=<không tồn tại>` → về "".
- `derive_big_ideas`: 2 key_idea chưa gắn → 2 big idea + back-link; **chạy lại → derived=0** (idempotent).
- `biz_data` (hoặc đọc thẳng) → `bizBigIdeas` phản ánh đúng.

## Ranh giới (đừng làm trong slice này)
- KHÔNG đổi `goal`→`purpose` (đó là việc #2). KHÔNG đụng 7 loại chiến dịch, ratio, kênh, journey.
- KHÔNG gộp trùng big idea. KHÔNG đụng calendar reconcile logic. KHÔNG rename `key_ideas`.
- Grep xác nhận caller quét cả `tests/` (AGENTS.md) trước khi kết luận gì "chưa dùng".
```
git grep -n "key_ideas\|save_key_idea\|bizKeyIdeas" -- webapp/ web/ tests/
```

## Handoff
1 commit (hoặc ít commit mạch lạc). Push → mở PR base `staging`. Dán self-verify report (5 lệnh + test mới)
vào PR body. Chờ Claude review PASS. **Không tự merge.**
