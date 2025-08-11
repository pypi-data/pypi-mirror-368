import os
import shutil
from pathlib import Path


def new_plugin_generator():
    """
    Uses the template embedded in this package to generate a new plugin
    """
    # determine the path to the plugin_template directory
    plugin_template_path = os.path.join(Path(__file__).parent, "plugin_template")
    # copy all files from the plugin_template directory to the current directory
    shutil.copytree(plugin_template_path, ".", dirs_exist_ok=True)
    print("Plugin template generated successfully.")
