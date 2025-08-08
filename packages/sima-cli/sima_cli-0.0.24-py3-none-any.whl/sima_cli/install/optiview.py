import sys
import platform
import click
import json
import tarfile
import os
import subprocess
from pathlib import Path
from sima_cli.download import download_file_from_url
from sima_cli.utils.env import is_sima_board
from sima_cli.utils.config_loader import load_resource_config

def install_optiview():
    try:
        # Special path for SiMa DevKit
        if is_sima_board():
            click.echo("🛠 Detected SiMa DevKit. Cleaning up existing installation...")
            subprocess.run(["sudo", "pip3", "uninstall", "-y", "optiview"], check=True)
            click.echo("📦 Installing Optiview via pip...")
            subprocess.run(["sudo", "pip3", "install", "optiview"], check=True)
            click.echo("✅ Optiview installed successfully on DevKit.")
            return

        cfg = load_resource_config()
        download_url_base = cfg.get('public').get('download').get('download_url')

        # Normal flow for other platforms
        click.echo("📥 Fetching Optiview version info...")
        version_url = f"{download_url_base}optiview/metadata.json"
        downloads_dir = Path.home() / "Downloads" / "optiview-installer"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Always redownload the metadata file to get the latest version
        metadata_path = downloads_dir / "metadata.json"
        if metadata_path.exists():
            metadata_path.unlink()

        metadata_path = download_file_from_url(version_url, dest_folder=downloads_dir, internal=False)

        with open(metadata_path, "r") as f:
            version_data = json.load(f)
            latest_version = version_data.get("latest")

        if not latest_version:
            raise Exception("Unable to retrieve latest version info.")

        # Determine architecture
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin" and machine == "arm64":
            arch = "aarch64"
        else:
            arch = "x86_64"

        pkg_url = f"{download_url_base}optiview/optiview-installation-{arch}-{latest_version}.tar.gz"
        click.echo(f"🌐 Downloading Optiview ({arch} v{latest_version})...")

        archive_path = download_file_from_url(pkg_url, dest_folder=downloads_dir)

        click.echo(f"📦 Extracting to {downloads_dir}...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=downloads_dir)

        install_script = "install.bat" if system == "windows" else "install.sh"
        script_path = os.path.join(downloads_dir, install_script)

        if not os.path.isfile(script_path):
            raise Exception(f"Installation script not found: {script_path}")

        click.echo(f"🚀 Running installer: {install_script}")
        if system == "windows":
            subprocess.run(["cmd", "/c", os.path.basename(script_path)], check=True, cwd=downloads_dir)
        else:
            subprocess.run(["bash", os.path.basename(script_path)], check=True, cwd=downloads_dir)

        script_name = "run.bat" if platform.system() == "Windows" else "run.sh"
        click.echo(f"✅ Optiview installed successfully. Run {downloads_dir}/{script_name} to start OptiView")

    except Exception as e:
        click.echo(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_optiview()