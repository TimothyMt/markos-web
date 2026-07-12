# ScrapeCreators API — Catalog tham chiếu (repo lôi ra dùng dần)

> Nguồn: docs.scrapecreators.com (tra 2026-07-08). Đây là **"đôi mắt"** cho Max — lấy data THẬT từ
> social/ad-library mà Graph API / official API không cho. Dùng làm nền cho **Bản đồ Cầu & Sự chú ý**
> và **grounding T1-T3** (thay/bổ sung Gemini Google-Search grounding).
>
> ⚠️ Chưa build — đây là catalog để tham chiếu. Khi build xem mục §5 (khớp repo).

## 0. Cách dùng chung
- **Base URL:** `https://api.scrapecreators.com` (docs ở `docs.scrapecreators.com`).
- **Auth:** header `x-api-key: <KEY>`. Đăng ký free ở app.scrapecreators.com.
- **Giá:** credits-based, **~1 credit/request** cho các endpoint chính. **Không rate limit cứng** (khuyến nghị <500 concurrent).
- **Format:** REST, trả JSON. Mã lỗi: 200 · 400 · 401 (sai key) · **402 (hết credit)** · 403 (platform chặn) · 404 · 500.
- **Tích hợp có sẵn:** REST, MCP, CLI, n8n, Apify, Agent Skill.
- **Triết lý dùng trong Max:** ScrapeCreators = **MẮT (data thật)** → LLM = **NÃO (gom cụm, phân tầng ý định, so-what)**.
  Vì có số thật (view/like/comment/ad đang chạy) → **bớt phải gắn "(ước tính)"** (đúng luật chống bịa N-15).
- **Chi phí = credits = tiền theo lượt** → chạy **on-demand** (nút "Quét"), **cache mạnh** vào `skill_runs`, KHÔNG auto quét nền.

---

## 1. Catalog đầy đủ endpoint (theo nền tảng)

### TikTok
`GET /v1/tiktok/profile` · `/v1/tiktok/user/audience` (nhân khẩu học audience) · `/v3/tiktok/profile/videos` ·
`/v2/tiktok/video` · `/v1/tiktok/video/transcript` · `/v1/tiktok/user/live` · `/v1/tiktok/video/comments` ·
`/v1/tiktok/user/following` · `/v1/tiktok/user/followers` · `/v1/tiktok/search/users` ·
**`/v1/tiktok/search/hashtag`** · **`/v1/tiktok/search/keyword`** · `/v1/tiktok/search/top` ·
`/v1/tiktok/songs/popular` · `/v1/tiktok/creators/popular` · **`/v1/tiktok/videos/popular`** ·
**`/v1/tiktok/hashtags/popular`** · `/v1/tiktok/song` · `/v1/tiktok/song/videos` · **`/v1/tiktok/get-trending-feed`**

### TikTok Shop
`/v1/tiktok/shop/search` · `/v1/tiktok/shop/products` · `/v1/tiktok/product` (sản phẩm + review)

### Instagram
`/v1/instagram/profile` · `/v1/instagram/basic-profile` · `/v2/instagram/user/posts` · `/v1/instagram/post` ·
`/v2/instagram/media/transcript` · `/v2/instagram/reels/search` · `/v2/instagram/post/comments` ·
`/v1/instagram/user/reels` · `/v1/instagram/user/highlights` · `/v1/instagram/user/highlight/detail` ·
`/v1/instagram/song/reels` · `/v1/instagram/user/embed`

### YouTube
`/v1/youtube/channel` · `/v1/youtube/channel-videos` · `/v1/youtube/channel/shorts` · `/v1/youtube/video` ·
`/v1/youtube/video/transcript` · `/v1/youtube/search` · `/v1/youtube/search/hashtag` ·
`/v1/youtube/video/comments` · `/v1/youtube/shorts/trending` · `/v1/youtube/playlist` · `/v1/youtube/community-post`

### Facebook (organic)
`/v1/facebook/profile` · `/v1/facebook/profile/reels` · `/v1/facebook/profile/photos` · `/v1/facebook/profile/posts` ·
**`/v1/facebook/group/posts`** · `/v1/facebook/post` · `/v1/facebook/post/transcript` · **`/v1/facebook/post/comments`**

### Facebook Ad Library ⭐ (đối thủ chạy ad gì)
**`/v1/facebook/adLibrary/search/ads`** (search theo keyword) · **`/v1/facebook/adLibrary/company/ads`** (ad của 1 page) ·
`/v1/facebook/adLibrary/ad` (chi tiết 1 ad) · **`/v1/facebook/adLibrary/search/companies`** (tìm pageId từ tên)

