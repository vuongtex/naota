"""Automations on a Facebook Page connected through the Messenger channel.

Three things a shop owner usually pays a CRM to do, done here for every engine and every brain:

  1. Auto private reply. Someone comments under a Page post: the Page sends them ONE private Messenger
     message (Meta's Private Replies, `recipient.comment_id`) and, optionally, a short public reply under the
     comment. Either every comment or only comments containing a keyword. One per person per post, so a person
     who comments three times under one post gets one message, not three.
  2. Follow-ups inside the 24-hour window. A private reply does not open a chat: Meta lets the Page write again
     only after the person answers. From then on every message the person sends restarts a clock, and the
     follow-ups configured (for example 3 hours and 20 hours later) go out when the person has said nothing
     since. Nothing is sent past 23.5 hours, because Messenger refuses it.
  3. Contacts out. When a person writes an email address or a phone number in Messenger, the contact is POSTed
     as JSON to a URL the owner sets (their CRM, their own website), signed `Authorization: Bearer <secret>`.
     Each value is sent once.

Settings live in the Messenger account's meta under `auto` (see `cau_hinh`); the secret is stored encrypted on the
account (`channel_accounts.dat_bi_mat_auto`), never in meta, so it never reaches the dashboard.
State (who got what) is one JSON file in STATE_DIR. Losing it only means a person could get a message again.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
import sys
import threading
import time
from typing import Optional

import httpx

from config import STATE_DIR

STATE_PATH = STATE_DIR / "messenger_auto.json"
_lock = threading.RLock()

MAX_FOLLOWUPS = 3
WINDOW_S = 23.5 * 3600          # Messenger's 24-hour window, with a margin
TICK_S = 120                    # how often due follow-ups are looked for
KEEP_S = 8 * 86400              # state older than this is dropped
MAX_PUBLIC = 10
MAX_TEXT = 1900
CONTACT_TRIES = 3
RETRY_BASE_S = 2               # wait 2, 4 seconds between tries

DEFAULTS = {
    "on": False,                # auto private reply on comments
    "keywords": [],             # empty = every comment
    "text": "",                 # the private message
    "public_replies": [],       # one is picked at random; empty = no public reply
    "followups": [],            # [{"after_h": 3, "text": "..."}]
    "contact_url": "",          # where contacts are POSTed; empty = off
    "contact_source": "messenger-naota",
    "contact_tags": [],
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# A Vietnamese mobile number as people type it: 0xxx or +84xxx, spaces, dots or dashes inside.
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?84|0)(?:[\s.\-]?\d){9}(?!\d)")


# ---------------------------------------------------------------- settings
def _clean_list(v, limit, size) -> list:
    if isinstance(v, str):
        v = [x for x in re.split(r"[\n,]", v)]
    if not isinstance(v, list):
        return []
    out = []
    for x in v:
        s = str(x or "").strip()[:size]
        if s and s not in out:
            out.append(s)
    return out[:limit]


def chuan_hoa(raw) -> dict:
    """Settings from the dashboard or from meta, made safe: unknown keys dropped, sizes capped."""
    r = raw if isinstance(raw, dict) else {}
    c = dict(DEFAULTS)
    c["on"] = bool(r.get("on"))
    c["keywords"] = _clean_list(r.get("keywords"), 20, 60)
    c["text"] = str(r.get("text") or "").strip()[:MAX_TEXT]
    c["public_replies"] = _clean_list(r.get("public_replies"), MAX_PUBLIC, 500)
    fu = []
    for f in (r.get("followups") or [])[:MAX_FOLLOWUPS] if isinstance(r.get("followups"), list) else []:
        if not isinstance(f, dict):
            continue
        try:
            h = float(f.get("after_h"))
        except Exception:
            continue
        t = str(f.get("text") or "").strip()[:MAX_TEXT]
        if t and 0.1 <= h <= 23.5:
            fu.append({"after_h": round(h, 2), "text": t})
    c["followups"] = sorted(fu, key=lambda f: f["after_h"])
    url = str(r.get("contact_url") or "").strip()[:500]
    c["contact_url"] = url if re.match(r"^https://[^\s/]+", url) else ""
    c["contact_source"] = str(r.get("contact_source") or DEFAULTS["contact_source"]).strip()[:120] or DEFAULTS["contact_source"]
    c["contact_tags"] = _clean_list(r.get("contact_tags"), 10, 60)
    return c


def cau_hinh(account_id: str) -> dict:
    try:
        import channel_accounts
        a = channel_accounts.get_account(account_id) or {}
    except Exception:
        a = {}
    return chuan_hoa((a.get("meta") or {}).get("auto"))


def _bo_dau(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", str(s or "").lower()).replace("đ", "d")
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def khop(text: str, keywords: list) -> bool:
    """Empty keyword list = every comment. Otherwise a keyword must appear as a whole word, ignoring case and
    Vietnamese accents ("naota" matches "NAOTA", "Naota ạ")."""
    if not keywords:
        return True
    t = " " + re.sub(r"[^0-9a-z]+", " ", _bo_dau(text)) + " "
    for k in keywords:
        kk = re.sub(r"[^0-9a-z]+", " ", _bo_dau(k)).strip()
        if kk and f" {kk} " in t:
            return True
    return False


def lay_lien_he(text: str) -> dict:
    """The first email and the first phone number in a message. {"email", "dien_thoai"}, either may be ""."""
    s = str(text or "")
    m = EMAIL_RE.search(s)
    email = m.group(0).lower().rstrip(".") if m else ""
    p = PHONE_RE.search(s)
    phone = re.sub(r"[^\d+]", "", p.group(0)) if p else ""
    return {"email": email, "dien_thoai": phone}


# ---------------------------------------------------------------- state
def _load() -> dict:
    try:
        d = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            d.setdefault("sent", {})
            d.setdefault("chats", {})
            d.setdefault("contacts", {})
            return d
    except Exception:
        pass
    return {"sent": {}, "chats": {}, "contacts": {}}


def _save(d: dict) -> None:
    now = time.time()
    for k in ("sent", "contacts"):
        d[k] = {x: t for x, t in d[k].items() if now - float(t or 0) < KEEP_S * (4 if k == "contacts" else 1)}
    d["chats"] = {x: v for x, v in d["chats"].items() if now - float((v or {}).get("t") or 0) < KEEP_S}
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_PATH)


def _claim(kind: str, key: str) -> bool:
    """Mark `key` done once. True the first time, False after."""
    with _lock:
        d = _load()
        if key in d[kind]:
            return False
        d[kind][key] = time.time()
        _save(d)
        return True


def _unclaim(kind: str, key: str) -> None:
    with _lock:
        d = _load()
        d[kind].pop(key, None)
        _save(d)


# ---------------------------------------------------------------- inbox
def _ghi(bot, chat: str, text: str, chat_type: str = "private") -> None:
    """Show what the automation sent in the inbox, as the bot's message (it does not take the chat over)."""
    try:
        import conversations
        conversations.ghi_su_kien({
            "channel": "messenger", "account_id": getattr(bot, "account_id", "") or bot.page_id,
            "account_name": getattr(bot, "bot_username", "") or "", "bot_id": "",
            "external_chat_id": chat, "chat_type": chat_type, "sender_type": "bot", "sender_name": "NAOTA",
            "message_type": "text", "text": text, "metadata": {"tu_dong": True},
        })
    except Exception as e:
        print(f"[messenger auto] inbox: {type(e).__name__}: {e}", file=sys.stderr)


