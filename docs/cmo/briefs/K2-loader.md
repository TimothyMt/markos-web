# Slice K2 — Loader runtime `webapp/brain.py` (mirror `.base`)

> **Mục tiêu:** Max **đọc + lọc** được vault brain/ bằng Python thuần (không DB), cho **cùng kết quả** với `.base`. Đây là engine truy hồi runtime. CHƯA wire vào business.py (đó là K3).
> **Đọc trước:** `docs/cmo/KNOWLEDGE.md` mục "Vỏ não truy hồi" + "Taxonomy ngành 2 tầng + degrade" → `docs/cmo/WIRING.md` (Hiến pháp) → `brain/_check.py` (tham khảo parser frontmatter tối giản).
> **Branch/worktree:** `feature/ai-cmo-core` tại `D:/MarkOS/wt-cmo`.

## Luật sống còn
1. **KHÔNG phụ thuộc pyyaml** (không có trong requirements). Viết parser frontmatter tối giản như `brain/_check.py` (scalar + list phẳng). KHÔNG thêm dependency.
2. **KHÔNG DB, KHÔNG đổi schema.** Chỉ đọc file `brain/`. KHÔNG đụng `web/`, intake, `business.py` (K3 mới wire).
3. **Không bịa nội dung** — loader chỉ đọc, không sinh.
4. `.base` và loader phải cho **cùng kết quả** trên seed hiện tại (test đối chiếu, F2).

## Phân tích mối nối (theo WIRING Hiến pháp)
- Khoá ĐỌC: frontmatter note trong `brain/` — producer: K1/B (tồn tại ✅). `industry` (input hàm) — producer thật là profile field (K3 sẽ truyền, chuẩn hoá snake→kebab **trong loader**). `stage`,`goal_type` — call-site (K3).
- Khoá GHI: không ghi gì (đọc thuần, trả list). Không đụng `intake_extra`.
- Derived-state? **Không** (loader không tự suy trạng thái user; chỉ lọc).
- Degrade: `industry` chuẩn hoá `_ -> -`; framework match khi `applies_to` chứa industry **HOẶC** `"all"`; `stage`/`goal_type` = None → **bỏ qua** chiều đó (không lọc). `status` gate mặc định `("live",)` nhưng test dùng `statuses=None` để đối chiếu `.base` (view `.base` KHÔNG lọc status).
- Addendum: test parity chỉ hardcode 2 view seed (chưa viết parser biểu thức `.base` tổng quát — để sau). Loader lọc thêm `goal_type` mà `.base` seed không lọc → test riêng.

## Chẻ theo FUNCTION

### F1 — parser + `load_notes()` · `webapp/brain.py` (file mới)
- Đường dẫn vault: `BRAIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brain")` (brain/ ở gốc repo, ngang webapp/).
- `_parse_note(path) -> dict`: đọc block frontmatter giữa cặp `---` đầu file (regex như `_check.py`), parse scalar + list phẳng (`[a, b]`, `["[[x]]"]`). Trả `{frontmatter..., "body": <phần sau ---> , "slug": <tên file>, "path": path}`.
- `load_notes(kinds=None) -> list[dict]`: quét `brain/frameworks|industries|craft|stages/*.md`, parse mỗi file; lọc theo `kinds` (vd `["framework"]`) nếu truyền. **Cache** kết quả (module-level dict hoặc `functools.lru_cache`), lazy — chỉ đọc đĩa lần đầu.
- Self-verify (dán vào commit): `py -c "import webapp.brain as b; ns=b.load_notes(); print(len(ns))"` → **9**; `load_notes(['framework'])` → **3**; mỗi note có `slug/type/status`.
- Commit: `feat(brain): K2 F1 webapp/brain.py loader + parse frontmatter (no pyyaml)`.

### F2 — `select()` + rank + test đối chiếu `.base`
- `_norm_industry(s) -> str`: `(s or "").strip().lower().replace("_","-")`.
- `select(industry=None, stage=None, goal_type=None, statuses=("live",)) -> list[dict]`:
  - `notes = load_notes(["framework"])`; `ind = _norm_industry(industry)`.
  - Giữ note khi: (industry None **hoặc** `ind` ∈ `applies_to` **hoặc** `"all"` ∈ `applies_to`) **VÀ** (stage None hoặc stage ∈ `note["stage"]`) **VÀ** (goal_type None hoặc goal_type ∈ `note["goal_type"]`) **VÀ** (statuses None hoặc `note["status"]` ∈ statuses).
  - **Rank:** maturity `evergreen`(0) < `fresh`(1) < `decaying`(2), rồi `updated` giảm dần. Trả list đã xếp.
- **Test đối chiếu (dán output vào commit)** — dùng `statuses=None` để so với `.base`:
  - `select(statuses=None)` (không lọc gì khác) → 3 framework = View 1 `.base` (`stp, jtbd, dunford-positioning`).
  - `select(industry="health-beauty", stage="launch", statuses=None)` → 3 framework = View 2 `.base`.
  - **Chuẩn hoá:** `select(industry="health_beauty", stage="launch", statuses=None)` (snake) cho **cùng** kết quả như `health-beauty`.
  - **goal_type (loader-only):** `select(goal_type="pricing", statuses=None)` → `[]`; `select(goal_type="positioning", statuses=None)` → 3.
  - **status gate:** `select()` (mặc định `("live",)`) → `[]` (mọi note đang `draft`).
- Commit: `feat(brain): K2 F2 select() mirror .base + chuẩn hoá industry + rank`.

## Verify chung
- `py -c "import webapp.brain"` import sạch (không lỗi cú pháp/đường dẫn).
- Mỗi F: chạy self-test, **dán output thật vào commit body** (đừng bịa). Khai "Chưa chắc / làm tắt / giả định".
- Windows dùng `py`. Push `feature/ai-cmo-core`, **dừng chờ review** sau mỗi F.

## Không làm
- KHÔNG wire vào `business.py` (K3). KHÔNG thêm pyyaml/dependency. KHÔNG parser biểu thức `.base` tổng quát (test hardcode seed là đủ). KHÔNG promote `live`.
