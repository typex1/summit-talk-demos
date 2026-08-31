#!/usr/bin/env bash
# Resume: record demos 4-6 + convert ALL casts to GIFs.
set -u
cd "$(dirname "$0")"
VENV=.venv/bin
RECDIR=recordings
export AWS_REGION=us-west-2 AWS_DEFAULT_REGION=us-west-2
export COLUMNS=100 LINES=32
export OTEL_SDK_DISABLED=true CREWAI_DISABLE_TELEMETRY=true CREWAI_TRACING_ENABLED=false

record () {
  local name=$1 dir=$2
  echo "=== Recording $name ==="
  "$VENV/asciinema" rec --overwrite --quiet --idle-time-limit 2 \
      -c "$VENV/python -u $dir/demo.py" "$RECDIR/$name.cast" \
      && echo "=== $name cast OK ===" || echo "=== $name cast FAILED ==="
}

"$VENV/python" 06_a2a/weather_agent_server.py > "$RECDIR/a2a_server.log" 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT

record 04_crewai 04_crewai
record 05_mcp    05_mcp

for i in $(seq 1 30); do
  curl -sf http://127.0.0.1:9000/.well-known/agent-card.json >/dev/null && break
  sleep 1
done
record 06_a2a 06_a2a

echo "=== Converting casts to GIFs ==="
for c in "$RECDIR"/*.cast; do
  ~/.local/bin/agg --cols 100 --rows 32 --font-size 16 --theme monokai \
      --idle-time-limit 2 "$c" "${c%.cast}.gif" \
      && echo "GIF OK: ${c%.cast}.gif" || echo "GIF FAILED: $c"
done
ls -lh "$RECDIR"
