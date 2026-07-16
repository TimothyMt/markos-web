# FLOW V3 — từ Nghiên cứu tới Lịch nội dung (chuỗi chính của Max)

> Chốt lại **1 chuỗi xương sống** user đi từ đầu tới cuối, thay vì các mảnh rời.
> Khung chủ vẫn là **6 miền CMO** (`00-PLAN.md`) — file này mô tả **đường đi của user** xuyên 6 miền đó.
> Thay vai trò "trục kể chuyện" của `docs/web/product-journey-4-tang.md` (file kia giữ làm lịch sử D4).
> **Trạng thái:** 12 quyết định đã chốt với founder (2026-07-16). Mockup §4.2 + §5: xem cuối file.

## 0. Chuỗi 7 chặng (mỗi chặng = 1 CỔNG, con người chốt mới đi tiếp)

```
① NGHIÊN CỨU T1-T3            → sự thật thị trường (grounding)
        ▼  ═══ CỔNG 1: HƯỚNG ĐÁNH (user chốt) ═══
② HƯỚNG ĐÁNH (intake)         → tệp · định vị(→USP) · giá · kênh
        ▼
③ T4-T5 CHIẾN LƯỢC            → Synthesis (định vị bền) + Tactical Playbook (kho góc đánh)
        ▼
④ THÔNG ĐIỆP (thường trực)    → Messaging House: cốt lõi + N trụ + giọng     ← sống qua NHIỀU đợt
        ▼
⑤ BIG IDEA (theo mùa)         → platform sáng tạo 1 mùa                       ← 1 big idea → N chiến dịch
        ▼  ═══ CỔNG 2: LẬP CHIẾN DỊCH (user chốt) ═══
⑥ CHIẾN DỊCH                  → mục đích · kênh · kỳ hạn   (tầng nhấn: Max suy)
        ▼
⑦ FUNNEL MAP /chiến dịch      → tỉ lệ + hành trình khách (rào cản) + tuyến + offer + rủi ro
        ▼  ═══ CỔNG 3: DUYỆT NỘI DUNG (user chốt) ═══
⑧ LỊCH (brief NỘI DUNG)       → mỗi ô: bài này NÓI GÌ · chặng · rào cản gỡ
        ▼
⑨ GEN BÀI (NÓI THẾ NÀO)  → ĐO ─┐
   └── số liệu vòng lại nuôi ⑤⑥⑦ (không nuôi ①②③ trừ khi lệch lớn → mở lại CỔNG 1)
```

**Luật thứ tự:** chặng sau **khoá** cho tới khi chặng trước có dữ liệu. Không nhảy cóc, nhưng luôn có
**đường degrade** (thiếu → Max dựng bản tối thiểu + gắn nhãn "nháp/giả thuyết"), trừ CỔNG 3 (§5).

---

## 1. CỔNG 1 — "Hướng đánh" (chặng ②)

Chạy sau T1-T3, **trước** T4-T5. Max đọc research → gợi ý option mỗi ô (`gen_bet_options`), user **chọn hoặc
tự ghi**. Ghi 1 lần, fan-out ra `bet_choices` + `spine` (`save_strategy_input` — đã có).

| Ô | Khoá | Ghi chú |
|---|---|---|
| Tệp khách nhắm trước (wedge) | `bet_choices.segment` → `spine.audience.who` | 1 tệp, không phải "tất cả" |
| **Định vị** (alternative → differentiator → statement) | `spine.positioning.*` | **→ sinh ra USP**, §1.1 |
| Phân khúc giá | `spine.positioning.price_posture` | premium/parity/value |
| Kênh triển khai chính | `bet_choices.channel_slugs[]` | **trần** cho kênh chiến dịch (§3.3) |
| Mục tiêu + số | `spine.objective.{metric,target,baseline}` | D6 đóng vòng đo bằng ô này |

