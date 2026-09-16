"""a small wiki parser utils"""

import json
import os
from pathlib import Path


def parselocalwiki(dir: str) -> str:
    """parse Header.json and return dictionary"""
    file = Path(f"{dir}/Header.json")
    try:
        with open(file, "r", encoding="utf-8") as file:
            wikitext = json.load(file)
    except Exception as err:
        return f"error: {err}"
    else:
        if (
            "enterpoint" in wikitext
            and "wikiname" in wikitext
            and "wikidescription" in wikitext
        ):
            return wikitext
        else:
            return "error: not all properties are in Header.json"


def wikilist(dir: str) -> list:
    """list all directories in directory, filter them and return list with them"""
    os.chdir(dir)
    wiki_list = []
    for component in os.listdir("."):
        path_to_check = Path(component)
        if path_to_check.is_dir() == True:
            header = Path(f"{path_to_check}/Header.json")
            if header.is_file() == True:
                wiki_list.append(path_to_check)
    wiki_list_str = [str(path) for path in wiki_list]
    return wiki_list_str
