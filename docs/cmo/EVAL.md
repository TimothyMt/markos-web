# EVAL — Standard đánh giá: một trường/tính năng có "kiếm được chỗ" không?

> Dùng cho **MỌI phase** (không riêng spine): mỗi lần thêm dữ liệu/tính năng đều qua đây. Đây là *standard* mà Orchestrator + auto-review căn vào — nên nó nằm ngoài hội thoại, trong file.

## Nguyên tắc trọng tài
- Repo tham khảo (`marketingskills`…) là **kho ứng viên trường + cách diễn đạt**, KHÔNG phải trọng tài. Nó viết cho SaaS; nhiều ô thừa với SME/đa-mảng VN.
- "Tốt hơn" **không** căn cứ "framework nó ghi vậy" (appeal to authority) hay "gọn/đẹp" (cảm tính). Trọng tài là **công dụng downstream trong chính Max** + **hợp persona** + **bằng chứng thực nghiệm**.

## Test 1 — CONSUMPTION (trọng tài chính, ổn định)
Trường này có được một **lớp output sau** đọc để RA QUYẾT ĐỊNH không? Ghi rõ **lớp nào**. Không nuôi quyết định nào → trang trí → **BỎ**, dù "canonical" đến đâu.

Đo ở **5 lớp — mỗi lớp một hướng khác nhau** (không chỉ "gen post"):

| Lớp output | Test hỏi: trường này có làm ĐỔI…? |
|---|---|
| **L1 Chiến lược** (Đặt cược → Synthesis → Messaging) | …**lựa chọn chiến lược**: cược vào đâu, góc tiếp cận, thông điệp cốt lõi + nhất quán định vị? (đổi *hướng*, không phải chữ) |
| **L2 Kế hoạch** (master plan, timing, calendar_plan) | …**hình dạng kế hoạch**: timing spike, mix kênh, **nhịp/khối lượng khớp capacity**, thứ tự? |
| **L3 Chiến dịch** (portfolio, journey/arc) | …**cái arc**: số điểm chạm, phủ đủ tầng phễu (nhận biết→chuyển đổi), cấu trúc offer, có leo về objective? |
| **L4 Sản xuất** (gen post, channel-native) | …**đơn vị nội dung**: hook, bằng chứng, CTA hướng mục tiêu, format native theo kênh? |
| **L5 Đo & Học** (P4) | …tạo **tín hiệu so được**: tính gap-to-target, quy attribution, ra chỉ số dẫn? |

→ Đạt nếu lái được **≥1 lớp**. Kết quả = **map "trường × lớp"** (chính là consumption map). Ví dụ: `objective.target(số)` → L2+L3+L5; `audience.where` → L2; `positioning` → L1+L4.

## Test 2 — ANSWERABILITY (theo BẬC persona, không hard-cut)
User là **một dải: founder solo → CMO → leader marketing nhiều mảng**. Không lọc bằng "SME 1 người điền nổi không" (sẽ cắt nhầm trường CMO cần). Thay bằng **progressive disclosure**:
- **Trường LÕI** — ai cũng điền nổi 1 dòng (outcome, metric+target số, who, positioning, capacity). Bắt buộc hiện.
- **Trường NÂNG CAO** — *tùy chọn*, cho user tinh vi (vd đối thủ/alternatives, phân khúc phụ, phân bổ ngân sách). Ẩn/thu gọn để solo bỏ qua, CMO mở ra.
- Neo `capacity` chính là tín hiệu user đang ở bậc nào → không cần hỏi bậc riêng.
→ Trượt: trường bắt *mọi* user nghĩ như phòng marketing lớn mà không thể để tùy chọn.

## Test 3 — EMPIRICAL (bằng chứng xác nhận, KHÔNG phải trọng tài chính)
Output LLM ngẫu nhiên → đừng để 1 lần chạy định đoạt. Cách chạy:
- **3 archetype** (vì trường vô dụng với cái này có thể quyết định với cái kia):
  1. Shop **D2C 1 người** (bán hàng online, capacity thấp)
  2. **SME có team nhỏ** (2–5 người, đa kênh)
  3. **Dịch vụ/tư vấn gom lead** (B2B nhẹ, chu kỳ dài)
- Với mỗi trường đang xét: set spine **CÓ** vs **KHÔNG** trường đó → chạy gen ở **đúng lớp mà Test 1 nói nó cắn** (không nhất thiết L4) → xem output **khác có hệ thống** không.
- Người đọc phán "có nghĩa không", **không diff máy**. Không đổi ở lớp nào cả, trên cả 3 archetype → nghi trượt.

## Cổng quyết định (ai chốt)
- Cline **chạy ma trận + xuất artifact** `docs/cmo/eval/<phase>-<tên>-eval.md` (bảng trường×lớp + vài đoạn output có/không-trường). **KHÔNG tự cắt trường.**
- Keep/cut = **quyết định sản phẩm** → chốt ở **cổng review (Human + Orchestrator)**, khớp WORKFLOW bước 6.
- Mọi **lệch** so cấu trúc gốc (thêm/bỏ trường) → **ghi lý do theo 3 test** trong artifact + commit. Không bê nguyên framework, không đổi mù.

## Mẫu artifact (rút gọn)
```
# <phase> eval — <tên>
## Test 1 (map trường × lớp)
| trường | L1 | L2 | L3 | L4 | L5 | giữ? |
|---|---|---|---|---|---|---|
| objective.target | | ✔ | ✔ | | ✔ | giữ |
| <trường mượn framework X> | | | | | | ? |
## Test 2 (bậc persona) — lõi / nâng cao / trượt + lý do
## Test 3 (3 archetype) — trích output CÓ vs KHÔNG, ở lớp Test 1 chỉ ra
## Đề xuất cho cổng: giữ / bỏ / để nâng-cao — chờ Human+Orchestrator chốt
```
