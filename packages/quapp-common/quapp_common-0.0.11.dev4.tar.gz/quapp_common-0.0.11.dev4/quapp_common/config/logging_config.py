#  Quapp Platform Project
#  logging_config.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import sys

from loguru import logger

# Define colors for each log level
level_colors = {"DEBUG": "blue", "INFO": "white", "WARNING": "yellow",
                "ERROR": "red", "CRITICAL": "bold red"}


def job_logger(job_id: str = None):
    return logger.bind(context=job_id)


def __custom_format(record):
    # Safely get context, default to "QuappLibs" if missing
    context = record["extra"].get("context", "QuappLibs")

    # Get the color for the current level, default to white if the level is unknown
    level_color = level_colors.get(record["level"].name, "white")
    return (
        f"<{level_color}>{{level}}</{level_color}> : <green>{{time: %Y-%m-%d %H:%M:%S}}</green> : <yellow>[{context}]</yellow> <{level_color}>{{message}}</{level_color}> : <magenta>{{process}}</magenta>\n")


logger.add(sink=sys.stderr, format=__custom_format, # Use custom format function
           level="DEBUG", colorize=True
           # Enable colors (supported by sys.stderr)
           )
