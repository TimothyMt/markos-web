# Slice VL1 — "Học từ video viral": nối skill đã có vào Max + vá đường tải + chồng cụm/công thức

> **⚠️ ĐỌC MỤC NÀY TRƯỚC — nếu không sẽ xây lại thứ đã tồn tại.**
> Repo **ĐÃ CÓ** skill `viral_video_analyzer` hoàn chỉnh (9 section, chất lượng cao):
> - `agents/operational_prompts.py` → `VIRAL_VIDEO_ANALYZER_SYSTEM` — prompt 9 section: hook breakdown (**9 công thức**), story structure + nhận diện framework, pacing/re-hook, verbal pattern, emotional trigger + cognitive bias, CTA design (8 loại), **8.1 template fill-in-the-blank**, replication risk, variation ideas, production brief (shot list + 3 script hoàn chỉnh).
> - `agents/operational_skills_config.py` → `ViralVideoAnalyzerSkill` (class, thời bot — dùng `Session`).
> - `tools/krillin_client.py` — transcript + segments + timestamp (KrillinAI → Whisper API → user paste).
> - `tools/video_vision.py` — ffmpeg keyframes + Claude vision (shot type, on-screen text).
>
> **VL1 KHÔNG viết lại prompt phân tích.** CLAUDE.md: *"business.py tái dùng prompt bot (`agents.operational_prompts`) qua import lazy/try-except — đây là **chủ ý để giữ chất lượng, đừng thay bằng prompt tự chế mỏng**."*

## Mục tiêu — lấp 5 khoảng trống THẬT
Skill đã giỏi nhưng **founder không với tới được**, và **đường tải video của nó hỏng**. VL1 lấp đúng những chỗ đó:

| # | Khoảng trống thật | Vì sao |
|---|---|---|
| **1** | **Skill không nối vào web app** | `git grep viral_video_analyzer -- webapp/ web/` → **0 kết quả**; cũng KHÔNG có trong `OPS_SKILL_TASK_TYPES` của router. Code thời bot mắc kẹt trong `agents/` |
| **2** | **Đường tải video hỏng** | `krillin._ensure_local_file()` chỉ `httpx.GET` thẳng URL → với `facebook.com/reel/123` nó tải về **trang HTML login**, không phải video. Đường `KRILLIN_BINARY` thì code tự thú *"Giả định convention… nếu binary khác CLI shape cần adapt"* = **chưa verify** |
| **3** | Không có stats tương tác | share/save/comment-rate → lọc "thật hay vs may mắn" |
| **4** | Chỉ phân tích **1 video** | công thức n=1 = đoán; cần **cụm** mới đáng tin |
| **5** | Kết quả là báo cáo HTML, **không chảy vào gen bài** | `accumulate_to_report=False`; công thức 8.1 không ai tiêu thụ |

## Quyết định nền (đã chốt — đừng lật)
- **Engine "xem" = Gemini** (thay `krillin` + `video_vision`): 1 call đa phương thức, **không cần ffmpeg, không cần KRILLIN_BINARY** (Railway đỡ phải cài binary; krillin CLI chưa verify). Gemini trả **đúng shape** mà prompt 9-section đang chờ (transcript có timestamp + visual block) → **prompt giữ nguyên, chỉ thay engine**. Đã chứng minh bằng prototype trên 2 FB Reel thật.
- **Hook taxonomy chuẩn = 9 công thức trong `VIRAL_VIDEO_ANALYZER_SYSTEM`** (đã tôi luyện, có VN context). **KHÔNG** đụng 5 nhóm hook của `gen_calendar_post` (tránh xung đột 3 chiều). Cầu nối map 9→5 khi cần set `hook_style`; chất lượng bài đến từ **template 8.1**, không từ nhãn hook.
- **Lưu trữ (không đổi schema):** artifact → `skill_runs` (`video_analysis`, `video_cluster`); thư viện công thức → `intake_extra.video_formulas` (**derived-state**: `confidence/updated/why/by`; `by:"human"` → Max không đè).
- **Degrade contract 3 tầng:** ① tải + phân tích sáng tạo (gendownload+Gemini) = **LUÔN có** · ② stats công khai (ScrapeCreators) = **tuỳ nền tảng** (đủ TikTok/IG, chỉ view ở FB) · ③ retention curve = **KHÔNG nguồn nào** (đừng đi tìm).

