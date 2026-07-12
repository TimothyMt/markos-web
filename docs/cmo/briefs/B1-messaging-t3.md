# Brief B1 — T3 Thông điệp: nối proof vào máy viết + luật dựng trụ (BACK-END)

> **Mục tiêu:** thi hành Bộ luật T3 (`CHAIN-V2-KIENTRUC.md`, mục "Bộ luật T3 THÔNG ĐIỆP") ở tầng back-end.
> Sau brief này: (a) máy viết bài **đọc được proof** của từng trụ và **vặn giọng** theo có/không proof —
> trụ có proof viết giọng khẳng định + lồng bằng chứng, trụ rỗng proof viết giọng quan điểm **cấm claim**;
> (b) khi Max dựng Thông điệp: cốt lõi có **thế đối lập**, trụ phải qua **2 cửa**, Max **tự đào proof** từ
> context, hygiene fact không lên trụ.
> **Phạm vi B1 = BACK-END ONLY.** Chip UI + dòng gợi ý proof-7-ngày → brief B1-UI riêng (chưa làm).
>
> **Đọc trước:** `docs/cmo/briefs/CHAIN-V2-KIENTRUC.md` (kiến trúc + bộ luật) · `webapp/business.py`:
> `_messaging_anchor_from` (~2621), `gen_messaging` (~2645), `_MSG_ADAPT_CORE` (~2572),
> `_MSG_ADAPT_PILLARS` (~2581), `_norm_messaging` (~2594).
> **Branch:** nhánh mới từ `main` (vd `feature/b1-messaging-t3`) · PR về `staging` · KHÔNG tự merge.

## ⚠️ Va chạm với brief D1-F2 (đọc trước khi sửa `gen_messaging`)
- **D1-F2** (`D1-F2-messaging-seam.md`, branch `feature/consolidate`) chèn 2 anchor định vị vào chuỗi
  **`user`** của `gen_messaging` — khúc ráp bắt đầu `user = (f"# Ngành\n{industry}..."` (~2694).
- **B1** chỉ sờ chuỗi **`system`** (2 hằng `_MSG_ADAPT_*`) + hàm **`_messaging_anchor_from`** (hàm KHÁC).
- → Hai brief chia đường sạch. **B1 TUYỆT ĐỐI KHÔNG đụng khúc `user=`** (đất D1-F2). Ai merge sau rebase,
  không xung đột logic. Nếu thấy D1-F2 đã merge vào base của mình → giữ nguyên anchor của họ, chỉ sửa phần B1.

## Bối cảnh — bằng chứng đã soi (không đọc chay)
- **Ô proof đang là ô trang trí.** `_messaging_anchor_from` (2621) — text nền chèn vào MỌI prompt gen bài —
  chỉ nhả `territory` mỗi trụ (dòng ~2629), **bỏ cả `angle` lẫn `proof`**. Trong khi `_norm_messaging`
  (2605-2606) đã LƯU đủ `angle`[:220] + `proof`[:180]. → Dữ liệu proof nằm trong DB nhưng máy viết bài
  không bao giờ thấy → mọi trụ ra bài giọng như nhau, không phân biệt "có bằng chứng thật" vs "chỉ quan điểm".
- **Luật dựng trụ** nằm ở 2 hằng prompt (`system`): `_MSG_ADAPT_CORE` (dựng MÁI/cốt lõi, 2572) và
  `_MSG_ADAPT_PILLARS` (dựng TRỤ + giọng, 2581). Ô nhập proof phía FE đã có sẵn (`app.js:1711`).

---

## MŨI ① — `_messaging_anchor_from`: máy viết bài đọc proof + chỉ dẫn vặn giọng (1 commit)

**File:** `webapp/business.py`, hàm `_messaging_anchor_from` (~2621). **Đây là miếng quan trọng nhất của B1.**

**ĐỌC:** `extra.messaging` (producer = `gen_messaging`/`save_messaging`; đã live). **GHI:** không — hàm trả string.
**Derived-state?** Không. **Degrade:** messaging rỗng → return `""` như cũ (giữ nguyên guard dòng 2624).

