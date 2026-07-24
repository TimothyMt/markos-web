# WIRING.md — Cổng kiểm mối nối (seam check)

> **Vì sao có file này:** lỗi nguy hiểm nhất không phải bug trong 1 hàm — mà là **lỗ hổng ở MỐI NỐI**: component A *tiêu thụ* một khoá dữ liệu mà **không component nào sản xuất** ra nó, hoặc sản xuất dưới **tên/kiểu/slug lệch**. Loại lỗi này **im lặng tới runtime mới nổ**.
> Ví dụ thật (2026-07): `select()` của recall cần `(industry, stage, goal_type)` nhưng `stage` **không ai khai** → chỉ lộ khi có người truy ngược "khoá này ai đẻ ra".
> Đây là **cổng CTO bắt buộc** ở mỗi slice, chạy TRƯỚC khi PASS — không đợi run.

## Hiến pháp mối nối — áp cho MỌI function của dự án (bất biến toàn cục)
> Nâng từ bài học K1/F2 thành **luật chung**: mọi function (brain, P*, D*, route, FE…) đều qua. Đây là bất biến — chốt 1 lần, không phân tích lại từng lần.

1. **Khai hợp đồng.** Mọi khoá dữ liệu function *đọc* hoặc *ghi* phải có 1 dòng trong "Sổ hợp đồng" dưới: `{consumer · producer · kiểu · slug/enum · status}`. **Khoá không có producer = FAIL** (đây là lỗ hổng đã suýt lọt với `stage`).
2. **Khớp mối nối (4 câu truy ngược).** (a) producer tồn tại? (b) tên/slug/enum khớp CHÍNH XÁC 2 đầu? (c) kiểu khớp (object vs string, list vs scalar)? (d) producer chạy TRƯỚC consumer lúc runtime?
3. **Đường degrade.** Input có thể thiếu/thô → định nghĩa fallback êm (vd family→slug tinh), không để vỡ.
4. **Luật derived-state** (xem mục riêng) nếu function tự suy trạng thái user.
5. **Kế thừa CLAUDE.md:** không đổi schema DB (khoá mới → `intake_extra`) · FE 1 nguồn (sửa thẳng `web/`, không mirror standalone — D-047) · không bịa số · 1 function = 1 commit + self-verify.

## Hai tốc độ (chống overload — không boil-ocean)
```
TỐC ĐỘ 1 — Hiến pháp (1 lần, đã chốt ở đây)   → bất biến, mọi function tuân, KHÔNG phân tích lại
TỐC ĐỘ 2 — Phân tích mối nối / từng function    → JIT tại brief-time, CHỈ function sắp build
```
- **Vì sao JIT:** phân tích function chưa build là phí + mốc (thiết kế phía trước còn trôi). Chỉ **bất biến toàn cục** đủ ổn định để chốt sớm; **mối nối cục bộ** rẻ & chính xác nhất khi làm ngay lúc viết brief (đi trước build 1 bước).
- **Hook bắt buộc:** mỗi brief function có mục **"Phân tích mối nối"** → điền dòng hợp đồng cho function đó + **note phần Hiến pháp không phủ** (addendum riêng của function). Cổng review chỉ PASS khi mục này xong.

Mẫu mục "Phân tích mối nối" (chép vào mỗi brief):
```md
## Phân tích mối nối (theo WIRING Hiến pháp)
- Khoá ĐỌC: <key> ← producer: <ai/đâu> · kiểu · khớp? · status
- Khoá GHI: <key> → consumer dự kiến: <ai> · kiểu
- Derived-state? (có/không) → nếu có: log confidence/why + review gate
- Degrade khi thiếu input: <mô tả>
- Addendum (Hiến pháp KHÔNG phủ chỗ nào cho function này): <ghi hoặc "không">
```

## Luật derived-state — khi Max TỰ SUY trạng thái user
> Áp cho MỌI thứ Max tự quyết về user (ngành tinh, `stage`, funnel, phân khúc…), không chỉ ngành. Để Max tự quyết mà không để vết = drift âm thầm → rối.

**Bắt buộc mọi quyết định suy luận:**
- Lưu vào `intake_extra` (append-only, cap ~20 sự kiện, KHÔNG đổi schema):
  `{ current: {value, confidence, updated}, log: [{ts, from, to, confidence, why:[tín hiệu], by}] }`.
- **`why`** ghi rõ tín hiệu nào đẩy quyết định (đọc log là hiểu, không phải đoán).

