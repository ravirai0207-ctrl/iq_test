"""
Main HTTP REST Server for CognitiveIQ 3D Platform.
Supports direct instant registration (NO OTP), dynamic randomized question sessions,
SQLite persistence, and psychometric scoring.
"""

import os
import re
import json
import secrets
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

import database
import iq_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class IQAppRequestHandler(SimpleHTTPRequestHandler):

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

        if path == "/api/health":
            self.send_json_response({"status": "healthy", "service": "CognitiveIQ 3D Engine v2.0"})
            return

        elif path == "/api/questions":
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

        elif path == "/api/leaderboard":
            leaders = database.get_leaderboard(limit=10)
            self.send_json_response({"success": True, "leaderboard": leaders})
            return

        elif path == "/api/admin/records":
            records = database.get_all_records()
            self.send_json_response({"success": True, "data": records})
            return

        clean_path = path.lstrip("/")
        if clean_path == "" or clean_path == "index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
        else:
            file_path = os.path.join(STATIC_DIR, clean_path)

        real_file_path = os.path.abspath(file_path)
        if not real_file_path.startswith(STATIC_DIR):
            self.send_error(403, "Forbidden")
            return

        if os.path.exists(real_file_path) and os.path.isfile(real_file_path):
            mime_type, _ = mimetypes.guess_type(real_file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            if real_file_path.endswith(".js"):
                mime_type = "application/javascript"
            elif real_file_path.endswith(".css"):
                mime_type = "text/css"

            try:
                with open(real_file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", f"{mime_type}; charset=utf-8" if "text" in mime_type or "javascript" in mime_type else mime_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")
                return

        fallback_index = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(fallback_index):
            with open(fallback_index, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "Resource Not Found")

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

        # Direct Registration & Session Initialization (NO OTP!)
        if path in ["/api/register", "/api/start-session", "/api/request-otp"]:
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
                # If email is invalid or missing, generate a clean fallback email
                email = f"{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}@cognitivelabs.ai"

            # Generate secure session token
            session_token = secrets.token_urlsafe(32)

            # Direct registration in SQLite (NO OTP!)
            user_info = database.register_user_direct(name, age, email, session_token)

            # Use questions fetched from external server if provided, otherwise generate fresh
            client_server_questions = body.get("server_questions")
            if client_server_questions and isinstance(client_server_questions, list) and len(client_server_questions) >= 5:
                session_questions = client_server_questions
            else:
                session_questions = iq_engine.generate_fresh_session_questions(12)

            # Save questions into active_sessions in SQLite
            database.save_active_session(session_token, user_info["id"], email, session_questions)

            # Sanitize for client
            client_questions = iq_engine.sanitize_questions_for_client(session_questions)

            self.send_json_response({
                "success": True,
                "message": f"Welcome {name}! Test session initialized.",
                "session_token": session_token,
                "user": user_info,
                "questions": client_questions
            }, 200)
            return

        # Legacy verify-otp handler (direct bypass)
        elif path == "/api/verify-otp":
            email = (body.get("email") or "").strip().lower()
            session_token = secrets.token_urlsafe(32)
            self.send_json_response({
                "success": True,
                "session_token": session_token,
                "message": "Instant verification active."
            }, 200)
            return

        # Submit Test & Calculate IQ
        elif path == "/api/submit-test":
            session_token = body.get("session_token")
            auth_header = self.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                session_token = auth_header[7:].strip()

            if not session_token:
                self.send_json_response({"success": False, "error": "Active session token required."}, 401)
                return

            user = database.get_user_by_session(session_token)
            if not user:
                self.send_json_response({"success": False, "error": "Session expired or user not registered."}, 401)
                return

            # Retrieve the exact questions assigned to this session
            session_questions = database.get_active_session_questions(session_token)
            if not session_questions:
                # Fallback if session questions were lost
                session_questions = iq_engine.generate_fresh_session_questions(12)

            answers = body.get("answers", {})
            time_taken = int(body.get("time_taken_seconds", 300))

            # Psychometric calculation against the session's specific questions
            result = iq_engine.calculate_iq(
                user_age=user["age"],
                session_questions=session_questions,
                answers=answers,
                time_taken_seconds=time_taken
            )

            # Save in database
            result_id = database.save_test_result(
                user_id=user["id"],
                email=user["email"],
                name=user["name"],
                age=user["age"],
                iq_score=result["iq_score"],
                percentile=result["percentile"],
                classification=result["classification"],
                category_scores=result["category_scores"],
                answers=result["detailed_eval"],
                time_taken_seconds=time_taken,
                certificate_id=result["certificate_id"]
            )

            result["result_id"] = result_id
            result["user"] = {
                "name": user["name"],
                "age": user["age"],
                "email": user["email"]
            }

            self.send_json_response({
                "success": True,
                "result": result
            }, 200)
            return

        self.send_json_response({"success": False, "error": "Endpoint not found"}, 404)


def find_free_port(start_port=8000, max_attempts=50):
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main():
    database.init_db()
    port = find_free_port(8000)
    server_address = ("127.0.0.1", port)

    print("\n" + "=" * 65)
    print("🌟 COGNITIVE IQ LABS - 3D NEURAL TESTING ENGINE v2.0")
    print(f"🚀 Server initialized and listening at: http://localhost:{port}")
    print("✨ Direct Instant Registration (NO OTP)")
    print("🎲 Dynamic Multi-Server & Procedural Questions (Unique Every Test)")
    print(f"📊 SQLite Database: {database.DB_FILE}")
    print("=" * 65 + "\n")

    httpd = ThreadedHTTPServer(server_address, IQAppRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down cleanly...")
        httpd.server_close()


if __name__ == "__main__":
    main()
