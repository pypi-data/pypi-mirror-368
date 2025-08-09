#!/bin/bash

UV_PATH=$(which uv 2>/dev/null)
if [ -z "$UV_PATH" ]; then
    echo "uv command not found. Please run: brew install uv" >&2
    exit 8
fi

uv sync

jq -n --arg command "$UV_PATH" --arg cwd "$(pwd)" --arg mainpy "$(pwd)/main.py" '{
  "mcpServers": {
    "ibm-cloud-browser": {
      "command": $command,
      "args": ["run", "python", $mainpy],
      "cwd": $cwd
    }
  }
}'