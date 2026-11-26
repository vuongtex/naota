"""Duplicate post guard (system/plugins/chong-dang-trung).

26/11/2026: the posting loop and a chat turn published the same post twice on three channels. These tests pin
the guard that now sits in front of every publishing tool call.
"""
import importlib.util
import json
import pathlib
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "system" / "plugins" / "chong-dang-trung" / "plugin.py"

CAPTION = ("Vương tin một hệ thống hơn khi người làm ra nó kể được hôm nó hỏng.\n\n"
           "Bình luận chữ NAOTA.\n\n#naota #hoangngocvuong")


class _Ctx:
    def __init__(self, d):
        self.data_dir = d
        self.hooks = {}

    def register_hook(self, event, cb):
        self.hooks[event] = cb


@pytest.fixture()
def guard(tmp_path):
    spec = importlib.util.spec_from_file_location("chong_dang_trung_plugin", PLUGIN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ctx = _Ctx(tmp_path)
    mod.register(ctx)
    return mod, ctx.hooks["pre_tool_call"], ctx.hooks["post_tool_call"], tmp_path


def _multi(slug, **arguments):
    return {"tools": [{"tool_slug": slug, "arguments": arguments}]}


OK = json.dumps({"successful": True, "data": {"id": "123_456"}})


def test_manifest_on_by_default():
    text = (PLUGIN.parent / "plugin.yaml").read_text(encoding="utf-8")
    assert "enabled: true" in text
    assert "pre_tool_call" in text and "post_tool_call" in text


def test_second_publish_of_same_post_is_denied(guard):
    _, pre, post, _ = guard
    tool = "composio__COMPOSIO_MULTI_EXECUTE_TOOL"
    args = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="788088527723595", message=CAPTION, url="https://x/a.jpg")
    assert pre(tool_name=tool, args=args) is None
    post(tool_name=tool, args=args, result=OK)
    again = pre(tool_name=tool, args=args)
    assert again and "Duplicate post blocked" in again["deny"]


def test_race_is_denied_while_first_call_runs(guard):
    _, pre, _, _ = guard
    args = _multi("INSTAGRAM_POST_IG_USER_MEDIA", ig_user_id="17841", caption=CAPTION, image_url="https://x/a.jpg")
    assert pre(tool_name="composio__COMPOSIO_MULTI_EXECUTE_TOOL", args=args) is None
    second = pre(tool_name="composio__COMPOSIO_MULTI_EXECUTE_TOOL", args=args)
    assert second and "has not finished" in second["deny"]


def test_only_hashtags_changed_is_still_a_duplicate(guard):
    _, pre, post, _ = guard
    a = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION)
    b = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION.replace("#naota", "#vibecoding"))
    pre(tool_name="t", args=a)
    post(tool_name="t", args=a, result=OK)
    assert pre(tool_name="t", args=b)


def test_other_channel_or_page_is_not_a_duplicate(guard):
    _, pre, post, _ = guard
    fb = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION)
    pre(tool_name="t", args=fb)
    post(tool_name="t", args=fb, result=OK)
    assert pre(tool_name="t", args=_multi("INSTAGRAM_POST_IG_USER_MEDIA", ig_user_id="9", caption=CAPTION)) is None
    assert pre(tool_name="t", args=_multi("FACEBOOK_CREATE_PHOTO_POST", page_id="2", message=CAPTION)) is None


def test_failed_publish_can_be_retried(guard):
    _, pre, post, _ = guard
    args = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION)
    pre(tool_name="t", args=args)
    post(tool_name="t", args=args, result=json.dumps({"successful": False, "error": "timeout"}))
    assert pre(tool_name="t", args=args) is None


@pytest.mark.parametrize("slug", ["FACEBOOK_CREATE_COMMENT", "FACEBOOK_REPLY_TO_COMMENT", "FACEBOOK_UPDATE_POST",
                                  "INSTAGRAM_SEND_MESSAGE", "FACEBOOK_GET_POST", "FACEBOOK_UPLOAD_PHOTOS_BATCH"])
def test_comments_replies_edits_reads_are_never_blocked(guard, slug):
    _, pre, post, _ = guard
    args = _multi(slug, page_id="1", message=CAPTION)
    for _ in range(3):
        assert pre(tool_name="t", args=args) is None
        post(tool_name="t", args=args, result=OK)


def test_native_facebook_tool_is_guarded(guard):
    _, pre, post, _ = guard
    args = {"page": "1", "message": CAPTION}
    assert pre(tool_name="fb_page_photo", args=args) is None
    post(tool_name="fb_page_photo", args=args, result="OK: đã đăng, id 1_2")
    assert pre(tool_name="fb_page_photo", args=args)


def test_short_text_is_ignored(guard):
    _, pre, post, _ = guard
    args = _multi("FACEBOOK_CREATE_POST", page_id="1", message="Chào")
    for _ in range(2):
        assert pre(tool_name="t", args=args) is None
        post(tool_name="t", args=args, result=OK)


def test_window_expires(guard, monkeypatch):
    mod, pre, post, _ = guard
    args = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION)
    pre(tool_name="t", args=args)
    post(tool_name="t", args=args, result=OK)
    real = time.time
    monkeypatch.setattr(mod.time, "time", lambda: real() + mod.WINDOW + 60)
    assert pre(tool_name="t", args=args) is None


def test_stale_reservation_expires(guard, monkeypatch):
    mod, pre, _, _ = guard
    args = _multi("FACEBOOK_CREATE_PHOTO_POST", page_id="1", message=CAPTION)
    pre(tool_name="t", args=args)
    real = time.time
    monkeypatch.setattr(mod.time, "time", lambda: real() + mod.PENDING_TTL + 60)
    assert pre(tool_name="t", args=args) is None
