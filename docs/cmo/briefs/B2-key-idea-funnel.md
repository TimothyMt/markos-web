# Brief B2 — T4 Key Idea (theo đợt) + T5 Funnel map per idea → danh sách bài dự kiến (BACK-END)

> **Mục tiêu:** thi hành 2 tầng giữa của CHAIN-V2 — **T4 KEY IDEA** (1 ý lớn/1 đợt) → **T5 FUNNEL MAP
> CỦA CHÍNH key idea đó** → **danh sách bài dự kiến**. Đây là "trái tim mới" thay funnel-map-tổng
> mồ-côi cũ: mẹ = key idea, con = danh sách bài (B3 sau đổ thành thẻ calendar).
> **Phạm vi B2 = BACK-END + nối ống (biz_data/api) ONLY.** Màn FE (đề xuất → chốt ý → xem danh sách
> bài) → brief **B2-UI** riêng (chưa làm) — giống cách đã tách B1 / B1-UI.
> **Dừng đúng ranh:** B2 kết thúc ở **danh sách bài dự kiến** (mỗi bài = tầng + kênh + vai trò).
> KHÔNG đổ thẻ calendar, KHÔNG sinh câu chữ bài — đó là B3.
>
> **Đọc trước:** `CHAIN-V2-KIENTRUC.md` (kiến trúc 7 tầng — hiện nằm ở branch `feature/pb-wire-t1-t3`,
> commit `7902f88`; sẽ đồng tồn khi branch đó merge) · `WIRING.md` (Hiến pháp mối nối) · `webapp/business.py`:
> `_gen_playbook`/`_TAC_SYSTEM` (~3820, producer `playbook_struct`), `_validate_playbook_struct` (~3916),
> `gen_messaging`/`_MSG_WEB_ADAPT` (~2794, producer `messaging`), `gen_funnel_map` (~2702, funnel CŨ — KHÔNG đụng),
> `biz_data` (~225).
> **Branch:** `feature/b2-key-idea-funnel` từ `staging` (đã có `playbook_struct` PR-A + B1) · PR về `staging` · KHÔNG tự merge.

## 3 quyết định đã chốt (bám vào — KHÔNG lệch)
1. **Degrade-safe** — B2 chạy được **KHÔNG cần** `playbook_struct`. Thiếu struct → tụt xuống
   `messaging.pillars` (territory+angle) + synthesis. Không bao giờ trả **cụt-im-lặng** (đúng lỗi funnel
   cũ ở handoff: trần token + không validate → string đứt giữa câu lưu thẳng DB).
2. **Additive** — tạo **key MỚI** `intake_extra.key_ideas`, **KHÔNG đụng** `campaigns_v2` / `funnel_map`
   objective-based cũ. B4 dọn 2-track + funnel cũ sau.
3. **Không nhảy cóc** — dừng ở danh-sách-bài. Thẻ calendar + sinh câu chữ khi bấm = B3.

## Hình dạng dữ liệu (key mới trong `intake_extra` — KHÔNG đổi schema DB)
```
intake_extra.key_ideas = [                       # LIST — chuỗi đợt nối nhau (nền Max đề xuất + dịp user thêm)
  {
    "id": "<ts-slug>",                           # ổn định, để B3 calendar + T7 đo truy vết
    "title": "<ý lớn 1 câu>",
    "angle": "<thế đối lập / góc — bám T3 messaging>",
    "source": "max" | "user",                    # Max đề xuất từ kho góc đánh · user tự thêm
    "source_ref": "<territory+tows của Hướng gốc nếu source=max; '' nếu user>",
    "goal": "awareness|consideration|conversion|retention|"  # MỤC TIÊU đợt — USER đặt; '' = Max suy khi gen
             # nhận biết · cân nhắc · chốt/xả · giữ chân → uốn ratio phễu
    "window_start": "", "window_end": "",         # kỳ hạn đợt — USER đặt (con người thắng)
    "status": "draft" | "active" | "done",
    "funnel_map": {                              # T5 — CỦA RIÊNG key idea này (rỗng cho tới khi gen)
      "ratio": "60/30/10",                        # SUY từ goal (bảng dưới); user chỉnh tay thắng
      "posts": [                                 # ★ DANH SÁCH BÀI DỰ KIẾN — B2 DỪNG Ở ĐÂY
        {"tier": "tofu|mofu|bofu", "channel": "Reels 15s", "role": "<vai trò/góc bài 1 câu>", "note": ""}
      ]
    },
    "created_at": <ts>, "updated_at": <ts>
  }
]
```

