# NHẬT KÝ GRILL — Tầng Chiến dịch 4 tầng (bản đối chiếu spec)

> **Đây là bản ghi TRUNG THỰC dòng suy luận của phiên grill 2026-07-23/24.** Spec (`SPEC-chien-dich-4-tang.md`) là bản NÉN — nếu spec sai/thiếu điểm nào, tra ở đây để lấy nguyên văn quyết định + lý do + thứ đã cân nhắc rồi bỏ.
> Người grill: founder (mtnguyen7200). Prototype: artifact `65b7cb17-ea09-48bc-bf72-462eae2d2d9a`.
> Cách đọc: theo trình tự thời gian phiên. Mỗi mục = *đề xuất → phản biện/bắt lỗi → chốt*.

---

## 0. Điểm xuất phát

Founder hỏi màn "✨ Chọn-đầu — Max soạn chiến dịch" (5 câu: nhắm ai / nói gì / để làm gì / ưu đãi / khi nào) nằm ở đâu trong chuỗi ②③④. Trả lời: nó là **mối nối ②→③④** (code tự gọi "mối nối ④"), làn SPIKE bắc cầu — đọc ② (trụ/cốt lõi), đẻ vật thể ③ (lưới tầng×kênh), đổ xuống ④ (băng đợt trên lịch). Founder quyết **thiết kế lại tầng này**.

---

## 1. Phân tích 3 tệp input founder gửi

**Bài "branding vs marketing"** (post giáo dục TOFU):
- Bắt lỗi: nó trộn *positioning* (lựa chọn chiến lược) với *identity/visual* (biểu đạt) — hai tầng khác nhau. App đã tách đúng (`spine.positioning` vs `messaging`), bài thì trộn → lấy nó làm khung = đi lùi.
- Câu "build your brand first" SAI: SME không có ngân sách cho trình tự tuần tự; brand phát hiện TRONG lúc bán. Code app đã đúng hơn bài: `gridLean` tính % xây/chốt (mô hình TỈ LỆ ~60/40), không phải TRÌNH TỰ. → đừng để bài kéo về tuyến tính.
- Giá trị: bài xác nhận sợi `sub_message` = con của `core` là trục đúng, nhưng không giúp thiết kế.

**Ảnh Gánh xôi** (bản đồ trận địa F&B): thứ quý nhất = **RÀO CẢN** (sợ chờ lâu/hết món/không biết điểm gần) + **NGUYÊN TẮC CẤM** (không giảm giá đại trà 30 ngày) + **kênh có VAI**. Phát hiện lớn: cơ chế đúng của Gánh xôi (đặt trước qua Zalo) **sinh từ rào cản, không từ mục tiêu**. Vòng quay may mắn không gỡ rào cản nào → generic.

**Bộ RBL 8 bước**: LẤY B3 nguồn-lực + B7 rủi-ro + B8 review + câu "khi nào KHÔNG cần dùng". BỎ thang-8-bước (quy trình agency tuyến tính) + bảng GPT-vs-Claude (mẹo dùng chat, không phải kiến trúc; app đã có `llm_router`). Đáng xây: vòng khai-phá→chuẩn-hoá→**phản-biện**→người-quyết, làm BÊN TRONG một lần gen (hiện `gen_*` không có bước tự phản biện).

---

## 2. Founder sửa "cơ chế" → "nước đi" (bước ngoặt 1)

