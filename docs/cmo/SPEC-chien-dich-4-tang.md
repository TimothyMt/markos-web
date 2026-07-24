# SPEC — Tầng Chiến dịch: Bản đồ trận địa → Nước đi → Việc → Lịch

> **Trạng thái: THIẾT KẾ CHỐT, chưa code.** Chốt qua grill 2026-07-23/24.
> Prototype bấm được (tham chiếu hình dạng FE): artifact `65b7cb17-ea09-48bc-bf72-642eae2d2d9a`.
> Thay thế cửa "Chọn-đầu 5 câu" hiện tại. Đọc kèm: `HANDOFF-lich-tru-redesign.md` (mìn key lịch), `LOOP.md` (pool + vòng lặp), `WIRING.md` (Hiến pháp mối nối).
> **Ràng buộc bất di:** KHÔNG đổi schema DB — mọi key mới vào `intake_extra` (dict). Giữ prompt bot (`agents/`). Verify: `node --check web/app.js` + `python -c "import webapp.business, webapp.api"`.

---

## 0. Một câu

User nói mục tiêu thô ("muốn thêm khách") → Max **chẩn** khách vướng gì (từ hội thoại), đề xuất **nước đi** gỡ đúng vấn đề đó (không chỉ bài đăng), user **chốt** → Max đẻ việc + lịch + nhắc. Người chốt luôn là người.

---

## 1. MÔ HÌNH — 4 tầng lồng nhau

```
TỆP KHÁCH  →  GIAI ĐOẠN  →  VẤN ĐỀ (nhiều)  →  NƯỚC ĐI (nhiều)
(3 vai)       (4 hành trình)  (loại + nguồn)     (bậc + giá + phanh)
```

- **Tệp** = 3 vai: **chính / tăng trưởng / duy trì** (KHÁC `AUDIENCE_SEGMENTS` vòng-đời cũ). Vai = "tiền/tăng trưởng/giữ đến từ đâu".
- **Giai đoạn** = **Nhận biết → Cân nhắc → Chuyển đổi → Duy trì** (mượn bảng Marketing Funnel của user; F&B chạy trong 2 phút, xưởng gỗ 3 tháng — cùng trục khác tốc độ). Tệp duy trì → 2 giai đoạn đầu = "không áp dụng".
- **Vấn đề** = khách bị chặn ở giai đoạn đó. Mang **loại** (6): `bất tiện · không biết · không tin · rủi ro · giá · không nhớ`. Một giai đoạn chứa **nhiều** vấn đề.
- **Nước đi** = cách xoá nhoà 1 vấn đề. Một vấn đề có **nhiều** nước đi.

**LUẬT VÀNG (sợi xuyên suốt):**
> mục tiêu × tệp → chọn **RÀO CẢN/VẤN ĐỀ** phải gỡ → vấn đề → **NƯỚC ĐI** → nội dung quảng bá nước đi.
> Chèn "vấn đề" vào giữa để nước đi bám thực tế, không rơi vào kho generic (minigame/giảm giá).

---

## 2. NƯỚC ĐI — không gian câu trả lời trải 5 bậc

Không chỉ "cơ chế khuyến mãi" — là **mọi nước đi CMO**, xếp thang bậc (bậc thấp = sâu/mạnh):

| Bậc | Loại | Ví dụ |
|---|---|---|
| 1 | **Vận hành** | mở nhận đặt trước qua Zalo |
| 2 | **Chào hàng** | 3 gói giá cố định công khai |
| 3 | **Phân phối** | gõ cửa 5 toà văn phòng / kênh KTS |
| 4 | **Kích hoạt** | thẻ tích điểm, minigame *(bậc thấp nhất)* |
| 5 | **Nội dung** | clip chỉ đường, live dạy nghề |

- **Max phải đề xuất từ ≥2 bậc khác nhau** — chống trọng lực app-máy-nội-dung kéo mọi thứ về bậc 4–5.
- Nước đi bốc từ **thư viện có neo** (`loại vấn đề × giai đoạn`, lọc theo ngành + nguồn lực), LLM **chọn 2–3 rồi biến tấu**, KHÔNG sinh tự do. Thư viện = la bàn (ép quét đủ bậc) + phanh (giá + "khi nào KHÔNG nên dùng").
- **Nội dung ngoài T1–T5 được phép**; **thông điệp thì KHÔNG** — `sub_message` vẫn buộc là con của `messaging.core`.

