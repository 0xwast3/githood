"""Turn a Spec into a folder of files, then hand back what it wrote."""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from . import templates as T
from .spec import Spec


@dataclass
class Result:
    root: Path
    files: list
    bytes_written: int
    ms: int
    git: str

    @property
    def summary(self) -> str:
        return (
            f"{len(self.files)} files · {self.bytes_written/1024:.1f}kb · "
            f"{self.ms}ms · git: {self.git}"
        )


def _values(spec: Spec, spec_file: str) -> dict:
    broker_class = spec.broker.capitalize() + "Broker"
    return {
        "name": spec.name,
        "slug": spec.slug,
        "module": spec.module,
        "spec_file": spec_file,
        "broker": spec.broker,
        "broker_upper": spec.broker.upper(),
        "broker_title": spec.broker.capitalize(),
        "broker_class": broker_class,
        "symbol_list": ", ".join(spec.symbols),
        "symbols_repr": repr(list(spec.symbols)),
        "timeframe": spec.timeframe,
        "cash": f"{spec.cash:g}",
        "max_position": spec.max_position,
        "stop_loss": spec.stop_loss,
        "max_position_pct": f"{spec.max_position:.0%}",
        "stop_loss_pct": f"{spec.stop_loss:.0%}",
        "rules_md": "\n".join(f"- {r}" for r in spec.rules),
        "rules_comments": "\n".join(f"#   - {r}" for r in spec.rules),
    }


def plan(spec: Spec) -> list:
    """The paths githood would write, in the order it writes them."""
    return [
        "README.md",
        ".gitignore",
        ".env.example",
        "requirements.txt",
        "Makefile",
        "Dockerfile",
        "compose.yml",
        ".github/workflows/ci.yml",
        "src/__init__.py",
        "src/main.py",
        "src/strategy.py",
        "src/risk.py",
        "src/broker/__init__.py",
        "src/broker/base.py",
        f"src/broker/{spec.broker}.py",
        "tests/test_risk.py",
        "runs/.gitkeep",
    ]


def build(spec: Spec, out: Path, spec_file: str = "spec.md", force: bool = False,
          git: bool = True) -> Result:
    started = time.time()
    root = Path(out)
    if root.exists() and any(root.iterdir()):
        if not force:
            raise FileExistsError(f"{root} is not empty (pass --force to overwrite)")
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    v = _values(spec, spec_file)
    files = {
        "README.md": T.render(T.README, v),
        ".gitignore": T.GITIGNORE,
        ".env.example": T.render(T.ENV_EXAMPLE, v),
        "requirements.txt": T.REQUIREMENTS,
        "Makefile": T.render(T.MAKEFILE, v),
        "Dockerfile": T.DOCKERFILE,
        "compose.yml": T.COMPOSE,
        ".github/workflows/ci.yml": T.render(T.CI, v),
        "src/__init__.py": T.INIT,
        "src/main.py": T.render(T.MAIN, v),
        "src/strategy.py": T.render(T.STRATEGY, v),
        "src/risk.py": T.render(T.RISK, v),
        "src/broker/__init__.py": T.INIT,
        "src/broker/base.py": T.BROKER_BASE,
        f"src/broker/{spec.broker}.py": T.render(T.BROKER_IMPL, v),
        "tests/test_risk.py": T.TEST_RISK,
        "runs/.gitkeep": "",
    }

    written, total = [], 0
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        written.append(rel)
        total += len(body.encode("utf-8"))

    status = _git_init(root) if git else "skipped"
    ms = int((time.time() - started) * 1000)
    return Result(root=root, files=written, bytes_written=total, ms=ms, git=status)


def _git_init(root: Path) -> str:
    """Best effort: a repo with no history is half a repo, but never fatal."""
    if shutil.which("git") is None:
        return "unavailable"
    try:
        env = {"GIT_TERMINAL_PROMPT": "0"}
        run = lambda *a: subprocess.run(a, cwd=root, check=True, capture_output=True, env=None)
        run("git", "init", "-q", "-b", "main")
        run("git", "add", ".")
        subprocess.run(
            ["git", "-c", "user.email=bot@githood.local", "-c", "user.name=githood",
             "commit", "-q", "-m", "chore: scaffold by githood"],
            cwd=root, check=True, capture_output=True,
        )
        return "initialised · 1 commit"
    except (subprocess.CalledProcessError, OSError):
        return "init failed (repo still written)"
