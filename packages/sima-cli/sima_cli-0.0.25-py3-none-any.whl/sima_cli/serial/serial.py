import platform
import subprocess
import shutil
import click
from sima_cli.utils.env import is_sima_board

def connect_serial(ctx, baud):
    """
    Connect to the UART serial console of the DevKit.
    Automatically installs required tools if missing.
    """
    if is_sima_board():
        click.echo("🚫 This command is not supported on the DevKit. Please run it from your host machine.")
        ctx.exit(1)

    system = platform.system()
    internal = ctx.obj.get("internal", False)

    if system == "Darwin":
        _connect_mac(baud)
    elif system == "Linux":
        _connect_linux(baud)
    elif system == "Windows":
        _print_windows_instructions()
    else:
        click.echo(f"⚠️ Unsupported OS: {system}. Only macOS, Linux, and Windows are supported.")
        ctx.exit(1)

    click.echo("✅ Serial session ended.")


def _connect_mac(baud):
    terminal = "picocom"
    if not shutil.which(terminal):
        click.echo("⚙️ 'picocom' is not installed. Attempting to install with Homebrew...")
        if shutil.which("brew"):
            subprocess.run(["brew", "install", "picocom"], check=True)
        else:
            click.echo("❌ Homebrew not found. Please install Homebrew first: https://brew.sh/")
            raise SystemExit(1)

    ports = sorted(
        subprocess.getoutput("ls /dev/tty.usbserial-* /dev/cu.usbserial-* 2>/dev/null").splitlines()
    )
    if not ports:
        click.echo("❌ No USB serial device found.")
        raise SystemExit(1)

    click.echo(f"Connecting to device with picocom ({baud} baud)...")
    click.echo("🧷 To exit: Press Ctrl + A, then Ctrl + X")
    click.echo("📜 Scrollback will work in your terminal as expected.\n")
    
    if not click.confirm("Proceed to connect?", default=True):
        click.echo("❎ Connection aborted by user.")
        return

    port = ports[0]
    click.echo(f"🔌 Connecting to {port} with picocom (115200 8N1)...")
    try:
        subprocess.run([
            terminal,
            "-b", f"{baud}",
            "--databits", "8",
            "--parity", "n",
            "--stopbits", "1",
            port
        ])
    except KeyboardInterrupt:
        click.echo("\n❎ Serial connection interrupted by user.")


def _connect_linux(baud):
    terminal = "picocom"
    if not shutil.which(terminal):
        click.echo("⚙️ 'picocom' is not installed. Attempting to install via apt...")
        if shutil.which("apt-get"):
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "picocom"], check=True)
        else:
            click.echo("❌ 'apt-get' not found. Please install picocom manually.")
            raise SystemExit(1)

    ports = sorted(
        subprocess.getoutput("ls /dev/ttyUSB* 2>/dev/null").splitlines()
    )
    if not ports:
        click.echo("❌ No USB serial device found.")
        raise SystemExit(1)

    port = ports[0]
    click.echo(f"🔌 Connecting to {port} with picocom ({baud} 8N1)...")
    try:
        subprocess.run(
            ["sudo", terminal, "-b", f"{baud}", "--databits", "8", "--parity", "n", "--stopbits", "1", port]
        )
    except KeyboardInterrupt:
        click.echo("\n❎ Serial connection interrupted by user.")


def _print_windows_instructions():
    click.echo("📘 To connect to the DevKit via a serial terminal on Windows, follow these steps:\n")

    click.echo("1. Identify the COM Port:")
    click.echo("   • Open **Device Manager** → Expand **Ports (COM & LPT)**.")
    click.echo("   • Look for an entry like **USB Serial Port (COMx)**.\n")

    click.echo("2. Install and Open a Serial Terminal:")
    click.echo("   • Use **PuTTY** (Download from https://www.putty.org/) or **Tera Term**.")
    click.echo("   • Set the **Connection Type** to **Serial**.")
    click.echo("   • Enter the correct **COM Port** (e.g., COM3).")
    click.echo("   • Set **Baud Rate** to **115200**.")
    click.echo("   • Click **Open** to start the connection.\n")

    click.echo("🔌 You are now ready to connect to the DevKit over serial.")
