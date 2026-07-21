# LAUNCH-READINESS — quy trình hoàn thiện Max để nhận user

> **Đề bài (từ founder):** Max chia làm *BE/FE user dùng* + *trí tuệ phía sau*. Muốn **hoàn thiện để nhận user vào dùng trước**; trí tuệ **vừa đủ** để user dùng được — KHÔNG build trọn bộ não 6 miền CMO ngay.
> **2 quyết định đã chốt:** ① loại user v1 = **self-serve công khai** · ② phạm vi v1 = **golden path ①→⑦ + Báo cáo kênh**.

## 0. Hiểu đúng "trí tuệ vừa đủ"
Max có ~30 trang trên nav, nhưng chỉ **1 chuỗi** là lõi giá trị đã nối data thật end-to-end. "Vừa đủ" = làm **đúng chuỗi này** chạy mạch lạc + chất lượng đủ dùng + mối nối không đứt, rồi **giấu/gác mọi thứ còn mock**. Không phải lấp trọn cột chiến lược 6 miền (đó là `00-PLAN.md`, tầm xa hơn).

**Golden path v1:**
```
① Hồ sơ → ② Nghiên cứu (Thị trường·Đối thủ·Khách·Giá·SWOT)
   → ③ Định vị & Chiến lược (Spine) → ④ Thông điệp (cốt lõi+trụ+giọng)
   → ⑤ Ma trận & Chiến dịch → ⑥ Lịch nội dung → ⑦ Gen bài  (+ Báo cáo kênh)
```

## 1. Ảnh chụp trạng thái (verify trong code, 2026-07-21)

### 1.1 Golden path — nối thật
- Routes đủ ở `webapp/api.py` (`/api/biz/*`), `biz_data()` đẩy real keys: `bizSpine`, `bizMessaging`, `bizBrandVoice`, `bizKeyIdeas`, `bizContentMatrix`, `bizCalendarBriefs`, `bizGaps`, `bizBetChoices`…
- FE: các trang `dossier/market/competitor/customer/pricing/swot/strategy/message/voice/tactical/direction/matrix/calendar` + `adscopy/inbox/sequence` (gọi `/api/biz/content/asset`, bám hồ sơ+chiến lược) + `channelreport` (social audit ScrapeCreators+LLM) đều đọc data thật.

### 1.2 Nợ chất lượng trên path (phải nâng — "vừa đủ")
- `spine.positioning` + `messaging.trụ` output **yếu** → gate mọi bài phía sau (định vị/thông điệp lệch thì content lệch hết).
- Logic **rải bài lên lịch** mỏng (cần window + lưới tầng×kênh→ngày theo phễu + neo cao điểm + nhịp + không dồn).
- **Repoint `voice`** (Pha 2): trang `voice` đọc `user_brand_voice` (CHỈ bot ghi — `webapp/` không có đường ghi từ web) → user self-serve luôn ra số giả "Đạt 92%". Đã đẩy xuống "Sắp có" ở Pha 0; Pha 2 repoint sang `messaging.giọng` (web sinh thật) rồi đưa lại lên ② Nền thương hiệu.
- FE **Báo cáo kênh** còn stub xấu → làm lại theo SocialLens (xem `docs/web/social-audit-notes.md`).

### 1.3 Mock / chờ FB Ads (GIẤU khỏi v1 — giữ code)
`voice` · `overview` · `brandhealth` · `adsanalytics` · `optimizer` · `spy` · `schedule` · `accounts` · `reports` — render từ mock/số giả (`data.js`: "Highlands Coffee", "3,09x→3,6x", "1.284 user"; `voice`: "Đạt 92%"). Phần lớn chờ auto-pull FB (pending). `admin` = operator-only, ẩn khỏi nav user.

### 1.4 ⚠️ Chốt chặn lớn nhất: CHƯA có đăng ký/đăng nhập
`pick_user_id()` (`webapp/business.py`) chọn user qua **query param → env → user active gần nhất**. Không login, không session; `user_id` truyền qua URL = **ai cũng đổi được để xem data người khác**. Max hiện là app **1 người vận hành**, KHÔNG phải multi-tenant.
→ "Self-serve công khai" kéo theo khối việc **không phải trí tuệ** mà là **sản phẩm/hạ tầng** — và đây là phần **nặng + rủi ro nhất**:
- Đăng ký/đăng nhập + session.
- Cách ly dữ liệu theo user (bỏ `user_id` khỏi query param, buộc từ session).
- **Chặn quota LLM** (`token_quota` đang *hiển thị*, chưa chắc *chặn* → public = chi phí LLM không đáy).
- Chống lạm dụng.

