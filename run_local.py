#!/usr/bin/env python3
"""Build and serve the Vite app on localhost, then open it in a browser.

Usage from the repository root:
    py run_local.py

Optional: set PORT=8765 before running. Requires Python 3 and pnpm (or npm).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8765"))


def build_app() -> None:
    if shutil.which("pnpm"):
        command = ["pnpm", "build"]
    elif shutil.which("npm"):
        command = ["npm", "run", "build"]
    else:
        raise RuntimeError("Node.js and pnpm (or npm) are required to build the app.")

    env = os.environ.copy()
    env["VITE_BASE_PATH"] = "/"
    subprocess.run(command, cwd=ROOT, env=env, check=True)

    if not (DIST / "index.html").is_file():
        raise RuntimeError("Vite build completed but dist/index.html was not found.")


class LocalAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def end_headers(self) -> None:
        # Required by SharedArrayBuffer/WebAssembly threads used by the app.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        print("[localhost] " + (fmt % args))


def main() -> int:
    try:
        build_app()
        server = ThreadingHTTPServer((HOST, PORT), LocalAppHandler)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Could not start the local app: {exc}", file=sys.stderr)
        return 1

    url = f"http://{HOST}:{PORT}/"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Wait until the local server responds before opening the browser.
    for _ in range(50):
        try:
            with urllib.request.urlopen(url, timeout=1):
                break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    else:
        server.shutdown()
        print("The local server did not become ready.", file=sys.stderr)
        return 1

    print(f"Game is running at {url}. Press Ctrl+C to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local server...")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