**3 luật chống rối:**
1. **Sàn tự tin** — `confidence` thấp → KHÔNG override, giữ mức thô + cờ "cần thêm tín hiệu".
2. **Đóng băng khi dao động** — value lật A→B→A ngắn hạn → freeze + cờ review (người/CTO xử).
3. **Con người thắng** — có đường sửa rẻ; value do người chốt (`by:"human"`) thì Max KHÔNG tự đè.

## 2 lớp kiểm

### Lớp 1 — Linter cơ học (chạy được, tự động)
`brain/_check.py` — bắt **synapse đứt** trong vault: `[[link]]` / `applies_to` / `fit_frameworks` / `expresses` / `industry` / giá trị `stage:` PHẢI trỏ tới file/slug có thật; `slug` khớp tên file.
```bash
py brain/_check.py     # exit 0 = thông · exit 1 = có synapse đứt
```
Chạy sau MỌI slice K* (thêm/sửa note brain). Không phụ thuộc pyyaml.

### Lớp 2 — Sổ hợp đồng + luật truy ngược (con người + CTO)
Linter chỉ thấy **trong vault**. Mối nối **xuyên hệ** (intake → recall → loader → call-site) thì linter không thấy — phải kiểm bằng **sổ hợp đồng** dưới đây.

**LUẬT (CTO chạy ở mỗi slice, trước khi PASS):**
Với **mọi khoá dữ liệu** mà code mới *đọc* hoặc *ghi*, truy 4 câu:
1. **Producer tồn tại?** — Khoá này ai GHI ra? (intake nào / slice nào / call-site nào). Không có producer = **FAIL**.
2. **Tên/slug/enum khớp?** — Chuỗi khoá & giá trị khớp CHÍNH XÁC hai đầu? (recall muốn `d2c-skincare` — intake có ghi đúng slug đó không, hay ghi `health_beauty`?).
3. **Kiểu khớp?** — object vs string, list vs scalar (vd bug `positioning` = chuỗi thay vì object).
4. **Tới được lúc chạy?** — Producer có thật sự chạy TRƯỚC consumer ở runtime không?

Bất kỳ câu nào "không" → ghi vào sổ dưới dạng **hàng GAP**, và slice tiêu thụ khoá đó **KHÔNG được PASS** cho tới khi có producer.

## Sổ hợp đồng — các khoá xuyên ranh giới

> Cập nhật mỗi khi thêm khoá xuyên component. `status`: ✅ nối · ⚠️ lệch (có nhưng sai tên/kiểu/slug) · ❌ thiếu producer.

### Hợp đồng recall: `select(industry, stage, goal_type)` (K3 sẽ cắm)
| Khoá | Kiểu | Consumer | Producer | Khớp? | Status |
|---|---|---|---|---|---|
| `industry` (family) | slug kebab | `brain.select()` (K2/K3) | profile `industry` (đã có, 14 key) — chuẩn hoá `.replace("_","-")` ở recall | canonical = 14 key; note family khớp | ✅ **B** (đã chốt: 14 key làm gốc, degrade family) |
| `industry` (slug tinh) | slug kebab | `brain.select()` degrade | **Max suy ra** (classifier, derived-state) — không phải intake | note tinh (seed dần) | ✅ nguồn = derived; degrade→family nếu chưa có note tinh |
| `stage` | enum `launch\|growth\|scale` | `brain.select()` (K2/K3) | **P0.1 Spine** (hỏi 1 câu, người khai; validate ∈ 3 slug `brain/stages/`) | slug khớp file stage; `""`→`select(stage=None)` | ✅ **A1 gộp P0.1** (người khai). Lớp Max tinh chỉnh theo tín hiệu = **A2** tương lai (derived-state) |
| `goal_type` | enum D1–D6 | `brain.select()` (K2/K3) | **call-site** (feature đang chạy truyền vào), KHÔNG phải intake | n/a | ✅ (nguồn = call-site) |
| `status==live` | enum | `brain.select()` | governance (draft→reviewed→live) | — | ✅ luật đã định (KNOWLEDGE.md) |

