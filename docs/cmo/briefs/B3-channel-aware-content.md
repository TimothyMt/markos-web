# Brief B3 — Sinh bài CHANNEL-AWARE (kênh quyết định FORM) + 1 nguồn prompt định dạng

> **Mục tiêu:** để **KÊNH của post quyết định ĐỊNH DẠNG** ngay khi sinh — bài TikTok ra kịch bản video
> native (hook 0-3s, shot list, caption, hashtag), bài FB ra bài dài, Zalo ra tin ngắn — tất cả **bám CÙNG
> một anchor** (giọng/cốt lõi/trụ/proof + tầng phễu + chiến lược) mà `gen_calendar_post` đã có (B2.2).
> Gom **prompt video xịn** (đang kẹt ở `_CAMPAIGN_TASK_GEN` của campaigns_v2 sắp khai tử) thành **1 nguồn
> registry định dạng** dùng chung cho cả writer chính lẫn đường derive 🎬.
> **Vấn đề đang có:** (1) writer chính (`gen_calendar_post`) mù kênh → mọi post ra 1 khuôn "bài viết FB"
> (Hook/Thân/CTA/hashtag/Gợi ý ảnh) kể cả khi `channel='TikTok'`. (2) Đường **derive 🎬** (`gen_derivative`)
> đang dùng thật thì mỏng ngữ cảnh (chỉ ngành+USP+text, KHÔNG giọng/tầng/trụ). (3) Prompt video tốt nhất
> nằm ở nhánh chết `campaigns_v2`.
>
> **Phạm vi B3 = BACK-END + nối `channel` từ FE (slot-gen/api).** UI repurpose "bung cụm biến thể theo kênh"
> (từ `sibling_group`) → **B3.1** riêng (FE-heavy).
> **Đọc trước:** `WIRING.md` · brief **B2.2** · `webapp/business.py`: `gen_calendar_post`(~3791, system prompt
> ~3882 — CHỖ SỬA) · `gen_derivative`/`_DERIVATIVES`(~3969) · `_CAMPAIGN_TASK_GEN['video_script']`(~4082, NGUỒN
> prompt xịn để rút ra) · `web/app.js` `slot-gen`(~3512, payload) + `post-derive`(~3600) · `webapp/api.py`
> `biz_calendar_gen`(~183) + `biz_content_derive`(~378).
> **Branch:** `claude/pb-wire-brief-b1-3iptbf` (đã có B2.1+B2.2) · PR về `staging` · KHÔNG tự merge.

---

## 🌏 LUẬT ĐA NGÀNH (bất biến)
1. **Format theo KÊNH, không theo ngành** — mapper `channel→format` dò chuỗi kênh (đa ngành, kênh nào cũng vào
   đúng khuôn). KHÔNG hardcode "spa dùng TikTok".
2. **Archetype nudge, không ép** — impulse (mua cảm xúc) → nghiêng trend/UGC/hook mạnh; trust_building →
   POV chuyên gia/bằng chứng; demand_gen → giáo dục/so sánh. Chỉ là gợi ý trong prompt, không đổi format.
3. **Proof trung thực** — chưa có data thật → `[chèn review/số thật]`, **CẤM bịa số** (ngành nhạy cảm bắt buộc).
   Trụ có proof (B1) → lồng; trụ rỗng proof → giọng quan điểm, không claim.
4. **Framework theo FUNNEL không theo ngành** — PAS/AIDA=TOFU · BAB/4P=MOFU · FAB=BOFU · Star-Story=viral.

## 3 quyết định đã chốt (bám — KHÔNG lệch)
1. **Kênh quyết định form, 1 anchor** — KHÔNG viết bài FB rồi "dịch" sang TikTok. Sinh native theo `channel`,
   nhưng bám đúng bộ anchor `gen_calendar_post` đã lắp (voice/core/pillar/proof/tier/synthesis) — không nhân bản anchor.
2. **1 nguồn prompt định dạng** — `_FORMAT_SPECS` (format → thân prompt + max_tokens + nhãn). Writer chính +
   derive đều đọc đây. Rút chất lượng từ `_CAMPAIGN_TASK_GEN.video_script` (đừng chế mỏng lại).
3. **Additive, không phá** — thêm param `channel` (mặc định '' → format `post` = HÀNH VI CŨ y nguyên). Không đổi
   schema DB, không đụng track/calendar. Derive giữ nguyên chữ ký ngoài, chỉ giàu thêm ngữ cảnh.

---