### Thẻ nước đi (thẻ mỏng) — 4 trường KHOÁ CỨNG, LLM không đụng
Nguồn từ thư viện, không phải model bịa: **bậc · 👤 ai nhúng tay · ⏱ bao lâu (CỠ, không số: "một buổi/vài tuần") · 🔄 có đổi vận hành không**. Cộng: 💰, nhãn bằng chứng, "gỡ vấn đề gì", "đo bằng".
- **Giá là CỠ, sửa được, và bản sửa là tín hiệu** (edit-diff → khẩu vị, LOOP §8.6). Max chịu trách nhiệm nhất quán với lời NÓ nói, KHÔNG với đời thật user.
- **Trường ⚠️ "chỉ nên chốt nếu…"** — CHỈ hiện khi có điều kiện tiên quyết mà sai thì **gây HẠI** (mất tiền/khách/uy tín, không lùi được), không phải "kém hiệu quả". Gắn sẵn ở thư viện, LLM không tự thêm.

### Phanh — 4 loại, hành xử khác nhau
| Phanh vì | Nắn? | Cách |
|---|---|---|
| **Nguyên tắc user tự đặt** | **KHÔNG** | Cứng tuyệt đối. Muốn đổi → user tự gỡ |
| Sai archetype ngành | CÓ | giữ động tác đổi ý đồ (livestream-chốt → livestream-dạy) |
| Vượt nguồn lực | CÓ | thu nhỏ liều |
| Chọi chẩn đoán | CÓ, có điều kiện | chỉ khi bản nắn trúng nghẽn CÓ THẬT khác; nếu không → hạ xuống 1 dòng checklist thẻ khác, hoặc chết |
- Luật chung: nắn được khi đánh vào **nghẽn có thật trên bản đồ**. Phải bịa nghẽn mới → chết.
- Thẻ nắn mang dấu vết `↻ nắn từ …` (dạy user "livestream không sai, sai là dùng nó để chốt").

### Xem kỹ (tầng 4) — mở nắp trước khi Chốt. 5 mục:
① Làm thế nào (các bước — **khung bước ở thư viện**, LLM điền chi tiết) · ② Vì sao Max chọn (+ "đã nghĩ tới rồi bỏ") · ③ Bằng chứng · ④ **Chốt thì sẽ có gì** (toàn bộ việc + bài, "không việc nào mọc thêm sau đó" — chống mồi-và-tráo) · ⑤ Đo + **ngưỡng dừng** (hỏng thì quay lại bản đồ đổi giả thuyết).
- Nút **"Không hợp — vì sao?"** cạnh Chốt → thu tín hiệu "bỏ có lý do" (LOOP §8.6, kênh mạnh).

---

## 3. NUÔI BẢN ĐỒ = hội thoại Max↔user (KHÔNG đo lường tự động)

- **Nguồn chính = chat.** Inbox/bình luận tự-động = GÁC (cần duyệt Meta, quyền đọc tin khách — nhạy). Không xây giờ.
- Mỗi ô vấn đề có **nguồn**: `bạn kể` / `nghiên cứu (T2/T3)` / `Max đoán`. Nhãn nhìn thấy — cho biết bao nhiêu phần bản đồ là thật.
- **Vấn đề = derived-state** (WIRING §2): Max SUY từ câu user, gắn confidence + why (= **trích dẫn câu gốc + đường về đoạn chat**), user override.
- **Ô chat chạy SONG SONG** (dock phải thường trực, mọi tab), KHÔNG phải modal. Bấm 2 chiều: vấn đề→câu chat gốc (nhấp nháy), câu chat→vấn đề trên bản đồ.
- **Max moi, không ghi bừa**: user nói "khách chê đắt" → Max vặn (grill lật vai: chất vấn QUAN SÁT của user) → lòi vấn đề thật. Tái dùng skill `grilling`, đổi đối tượng.
- **Max chủ động hỏi = quan tâm nhẹ, có cớ cụ thể** (ô trống cạnh chỗ vừa nhắc / vấn đề cũ 3 tuần / câu mơ hồ), tối đa 1 câu/phiên. KHÔNG hỏi khơi khơi. (Gác chi tiết, đừng nặng.)
- **Cắt ngữ cảnh**: hiện vài tin trước/sau câu gốc, không dội cả lịch sử.
- **Vấn đề già đi**: >14 ngày chưa nhắc lại → nhãn "chưa xác nhận lại", **giữ nguyên, không tự xoá, không hỏi lần 2**.
- **Ranh giới dữ liệu**: nuôi 100% từ chat user — KHÔNG đọc inbox khách. (Nói rõ trong UI để giữ niềm tin.)

