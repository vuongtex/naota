"""Office page (server/office.py): built only from the brain's logs, read only, no secret or path leaks.

The fixture mirrors a real day: a posting loop ran 9 times, 3 checks failed, it paused itself at 20:01, while a
reminder with the same name kept running. One agent per tag, and departments with nobody in them still show.
"""
import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "server"))
import office  # noqa: E402

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
fails = 0


def check(name, ok):
    global fails
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        fails += 1


def ts(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp()


def write(p: Path, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text if isinstance(text, str) else json.dumps(text, ensure_ascii=False), encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    b = Path(tmp)
    write(b / "agents" / "viet-bai.md", "---\nname: Người viết bài\nrole: viết bài fanpage\ntags: [marketing, content]\n---\nx")
    write(b / "agents" / "ke-toan.md", "---\nname: Kế toán\ntags:\n  - tài chính\n---\n")
    write(b / "agents" / "tro-ly.md", "---\nname: Trợ lý chung\n---\n")
    write(b / "agents" / "seo.md", "---\nname: SEO\ntags: [SEO]\n---\n")
    write(b / "Naota" / "loops" / "dang-theo-lich.md",
          "---\nname: Đăng theo lịch\nenabled: true\ninterval_min: 60\n---\nĐăng bài lên fanpage")
    write(b / "Naota" / "loops" / "don-rac.md", "---\nname: Dọn file tạm\nenabled: false\ninterval_min: 1440\n---\n")
    write(b / "Naota" / "loop-state.json", {
        "dang-theo-lich": {"last_run": ts("2026-11-07 20:00"), "last_status": "✗ lỗi đăng",
                           "fail_streak": 3,
                           "auto_paused_reason": "3 lần liền không đạt: token=EAAGabcdefghijklmnopqrstuvwxyz0123 hết hạn ở /opt/naota/x.py"},
        "da-go": {"last_run": ts("2026-11-01 08:00"), "last_status": "✓"},
    })
    log = []
    for i, (hm, ok) in enumerate([("08:00", 1), ("09:00", 1), ("10:00", 0), ("11:00", 1), ("12:00", 1),
                                  ("13:00", 1), ("18:00", 0), ("19:00", 1), ("20:00", 0)]):
        log.append(f"## [2026-11-07 {hm}] dang-theo-lich lượt {i + 1}\nĐã đăng bài số {i + 1}\n"
                   f"**Kiểm chứng:** {'✓' if ok else '✗'} {'ok' if ok else 'bài không hiện, sk-ABCDEFGHIJKLMNOPQRSTUV'}\n")
    write(b / "Naota" / "loop-log" / "2026-11-07.md", "\n".join(log))
    write(b / "Naota" / "reminders.json", {"reminders": [
        {"id": "r1", "label": "Đăng theo lịch Threads", "cron": "0 9 * * *", "status": "pending", "error": ""},
        {"id": "r2", "label": "Gia hạn token Threads", "repeat_min": 1440, "status": "pending", "error": ""},
        {"id": "r3", "label": "Nhắc gọi khách", "due_at": ts("2026-11-07 10:00"), "status": "done"},
        {"id": "r4", "label": "Báo cáo doanh thu", "cron": "0 7 * * 1", "status": "cancelled"},
    ]})
    write(b / "Naota" / "work-log.jsonl", "\n".join(json.dumps(x) for x in [
        {"ts": ts("2026-11-07 09:00"), "kind": "reminder", "ref": "r1", "title": "Đăng theo lịch Threads", "status": "ok"},
        {"ts": ts("2026-11-07 09:30"), "kind": "reminder", "ref": "r2", "title": "Gia hạn token", "status": "fail"},
        {"ts": ts("2026-11-07 10:00"), "kind": "reminder", "ref": "r3", "title": "Nhắc gọi khách", "status": "ok"},
    ]) + "\nnot json\n")
    write(b / "Naota" / "kanban.json", {"tasks": [{"id": "t1", "title": "Duyệt bài mới", "status": "review"},
                                                  {"id": "t2", "title": "Viết email", "status": "done"}]})
    write(b / "Naota" / "office.json", {"targets": {"r1": 2}})
    write(b / "secrets" / "token.txt", "SHOULD-NEVER-SHOW")

    now = ts("2026-11-07 21:00")
    d = office.build(b, now, TZ, "2026-11-07")
    jobs = {j["id"]: j for j in d["jobs"]}
    depts = {x["id"]: x for x in d["depts"]}
    blob = json.dumps(d, ensure_ascii=False)

    check("one job per loop file, per removed loop state, per reminder", sorted(jobs) == ["da-go", "dang-theo-lich", "don-rac", "r1", "r2", "r3", "r4"])
    L = jobs["dang-theo-lich"]
    check("the posting loop is paused with its reason", L["state"] == "paused" and "3 lần liền" in L["paused_reason"])
    check("07/11: 9 runs, 3 failed checks, 6 passed", L["day"] == {"runs": 9, "ok": 6, "fail": 3})
    check("the loop is placed in Marketing by its name", L["dept"] == "marketing" and L["dept_guessed"])
    check("a disabled loop is off", jobs["don-rac"]["state"] == "off")
    check("a loop removed from loops/ but still in state is removed", jobs["da-go"]["state"] == "removed")
    check("reminder with a failed last run is failed", jobs["r2"]["state"] == "failed")
    check("renewing a token is operations, not marketing", jobs["r2"]["dept"] == "ops")
    check("a one-off that ran is done, a cancelled one cancelled", jobs["r3"]["state"] == "done" and jobs["r4"]["state"] == "cancelled")
    check("target from office.json", jobs["r1"]["target"] == 2)
    check("Marketing light is red", depts["marketing"]["light"] == "red")
    check("agent department from its first tag, Vietnamese words map to the base id",
          [s["slug"] for s in depts["marketing"]["staff"]] == ["viet-bai"] and [s["slug"] for s in depts["finance"]["staff"]] == ["ke-toan"])
    check("an agent with no tag sits under system", [s["slug"] for s in depts["system"]["staff"]] == ["tro-ly"])
    check("a tag outside the base list becomes its own department", "SEO" in depts)
    check("sales has nobody and says so", depts["sales"]["status"] == "empty" and depts["sales"]["light"] == "grey")
    kinds = [i["kind"] for i in d["issues"]]
    check("issues: paused first", kinds[0] == "paused")
    check("issues: failed, waiting, empty department, idle department",
          {"failed", "waiting", "dept_empty", "dept_idle"} <= set(kinds))
    check("issues: the same-name reminder still running while the loop stopped",
          any(i["kind"] == "twin_running" and i["job"] == "r1" and i["other"] == "dang-theo-lich" for i in d["issues"]))
    check("waiting tasks counted from the board", d["totals"]["waiting"] == 1)
    check("totals: runs of the day = 9 loop runs + 3 reminder runs", d["totals"]["runs"] == 12)
    check("feed newest first, with the owner's clock", d["feed"][0]["at"] == "20:00" and d["feed"][0]["result"] == "verified_fail")
    check("pause time shown from the last run", L["last_at"] == "20:00")
    check("footer time in the owner's zone", d["now_at"] == "21:00:00")
    check("no token value leaks", "EAAGabcdef" not in blob and "sk-ABCDEF" not in blob)
    check("no server path leaks", "/opt/naota" not in blob)
    check("nothing from secrets/ is read", "SHOULD-NEVER-SHOW" not in blob)
    check("the page wrote nothing into the brain", not (b / "Naota" / "office-cache.json").exists()
          and sorted(p.name for p in (b / "Naota").iterdir()) == ["kanban.json", "loop-log", "loop-state.json", "loops",
                                                                    "office.json", "reminders.json", "work-log.jsonl"])

    df = d["day_feed"]
    check("replay feed: every run of 07/11, oldest first", len(df) == 12 and [x["ts"] for x in df] == sorted(x["ts"] for x in df))
    check("replay feed: the posting loop's 9 runs with 3 crosses, last at 20:00",
          [x["result"] for x in df if x["job"] == "dang-theo-lich"].count("verified_fail") == 3 and df[-1]["hm"] == "20:00")
    check("replay feed carries no secret", "sk-ABCDEF" not in json.dumps(df, ensure_ascii=False))

    # another day: a fixed record, the paused loop shows no runs that day
    d2 = office.build(b, now, TZ, "2026-11-06")
    check("a past day with no log has no runs", next(j for j in d2["jobs"] if j["id"] == "dang-theo-lich")["day"]["runs"] == 0)
    check("bad day string falls back to today", office.build(b, now, TZ, "../etc")["day"] == "2026-11-07")

with tempfile.TemporaryDirectory() as tmp:
    d = office.build(Path(tmp), time.time(), TZ)
    check("an empty brain still draws the five base departments", [x["id"] for x in d["depts"]] == office.BASE_DEPTS)
    check("missing files are reported, counts unknown", d["files"] == {"reminders": False, "work_log": False, "loop_state": False, "kanban": False}
          and d["totals"]["waiting"] is None)

# running right now: ids match the desks, times in the owner's zone, no secret, oldest first
with tempfile.TemporaryDirectory() as tmp:
    b = Path(tmp)
    write(b / "Naota" / "loops" / "dang.md", "---\nname: Đăng bài\n---\n")
    write(b / "Naota" / "reminders.json", {"reminders": [{"id": "r1", "label": "Báo cáo sáng"}]})
    now = ts("2026-11-07 21:00")
    lv = office.live(b, now, TZ, {"slug": "dang", "since": now - 125}, {"r1": now - 30, "gone": now - 5},
                     [{"id": "t1", "title": "Gửi token=sk-ABCDEF123456", "status": "running", "updated_at": now - 600},
                      {"id": "t2", "title": "Chờ", "status": "todo"}],
                     [{"id": "j1", "mo_ta": "render video", "bat_dau": now - 3700}])
    it = lv["items"]
    check("live: loop, reminder, running task and shell job, oldest first",
          [x["kind"] for x in it] == ["job", "task", "loop", "reminder"])
    lp = next(x for x in it if x["kind"] == "loop")
    check("live: loop keyed by slug with its name, start and seconds",
          lp["id"] == "dang" and lp["name"] == "Đăng bài" and lp["since_at"] == "20:57" and lp["secs"] == 125)
    check("live: a reminder not in this brain is left out", [x["id"] for x in it if x["kind"] == "reminder"] == ["r1"])
    check("live: task titles are scrubbed", "sk-ABCDEF" not in json.dumps(lv, ensure_ascii=False))
    check("live: nothing running is an empty list", office.live(b, now, TZ, {}, {}, [], [])["items"] == [])

check("scrub masks key=value secrets", "abc123" not in office.scrub("password: abc123 ok"))
check("scrub masks Windows paths", "Users" not in office.scrub(r"lỗi ở C:\Users\x\secret.txt"))
check("scrub keeps normal words", office.scrub("Đăng bài lên fanpage") == "Đăng bài lên fanpage")

sys.exit(1 if fails else 0)
