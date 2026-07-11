# [PB-WIRE] Playbook = tầng "cách đánh" (vĩ mô) — cho hợp đồng output rồi nối GÓC ĐÁNH xuống D4/D6

> Tầng ② (Playbook) → ③ (Content) + ⑥ (Đo). **Tính năng nối + hạ độ cao playbook, KHÔNG vá bug crash.**
> Luật: `docs/cmo/WIRING.md` (Hiến pháp mối nối). **KHÔNG đổi schema DB** (dữ liệu mới → `intake_extra`).
> Nền: finding 2026-07-10 — playbook đẻ chi tiết tác chiến (hook/test/cut/KPI) nhưng downstream không
> dùng lại. Founder chốt hướng xử lý (2026-07-10): **playbook phải Ở TẦNG VĨ MÔ (góc đánh), KHÔNG
> xuống câu chữ (hook cụ thể)**. Hook là sản phẩm THỰC THI, đẻ lúc viết bài, bám Messaging House.

## Mô hình 3 tầng độ cao (kim chỉ nam cả brief — Cline đọc kỹ)
| Tầng | Trả lời | Đầu ra | Producer |
|---|---|---|---|
| ① Chiến lược | Đánh Ở ĐÂU, thắng bằng gì | Định vị · đặt cược · wedge | `synthesis` |
| **② Cách đánh (Playbook)** ← brief này | Tệp này × tầng phễu này: **GÓC ĐÁNH** gì · **kênh** nào · **test & đọc tín hiệu** ra sao · **KPI** nhìn gì | Góc đánh + luật chơi | `tactical_playbook` |
| ③ Thực thi | Nói bằng **CÂU CHỮ** gì | Hook · caption · bài | `gen_calendar_post` (bám Messaging House) |

**Playbook dừng ở ②, KHÔNG chạm ③.** Hook đóng băng trong playbook = (a) lỗi thời khi Messaging đổi
giọng/chủ đề khác; (b) 2-nguồn-hook đá nhau (playbook vs calendar_post) — đúng lỗi vừa tỉa ở D1 hôm nay.
Góc đánh vĩ mô thì tái dùng cho N bài; hook chỉ xài 1 lần.

## Vấn đề (vì sao) — đã soi code, KHÔNG đoán
**Producer:** `_gen_playbook` (`business.py:3794`) + `_TAC_SYSTEM` (`business.py:3752`) → skill_run
`tactical_playbook`, **markdown tự do, KHÔNG khoá máy**. `_TAC_SYSTEM` luật #3 + #8b **ép playbook xuống
tầng ③**: đòi "Copy mẫu (câu quote dùng ngay)", "hook thật, KHÔNG placeholder" trong MỖI mũi → đây chính
là chỗ playbook lấn việc content.

**Consumer hiện tại (đọc như context nén `tact[:1500-2500]`):** `campaign_plan` (trụ) · `gen_campaign`
(brief) · `gen_funnel_map` · big idea/occasion/retention. → định hướng chảy xuống dạng văn bản nén, KHÔNG khoá.

**KHÔNG consumer:** `gen_calendar_topics` (`business.py:610`) + `gen_calendar_post` (`business.py:3142`)
đều KHÔNG đọc playbook (post writer nhận `hook_style`=tên nhóm 1/5, `angle`=chủ đề → tự chế). **Ngưỡng cut
+ KPI của playbook: KHÔNG ai đọc lại** = lỗ D6.

## Kết quả mong muốn
1. **Hạ độ cao playbook**: bỏ ép hook/copy-mẫu-làm-chuẩn; playbook đưa **GÓC ĐÁNH + kênh + khung test + KPI**.
   Giữ **1 ví dụ minh hoạ/Hướng, DÁN NHÃN rõ "ví dụ cho dễ hình dung — KHÔNG phải bản chính thức"**
   (founder chốt option B) — ví dụ này **KHÔNG là khoá máy, downstream KHÔNG bám vào**.
2. Playbook có **hợp đồng output ổn định** (khoá máy) song song markdown người-đọc — markdown giữ nguyên chất.
3. `gen_calendar_post` **kéo được GÓC ĐÁNH + kênh** đúng Hướng của playbook (KHÔNG kéo hook) → tự viết hook
   bằng giọng Messaging House. Mỗi mối lo 1 nguồn: góc từ playbook, chữ từ content.
4. Ngưỡng cut + KPI mỗi Hướng **có khoá + có nơi lưu** để D6 sau này đối chiếu số thật.

