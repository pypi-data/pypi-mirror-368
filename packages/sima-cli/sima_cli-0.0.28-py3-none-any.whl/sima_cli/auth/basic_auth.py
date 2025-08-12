import os
import click
import getpass
import requests
import json
from http.cookiejar import MozillaCookieJar

HOME_DIR = os.path.expanduser("~/.sima-cli")
COOKIE_JAR_PATH = os.path.join(HOME_DIR, ".sima-cli-cookies.txt")
CSRF_PATH = os.path.join(HOME_DIR, ".sima-cli-csrf.json")

CSRF_URL = "https://developer.sima.ai/session/csrf"
LOGIN_URL = "https://developer.sima.ai/session"
DUMMY_CHECK_URL = "https://docs.sima.ai/pkg_downloads/dummy"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://developer.sima.ai/login",
    "Origin": "https://developer.sima.ai",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def _is_session_valid(session: requests.Session) -> bool:
    try:
        response = session.get(DUMMY_CHECK_URL, allow_redirects=False)
        return response.status_code == 200
    except Exception:
        return False

def _delete_auth_files():
    for path in [COOKIE_JAR_PATH, CSRF_PATH]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                click.echo(f"⚠️ Could not delete {path}: {e}")


def _save_cookie_jar(session: requests.Session):
    cj = MozillaCookieJar(COOKIE_JAR_PATH)
    for c in session.cookies:
        cj.set_cookie(c)
    cj.save(ignore_discard=True)


def _load_cookie_jar(session: requests.Session):
    if os.path.exists(COOKIE_JAR_PATH):
        cj = MozillaCookieJar()
        cj.load(COOKIE_JAR_PATH, ignore_discard=True)
        session.cookies.update(cj)


def _load_csrf_token() -> str:
    if os.path.exists(CSRF_PATH):
        with open(CSRF_PATH, "r") as f:
            data = json.load(f)
            return data.get("csrf", "")
    return ""


def _fetch_and_store_csrf_token(session: requests.Session) -> str:
    try:
        resp = session.get(CSRF_URL)
        resp.raise_for_status()
        csrf_token = resp.json().get("csrf")
        if csrf_token:
            with open(CSRF_PATH, "w") as f:
                json.dump({"csrf": csrf_token}, f)
        return csrf_token
    except Exception as e:
        click.echo(f"❌ Failed to fetch CSRF token: {e}")
        return ""


def login_external():
    """Interactive login workflow with CSRF token, cookie caching, and dummy session validation."""
    for attempt in range(1, 4):
        session = requests.Session()
        session.headers.update(HEADERS)

        _load_cookie_jar(session)
        csrf_token = _load_csrf_token()

        if not csrf_token:
            csrf_token = _fetch_and_store_csrf_token(session)

        if not csrf_token:
            click.echo("❌ CSRF token is missing or invalid.")
            continue

        session.headers["X-CSRF-Token"] = csrf_token

        if _is_session_valid(session):
            click.echo("🚀 You are already logged in.")
            return session

        # Prompt user login
        _delete_auth_files()
        click.echo(f"🔐 Sima.ai Developer Portal Login Attempt {attempt}/3")
        username = click.prompt("Email or Username")
        password = getpass.getpass("Password: ")

        login_data = {
            "login": username,
            "password": password,
            "second_factor_method": "1"
        }

        try:
            resp = session.post(LOGIN_URL, data=login_data)
            name = resp.json().get('users')[0]['name'] if 'users' in resp.json() else ''
            if resp.status_code != 200:
                click.echo(f"⚠️ Login request returned status {resp.status_code}")
                continue
        except Exception as e:
            click.echo(f"❌ Login request failed: {e}")
            continue

        if _is_session_valid(session):
            _save_cookie_jar(session)
            click.echo(f"✅ Login successful. Welcome to Sima Developer Portal, {name}!")
            return session
        else:
            click.echo("❌ Login failed.")

    click.echo("❌ Login failed after 3 attempts.")
    raise SystemExit(1)
