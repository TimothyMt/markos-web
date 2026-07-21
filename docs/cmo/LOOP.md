# LOOP.md — Max như một phòng ban MKT có vòng lặp riêng cho từng user

> **Trạng thái: THIẾT KẾ — chưa code dòng nào.** Chốt qua grill 2026-07-20.
> Trục: `00-PLAN.md` (6 miền CMO) · Hiến pháp mối nối: `WIRING.md` · Kho kiến thức: `KNOWLEDGE.md` (**khác** brain trong file này — xem §3).
> **Rà soát độc lập 2026-07-21** (reviewer không tham gia thiết kế): sửa 7 điểm — §5 (pattern làm xương sống, hạ ❓), §3 (hai đường chéo-user + Hermes), §10 (chỗ chứa thẻ ① + Supabase-only), §3b (① là trích-xuất per-item mới), §12 (① phải đo được + van chi phí E1), §2 (Thủ thư máy/người), §9 (tầng giữa cào công khai). Chi tiết ở từng mục.

## 0. Một câu

Trước: Max là **một chuỗi hàm chạy khi user bấm**. Sau: Max là **một phòng ban tự thức dậy, đi soi thị trường, họp, và cập nhật kế hoạch của user theo thời gian** — nhưng **không bao giờ tự quyết thay user**.

## 1. Mục đích — vì sao có Pool

**KHÔNG phải vì user thiếu ý tưởng.** SME/freelancer/agency không thiếu ý — họ **không dám chốt**, vì không biết ý nào hiệu quả. Giá trị Max bán ra là **phán đoán**, không phải sinh chữ.

Hệ quả bắt buộc, ràng mọi quyết định sau:
- Mọi cơ chế làm user **cuộn nhiều hơn** đều PHẢN mục đích (xem §7 dopamine).
- Trụ nội dung của Max **chưa chứng minh được gì** → không được ép user viết theo. Nên có **nhãn bằng chứng** (§5).

## 2. Roster phòng ban

**Phép thử một ghế:** có mục tiêu riêng · đẻ ra thứ phòng khác tiêu thụ · **nói KHÔNG được với phòng khác**. Không phản đối được ai ⇒ chỉ là một đoạn trong prompt của phòng khác, không phải một phòng.

### Ca đêm — theo đồng hồ, RẺ
| | Mục tiêu | Nói KHÔNG với | Nuôi |
|---|---|---|---|
| 🔍 **Spy** | Mang **sự kiện** về. **Cấm có ý kiến.** | Mọi phòng: *"không bằng chứng nào đỡ ý này"* | Nguyên liệu thô thư viện góc |

Spy **không dùng LLM** — chỉ gọi API. Rẻ nên chạy được đều. Đây là van tầng 1.

### Ca họp — chỉ mở khi Spy thấy khác thật, ĐẮT
| | Mục tiêu | Nói KHÔNG với | Nuôi |
|---|---|---|---|
| 🔬 **Phân tích** | Quan sát thô → **góc** + gắn nhãn bằng chứng | Content: *"cả ngành đang làm rồi, hết mới"* | **Thư viện góc** |
| ✍️ **Content** | Đẻ **nhiều** ý, ưu tiên lạ hơn an toàn | CMO: *"trụ này chán, góc ngoài trụ hay hơn"* | — (tiêu thụ) |
| 🎯 **CMO** | **Cắt**, xếp ưu tiên, buộc vào chiến lược | Content: *"hay nhưng lệch định vị đã chốt"* | **Khẩu vị user** |
| 👤 **Khách** | Đọc bằng mắt người mua. *"Rồi thì sao?"* | Cả hai: *"đọc xong vẫn không thấy liên quan tới tôi"* | — |
| 📊 **Data** | Bài đã đăng ra kết quả gì | Tất cả: *"góc này bạn làm rồi, không ăn"* | **Kết quả + khẩu vị (edit-diff)** |

**Vì sao Spy và Phân tích phải tách** dù nghe như một việc: chúng ở **hai bên cái van**. Spy rẻ → chạy mỗi nhịp; Phân tích đắt → chỉ chạy khi có cớ. Gộp = mất luôn cơ chế tiết kiệm.

### KHÔNG cho làm phòng ban (cố ý)
- **Kênh/Format** — "góc này lên TikTok hay bài dài" đã là **luật xác định** (tầng × kênh). Cho ghế LLM = trả tiền để mô hình đoán lại thứ đã biết chắc.
- **Thủ thư** (gộp góc trùng, cho góc cũ mục, ép chọn khi hai niềm tin mâu thuẫn) — **bắt buộc phải có, nhưng là đường ống chứ không phải phòng**. Ghép vào Phân tích. ⚠️ Nếu xây brain thì đây là **cột chịu lực**: brain không biết quên thì mỗi tháng đoán *tệ đi*, không phải giữ nguyên. **Hai nửa (chốt 2026-07-21): GOM = máy** (đường ống: gộp nhãn trùng, cho góc cũ mục) · **NẮN TỪ ĐIỂN khi trôi = cổng NGƯỜI, nhịp tháng** — máy đề xuất *"các nhãn này hay đi cùng nhau / tên mới đang nổi"*, người quyết gộp-tách-đặt-tên (§8.1 "Max đề xuất, người chốt"). Để máy tự nắn từ điển = Max tự chấm Max, đúng điểm mù §3b/nguồn-C cấm.

## 3. Ba bộ não — KHÔNG gộp

| | `brain/` (đã spec ở KNOWLEDGE.md) | Thư viện góc | Não user |
|---|---|---|---|
| Chứa | Kiến thức MKT: framework · ngành · craft · stage | Góc + bằng chứng thị trường | Kế hoạch · khẩu vị · kết quả của **1** user |
| Phạm vi | 1 bản cho mọi user | Chung, **ẩn danh** | Riêng user |
| Cập nhật | **Người duyệt, KHÔNG auto** | **Máy, auto** | Máy + user sửa |
| Nhịp | Chậm, evergreen | Nhanh, mau cũ | Theo user |
| Ở đâu | Repo, trong git | Kho dữ liệu | Kho dữ liệu |

⚠️ **Mâu thuẫn quản trị phải tôn trọng:** KNOWLEDGE.md quy định *"promote `live` = cổng Human, KHÔNG auto"*. Vòng lặp này **bản chất auto**. ⇒ Thư viện góc **không được** sống dưới governance của `brain/`. Nhưng **mượn nguyên từ vựng** (`updated`, `maturity: fresh|decaying`, `source`, `[[link]]`) — đừng đẻ tên trường song song.