## Đọc trước + cách tự định vị code
`AGENTS.md` (luật môi trường) · `CLAUDE.md` · `docs/cmo/WIRING.md`. **Tự grep, brief này cố ý KHÔNG ghi số dòng:**
```
git grep -n "VIRAL_VIDEO_ANALYZER_SYSTEM" -- agents/
git grep -n "class ViralVideoAnalyzerSkill" -- agents/
git grep -n "def extract_transcript\|def _ensure_local_file" -- tools/krillin_client.py
git grep -n "def gen_calendar_post\|def _messaging_anchor_from\|def biz_data" -- webapp/
git grep -n "OPS_SKILL_TASK_TYPES" -- tools/llm_router.py
```
Quét caller phải quét **cả `tests/`**.
**Branch:** cắt từ `staging`, PR `--base staging`. KHÔNG tự merge. **FE 1 nguồn** (`web/app.js`…), không mirror.

## Sổ hợp đồng WIRING
| Khoá | Kiểu | Consumer | Producer | Status |
|---|---|---|---|---|
| `local_path` + `meta` | dict | F2 | **F1** `extract_media` | ✅ build |
| transcript block + visual block | str (shape krillin/video_vision) | prompt 9-section (đã có) | **F2** Gemini watcher | ✅ build — shape PHẢI khớp cái prompt đang chờ |
| `skill_runs['video_analysis']` | blob | FE, F6 | **F3** | ✅ build |
| `OPS_SKILL_TASK_TYPES['viral_video_analyzer']` | TaskType | router `_run_skill` | **F3** (thêm entry) | ❌ **thiếu producer hiện tại** → F3 vá |
| `stats{view,like,comment,share,save}` | obj **nullable** | F5 lọc, FE | **F4** ScrapeCreators | ⚠️ nullable — consumer PHẢI degrade |
| `skill_runs['video_cluster']` | blob | FE, F6 | **F5** | ✅ build |
| `intake_extra.video_formulas` | list[obj] | **F6** `gen_calendar_post`, FE | **F6** + founder curate | ✅ derived-state |
| `formula_id` | str | `gen_calendar_post` | FE nút "Viết bài từ công thức" | ✅ |

---

## F1 — `extract_media(url)` : vá đường tải (gendownload)
**Mối nối:** ĐỌC `url`. GHI: trả dict cho F2 (không chạm DB). Derived-state? Không. Degrade: lỗi → `{"ok": False, "error"}`, **KHÔNG raise**.
**Sự thật đã kiểm (đừng khám phá lại):**
- `POST https://gendownload.com/api/extract` body `{"url":"..."}` → JSON `{title, thumbnail, source, formats[]}`.
- ⚠️ **Chặn UA mặc định của Python → 403.** Phải gửi `User-Agent: Mozilla/5.0` cho **cả extract lẫn tải file**.
- ⚠️ `duration` = null; **view/reactions bị nhét trong chuỗi `title`** (`"15K views · 186 reactions | <caption>"`) → phải parse ("15K"/"1.2M" → số).
- Đã test thật: FB Reel 83s → SD mp4 ~2.8MB.
**Contract:** `async def extract_media(url) -> {"ok", "source", "title", "caption", "view", "reactions", "duration", "thumbnail", "local_path"}`.
**Đặt ở:** `tools/video_source.py` (mới) — đúng pattern tích hợp ngoài. Dùng `httpx` (đã có, **đừng thêm dep**).

