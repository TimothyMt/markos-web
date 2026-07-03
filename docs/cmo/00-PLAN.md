# KẾ HOẠCH — Max thành AI CMO thực thụ

> **Mục tiêu sản phẩm:** Max = AI CMO phụ trách **chẩn đoán → chiến lược → kế hoạch → sản xuất nội dung đa nền tảng → đo & học**, lái bởi *chiến lược nền của business*.
> **Mức tự chủ đã chốt:** **"Chủ động đề xuất"** — Max tự quét timing + hiệu suất, CHỦ ĐỘNG nhắc **1 việc nên làm bây giờ**; **user chốt**.
> **Branch:** `feature/ai-cmo-core` (worktree `D:/MarkOS/wt-cmo`, base = `main`).
> **Cách làm:** Cline làm **từng phase → từng slice nhỏ**, commit sau mỗi slice, Claude review rồi mới brief phase sau.

## Target model — vòng lặp CMO
```
Chẩn đoán → Chiến lược → Kế hoạch(timing) → Sản xuất đa kênh → Phân phối → Đo & Học → (quay lại)
              ▲                                                                     │
              └──────── mọi thứ truy ngược về STRATEGY SPINE (4 neo dưới) ──────────┘
```
Max hôm nay = "engine nội dung có chiến lược gắn trên". CMO = "hệ điều hành lấy **Strategy Spine** làm xương sống + đóng **vòng đo-học** + **nhịp chủ động**".

## 6 NGUYÊN TẮC THIẾT KẾ (cross-cutting — mọi phase phải tuân)
Đây là phần rút ra sau review marketing; **áp cho tất cả brief P0–P6**, không chỉ P0.

1. **Spine = 4 neo, không chỉ objective.** Objective một mình KHÔNG quyết định kênh hay thông điệp. Xương sống gồm:
   **① Objective (đo được bằng SỐ) · ② Audience/ICP · ③ Định vị (vì sao chọn mình) · ④ Capacity (năng lực thật).**
   Cả 4 cùng được bơm vào prompt (P0.2), không chỉ objective.
2. **Đo được bằng SỐ.** `metric/target/baseline` phải có `{value, unit, period}` (cho phép trống, nhưng khi có thì là số). Nếu target là chuỗi tự do → **vòng đo-học (P4) không bao giờ đóng được**. Đây là sửa lỗi nặng nhất của bản plan cũ.
3. **Capacity LÁI phạm vi.** Nhân lực/ngân sách/nhịp làm nổi (neo ④) **cắt** số kênh (P2) và độ dài journey (P3). Persona là founder/SME thường 1 người → CMO giỏi kê đơn "**làm ÍT lại, làm sâu**", KHÔNG đẩy user làm nhiều hơn sức. Capacity là *biến điều khiển thiết kế*, không phải ô nhập trang trí.
4. **Data-in thật.** Vòng học chỉ tốt bằng số nạp vào. Doanh thu SME VN nằm ở Shopee/TikTok Shop/inbox/offline — KHÔNG chỉ Ads snapshot. P4 phải có **ô nhập kết quả kỳ (thủ công)**; không có số thật thì không có gì để học.
5. **Nudge = 1 việc nên làm BÂY GIỜ.** P5 trả **một** đề xuất ưu tiên cao nhất (ranked) + có capping/tần suất, KHÔNG đổ một danh sách. "List nudges" là mùi của tool, không phải của CMO.
6. **Đa mục tiêu — chừa chỗ nới.** MVP dùng 1 spine cho gọn, nhưng biết rằng brand-nền và conversion-spike phục vụ mục tiêu khác nhau. Thiết kế đừng khoá cứng vào đúng 1 objective vĩnh viễn (vd cho phép `spine` là bản mới nhất, đổi được theo mùa/chiến dịch lớn).

## GIỮ / THÊM / BỎ (đối chiếu code thật)
**GIỮ:** Research T1-T5, Đặt cược, Synthesis+Playbook, Messaging House, 6 dạng+nhịp nền, Funnel map×kênh, hạ tầng campaign (`gen_campaign_portfolio`/`commit_subcampaign`/`gen_sub_content`/`gen_campaign_task`), occasion, `calendar_plan`, Ads snapshots.