### Hai đường học CHÉO-USER — Hermes chỉ dạy được NỬA
> Thêm 2026-07-21. Phân biệt học **per-user** (thích nghi với 1 user) khỏi học **chéo-user** (A dạy Max để giúp B). Nhầm hai cái = kỳ vọng sai chỗ.

**Hermes Agent** (Nous Research — tham chiếu hay bị nhắc khi bàn "làm Max khôn dần") học **PER-USER**: bộ nhớ markdown 3 lớp (sở thích · ngữ cảnh · quan hệ) + tự sinh "skill" khi thấy pattern lặp. Max **đã có** đúng tầng này: KNOWLEDGE.md (markdown+frontmatter), khẩu vị derived-state (§8.6), "gom → từ điển mọc từ dưới" (§3b). ⇒ Hermes **xác nhận** nửa per-user đã đúng hướng, nhưng **không** dạy được phần chéo-user — đó là thứ Max đi xa hơn Hermes.

Phần **chéo-user** có **hai đường độc lập rủi ro pháp lý** (đừng để cả tham vọng "học cho user sau" treo vào mỗi đường (a)):

| Đường | Đi cái gì chéo user | Pháp lý |
|---|---|---|
| (a) **Vault thẻ-cào** (§3b) | mẫu hình rút từ data cào đối thủ | **Mạnh nhưng KẸT** — ToS Meta/ScrapeCreators (§10), gated sau ④ |
| (b) **Pattern-lựa-chọn ẩn danh** | *"pattern nào user ngành X hay chọn"* (gom ẩn danh) | **SẠCH** — dữ liệu **bên-thứ-nhất** (user tương tác với chính Max), KHÔNG phải data cào |

⇒ Nếu §10 trả lời KHÔNG cho (a): Max **vẫn** còn (b) để "học cho user sau" — hợp pháp, dùng `skill_runs.rating/feedback_text` (không đổi schema). Đường (b) đáng cắm sớm vì **không phụ thuộc đèn xanh** và **không tốn model-mạnh-mỗi-bài**. Luật pattern-là-chính vs lựa-chọn: xem §5.

### Não user = kế hoạch đã có, thêm chiều thời gian
Không phải nơi mới phải nuôi. Lượt chạy đầu (tầng ①②③) **đã đổ đầy nó**. Cái thêm vào là **khả năng già đi và đổi được**.

- **Đơn vị không phải "ghi chú" mà là "một QUYẾT ĐỊNH, có lý do, có tuổi"**: nội dung · viết ngày nào · dựa bằng chứng nào · tin bao nhiêu · lần cuối kiểm khi nào.
- **Thứ đáng xem không phải bản mới nhất — mà là CHỖ ĐỔI.** *"Tháng trước Max nghĩ khách bạn ngại giá. Giờ nghĩ họ ngại hiệu quả. Vì 3 tháng qua đối thủ đều chuyển sang nói kết quả, và bạn đã bỏ qua 4 ý về giá."* ← đây là **aha moment**, và nó **không cần dựng gì mới**, chỉ cần đọc thứ `skill_runs` đã lưu sẵn (hiện chưa ai đọc phần chênh giữa hai bản).

### Ranh giới dữ liệu — KHÔNG được nhoè
> Gom thứ user **đi soi** (data công khai bên thứ 3). **KHÔNG** gom thứ user **làm ra**.

Kết quả bài của user + khẩu vị ⇒ **ở lại với user**, không vào thư viện chung.

## 3b. Vault & Thợ đọc — thô → thẻ

> Chốt qua grill 2026-07-20 (đợt 2). Đây là phần **cụ thể hoá "Thư viện góc"** ở §3.

### Hai vault, phân biệt bằng CỬA VÀO chứ không bằng nội dung

| | **Vault Max** (chung) | **Vault user** (riêng) |
|---|---|---|
| Chứa | Thẻ góc đa ngành đa kênh — rút từ thứ **spy** kéo về | Thứ Max chạy ra **cho user đó**: kế hoạch, khẩu vị, kết quả |
| Dùng cho | Mọi user | Đúng 1 user |

⚠️ **Xung đột "user B soi user A" — luật phát biểu đúng phải nói về CỬA, không nói về nội dung.** Luật *"không lấy thứ Max viết cho A"* **không thi hành được và cũng sai**: một khi A đã **đăng công khai**, bài đó đã ra thị trường, spy của B tìm thấy là **hợp lệ** — nó là thứ đối thủ đang chạy thật.

| Đường vào | |
|---|---|
| Công khai (spy đi cào trang A) | ✅ được vào vault Max |
| Nội bộ (đọc DB của A) | ❌ **tuyệt đối cấm** |

Cùng một đoạn chữ, **vào bằng cửa nào** quyết định hợp lệ hay không. Thi hành được thật: **spy không có quyền đọc DB.** Thứ vĩnh viễn không rời vault user: bản nháp chưa đăng · khẩu vị · số kết quả · chiến lược.

### Hai Max — tách vì TIỀN, không vì vai

| | 🔬 **Thợ đọc vault** | 🎯 **Cố vấn user** |
|---|---|---|
| Vào → Ra | thô → **thẻ** | não user + thẻ liên quan → **lời khuyên** |
| Biết user là ai | **không** | có |
| Nhịp | hàng loạt, ca đêm | đúng lúc user đang quyết |
| Cấm | **cấm khuyên** | — |

**Lý do tách là chi phí, không phải thẩm mỹ:** việc đọc một bài **không phụ thuộc ai đang xem** ⇒ mổ **một lần, dùng cho cả thiên hạ**. Trộn hai việc ⇒ chi phí nhân theo **số user**; tách ⇒ nhân theo **số bài trên đời**.

⚠️ **Model rẻ KHÔNG đủ.** Việc này là **diễn giải** (đọc ý đồ bài trong bối cảnh mô hình kinh doanh của người đăng), không phải dán nhãn — model rẻ sẽ làm tròn và làm ẩu. Cái tiết kiệm **chưa bao giờ là "model rẻ"**, mà là **"đọc một lần dùng chung"**. Có thể đặt **cửa lọc rẻ** phía trước (bài này có phải nội dung thật không, hay chỉ là "chúc mừng năm mới") rồi mới thả model mạnh vào phần sống sót — vẫn đúng kiểu van §4.