# ---------------------------------------------------------------- 1. comments
async def on_comment(bot, com: dict, cfg: Optional[dict] = None) -> dict:
    """Run the auto private reply for one new comment. Returns what happened, for logs and tests."""
    c = cfg or cau_hinh(getattr(bot, "account_id", ""))
    if not (c["on"] and c["text"]):
        return {"done": False, "why": "off"}
    from_id = str(com.get("from_id") or "")
    if not from_id or from_id in (bot.page_id, getattr(bot, "ig_id", "")):
        return {"done": False, "why": "page"}
    if not khop(com.get("message") or "", c["keywords"]):
        return {"done": False, "why": "keyword"}
    key = f"{bot.page_id}:{from_id}:{com.get('post_id') or com.get('root_id')}"
    if not _claim("sent", key):
        return {"done": False, "why": "already"}
    r = await bot.private_reply(com["comment_id"], c["text"])
    if not r.get("ok"):
        _unclaim("sent", key)
        print(f"[messenger auto] private reply failed: {r.get('error')}", file=sys.stderr)
        return {"done": False, "why": "send_failed", "error": r.get("error", "")}
    _ghi(bot, ("ig:" if com.get("instagram") else "") + (r.get("recipient_id") or from_id), c["text"])
    pub = ""
    if c["public_replies"]:
        pub = random.choice(c["public_replies"])
        ok = await bot.public_reply(com["comment_id"], pub, instagram=bool(com.get("instagram")))
        if not ok:
            pub = ""
    return {"done": True, "public": pub}


