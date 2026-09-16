"""all the UI of app"""

import os
import sys
from pathlib import Path
from time import sleep
import shutil

from about import get_about_info
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Header,
    Input,
    Label,
    Markdown,
    MarkdownViewer,
    Static,
    TextArea,
)
from utils.config_utils import parse_config
from utils.editor_utils import createwiki, writefile
from utils.wikiparser import parselocalwiki, wikilist

ABOUT = get_about_info()

class WikiScreen(Screen):
    """wiki screen, displays wiki content"""
    BINDINGS = [
        Binding("m", "app.push_screen('WikiListScreen')", "back to wiki list", priority=True),
        Binding("alt+e", "toggle_editor()", "toggle markdown editor", priority=True),
        Binding("ctrl+s", "write()", "write changes to file", priority=True)
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield MarkdownViewer(open_links=False, id="wikiviewer") 
        yield TextArea(id="markdown_editor", language="markdown")
    
    def on_mount(self) -> None:
        self.query_one("#markdown_editor").styles.display = "none" 

    def action_toggle_editor(self) -> None:
        """toggle editor"""
        md_text = self.query_one("#wikiviewer").document.source # get text from markdown viewer
        if self.query_one("#markdown_editor").styles.display == "none":
            self.query_one("#markdown_editor").styles.display = "block"
            self.query_one("#markdown_editor").text = md_text # load text from variable to editor
        elif self.query_one("#markdown_editor").styles.display == "block":
            self.query_one("#markdown_editor").styles.display = "none"

    async def on_screen_resume(self) -> None:
        """start wiki after pushing screen"""

        global mdfile_path
        viewer = self.query_one("#wikiviewer")
        os.chdir(config["wikistorage"])
        wikijson = parselocalwiki(path_to_wiki) # get info about wiki
        mdfile = wikijson["enterpoint"]
        mdfile_path = Path(f"{config["wikistorage"]}/{path_to_wiki}/{mdfile}")
        if mdfile_path.exists() == True:
            await viewer.go(mdfile_path) # open main file of wiki
        else:
            self.app.push_screen("WikiListScreen")
            self.notify(f"{mdfile_path!s} Path not exists") # notify if there arent main file of wiki

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
        if result != "succes":
            self.notify(f"file {mdfile_path} not writen cause of {result}") 
        else:
            self.notify(f"file {mdfile_path} succes writen")
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
            if result != "succes":
                self.notify(f"An error ocured creating wiki: {result}")
            else:
                self.notify("Wiki sucess created")
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
        self.push_screen("MainMenu")
        self.theme = config["theme"]
    
    async def action_to_menu(self) -> None:
        """back to mainmenu"""
        os.chdir(config["wikistorage"])
        self.app.push_screen("MainMenu")

    @on(Button.Pressed, "#Wiki")
    def mowetowikilist(self) -> None:
        self.push_screen("WikiListScreen")

    @on(Button.Pressed, "#About")
    def mowetoaboutscreen(self) -> None:
        self.push_screen("About") 
        
def main():
    """a main app runner function"""
    global app     
    global config 
    
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

    if type(config["allow_edit"]) != bool:
        print("error: 'allow_edit' value in config is not bool") 
        print("exiting")
        sys.exit(1)
    else:
        print("succes: 'allow_edit' value in config is bool")

    if type(config["editor"]) != str:
        print("error: 'editor' value in config is not str") 
        print("exiting")
        sys.exit(1)
    else:
        print("succes: 'editor' value in config is str")

    print("all data types from config are valid") 
    print("starting app")
    sleep(1)

    # running app
    app = CoreApp()
    app.run()
