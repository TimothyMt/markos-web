# BRIEF S1 — Bản đồ trận địa (đọc/sửa) + nguồn lực + kênh offline/Maps

> **Đây là brief tầng MỤC TIÊU, KHÔNG phải lệnh từng dòng.** Bạn tự tìm anchor bằng **tên hàm** (số dòng đã trôi), tự quyết cách chẻ hàm/đặt UI, **tự verify**. Người review (Claude Code) sẽ soi diff + mối nối; nếu tôi vừa chỉ từng dòng vừa review thì review vô nghĩa.
> **Đọc trước khi code (bắt buộc):** `AGENTS.md` (luật môi trường Windows/pager/Write) · `docs/cmo/SPEC-chien-dich-4-tang.md` (spec chốt, §1–§8) · `docs/cmo/GRILL-LOG-chien-dich-4-tang.md` (nguyên văn quyết định, tra khi spec mơ hồ) · `docs/cmo/WIRING.md` (Hiến pháp mối nối) · CLAUDE.md.
> **Prototype hình dạng FE (tham chiếu, đừng chép cứng):** artifact `65b7cb17-ea09-48bc-bf72-642eae2d2d9a`.

---

## 0. Một câu — S1 làm gì

Dựng **Bản đồ trận địa**: từ nghiên cứu đã có, Max sinh **3 tệp-có-vai → 4 giai đoạn → vấn đề (loại + nguồn)**, user **đọc/sửa/override** được; cộng **nguồn lực** (cờ có/không) + **nguyên tắc cấm** (user tự gõ, có hạn) + mở kênh **Google Maps**. Đây là **bộ nhớ nền** mọi tầng dưới (S2 nước đi, S3 lịch, S4 nuôi-từ-chat) đọc vào.

---

## 1. RANH GIỚI — trong S1 vs ĐỂ SAU (đọc kỹ, đừng lấn)

**TRONG S1:**
1. Model + generator + UI đọc/sửa cho **Bản đồ trận địa**: tệp (3 vai) × giai đoạn (4) × vấn đề (loại + nguồn + confidence + why). **Vấn đề dừng ở đây — CHƯA có nước đi.**
2. **Nguồn lực**: cờ có/không (`intake_extra.resources`), đọc/sửa.
3. **Nguyên tắc cấm**: `intake_extra.principles`, **CHỈ user gõ** (Max KHÔNG suy), có ngày hết hạn, đọc/sửa.
4. **Kênh**: thêm `google_maps` vào từ điển `CHANNELS`; đảm bảo `offline` + `google_maps` chọn được trong picker kênh chiến dịch (offline **đã có** trong `CHANNELS` — kiểm FE có lọc mất không).
5. Expose ra FE qua `biz_data()`; route + handler đầy đủ.
6. Cập nhật **sổ hợp đồng** trong `docs/cmo/WIRING.md` cho các key mới.

**KHÔNG phải S1 (đừng làm, chỉ chừa chỗ):**
- **Nước đi / thư viện nước đi / phanh / Xem-kỹ** → **S2**. Vấn đề trong map CHƯA đẻ nước đi.
- **Chốt → việc 🔑/⚙ → lịch mọc theo pha** → **S3**.
- **Nuôi map từ chat (dock 2 chiều) · cốt lõi tự kiểm · nhắc Telegram** → **S4**. Map S1 chỉ nuôi từ **generator + sửa tay**, chưa có chat.
- **Đừng gỡ/khai tử wizard "Chọn-đầu 5 câu" (`gen_campaign_from_setup` / `dirWizard`)** trong S1. Nó sống tới khi S2/S3 thay được phần "Max soạn". S1 chỉ **dựng map song song** làm nguồn input mới. (Ghi 1 dòng TODO "S2/S3 sẽ thay wizard" là đủ.)

---

## 2. HỢP ĐỒNG DỮ LIỆU (Hiến pháp — CHỐT, đừng tự đổi tên/slug)

> Các key này là **giao kèo** S2/S3/S4 sẽ đọc. Sai tên/slug 2 đầu = mối nối đứt tới runtime mới nổ. **Giữ đúng slug dưới đây.** Nếu thấy shape nào KHÔNG dựng được → **dừng, hỏi review**, đừng tự chế slug khác.
> Ràng buộc bất di: **KHÔNG đổi schema DB** — tất cả vào `intake_extra` (dict).

