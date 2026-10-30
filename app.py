from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)


def validate_url(url):
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
    except Exception:
        return False


@app.route("/api/test", methods=["POST"])
def test_website():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not validate_url(url):
        return jsonify({
            "success": False,
            "error": "Enter a valid HTTP or HTTPS URL.",
            "logs": ["[ERROR] Invalid website URL"]
        }), 400

    logs = [
        "[INFO] Testing started",
        "[INFO] Website URL validated",
        "[INFO] Sending HTTP request"
    ]

    start_time = time.perf_counter()

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            stream=True
        )

        response_time = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        status_code = response.status_code
        response.close()

        success = 200 <= status_code < 400

        logs.append(f"[INFO] HTTP status: {status_code}")
        logs.append(f"[INFO] Response time: {response_time} ms")
        logs.append(
            "[PASS] Website is accessible"
            if success
            else "[FAIL] Website returned an unsuccessful status"
        )

        return jsonify({
            "success": success,
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time,
            "logs": logs
        })

    except requests.RequestException as exc:
        logs.append(f"[ERROR] Request failed: {type(exc).__name__}")

        return jsonify({
            "success": False,
            "url": url,
            "error": "Website could not be reached or the request failed.",
            "logs": logs
        }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)