### Hợp đồng Spine (P0.1): `intake_extra.spine`
| Khoá | Kiểu | Consumer | Producer | Status |
|---|---|---|---|---|
| `spine.objective.target.value` | number\|null | P0.2 prompt · D6 đo gap | P0.1 F1 `save_spine` (ép số **locale VN**) | ✅ build (07eb89d) |
| `spine.positioning` | **object** `{alternative,differentiator,statement}` | P0.2 prompt · D1 | P0.1 F1 (KHÔNG phải chuỗi) | ✅ build (07eb89d) |
| `spine.constraint` | object | D3/D4 cắt phạm vi | P0.1 F1 | ✅ build (07eb89d) |
| `spine.stage` (A1 gộp) | enum `launch\|growth\|scale\|""` | `brain.select()` (qua K3) | P0.1 F1/F4 (người khai, validate enum) | ⚠️ **dual-producer**: cũng có `profile.stage` (intake). Nay không vỡ (select đọc spine.stage); **A3** hợp nhất (spine pre-fill từ profile). Cùng: `audience.who↔target_customer`, `positioning↔usp` |

### Hợp đồng Auth (Luồng B): session ↔ user_id ↔ entitlement
| Khoá | Kiểu | Consumer | Producer | Khớp | Status |
|---|---|---|---|---|---|
| session `uid` | int\|None | `UidContextMiddleware`→`business._current_uid`→`pick_user_id` | OAuth callback `google_oauth.callback` set `request.session['uid']` | cookie ký (itsdangerous) | ✅ build |
| session `email` | str | `api._is_admin` (gác `/api/admin/*`) | OAuth callback set `session['email']` | so `ADMIN_EMAILS` (lower) | ✅ build |
| `auth_identities.(provider,external_id)` | (text,text) UNIQUE | `find_or_create` | Google `sub` | sub ≤ chuỗi; user_id nội bộ tách khỏi sub | ✅ build |
| `auth_identities.user_id` | bigint FK→users | `find_or_create`, `admin_*`, `biz_data.identity` | `web_user_id_seq` (DEFAULT trên `users.user_id`) | seq ≥ 10^12, trên dải Telegram | ✅ build |
| `auth_identities.status` | enum `pending\|active\|blocked` | `quota.ensure_can_spend` (gate), FE `bizAuthStatus` | `find_or_create`(pending) · `admin_set_access` | **gate TRUY CẬP**, KHÁC `token_quota` | ✅ build |
| `users.token_quota/used` | int | `quota.ensure_can_spend` (chặn cứng), `record_usage` | admin kích hoạt (quota) · `_post_hook` (used) | **ngân sách token**, KHÁC status | ✅ build |
| `bizAuthed/bizAuthStatus/bizEmail/bizIsAdmin` | bool/enum/str/bool | FE `_authGateMode`, `P.admin` | `biz_data` (từ identity) | tên khớp FE↔`biz_data` | ✅ build |
| `bizUsers` | list | FE user-switcher, `P.admin` | `biz_data` — **chỉ khi `is_admin`** (non-admin → `[]`) | chống rò danh sách user | ✅ build (siết) |

> **Seam quan trọng:** hàm user-scoped (59 hàm) đọc user_id CHỈ qua `pick_user_id` (choke point đã verify 0 bypass). HTTP → contextvar (session) là nguồn DUY NHẤT, `requested` client **inert**. `admin_*` CỐ Ý nhận user_id tường minh (thao tác trên user khác) → bảo vệ bằng gác `ADMIN_EMAILS` ở api layer, KHÔNG qua `pick_user_id`.

### Hợp đồng S1 — Bản đồ trận địa (`intake_extra.battle_map` / `resources` / `principles`)
Spec: `SPEC-chien-dich-4-tang.md` · Brief: `BRIEF-S1-ban-do-tran-dia.md` §2. Test cổng: `tests/test_s1_battle_map.py`.

