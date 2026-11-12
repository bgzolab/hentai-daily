#!/usr/bin/env bash
# Local copy of .github/workflows/sync.yml, meant to be called by cron.
# It works in its own shallow clone, so the pipeline never touches your edits.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BRANCH=vitepress
WORK="${XDG_DATA_HOME:-$HOME/.local/share}/hentai-daily-sync"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/hentai-daily-sync"
MIN_AGE="${MIN_AGE:-7200}" # seconds, same 2h guard as the workflow

mkdir -p "$STATE"
if [ -f "$STATE/sync.log" ] && [ "$(stat -c %s "$STATE/sync.log")" -gt 5000000 ]; then
  mv -f "$STATE/sync.log" "$STATE/sync.log.1"
fi
exec >>"$STATE/sync.log" 2>&1
echo "=== $(date '+%F %T') sync start"

if [ ! -d "$WORK/.git" ]; then
  git clone --depth 1 --branch "$BRANCH" "$(git -C "$REPO" remote get-url origin)" "$WORK"
fi
cd "$WORK"
git fetch --depth 1 origin "$BRANCH"
git reset --hard FETCH_HEAD

now=$(date +%s)
last_commit=$(git log -1 --format=%ct)
last_run=$(cat "$STATE/last-run" 2>/dev/null || echo 0)
if [ $((now - last_commit)) -lt "$MIN_AGE" ] || [ $((now - last_run)) -lt "$MIN_AGE" ]; then
  # last-run covers runs that produced no commit (nothing new), otherwise every
  # cron tick would scrape again until something changes.
  echo "commit $((now - last_commit))s ago, last run $((now - last_run))s ago, skip"
  exit 0
fi

PY="$REPO/.venv/bin/python3"
[ -x "$PY" ] || PY=python3
"$PY" src/sync.py
"$PY" src/heatmap-count.py

find api/archives -maxdepth 4 -name '*.json' -type f -print0 |
  while IFS= read -r -d '' file; do
    if jq --indent 2 '.' "$file" > "$file.tmp" 2>/dev/null; then
      mv -f "$file.tmp" "$file"
    else
      rm -f "$file.tmp"
    fi
  done

if [ -z "$(git status --porcelain)" ]; then
  echo "no changes"
else
  git add .
  git commit -m "chore(ci): sync feed by local cron"
  git pull --rebase origin "$BRANCH"
  git push origin "HEAD:$BRANCH"
fi

date +%s > "$STATE/last-run"
echo "=== done in ${SECONDS}s"
