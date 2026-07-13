# Brief R1 — Reframe 2 TẦNG: NỀN THƯƠNG HIỆU (bền) → MARKETING (theo mục tiêu)

> **Mục tiêu:** tách rõ 2 tầng chiến lược mà sản phẩm đang **trộn thành 1 pipeline** — đúng cái nhập nhằng
> Brand↔Marketing hay gặp. **Brand = "thương hiệu là ai, muốn được nhớ điều gì" (dài hạn, chốt 1 lần)**;
> **Marketing = "truyền tải gì · qua đâu · làm sao đạt mục tiêu KD" (theo kỳ, đổi liên tục, KẾ THỪA Brand)**.
> Cơ chế sản phẩm **đã đúng** (research → messaging anchor → Layered inherit), chủ yếu **đổi cách nhóm/gọi tên +
> bổ vài field brand bền + tách đo** — KHÔNG đập lại engine.
>
> **Vấn đề hiện tại (đã soi code):**
> - Mảnh **Brand rải khắp:** Định vị chìm trong `strategy` (② Chiến lược) · **Thông điệp (#message) KHÔNG có
>   trong nav** (chỉ vào qua link) · **Brand Voice xếp nhầm ở ③ Sản xuất**.
> - Thiếu artifact Brand **bền**: Position (1 câu) · Promise · Personality (chỉ ẩn trong voice do/don't).
> - Đo (④) **nghiêng hẳn performance** (reach/CTR/ROAS) — thiếu **sức khỏe thương hiệu** (nhận biết/cảm nhận/trung thành).
> - Guardrail bài cảnh báo: đừng nhảy vào content/visual khi chưa chốt "mình là ai" → content thành "áo khoác đẹp".
>
> **Đọc trước:** `docs/cmo/00-PLAN.md` (6 miền CMO) · `web/data.js` (nav) · `web/app.js` `P.message`(~1846,
> Messaging House) · `P.voice`(~2186) · `P.strategy`(~984, synthesis/Định vị) · `_messaging_anchor_from`
> (anchor bơm vào máy viết — chỗ nối Brand→content).
> **Branch:** `claude/pb-wire-brief-b1-3iptbf` · PR về `staging` · KHÔNG tự merge.
> **Thứ tự:** làm R1 **TRƯỚC Auth** (định hình lại IA; Auth không phụ thuộc — làm sau đỡ sửa 2 lần).

---

## 🌏 LUẬT ĐA NGÀNH (bất biến)
1. 2 tầng Brand/Marketing đúng cho **mọi ngành** (B2B/B2C, sản phẩm/dịch vụ). Không hardcode ví dụ ngành.
2. Personality/Promise sinh từ **định vị + insight của chính DN** (Max nháp, user chỉnh) — không áp khuôn.
3. Sức khỏe thương hiệu: chỉ số **directional** (không bịa số) — ngành nào chưa đo được thì để trống + gợi ý cách đo rẻ.

## Nguyên tắc đã chốt
1. **Reframe chứ không đập** — giữ nguyên producer (synthesis/messaging/matrix/calendar/measure); chủ yếu **regroup nav
   + surface #message + kéo Voice về Brand + thêm 3 field brand + tách đo**. Rủi ro thấp.
2. **Brand chốt TRƯỚC Marketing** — cổng: chưa có Định vị+Thông điệp → Marketing (Ma trận/Chiến dịch/Lịch) hiện
   empty-state đẩy về Brand (mở rộng guard B1 sẵn có). "Brand dẫn dắt Marketing, không ngược lại."
3. **1 khái niệm 1 nơi** — Essence/Voice/Tagline/Pillars ĐÃ ở `messaging` (giữ). Field MỚI (positioning/promise/
   personality) → `intake_extra.brand` (không trùng, không đổi schema DB).

---

## Cấu trúc 2 tầng (nav mới)
| Nhóm nav mới | Item | Từ đâu |
|---|---|---|
| **① Chẩn đoán** | Hồ sơ · Thị trường · Đối thủ · Khách hàng · Định giá · SWOT | giữ (research grounding) |
| **② NỀN THƯƠNG HIỆU** ⭐ | **Định vị** (strategy/synthesis) · **Thông điệp** (message — SURFACE) · **Giọng & Tính cách** (voice + personality) | gom mảnh đang rải |
| **③ MARKETING** | **Playbook** (tactical, cách đánh) · **Ma trận & Chiến dịch** (matrix) · **Lịch** (calendar) · Quảng cáo/Inbox/Email | Layered vừa xây |
| **④ Đo & Tối ưu** | **Sức khỏe thương hiệu** (MỚI) · **Hiệu quả Marketing** (overview/ads) · optimizer/spy/schedule/accounts | tách đo |
| **⑤ Hệ thống** | Báo cáo · Quản trị · Cài đặt | giữ |

---

## Phase 1 — Regroup nav + surface Brand (FE-only, 1 commit) — LÕI, rủi ro thấp
**File:** `web/data.js` (nav) + `web/app.js` (empty-state gate).
- `data.js nav`: dựng 5 nhóm trên. **Thêm item `message` ("🏛️ Thông điệp")** vào ② (surface từ ẩn). **Chuyển `voice`**
  từ ③ → ②, đổi nhãn **"Giọng & Tính cách"**. `strategy` đổi nhãn **"Định vị & Chiến lược"** đưa lên đầu ②.
  `tactical` (Playbook) → đầu ③ Marketing. Nhóm ③ đổi tên **"③ MARKETING"**, ② → **"② NỀN THƯƠNG HIỆU"**.
- **Cổng Brand→Marketing:** trong `P.matrix`/`P.calendar` (Marketing), nếu thiếu Định vị+Thông điệp → empty-state
  "Chốt Nền thương hiệu trước → [Tới Thông điệp]" (mở rộng guard `msgHas()` B1). KHÔNG chặn cứng, chỉ dẫn hướng.
- **KHÔNG** đổi route id / producer / api. Chỉ nav + nhãn + empty-state. `node --check` + Playwright smoke.

## Phase 2 — 3 artifact Brand BỀN (BE + FE, 1-2 commit)
**File:** `webapp/business.py` (producer + anchor) · `api.py` · `web/app.js` (Brand page).
- **Hình dữ liệu:** `intake_extra.brand = {positioning, promise, personality: [<3-5 tính cách>]}` (KHÔNG đổi schema DB).
- **Producer `save_brand` + `suggest_brand`** — Max nháp `positioning` (1 câu, từ synthesis) · `promise` (khách kỳ vọng
  gì, từ core+insight) · `personality` (3-5 tính cách, từ voice+định vị). User chỉnh = chốt. Degrade: thiếu synthesis
  → nháp từ profile.
- **Anchor:** mở rộng `_messaging_anchor_from` → bơm thêm `brand.positioning/promise/personality` vào MỌI máy viết
  (calendar_post/derivative/asset) → bài nhất quán tính cách + lời hứa. Tương thích ngược: thiếu `brand` → như cũ.
- **FE:** thêm ô Position/Promise/Personality vào trang **Thông điệp** (Brand tier) — 1 chỗ chốt nền.
- `biz_data`: expose `bizBrand`.

## Phase 3 — Tách ĐO: Sức khỏe thương hiệu vs Hiệu quả Marketing (1 commit)
**File:** `web/app.js` (overview) + (nếu cần) `business.py`.
- **Hiệu quả Marketing** (giữ overview/adsanalytics): reach·CTR·lead·CPA·ROAS·đơn — nhanh, per-campaign.
- **Sức khỏe thương hiệu** (MỚI, nhẹ, directional): nhận biết (mentions/search/follower) · cảm nhận (sentiment/review) ·
  trung thành (mua lại/giới thiệu) · share of voice. Ngành chưa đo được → để trống + gợi ý cách đo rẻ (KHÔNG bịa số).
- Tránh trộn: 2 khối rõ ràng; Brand = chậm/directional, Marketing = nhanh/performance.

---

## 🔌 Phân tích mối nối (seam)
| Khoá | Producer | Khớp? | Degrade |
|---|---|---|---|
| nav groups (P1) | `data.js` | render sidebar | — (chỉ data) |
| `brand.{positioning,promise,personality}` (P2) | `save_brand`/`suggest_brand` | dict, đọc ở anchor + FE | thiếu → anchor bỏ khối brand (không vỡ) |
| anchor brand (P2) | `_messaging_anchor_from` mở rộng | str khớp máy viết | thiếu `brand` → như cũ (tương thích ngược) |
| `bizBrand` (P2 → FE) | `biz_data` | guard dict | {} |
| brand-health metrics (P3) | view (đọc số có thật) | directional | thiếu → để trống + gợi ý đo |
- **Derived-state? KHÔNG** — brand artifacts do user chốt (Max nháp), con người thắng.

## Verify (offline)
```bash
node --check web/data.js && node --check web/app.js
python3 -c "import webapp.business, webapp.api"   # (sandbox thiếu starlette → khai rõ)
python3 tests/test_r1_brand.py                    # P2: save_brand chuẩn hoá + anchor bơm brand + degrade
```
- Playwright: nav 5 nhóm mới · #message + voice ở ② · cổng Brand→Marketing hiện khi thiếu nền · 0 pageerror.
- P2 test: `save_brand` chuẩn hoá personality (list, cắt) · `_messaging_anchor_from` có positioning/promise/personality ·
  thiếu brand → anchor như cũ (test_b1/b3 vẫn PASS).

## Self-review report (commit cuối)
```
[R1] Reframe 2 tầng Brand→Marketing — nav gom + surface Thông điệp/Voice + 3 field brand bền + tách đo
Đã check: nav 5 nhóm · #message+voice ở NỀN THƯƠNG HIỆU · cổng Brand→Marketing · brand.{positioning,promise,personality}
          + anchor bơm vào máy viết (tương thích ngược) · đo tách brand-health/performance · KHÔNG đổi engine/route/schema DB
Chưa chắc (chờ runtime): Max nháp positioning/personality có "ra chất" · brand-health số thật → soi staging
```

## Không làm
- KHÔNG đập engine/producer (synthesis/messaging/matrix/calendar) — chỉ reframe + thêm field/anchor/đo.
- KHÔNG đổi route id / schema DB / schema messaging (Essence/Voice/Tagline/Pillars giữ ở messaging).
- KHÔNG chặn cứng Marketing khi thiếu Brand (chỉ dẫn hướng empty-state).
- KHÔNG bịa số brand-health. KHÔNG hardcode ngành. KHÔNG làm Brand Architecture/Touchpoint-audit (để sau, ngành cần mới bật).
- Mỗi phase 1(-2) commit · push nhánh riêng · PR về `staging` · **dừng chờ review, KHÔNG tự merge.**
