from pathlib import Path

from . import operations as ops
from . import display


class Rsyslog:
    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        display.print_log("Installing rsyslog...")
        self._do_install()

    def _do_install(self):
        ops.subprocess_exec(
            "Install rsyslog", ["sudo", "apt-get", "-qq", "install", "rsyslog"]
        )

        log_directory = Path("/var/log/containers")
        ops.logged_ensure_dir(log_directory, mode=0o755)
        ops.logged_ensure_owner_group(log_directory, owner="root", group="adm")
        display.print_complete("Prepared log directory")

        docker_conf_file = Path("/etc/rsyslog.d/40-docker.conf")
        rsyslog_conf = """
        # Create a template for the target log file
        $template CUSTOM_LOGS,"/var/log/containers/%programname%.log"

        if $programname startswith  'docker-' then ?CUSTOM_LOGS
        & ~
        """

        ops.logged_file_write(docker_conf_file, "w", rsyslog_conf)
        display.print_complete("Generated config file")

        ops.subprocess_exec(
            "Restart rsyslog", ["sudo", "systemctl", "restart", "rsyslog"]
        )

    def update(self):
        display.print_log("Updating rsyslog...")
        self._do_install()
