# Slice B — Re-seed taxonomy ngành (family) cho vault brain/

> **Mục tiêu:** đưa 2 note industry placeholder của K1 (`d2c-skincare`/`service-local` — slug tôi bịa) về **taxonomy family THẬT** (`health-beauty`, `fnb` — trùng key `industry_context` sẵn có), thêm khoá `family`, để recall đọc thẳng field `industry` cũ được. CHƯA làm slug tinh (đó là derived-state, seed sau).
> **Đọc trước:** `docs/cmo/KNOWLEDGE.md` mục "Taxonomy ngành 2 tầng + degrade" + schema `industry` → `docs/cmo/WIRING.md` (Hiến pháp + Sổ hợp đồng).
> **Branch/worktree:** `feature/ai-cmo-core` tại `D:/MarkOS/wt-cmo`.

## Luật sống còn của slice này
1. **1 slice = 1 commit ATOMIC.** Đổi tên industry làm đứt link craft + `.base`; phải sửa HẾT rồi mới `py brain/_check.py` rồi commit (không commit giữa chừng khi linter còn đỏ).
2. **Chỉ đụng `brain/`.** KHÔNG đụng `webapp/`, `web/`, DB, `industry_context.py`.
3. Frontmatter THẬT + đúng schema; thân note = placeholder (không nội dung marketing).
4. `family` của note tầng-family = chính `slug` của nó.

## Phân tích mối nối (theo WIRING Hiến pháp)
- Khoá GHI: `industry.slug` = `health-beauty`/`fnb` (kebab) · `industry.family` = self. Kiểu: string kebab.
- Khoá ĐỌC (bởi recall K3 sau): `industry` — producer = profile field cũ (14 key snake) qua `.replace("_","-")`. → slug note PHẢI khớp key sau chuẩn hoá: `health_beauty→health-beauty`, `fnb→fnb`. ✅
- Derived-state? **Không** ở slice này (family do user khai, không suy). Slug tinh (derived) để sau.
- Degrade: recall không có note tinh → dùng note family này. Slice B chỉ tạo tầng family.
- Addendum: kiểm chéo `fit_frameworks`/`expresses` vẫn trỏ framework có thật sau khi đổi tên industry.

## Việc — làm HẾT rồi mới verify + commit (atomic)

### 1) Thay 2 note industry
**Xoá** `brain/industries/d2c-skincare.md` và `brain/industries/service-local.md`.
**Tạo** `brain/industries/health-beauty.md`:
```markdown
---
type: industry
title: "Sức khỏe & Làm đẹp"
status: draft
maturity: fresh
updated: 2026-07-04
source: ""
slug: health-beauty
family: health-beauty
channels: [tiktok, tiktok-shop, fb, instagram]
fit_frameworks: ["[[stp]]", "[[jtbd]]", "[[dunford-positioning]]"]
pitfalls: []
---

> [!note] Nội dung do vòng tri thức lấp (status: draft — chờ research, có nguồn+ngày)

## Hành vi mua
## Kênh trội
## Pitfall thường gặp
```
**Tạo** `brain/industries/fnb.md`:
```markdown
---
type: industry
title: "F&B (Ăn uống)"
status: draft
maturity: fresh
updated: 2026-07-04
source: ""
slug: fnb
family: fnb
channels: [fb, tiktok, google-maps, shopeefood]
fit_frameworks: ["[[stp]]", "[[jtbd]]"]
pitfalls: []
---

> [!note] Nội dung do vòng tri thức lấp (status: draft — chờ research, có nguồn+ngày)

## Hành vi mua
## Kênh trội
## Pitfall thường gặp
```

### 2) Đổi craft card theo ngành mới
**Xoá** `brain/craft/tiktok-hook__d2c-skincare.md`.
**Tạo** `brain/craft/tiktok-hook__health-beauty.md`:
```markdown
---
type: craft
title: "TikTok Hook — Sức khỏe & Làm đẹp"
status: draft
maturity: fresh
updated: 2026-07-04
source: ""
output: hook
channel: tiktok
industry: health-beauty
expresses: "[[jtbd]]"
exemplars: []
---

> [!note] Nội dung do vòng tri thức lấp (status: draft — chờ research, có nguồn+ngày)

## Khi nào dùng
## Công thức
## Exemplars
<!-- chờ research: mỗi exemplar cần nguồn + ngày, KHÔNG bịa -->
```

### 3) Sửa view `.base`
Trong `brain/_bases/framework-selector.base`, view thứ 2: đổi `name` và filter `d2c-skincare` → `health-beauty`:
- `name: Route - health-beauty x launch`
- filter: `'applies_to.containsAny("health-beauty", "all")'` (giữ nguyên dòng `stage.contains("launch")`).
Không đổi gì khác trong file.

## Self-verify + commit (atomic)
- Chạy `py brain/_check.py` → PHẢI `OK` (mọi synapse thông; nếu đỏ = còn sót link cũ, sửa cho xanh mới commit).
- Kiểm: không còn file/slug `d2c-skincare`/`service-local` nào trong `brain/` (kể cả trong `.base`).
- Commit (1 commit atomic): `feat(brain): B re-seed taxonomy family (health-beauty + fnb) + family key`.
- Dán self-review + kết quả `brain/_check.py` vào commit body ("Chưa chắc / làm tắt / giả định").
- Push `feature/ai-cmo-core` rồi **dừng chờ review**.

**Circuit-breaker:** 2 lần không xong 1 bước → DỪNG, báo. **Windows/PowerShell:** đường dẫn dấu `\`; ghi file bằng Write; xoá bằng `Remove-Item` (không `-Force` lên file đang mở).

## Không làm
- KHÔNG tạo slug tinh (`d2c-skincare`…) — đó là derived-state, seed sau. KHÔNG đụng `industry_context.py`, `webapp/`, DB. KHÔNG promote `status: live`.
