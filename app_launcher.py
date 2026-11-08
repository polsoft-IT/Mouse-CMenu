from __future__ import annotations

import os
import subprocess
from pathlib import Path


def launch_application(path: str) -> subprocess.Popen[bytes] | None:
    normalized_path = path.strip().strip('"')
    if not normalized_path:
        raise ValueError("Application path cannot be empty")

    if os.name == "nt" and Path(normalized_path).suffix.lower() == ".lnk":
        os.startfile(normalized_path)
        return None

    application_path = Path(normalized_path)
    return subprocess.Popen(
        [str(application_path)],
        cwd=str(application_path.resolve().parent),
        shell=False,
    )