## ① `_FORMAT_SPECS` + `_channel_to_format` — 1 nguồn định dạng (1 commit)
**File:** `webapp/business.py` (registry + mapper mới, cạnh `gen_calendar_post`).
- **`_channel_to_format(channel) -> str`**: dò lỏng chuỗi kênh (lower) →
  - `video`: chứa `tiktok|reel|short|shorts|douyin|video|yt short|kịch bản`.
  - `short`: chứa `zalo|sms|tin nhắn|story|status` (tin ngắn/nhắc).
  - `longform`: chứa `blog|website|bài dài|seo|landing|note`.
  - `post` (mặc định): còn lại (FB/IG feed…) + khi `channel=''` (tương thích ngược).
- **`_FORMAT_SPECS`** dict `format → {label, body, max_tokens}`:
  - `post`: **thân prompt CŨ** (Hook 5 nhóm · THÂN PAS/AIDA · CTA · 3-5 hashtag · "Gợi ý ảnh") — tách nguyên xi ra đây.
  - `video`: **rút từ `_CAMPAIGN_TASK_GEN.video_script`** — chọn framework theo funnel · **lời thoại thật từng
    beat kèm timing (Xs), CẤM placeholder '[giới thiệu SP]'** · Hook 0-3s (1/5 nhóm) · Visual direction (shot list) ·
    Music/SFX · Caption hook ≤125 ký tự · 8-12 hashtag VN (branded+niche+trending). `max_tokens≈1500`.
  - `short`: 1 tin ngắn (≤ vài dòng) + CTA mềm, hợp Zalo/SMS. `max_tokens≈700`.
  - `longform`: bài dài có tiêu đề + 3-5 khối + CTA. `max_tokens≈1400`.
- **Phần CHUNG mọi format** (giữ ở system, KHÔNG lặp trong body): vai writer Việt · triết lý HOOK · 🔴 cấm generic/
  bịa số/in nhãn khung · gọi 'bạn/anh chị' · bám 'Chủ đề cụ thể' · VN tự nhiên · MARKDOWN.

## ② `gen_calendar_post` CHANNEL-AWARE (1 commit) — LÕI
**File:** `webapp/business.py` `gen_calendar_post`. **Thêm param** `channel: str = ""`.
- `fmt = _channel_to_format(channel)`; lấy `spec = _FORMAT_SPECS[fmt]`.
- **Dựng system = phần CHUNG + `spec['body']` + `hook_rule`** (thay khối thân text cứng hiện tại). `kind` gắn nhãn
  format (vd "1 KỊCH BẢN VIDEO cho <kênh>" / "1 BÀI ĐĂNG…"). `max_tokens = spec['max_tokens']` (thay 900 cứng).
- **GIỮ NGUYÊN** toàn bộ anchor đã có: `msg_anchor` (giọng/cốt lõi/trụ/proof) · `strat_anchor` · `_spine_anchor` ·
  các dòng `lines` (Ý LỚN đợt/pillar/TẦNG PHỄU/repurpose/chủ đề). Thêm 1 dòng ctx: `Kênh đăng: {channel}`.
