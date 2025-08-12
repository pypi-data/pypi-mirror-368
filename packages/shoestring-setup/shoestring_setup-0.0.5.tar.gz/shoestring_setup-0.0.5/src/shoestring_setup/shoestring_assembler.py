from . import display
from pathlib import Path
import os

from . import operations as ops


class Assembler:

    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        display.print_log("Installing Shoestring Assembler...")

        sudo_user = os.getenv("SUDO_USER")
        if sudo_user == "":
            display.print_error(
                "Unable to get user, run 'pipx install shoestring-assembler' once this setup has completed to fix this."
            )
        else:
            ops.subprocess_exec(
                "Install shoestring assembler",
                ["sudo", "-u", sudo_user, "pipx", "install", "shoestring-assembler"],
            )

            ops.subprocess_exec(
                "Ensure command completions are active",
                ["sudo", "-u", sudo_user, "pipx", "completions"],
            )

            result = ops.logged_subprocess_run(
                ["sudo", "-u", sudo_user, "/bin/sh", "-c", "echo ~"]
            )
            print(result)
            user_home_raw = result.stdout.decode().strip()
            user_home = Path(user_home_raw)

            # Add desktop shortcut to app
            desktop_shortcut = f"""
                [Desktop Entry]
                Name=Shoestring
                Exec={str(user_home / ".local/bin/shoestring")} app
                Comment=shoestring assembler
                Type=Application
                Terminal=true
                Encoding=UTF-8
                Categories=Utility;
            """
            ops.logged_file_write(
                "/usr/share/applications/shoestring.desktop",
                mode="w",
                content=desktop_shortcut,
            )  # file permissions should be 644 if needed

    def update(self):
        display.print_log("Updating Shoestring Assembler...")

        sudo_user = os.getenv("SUDO_USER")
        if sudo_user == "":
            display.print_error(
                "Unable to get user, run 'pipx upgrade shoestring-assembler' once this setup has completed to fix this."
            )
        else:
            ops.subprocess_exec(
                "Install shoestring assembler",
                ["sudo", "-u", sudo_user, "pipx", "upgrade", "shoestring-assembler"],
            )
