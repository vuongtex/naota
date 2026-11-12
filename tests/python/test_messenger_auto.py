"""Messenger automations: auto private reply on comments, follow-ups, contacts out.

    python tests/run.py messenger_auto      (no network: Graph and the contact URL are faked)

Guarded, in order of what would hurt most if it broke:

  1. The contact secret never reaches the dashboard (account view, settings route).
  2. One private reply per person per post: a person commenting three times gets one message; the Page's own
     comments and comments without the keyword get none. A failed send can be retried.
  3. A public reply from the automation stops the A.I. answering the same comment publicly a second time.
  4. Contacts: an email or Vietnamese phone in a message is POSTed once, signed with the secret; a 5xx is retried,
     a 4xx is not, and an undelivered contact is not marked as sent.
  5. Follow-ups: due only after their delay, only once, never past the 24-hour window, and a new message from the
     person restarts the clock.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import asyncio
import os
import sys
import tempfile
import time

os.environ["NAOTA_STATE_DIR"] = tempfile.mkdtemp(prefix="naota-ms-auto-")
os.environ["NAOTA_ALLOWED_HOSTS"] = "testserver"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import channel_accounts  # noqa: E402
import messenger_auto  # noqa: E402
import messenger_bot  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402

_fails = []


def check(name, cond, extra=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(extra) + "]") if extra and not cond else ""))
    if not cond:
        _fails.append(name)


PAGE = "1234567890123"
TOKEN = "EAA" + "t" * 60
APP_SECRET = "c" * 32
SECRET = "s3cr3t-" + "x" * 20
SENT = []
MODE = {"graph": "ok"}


async def fake_post_json(self, client, path, payload):
    SENT.append((path, payload))
    if MODE["graph"] == "fail":
        return {"ok": False, "code": 200, "error": "no permission"}
    return {"ok": True, "recipient_id": "PSID-9", "message_id": "m_1", "id": "c_1"}


messenger_bot.MessengerBot._post_json = fake_post_json
run = asyncio.run

aid, err = channel_accounts.create_account({"channel": "messenger", "token": f"{PAGE} {TOKEN} {APP_SECRET}",
                                            "external_id": PAGE, "label": "Shop", "meta": {"bot_name": "Shop"}})
check("a Messenger account to work with", bool(aid), err)
cl = TestClient(main.app)

# ============================================================ 1. settings and secret
cfg = {"on": True, "keywords": "NAOTA", "text": "Chào bạn, link: https://vuong.ai/tro-ly-ai",
       "public_replies": ["Vương đã nhắn riêng bạn nhé."],
       "followups": [{"after_h": 3, "text": "Nhắc 1"}, {"after_h": 20, "text": "Nhắc 2"}, {"after_h": 30, "text": "x"}],
       "contact_url": "https://vuong.ai/api/lien-he-naota", "contact_tags": ["binh-luan-naota"]}
r = cl.post("/messenger/auto", json={"account_id": aid, "auto": cfg, "secret": SECRET})
check("settings save", r.status_code == 200 and r.json().get("ok"), r.text[:200])
check("a follow-up past 23.5 hours is dropped", len(r.json()["auto"]["followups"]) == 2)
check("keywords typed as text become a list", r.json()["auto"]["keywords"] == ["NAOTA"])
g = cl.get("/messenger/auto", params={"account_id": aid}).json()
check("secret reported as set", g.get("secret_set") is True)
check("secret never returned by the settings route", SECRET not in str(g))
acc = channel_accounts.get_account(aid)
check("secret never in the account view", SECRET not in str(acc) and "auto_secret_enc" not in acc)
check("secret readable internally", channel_accounts.bi_mat_auto(aid) == SECRET)
r = cl.post("/messenger/auto", json={"account_id": aid, "auto": {**cfg, "text": ""}})
check("on without a message is refused", r.status_code == 400)
r = cl.post("/messenger/auto", json={"account_id": aid, "auto": {**cfg, "contact_url": "http://x.vn"}})
check("a non-https contact link is refused", r.status_code == 400)
cl.post("/messenger/auto", json={"account_id": aid, "auto": cfg})
check("secret kept when not sent again", channel_accounts.bi_mat_auto(aid) == SECRET)

# ============================================================ 2-3. comments
bot = messenger_bot.MessengerBot(f"{PAGE} {TOKEN} {APP_SECRET}", "", None, giau_trang_thai=True)
bot.account_id = aid
C = messenger_auto.cau_hinh(aid)


def com(cid, msg, who="777", post="p1"):
    return {"comment_id": cid, "root_id": cid, "post_id": post, "from_id": who, "from_name": "Lan", "message": msg}


check("keyword match ignores case and accents", messenger_auto.khop("cho mình xin Naota ạ", ["NAOTA"]))
check("keyword must be a whole word", not messenger_auto.khop("naotastore", ["NAOTA"]))
check("no keyword means every comment", messenger_auto.khop("hay quá", []))

SENT.clear()
r1 = run(messenger_auto.on_comment(bot, com("c1", "NAOTA"), C))
check("matching comment gets a private reply", r1.get("done") and any(p[1].get("recipient") == {"comment_id": "c1"} for p in SENT), r1)
check("and the public reply under it", r1.get("public") and any(p[0] == "c1/comments" for p in SENT))
r2 = run(messenger_auto.on_comment(bot, com("c2", "naota nữa"), C))
check("same person, same post: no second message", r2.get("why") == "already")
r3 = run(messenger_auto.on_comment(bot, com("c3", "NAOTA", post="p2"), C))
check("same person, another post: a message", r3.get("done"))
check("a comment without the keyword is skipped", run(messenger_auto.on_comment(bot, com("c4", "hay", who="8"), C)).get("why") == "keyword")
check("the Page's own comment is skipped", run(messenger_auto.on_comment(bot, com("c5", "NAOTA", who=PAGE), C)).get("why") == "page")
MODE["graph"] = "fail"
check("a failed send reports it", run(messenger_auto.on_comment(bot, com("c6", "NAOTA", who="9"), C)).get("why") == "send_failed")
MODE["graph"] = "ok"
check("and can be retried", run(messenger_auto.on_comment(bot, com("c7", "NAOTA", who="9"), C)).get("done"))
off = dict(C, on=False)
check("off sends nothing", run(messenger_auto.on_comment(bot, com("c8", "NAOTA", who="10"), off)).get("why") == "off")

# The bot path: with a public auto reply, the comment is only logged, the A.I. does not answer it publicly too.
seen = []


async def fake_answer(text, meta, progress):
    seen.append(dict(meta))
    return ""

bot.answer_fn = fake_answer
messenger_bot.comment_mode = lambda account_id: "reply"
run(bot._on_comment(com("c9", "NAOTA", who="11")))
check("auto public reply makes the A.I. stay silent on that comment", seen and seen[-1].get("log_only") is True, seen)

# ============================================================ 4. contacts
check("phone found", messenger_auto.lay_lien_he("sđt mình 0904 950 355 nhé")["dien_thoai"] == "0904950355")
check("+84 phone found", messenger_auto.lay_lien_he("+84 904.950.355")["dien_thoai"] == "+84904950355")
check("email found", messenger_auto.lay_lien_he("mail: Lan.Nguyen@Gmail.com.")["email"] == "lan.nguyen@gmail.com")
check("a price is not a phone", messenger_auto.lay_lien_he("giá 1868000 đ")["dien_thoai"] == "")

POSTS = []
CODES = [200]


async def fake_post(url, body, headers):
    POSTS.append((url, body, headers))
    return (CODES.pop(0) if CODES else 200), "{}"

messenger_auto.RETRY_BASE_S = 0
r = run(messenger_auto.on_message(bot, "PSID-9", "số mình 0904950355", "Lan", C, post=fake_post))
check("contact posted", r["contact"] and r["contact"].get("ok") and len(POSTS) == 1, r)
u, body, headers = POSTS[0]
check("to the owner's link", u == C["contact_url"])
check("signed with the secret", headers.get("Authorization") == "Bearer " + SECRET)
check("body has phone, Facebook id, source, tags",
      body["dien_thoai"] == "0904950355" and body["facebook_id"] == "PSID-9" and body["the"] == ["binh-luan-naota"]
      and body["nguon"] == "messenger-naota" and body["email"] is None)
run(messenger_auto.on_message(bot, "PSID-9", "0904950355 đó", "Lan", C, post=fake_post))
check("the same contact is sent once", len(POSTS) == 1)
POSTS.clear(); CODES[:] = [503, 200]
r = run(messenger_auto.on_message(bot, "PSID-10", "a@b.vn", "B", C, post=fake_post))
check("a 5xx is retried", r["contact"].get("ok") and len(POSTS) == 2)
POSTS.clear(); CODES[:] = [401]
r = run(messenger_auto.on_message(bot, "PSID-11", "c@d.vn", "C", C, post=fake_post))
check("a 4xx is not retried", not r["contact"].get("ok") and len(POSTS) == 1)
CODES[:] = [200]
r = run(messenger_auto.on_message(bot, "PSID-11", "c@d.vn", "C", C, post=fake_post))
check("an undelivered contact is tried again next time", r["contact"].get("ok") and not r["contact"].get("already"))

# ============================================================ 5. follow-ups
messenger_bot._REGISTRY[PAGE] = bot
run(messenger_auto.on_message(bot, "PSID-20", "chào shop", "D", C))
now = time.time()
check("nothing due right away", not [d for d in messenger_auto.due(now) if d[1] == "PSID-20"])
d3 = [d for d in messenger_auto.due(now + 3.1 * 3600) if d[1] == "PSID-20"]
check("first follow-up due after 3 hours", [x[3] for x in d3] == ["Nhắc 1"], d3)
d20 = [d for d in messenger_auto.due(now + 20.5 * 3600) if d[1] == "PSID-20"]
check("both due after 20 hours", [x[3] for x in d20] == ["Nhắc 1", "Nhắc 2"], d20)
check("none past the window", not [d for d in messenger_auto.due(now + 24 * 3600) if d[1] == "PSID-20"])

SENT.clear()
st = messenger_auto._load()
st["chats"][f"{PAGE}|PSID-20"]["t"] = now - 3.2 * 3600
messenger_auto.STATE_PATH.write_text(__import__("json").dumps(st), encoding="utf-8")
n = run(messenger_auto.tick())
check("tick sends the due follow-up", n == 1 and any(p[1].get("message", {}).get("text") == "Nhắc 1" for p in SENT), SENT)
check("and not twice", run(messenger_auto.tick()) == 0)
run(messenger_auto.on_message(bot, "PSID-20", "ừ", "D", C))
check("a new message restarts the clock", not [d for d in messenger_auto.due() if d[1] == "PSID-20"])

print()
if _fails:
    print(f"{len(_fails)} FAILED")
    sys.exit(1)
print("all ok")