Hiện tại vòng lặp trụ chỉ gom `territory`. Sửa để **mỗi trụ nhả kèm `angle` và `proof` (nếu có)**, và
thêm 1 khối chỉ dẫn giọng để máy viết biết vặn:

- Trụ **CÓ proof** → bài giọng **khẳng định**, được phép **lồng bằng chứng đó** vào bài.
- Trụ **RỖNG proof** → bài **VẪN lên sóng** nhưng giọng **quan điểm/kể chuyện**, **CẤM claim** (không được
  khẳng định điều chưa chứng minh, không bịa số/chứng cứ).

Gợi ý hình dạng (không bắt buộc từng chữ — giữ tinh thần, tiếng Việt tự nhiên; KHÔNG tăng độ dài vô ích):
```python
    # thay đoạn gom territory-only bằng: mỗi trụ 1 dòng có angle + trạng thái proof
    prows = []
    for p in (m.get("pillars") or [])[:5]:
        terr = (p.get("territory") or "").strip()
        if not terr:
            continue
        ang = (p.get("angle") or "").strip()
        prf = (p.get("proof") or "").strip()
        head = f"• {terr}" + (f" — {ang}" if ang else "")
        if prf:
            prows.append(f"{head}\n  [CÓ BẰNG CHỨNG: {prf}] → giọng KHẲNG ĐỊNH, được lồng bằng chứng này vào bài.")
        else:
            prows.append(f"{head}\n  [CHƯA CÓ bằng chứng] → giọng QUAN ĐIỂM/kể chuyện; CẤM claim/khẳng định điều chưa chứng minh.")
    if prows:
        lines.append("Trụ thông điệp (lãnh địa + góc nói + cách vặn giọng theo bằng chứng):\n" + "\n".join(prows))
```
- **GIỮ NGUYÊN** phần `core`, `focus`, `voice do/dont` phía trước/sau (dòng 2627-2638) — chỉ thay khối trụ.
- **GIỮ** guard đầu hàm (2624) và header khối cuối (2641). Cập nhật câu mô tả header nếu cần cho khớp
  (vd nói rõ "bài bám cốt lõi/giọng + vặn theo bằng chứng từng trụ").
- Hàm này được cả `gen_calendar_post` (2780) và các chỗ gen bài khác dùng → sửa 1 chỗ, mọi bài hưởng.

---

## MŨI ② — 2 hằng prompt dựng Thông điệp: cốt lõi có thế đối lập · trụ 2 cửa · Max đào proof (1 commit)

**File:** `webapp/business.py`, hằng `_MSG_ADAPT_CORE` (~2572) + `_MSG_ADAPT_PILLARS` (~2581).
Chỉ sửa **text prompt** (không đổi schema JSON, không đổi code Python quanh nó).

### ②a — `_MSG_ADAPT_CORE` (dựng cốt lõi/MÁI): thêm luật THẾ ĐỐI LẬP
Cốt lõi hiện chỉ yêu cầu "1 câu định vị ≤14 từ". Thêm luật:
- Cốt lõi = **1 ý, có THẾ ĐỐI LẬP** (nói rõ mình chống lại/khác điều gì). Chọn kẻ thù 1 trong 4 dạng
  theo ngành + khẩu vị founder: **(a)** cách làm phổ biến của ngành · **(b)** thói quen cũ của khách ·
  **(c)** một lầm tưởng · **(d)** chính vấn đề khách gặp.
- **Ngành nhạy cảm/luxury** → ưu tiên (b)(c)(d), **KHÔNG bắt buộc đối đầu đối thủ** trực diện.
- Giữ nguyên schema output (`core` + `taglines`) và luật "≤14 từ, truy vết USP, không bịa".

### ②b — `_MSG_ADAPT_PILLARS` (dựng TRỤ + giọng): 2 cửa + đào proof + 3 bậc-nhẹ
Thêm vào phần luật dựng trụ (giữ nguyên schema `pillars[]`+`voice`, giữ luật "linh hoạt 2-5, không ép 3"):