### Hai tầng lưu — thô là NHIÊN LIỆU, không phải kho lưu niệm

| Tầng | Ai thấy | Vòng đời |
|---|---|---|
| **Thô** | không ai — chỉ máy đọc | riêng tư. **Không bao giờ phục vụ ra ngoài, không dùng chéo khách** |
| **Thẻ** | cố vấn + user | thứ **duy nhất** đi chéo user |

**Bắt buộc giữ thô**, vì không có thô thì **không mổ lại được** — thợ đọc v2 ra đời mà quá khứ **chết cứng ở phiên bản 1** ⇒ vault chỉ tích, không học. Nhưng chỉ giữ **chữ**: caption + transcript + metadata. **Media không tải về** (link thôi) — nặng, và không phải thứ mang nghĩa.

Vòng phát triển thợ đọc: `thô + phiên_bản_prompt → thẻ`. Ra v2 ⇒ chạy lại trên kho thô ⇒ **so thẻ cũ/mới**, chỗ lệch nhiều = chỗ v1 đọc sai. Diff tự nó là thước, không cần ai chấm tay.

### Trường trong thẻ

**Công thức: cố định CÂU HỎI, tự do CÂU TRẢ LỜI.** Ép chọn trong danh sách = ép Max **làm tròn** cái nó thấy vào ô gần nhất, và cái mới thì vĩnh viễn không có chỗ.

| Trường | Kiểu |
|---|---|
| `bối_cảnh_người_đăng` — bán gì, **đường tới tiền** | văn xuôi, **1 lần / trang** |
| `nói_cái_gì` | văn xuôi tự do |
| `nói_như_nào` | văn xuôi tự do |
| `mục_đích_cụ_thể` — muốn người xem **làm gì tiếp** | **cụ thể**, cấm quy về danh mục |
| `tầng_theo_người_đăng` | **phán đoán** + `confidence` + `why` |
| kênh · định dạng · ngành nguồn · link | dữ kiện |
| 💰 ❓ 👀 | **để riêng, không trộn vào nghĩa** |

**"Đường tới tiền"** = chuỗi bước một người lạ phải đi trước khi tiền về túi, và **bước nào là bước chốt**. Ba câu là đủ: *(1) tiền về bằng cách nào* · *(2) chốt ở đâu* (quầy · inbox · web · sale gọi · gặp mặt) · *(3) xa bao nhiêu bước*. Đọc được từ thứ công khai: **CTA của ads** (`ctaDist` audit đã gom sẵn), có hiện giá hay giấu giá, họ bảo người ta làm gì.

⇒ **"Tầng" KHÔNG phải thuộc tính của bài.** Cùng cơ chế "kéo tới sự kiện": quán ăn — tới quán ≈ đã chốt (**BOFU**); SaaS — webinar là bước 2/5 (**MOFU**). Không biết đường tới tiền thì **không thể đọc đúng tầng**.

**Cấm quy `mục_đích` về danh mục** (Max đang có 7 `purpose` enum): bài F&B "kéo khách tới sự kiện offline" sẽ bị nhét vào ô gần nhất và **mất sạch cái riêng**. Và chính việc ghi cụ thể mới **cứu nhãn 🔵**: bước gom sau đó mới nhìn ra *"kéo tới sự kiện offline"* (F&B) và *"đăng ký webinar"* (SaaS) là **cùng một hình**. ⇒ **Trừu tượng hoá xảy ra ở bước GOM, không ở bước ĐỌC.**

**`đòn bẩy` (sợ mất / bằng chứng / quyền uy / khan hiếm / tò mò): KHÔNG hỏi thợ đọc.** Nó **mọc ra** từ `nói_như_nào` ở bước gom.

**Từ điển mọc từ dưới lên.** Bẫy ở đầu kia: để tự do hoàn toàn thì *"khan hiếm"* / *"sợ lỡ"* / *"chỉ còn 3 suất"* nằm ba thẻ khác nhau ⇒ **không đếm được** ⇒ mà 🔵 bản chất là **phép đếm chéo ngành**. Lối ra: thợ đọc viết tự do → **bước gom** (chạy sau, trên toàn kho) gộp nhãn hay đi cùng nhau thành họ. Tên mới xuất hiện nhiều lần = **tín hiệu thị trường đang đổi**, thứ mà enum cứng sẽ nuốt mất không dấu vết. Đổi lại: từ điển sẽ có lúc trôi ⇒ **cần liếc mắt định kỳ** (việc thật của Thủ thư, §2).

### Lưu NGUYÊN LIỆU cạnh KẾT LUẬN

Vì `tầng` là trường **đổi nghĩa khi người đọc đổi**:

```
mục_đích_cụ_thể       "kéo người tới quán tối thứ 6"
đường_tới_tiền        "ăn tại chỗ, chốt ngay khi tới"
tầng_theo_người_đăng  BOFU   (confidence: cao)
why                   "tới quán ≈ mua, không còn bước trung gian"
```

Thẻ giữ **kết luận để MÁY đếm** (tầng là trục chung duy nhất đếm được ngay; `mục_đích` tự do thì chưa đếm được cho tới khi gom xong) và giữ **nguyên liệu để CỐ VẤN cãi lại**: gặp user SaaS, đọc `why`, thấy *"tới quán ≈ mua"* không đúng mô hình của user ⇒ **tự dịch lại thành MOFU tại chỗ**, không cần kéo lại data, không đọc lại bài.

⇒ `why-log` (WIRING §2) từ **thủ tục cho có** thành **thứ có công dụng thật**. Lợi thêm: có nguyên liệu trong thẻ thì lúc ra v2, **sàng được chỗ đáng mổ lại trước khi đụng kho thô**.

### Tư cách vào vault: **(C)** — vào hết, nhưng có tuổi

Vào hết; thẻ **không tín hiệu thì mục dần và rụng**. Không lọc-ngay-từ-cửa (B) vì làm thế **giết nhãn 🟡**: muốn thấy *khoảng trống chưa ai làm* thì phải nhìn được cả **cái không ai chạy** — vứt phần im lặng đi là mù nửa bản đồ. Tái dùng đúng `maturity: evergreen|fresh|decaying` đã có trong `brain/`.

### Ba nguồn phán — cái gì dạy thợ đọc rằng nó đọc sai

