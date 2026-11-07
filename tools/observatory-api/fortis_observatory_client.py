#!/usr/bin/env python3
"""Fortis Repo -> Observatory Gateway client. Standard library only.

Does not use the Windows owner bearer. The Repo secret lives outside Git under
a 0700 private directory of the shared Docker workspace volume. Other
containers mounting the whole workspace as UID 1000 may also read that key;
see README before granting write scopes. No Docker network changes required
on the verified 2026-11-04 Docker Desktop topology.
"""
from __future__ import annotations

import argparse
import hashlib
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
from urllib.parse import urlencode

ROOT = Path("/workspace/repo/.fortis-observatory-repo-client")
TOKEN = ROOT / "token"
HOST = "host.docker.internal"
PORT = 18756
# The Gateway rejects host.docker.internal Host. The correct virtual service
# authority was independently verified to return HTTP 401 without a token.
HTTP_HOST = "fortis-observatory-api:18756"

SID = re.compile(r"rs_[0-9a-f]{32}\Z")
TASK = re.compile(r"task_[0-9a-f]{32}\Z")
REQ = re.compile(r"req_[0-9a-f]{32}\Z")


def secure_directory() -> None:
    if ROOT.is_symlink():
        raise ValueError("Refusing symlink for private directory")
    if not ROOT.exists():
        ROOT.mkdir(mode=0o700)
    metadata = ROOT.lstat()
    if (not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o700):
        raise ValueError("Private directory must be owned by UID 1000 with mode 0700")


def read_token() -> str:
    secure_directory()
    meta = TOKEN.lstat()
    if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.geteuid()
            or stat.S_IMODE(meta.st_mode) != 0o600 or meta.st_size > 200):
        raise ValueError("Client token owner, mode or size refused")
    token = TOKEN.read_text(encoding="ascii")
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,128}", token):
        raise ValueError("Client token format invalid")
    return token


def init_key() -> None:
    secure_directory()
    if not TOKEN.exists() and not TOKEN.is_symlink():
        key = secrets.token_urlsafe(48)
        fd = os.open(TOKEN, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="ascii") as output:
            output.write(key)
            output.flush()
            os.fsync(output.fileno())
    key = read_token()
    print("REPO_CLIENT_TOKEN=READY (not printed)")
    print("REPO_CLIENT_SHA256=" + hashlib.sha256(key.encode("ascii")).hexdigest())


def forbid_json_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("Duplicate field in JSON payload")
        obj[key] = value
    return obj


def request(method: str, endpoint: str, payload=None) -> int:
    key = read_token()
    headers = {"Host": HTTP_HOST, "Authorization": "Bearer " + key,
               "Accept": "application/json"}
    body = None
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(body) > 350 * 1024:
            raise ValueError("Request exceeds Gateway body limit")
        headers["Content-Type"] = "application/json"
    client = HTTPConnection(HOST, PORT, timeout=6)
    try:
        client.request(method, endpoint, body=body, headers=headers)
        response = client.getresponse()
        raw = response.read(512 * 1024)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Unexpected Gateway response (not JSON)") from None
        if not isinstance(data, dict):
            raise ValueError("Unexpected Gateway response (not object)")
        if response.status >= 400:
            print(json.dumps({"http_status": response.status, "error": data.get("error", "request_failed")}, ensure_ascii=False))
            return 1
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    finally:
        client.close()


def valid(pattern, value: str, name: str) -> str:
    if not pattern.fullmatch(value):
        raise ValueError("Invalid " + name)
    return value


def read_payload(path: str, action: str):
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 350 * 1024:
        raise ValueError("Payload file unavailable/too large")
    obj = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=forbid_json_duplicates)
    if not isinstance(obj, dict):
        raise ValueError("Payload must be an object")
    expected = ({"request_id", "chat_id", "task_id", "event", "stage", "summary",
                 "sequence", "detail"} if action == "events" else
                {"request_id", "chat_id", "task_id", "kind", "body"})
    if set(obj) != expected:
        raise ValueError("Invalid payload field set for " + action)
    valid(REQ, obj["request_id"], "request_id")
    valid(TASK, obj["task_id"], "task_id")
    return obj


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("init-key", help="Make/reuse private Repo token and print only its SHA-256")
    for simple in ("health", "sessions"):
        subs.add_parser(simple)
    ev = subs.add_parser("events")
    ev.add_argument("session_id")
    history = subs.add_parser("history")
    history.add_argument("session_id")
    history.add_argument("task_id")
    rec = subs.add_parser("receipt")
    rec.add_argument("request_id")
    for cmd in ("stage-event", "stage-message"):
        op = subs.add_parser(cmd)
        op.add_argument("json_file")
    args = parser.parse_args(argv)

    if args.command == "init-key":
        init_key()
        return 0
    if args.command in ("health", "sessions"):
        return request("GET", "/v1/" + args.command)
    if args.command == "events":
        sid = valid(SID, args.session_id, "session_id")
        return request("GET", "/v1/sessions/" + sid + "/events")
    if args.command == "history":
        sid = valid(SID, args.session_id, "session_id")
        tid = valid(TASK, args.task_id, "task_id")
        return request("GET", "/v1/history?" + urlencode({"session": sid, "task": tid}))
    if args.command == "receipt":
        rid = valid(REQ, args.request_id, "request_id")
        return request("GET", "/v1/requests/" + rid)
    if args.command in ("stage-event", "stage-message"):
        action = "events" if args.command == "stage-event" else "messages"
        return request("POST", "/v1/" + action, read_payload(args.json_file, action))
    parser.error("Unrecognized command")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        # Avoid printing raw auth tokens or HTTP request bodies.
        print("CLIENT_ERROR: " + str(exc), file=sys.stderr)
        sys.exit(2)