---

## 4. POOL = pool CHIẾN DỊCH (không phải pool content)

- Món pool = **ĐỀ XUẤT chưa cam kết** (kệ), KHÔNG phải hàng-chờ-đã-cam-kết → giữ nguyên LOOP §8.2 (pool rẻ, Max tự đổi).
- Bốc xuống ("Chốt") = điểm thưởng **(B)** trong lộ trình B→C (LOOP §7). Mục đích pool = **"dám chốt"**, không phải thiếu ý.
- **Kệ luôn có thẻ kể cả ngày đầu** (LOOP §8.3 sai-sẵn > trống-sẵn) — nhưng nhãn thật: `⚪ Max đoán — mới biết bạn N ngày`.
- Xếp theo **ô (tệp×giai đoạn×vấn đề)**, KHÔNG theo "mục đích". Mỗi vấn đề ≤ vài nước đi (cần trần cứng khi thư viện đẻ nhiều).
- **Gộp Kệ vào Bản đồ** — nước đi chỉ tới được qua vấn đề (LOOP §7: đổ vào chỗ user đang đứng).

---

## 5. CHỐT → VIỆC → LỊCH (khoá lịch, không khoá bài)

- Chốt nước đi = tạo **big_idea (is_campaign)** + đóng băng **bản chụp** (tệp/vấn đề/loại lúc chốt). Bản đồ đổi sau → Max **báo lệch, KHÔNG sửa ngầm**. (Giải mìn HANDOFF §4: key bám id ổn định, không bám chữ.)
- Việc chia 2 loại (thư viện đánh dấu, LLM không tự phong):
  - **🔑 Việc mở khoá** — thiếu thì **bài nói dối** (vd bài "đặt qua Zalo" mà Zalo chưa bật). **Lịch chưa có ngày cho tới khi 🔑 xong.**
  - **⚙ Chuẩn bị** — không giữ lịch (bài vẫn đúng, chỉ kém tiện).
- **Lịch MỌC RA từ lúc 🔑 xong** — user KHÔNG đoán ngày bắt đầu. Trước đó lịch rỗng thật (không bài giả lấp).
- **Bài rải theo PHA** (Báo tin → Thể lệ → Bằng chứng → Nhắc chót → Tổng kết) cho đợt có nước đi — KHÁC trục phễu. Đợt thuần thông điệp (không nước đi) vẫn chạy trục phễu cũ (`_PURPOSE_RATIO`/`gridLean`). Thêm khoá `mechanic` (rỗng được) phân biệt 2 chế độ.
- **Việc cần làm = (A) trong thẻ + (B) mặt phẳng riêng** (cả hai, như Todoist). Dải "Đang chờ bạn" đầu Lịch.
- **Va chạm nguồn lực**: KHÔNG sổ-cái-số (số Max tự bịa = chính-xác-giả). Chỉ nói định tính khi ≥2 thẻ cùng cần đích thân user: *"cả 3 việc này đều cần đích thân bạn"*. Uỷ-được/không × một-lần/đều-đặn (rút từ thư viện, user không khai).

---

## 6. NHẮC — in-app (luôn bật) + Telegram (user tự nối)

