"""utils for working with config"""

import json
import os
from pathlib import Path

from platformdirs import PlatformDirs

def parse_config():
    pdirs = PlatformDirs("microwiki", "justtechno") 
    configdirpath = pdirs.user_config_path
    configfilepath = Path(f"{pdirs.user_config_dir}/config.json")
    if configdirpath.is_dir():
        with open(configfilepath, "r", encoding="utf-8") as file:
            config = json.load(file)
        return config
    else:
        os.mkdir(configdirpath)
        with open(configfilepath, "w", encoding="utf-8") as file:
            baseconfigdict = {
                "theme": "nord",
                "wikistorage": f"{pdirs.user_data_dir}",
                "allow_edit": True,
            }
            baseconfigjson = json.dumps(baseconfigdict)
            file.write(baseconfigjson)
        return baseconfigdict
