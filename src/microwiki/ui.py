"""all the UI of app"""

import os
from posixpath import isfile
import shutil
import sys
from pathlib import Path
import asyncio
from time import sleep

from about import get_about_info
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DirectoryTree,
    Header,
    Input,
    Label,
    Markdown,
    MarkdownViewer,
    Static,
    TextArea,
    DirectoryTree,
)
from utils.config_utils import parse_config
from utils.editor_utils import createwiki, writefile
from utils.wikiparser import parselocalwiki, wikilist

from enums import WriteStatus

ABOUT = get_about_info()

class WikiFileManager(Screen):
    """wiki file manager"""
    BINDINGS = [
            Binding("m", "app.push_screen('Wiki')", priority=True),
            Binding("ctrl+a", "pre_mkfile"),
            Binding("ctrl+r", "pre_rename"),
            Binding("ctrl+d", "pre_rmfile"),
            Binding("enter", "filedispatch", priority=True)
]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DirectoryTree("./", id="fm_core") 
        yield Input(id="fm_name_input", placeholder="input file name")
        yield Container(
        Static("Are you sure want to delete file?", id="deletetitle"),
        Horizontal(
            Button("Yes", id="fm_yes", classes="fm_delete_button"),
            Button("No", id="fm_no", classes="fm_delete_button"),
            ),
            id="fm_deletecontainer"
        )



    def on_mount(self) -> None:
        self.query_one("#fm_name_input").styles.display = "none"
        self.query_one("#fm_deletecontainer").styles.display = "none"
        # ----------states----------
        self.creating_file = False
        self.editing_filename = False
        self.removing_file = False

    def get_focused_file(self) -> None:
        """return focused file"""
        tree = self.query_one(DirectoryTree)
        node = tree.cursor_node 
        if node and node.data: # check if node exists
            current_path = node.data.path
            return current_path # return path to focused file
        else: 
            return None # if there are not node exists return None
     
    async def action_move_viewer(self) -> None:
        """opens other document via viewer"""      
        global mdfile_path
        global moving_via_fm
        mdfile_path = self.get_focused_file()
        moving_via_fm = True
        self.app.push_screen("Wiki")

    def action_pre_rename(self) -> None:
        """a pre-rename file function"""
        if self.editing_filename == False:
            self.query_one("#fm_name_input").styles.display = "block"
            self.query_one("#fm_core").styles.display = "none"
            self.editing_filename = True

    def action_rename(self) -> None:
        """rename file"""
        if self.editing_filename == True:
            newname = self.query_one("#fm_name_input").value
            file = self.get_focused_file()         
            file.rename(newname)
            self.editing_filename = False
            self.query_one("#fm_core").styles.display = "block"
            self.query_one("#fm_name_input").styles.display = "none"
            self.query_one("#fm_core").reload()
    
    def action_pre_mkfile(self) -> None:
        """a pre-make file function"""
        if self.creating_file == False:
            self.query_one("#fm_name_input").styles.display = "block"
            self.query_one("#fm_core").styles.display = "none"
            self.creating_file = True
    
    async def action_pre_rmfile(self) -> None:
        """start remove file"""
        if self.removing_file == False:
            self.query_one("#fm_core").styles.display = "none"
            self.query_one("#fm_deletecontainer").styles.display = "block"
            self.removing_file = True

    def action_mkfile(self) -> None:
        """make file"""
        if self.creating_file == True:
            name = self.query_one("#fm_name_input").value
            result = writefile("", name)
            if result == WriteStatus.SUCCESS:
                self.notify(f"file {os.getcwd()}{name} successfully created")
                self.query_one("#fm_core").reload()
            else: 
                self.notify(f"an error ocured creating file: {result.value}")
            self.creating_file = False
            self.query_one("#fm_name_input").styles.display = "none"
            self.query_one("#fm_core").styles.display = "block"
 
    async def action_filedispatch(self) -> None:
        """dispatches file-interaction function based on variables value"""
        if self.editing_filename == True:
            self.action_rename()
        elif self.creating_file == True:
            self.action_mkfile()
        elif self.removing_file ==  True:
            focused = self.screen.focused
            self.query_one(f"#{focused.id}").press()
        elif self.creating_file == False and self.editing_filename == False and self.removing_file == False:
            await self.action_move_viewer()

    @on(Button.Pressed, "#fm_yes")
    def remove_confirm(self) -> None:
        """confirm removing file"""
        if self.removing_file == True:
            file = self.get_focused_file()
            if file.is_file() == True and file.is_dir() == False:
                file.unlink()
            self.removing_file = False
            self.query_one("#fm_deletecontainer").styles.display = "none"
            self.query_one("#fm_core").styles.display = "block"
            self.query_one("#fm_core").reload()
            self.query_one("#fm_core").focus()
    

    @on(Button.Pressed, "#fm_no")
    def remove_cancel(self) -> None:
        """cancel removing file"""
        if self.removing_file == True:
            self.removing_file = False
            self.query_one("#fm_deletecontainer").styles.display = "none"
            self.query_one("#fm_core").styles.display = "block"
            self.query_one("#fm_core").focus()

