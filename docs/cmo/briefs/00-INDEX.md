# BRIEFS cho Cline — cách làm

> **Đọc `docs/cmo/00-PLAN.md` 1 lần** để hiểu bức tranh. Rồi làm **từng slice**, KHÔNG ôm cả phase.
> **Branch:** `feature/ai-cmo-core` (worktree `D:/MarkOS/wt-cmo`). **KHÔNG mở PR** — commit từng slice, báo Claude review.

## Luật mỗi slice
1. Chỉ đọc file brief của slice đó + đúng vài hàm code liên quan (brief chỉ tên hàm/dòng). ĐỪNG đọc cả `business.py`.
2. **KHÔNG đổi schema DB** → dữ liệu mới vào `profile.intake_extra`.
3. **MIRROR FE:** `web/app.js` ↔ `<script>` standalone; `web/styles.css` ↔ `<style>` standalone.
4. Verify trước khi commit:
   ```bash
   node --check web/app.js
   python3 -c "import re;h=open('web/dashboard-standalone.html').read();open('/tmp/s.js','w').write(max(re.findall(r'<script[^>]*>(.*?)</script>',h,re.S),key=len))" && node --check /tmp/s.js
   python3 -c "import webapp.business, webapp.api"
   ```
5. Commit 1 slice = 1 commit, message rõ. Báo Claude. **Chờ review xong mới sang slice sau.**

## Thứ tự slice (chỉ P0 có brief sẵn — phase sau brief sau khi review)
| Slice | File | Xong chưa |
|---|---|---|
| 0.1 | `P0.1-objective-intake.md` | ⬜ |
| 0.2 | `P0.2-objective-wire.md` | ⬜ |
| … | (P1+ sẽ được Claude brief sau khi P0 review xong) | |

> Không chắc chỗ nào → hỏi lại, ĐỪNG bịa. Được tham khảo `marketingskills` repo + `product-journey-4-tang.md` (xem PLAN mục "Tham khảo").
