# Configuration File

Stata-MCP stores settings in `~/.stata-mcp/config.toml`. A sample file is located at `src/stata_mcp/config/example.toml`.
Copy it to your home folder if the file does not exist and modify as needed.

## Accessing Values

You can read and write values in the configuration using dot notation:

```python
from stata_mcp.config import Config
cfg = Config()
model = cfg.get("llm.ollama.MODEL")
cfg.set("stata.stata_cli", "/path/to/stata")
```

Sections mirror the TOML hierarchy, so `llm.ollama.MODEL` refers to the `MODEL` key inside `[llm.ollama]`.
