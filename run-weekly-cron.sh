#!/bin/bash
# Cron wrapper for weekly-update.sh
# Cron runs in a minimal environment — this sets up PATH correctly.

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export HOME="/Users/rinku.soni"

# Add Homebrew and common Python locations
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

SCRIPT_DIR="/Users/rinku.soni/mce-prom-dashboard"
LOG_FILE="$SCRIPT_DIR/weekly-update.log"

echo "======================================" >> "$LOG_FILE"
echo "Cron run: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

cd "$SCRIPT_DIR" && ./weekly-update.sh >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    # Send a macOS notification if it failed
    osascript -e "display notification \"Weekly update FAILED (exit $EXIT_CODE). Check $LOG_FILE\" with title \"MCE ProM Dashboard\"" 2>/dev/null || true
else
    osascript -e "display notification \"Weekly update complete ✅ Dashboard updated.\" with title \"MCE ProM Dashboard\"" 2>/dev/null || true
fi

echo "Exit code: $EXIT_CODE" >> "$LOG_FILE"
