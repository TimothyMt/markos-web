# HOÀ GIẢI 2 LUỒNG TƯ DUY SẢN PHẨM MAX — cho CEO quyết

> 2026-07-09 · Mục đích: gộp **2 luồng định hình sản phẩm đang chạy song song** thành 1 bức tranh để
> CEO ra quyết định. KHÔNG tự chốt — chỉ bày ra chỗ khớp, chỗ lệch, và các điểm cần bạn quyết.
>
> **Luồng 1 — Hội đồng persona** (`product-council-2026-07-07.md`, nhánh `feature/research-scrub`):
> tranh luận *Max NÊN LÀ GÌ* (danh tính · GTM · business model). Kết = 4 QĐ CEO **chưa chốt**.
> **Luồng 2 — CMO-core** (`docs/cmo/`, nhánh `feature/ai-cmo-core`): bản thiết kế *đã chốt hướng + đang
> BUILD* — Max = AI CMO, **2 tầng × 6 miền**, Strategy Spine, đã commit P0/K1/K2/P0.1/P0.2.
>
> Chúng **bổ sung** nhau (WHAT/WHY vs HOW), không phải bản nháp của nhau.

---

## PHẦN 1 — 4 QĐ của hội đồng, đối chiếu trạng thái CMO-core

| QĐ | Hội đồng hỏi | CMO-core đã trả lời chưa? | Còn phải quyết gì |
|---|---|---|---|
| **QĐ1 · Danh tính** (A→B→C tuần tự / A+B rồi dồn C / B trước) | Max là con gì 12 tháng tới | **NỬA rồi:** CMO-core chốt "strategist-first, không content-tool" = đúng tinh thần A-là-linh-hồn. **Nhưng** không bàn *sequencing A→B→C* + lens *business-model/churn*. | Chốt **thứ tự phát hành** (cố vấn→làm hộ→vận hành) + có lấy lens churn/LTV làm kim chỉ nam không |
| **QĐ2 · Triết lý input** (N3→N2 + nghi thức câu lựa chọn + 3-số-tiền) | Khách nhập gì | **Khớp mạnh:** Spine đã bắt `objective(SỐ)` + progressive disclosure (EVAL Test 2) + capacity. **Nhưng** thiếu **N3 hút-từ-link** + "kể khổ tự do". | Có đưa N3 (hút link fanpage/web/sàn) làm cửa vào không → **giao với D-048 ScrapeCreators** |
| **QĐ3 · Trục output** (bản đồ 1 trang / bảng tuần) | Dồn lực tầng nào trước | **Một phần:** CMO-core có 5 lớp output (EVAL L1-L5) nhưng để *đánh giá*, chưa chốt *cái nào user thấy trước*. Nudge chủ động ≈ bảng tuần. | Chốt **mặt tiền user**: "1 trang dán tường" hay "bảng tuần" là thứ làm xuất sắc trước |
| **QĐ4 · Function đầu sau lõi** (F1 đo-học / F3 KPI ngược / F2 xưởng content) | Làm gì kế | **Khớp:** F1 đo-học ≡ D6 Measurement "xuyên suốt". F3 KPI-ngược ≡ Spine objective→target tree. | Chốt F1 hay F3 làm **spike giá trị** đầu tiên (cả hai đều đã nằm trong khung CMO-core) |

**Đọc bảng này:** QĐ1 & QĐ2 **phần lớn đã được CMO-core định hướng** — chỉ cần bạn xác nhận + bổ sung phần hội đồng thêm. QĐ3 & QĐ4 là **lựa chọn ưu tiên**, không phải lựa chọn kiến trúc.

---

## PHẦN 2 — 3 điểm LỆCH thật (checklist merge, bắt buộc xử trước khi 2 nhánh gặp nhau)

### L1 · 🔴 Luật mirror standalone: CHẾT ở nhánh này, CÒN SỐNG ở `docs/cmo/`
- **Nhánh `research-scrub`:** D-047 đã **xoá hẳn** `dashboard-standalone.html` + `build_standalone.py`, gỡ luật mirror.
- **`docs/cmo/`:** `00-PLAN §Ràng buộc`, `WORKFLOW`, `briefs/00-INDEX` **vẫn bắt buộc** mirror `app.js ↔ standalone` + verify command đọc file standalone (đã bị xoá).
- **Rủi ro:** merge `ai-cmo-core` → tái sinh luật chết + lệnh verify đọc file không tồn tại → Cline làm theo sẽ lỗi/loạn.
- **Việc:** khi merge, sửa `docs/cmo/` bỏ mọi dòng mirror + đổi verify command (bỏ dòng standalone). **Chưa làm.**

### L2 · 🔴 Fork khung sản phẩm: "4 tầng nội dung" vs "6 miền CMO"
- **Nhánh này:** `roadmap.md v2` + `product-journey-4-tang.md` tổ chức theo **4 tầng** (Nghiên cứu→Chiến lược→Sáng tạo→Phân phối).
- **CMO-core:** `00-PLAN` nói thẳng *"4 tầng nội dung chỉ ~40% việc CMO"* → thay bằng **6 miền** (D1 Positioning · D2 Pricing · D3 Channel/Budget · D4 Content · D5 Retention · D6 Measurement).
- **Bản chất:** KHÔNG mâu thuẫn — **4 tầng ≈ D4 (Content) trải dài + chạm D6**. CMO-core mở rộng chứ không phủ nhận. Nhưng **chưa ai chốt khung nào là chính thức** → 2 roadmap, 2 cách nói.
- **Việc:** 1 quyết định chốt: *"khung chính = 6 miền; 4 tầng = cách triển khai D4"* hay giữ song song. **Chưa làm.**

### L3 · 🟡 2 nhánh, 2 roadmap, chưa có nguồn "làm gì tiếp" chung
- `feature/research-scrub` = verify research (R-1) + N-xx + D-048 ScrapeCreators.
- `feature/ai-cmo-core` = spine + lấp cột chiến lược 6 miền (P0 xong, D1→D6 tiếp).
- **Rủi ro:** làm chồng/lệch (vd cả 2 đụng messaging/positioning; cả 2 cần competitor data).
- **Việc:** chọn **1 nhánh làm trục chính**, nhánh kia rã vào; hoặc định rõ ranh giới. **Chưa làm.**

---

## PHẦN 3 — Điểm giao có lợi (không phải lệch, mà là cộng hưởng)
- **D-048 ScrapeCreators phục vụ CẢ 2 luồng:** N3 cửa-vào (hội đồng) + F4 trạm-đối-thủ (hội đồng) + grounding D1 Positioning/D-competitor (CMO-core). → giữ nguyên ưu tiên, đây là hạ tầng dùng chung.
- **Vòng đo-học** = F1 (hội đồng) = D6 (CMO-core) = auto-pull Lô I+ (roadmap tầng ④). **3 tên gọi, 1 thứ.** Khi làm chỉ làm 1 lần.
- **Messaging House** đã có (nhánh này) = D1 execution (CMO-core). Không làm lại.

---

## PHẦN 4 — Việc kế (chờ CEO quyết ở reply, tôi chưa làm gì)
Xem danh sách "điểm cần quyết" gửi kèm. Sau khi bạn chốt → tôi ghi thành **D-048b…D-05x** trong `DECISIONS.md`
+ cập nhật `roadmap.md`, và (nếu chọn) soạn plan merge `docs/cmo/` cho sạch 3 điểm lệch.
