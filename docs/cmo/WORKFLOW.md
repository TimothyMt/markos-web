# WORKFLOW — Build Loop (Orchestrator thiết kế hệ thống, Cline chạy vòng)

> Đây là **loop XÂY Max**, KHÔNG phải loop sản phẩm bên trong Max. Mục tiêu: tôi (Claude = Orchestrator) thiết kế *chuẩn* rồi **bước ra**; Cline (Executor) tự chạy + tự soi; bạn (Human) đặt goal + chốt merge.

## 3 vai
| Vai | Làm | KHÔNG làm |
|---|---|---|
| **Human** (bạn) | Đặt GOAL 1 lần · ngồi cổng quyết định · merge | Code |
| **Orchestrator** (Claude) | Thiết kế hệ thống: standard, brief, `EVAL.md`, tiêu chí verify · review ở cổng · chốt keep/cut | **Viết code tính năng** |
| **Executor** (Cline) | Discovery→Plan→Execute→**Tự-verify** từng function · commit + self-review · bàn giao | Tự quyết keep/cut · tự merge · mở rộng ngoài brief |

**MEMORY sống NGOÀI hội thoại** = `docs/cmo/*` (PLAN, WORKFLOW, EVAL, briefs) + commit history + eval artifacts. Mỗi đơn vị việc Cline **khởi động lạnh**, chỉ đọc brief + PLAN + EVAL → đủ grounded, không cần ai kể lại. Vì chuẩn nằm trong file nên Cline tự soi được → Orchestrator mới bước ra được.

## Đơn vị việc = 1 FUNCTION (phiên Cline ngắn)
Cline có phiên ngắn → **KHÔNG ôm cả slice**. Mỗi brief chẻ thành các **function-task** (F1, F2…). Một phiên = **1 function** = 1 commit = 1 lần review.
- Ngoại lệ **mirror FE**: sửa `app.js` + mirror `dashboard-standalone.html` phải nằm **cùng 1 commit** (không để repo lệch giữa 2 bản). Coi cặp này là *một* function-task.
- Function tí hon (vd expose 1 key trong `biz_data`) có thể gộp commit với function liền kề — nêu rõ trong message.

## Vòng mỗi function-task
```
GOAL (human, 1 lần — khoá trong 00-PLAN)
   │
   ▼
1 DISCOVERY  — đọc ĐÚNG brief của function + grep tên hàm liên quan (đừng đọc cả business.py).
   │            Kể lại ý định 1–2 câu + nêu ẩn số.  Brief mơ hồ → HỎI, KHÔNG đoán.
   ▼
2 PLAN       — liệt kê edit cụ thể: file · hàm · key intake_extra · điểm mirror FE.
   ▼
3 EXECUTE    — sửa TỐI THIỂU, đúng ràng buộc (không đổi schema, tái dùng prompt agents/).
   ▼
4 SELF-VERIFY (Cline tự soi TRƯỚC khi gọi review):
   │   a) vs GOAL     — đúng ý marketing của brief?
   │   b) vs STANDARD — chạy verify commands (dưới) · checklist ràng buộc · rubric EVAL nếu là slice dữ liệu/tính năng
   │   c) EVIDENCE    — slice thêm trường dữ liệu/tính năng: xuất eval artifact theo EVAL.md
   ▼
5 HANDOFF    — commit + đưa lên GitHub + "self-review report" ngắn (mẫu dưới).
   ▼
6 GATE (Orchestrator + Human) — auto-review chạy trước (bên dưới), rồi tôi soi vs goal+standard.
   │            Chốt keep/cut ở ĐÂY (không phải Cline).
   ├── PASS → function sau  → cập nhật MEMORY (log quyết định vào docs/cmo)
   └── FAIL → quay lại (1) kèm ghi chú
```

### Verify commands (STANDARD — chạy ở bước 4b)
```bash
node --check web/app.js
python3 -c "import re;h=open('web/dashboard-standalone.html').read();open('/tmp/s.js','w').write(max(re.findall(r'<script[^>]*>(.*?)</script>',h,re.S),key=len))" && node --check /tmp/s.js
python3 -c "import webapp.business, webapp.api"
```

