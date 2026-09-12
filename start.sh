#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start backend
python3 -m backend.app &
BACK_PID=$!

cleanup() {
  kill $BACK_PID >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Start frontend (install deps if missing)
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  (cd "$ROOT_DIR/frontend" && npm install)
fi

cd "$ROOT_DIR/frontend"
npm run dev -- --host