1. **Trụ phải qua 2 CỬA:**
   - **Cửa 1 (bằng chứng-24h):** tự hỏi *"Khách bảo 'chứng minh đi' — mình đưa được CÁI GÌ cho họ XEM
     trong 24h?"* Có thứ đưa được → điền vào ô `proof`.
   - **Cửa 2 (đẻ ≥10 bài):** lãnh địa này viết đều mỗi tuần 2-3 tháng **không cạn ý** (đẻ được ≥10 bài
     không lặp) mới là TRỤ. Nếu rõ ràng cạn (nói 1-2 bài là hết) → đó là **hygiene fact** (giá, vị trí,
     "máy mới") → **KHÔNG lên trụ**, chỉ là chi tiết rắc vào bài. *(Nghi ngờ thì GIỮ — chỉ gạt xuống fact
     khi trụ rõ ràng cạn, tránh loại oan trụ tốt.)*
2. **Max TỰ ĐÀO proof từ context** (synthesis/tactical/customer_insight/USP/đặt cược đã có trong prompt) —
   điền ô `proof` khi tìm thấy bằng chứng THẬT. Ưu tiên theo **5 hạng proof** (mạnh → yếu):
   số vận hành > giấy tờ/chứng nhận > bằng chứng từ khách > quy trình nhìn thấy được > cam kết chịu rủi ro.
   🔴 CHỈ dùng bằng chứng có THẬT trong context — **KHÔNG bịa proof/số**. Không thấy → để `proof` = `""`.
3. **Trụ rỗng proof VẪN hợp lệ** (ra trụ bình thường, giọng quan điểm) — proof rỗng KHÔNG phải lý do loại trụ.

- **KHÔNG** đưa vào B1: bậc "mãi không có proof → Max đề xuất ĐỔI trụ" (cần tín hiệu nhiều đợt) và
  PROOF-QUEST 30 ngày → backlog, brief sau.
- **KHÔNG** tạo cấu trúc dữ liệu "fact sheet" — ở B1 fact sheet chỉ là **luật prompt** (hygiene fact không
  lên trụ). Ống fact-sheet thật → backlog.

---

## Verify (dán output thật vào commit)
```bash
python3 -c "import webapp.business"                 # (webapp.api có thể thiếu starlette trong sandbox — khai rõ nếu vậy)
python3 -c "import webapp.business as B; print('anchor OK', callable(B._messaging_anchor_from))"
python3 -c "import webapp.business as B; assert 'ĐỐI LẬP' in B._MSG_ADAPT_CORE or 'đối lập' in B._MSG_ADAPT_CORE.lower(); assert 'cửa' in B._MSG_ADAPT_PILLARS.lower(); print('prompt rules OK')"
```
- **Không sờ FE** ở B1 → không cần mirror standalone / node --check trong brief này.
- Không có key/DB → verify **tĩnh** (compile/import + string có mặt). Hành vi runtime (giọng vặn theo
  proof; Max điền proof đúng) **chờ chạy thật** với 1 profile có Thông điệp — khai rõ trong self-review.

## Self-review report (dán vào commit)
```
[B1] T3 back-end — máy viết đọc proof để vặn giọng + luật dựng trụ (thế đối lập · 2 cửa · Max đào proof)
Đã check: import OK · _messaging_anchor_from nhả angle+proof+chỉ dẫn giọng · 2 hằng prompt có luật mới ·
          giữ schema messaging dict + degrade "" · KHÔNG đụng khúc user= (đất D1-F2)
Chưa chắc (chờ runtime): Max có điền proof đúng 5 hạng không · giọng "cấm claim" khi rỗng proof có được
          máy viết tôn trọng không → soi output bài thật rồi mới siết thêm, đừng sửa mù
```

## Không làm
- KHÔNG đụng khúc ráp `user=` của `gen_messaging` (đất brief D1-F2).
- KHÔNG đổi schema `messaging` dict / `_norm_messaging`, KHÔNG đổi schema DB.
- KHÔNG làm chip UI, dòng gợi ý proof-7-ngày (→ brief B1-UI), KHÔNG làm bậc "đổi trụ" / PROOF-QUEST.
- KHÔNG tạo cấu trúc "fact sheet" mới (chỉ luật prompt).
- KHÔNG bịa số/proof trong prompt (giữ luật cấm bịa sẵn có).
- Mỗi mũi 1 commit · push nhánh riêng · PR về `staging` · **dừng chờ review, KHÔNG tự merge.**
