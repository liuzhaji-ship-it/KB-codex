import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "handoff" / "latest_status.json"
LOG_FILE = ROOT / "scripts" / "watcher.log"

ALLOWED_STAGES = {"waiting_for_manager", "waiting_for_review"}
MIN_STABLE_SECONDS = 5
MIN_TRIGGER_INTERVAL_SECONDS = 60


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="")


def load_status() -> dict:
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def parse_iso(ts: str):
    if not ts:
        return None
    # 支持 2026-...+08:00 和 ...Z
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def decide_action(stage: str) -> str:
    if stage == "waiting_for_manager":
        return "would_trigger_manager"
    if stage == "waiting_for_review":
        return "would_trigger_reviewer"
    return "no_action"


def evaluate_once(last_trigger_epoch: float = 0.0):
    now_epoch = time.time()
    status = load_status()

    stage = status.get("stage", "")
    last_updated_raw = status.get("last_updated", "")
    last_updated_dt = parse_iso(last_updated_raw)

    if not last_updated_dt:
        log("invalid_status: missing/invalid last_updated")
        return False, "invalid_last_updated", last_trigger_epoch

    stable_seconds = now_epoch - last_updated_dt.timestamp()
    since_last_trigger = now_epoch - last_trigger_epoch

    stage_ok = stage in ALLOWED_STAGES
    stable_ok = stable_seconds >= MIN_STABLE_SECONDS
    interval_ok = since_last_trigger >= MIN_TRIGGER_INTERVAL_SECONDS

    action = decide_action(stage)

    log(
        f"status stage={stage} stable={stable_seconds:.1f}s since_last_trigger={since_last_trigger:.1f}s "
        f"checks(stage_ok={stage_ok}, stable_ok={stable_ok}, interval_ok={interval_ok}) action={action}"
    )

    if stage_ok and stable_ok and interval_ok and action != "no_action":
        # 第一版仅记录“可触发”，不真正执行外部动作
        log(f"trigger_decision: {action}")
        return True, action, now_epoch

    return False, "not_triggered", last_trigger_epoch


def main():
    log("watcher_minimal started")
    last_trigger_epoch = 0.0
    # 第一版只做一次受控验证，不进入无限循环
    triggered, reason, last_trigger_epoch = evaluate_once(last_trigger_epoch)
    log(f"watcher_minimal done triggered={triggered} reason={reason}")


if __name__ == "__main__":
    main()