Claude hiểu hẹp "cơ chế" = cơ chế khuyến mãi (vòng quay/minigame). Founder sửa: **không, là Max nghĩ ra chiến dịch gì đó để kéo khách** — rộng hơn.
- Bằng chứng ngay trong ảnh: Gánh xôi chọn "nhận đặt trước qua Zalo" = đổi **vận hành**, không phải khuyến mãi, không phải nội dung.
- **Chốt: NƯỚC ĐI trải 5 bậc** — vận hành / chào hàng / phân phối / kích hoạt / nội dung. Max phải đề xuất ≥2 bậc (chống trọng lực app-máy-nội-dung + trọng lực LLM về "giảm giá/minigame").
- **Chốt: chẩn đoán là việc của Max, không phải câu hỏi cho user.** Rào cản chuyển từ *input user chọn* → *output Max suy* (confidence+why, user override). "Founder chẩn được thì đã không cần Max."
- **Bản đồ L1 QUAN TRỌNG HƠN, không phải bớt đi**: input được phép nghèo ("thêm khách"), nhưng bộ nhớ phải giàu. Chất lượng nước đi = chất lượng bản đồ.

**Cửa founder quyết (b):** Max quản nước đi bậc 1–3 (không đẻ bài đăng) như **checklist việc-cần-làm** cạnh lịch bài — chứ không chỉ "nói ra rồi thôi" (a). Lý do (b): bài quảng bá "đặt trước qua Zalo" vô nghĩa nếu Zalo chưa mở → hai thứ buộc sống chung. → founder gọi grill vì "khá lớn".

---

## 3. GRILL POOL CHIẾN DỊCH (không phải pool content)

Founder nhắc: phiên trước có bàn 1 pool, **pool đó là pool CHIẾN DỊCH thuộc các mục đích khác nhau**, không phải pool content. → va chạm với LOOP.md (viết pool theo nghĩa content). Luật §8.2 (Max tự đổi pool không cần báo) sẽ GÃY nếu pool = chiến dịch (chiến dịch là cam kết người/tiền).

**Câu 1 — món pool là đề xuất hay cam kết?** Founder chốt **(A) kệ ĐỀ XUẤT chưa cam kết**. Giữ §8.2 nguyên; khớp mục đích "dám chốt"; "bốc xuống" = điểm thưởng (B).

**Câu 2 — thẻ dày tới đâu?** Chốt **(B) mỏng ở kệ, dày khi bốc**. Luật: thẻ mỏng được phép THIẾU, KHÔNG được nói dối về GIÁ (chống mồi-và-tráo — user bị lừa 1 lần là không bốc thẻ 2). **4 trường khoá cứng**: bậc · ai nhúng tay · bao lâu · có đổi vận hành. Con số kế thừa từ thư viện, LLM không bịa.

**Founder yêu cầu ví dụ thẻ** → Claude dựng thẻ Gánh xôi (3 thẻ: đặt-trước bậc1 / gõ-cửa-toà bậc3 / clip-chỉ-đường bậc5) + 1 thẻ bị chặn (đồng giá 25k — chặn bởi nguyên tắc cấm). Rồi thẻ Xưởng gỗ (mục đích "hỏi giá nhiều chốt ít"): gói-giá-cố-định / cam-kết-ngày-giao / live-dạy-nghề. Rút ra: **rào cản đổi bản chất theo ngành** → thư viện index theo **LOẠI rào cản**, không theo ngành (gọn đi vài lần).

**Founder bắt lỗi phanh (bước ngoặt 2):** "livestream bán tủ" bị chặn — founder chỉ ra livestream CHIA SẺ (dạy chọn gỗ) thì được. → Claude sai độ mịn: chữ sai là "chốt-nhanh" không phải "livestream". **Chốt: phanh NẮN (giữ động tác đổi ý đồ), không XOÁ.** Ra **phanh 4 loại**:
- nguyên tắc user tự đặt → KHÔNG nắn (lách chữ user = mất niềm tin)
- sai archetype ngành → nắn (đổi ý đồ)
- vượt nguồn lực → nắn (thu nhỏ liều)
- chọi chẩn đoán → nắn có điều kiện (trúng nghẽn thật khác; nếu không → hạ thành dòng checklist, hoặc chết)
- Luật chung: nắn được khi đánh vào nghẽn CÓ THẬT trên bản đồ.

