# Báo cáo kênh (Social Page Audit) — BE xong, FE làm sau

> Trạng thái (2026-07-19): **Backend nối xong + verify chạy thật end-to-end.** FE mới ở mức
> **stub thô, cần làm lại** theo giao diện SocialLens. Note này để phiên sau dựng FE nhanh.

## 1. Cái gì đã xong (BACKEND — dùng được ngay)

Endpoint thật, đã test qua HTTP (`python run_web.py` + POST → HTTP 200, ra đủ 12 mục):

```
POST /api/biz/social/audit
body: { "url": "<link fanpage FB>", "platform": "facebook", "posts": 8, "user_id": null }
```

**Response (đây là hợp đồng FE bám vào):**
```jsonc
{
  "name": "SpeeGo Logistics Trung - Mỹ",
  "platform": "facebook",
  "url": "...",
  "dataScope": "Phân tích 6 bài đăng gần nhất",
  "provider": "anthropic_sonnet",
  "kpi": { "like": 1456, "follower": 1400, "lf": "104.00%", "rating": "Not yet rated (0 Reviews)" },
  "posts": [
    { "n":1, "date":"16/07/2026", "weekday":"T5", "react":0, "comment":0,
      "format":"Ảnh", "views":null, "text":"...", "url":"..." }
  ],
  "ads": [
    { "n":1, "format":"Video", "cta":"Nhắn tin", "active":true,
      "spend":null, "reach":null, "platforms":["FACEBOOK","INSTAGRAM"], "body":"...",
      "url":"https://www.facebook.com/ads/library/?id=..." }   // mở ad trong Ad Library
  ],
  "derived": {
    "freqPerDay": 0.5, "freqLabel": "Thấp",
    "totalReact": 0, "totalComment": 0, "avgReact": 0, "avgComment": 0,
    "formatDist":   [["Ảnh",5],["Video",1]],   // [[nhãn, số]] — cho donut
    "adFormatDist": [["Video",3]],
    "ctaDist":      [["Nhắn tin",3]],
    "weekday": { "react":[0,0,0,0,0,0,0], "comment":[0,0,0,0,0,0,0] }  // T2..CN
  },
  "analysis": [ { "n":1, "title":"Định vị Thương hiệu", "body":"<markdown>" }, ... 12 mục ],
  "analysis_markdown": "## 1. ...\n..."   // bản đầy đủ nếu muốn render 1 khối
}
```

**Lỗi:** thiếu key → `{ "error": "Chưa cấu hình SCRAPECREATORS_API_KEY..." }` (HTTP 400).
LLM hụt token (page lớn) → vẫn trả `kpi/posts/ads` + `{ "error": ... }` (HTTP 200) → FE nên hiện phần đã có + báo mục phân tích lỗi.

## 2. FE cần làm gì

1. Trang/nút "Tạo báo cáo kênh mới" (modal: **Nền tảng** ▾ · **URL** · **Mô hình phân tích**) → `POST` endpoint trên.
2. Render report: header (avatar + tên + link) · 4 thẻ KPI · lưới **Bài đăng** (n · react · comment · format) · lưới **Quảng cáo** (format · cta · active) · biểu đồ **theo Thứ/Ngày** (dùng `derived.weekday`) · **donut** định dạng/QC/CTA (dùng `formatDist`/`adFormatDist`/`ctaDist`) · **Tần suất** (`freqPerDay`/`freqLabel`) · **Tổng/TB tương tác** · **accordion 12 mục** (`analysis[]`, body là markdown → cần renderer md: bold/bullet/table/`→`).
   - **Mỗi thẻ Bài/QC bấm mở đúng bài/ads trên Facebook** (giống SocialLens): thẻ là link `posts[].url` / `ads[].url`, có icon ↗. (Backend đã trả sẵn 2 url này — post = permalink, ad = Ad Library.)
3. Trạng thái loading (call tốn ~30–90s) + xử lý `error`.

### Giao diện tham chiếu = SocialLens (theme SÁNG, sạch, accordion đánh số 01–12)
- User đã chốt: **theo SocialLens**, KHÔNG theo theme tối Max. Report có thể là overlay sáng riêng dù shell Max tối.
- 2 bản preview đúng-ý (render thật, có thể mở xem lại để bám layout):
  - SpeeGo: https://claude.ai/code/artifact/edc45d56-24eb-4cfb-8b0b-602c19ba77a2
  - Highlands: https://claude.ai/code/artifact/278ca5e0-a5cd-414a-a0db-f4ee13e8a488
