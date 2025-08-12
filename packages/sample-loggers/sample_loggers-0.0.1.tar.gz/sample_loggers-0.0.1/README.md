# Deep Learning Tools for Pytorch

[![Python >= 3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/release/)

This package provides some common configurations to quickly create your own logger through the logging library. 

## Installation

```bash
pip install sample_loggers
```

## Example for using

```python
import os
import logging
from loggers import LoggerController

os.makedirs('./output', exist_ok=True)
logger_controller = LoggerController(log_file_name="log.txt" ,output_dir=config.OUTPUT)
logger = logger_controller.create_logger(
    logger_name='food_classification',
    log_level=logging.DEBUG,
    format_type="default"
)
```


## Update
- 0.0.1 - We provide the common config for logging to create logger.

## License

Sample Loggers is MIT licensed. See the [LICENSE](LICENSE) for details.

