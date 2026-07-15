# Slice VL1 — "Học từ video viral" (mổ video ngắn → công thức → gen bài)

> **Mục tiêu:** biến 1 video ngắn viral (TikTok/Reel/Short/FB, **mọi nền tảng**) thành **công thức lặp lại được** để founder tự đẻ bài của mình — bám Thông điệp. Một cỗ máy bóc tách chung nuôi **3 lăng kính**: **B** học công thức (anchor) · **A** soi đối thủ · **C** soi video mình.
> **Đọc trước:** `AGENTS.md` (luật môi trường Windows/pager/Edit) + `CLAUDE.md` + `docs/cmo/WIRING.md` + `docs/cmo/00-PLAN.md` (4 tầng).
> **Tự tìm code bằng grep tên hàm** (ĐỪNG tin số dòng — brief này cố ý KHÔNG ghi số dòng):
> ```
> git grep -n "def gen_calendar_post\|def _messaging_anchor_from\|def biz_data" -- webapp/
> git grep -n "hook" -- webapp/business.py        # khối taxonomy hook trong system prompt gen bài
> git grep -n "insert_skill_run\|get_latest_skill_run" -- webapp/ storage/
> ```
> Cần quét caller thì quét **cả `tests/`**, không chỉ `web/` + `webapp/`.
> **Branch:** cắt nhánh mới **từ `staging`** (vd `feature/video-viral-learn`); PR `--base staging`. KHÔNG commit thẳng `main`/`staging`, KHÔNG tự merge.
> **FE 1 nguồn:** sửa thẳng `web/app.js` · `web/styles.css` · `web/index.html` — **không mirror đi đâu cả** (standalone đã khai tử).

## Bối cảnh + feasibility (ĐÃ chứng minh bằng prototype)
Prototype `reel_analyzer.py` (scratchpad) đã chạy **end-to-end trên 2 Facebook Reel thật**: gendownload tải video → Gemini "xem" (hình+audio+chữ overlay) → nhả JSON bóc tách 2 tầng đúng schema. Feasibility ✅. Những **bẫy đã phát hiện** (đưa vào code luôn):
- **gendownload chặn UA mặc định** → phải gửi header `User-Agent: Mozilla/5.0`, không thì **403**.
- gendownload trả `title` nhét sẵn view+reaction ("15K views · 186 reactions"), `duration` để `null` (nằm trong URL param) → **phải parse tay**, đừng giả định field sạch.
- Gemini Files API: `upload` → chờ `state==ACTIVE` → `generate_content(response_mime_type="application/json")`, model `gemini-2.5-pro`. **SDK sync** → trong code async phải bọc `asyncio.to_thread` hoặc dùng `client.aio`.

## Nguồn dữ liệu (3 lớp — degrade contract)
| Tầng | Nguồn | Đảm bảo | Key |
|---|---|---|---|
| Tải + bóc tách sáng tạo (hook/cấu trúc/nhịp/transcript) | **gendownload** (free) + **Gemini** | ✅ LUÔN có, mọi nền tảng | `GEMINI_API_KEY` (đã có) |
| Stats công khai (share/like/comment-**rate**) | **ScrapeCreators** | ⚠️ tuỳ nền tảng: đủ TikTok/IG, chỉ view ở FB | `SCRAPECREATORS_API_KEY` (mới, env — KHÔNG vào DB) |
| Retention curve (watch-through/drop-off) | — | ❌ không nguồn nào, trừ lăng kính C (user tự dán analytics) | — |

**Luật degrade:** thiếu ScrapeCreators (nền tảng không hỗ trợ / hết credit / thiếu key) → ③ rơi về ② (chỉ cụm user dán) → rơi về ① (chỉ seed). **Function không bao giờ chết.**

## Kiến trúc lưu trữ (KHÔNG đổi schema DB)
| Dữ liệu | Kho | Ghi chú |
|---|---|---|
| Bản bóc tách 1 video (atom) + cụm ③ | `skill_runs` (`video_analysis`, `video_cluster`) | artifact lớn, append-only, versioned |
| **Thư viện công thức** (`cong_thuc` ô-điền, tái dùng) | `intake_extra.video_formulas` (list) | config nhỏ, founder curate; **derived-state** |
| Config nguồn (nền tảng chính, cap độ sâu) | `intake_extra` | KHÔNG cột mới |