## Bước 0 (ĐẦU TIÊN) — hợp đồng return của playbook
> Không có bước này thì nối là nối mù (playbook hiện markdown tự do, parse regex thì giòn).

**CHỐT: Route B — playbook TỰ in 1 khối JSON** sau markdown (đúng pattern đã có trong repo: bản đồ định vị
JSON cuối `competitor`; `gen_funnel_map` output JSON). Sửa `_TAC_SYSTEM` thêm yêu cầu in khối máy cuối bài.
*(Route A = parse markdown đã loại: format LLM trôi → parse rớt im lặng, giòn.)*

**Schema hợp đồng — khoá là GÓC ĐÁNH, KHÔNG phải hook:**
```json
{ "segments": [ {
    "name": "", "archetype": "", "is_wedge": true,
    "insight": "",                         // 1-2 câu NÉN từ 🧠 Insight cốt lõi — phần hồn của tệp,
                                           // downstream bơm kèm territory (Q-B, chốt 2026-07-11)
    "tiers": {
      "tofu": [ {
        "huong": "",                       // tên Hướng (góc đánh), vd "Bóc trần lầm tưởng skincare"
        "territory": "",                   // lãnh địa/góc nội dung 1 câu — thứ downstream BÁM;
                                           // = mệnh đề MÔ TẢ (nói VỀ nội dung), KHÔNG phải câu nói VỚI khách
        "tows": "SO1",                     // mã dẫn về nước cờ SWOT
        "channels": ["Reels 15s"],         // kênh + định dạng đích danh
        "test": "",                        // cấu trúc test (vd '3 biến thể góc, cùng thân bài')
        "cut": "sau 7 ngày, biến thể thắng ≥1.5× CTR biến thể thua",
                                           // ngưỡng go/kill ưu tiên dạng SO SÁNH; số tuyệt đối phải
                                           // dán nhãn "ngưỡng giả định — chỉnh theo baseline thật" (Q-A)
        "kpis": ["lượt xem","xem hết","share"],
        "example": ""                      // 1 VÍ DỤ minh hoạ — KHÔNG phải khoá downstream bám; có thể rỗng
      } ], "mofu": [ ... ], "bofu": [ ... ]
    }
} ] }
```
**Lưu (CHỐT):** `intake_extra.playbook_struct`, versioned theo `playbook_synth_id` đã có (`business.py:315`).
KHÔNG đổi schema DB. Regen playbook → regen struct theo (khớp `bizPlaybookStale` `business.py:317`).

## Việc (sau Bước 0)
- **W0 — Hạ độ cao `_TAC_SYSTEM`:** sửa luật #3/#8b: mũi tactic xuống tới **góc đánh + kênh + khung test +
  KPI**, KHÔNG bắt "copy mẫu dùng ngay". Thêm: mỗi Hướng CÓ THỂ kèm **1 ví dụ minh hoạ dán nhãn rõ** (option
  B). Thêm block yêu cầu **in khối JSON `playbook_struct`** cuối bài theo schema trên.
- **W1 — Nối GÓC ĐÁNH vào sản xuất bài:** `gen_calendar_post` (bài lẻ — CHỐT làm trước; `gen_calendar_topics`
  để sau nếu cần): khi slot thuộc tầng phễu X của tệp wedge, đọc `playbook_struct` → truyền **territory +
  channels + huong** của Hướng khớp **+ `insight` segment-level (Q-B)** vào prompt làm *"góc đánh tham chiếu —
  bám góc này + tinh thần insight này, tự viết câu chữ bằng giọng Thông điệp"*. **KHÔNG truyền `example` vào
  như hook.** Degrade: thiếu struct → giữ hành vi cũ (tự chế).
- **W2 — cut+KPI có khoá cho D6:** đảm bảo `cut`+`kpis` lưu được trong `playbook_struct`, truy lại bằng khoá.
  *(Vòng đo thật/UI = slice D6 riêng, NON-GOAL brief này. Ở đây chỉ ĐẢM BẢO khoá tồn tại + có test đọc lại.)*

## Phân tích mối nối (seam — theo WIRING.md, JIT brief-time)
- **Producer khoá `playbook_struct`:** `_gen_playbook` (LLM emit khối JSON, W0). **Consumer:** W1 (`gen_calendar_post`
  đọc `territory/channels/huong`), W2/D6 (đọc `cut/kpis`). Khớp 2 đầu: enum tầng `tofu/mofu/bofu`; `tows` mã SWOT;
  `channels/kpis` = list[str]; `territory/huong/test/cut/example` = str.
