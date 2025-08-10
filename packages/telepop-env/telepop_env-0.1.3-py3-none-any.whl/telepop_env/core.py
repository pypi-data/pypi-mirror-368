import os
from pathlib import Path

class TelepopEnv:
    def __init__(self, env_file=".env"):
        self._data = {}
        self._used = set()
        self._load_env_file(env_file)

    def _load_env_file(self, env_file):
        """Load variables from .env file and merge with os.environ."""
        if Path(env_file).exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, _, value = line.partition("=")
                    self._data[key.strip()] = value.strip()
        self._data.update(os.environ)  # OS vars override .env

    def _get(self, key, default, cast, required):
        self._used.add(key)
        value = self._data.get(key, default)
        if value is None and required:
            raise RuntimeError(f"Missing required env variable: {key}")
        if value is None:
            return default
        try:
            return cast(value)
        except Exception as e:
            raise ValueError(f"Invalid value for {key}: {value} ({e})")

    def str(self, key, default=None, required=False):
        return self._get(key, default, str, required)

    def int(self, key, default=None, required=False):
        return self._get(key, default, int, required)

    def float(self, key, default=None, required=False):
        return self._get(key, default, float, required)

    def bool(self, key, default=None, required=False):
        return self._get(key, default, self._to_bool, required)

    def get(self, key, default=None, type=str, required=False):
        return self._get(key, default, type, required)

    def _to_bool(self, v):
        return str(v).strip().lower() in ("1", "true", "yes", "y", "on")

    def generate_example(self, filepath=".env.example"):
        """Generate .env.example from used keys."""
        with open(filepath, "w", encoding="utf-8") as f:
            for key in sorted(self._used):
                f.write(f"{key}=\n")

env = TelepopEnv()