### Google
`/v1/google/search` (SERP) · `/v1/google/company/ads` · `/v1/google/ad` · `/v1/google/adLibrary/advertisers/search`

### Ad Library khác
LinkedIn: `/v1/linkedin/ads/search` · `/v1/linkedin/ad`. Reddit: `/v1/reddit/ads/search` · `/v1/reddit/ad`.

### Nền tảng khác (đủ dùng khi cần)
LinkedIn (`/v1/linkedin/profile|company|post`) · Twitter/X · **Reddit** (`/v1/reddit/subreddit`, `/subreddit/search`,
`/post/comments`, `/search`) · Threads · Bluesky · Pinterest (`/v1/pinterest/search|pin|board`) · Truth Social ·
Twitch · Kick · Snapchat · Amazon Shop (`/v1/amazon/shop`) · FB Marketplace (search/item — qua nhóm commerce) ·
Link-in-bio (Linktree/Komi/Pillar/Linkbio/Linkme).

### Utility
`/v1/credit-balance` (xem credit còn) · `/v1/detect-age-gender`.

---

## 2. Endpoint "NÓNG" cho Max — param + trả về (đã tra chi tiết)

### 2.1 FB Ad Library — Search ads · `GET /v1/facebook/adLibrary/search/ads` — **1 credit**
- **Bắt buộc:** `query` (keyword).
- **Tuỳ chọn:** `country` (2 chữ, vd `VN`) · `status` (ALL/ACTIVE/INACTIVE, mặc định ACTIVE) ·
  `media_type` (ALL/IMAGE/VIDEO/MEME/…) · `search_type` (keyword_unordered/keyword_exact_phrase) ·
  `sort_by` (total_impressions/relevancy_monthly_grouped) · `start_date`/`end_date` (YYYY-MM-DD) · `cursor` · `trim`.
- **Trả:** `searchResults[]` mỗi ad: `page_name`, `page_id`, `is_active`, `snapshot{body.text, images[], videos[],
  display_format, cta_type}`, `start_date`/`end_date`, `total_active_time`, `publisher_platform[]`, `page_categories[]`;
  + `searchResultsCount`, `cursor`. *(cap ~1500 results/GET — nhiều hơn thì dùng POST.)*

### 2.2 FB Ad Library — Company ads · `GET /v1/facebook/adLibrary/company/ads` — **1 credit**
- **Bắt buộc:** `pageId` HOẶC `companyName`.
- **Tuỳ chọn:** `country` · `status` · `media_type` · `language` · `sort_by` · `start_date`/`end_date` · `cursor` · `trim`.
- **Trả:** mỗi ad: `ad_archive_id`, `is_active`, `collation_id`/`collation_count` (nhóm campaign),
  `start_date`/`end_date` (unix), `snapshot` (text+ảnh+video+CTA), `publisher_platform`, **`spend` (khi có)**, `cursor`.
- *Tìm `pageId`:* trước tiên gọi `/adLibrary/search/companies?query=<tên>`.

### 2.3 TikTok — Search by keyword · `GET /v1/tiktok/search/keyword` — **1 credit**
- Param cụ thể docs chưa list rõ (cần thử `query`/`cursor`).
- **Trả:** mỗi video: `play_count` (view thật), `digg_count` (like), `comment_count`, `share_count`,
  author (nickname/handle/followers/verified), `desc` (caption), hashtags (`text_extra[]`), `aweme_id`, music, timestamps; + `cursor`.
- Họ hàng: `/search/hashtag`, `/search/top`, `/hashtags/popular`, `/videos/popular`, `/get-trending-feed` (trend theo vùng).

### 2.4 Voice-of-customer (nỗi đau + ngôn ngữ khách)
`/v1/tiktok/video/comments` · `/v1/facebook/post/comments` · `/v1/facebook/group/posts` ·
`/v1/tiktok/product` (review TikTok Shop) · `/v1/reddit/post/comments`. → từ ngữ + phản đối THẬT của khách.

### 2.5 Nhân khẩu học + giá
`/v1/tiktok/user/audience` (demographics audience đối thủ) · `/v1/tiktok/shop/search` + `/v1/amazon/shop` (giá + review thật).

---

## 3. Map "Bề mặt cầu" → endpoint (cho Bản đồ Cầu & Sự chú ý)
| Bề mặt | Trả lời | Endpoint chính |
|---|---|---|
| Google (cầu chủ động) | khách gõ gì · đối thủ bid gì | `/google/search` · `/google/company/ads` |
| TikTok (cầu tạo ra, TOFU) | đang hot gì, format/hashtag/sound nào lên | `/tiktok/search/keyword` · `/search/hashtag` · `/hashtags/popular` · `/get-trending-feed` |
| FB Ad Library (cách đối thủ bán) | góc/offer/hook/CTA đối thủ chạy | `/facebook/adLibrary/company/ads` · `/search/ads` |
| Comment/review (ngôn ngữ + đau) | khách than gì, dùng từ gì | `/tiktok/video/comments` · `/facebook/post/comments` · `/tiktok/product` · `/reddit/post/comments` |

