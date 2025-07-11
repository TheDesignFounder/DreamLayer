#!/bin/bash
# DreamLayer Node.js Environment Setup
# This script ensures the correct Node.js version is used

export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo "Node.js location: $(which node)"
echo ""
echo "Environment ready for DreamLayer frontend development!"
echo "Use: source setup_node_env.sh && npm run dev"