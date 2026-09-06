"""Every pass leaves a receipt under runs/ — never edited, only appended to."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write(result, spec, spec_file: str) -> Path:
    stamp = datetime.now(timezone.utc)
    day = stamp.strftime("%Y-%m-%d")
    run_dir = Path(result.root) / "runs" / day
    run_dir.mkdir(parents=True, exist_ok=True)

    receipt = {
        "at": stamp.isoformat(timespec="seconds"),
        "spec": spec_file,
        "project": spec.name,
        "broker": spec.broker,
        "symbols": list(spec.symbols),
        "risk": {"max_position": spec.max_position, "stop_loss": spec.stop_loss},
        "files": result.files,
        "bytes": result.bytes_written,
        "ms": result.ms,
        "git": result.git,
    }
    path = run_dir / f"receipt-{stamp.strftime('%H%M%S')}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    trace = Path(result.root) / "runs" / "trace.log"
    with trace.open("a", encoding="utf-8") as fh:
        fh.write(
            f"{stamp.strftime('%H:%M:%S')}  scaffold  {spec.slug}  "
            f"{len(result.files)} files  {result.ms}ms  {result.git}\n"
        )
    return path