---

## ① `suggest_key_ideas` — Max đề xuất ý lớn (KHÔNG lưu — trả list đề xuất) (1 commit)
**File:** `webapp/business.py` (hàm mới). **ĐỌC:** `playbook_struct` · degrade `messaging`+synthesis. **GHI:** không.

- Nguồn chính: `extra.playbook_struct.struct.segments[].tiers.{tofu,mofu,bofu}[].{territory,huong,tows,channels}`
  (producer = `_gen_playbook`/PR-A, live staging ✓). Xoay lần lượt các Hướng làm ứng viên ý lớn (mỗi đề xuất
  bám 1 territory + tows → giữ `source_ref`).
- **Degrade:** thiếu/không-validate struct → đọc `extra.messaging.pillars[].{territory,angle}`
  (producer `save_messaging` ✓) + synthesis. Cả 2 đường degrade đều có producer.
- 1 LLM call JSON: nhào territory/angle + cốt lõi messaging → **N ý lớn** (title ≤14 từ + angle 1 câu, bám
  thế-đối-lập T3). `_VN_NATURAL_RULE` + cấm bịa. Trần token gọn (~2000). Parse lỗi/rỗng → trả `{ideas: []}`
  (FE hiện "chưa đề xuất được — thử lại"), KHÔNG ném.
