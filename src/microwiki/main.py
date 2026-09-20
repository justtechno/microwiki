from ui import main
from platformdirs import PlatformDirs
from pathlib import Path
from os import mkdir

if __name__ == "__main__":
    pdirs = PlatformDirs("microwiki", "justtechno")
    if Path(pdirs.user_data_dir).exists() != True:
        mkdir(pdirs.user_data_dir)
    main()