- **Nudge archetype** (đa ngành #2): thêm 1 dòng vào `lines` theo `get_purchase_archetype(industry)`.
- **Nối FE:** `slot-gen` payload thêm `channel: _slotCtx.channel || ''` (slot ĐÃ có `channel` từ B2.2); `api.biz_calendar_gen`
  forward `d.get("channel","")`.
- **Tương thích ngược:** `channel=''` → `post` → prompt = y HỆT hiện tại (chỉ tách chỗ, không đổi chữ).

## ③ `gen_derivative` giàu ngữ cảnh + dùng registry (1 commit) — fix đường 🎬 đang dùng
**File:** `webapp/business.py` `gen_derivative`. **Thêm param** (tùy chọn) `pillar, tier, target_channel`.
- Đọc `_FORMAT_SPECS` (video → spec video) thay instruction mỏng trong `_DERIVATIVES`.
- **Bơm anchor** như writer chính: `_messaging_anchor_from(_pe)` (giọng/cốt lõi/trụ/proof) + tầng phễu (nếu có) +
  archetype — vào system/user, cạnh `# BÀI GỐC`. Vẫn "bám bài gốc + KHÔNG bịa số".
- **Nối FE:** `post-derive` truyền thêm `pillar/tier/channel` của bài gốc (`_postBase` giữ lại khi mở modal Tạo bài).
  Thiếu → degrade như cũ (chỉ ngành+USP+text). `api.biz_content_derive` forward.
- (Prompt xịn giờ 1 nguồn `_FORMAT_SPECS` — `_CAMPAIGN_TASK_GEN.video_script` trỏ về đây hoặc để degrade; KHÔNG xoá.)

---

## 🔌 Phân tích mối nối (seam)
| Khoá đọc/ghi | Producer | Khớp? | Degrade |
|---|---|---|---|
| `channel` (slot→api→gen_calendar_post) | slot matrix/funnel (B2.2 ✓) | str khớp 2 đầu | '' → format `post` = hành vi CŨ |
| `_channel_to_format(channel)` | mapper (①) | trả enum format ∈ {post,video,short,longform} | không khớp → `post` |
| `_FORMAT_SPECS[fmt]` | registry (①) | fmt luôn có trong dict | fmt lạ → `post` |
| `tier`/`pillar` (→ derive) | post B2.2 | như B2.2 | thiếu → derive chạy như cũ |
| `msg_anchor` (giọng/proof) | `_messaging_anchor_from` (B1 ✓) | dùng ở cả writer + derive | rỗng → prompt không có khối giọng (không vỡ) |
| archetype nudge | `get_purchase_archetype` (✓) | 1 dòng gợi ý | lỗi → bỏ qua (try/except) |
- **Derived-state? KHÔNG** — format suy từ `channel` do user/matrix đặt (ephemeral mỗi lần sinh), user đổi kênh = đổi form.

## Verify (offline — không key/DB)
```bash
python3 -c "import webapp.business as B; assert callable(B._channel_to_format) and isinstance(B._FORMAT_SPECS, dict); \
  assert B._channel_to_format('TikTok')=='video' and B._channel_to_format('Reels 15s')=='video' \
  and B._channel_to_format('Zalo OA')=='short' and B._channel_to_format('Bài FB')=='post' and B._channel_to_format('')=='post'; print('mapper OK')"
python3 -c "import webapp.business, webapp.api"      # (sandbox thiếu starlette → khai rõ)
node --check web/app.js
python3 tests/test_b22_calendar_source.py            # B2.2 vẫn PASS (channel='' → hành vi cũ)
python3 tests/test_b3_channel_format.py              # MỚI
```
Regression `tests/test_b3_channel_format.py` (mới, stub LLM ghi prompt) chốt:
- `_channel_to_format`: TikTok/Reels/Shorts→video · Zalo→short · Bài dài→longform · FB/''→post.
- `gen_calendar_post(channel='TikTok')` → prompt system mang khối VIDEO (shot list/timing/caption/hashtag) + VẪN có
  anchor (giọng/cốt lõi + TẦNG PHỄU); `max_tokens` = 1500.
- `gen_calendar_post(channel='')` → prompt = format `post` (có "Gợi ý ảnh", KHÔNG có shot list) — **tương thích ngược**.
- `gen_derivative(video, pillar/tier)` → prompt mang khối video + giọng thương hiệu (không còn chỉ ngành+USP).
- Hành vi LLM thật (script TikTok có native/đúng nhịp không) → soi staging.

## Self-review report (dán commit cuối)
```
[B3] Channel-aware content — kênh quyết định format + 1 nguồn _FORMAT_SPECS
Đã check: _channel_to_format map đúng · gen_calendar_post +channel chọn format giữ anchor · channel='' = hành vi cũ
          (tương thích ngược, test_b22 PASS) · gen_derivative giàu anchor + registry · FE slot-gen/post-derive forward channel ·
          prompt video rút từ _CAMPAIGN_TASK_GEN (1 nguồn) · KHÔNG đổi schema DB · KHÔNG bịa số/hardcode ngành
Chưa chắc (chờ runtime): script TikTok có native/đúng nhịp · repurpose cụm biến thể (B3.1) → soi staging
```

## Không làm
- KHÔNG viết bài text rồi "dịch" sang video (sinh native theo kênh).
- KHÔNG hardcode kênh theo ngành · KHÔNG bịa số/proof (giữ luật cấm bịa + `[chèn review thật]`).
- KHÔNG đổi schema DB / track calendar / hợp đồng `gen_calendar_post` cũ (chỉ THÊM param `channel` mặc định '').
- KHÔNG xoá `_CAMPAIGN_TASK_GEN`/`_DERIVATIVES` (rút prompt ra registry, giữ degrade).
- KHÔNG làm UI repurpose "bung cụm biến thể" (→ B3.1).
- Mỗi mũi 1 commit · push nhánh riêng · PR về `staging` · **dừng chờ review, KHÔNG tự merge.**
