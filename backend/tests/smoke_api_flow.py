"""
Smoke test for ExamBuddy protected API flow.

Flow:
1) GET /api/questions
2) POST /api/questions
3) GET /api/questions (verify created)
4) POST /api/exams/start
5) POST /api/exams/{session_id}/answers
6) POST /api/exams/{session_id}/submit

Usage examples:
  python tests/smoke_api_flow.py --base-url https://.../prod --token-file ../id_token.txt
  python tests/smoke_api_flow.py --base-url https://.../prod --use-fallback-token
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import uuid
from typing import Any, Dict, Optional, Tuple
from urllib import error, request


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def make_fallback_token() -> str:
    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "sub": "smoke-user",
        "token_use": "access",
        "exp": int(time.time()) + 3600,
        "email": "smoke@example.com",
    }
    return f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(payload).encode())}.sig"


def load_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token.strip()

    if args.token_file:
        with open(args.token_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()

    env_token = os.getenv("EXAMBUDDY_BEARER_TOKEN", "").strip()
    if env_token:
        return env_token

    if args.use_fallback_token:
        return make_fallback_token()

    raise ValueError(
        "No token provided. Use --token, --token-file, EXAMBUDDY_BEARER_TOKEN, or --use-fallback-token."
    )


def call_api(
    method: str,
    url: str,
    token: str,
    body: Optional[Dict[str, Any]] = None,
    origin: str = "http://localhost:5175",
) -> Tuple[int, Dict[str, str], Any]:
    payload_bytes = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": origin,
    }

    if body is not None:
        payload_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, method=method, headers=headers, data=payload_bytes)

    try:
        with request.urlopen(req, timeout=20) as resp:
            status = resp.getcode()
            resp_headers = dict(resp.headers.items())
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        status = exc.code
        resp_headers = dict(exc.headers.items()) if exc.headers else {}
        raw = exc.read().decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Request failed {method} {url}: {exc}") from exc

    try:
        data = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        data = raw

    return status, resp_headers, data


def expect(status: int, allowed: Tuple[int, ...], label: str, data: Any) -> None:
    if status not in allowed:
        raise AssertionError(
            f"{label} failed. expected {allowed}, got {status}. response={data}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="ExamBuddy protected API smoke test")
    parser.add_argument(
        "--base-url",
        default="https://ugx3jtet03.execute-api.eu-north-1.amazonaws.com/prod",
        help="API base URL",
    )
    parser.add_argument("--token", default="", help="Bearer token value")
    parser.add_argument("--token-file", default="", help="Path to file containing bearer token")
    parser.add_argument(
        "--use-fallback-token",
        action="store_true",
        help="Generate a syntactically valid fallback token (for fallback runtime testing)",
    )
    parser.add_argument("--origin", default="http://localhost:5175", help="Origin header")
    args = parser.parse_args()

    token = load_token(args)
    base = args.base_url.rstrip("/")
    created_text = f"Smoke question {uuid.uuid4().hex[:8]}"

    print("[1/6] GET /api/questions")
    status, _, data = call_api("GET", f"{base}/api/questions", token, origin=args.origin)
    expect(status, (200,), "GET /api/questions", data)

    print("[2/6] POST /api/questions")
    new_question = {
        "text": created_text,
        "answer_options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer_index": 1,
        "project_id": "default",
    }
    status, _, data = call_api("POST", f"{base}/api/questions", token, new_question, origin=args.origin)
    expect(status, (201,), "POST /api/questions", data)
    created_id = data.get("question_id") if isinstance(data, dict) else None

    print("[3/6] GET /api/questions (verify create)")
    status, _, data = call_api("GET", f"{base}/api/questions", token, origin=args.origin)
    expect(status, (200,), "GET /api/questions verify", data)
    items = data.get("items", []) if isinstance(data, dict) else []
    if not any(q.get("question_id") == created_id or q.get("text") == created_text for q in items):
        raise AssertionError("Created question not found in questions list")

    print("[4/6] POST /api/exams/start")
    start_payload = {
        "project_id": "default",
        "mode": "test",
        "difficulty": "easy",
        "question_count": 1,
    }
    status, _, data = call_api("POST", f"{base}/api/exams/start", token, start_payload, origin=args.origin)
    expect(status, (201,), "POST /api/exams/start", data)
    session_id = data.get("session_id")
    questions = data.get("questions", [])
    if not session_id or not questions:
        raise AssertionError("Exam start response missing session_id or questions")

    print("[5/6] POST /api/exams/{session_id}/answers")
    answer_payload = {
        "question_id": questions[0].get("question_id"),
        "answer_index": 1,
    }
    status, _, data = call_api(
        "POST",
        f"{base}/api/exams/{session_id}/answers",
        token,
        answer_payload,
        origin=args.origin,
    )
    expect(status, (200,), "POST /api/exams/{session_id}/answers", data)

    print("[6/6] POST /api/exams/{session_id}/submit")
    status, _, data = call_api(
        "POST",
        f"{base}/api/exams/{session_id}/submit",
        token,
        body={},
        origin=args.origin,
    )
    expect(status, (200,), "POST /api/exams/{session_id}/submit", data)

    print("\n✅ Smoke flow passed")
    print(json.dumps({
        "session_id": session_id,
        "attempt_id": data.get("attempt_id") if isinstance(data, dict) else None,
        "score": data.get("score") if isinstance(data, dict) else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\n❌ Smoke flow failed: {exc}")
        raise SystemExit(1)