| | Đo cái gì | Nhịp | Bản chất |
|---|---|---|---|
| **C** soi mẫu | đọc có **ĐÚNG** không | định kỳ, chủ động | suy luận — **phải soi mù** |
| **A** cố vấn chấm ngược | thẻ có **ÍCH** không | liên tục, miễn phí | suy luận — dễ trôi |
| **B** kết quả thật | góc có **ĂN** không | thưa, chậm | **sự thật ngoại lai** |

**Chốt: C (soi mù) làm ngay · A ghi log từ ngày đầu, chưa đọc vội · B đặt móc từ ngày đầu, đọc khi đủ dày.**

- **A và C đo hai thứ khác nhau** dù dễ tưởng là một. Thẻ đọc chuẩn vẫn có thể vô ích; thẻ đọc sai vẫn có thể tình cờ hợp ý. **Chỉ có A** ⇒ thợ đọc học cách viết thẻ **dễ bán** thay vì thẻ **đúng** — đúng bệnh "thưởng cho XEM" §7.
- **C là Max chấm Max** ⇒ điểm mù hệ thống sống sót nguyên vẹn. Nên **C phải soi mù**: người chấm chỉ nhìn **thô**, không nhìn thẻ cũ, và tốt nhất là **model khác** thợ đọc.
- **B là cái NEO, không phải cái loop.** Quá thưa để vận hành hằng ngày, nhưng là **thước chuẩn hiệu chỉnh A và C**: thẻ A khen mà liên tục thua trên B ⇒ **A đang nói dối**. Không có B thì A với C gật gù với nhau, log xanh, vault mục dần.
- **B lẫn hai thứ**: bài thua có thể vì **thẻ đọc sai**, cũng có thể vì **user viết dở**. Phải nhìn **cùng một góc qua nhiều user** mới tách được nhiễu.
- ⚠️ **Móc cho B phải đặt TỪ BÂY GIỜ** dù data còn nhỏ giọt — tức là cái nối bài-đã-đăng về đúng thẻ (§6). Để sau mới làm thì mọi bài chạy trong lúc chờ **mất dấu vĩnh viễn**.

### 🔑 `audit_social_page` đã là ~70% thợ đọc — chỉ đang sai HÌNH DẠNG

`SOCIAL_PAGE_AUDIT_SYSTEM` (`agents/operational_prompts.py:2035`) đã chạy thật, đã test SpeeGo (logistics) vs Highlands (cà phê) ra hai báo cáo khác hẳn ⇒ không dính page nào. Nó **đã làm đúng kiến trúc trên**:

- Thứ tự **① định vị → ③ khách hàng → … → ⑨ phễu** = **đọc trang trước, xếp tầng từng bài sau** — đúng hai lớp.
- `## 5 Tuyến Nội dung` — *"gom bài thành 2-4 tuyến, mỗi tuyến: tên · mục đích · cách thể hiện"*, **không liệt kê tuyến nào** ⇒ đúng "bước gom", đã chạy ở quy mô 1 trang.
- `## 6 Công thức` — *"(PAS, Storytelling, Info+Authority, BTS**…**)"* ⇒ **ví dụ mồi, không phải enum**. Đã là nếp nhà.
- `## 9 Phễu` — gán TOFU/MOFU/BOFU **từng bài + ads** trong bối cảnh định vị của trang, **kèm "khoảng trống"** (= 🟡).
- Có sẵn phanh chống làm-tròn: *"phân tích dựa trên **NGÔN TỪ THẬT**, không suy diễn từ tên ngành"*, *"số tương tác = 0 là tín hiệu thật"*.

**Bốn chỗ lệch — và đều lệch cùng hướng: nó là CỐ VẤN, chưa phải THỢ ĐỌC.**

| | Audit hiện tại | Thợ đọc cần |
|---|---|---|
| Đầu ra | **văn xuôi cho người**, 12 mục / trang | **thẻ có cấu trúc, từng item** — đếm & gom chéo trang |
| Chạy khi nào | on-demand, **mỗi user gọi lại từ đầu** | 1 lần / bài, dùng chung |
| Phiên bản | không có; nhét cả cục vào `skill_runs` | `phiên_bản_prompt` + mổ lại được |
| Khuyên | `## 11`, `## 12` khuyên thẳng (*"→ Cơ hội cho sếp"*) | **cấm khuyên** |

⇒ **Việc phải làm KHÔNG phải viết thợ đọc mới, mà là TÁCH cái đang có làm hai đầu ra:** cùng một lần kéo data → phát ra **(a) thẻ cho máy** (mục 5·6·9 + `mục_đích_cụ_thể` từng bài) và **(b) báo cáo cho người** (12 mục như giờ). Giữ được **đường kéo thô + khung phân tích** đã kiểm chứng.

⚠️ **"Giữ nguyên prompt, rẻ hơn nhiều" là claim MỀM** (sửa 2026-07-21): output hiện tại là **12 mục văn xuôi**; per-post **không** phát thẻ có cấu trúc (mục 9 gán tầng bằng văn xuôi, **không** `confidence`; các trường `nói_cái_gì`/`mục_đích_cụ_thể`/`tầng+confidence` **chưa tồn tại** — verify prompt `operational_prompts.py:2048-2086`). ⇒ rút thẻ per-item là **một lần trích-xuất MỚI**, không phải byproduct miễn phí. Hai đường, mỗi đường phá một lời hứa:
- **(a) mở rộng prompt** phát thêm khối thẻ có cấu trúc cạnh 12 mục — **đụng prompt đã test** ⇒ bắt buộc **regression check** (chạy lại SpeeGo/Highlands, so 12 mục cũ↔mới).
- **(b) LLM lần hai** chuyên rút thẻ, dùng chung data đã kéo — giữ prompt cũ nhưng **2× token output**.
- **Khuyến nghị (a):** data-fetch mới là phần đắt; thêm token output rẻ hơn một call mới. Ước lượng công của ① phải tính phần trích-xuất mới này, đừng coi là "chỉ tách".

**Ba thứ phải thêm khi tách:** `## 9` hiện **phán tầng bằng giọng chắc nịch, không có `confidence`** — bê thẳng sang thẻ thì sai số **đông cứng thành sự thật** trong vault · **💰 thời lượng ad chạy** phải thành **trường tín hiệu trên thẻ** (giờ đang tan vào văn xuôi mục 8) · **cắt mục 11–12 khỏi nhánh thợ đọc** (giữ nguyên cho nhánh báo cáo người đọc).

## 4. Vòng quay — có van 2 tầng

