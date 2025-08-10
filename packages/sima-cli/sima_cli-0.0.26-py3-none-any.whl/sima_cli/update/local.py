import os
from typing import Tuple
import pty
import click

from sima_cli.utils.env import is_board_running_full_image, get_exact_devkit_type

def _run_local_cmd(command: str, passwd: str) -> bool:
    """
    Run a local command using a pseudo-terminal (pty) to force live output flushing,
    and optionally pass a sudo password.
    """
    click.echo(f"🖥️  Running: {command}")

    needs_sudo = command.strip().startswith("sudo")
    if needs_sudo:
        command = f"sudo -S {command[len('sudo '):]}"

    try:
        pid, fd = pty.fork()

        if pid == 0:
            # Child process: execute the shell command
            os.execvp("sh", ["sh", "-c", command])
        else:
            if needs_sudo:
                os.write(fd, (passwd + "\n").encode())

            while True:
                try:
                    output = os.read(fd, 1024).decode()
                    if not output:
                        break
                    for line in output.splitlines():
                        click.echo(line)
                except OSError:
                    break

            _, status = os.waitpid(pid, 0)
            return os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0

    except Exception as e:
        click.echo(f"❌ Command execution error: {e}")
        return False


def get_local_board_info() -> Tuple[str, str, bool]:
    """
    Retrieve the local board type and build version by reading /etc/build or /etc/buildinfo.

    Returns:
        (board_type, build_version, fdt_name, full_image): Tuple of strings, or ('', '') on failure.
    """
    board_type = ""
    build_version = ""
    build_file_paths = ["/etc/build", "/etc/buildinfo"]

    for path in build_file_paths:
        try:
            if os.path.isfile(path):
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("MACHINE"):
                            board_type = line.split("=", 1)[-1].strip()
                        elif line.startswith("SIMA_BUILD_VERSION"):
                            build_version = line.split("=", 1)[-1].strip()
                if board_type or build_version:
                    break  # Exit early if data found
        except Exception:
            continue

    fdt_name = get_exact_devkit_type()

    return board_type, build_version, fdt_name, is_board_running_full_image()


def push_and_update_local_board(troot_path: str, palette_path: str, passwd: str, flavor: str):
    """
    Perform local firmware update using swupdate commands.
    Calls swupdate directly on the provided file paths.
    """
    click.echo("📦 Starting local firmware update...")

    try:
        # Run tRoot update
        if troot_path != None:
            click.echo("⚙️  Flashing tRoot image...")
            if not _run_local_cmd(f"sudo swupdate -H simaai-image-troot:1.0 -i {troot_path}", passwd):
                click.echo("❌ tRoot update failed.")
                return
            click.echo("✅ tRoot update completed.")
            
        # Run Palette update
        click.echo("⚙️  Flashing System image...")
        _flavor = 'palette' if flavor == 'headless' else 'graphics'
        if not _run_local_cmd(f"sudo swupdate -H simaai-image-{_flavor}:1.0 -i {palette_path}", passwd):
            click.echo("❌ System image update failed.")
            return
        click.echo("✅ System image update completed. Please powercycle the device")

    except Exception as e:
        click.echo(f"❌ Local update failed: {e}")