## 2. Sequencing (founder chốt 2026-07-21): auth-first, KHÔNG beta shim
Mốc muốn có user thật = **tuần tới / trong tháng**, và **không dựng khâu beta cấp-tài-khoản-tay** — user vào bằng **auth thật** ngay. → Luồng B (đăng nhập + đa tenant + chặn quota) là **đường tới hạn near-term**, kéo lên làm sớm chứ không gác cuối. Không có "beta kín" trung gian: xong auth + cổng Pha 4 là mở.
→ Hệ quả: mọi thứ build từ giờ **không được giả định `user_id` từ query param** — viết sẵn theo hướng user-từ-session để khỏi đập lại khi cắm auth.

## 3. Bốn luồng việc
- **A · Chuỗi golden path mạch lạc + chất lượng** *(trí tuệ vừa đủ — lõi)*
- **B · Đăng nhập + đa người dùng + chặn quota** *(hạ tầng — blocker của public; dài nhất, khởi động sớm)*
- **C · Onboarding self-serve + chống lỗi** *(nặng vì công khai)*
- **D · FE Báo cáo kênh** *(đã đưa vào phạm vi v1)*

## 4. Năm pha có cổng

| Pha | Làm gì | Luồng | Cổng qua pha |
|---|---|---|---|
| **0 · Chốt phạm vi** | Trim nav còn golden path + gom mock vào "Sắp có"; ẩn `admin`; bỏ footer `demo dữ liệu mock`; sửa label brand | A | User chỉ thấy màn dùng được, không màn nào ra số bịa · `node --check web/app.js` |
| **1 · Đi bộ end-to-end** | Nhập 1 business thật, đi ①→⑦, soi từng mối nối theo `WIRING.md`, ghi chỗ đứt | A | Đi trọn chuỗi không kẹt; mỗi output nuôi bước kế |
| **2 · Nâng nút thắt + lịch + FE báo cáo** | Nâng `gen_positioning_from_usp` + `gen_messaging`; logic rải lịch; sửa empty-state `voice`; **làm lại FE Báo cáo kênh** | A,D | EVAL (`EVAL.md`): định vị/thông điệp/bài đọc như CMO thật |
| **3 · Auth + đa tenant + onboarding** | Đăng ký/đăng nhập + session; **cách ly `user_id` khỏi query param**; **chặn quota**; empty-state + nudge "1 việc nên làm"; degrade khi LLM lỗi/rate-limit | B,C | User lạ tự đi từ đăng ký → bài đầu tiên, không kèm; không xem được data người khác |
| **4 · Cổng phát hành** | `import webapp.business, webapp.api` + `node --check` xanh; đi bộ Pha 1 pass; tải thử N user; **mở public** (không beta shim) | tất cả | Cổng xanh → gạt công tắc self-serve |

**Thứ tự (sau khi founder chốt auth-first):** Pha 0 (xong) → Pha 1 walk → rồi **3 luồng chạy tới cổng Pha 4**:
- **Luồng B · Auth (tới hạn)** = kéo lên NGAY sau Pha 1, làm nền trước (Pha "3" auth không gác cuối nữa) — vì user vào bằng auth thật, không có beta.
- **Luồng A · Quality** (positioning/messaging + rải lịch + repoint voice) — song song, vì user tháng này sẽ thấy output.
- **Luồng D · FE Báo cáo kênh + onboarding/empty-state** — song song.
Ba luồng độc lập file (B=backend/session · A=prompt · D=FE) → dispatch song song được. **Không giả định `user_id` từ query** ở bất kỳ code mới nào.

**Phân vai (theo CLAUDE.md):** việc cơ học/nhỏ (Pha 0) Claude tự làm; slice lớn có mối nối (auth, gen chất lượng, FE báo cáo) → brief mục tiêu cho Cline, Claude review, merge qua `staging`.

## 4b. Luồng B — Thiết kế Auth (founder chốt 2026-07-21, grill lần lượt)
Verify: `users` KHÔNG có cột email/mật khẩu/sub (chỉ `user_id BIGINT` = Telegram ID cũ, `name`, `token_quota/used`, `plan`); chưa có `SessionMiddleware`; có sẵn pattern `/oauth/fb/callback` + `upsert_user` find-or-create.