### 2.1 `intake_extra.battle_map`
```jsonc
{
  "version": 1,
  "updated": "<iso8601>",
  "audiences": [
    {
      "id": "aud_<8hex>",                 // id ỔN ĐỊNH: mint 1 lần, SỐNG qua mọi edit/regen (S3 khoá lịch bám id — giải mìn HANDOFF §4)
      "role": "core|growth|retain",       // 3 vai: chính | tăng trưởng | duy trì
      "label": "chủ shop nhỏ ngại đổi công cụ",
      "source": "wedge|segment_gap|asked|user|max",  // wedge→core, segment_gap→growth, asked/max→retain
      "confidence": "high|med|low",
      "why": "vì sao Max gán vai này (trích nguyên liệu gốc)",
      "stages": {
        "awareness":     { "applicable": true, "problems": [ /* Problem */ ] },
        "consideration": { "applicable": true, "problems": [] },
        "conversion":    { "applicable": true, "problems": [] },
        "retention":     { "applicable": true, "problems": [] }
      }
    }
  ]
}
```
- **role enum (3):** `core` (chính) · `growth` (tăng trưởng) · `retain` (duy trì). Tối đa ~3 tệp (mỗi vai ~1).
- **stage enum (4), ĐÚNG THỨ TỰ:** `awareness` → `consideration` → `conversion` → `retention`.
- **`applicable`:** tệp `retain` mặc định `awareness` + `consideration` = `false` ("không áp dụng"). User bật/tắt được.
- **`id`:** ổn định tuyệt đối. Regen map **không được đổi id** của tệp đã có (match theo role/label để giữ id cũ; chỉ mint id mới cho tệp mới). Đây là hợp đồng persist cho S3.

**Problem** (derived-state — WIRING §2):
```jsonc
{
  "id": "prob_<8hex>",
  "text": "sợ chờ lâu giờ cao điểm",
  "type": "inconvenience|unaware|distrust|risk|price|forget",  // 6 loại, slug cố định (bảng dưới)
  "source": "user|research|max",          // bạn kể | nghiên cứu (T2/T3) | Max đoán
  "confidence": "high|med|low",
  "why": "vì sao suy ra (S4 sẽ nối trích-câu-chat vào đây)",
  "updated": "<iso8601>"
}
```

**6 loại vấn đề — slug ⇄ nhãn VN (CỐ ĐỊNH):**
| slug | nhãn VN |
|---|---|
| `inconvenience` | bất tiện |
| `unaware` | không biết |
| `distrust` | không tin |
| `risk` | rủi ro |
| `price` | giá |
| `forget` | không nhớ |

**Nguồn vấn đề — slug ⇄ nhãn:** `user`=bạn kể · `research`=nghiên cứu (T2/T3) · `max`=Max đoán. (Nhãn phải NHÌN THẤY trên UI — cho user biết bao nhiêu phần bản đồ là thật, SPEC §3.)

### 2.2 `intake_extra.resources`
```jsonc
{
  "can_owner_on_camera": true,   // chủ lên hình
  "can_shoot_video": false,      // quay video
  "can_render_3d": false,        // dựng 3D
  "updated": "<iso8601>"
}
```
Chỉ **cờ có/không** — **BỎ định lượng** (số giờ/team_size là mô hình cũ đã vứt, GRILL-LOG §7). S2 đọc cờ này lọc nước đi.

### 2.3 `intake_extra.principles`
```jsonc
[
  { "id": "prin_<8hex>", "text": "không giảm giá đại trà", "expires": "<iso8601|null>", "created": "<iso8601>" }
]
```
**CHỈ user gõ. Max KHÔNG suy, KHÔNG tự thêm.** Đây là phanh loại-1 (SPEC §2 "nguyên tắc user tự đặt → KHÔNG nắn"). `expires` null = vô hạn.

---

## 3. PHÂN TÍCH MỐI NỐI (JIT — producer/consumer/degrade)

