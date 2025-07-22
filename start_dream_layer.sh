#!/bin/bash

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname)" in
  Darwin)
    echo "[INFO] Detected macOS"
    exec "${SCRIPT_DIR}/start_dream_layer_mac.sh" "$@"
    ;;
  Linux)
    echo "[INFO] Detected Linux"
    exec "${SCRIPT_DIR}/start_dream_layer_linux.sh" "$@"
    ;;
  *)
    echo "[ERROR] Unsupported OS: $(uname)"
    exit 1
    ;;
esac
