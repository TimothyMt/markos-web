# [S2-DM] Bản đồ Cầu & Sự chú ý — grounding đối thủ bằng ScrapeCreators

> Tầng ② (Chiến lược). Tính năng MỚI (không phải vá bug). Ngấu nghiến cùng D-048.
> Reference API: `docs/web/references/scrapecreators-api.md`. North-star nhỏ: **cho Max đôi
> mắt data thật** (social + ad-library) thay vì chỉ Gemini Google-Search → research dày lên,
> bớt "(ước tính)", trực tiếp trị N-08 (playbook mỏng vì research mỏng).

## Vấn đề (vì sao)
Research T1-T3 hiện grounding **chỉ bằng Gemini Google-Search**. Ở VN cầu & sự chú ý sống
trên **TikTok / FB / page đối thủ** nhiều hơn Google → Max "mù" phần lớn dữ liệu thật:
đối thủ đang chạy ad gì (hook/offer/CTA), content nào đang lên, khách than gì bằng từ gì.
Thiếu số thật → nhiều "(ước tính)", playbook (T5) mỏng theo (N-08).

## Kết quả mong muốn
User bấm **"Quét đối thủ / cầu"** trên trang research → Max gọi ScrapeCreators lấy data THẬT
(ad đối thủ + content đang hot + comment), **tự lọc-gom-tóm gọn**, bơm vào block "DỮ LIỆU
GROUNDED" của prompt competitor → output research **dẫn số thật có nguồn** (không phải số đoán),
và **hết mỏng**. User có thể chạy lại (tốn credit) và xem lần quét đã cache.

## Phạm vi
- **TRONG (v1):**
  - Client mỏng `tools/scrapecreators.py` (1 key hệ thống, đọc env — pattern D-005).
  - **2 bề mặt v1:** FB Ad Library (đối thủ chạy ad gì) + TikTok (content/hashtag đang lên).
    *(Comment/review = v1.1; Google volume/DataForSEO = v2 — xem Non-goal.)*
  - **Pipeline 5 tầng lọc data** (mục "Xử lý dữ liệu" dưới) — xương sống chống "rối & quá nhiều".
  - Nối vào **`competitor` skill** trong `research_web` (`business.py _rw_specs`): bơm kết quả đã
    tóm gọn vào block "DỮ LIỆU GROUNDED" của user message. **KHÔNG sửa prompt** (`COMPETITOR_SYSTEM`
    `agents/prompts.py:281-284` đã đọc block này làm nguồn sự thật).
  - Nút FE **"Quét cầu / đối thủ"** (on-demand) + trạng thái + hiển thị "đã quét lúc X, N nguồn".
  - Cache kết quả (thô + gọn) vào `skill_runs` versioned — **không đổi schema DB**.
  - Degrade: không có key / lỗi 402 hết credit → giữ nguyên Gemini grounding hiện tại (như cũ).
- **NGOÀI (non-goal v1):**
  - Google search volume / DataForSEO (v2).
  - Trang "Bản đồ Cầu" trực quan riêng (dashboard 4 bề mặt) — v1 chỉ *feed vào research*, chưa vẽ trang.
  - Auto quét nền / lịch quét định kỳ (tốn credit — chỉ on-demand).
  - Mở rộng sang market/customer/pricing (audit §4 đã map — làm sau khi competitor chạy tốt).
  - Tái dùng cho vòng đo-học tầng ④ (ghi nhận, làm ở Lô I+).

## Luồng / màn hình
1. Trang research (sau intake, trước/khi chạy `competitor`) có nút **"🔍 Quét đối thủ (data thật)"**.
2. Bấm → backend: **seed** (LLM rẻ sinh keyword/hashtag + resolve pageId đối thủ từ `tracked_competitors`)
   → **gọi API** (cap số call/lần) → **pipeline lọc** → lưu cache `skill_runs('demand_scan')`.
3. FE hiện trạng thái ("đang quét… / xong: N ad · M video · đã gom K cụm") + thời điểm quét.
4. Khi user chạy `competitor` → business đọc cache `demand_scan` mới nhất → **ghép vào block
   "DỮ LIỆU GROUNDED"** → output competitor dẫn số thật.
5. Chạy lại "Quét" = bản `skill_runs` mới (versioned, bản mới thắng — pattern N-01).

## Dữ liệu
- **Đọc:** `profile.intake_extra` (ngành/sản phẩm/khách để seed) + `tracked_competitors` (đã có,
  `bizCompetitors` — page/handle đối thủ).
