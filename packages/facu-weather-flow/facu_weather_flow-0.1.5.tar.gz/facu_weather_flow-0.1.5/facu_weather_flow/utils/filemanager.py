import os
from typing import Optional


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "output_weather")


def ensure_dir_exists(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_output_dir(custom_dir: Optional[str] = None) -> str:
    env_dir = os.getenv("WEATHER_OUTPUT_DIR")
    output_dir = os.path.abspath(custom_dir or env_dir or DEFAULT_OUTPUT_DIR)
    ensure_dir_exists(output_dir)
    return output_dir


def get_output_path(filename: str, custom_dir: Optional[str] = None) -> str:
    output_dir = get_output_dir(custom_dir)
    return os.path.join(output_dir, filename)