> **Nhân lực/ngân sách — GÁC LẠI (chốt 2026-07-16).** Không đưa vào form lần này. Khoá `spine.constraint.*`
> giữ nguyên, **không đụng**. Ghi lại lý do để phiên sau khỏi đào lại: nó là **ràng buộc**, không phải hướng
> đánh (nguyên tắc #4) — nó không *sinh* chiến lược mà **cắt** chiến lược (cắt số kênh ở ⑥, số bài ở ⑦/⑧).
> Khi làm, đặt cuối form, nhóm riêng, nhãn "Sức mình tới đâu", hiện hệ quả ngay.

### 1.1 Chiều USP ↔ Định vị: **nháp USP → Max truy ngược** (chốt)

Không làm "định vị suy ra từ USP" như ý gốc. Lý do: USP tự khai không neo vào ai ("chất lượng tốt, tận tâm")
→ suy định vị từ đó ra rác. Dunford (nguyên tắc #2) đi ngược lại: `alternative` → `differentiator` → **rồi USP
mới rớt ra**. Code hiện đã đúng chiều (`save_strategy_input` fan-out ra `profile.usp`); đảo lại = phá `_spine_anchor`.

Nhưng giữ **trải nghiệm** của ý gốc, vì founder trong đầu chỉ có USP:

```
founder gõ USP thô 1 câu
       ▼
Max TRUY NGƯỢC (bám T2 competitor + T3 customer) → alternative + differentiator
       ▼
user XÁC NHẬN / SỬA  ← đây là lưới an toàn
       ▼
ghi spine.positioning + fan-out profile.usp
```

Đây là **derived-state** → theo WIRING §2: bắt buộc `confidence` + `updated` + `why-log` + **human-override**.

### 1.2 Khi research mỏng, user nhìn cũng không gật được (chốt)

**Max tự điền, hạ confidence, KHÔNG hỏi thêm câu nào** — bước user duyệt ở trên đã là lưới an toàn.

Ba điều làm cho việc này an toàn:
1. **`alternative` không đồng nghĩa "đối thủ"** — Dunford có 3 dạng: đối thủ trực tiếp · khách **tự làm** (DIY)
   · khách **không làm gì, chịu đựng** (status quo). Với SME VN thì "khách tự mua serum về bôi" hay "khách đang
   chịu đựng" là alternative hợp lệ → **không bao giờ có ô trống thật sự**, luôn tụt được xuống nấc status quo.
2. **`differentiator` bí thì để RỖNG, không bịa.** Đường lấp đã có: brief `intake-usp-sharpen.md` F3/F4 rút
   *onliness / white-space* từ competitor. Nối vào, không viết mới.
3. **Không chặn flow, nhưng không im.** `confidence: low` mà user bấm qua luôn → T4-T5 nhận nhãn
   **"định vị = giả thuyết"**, và Max nudge vá lại khi có đơn thật ("Bạn đã có 5 khách — trước đó họ đang làm gì?").

---

## 2. Chặng ④ vs ⑤ — **Key message ≠ Big idea** (chốt: tách 1→N)

| | **THÔNG ĐIỆP** (Messaging House) | **BIG IDEA** |
|---|---|---|
| Là gì | Ta nói gì với khách, mãi mãi | Cách kể của **1 mùa** |
| Tuổi thọ | Đổi khi **định vị** đổi (hiếm) | 1 quý / 1 mùa vụ |
| Số lượng | **1** | nhiều, nối tiếp |
| Khoá | `intake_extra.messaging` {core, pillars[], voice} | `intake_extra.big_ideas[]` ← **MỚI** |
| Nuôi bởi | Synthesis T4 + định vị | Playbook (kho góc đánh) + Thông điệp |

**Code hiện sai:** `key_ideas[]` vừa là big idea vừa là chiến dịch (1:1, nhét chung `window`+`goal`+`funnel_map`).
Hệ quả: không chạy được **1 big idea qua 2 chiến dịch** (vd "Tết không cần hoàn hảo" → 1 chiến dịch branding
ToFu trên TikTok + 1 chiến dịch chốt đơn BoFu trên Zalo). Founder phải copy-paste 2 lần → 2 bản trôi khác nhau.

```
big_ideas[] = {id, title, angle, source_ref(trụ gốc), season, created_at}
campaigns[] = {id, big_idea_id ──┘, ...}    ← FK mềm; big_idea_id rỗng = chiến dịch trần (degrade OK)
```
Di trú: `key_ideas[]` tách đôi (title/angle/source_ref → `big_ideas`; phần còn lại → `campaigns`), `big_idea_id`
trỏ ngược. **Additive + idempotent**, không xoá `key_ideas` (tiền lệ: `migrate_campaigns_to_key_ideas`).

---

## 3. CỔNG 2 — Lập chiến dịch (chặng ⑥)

### 3.1 Bảy loại chiến dịch (chốt)

| Key | Nhãn VN | Để làm gì | Đo bằng |
|---|---|---|---|
| `branding` | 🎨 Xây thương hiệu | Người ta **nhớ** mình là ai | reach · nhắc nhớ · follow |
| `launch` | 🚀 Ra mắt | Tung sản phẩm/dịch vụ mới | biết tới sp mới · đơn đầu |
| `demand` | 🧲 Kéo nhu cầu | Gom người **quan tâm** (lead) | lead · inbox · giữ liên hệ |
| `conversion` | 💰 Chốt đơn / Sale | Biến quan tâm → **tiền** | đơn · doanh thu · CR |
| `retention` | 🔁 Giữ chân | Khách cũ **mua lại** | mua lại · tần suất |
| `winback` | 🪃 Kéo lại khách cũ | Đánh thức khách ngủ | tỉ lệ đánh thức |
| `advocacy` | 📣 Lan truyền | Khách **kể hộ** (UGC/referral) | UGC · giới thiệu · share |

Cố tình **bỏ** recruitment/employer-branding và reputation/crisis — không phải việc marketing thường ngày của
SME, thêm chỉ làm loãng menu. Mở lại khi có nhu cầu thật.

Enum cũ `_KI_GOALS` (`awareness|consideration|conversion|retention`) thực chất là **tầng phễu đội lốt mục đích**
— đó chính là gốc của cái lẫn ở §3.2. Map di trú:
`awareness→branding · consideration→demand · conversion→conversion · retention→retention`;
3 loại mới (`launch/winback/advocacy`) là bổ sung.

### 3.2 Tầng nhấn = **Max suy từ mục đích**, user chỉ chọn mục đích (chốt)

User **không** chọn tầng nhấn. Hai ô không độc lập → cho chọn cả hai thì "branding + nặng BoFu" là mâu thuẫn
và Max không biết nghe ai.

| Mục đích | ToFu/MoFu/BoFu |
|---|---|
| `branding` | 70/25/5 |
| `launch` | 55/30/15 |
| `demand` | 30/50/20 |
| `conversion` | 20/30/50 |
| `retention` | 10/35/55 |
| `winback` | 5/30/65 |
| `advocacy` | 40/35/25 |

Max hiện tỉ lệ + câu **why** ("Branding → nặng ToFu vì mục tiêu là người lạ nhớ mình"). User kéo lệch → ghi
`ratio_source: "user"`, Max **không đè lại**. (Luật derived-state, WIRING §2. Bảng `_GOAL_RATIO` hiện có = hạt giống.)

### 3.3 Kênh — làm kỹ

#### Gốc của bug: **không ràng ⊆ được, vì cả hai đầu đều là text tự do**
`bet_choices.channel` = list chuỗi 160 ký tự người/Max viết ("đánh mạnh TikTok cho tệp mẹ bỉm").
`funnel_map.posts[].channel` = chuỗi 60 ký tự LLM chế ("Reels 15s").
So `"TikTok"` với `"Reels 15s"` bằng gì? → Muốn ràng thì **phải có slug chuẩn hai đầu trước**
(WIRING #1: "khớp tên/slug/enum/kiểu 2 đầu"). Thiếu validate chỉ là triệu chứng.

#### Đang có 4 nơi nói về kênh, không nơi nào là nguồn
| Nơi | Kiểu | Vấn đề |
|---|---|---|
| `bet_choices.channel` | text tự do | chiến lược |
| `profile.current_channels` | text tự do | "kênh đang dùng" |
| `funnel_map.posts[].channel` | text tự do (LLM) | **trộn kênh × định dạng** |
| `CHANNEL_SPECS` | **đã slug hoá** (5 kênh) | ở nhánh WIP `feature/content-quality-rationale`, chưa merge; chỉ tả *cách viết* |
| `agents/campaign_scope_library.py:top_channels` | text tự do theo ngành | gợi ý ngành |

Trùng ý slice **A3** (`briefs/00-INDEX.md`): *1 khái niệm = 1 producer*.

#### Bước 1 — Từ điển kênh: **nâng CHANNEL_SPECS thành từ điển đầy đủ** (chốt)
Kéo `CHANNEL_SPECS` từ nhánh WIP về, mở rộng ~12 kênh SME VN. Mỗi kênh:
```
slug        "tiktok"
label       "TikTok"
aliases     ["tik tok", "reels", "video ngắn"]   ← khớp lỏng text cũ + LLM bịa
tiers       ("tofu", "mofu")                     ← tầng phễu kênh này làm tốt
formats     ["video 15-30s", "livestream"]
write_spec  ← đã có sẵn trong CHANNEL_SPECS
```
12 kênh: `facebook · facebook_group · instagram · tiktok · tiktok_shop · shopee · youtube · zalo_oa ·
website_seo · email · offline · kol_pr`.

> **Paid/organic — GÁC LẠI (chốt).** Chưa đụng. Làm kênh thuần trước, tính lúc làm D3 ngân sách.

#### Bước 2 — Tách `channel` khỏi `format` (hệ quả bắt buộc, không phải fork)
`posts[].channel = "Reels 15s"` đang trộn **kênh** (Instagram? TikTok? cả hai đều có) × **định dạng** (video 15s).
Không tách thì validate cái gì cũng sai.
→ `posts[] = {channel: "tiktok", format: "video ngắn 15s"}`. `channel` ∈ từ điển (validate được);
`format` gợi ý từ `CHANNELS[slug].formats` nhưng **không khoá cứng** (định dạng phải sáng tạo được).

#### Bước 3 — Ba tầng kênh
```
① bet_choices.channel_slugs[]   TRẦN chiến lược   (cổng 1)
        ⊇
② campaigns[].channels[]        đợt này đánh đâu   (cổng 2)   ← MỚI, hiện thiếu hẳn
        ⊇
③ posts[].channel               bài này lên đâu    (funnel map)
```

#### Bước 4 — Vi phạm: **2 nguồn, 2 cách xử**
*(Rút lại đề xuất "ép về kênh gần nhất" của bản trước — đó là im lặng sửa dữ liệu, trái human-override.)*

| Nguồn | Bản chất | Xử |
|---|---|---|
| **LLM bịa kênh lạ** ở ③ | lỗi máy | khớp lỏng qua `aliases` → ra slug thì nhận. Không khớp → gán **kênh chính của chiến dịch** + cờ `channel_guessed: true` + badge để user sửa. *(Tiền lệ `_match_pillar`: "model bịa trụ lạ → bỏ trục, bài vẫn giữ")* |
| **User cố ý chọn ngoài trần** ở ② | ý người | **CHO, không chặn.** Ghi `off_strategy: true` + hỏi 1 câu: *"Kênh này ngoài chiến lược — thử nghiệm đợt này thôi, hay đổi chiến lược?"* Chọn "đổi" → **bơm ngược** lên `bet_choices.channel_slugs`. |

#### Bước 5 — Đường bơm ngược (chốt) — phần giá trị nhất
Founder chạy Instagram 3 đợt liền trong khi chiến lược ghi "TikTok + Zalo" → **chiến lược trên giấy đã chết mà
không ai biết**. Max nudge: *"3 đợt gần đây bạn đều đánh Instagram nhưng nó không có trong chiến lược — cập nhật chứ?"*
(Đúng nguyên tắc #6: 1 việc nên làm bây giờ, ranked + capping.)

#### Bước 6 — Degrade + reconcile
- ② trống → lấy ① ; ① trống → `profile.current_channels` (khớp lỏng ra slug) ; vẫn trống →
  `campaign_scope_library.top_channels[ngành]` (**đã có sẵn**) + nhãn "gợi ý theo ngành, chưa chốt". Không chặn.
- Sửa ① bỏ 1 kênh mà chiến dịch đang chạy vẫn dùng → **không tự xoá gì**, gắn cờ + báo
  *"2 chiến dịch đang dùng Zalo mà bạn vừa bỏ Zalo khỏi chiến lược"*. User quyết.

### 3.4 Trường của 1 chiến dịch
```
campaigns[] = {
  id, big_idea_id,
  purpose,             # enum 7 loại §3.1        ← user chốt
  ratio, ratio_source, # derived §3.2 + override
  channels[],          # slug ⊆ bet_choices §3.3
  off_strategy,        # cờ nếu có kênh ngoài trần
  window_start/end,
  budget,              # optional
  kpi,                 # 1 số, truy về spine.objective (D6)
  funnel_map: {...},   # §4
  status               # draft|active|done
}
```

---

## 4. Funnel map — theo **từng** chiến dịch (chặng ⑦)

Đối chiếu code (`gen_funnel_map_for_idea` trả `{ratio, posts[], offers, risks}`):

| Thành phần | Trạng thái |
|---|---|
| Tỉ lệ phễu | ✅ có — chuyển thành derived §3.2 |
| **Hành trình khách hàng** | ❌ **thiếu hẳn** — §4.1 |
| Tuyến nội dung | ⚠️ có nửa (`posts[].pillar`) — §4.2 |
| Offer theo tầng | ✅ có (`offers.{tofu,mofu,bofu}`) |
| Rủi ro + phương án B | ✅ có (`risks[]`) |
| Danh sách bài dự kiến | ✅ có (`posts[]`) |

### 4.1 Hành trình khách hàng (MỚI — chốt: có rào cản, ràng post vào chặng)

Đây là mắt xích **nối tỉ lệ với danh sách bài**. Không có nó, `posts[]` chỉ là list rải cho đủ tỉ lệ.
```
journey[] = [{ stage, trigger, barrier, content_role }]
```
- `stage` — `nhận biết → tìm hiểu → cân nhắc → mua → quay lại`; cắt theo archetype ngành (hàng gấp thì "cân nhắc"
  gần như biến mất — `frameworks.industry_context` đã có archetype, tái dùng).
- `trigger` — cái gì đẩy khách sang chặng sau.
- `barrier` — **rào cản** giữ khách lại; lấy từ T3 customer_insight (nỗi đau thật, không bịa).
- `content_role` — nội dung nào **gỡ đúng rào cản đó**.

**Ràng buộc mối nối:** mỗi `posts[]` trỏ về 1 `journey[].stage`. **Bài không gỡ rào cản nào = bài thừa → cắt.**
Đây là cách Max chứng minh "bài này để làm gì" thay vì rải cho đủ số.

### 4.2 "Tuyến nội dung" = **lát cắt (trụ × dạng) + biệt danh** — bản A+ (chốt)

Hệ đã có 2 trục, không đẻ trục thứ 3:
- **TRỤ** (`messaging.pillars[].territory`) = **nói CHUYỆN GÌ** — thường trực.
- **DẠNG** (6 dạng: 📖 Câu chuyện · 🎓 Giáo dục · 🤝 Review · 💰 Đẩy đơn · ✨ Tương tác · 🔁 Giữ chân) = **kể KIỂU GÌ**.

→ **Tuyến := GROUP BY (pillar, format)** — lát cắt, không phải bảng mới. `posts[]` gắn `{pillar, format}` là đủ dựng.

Vì sao không làm `tracks[]` là thực thể riêng (phương án B):
- Tuyến tự đặt tên kiểu "Câu chuyện Tết" **trộn trụ với dạng** → founder không phân biệt nổi nó với trụ nữa.
- Tuyến **trôi khỏi Thông điệp** (không truy về trụ nào) → Max mất đường kiểm nhất quán, đúng thứ Max bán.
- **Trùng lặp âm thầm**: "Review khách thật" và "Bằng chứng da thật" là một tuyến viết hai lần, máy không bắt được.

**A+ = vá cái được duy nhất của B (tên tự đặt) mà không rước cái mất:**
```
tracks[] = { pillar: "Da nhạy cảm", format: "review",
             alias: "Chuyện da thật của khách" }   # chỉ là cái TÊN đè lên lát cắt có sẵn
```
Mặc định tên máy ghép ("Da nhạy cảm × Review"); founder muốn thì đặt biệt danh. **Tên là của họ, trục vẫn là 2,
đường truy về Thông điệp còn nguyên.**

---

## 5. CỔNG 3 — Lịch: **brief NỘI DUNG**, không phải hook (chặng ⑧)

> **Luật:** **Lịch quyết NÓI GÌ · Gen quyết NÓI THẾ NÀO.**

Bản trước của doc này để `hook_draft` + `cta` trong ô lịch. **Sai** — cả hai đều là *câu chữ phụ thuộc kênh*:
- CHANNEL_SPECS bắt TikTok "hook video 3 giây đầu", Facebook "hook mạnh 1-2 câu", Zalo gần như không hook.
  Cùng 1 brief ra 3 hook khác hẳn → hook viết ở tầng lịch là **hook mù kênh**, gen xong vẫn bị viết đè.
  **Duyệt một thứ, máy giao thứ khác.**
- CTA y hệt: Zalo "nhắn ngay" · TikTok "follow" · Facebook "inbox".
- **Repo đã chốt điều này:** brief PB-WIRE (`00-INDEX.md`) — *"W0 hạ độ cao `_TAC_SYSTEM` (**góc đánh, không
  hook**)"* + *"W1 → gen_calendar_post (**hook tự viết** bám Messaging)"*.

### Ô lịch
```
{ date, channel, tier, pillar, format, campaign_id,   # ← đã có
  journey_stage: "cân nhắc",                          # ← §4.1, ràng bài vào chặng
  barrier_ref:   "sợ lại kích ứng",                   # ← rào cản bài này gỡ
  content_brief: "kể ca khách kích ứng 3 lần →        # ← BÀI NÀY NÓI GÌ. 1-2 dòng.
                  soi da trước khi làm là bắt buộc",  #   KHÔNG phải câu chữ.
  material:      "ca khách thật — founder xác nhận",  # ← không có thì Max KHÔNG bịa
  offer_ref:     "mofu",                              # ← trỏ campaign.funnel_map.offers
  status:        "draft | approved" }

# gen_calendar_post lo — KHÔNG nằm ở lịch:
#   hook  ← CHANNEL_SPECS[channel] + Messaging.voice
#   CTA   ← channel + tier + offer_ref
#   câu chữ, độ dài, hashtag, giọng
```

**CỔNG CỨNG (chốt):** `status` phải = `approved` mới gen được bài. Founder buộc phải đọc luận điểm trước khi
tốn token. Duyệt 1-2 dòng nhẹ hơn duyệt bài đủ chữ nhiều, và **cắt lúc còn 1 dòng thì không tiếc**.
Rải ngày theo `content_rhythm` (nền móng) + chiến dịch (spike) — `reconcile_calendar` (B2.2) đã làm, chỉ bơm thêm trường.

---

## 6. Việc phải làm (theo thứ tự phụ thuộc)

| # | Việc | Đụng | Vì sao thứ tự này |
|---|---|---|---|
| 1 | Tách `big_ideas[]` khỏi `key_ideas[]` (+ migrate additive, idempotent) | `business.py` | mọi thứ dưới treo vào `big_idea_id` |
| 2 | `campaigns[].purpose` 7 loại + migrate 4 enum cũ | `business.py` | §3.1 |
| 3 | `ratio` derived từ purpose + `ratio_source` override | `business.py`, `app.js` | cần #2 |
| 4a | **Từ điển kênh**: kéo `CHANNEL_SPECS` từ WIP → 12 kênh + slug/alias/tiers/formats | `business.py` | **nền của #4b-4d** |
| 4b | Tách `posts[].channel` (slug) khỏi `posts[].format` | `business.py` | cần #4a |
| 4c | `campaigns[].channels[]` + validate ⊆ + 2 cách xử vi phạm | `business.py`, `app.js` | cần #4a,#4b — **seam bug thật** |
| 4d | Đường bơm ngược + nudge lệch chiến lược | `business.py`, `app.js` | cần #4c |
| 5 | `funnel_map.journey[]` (rào cản từ T3) + `posts[].journey_stage` + cắt bài thừa | `business.py` | §4.1 |
| 6 | `tracks[].alias` (biệt danh lát cắt) | `business.py`, `app.js` | §4.2, nhỏ, độc lập |
| 7 | Brief nội dung + cổng cứng `status` | `business.py`, `app.js` | cần #5 (journey_stage) |
| 8 | Ô nháp USP → truy ngược Dunford (derived + confidence + override) | `business.py`, `app.js` | §1.1 — độc lập hẳn, làm lúc nào cũng được |

**Gác lại có chủ ý:** nhân lực/ngân sách (§1.2) · paid-vs-organic (§3.3) — ghi lý do ở chỗ tương ứng để phiên
sau khỏi đào lại.

Mỗi việc = 1 function = 1 brief trong `briefs/`, qua **cổng mối nối** (`WIRING.md`) trước khi PASS.
**KHÔNG đổi schema DB** — mọi khoá mới nằm trong `profile.intake_extra`.

---

## Mockup (§4.2 + §5)
Bản dựng để chốt hai mục này: <https://claude.ai/code/artifact/4a95b71f-f9c9-4a55-9b83-e232c03e56a0>
