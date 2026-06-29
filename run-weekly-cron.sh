#!/bin/bash
# Cron wrapper for weekly-update.sh
# Cron runs in a minimal environment — this sets up PATH correctly.
#
# Two cron entries are installed:
#   2pm Friday  — primary run
#   3pm Friday  — retry, only if 2pm run failed
#
# A status file (weekly-update.status) records whether today's run succeeded.
# The retry job checks that file before running.

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export HOME="/Users/rinku.soni"
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

SCRIPT_DIR="/Users/rinku.soni/mce-prom-dashboard"
LOG_FILE="$SCRIPT_DIR/weekly-update.log"
STATUS_FILE="$SCRIPT_DIR/weekly-update.status"
TODAY=$(date +%Y-%m-%d)
IS_RETRY="${1:-}"   # pass "retry" as $1 when called from the 3pm cron entry

# ── Retry logic ──────────────────────────────────────────────────────────────
if [ "$IS_RETRY" = "retry" ]; then
    # Check if today already succeeded
    if [ -f "$STATUS_FILE" ] && grep -q "^SUCCESS $TODAY" "$STATUS_FILE" 2>/dev/null; then
        echo "$(date): Retry skipped — primary run already succeeded today." >> "$LOG_FILE"
        exit 0
    fi
    echo "" >> "$LOG_FILE"
    echo "======================================" >> "$LOG_FILE"
    echo "RETRY run: $(date)" >> "$LOG_FILE"
    echo "======================================" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "======================================" >> "$LOG_FILE"
    echo "PRIMARY run: $(date)" >> "$LOG_FILE"
    echo "======================================" >> "$LOG_FILE"
fi

# ── Run the update ────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR" && ./weekly-update.sh >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# ── Record status and notify ─────────────────────────────────────────────────
if [ $EXIT_CODE -eq 0 ]; then
    # Write success so the 3pm retry knows to skip
    echo "SUCCESS $TODAY" > "$STATUS_FILE"
    osascript -e "display notification \"Weekly update complete ✅ Dashboard updated.\" with title \"MCE ProM Dashboard\"" 2>/dev/null || true
    echo "Exit code: 0 (success)" >> "$LOG_FILE"
else
    echo "FAILED $TODAY" > "$STATUS_FILE"
    if [ "$IS_RETRY" = "retry" ]; then
        osascript -e "display notification \"Weekly update FAILED on retry too. Check weekly-update.log\" with title \"MCE ProM Dashboard ❌\"" 2>/dev/null || true
    else
        osascript -e "display notification \"Weekly update failed — will retry at 3pm. Check weekly-update.log\" with title \"MCE ProM Dashboard ⚠️\"" 2>/dev/null || true
    fi
    echo "Exit code: $EXIT_CODE (failed)" >> "$LOG_FILE"
fi
