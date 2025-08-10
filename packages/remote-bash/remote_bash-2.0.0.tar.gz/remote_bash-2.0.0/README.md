# Remote Bash Shell (`remote-bash`)

[![PyPI version](https://badge.fury.io/py/remote-bash.svg)](https://badge.fury.io/py/remote-bash)  
[![Python Version](https://img.shields.io/pypi/pyversions/remote-bash.svg)](https://pypi.org/project/remote-bash/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Make Your Remote Server Feel Local — Instantly

Tired of juggling `rsync`, `scp`, or NFS just to work with a remote server?  
Need the power of a remote GPU server, but still want the comfort of editing locally?  

**`remote-bash`** lets you **mount your local directory directly into a remote server**, run commands there, and clean up when you’re done — all with **one command**.

No messy setup, no permanent SSH key sharing, no manual reverse tunnels.

---

## ✨ How It Works (Version 2.0.0)

When you run:

```bash
rbash myserver
```

Here’s what happens under the hood:

1. **Validate Host** – confirms that `myserver` exists in your `~/.ssh/config` (but can proceed even if missing).
2. **Prepare Remote Workspace** – creates a unique workspace folder (e.g., `/home/user/workspace12345678`) on the remote machine.
3. **Temporary SSH Key Exchange**  
   - Generates a **remote-only** keypair.  
   - Adds the remote public key to your **local** `authorized_keys` (with a special tag for later removal).
4. **Reverse SSH Tunnel** – opens a reverse tunnel from the remote back to your local machine.
5. **SSHFS Mount** – mounts your **local** working directory into the remote workspace using the reverse tunnel.
6. **Interactive Remote Bash** – drops you into a bash shell on the remote with your local files mounted and ready.
7. **Automatic Cleanup** (on exit) – unmounts the workspace, deletes temporary keys (both sides), and removes the workspace folder.

---

## 🔹 Why Use This Instead of NFS / Manual SSHFS?

- **No permanent key sharing** — security-friendly  
- **No root or NFS setup** — works in user space  
- **Automatic reverse tunnel** — works even if remote server can’t directly reach your machine  
- **One command** — handles mount, shell, and cleanup for you  
- **Python-powered** — portable and easily installed via `pip`

---

## 📦 Installation

```bash
pip install remote-bash
```

Requires:
- Python **3.8+**
- `ssh` client installed locally
- `sshfs` installed locally and remotely
- FUSE enabled on both machines

---

## 🔹 Example Usage

List available hosts from your SSH config:
```bash
rbash
```

Connect to a host:
```bash
rbash myserver
```

Mount a specific local path:
```bash
rbash myserver --path ~/projects/myapp
```

Change the base reverse tunnel port:
```bash
rbash myserver --port 2225
```

Strict host key checking (disable host-key suppression):
```bash
rbash myserver --strict
```

---

## 🛠 Requirements

### Local
- Python 3.8+
- `ssh`
- `sshfs`

### Remote
- `ssh`
- `sshfs`
- FUSE enabled

---

## ⚙ SSH Configuration Example

`~/.ssh/config`:

```sshconfig
Host myserver
    HostName 192.168.1.100
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
```

---

## 🔍 Security

- All SSH keys used are **temporary** and automatically removed.
- Your `authorized_keys` entry is tagged, so it’s deleted after the session.
- No changes are made to system-level SSH configuration.
- Reverse tunnel exists **only** for the duration of your session.

---

## 🧼 Cleanup Behavior

When you exit the remote bash session:
- Workspace is unmounted
- Temporary SSH keys are deleted
- Reverse tunnel is closed
- Authorized key entry is removed

If you pass `--no-clean`, keys and mounts remain for debugging.

---

## 🐛 Troubleshooting

**Permission Denied**  
Ensure your SSH connection to the host works manually:
```bash
ssh myserver
```

**`sshfs` not found**  
Install on both local and remote:
```bash
sudo apt install sshfs  # Ubuntu/Debian
brew install sshfs      # macOS
```

**`remote port forwarding failed`**  
The requested port is in use on remote; `rbash` will automatically select an available one starting from `--port`.

**`fuse: unknown option(s): -o nonempty`**  
Remove `-o nonempty`. Newer FUSE versions don’t support it. `remote-bash` doesn’t use it.

---

## 📄 License
MIT License — see `LICENSE`.

---

## 📜 Changelog

### [2.0.0] - 2025-08-10
#### Changed
- Completely rewrote core logic in Python (`remote.py` class + `cli.py` entrypoint) replacing older shell script.
- Manages session lifecycle programmatically (prepare, run, clean).
- **Temporary SSH key** injection/removal to local `authorized_keys`.
- **Local port availability check** before starting reverse tunnel.
- Clear subprocess logging and error handling.

### [1.2.0] - 2025-08-01
#### Fixed
- Remote system check for `sshfs` and FUSE before attempting mount.

### [1.1.0] - 2025-07-31
#### Fixed
- Corrected path resolution for `bash.sh`.

### [1.0.1] - 2025-07-31
#### Added
- README updated with `pip install remote-bash`.

### [1.0.0] - 2025-07-31
#### Added
- Initial release of `remote_bash`.
- CLI commands: `rbash` and `remote_bash`.
- Reverse SSHFS mounting with local → remote path mapping.
- Remote temporary SSH key exchange.
- Automatic cleanup of keys, mounts, and workspace.
- Host listing from `~/.ssh/config` in table format.
