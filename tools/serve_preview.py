from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIEW_DIR = ROOT / "preview"
HOST = "127.0.0.1"
PORT = 8008


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    handler = partial(QuietHandler, directory=str(PREVIEW_DIR))
    server = ThreadingHTTPServer((HOST, PORT), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
