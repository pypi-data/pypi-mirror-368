# Getting Started

> Minimal setup to start logging

## Install

```bash
uv add jinpy-utils
# or
pip install jinpy-utils
```

## Configure and Log

```python
from jpy_utils.logger.config import GlobalLoggerConfig, ConsoleBackendConfig
from jpy_utils.logger.core import Logger

# Configure once (12-factor friendly). You can use GlobalLoggerConfig.from_env().
cfg = GlobalLoggerConfig(backends=[ConsoleBackendConfig(name="console")])
Logger.set_global_config(cfg)

# Get a logger and use it
log = Logger.get_logger("app")
log.info("hello", {"env": "dev"})
```

## Environment Configuration

```bash
export LOGGER_APP_NAME="demo"
export LOGGER_ENVIRONMENT="dev"
export LOGGER_LEVEL="debug"
# ...more as needed
```

```python
from jpy_utils.logger.core import Logger
from jpy_utils.logger.config import GlobalLoggerConfig

Logger.set_global_config(GlobalLoggerConfig.from_env())
log = Logger.get_logger("app")
log.debug("env-configured")
```

## File Backend Example

```python
from pathlib import Path
from jpy_utils.logger.config import GlobalLoggerConfig, FileBackendConfig
from jpy_utils.logger.core import Logger

cfg = GlobalLoggerConfig(
    backends=[
        FileBackendConfig(name="file", file_path=Path("logs/app.log"))
    ]
)
Logger.set_global_config(cfg)
Logger.get_logger("file-demo").info("to-file")
```

## Graceful Shutdown

```python
import asyncio
from jpy_utils.logger.core import Logger

async def main() -> None:
    log = Logger.get_logger("app")
    await log.ainfo("bye")
    await log.close()

asyncio.run(main())
```