- **Ghi:** `skill_runs` skill=`demand_scan` — payload gồm `{raw_trimmed, refined, fingerprint, scanned_at, credits_used}`.
  **KHÔNG thêm cột/bảng.** Fingerprint = hash(ngành + set đối thủ + ngày) để tránh quét lặp.
- **Env:** `SCRAPECREATORS_API_KEY` (1 key hệ thống). Thiếu → degrade.
- **Nối:** `research_web` đọc `demand_scan` mới nhất, string-ify phần `refined` vào block GROUNDED.

## Xử lý dữ liệu — pipeline 5 tầng (xương sống chống "rối & quá nhiều")
> Nguyên tắc: **KHÔNG BAO GIỜ đổ data thô vào LLM synthesis.** Rẻ hoá + thu nhỏ trước, LLM mạnh chỉ gặp phần đã gom.

| Tầng | Việc | Ai làm | Vì sao |
|---|---|---|---|
| **0. Seed** | LLM rẻ sinh keyword/hashtag + resolve `pageId` đối thủ (`adLibrary/search/companies`) từ intake+tracked | LLM nano/mini | seed sai → quét rác; rẻ |
| **1. Fetch** | Gọi ScrapeCreators (`adLibrary/company/ads`, `tiktok/search/keyword`…), **cap số call/lần** | code | kiểm soát credit |
| **2. Refine** | **dedupe** (gộp ad trùng theo collation_id, video trùng id) · **rank** theo SỐ THẬT (total_active_time / play_count / comment_count) · **trim top-N** (vd 10/đối thủ) · vứt field thừa | **code, KHÔNG LLM** | cắt 90% noise miễn phí; giữ tín hiệu mạnh |
| **3. Extract** | mỗi item top-N → LLM rẻ trích **schema gọn** `{hook, offer, cta, angle, format, metric}` | LLM nano/mini (rẻ, cache) | biến text lộn xộn → cấu trúc; song song |
| **4. Cluster** | gom theo **góc/hook/offer** → đếm tần suất → tìm **khoảng trống** (narrative/kênh nào bị bỏ) | code (gom key) + LLM rẻ (đặt tên cụm) | ra "cụm" không phải "list dài" |
| **5. Synthesize** | LLM MẠNH (competitor prompt) gặp **cụm + số**, ra so-what/market-gap | LLM mạnh (đã có) | não chỉ thấy tín hiệu đã lọc |

Output tầng 4 (thứ bơm vào GROUNDED) = **gọn**: vài cụm góc + top hook có số + khoảng trống, KHÔNG phải trăm dòng thô.

## Acceptance (done = kiểm thế nào)
- [ ] Có key + bấm "Quét" → gọi API thật, lưu `skill_runs('demand_scan')`, FE hiện "đã quét N nguồn / K cụm".
- [ ] Chạy `competitor` sau khi quét → output **dẫn số thật** (view/ad active) trong phân tích, ít "(ước tính)" hơn rõ rệt.
- [ ] **Không** key / lỗi 402 → research vẫn chạy bằng Gemini grounding như cũ (không crash, không nút chết).
- [ ] Quét lại → bản `skill_runs` mới thắng (không đẻ trùng), fingerprint chặn quét lặp cùng ngày.
- [ ] Pipeline trim: raw > top-N → block GROUNDED bơm vào chỉ còn phần gọn (kiểm bằng độ dài payload `refined`).
- [ ] `python3 -c "import webapp.business, webapp.api"` + `node --check web/app.js` pass. Test `test_demand_scan`.

## Phụ thuộc
- `tracked_competitors` (đã có) để có đối thủ mà quét. Không có đối thủ → seed từ keyword ngành (vẫn chạy được).
- Không phụ thuộc R-1; nhưng **R-1 nên xong trước** để biết baseline research "mỏng" tới đâu (đo cải thiện).

## Câu hỏi mở (?) — cần chốt trước khi code
1. **(?) Độ sâu v1:** gọn (~10 item/đối thủ, 3-5 đối thủ, ~1 keyword TikTok) **[đề xuất]** vs sâu (nhiều hơn).
   Ảnh hưởng credit/lần. Đề xuất: **gọn** cho v1, mở rộng sau khi thấy chất lượng.
2. **(?) Cap credit/lần quét** — đặt trần cứng bao nhiêu call/lần (vd ≤15)? Có cảnh báo trước khi tiêu credit không?
3. **(?) v1 có gồm comment/review (voice-of-customer) luôn hay để v1.1?** Đề xuất: **để v1.1** (v1 tập trung ad + content).
4. **(?)** Quyết định key: dùng chung quota-per-user như LLM (D-005) hay credit ScrapeCreators tách riêng, đếm sao?
