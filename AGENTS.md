# AGENTS.md — luật cho AI coding agent (Cline / Antigravity / …)

Đọc `CLAUDE.md` trước khi code (kiến trúc, quy ước dữ liệu). Đụng function/mối nối → đọc thêm `docs/cmo/WIRING.md`.

## Môi trường: Windows PowerShell
- Git: LUÔN `git --no-pager ...`. **Terminal treo = pager, KHÔNG phải lệnh chậm** → chạy lại, đừng ngồi chờ/đoán.
- Tìm chuỗi: `git grep -n "x" -- web/ webapp/`. **Không có** `grep` / `head` / `tail`.
- Python: `python` (fallback `py`), **không** `python3`.
- Cấm lệnh cần nhập phím: `git rebase -i`, `git add -i`.

## Sửa file
- Chỉ **Edit chèn/xoá có mục tiêu**. **KHÔNG Write đè cả file** — `web/app.js` và `webapp/business.py` rất lớn, đè = mất nội dung.
- FE 1 nguồn: `web/app.js` · `web/data.js` · `web/index.html` · `web/styles.css`.
  **Không còn `dashboard-standalone.html`** (D-047) → **không mirror đi đâu cả**.

## Không làm
- **Không đổi schema DB** — mọi config mới → key trong `profile.intake_extra`.
- Không bịa số liệu trong output AI. Không hardcode ví dụ 1 ngành (sản phẩm đa ngành).
- Không đụng `bot/`, không thêm phụ thuộc Telegram.

## Verify trước khi commit
```
python -m py_compile webapp/business.py webapp/api.py
node --check web/app.js
python tests/<file>.py        # exit 0 = pass
```

## Git workflow
- Nhánh riêng từ `staging`. **Không** commit thẳng `main`/`staging`.
- PR: `gh pr create --base staging` (base = **staging**, không phải main).
- **Không tự merge.** Claude review → user quyết.
- Sửa theo feedback → commit thêm vào cùng branch/PR, không mở PR mới.