## F2 — Gemini watcher : thay krillin + video_vision, GIỮ prompt
**Mối nối:** ĐỌC `local_path` (F1). GHI: trả **transcript block + visual block đúng shape prompt 9-section đang chờ** (xem `krillin_client.format_transcript_for_prompt` + `video_vision.extract_visual_analysis` để khớp). Derived-state? Không (F3 mới suy). Degrade: Gemini lỗi/safety → rơi về `krillin_client` cũ; cả hai lỗi → cho user paste transcript (skill vẫn chạy).
- Thêm đường video vào `tools/llm_router.py` (Files API: upload → chờ `state==ACTIVE` → `generate_content`). **SDK sync** → bọc `asyncio.to_thread` hoặc `client.aio`. Model `gemini-2.5-pro`.
- Trả dict **cùng shape** `krillin_client.extract_transcript` (`transcript, segments[{start,end,text}], duration_seconds, language, source, local_video_path`) → prompt 9-section dùng được **không sửa gì**.

## F3 — Nối skill vào web app ⭐ (khoảng trống lớn nhất — sau F3 tính năng đã DÙNG ĐƯỢC)
**Mối nối:** ĐỌC profile + `synthesis` (từ `skill_runs`, để tailor công thức — xem `ViralVideoAnalyzerSkill.build_context` làm mẫu). GHI `skill_runs['video_analysis']` + thêm entry vào `OPS_SKILL_TASK_TYPES`. Degrade: thiếu synthesis → vẫn chạy với profile.
- `webapp/business.py`: `async def analyze_viral_video(user_id, url, platform="", niche_context="", creator_persona="", why_picked="")` — **lazy import** `agents.operational_prompts.VIRAL_VIDEO_ANALYZER_SYSTEM`, dựng user message theo dữ liệu web-era (KHÔNG dùng `Session` thời bot), gọi F1+F2 rồi router, lưu skill_run.
- `webapp/api.py`: handler + `Route(...)` trong `api_routes()`.
- `tools/llm_router.py`: thêm `"viral_video_analyzer": TaskType.OPS_ANALYSIS` (hoặc TaskType hợp lý — **tự quyết + giải thích**). Thiếu entry → rơi `GENERIC_CREATIVE`, dồn tải Sonnet.
- `biz_data()`: expose `bizVideoAnalyses` (theo pattern `bizMessaging`).

## F4 — ScrapeCreators stats (tuỳ chọn, degrade an toàn)
**Mối nối:** GHI `stats` (nullable) vào analysis. Degrade: thiếu `SCRAPECREATORS_API_KEY`/nền tảng không hỗ trợ → `stats=None`, mọi consumer vẫn chạy.
- `tools/scrapecreators.py` (mới, `httpx`). TikTok `/v2/tiktok/video` → `statistics{play_count, digg_count, comment_count, share_count, collect_count}`; `/v3/tiktok/profile/videos?handle=`; `/search/keyword`; `/search/hashtag`. FB `/v1/facebook/post` (by url — stats mỏng, thường chỉ view).
- Skill có sẵn field `engagement_data` trong intake → đây là chỗ bơm số thật vào.

## F5 — Cụm ③ auto-discovery (nặng nhất — làm CUỐI)
**Mối nối:** GHI `skill_runs['video_cluster']`. Degrade ③→②(cụm user dán)→①(chỉ seed).
- Lọc chất lượng: **share-rate + like-rate + comment-rate** (÷view); saves cơ hội. *(Reference `last30days/signals.py` chấm engagement chỉ 10% và KHÔNG chấm share — ta làm khác vì ta mổ viral.)*
- **Bao chi phí** (pattern `last30days/scripts/lib/pipeline.py` — đọc code thật): tier độ sâu · `MAX_SOURCE_FETCHES` · `ENRICH_LIMIT`+workers+**budget đồng hồ** · **prune trước enrich** · hết budget → nomination-only, không chết · cache theo `video_id`.
- **RÀNG BUỘC CỨNG:** stats rẻ lọc rộng; **Gemini-xem-video đắt chỉ cho số ít đã lọc** (seed + top 2-3). Nở N lần bước đắt = FAIL.

