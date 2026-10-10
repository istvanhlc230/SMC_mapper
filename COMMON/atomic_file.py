"""Shared atomic UTF-8 text-file replacement."""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path


def atomic_write_text(
    path: str | Path,
    content: str,
    *,
    prefix: str = ".atomic.",
    retry_limit: int = 1,
    retry_delay_seconds: float = 0.0,
) -> None:
    """Atomically replace a UTF-8 text file using a same-directory temporary file."""
    destination = Path(path)
    if retry_limit < 1:
        raise ValueError("retry_limit must be at least one")
    if retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must not be negative")

    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error: OSError | None = None

    for attempt in range(1, retry_limit + 1):
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=prefix,
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(temporary_path, destination)
            temporary_path = None
            return
        except OSError as exc:
            last_error = exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    # Preserve the original write/replace failure as the primary error.
                    pass

        if attempt < retry_limit and retry_delay_seconds:
            time.sleep(retry_delay_seconds * attempt)

    raise OSError(f"atomic file replacement failed: {last_error}") from last_error
