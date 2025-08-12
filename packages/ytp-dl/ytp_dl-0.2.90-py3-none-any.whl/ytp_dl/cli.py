#!/usr/bin/env python3
import argparse
from .downloader import download_video, manual_login

def main():
    parser = argparse.ArgumentParser(description="YouTube downloader over Mullvad VPN (ytp-dl)")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--resolution", help="Desired resolution (e.g., 1080)", default=None)
    parser.add_argument("--extension", help="Desired file extension (e.g., mp4, mp3)", default=None)
    parser.add_argument("--login", dest="mullvad_account", help="(Optional) One-time Mullvad login: account number")
    args = parser.parse_args()

    # Optional one-time login from CLI (does not connect)
    if args.mullvad_account:
        manual_login(args.mullvad_account)

    result = download_video(
        url=args.url,
        resolution=args.resolution,
        extension=args.extension
    )

    if result:
        print(f"Successfully downloaded: {result}")
    else:
        print("Download failed")
        exit(1)

if __name__ == "__main__":
    main()
