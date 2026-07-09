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
- FE = 1 nguồn duy nhất: sửa thẳng `web/app.js` · `styles.css` · `index.html` (không còn standalone để mirror — D-047).
- Function tí hon (vd expose 1 key trong `biz_data`) có thể gộp commit với function liền kề — nêu rõ trong message.

### Hợp đồng executor — robustness (model-agnostic)
User tự chọn model cho Cline; brief viết bình thường, không chốt model. **3 chốt bất kể model:**
1. **Pre-flight** — model/phiên MỚI: hành động đầu là 1 bước trivial (tạo file rác / hoặc chính function scaffold đầu tiên) để xác nhận **tool-call format chạy** TRƯỚC khi giao việc thật. Bắt sớm lỗi "model không bắn nổi tool-call" (đỡ loop đốt token).
2. **Template inline** — việc cấu trúc (frontmatter / chữ ký hàm) → brief **dán khuôn copy-paste**, đừng bắt "tự suy từ schema".
3. **Chốt loop** — brief ghi: *"2 lần không hoàn tất nổi 1 bước → DỪNG, báo, KHÔNG lặp."* Human + noti Telegram = circuit-breaker chính (kiến trúc review chặn được rác, nhưng KHÔNG chặn loop-đốt-tiền → mắt người chặn).

## Luật vận hành (rút từ thực chiến — áp cho MỌI phiên Orchestrator)
> 4 luật này nâng từ bài học chạy thật (2026-07). Bản gốc ở memory local; chép vào đây để **đi theo git sang máy/IDE khác**.

1. **Việc nhỏ → Orchestrator TỰ LÀM, không vòng qua Cline.** Task 1–vài dòng / 1 hàm nhỏ theo khuôn có sẵn (thêm 1 route, expose 1 key, chèn 1 dòng inject) → Claude tự Edit + verify + commit + push. *Vì sao:* round-trip Cline cho việc tí hon vừa chậm vừa hay kẹt (pager git, lệnh Unix `head`/`tail` trên PowerShell). Đây là **ngoại lệ có kiểm soát** của luật "Orchestrator không viết code" — chỉ cho việc nhỏ/recovery, KHÔNG ôm luôn function lớn.
2. **Cline CẮT CỤT file lớn khi Write đè.** Với file rất lớn (vd `webapp/business.py` ~4000+ dòng), nếu Cline **ghi đè cả file bằng Write** → output vượt ngưỡng token → **mất hàng nghìn dòng cuối** (đã xảy ra: 4073→605). *Cổng review:* LUÔN chạy `git --no-pager diff --numstat <file>` — thấy dòng **xoá** bất thường = FAIL, KHÔNG commit, reset `git checkout HEAD -- <file>` rồi chèn lại có mục tiêu. Dispatch file lớn: **cấm Write đè, bắt Edit chèn có mục tiêu**.
3. **Ưu tiên tự thực thi khi đã có quyền/key.** User cấp quyền/secret → tự chạy (set secret, push, chạy test) rồi báo kết quả; đừng trả về "các bước thủ công để bạn tự làm". Key/secret chỉ set env cho lần chạy, **KHÔNG commit/ghi file/lưu memory**.
4. **KHÔNG nịnh — đối chiếu goal + research rồi mới quyết.** User hỏi/đề xuất → KHÔNG gật cho vừa lòng. Đối chiếu (a) goal thật, (b) bằng chứng research (docs/WIRING/EVAL/nguồn). Rồi mới **đồng ý (ngắn)** hay **phản biện thẳng (kèm lý do + phương án đúng)**. Không chắc → nói "chưa chắc" + cách kiểm, đừng đoán cho xong.

## Vòng mỗi function-task
```
GOAL (human, 1 lần — khoá trong 00-PLAN)
   │
   ▼
1 DISCOVERY  — đọc ĐÚNG brief của function + grep tên hàm liên quan (đừng đọc cả business.py).
   │            Kể lại ý định 1–2 câu + nêu ẩn số.  Brief mơ hồ → HỎI, KHÔNG đoán.
   ▼
2 PLAN       — liệt kê edit cụ thể: file · hàm · key intake_extra · điểm chạm FE.
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
python3 -c "import webapp.business, webapp.api"
```

