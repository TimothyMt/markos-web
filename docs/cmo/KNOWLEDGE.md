# KNOWLEDGE.md — Giải phẫu bộ não (second brain của Max)

> Đây là **standard** cho kho tri thức. Cline xây theo file này; Orchestrator + Human gate. Substrate = **Obsidian-flavored vault** (markdown + frontmatter + `[[link]]` + `.base`), sống trong repo tại `brain/`, KHÔNG bảng DB.
> Vì sao kho này = moat: xem `00-PLAN.md` (3 đầu: thước · nhiên liệu gen · bản thiết kế) + `WORKFLOW.md` (vòng tri thức đi trước build 1 nhịp).

## Nguyên tắc nền
1. **Vault = source of truth di động.** Markdown thuần + frontmatter. Portable, git-friendly, LLM đọc được, người soạn được (Obsidian).
2. **Obsidian = buồng lái AUTHORING, KHÔNG phải engine RUNTIME.** Build-time: bạn/tôi/Cline dùng Obsidian GUI/CLI/Bases/Canvas để xây + soi. Runtime: Max đọc **chính đám file** bằng loader Python nhẹ (mirror filter Bases). Một nguồn (frontmatter), hai mặt tiêu thụ. → `obsidian-cli` (cần GUI chạy) chỉ dùng build-time.
3. **Cline xây DÂY THẦN KINH, không xây kiến thức.** Cline làm structure + frontmatter hợp lệ + `.base` + loader. **Nội dung marketing (thân note) do VÒNG TRI THỨC lấp** (research → gate). Slice skeleton dùng thân **placeholder**.
4. **Freshness + governance là công dân hạng nhất.** Mọi note có `updated` + `status`; chỉ `status: live` mới phục vụ user.

## Bản đồ thần kinh (5 skill obsidian → bộ phận)
| Bộ phận | Cơ chế | Skill |
|---|---|---|
| Nơ-ron + thụ thể | note + **frontmatter** (khoá routing) | obsidian-markdown |
| Synapse | `[[link]]` + backlinks | obsidian-markdown |
| Vỏ não truy hồi | `.base` filter (build-time) ↔ loader Python (runtime) | obsidian-bases |
| Nhận thức không gian | `.canvas` (bản đồ chiến lược) | json-canvas |
| Cảm giác (nạp ngoài vào) | defuddle bóc web → note sạch | defuddle |

## Ontology — 4 loại note (v1), sống ở `brain/`
```
brain/
  frameworks/   # lens phân tích/chiến lược (STP, JTBD, Dunford, AARRR, Bullseye, 4P, category…)
  industries/   # 15 hồ sơ ngành: hành vi mua VN · kênh trội · phễu · pitfall · framework hợp
  craft/        # craft card (output×kênh×ngành) cho chất lượng THỰC THI (3 đầu)
  stages/       # giai đoạn business + cái gì quan trọng + dấu hiệu nhận biết
  _bases/       # file .base — buồng lái query (con người xem)
  _canvas/      # bản đồ .canvas (tuỳ chọn)
  README.md     # convention vault (điền ở K1)
```
Mở rộng sau (KHÔNG làm v1): `plays/` (playbook đã hợp thành).

## Schema frontmatter — KHOÁ ROUTING (bắt buộc đúng, đây là "thụ thể")
**Chung mọi note:**
```yaml
type:     framework | industry | craft | stage   # phân loại
title:    "..."
status:   draft | reviewed | live                 # governance — chỉ 'live' ra user
maturity: evergreen | fresh | decaying            # freshness
updated:  2026-07-03                              # ngày cập nhật (decay)
source:   "url/ghi chú nguồn"                     # provenance (chống bịa)
```
**framework** (thêm):
```yaml
applies_to: [d2c-skincare, service-local, ...]   # slug ngành, hoặc [all]
stage:      [launch, growth, scale]              # giai đoạn hợp
goal_type:  [positioning, pricing, channel, content, lifecycle, measurement]  # ↔ D1–D6
composes_with: ["[[JTBD]]", "[[STP]]"]           # framework hay dùng chung
```
**industry** (thêm): `slug` · `channels: [tiktok-shop, zalo, fb, ...]` · `fit_frameworks: ["[[STP]]"]` · `pitfalls: [...]`
**craft** (thêm): `output` (hook|post|email|caption…) · `channel` (tiktok|fb|…) · `industry` (slug|[all]) · `expresses: "[[framework]]"` · `exemplars` (mỗi cái có **nguồn+ngày**)
**stage** (thêm): `slug` · `priorities: [...]` · `signals: [...]` (cách nhận biết business đang ở stage này)

> Slug quy ước: kebab-case, khớp giữa `applies_to`/`industry`/`slug` (vd `d2c-skincare`). Sai slug = synapse đứt → routing trượt.

## Synapse — nghĩa của `[[link]]`
- framework `[[link]]` ngành nó hợp; craft `[[link]]` framework nó biểu đạt + ngành; industry `[[link]]` framework fit.
- **Backlink = duyệt ngược** (loader + Bases đọc `file.backlinks`): từ 1 ngành thấy mọi framework/craft trỏ vào nó.

## Vỏ não truy hồi — routing (dây thần kinh cốt lõi)
Input từ **Spine**: `(industry, stage, goal_type)`. Output: nhúm note "cháy" → LLM hợp thành phân tích.
- **Build-time (buồng lái):** `.base` trong `_bases/` cho con người thấy bảng "framework nào cháy cho ngành×stage".
- **Runtime (Max):** loader `webapp/brain.py` mirror **cùng logic filter**:
```
select(industry, stage, goal_type) -> [note]:
  lọc type==framework
  AND (applies_to chứa industry OR applies_to chứa "all")
  AND stage chứa stage
  AND goal_type chứa goal_type
  AND status == "live"
  → xếp hạng (maturity/updated) → trả
```
Loader = parse frontmatter (yaml) + filter thuần Python, **không DB**, cache/lazy-load. `.base` và loader phải cho **cùng kết quả** (test đối chiếu).

## Governance + freshness (đầu③ gated)
- `status`: research tạo `draft` → Orchestrator+Human review → `reviewed` → chốt `live`. **Chỉ `live` ra user.**
- `maturity`+`updated`: `fresh`/`decaying` (exemplar trend) có hạn → lịch re-research; `evergreen` (framework kinh điển) bền.
- Keep/cut / promote `live` = **cổng Human + Orchestrator**, KHÔNG phải Cline, KHÔNG auto.

## Cách xây (depth-first, không boil-ocean)
Seed nhỏ chứng minh dây thần kinh bắn đúng TRƯỚC, rồi vòng tri thức fan-out từng ngành:
- **K1** vault skeleton + seed **placeholder** (3 framework · 2 ngành · 1 craft · 3 stage) + 1 `.base` route ngành×stage. (Cline — structure, KHÔNG nội dung marketing)
- **K2** loader runtime `webapp/brain.py` mirror `.base` + test đối chiếu.
- **K3** wire `select()` vào business.py (điểm dùng đầu tiên).
- Sau đó: vòng tri thức lấp nội dung `draft→live` từng ngành (gated).

## Ràng buộc kế thừa (CLAUDE.md)
Không đổi schema DB · không bịa số (exemplar phải có nguồn) · loader import lazy trong hàm như phần còn lại của `business.py`.