| Khoá | Kiểu | Consumer | Producer | Khớp / degrade | Status |
|---|---|---|---|---|---|
| `battle_map.audiences[].id` | `aud_<8hex>` | S2 nước đi · **S3 khoá lịch** · S4 | `gen_battle_map` mint 1 lần · `save_battle_map` TÔN TRỌNG id client | **id ổn định qua đổi tên** — giải mìn HANDOFF §4. KHÔNG bám label | ✅ build |
| `battle_map.audiences[].role` | enum `core\|growth\|retain` | S2 lọc nước đi | `gen_battle_map` (core←`wedge` · growth←T2 synthesis · retain←`asked`) | thiếu nguyên liệu → vẫn dựng khung, `source='max'`, `confidence='low'` | ✅ build |
| `…stages.<stage>.applicable` | bool | S2/S3 bỏ qua ô không áp dụng | mặc định `_stage_applicable_default` (retain → 2 giai đoạn đầu = false); người toggle | 4 stage enum `awareness\|consideration\|conversion\|retention` | ✅ build |
| `…problems[].type` | enum 6 loại | **S2 index thư viện nước đi** (`loại × giai đoạn`) | LLM chọn, code chuẩn hoá `_norm_problem_type` | slug lạ → vấn đề bị **vứt** (không nhận loại tự chế) | ✅ build |
| `…problems[].source` | enum `user\|research\|max` | nhãn độ thật trên UI · S4 | LLM gán; `user` = founder tự kể (Q9) | rỗng → `max` | ✅ build |
| `…problems[].text` | str ≤200 | S2 sinh nước đi | LLM (câu cụ thể, giọng khách) | **guard**: text = tên loại ("bất tiện"/"price") hoặc <8 ký tự → vứt (brief §9) | ✅ build |
| `…edited_by_user` (tệp + vấn đề) | bool | `gen_battle_map` merge | `save_battle_map` **tự diff** với bản đã lưu (không cần FE khai) | **người thắng máy**: regen không đè mục edited, không đè `source='user'`, không xoá tệp | ✅ build |
| `resources.can_*` | bool ×3 | S2 lọc liều nước đi | `save_resources` (người tick) | thiếu → `False`; **không định lượng** (GRILL §7) | ✅ build |
| `principles[].expires` | iso\|**None** | S2 phanh loại-1 | `save_principles` (CHỈ người gõ) | vô hạn = `None`, KHÔNG dùng `""` (tránh trạng thái thứ 3) | ✅ build |
| `bizBattleMap/bizResources/bizPrinciples` | dict/dict/list | FE trang Bản đồ | `biz_data` (đọc thẳng `intake_extra`) | ⚠️ **cấm gọi LLM trong `biz_data`** — chạy mỗi lần tải trang | ✅ build |
| `CHANNELS['google_maps']` | dict spec kênh | picker kênh · S3 rải | `CHANNELS` (business.py) | alias phải đủ dài — `channel_slug` khớp **substring**, alias ngắn nuốt nhầm từ khác | ✅ build |

> **Derived-state (§ luật trên):** `battle_map` là Max SUY → mọi tệp/vấn đề mang `confidence` + `why` + `updated`, có đường human-override (`save_battle_map`), và degrade thật thà khi LLM/nguyên liệu hỏng (`degraded=True`, giữ nguyên bản cũ).
> **Nợ đã biết:** `channel_slug` khớp substring nên alias 2 ký tự bắt nhầm — `"oa"` (zalo_oa) nuốt `"roadmap"`. Sửa đúng = khớp theo biên từ, chưa làm (ngoài phạm vi S1).

**Seam grounding T3 (nuôi chất `battle_map`):** `gen_battle_map` đọc `customer_insight` (T3). T3 giờ chạy **grounded** qua task type `CUSTOMER_INSIGHT_GROUNDED` (`llm_router.py`: Gemini+Google Search → fallback Anthropic khi thiếu `GEMINI_API_KEY`) và **tiêu thụ `social_page_audit`** (producer = `audit_social_page`, "Báo cáo kênh") nếu đã cache → tiêm voice khách thật vào prompt T3. Degrade: thiếu Gemini/audit → T3 = suy luận như cũ (không mất gì). Bật thật cần prod có `GEMINI_API_KEY` + user chạy Báo cáo kênh 1 lần. Gate 2 (SPEC §10): bằng chứng thật đẩy vấn đề lên `source='research'`; chỗ trống vẫn suy luận nhưng gắn nhãn.

### Hợp đồng S2 — Nước đi (`gen_moves` → ứng viên; `commit_move` → `big_ideas`)
Gate 1 ĐÓNG (floor-test sống): **KHÔNG thư viện nước đi theo ngành**. "Thư viện" = 1 prompt-khung bất biến (JTBD Four-Forces × 5 bậc + phanh + grounding) + rubric mỏng. gen_moves = 2-call **Sonnet nháp → Opus tối-ưu**.

