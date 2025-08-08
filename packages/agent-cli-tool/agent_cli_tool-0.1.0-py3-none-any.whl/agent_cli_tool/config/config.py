from dotenv import dotenv_values
from pathlib import Path

# 加载配置文件
config_file = Path.home() / ".config" / "agent-cli-tool.env"
if config_file.exists():
    env_config = dotenv_values(stream=config_file.open("r", encoding="utf-8"))
else:
    env_config = dotenv_values()

assert env_config, (
    f"environment config not found, please edit your config file: {config_file.absolute()}"
)
