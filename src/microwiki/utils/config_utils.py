"""utils for working with config"""

import json
import os
from pathlib import Path


def parse_config():
    configdirpath = Path(f"{os.getenv('HOME')}/.config/microwiki/")
    configfilepath = Path(f"{os.getenv('HOME')}/.config/microwiki/config.json")
    if configdirpath.is_dir():
        with open(configfilepath, "r", encoding="utf-8") as file:
            config = json.load(file)
        return config
    else:
        os.mkdir(configdirpath)
        with open(configfilepath, "w", encoding="utf-8") as file:
            baseconfigdict = {
                "theme": "nord",
                "wikistorage": f"{os.getenv('HOME')}/.micronote/wikistorage/",
                "allow_edit": True,
                "editor": "nvim",
                "lang": "eng",
            }
            baseconfigjson = json.dumps(baseconfigdict)
            file.write(baseconfigjson)
        return baseconfigdict
