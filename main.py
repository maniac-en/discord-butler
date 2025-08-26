#!/usr/bin/env python3
import subprocess
import shutil
import sys
import requests

from os.path import exists

from packaging.version import Version
from urllib.parse import ParseResult, urlparse

TMP_DIR = "/tmp"


def sys_exit_error():
    sys.exit(1)


def install_discord():
    """Install Discord on Debian/Ubuntu systems."""
    try:
        print("Discord not found. Installing Discord...")

        # Download Discord .deb package
        response = requests.head(
            "https://discord.com/api/download/stable?platform=linux&format=deb",
            allow_redirects=False,
        )

        if response.status_code != requests.codes.found:
            print("Error: Could not get Discord download URL")
            return False

        download_url = response.headers["Location"]
        filename = download_url.split("/")[-1]
        filepath = f"{TMP_DIR}/{filename}"

        print("Downloading Discord...")
        download_response = requests.get(download_url, stream=True)
        download_response.raw.decode_content = True

        if download_response.status_code == requests.codes.ok:
            with open(filepath, "wb") as f:
                for chunk in download_response.iter_content(chunk_size=1024):
                    f.write(chunk)
        else:
            print("Error downloading Discord")
            return False

        if not exists(filepath):
            print("Error: downloaded file doesn't exist")
            return False

        print(f"File downloaded successfully: {filepath}")

        # Use pkexec for authentication
        print("Authentication required to install Discord...")
        proc = subprocess.run(
            ["pkexec", "dpkg", "-i", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr)

        if proc.returncode == 0:
            print("Discord installed successfully!")
            return True
        elif proc.returncode == 126 or proc.returncode == 127:
            # User cancelled authentication or permission denied
            print("Authentication cancelled or failed. Cannot install Discord.")
            return False
        else:
            # Installation failed, try to fix dependencies
            print("Attempting to fix dependencies...")
            dep_proc = subprocess.run(
                ["pkexec", "apt", "-f", "install", "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if dep_proc.returncode == 0:
                print("Dependencies fixed. Discord should now be available.")
                return True
            else:
                print("Error installing Discord and fixing dependencies")
                return False

    except Exception as e:
        print(f"Error installing Discord: {e}")
        return False


discord_bin: str | None = shutil.which("discord")
dpkg_bin: str | None = shutil.which("dpkg")

if not dpkg_bin:
    print("Error: dpkg binary not found as executable in $PATH")
    print("This script only supports Debian/Ubuntu systems with dpkg package manager")
    sys_exit_error()

if not discord_bin:
    if install_discord():
        discord_bin = shutil.which("discord")
        if not discord_bin:
            print(
                "Error: Discord installation completed but binary still not found in $PATH"
            )
            print("You may need to restart your terminal or add Discord to your PATH")
            sys_exit_error()
    else:
        print("Failed to install Discord. Please install it manually and try again.")
        sys_exit_error()

current_version: Version

try:
    proc = subprocess.Popen(
        discord_bin,
        stdout=subprocess.PIPE,
        text=True,
    )
    version_line: str = proc.stdout.readline()
    current_version = Version(version_line[7:])
    print(f"Current version: {current_version}")
    proc.kill()
except Exception as e:
    print(f"Error getting Discord version: {e}")
    sys_exit_error()

response: requests.Response = requests.head(
    "https://discord.com/api/download/stable?platform=linux&format=deb",
    allow_redirects=False,
)

if response.status_code == requests.codes.found:
    try:
        latest_version_parsed_url: ParseResult = urlparse(
            url=response.headers["Location"]
        )
    except Exception as e:
        print(f"Error parsing version URL: {e}")
        sys_exit_error()
else:
    print("Error: something went wrong with the URL redirection")
    sys_exit_error()

latest_version_file_name: str = latest_version_parsed_url.path.rsplit(
    sep="/", maxsplit=1
)[-1]
latest_version: Version = Version(latest_version_file_name[8:-4])
print(f"Latest version: {latest_version}")

if latest_version <= current_version:
    print("\nStarting discord...")
    subprocess.Popen(discord_bin, start_new_session=True)
    sys.exit()
else:
    print(f"Downloading the latest version: {latest_version}")
    response: requests.Response = requests.get(
        url=latest_version_parsed_url.geturl(),
        stream=True,
    )
    response.raw.decode_content = True
    downloaded_file_path: str = f"{TMP_DIR}/{latest_version_file_name}"

    try:
        if response.status_code == requests.codes.ok:
            with open(downloaded_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
    except Exception as e:
        print(f"Error downloading Discord: {e}")
        sys_exit_error()

    if exists(downloaded_file_path):
        print(f"File downloaded successfully: {downloaded_file_path}")
    else:
        print("Error: downloaded file doesn't exist or insufficient permissions")
        sys_exit_error()

    print("Authentication required to install newer version of Discord...")
    proc = subprocess.run(
        args=["pkexec", dpkg_bin, "-i", downloaded_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr)
    except Exception as e:
        print(e)
        sys_exit_error()

    if proc.returncode == 0:
        print("\nRunning the newly installed discord...")
        subprocess.Popen(discord_bin, start_new_session=True)
    elif proc.returncode == 126 or proc.returncode == 127:
        print("Authentication cancelled or failed. Exiting...")
        sys_exit_error()
    else:
        print("There were some issues installing the newer version of discord...")
        sys_exit_error()
