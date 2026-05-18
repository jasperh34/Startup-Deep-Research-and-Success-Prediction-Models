from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path = ".env.local") -> None:
    """Load simple KEY=VALUE lines without introducing a runtime dependency."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def env_value(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def normalized_url(value: str | None) -> str | None:
    if not value:
        return None
    return value if value.startswith(("http://", "https://")) else f"https://{value}"
