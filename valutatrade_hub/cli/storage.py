import json
from typing import Any, Dict, List


class FileStorageManager:

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def load(self) -> None:
        """Load users from file into memory."""
        if not self._file_path:
            return []

        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: List[Dict[str, Any]]) -> None:
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
