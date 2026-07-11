# BRIEFS cho Cline — cách làm

> **Đọc trước khi làm bất cứ gì:**
> 1. `docs/cmo/00-PLAN.md` — bức tranh + **6 NGUYÊN TẮC THIẾT KẾ**.
> 2. `docs/cmo/WORKFLOW.md` — **Build Loop**: đơn vị việc = **1 function**, vòng Discovery→Plan→Execute→Self-verify→Handoff→Gate.
> 3. `docs/cmo/EVAL.md` — **standard** đánh giá trường/tính năng (3 test · 5 lớp · 3 archetype).
> 4. `docs/cmo/KNOWLEDGE.md` — **standard** bộ não/vault (ontology · frontmatter routing · loader · governance). Đọc khi làm slice **K***.
> 5. `docs/cmo/WIRING.md` — **cổng kiểm mối nối** (seam check): linter `brain/_check.py` (Lớp 1) + sổ hợp đồng khoá xuyên component (Lớp 2). CTO chạy mỗi slice để bắt "consumer không có producer" TRƯỚC runtime.
> **Branch:** đã HỢP NHẤT về 1 cây (D-050) — làm trên nhánh tích hợp hiện hành (`feature/consolidate`, sau merge = `main`). *(Brief cũ ghi `feature/ai-cmo-core` = trước hợp nhất.)*

## Luật mỗi function-task (rút gọn từ WORKFLOW)
1. Đọc ĐÚNG brief của function + **grep tên hàm** (đừng tin số dòng, đừng đọc cả `business.py`). Brief mơ hồ → **HỎI, không đoán**.
2. **KHÔNG đổi schema DB** → dữ liệu mới vào `profile.intake_extra`.
3. **FE 1 nguồn duy nhất:** sửa thẳng `web/app.js` · `styles.css` · `index.html` — KHÔNG còn standalone để mirror (D-047).
4. **Self-verify TRƯỚC khi gọi review** (verify commands dưới) + dán self-review report vào commit.
5. **Cổng mối nối (WIRING.md):** làm mục "Phân tích mối nối" trong brief — mọi khoá đọc/ghi có producer + khớp tên/slug/kiểu; nếu tự suy trạng thái user → luật derived-state. Đụng `brain/` → `py brain/_check.py`.
6. 1 function = 1 commit. Push → auto-review chạy + báo Claude. **Chờ cổng PASS mới sang function sau. KHÔNG tự quyết keep/cut, KHÔNG tự merge.**

```bash
node --check web/app.js
python3 -c "import webapp.business, webapp.api"
```

## Thứ tự slice (chỉ P0 có brief sẵn — phase sau brief sau khi review)
| Slice | File | Function | Xong chưa |
|---|---|---|---|
| **K1** | `K1-vault-skeleton.md` | F1 scaffold · F2 3 framework · F3 2 industry · F4 1 craft · F5 3 stage · F6 base | ✅ xong (F2 CTO vá goal_type) |
| **B** | `B-industry-taxonomy.md` | re-seed family `health-beauty`+`fnb` + khoá `family` (1 commit atomic) | ✅ xong (142fd0a) |
| **K2** | `K2-loader.md` | F1 `webapp/brain.py` loader+parse · F2 `select()` mirror .base + rank | ✅ xong (75be2b9) |
| 0.1 | `P0.1-strategy-spine.md` | F1 save_spine (**+stage A1**) · F2 bizSpine · F3 route · F4 FE+mirror (Spine ở **trang Hồ sơ**) | ✅ xong (07eb89d…f749d04; A1 gộp: `stage` người khai) |
| A2 | (brief sau) | Max **tinh chỉnh** `stage` theo tín hiệu (derived-state: confidence/why/freeze/override) — khi đã có baseline/lịch sử | ⬜ tương lai |
| A3 | (brief sau) | **Hợp nhất intake** — Spine trùng field với profile (`p.stage↔spine.stage`, `target_customer↔audience.who`, `usp↔positioning`). Dọn: spine **pre-fill từ profile** (khuyến nghị) hoặc bỏ field trùng. 1 khái niệm = 1 producer. | ⬜ tương lai |
| 0.2 | `P0.2-spine-wire.md` | F1 `_spine_anchor`+gen_master_plan · F2 gắn campaign_plan/portfolio/calendar_post (calendar_plan skip: không LLM) | ✅ xong (e23b1a0, ab105f7) — *Test 3 empirical cần key thật để chạy* |
| GF | (brief sau) | **#4 Hướng tăng trưởng trọng tâm** — `spine.growth_focus` (enum AARRR/STDC): intake 1 câu + degrade suy từ stage (derived-state). Spec ở `STRATEGY-FRAMEWORK.md`. Bổ nốt 15% khung 6-lựa-chọn. | ⬜ tương lai |
| **D1-F1** | `D1-positioning.md` | `_framework_anchor` nối vault → mục Định vị synthesis (**K3 gộp vào đây**) | ✅ xong (1959edb) — *code bởi Orchestrator, Tester độc lập = R-1* |
| **D1-F2** | `D1-F2-messaging-seam.md` | nối Spine + vault vào `gen_messaging` (định vị→Messaging House) | ⬜ brief xong, **chờ Cline** |
| **INTAKE-USP** | `intake-usp-sharpen.md` | F1 bỏ nhồi-2-ý+giọng buộc tội · F2 thêm alternative→intake_extra.answers · F3 competitor onliness/white-space · F4 usp_stance missing→white-space | ⬜ brief xong, **chờ Cline** |
| **PB-WIRE** | `playbook-artifact-wiring.md` (+ `PB-WIRE-tasks.md` = cắt nhỏ T1–T6/3 PR) | W0 hạ độ cao `_TAC_SYSTEM` (góc đánh, không hook) + emit JSON `playbook_struct` · W1 nối territory/kênh→gen_calendar_post (hook tự viết bám Messaging) · W2 cut+KPI có khoá cho D6 | ⬜ brief CHỐT, **chờ Cline** |
| … | (F5 nháp-xác-nhận UX · D1-F3 QC rubric · D2/D3/D6 lấp card→brief→wire · chốt sau R-1) | | |

> Không chắc chỗ nào → hỏi lại, ĐỪNG bịa. Được tham khảo `marketingskills` repo + `product-journey-4-tang.md` (xem PLAN mục "Tham khảo").