`video_formulas[i]` = derived-state (Max tự rút) → theo WIRING luật derived-state:
```json
{ "id": "...", "loai": "<hook-slug 10-taxonomy>", "template": "Mình đã kiếm được [TIỀN] trong [THỜI_GIAN] khi làm [NGHỀ]",
  "cac_o_dien": ["TIỀN","THỜI_GIAN","NGHỀ"], "nganh_ap_dung": ["nail","spa"],
  "confidence": 0.0, "updated": "<iso>", "why": ["<tín hiệu>"], "by": "max|human", "source_video_id": "..." }
```
`by:"human"` (founder sửa/pin) → Max **KHÔNG tự đè**. Confidence thấp → giữ, cờ "cần thêm mẫu". Lật A→B→A → freeze + cờ review.

## Hook taxonomy — 10 loại, SINGLE SOURCE OF TRUTH (khoá seam)
Định nghĩa **1 hằng số** dùng chung cho **analysis `loai_hook` ↔ generation `hook_style` ↔ FE dropdown** → producer=consumer khớp enum theo thiết kế (hết seam lệch 5↔10). Đặt ở `webapp/business.py` (hoặc `tools/` nếu dùng chung):
```python
HOOK_TAXONOMY = [  # (slug, nhãn VN, mô tả sắc cho prompt)
  ("curiosity","Tò mò","khe tò mò/paradox/câu hỏi tiết lộ"),
  ("contrarian","Tương phản","đảo niềm tin phổ biến"),
  ("emotional","Cảm xúc","chạm pain thật"),
  ("authority","Góc chuyên gia","POV người trong nghề"),
  ("storytelling","Kể chuyện","kéo vào câu chuyện/đồng cảm trải nghiệm"),
  ("listicle","Danh sách","N cách / N lỗi / N bước"),
  ("how-to","Hướng dẫn","giải pháp tức thì, làm được ngay"),
  ("challenge","Thách thức","đố/thử thách, dám xem tiếp"),
  ("trend-jacking","Bắt trend","mượn sóng format/audio đang nóng"),
  ("visual-interrupt","Ngắt hình","hành động/hình gây khựng, không chỉ lời"),
]
```
Nguồn: taxonomy research (FluxNote 10-type, đối chiếu 2 reel thật). 5 nhãn đầu là 5 nhóm VN cũ (founder quen).

## Sổ hợp đồng WIRING (khoá xuyên component)
| Khoá | Kiểu | Consumer | Producer | Status |
|---|---|---|---|---|
| `skill_runs['video_analysis']` | JSON blob | FE (view), F3 cụm, F4 rút formula | **F2** `analyze_video` | ✅ build |
| `skill_runs['video_cluster']` | JSON blob | FE (view A), F4 | **F3** `discover_cluster` | ✅ build |
| `intake_extra.video_formulas` | list[obj] | **F5** `gen_calendar_post`, FE thư viện | **F4** `extract_formulas` (+ founder curate) | ✅ build; derived-state |
| `loai_hook` / `hook_style` | slug ∈ `HOOK_TAXONOMY` | F2 analysis + F5 gen | `HOOK_TAXONOMY` (1 hằng) | ✅ khớp 2 đầu by design |
| `formula_id` | str | `gen_calendar_post` | FE nút "Viết bài từ công thức" | ✅ |
| `stats` (view/like/comment/share) | obj nullable | F3 lọc rate, FE | ScrapeCreators (F3) / gendownload title (parse) | ⚠️ nullable — consumer PHẢI degrade khi null |

---

## F1 — `extract_media(url)` : gendownload → file video + metadata
**Phân tích mối nối:** ĐỌC `url` (từ FE/F3). GHI: trả dict `{title, source, view, reactions, duration, formats, local_path}` (không lưu DB — F2 tiêu thụ trực tiếp). Derived-state? Không. Degrade: gendownload lỗi → `{error}`; thiếu format video → thử audio.
```python
async def extract_media(url: str) -> dict:
    # POST https://gendownload.com/api/extract  header UA browser (KHÔNG thì 403)
    # parse title → tách view/reactions (regex "([\d.,KM]+) views"); duration từ formats/param
    # chọn format SD (nhẹ, đủ Gemini) → tải về temp (UA browser) → local_path
    # return {title, source, view, reactions, duration, formats, local_path}
```
Verify: chạy thật trên 1 URL TikTok + 1 FB reel, in `source/view/local_path size`.