- **Chỉ nhắc thứ user ĐÃ CAM KẾT** (việc 🔑). KHÔNG nhắc thứ Max nghĩ ra. KHÔNG chủ động bắt chuyện.
- Kênh: **in-app** (không tắt được, lưới an toàn) + **Telegram** (per-user, user chọn). Bỏ email + Zalo. Zalo cá nhân KHÔNG có API; Zalo OA cần duyệt → gác. Telegram rẻ/tự do/inline-keyboard nhưng tệp user Việt ít dùng → theo dõi % nối.
- Nối Telegram: tái dùng pattern `oauth_states` (token 1 lần) → deep-link `t.me/<bot>?start=<token>` → **route mới `POST /api/notify/telegram/webhook`** → lưu `intake_extra.notify.telegram.chat_id`. Gửi: đổi `notify.py` từ chat_id-env → chat_id-user. Webhook mở luôn đường 2 chiều (co-pilot sau).
- **Tin GỘP mỗi ngày** (giờ user chọn), 1 tin, có nút `[Xong] [Dời] [Bỏ thẻ]`. Quá hạn → **im**, không nhắc lần 2. Đứng 1 tuần → **1 câu CMO** hỏi cam kết còn không.
- **Danh mục ĐÓNG** — chỉ 4 loại được gửi: việc 🔑 tới hạn · thẻ đứng 1 tuần · đối thủ mở đợt trùng tuần · bằng chứng ngược cam kết. Cấm: "12 ý mới", "400 view", "lâu chưa vào".
- **Hỏng phải kêu**: 2 lần gửi fail → tự tắt Telegram, tụt in-app, hiện cảnh báo.
- Chỗ chứa: `intake_extra.notify = {telegram:{chat_id,linked_at}, time, tz}`. ĐỪNG mượn `user_fb_connections.notify_time` (của thông báo ads).

---

## 7. CỐT LÕI TỰ KIỂM (D6 Measurement — mảnh app đang trống)

- **KHÔNG A/B test câu chữ** (SME thiếu traffic; cốt lõi là NEO, test = tháo neo; thương hiệu đo bằng năm).
- **Test = bằng chứng chảy NGƯỢC**: vấn đề (nuôi từ chat) xác nhận hay thách thức cốt lõi. Scoped ở **tệp chính**.
  - Vấn đề độ-chắc-cao (bạn kể) mà cốt lõi CHẠM tới → **✓ đang được xác nhận**.
  - Vấn đề cốt lõi chưa chạm + độ chắc thấp → **theo dõi**, chưa báo động.
  - Vấn đề TRỘI + độ-chắc-cao + NẰM NGOÀI cốt lõi → **⚠ lệch trọng tâm** = gõ cửa hợp lệ (LOOP §8, "mâu thuẫn cam kết").
- **"Xem lại cốt lõi"** = phiên bằng-chứng-đối-chất, KHÔNG phải ô sửa:
  - Max bày: cốt lõi hiện tại + vẫn-xác-nhận-bởi-gì + chỗ gợn (câu chat thật, mấy lần) — **nêu mâu thuẫn, không giải**.
  - **3 cửa, nghiêng về GIỮ** (phần lớn "vấn đề mới" là chiến dịch trá hình): `Giữ nguyên` (mặc định, 1 chạm, im vài tuần) / `Mở rộng` / `Đổi hẳn`.
  - **Dễ giữ, khó đổi** (ma sát bất đối xứng — neo không trôi vì cú bấm vội).
  - Trước khi ĐỔI commit → **bán kính nổ**: N trụ + M đợt có sub_message con của cốt lõi cũ + lịch đã rải → offer dựng-lại-trụ / đánh-dấu-lệch / huỷ. KHÔNG sửa ngầm.
  - Max **soạn nháp** (chạy `gen_messaging` stage='core' + bằng chứng mới), user sửa+chốt. confidence+why.
  - Van: alarm phải **tái diễn nhiều tuần** mới kích; **đã bỏ qua thì im**.

---

## 8. WIRING — producer/consumer, có gì / làm mới