**Founder sửa (bước ngoặt 3):** Claude đặt nặng SỐ (sổ cái nguồn lực trừ dần). Founder: "số ngày con người thay được, bạn chỉ cung cấp ý tưởng, user sẽ thay đổi cho phù hợp." → **BỎ sổ cái nguồn lực** (trừ số Max tự bịa = chính-xác-giả). Giá = CỠ không số, sửa được, và **bản sửa là tín hiệu** (edit-diff). Giữ quan sát "nhiều thẻ cùng ăn một người" nhưng dạng ĐỊNH TÍNH (uỷ-được/không × một-lần/đều-đặn, rút từ thư viện, user không khai). Luật: **Max chịu trách nhiệm nhất quán với lời NÓ nói, không với đời thật user.**

**Chốt ①②:** phanh 4 loại (theo bảng) + trường ⚠️ "chỉ nên chốt nếu…" (chỉ hiện khi sai thì gây HẠI không-lùi-được, không phải kém hiệu quả; gắn sẵn thư viện, LLM không tự thêm).

**Câu 3 — theo dõi tới mức nào?** Founder chốt **(iii) khoá LỊCH không khoá BÀI**: ngày rải bài = ngày việc-mở-khoá tick xong; trước đó lịch chưa có ngày (không phải bị chặn). Việc do Max gợi ý, user tự quyết xong/chưa, có deadline + nhắc Telegram. "Vừa todoist vừa CMO." Chỉ một số việc = 🔑 (thiếu thì bài NÓI DỐI); còn lại ⚙ không giữ lịch.

**Telegram per-user + notify:** founder chốt (a) xây liên kết Telegram per-user, (b) không phụ thuộc flow bot cũ (nhưng gọi API trực tiếp OK — tiền lệ `notify.py`), (c) user tự chọn nhận noti từ đâu. Ngân sách nhắc hẹp: 1 tin/hạn, quá hạn IM, đứng 1 tuần → 1 câu CMO. Danh mục ĐÓNG 4 loại.

**Zalo OA vs Telegram:** Zalo cá nhân KHÔNG có API. Zalo OA: tin-follower (cần quan tâm OA) vs ZNS (template cứng, không chở tin động có nút). → Telegram thắng về chi phí/tự do/nút bấm, thua về tệp-user-Việt. Founder chốt: **lùi lại in-app + Telegram, bỏ email + Zalo.**

**Câu 4 — checklist ở đâu?** Founder chốt **cả (A) trong thẻ + (B) mặt phẳng riêng** ("todoist cũng có cả 2").

---

## 4. MÔ HÌNH 4 TẦNG nổi lên (bước ngoặt 4)

Founder: "xây nhiều tầng đi sâu hơn — 1 tầng tệp, 1 tầng giai đoạn, xác định vấn đề tại giai đoạn + cách xoá nhoà."
→ **TỆP → GIAI ĐOẠN → VẤN ĐỀ (nhiều) → NƯỚC ĐI (nhiều)**. Claude trước đó "dí phẳng" (tệp→rào cản→nước đi), giấu mất tầng giai đoạn.
- Thấy ngay ở xưởng gỗ: 3 "rào cản" thật ra ở 3 giai đoạn khác nhau; 2 ô trống (Nhận biết, Duy trì) hiện ra — mà cách nhóm-theo-mục-đích không thấy.
- Giai đoạn = **Nhận biết→Cân nhắc→Chuyển đổi→Duy trì** (mượn bảng của founder, không đẻ taxonomy mới). Cùng trục khác tốc độ (F&B 2 phút / gỗ 3 tháng).
- **Ô trống = sản phẩm, không phải lỗi** (chỗ phễu rò Max chưa có gì).
- Thư viện đổi khoá index: **loại vấn đề × giai đoạn** (cùng loại khác giai đoạn → nước đi khác: "không biết"×nhận-biết ≠ "không biết"×cân-nhắc).

