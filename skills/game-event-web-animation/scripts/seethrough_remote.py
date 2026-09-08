"""See-through sample worker: continuous SSE and local-only status polling."""
from __future__ import annotations
import argparse
import json
import os
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = "https://24yearsold-see-through-demo.hf.space"
AUTH_TOKEN = None

def read_user_token(name):
    """Read only the explicitly selected Windows User environment value."""
    if os.name != "nt":
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value if isinstance(value, str) and value else None
    except FileNotFoundError:
        return None

def load_token(name):
    return os.environ.get(name) or read_user_token(name)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a credential to an unreviewed redirect destination.
        return None

def request(path, payload=None, timeout=45):
    headers = {"Content-Type": "application/json", "User-Agent": "layer-validation/2.0"}
    if AUTH_TOKEN:
        headers["Authorization"] = "Bearer " + AUTH_TOKEN
    req = urllib.request.Request(BASE + path,
        data=None if payload is None else json.dumps(payload).encode(), headers=headers)
    return urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout)

def save(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)

def consume_queue(out, job, stream, budget=300):
    """Keep ONE stream open across heartbeats; preserve full terminal errors."""
    start = time.monotonic()
    with (out / "events.jsonl").open("a", encoding="utf-8") as log:
        while time.monotonic() - start < budget:
            raw = stream.readline()
            if not raw:
                break
            line = raw.decode("utf-8").strip()
            if not line.startswith("data: "):
                continue
            msg = json.loads(line[6:])
            log.write(json.dumps(msg, ensure_ascii=False) + "\n")
            log.flush()
            job["last_event"] = msg.get("msg")
            job["updated_at"] = time.time()
            if msg.get("msg") == "process_completed":
                output = msg.get("output") or {}
                data = output.get("data")
                valid = (msg.get("success") is True and isinstance(data, list)
                         and len(data) == 2 and isinstance(data[0], dict)
                         and bool(data[0].get("url") or data[0].get("path")))
                job["status"] = "RESULT_READY" if valid else "FAILED"
                if not valid:
                    job["error"] = output.get("error") or "Server returned no PSD descriptor"
                    job["error_title"] = output.get("title") or msg.get("title")
                save(out / "result.json", msg)
                save(out / "job.json", job)
                return 0 if valid else 2
            if msg.get("msg") == "unexpected_error":
                job["status"] = "FAILED"
                job["error"] = msg.get("message", "Queue session lost")
                save(out / "result.json", msg)
                save(out / "job.json", job)
                return 2
            save(out / "job.json", job)
    job["status"] = "FAILED"
    job["error"] = "Stream ended or budget elapsed without terminal result; session is not resumable"
    save(out / "job.json", job)
    return 2

def main():
    global AUTH_TOKEN
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["probe", "run-sample", "poll"])
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--hf-token-env", help="Explicit process/User environment variable name; never the token value")
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if a.action == "poll":
        job = json.loads((a.out / "job.json").read_text(encoding="utf-8"))
        print(json.dumps(job, ensure_ascii=True))
        return 2 if job["status"] == "FAILED" else 0
    if a.hf_token_env:
        AUTH_TOKEN = load_token(a.hf_token_env)
        if not AUTH_TOKEN:
            raise RuntimeError("Explicitly selected token variable is empty")
    if a.action == "run-sample" and (a.out / "job.json").exists():
        raise RuntimeError("Job exists; deliberate retries require a fresh output directory")
    with request("/config", timeout=20) as r:
        config = json.load(r)
    deps = [d for d in config["dependencies"] if d.get("api_name") == "inference"]
    if len(deps) != 1 or len(deps[0]["inputs"]) != 4 or len(deps[0]["outputs"]) != 2:
        raise RuntimeError("API contract changed; inspect config before inference")
    sample = next(c["props"]["samples"][0] for c in config["components"] if c["type"] == "dataset")
    save(a.out / "probe.json", {"endpoint": BASE, "version": config["version"],
                               "inference": deps[0], "sample": sample})
    if a.action == "probe":
        print(json.dumps({"status": "API_REACHABLE", "version": config["version"]}))
        return 0
    session = uuid.uuid4().hex
    with request("/gradio_api/queue/join", {
        "data": [sample[0], 768, 42, True], "fn_index": deps[0]["id"], "session_hash": session,
    }, timeout=20) as r:
        response = json.load(r)
    job = {"event_id": response["event_id"], "session_hash": session, "endpoint": BASE,
           "sample": sample[0], "resolution": 768, "seed": 42, "split_limbs": True,
           "submitted_at": time.time(), "status": "SUBMITTED",
           "layers_validated": False, "rig_validated": False, "browser_validated": False,
           "authentication": "explicit-env" if AUTH_TOKEN else "anonymous"}
    save(a.out / "job.json", job)
    print(json.dumps({"status": "SUBMITTED", "event_id": job["event_id"]}), flush=True)
    try:
        with request("/gradio_api/queue/data?session_hash=" + urllib.parse.quote(session)) as stream:
            code = consume_queue(a.out, job, stream)
    except Exception as exc:
        job["status"] = "FAILED"
        job["error"] = type(exc).__name__ + ": " + str(exc)
        save(a.out / "job.json", job)
        code = 2
    print(json.dumps(job, ensure_ascii=True), flush=True)
    return code

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "CALL_FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        raise SystemExit(2)
