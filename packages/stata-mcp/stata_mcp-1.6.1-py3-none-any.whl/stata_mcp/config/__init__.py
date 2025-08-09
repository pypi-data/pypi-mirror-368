import os
import platform

import tomllib


class Config:
    """Configuration manager supporting nested TOML sections."""

    CONFIG_FILE_PATH = os.path.expanduser("~/.stata-mcp/config.toml")

    def __init__(self) -> None:
        os.makedirs(os.path.dirname(self.CONFIG_FILE_PATH), exist_ok=True)
        if not os.path.exists(self.CONFIG_FILE_PATH):
            self.config: dict = self._default_config()
            self._save()
        else:
            self.config = self.load_config()

    def _default_config(self) -> dict:
        sys_os = platform.system()
        if sys_os in ["Darwin", "Linux"]:
            documents_path = os.path.expanduser("~/Documents")
        elif sys_os == "Windows":
            documents_path = os.path.join(
                os.environ.get("USERPROFILE", "~"), "Documents")
        else:
            documents_path = os.path.expanduser("~/Documents")
        return {
            "stata": {"stata_cli": ""},
            "stata-mcp": {
                "output_base_path": os.path.join(
                    documents_path, "stata-mcp-folder"
                )
            },
            "llm": {
                "LLM_TYPE": "ollama",
                "ollama": {
                    "MODEL": "qwen2.5-coder:7b",
                    "BASE_URL": "http://localhost:11434",
                },
                "openai": {
                    "MODEL": "gpt-3.5-turbo",
                    "BASE_URL": "https://api.openai.com/v1",
                    "API_KEY": "<YOUR_OPENAI_API_KEY>",
                },
            },
        }

    def _write_dict(self, f, data: dict, prefix: str = "") -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                section = f"{prefix}.{key}" if prefix else key
                f.write(f"\n[{section}]\n")
                self._write_dict(f, value, section)
            else:
                escaped = str(value).replace('"', '\\"')
                f.write(f"{key} = \"{escaped}\"\n")

    def _save(self) -> None:
        """Write the current config to the TOML file."""
        with open(self.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            self._write_dict(f, self.config)

    def load_config(self) -> dict:
        with open(self.CONFIG_FILE_PATH, "rb") as f:
            return tomllib.load(f)

    def _get_nested(self, data: dict, keys: list[str], default=None):
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

    def get(self, key: str, default: str | None = None):
        keys = key.split(".")
        return self._get_nested(self.config, keys, default)

    def _set_nested(self, data: dict, keys: list[str], value):
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value

    def set(self, key: str, value: str) -> None:
        keys = key.split(".")
        self._set_nested(self.config, keys, value)
        self._save()

    def _delete_nested(self, data: dict, keys: list[str]):
        for k in keys[:-1]:
            data = data.get(k)
            if not isinstance(data, dict):
                return
        data.pop(keys[-1], None)

    def delete(self, key: str) -> None:
        keys = key.split(".")
        self._delete_nested(self.config, keys)
        self._save()
