"""Zero-Dependency Local Server for AI Resume Screening.
Uses Python's standard library `http.server` so it runs immediately out-of-the-box
WITHOUT needing `pip install` or internet access!
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.handlers.presigned_url_handler import generate_presigned_url
from backend.handlers.s3_trigger_handler import process_resume_payload
from backend.services.dynamodb_service import DynamoDBService
from backend.services.matching_engine import MatchingEngine

db_service = DynamoDBService()
matching_engine = MatchingEngine()


class SimpleAPIHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/api":
            self._send_json(200, {
                "status": "online",
                "server": "AI Resume Screening Pipeline (Built-in HTTP Server)",
                "active_job": db_service.get_active_job().get("title"),
            })
        elif path == "/api/candidates":
            job_id = query.get("job_id", [None])[0]
            cands = db_service.list_candidates(job_id=job_id)
            self._send_json(200, {"count": len(cands), "candidates": cands})
        elif path.startswith("/api/candidates/"):
            cand_id = path.replace("/api/candidates/", "").strip("/")
            cand = db_service.get_candidate(cand_id)
            if cand:
                self._send_json(200, cand)
            else:
                self._send_json(404, {"error": "Candidate not found"})
        elif path == "/api/jobs":
            self._send_json(200, {"jobs": db_service.list_jobs()})
        elif path == "/api/jobs/active":
            self._send_json(200, db_service.get_active_job())
        else:
            self._send_json(404, {"error": f"Path '{path}' not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if path == "/api/upload-url":
            data = json.loads(body.decode("utf-8") or "{}")
            filename = data.get("filename", "resume.pdf")
            content_type = data.get("content_type", "application/pdf")
            job_id = data.get("job_id", "job-cloud-architect")
            res = generate_presigned_url(filename, content_type, job_id)
            self._send_json(200, res)

        elif path == "/api/upload-direct":
            # Direct file upload simulation
            filename = "uploaded_resume.txt"
            raw_content = body
            # Check if multipart form
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" in content_type:
                # Simple extraction of text content from multipart payload
                boundary = content_type.split("boundary=")[1].encode()
                parts = body.split(b"--" + boundary)
                for part in parts:
                    if b'filename="' in part:
                        headers_part, file_data = part.split(b"\r\n\r\n", 1)
                        file_data = file_data.rsplit(b"\r\n", 1)[0]
                        raw_content = file_data
                        import re
                        match = re.search(r'filename="([^"]+)"', headers_part.decode("utf-8", errors="ignore"))
                        if match:
                            filename = match.group(1)
                        break

            candidate = process_resume_payload(
                file_bytes=raw_content,
                filename=filename,
                s3_bucket="local-mock-bucket",
                s3_key=f"resumes/{filename}",
                job_id="job-cloud-architect",
            )
            self._send_json(200, {
                "status": "success",
                "message": f"Resume '{filename}' parsed and screened successfully.",
                "candidate": candidate,
            })

        elif path == "/api/candidates/rescore":
            parsed_query = urllib.parse.parse_qs(parsed.query)
            job_id = parsed_query.get("job_id", [None])[0]
            target_job = db_service.get_job(job_id) if job_id else db_service.get_active_job()
            cands = db_service.list_candidates(job_id=job_id)
            for c in cands:
                ev = matching_engine.evaluate_candidate(c, target_job)
                c.update({
                    "match_score": ev["match_score"],
                    "status": ev["status"],
                    "badge_color": ev["badge_color"],
                    "verdict": ev["verdict"],
                    "summary": ev["summary"],
                    "matched_skills": ev["matched_skills"],
                    "missing_skills": ev["missing_skills"],
                    "breakdown": ev["breakdown"],
                })
                db_service.save_candidate(c)
            updated = db_service.list_candidates(job_id=target_job["job_id"])
            self._send_json(200, {"message": "Rescored candidates", "candidates": updated})

        elif path == "/api/jobs":
            data = json.loads(body.decode("utf-8") or "{}")
            saved = db_service.save_job(data)
            self._send_json(201, {"message": "Job created", "job": saved})

        else:
            self._send_json(404, {"error": f"Path '{path}' not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/candidates/"):
            cand_id = path.replace("/api/candidates/", "").strip("/")
            success = db_service.delete_candidate(cand_id)
            self._send_json(200, {"success": success, "deleted_id": cand_id})
        else:
            self._send_json(404, {"error": f"Path '{path}' not found"})


def run(port: int = 8000):
    server = HTTPServer(("0.0.0.0", port), SimpleAPIHandler)
    print(f"[INFO] Server running on http://localhost:{port}")
    print("[INFO] Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped.")


if __name__ == "__main__":
    run(8000)