## F2 — `analyze_video(local_path, meta)` : Gemini bóc tách 2 tầng
**Phân tích mối nối:** ĐỌC `local_path`+`meta` (F1). GHI `skill_runs['video_analysis']` (JSON). Derived-state? **Có** — tầng Chẩn đoán → mỗi field mang `confidence`+`why`; **view là số cứng duy nhất**, phần còn lại là giả thuyết về phần sáng tạo. Degrade: Gemini empty/safety → lưu Mô tả, Chẩn đoán = null + cờ.
- **Router:** hàm hiện tại (`_call_gemini_pro`) chỉ nhận text system/user → **F2 thêm đường video**: hoặc thêm `call_video(file, prompt)` vào `tools/llm_router.py` (Files API, bọc `asyncio.to_thread`/`client.aio`), hoặc gọi trực tiếp trong business (lazy import `google.genai`). Ưu tiên đặt ở router cho nhất quán.
- **Prompt:** schema 2 tầng (6 Mô tả + 6 Chẩn đoán) + `cong_thuc`(ô-điền) + `thu_thuat`(mảng); `loai_hook ∈ HOOK_TAXONOMY`; ép `response_mime_type=application/json`. **Cấm bịa số** (giữ luật prompt hiện có).
```
mo_ta:  hook{cau_mo, loai_hook∈slug}, transcript, cau_truc[{beat:Hook|Problem|Solution|CTA, giay, nhiem_vu}], cta, chu_tren_man_hinh[]
chan_doan (mỗi field {value, confidence, why}): co_che_hook, cam_xuc{loai,arousal,so_dinh}, nhip_giu_chan, payoff, ly_do_share_save, don_bay_trend, yeu_to_con_nguoi, do_moc
stats: {view, like, comment, share, save, source} (nullable)
cong_thuc: {loai, template, cac_o_dien[], nganh_ap_dung[]}
thu_thuat: [mo_i_nhu_sai, cta_vong_ho, chong_bang_chung, ...]
```
Verify: chạy trên video F1 tải, in JSON, kiểm parse + `loai_hook` ∈ slug.

## F3 — `discover_cluster(seed_url|handle, depth)` : nấc ③ auto-discovery (reuse last30days pattern)
**Phân tích mối nối:** ĐỌC `seed_url`/`handle`. GHI `skill_runs['video_cluster']`. Derived-state? Không (chỉ gom+xếp). Degrade: thiếu ScrapeCreators → chỉ seed (①) hoặc cụm user dán (②).
- **Discovery (ScrapeCreators):** `/v3/tiktok/profile/videos` (theo handle) + `/search/keyword` + `/search/hashtag`. FB: `/v1/facebook/profile/reels` / `/v1/facebook/post`.
- **Bộ lọc chất lượng (đã chốt A):** tính **share-rate + like-rate + comment-rate** (÷view) từ stats; `save` cơ hội. **Đảo trọng số** cho virality (khác reference last30days chấm engagement 10%). Lọc **TRƯỚC** khi tải+Gemini.
- **Bao chi phí (pattern last30days `pipeline.py`):** 3 tier độ sâu (quick/default/deep) + **ENRICH_LIMIT nhỏ** (Gemini-xem seed + top 2-3 đã lọc, phần còn lại **transcript+stats only**) + **budget đồng hồ** (~240s) → hết budget rơi về nomination-only + **cache theo `video_id`**. Fan-out song song có cap workers.
```python
DEPTH = {"quick":{"cap":4}, "default":{"cap":8}, "deep":{"cap":12}}   # tuỳ chỉnh
# seed → discover N → stats-rate filter → top-K → F1+F2 (đắt) cho seed+top2-3; còn lại transcript+stats
```
Verify: chạy 1 handle TikTok, in số video discover / sau lọc / số Gemini-xem thật.