class WikiScreen(Screen):
    """wiki screen, displays wiki content"""
    BINDINGS = [
        Binding("m", "app.push_screen('WikiListScreen')", "back to wiki list", priority=True),
        Binding("alt+e", "toggle_editor()", "toggle markdown editor", priority=True),
        Binding("ctrl+s", "write()", "write changes to file", priority=True),
        Binding("ctrl+f", "app.push_screen('WikiFileManager')", priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield MarkdownViewer(open_links=False, id="wikiviewer") 
        yield TextArea(id="markdown_editor", language="markdown")

    def on_mount(self) -> None:
        self.query_one("#markdown_editor").styles.display = "none" 

    async def action_toggle_editor(self) -> None:
        """toggle editor"""
        md_text = self.query_one("#wikiviewer").document.source # get text from markdown viewer
        if config["editor"] == "Built-in":
            if self.query_one("#markdown_editor").styles.display == "none":
                self.query_one("#markdown_editor").styles.display = "block"
                self.query_one("#markdown_editor").text = md_text # load text from variable to editor
            elif self.query_one("#markdown_editor").styles.display == "block":
                self.query_one("#markdown_editor").styles.display = "none"
        else:
            with self.app.suspend():
                os.system(f"{config["editor"]} {mdfile_path}")
            with open(mdfile_path, "r", encoding="utf-8") as file:
                text = file.read()
            await self.query_one("#wikiviewer").document.update(text)
    


    async def on_screen_resume(self) -> None:
        """start wiki after pushing screen"""
        global mdfile_path
        global moving_via_fm
        if moving_via_fm == False:
            viewer = self.query_one("#wikiviewer")
            os.chdir(config["wikistorage"])
            wikijson = parselocalwiki(path_to_wiki) # get info about wiki
            mdfile = wikijson["enterpoint"]
            mdfile_path = Path(f"{config["wikistorage"]}/{path_to_wiki}/{mdfile}")
            if mdfile_path.exists() == True:
                await viewer.go(mdfile_path) # open main file of wiki
                os.chdir(path_to_wiki)
            else:
                self.app.push_screen("WikiListScreen")
                self.notify(f"{mdfile_path!s} Path not exists") # notify if there arent main file of wiki
        elif moving_via_fm == True:
            self.app.notify(f"debug {mdfile_path}")
            viewer = self.query_one("#wikiviewer") 
            if mdfile_path.exists() == True:
                await viewer.go(mdfile_path)
            moving_via_fm = False

    async def on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
        """change markdown file""" 
        global mdfile_path
        viewer = self.query_one(MarkdownViewer)
        mdfile_path = Path(message.href)
        
        if mdfile_path.exists() and mdfile_path.suffix == ".md":
            await viewer.go(mdfile_path)

    async def action_write(self) -> None:
        """write changes to file and notify user"""
        viewer = self.query_one("#wikiviewer")
        text = self.query_one("#markdown_editor").text
        result = writefile(text, mdfile_path)
        # notifying about result
        self.notify(f"{result.value}: {mdfile_path}")
        if result == WriteStatus.SUCCESS:
            await viewer.document.update(text)
 

class MainMenu(Screen):
    """main menu screen"""
    BINDINGS = [
        Binding("h", "app.focus_previous"),
        Binding("l", "app.focus_next")
]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
        Static("Main Menu", id="maintitle"),
        Horizontal(
            Button("Open wiki list", id="Wiki", classes="main_button"),
            Button("About", id="About", classes="main_button"),
            id="main_button_container",
            ),
            id="mainmenu",
        )

class WikiListScreen(Screen):
    """screen with a list of wiki"""
    BINDINGS = [
            Binding("ctrl+a", "app.push_screen('WikiCreator')"),
            Binding("ctrl+d", "delete_wiki()"),
            Binding("j", "app.focus_next"),
            Binding("k", "app.focus_previous"),
            # force focus to move from input
            Binding("ctrl+j", "app.focus_next", priority=True), 
            Binding("ctrl+k", "app.focus_previous", priority=True),
]

    def compose(self) -> ComposeResult:
        wiki_list = wikilist(config["wikistorage"])
        yield Label("Select wiki", id="wikilist_label")
        yield Input(id="search")
        with VerticalScroll(id="scroller"): 
            for wikiname in wiki_list:
                yield Button(wikiname, classes="wiki_button") # display all wiki
    
    def action_delete_wiki(self) -> None:
        """delete wiki via pushing screen"""
        global dirtodelete
        focused = self.screen.focused
        # Checking is focused widget a button
        if isinstance(focused, Button):
            dirtodelete = str(focused.label)
            self.app.push_screen("ConfirmDelete")
        else:
            self.notify("Can not delete wiki, the focused widhet is not a wiki")
        

    def on_input_changed(self, event: Input.Changed) -> None:
        """filter wikis by input"""
        search_text = event.value.lower() # saves input to search case-insensitive
        all_buttons = self.query(Button) 
        for button in all_buttons:
            button_text = str(button.label).lower()
            if search_text in button_text:
                button.styles.display = "block" # Keeps button visible if it's label matches woth query
            else:
                button.styles.display = "none" # Hides button if it's label doesn't match the query 

    def on_screen_resume(self) -> None:
        wiki_list = wikilist(config["wikistorage"])
        self.query(".wiki_button").remove()
        for wikiname in wiki_list:
            self.query_one("#scroller").mount(Button(wikiname, classes="wiki_button"))
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """open wiki on button clicked"""
        if event.button.has_class("wiki_button"): # do only if button is wiki button
            global path_to_wiki
            path_to_wiki = Path(f"./{event.button.label}/") 
            self.app.push_screen("Wiki")

class ConfirmDelete(Screen):
    """screen to confirm wiki deleting"""
    BINDINGS = [
        Binding("h", "app.focus_previous"),
        Binding("l", "app.focus_next")
]

    def compose(self) -> ComposeResult:
        yield Container(
        Static("Are you sure want to delete wiki?", id="deletetitle"),
        Horizontal(
            Button("Yes", id="yes", classes="delete_button"),
            Button("No", id="no", classes="delete_button"),
            ),
            id="deletecontainer"
        )

    @on(Button.Pressed, "#yes")
    def delete_wiki(self) -> None:
        global dirtodelete
        shutil.rmtree(dirtodelete, ignore_errors=True)
        dirtodelete = None
        self.app.push_screen("WikiListScreen")

    @on(Button.Pressed, "#no")
    def cancel(self) -> None:
        global dirtodelete
        dirtodelete = None
        self.app.push_screen("WikiListScreen")

class WikiCreator(Screen):
    """screen creating wiki"""
    BINDINGS = [
    Binding("ctrl+enter", "confirm"),
    Binding("ctrl+escape", "app.push_screen('WikiListScreen')"),
    Binding("ctrl+k", "app.focus_previous", priority=True),
    Binding("ctrl+j", "app.focus_next", priority=True)
]

    def compose(self) -> ComposeResult:
        yield Input(id="name_input", placeholder="Wiki name", type="text")
        yield Input(id="description_input", placeholder="Wiki description(optional)", type="text")

    def action_confirm(self) -> None:
        """validating input and configrming"""
        name = self.query_one("#name_input").value
        description = self.query_one("#description_input").value
        if len(name) == 0:
            self.notify("Fill the name input!")
        else:
            result = createwiki(name, description)
            if result == WriteStatus.FAILED:
                self.notify(f"{result.value}")
            elif result == WriteStatus.SUCCESS:
                self.notify(f"{result.value}")
            self.app.push_screen("WikiListScreen")
        

class AboutScreen(Screen):
    """screen with info about microwiki"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Markdown(ABOUT, id="about_container")


class CoreApp(App):
    """a main app class"""

    TITLE = "microwiki"
    CSS_PATH = "data/style.tcss"
    BINDINGS = [
        Binding("m", "to_menu()", "Back to main menu"),
    ]

    def on_mount(self):
        """mounting screens, pushing screens and aplying theme"""
        self.install_screen(WikiScreen(), name="Wiki")
        self.install_screen(MainMenu(), name="MainMenu")
        self.install_screen(WikiListScreen(), name="WikiListScreen")
        self.install_screen(AboutScreen(), name="About")
        self.install_screen(WikiCreator(), name="WikiCreator")
        self.install_screen(ConfirmDelete(), name="ConfirmDelete")
        self.install_screen(WikiFileManager(), name="WikiFileManager")
        self.push_screen("MainMenu")
        self.theme = config["theme"]
    
    async def action_to_menu(self) -> None:
        """back to mainmenu"""
        os.chdir(config["wikistorage"])
        self.app.push_screen("MainMenu")

    @on(Button.Pressed, "#Wiki")
    def move_to_wikilist(self) -> None:
        self.push_screen("WikiListScreen")

    @on(Button.Pressed, "#About")
    def move_to_about_screen(self) -> None:
        self.push_screen("About") 

def main():
    """a main app runner function"""
    global app     
    global config 
    global moving_via_fm
    moving_via_fm = False 

    # checking config data types
    config = parse_config()

    print("START CHECKING DATA TYPES FROM CONFIG")
    if type(config["theme"]) != str:
        print("error: 'theme' value in config is not str") 
        print("exiting")
        sys.exit(1)
    else:
        print("succes: 'theme' value in config is str")
    
    if type(config["wikistorage"]) != str:
        print("error: 'wikistorage' value in config is not str")
        print("exiting")
        sys.exit(1)
    else:
        print("succes: 'wikistorage' value in config is str")


    print("all data types from config are valid") 
    print("starting app")
    sleep(1)

    # running app
    app = CoreApp()
    app.run()
