# Slice K1 — Vault skeleton + seed placeholder + 1 Base

> **Mục tiêu:** dựng bộ khung "bộ não" + đủ note mẫu để chứng minh **dây thần kinh truy hồi bắn đúng** (1 `.base` lọc framework theo ngành×stage). CHƯA có code Python (đó là K2). CHƯA có nội dung marketing thật.
> **Đọc trước:** `docs/cmo/KNOWLEDGE.md` (giải phẫu — schema frontmatter, ontology, folder) → `docs/cmo/WORKFLOW.md` (đơn vị = 1 function, self-verify) → `docs/cmo/00-PLAN.md`.
> **Branch:** `feature/ai-cmo-core` (worktree `D:/MarkOS/wt-cmo`).

## Luật sống còn của slice này
1. **Cline xây DÂY THẦN KINH, KHÔNG xây kiến thức.** Frontmatter (khoá routing) phải THẬT + đúng schema; **thân note = placeholder** (vd `> [!note] Nội dung do vòng tri thức lấp (status: draft)`). KHÔNG tự chế nội dung marketing (STP là gì, hook hay ra sao) — đó là việc research gated sau.
2. **Slug kebab-case, khớp chéo** giữa `applies_to`/`industry`/`slug`. Sai slug = synapse đứt.
3. Mọi seed note `status: draft` (chưa `live`). Framework `maturity: evergreen`; craft exemplar để trống + ghi `(chờ research, có nguồn+ngày)`.
4. KHÔNG đụng `webapp/`, `web/`, DB. Slice này chỉ tạo file trong `brain/`.

## Khuôn frontmatter (CHÉP, đổi giá trị — đừng tự suy từ schema)
```yaml
# framework (F2)
---
type: framework
title: "STP"
status: draft
maturity: evergreen
updated: 2026-07-04
source: ""
applies_to: [all]                 # hoặc [d2c-skincare, service-local]
stage: [launch, growth, scale]
goal_type: [positioning, content] # tập con của: positioning|pricing|channel|content|lifecycle|measurement
composes_with: []                 # vd ["[[jtbd]]"]
---
```
```yaml
# industry (F3)
---
type: industry
title: "D2C Skincare"
status: draft
maturity: fresh
updated: 2026-07-04
source: ""
slug: d2c-skincare               # khớp tên file
channels: [tiktok-shop, tiktok, fb, shopee]
fit_frameworks: ["[[stp]]", "[[jtbd]]"]
pitfalls: []
---
```
```yaml
# craft (F4)
---
type: craft
title: "TikTok Hook — D2C Skincare"
status: draft
maturity: fresh
updated: 2026-07-04
source: ""
output: hook
channel: tiktok
industry: d2c-skincare
expresses: "[[jtbd]]"
exemplars: []                    # chờ research: mỗi exemplar cần nguồn+ngày
---
```
```yaml
# stage (F5)
---
type: stage
title: "Launch"
status: draft
maturity: evergreen
updated: 2026-07-04
source: ""
slug: launch                     # khớp tên file + khớp giá trị stage: trong framework
priorities: []
signals: []
---
```
Thân note = placeholder (vd `> [!note] Nội dung do vòng tri thức lấp (status: draft)`).

## Chẻ theo FUNCTION (mỗi F = 1 commit = 1 review)
> **Pre-flight:** F1 (scaffold) đóng luôn vai smoke-test tool-call cho model executor. Nếu 2 lần không hoàn tất nổi 1 bước → **DỪNG, báo, đừng lặp.**

### F1 — scaffold `brain/` + README convention
- Tạo cây thư mục: `brain/frameworks/ industries/ craft/ stages/ _bases/ _canvas/` (mỗi thư mục rỗng thêm `.gitkeep`).
- `brain/README.md`: tóm tắt convention từ `KNOWLEDGE.md` — 4 loại note, quy ước slug kebab-case, `status/maturity/updated`, `[[link]]` nghĩa gì, "Obsidian = authoring, Max đọc file lúc runtime". Ngắn gọn (≤40 dòng).
- Commit: `feat(brain): K1 F1 scaffold vault brain/ + README convention`.

