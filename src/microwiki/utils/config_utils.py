"""utils for working with config"""

import json
import os
from pathlib import Path

from platformdirs import PlatformDirs

def parse_config():
    pdirs = PlatformDirs("microwiki", "justtechno") 
    configdirpath = Path(pdirs.user_config_dir)
    configfilepath = Path(f"{pdirs.user_config_dir}/config.json")
    if configdirpath.is_dir():
        with open(configfilepath, "r", encoding="utf-8") as file:
            config = json.load(file)
        return config
    else:
        os.mkdir(pdirs.user_data_dir)
        with open(configfilepath, "w", encoding="utf-8") as file:
            baseconfigdict = {
                "theme": "nord",
                "wikistorage": f"{pdirs.user_data_dir}",
            }
            baseconfigjson = json.dumps(baseconfigdict)
            file.write(baseconfigjson)
        return baseconfigdict