**4 quyết định:**
1. **Provider = Google OAuth** (v1). Nhanh, ít hạ tầng; FB "tưởng sẵn" là ảo — FB OAuth repo là scope ads, login-danh-tính cần app-review + có thể thiếu email. Nối FB-ads sau vẫn là OAuth tách biệt dù login bằng gì.
2. **Danh tính = bảng `auth_identities(provider, external_id, user_id)` riêng** — **NỚI LUẬT "không thêm bảng"** cho auth (carve-out có chủ ý khỏi CLAUDE.md: auth là hạ-tầng-nền-móng, không phải config; sai thì đắt gỡ). Con trỏ external_id→user_id ổn định → đa-provider + link tài khoản + xoay OAuth client về sau đều gọn. (Loại A hash-tất-định vì hàn danh tính vào Google; loại web_users.uid vì dính 2-schema.)
3. **Session** = cookie httpOnly ký (SessionMiddleware / JWT), chứa `user_id`. **Cách ly (giết blocker §1.4):** `pick_user_id` đọc từ session, **BỎ query param**; không session → 401. Đụng xuyên `api.py`.
4. **Không freemium — trả phí từ đầu; access do ADMIN mở qua dashboard.** Default-deny: user mới login Google → chờ admin kích hoạt (cấp quyền + quota). **Chặn quota cứng** trước mỗi LLM call (van chi phí). Dùng hạ tầng sẵn (`set_quota`/`add_quota`) → **`admin` thành dashboard cấp quyền THẬT** (nay mock) — vẫn operator-only, không vào nav user. **Sửa Pha 0:** admin không chỉ "giấu" mà là hạng-mục build của Luồng B.

5. **Thanh toán v1 = THỦ CÔNG** (chốt): thu tiền offline, admin bật quyền qua dashboard; **KHÔNG dựng billing tự động ở v1** (Stripe/VNPay để sau).
**Cần đo:** cost/1 lần chạy trọn chuỗi (ước lượng tĩnh từ `max_tokens` các LLM call) → admin biết cấp quota bao nhiêu.

## 5. Nhật ký pha
- **Pha 0 — XONG + đã grill (2026-07-21).** Trim nav còn golden path; nhóm "Sắp có" (soon:true) cho trang mock; ẩn `admin`; bỏ footer "demo dữ liệu mock"; label brand → "AI CMO cho founder Việt". Grill ra 2 chỉnh: (1) **`voice` → "Sắp có"** (verified: web không ghi được brand_voice → luôn số giả); (2) **auth-first, bỏ beta shim** (user vào tháng này bằng auth thật). Verify `node --check` + import backend xanh; chưa commit.
- **Pha 1 — XONG walk tĩnh (2026-07-21).** Trace seam golden path theo WIRING (producer/consumer khóa `intake_extra`). Kết quả:

### Bản đồ seam (mỗi bước nuôi bước kế?)
| Seam | Trạng thái | Ghi chú |
|---|---|---|
| Mọi khóa `intake_extra` (spine/messaging/key_ideas/content_matrix/big_ideas/calendar_posts/funnel_map…) | ✅ có producer, khớp tên `biz_data` | Seam bậc-1 (tên khóa) PASS toàn bộ |
| ③ Spine → ④ Messaging | ✅ gate cứng | `gen_messaging` đòi synthesis/tactical, thiếu → lỗi rõ "Cần Chiến lược trước" |
| ④ Messaging → ⑤ Matrix | ✅ **mẫu mực** | `gen_content_matrix` đọc `messaging.pillars` theo `territory`, degrade rõ, `_match_pillar` ép trụ-lạ về trụ hợp lệ, chống cụt-im-lặng |
| ④ Messaging → ⑥ Calendar | 🟡 **drift + trộn danh tính** | Calendar NỀN ưu tiên `content_matrix` (coherent) → rhythm → `campaign_plan` pillars (degrade). Nhưng danh tính trụ cho bài đã lưu giải qua `campaign_plan` pillars (name/`_pillar_id`) ≠ `messaging.pillars` (territory) → `pillarId` bài lưu có thể miss → title fallback "Bài brand" |
| ⑥ Calendar nội tại | 🟡 | rải bài logic mỏng (nợ đã ghi [[calendar-post-distribution-logic]]); `campaign_plan` thiếu synthesis → return `{}` IM (FE giữ **mock**) |
| ⑥ → ⑦ Gen bài | ✅ | `_messaging_anchor_from` bơm core+trụ+giọng-theo-proof vào mọi bài → **coherence nội dung giữ** kể cả khi khung lịch lệch |
| Báo cáo kênh | 🟡 | BE thật, FE stub |

