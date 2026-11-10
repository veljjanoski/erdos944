"""Stop the cube-mode workers of a safe_run job set WITHOUT losing work: each worker is killed right after it appends
its next finished cube to its progress file (a cube boundary), so at most --poll seconds of the following cube are lost.

The workers of the four PSL(2,8) shards spend hours on single cubes, and progress is only recorded per cube, so a plain
STOPNOW loses up to several hours per worker.  This watcher waits for each worker's next progress line instead.

    python stop_at_boundary.py runs/sweep9 [--jobs jobs_cubes2.txt] [--by HH:MM] [--poll 5] [--dry-run]

  * matches running python processes to the job file's commands (the process command line must end with the job's
    arguments and its parent must be the safe_run.py of that job file), and each cube job to its progress file
    progress/<spec>_r<r>_d<a>-<b>_s<k>_fp*_A*[_shard<i>of<m>].txt;
  * --by HH:MM: deadline (today, or tomorrow if already past); workers still busy then are killed anyway, and the
    lost in-progress time is printed;
  * --dry-run: only report the workers and how long each has been on its current cube.
After a kill the runner records the job as FAILED and goes on; it exits by itself once nothing is running and nothing
is queued.  Resume with the usual run script (run_cubes2.sh drops non-DONE records, so the killed jobs restart and
skip every finished cube).  The STOP/STOPNOW files are not touched.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def python_processes():
    """[(pid, parent pid, command line)] of every python.exe, via PowerShell/CIM (no psutil on this machine)."""
    cmd = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
           "Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True).stdout.strip()
    if not out: return []
    d = json.loads(out)
    if isinstance(d, dict): d = [d]
    return [(p["ProcessId"], p["ParentProcessId"], p["CommandLine"] or "") for p in d]


def read_jobs(path):
    jobs = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line.strip() or line.startswith("#"): continue
        jid, cmd = line.split("\t", 1)
        jobs.append((jid.strip(), cmd.strip()))
    return jobs


def progress_pattern(cmd):
    """Glob pattern of the progress file a cube job writes, or None if the job is not a cube job."""
    a = shlex.split(cmd, posix=True)
    if len(a) < 6 or not a[1].endswith("cegar944s.py") or "--cubes" not in a: return None
    spec, r, dmin, dmax = a[2].replace("|", "_"), a[3], a[4], a[5]
    k = a[a.index("--sigma") + 1] if "--sigma" in a else "id"
    pat = os.path.join(HERE, "progress", f"{spec}_r{r}_d{dmin}-{dmax}_s{k}_fp*_A*")
    if "--shard" in a:
        i, m = a[a.index("--shard") + 1].split("/")
        return pat + f"_shard{i}of{m}.txt"
    return pat + ".txt"


def find_file(pat):
    """The one progress file matching pat (whole-lane pattern must not pick up shard files)."""
    shard = "_shard" in os.path.basename(pat)
    hits = [f for f in glob.glob(pat) if shard or "_shard" not in os.path.basename(f)]
    if len(hits) > 1: sys.exit(f"ambiguous progress files for {pat}: {hits}")
    return hits[0] if hits else None


def last_cube(path):
    key, n = None, 0
    try:
        for l in open(path):
            f4 = l.split()
            if len(f4) == 4 and f4[1] == "NO": key, n = f4[0], n + 1
    except OSError: pass
    return key, n


def fmt(sec): return f"{sec / 3600:.1f} h" if sec >= 3600 else f"{sec / 60:.0f} min"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir"); ap.add_argument("--jobs", default="jobs_cubes2.txt")
    ap.add_argument("--by", help="HH:MM deadline; busy workers are killed then anyway")
    ap.add_argument("--poll", type=float, default=5); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    jobfile = os.path.join(a.rundir, a.jobs)
    jobs = read_jobs(jobfile)
    deadline = None
    if a.by:
        h, m = map(int, a.by.split(":"))
        deadline = dt.datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        if deadline <= dt.datetime.now(): deadline += dt.timedelta(days=1)
    procs = python_processes()
    parents = {pid for pid, _, cl in procs if "safe_run.py" in cl and os.path.basename(jobfile) in cl}
    if not parents: sys.exit(f"no safe_run.py running {os.path.basename(jobfile)} found")
    watched = {}      # pid -> dict(id, cmd, pat, file, size0)
    for pid, ppid, cl in procs:
        if ppid not in parents: continue
        norm = " ".join(cl.split())
        for jid, cmd in jobs:
            args = " ".join(shlex.split(cmd, posix=True)[1:])
            if norm.endswith(" " + args):
                pat = progress_pattern(cmd); f = find_file(pat) if pat else None
                watched[pid] = dict(id=jid, args=args, pat=pat, file=f, size0=os.path.getsize(f) if f else 0)
    if not watched: sys.exit("no running workers of this job file")
    now = time.time(); loss = 0
    for pid, w in watched.items():
        if w["file"]:
            key, n = last_cube(w["file"]); age = now - os.path.getmtime(w["file"]); loss += age
            print(f"{w['id']} (pid {pid}): {n} cubes in file, last {key}, on its current cube for {fmt(age)}")
        else:
            print(f"{w['id']} (pid {pid}): no progress file yet" + ("" if w["pat"] else " (not a cube job: deadline only)"))
    print(f"killing all {len(watched)} now would lose {fmt(loss)} of work" + (f"; deadline {deadline:%H:%M}" if deadline else ""))
    if a.dry_run: return
    print(f"waiting for each worker's next finished cube (poll {a.poll:g} s) ...", flush=True)
    while watched:
        time.sleep(a.poll)
        alive = {pid: " ".join(cl.split()) for pid, _, cl in python_processes()}
        for pid in list(watched):
            w = watched[pid]
            if pid not in alive or not alive[pid].endswith(" " + w["args"]):    # gone (or the pid reused): never kill
                print(f"[{time.strftime('%H:%M:%S')}] {w['id']}: exited by itself", flush=True); del watched[pid]; continue
            if w["pat"] and not w["file"]: w["file"] = find_file(w["pat"])
            grown = w["file"] is not None and os.path.getsize(w["file"]) > w["size0"]
            due = deadline is not None and dt.datetime.now() >= deadline
            if grown or due:
                try: os.kill(pid, signal.SIGTERM)
                except OSError as e: print(f"kill {pid} failed: {e}"); del watched[pid]; continue
                key, n = last_cube(w["file"]) if w["file"] else (None, 0)
                why = f"after cube {key} ({n} cubes in file; <= {a.poll:g} s lost)" if grown else \
                      f"at the deadline (lost {fmt(time.time() - os.path.getmtime(w['file'])) if w['file'] else 'unknown'} of work)"
                print(f"[{time.strftime('%H:%M:%S')}] killed {w['id']} (pid {pid}) {why}", flush=True)
                del watched[pid]
    print("all workers stopped; the runner exits on its own. Resume: bash run_cubes2.sh in the run dir.")


if __name__ == "__main__":
    main()
