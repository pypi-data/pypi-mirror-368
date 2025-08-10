#!/bin/bash
set -euo pipefail
# === Configuration ===
conf="${SSH_CONFIG:-$HOME/.ssh/config}"
authorized_keys="${SSH_AUTHORIZED_KEYS:-$HOME/.ssh/authorized_keys}"

ACTION="${1:-run}"
host="${2:-localhost}"

if [[ "$ACTION" == "clean" ]]; then
  ssh "$host" "bash /tmp/rbash_clean.sh || true"
  ssh "$host" "rm -f ~/.ssh/id_rbash ~/.ssh/id_rbash.pub /tmp/rbash.sh /tmp/rbash_clean.sh"
  echo "✅ Done. Session closed and cleaned up."
  exit 0
fi

if [[ "$ACTION" != "run" ]]; then
  echo "❌ Unknown action: $ACTION"
  exit 1
fi

default_port=2222
#echo "=== Using SSH config: $conf ==="
# Local path and user
localpath=$(realpath .)
local_user=$(whoami)
# Remote home and workspace
remote_home=$(ssh "$host" 'echo $HOME')
pid=$$
remote_workspace="$remote_home/workspace${pid}"
echo "📂 Local path: $localpath"
echo "📂 Will mount to: $host:$remote_workspace"
# 🔎 Find available port for reverse SSH tunnel
function find_available_port() {
  for port in $(seq $default_port 2299); do
    if ! lsof -i ":$port" &>/dev/null; then
      echo "$port"
      return
    fi
  done
  echo "❌ No available ports in range 2222-2299." >&2
  exit 1
}
mapport=$(find_available_port)
#echo "🔁 Selected reverse tunnel port: $mapport"
# 🔐 Create temp SSH key on remote
#echo "🔑 Generating temporary keypair on remote host..."
ssh "$host" 'mkdir -p ~/.ssh && rm -f ~/.ssh/id_rbash ~/.ssh/id_rbash.pub && ssh-keygen -t rsa -N "" -f ~/.ssh/id_rbash -q'
# ⬇️ Fetch remote public key
pubkey=$(ssh "$host" "cat ~/.ssh/id_rbash.pub")
pubkey_tag="# rbash-temp-key"
# ✅ Authorize remote key locally
#echo "🔐 Adding remote public key to local authorized_keys..."
#echo "$pubkey $pubkey_tag" >> "$authorized_keys"
# 📝 Remote run script
cat > /tmp/rbash.${pid}.sh <<EOF
#!/bin/bash
set -euo pipefail
mkdir -p $remote_workspace

echo "🔄 Check system requirements ..."
# Check if sshfs is installed
if ! command -v sshfs >/dev/null; then
  echo "❌ sshfs not found. Please install sshfs (e.g. 'sudo apt install sshfs') before continuing."
  exit 0
fi

if ! modprobe fuse 2>/dev/null; then
  command -v sudo >/dev/null && sudo modprobe fuse || modprobe fuse
fi

#echo "🔄 Mounting remote workspace..."
# Gracefully unmount if already mounted
if mount | grep -q "$remote_workspace"; then
  echo "⚠️  Already mounted. Attempting to unmount..."
  fusermount -uz "$remote_workspace" || true
  for i in {1..10}; do
    if ! mount | grep -q "$remote_workspace"; then break; fi
    echo "⏳ Waiting for unmount... (\$i)"
    sleep 1
  done
fi
# Mount local path via sshfs over reverse tunnel
sshfs -o StrictHostKeyChecking=no -o IdentityFile=~/.ssh/id_rbash \
  -p ${mapport} ${local_user}@localhost:${localpath} ${remote_workspace}
#df -h "$remote_workspace"
sleep 3
cd "$remote_workspace" && bash --rcfile <(echo "export PS1='[rbash] \w \$ '")
EOF

# 🧼 Remote cleanup script
cat > /tmp/rbash_clean.${pid}.sh <<EOF
#!/bin/bash
set -euo pipefail
echo "🧹 Cleaning up remote workspace..."
cd
sleep 3
if mount | grep -q "$remote_workspace"; then
  #echo "🔌 Still mounted. Trying to unmount in background..."
  nohup bash -c '
    cd && pwd && fusermount -uz "$remote_workspace" || true
    for i in {1..10}; do
      if ! mount | grep -q "$remote_workspace"; then break; fi
      sleep 1
    done
    rmdir "$remote_workspace" 2>/dev/null || true
  ' >/dev/null 2>&1 &
else
  rmdir "$remote_workspace" 2>/dev/null || true
fi
EOF
# 🛰️ Transfer scripts
scp /tmp/rbash.${pid}.sh "$host:/tmp/rbash.sh" >/dev/null 
scp /tmp/rbash_clean.${pid}.sh "$host:/tmp/rbash_clean.sh" >/dev/null
rm -f /tmp/rbash.${pid}.sh /tmp/rbash_clean.${pid}.sh
# 🚀 Start remote shell with reverse tunnel
echo "🚀 Starting remote session with $(basename $remote_workspace) ..."
ssh -t -R ${mapport}:localhost:22 "$host" "bash /tmp/rbash.sh"
# 🧹 Cleanup after session exit
#echo "🧽 Cleaning up keys and temp files..."
sed -i.bak "/$pubkey_tag/d" "$authorized_keys"

#ssh "$host" "bash /tmp/rbash_clean.sh"
#ssh "$host" "rm -f ~/.ssh/id_rbash ~/.ssh/id_rbash.pub /tmp/rbash.sh /tmp/rbash_clean.sh"
#echo "✅ Done. Session closed and cleaned up."