| Khoá | Producer (S1 xây) | Consumer | Degrade khi thiếu input |
|---|---|---|---|
| `battle_map.audiences[].role/label` | `gen_battle_map` bốc từ **`wedge`** (→core) · **T2 Segment Gap** (→growth) · **hỏi/không-có-data** (→retain) | S2 nước đi, S3 lịch, S4 | thiếu wedge/segment → map rỗng + nhãn `⚪ Max đoán` conf `low`, KHÔNG crash |
| `battle_map...problems[]` | `gen_battle_map` chẻ **T3 Fears + intake Q9 `objection`** theo tệp×giai đoạn, gắn `type`+`source` | S2 (nước đi gỡ vấn đề) | không có Fears → giai đoạn để trống (ô trống = sản phẩm, không phải lỗi, GRILL §4) |
| `resources.*` | UI user tick (seed từ intake Q12 `team_size` nếu suy được, conf thấp) | S2 lọc liều nước đi | thiếu → mặc định `false`, user tự bật |
| `principles[]` | **chỉ** UI user gõ | S2 phanh loại-1 | rỗng = không phanh |
| `CHANNELS['google_maps']` | thêm vào dict `CHANNELS` (business.py) | picker kênh, S3 rải | — |

**Nguyên liệu đọc từ đâu (grep tên, đừng tin số dòng):**
- `wedge`: `intake_extra.wedge` (producer `save_gate` / `save_bet`).
- T3 khách/Fears: `await _latest_content(uid, "customer_insight")` (xem cách `gen_campaign_from_setup` gọi).
- intake Q9 `objection`, Q12 `team_size`: trong `intake_extra` / profile intake — grep `objection`, `team_size`.
- messaging.core (chỉ để hiển thị NEO cạnh map, KHÔNG đụng): `intake_extra.messaging.core`, chuẩn hoá `_norm_messaging`.

---

## 4. VIỆC CỤ THỂ (mục tiêu — tự tìm anchor, tự quyết cách làm)

### BE — `webapp/business.py` (FILE LỚN → **Edit chèn có mục tiêu, TUYỆT ĐỐI KHÔNG Write đè cả file**)
1. **`gen_battle_map(user_id)`** — sinh `battle_map` từ nguyên liệu (§3). Là **derived-state (WIRING §2)**: mỗi audience/problem **BẮT BUỘC** có `confidence` + `updated`/`why` + đường **human-override**. Bốc từ research, **không bịa tự do**. Degrade rõ khi thiếu. Idempotent-thân-thiện: chạy lại **giữ id cũ** (match role/label), không nhân bản. Tái dùng `router_call`/`TaskType` như các `gen_*` khác; **giữ chất lượng prompt** (đừng prompt mỏng tự chế).
2. **`save_battle_map(user_id, ...)`** — ghi bản user sửa (thêm/xoá/sửa tệp·vấn đề, đổi role/type/source, toggle `applicable`). **Human-override thắng**: bản user sửa không bị regen ghi đè. Theo đúng pattern read-modify-write `intake_extra` của `save_gate`.
3. **`save_resources(user_id, ...)`** + **`save_principles(user_id, ...)`** — ghi 2 key kia. `principles` chỉ nhận text user (không LLM).
4. **`CHANNELS`**: thêm mục `google_maps` (label "Google Maps / GBP", tiers hợp lý cho điểm bán, formats, write_spec) đúng shape các mục sẵn có. Kiểm `offline` đã có — nếu FE picker lọc mất thì mở ra.
5. **`biz_data()`**: expose `bizBattleMap`, `bizResources`, `bizPrinciples` (theo đúng pattern try/except degrade của các `bizXxx` sẵn có). `CHANNELS` mới tự chảy qua `bizChannels`.

### API — `webapp/api.py`
6. Thêm handler + `Route(...)` trong `api_routes()` cho từng hàm mới (theo mẫu `biz_save_gate` / route `/api/biz/gate`). Đặt path nhất quán, vd `/api/biz/map/gen`, `/api/biz/map/save`, `/api/biz/resources`, `/api/biz/principles`.

### FE — `web/app.js` + `web/styles.css` (app.js LỚN → **Edit chèn, KHÔNG Write đè**)
7. Trang/tab **Bản đồ trận địa**: render 4 tầng lồng nhau (tệp → giai đoạn → vấn đề), **nhãn nguồn + confidence nhìn thấy**, ô trống hiện rõ (không lấp giả). Sửa được: thêm/xoá/sửa vấn đề, đổi loại/nguồn (override), đổi vai tệp, toggle "không áp dụng". Handler trong `handleAction()`.
8. Panel **Nguồn lực** (tick cờ) + **Nguyên tắc cấm** (thêm dòng text + ngày hết hạn).
9. Hình dạng tham chiếu ở prototype artifact; **màn hẹp đọc được** (đừng lưới ngang 900px — GRILL §7 đã vứt).

