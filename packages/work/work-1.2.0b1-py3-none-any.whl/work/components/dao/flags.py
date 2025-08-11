"""The DAO for the flags file."""

import json
import pathlib
from typing import List


class Flags:
    """Read and modify flags."""

    def __init__(self, flag_file: pathlib.Path, no_set_flags: bool = False) -> None:
        self._file: pathlib.Path = flag_file
        self._no_set_flags = no_set_flags
        self._flags: List[str] = []
        self._load()

    def _load(self) -> None:
        """Load flags into memory."""

        if not self._file.exists():
            return

        with self._file.open(mode="r", encoding="utf-8") as flag_file:
            try:
                self._flags = json.load(flag_file)
            except json.JSONDecodeError:
                self._file.unlink()
                return

    def is_set(self, key: str) -> bool:
        """Return if given flag is set."""
        return key in self._flags

    def set(self, *flags: str) -> None:
        """Add given flag(s) to flag store."""
        if self._no_set_flags:
            return
        self._flags.extend(flags)
        self._write()

    def remove(self, *flags: str) -> None:
        """Remove given flag(s) from flag store. Accepts nonexistent flags."""
        for flag in filter(lambda f: f in self._flags, flags):
            self._flags.remove(flag)
        self._write()

    def _write(self) -> None:
        """Write flags to disk."""
        # Ensure that the state directory exists before writing
        self._file.parent.mkdir(parents=True, exist_ok=True)

        with self._file.open(mode="w", encoding="utf-8", newline="\n") as flag_file:
            json.dump(self._flags, flag_file, indent="\t", ensure_ascii=False)