| Khoá | Kiểu | Consumer | Producer | Khớp / degrade | Status |
|---|---|---|---|---|---|
| `audience_id` (input) | `aud_<8hex>` | `gen_moves`/`commit_move` `_find_aud_problem` | **S1** `battle_map.audiences[].id` | **seam đứt phải NỔ**: id không thấy → `error`, KHÔNG im | ✅ build |
| `problem_id` (input) | `prob_<8hex>` | `gen_moves`/`commit_move` | **S1** `…problems[].id` | id không thấy trong tệp → `error` | ✅ build |
| `TaskType.CAMPAIGN_MOVES_DRAFT` | enum | `gen_moves` call-1 | routing `[SONNET, HAIKU]` (`llm_router`) | Sonnet nháp; Haiku degrade. Chuỗi CHỦ Ý bám Anthropic | ✅ build |
| `TaskType.CAMPAIGN_MOVES_OPTIMIZE` | enum | `gen_moves` call-2 | routing `[OPUS, SONNET]` | Opus tối-ưu; **Opus hỏng → degrade Sonnet**; optimize ra rác → dùng bản nháp (`optimized=False`) | ✅ build |
| `Provider.ANTHROPIC_OPUS` | provider | router | `_call_anthropic_opus` (model `CLAUDE_OPUS_MODEL=claude-opus-4-8`) | key = `ANTHROPIC_API_KEY` (chung Sonnet/Haiku); cắt giữa câu → raise → failover | ✅ build |
| nước đi `.bac` | enum 5 slug `van_hanh\|chao_hang\|phan_phoi\|kich_hoat\|noi_dung` | thẻ FE · `commit_move` | LLM chọn, `_norm_bac` chuẩn hoá (nhận số/nhãn/EN) | **KHOÁ CỨNG**: không suy được bậc → nước đi bị **vứt** (`_sanitize_move`→None) | ✅ build |
| nước đi `.phanh` / `.phanh_loai` | str / enum 4 | thẻ FE (⚠️ + dấu vết nắn) | LLM (khung Tầng 4) | `phanh` chỉ khi sai gây HẠI không lùi; principle-vi-phạm → LLM VỨT (không nắn) | ✅ build |
| `luc_chan` + `.xem_ky{…}` | str + object 6 mục | FE Xem-kỹ | LLM (khung) | parse vá `_parse_first_json` (raw_decode, bỏ đuôi rác); max_tokens 6000 | ✅ build |
| moves (output) | list ≤3 | **FE giữ tới khi chốt** | `gen_moves` | **KHÔNG persist** (ứng viên) — chốt mới ghi; `bac_spread<2` → note cảnh báo dồn bậc | ✅ build |
| `big_ideas[].{is_campaign,mechanic,snapshot}` | bool/obj/obj | S3 (việc→lịch) · `_build_campaign_bands` | `commit_move` | `snapshot` = chụp `audience_id+problem_id+text+type+stage` lúc chốt → không trôi khi bản đồ đổi; `grid/window` rỗng = DRAFT (S3 wire lịch) | ✅ build |
| `bizMoveMeta` | dict (bac/phanh_loai labels) | FE thẻ (nhãn 5 bậc + 4 phanh) | `biz_data` (tĩnh, KHÔNG đọc DB) | tách khỏi bizBigIdeas (chốt) | ✅ build |

> **Phanh 4-loại (SPEC §2) = rubric trong prompt, KHÔNG deterministic guard:** principle → VỨT (tuyệt đối); archetype sai-ý-đồ → giữ động tác đổi ý đồ + `nan_tu`; vượt nguồn lực → thu nhỏ liều; chọi chẩn đoán → chỉ nắn nếu trúng nghẽn thật khác. Enforce generatively (floor-test chứng: SCAFFOLD tôn trọng cấm, FREE phá) + Opus tối-ưu re-check. Guard cứng cho principle-violation = **nợ đã biết** (phát hiện NLP mong manh, để sau).
> **FE nợ:** S2 mới là BE (như S1 = BE PR #43). Trang Bản đồ (S1 FE) + UI thẻ nước đi/Xem-kỹ/Chốt (S2 FE) là slice sau — cần S1 FE làm chỗ chọn tệp+vấn đề để gọi `/api/biz/moves/gen`.

## Khi nào chạy cổng này
- **Brief-time (mọi function):** điền mục "Phân tích mối nối" (Tốc độ 2) — dòng hợp đồng + addendum. Không có = brief chưa xong.
- **Mỗi slice K***: chạy `py brain/_check.py` (Lớp 1) + rà Lớp 2 cho khoá slice đụng tới.
- **Mỗi slice tiêu thụ/đẻ khoá xuyên component** (P*, D*, route, FE): rà 4 câu Hiến pháp + cập nhật Sổ hợp đồng; nếu tự suy trạng thái → áp Luật derived-state.
- Kết quả rà dán vào review CTO của slice (giống self-review của builder). Cổng PASS = Hiến pháp qua hết.