| Tầng | Chạy khi nào | Giá |
|---|---|---|
| 🔍 Spy | Mỗi nhịp, quét "ai tới hạn kiểm" | **Rẻ** — gọi API, không LLM |
| 🎯 Phòng ban họp | **Chỉ khi Spy thấy khác thật** | Đắt — nhiều lượt LLM |

Cái rẻ chạy đều; cái đắt chỉ chạy khi có cớ.

### Báo user — **mới ≠ đáng**
Mỗi lần báo là **vay sự chú ý**. ~3 lần vay hụt là user tắt hết, và vòng lặp **chết âm thầm trong khi log vẫn xanh**.

| Mức | Khi nào | Max làm |
|---|---|---|
| **Im** | Spy thấy bài mới, phòng ban đẻ thêm ý | Pool dày lên. **Không báo gì.** |
| **Dấu** | Ý user từng lưu nay có bằng chứng mạnh hơn | Đổi nhãn. Thấy khi vào. |
| **Gõ cửa** | CHỈ 2 loại (xem dưới) | Cắt ngang thật |

**Gõ cửa chỉ đúng 2 loại, và đều KHÔNG phải ý tưởng:**
1. **Có hạn** — đối thủ vừa mở đợt đúng tuần user định chạy; dịp ngành sắp tới mà lịch trống.
2. **Mâu thuẫn cam kết** — bằng chứng mới **ngược trụ user đang viết theo**, hoặc ngược chiến dịch đã duyệt.

*"Có 12 ý mới"* → **im**.

### Kéo user quay lại: KHÔNG kéo user vào pool — đổ pool vào chỗ user đã đứng
Lúc user mở lịch, tạo chiến dịch, ngồi trước ô trống chưa biết viết gì — **đó** là lúc ý có giá trị nhất. **Thời điểm quyết định giá trị nhiều hơn chất lượng ý.** Không cần thông báo, không cần user học thói quen mới, không cần kênh gửi ra ngoài app.

## 5. Thước đo — PATTERN là xương sống, mỗi tín hiệu một việc

> Sửa lớn 2026-07-21. Bản cũ lấy **❓ tỉ lệ hỏi** làm "đơn vị chung cả hệ" — hỏng vì mẫu số reach riêng tư **và** comment vốn thưa (xem dưới). Đơn vị chung phải là thứ **luôn có**, không phải một tỉ lệ phần lớn thời gian bằng 0.

**Đơn vị chung giữa hai phía KHÔNG phải một con số — mà là PATTERN.** Thợ đọc rút từ **chữ** mỗi bài/ad *làm gì*: góc · kiểu hook · CTA · `đường_tới_tiền` · tầng phễu. Đọc từ ngôn từ nên **bài 0 comment vẫn đọc đủ** — dày, luôn có, so được hai phía. Các tín hiệu số bên dưới **không tự đứng một mình**; chúng chỉ **gắn nhãn / xê dịch thứ hạng** cho pattern.

| Tín hiệu | Nói được gì | Việc của nó | Thấy ở đâu |
|---|---|---|---|
| 💰 **Tiền** — quảng cáo chạy bao nhiêu ngày, chạy lại mấy lần | *"Có người đặt tiền vào góc này và không rút ra"* | **Cấp nhãn 🟢** cho pattern | Chỉ phía đối thủ |
| ✅ **Lựa chọn** — user chọn ý nào, bỏ ý nào | *"Pattern này cộng hưởng với user"* | **Tái xếp hạng NHANH** — nhưng dưới bằng chứng, neo bằng kết quả (luật dưới) | Chỉ phía user (bên-thứ-nhất, trong Max) |
| ❓ **Tỉ lệ hỏi** — comment mang ý định (*"giá?"*, *"ib"*) | *"Góc này biến người nhìn thành người hỏi"* | Tín hiệu **THƯA** — dùng KHI CÓ, **không làm xương sống** | Cả hai phía, nhưng thưa |
| 👀 **Tương tác** — like/view/share | *"Đang nổi"* / *"ai cũng làm rồi"* | Phát hiện xu hướng + **độ bão hoà**. **KHÔNG BAO GIỜ gọi là bằng chứng.** | Cả hai phía |

**Vì sao ❓ tỉ lệ hỏi KHÔNG làm được xương sống:** (a) mẫu số **reach riêng tư** — chỉ chủ page thấy; phía đối thủ không có ⇒ hai phía buộc dùng hai mẫu số khác nhau, **không so tuyệt đối chéo phía được**. (b) **comment vốn thưa** — đa số bài SME 0–vài comment ⇒ tỉ lệ phần lớn thời gian = 0, không đủ dày để chở cả hệ. ⇒ Khi có comment thì dùng, **so thứ hạng NỘI BỘ mỗi phía**, cấm so số tuyệt đối chéo phía; ghi chú thiên lệch `topComments` (chỉ lấy được bình luận nổi, không phải toàn bộ).

### Pattern là ĐƠN VỊ · lựa chọn là TÍN HIỆU HỌC — luật khi hai cái cãi nhau
> Chốt 2026-07-21. Giá trị Max bán ra là **bằng chứng** (§1); bằng chứng bám vào **pattern**, không vào lựa chọn (lựa chọn trần = *"ý này dễ bấm"*, chưa chứng minh gì). Nên pattern làm đơn vị mang nhãn; lựa chọn chỉ tái xếp hạng **trong khung bằng chứng cho phép**.

- Pattern có bằng chứng mạnh (🟢/🔵) **mà ít được chọn** → **vẫn bày** (đổi cách diễn đạt), không chôn. Bằng chứng thắng phổ biến.
- Pattern **được chọn nhiều nhưng không bằng chứng + kết quả kém** → **hạ**. Đây đúng bẫy §7 (*"thưởng cho XEM"*) dời lên một tầng — phải chặn.
- ⇒ Lựa chọn là bộ tái-xếp-hạng **rẻ · dày · miễn phí**, nhưng **luôn có dây xích**: dưới bằng chứng, **neo bằng nguồn-B (kết quả thật)**. Không neo ⇒ Max học viết ý *dễ chọn* thay vì ý *chạy được*.
- **Cold-start:** pattern bơm được từ data cào đối thủ **trước khi có user nào chọn gì**; lựa-chọn-làm-chính thì user mới mở Max ra không có gì để bày.

