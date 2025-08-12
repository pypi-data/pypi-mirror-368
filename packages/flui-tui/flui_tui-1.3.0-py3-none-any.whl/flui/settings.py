import tomllib
from functools import cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

TOML_NAME = "flui.toml"


class Settings(BaseModel):
    """Default settings.

    These can be modified by creating a TOML file in the folder where you
    run the flew application.
    """

    # Number of workers in background reading kmers
    workers: int = 2

    # -----------------
    # The following values were obtained by assessing several existing runs

    # Minimum kmers required before attempting to subtype.
    minimum_kmers: int = 2000

    # Only accept scores above this.
    minimum_score: float = 6.0

    # The best one should be at least this much better than the second best.
    minimum_gap: float = 2.5

    # Kmers size to use for HA segment.
    ha_kmer_size: int = 17

    # Kmer size to use for NA segment.
    na_kmer_size: int = 13

    # Default theme and colors
    theme: str = "textual-dark"
    success_color: str = "green"
    failure_color: str = "red"

    model_config = ConfigDict(extra="forbid")


@cache
def load_toml(toml_path: Path) -> dict[str, Any]:
    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    return data


def find_file_in_parents(filename: str, start_path: Path | None = None) -> Path | None:
    current_path: Path = Path.cwd() if start_path is None else start_path

    while True:
        target_file: Path = current_path / filename
        git_dir: Path = current_path / ".git"

        if target_file.exists():
            return target_file

        # Break out of project dir.
        if git_dir.exists():
            return None

        next_path = current_path.parent
        if current_path == next_path:
            # We must be at the root folder
            break

        current_path = next_path

    return None


class SettingsError(Exception):
    """Convert into readable errors."""

    def __init__(self, e: ValidationError):
        readable_errors = []
        for error in e.errors():
            field_path = ".".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_type = error["type"]
            formatted_error = (
                f"Error in field '{field_path}': {message} (type: {error_type})"
            )
            readable_errors.append(formatted_error)
        self.readable_errors = readable_errors


def get_settings_path() -> Path | None:
    """Look in current folder and parent folders and home."""
    env_pth = Path.cwd()
    toml_path = find_file_in_parents(TOML_NAME, env_pth)
    if toml_path is None:
        # Try home folder
        toml_path = Path.home() / TOML_NAME
        if not toml_path.exists():
            toml_path = None

    return toml_path


@cache
def get_settings() -> Settings:
    """Look in current folder and parent folders."""
    toml_path = get_settings_path()
    dct = load_toml(toml_path) if toml_path is not None else {}
    try:
        settings = Settings(**dct)
    except ValidationError as e:
        raise SettingsError(e) from e

    return settings
