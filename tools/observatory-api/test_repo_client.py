"""Offline tests: no Docker Engine, no live Gateway auth, no real Repo secret."""
from contextlib import redirect_stdout
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RepoApiClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.client = load("client_test", "fortis_observatory_client.py")
        self.client.ROOT = self.base / "private"
        self.client.TOKEN = self.client.ROOT / "token"

    def test_key_is_private_and_not_printed_and_reused(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.client.init_key()
        key = self.client.read_token()
        self.assertEqual(self.client.TOKEN.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.client.ROOT.stat().st_mode & 0o777, 0o700)
        self.assertNotIn(key, out.getvalue())
        self.assertIn(hashlib.sha256(key.encode()).hexdigest(), out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.client.init_key()
        self.assertEqual(self.client.read_token(), key)

    def test_http_authority_and_auth_are_correct(self):
        self.client.init_key()
        wanted_key = self.client.read_token()

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                correct = (self.headers.get("Host") == "fortis-observatory-api:18756"
                           and self.headers.get("Authorization") == "Bearer " + wanted_key
                           and self.path == "/v1/health")
                payload = json.dumps({"ok": True, "mode": "staging_only"}).encode()
                self.send_response(200 if correct else 403)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.daemon_threads = True
        self.addCleanup(server.server_close)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.shutdown)
        self.client.HOST = "127.0.0.1"
        self.client.PORT = server.server_address[1]
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(self.client.request("GET", "/v1/health"), 0)
        self.assertIn('"ok": true', out.getvalue())

    def test_payload_schema_validation(self):
        path = self.base / "event.json"
        path.write_text(json.dumps({"request_id": "req_" + "1"*32, "chat_id": "chat-12345678",
                                    "task_id": "task_" + "2"*32, "event": "progress",
                                    "stage": "testing", "summary": "test",
                                    "sequence": 0, "detail": None}))
        self.assertEqual(self.client.read_payload(str(path), "events")["stage"], "testing")
        path.write_text('{"request_id":"a","request_id":"b"}')
        with self.assertRaises(ValueError):
            self.client.read_payload(str(path), "events")


class GatewayConfigUpdaterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.private = self.base / "private"
        self.private.mkdir(mode=0o700)
        self.requestfile = self.base / "request.json"
        self.update = load("update_test", "add_repo_client.py")
        self.update.PRIVATE = self.private
        self.update.CONFIG = self.private / "clients.json"
        self.update.REQUEST = self.requestfile
        self.cfg = {"version": 1, "clients": [
            {"id": "windows", "scope": "all_registered", "chats": [],
             "token_sha256": "f"*64, "permissions": ["read:metadata"]}]}
        self.update.CONFIG.write_text(json.dumps(self.cfg))
        self.update.CONFIG.chmod(0o600)
        self.entry = {"id": "fortis-repo", "token_sha256": "e"*64,
                      "permissions": ["read:metadata", "read:history"],
                      "chats": ["chat-12345678", "chat-23456789"]}
        self.requestfile.write_text(json.dumps(self.entry))

    def test_atomic_add_preserves_windows_owner(self):
        with redirect_stdout(io.StringIO()):
            self.update.main()
        new = json.loads(self.update.CONFIG.read_text())
        self.assertEqual(new["clients"][0], self.cfg["clients"][0])
        self.assertEqual(new["clients"][1], self.entry)
        self.assertEqual(self.update.CONFIG.stat().st_mode & 0o777, 0o600)
        backups = list(self.private.glob("clients.json.before-fortis-repo-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), self.cfg)
        with redirect_stdout(io.StringIO()):
            self.update.main()
        self.assertEqual(len(list(self.private.glob("clients.json.before-fortis-repo-*"))), 1)

    def test_refuses_different_existing_key_without_mutation(self):
        with redirect_stdout(io.StringIO()):
            self.update.main()
        raw = self.update.CONFIG.read_bytes()
        self.entry["token_sha256"] = "a"*64
        self.requestfile.write_text(json.dumps(self.entry))
        with self.assertRaises(ValueError):
            self.update.main()
        self.assertEqual(self.update.CONFIG.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
