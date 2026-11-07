"""
Database Layer for IQ Test Application
Uses SQLite3 for persistent storage of users, active test sessions,
and test results. Supports local environments and Vercel Serverless (/tmp/iq_test.db).
"""

import sqlite3
import json
import os
from datetime import datetime

# Vercel serverless functions have a read-only filesystem except for /tmp/
if os.environ.get("VERCEL") or not os.access(os.path.dirname(os.path.abspath(__file__)), os.W_OK):
    DB_FILE = "/tmp/iq_test.db"
else:
    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iq_test.db")


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for registered users (direct registration, is_verified=1 by default)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        is_verified INTEGER DEFAULT 1,
        session_token TEXT,
        created_at TEXT NOT NULL,
        verified_at TEXT
    );
    """)

    # Table for active test sessions (stores the randomized questions for that session)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_sessions (
        session_token TEXT PRIMARY KEY,
        user_id INTEGER,
        email TEXT,
        questions_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    # Table for IQ test submissions & detailed results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        email TEXT NOT NULL COLLATE NOCASE,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        iq_score INTEGER NOT NULL,
        percentile REAL NOT NULL,
        classification TEXT NOT NULL,
        category_scores_json TEXT NOT NULL,
        answers_json TEXT NOT NULL,
        time_taken_seconds INTEGER NOT NULL,
        certificate_id TEXT UNIQUE NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_email ON test_results(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_iq ON test_results(iq_score DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON active_sessions(session_token);")

    conn.commit()
    conn.close()


def register_user_direct(name: str, age: int, email: str, session_token: str):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()

    if existing:
        user_id = existing["id"]
        cursor.execute("""
            UPDATE users 
            SET name = ?, age = ?, is_verified = 1, session_token = ?, verified_at = ?
            WHERE id = ?
        """, (name, age, session_token, now_iso, user_id))
    else:
        cursor.execute("""
            INSERT INTO users (name, age, email, is_verified, session_token, created_at, verified_at)
            VALUES (?, ?, ?, 1, ?, ?, ?)
        """, (name, age, email, session_token, now_iso, now_iso))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "name": name,
        "age": age,
        "email": email,
        "session_token": session_token
    }


def save_active_session(session_token: str, user_id: int, email: str, questions: list):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    cursor.execute("""
        INSERT OR REPLACE INTO active_sessions (session_token, user_id, email, questions_json, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_token, user_id, email, json.dumps(questions), now_iso))

    conn.commit()
    conn.close()


def get_active_session_questions(session_token: str):
    if not session_token:
        return None
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT questions_json FROM active_sessions WHERE session_token = ?", (session_token,))
    row = cursor.fetchone()
    conn.close()
    if row and row["questions_json"]:
        try:
            return json.loads(row["questions_json"])
        except Exception:
            return None
    return None


def get_user_by_session(session_token: str):
    if not session_token:
        return None
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, email, is_verified FROM users WHERE session_token = ?", (session_token,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None


def save_test_result(user_id: int, email: str, name: str, age: int, iq_score: int, 
                     percentile: float, classification: str, category_scores: dict, 
                     answers: list, time_taken_seconds: int, certificate_id: str):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO test_results 
        (user_id, email, name, age, iq_score, percentile, classification, 
         category_scores_json, answers_json, time_taken_seconds, certificate_id, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, email, name, age, iq_score, percentile, classification,
        json.dumps(category_scores), json.dumps(answers),
        time_taken_seconds, certificate_id, now_iso
    ))

    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return result_id


def get_leaderboard(limit: int = 10):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, age, iq_score, percentile, classification, time_taken_seconds, completed_at
        FROM test_results
        ORDER BY iq_score DESC, time_taken_seconds ASC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_records():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, age, email, is_verified, created_at, verified_at
        FROM users
        ORDER BY id DESC
    """)
    users = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT id, user_id, email, name, age, iq_score, percentile, classification, 
               category_scores_json, time_taken_seconds, certificate_id, completed_at
        FROM test_results
        ORDER BY id DESC
    """)
    results = []
    for r in cursor.fetchall():
        row_dict = dict(r)
        try:
            row_dict["category_scores"] = json.loads(row_dict["category_scores_json"])
        except Exception:
            row_dict["category_scores"] = {}
        del row_dict["category_scores_json"]
        results.append(row_dict)

    conn.close()
    return {"users": users, "test_results": results}
