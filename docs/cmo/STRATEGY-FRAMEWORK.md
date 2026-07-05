# STRATEGY-FRAMEWORK.md — Khung 6 lựa chọn chiến lược (xương của Max)

> **Vì sao có file này:** Max cần một **khung phân tích chiến lược phổ quát** áp cho khách **đa ngành** — không bê nguyên một tờ khoá học, mà tổng hợp từ canon chiến lược có uy tín. File này chốt **xương** (6 lựa chọn); nội dung từng lựa chọn *thay đổi theo ngành* qua `brain/` vault.
> **Quan hệ với các doc khác:** `00-PLAN.md` = kiến trúc 2 tầng × **6 MIỀN** (thứ CMO *sở hữu*). File này = **6 LỰA CHỌN** (cách *dựng* chiến lược). Hai lăng kính bổ nhau, không thay nhau. Spine (P0.1) là hiện thân ~85% khung này.

## Nguồn research (2026-07) — không phán solo
- **Playing to Win** (Lafley & Martin, P&G) — chiến lược = 5 lựa chọn xếp tầng: *khát vọng thắng → chơi ở đâu → thắng bằng cách nào → năng lực lõi → hệ thống quản trị*. Chuẩn vàng "chiến lược thực sự là gì". ([fs.blog](https://fs.blog/playing-to-win-how-strategy-really-works/))
- **Strategy Diamond** (Hambrick & Fredrickson) — 5 yếu tố: Arenas · Vehicles · Differentiators · Staging · Economic logic. ([strategicmanagementinsight](https://strategicmanagementinsight.com/tools/hambrick-fredericksons-strategy-diamond/))
- **STP** (Kotler) — Segmentation → Targeting → Positioning; chuẩn marketing-strategy. ([Adobe](https://business.adobe.com/blog/basics/stp-marketing-model))
- **Positioning** (Dunford) — đối thủ thay thế → khác biệt → giá trị → khách tốt nhất → category. ([aprildunford](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning))
- **See-Think-Do-Care** (Kaushik) — chia theo Ý ĐỊNH khách: See/Think/Do/Care. ([kaushik.net](https://www.kaushik.net/avinash/see-think-do-care-win-content-marketing-measurement/))
- **AARRR** (McClure) — đòn bẩy tăng trưởng: Acquisition/Activation/Retention/Referral/Revenue. ([Amplitude](https://amplitude.com/blog/pirate-metrics-framework))

## 6 lựa chọn chiến lược (xương Playing-to-Win + nhồi marketing canon)

| # | Lựa chọn (Max hỏi/quyết) | Nội dung | Gốc | Producer hiện tại |
|---|---|---|---|---|
| 1 | **Khát vọng thắng** | mục tiêu đo bằng SỐ (outcome/metric/target/baseline/deadline) | PtW · OKR | `spine.objective` ✅ |
| 2 | **Chơi ở đâu** | phân khúc + tệp (ICP) + thị trường + kênh chính | STP(S+T) · Diamond Arenas | `spine.audience` + D3 ✅ (kênh mỏng) |
| 3 | **Thắng bằng cách nào** | định vị/lợi thế (Dunford: alternative→differentiator→value→best-fit→category) | Dunford · STP(P) | `spine.positioning` ✅ |
| 4 | **⚡ Hướng tăng trưởng trọng tâm** | ưu tiên đòn bẩy nào kỳ này: kéo mới / kích hoạt / giữ chân / lan truyền — theo ý định khách | **STDC + AARRR** | ⚠️ **THIẾU** (chỉ có "gate posture" rời) |
| 5 | **Năng lực & ràng buộc** | người/ngân sách/nhịp + giai đoạn trưởng thành | PtW Capabilities | `spine.constraint` + `spine.stage` ✅ |
| 6 | **Hệ thống đo & nguyên tắc** | KPI tree từ mục tiêu · làm/không làm · nhịp | PtW Mgmt Systems · AARRR metrics | D6 + giọng NÊN/TRÁNH ✅ |

> **Thông điệp cốt lõi KHÔNG phải 1 lựa chọn** — nó là **output** của #3 (Dunford nói rõ: positioning → messaging). Trong Max = `messaging` (Messaging House), sinh sau khi có #3.

## Đối chiếu Max hiện có → coverage ~85%, thiếu đúng #4
Spine (P0.1) build trên Dunford + STP thật, nên khung Max **vốn đã bám chuẩn vàng**. Research **xác nhận** hướng đúng; khoảng trống DUY NHẤT là **#4 Hướng tăng trưởng trọng tâm** — cũng chính là "phần 3" mà khung khoá học (ảnh nguồn) highlight, nhưng ta grounded nó trên STDC/AARRR thay vì 4 chữ tuỳ hứng.

## Spec #4 — Hướng tăng trưởng trọng tâm (mục tiêu build sau)

**Định nghĩa:** kỳ này Max **ưu tiên 1 đòn bẩy chính** (tuỳ chọn thêm 1 phụ) trong AARRR — nhưng là **TRỌNG SỐ, không bật/tắt**. Gộp Activation+Revenue của AARRR thành "Chốt đơn" cho hợp SME (SME không tách activation/revenue kiểu SaaS).

**4 đòn bẩy** (`spine.growth_focus` enum `acquisition|conversion|retention|referral|""`):

| Đòn bẩy | Nhãn VN (intake) | STDC | Nghĩa cho SME |
|---|---|---|---|
| **acquisition** | 🎯 Kéo khách mới biết đến | See·Think | chưa ai biết → cần phủ |
| **conversion** | 💰 Chốt đơn (quan tâm → mua) | Do | có quan tâm, thiếu đơn |
| **retention** | 🔁 Giữ khách quay lại | Care | mua 1 lần rồi mất |
| **referral** | 📣 Khách giới thiệu khách | Care→See | khách hài lòng, nhân lên |

**Intake (1 câu, chống friction):** *"Kỳ này bạn cần dồn sức vào đâu nhất?"* → 4 nhãn trên + *(bỏ trống → Max gợi ý từ giai đoạn)*. Chọn 1 chính, tuỳ chọn 1 phụ.

**Núm re-weight cả kế hoạch (đây là lý do #4 là lựa chọn hạng-nhất, không phải trang trí — bơm vào mà output KHÔNG đổi = trượt EVAL Test 3):**

| Focus | Nội dung D4 nghiêng | Kênh D3 | Metric D6 trọng tâm |
|---|---|---|---|
| Kéo mới | hook, phủ rộng, cho người CHƯA biết | reach cao (TikTok/FB/SEO) | người mới · reach · CPM |
| Chốt đơn | review, so sánh, chào giá, CTA mạnh | retargeting · landing · inbox | CR · số đơn · CPL |
| Giữ chân | hướng dẫn dùng, chăm sóc, upsell | email/Zalo/CRM sequence | mua lặp · LTV · churn |
| Giới thiệu | khơi chia sẻ, UGC, ưu đãi ref | community · referral program | % từ giới thiệu · K-factor |

**Degrade khi bỏ trống (derived-state, theo WIRING):** gợi ý mặc định từ `stage` — launch→Kéo mới · growth→Chốt đơn · scale→Giữ chân/Giới thiệu. Lưu `{current:{value,confidence,updated}, log:[{why,by}]}`; confidence thấp → **gợi ý chứ KHÔNG đè**; người chốt (`by:human`) thắng.

**2 điểm phải giữ đúng (kẻo lẫn/lệch):**
1. **`stage` ≠ `growth_focus`.** Stage = độ trưởng thành; focus = đòn bẩy ưu tiên *lúc này*. Shop scale vẫn có thể focus Kéo-mới khi mở thị trường mới → **giữ 2 field RIÊNG**, stage chỉ *gợi ý* focus mặc định.
2. **Trọng số, không bật/tắt.** Focus Chốt-đơn KHÔNG bỏ hẳn branding. `_spine_anchor` phải ghi *"ưu tiên X, không bỏ phần còn lại"* — tránh Max làm lệch cực đoan.

**Xuôi dòng (consumer):** D4 (nghiêng dạng/nhịp nội dung) · D5 (bật motion giữ chân khi focus=retention) · D6 (chọn 1 metric trọng tâm khớp đòn bẩy, không đo tất) · bơm prompt qua `_spine_anchor` (P0.2).

**Theo ngành (vault):** `brain/industries/*` tag đòn bẩy trội (F&B→retention/referral; D2C launch→acquisition) làm gợi ý mặc định — vẫn người chốt.

**Seam/WIRING:** khoá mới `spine.growth_focus` (enum `acquisition|conversion|retention|referral|""`). Producer = Spine intake (người khai) + Max-suy (derived, để sau). Consumer = D4/D5/D6 + `_spine_anchor`. Thêm dòng vào Sổ hợp đồng khi build slice GF.

## Ranh giới
- File này là **xương + spec**, KHÔNG code. Build #4 = slice riêng (xem INDEX).
- KHÔNG thay `00-PLAN` (6 miền) — bổ sung lăng kính "6 lựa chọn".
- Mọi thêm/bỏ trường vẫn qua `EVAL.md` (Test 1/2/3).

## Liên kết
`00-PLAN.md` (6 miền) · `WIRING.md` (sổ hợp đồng — thêm `spine.growth_focus`) · `EVAL.md` (validate trường #4) · `briefs/00-INDEX.md` (slice build #4).
