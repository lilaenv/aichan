from pathlib import Path

import yaml

# 数字で上の階層を指定する (0は現在の階層、1は1つ上、2は2つ上...)
with Path(__file__).parents[3].joinpath(".prompt.yml").open(encoding="utf-8") as f:
    config = yaml.safe_load(f)

CHAT_SYSTEM: str = config.get("chat_system")
CLAUDE_SYSTEM: str = config.get("claude_system")
FIXPY_SYSTEM: str = config.get("fixpy_system")
