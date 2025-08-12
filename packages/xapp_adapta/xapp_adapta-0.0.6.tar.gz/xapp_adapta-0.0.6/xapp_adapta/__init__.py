# module initialization
from .adapta_test import main as test
from .adapta_main import main
import shutil, os


# make_local icons and desktop files
def make_local():
    file = os.path.dirname(__file__)
    home = os.path.expanduser("~")
    copy_files_of_type(file, home + "/.local/share/applications", ".desktop")
    copy_files_of_type(file, home + "/.local/share/icons", ".svg")


def copy_files_of_type(src_dir, dst_dir, extension):
    # Ensure destination exists
    os.makedirs(dst_dir, exist_ok=True)

    for filename in os.listdir(src_dir):
        if filename.lower().endswith(extension.lower()):
            src_path = os.path.join(src_dir, filename)
            dst_path = os.path.join(dst_dir, filename)
            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
