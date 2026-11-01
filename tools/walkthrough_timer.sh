#!/usr/bin/env bash
# Timestamps for the by-hand walkthrough (RUN_REPORT §8).
#   tools/walkthrough_timer.sh start            # new log
#   tools/walkthrough_timer.sh step "read docs" # marks the END of the named step
#   tools/walkthrough_timer.sh stop             # prints the table
# Log: review/walkthrough_log.txt (outside git).
set -euo pipefail
LOG=${WALKTHROUGH_LOG:-"$(cd "$(dirname "$0")/.." && pwd)/review/walkthrough_log.txt"}
now=$(date +%s)
case "${1:-}" in
  start) mkdir -p "$(dirname "$LOG")"; echo "start $now $(date '+%Y-%m-%d %H:%M:%S')" > "$LOG"; echo "started $(date '+%H:%M:%S')";;
  step)  last=$(tail -n1 "$LOG" | awk '{print $2}'); mins=$(( (now - last + 30) / 60 ))
         echo "step $now ${2:-unnamed} ${mins}" >> "$LOG"; echo "$(date '+%H:%M:%S')  ${2:-unnamed}  ${mins} min";;
  stop)  first=$(head -n1 "$LOG" | awk '{print $2}'); total=$(( (now - first + 30) / 60 ))
         echo "stop $now total ${total}" >> "$LOG"
         echo; echo "| step | minutes | stuck? |"; echo "|---|---|---|"
         awk '$1=="step"{name=""; for(i=3;i<NF;i++) name=name $i " "; printf "| %s| %s | |\n", name, $NF}' "$LOG"
         echo "| **total** | **${total}** | |";;
  *) echo "usage: $0 start | step \"name\" | stop"; exit 2;;
esac
