#!/usr/bin/env python3
import subprocess
import shutil
import sys
import requests
import tkinter as tk
from tkinter import simpledialog

from os.path import exists

from packaging.version import Version
from urllib.parse import ParseResult, urlparse

TMP_DIR = "/tmp"


def sys_exit_error():
    sys.exit(1)


def get_sudo_password(message="Enter sudo password:"):
    """Get sudo password from user."""
    root = tk.Tk()
    root.withdraw()
    sudo_pass = simpledialog.askstring(
        "Discord Butler",
        message,
        show="*",
    )
    root.destroy()
    return sudo_pass


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
        
        # Get sudo password and install
        sudo_pass = get_sudo_password("Enter sudo password to install Discord:")
        if not sudo_pass:
            print("Password not provided, cannot install Discord")
            return False
            
        proc = subprocess.Popen(
            ["sudo", "-S", "dpkg", "-i", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        
        out, err = proc.communicate(input=(sudo_pass + "\n").encode())
        print(out.decode())
        if err:
            print(err.decode())
        
        if proc.returncode == 0:
            print("Discord installed successfully!")
            return True
        else:
            # Try to fix dependencies
            print("Attempting to fix dependencies...")
            dep_proc = subprocess.run(
                ["sudo", "-S", "apt", "-f", "install", "-y"], 
                input=(sudo_pass + "\n").encode(), 
                capture_output=True
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
            print("Error: Discord installation completed but binary still not found in $PATH")
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

    sudo_pass = get_sudo_password("Enter sudo password to install newer version of discord:")

    if not sudo_pass:
        print("Password not provided, exiting...")
        sys_exit_error()
    proc = subprocess.Popen(
        args=["sudo", "-S", dpkg_bin, "-i", downloaded_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )

    try:
        out, err = proc.communicate(input=(sudo_pass + "\n").encode())
        print(out.decode())
        if err:
            print(err.decode())
    except Exception as e:
        print(e)
        proc.kill()
        sys_exit_error()

    if proc.returncode == 0:
        print("\nRunning the newly installed discord...")
        subprocess.Popen(discord_bin, start_new_session=True)
    else:
        print("There were some issues installing the newer version of discord...")
        sys_exit_error()
