# CAPEv2 Host Install Notes (Day 24-25)

Host: spare laptop, Ubuntu Server 26.04, accessed over SSH.
Python on host: 3.14 (system default). CAPEv2 runs on Python 3.12 (see Day 25).

## Day 24 - Host dependencies + database

What I did:
1. Cloned CAPEv2 and ran the installer: `sudo ./cape2.sh base | tee -a docs/capev2_install_log.md`
2. Installed PostgreSQL (version 18 came with this Ubuntu).

Problems and fixes:
- Terminal looked stuck and Ctrl+C did nothing. The script had actually finished with errors and I was at an empty prompt. Closing the session and opening a new SSH session fixed it.
- `yara-python` failed to build. Cause: missing build tools. Fix:
  `sudo apt install -y build-essential automake libtool libtool-bin pkg-config python3-dev libssl-dev libjansson-dev libmagic-dev flex bison`
  then re-ran the installer.
- Harmless messages I chose to ignore for now:
  - `dc4dot ... libdnlib2.1-cil not installable` (optional .NET tool, not needed yet)
  - `cp: cannot stat './conf/default/*.env'` (template files not in this version)
  - `/etc/sudoers.d/ip_netns: wildcards are not allowed` (broken rule for network isolation, matters in the networking days; shows on every sudo command)

Verification:
- `pg_lsclusters` showed cluster 18/main online on port 5432.
- `sudo -u postgres psql -c "SELECT version();"` returned PostgreSQL 18.6.
- Note: `systemctl status postgresql` shows "active (exited)". That is normal, it is only a wrapper. The real check is `pg_lsclusters`.

Checkpoint: What is CAPEv2's database actually storing?
(Write your own answer here in your own words.)

## Day 25 - Web and API services

Symptom: `cape` and `cape-web` were stuck in "activating auto-restart" (crash loop, 420+ restarts). Port 8000 was closed.

Root cause chain (one root problem, not many):
1. **DNS was broken.** The server could ping 8.8.8.8 but could not resolve names like pypi.org, so `poetry install` could not download packages. The only DNS server known to the machine was Tailscale's (100.100.100.100), which only answers Tailscale names. The normal network link had no DNS server.
2. Because the install never finished, `sqlalchemy` was missing, so cape and cape-web crashed with `No module named 'sqlalchemy'`.
3. After DNS was fixed, install failed on **gevent 24.2.1**: it cannot be compiled on Python 3.14 (Cython error `undeclared name not builtin: long`). CAPEv2 pins that old gevent version.

Fixes:
- Temporary DNS: `sudo resolvectl dns <interface> 8.8.8.8 1.1.1.1` and `sudo resolvectl default-route <interface> yes`
- Permanent DNS: created `/etc/systemd/resolved.conf.d/dns.conf` containing:
  ```
  [Resolve]
  DNS=8.8.8.8 1.1.1.1
  Domains=~.
  ```
  then `sudo systemctl restart systemd-resolved`
- Python 3.12 without touching system Python (Ubuntu only offers 3.14 via apt):
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  sudo mkdir -p /opt/python
  sudo env UV_PYTHON_INSTALL_DIR=/opt/python $HOME/.local/bin/uv python install 3.12
  cd /opt/CAPEv2
  sudo -u cape /etc/poetry/bin/poetry env use /opt/python/cpython-3.12.16-linux-x86_64-gnu/bin/python3.12
  sudo -u cape env POETRY_HTTP_TIMEOUT=600 /etc/poetry/bin/poetry install --no-root
  ```
- Restarted: `sudo systemctl start cape cape-web`

Verification:
- `cape` and `cape-web` both "active (running)", with no restart loop.
- `ss -tlnp | grep 8000` shows the web server listening.
- `curl -I http://localhost:8000` returned `HTTP/1.1 200 OK`.
- `curl http://localhost:8000/apiv2/` returned the "API - CAPE Sandbox" page.

Warnings that are harmless for now:
- Missing optional dependency: httpreplay
- Django deprecation warning about ACCOUNT_EMAIL_REQUIRED

Security notes:
- Web server listens on `0.0.0.0:8000` with the Werkzeug debugger active. Fine on a private network only. Tailscale is now installed so a teammate can reach the server. Do not expose this to the public internet. Lock down later.

Lesson learned: CAPEv2 expects older Python (3.10-3.12). A newer Ubuntu with Python 3.14 breaks pinned packages. Check Python version first on future installs.

Checkpoint: What is the API service's role vs the web UI's role?
(Write your own answer here in your own words.)

## Open items
- Confirm API status code: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/apiv2/cuckoo/status/`
- Reboot test: confirm DNS, cape and cape-web come back on their own.
- Day 26: guest agent in the Windows VM + smoke test.