#!/bin/bash

set -e

case "$(uname)" in
  Darwin)
    echo "[INFO] Detected macOS"
    exec ./start_dream_layer_mac.sh "$@"
    ;;
  Linux)
    echo "[INFO] Detected Linux"
    exec ./start_dream_layer_linux.sh "$@"
    ;;
  *)
    echo "[ERROR] Unsupported OS: $(uname)"
    exit 1
    ;;
esac
