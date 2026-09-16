import platform
import sys
from importlib.metadata import version

import version_info


def get_about_info():
    textual_version = version("textual") 
    rich_version = version("rich")
    python_version = sys.version.split(' ', 1)[0]
    os_name = platform.platform()
    return f"""
# ABOUT

## Libraries

| library | version |
|---------|---------|
| textual | {textual_version} |
| rich    | {rich_version}    |


## System

| component | version |
|-----------|---------|
| python_interpreter | {python_version} |
| os | {os_name} |

## About version
| version | channel  | modified_by |
|---------|----------|-------------|
| {version_info.version} | {version_info.channel} | {version_info.modified_by} |
"""
