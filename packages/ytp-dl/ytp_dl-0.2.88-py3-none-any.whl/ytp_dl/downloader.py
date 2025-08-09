#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import shutil

def run_command(cmd, check=True):
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {cmd}\n{e.output.strip()}") from e

def get_venv_path():
    """Get the expected virtual environment path"""
    return "/opt/yt-dlp-mullvad/venv"

def validate_environment():
    """Validate that we're running in the correct environment"""
    venv_path = get_venv_path()

    # Check if we're in the expected venv
    current_venv = os.environ.get('VIRTUAL_ENV')
    if not current_venv or current_venv != venv_path:
        raise RuntimeError(
            "This package must run from the virtual environment at "
            f"{venv_path}\nCurrent VIRTUAL_ENV: {current_venv}\n\n"
            "To fix:\n"
            f"  1) python3 -m venv {venv_path}\n"
            f"  2) source {venv_path}/bin/activate\n"
            "  3) pip install ytp-dl"
        )

    # Check if yt-dlp exists in the venv
    ytdlp_path = f"{venv_path}/bin/yt-dlp"
    if not os.path.exists(ytdlp_path):
        raise RuntimeError(
            f"yt-dlp not found at {ytdlp_path}. Reinstall the package inside the venv."
        )

    return venv_path

def check_mullvad():
    """Check if Mullvad CLI is available"""
    if not shutil.which("mullvad"):
        raise RuntimeError(
            "Mullvad CLI not found.\n"
            "Install:\n"
            "  curl -fsSLo /tmp/mullvad.deb https://mullvad.net/download/app/deb/latest/\n"
            "  sudo apt install -y /tmp/mullvad.deb"
        )

def is_logged_in() -> bool:
    """Return True if Mullvad is already logged in on this machine."""
    out = run_command("mullvad account get", check=False) or ""
    low = out.lower()
    # Mullvad prints account info if logged in; if not, it mentions 'not logged in'
    return "not logged in" not in low

def manual_login(mullvad_account: str):
    """One-time login helper (no connect)."""
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account for manual login.")
    if is_logged_in():
        print("Already logged into Mullvad on this server.")
        return
    print("Logging into Mullvad (one-time)…")
    run_command(f"mullvad account login {mullvad_account}")
    print("Login complete. No VPN connection was started.")

def require_logged_in():
    """Ensure we are logged into Mullvad, but do not log in automatically."""
    if not is_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server. "
            "SSH in and run: mullvad account login <ACCOUNT> (one-time)."
        )

def wait_for_connection(timeout=10):
    """Poll Mullvad status until connected or timeout"""
    for _ in range(timeout):
        status = run_command("mullvad status", check=False) or ""
        if "Connected" in status:
            print("Mullvad VPN connected.")
            return True
        time.sleep(1)
    print("Failed to confirm Mullvad VPN connection within timeout.")
    return False

def download_video(url, resolution=None, extension=None):
    """
    Download a video using yt-dlp through Mullvad VPN

    Args:
        url (str): YouTube URL
        resolution (str, optional): Desired resolution (e.g., '1080')
        extension (str, optional): Desired file extension (e.g., 'mp4', 'mp3')

    Returns:
        str: Path to downloaded file or None if failed
    """
    venv_path = validate_environment()
    check_mullvad()
    require_logged_in()  # <— do NOT create new devices automatically

    # Always rotate IP for this run: disconnect -> random relay -> connect
    run_command("mullvad disconnect", check=False)
    run_command("mullvad relay set location any", check=False)

    print("Connecting to Mullvad VPN...")
    run_command("mullvad connect")

    if not wait_for_connection():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    print(f"Downloading: {url}")

    try:
        audio_extensions = ["mp3", "m4a", "aac", "wav", "flac", "opus", "ogg"]
        if extension and extension.lower() in audio_extensions:
            # Audio download (leave as requested; m4a is most iOS-friendly)
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp -x --audio-format {extension} "
                f"--embed-metadata "
                f"--output '/root/%(title)s.%(ext)s' "
                f"--user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/91.0.4472.124 Safari/537.36' {url}"
            )
        else:
            # --- iOS-safe video download: H.264 (avc1) + AAC (mp4a), MP4 container, faststart ---
            if resolution:
                fmt = (
                    f"bv*[ext=mp4][vcodec^=avc1][height<={resolution}]"
                    f"+ba[ext=m4a][acodec^=mp4a]/"
                    f"b[ext=mp4][vcodec^=avc1][height<={resolution}]/"
                    f"b[ext=mp4][height<={resolution}]"
                )
            else:
                fmt = (
                    "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a][acodec^=mp4a]/"
                    "b[ext=mp4][vcodec^=avc1]/b[ext=mp4]"
                )

            merge_extension = (extension or "mp4").lower()
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp "
                f"-f \"{fmt}\" "
                f"--merge-output-format {merge_extension} "
                f"--embed-thumbnail --embed-metadata "
                f"--postprocessor-args \"ffmpeg:-movflags +faststart\" "
                f"--retries 3 --fragment-retries 3 "
                f"--output '/root/%(title)s.%(ext)s' "
                f"--user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/91.0.4472.124 Safari/537.36' {url}"
            )

        output = run_command(ytdlp_cmd)
        filename = None
        for line in output.splitlines():
            if line.startswith("[download]"):
                if "Destination:" in line:
                    filename = line.split("Destination: ")[1].strip()
                elif "has already been downloaded" in line:
                    start = line.find("] ") + 2
                    end = line.find(" has already been downloaded")
                    filename = line[start:end].strip()
                if filename and filename.startswith("'") and filename.endswith("'"):
                    filename = filename[1:-1]
                break

        if filename and os.path.exists(filename):
            print(f"DOWNLOADED_FILE:{filename}")
            return filename
        else:
            print("Download failed: File not found")
            return None

    except Exception:
        # Let api.py surface the error text
        raise
    finally:
        print("Disconnecting VPN...")
        run_command("mullvad disconnect", check=False)