**Ba nhịp — sức nặng của lựa chọn tăng dần khi B dày:**
1. **B mỏng (đầu):** chạy bằng pattern + 💰 (cào đối thủ) + lựa chọn (dày nhưng **CHƯA neo** — chỉ sắp thứ tự cho dễ nhìn, **KHÔNG** gọi là "hiệu quả").
2. **B tích dần:** bắt đầu neo — pattern được chọn **rồi ra kết quả** mới lên hạng; được-chọn-mà-thua bị hạ.
3. **Bắt buộc từ ngày đầu:** hạ tầng thu B (móc §6) cắm ngay dù data nhỏ giọt — đúng §12② (*"neo không thả muộn được"*).

**Vì sao dừng ở "hỏi", không đo tới đơn:** việc của nội dung là **biến người nhìn thành người hỏi**. Biến người hỏi thành người mua là việc của **giá, sản phẩm, người trả lời inbox**. Bài tạo 20 câu hỏi mà chốt 0 đơn **không phải lỗi bài viết** — chấm nó điểm thấp là học sai rồi đề xuất tệ hơn. Đo tới đơn **trộn nhiễu khâu bán vào điểm khâu viết**.

### Nhãn bằng chứng (mặt user nhìn thấy)
- 🟢 **đã chạy tốt trong ngành bạn** — có tín hiệu tiền
- 🔵 **chạy tốt ở ngành khác** — ⭐ **điểm ngọt**: có bằng chứng mà vẫn mới
- 🟡 **khoảng trống** — chưa ai làm
- ⚪ **Max tự nghĩ** từ insight của bạn

Đi **cả hai hướng**: chỉ bám bằng chứng thật ⇒ suốt ngày đi sau người ta. Phải có ⚪/🟡.

**Điểm yếu phải nói thẳng với user:** ngách nào đối thủ **không chạy quảng cáo** thì vô hình với thang tiền → thư viện 🟢 mỏng đúng ở đó. Max phải nói *"ngành bạn tôi chưa đủ bằng chứng"*, **không được lấy like lấp cho đầy**.

## 6. Nối kết quả về đúng ý — chỗ đứt nằm ở Ctrl-C

Phân phối là **thủ công** (đã chốt): Max viết, user tự đăng. ⇒ Sợi dây giữa *"ý số 7 trong pool"* và *"bài trên fanpage"* **đứt ngay tại nút copy**. Lấy số thì dễ (đã có FB OAuth). **Biết số thuộc ý nào** mới là bài toán.

**Cách chốt: Max tự dò.** Đọc bài đã đăng trên page user → so với **chính nội dung mình vừa sinh ra** → tự nối; khớp mờ thì hỏi đúng 1 câu.
- Đúng luật §8: Max **sai-sẵn**, user **sửa** — không phải user nhập.
- Bài toán khớp **dễ bất thường** vì văn bản đó chính Max viết; user sửa thì vẫn gần trùng. Không phải attribution mù.
- **Phần đắt nhất:** khớp được thì nhặt luôn **chênh lệch giữa bản Max viết và bản user thật sự đăng** — bỏ câu nào, thêm gì, đổi giọng ra sao. Đây là **tín hiệu khẩu vị chất lượng cao nhất trong cả hệ thống**, và đây là cách duy nhất lấy được nó mà **user không phải làm gì**.

**Quyền riêng tư — ranh giới cứng:** ĐẾM *"có 12 hội thoại mới"* ≠ ĐỌC nội dung 12 hội thoại đó. Bên trong là tin nhắn của **khách hàng thật, người không hề biết Max tồn tại**. ⇒ **Chỉ đếm, không đọc**, cho tới khi có đường xin phép tử tế. Đọc nội dung là **quyết định về niềm tin**, không phải một tính năng — phải hỏi riêng, không được lẳng lặng bật.

## 7. Học Meta có chọn lọc

**LẤY — phần thưởng biến thiên.** Pool **không đều đặn** ("mỗi thứ Hai 5 ý" ⇒ tuần thứ ba user thôi mở). Khác biệt đạo đức quan trọng: **Meta phải bịa ra sự bất định; của ta là THẬT** — thị trường vốn lúc có lúc không. Ta chỉ ngừng làm phẳng nó đi.

**BỎ HẲN — cuộn vô tận.** Sinh **tê liệt vì quá nhiều lựa chọn** = **đúng cái bệnh ta đang chữa** (§1). User cuộn 40 phút, thấy sướng, đóng máy, **không đăng gì** — Meta gọi đó là thành công, Max thì vừa thất bại hoàn toàn.

> **Vòng của Meta thưởng cho XEM. Vòng của Max phải thưởng cho XONG.**

Lấy "thời gian trong app" làm thước đo ⇒ Max sẽ học cách đưa ý **quyến rũ mà vô dụng**, vì đó đúng là thứ tối ưu cho thước đo đó.

### Lộ trình thưởng B → C
- **(B) Thưởng khi CHỐT được ý** — làm ngay, phản hồi tức thì, đúng mục đích "dám chốt".
- **(C) Thưởng khi bài đã đăng RA KẾT QUẢ** — *"ý bạn lấy 3 tuần trước giờ là bài nhiều người hỏi nhất tháng"*. Có đủ tính biến thiên như Meta nhưng thưởng **đúng hành vi cần**. Với người kinh doanh, **bằng chứng rằng phán đoán của mình đúng** gây nghiện hơn cảm giác được nhìn.

**B là bậc thang BẮT BUỘC để lên C:** không có B ⇒ không ý nào được chốt ⇒ không bài nào được đăng ⇒ C **vĩnh viễn không có nguyên liệu**.

## 8. Luật (đã chốt — ràng mọi thiết kế sau)