---

## 4. Map T1-T3 (research web-owned) → chỗ "khát" data đối thủ → endpoint
> Audit prompt research thật (`agents/prompts.py`) — chỗ nào cần data đối thủ/thị trường ngoài.
> **Competitor (T1) là nơi tiêu thụ chính**; market/customer/pricing cũng hưởng lợi.

| Skill (T) | Mục trong prompt cần data ngoài | Endpoint ScrapeCreators feed vào |
|---|---|---|
| **competitor (T1)** ⭐ | 8 chiều/đối thủ: ①Positioning&Messaging · ③Content Strategy · ④Channel Distribution · ⑤Est. Spend&Scale · ⑥Audience Overlap · ⑦Pricing | ① `adLibrary/company/ads` (claim/hook trong ad) · ③ `facebook/profile/posts`+`tiktok/profile/videos` (loại/tần suất content) · ④ check hiện diện đa nền + `adLibrary` (có chạy ad?) · ⑤ `adLibrary/company/ads` (số ad active + thời gian chạy = proxy scale) · ⑥ `tiktok/user/audience` · ⑦ `tiktok/shop`/`amazon/shop` |
| competitor — **Market Gap** | Messaging Gap (narrative nào bị bỏ trống) · Channel Gap (kênh nào trống) | `adLibrary/search/ads?query=<ngành>` gom claim toàn thị trường → tìm khoảng trống; check nền tảng nào đối thủ vắng |
| **market_research (T1)** | Market Dynamics: xu hướng / timing "đây có phải lúc tốt" | `tiktok/hashtags/popular` · `get-trending-feed` · `google/search` (tín hiệu cầu đang lên/xuống) |
| **customer_insight (T2)** | Pain-Gain · JTBD · ngôn ngữ khách · nhân khẩu | comments (`tiktok/video/comments`, `facebook/post/comments`, `reddit`) · `tiktok/user/audience` |
| **psychology_pricing (T2)** | Giá đối thủ thật · phản đối về giá | `tiktok/shop/search` · `amazon/shop` · review (`tiktok/product`) |
| **swot (T3)** | (tổng hợp 4 phần trên — không cần call mới) | — |

**Cách nối kỹ thuật (khi build):** prompt competitor đã có cơ chế đọc block **"DỮ LIỆU GROUNDED"**
(`COMPETITOR_SYSTEM` `agents/prompts.py:281-284` — coi đó là nguồn sự thật chính, giữ link). → chỉ cần
**bơm kết quả ScrapeCreators (đã tóm gọn) vào block "DỮ LIỆU GROUNDED"** của user message; prompt tự bám,
tự gắn "(ước tính)" cho số không có nguồn. **Không phải sửa prompt.**

---

## 5. Khớp repo khi build (chưa làm — tham chiếu)
- **Client:** `tools/scrapecreators.py` mỏng (đặt cạnh `tools/llm_router.py`, `tools/fb_marketing.py`).
  Đọc `SCRAPECREATORS_API_KEY` từ env — **1 key hệ thống** (đúng pattern **D-005**), không phải OAuth từng user.
- **Nơi dùng đầu tiên:** grounding cho `competitor` skill trong `research_web` (`webapp/business.py` `_rw_specs`) →
  bơm vào block "DỮ LIỆU GROUNDED". Sau đó mở rộng market/customer/pricing.
- **Lưu:** kết quả thô + tóm gọn cache vào `skill_runs` (versioned) — **không đổi schema**.
- **Degrade:** không có key → giữ nguyên Gemini Google-Search grounding hiện tại (gắn "(ước tính)"). Có key → data thật.
- **Credits:** chạy on-demand (nút "Quét cầu / Quét đối thủ"), cache theo fingerprint (ngành+đối thủ+ngày), giới hạn số call/lần.
- **Seed:** LLM sinh seed (keyword/hashtag/tên page đối thủ) từ intake + `tracked_competitors` (đã có) trước khi gọi API — seed sai → quét rác.

## Liên quan
- Bản đồ Cầu & Sự chú ý (tính năng tầng ②) — xem `roadmap.md`.
- Vòng đo-học auto-pull (tầng ④, Lô I+) có thể tái dùng client này để kéo hiệu suất bài chính chủ.
