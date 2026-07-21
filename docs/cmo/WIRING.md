# WIRING.md — Cổng kiểm mối nối (seam check)

> **Vì sao có file này:** lỗi nguy hiểm nhất không phải bug trong 1 hàm — mà là **lỗ hổng ở MỐI NỐI**: component A *tiêu thụ* một khoá dữ liệu mà **không component nào sản xuất** ra nó, hoặc sản xuất dưới **tên/kiểu/slug lệch**. Loại lỗi này **im lặng tới runtime mới nổ**.
> Ví dụ thật (2026-07): `select()` của recall cần `(industry, stage, goal_type)` nhưng `stage` **không ai khai** → chỉ lộ khi có người truy ngược "khoá này ai đẻ ra".
> Đây là **cổng CTO bắt buộc** ở mỗi slice, chạy TRƯỚC khi PASS — không đợi run.

## Hiến pháp mối nối — áp cho MỌI function của dự án (bất biến toàn cục)
> Nâng từ bài học K1/F2 thành **luật chung**: mọi function (brain, P*, D*, route, FE…) đều qua. Đây là bất biến — chốt 1 lần, không phân tích lại từng lần.

1. **Khai hợp đồng.** Mọi khoá dữ liệu function *đọc* hoặc *ghi* phải có 1 dòng trong "Sổ hợp đồng" dưới: `{consumer · producer · kiểu · slug/enum · status}`. **Khoá không có producer = FAIL** (đây là lỗ hổng đã suýt lọt với `stage`).
2. **Khớp mối nối (4 câu truy ngược).** (a) producer tồn tại? (b) tên/slug/enum khớp CHÍNH XÁC 2 đầu? (c) kiểu khớp (object vs string, list vs scalar)? (d) producer chạy TRƯỚC consumer lúc runtime?
3. **Đường degrade.** Input có thể thiếu/thô → định nghĩa fallback êm (vd family→slug tinh), không để vỡ.
4. **Luật derived-state** (xem mục riêng) nếu function tự suy trạng thái user.
5. **Kế thừa CLAUDE.md:** không đổi schema DB (khoá mới → `intake_extra`) · FE 1 nguồn (sửa thẳng `web/`, không mirror standalone — D-047) · không bịa số · 1 function = 1 commit + self-verify.

## Hai tốc độ (chống overload — không boil-ocean)
```
TỐC ĐỘ 1 — Hiến pháp (1 lần, đã chốt ở đây)   → bất biến, mọi function tuân, KHÔNG phân tích lại
TỐC ĐỘ 2 — Phân tích mối nối / từng function    → JIT tại brief-time, CHỈ function sắp build
```
- **Vì sao JIT:** phân tích function chưa build là phí + mốc (thiết kế phía trước còn trôi). Chỉ **bất biến toàn cục** đủ ổn định để chốt sớm; **mối nối cục bộ** rẻ & chính xác nhất khi làm ngay lúc viết brief (đi trước build 1 bước).
- **Hook bắt buộc:** mỗi brief function có mục **"Phân tích mối nối"** → điền dòng hợp đồng cho function đó + **note phần Hiến pháp không phủ** (addendum riêng của function). Cổng review chỉ PASS khi mục này xong.

Mẫu mục "Phân tích mối nối" (chép vào mỗi brief):
```md
## Phân tích mối nối (theo WIRING Hiến pháp)
- Khoá ĐỌC: <key> ← producer: <ai/đâu> · kiểu · khớp? · status
- Khoá GHI: <key> → consumer dự kiến: <ai> · kiểu
- Derived-state? (có/không) → nếu có: log confidence/why + review gate
- Degrade khi thiếu input: <mô tả>
- Addendum (Hiến pháp KHÔNG phủ chỗ nào cho function này): <ghi hoặc "không">
```

## Luật derived-state — khi Max TỰ SUY trạng thái user
> Áp cho MỌI thứ Max tự quyết về user (ngành tinh, `stage`, funnel, phân khúc…), không chỉ ngành. Để Max tự quyết mà không để vết = drift âm thầm → rối.

**Bắt buộc mọi quyết định suy luận:**
- Lưu vào `intake_extra` (append-only, cap ~20 sự kiện, KHÔNG đổi schema):
  `{ current: {value, confidence, updated}, log: [{ts, from, to, confidence, why:[tín hiệu], by}] }`.
- **`why`** ghi rõ tín hiệu nào đẩy quyết định (đọc log là hiểu, không phải đoán).