## F4 — `extract_formulas(analysis_or_cluster)` : rút thư viện công thức
**Phân tích mối nối:** ĐỌC `video_analysis`/`video_cluster` (F2/F3). GHI `intake_extra.video_formulas` (append/merge). Derived-state? **Có** → `{confidence,updated,why,by}`; founder pin/sửa (`by:"human"`) Max không đè. Degrade: cụm mỏng → formula confidence thấp + cờ "cần thêm mẫu".
- Từ 1 atom → formula *dự kiến* (confidence thấp). Từ cụm → formula *đáng tin* (confidence theo #video cùng mẫu / N).

## F5 — cầu `formula → gen_calendar_post` + nâng hook 5→10
**Phân tích mối nối:** ĐỌC `intake_extra.video_formulas[formula_id]` (F4). GHI `skill_runs['calendar_post']` (như cũ). Degrade: `formula_id` rỗng → gen như hiện tại (0 hồi quy).
- Thêm param `formula_id: str = ""` vào `gen_calendar_post`. Thêm helper `_formula_anchor_from(extra, formula_id)` (**gương** `_messaging_anchor_from`) → prepend block *"# CÔNG THỨC VIDEO — mượn cấu trúc/hook, KHÔNG sao chép; bẻ theo Thông điệp"*.
- **LUẬT thứ tự:** khối Công thức đặt **DƯỚI** khối Thông điệp (Thông điệp thắng — giữ voice, chống chỏi giọng hook lạ).
- **Nâng hook 5→10:** trong system prompt `gen_calendar_post` hiện có một khối liệt kê **5 nhóm hook cứng** (Tò mò · Trái ngược · Cảm xúc · Góc chuyên gia · Đồng cảm) — **tự grep tìm**, thay bằng render từ `HOOK_TAXONOMY`. FE dropdown `hook_style` → 10 option (value=slug, label=VN). Tự kiểm còn chỗ nào hardcode 5 nhóm không (quét cả `tests/`).

## FE — tab "Học từ video viral" (surface A, một cửa vào)
**Phân tích mối nối:** ĐỌC `bizVideoAnalyses`/`bizVideoFormulas` (expose ở `biz_data`, key `bizXxx`). GHI: gọi route dán URL. Derived-state? Không (FE).
- Vòng: **dán 1 URL seed** (③ nở cụm) *hoặc* dán nhiều URL thủ công → bóc tách + thư viện công thức → nút **"Viết bài từ công thức này"** mở `gen_calendar_post(formula_id=…)` (cạnh dropdown `hook_style` 10 loại).
- 3 lăng kính = 3 view trên cùng surface: B (công thức) mặc định · A (soi đối thủ — bản tóm) · C (dán video mình + tuỳ chọn analytics).
- `biz_data()` thêm `out["bizVideoFormulas"]`/`out["bizVideoAnalyses"]` (theo đúng pattern `bizXxx` sẵn có — grep `bizMessaging` xem mẫu).

---

## Verify chung (dán output THẬT vào mỗi commit — theo AGENTS.md)
```
python -m py_compile webapp/business.py webapp/api.py
node --check web/app.js
```
- Windows: dùng `python` (fallback `py`), **không** `python3`. Git luôn `git --no-pager`. Không có `grep`/`head`/`tail` → dùng `git grep -n`.
- Không có key/DB → verify tĩnh (compile/parse JSON mẫu); hành vi runtime khai rõ "chờ key thật", ĐỪNG khai đã test.

## Cấu hình mới (env — KHÔNG vào DB)
- `SCRAPECREATORS_API_KEY` (F3, tuỳ chọn — thiếu thì degrade). `GEMINI_API_KEY` (đã có). gendownload: không key.
- Thêm `requests`/dùng `urllib` sẵn; `google-genai` đã cài (1.0.0).

## Mở — chốt SAU khi có runtime thật (đừng làm sớm)
- Tinh chỉnh `ENRICH_LIMIT`/budget theo latency Gemini thật (video dài > 2 phút?).
- Lăng kính C: schema nhận analytics user tự dán (retention curve) — chỉ khi có nhu cầu.
- Coverage ScrapeCreators theo từng nền tảng (test thật TikTok/IG/YT/FB).
- Formula confidence formula (bao nhiêu/N video → mức tin) — hiệu chỉnh khi có dữ liệu.

## Không làm
- KHÔNG đổi schema DB (mọi khoá mới → `intake_extra`/`skill_runs`). KHÔNG bịa số trong output AI. KHÔNG hardcode ví dụ 1 ngành (sản phẩm đa ngành).
- **KHÔNG Write đè cả file** `business.py`/`app.js` (rất lớn — đè = mất nội dung). Chỉ **Edit chèn/xoá có mục tiêu**.
- KHÔNG để consumer đọc `stats`/`save` mà không degrade khi null. KHÔNG truyền `loai_hook` ngoài `HOOK_TAXONOMY`.
- 1 function = 1 commit → push → **chờ cổng review PASS mới sang function sau**. KHÔNG tự merge.
```
Thứ tự build: F1 → F2 → (verify feasibility lại) → F4 → F5 → FE → F3 (nặng nhất, cuối).
```