- **File nguồn preview đã đưa vào repo:** [`docs/web/social-audit-preview.html`](social-audit-preview.html)
  (self-contained HTML + CSS + vẽ chart bằng **inline SVG**, KHÔNG cần Chart.js) — **copy CSS/markup + hàm
  `lineChart` / `donut` / `md` (md renderer có bảng) từ đây sang `web/` là nhanh nhất.** Mở file này bằng
  browser để xem đúng layout SocialLens (chart đa-lát + line auto-scale).

## 3. FE stub hiện có (THÔ — sửa/thay, đừng tưởng là bản cuối)

- `web/data.js` → key `channelReports` = **1 báo cáo mẫu SpeeGo** (giữ để dev FE offline không tốn credit).
- `web/data.js` nav → thêm mục `channelreport` (nhóm ④, cạnh `spy`).
- `web/app.js` → `P.channelreport` + `crLanding/crReportHTML/crMountCharts/crOpen/crFormModal` + handlers `cr-*` trong `handleAction`. **Theme TỐI, xấu — user muốn làm lại theo SocialLens.** Có thể xoá phần render, giữ khung modal + cách gọi.
- `web/styles.css` → block `/* Báo cáo kênh */` (cr-*), theme tối — thay bằng CSS SocialLens.
- **Nối API thật:** hiện nút "Tạo báo cáo" đang mở data mẫu. Đổi handler `cr-submit` → `API.post('api/biz/social/audit', {url, platform, posts})` rồi render response.

## 4. Non-obvious (đã fix, đừng phá)

- **Ngày/thứ tính SẴN ở backend** (`_fmt_ts`, unix→"16/07/2026 (T5)"). Trước đây để LLM tự đổi → nó đoán sai năm. FE cứ dùng `posts[].date/weekday` thẳng.
- **Token budget 16k** cho LLM (page hoạt động mạnh output dài; 8k bị router loại giữa câu).
- **`spend`/`reach` của ad = null** với ad thương mại (Ad Library chỉ lộ ad chính trị) — prompt tự nói rõ, đừng bịa số.
- **`topComments`** đã bơm vào input → mục ⑩ đọc được bình luận thật (chỉ khi page có comment).
- **Tổng quát mọi page**: engine không gắn page nào (đã test SpeeGo logistics + Highlands cà phê ra 2 report khác hẳn). Chỉ FE stub + data mẫu đang cứng SpeeGo.
- **Chi phí**: ScrapeCreators ~1 credit/request (1 report ≈ 4 credits: profile + posts vài trang + ads) + LLM tokens. Gọi ON-DEMAND, đã cache best-effort vào `skill_runs` (skill `social_page_audit`).

## 5. File đã đụng (mối nối)

| Lớp | File | Vai |
|---|---|---|
| Client | `tools/scrapecreators.py` (mới) | `fetch_facebook_page(url)` → profile + posts (cursor) + ads. Key: `SCRAPECREATORS_API_KEY` |
| Prompt | `agents/operational_prompts.py` | `SOCIAL_PAGE_AUDIT_SYSTEM` (12 mục, chống-bịa) + đăng ký `OPERATIONAL_SYSTEMS["social_page_audit"]` |
| Logic | `webapp/business.py` | `audit_social_page()` + `_build_social_report / _social_audit_input / _parse_audit_sections / _fmt_ts / _post_format`; **ASR: `_fill_transcripts_asr()` + gate `run_asr`** |
| ASR | `tools/krillin_client.py` | `extract_transcript()` — **yt-dlp tải → Whisper-HTTP (timestamp) / Gemini fallback**. `is_available()` gồm OPENAI/GEMINI |
| ASR util | `tools/scrapecreators.py` | `video_play_url()` (rút MP4) + `_vtt_to_text()` (dọn WEBVTT CC) |
| Route | `webapp/api.py` | handler `biz_social_audit` + `Route("/api/biz/social/audit", POST)`; nhận cờ `asr` |
| Deps | `requirements.txt` | thêm `yt-dlp` (tải video social cho ASR) |
| Env | `.env.example` | `SCRAPECREATORS_API_KEY` (+ `OPENAI_API_KEY`/`GEMINI_API_KEY` cho ASR) |
| FE stub | `web/app.js` · `web/styles.css` · `web/data.js` | **thô — làm lại theo SocialLens** |

## 5b. TikTok (đã thêm — cùng endpoint)

`POST /api/biz/social/audit` với `"platform":"tiktok"`, `url` = handle hoặc link kênh
(`@highlandscoffeevietnam` hoặc `https://www.tiktok.com/@highlandscoffeevietnam`). Đã test HTTP 200.