### Docs
10. Cập nhật **`docs/cmo/WIRING.md`** sổ hợp đồng: thêm dòng cho `battle_map` / `resources` / `principles` / `google_maps` (producer + consumer + slug enum).

---

## 5. RÀNG BUỘC BẤT DI
- **KHÔNG đổi schema DB.** Mọi key mới vào `intake_extra`. Không thêm cột/bảng.
- **FE 1 nguồn** = sửa thẳng `web/app.js`·`styles.css`·`index.html`, KHÔNG mirror đi đâu.
- **Derived-state law (WIRING §2):** mọi thứ Max SUY (vai tệp, loại vấn đề) phải có `confidence` + `updated`/`why` + human-override + degrade. `principles` KHÔNG phải derived (chỉ user gõ).
- **Giữ prompt bot** — tái dùng `router_call`/`agents` prompt như `gen_*` hiện có; đừng thay bằng prompt mỏng.
- **id ổn định** cho audience/problem (mint 1 lần, sống qua regen) — hợp đồng persist cho S3.

## 6. VERIFY (tự chạy trước khi mở PR)
```bash
node --check web/app.js
python -c "import webapp.business, webapp.api"
git --no-pager diff --numstat   # BE/FE task chèn: KHÔNG được là "cả file đổi" (formatter đè = fail review)
```
- Grep xác nhận caller/khoá phải quét cả `tests/`, không chỉ `web/`+`webapp/`.
- Đụng `brain/` → `py brain/_check.py` (S1 chắc không đụng).

## 7. GIT
- Cắt branch **từ `staging`** (vd `feature/s1-battle-map`). KHÔNG commit thẳng `main`/`staging`.
- `gh pr create --base staging` — **KHÔNG tự merge**. Claude Code review trước.
- Cạm bẫy Windows: `core.pager=cat` đã set nhưng cứ dùng `git --no-pager` cho chắc.

## 8. ĐỊNH NGHĨA "XONG" (người review chấm theo đây)
- [ ] 3 key mới đúng **slug/shape §2**; 0 thay đổi schema DB.
- [ ] `gen_battle_map` sinh ≥1 tệp/vai áp-dụng-được từ nguyên liệu THẬT; mỗi vấn đề có `type`+`source`+`confidence`+`why`; **degrade** khi thiếu (map rỗng + nhãn thật, không crash); regen **giữ id cũ**.
- [ ] UI đọc/sửa map chạy: override vai/loại/nguồn, toggle applicable, thêm/xoá vấn đề — **user sửa thắng regen**.
- [ ] Resources (cờ) + Principles (user gõ + hạn) đọc/sửa được; principles KHÔNG do LLM sinh.
- [ ] `google_maps` thêm; `offline`+`maps` chọn được trong picker.
- [ ] `biz_data` expose 3 key; route đăng ký trong `api_routes()`; handler trong `handleAction()`.
- [ ] `node --check` + `python -c import` PASS; `--numstat` gọn (không reformat cả file).
- [ ] WIRING.md có dòng hợp đồng mới.
- [ ] Wizard cũ **còn nguyên** (chưa gỡ); chỉ chừa TODO "S2/S3 thay".

## 9. CẠM BẪY ĐÃ BIẾT (đọc để khỏi vấp)
- **Write đè file lớn = cắt cụt file.** `business.py`/`app.js` chỉ được **Edit chèn có mục tiêu**. Task chèn mà numstat báo cả-file-đổi = làm lại.
- **Đừng dí phẳng** tệp→vấn đề (giấu tầng giai đoạn) — GRILL §4 đã bắt lỗi này; giữ đủ 4 tầng.
- **Đừng bắt user CHỌN vấn đề từ menu** — Max chẩn (suy), user override. Chẩn là việc của Max (GRILL §2).
- **Ô trống = sản phẩm**, không phải bug cần lấp bằng nội dung giả.
- Nếu thấy shape §2 dựng không nổi hoặc research T3 KHÔNG đẻ vấn đề cụ thể (chỉ chung chung) → **dừng, báo review** (SPEC §9 "chặn trước khi tin S2"): thà sửa nguồn còn hơn map generic.

---
*Brief viết bởi Claude Code (phiên review), 2026-07-24. Nguồn chốt: `SPEC-chien-dich-4-tang.md` + `GRILL-LOG-chien-dich-4-tang.md`. Lệch nhau → GRILL-LOG là nguyên bản.*
