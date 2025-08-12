#!/usr/bin/python3

# sudo apt install libgirepository-2.0-dev
from typing import Callable
import gi
import sys
import importlib.metadata as metadata

gi.require_version("Gtk", "4.0")
# so Gtk for graphics
# Gio for data files
# GLib.Error (FileDialog?)
from gi.repository import Gtk, Gio, GLib

# libAdapta uses its own module name (Adap.ApplicationWindow etc..).
# We would normally import it like this:
# from gi.repository import Adap
# Since libAdapta and libAdwaita use the same class names,
# the same code can work with both libraries, as long as we rename
# the module when importing it
try:
    gi.require_version("Adap", "1")
    from gi.repository import Adap as Adw
except ImportError or ValueError as ex:
    # To use libAdwaita, we would import this instead:
    print("Using Adwaita as Adapta not found:\n", ex)
    gi.require_version("Adw", "1")
    from gi.repository import Adw

from .adapta_test import _, MainWindow, domain


# doesn't need to be class method
def button(icon: str, callback: Callable):
    button = Gtk.Button()
    button.set_icon_name(icon)
    button.connect("clicked", callback)
    return button


class MyWindow(MainWindow):  # pyright: ignore
    # override for different behaviour
    def layout(self):
        # multipaned content by selection widget
        # set list name [] and button nav {}
        self.pages = [self.content()]
        self.buttons = {
            "left": [self.burger()],  # the burger menu
            "right": [button("utilities-terminal", self.about)],  # about icon
            # 1:1 pages match of subtitle injection
            "subs": [_("Sub Title")],
            # 1:1 pages match of icon names injection
            "icons": ["utilities-terminal"],
        }

    # methods to define navigation pages
    def content(self) -> Adw.NavigationPage:
        # Create the content page _() for i18n
        content_box = self.fancy()
        status_page = Adw.StatusPage()
        status_page.set_title("Python libAdapta Example")
        status_page.set_description(
            "Split navigation view, symbolic icon and a calendar widget to feature the accent color."
        )
        status_page.set_icon_name("document-open-recent-symbolic")
        calendar = Gtk.Calendar()
        content_box.append(status_page)
        content_box.append(calendar)
        # set title and bar
        return self.top(content_box, _("Content"), **{})

    def about(self, action):
        about = Gtk.AboutDialog()
        about.set_transient_for(
            self
        )  # Makes the dialog always appear in from of the parent window
        about.set_modal(
            True
        )  # Makes the parent window unresponsive while dialog is showing
        about.set_authors(
            [
                "Simon Jackson",  # project authors
                "Linux Mint Team",
                "GNOME Adwaita Team",  # teams
                "All Di Nice",  # ha, ha!
            ]
        )
        about.set_copyright("(C) 2025 Simon P. Jackson")
        about.set_license_type(Gtk.License.LGPL_3_0_ONLY)
        about.set_website("https://github.com/jackokring/mint-python-adapta")
        about.set_website_label("xapp_adapta")
        about.set_version(metadata.version("xapp_adapta"))
        about.set_logo_icon_name("utilities-terminal")
        about.set_visible(True)


class MyApp(Adw.Application):  # pyright: ignore
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.connect("open", self.on_open)
        self.connect("command-line", self.on_command_line)
        self.set_flags(Gio.ApplicationFlags.HANDLES_OPEN)
        self.set_flags(Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.win = None

    def on_activate(self, app):
        if not self.win:
            self.win = MyWindow(application=app)
        self.win.present()

    # detects if present, but doesn't print anything?
    def on_open(self, app, files, n_files, hint):
        self.on_activate(app)
        for file in n_files:
            print("File to open: " + file.get_path() + "\n")

    def on_command_line(self, app, argv):
        self.on_activate(app)
        for file in argv.get_arguments()[1:]:
            print("File to open: " + file + "\n")
        return 0  # exit code


def main():
    app = MyApp(application_id=domain)
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    main()