### F2 — 3 framework note (placeholder, frontmatter đúng schema)
- `brain/frameworks/stp.md`, `dunford-positioning.md`, `jtbd.md`.
- Frontmatter đủ khoá `framework` theo KNOWLEDGE.md: `type/title/status:draft/maturity:evergreen/updated/source` + `applies_to/stage/goal_type/composes_with`.
  - vd `stp.md`: `goal_type: [positioning, content]`, `applies_to: [all]`, `stage: [launch, growth, scale]`.
  - `dunford-positioning.md`: `goal_type: [positioning]`, `composes_with: ["[[jtbd]]"]`.
  - `jtbd.md`: `goal_type: [positioning, product-mkt]`.
- Thân = placeholder (mục `## Khi nào dùng / ## Cách áp / ## Ví dụ` để trống có ghi chú chờ research).
- Commit: `feat(brain): K1 F2 seed 3 framework placeholder`.

### F3 — 2 industry note + synapse `[[link]]`
- `brain/industries/d2c-skincare.md`, `service-local.md`.
- Frontmatter `industry`: `slug` (khớp tên file) · `channels` (vd `[tiktok-shop, tiktok, fb, shopee]` / `[fb, zalo, google-maps]`) · `fit_frameworks: ["[[stp]]", "[[jtbd]]"]` · `pitfalls`.
- Kiểm: slug trong `fit_frameworks` khớp tên file framework F2. Backlink phải hiện (framework ← industry).
- Commit: `feat(brain): K1 F3 seed 2 industry + link frameworks`.

### F4 — 1 craft card (placeholder, exemplar rỗng có nguồn-slot)
- `brain/craft/tiktok-hook__d2c-skincare.md`.
- Frontmatter `craft`: `output: hook` · `channel: tiktok` · `industry: d2c-skincare` · `expresses: "[[jtbd]]"` · `exemplars: []` (ghi chú "chờ research: mỗi exemplar cần nguồn+ngày").
- Commit: `feat(brain): K1 F4 seed 1 craft card placeholder`.

### F5 — 3 stage note (routing theo "thời điểm")
- `brain/stages/launch.md`, `growth.md`, `scale.md`.
- Frontmatter `stage` theo KNOWLEDGE.md: `type: stage · title · status: draft · updated` + `slug` (khớp tên file) · `priorities: [...]` · `signals: [...]` (cách nhận biết business đang ở stage này).
- Thân = placeholder (chờ research lấp). `priorities/signals` để **vài mục gợi ý cấu trúc**, KHÔNG chế sâu.
- Kiểm: slug stage (`launch/growth/scale`) khớp giá trị `stage:` trong frontmatter 3 framework F2 → synapse routing-theo-stage thông.
- Commit: `feat(brain): K1 F5 seed 3 stage (launch/growth/scale)`.

### F6 — 1 Base: framework-selector (vỏ não truy hồi, xem được trong Obsidian)
- `brain/_bases/framework-selector.base` (YAML hợp lệ theo skill obsidian-bases).
- **View 1 "all frameworks":** filter `type == "framework"` — table hiện `title · goal_type · applies_to · stage · updated`.
- **View 2 "route: d2c-skincare × launch"** (chứng minh routing 2 khoá): filter thêm
  `(applies_to.containsAny("d2c-skincare") || applies_to.contains("all"))` **AND** `stage.contains("launch")`
  → ra đúng subset framework "cháy" cho ngành×thời-điểm đó.
- Self-verify: mở trong Obsidian, `.base` render không lỗi YAML; View 1 ra đủ 3 framework, View 2 ra đúng subset. Dán mô tả kết quả (hoặc screenshot) vào commit.
- Commit: `feat(brain): K1 F6 base framework-selector (recall cortex, route ngành×stage)`.

## Self-verify (mỗi F, dán report vào commit)
- Frontmatter parse được (YAML hợp lệ) · slug khớp chéo · `.base` không lỗi.
- Không có nội dung marketing tự chế (chỉ placeholder).
- Khai phần "Chưa chắc / làm tắt / giả định".

## Không làm ở slice này
- KHÔNG loader Python (K2). KHÔNG wire vào Max (K3). KHÔNG viết nội dung framework/craft thật (research gated). KHÔNG promote `status: live`.

## Xong khi
F1–F6 PASS cổng review. Reviewer: **CTO** (schema/slug/`.base` YAML) + **Tester** (mở Obsidian, `.base` lọc đúng cả 2 view). CMO-persona KHÔNG nổ (chưa có bề mặt marketing).
