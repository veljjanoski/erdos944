"""Safe, resumable job runner (Windows).  One supervisor process runs the jobs of a job file with a few workers.

Safety:
  * every worker process is placed in ONE Windows Job Object with a per-process committed-memory limit (--mem-gb, default 2)
    and a total limit for all workers (--total-gb, default 12); a process that exceeds its limit gets allocation failures
    (MemoryError) and exits; KILL_ON_JOB_CLOSE kills all workers if the supervisor dies, so nothing is left running;
  * workers run at BELOW_NORMAL priority with one BLAS/OpenMP thread;
  * no new job starts while free physical RAM is below --min-free-gb (default 6);
  * a file STOP next to the job file stops starting new jobs (running jobs finish); STOPNOW kills running jobs too;
  * every job has a wall-clock cap (--cap seconds, default 1800); over-cap jobs are killed and recorded as TIMEOUT.
Resumability: each finished job is appended (with fsync) to RESULTS as one JSON line; on restart, jobs whose last record
is DONE or TIMEOUT are skipped, FAILED jobs are retried at most --retries times.  Job stdout+stderr go to logs/<id>.out.
The number of workers can be changed while running by writing a number into workers.txt next to the job file.

Job file: one job per line, "ID<TAB>command line" (the command is run with the current python if it starts with
'python '); lines starting with # are ignored.  Commands are split like a POSIX shell (no shell is used): write paths
with forward slashes, never backslashes.  Job ids must be unique and usable as file names.  A job is DONE if it exits with code 0, FAILED otherwise.
Usage: python safe_run.py JOBS.txt RESULTS.jsonl [--workers 6] [--cap 1800] [--mem-gb 2] [--total-gb 12] [--min-free-gb 6]
"""
import sys, os, time, json, shlex, subprocess, ctypes, argparse
from ctypes import wintypes

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
k32.CreateJobObjectW.restype = wintypes.HANDLE
k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.CloseHandle.argtypes = [wintypes.HANDLE]

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                                                   'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', wintypes.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]
class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION), ('IoInfo', IO_COUNTERS),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]
JOB_OBJECT_LIMIT_PROCESS_MEMORY, JOB_OBJECT_LIMIT_JOB_MEMORY, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x100, 0x200, 0x2000
JobObjectExtendedLimitInformation = 9
PROCESS_SET_QUOTA, PROCESS_TERMINATE = 0x0100, 0x0001
BELOW_NORMAL_PRIORITY_CLASS = 0x4000

def make_job(mem_gb, total_gb):
    h = k32.CreateJobObjectW(None, None)
    if not h: raise OSError(ctypes.get_last_error(), 'CreateJobObject failed')
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_PROCESS_MEMORY | JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    info.ProcessMemoryLimit = int(mem_gb * 2**30); info.JobMemoryLimit = int(total_gb * 2**30)
    if not k32.SetInformationJobObject(h, JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info)):
        raise OSError(ctypes.get_last_error(), 'SetInformationJobObject failed')
    return h