- **Derived-state? KHÔNG** — đây là *đề xuất* non-binding; user chọn/sửa/bỏ = human-override sẵn trong thiết kế
  (luật WIRING #2 không áp — không tự-suy trạng-thái user, không cần confidence/why-log).

## ② `save_key_idea` — user chốt 1 ý (từ đề xuất hoặc tự viết) + đặt kỳ hạn đợt (1 commit)
**File:** `webapp/business.py`. **ĐỌC:** `key_ideas` hiện có. **GHI:** append/update `extra.key_ideas`.

- Input: `title, angle, source, source_ref, goal, window_start, window_end, id(rỗng=tạo mới)`. Có `id` khớp →
  update (giữ `funnel_map` cũ, đổi meta); không → append với `id` mới + `created_at`.
- `goal` chuẩn hoá về enum `{awareness,consideration,conversion,retention}` (rác/khác → `""`). Rỗng hợp lệ.
- `window_*` từ user (con người thắng). Rỗng → `status="draft"`, KHÔNG chặn. Có đủ window → cho set `"active"`.
- Cắt độ dài (title[:140], angle[:220], role/note sau). Dedupe theo `id`. Trả `{ok, key_idea}`.

## ③ `gen_funnel_map_for_idea` — T5: funnel + danh sách bài cho 1 key idea (1 commit)
**File:** `webapp/business.py`. **ĐỌC:** key_idea (②) + `playbook_struct`(degrade messaging) + `voice` +
synthesis + `current_channels` + archetype. **GHI:** `key_ideas[i].funnel_map`.

- Input: `id` của key idea. Không thấy id → `{error}`.
- Ghép context: key_idea.title/angle + Hướng khớp `source_ref` trong `playbook_struct` (lấy `channels`/`tofu-mofu-bofu`
  làm khung) + `messaging.voice` (giọng) + synthesis[:1600] + `current_channels` + archetype
  (`frameworks.industry_context.get_purchase_archetype` ✓).
- **Degrade:** thiếu struct → dựng khung từ `messaging.pillars` + archetype (chọn kênh hợp archetype) + synthesis.
- 1 LLM call JSON → `{ratio, posts:[{tier,channel,role,note}]}`. **Hợp đồng khoá cho B3:**
  `tier ∈ {tofu,mofu,bofu}` (khớp tier lịch/đo cũ để T6/T7 ráp được) · `channel` đích danh · `role` 1 câu.
- **CHỐNG lỗi funnel cũ (bắt buộc):**
  - **Validate** output: chuẩn hoá `tier` về enum (rác → bỏ post đó); post thiếu `channel`/`role` → bỏ.
  - posts rỗng sau validate → **degrade dựng tối thiểu** từ messaging pillars (KHÔNG trả cụt-im-lặng).
  - Trần token cứng · KHÔNG lưu string đứt.
  - **Ratio UỐN THEO MỤC TIÊU ĐỢT (không cố định):** đợt cố định 60/30/10 hại đợt-chốt (60% bài đi sai
    tầng phễu). Suy ratio từ `key_idea.goal` theo **khung gợi ý** (LLM chỉnh ±, dán nhãn "chỉnh theo baseline"):

    | goal | hình phễu | ratio khung |
    |---|---|---|
    | `awareness` (phủ nhận biết) | nặng đầu | ~65/25/10 |
    | `consideration` (nuôi/cân nhắc) | nặng giữa | ~25/50/25 |
    | `conversion` (chốt/xả/sale) | nặng đáy | ~20/30/50 |
    | `retention` (giữ chân) | ít TOFU, xoay khách cũ | ~10/40/50 |
    | `""` (trống) | Max SUY từ title/angle | suy được → theo khung; không rõ → **lưới cuối 60/30/10** |

    `goal` trống → Max suy tại gen-time (ephemeral, KHÔNG lưu lại thành nhãn — user thấy ratio + sửa tay = override).
    Đây KHÔNG phải derived-state phải-why-log: `goal` là trường user-sở-hữu; suy chỉ là default 1 lần cho gen đó.
  - **Volume tỉnh táo:** theo độ dài đợt + nguồn lực, KHÔNG ép dày (handoff: lịch cũ 9 bài/tuần quá tải team 2-3).
- GHI ngược `funnel_map` vào đúng phần tử `key_ideas[i]`, cập nhật `updated_at`. Trả `{ok, funnel_map}`.

## ④ Nối ống ra FE
- **`biz_data`** (~225): thêm `out["bizKeyIdeas"] = extra.get("key_ideas") or []` (guard dict như các block khác).
- **`api.py`** `api_routes()`: 3 handler + `Route(...)`: `suggest_key_ideas` · `save_key_idea` · `gen_funnel_map_for_idea`.

---

## Verify (offline — không key/DB)
```bash
python3 -c "import webapp.business as B; assert callable(B.suggest_key_ideas) and callable(B.save_key_idea) and callable(B.gen_funnel_map_for_idea); print('funcs OK')"
python3 -c "import webapp.business, webapp.api"      # (sandbox có thể thiếu starlette/anthropic — khai rõ nếu vậy)
python3 tests/test_b2_key_idea.py                    # regression mới (stub llm_router+storage): seam key_ideas
```
Regression `tests/test_b2_key_idea.py` (mới) kiểm TĨNH + hành vi thuần:
- `save_key_idea` append đúng, dedupe theo id, giữ `funnel_map` khi update meta.
- `gen_funnel_map_for_idea` (stub LLM trả JSON có tier rác + post thiếu khoá) → validate lọc sạch,
  tier chuẩn enum, posts KHÔNG rỗng.
- ratio uốn theo goal: goal=`conversion` → khung nặng-đáy vào prompt; goal=`""` → lưới cuối 60/30/10.
- degrade: không `playbook_struct` → ① và ③ vẫn ra output từ messaging (KHÔNG ném, KHÔNG cụt).
- Hành vi LLM thật (Max xoay góc đánh hợp lý; volume/ratio đúng nguồn lực) **chờ chạy staging** — khai rõ self-review.

## Self-review report (dán vào commit cuối)
```
[B2] T4+T5 back-end — Key Idea theo đợt + funnel map per idea → danh sách bài dự kiến
Đã check: 3 func import OK · key_ideas append/dedupe/degrade · funnel validate lọc tier rác + posts không rỗng ·
          biz_data expose bizKeyIdeas · 3 api route · KHÔNG đụng funnel cũ/campaigns_v2 · KHÔNG đổi schema DB
Chưa chắc (chờ runtime): Max xoay góc đánh có hợp lý · ratio/volume có tỉnh táo theo nguồn lực không → soi output thật rồi siết
```

## Không làm
- KHÔNG đụng `gen_funnel_map` cũ / `campaigns_v2` / `funnel_map` objective-based (B4 dọn).
- KHÔNG đổ thẻ calendar, KHÔNG sinh câu chữ bài, KHÔNG "sinh khi bấm" (B3).
- KHÔNG làm FE (→ B2-UI riêng).
- KHÔNG đổi schema DB / schema `messaging` / schema `playbook_struct`.
- KHÔNG bịa số/proof trong prompt (giữ luật cấm bịa sẵn có).
- Mỗi mũi 1 commit · push nhánh riêng · PR về `staging` · **dừng chờ review, KHÔNG tự merge.**
