"""WebPay đứng đầu trang Kết nối, và link MCP của nó được giữ như mật khẩu.

    python tests/run.py webpay_ket_noi      (KHÔNG mạng)

Link MCP của WebPay mang khoá ngay trên đường dẫn (https://webpay.vn/mcp/wpm_...), vì MCP không có
chỗ cho header. Lưu trần nó vào ô `url` của mcp_servers.json hay trả nó ra frontend là lộ khoá vào
danh sách học viên và quyền lập khoản thu của shop.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import json
import os
import sys
import tempfile

os.environ["NAOTA_STATE_DIR"] = tempfile.mkdtemp(prefix="naota-webpay-")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import mcp_catalog  # noqa: E402
import mcp_store  # noqa: E402

fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(them) + "]") if them and not cond else ""))
    if not cond:
        fails.append(name)


KHOA = "wpm_" + "a1B2c3D4e5F6g7H8i9J0kLmN"
LINK = "https://webpay.vn/mcp/" + KHOA

goc = json.loads((ROOT / "system" / "mcp-catalog.json").read_text(encoding="utf-8"))["connectors"]
check("WebPay là connector đầu tiên của catalog", goc[0]["id"] == "webpay", goc[0]["id"])
con = mcp_catalog.get("webpay")
check("catalog nạp được WebPay", bool(con))
check("logo WebPay có thật trong dashboard", (ROOT / "dashboard" / "logos" / "webpay.svg").exists())

pub = {c["id"]: c for c in mcp_catalog.public_catalog()}
check("bản cho UI đánh dấu WebPay ghim đầu", pub["webpay"]["pin"] is True)
check("connector khác không bị ghim", not any(c["pin"] for k, c in pub.items() if k != "webpay"))
check("mặc định chỉ đọc", pub["webpay"]["default_perm"] == "readonly")

tm = con["tool_meta"]
for t in ("tao_link_thu_tien", "thu_tien_ngay", "bat_dau_thu_dinh_ky"):
    check(f"{t} (lập khoản thu) chỉ chạy ở Toàn quyền", t in tm["danger"])
check("tool đọc không lẫn tool tạo", not [t for t in tm["read"] if t.startswith(("tao_", "thu_", "bat_dau"))])

# Ráp link: nhận cả link đầy đủ lẫn mỗi khoá, từ chối địa chỉ lạ.
bu = lambda v: mcp_catalog.build_url(con, {"mcp_link": v})  # noqa: E731
check("link đầy đủ giữ nguyên", bu(LINK) == LINK, bu(LINK))
check("link app.webpay.vn cũng nhận", bu("https://app.webpay.vn/mcp/" + KHOA) == "https://app.webpay.vn/mcp/" + KHOA)
check("dán mỗi khoá thì ghép vào webpay.vn", bu(KHOA) == LINK, bu(KHOA))
check("khoảng trắng và gạch chéo cuối được cắt", bu("  " + LINK + "/ ") == LINK)
check("địa chỉ lạ bị từ chối (không gửi khoá tới chỗ lạ)", bu("https://evil.example/mcp/" + KHOA) == "")
check("tên miền giả dạng bị từ chối", bu("https://webpay.vn.evil.example/mcp/" + KHOA) == "")
check("đuôi có ký tự lạ bị từ chối", bu(LINK + "?x=1") == "" and bu("https://webpay.vn/mcp/../admin") == "")
check("ô trống thì không đẻ URL", bu("") == "")

# Thêm kết nối: link không đúng thì báo lỗi, đúng thì cất mã hoá, không lưu trần.
cid, err = mcp_store.add_connection("webpay", {"fields": {"mcp_link": "https://evil.example/x"}})
check("link sai bị từ chối khi thêm", cid is None and bool(err), err)
cid, err = mcp_store.add_connection("webpay", {"fields": {"mcp_link": LINK}})
check("link đúng thêm được", bool(cid) and not err, err)
tho = mcp_store.STORE.read_text(encoding="utf-8")
check("khoá KHÔNG nằm trần trong mcp_servers.json", KHOA not in tho)
check("bản trả ra frontend không có URL", KHOA not in json.dumps(mcp_store.list_connections()))
r = next(x for x in mcp_store.resolved(enabled_only=False) if x["id"] == cid)
check("lúc chạy dựng lại đúng URL từ ô đã mã hoá", r["url"] == LINK, r.get("url"))
check("kết nối mới mặc định chỉ đọc", mcp_store.get_connection(cid)["perm"] == "readonly")

# Sửa kết nối: gửi kèm url cũng không làm khoá rơi ra file.
mcp_store.update_connection(cid, {"url": LINK, "label": "Shop A"})
check("sửa kết nối không ghi URL trần", KHOA not in mcp_store.STORE.read_text(encoding="utf-8"))
moi = "wpm_" + "Z" * 24
mcp_store.update_connection(cid, {"fields": {"mcp_link": moi}})
r = next(x for x in mcp_store.resolved(enabled_only=False) if x["id"] == cid)
check("dán khoá mới thì URL chạy theo khoá mới", r["url"] == "https://webpay.vn/mcp/" + moi, r.get("url"))

# Trang Kết nối vẽ thẻ ghim trước thẻ Tự thêm MCP.
js = (ROOT / "dashboard" / "console.js").read_text(encoding="utf-8")
i_pin = js.find("catSolo(cat).filter(c => c.pin).map(catalogCard)")
i_custom = js.find("catalogCard(byId.custom)")
check("lưới Sẵn có vẽ thẻ ghim trước thẻ Tự thêm MCP", 0 <= i_pin < i_custom, (i_pin, i_custom))
check("thẻ ghim không vẽ hai lần", "catSolo(cat).filter(c => !c.pin).map(catalogCard)" in js)

print()
if fails:
    print(f"{len(fails)} FAIL")
    sys.exit(1)
print("ALL OK")
