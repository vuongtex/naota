"""Bundled plugin: never publish the same post twice.

Why it exists (26/11/2026): the scheduled posting loop and a chat turn both published the same
image post to Facebook, Instagram and Threads within 15 minutes. Each one read the sheet before the
other had written its links, so each saw the row as "not posted yet". Rules in a skill cannot stop
that: both sides followed the rules. The only reliable place is the tool call itself, so this hook
sits in front of every publishing call on every engine.

How it decides:
- A call is a PUBLISH when its action name says so (Composio slugs like FACEBOOK_CREATE_PHOTO_POST,
  INSTAGRAM_POST_IG_USER_MEDIA, or the native fb_page_post/photo/album/video tools) and it carries
  a caption long enough to be a post. Comments, replies, messages, edits, uploads and reads are
  never touched: a bot answering 50 commenters with the same sentence is normal.
- Fingerprint = platform + target account + the caption with hashtags and spacing removed. Changing
  only the hashtags does not make a post new.
- `pre_tool_call` reserves the fingerprint BEFORE the call runs, so two calls racing each other
  cannot both pass. A second call with the same fingerprint within 24 hours is denied.
- `post_tool_call` turns the reservation into "published", or releases it when the call clearly
  failed, so a failed post can be retried at once. A reservation left behind by a crash expires
  after 15 minutes.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import unicodedata

WINDOW = 24 * 3600          # same post on same channel within this window = duplicate
PENDING_TTL = 15 * 60       # a reservation whose call never reported back
KEEP = 48 * 3600            # prune older entries
MIN_TEXT = 20               # shorter captions are not treated as posts

_TEXT_KEYS = ("message", "caption", "text", "description", "content", "body", "post_text")
_TARGET_KEYS = ("page_id", "page", "ig_user_id", "instagram_business_account_id", "user_id",
                "account_id", "profile_id", "owner_id", "location_id")
_SKIP = re.compile(r"COMMENT|REPLY|MESSAGE|_DM\b|_DM_|CHAT|UPDATE|EDIT|DELETE|REMOVE|GET|LIST|"
                   r"SEARCH|FETCH|UPLOAD|EMAIL|THUMBNAIL|INSIGHT", re.I)
_PUBLISH = re.compile(r"POST|PUBLISH|CREATE|SHARE|TWEET|REEL|STORY|CAROUSEL|MEDIA", re.I)
_NATIVE = re.compile(r"^fb_page_(post|photo|album|video)$")
_HASHTAG = re.compile(r"#[^\s#]+")
_FAIL = re.compile(r'"successful"\s*:\s*false|"success"\s*:\s*false|"error"\s*:\s*\{', re.I)
_OK = re.compile(r'"successful"\s*:\s*true|"success"\s*:\s*true|"id"\s*:', re.I)


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFC", str(text or "")).lower()
    t = _HASHTAG.sub(" ", t)
    return " ".join(t.split())


def _caption(arguments: dict) -> str:
    for k in _TEXT_KEYS:
        v = arguments.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _target(arguments: dict) -> str:
    for k in _TARGET_KEYS:
        v = arguments.get(k)
        if isinstance(v, (str, int)) and str(v).strip():
            return str(v).strip()
    return ""


def _actions(tool_name: str, args) -> list:
    """Every (platform, slug, arguments) publish action inside one tool call."""
    out = []
    if not isinstance(args, dict):
        return out
    last = str(tool_name or "").split("__")[-1]
    if _NATIVE.match(last):
        out.append(("facebook", last, args))
        return out
    pairs = []
    if re.fullmatch(r"[A-Z][A-Z0-9_]+", last) and "COMPOSIO" not in last:
        pairs.append((last, args))
    for key in ("tools", "actions"):
        for item in args.get(key) or []:
            if isinstance(item, dict):
                slug = item.get("tool_slug") or item.get("slug") or item.get("action")
                a = item.get("arguments") or item.get("params") or item.get("input") or {}
                if isinstance(slug, str) and isinstance(a, dict):
                    pairs.append((slug, a))
    if isinstance(args.get("tool_slug"), str) and isinstance(args.get("arguments"), dict):
        pairs.append((args["tool_slug"], args["arguments"]))
    for slug, a in pairs:
        if _SKIP.search(slug) or not _PUBLISH.search(slug):
            continue
        out.append((slug.split("_")[0].lower(), slug, a))
    return out


def _fingerprints(tool_name: str, args) -> list:
    fps = []
    for platform, slug, a in _actions(tool_name, args):
        text = _norm(_caption(a))
        if len(text) < MIN_TEXT:
            continue
        raw = f"{platform}|{_target(a)}|{text}"
        fps.append((hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24], platform, slug, text[:80]))
    return fps


def _when(ts: float) -> str:
    return time.strftime("%H:%M %d/%m/%Y", time.localtime(ts))


def register(ctx):
    store = ctx.data_dir / "da-dang.json"
    lock = threading.Lock()

    def _load() -> dict:
        try:
            d = json.loads(store.read_text(encoding="utf-8"))
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}

    def _save(d: dict) -> None:
        now = time.time()
        d = {k: v for k, v in d.items() if now - float(v.get("t", 0)) < KEEP}
        tmp = store.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        tmp.replace(store)

    def _pre(tool_name="", args=None, **_):
        fps = _fingerprints(tool_name, args)
        if not fps:
            return None
        now = time.time()
        with lock:
            d = _load()
            for fp, platform, slug, preview in fps:
                e = d.get(fp)
                if not e:
                    continue
                age = now - float(e.get("t", 0))
                if e.get("state") == "done" and age < WINDOW:
                    return {"deny": (
                        f"Duplicate post blocked: the same text was already published to {platform} at "
                        f"{_when(e['t'])} (\"{preview}...\"). Do NOT publish it again and do NOT retry "
                        f"with small wording changes to get around this. Tell the owner it is already "
                        f"live, and mark the row as posted if a sheet tracks it. Only the owner can ask "
                        f"for a real repost, after 24 hours or with genuinely new text.")}
                if e.get("state") == "pending" and age < PENDING_TTL:
                    return {"deny": (
                        f"Duplicate post blocked: another session started publishing this same text to "
                        f"{platform} at {_when(e['t'])} and has not finished. Do NOT publish it. Wait for "
                        f"that run's result instead, then report it.")}
            for fp, platform, slug, preview in fps:
                d[fp] = {"t": now, "state": "pending", "platform": platform, "slug": slug,
                         "preview": preview}
            _save(d)
        return None

    def _post(tool_name="", args=None, result=None, denied=False, **_):
        if denied:
            return
        fps = _fingerprints(tool_name, args)
        if not fps:
            return
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
        failed = (text.lstrip().startswith("ERROR") or bool(_FAIL.search(text))) and not _OK.search(text)
        now = time.time()
        with lock:
            d = _load()
            for fp, *_rest in fps:
                e = d.get(fp)
                if not e or e.get("state") != "pending":
                    continue
                if failed:
                    d.pop(fp, None)
                else:
                    e["state"], e["t"] = "done", now
            _save(d)

    ctx.register_hook("pre_tool_call", _pre)
    ctx.register_hook("post_tool_call", _post)