1. **Max đề xuất, người chốt.** Đã xuất hiện 3 chỗ độc lập (co-pilot PHANH · `gen_campaign_from_setup` không persist · pool) ⇒ **luật chung sản phẩm**, không phải quyết định từng tính năng.
2. **Tự-do-đổi tỉ lệ NGHỊCH với mức cam kết.** Pool (rẻ, đảo ngược được) → tự đổi, **không cần cả báo**. Chiến lược (đắt, đã cam kết) → **phải gõ cửa**.
3. **Max phải SAI-SẴN, không được TRỐNG-SẴN.** Một dòng sai thì user sửa (bực ngay, 5 giây). Một ô trống thì user đóng lại. ⇒ **Không tính năng nào được phụ thuộc vào việc user nhớ phải nhập gì đó** — đó là kiểu hỏng mòn dần, không gãy, và số liệu tuần đầu luôn đẹp.
4. **Trụ = NHÃN, không phải CỔNG.** Tái dùng pattern `off_strategy` ("ý người thắng"). Chọn lệch trụ nhiều lần ⇒ gợi ý **trụ mới**.
5. **Đã duyệt thì KHÔNG tự sửa — đeo nhãn.** Kế hoạch đổi ⇒ bài đã duyệt giữ nguyên + dấu *"viết theo thông điệp cũ (12/6)"* + nút *viết lại*. (Áp §8.2 + `off_strategy`.)
6. **Khẩu vị = derived-state** (WIRING §2): `confidence` + `updated` + `why` + human-override. Max suy từ hành vi nhưng **chưng thành vài dòng NHÌN THẤY + SỬA ĐƯỢC**.
7. **Hai kênh tín hiệu khẩu vị:** **mạnh** (dùng · lưu · bỏ có lý do · edit-diff) → cập nhật khẩu vị. **yếu** (mở mà không lấy) → **KHÔNG** cập nhật; tích ≥3 lần cùng hướng mới **hỏi** user đang cấn gì (tối đa 1 câu/phiên).
8. **Không bịa** (kế thừa CLAUDE.md): thiếu bằng chứng thì nói thiếu, không lấy số yếu lấp vào.

## 9. Đường lùi (WIRING bắt buộc)

| Thiếu gì | Vòng lặp thoái xuống thành |
|---|---|
| User chưa nối page | **KHÔNG nhị phân — có tầng giữa** (làm rõ 2026-07-21). Lựa chọn (§5) + khớp bài + edit-diff/khẩu vị (§6) + **kết quả THÔ** (react/comment công khai) chạy được nhờ **cào trang công khai của chính user** (`fetch_facebook_page` chạy trên mọi page công khai), **không cần OAuth**. Chỉ **kết quả MẠNH** (reach, ❓ có mẫu số, số inbox, chi ad) mới cần nối. ⇒ chưa nối = **neo-B mức yếu vẫn có, không phải số 0**; nói thẳng *"học từ thị trường + kết quả thô của bạn, chưa thấy reach/inbox"*. Mất bậc thưởng (C) **mạnh** + mất tự sửa **đầy đủ**. |
| Ngành không ai chạy ads | Thư viện 🟢 mỏng. Ngả về 🔵/🟡/⚪ + **nói rõ chưa đủ bằng chứng**. |
| Chưa có `spine`/`messaging` | Pool vẫn chạy nhưng không neo được vào chiến lược → ý chung chung. Dẫn về `#message`. |
| Spy không lấy được data | Pool đứng yên, **không sinh ý bịa**. Ý cũ mang tuổi ngày một già. |

## 10. Chặn — phải gỡ trước khi xây

- ⚖️ **Hợp đồng ScrapeCreators + ToS Meta/TikTok** về việc **phát tán lại data cào giữa các khách hàng** (thư viện góc là chéo user). **Chưa kiểm.** ⚠️ Việc **giữ thô lâu dài** (§3b) làm câu hỏi này nặng thêm — đỡ được phần nào nhờ ranh giới **thô = vật liệu nội bộ, thẻ = sản phẩm**: thứ đi chéo user là **mẫu hình đã học**, không phải data cào nguyên bản.
- 🔐 **Quyền riêng tư inbox** — §6. Chốt "chỉ đếm" trước khi động vào Page API messages.
- 🕰️ **Không có đồng hồ.** Hiện job nằm trong **dict RAM**, user bấm mới chạy, restart là mất (`business.py` `run_agent` → `asyncio.create_task`). Vòng lặp cần **trạng thái ở DB, không phải RAM**, và mỗi lượt phải **idempotent**.
- 📋 **Không đổi schema DB** (CLAUDE.md). Chỗ chứa chốt theo phạm vi (2026-07-21): **thẻ ① per-user → `skill_runs`** (append-only, có sẵn `version`+`rating`+`feedback_text`; thẻ = content-JSON, **KHÔNG** nhét `intake_extra` vì blob load cả cục sẽ phình). **Thư viện góc chéo-user** (④) không thuộc `intake_extra` của ai ⇒ **chỗ chứa vẫn là câu hỏi mở** (cần queryable thật, không phải JSON-in-text — khác thẻ ①).
- 🗄️ **Vòng lặp yêu cầu Supabase — SQLite dev là no-op IM LẶNG** (phát hiện 2026-07-21). `insert_skill_run` + `tracked_competitors` đi qua Supabase client; chạy SQLite mặc định (`webapp/store.py`) thì `get_client()` trả `None` và **insert nuốt lặng, không lỗi** (`storage/v2/skill_runs.py:29-31`). ⇒ §11 "đã có sẵn `skill_runs`/`idx_tracked_due`" **chỉ đúng trên Supabase**. Hành động: (1) tuyên vòng lặp chạy trên Supabase, dev phải set `SUPABASE_URL`; (2) **hàng GAP cho người xây ①** — sửa `insert_skill_run` **kêu lên** (log/raise) khi thiếu client TRƯỚC khi bật loop, nếu không thẻ mất mà log vẫn xanh (đúng bẫy §8.3). Ghi vào Sổ hợp đồng WIRING lúc brief ① (theo hai-tốc-độ WIRING: mối nối cục bộ làm JIT tại brief-time, không sửa `WIRING.md` bây giờ).

## 11. Đã có sẵn trong repo (chưa xác minh sâu)

- `tracked_competitors` — có `user_id`, `is_active`, `last_check_at`, và index `idx_tracked_due(last_check_at, is_active)`. **Index đó chỉ có một công dụng: quét "ai tới hạn kiểm"** ⇒ vòng-spy-theo-user **đã được thiết kế từ trước và chưa bao giờ xây**. ⚠️ **Chỉ tồn tại trên Supabase** — SQLite dev không có bảng này (xem §10 🗄️).
- FB OAuth + `user_fb_connections` + `ads_snapshots` — hạ tầng nối page đã có. (Tên bảng thật là `user_fb_connections`, `supabase_full_schema.sql:494` — bản cũ ghi tắt `fb_connections`, sửa 2026-07-21.)
- `brain/` + `webapp/brain.py` loader + linter `py brain/_check.py` — bộ khung vault (xem §3, **khác** brain này).
- `skill_runs` cộng dồn, bản mới thắng — **đã lưu lịch sử**, chưa ai đọc phần chênh.
- `off_strategy` — pattern gắn cờ không chặn, tái dùng ở §8.4/§8.5.
- `TaskType.CRITIC_REVIEW` trong `llm_router.py` — định tuyến theo vai đã có.
- `agents/` — thư viện prompt dùng chung ⇒ **một phòng ban = prompt + TaskType + hợp đồng in/out**, không phải hạ tầng mới.
- 🔑 **`audit_social_page()` + `SOCIAL_PAGE_AUDIT_SYSTEM`** (`business.py:7262` · `operational_prompts.py:2035`) — **~70% thợ đọc, đã chạy thật**, xem §3b. Kèm `tools/scrapecreators.py` (FB profile+posts+ads, TikTok video+transcript) và `tools/krillin_client.py` (ASR Whisper bù transcript null) ⇒ **đường lấy thô đã thông cho cả FB và TikTok**.
- `skill_runs` skill `social_page_audit` — đã chứa báo cáo thật của các page đã chạy ⇒ **(C) soi mẫu có nguyên liệu ngay**, không phải chờ gom data mới.