## F6 — Thư viện công thức + cầu sang `gen_calendar_post`
**Mối nối:** ĐỌC section **8.1 template fill-in-the-blank** từ `video_analysis` → GHI `intake_extra.video_formulas` (derived-state). Consumer = `gen_calendar_post`. Degrade: `formula_id` rỗng → gen như cũ (0 hồi quy).
- Thêm param `formula_id: str = ""` + helper `_formula_anchor_from(extra, formula_id)` (**gương** `_messaging_anchor_from`) → prepend block *"# CÔNG THỨC VIDEO — mượn cấu trúc, KHÔNG sao chép; bẻ theo Thông điệp"*.
- **LUẬT thứ tự:** khối Công thức đặt **DƯỚI** khối Thông điệp (Thông điệp thắng — giữ giọng).
- **KHÔNG đụng taxonomy 5 nhóm hook** của `gen_calendar_post`. Cần set `hook_style` thì map 9→5 bằng bảng cố định.

## FE — tab "Học từ video viral"
Dán 1 URL seed (F5 nở cụm) *hoặc* nhiều URL thủ công → xem phân tích 9 section + thư viện công thức → nút **"Viết bài từ công thức này"** → `gen_calendar_post(formula_id=…)`. 3 lăng kính = 3 view: **B** công thức (mặc định) · **A** soi đối thủ (bản tóm) · **C** soi video mình.

---

## Thứ tự build
```
F1 → F2 → F3 ⭐(tới đây tính năng ĐÃ DÙNG ĐƯỢC — dừng lại đánh giá thật trước khi đi tiếp)
   → FE → F6 → F4 → F5 (nặng nhất, cuối)
```

## Verify (dán output THẬT vào mỗi commit — theo AGENTS.md)
```
python -m py_compile webapp/business.py webapp/api.py
node --check web/app.js
```
- Windows: `python` (không `python3`); `git --no-pager`; không có `grep`/`head`/`tail` → `git grep -n`.
- F1/F2: chạy thật **≥2 nền tảng** (1 FB reel + 1 TikTok), in source/view/đường dẫn/kích thước.
- Không có key/DB → verify tĩnh, **khai rõ** "chưa verify runtime"; ĐỪNG khai đã test.

## Cấu hình (env — KHÔNG vào DB)
`GEMINI_API_KEY` (đã có) · `SCRAPECREATORS_API_KEY` (F4, tuỳ chọn) · gendownload: không key. `google-genai` + `httpx` đã có.

## Không làm
- **KHÔNG viết lại prompt phân tích** — tái dùng `VIRAL_VIDEO_ANALYZER_SYSTEM` (lazy import). Không chế prompt mỏng.
- **KHÔNG đụng 5 nhóm hook** của `gen_calendar_post`. **KHÔNG** đổi schema DB. **KHÔNG** bịa số.
- **KHÔNG Write đè cả file** (`business.py`/`app.js` rất lớn) — chỉ **Edit chèn có mục tiêu**.
- KHÔNG để consumer đọc `stats` mà không degrade khi null. KHÔNG đi tìm retention curve (không tồn tại).
- 1 function = 1 commit → push → **chờ review PASS mới sang function sau**. KHÔNG tự merge.

## Mở — chốt sau khi có runtime thật
- Gemini watcher vs krillin+vision: so chất lượng thật rồi mới quyết bỏ hẳn 2 tool cũ hay giữ làm fallback.
- `ViralVideoAnalyzerSkill` (class thời bot) sau khi F3 nối web: giữ hay dọn? — chốt sau, đừng xoá sớm.
- Số cap/budget F5 theo latency Gemini thật.
