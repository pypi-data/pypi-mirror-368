from pathlib import Path

from . import operations as ops
from . import display

class LogRotate:
    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        display.print_log("Installing logrotate...")
        self._do_install()

    def _do_install(self):
        ops.subprocess_exec(
            "Install logrotate", ["sudo", "apt-get", "-qq", "install", "logrotate"]
        )

        logrotate_conf_file = Path("/etc/logrotate.d/docker")
        logrotate_conf = """
        /var/log/containers/*.log {
            rotate 7
            daily
            maxsize 100M
            missingok
            notifempty
            compress
            delaycompress
            postrotate
                /usr/lib/rsyslog/rsyslog-rotate
            endscript
        }
        """

        ops.logged_file_write(logrotate_conf_file, "w", logrotate_conf)
        display.print_complete("Generated config file")

        # prepare cron
        cron_daily_logrotate_file = Path("/etc/cron.daily/logrotate")
        if cron_daily_logrotate_file.exists():
            cron_hourly_dir = Path("/etc/cron.hourly")
            cron_hourly_logrotate_file = cron_hourly_dir/"logrotate"
            ops.logged_ensure_dir(cron_hourly_dir)

            ops.logged_copy(cron_daily_logrotate_file, cron_hourly_logrotate_file)

            display.print_complete("Cron configured to check for log rotation hourly")
        else:
            display.print_complete("Cron already configured to check for log rotation hourly")

    def update(self):
        display.print_log("Updating logrotate...")
        self.install()