def assign(job, pid):
    ph = k32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid)
    if not ph: raise OSError(ctypes.get_last_error(), 'OpenProcess failed')
    ok = k32.AssignProcessToJobObject(job, ph); err = ctypes.get_last_error(); k32.CloseHandle(ph)
    if not ok: raise OSError(err, 'AssignProcessToJobObject failed')

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', wintypes.DWORD), ('dwMemoryLoad', wintypes.DWORD), ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong), ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong), ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
def free_gb():
    m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(m); k32.GlobalMemoryStatusEx(ctypes.byref(m)); return m.ullAvailPhys / 2**30

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs'); ap.add_argument('results')
    ap.add_argument('--workers', type=int, default=6); ap.add_argument('--cap', type=float, default=1800)
    ap.add_argument('--mem-gb', type=float, default=2); ap.add_argument('--total-gb', type=float, default=12)
    ap.add_argument('--min-free-gb', type=float, default=6); ap.add_argument('--retries', type=int, default=1)
    a = ap.parse_args()
    sys.stdout.reconfigure(errors='replace')
    here = os.path.dirname(os.path.abspath(a.jobs)); logdir = os.path.join(here, 'logs'); os.makedirs(logdir, exist_ok=True)
    wfile, stop, stopnow = (os.path.join(here, f) for f in ('workers.txt', 'STOP', 'STOPNOW'))
    jobs = []
    for line in open(a.jobs, encoding='utf-8'):
        line = line.rstrip('\r\n')
        if not line.strip() or line.startswith('#'): continue
        jid, cmd = line.split('\t', 1); jobs.append((jid.strip(), cmd.strip()))
    ids = [j for j, _ in jobs]; dup = {j for j in ids if ids.count(j) > 1}
    bad = [j for j in ids if not j or any(ch in j for ch in '\\/:*?"<>|')]
    if dup or bad: sys.exit(f"job file error: duplicate ids {sorted(dup)[:5]}, ids unusable as file names {bad[:5]}")
    last, fails = {}, {}
    if os.path.exists(a.results):
        for line in open(a.results, encoding='utf-8'):
            try: r = json.loads(line)
            except ValueError: continue
            last[r['id']] = r['status']
            if r['status'] == 'FAILED': fails[r['id']] = fails.get(r['id'], 0) + 1
    todo = [j for j in jobs if last.get(j[0]) not in ('DONE', 'TIMEOUT') and fails.get(j[0], 0) <= a.retries]
    print(f"{len(jobs)} jobs, {len(jobs) - len(todo)} already finished/skipped, {len(todo)} to run", flush=True)
    job = make_job(a.mem_gb, a.total_gb)
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUNBUFFERED='1', PYTHONIOENCODING='utf-8')
    running = {}   # jid -> (Popen, start time, file)
    def record(jid, status, rc, t0):
        tail = ''
        try:
            with open(os.path.join(logdir, jid + '.out'), encoding='utf-8', errors='replace') as f: tail = f.read()[-400:].strip().splitlines()[-1:]
        except OSError: pass
        rec = dict(id=jid, status=status, rc=rc, seconds=round(time.time() - t0, 1), last=tail[0] if tail else '', time=time.strftime('%Y-%m-%d %H:%M:%S'))
        with open(a.results, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n'); f.flush(); os.fsync(f.fileno())
        print(f"[{rec['time']}] {jid}: {status} ({rec['seconds']} s) {rec['last'][:160]}", flush=True)
    queue = list(todo)
    while queue or running:
        nw = a.workers
        try: nw = int(open(wfile).read().strip())
        except (OSError, ValueError): pass
        if os.path.exists(stopnow):
            for jid, (p, t0, f) in running.items():
                rc = p.poll()
                if rc is None: p.kill(); p.wait(); f.close(); record(jid, 'KILLED', None, t0)
                else: f.close(); record(jid, 'DONE' if rc == 0 else 'FAILED', rc, t0)
            print('STOPNOW: all jobs killed', flush=True); break
        for jid, (p, t0, f) in list(running.items()):
            rc = p.poll()
            if rc is None and time.time() - t0 > a.cap:
                p.kill(); p.wait(); f.close(); del running[jid]; record(jid, 'TIMEOUT', None, t0); continue
            if rc is not None:
                f.close(); del running[jid]; record(jid, 'DONE' if rc == 0 else 'FAILED', rc, t0)
        if queue and len(running) < nw and not os.path.exists(stop):
            if free_gb() < a.min_free_gb:
                time.sleep(5); continue
            jid, cmd = queue.pop(0)
            try:
                args = shlex.split(cmd, posix=True)
                if args[0] == 'python': args[0] = sys.executable
                f = open(os.path.join(logdir, jid + '.out'), 'w', encoding='utf-8')
                p = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT, cwd=here, env=env, creationflags=BELOW_NORMAL_PRIORITY_CLASS)
            except Exception as ex:          # a bad job line must not take the supervisor (and all workers) down
                record(jid, 'FAILED', f'launch: {type(ex).__name__}: {ex}', time.time()); continue
            try: assign(job, p.pid)
            except OSError as e:
                p.kill(); p.wait(); f.close(); record(jid, 'FAILED', f'job-object: {e}', time.time()); continue
            running[jid] = (p, time.time(), f)
            continue
        if not queue and os.path.exists(stop) is False and not running: break
        if os.path.exists(stop) and not running: print('STOP file: no new jobs; exiting', flush=True); break
        time.sleep(1)
    print('runner finished', flush=True)

if __name__ == '__main__':
    main()
