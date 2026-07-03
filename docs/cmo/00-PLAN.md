# KẾ HOẠCH — Max thành AI CMO thực thụ

> **Mục tiêu sản phẩm:** Max = AI CMO phụ trách **chiến lược → kế hoạch → sản xuất nội dung đa nền tảng**, lái bởi *business + mục tiêu + timing* của user.
> **Mức tự chủ đã chốt:** **"Chủ động đề xuất"** — Max tự quét timing + hiệu suất, CHỦ ĐỘNG nhắc/đề xuất campaign & điều chỉnh; **user chốt**.
> **Branch:** `feature/ai-cmo-core` (worktree `D:/MarkOS/wt-cmo`, base = `main`).
> **Cách làm:** Cline làm **từng phase → từng slice nhỏ**, commit sau mỗi slice, Claude review rồi mới brief phase sau.

## Target model — vòng lặp CMO
```
Chẩn đoán → Chiến lược → Kế hoạch(timing) → Sản xuất đa kênh → Phân phối → Đo & Học → (quay lại)
              ▲                                                                     │
              └──────────── mọi thứ truy ngược về 1 OBJECTIVE đo được ──────────────┘
```
Max hôm nay = "engine nội dung có chiến lược gắn trên". CMO = "hệ điều hành lấy **Objective** làm xương sống + đóng **vòng đo-học** + **nhịp chủ động**".

## GIỮ / THÊM / BỎ (đối chiếu code thật)
**GIỮ:** Research T1-T5, Đặt cược, Synthesis+Playbook, Messaging House, 6 dạng+nhịp nền, Funnel map×kênh, hạ tầng campaign (`gen_campaign_portfolio`/`commit_subcampaign`/`gen_sub_content`/`gen_campaign_task`), occasion, `calendar_plan`, Ads snapshots.

**THÊM:**
1. **Objective spine** — `intake_extra.objective` {outcome, metric, target, baseline, deadline, ràng buộc}. (Hiện `gen_funnel_map(objective=)` chỉ là bias brand/đơn, không phải mục tiêu đo được.)
2. **Timing engine** — nâng occasion → lịch business thật + preset mùa vụ VN (Tết, 9.9/10.10/11.11/12.12, Trung Thu…), lái spike.
3. **Channel portfolio strategy** — bước chọn danh mục kênh + vai trò phễu mỗi kênh; + hoàn thiện **channel-native** (WIP `feature/content-quality-rationale` @ `3eaf474`).
4. **Campaign-as-journey** — sản xuất nội dung theo CHUỖI/arc neo objective+timing+kênh, không chỉ bài rời.
5. **Vòng đo-học đóng** — success criteria per objective + đọc số (Ads snapshots + content feedback) + review.
6. **Nhịp chủ động** — vòng kỳ quét *timing sắp tới* + *hiệu suất gần đây* → đẩy danh sách đề xuất ("CMO nudges"), user chốt.

**BỎ/GỌN:** hợp nhất các đường tạo kế hoạch/nội dung chồng nhau (`gen_calendar_topics` vs `campaign_plan` vs `gen_campaign_portfolio`) về 1 flow do Objective dẫn — **xác minh flow trùng thật trước khi gỡ**, không xoá mù.

## Ràng buộc (bất di bất dịch — CLAUDE.md)
- **KHÔNG đổi schema DB.** Mọi dữ liệu mới → key trong `profile.intake_extra` (dict).
- **MIRROR FE:** sửa `web/app.js` phải mirror y hệt `<script>` trong `web/dashboard-standalone.html`; CSS tương tự.
- Tái dùng prompt trong `agents/` (lazy import), đừng tự chế prompt mỏng.
- Không bịa số trong output AI.

## Lộ trình theo phase (dependency từ trên xuống)
| Phase | Nội dung | Phụ thuộc | Slice (dự kiến) |
|---|---|---|---|
| **P0** | **Objective spine** — intake + lưu + bơm vào prompt | — | 0.1 intake+store · 0.2 wire vào prompts |
| **P1** | **Timing engine** — timing thật + preset VN → spike | P0 | 1.1 timing intake+preset · 1.2 calendar dùng timing |
| **P2** | **Channel strategy + native** | P0 | 2.1 channel portfolio step · 2.2 port channel-native (3eaf474) |
| **P3** | **Campaign-as-journey** — sequence/arc | P0,P2 | 3.1 journey gen · 3.2 gắn vào calendar |
| **P4** | **Vòng đo-học** — success criteria + đọc số + review | P0 | 4.1 success criteria · 4.2 đọc số+review digest |
| **P5** | **Nhịp chủ động** — CMO nudges (đề xuất theo timing+số) | P1,P4 | 5.1 engine đề xuất · 5.2 UI "Việc CMO đề xuất" |
| **P6** | **QC guardrail** — rule-check + editor "Soi & nâng" | P2 | 6.1 rule-check · 6.2 editor on-demand |

> **Bắt đầu từ P0** (xương sống — mọi phase sau bám vào). Briefs từng slice ở `docs/cmo/briefs/`.

## Tham khảo được phép
- **Codebase Max:** `webapp/business.py` (các hàm ở bảng GIỮ), `docs/web/product-journey-4-tang.md`, `CLAUDE.md`.
- **Repo `marketingskills` (Corey Haines):** mượn framework — `product-marketing` (↔ objective/messaging), `content-strategy`, `social` (channel-native), `marketing-plan` (P0/P1), `copywriting`/`copy-editing` (P6). KHÔNG bê nguyên, chỉ rút khung.
- **WIP channel-native:** `feature/content-quality-rationale` commit `3eaf474` (CHANNEL_SPECS + `_channel_block`) cho P2.
