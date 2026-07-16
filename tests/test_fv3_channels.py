"""Test FV3-4a — Từ điển kênh (CHANNELS 12 kênh + channel_slug/channel_label).

Thuần đồng bộ, KHÔNG cần DB/LLM: import trực tiếp const + helper. (Không đụng gen/save nên khỏi stub storage.)

Chốt đúng phạm vi brief FV3-4a (doc §3.3 Bước 1):
  ① CHANNELS đúng 12 kênh, mỗi kênh có label/aliases/tiers/formats/write_spec; tiers ⊆ (tofu,mofu,bofu).
  ② channel_slug: slug thẳng · nhãn · alias · text LLM lỏng ('Reels 15s'→instagram) ·
     ĐẶC THÙ thắng chung chung ('facebook group'→facebook_group, 'tiktok shop'→tiktok_shop) ·
     lạ → '' · rỗng → ''.
  ③ channel_label: slug → nhãn · slug lạ → ''.

Chạy:  python tests/test_fv3_channels.py   (exit 0 = pass)
"""
import sys, os, types

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

# business.py import nội bộ lazy → import module KHÔNG chạm storage/LLM. Vẫn chặn cứng cho chắc.
for _m in ("storage", "storage.v2", "tools.llm_router"):
    sys.modules.setdefault(_m, types.ModuleType(_m))
import webapp.business as B


def _run():
    res = []
    C = B.CHANNELS
    EXPECT = {"facebook", "facebook_group", "instagram", "tiktok", "tiktok_shop", "shopee",
              "youtube", "zalo_oa", "website_seo", "email", "offline", "kol_pr"}

    # ---- ① cấu trúc từ điển ----
    res += [
        ("① đúng 12 kênh, đúng bộ slug", set(C.keys()) == EXPECT and len(C) == 12),
        ("① mỗi kênh đủ field label/aliases/tiers/formats/write_spec",
         all({"label", "aliases", "tiers", "formats", "write_spec"} <= set(v.keys()) for v in C.values())),
        ("① tiers ⊆ (tofu,mofu,bofu) và không rỗng",
         all(v["tiers"] and set(v["tiers"]) <= {"tofu", "mofu", "bofu"} for v in C.values())),
        ("① aliases/formats là list, write_spec có chữ",
         all(isinstance(v["aliases"], list) and isinstance(v["formats"], list) and str(v["write_spec"]).strip()
             for v in C.values())),
    ]

    # ---- ② channel_slug ----
    cs = B.channel_slug
    res += [
        ("② slug thẳng 'tiktok' → tiktok", cs("tiktok") == "tiktok"),
        ("② nhãn 'TikTok' → tiktok", cs("TikTok") == "tiktok"),
        ("② alias 'fanpage' → facebook", cs("fanpage") == "facebook"),
        ("② LLM lỏng 'Reels 15s' → instagram", cs("Reels 15s") == "instagram"),
        ("② ĐẶC THÙ 'facebook group' → facebook_group (KHÔNG facebook)", cs("facebook group") == "facebook_group"),
        ("② ĐẶC THÙ 'Live bán hàng TikTok Shop' → tiktok_shop (KHÔNG tiktok)",
         cs("Live bán hàng TikTok Shop") == "tiktok_shop"),
        ("② 'Zalo OA broadcast' → zalo_oa", cs("Zalo OA broadcast") == "zalo_oa"),
        ("② lạ hẳn → ''", cs("bồ câu đưa thư") == ""),
        ("② rỗng/None → ''", cs("") == "" and cs(None) == ""),
    ]

    # ---- ③ channel_label ----
    res += [
        ("③ slug → nhãn", B.channel_label("zalo_oa") == "Zalo OA"),
        ("③ slug lạ → ''", B.channel_label("xxx") == ""),
    ]

    return res


def main():
    ok = True
    for name, passed in _run():
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok = ok and passed
    print("FV3-4a channels:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