## 12. Thứ tự xây — CHỐT

> Chốt 2026-07-20. Phương án **A**: chạy ①②③ ngay, **kiểm pháp lý song song**, đèn xanh thì làm ④.

| | Bước | Vì sao ở đây | Cần gì trước |
|---|---|---|---|
| **①** | **Tách `audit_social_page` thành 2 đầu ra** → thẻ có nhãn, **chạy theo yêu cầu**, chỉ soi đối thủ của **chính user đó** | Bước **chứng minh cược**: *ý mang bằng chứng khiến user dám chốt*. Không cần đồng hồ, không cần đèn xanh pháp lý (không phát tán chéo khách) | — (đường lấy thô đã thông, §11) |
| **②** | **Móc attribution** — nối bài đã đăng về đúng thẻ (§6) | **Cùng đợt với ①, không phải sau.** Bài đăng lúc chưa có móc là **mất dấu vĩnh viễn** — B là cái neo, neo không thả muộn được. Nhặt luôn **edit-diff ⇒ khẩu vị** | FB OAuth (đã có) |
| **③** | **Đồng hồ** — trạng thái job ở DB, idempotent | Chỉ đáng bật khi **đã có thứ đáng chạy mỗi đêm**. Bật sớm = trả tiền cho vòng quay rỗng | ① chạy được |
| **④** | **Thư viện góc chéo user + nhãn 🔵** | Cần cả **lượng** lẫn **đèn xanh pháp lý** | ①②③ + §10 pháp lý |

**(C) soi mù chạy được ngay từ ①** — `skill_runs` đã có báo cáo thật làm nguyên liệu.

**① cố tình thiếu 🔵** ⇒ đang kiểm cược bằng bộ nhãn **yếu hơn bản thật**. Nếu ① thất bại phải đọc kết quả cẩn thận: có thể cược đúng mà chỉ là **🟢 một mình không đủ mạnh**.

**① phải ĐO ĐƯỢC, không chỉ trích-xuất** (chốt 2026-07-21): ① là *bước chứng minh cược*, mà cược không đo được thì chưa chứng minh gì (§8.3: cấm cột mốc rỗng — trông-xong-mà-hổng, tuần đầu đẹp rồi mòn). ⇒ deliverable ① gồm **ba thứ, không tách rời**:
1. **Thẻ có nhãn** (phần trích-xuất) — như trên.
2. **Bề mặt tối thiểu** — thẻ hiện ở **đúng chỗ user đang quyết** (ô trống trong lịch/chiến dịch, §4), **không** nằm im trong DB. Không bề mặt = không đo được "user dám chốt". (Đây là lý do chọn gộp vào ① thay vì tách ①b: một ① không đo được là cột mốc rỗng.)
3. **Log sự kiện A từ ngày đầu** — user chọn/bỏ thẻ nào (`skill_runs.rating`/`feedback_text`). Không đặt sớm = mất dấu như móc B.

**Thước pre-register (chốt TRƯỚC khi chạy, để "đọc kết quả cẩn thận" không thành đọc-theo-ý-muốn):** sau **N tuần**, **≥X% thẻ được bày dẫn tới một hành động chốt/lưu**. ⚠️ `N`/`X` **cần user điền trước khi bật ①** — để trống là **cố ý**, không phải quên. (Không đo tới đơn — §5 đã chốt dừng ở "chốt/hỏi".)

### ⚖️ Kiểm pháp lý: khởi động NGAY, không để tới ④

Chặn ở §10 **không chỉ chặn ④ — nó quyết định §3b có tồn tại hay không.** Nếu đáp án là KHÔNG được dùng chéo khách: vault Max **co lại thành nhiều vault per-user**, 🔵 chết, "big data riêng của Max" chết, câu chuyện *phòng ban học chung cho mọi user* chết. Còn lại vẫn là sản phẩm tốt — nhưng **là sản phẩm khác**.

⇒ Biết sớm thì ① vẫn nguyên giá trị; biết muộn thì **đã xây nhầm nền**. Kiểm pháp lý tốn **thời gian chờ**, không tốn **công làm** ⇒ chạy song song, đừng ngồi chờ.

**Chi phí nếu ④ bị chặn — cắm van sẵn (E1, chốt 2026-07-21):** cổ tức *"đọc một lần dùng chung"* (§3b) **chỉ hiện thực ở ④** (chéo user). Ở ①②③ thợ đọc chạy **per-competitor-per-user** = trả đủ tiền model-mạnh mà **chưa được khấu hao**. Nếu ④ bị chặn, ①②③ **vẫn đáng giữ** (giá trị per-user thật) nhưng phải rẻ hơn ⇒ cắm sẵn **cửa lọc rẻ** phía trước (*"bài này có phải nội dung thật không, hay chỉ 'chúc mừng năm mới'"*) rồi mới thả model mạnh vào phần sống sót (đúng van §4). Đường (b) học-từ-lựa-chọn (§3, sạch pháp lý) cũng tự làm nhẹ chỗ này — không tốn model-mạnh-mỗi-bài.

### ⚠️ Điều kiện khởi động ①

① chồng lên đúng vùng `feature/social-audit-report` đang sửa (`business.py` + `tools/scrapecreators.py`). **Đợi nhánh đó merge xong mới bắt tay vào ①**, nếu không lại đụng nhau như vụ #35/#36. ① **không đụng** Báo cáo kênh: giữ nguyên đường kéo thô + prompt 12 mục, chỉ **thêm** nhánh phát ra thẻ.
