# SESSION HANDOFF — phiên hội đồng 2026-07-11 (Claude Fable + founder)

> Mục đích file: mở ở PHIÊN KHÁC là nắm được toàn bộ ngữ cảnh + quyết định, không cần đọc lại hội thoại.
> Tài liệu chuẩn đi kèm: `CHAIN-V2-KIENTRUC.md` (kiến trúc chốt) · `PB-WIRE-tasks.md` (task PR-A/B/C).

## Dòng thời gian quyết định trong phiên

1. **Hội đồng V1 (PB-WIRE T1–T3)** — chốt 7 điểm, ĐÃ ghi vào brief + tasks + code push
   (`feature/pb-wire-t1-t3`, commit `5c4c462` docs / `c4e2f73` code): max_tokens 10k, JSON compact +
   không cắt JSON, validate 2 mức, strip JSON khỏi markdown, cut TƯƠNG ĐỐI, thêm `insight` segment-level,
   luật compliance/seeding. **Q-A/Q-B/Q-C CHƯA có trong code — cần bổ sung khi code tiếp.**
2. **Bằng chứng thật đã soi** (Railway `marketing-os-bot-production.up.railway.app`, user_id 990555, spa Q3):
   - Playbook v2 (run `606d1bb7`) CỤT ở trần 4000 token, tự bịa ngưỡng tuyệt đối, đề xuất seeding giả.
   - Slot lịch thật KHÔNG có `dang`/`track_role` (đường fallback pillars) — chỉ có `funnel`;
     4/36 slot nhãn rác `"TOFU|MOFU"`.
   - Funnel map cũ: mồ côi consumer + string đứt giữa câu lưu thẳng DB.
   - Lịch chạy 33/44/11 (TOFU/MOFU/BOFU) — NGƯỢC tỉ lệ 60/30/10 chính hệ thống khuyên; 9 bài/tuần
     cho team 2-3 người (quá tải).
   - **0 run** calendar_post/derivative trên toàn deployment — chưa có baseline bài thật.
3. **Hội đồng V2 (T4–T5 cũ) đã họp + runtime sửa lưng** → nhưng sau đó founder ĐỔI KIẾN TRÚC (mục 5)
   → các chốt V2 (funnel/dang qua API, SWAP tact[:1400], bảng map dang→tier) **KHÔNG thi hành nữa**,
   chỉ giữ làm tư liệu.
4. **Research 2 agent (không dựa codebase):**
   - Content ops chuẩn: pipeline 6 bậc; repurpose SAU bài gốc TRƯỚC lịch; slot có trước bài đổ sau;
     mẹ-con (1 pillar → nhiều micro); nguồn GaryVee/COPE/HubSpot/Justin Welsh.
   - Vòng đo organic: so TƯƠNG ĐỐI median chính kênh (không so số ngành — kill oan 90 ngày đầu);
     3–5 bài/góc mới kết luận; review tuần=tactical tháng=trend; feedback tuần→lịch, tháng→mix/trụ.
   - Agent 3 (khảo sát sản phẩm AI CMO: Jasper/Lately/FeedHive) bị dừng giữa chừng — chưa có kết quả.
5. **Founder chốt KIẾN TRÚC MỚI (quan trọng nhất phiên)** — xem `CHAIN-V2-KIENTRUC.md`:
   Góc đánh → Thông điệp → **KEY IDEA (1 ý/đợt, user đặt kỳ hạn, Max đề xuất từ struct + user thêm)**
   → **FUNNEL MAP của key idea** → **CALENDAR thẻ chứa post (sinh khi bấm)** → đo cuối đợt.
   Hợp nhất 2-track thành chuỗi đợt. Repurpose = thẻ anh em cùng idea.
6. **Bộ luật T3 Thông điệp chốt trọn** (cốt lõi 1 ý + 4 dạng kẻ thù · 3 trụ 2 cửa · proof núm-vặn-giọng
   5 hạng + 3 bậc khi không có proof · hội đồng UX chốt: không thêm bước onboarding, chỉ chip + gợi ý;
   phát hiện: ô proof đã có `app.js:1883` nhưng máy viết không đọc `business.py:2867`).

## Trạng thái việc

| Việc | Trạng thái |
|---|---|
| PB-WIRE PR-A (T1-T3 struct) | ✅ code + push, CHƯA mở PR → staging; còn nợ Q-A/Q-B/Q-C |
| PB-WIRE PR-B (T4-T5 cũ) | ⛔ TẠM DỪNG — kiến trúc mới thay thế |
| Brief B1 (T3 Thông điệp) | ⬜ đủ luật, CHƯA viết brief |
| Brief B2 (Key Idea + Funnel map mới) | ⬜ chưa viết — cần seam analysis JIT |
| Brief B3 (Calendar thẻ-chứa-post) | ⬜ chưa viết |
| Nợ ghi sổ | funnel map cũ cụt-im-lặng · enum funnel thiếu Retention · nhãn rác TOFU\|MOFU |

## Quy trình làm việc founder muốn (ghi nhớ khi tiếp tục)

- **Làm TỪNG BƯỚC MỘT** — không nhảy cóc, mỗi tầng chốt xong mới sang tầng sau.
- Phiên thảo luận (Claude + founder) chốt spec → **phiên khác (Opus 4.8) code**.
- Trình bày: verdict trước, ✅TỐT/❌HỎNG/📋LÀM GÌ, nói bằng hệ quả kinh doanh, không nói tên field.
- Đánh giá phải soi CẢ code LẪN output/runtime thật (đã 2 lần runtime sửa lưng phân tích code-only).
- Format hội đồng persona được founder thích — nhưng biên bản NGẮN, chốt RÕ.