### Self-review report (dán vào commit body hoặc comment sau khi push)
```
[F<n>] <tên function> — <làm gì / vì sao>
Đã check: <verify commands pass?> · <ràng buộc: schema/mirror/prompt>
Bằng chứng: <link eval artifact nếu có>
Chưa chắc: <điểm cần Orchestrator quyết, vd trường X qua EVAL chưa?>
```

## Cổng review của Orchestrator — 2 MŨ: CTO + CMO (bước 6 chi tiết)
Người đánh giá output cuối của Cline = **Human + Orchestrator**. Orchestrator đội **2 mũ tách bạch** trên cùng một output:

```
Cline code xong
   │
   ▼  [CTO]  đọc code vs ràng buộc + EVAL cơ học → CHẠY THẬT → xuất ARTIFACT
   ▼  [CMO]  đọc ARTIFACT (hành vi chạy, KHÔNG đọc code) → viết kết quả cho Human trong chat
   ▼  [Human + Orchestrator]  cùng đánh giá: đúng mục tiêu marketing? giữ/sửa/bỏ?
   ▼  [CTO]  viết brief function kế → giao Cline
   └─► lặp
```

**Mũ CTO — "xây có đúng không":**
- So diff với: (A) ý định brief · (B) ràng buộc cứng (schema/mirror-FE/prompt agents/không bịa số) · (C) EVAL phần cơ học.
- **Chạy thật:** `python run_web.py` (SQLite, không cần key) drive luồng non-LLM; luồng gen thì chạy với key → **xuất artifact** (persistence round-trip; hoặc output CÓ/KHÔNG-trường cho EVAL Test3).

**Mũ CMO — "có đúng thứ cần làm không":**
- **Đọc ARTIFACT, KHÔNG đọc code.** Nhìn *output/hành vi thật* qua lăng kính marketing: (D) có phục vụ mục tiêu "Max = AI CMO" · (C) EVAL Test1 consumption + persona.
- Viết verdict cho Human **trong chat**, cùng chốt.

**Kỷ luật chống rationalize chéo:** CTO pass TRƯỚC & độc lập; CMO chỉ nhìn *kết quả* chứ không nhìn *cách làm* — nếu CMO đi đọc code thì 2 mũ sụp thành 1, mất khả năng bắt cái CTO bỏ sót. Đây là cách đóng phần **15%** mà self-review của Cline không đóng được.

**Verdict** (tầng function/hành vi, kèm file:dòng): **PASS** / **cần sửa** (liệt kê A/B/C) / **cờ cổng người** (quyết định sản phẩm keep/cut — Orchestrator KHÔNG tự chốt).

**Key:** chỉ artifact cần gen mới cần key → set **env var** cho session (đừng để trong chat/commit). Non-LLM chạy khô.

## Khoảng cách "bước ra" tăng dần
Không buông ngay: **P0 tôi đứng gần** (review kỹ từng function). Chuẩn nào đã chứng minh qua vài function → tôi **lùi xa dần**, giao Cline chạy dài hơn. Trust tăng theo harness đã kiểm chứng.

## Auto-review khi push GitHub
- Workflow `.github/workflows/claude-review.yml` chạy Claude review **tự động trên mỗi push/PR**, đọc **chính `docs/cmo/WORKFLOW.md` + `EVAL.md`** làm chuẩn (đây là lý do phải externalize chuẩn ra file).
- Đây là **một Claude instance riêng trong CI**, không mang context hội thoại này — nó chỉ biết những gì trong file. Coi nó là **lớp gác cửa đầu tiên** (bắt lỗi verify/ràng buộc/altitude), còn **quyết định sản phẩm (keep/cut) vẫn ở cổng người** (bạn + tôi).
- Cần secret `ANTHROPIC_API_KEY` trong repo. Cách bật + cách vận hành: xem cuối file workflow.
- **Khuyến nghị bề mặt review:** mở **1 draft PR sống lâu cho cả phase** (feature/ai-cmo-core → staging), mỗi function-task push lên là auto-review comment vào đúng PR đó — gọn hơn review rời từng commit. Draft PR chỉ để *review*, KHÔNG để merge (merge vẫn theo git workflow ở CLAUDE.md).
