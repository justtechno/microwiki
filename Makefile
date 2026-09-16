pyinstaller := uv run pyinstaller

# variables for posix
project := ./src/microwiki/main.py
data := ./src/microwiki/data/:data

# variables for windows
project_windows := .\src\microwiki\main.py
data_windows := .\src\microwiki\main.py

build:	# main build target for posix systems
	uv sync
	$(pyinstaller) --name="MicroWiki" --onefile --console --paths=. --noconfirm --collect-all textual --add-data "$(data)" $(project)

build_windows: # windows has other paths syntax so there are second build target for windows users
	uv sync
	$(pyinstaller) --name="MicroWiki" --onefile --console --paths=. --noconfirm --collect-all textual --add-data "$(data_windows)" $(project_windows)

run:
	uv sync && uv run $(project)
