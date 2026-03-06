import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "handoff" / "latest_status.json"
LOG_FILE = ROOT / "scripts" / "watcher.log"

POLL_SECONDS = 5
COOLDOWN_SECONDS = 20

last_fingerprint = None
last_trigger_at = 0.0


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="")


def load_status() -> dict:
    if not STATUS_FILE.exists():
        raise FileNotFoundError(f"status file not found: {STATUS_FILE}")
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def save_status(status: dict) -> None:
    status["last_updated"] = datetime.now().isoformat(timespec="seconds")
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def status_fingerprint(status: dict) -> str:
    # 只用关键调度字段，避免无关字段导致重复触发
    key = {
        "stage": status.get("stage"),
        "round": status.get("round"),
        "needs_manager": status.get("needs_manager"),
        "needs_review": status.get("needs_review"),
        "needs_fix": status.get("needs_fix"),
        "current_task": status.get("current_task"),
    }
    return json.dumps(key, ensure_ascii=False, sort_keys=True)


def run_codex_with_prompt(prompt_path: Path) -> tuple[int, str, str]:
    cmd = [
        "codex",
        "exec",
        f"Please follow instructions in file: {prompt_path.as_posix()}"
    ]
    p = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        shell=False,
    )
    return p.returncode, p.stdout, p.stderr


def trigger_manager(status: dict) -> None:
    prompt = ROOT / "scripts" / "manager_prompt.txt"
    log(f"Trigger manager with prompt: {prompt}")
    code, out, err = run_codex_with_prompt(prompt)
    log(f"Manager exit={code}")
    if out.strip():
        log(f"Manager stdout: {out[-1000:]}")
    if err.strip():
        log(f"Manager stderr: {err[-1000:]}")

    # 如果 Codex 没有正确更新状态，watcher 做兜底迁移
    status = load_status()
    if status.get("stage") == "waiting_for_manager":
        status["stage"] = "ready_for_build"
        status["needs_manager"] = False
        status["producer"] = "watcher_fallback"
        save_status(status)
        log("Manager fallback status update applied: waiting_for_manager -> ready_for_build")


def trigger_reviewer(status: dict) -> None:
    prompt = ROOT / "scripts" / "reviewer_prompt.txt"
    log(f"Trigger reviewer with prompt: {prompt}")
    code, out, err = run_codex_with_prompt(prompt)
    log(f"Reviewer exit={code}")
    if out.strip():
        log(f"Reviewer stdout: {out[-1000:]}")
    if err.strip():
        log(f"Reviewer stderr: {err[-1000:]}")


def should_skip_duplicate(fp: str) -> bool:
    global last_fingerprint, last_trigger_at
    now = time.time()
    if fp == last_fingerprint and (now - last_trigger_at) < COOLDOWN_SECONDS:
        return True
    return False


def mark_triggered(fp: str) -> None:
    global last_fingerprint, last_trigger_at
    last_fingerprint = fp
    last_trigger_at = time.time()


def main() -> None:
    log("Watcher started")
    while True:
        try:
            status = load_status()
            fp = status_fingerprint(status)

            if should_skip_duplicate(fp):
                time.sleep(POLL_SECONDS)
                continue

            stage = status.get("stage")
            if stage == "waiting_for_manager":
                mark_triggered(fp)
                trigger_manager(status)
            elif stage == "waiting_for_review":
                mark_triggered(fp)
                trigger_reviewer(status)

        except Exception as e:
            log(f"Watcher error: {e}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
