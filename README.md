# Microwiki

## Languages

[русский](README_RU.md) | english(current)

### About microwiki

A TUI(Terminal user interface), Local wiki-system/knowledge base and markdown editor, made with textual and python.
Supported systems:
- Linux systems(e.g Arch, Fedora, Debian, Omarchy, CachyOS, RHEL, etc, even android via termux or chromeOS via crostini)
- Windows
- MacOS


### Features

- Low system requirments
- No graphical environment needed(it is TUI so it runs in terminal)
- External editors support
- Vim-like layout partially suported(links in text still requires mouse but all other things can be performed only with keyboard)


### Disfeatures

- No many features currently supported
- No images supported
- No obsidian-like notes tree supported


### Who is it designed for

- Tiling window-manager users
- Developers
- Vim/Nvim users


### Installation
There are three installation ways

##### From source
The recomended way is build it from source

on mac/linux:
```bash
git clone # cloning repo
cd ./microwiki # moving into cloned repo
make build # building project
```

on windows:
```powershell
git clone # cloning repo
cd ./microwiki # moving into cloned repo
make build_windows # building project with windows path syntax
```

#### Running without building
You can run microwiki without building it, at first you need to clone repo the dsame as in installation, then just run
```bash
make run
```

#### From releases
Just go to releases select release for you system(no mac build, sorry) install it and execute


### License

Project is licensed under [MIT](LICENSE)
