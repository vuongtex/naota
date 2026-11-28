"""Windows watchdog (naota-watchdog.ps1): the server once died silently and nothing on Windows restarted it.

    python tests/run.py watchdog_windows

Static checks run everywhere. On Windows the real `naota-watchdog.ps1 check` also runs against a temporary state
dir and a dead port, with the restart swapped for `echo` through NAOTA_WATCHDOG_KICK_CMD, so the counting,
threshold, reset and stopped-on-purpose paths are the real code.
"""
from _paths import ROOT  # noqa: E402,F401
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

_fails = []


def check(name, cond, extra=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(extra) + "]") if extra and not cond else ""))
    if not cond:
        _fails.append(name)


PS1 = ROOT / "naota-watchdog.ps1"
VBS = ROOT / "naota-watchdog.vbs"
BAT = ROOT / "naota-watchdog.bat"
check("naota-watchdog.ps1/.vbs/.bat exist at the repo root", PS1.exists() and VBS.exists() and BAT.exists())

src = PS1.read_text(encoding="utf-8")
for name, path in (("naota-watchdog.ps1", PS1), ("naota-watchdog.vbs", VBS), ("naota-watchdog.bat", BAT)):
    raw = path.read_bytes()
    check(f"{name} is plain ASCII (PowerShell 5.1 and wscript read the ANSI code page)", all(b < 128 for b in raw))
check("install/uninstall/check/status all present",
      all(f'"{k}"' in src for k in ("install", "uninstall", "check")) and "default" in src)
check("per-user scheduled task, repeats every minute and resumes at logon (no admin)",
      "Register-ScheduledTask" in src and "-RepetitionInterval (New-TimeSpan -Minutes 1)" in src and "-AtLogOn" in src)
check("task runs through the hidden vbs runner, not a visible powershell window",
      "naota-watchdog.vbs" in src and ", 0, True" in VBS.read_text(encoding="utf-8"))
check("restarts through start-naota.vbs (kills a hung server too)", "start-naota.vbs" in src)
check("honours NAOTA_PORT and NAOTA_STATE_DIR", "NAOTA_PORT" in src and "NAOTA_STATE_DIR" in src)
check("stays out of a running update (update_state.json, only while fresh)",
      "update_state.json" in src and "AddMinutes(-15)" in src)

stop = (ROOT / "stop-naota.ps1").read_text(encoding="utf-8")
start = (ROOT / "start-naota.vbs").read_text(encoding="utf-8")
check("stop-naota.ps1 leaves the stopped-on-purpose marker", "stopped-on-purpose" in stop)
check("start-naota.vbs removes the marker after its own stop step",
      "stopped-on-purpose" in start and start.index("stop-naota.bat") < start.index("DeleteFile marker"))
check("install.ps1 installs the watchdog with autostart", "naota-watchdog.ps1" in (ROOT / "install.ps1").read_text(
    encoding="utf-8"))


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


ps = shutil.which("powershell") if os.name == "nt" else None
if ps:
    dead_port = str(_free_port())

    def run(state_dir):
        env = dict(os.environ, NAOTA_PORT=dead_port, NAOTA_STATE_DIR=state_dir, NAOTA_WATCHDOG_FAILS="3",
                   NAOTA_WATCHDOG_KICK_CMD="echo KICKED")
        p = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PS1), "check"],
                           capture_output=True, text=True, env=env, timeout=120)
        return p.stdout + p.stderr

    def fails(state_dir):
        return (Path(state_dir) / "watchdog-fails").read_text(encoding="ascii").strip()

    with tempfile.TemporaryDirectory() as td:
        outs = [run(td) for _ in range(3)]
        check("misses 1 and 2 only count", "KICKED" not in outs[0] + outs[1], outs[1])
        check("miss 3 restarts and resets the count", "KICKED" in outs[2] and fails(td) == "0", outs[2])
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "stopped-on-purpose").write_text("x", encoding="ascii")
        out = "".join(run(td) for _ in range(4))
        check("stopped on purpose: never restarts", "KICKED" not in out and fails(td) == "0", out)
else:
    print("skip (not Windows): live check runs only where powershell is available")

print()
if _fails:
    print(f"{len(_fails)} test(s) FAILED: " + ", ".join(_fails))
    sys.exit(1)
print("All Windows watchdog tests passed.")