**THÊM:**
1. **Strategy Spine (4 neo)** — `intake_extra.spine` {objective(số), audience, positioning, constraint}. Thay cho ý "objective spine" mỏng của bản cũ. (Lưu ý: `gen_funnel_map(objective=)` hiện chỉ là bias brand/đơn, không phải mục tiêu đo được.)
2. **Timing engine** — nâng occasion → lịch business thật + preset mùa vụ VN (Tết, 9.9/10.10/11.11/12.12, Trung Thu…), lái spike.
3. **Channel portfolio strategy (capacity-gated)** — chọn danh mục kênh + vai trò phễu mỗi kênh, **số kênh bị cắt theo neo ④**; + hoàn thiện **channel-native** (WIP `feature/content-quality-rationale` @ `3eaf474`).
4. **Campaign-as-journey (scale theo capacity)** — sản xuất nội dung theo CHUỖI/arc neo spine+timing+kênh, độ dài arc theo năng lực thật, không chỉ bài rời.
5. **Vòng đo-học đóng** — success criteria per objective + **nhập kết quả thật** + đọc số (Ads snapshots + content feedback) + review gap-vs-target.
6. **Nhịp chủ động** — vòng kỳ quét *timing sắp tới* + *hiệu suất gần đây* → **1 nudge ưu tiên nhất**, user chốt.
7. **QC guardrail** — rule-check channel-native (chuyển sớm, gắn cùng P2) + editor "Soi & nâng" on-demand (P6).

**BỎ/GỌN:** hợp nhất các đường tạo kế hoạch/nội dung chồng nhau (`gen_calendar_topics` vs `campaign_plan` vs `gen_campaign_portfolio`) về 1 flow do Spine dẫn — **xác minh flow trùng thật trước khi gỡ**, không xoá mù.

## Ràng buộc (bất di bất dịch — CLAUDE.md)
- **KHÔNG đổi schema DB.** Mọi dữ liệu mới → key trong `profile.intake_extra` (dict).
- **MIRROR FE:** sửa `web/app.js` phải mirror y hệt `<script>` trong `web/dashboard-standalone.html`; CSS tương tự.
- Tái dùng prompt trong `agents/` (lazy import), đừng tự chế prompt mỏng.
- Không bịa số trong output AI.

## Lộ trình theo phase (dependency từ trên xuống)
| Phase | Nội dung | Phụ thuộc | Slice (dự kiến) |
|---|---|---|---|
| **P0** | **Strategy Spine** — 4 neo (objective số + audience + định vị + capacity), intake+lưu+bơm prompt | — | 0.1 spine intake+store · 0.2 wire spine anchor |
| **P1** | **Timing engine** — lịch business thật + preset mùa vụ VN → spike | P0 | 1.1 timing intake+preset · 1.2 calendar dùng timing |
| **P2** | **Channel strategy (capacity-gated) + native + QC rule-check** | P0 | 2.1 channel portfolio (cắt theo capacity) · 2.2 channel-native (3eaf474) · 2.3 QC rule-check |
| **P3** | **Campaign-as-journey** — arc scale theo capacity, neo spine+timing+kênh | P0,P2 | 3.1 journey gen · 3.2 gắn vào calendar |
| **P4** | **Vòng đo-học** — success criteria + **nhập kết quả thật** + đọc số + review | P0 | 4.1 success criteria + results-in · 4.2 gap-vs-target + review digest |
| **P5** | **Nhịp chủ động** — CMO nudge = 1 việc bây giờ (ranked + cap) | P1,P4 | 5.1 nudge engine (ranked) · 5.2 UI "Việc nên làm bây giờ" |
| **P6** | **Editor "Soi & nâng"** on-demand | P2 | 6.1 editor on-demand |

> **Bắt đầu từ P0** (xương sống — mọi phase sau bám vào).
> **Chứng minh vòng lõi sớm:** slice **4.1 (success criteria + results-in)** phụ thuộc *chỉ P0* → có thể làm ngay sau P0, song song P1/P2, để "vòng đo-học" — thứ tạo khác biệt của CMO — không nằm mãi cuối lộ trình.
> **QC rule-check** đã chuyển từ cuối lên **P2.3** (gần chỗ làm channel-native) vì chất lượng nội dung tạo/mất niềm tin ngay từ đầu.
> Briefs từng slice ở `docs/cmo/briefs/` (chỉ P0 có brief sẵn — phase sau brief sau khi review).

## Tham khảo được phép
- **Codebase Max:** `webapp/business.py` (các hàm ở bảng GIỮ), `docs/web/product-journey-4-tang.md`, `CLAUDE.md`.
- **Repo `marketingskills` (Corey Haines):** mượn framework — `product-marketing` (↔ objective/audience/positioning/messaging), `content-strategy`, `social` (channel-native), `marketing-plan` (P0/P1), `copywriting`/`copy-editing` (P6). KHÔNG bê nguyên, chỉ rút khung.
- **WIP channel-native:** `feature/content-quality-rationale` commit `3eaf474` (CHANNEL_SPECS + `_channel_block`) cho P2.
