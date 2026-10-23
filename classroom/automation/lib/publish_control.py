"""Publication control: global lock helpers, PR resume, retries, deploy gating.

Used by scheduled AM/late/news jobs. Timers must remain disabled until activation.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import Config, JsonLogger, atomic_write_json, utc_now


@dataclass
class RetryPolicy:
    max_attempts: int = 5
    base_delay_sec: float = 2.0
    max_delay_sec: float = 60.0
    retryable: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError, OSError, urllib.error.URLError)

    def sleep_for(self, attempt: int) -> float:
        # attempt is 1-based for the failure that just happened
        delay = min(self.max_delay_sec, self.base_delay_sec * (2 ** (attempt - 1)))
        return delay


def with_bounded_retries(
    fn: Callable[[], Any],
    *,
    policy: RetryPolicy | None = None,
    logger: JsonLogger | None = None,
    label: str = "op",
) -> Any:
    policy = policy or RetryPolicy()
    last: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except policy.retryable as e:
            last = e
            if logger:
                logger.event("retry", label=label, attempt=attempt, error=type(e).__name__, detail=str(e)[:200])
            if attempt >= policy.max_attempts:
                break
            time.sleep(policy.sleep_for(attempt))
        except Exception as e:
            # Non-retryable: fail closed immediately
            if logger:
                logger.event("fail_closed", label=label, error=type(e).__name__, detail=str(e)[:200])
            raise
    assert last is not None
    raise last


@dataclass
class SlotState:
    """Durable per-slot state for duplicate prevention / PR resume."""

    slot: str
    batch_ids: list[int] = field(default_factory=list)
    branch: str | None = None
    pr_number: int | None = None
    pr_url: str | None = None
    status: str = "idle"  # idle|generating|pr_open|merged|deploy_pending|deployed|failed
    fingerprint: str | None = None
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return {
            "slot": self.slot,
            "batch_ids": self.batch_ids,
            "branch": self.branch,
            "pr_number": self.pr_number,
            "pr_url": self.pr_url,
            "status": self.status,
            "fingerprint": self.fingerprint,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlotState":
        return cls(
            slot=str(data.get("slot") or ""),
            batch_ids=[int(x) for x in data.get("batch_ids") or []],
            branch=data.get("branch"),
            pr_number=data.get("pr_number"),
            pr_url=data.get("pr_url"),
            status=str(data.get("status") or "idle"),
            fingerprint=data.get("fingerprint"),
            updated_at=str(data.get("updated_at") or utc_now()),
        )


def slot_state_path(cfg: Config, slot: str) -> Path:
    return cfg.state_dir / f"slot_{slot}.json"


def load_slot_state(cfg: Config, slot: str) -> SlotState:
    path = slot_state_path(cfg, slot)
    if path.is_file():
        try:
            return SlotState.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            pass
    return SlotState(slot=slot)


def save_slot_state(cfg: Config, state: SlotState) -> None:
    state.updated_at = utc_now()
    atomic_write_json(slot_state_path(cfg, state.slot), state.to_dict())


def batch_fingerprint(class_ids: list[int]) -> str:
    return "batch:" + ",".join(str(i) for i in class_ids)


def resume_or_create_batch(
    cfg: Config,
    slot: str,
    class_ids: list[int],
    *,
    logger: JsonLogger | None = None,
) -> SlotState:
    """Idempotent: same slot + same ids resume existing PR; never open a duplicate."""
    fp = batch_fingerprint(class_ids)
    state = load_slot_state(cfg, slot)
    if state.fingerprint == fp and state.status in {"pr_open", "merged", "deploy_pending", "deployed", "generating"}:
        if logger:
            logger.event(
                "resume_existing",
                slot=slot,
                status=state.status,
                pr_number=state.pr_number,
                branch=state.branch,
                fingerprint=fp,
            )
        return state
    # New batch for this slot
    state = SlotState(slot=slot, batch_ids=list(class_ids), fingerprint=fp, status="generating")
    save_slot_state(cfg, state)
    if logger:
        logger.event("new_batch_state", slot=slot, batch_ids=class_ids, fingerprint=fp)
    return state


def mark_pr_open(cfg: Config, state: SlotState, *, branch: str, pr_number: int, pr_url: str) -> SlotState:
    state.branch = branch
    state.pr_number = pr_number
    state.pr_url = pr_url
    state.status = "pr_open"
    save_slot_state(cfg, state)
    return state


STALE_LOCK_SEC = int(os.environ.get("CLASSROOM_STALE_LOCK_SEC", "7200"))


def recover_stale_lock(cfg: Config, logger: JsonLogger | None = None) -> bool:
    """Remove lock owner file if older than STALE_LOCK_SEC (crash/reboot recovery).

    filelock uses ``<lock>.lock`` companion; we also track ``<lock>.owner`` with pid+ts.
    """
    owner = Path(str(cfg.lock_file) + ".owner")
    if not owner.is_file():
        return False
    try:
        data = json.loads(owner.read_text(encoding="utf-8"))
        ts = float(data.get("ts", 0))
        pid = int(data.get("pid", 0))
    except Exception:
        owner.unlink(missing_ok=True)
        return True
    age = time.time() - ts
    alive = False
    if pid > 0:
        try:
            os.kill(pid, 0)
            alive = True
        except OSError:
            alive = False
    if age >= STALE_LOCK_SEC or not alive:
        if logger:
            logger.event("stale_lock_recovered", age_sec=int(age), pid=pid, alive=alive)
        owner.unlink(missing_ok=True)
        # Best-effort remove filelock sidecar if present and stale
        sidecar = Path(str(cfg.lock_file) + ".lock")
        if sidecar.is_file() and not alive:
            try:
                sidecar.unlink()
            except OSError:
                pass
        return True
    return False


def write_lock_owner(cfg: Config) -> None:
    owner = Path(str(cfg.lock_file) + ".owner")
    atomic_write_json(owner, {"pid": os.getpid(), "ts": time.time(), "at": utc_now()})


def clear_lock_owner(cfg: Config) -> None:
    Path(str(cfg.lock_file) + ".owner").unlink(missing_ok=True)


def verify_live_deploy(
    *,
    urls: list[str],
    expect_class_min: int | None = None,
    logger: JsonLogger | None = None,
    policy: RetryPolicy | None = None,
) -> dict:
    """Verify deployment URLs before advancing curriculum numbering."""
    policy = policy or RetryPolicy(max_attempts=4, base_delay_sec=3.0)

    def _once() -> dict:
        results = []
        for url in urls:
            req = urllib.request.Request(url, headers={"User-Agent": "otaconskeep-classroom-deploy-verify/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
                results.append({"url": url, "status": resp.status, "len": len(body)})
                if expect_class_min is not None:
                    import re

                    ids = {int(n) for n in re.findall(r"classes/(\d{1,3})", body)}
                    if max(ids or {0}) < expect_class_min and len(ids) < expect_class_min:
                        raise RuntimeError(f"deploy_verify_class_count url={url} ids={sorted(ids)}")
        return {"ok": True, "results": results}

    try:
        out = with_bounded_retries(_once, policy=policy, logger=logger, label="deploy_verify")
        if logger:
            logger.event("deploy_verified", **out)
        return out
    except Exception as e:
        if logger:
            logger.event("deploy_verify_failed", error=str(e)[:300])
        return {"ok": False, "error": str(e)[:300]}


def may_advance_numbering(cfg: Config, *, last_batch_ids: list[int], logger: JsonLogger | None = None) -> bool:
    """Numbering advances only after preceding deployment is verified."""
    gate = cfg.state_dir / "last_deploy_verified.json"
    if not gate.is_file():
        if logger:
            logger.event("advance_blocked", reason="no_deploy_verification")
        return False
    try:
        data = json.loads(gate.read_text(encoding="utf-8"))
    except Exception:
        return False
    verified_ids = [int(x) for x in data.get("batch_ids") or []]
    if verified_ids != list(last_batch_ids):
        if logger:
            logger.event("advance_blocked", reason="batch_mismatch", verified=verified_ids, expected=last_batch_ids)
        return False
    if not data.get("ok"):
        return False
    return True


def record_deploy_verified(cfg: Config, batch_ids: list[int], evidence: dict) -> None:
    atomic_write_json(
        cfg.state_dir / "last_deploy_verified.json",
        {"ok": True, "batch_ids": batch_ids, "evidence": evidence, "at": utc_now()},
    )


def next_expected_batches(existing_max: int) -> dict:
    """Exact next two core batches after published classes."""
    start = existing_max + 1
    first = list(range(start, start + 6))
    second = list(range(start + 6, start + 12))
    return {"next": first, "following": second}