- **Tới được runtime:** struct sinh CÙNG call playbook (W0) → có trước calendar (calendar cần strategy xong). ✓
- **Đường degrade (bắt buộc):** JSON thiếu/rỗng/không parse → W1 về hành vi cũ (tự chế hook), W2 bỏ qua —
  **KHÔNG crash, KHÔNG nút chết.** Playbook cũ (trước tính năng) không có struct → calendar chạy như cũ.
- **Không derived-state** → không dính luật confidence/override.
- **Map Hướng↔slot theo TẦNG PHỄU + wedge, KHÔNG theo tên Hướng** (tên trôi mỗi lần gen).
- **Ranh giới tầng (bất biến brief này):** playbook KHÔNG sinh câu chữ chính thức; hook/caption CHỈ sinh ở
  `gen_calendar_post` bám Messaging House. `example` trong struct là minh hoạ, cấm downstream dùng làm hook.

## Acceptance (done = kiểm thế nào)
- [ ] Chạy strategy → `intake_extra.playbook_struct` parse ra được, đủ segment × 3 tầng, có `territory/channels/cut/kpis`.
- [ ] Markdown playbook KHÔNG còn "Copy mẫu (dùng ngay)" như bản chính; nếu có `example` thì kèm nhãn "ví dụ minh hoạ".
- [ ] `gen_calendar_post` cho slot TOFU tệp wedge → prompt CÓ `territory`+`channels` của Hướng TOFU tương ứng,
      KHÔNG chèn `example` làm hook (nhìn payload/log). Hook trong bài do model viết mới, bám giọng Messaging.
- [ ] Thiếu struct (playbook cũ) → calendar vẫn chạy, không lỗi.
- [ ] `cut`+`kpis` truy được bằng khoá (test đọc lại).
- [ ] `python3 -c "import webapp.business, webapp.api"` pass (FE nếu đụng: `node --check web/app.js`). Test `test_playbook_struct`.

## Quyết định đã chốt (founder OK giao Cline — Cline vướng thì HỎI, đừng đoán)
1. Playbook độ cao: **tầng ② góc đánh, KHÔNG xuống hook** (founder chốt).
2. Ví dụ minh hoạ: **B — giữ 1/Hướng, dán nhãn rõ, không là khoá downstream** (founder chốt).
3. Hợp đồng: **Route B (playbook tự emit JSON)**, lưu `intake_extra.playbook_struct` (đề xuất Claude).
4. W1 phạm vi: **`gen_calendar_post` (bài lẻ) trước**, topics sau nếu cần (đề xuất Claude).
5. W2 phạm vi: **chỉ đảm bảo khoá `cut/kpis` tồn tại + lưu**; vòng đo để slice D6 (đề xuất Claude).
6. **Hội đồng V1 2026-07-11 (founder chốt cả 7 — chi tiết thi công ở `PB-WIRE-tasks.md`):**
   (a) `max_tokens` `_gen_playbook` 4000 → **10000**; (b) JSON emit **COMPACT** + luật *"rút gọn markdown,
   TUYỆT ĐỐI không cắt JSON"*; (c) validate **2 mức** — nghiêm wedge, lỏng tệp phụ; (d) **strip JSON khỏi
   markdown kể cả khi parse fail** + `logger.warning` (degrade êm nhưng không MÙ); (e) **Q-A** example `cut`
   dạng TƯƠNG ĐỐI, số tuyệt đối dán nhãn "ngưỡng giả định"; (f) **Q-B** schema thêm **`insight` segment-level**,
   W1 bơm kèm; (g) **Q-C** thêm luật **compliance/seeding** vào `_TAC_SYSTEM` (không review giả, cẩn trọng
   before-after ngành nhạy cảm). **Bằng chứng:** playbook v2 thật (user 990555, spa Q3) CỤT ở trần 4000
   ngay cả khi chưa có JSON + tự bịa ngưỡng tuyệt đối ("Watch-through>30%") + đề xuất seeding giả không cảnh báo.

## Phụ thuộc
- Cần strategy (synthesis + playbook) chạy được — đã có. Không phụ thuộc S2/ScrapeCreators.
- `bizPlaybookStale` (`business.py:317`): playbook regen → `playbook_struct` regen theo cùng `playbook_synth_id`.
- Messaging House (`intake_extra.messaging`) là nguồn GIỌNG cho hook ở `gen_calendar_post` — đã có (`_messaging_anchor_from`).
