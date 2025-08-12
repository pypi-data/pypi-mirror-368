from . import display
import urllib.error
from pathlib import Path
import os

from . import operations as ops


class Docker:

    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        display.print_log("Installing Docker...")
        existing_version = self.get_version()

        if existing_version:
            display.print_complete(f"Docker already installed ({existing_version})")
            if not self.force:
                return

        if self.os_env["os_id"] in ["debian", "ubuntu"]:
            self.install_via_apt()
        else:
            display.print_error(
                f"This operating configuration isn't currenly supported. Please contact the Shoestring team for support and provide them with these details:\n{self.os_env}"
            )

    def update(self):
        display.print_log("Updating Docker...")

        if self.os_env["os_id"] in ["debian", "ubuntu"]:
            self.update_via_apt()
        else:
            display.print_error(
                f"This operating configuration isn't currenly supported. Please contact the Shoestring team for support and provide them with these details:\n{self.os_env}"
            )

    def get_version(self):
        # fetch updates
        command = [
            "docker",
            "-v",
        ]
        display.print_debug("Checking Docker Version...")
        result = ops.logged_subprocess_run(command)

        if result and result.returncode == 0:
            return result.stdout.decode().strip()
        else:
            return None

    def install_via_apt(self):
        self.set_up_apt_source()

        # for install
        ops.subprocess_exec(
            "Install docker",
            [
                "apt-get",
                "install",
                "-qq",
                "docker-ce",
                "docker-ce-cli",
                "containerd.io",
                "docker-buildx-plugin",
                "docker-compose-plugin",
            ],
        )

        ops.subprocess_exec(
            "Create docker permissions group", ["groupadd", "docker", "-f"]
        )

        ops.subprocess_exec(
            "Let the user account run Docker without elevated privileges by adding user to permissions group",
            "usermod -a -G docker $SUDO_USER",
        )

        sudo_user = os.getenv("SUDO_USER")
        if sudo_user == "":
            display.print_error("Unable to get user, run 'sudo usermod -a -G docker $USER' once this setup has completed to fix this.")
            
        ops.subprocess_exec(
            "Start Docker in the background", ["systemctl", "start", "docker"]
        )
        ops.subprocess_exec(
            "Set Docker to run in the background whenever the system boots up",
            ["systemctl", "enable", "docker"],
        )

        installed_version = self.get_version()
        if installed_version:
            display.print_complete(f"Docker installed ({installed_version})")
        else:
            display.print_error(f"Docker installation failed!")

        # Prompt to restart

    def update_via_apt(self):
        ops.subprocess_exec(
            "Update docker",
            [
                "apt-get",
                "install",
                "-qq",
                "docker-ce",
                "docker-ce-cli",
                "containerd.io",
                "docker-buildx-plugin",
                "docker-compose-plugin",
            ],
        )

        installed_version = self.get_version()
        if installed_version:
            display.print_complete(f"Complete: {installed_version}")
        else:
            display.print_error(f"Docker update failed!")

    def set_up_apt_source(self):
        apt_source_file = Path("/etc/apt/sources.list.d/docker.list")

        if apt_source_file.exists():
            display.print_complete("APT source already set up")
            if not self.force:
                return

        display.print_log("Setting up docker apt source...")

        ops.subprocess_exec("Update apt index", ["apt-get", "update"])
        ops.subprocess_exec(
            "Ensure https certificates are installed and up-to-date",
            ["apt-get", "install", "ca-certificates"],
        )

        keyring_dir = Path("/etc/apt/keyrings")

        ops.logged_ensure_dir(keyring_dir, mode=0o755)

        keyring_file = keyring_dir / "docker.asc"

        try:
            ops.logged_ensure_file(keyring_file, mode=0o644)
        except PermissionError:
            display.print_error(
                f"Elevated permissions required to write to the {keyring_file} file.\nPlease run with sudo."
            )

        URL_SET = {
            "debian": "https://download.docker.com/linux/debian",
            "ubuntu": "https://download.docker.com/linux/ubuntu",
        }

        base_url = URL_SET[self.os_env["os_id"]]
        try:
            url = f"{base_url}/gpg"
            keyring = ops.logged_file_download(url)
        except urllib.error.HTTPError:
            display.print_error("Failed to Fetch Docker keyring certificate")
            return False

        try:
            ops.logged_file_write(keyring_file, "wb", keyring)
            display.print_complete("Downloaded keyring file")
        except PermissionError:
            display.print_error(
                f"Elevated permissions required to write to the {keyring_file} file.\nPlease run with sudo."
            )

        result = ops.logged_subprocess_run(["dpkg", "--print-architecture"])
        dpkg_arch = result.stdout.decode().strip()

        source_desc = f'deb [arch={dpkg_arch} signed-by=/etc/apt/keyrings/docker.asc] {base_url} {self.os_env["codename"]} stable'
        ops.logged_file_write(apt_source_file, "w", source_desc)
        display.print_complete("Created apt source file")

        ops.subprocess_exec("Update apt index", ["apt-get", "update"])
        display.print_complete("Apt source set up for docker")
