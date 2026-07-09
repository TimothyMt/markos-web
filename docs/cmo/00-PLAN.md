# KẾ HOẠCH — Max thành AI CMO thực thụ

> **Đích sản phẩm:** Max = **AI CMO** cho founder/SME Việt — sở hữu **chiến lược marketing tích hợp** (định vị · giá · kênh · nội dung · giữ khách · đo lường) lái bởi **Strategy Spine** của business.
> **Nhãn hiện tại (không overclaim):** *"CMO = đích, đang ở giai đoạn content-first execution."* Tầng **chiến lược** làm CMO-grade ngay; tầng **thực thi** hoàn thiện dần, bắt đầu từ nội dung.
> **Mức tự chủ đã chốt:** "Chủ động đề xuất" — Max tự quét timing + hiệu suất, chủ động nhắc **1 việc nên làm bây giờ**; user chốt.
> **Branch:** đã HỢP NHẤT về 1 cây (D-050) — làm trên nhánh tích hợp hiện hành (`feature/consolidate`, sau merge = `main`); base = `main`. *(Các brief cũ ghi `feature/ai-cmo-core` = lịch sử trước hợp nhất.)*

## Vì sao kiến trúc này (đã validate, không phán solo)
Bản plan cũ coi "4 tầng nội dung" là toàn bộ Max. Core-validation (có nguồn, 2026-07) chỉ ra: đó là **content marketing lifecycle** — đúng, nhưng chỉ ~40% việc CMO. CMO thật sở hữu thêm **định giá, product-marketing, kênh/GTM, phân bổ ngân sách, giữ khách, đo lường xuyên miền** ([AMA](https://www.ama.org/marketing-news/the-role-of-the-cmo/), [Deloitte](https://www.deloitte.com/us/en/programs/chief-marketing-officer/articles/roles-of-the-cmo.html)). Và CMO **về bản chất là vai chiến lược/quyết định**; sản xuất là việc specialist.
→ Nên Max phủ **đủ 6 miền CMO ở tầng CHIẾN LƯỢC trước** (đó đã là một CMO thật), rồi hoàn thiện tầng THỰC THI sau, content trước.

## Kiến trúc — 2 TẦNG × 6 MIỀN
Mọi miền truy ngược về **Spine**. Mỗi miền có 2 tầng: **chiến lược** (bộ não — quyết định) và **thực thi** (bàn tay — sản xuất artifact).

```
TẦNG 0 · SPINE (lõi chiến lược) — nuôi TẤT CẢ
   objective(SỐ) · segmentation→ICP · POSITIONING(quan hệ, Dunford) · capacity(RÀNG BUỘC)
```

| Miền | TẦNG CHIẾN LƯỢC (làm đủ TRƯỚC) | TẦNG THỰC THI (content-first, sau) | Hiện trạng code |
|---|---|---|---|
| **D1 Positioning & product-mkt** | alternative · differentiator · category · value prop → Messaging House | trang/nội dung định vị | messaging (một phần) |
| **D2 Pricing & Offer** | mô hình giá · đóng gói theo giá trị | bảng giá · copy chào giá | — (mới) |
| **D3 Channel/GTM & Budget** | chọn kênh + phân bổ ngân sách + vai trò phễu (cắt theo capacity) | set-up chiến dịch từng kênh | funnel_map (một phần) |
| **D4 Content / Demand-gen** | Thông điệp · trụ · nhịp · timing (bản KẾ HOẠCH) | **gen bài đa kênh · calendar · journey · native · QC** | nhiều (gen/rhythm/calendar) |
| **D5 Lifecycle / Retention** | phễu · motion giữ khách · LTV | email/CRM sequence | — (mỏng) |
| **D6 Measurement** | KPI · target tree (từ objective) · success criteria | dashboard · nhập kết quả · đọc số | Ads snapshots (một phần) |

## Thứ tự build
```
P0 · SPINE (đã vá: positioning quan hệ, capacity = ràng buộc)
      ▼
GIAI ĐOẠN 1 · lấp TRỌN cột CHIẾN LƯỢC D1→D6  = BỘ NÃO CMO
      thứ tự nội bộ: D1 (nuôi mọi miền) → {D2, D3, D6 song song} → D5
      ↳ ship được: founder nhận 1 chiến lược marketing tích hợp dù chưa gen bài nào
      ▼
GIAI ĐOẠN 2+ · lấp cột THỰC THI, content (D4) trước → D3 → D2 → D5
      ↳ code content đang có = hạt giống D4-thực-thi, KHÔNG phí
      ▼
XUYÊN SUỐT · D6 Measurement (nối objective→kết quả) · Nudge chủ động (1 việc/lúc, ranked)
```
> **Vòng tri thức đi TRƯỚC build 1 nhịp:** mỗi ô chiến lược trước khi brief → research→craft card (3 đầu: thước · nhiên liệu gen · hàm ý thiết kế). Xem `WORKFLOW.md` + `KNOWLEDGE.md`.
> **Redesign lõi = gated:** đề xuất từ tri thức đi qua cổng Human+Orchestrator, không auto-apply.

## 7 NGUYÊN TẮC THIẾT KẾ (cross-cutting — mọi brief phải tuân)
1. **Chiến lược đủ TRƯỚC, thực thi sau.** Hoàn thiện cột chiến lược 6 miền = CMO thật; thực thi content-first. Đừng làm 1 miền full-stack rồi bỏ trống miền khác (thành content specialist, phản nhãn CMO).
2. **Spine = 3 trụ + 1 ràng buộc.** ① Objective (SỐ) · ② Audience (segmentation→ICP) · ③ **Positioning (cấu trúc QUAN HỆ**: khách làm gì nếu không có bạn → bạn khác biệt gì; Dunford — [nguồn](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning)). ④ **Capacity = ràng buộc** định hình phạm vi, KHÔNG phải trụ chiến lược co-equal.
3. **Đo được bằng SỐ.** `metric/target/baseline` = `{value, unit, period}` (trống được, có thì là số). Target chuỗi tự do → vòng đo-học (D6) không đóng.
4. **Capacity LÁI phạm vi.** Nhân lực/ngân sách/nhịp cắt số kênh (D3) + độ dài journey (D4). Persona thường 1 người → kê đơn "làm ÍT mà sâu", không đẩy user làm nhiều hơn sức.
5. **Data-in thật.** D6 phải có ô nhập kết quả kỳ (thủ công) — doanh thu SME VN ở Shopee/TikTok Shop/inbox/offline, không chỉ Ads snapshot.
6. **Nudge = 1 việc nên làm BÂY GIỜ** (ranked + capping), không đổ list. "List nudges" là mùi tool.
7. **Đa mục tiêu — chừa chỗ nới.** `spine` là bản mới nhất, đổi được theo mùa/chiến dịch lớn; đừng khoá cứng 1 objective vĩnh viễn.

## Ràng buộc (bất di bất dịch — CLAUDE.md)
- **KHÔNG đổi schema DB.** Dữ liệu mới → key trong `profile.intake_extra`. Kho tri thức (craft cards) = **file trong repo**, không phải data user, không phải bảng DB.
- **FE 1 nguồn duy nhất:** sửa thẳng `web/app.js` · `styles.css` · `index.html` — KHÔNG còn standalone để mirror (khai tử 2026-07-08, D-047).
- Tái dùng prompt trong `agents/` (lazy import), đừng tự chế prompt mỏng.
- Không bịa số trong output AI.

## Tham khảo được phép
- **Nguồn validate lõi (2026-07):** [Dunford positioning](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning) · [STP](https://www.adjust.com/glossary/stp/) · [CMO scope – AMA](https://www.ama.org/marketing-news/the-role-of-the-cmo/)/[Deloitte](https://www.deloitte.com/us/en/programs/chief-marketing-officer/articles/roles-of-the-cmo.html) · [content lifecycle](https://www.sitecore.com/resources/insights/content-strategy/content-marketing-lifecycle) · [SME budget-constraint](https://www.score.org/landoflincoln/resource/article/how-develop-a-marketing-strategy-a-limited-budget).
- **Codebase Max:** `webapp/business.py`, `docs/web/product-journey-4-tang.md`, `CLAUDE.md`.
- **Repo `marketingskills` (Corey Haines):** kho ứng viên framework (KHÔNG phải trọng tài) — `product-marketing`↔D1, `marketing-plan`↔chiến lược, `social`↔D4-native, `copywriting`↔D4-QC. Chỉ rút khung, mọi thêm/bỏ trường qua `EVAL.md`.
- **WIP channel-native:** `feature/content-quality-rationale` @ `3eaf474` (CHANNEL_SPECS + `_channel_block`) cho D4-thực-thi.

## Trạng thái
- **P0.1 spine đang build (treo để vá):** positioning → cấu trúc quan hệ; capacity giữ nguyên key `constraint` nhưng hạ nhãn. Xem `briefs/P0.1-strategy-spine.md`.
- Briefs từng ô ở `docs/cmo/briefs/` — Giai đoạn 1 (D1→D6 chiến lược) brief dần, mỗi ô có vòng tri thức đi trước.