### Self-review report (dán vào commit body hoặc comment sau khi push)
```
[F<n>] <tên function> — <làm gì / vì sao>
Đã check: <verify commands pass?> · <ràng buộc: schema/mirror/prompt>
Bằng chứng: <link eval artifact nếu có>
Chưa chắc: <điểm cần Orchestrator quyết, vd trường X qua EVAL chưa?>
```

## Cổng review — 4 VAI, nổ theo LỚP (bước 6 chi tiết)
Người đánh giá output cuối = **Human + Orchestrator**, nhưng tách thành **4 vai**, mỗi vai chỉ nổ ở đúng lớp (tránh vai bịa việc ở lớp không có bề mặt của nó):

| Vai | Ai đóng | Chấm gì | Nổ ở lớp |
|---|---|---|---|
| **CTO** | Orchestrator | Code vs ràng buộc (schema/mirror-FE/prompt agents/không bịa số) + verify commands | mọi function |
| **Tester** | **subagent TƯƠI** (≠ Cline builder, ≠ tôi) | Chạy thật · edge case · round-trip · trace flow → xuất artifact, báo works/breaks | mọi function có hành vi runtime |
| **CMO-persona** | **subagent** đóng 1 archetype EVAL (D2C solo / SME / dịch vụ) | Phản ứng NGƯỜI THẬT: câu hỏi có hiểu/điền được? output có phải bài dám đăng? | lớp có form hỏi user hoặc output AI |
| **CMO-tổng hợp + gate** | Orchestrator + Human | Chuẩn marketing (rubric EVAL) · keep/cut · redesign | lớp chiến lược/gen; cổng cuối |

```
Cline code xong
   ▼ [CTO]        code vs ràng buộc + verify  (mọi function)
   ▼ [Tester]     chạy thật → ARTIFACT + works/breaks  (độc lập với builder)
   ▼ [CMO-persona] đọc ARTIFACT như founder thật  (chỉ lớp có bề mặt marketing)
   ▼ [CMO-tổng hợp + Human]  rubric + keep/cut  → brief kế
   └─► lặp
```

**Vì sao tách vai (không chỉ đổi tên):**
- **Tester ≠ builder** → không ai tự chấm bài mình; đóng đúng phần **15%** self-review của Cline mù.
- **Tester ≠ CTO/CMO** → ở lớp backend, CMO khỏi bịa việc (không có output marketing để chấm); ở lớp gen, phán marketing khỏi loãng vì QA.
- **CMO-persona là subagent tươi** → phản ứng thật thà như user thật. Tôi *giả vờ* làm founder thì hỏng: tôi thiết kế nó nên không bao giờ bối rối ở chỗ founder thật bối rối (không ai usability-test được thiết kế của chính mình).
- **CTO + CMO-tổng hợp giữ ở Orchestrator** → đây là phán xét cốt lõi (code-vs-brief, chuẩn marketing, keep/cut), uỷ đi chỉ thêm khâu trung gian.

**Ma trận lớp × vai:**
| Lớp | CTO | Tester | CMO-persona | CMO-tổng hợp + gate |
|---|:-:|:-:|:-:|:-:|
| Backend thuần (vd F1 save_spine) | ✅ | ✅ | — | — |
| Form hỏi user (vd F4) | ✅ | ✅ | ✅ | ✅ |
| Output AI (P0.2, D1+ gen) | ✅ | ✅ | ✅ | ✅ (keep/cut) |

**CMO sâu, không nông** (vai nặng nhất — quyết chất lượng sản phẩm). Chống nông bằng cấu trúc, không bằng "cố hơn":
- **Mốc vàng do Human gieo** — vài bài/định vị "chuẩn" + vài cái "dở" → khẩu vị của founder này, không phải trung bình internet.
- **Rubric có răng** (trong `EVAL.md`) — danh sách lỗi chết người có tên, không hỏi "hay không".
- **CMO đóng vai ĐAO PHỦ:** output = "3 lý do một CMO thật sẽ GIẾT cái này", không phải điểm số. Không tìm ra lý do giết mới được PASS.
- **Hai mắt độc lập hội tụ:** CMO-persona (naive) + CMO-tổng hợp (rubric). Lệch nhau → cờ cổng người.