**Founder hỏi 4 câu "lấy thông tin từ đâu" (Claude tra code thật):**
- 3 tệp có vai: nguyên liệu có (T3 ICP + T2 Segment Gap + `wedge`), kết-luận-có-vai CHƯA có. `AUDIENCE_SEGMENTS` là vòng-đời khác trục.
- Rào cản: ĐÃ CÓ (intake Q9 `objection` + T3 Fears) — việc là chẻ theo tệp + gắn loại, không phải moi mới.
- Thông điệp chính: ĐỦ, nối sẵn (`gen_messaging stage='core'`) — ô DUY NHẤT xong hẳn, đừng đụng.
- Nguồn lực: 1 câu thô (Q12 team_size) — thêm cờ có/không, bỏ định lượng.

**Founder xác nhận câu 5:** tệp → nhiều giai đoạn → vấn đề của họ → nhiều nước đi/khai thác. Đúng cấu trúc.

---

## 5. NGUỒN VẤN ĐỀ = hội thoại Max↔user (bước ngoặt 5)

Founder hỏi "hỏi giá rồi im lấy thông tin từ đâu trong case thực tế". Claude tra: chỉ có intake Q9 (niềm tin founder) + T3 (của ngành) — inbox/bình luận KHÔNG có trong ScrapeCreators/FB-connection. Đề xuất tách QUAN SÁT (đếm) / DIỄN GIẢI (suy).

Founder chốt hướng khác: **giải bằng MAX CHAT** — thi thoảng Max hỏi vấn đề user gặp, hoặc user tự chat → Max nhận + tìm cách giải. → **nguồn chính = hội thoại, inbox tự-động GÁC.**
- Hệ quả: bỏ cột "bao nhiêu lần" (không đo thì không có số). Còn: câu user nói → Max suy vấn đề.
- "Max thi thoảng hỏi": founder — đừng nặng nề, như noti quan tâm, tạm bỏ qua chi tiết. User chủ động kể → áp **grill lật vai** (Max chất vấn QUAN SÁT của user để moi vấn đề thật; "khách chê đắt" → vặn → "hỏi xong im").
- Câu 4 (vấn đề không trả lời khi hỏi lại): **giữ nguyên, đánh dấu "chưa xác nhận lại", không hỏi lần 2.**

**"bạn nhắn 11/7" gây hiểu nhầm** → founder: ý là rút từ **hội thoại user↔Max**, không phải user nhắn khách. → mỗi vấn đề: trích câu gốc + **bấm về đoạn chat**.

**Chat chạy SONG SONG** (founder: "bản chất là chat song song với trang") → KHÔNG modal, mà **dock phải thường trực** mọi tab. Bấm 2 chiều: vấn đề↔câu chat. Ranh giới: nuôi 100% từ chat, KHÔNG đọc inbox khách. Claude bị founder dừng 1 lần vì tự sửa code khi founder đang hỏi logic → **bài học: founder hỏi logic thì bày logic, đừng nhảy vào code.**

---

## 6. XEM KỸ (tầng 4) + CỐT LÕI TỰ KIỂM

**Xem kỹ** (founder hỏi "bấm ra gì"): mở nắp toàn bộ thứ sẽ xảy ra nếu Chốt + lý do Max chọn. 5 mục: ① làm thế nào (khung bước ở thư viện) · ② vì sao + "đã nghĩ rồi bỏ" · ③ bằng chứng · ④ **chốt thì có gì** (chống mồi-tráo) · ⑤ đo + **ngưỡng dừng** (hỏng → quay lại bản đồ). Nút "Không hợp — vì sao?" thu tín hiệu bỏ-có-lý-do.

