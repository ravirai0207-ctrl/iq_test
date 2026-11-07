"""
Vercel Serverless Function Handler for CognitiveIQ 3D Engine.
Handles all /api/* routes on Vercel's global edge network.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import secrets
import re
from urllib.parse import urlparse, parse_qs

# Add root directory to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import database
import iq_engine

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class handler(BaseHTTPRequestHandler):

    def send_json_response(self, data, status_code=200):
        encoded = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.endswith("/health") or path == "/api/health":
            self.send_json_response({"status": "healthy", "service": "CognitiveIQ Vercel Edge Serverless"})
            return

        elif path.endswith("/questions") or path == "/api/questions":
            session_token = query.get("session_token", [None])[0]
            if session_token:
                session_q = database.get_active_session_questions(session_token)
                if session_q:
                    clean = iq_engine.sanitize_questions_for_client(session_q)
                    self.send_json_response({"success": True, "questions": clean})
                    return

            fresh_q = iq_engine.generate_fresh_session_questions(12)
            clean = iq_engine.sanitize_questions_for_client(fresh_q)
            self.send_json_response({"success": True, "questions": clean})
            return

        elif path.endswith("/leaderboard") or path == "/api/leaderboard":
            leaders = database.get_leaderboard(limit=10)
            self.send_json_response({"success": True, "leaderboard": leaders})
            return

        elif path.endswith("/admin/records") or path == "/api/admin/records":
            records = database.get_all_records()
            self.send_json_response({"success": True, "data": records})
            return

        self.send_json_response({"success": False, "error": f"API endpoint not found: {path}"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self.send_json_response({"success": False, "error": "Invalid JSON payload"}, 400)
            return

        if any(path.endswith(p) for p in ["/register", "/start-session", "/request-otp"]):
            name = (body.get("name") or "").strip()
            age_raw = body.get("age")
            email = (body.get("email") or "").strip().lower()

            if not name or len(name) < 2:
                self.send_json_response({"success": False, "error": "Please enter a valid full name."}, 400)
                return

            try:
                age = int(age_raw)
                if age < 6 or age > 120:
                    raise ValueError()
            except Exception:
                self.send_json_response({"success": False, "error": "Please enter an age between 6 and 120."}, 400)
                return

            if not email or not EMAIL_REGEX.match(email):
                email = f"{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}@cognitivelabs.ai"

            session_token = secrets.token_urlsafe(32)
            user_info = database.register_user_direct(name, age, email, session_token)

            client_server_questions = body.get("server_questions")
            if client_server_questions and isinstance(client_server_questions, list) and len(client_server_questions) >= 5:
                session_questions = client_server_questions
            else:
                session_questions = iq_engine.generate_fresh_session_questions(12)

            database.save_active_session(session_token, user_info["id"], email, session_questions)
            client_questions = iq_engine.sanitize_questions_for_client(session_questions)

            self.send_json_response({
                "success": True,
                "message": f"Welcome {name}! Test session initialized.",
                "session_token": session_token,
                "user": user_info,
                "questions": client_questions
            }, 200)
            return

        elif path.endswith("/submit-test"):
            session_token = body.get("session_token")
            auth_header = self.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                session_token = auth_header[7:].strip()

            if not session_token:
                self.send_json_response({"success": False, "error": "Active session token required."}, 401)
                return

            user = database.get_user_by_session(session_token)
            if not user:
                # If serverless container restarted, build a fallback user
                user = {"id": 1, "name": body.get("name", "Candidate"), "age": int(body.get("age", 25)), "email": "user@cognitivelabs.ai"}

            session_questions = database.get_active_session_questions(session_token)
            if not session_questions:
                session_questions = body.get("questions") or iq_engine.generate_fresh_session_questions(12)

            answers = body.get("answers", {})
            time_taken = int(body.get("time_taken_seconds", 300))

            result = iq_engine.calculate_iq(
                user_age=user.get("age", 25),
                session_questions=session_questions,
                answers=answers,
                time_taken_seconds=time_taken
            )

            try:
                result_id = database.save_test_result(
                    user_id=user.get("id", 1),
                    email=user.get("email", "user@cognitivelabs.ai"),
                    name=user.get("name", "Candidate"),
                    age=user.get("age", 25),
                    iq_score=result["iq_score"],
                    percentile=result["percentile"],
                    classification=result["classification"],
                    category_scores=result["category_scores"],
                    answers=result["detailed_eval"],
                    time_taken_seconds=time_taken,
                    certificate_id=result["certificate_id"]
                )
            except Exception:
                result_id = 1

            result["result_id"] = result_id
            result["user"] = {
                "name": user.get("name", "Candidate"),
                "age": user.get("age", 25),
                "email": user.get("email", "user@cognitivelabs.ai")
            }

            self.send_json_response({
                "success": True,
                "result": result
            }, 200)
            return

        self.send_json_response({"success": False, "error": f"Endpoint not found: {path}"}, 404)

