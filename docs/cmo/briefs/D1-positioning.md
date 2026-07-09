# Slice D1 (F1) — Nối vault khung định vị vào Synthesis (K3 gộp vào đây)

> **Mục tiêu:** mục "## 3. Định vị" trong Synthesis được **grounded bằng craft card** trong vault (`dunford-positioning`, `jtbd`, `stp`) — LLM viết định vị THEO khung nghề, không tự chế. Đây là **K3 (wire `select()` vào business.py) gộp vào D1** vì K3 đứng một mình sẽ nối vào pipe rỗng.
> **Đọc trước:** `brain/frameworks/*.md` (3 card đã `live`, đã lấp ruột) · `webapp/brain.py` (`select()`) · `webapp/business.py` hàm `strategize_web` (~dòng 3549) + `_spine_anchor` (~2883, mẫu inject) · `docs/cmo/WIRING.md`.
> **Branch:** `feature/consolidate` (nhánh tích hợp hiện hành).

## Bối cảnh — vòng tri thức ĐÃ xong (đừng làm lại)
Orchestrator đã lấp ruột 3 card định vị + promote `draft→live` + verify (`select(goal_type='positioning')` trả đủ 3, `brain/_check.py` OK). **Việc của Cline = CHỈ phần wiring**, KHÔNG sửa card, KHÔNG sửa `brain.py`.

## Luật sống còn
1. **KHÔNG đổi schema DB**, KHÔNG sửa `brain/*` hay `brain.py`. Chỉ thêm code trong `webapp/business.py`.
2. **Degrade an toàn:** vault trống / import lỗi / `select()` raise → `_framework_anchor` trả `""`; prompt chỉ thiếu block, KHÔNG vỡ. Đây là bất biến — bọc try/except, KHÔNG raise ra ngoài.
3. **KHÔNG bịa số**, tái dùng prompt `agents/` như cũ (không đụng).
4. File lớn (`business.py` ~4000+ dòng): **Edit chèn có mục tiêu, CẤM Write đè cả file** (WORKFLOW luật 2).

## Phân tích mối nối (WIRING Hiến pháp)
- **Khoá ĐỌC:** card frontmatter + body trong `brain/` — **producer = knowledge-loop (đã live ✅)**. `industry` (tham số) — producer = `prof.get("industry")` (đã đọc sẵn trong `strategize_web` dòng ~3593). `goal_type="positioning"` = hằng call-site.
- **Khoá GHI:** không ghi gì (đọc thuần, trả str). KHÔNG đụng `intake_extra`.
- **Derived-state?** KHÔNG — chỉ lọc/format, không suy trạng thái user.
- **Tới được runtime?** `strategize_web` chạy khi founder bấm "Lập chiến lược" ✅.
- **Đường degrade:** đã nêu ở Luật 2. `select()` mặc định `statuses=("live",)`; 3 card đã `live` nên nhận được — KHÔNG truyền `statuses` khác.
- **Chống parrot:** chỉ bơm **Spec gen + dòng "Mạch"** (khuôn + luật), KHÔNG bơm Exemplar/Rubric (tránh LLM chép "theo Dunford…"/"TH true MILK…" ra output founder). Block có câu dặn "nội bộ, đừng nhắc tên khung/ví dụ ra output".

## F1 — `_framework_anchor()` + chèn vào `syn_user`

### (a) Thêm helper — đặt NGAY TRÊN `_spine_anchor` (~dòng 2883), khuôn dán sẵn:
```python
def _framework_anchor(industry: str = "", goal_type: str = "positioning", limit: int = 3) -> str:
    """D1: lôi craft card khung (Spec gen + Mạch) từ vault → block bơm vào prompt Synthesis.
    Chỉ lấy phần 'nhiên liệu gen', KHÔNG lấy exemplar/rubric (chống parrot).
    Degrade: vault trống / lỗi → "" (KHÔNG raise)."""
    try:
        from webapp import brain
        notes = brain.select(industry=industry or None, goal_type=goal_type or None)
    except Exception:
        return ""
    if not notes:
        return ""
    blocks = []
    for n in notes[:limit]:
        body = n.get("body") or ""
        title = n.get("title") or n.get("slug") or ""
        # trích dòng "Mạch" (khuôn nén) + section "## Spec gen"
        mach = ""
        spec = []
        in_spec = False
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("> Mạch") or s.startswith("Mạch:"):
                mach = s.lstrip("> ").strip()
            if s.startswith("## "):
                in_spec = s.startswith("## Spec gen")
                continue
            if in_spec and s:
                spec.append(s)
        if not spec and not mach:
            continue
        part = f"### {title}\n"
        if mach:
            part += f"{mach}\n"
        if spec:
            part += "\n".join(spec) + "\n"
        blocks.append(part.strip())
    if not blocks:
        return ""
    return ("\n\n# KHUNG ĐỊNH VỊ (nội bộ — bám các luật này khi viết mục Định vị; "
            "ĐỪNG nhắc tên khung/ví dụ ra output cho founder)\n\n" + "\n\n".join(blocks) + "\n")
```

### (b) Chèn vào prompt Synthesis — trong `strategize_web`, chỗ ráp `syn_user` (~dòng 3677):
`syn_user` hiện bắt đầu `f"# Ngành\n{industry}\n{ictx}\n\n"`. Chèn framework block NGAY SAU dòng ngành (industry đã có sẵn ở scope):
```python
        fw_anchor = _framework_anchor(industry=industry, goal_type="positioning")
        syn_user = (
            f"# Ngành\n{industry}\n{ictx}\n"
            f"{fw_anchor}\n"
            f"{bet_block}"
            ... # giữ nguyên phần còn lại
        )
```
> Chỉ synthesis (mục Định vị). KHÔNG đụng `_gen_playbook`/`tac_user` ở F1 (playbook là Segment→Phễu, không phải consumer định vị — để slice sau nếu cần).

## Verify (bước 4b — dán output thật vào commit)
```bash
python3 -c "import webapp.business, webapp.api"
py -c "from webapp.business import _framework_anchor; b=_framework_anchor(goal_type='positioning'); print('LEN', len(b)); print(b[:400])"
```
- Kỳ vọng: block chứa "KHUNG ĐỊNH VỊ" + luật Spec gen của 3 card (alternative/so-what/job/wedge…), KHÔNG chứa "TH true MILK"/"Milkshake"/"Biti's".
- Degrade test: `py -c "from webapp.business import _framework_anchor; print(repr(_framework_anchor(goal_type='nonexistent')))"` → `''`.

## Self-review report (dán vào commit)
```
[D1-F1] _framework_anchor + wire synthesis — grounded mục Định vị bằng vault
Đã check: import sạch · anchor trả block Spec-gen 3 card, không lộ exemplar · degrade '' khi rỗng
Chưa chắc: có nên bơm cả vào playbook không (đề xuất KHÔNG ở F1)
```

## Không làm
- KHÔNG sửa `brain/*`, `brain.py`. KHÔNG bơm exemplar/rubric vào prompt. KHÔNG đụng playbook. KHÔNG đổi `select()` statuses. KHÔNG Write đè `business.py`.
- 1 function = 1 commit, push, **dừng chờ review** (KHÔNG tự merge).