**Kỷ luật:** CTO + Tester pass TRƯỚC & độc lập; CMO-persona chỉ nhìn *artifact* không nhìn *code*.
**Verdict** (kèm file:dòng): **PASS** / **cần sửa** (A/B/C) / **cờ cổng người** (keep/cut — Orchestrator KHÔNG tự chốt).
**Key:** chỉ artifact cần gen mới cần key → **env var** cho session (đừng để chat/commit). Non-LLM chạy khô.

## Vòng TRI THỨC — đi trước build 1 nhịp (kho = moat của Max)
LLM là hàng chợ; **kho craft marketing tuyển chọn, tươi, theo (output × kênh × ngành)** mới là moat. Kho phục vụ **3 đầu từ một nguồn:**
1. **Thước** — CMO chấm output vs best-practice thật (không vibes).
2. **Nhiên liệu gen** — rule/few-shot nhét prompt để LLM Max ra đúng chất.
3. **Bản thiết kế** — định hình chính step/flow/function/câu-hỏi/output của Max (marketing quyết kiến trúc, không phải tôi bịa flow).

**Đơn vị = Craft Card** cho mỗi node `(output × kênh × ngành)`, 5 phần: nguyên tắc craft (bền) · exemplar tươi (**nguồn + ngày**, chống bịa + biết khi rữa) · rubric chấm [đầu①] · spec gen [đầu②] · hàm ý thiết kế [đầu③].

**Vòng (chạy TRƯỚC vòng build 1 nhịp):**
```
① bản đồ hệ thống (node) → ② CMO giao research-subagent (web/grounded) → ③ distill → CRAFT CARD
   → ④ CTO chọn cơ chế (prompt bake / file-store /industry / LLM-grounded lôi) → brief Cline
   → ⑤ Cline build wiring → ⑥ Max gen → Tester+CMO chấm vs CÙNG card → ⑦ hết đát → re-research
```
Bước ① là **output tự sửa** (research phát hiện node sai/thiếu → viết lại bản đồ). Tri thức ngồi TRÊN kiến trúc.

**Governance (đầu③ gây bất ổn — 3 chốt):**
1. **Không auto-apply** — redesign đi qua cổng Human + Orchestrator (keep/cut).
2. **Lõi ổn định neo** — Spine + 6 miền là bedrock đã validate; tri thức chỉnh ở rìa/miền chưa build.
3. **Đi trước build 1 nhịp** — research miền kế TRƯỚC khi brief nó (redesign rẻ nhất khi code chưa tồn tại). Research sau khi Cline đã code = chỉ tạo việc đập-xây-lại.

> Cơ chế đưa vào Max (đầu②): craft bền → prompt `agents/`; card theo ngành/kênh → file repo lazy-load (KHÔNG bảng DB); ngành chưa có card → LLM grounded (`llm_router`) lôi live. Bắt đầu file-based, chỉ lên RAG khi ma trận phình. Chi tiết chuẩn kho: `KNOWLEDGE.md` (sẽ viết khi Giai đoạn 1 khởi động).

## Khoảng cách "bước ra" tăng dần
Không buông ngay: **P0 tôi đứng gần** (review kỹ từng function). Chuẩn nào đã chứng minh qua vài function → tôi **lùi xa dần**, giao Cline chạy dài hơn. Trust tăng theo harness đã kiểm chứng.

## Auto-review khi push GitHub
- Workflow `.github/workflows/claude-review.yml` chạy Claude review **tự động trên mỗi push/PR**, đọc **chính `docs/cmo/WORKFLOW.md` + `EVAL.md`** làm chuẩn (đây là lý do phải externalize chuẩn ra file).
- Đây là **một Claude instance riêng trong CI**, không mang context hội thoại này — nó chỉ biết những gì trong file. Coi nó là **lớp gác cửa đầu tiên** (bắt lỗi verify/ràng buộc/altitude), còn **quyết định sản phẩm (keep/cut) vẫn ở cổng người** (bạn + tôi).
- Cần secret `ANTHROPIC_API_KEY` trong repo. Cách bật + cách vận hành: xem cuối file workflow.
- **Khuyến nghị bề mặt review:** mở **1 draft PR sống lâu cho cả phase** (feature/ai-cmo-core → staging), mỗi function-task push lên là auto-review comment vào đúng PR đó — gọn hơn review rời từng commit. Draft PR chỉ để *review*, KHÔNG để merge (merge vẫn theo git workflow ở CLAUDE.md).