| Ô/khoá | Đã có (producer) | Việc |
|---|---|---|
| **Thông điệp chính** `messaging.core` | ✅ `gen_messaging(stage='core')` — GIỮ NGUYÊN | chỉ hiển thị + gắn dải bằng chứng |
| **3 tệp có vai** | ⚠️ nguyên liệu: T3 ICP + T2 Segment Gap + `wedge` | đẻ MỚI bộ-ba-có-vai (chính≈wedge · tăng trưởng←Segment Gap · duy trì←hỏi, không có data bán) |
| **Vấn đề + loại + giai đoạn** | ⚠️ intake Q9 `objection` + T3 Fears | chẻ theo tệp×giai đoạn + gắn loại + nuôi từ chat (derived-state) |
| **Nguồn lực (có/không)** | ⚠️ intake Q12 `team_size` + Q11 kênh | thêm cờ có/không: chủ-lên-hình · quay-video · dựng-3D. BỎ định lượng (mau cũ) |
| **Nguyên tắc cấm + hạn** | ❌ | MỚI, chỉ user gõ (Max không suy), có ngày hết hạn |
| **Kênh có vai** | ⚠️ `_dirChannels()` thiếu offline/Maps | **mở offline + Google Maps** (F&B điểm bán cần) |
| **Nước đi / grid** | ⚠️ `_grid_from_ratio`, `_PURPOSE_RATIO`, `gridLean` | GIỮ cho đợt thuần-thông-điệp; thêm chế độ `mechanic` |
| **Chiến dịch** | ✅ `save_campaign` (big_idea is_campaign) | thêm khoá `mechanic`, `snapshot` (bản chụp vấn đề) |
| **Rải bài** | ⚠️ `distribute_grid_posts` (nợ C3) | thêm chế độ PHA + key bám id ổn định (giải mìn HANDOFF §4) |
| **Nhắc** | ⚠️ `notify.py` (chat_id env) | webhook per-user + chat_id user + danh mục đóng |
| **Thư viện nước đi** | ❌ | MỚI — vốn liếng nội dung: `loại vấn đề × giai đoạn × ngành`, mỗi nước đi: bậc·👤·⏱·🔄·khung-bước·⚠️·khi-nào-KHÔNG-dùng |
| **Bãi legacy** | `pillars_locked`/`save_pillars`/UI chốt-trụ chết | DỌN khi mở mặt bằng (HANDOFF §5) |

**Cửa "Chọn-đầu 5 câu" hiện tại** (`gen_campaign_from_setup`, `dirWizard`) → **co lại/thay**: 4/5 câu là thứ bản đồ đã biết. Ô "Nhắm ai" → chọn tệp; "Ưu đãi" → chọn vấn đề (thực ra Max chẩn, không bắt user chọn).

---

## 9. THỨ TỰ XÂY (slice — mỗi slice 1 phiên, /clear giữa các phiên)

| # | Slice | Vì sao trước | Nặng |
|---|---|---|---|
| **S1** | Bản đồ trận địa (4 tầng, đọc/sửa) + nguồn lực + mở kênh offline | mọi tầng dưới đọc nó; thay 4/5 câu wizard | vừa |
| **S2** | Thư viện nước đi + gen từ vấn đề + phanh 4-loại + Xem-kỹ | trái tim; cần đổ vốn nội dung; **rủi ro #1** | NẶNG |
| **S3** | Chốt → việc 🔑/⚙ → lịch mọc theo pha + key ổn định (gộp nợ C3 + mìn HANDOFF §4) | | vừa |
| **S4** | Nuôi bản đồ từ chat (dock 2 chiều) + cốt lõi tự kiểm + nhắc Telegram | khép vòng | vừa |

**Chặn trước khi tin S2**: nếu T3 research không đẻ vấn đề cụ thể ("sợ chờ lâu") mà chỉ chung chung ("quan tâm chất lượng") → sửa T3 trước. Nếu không đủ sức đổ vốn thư viện → **đừng xây S2**, giữ đợt-thông-điệp cũ.

---

## 10. RỦI RO ĐÃ BIẾT
1. **Thư viện nước đi = cam kết nội dung lớn** (loại×giai đoạn×15 ngành, mỗi nước đi nhiều trường). Không đủ vốn → cả tháp sụp về generic.
2. **Chat dài** → cần cắt ngữ cảnh + phân trang; đừng dội cả lịch sử vào LLM mỗi lượt.
3. **3 lần bấm mới tới nước đi** → cần lối tắt "N nước đi mới từ lần vào trước" ở tầng 1.
4. **Lưới/dock cùng mở** trên màn hẹp → chật; cân thu gọn rail.