### Phát hiện đầu bảng
1. **2 mô hình trụ song song** (seam gốc): `messaging.pillars {icon,territory,angle,proof}` (danh tính = chuỗi territory; dùng bởi matrix/tracks/gen-anchor) vs `campaign_plan`/`pillars_locked {id,name,role}` (danh tính = `_pillar_id`; dùng bởi calendar/normalize). → cùng bắt nguồn synthesis nhưng 2 LLM-call, 2 shape, có thể lệch. **Content coherence vẫn giữ** (gen anchor); **khung lịch + title bài lưu** mới là chỗ lệch.
2. **Mìn `_pillar_id`**: đọc `p.get("name")` — messaging pillar KHÔNG có `name` (chỉ territory) → nếu ai đó nối messaging.pillars thẳng vào calendar, mọi trụ ra cùng id `"n_pillar"` (đụng độ). Hiện CHƯA nổ (chỉ gọi trên campaign_plan pillars), nhưng là bẫy khi hợp nhất.
3. **Empty → mock** (cross-cutting, launch-trust): trang thiếu data thật render **mock** (calendar {} → FE giữ mock; ads/analytics số cứng). Với self-serve công khai, user mới thấy số bịa. → Pha 3 (onboarding) phải thay mock bằng empty-state thật.

### Verdict cổng Pha 1
**Chuỗi ĐI ĐƯỢC, không kẹt cứng** — mọi bước có gate/degrade, không dead-end. "Mỗi output nuôi bước kế": ✅ tới ⑤; **⑥ Calendar mang nợ** (trộn danh tính trụ + rải bài mỏng + empty→mock). → **Pha 2 nhận thêm 1 việc gốc: hợp nhất/bridge 2 mô hình trụ** (cho calendar đọc thẳng `messaging.pillars`, hoặc bridge territory↔id 1 lần).

### Chưa walk (honest)
Chi tiết ①→② (research pipeline tạo skill_runs) chưa soi sâu; `tests/test_b22_calendar_source.py` (đã có, chưa đọc) — đối chiếu ở Pha 2; FE modal kênh (nợ [[fv3-calendar-pending-and-channel-format]]).

---

## §6 — Luồng B (Auth self-serve): XÂY XONG (2026-07-21)

Nhánh `feature/auth` (worktree `wt-auth`, cắt từ `origin/staging`). 7 slice, verify từng bước, **0 regression** (19 test cũ vẫn xanh — 4 fail còn lại đã fail sẵn trên staging; +4 test auth mới xanh: `tests/test_auth.py`).

| Slice | Việc | File | Verify |
|---|---|---|---|
| 1 | Bảng `auth_identities` + `web_user_id_seq` (mint user_id web) + module find-or-create (default-deny `pending`) | `supabase_full_schema.sql`, `storage/v2/auth_identities.py` | import OK |
| 2 | Google OAuth (OpenID, httpx thủ công) + SessionMiddleware + secret env | `services/google_oauth.py`, `run_web.py`, `config.py`, `requirements.txt` (+itsdangerous) | route 503/303 khi thiếu creds |
| 5 | **FLIP** `pick_user_id` → đọc session qua contextvar (sentinel `_UNSET` để caller nội bộ/test vẫn tin arg); pure-ASGI `UidContextMiddleware` | `webapp/business.py`, `run_web.py` | test ①② — client user_id **inert** |
| 3+4 | Gate truy cập (`status`≠active→chặn) + **quota cứng** — hook pre/post vào `llm_router.call`; `biz_data` lộ `bizAuthed/bizAuthStatus/bizEmail/bizIsAdmin`, `bizUsers` chỉ cho admin | `tools/llm_router.py`, `webapp/quota.py`, `webapp/business.py` | test ③ — LLM chặn TRƯỚC provider |
| 6 | FE cổng login / "chờ kích hoạt" / "khoá" + logout; client vẫn gửi user_id (inert) → không sửa 40 call-site | `web/app.js`, `web/styles.css` | `node --check` OK |
| 7 | Admin dashboard THẬT (list identity + quota; kích hoạt/sửa-quota/khoá); route `/api/admin/*` gác bằng `ADMIN_EMAILS` | `webapp/api.py`, `webapp/business.py`, `web/app.js` | test ④ — anon/non-admin=403, admin=200 |

