#!/usr/bin/env bash
set -euo pipefail

ALL_DISTROS=( "ubuntu:24.04" "debian:stable" "fedora:latest" "archlinux" )
LOGDIR="test-logs"
PROJECT_DIR="$(pwd)"
INSTALL_SCRIPT="install_linux_dependencies.sh"
START_SCRIPT="start_dream_layer_linux.sh"

# Function to show usage
usage() {
    echo "Usage: $0 [distro]"
    echo "Available distros: ubuntu:24.04, debian:stable, fedora:latest, archlinux"
    echo "If no distro is provided, all distros will be tested."
}

# Function to parse and validate arguments
parse_args() {
    if [[ $# -gt 1 ]]; then
        echo "Error: Too many arguments"
        usage
        exit 1
    elif [[ $# -eq 1 ]]; then
        if [[ "$1" == "-h" || "$1" == "--help" ]]; then
            usage
            exit 0
        fi
        
        # Check if the provided distro is valid
        local distro_found=false
        for distro in "${ALL_DISTROS[@]}"; do
            if [[ "$distro" == "$1" ]]; then
                distro_found=true
                break
            fi
        done
        
        if [[ "$distro_found" == "false" ]]; then
            echo "Error: Invalid distro '$1'"
            echo "Available distros: ${ALL_DISTROS[*]}"
            exit 1
        fi
        
        DISTROS=( "$1" )
        echo "Testing single distro: $1"
    else
        DISTROS=( "${ALL_DISTROS[@]}" )
        echo "Testing all distros"
    fi
}

# Parse arguments
parse_args "$@"

rm -rf $LOGDIR
mkdir -p "$LOGDIR"

echo -e "\n=== Starting integration tests ===\n"

for img in "${DISTROS[@]}"; do
  name="${img//[:\/]/_}"
  log="$LOGDIR/$name.log"
  echo "📦 Testing on $img"
  docker pull "$img" >/dev/null
  
  CMD=$(cat <<'EOF'
set -e
if command -v apt-get &>/dev/null; then
  apt-get update && apt-get install -y sudo
elif command -v dnf &>/dev/null; then
  dnf install -y sudo
elif command -v pacman &>/dev/null; then
  pacman -Sy --noconfirm sudo
fi
cd /project
chmod +x install_linux_dependencies.sh start_dream_layer.sh
CI=true bash install_linux_dependencies.sh --yes && CI=true bash start_dream_layer.sh
EOF
)

 if docker run --rm \
    -v "$PROJECT_DIR":/project \
    -w /project \
    -e CI=true \
    "$img" bash -c "$CMD" > "$log" 2>&1; then
    if grep -q "\[CI-SUCCESS\]" "$log"; then
      echo "✅ $img succeeded"
      rm -f "$log"
    else
      echo "❌ $img FAILED — see $log for details"
    fi
  else
    echo "❌ $img FAILED — see $log for details"
  fi
  echo
done

echo "=== Tests complete ==="