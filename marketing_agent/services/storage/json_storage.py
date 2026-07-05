"""JSONStorageService — concrete file-backed storage service."""

import json
import os
from typing import Any

from marketing_agent.configs.settings import get_settings
from marketing_agent.services.storage.base import StorageService


def _get_path(filename: str) -> str:
    settings = get_settings()
    return os.path.join(settings.outputs_dir, filename)


class JSONStorageService(StorageService):
    async def save(self, key: str, data: Any) -> None:
        path = _get_path(f"{key}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    async def load(self, key: str) -> Any:
        path = _get_path(f"{key}.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None
        return None
