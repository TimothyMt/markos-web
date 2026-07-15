# Brief R2 — Hợp nhất bề mặt nhập chiến lược (Spine ⊕ Đặt cược)

> **Vấn đề (đã soi code):** tầng chiến lược có **2 thế hệ chồng nhau** → flow "cấn":
> - **Đặt cược** (`bet_choices`, T4-T5) → nuôi **synthesis + playbook**. 5 nhóm: market · segment · positioning · price · channel.
> - **Spine** (`intake_extra.spine`, P0.1) → nuôi **`_spine_anchor`** (máy viết bài). 6 nhóm: stage · growth_focus · objective · audience · positioning(+price_posture) · constraint.
> - **Trùng 4 thứ hỏi 2 lần:** tệp (segment↔audience) · định vị (positioning↔positioning) · giá (price↔price_posture) · hướng-ưu-tiên (growth_focus ↔ gate posture brand/balanced/activation).
> - Trên trang ② "Định vị & Chiến lược" giờ chồng **Spine + Đặt cược + Synthesis** → "định vị" hiện 3 lần, thứ tự nhập mơ hồ.
>
> **Nguyên tắc:** REFRAME không đập engine. Gộp **UI nhập-1-lần**; lưu **fan-out ghi cả 2 store** (dedupe ô chung) →
> downstream (synthesis đọc `bet_choices` @3336, playbook @4622/4922, anchor đọc `spine` @3185) **KHÔNG đổi** → tương thích ngược.
>
> **Đọc trước:** `web/app.js` `P.strategy`(~1024, có Spine collapsible + betForm + synthesis) · `betForm()` · `spineBand()` ·
> `save_bet_choices`(~1903) · `save_spine`(~470) · `_spine_anchor`(~3180) · `BET_CATEGORIES`(~1798).
> **Branch:** `claude/pb-wire-brief-b1-3iptbf` · PR về `staging` · KHÔNG tự merge.

---

## 🌏 LUẬT ĐA NGÀNH (bất biến)
- 8 quyết định chiến lược đúng cho mọi ngành; Max gợi ý từ research của CHÍNH DN, không áp khuôn.
- Con người chốt (Max nháp). KHÔNG derived-state persist máy đoán.

## Bản đồ hợp nhất (dedupe)
| Ô nhập (1 lần) | Ghi vào `bet_choices` | Ghi vào `spine` | Ghi chú |
|---|---|---|---|
| Khoảng trống thị trường | `market` | — | chỉ Bet |
| Tệp khách (wedge) | `segment` | `audience.who` | **gộp** |
| Góc định vị | `positioning` | `positioning.statement` | **gộp** |
| Phân khúc giá-trị | `price` | `positioning.price_posture` (map enum) | **gộp** |
| Kênh chính | `channel` | — | chỉ Bet |
| Mục tiêu (SMART) | — | `objective` | chỉ Spine |
| Hướng tăng trưởng | (map → gate posture) | `growth_focus` | **gộp** — 1 câu hỏi |
| Giai đoạn | — | `stage` | chỉ Spine |
| Năng lực (người/ngân sách/nhịp) | — | `constraint` | chỉ Spine |

- **price → price_posture map:** "cao cấp"→premium · "ngang tầm/tầm trung"→parity · "giá tốt/rẻ"→value (khớp lỏng).
- **growth_focus → gate posture map:** acquisition→brand(xây nhận biết) · conversion→activation(ra đơn) · retention/referral→balanced (hoặc giữ posture riêng). Chốt map lúc build.

## Target flow (② Định vị & Chiến lược)
```
Research T1-T3 xong
  → 1 bề mặt "Chiến lược" (8 quyết định, Max gợi ý + người chốt) — nhập 1 LẦN
  → 💾 Lưu (fan-out → bet_choices + spine)
  → 🎯 Max lập Synthesis (đọc bet_choices như cũ)
  → chốt Synthesis
  → xuôi: Thông điệp · Playbook · Ma trận · Lịch (anchor đọc spine như cũ)
```
Bỏ: Spine collapsible RỜI + betForm RỜI → **1 form**. Synthesis giữ là OUTPUT bên dưới.

## Phases
- **P1 — Gộp UI + fan-out 2 store (LÕI, rủi ro thấp).** FE: 1 form thay Spine+Bet; producer `save_strategy_input`
  (hoặc mở rộng save hiện có) ghi cả `bet_choices` + `spine` từ 1 payload, dedupe. Downstream KHÔNG đụng.
  Verify: synthesis vẫn đọc bet_choices, anchor vẫn đọc spine (test cũ b1/b5 PASS).
- **P2 — (tuỳ chọn, sau) dọn 1 nguồn thật.** Rewire synthesis/playbook + anchor cùng đọc 1 store hợp nhất, bỏ
  fan-out. Bigger — chỉ làm khi P1 chạy ổn + có nhu cầu. KHÔNG làm chung P1.

## 🔌 Seam
| Khoá | Producer | Consumer | Degrade |
|---|---|---|---|
| form hợp nhất | `save_strategy_input` (fan-out) | ghi `bet_choices` + `spine` | thiếu ô → store đó rỗng phần đó |
| `bet_choices` | (như cũ, nay từ form gộp) | synthesis@3336 · playbook@4622/4922 | như cũ |
| `spine` | (như cũ, nay từ form gộp) | `_spine_anchor`@3185 | như cũ |
- **Không derived-state** — người chốt. Fan-out chỉ là ghi 1→2, không suy đoán.

## Verify (offline)
```bash
python3 -c "import webapp.business, webapp.api"   # (sandbox thiếu starlette → khai rõ)
python3 tests/test_r2_unify_strategy.py           # save_strategy_input fan-out đúng 2 store + dedupe + map enum
node --check web/app.js
```
- test cũ b1/b3/b5 vẫn PASS (downstream không đổi). Playwright: ② chỉ còn 1 form chiến lược, không còn Spine+Bet rời.

## Không làm
- KHÔNG đập synthesis/playbook/anchor (P1 chỉ đổi INPUT, downstream đọc y như cũ).
- KHÔNG đổi schema DB. KHÔNG bỏ store nào ở P1 (fan-out giữ cả 2). KHÔNG derived-state. KHÔNG hardcode ngành.
- P2 (dọn 1 nguồn) KHÔNG gộp vào P1.
