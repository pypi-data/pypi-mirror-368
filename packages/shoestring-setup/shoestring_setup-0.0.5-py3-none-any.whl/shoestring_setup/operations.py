from . import display
import subprocess
import urllib.request
from pathlib import Path
import shutil

"""
Contains logged versions of every key operation performed by the setup process.
Enables full logging trail of everything that is done.
"""


def logged_subprocess_run(command):
    command_str = " ".join(command) if isinstance(command, list) else command
    display.print_log(f"\[exec]: {command_str}")
    try:
        return subprocess.run(command, capture_output=True, shell=isinstance(command, str))
    except FileNotFoundError:
        return None


def logged_file_write(filename, mode, content):
    display.print_log(f"\[write]: {filename}")
    with open(filename, mode) as file:
        file.write(content)


def logged_file_download(url):
    display.print_log(f"\[download]: {url}")
    with urllib.request.urlopen(url) as web_in:
        content = web_in.read()
    return content

def logged_ensure_dir(dir_path:Path, mode=None):
    display.print_log(f"\[ensure_dir]: {dir_path} {oct(mode) if mode else ''}")
    kwargs= {
        "parents":True, # create parent directories if needed
        "exist_ok":True # don't throw error if already present
    }
    if mode:
        kwargs["mode"] = mode  # add permissions if specified
    dir_path.mkdir(**kwargs)


def logged_ensure_file(file_path: Path, mode=None):
    display.print_log(f"\[ensure_file]: {file_path} {oct(mode) if mode else ''}")
    kwargs = {"exist_ok": True}  # don't throw error if already present
    if mode:
        kwargs["mode"] = mode  # add permissions if specified
    file_path.touch(**kwargs)

def logged_ensure_owner_group(path:Path,owner=None,group=None):
    display.print_log(f"\[ownership]: {path} o: {owner} g: {group}")
    shutil.chown(path, owner, group)

def logged_copy(src:Path,dest:Path):
    display.print_log(f"\[copy]: {src} -> {dest}")
    shutil.copy2(src, dest)


def subprocess_exec(label, command):
    result = logged_subprocess_run(command)
    if result is None or result.returncode != 0:
        display.print_error(result.stderr.decode().strip())
    elif label:
        display.print_complete(label)