**Khác FB trong response:**
- `kpi`: `{ follower, heart (tổng tim), videoCount, engRate:"0.04%", verified }` — KHÔNG có `lf`/`rating`.
- `posts` (= video): mỗi item thêm `views` (thật), `share`, `save`, `hashtags[]`, **`transcript`** (lời thoại, có thể null); `react` = số like (digg).
- `ads`: **luôn `[]`** — TikTok KHÔNG có Ad Library công khai qua ScrapeCreators → mục ⑧ tự ghi rõ. (FB vẫn là kênh soi ads đối thủ.)
- `derived` thêm: `totalView`, `avgView`, `totalShare/Save`, `engRate`.
- Insight đặc thù TikTok: view khủng nhưng engRate rất thấp (Highlands: avgView 3.88M, engRate 0.04%) — mục ⑦ tự dựng bảng Like/View.

**FE:** dropdown đã có TikTok. Render nhánh theo `platform`: TikTok hiện cột **Lượt xem / Thích / Bình luận / Lưu / Chia sẻ** (giống SocialLens) + khối **Lời thoại** (`posts[].transcript`) khi có; ẩn phần Quảng cáo.

### Scripts (lời thoại video) — như SocialLens ✅ ĐÃ NỐI ASR + TEST THẬT
Field `posts[].transcript`. Thiết kế **ASR-first** (đã đo thực tế mới chốt vậy):

- **Vì sao KHÔNG dùng CC của ScrapeCreators làm chính:** `/tiktok/video/transcript` khi CÓ trả về là
  **WEBVTT thô + auto-dịch TIẾNG ANH** (test @thaiduongfulfillment: CC = *"What is Fullhuman… order
  fulfillment… Phu Phu Phu Uman"* — sai ngôn ngữ + méo), vô dụng cho audit tiếng Việt. Whisper đọc
  audio ra **tiếng Việt sạch**: *"Fulfillment là dịch vụ hoàn tất đơn hàng…"*.
- **Luồng chính (khi có OPENAI/GEMINI key):** `audit_social_page` đặt `run_asr=True` → **BỎ gọi CC**
  (khỏi tốn credit + khỏi dính WEBVTT Anh) → `_fill_transcripts_asr()` đưa **URL TRANG XEM** video cho
  `krillin_client.extract_transcript()`:
  - **Tải = yt-dlp** (`requirements.txt`) — bền với CDN TikTok. ⚠️ **httpx GET thẳng `play_addr` = 403**
    (URL CDN ký-tạm/hết hạn) → đã bỏ, yt-dlp lấy link tải mới từ trang xem. (`video_play_url()` giữ lại
    cho fallback httpx/nền tảng khác.)
  - **Đọc = Whisper-1 qua HTTP TRỰC TIẾP** (không qua openai SDK — SDK dựng `httpx(proxies=)` chết với
    httpx≥0.28) → **verbose_json có timestamp segment** (đúng kiểu SocialLens). **Fallback = Gemini 2.5-flash**
    đọc thẳng video (không timestamp) khi thiếu OpenAI key / Whisper lỗi.
  - Best-effort: tải/đọc 1 video hỏng → video đó null, KHÔNG chặn report. Cap `limit`=số video, Semaphore 2,
    timeout 180s/video. **Test thật:** 2 video (7.79MB+5.18MB) tải + Whisper xong **20s**, ra VN sạch.
- **Phương án chót (KHÔNG có ASR key):** `run_asr=False` → vẫn lấy CC ScrapeCreators, nhưng **đã dọn WEBVTT**
  → text (`scrapecreators._vtt_to_text`); ngôn ngữ có thể vẫn Anh (giới hạn của CC).
- **Key:** Whisper cần `OPENAI_API_KEY`; Gemini cần `GEMINI_API_KEY` (Anthropic KHÔNG đọc audio). Chi phí thêm:
  Whisper ~$0.006/phút/video + băng thông tải (yt-dlp, vài MB). Tắt ASR/lượt: body `{"asr": false}`.
- FE: hiện `posts[].transcript` trong khối **Lời thoại** khi có (CC-dọn hay ASR — cùng field).

## 6. Chạy thử
```bash
# cần SCRAPECREATORS_API_KEY + ≥1 LLM key trong env
python run_web.py
curl -X POST localhost:8000/api/biz/social/audit \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.facebook.com/highlandscoffeevietnam","platform":"facebook","posts":6}'
# TikTok:
curl -X POST localhost:8000/api/biz/social/audit \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@highlandscoffeevietnam","platform":"tiktok","posts":6}'
```