# ---------------------------------------------------------------- 2 + 3. messages
async def on_message(bot, chat: str, text: str, name: str = "", cfg: Optional[dict] = None,
                     post=None) -> dict:
    """A person wrote to the Page in Messenger: restart their follow-up clock and send out any contact found."""
    c = cfg or cau_hinh(getattr(bot, "account_id", ""))
    out = {"clock": False, "contact": None}
    if c["followups"]:
        with _lock:
            d = _load()
            d["chats"][f"{bot.page_id}|{chat}"] = {"t": time.time(), "sent": [], "name": name}
            _save(d)
        out["clock"] = True
    if c["contact_url"]:
        lh = lay_lien_he(text)
        if lh["email"] or lh["dien_thoai"]:
            out["contact"] = await gui_lien_he(bot, chat, name, lh, text, c, post=post)
    return out


async def gui_lien_he(bot, chat, name, lh, text, c, post=None) -> dict:
    key = f"{bot.page_id}|{chat}|{lh['email']}|{lh['dien_thoai']}"
    if not _claim("contacts", key):
        return {"ok": True, "already": True}
    try:
        import channel_accounts
        secret = channel_accounts.bi_mat_auto(getattr(bot, "account_id", ""))
    except Exception:
        secret = ""
    body = {
        "ten": str(name or "")[:120], "email": lh["email"] or None, "dien_thoai": lh["dien_thoai"] or None,
        "facebook_id": chat.split(":", 1)[-1], "nguon": c["contact_source"], "the": c["contact_tags"],
        "kenh": "instagram" if chat.startswith("ig:") else "messenger", "page_id": bot.page_id,
        "tin_goc": str(text or "")[:500],
    }
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["Authorization"] = "Bearer " + secret
    send = post or _post
    last = ""
    for i in range(CONTACT_TRIES):
        try:
            code, resp = await send(c["contact_url"], body, headers)
        except Exception as e:
            code, resp = 0, f"{type(e).__name__}: {e}"
        if 200 <= code < 300:
            return {"ok": True, "code": code}
        last = f"{code} {str(resp)[:200]}"
        if code and code < 500:
            break
        await asyncio.sleep(RETRY_BASE_S * (2 ** i))
    _unclaim("contacts", key)
    print(f"[messenger auto] contact not delivered: {last}", file=sys.stderr)
    return {"ok": False, "error": last}


async def _post(url, body, headers):
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        r = await client.post(url, json=body, headers=headers)
        return r.status_code, r.text


def due(now: Optional[float] = None) -> list:
    """Follow-ups to send now: [(page_id, chat, index, text)]. Pure read of the state plus settings."""
    now = now or time.time()
    out = []
    with _lock:
        d = _load()
    import messenger_bot
    for key, v in d["chats"].items():
        page_id, _, chat = key.partition("|")
        bot = messenger_bot.registered().get(page_id)
        if bot is None:
            continue
        c = cau_hinh(getattr(bot, "account_id", ""))
        age = now - float(v.get("t") or 0)
        if age >= WINDOW_S:
            continue
        for i, f in enumerate(c["followups"]):
            if i in (v.get("sent") or []):
                continue
            if age >= f["after_h"] * 3600:
                out.append((page_id, chat, i, f["text"]))
    return out


def _mark(page_id, chat, i, t0) -> bool:
    with _lock:
        d = _load()
        v = d["chats"].get(f"{page_id}|{chat}")
        if not v or float(v.get("t") or 0) != t0 or i in v.get("sent", []):
            return False
        v.setdefault("sent", []).append(i)
        _save(d)
        return True


async def tick() -> int:
    import messenger_bot
    n = 0
    for page_id, chat, i, text in due():
        with _lock:
            v = _load()["chats"].get(f"{page_id}|{chat}") or {}
        t0 = float(v.get("t") or 0)
        if not _mark(page_id, chat, i, t0):
            continue
        bot = messenger_bot.registered().get(page_id)
        if bot is None:
            continue
        try:
            ok, err = await bot.send_text(chat, text)
        except Exception as e:
            ok, err = False, f"{type(e).__name__}: {e}"
        if ok:
            _ghi(bot, chat, text)
            n += 1
        else:
            print(f"[messenger auto] follow-up not sent: {err}", file=sys.stderr)
    return n


async def loop() -> None:
    """Started once with the server. Cheap when nothing is configured: one small file read per tick."""
    while True:
        await asyncio.sleep(TICK_S)
        try:
            await tick()
        except Exception as e:
            print(f"[messenger auto] {type(e).__name__}: {e}", file=sys.stderr)
