# BRIEFS cho Cline — cách làm

> **Đọc trước khi làm bất cứ gì:**
> 1. `docs/cmo/00-PLAN.md` — bức tranh + **6 NGUYÊN TẮC THIẾT KẾ**.
> 2. `docs/cmo/WORKFLOW.md` — **Build Loop**: đơn vị việc = **1 function**, vòng Discovery→Plan→Execute→Self-verify→Handoff→Gate.
> 3. `docs/cmo/EVAL.md` — **standard** đánh giá trường/tính năng (3 test · 5 lớp · 3 archetype).
> 4. `docs/cmo/KNOWLEDGE.md` — **standard** bộ não/vault (ontology · frontmatter routing · loader · governance). Đọc khi làm slice **K***.
> 5. `docs/cmo/WIRING.md` — **cổng kiểm mối nối** (seam check): linter `brain/_check.py` (Lớp 1) + sổ hợp đồng khoá xuyên component (Lớp 2). CTO chạy mỗi slice để bắt "consumer không có producer" TRƯỚC runtime.
> **Branch:** `feature/ai-cmo-core` (worktree `D:/MarkOS/wt-cmo`).

## Luật mỗi function-task (rút gọn từ WORKFLOW)
1. Đọc ĐÚNG brief của function + **grep tên hàm** (đừng tin số dòng, đừng đọc cả `business.py`). Brief mơ hồ → **HỎI, không đoán**.
2. **KHÔNG đổi schema DB** → dữ liệu mới vào `profile.intake_extra`.
3. **MIRROR FE cùng 1 commit:** `web/app.js` ↔ `<script>` standalone; `web/styles.css` ↔ `<style>` standalone.
4. **Self-verify TRƯỚC khi gọi review** (verify commands dưới) + dán self-review report vào commit.
5. **Cổng mối nối (WIRING.md):** làm mục "Phân tích mối nối" trong brief — mọi khoá đọc/ghi có producer + khớp tên/slug/kiểu; nếu tự suy trạng thái user → luật derived-state. Đụng `brain/` → `py brain/_check.py`.
6. 1 function = 1 commit. Push → auto-review chạy + báo Claude. **Chờ cổng PASS mới sang function sau. KHÔNG tự quyết keep/cut, KHÔNG tự merge.**

```bash
node --check web/app.js
python3 -c "import re;h=open('web/dashboard-standalone.html').read();open('/tmp/s.js','w').write(max(re.findall(r'<script[^>]*>(.*?)</script>',h,re.S),key=len))" && node --check /tmp/s.js
python3 -c "import webapp.business, webapp.api"
```

## Thứ tự slice (chỉ P0 có brief sẵn — phase sau brief sau khi review)
| Slice | File | Function | Xong chưa |
|---|---|---|---|
| **K1** | `K1-vault-skeleton.md` | F1 scaffold · F2 3 framework · F3 2 industry · F4 1 craft · F5 3 stage · F6 base | ✅ xong (F2 CTO vá goal_type) |
| **B** | `B-industry-taxonomy.md` | re-seed family `health-beauty`+`fnb` + khoá `family` (1 commit atomic) | ⬜ |
| 0.1 | `P0.1-strategy-spine.md` | F1 save_spine · F2 bizSpine · F3 route · F4 FE+mirror | ⬜ (chưa build — brief đã vá) |
| A1 | (brief sau) | thêm `stage` vào Spine (hỏi 1 câu / suy baseline) | ⬜ |
| 0.2 | `P0.2-spine-wire.md` | helper `_spine_anchor` + gắn từng hàm gen | ⬜ |
| … | (K2 loader · K3 wire select() · P1+ brief sau khi review) | | |

> Không chắc chỗ nào → hỏi lại, ĐỪNG bịa. Được tham khảo `marketingskills` repo + `product-journey-4-tang.md` (xem PLAN mục "Tham khảo").