**3 luật chống rối:**
1. **Sàn tự tin** — `confidence` thấp → KHÔNG override, giữ mức thô + cờ "cần thêm tín hiệu".
2. **Đóng băng khi dao động** — value lật A→B→A ngắn hạn → freeze + cờ review (người/CTO xử).
3. **Con người thắng** — có đường sửa rẻ; value do người chốt (`by:"human"`) thì Max KHÔNG tự đè.

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
| `industry` (family) | slug kebab | `brain.select()` (K2/K3) | profile `industry` (đã có, 14 key) — chuẩn hoá `.replace("_","-")` ở recall | canonical = 14 key; note family khớp | ✅ **B** (đã chốt: 14 key làm gốc, degrade family) |
| `industry` (slug tinh) | slug kebab | `brain.select()` degrade | **Max suy ra** (classifier, derived-state) — không phải intake | note tinh (seed dần) | ✅ nguồn = derived; degrade→family nếu chưa có note tinh |
| `stage` | enum `launch\|growth\|scale` | `brain.select()` (K2/K3) | **P0.1 Spine** (hỏi 1 câu, người khai; validate ∈ 3 slug `brain/stages/`) | slug khớp file stage; `""`→`select(stage=None)` | ✅ **A1 gộp P0.1** (người khai). Lớp Max tinh chỉnh theo tín hiệu = **A2** tương lai (derived-state) |
| `goal_type` | enum D1–D6 | `brain.select()` (K2/K3) | **call-site** (feature đang chạy truyền vào), KHÔNG phải intake | n/a | ✅ (nguồn = call-site) |
| `status==live` | enum | `brain.select()` | governance (draft→reviewed→live) | — | ✅ luật đã định (KNOWLEDGE.md) |

### Hợp đồng Spine (P0.1): `intake_extra.spine`
| Khoá | Kiểu | Consumer | Producer | Status |
|---|---|---|---|---|
| `spine.objective.target.value` | number\|null | P0.2 prompt · D6 đo gap | P0.1 F1 `save_spine` (ép số **locale VN**) | ✅ build (07eb89d) |
| `spine.positioning` | **object** `{alternative,differentiator,statement}` | P0.2 prompt · D1 | P0.1 F1 (KHÔNG phải chuỗi) | ✅ build (07eb89d) |
| `spine.constraint` | object | D3/D4 cắt phạm vi | P0.1 F1 | ✅ build (07eb89d) |
| `spine.stage` (A1 gộp) | enum `launch\|growth\|scale\|""` | `brain.select()` (qua K3) | P0.1 F1/F4 (người khai, validate enum) | ⚠️ **dual-producer**: cũng có `profile.stage` (intake). Nay không vỡ (select đọc spine.stage); **A3** hợp nhất (spine pre-fill từ profile). Cùng: `audience.who↔target_customer`, `positioning↔usp` |

### Hợp đồng Auth (Luồng B): session ↔ user_id ↔ entitlement
| Khoá | Kiểu | Consumer | Producer | Khớp | Status |
|---|---|---|---|---|---|
| session `uid` | int\|None | `UidContextMiddleware`→`business._current_uid`→`pick_user_id` | OAuth callback `google_oauth.callback` set `request.session['uid']` | cookie ký (itsdangerous) | ✅ build |
| session `email` | str | `api._is_admin` (gác `/api/admin/*`) | OAuth callback set `session['email']` | so `ADMIN_EMAILS` (lower) | ✅ build |
| `auth_identities.(provider,external_id)` | (text,text) UNIQUE | `find_or_create` | Google `sub` | sub ≤ chuỗi; user_id nội bộ tách khỏi sub | ✅ build |
| `auth_identities.user_id` | bigint FK→users | `find_or_create`, `admin_*`, `biz_data.identity` | `web_user_id_seq` (DEFAULT trên `users.user_id`) | seq ≥ 10^12, trên dải Telegram | ✅ build |
| `auth_identities.status` | enum `pending\|active\|blocked` | `quota.ensure_can_spend` (gate), FE `bizAuthStatus` | `find_or_create`(pending) · `admin_set_access` | **gate TRUY CẬP**, KHÁC `token_quota` | ✅ build |
| `users.token_quota/used` | int | `quota.ensure_can_spend` (chặn cứng), `record_usage` | admin kích hoạt (quota) · `_post_hook` (used) | **ngân sách token**, KHÁC status | ✅ build |
| `bizAuthed/bizAuthStatus/bizEmail/bizIsAdmin` | bool/enum/str/bool | FE `_authGateMode`, `P.admin` | `biz_data` (từ identity) | tên khớp FE↔`biz_data` | ✅ build |
| `bizUsers` | list | FE user-switcher, `P.admin` | `biz_data` — **chỉ khi `is_admin`** (non-admin → `[]`) | chống rò danh sách user | ✅ build (siết) |

> **Seam quan trọng:** hàm user-scoped (59 hàm) đọc user_id CHỈ qua `pick_user_id` (choke point đã verify 0 bypass). HTTP → contextvar (session) là nguồn DUY NHẤT, `requested` client **inert**. `admin_*` CỐ Ý nhận user_id tường minh (thao tác trên user khác) → bảo vệ bằng gác `ADMIN_EMAILS` ở api layer, KHÔNG qua `pick_user_id`.

## Khi nào chạy cổng này
- **Brief-time (mọi function):** điền mục "Phân tích mối nối" (Tốc độ 2) — dòng hợp đồng + addendum. Không có = brief chưa xong.
- **Mỗi slice K***: chạy `py brain/_check.py` (Lớp 1) + rà Lớp 2 cho khoá slice đụng tới.
- **Mỗi slice tiêu thụ/đẻ khoá xuyên component** (P*, D*, route, FE): rà 4 câu Hiến pháp + cập nhật Sổ hợp đồng; nếu tự suy trạng thái → áp Luật derived-state.
- Kết quả rà dán vào review CTO của slice (giống self-review của builder). Cổng PASS = Hiến pháp qua hết.
