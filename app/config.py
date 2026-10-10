"""Runtime configuration derived from environment variables."""
import os
import socket


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("TITAN_DATA_DIR", os.path.join(BASE_DIR, "data"))

def _usable_data_dir(path: str) -> str:
    """A data dir we can actually write to - or a loud downgrade instead of a crash.

    The very first thing boot does is open the SQLite file, so an unwritable
    `TITAN_DATA_DIR` (a Volume mounted at the wrong path, or read-only) used to
    raise before anything could answer the healthcheck: the platform then shows a
    generic "Application failed to respond" and the real reason is only in the
    logs. Boot anyway, say why, and make the persistence loss visible.
    """
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".titan-write-test")
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(probe)
        return path
    except OSError as exc:
        import logging
        import tempfile
        fallback = tempfile.mkdtemp(prefix="titan-data-")
        logging.getLogger("titan.config").error(
            "data dir %s is unusable (%s); falling back to %s. The panel will boot and "
            "stay reachable, but users and settings will NOT survive a restart: mount "
            "the Volume at /app/data or point TITAN_DATA_DIR at a writable path.",
            path, exc, fallback)
        return fallback


DATA_DIR = _usable_data_dir(DATA_DIR)
DB_PATH = os.environ.get("TITAN_DB_PATH", os.path.join(DATA_DIR, "titan.db"))
XRAY_CONFIG_PATH = os.environ.get(
    "TITAN_XRAY_CONFIG", "/usr/local/bin/config.json"
)

PUBLIC_PORT = int(os.environ.get("PORT", "8080"))


PANEL_PORT = int(os.environ.get("PANEL_PORT", "8080"))


def _ipv6_available() -> bool:
    """True when this kernel can bind an IPv6 socket at all."""
    try:
        probe = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    except OSError:
        return False
    try:
        probe.bind(("::", 0))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def _panel_hosts() -> list:
    """Every address family the panel must answer on.

    Serving one family is invisible from inside the container: a healthcheck on
    127.0.0.1 passes, the logs stay clean, and the admin sees only "Application
    failed to respond" from the platform edge, which may be dialling the other
    family. So the panel binds both whenever the kernel offers both.

    They are two sockets, not one v4-mapped socket: asyncio sets IPV6_V6ONLY on
    the socket it binds, so `uvicorn --host ::` is IPv6-*only* - the trap that
    turns "add IPv6 support" into "IPv4 stops working". See app.main.
    """
    explicit = (os.environ.get("PANEL_HOST") or "").strip()
    if explicit:
        return [explicit]
    return ["0.0.0.0", "::"] if _ipv6_available() else ["0.0.0.0"]


PANEL_BIND_HOSTS = _panel_hosts()

PANEL_HOST = PANEL_BIND_HOSTS[0]
XRAY_VLESS_WS_PORT = int(os.environ.get("XRAY_VLESS_WS_PORT", "10001"))
XRAY_VMESS_WS_PORT = int(os.environ.get("XRAY_VMESS_WS_PORT", "10002"))
XRAY_TROJAN_WS_PORT = int(os.environ.get("XRAY_TROJAN_WS_PORT", "10003"))
XRAY_XHTTP_PORT = int(os.environ.get("XRAY_XHTTP_PORT", "10004"))
XRAY_GRPC_PORT = int(os.environ.get("XRAY_GRPC_PORT", "10005"))
XRAY_API_PORT = int(os.environ.get("XRAY_API_PORT", "10085"))


SUPPORT_URL = os.environ.get("TITAN_SUPPORT_URL", "https://t.me/Code_Shield").strip()
GITHUB_URL = os.environ.get("TITAN_GITHUB_URL", "https://github.com/mr-rashidi").strip()



XRAY_HTTPUPGRADE_PORT = int(os.environ.get("XRAY_HTTPUPGRADE_PORT", "10013"))



XRAY_BIN = os.environ.get("XRAY_BIN", "/usr/local/bin/xray")

XRAY_LOG_PATH = os.environ.get("TITAN_XRAY_LOG", os.path.join(DATA_DIR, "xray.log"))


SESSION_COOKIE = "titan_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

LOGIN_SOFT_FAILS = 3
LOGIN_BACKOFF_CAP_SECONDS = 15

LOGIN_MAX_ATTEMPTS = 8
LOGIN_HARD_LOCK_ATTEMPTS = 30
LOGIN_LOCK_SECONDS = 10 * 60  # 10 minutes


ROLE = os.environ.get("TITAN_ROLE", "main").strip().lower() or "main"
IS_NODE = ROLE == "node"


NODE_SECRET = os.environ.get("TITAN_NODE_SECRET", "")


NODE_TOKEN = os.environ.get("TITAN_NODE_TOKEN", "")


NODE_NAME = os.environ.get("TITAN_NODE_NAME", "").strip()


def _node_public_url() -> str:
    d = os.environ.get("TITAN_NODE_URL", "").strip()
    if d:
        return d
    d = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if not d:
        return ""
    if d.startswith(("http://", "https://")):
        return d
    return "https://" + d


NODE_URL = _node_public_url()


MAIN_URL = os.environ.get("TITAN_MAIN_URL", "").strip().rstrip("/")


NODE_SYNC_INTERVAL = int(os.environ.get("TITAN_NODE_SYNC_INTERVAL", "60"))



DEFAULT_SETTINGS = {
    "public_domain": "",
    "public_port": 443,
    "admin_avatar": "titan",
    "default_transport": "ws",
    "default_fingerprint": "chrome",
    "default_alpn": "http/1.1",
    "sni_override": "",
    "fragment_enabled": False,
    "fragment_length": "10-30",
    "fragment_interval": "10-20",
    "restrict_ips": True,
    "block_ads": True,
    "block_iran_sites": False,
    "backup_enabled": True,
    "backup_interval_hours": 24,
}


VALID_FINGERPRINTS = {"chrome", "firefox", "safari", "ios", "android", "edge", "360", "qq", "random", "randomized"}
VALID_ALPNS = {"http/1.1", "h2,http/1.1", "h3,h2,http/1.1", ""}
VALID_TRANSPORTS = {"ws", "xhttp", "grpc", "httpupgrade"}
VALID_SECURITY = {"tls"}
VALID_PROTOCOLS = {"vless", "vmess", "trojan"}
