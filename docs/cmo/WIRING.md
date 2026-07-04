# WIRING.md — Cổng kiểm mối nối (seam check)

> **Vì sao có file này:** lỗi nguy hiểm nhất không phải bug trong 1 hàm — mà là **lỗ hổng ở MỐI NỐI**: component A *tiêu thụ* một khoá dữ liệu mà **không component nào sản xuất** ra nó, hoặc sản xuất dưới **tên/kiểu/slug lệch**. Loại lỗi này **im lặng tới runtime mới nổ**.
> Ví dụ thật (2026-07): `select()` của recall cần `(industry, stage, goal_type)` nhưng `stage` **không ai khai** → chỉ lộ khi có người truy ngược "khoá này ai đẻ ra".
> Đây là **cổng CTO bắt buộc** ở mỗi slice, chạy TRƯỚC khi PASS — không đợi run.

## 2 lớp kiểm

### Lớp 1 — Linter cơ học (chạy được, tự động)
`brain/_check.py` — bắt **synapse đứt** trong vault: `[[link]]` / `applies_to` / `fit_frameworks` / `expresses` / `industry` / giá trị `stage:` PHẢI trỏ tới file/slug có thật; `slug` khớp tên file.
```bash
py brain/_check.py     # exit 0 = thông · exit 1 = có synapse đứt
```
Chạy sau MỌI slice K* (thêm/sửa note brain). Không phụ thuộc pyyaml.

### Lớp 2 — Sổ hợp đồng + luật truy ngược (con người + CTO)
Linter chỉ thấy **trong vault**. Mối nối **xuyên hệ** (intake → recall → loader → call-site) thì linter không thấy — phải kiểm bằng **sổ hợp đồng** dưới đây.

**LUẬT (CTO chạy ở mỗi slice, trước khi PASS):**
Với **mọi khoá dữ liệu** mà code mới *đọc* hoặc *ghi*, truy 4 câu:
1. **Producer tồn tại?** — Khoá này ai GHI ra? (intake nào / slice nào / call-site nào). Không có producer = **FAIL**.
2. **Tên/slug/enum khớp?** — Chuỗi khoá & giá trị khớp CHÍNH XÁC hai đầu? (recall muốn `d2c-skincare` — intake có ghi đúng slug đó không, hay ghi `health_beauty`?).
3. **Kiểu khớp?** — object vs string, list vs scalar (vd bug `positioning` = chuỗi thay vì object).
4. **Tới được lúc chạy?** — Producer có thật sự chạy TRƯỚC consumer ở runtime không?

Bất kỳ câu nào "không" → ghi vào sổ dưới dạng **hàng GAP**, và slice tiêu thụ khoá đó **KHÔNG được PASS** cho tới khi có producer.

## Sổ hợp đồng — các khoá xuyên ranh giới

> Cập nhật mỗi khi thêm khoá xuyên component. `status`: ✅ nối · ⚠️ lệch (có nhưng sai tên/kiểu/slug) · ❌ thiếu producer.

### Hợp đồng recall: `select(industry, stage, goal_type)` (K3 sẽ cắm)
| Khoá | Kiểu | Consumer | Producer | Khớp? | Status |
|---|---|---|---|---|---|
| `industry` | slug (kebab) | `brain.select()` (K2/K3) | profile `industry` (đã có) — **taxonomy cũ** `fnb/ecommerce/health_beauty…` | slug **lệch** brain (`d2c-skincare/service-local`) | ⚠️ cần **B** (hợp nhất taxonomy / lớp map) |
| `stage` | enum `launch\|growth\|scale` | `brain.select()` (K2/K3) | **CHƯA AI** — Spine không hỏi; `stage` trong code là stage-phễu (khái niệm khác) | — | ❌ cần **A1** (thêm ô stage vào Spine) |
| `goal_type` | enum D1–D6 | `brain.select()` (K2/K3) | **call-site** (feature đang chạy truyền vào), KHÔNG phải intake | n/a | ✅ (nguồn = call-site) |
| `status==live` | enum | `brain.select()` | governance (draft→reviewed→live) | — | ✅ luật đã định (KNOWLEDGE.md) |

### Hợp đồng Spine (P0.1): `intake_extra.spine`
| Khoá | Kiểu | Consumer | Producer | Status |
|---|---|---|---|---|
| `spine.objective.target.value` | number\|null | P0.2 prompt · D6 đo gap | P0.1 F1 `save_spine` (ép số **locale VN**) | ⬜ chưa build |
| `spine.positioning` | **object** `{alternative,differentiator,statement}` | P0.2 prompt · D1 | P0.1 F1 (KHÔNG phải chuỗi) | ⬜ chưa build |
| `spine.constraint` | object | D3/D4 cắt phạm vi | P0.1 F1 | ⬜ chưa build |
| `spine.stage` ⟵ **thêm ở A1** | enum | `brain.select()` | P0.1 (mở rộng) | ❌ chưa có |

## Khi nào chạy cổng này
- **Mỗi slice K***: chạy `py brain/_check.py` (Lớp 1) + rà Lớp 2 cho khoá slice đụng tới.
- **Mỗi slice tiêu thụ khoá từ intake/recall** (P*, D*): rà Lớp 2 — khoá có producer chưa, khớp chưa.
- Kết quả rà dán vào review CTO của slice (giống self-review của builder).
