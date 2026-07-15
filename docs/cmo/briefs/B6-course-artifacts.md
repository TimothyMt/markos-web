# Brief B6 — 3 artifact lấy từ khoá (Run by Linh) vào Max

> **Bối cảnh:** soi 5 bước khoá marketing (research → phễu 7 tầng → campaign brief → content strategy → calendar).
> Max **đã hơn ở khâu thực thi** (sinh content thật, Layered matrix, brand-health). Khoá hơn Max đúng **3 artifact
> tầng lập kế hoạch** → lấy về. **KHÔNG đập engine** — chỉ thêm field vào hợp đồng dữ liệu sẵn có (`intake_extra`).
>
> **Branch:** `claude/pb-wire-brief-b1-3iptbf` · PR về `staging` · KHÔNG tự merge (trừ khi user cho phép).

## 🌏 LUẬT ĐA NGÀNH (bất biến)
- Risk/Offer/Mix sinh từ **chính dữ liệu DN** (Max nháp, user chỉnh) — KHÔNG hardcode ví dụ ngành.
- KHÔNG bịa số. Mix % là **phân bổ tỉ trọng**, không phải cam kết KPI.

## Nguyên tắc
1. **Additive, degrade-safe, tương thích ngược** — thiếu field mới → FE ẩn khối, anchor như cũ, test cũ vẫn PASS.
2. **Producer sinh (Max nháp) + human override** (save nhận field) — con người thắng. KHÔNG derived-state (user chốt).
3. Mỗi artifact = **1 commit + 1 test**. Thứ tự: A (🔴 Risk) → B (Offer) → C (Mix).

---

## Artifact A — Risk & Contingency (🔴 giá trị cao nhất)
Khoá "Bước 5": brief chiến dịch có bảng **rủi ro · xác suất · impact · backup plan**. Max **chưa có**.

| Khoá | Producer | Consumer | Degrade |
|---|---|---|---|
| `key_idea.risks = [{risk, likelihood, impact, backup}]` | `gen_funnel_map_for_idea` emit `risks` (Max nháp) + `save_key_idea(risks=…)` (human sửa) | FE thẻ đợt: bảng ⚠️ Rủi ro & dự phòng | thiếu → ẩn khối |

- `likelihood`/`impact` enum `thấp|trung bình|cao` (rác → ''). `risk`/`backup` str cắt độ dài. Cap 6 rủi ro.
- KHÔNG bơm anchor (là artifact tầng kế hoạch, không cần vào từng bài).

## Artifact B — Offer theo tầng
Khoá "Bước 5": **Offer & Funnel** rõ offer/hook cho TOFU/MOFU/BOFU. Max chỉ có `angle`/`offer_lever` chung (mỏng).

| Khoá | Producer | Consumer | Degrade |
|---|---|---|---|
| `key_idea.funnel_map.offers = {tofu, mofu, bofu}` | `gen_funnel_map_for_idea` emit `offers` | FE funnel: offer/tầng · **anchor** `gen_calendar_post` camp bơm `offers[tier]` | thiếu → như cũ |

- Mỗi offer str ngắn. Anchor: post đợt tầng X mang offer tầng X → câu chữ bám đúng chào mời.

## Artifact C — % tỉ trọng pillar (content mix)
Khoá "Bước 6": **phân bổ % theo pillar** (P1 30%···P5 10%, tổng 100). Max có *nhịp/ô* nhưng chưa có mix pillar-level.

| Khoá | Producer | Consumer | Degrade |
|---|---|---|---|
| `content_matrix.mix = [{pillar, pct}]` (chuẩn hoá tổng ~100) | `gen_content_matrix` emit `mix` | FE tab Ma trận nền: thanh mix % | thiếu → ẩn |

- Validate: pct int ≥0; chuẩn hoá về tổng 100 (chia đều nếu lệch). pillar phải khớp danh sách trụ.

---

## Verify (offline — sandbox thiếu LLM key)
```bash
python3 -m py_compile webapp/business.py && node --check web/app.js web/data.js
python3 tests/test_b6_course_artifacts.py   # save nhận field · parse emit · validate/degrade · anchor offer
```
- Stub router (như test_b4/b5): drive save_key_idea(risks/…) · assert normalize · assert system prompt gen có schema mới ·
  `gen_calendar_post` camp có offer trong prompt. Test cũ (b1-b5) vẫn PASS (tương thích ngược).

## Không làm
- KHÔNG đập engine gen (chỉ thêm field output + parse). KHÔNG đổi schema DB. KHÔNG derived-state.
- KHÔNG tắt Spine (chờ brief gộp Spine↔Đặt cược riêng). KHÔNG bịa số. KHÔNG hardcode ngành.
- Phễu 7 tầng (Bước 3) **BỎ** — Max 3 tầng TOFU/MOFU/BOFU đã đủ cho SME.