**Quyết định build (ngoài 5 quyết định đã grill):**
- Auth CHỈ chạy khi Supabase bật (biz layer vốn Supabase-only) — nhất quán, SQLite dev không cần auth.
- **`status` tách khỏi `token_quota`**: gate truy cập (pending/active/blocked) ≠ ngân sách token — để phân biệt "chờ duyệt" vs "đã duyệt nhưng hết token".
- user_id web mint từ sequence bắt đầu 10^12 (trên dải Telegram cũ ~10 chữ số).

### ⛳ CÒN LẠI trước khi nhận user thật (deploy config, KHÔNG phải code)
1. **Chạy migration Supabase**: apply `webapp/supabase_full_schema.sql` (thêm `auth_identities` + `web_user_id_seq` + DEFAULT trên `users.user_id`) — idempotent, an toàn re-run.
2. **Google Cloud Console**: tạo OAuth Client (Web), set redirect `https://<domain>/auth/google/callback` → lấy `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.
3. **Env production**: `SESSION_SECRET` (bắt buộc, ký cookie), `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` (nếu muốn cố định), `ADMIN_EMAILS`.
4. Deploy → admin đăng nhập → kích hoạt user đầu qua dashboard → thu tiền thủ công (quyết định #5).

### Chưa làm (auth, honest)
- Chưa chạy OAuth end-to-end thật (cần creds Google + Supabase) — chỉ test tới ranh giới (route/guard/gate) offline.
- Nav "Quản trị" vẫn hiện cho non-admin (trang tự chặn + API 403; ẩn nav là việc Pha 0 nhánh khác).
- Chưa đo cost-per-chuỗi để gợi ý quota mặc định (admin tự đặt lúc kích hoạt).

---

## §7 — Backlog còn lại (SẼ LÀM HẾT, làm lần lượt)

> **Luật vận hành (founder chốt 2026-07-21):** mỗi mảnh **grill TRƯỚC khi code** (bày trade-off → user vặn → mới làm). **Việc trivial/cơ học/khó-đảo-ngược-thấp → bỏ qua grill, làm thẳng.** Đằng nào cũng làm hết cả backlog này.

| Mảnh | Thuộc | Việc | Grill? |
|---|---|---|---|
| Onboarding | Pha 3 (mảnh cuối) | Thay trang **mock → empty-state thật** cho user mới; UX chạy-lần-đầu (phát hiện #3 Pha 1: empty→mock ⇒ user mới thấy số bịa) | ✅ có |
| Deploy auth | Pha 3 (bọc) | Apply schema Supabase · Google OAuth creds · env (`SESSION_SECRET`/`GOOGLE_*`/`ADMIN_EMAILS`) · chạy OAuth end-to-end thật | ⏭ trivial phần config; grill nếu phát sinh |
| Nâng messaging/positioning | Pha 2 | `messaging.trụ` + `spine.positioning` yếu ([[messaging-pillars-positioning-quality-debt]]); chặn câu ② chọn-đầu | ✅ có |
| Rải lịch có logic | Pha 2 | window+grid tầng×kênh→ngày theo phễu+neo cao điểm+nhịp ([[calendar-post-distribution-logic]]) | ✅ có |
| Hợp nhất 2 mô hình trụ | Pha 2 (seam gốc) | messaging.pillars (territory) ↔ campaign_plan pillars (id/name) — bridge 1 lần; gỡ mìn `_pillar_id` | ✅ có |
| FE Báo cáo kênh | Pha 2 | BE thật rồi, FE stub xấu → làm lại theo SocialLens ([[social-audit-feature]]) | ✅ có |
| Repoint `voice` | Pha 2 | trang voice → messaging.giọng (nay là "Sắp có") | ⏭ chủ yếu cơ học |
| Cổng phát hành | Pha 4 | gate xanh → gạt công tắc public | ✅ có (checklist) |
</content>
</invoke>