**Cốt lõi có nên test?** Claude phản biện (không nịnh): **KHÔNG A/B test câu chữ** (SME thiếu traffic; cốt lõi là NEO, test = tháo neo; brand đo bằng năm). **Test = bằng chứng chảy NGƯỢC** từ vấn đề (nuôi từ chat) → xác nhận/thách thức cốt lõi. Scoped tệp chính. 3 trạng thái: ✓ xác nhận / theo dõi / ⚠ lệch (= gõ cửa hợp lệ "mâu thuẫn cam kết"). Gánh xôi: 3 vấn đề độ-chắc-cao khớp "không lo chờ lâu/hết món" → cốt lõi tự kiếm được bằng chứng.

**"Xem lại cốt lõi" hoạt động thế nào** (founder hỏi): = phiên bằng-chứng-đối-chất, KHÔNG phải ô sửa. Max bày mâu thuẫn (không giải) + câu chat thật. **3 cửa nghiêng-về-GIỮ** (phần lớn "vấn đề mới" là chiến dịch trá hình): Giữ nguyên (mặc định, 1 chạm, im vài tuần) / Mở rộng / Đổi hẳn. **Dễ giữ khó đổi** (ma sát bất đối xứng). Trước ĐỔI commit → **bán kính nổ** (N trụ + M đợt có sub_message con cốt lõi cũ + lịch đã rải) → offer migration, không sửa ngầm. Max soạn nháp (`gen_messaging` + bằng chứng mới), user chốt. Van: alarm phải tái diễn nhiều tuần; đã bỏ qua thì im.

---

## 7. Những thứ ĐÃ CÂN NHẮC RỒI BỎ (dễ mất nhất trong spec)

| Đã cân nhắc | Vì sao bỏ |
|---|---|
| Sổ cái nguồn lực (trừ số giờ dần) | số Max bịa = chính-xác-giả; founder: người thay số được |
| Cột "bao nhiêu lần" (đếm quan sát) | nguồn = chat không đo → không có số |
| Inbox/bình luận đọc tự động | cần duyệt Meta + quyền đọc tin khách (nhạy); founder chọn chat |
| Email + Zalo làm kênh nhắc | founder lùi về in-app + Telegram |
| Bắt user CHỌN rào cản từ danh sách | đẩy phần khó (chẩn) về user; Max phải tự chẩn |
| Nhóm kệ theo "mục đích" | trộn 2 giai đoạn khác nhau; nhóm theo tệp×giai đoạn |
| Lưới ngang 12 ô (900px) | không đọc trên điện thoại; dùng dải-thu-nhỏ-trong-thẻ-tệp |
| Modal đoạn chat | founder: chat song song → dock thường trực |
| Chấm ●●○ độ chắc | Claude tự đánh giá sai kiểu (thang vs phân-loại) + đọc kém; dùng chữ "bạn kể/nghiên cứu/Max đoán" |
| Test cốt lõi bằng A/B | tháo neo; test bằng bằng-chứng-chảy-ngược |
| Thang RBL 8 bước làm khung | quy trình agency tuyến tính; lấy 3 mảnh vứt thang |
| Bảng GPT-vs-Claude | mẹo dùng chat; app đã có llm_router |

---

## 8. Chỗ CHƯA CHỐT (để phiên xây/thiết-kế sau)

- Trần cứng số nước đi/vấn đề (thư viện đẻ nhiều thì kệ phình).
- Lối tắt "N nước đi mới từ lần vào trước" ở tầng 1 (3 lần bấm mới tới nước đi).
- Cắt ngữ cảnh chat: mấy tin trước/sau câu gốc; phân trang chat dài.
- Sửa-trong-chat (Max hiểu sai → gõ lại) là modal hay trang.
- Vấn đề chưa có "tuổi" như nước đi (nhãn bằng chứng).
- "Max chủ động hỏi khi nào" — gác, đừng nặng.
- T3 research có đẻ vấn đề đủ cụ thể không (chặn S2 nếu chỉ ra chung chung).

---

*Ghi bởi phiên grill 2026-07-24. Đối chiếu: `SPEC-chien-dich-4-tang.md` (bản nén thi công). Nếu 2 file lệch nhau → file NÀY là nguyên bản quyết định.*
