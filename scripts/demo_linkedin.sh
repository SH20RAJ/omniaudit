#!/usr/bin/env bash
# ==============================================================================
# OmniAudit-GEO — Automated LinkedIn Terminal Demo Player
# Run this script in your terminal to record a clean, beautiful live demo!
# Tip: On macOS, press Cmd + Shift + 5 to select your terminal window and record.
# ==============================================================================

set -e

# Terminal Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Typing simulation function
type_command() {
    local cmd="$1"
    local delay=0.035
    printf "${BOLD}${GREEN}shaswatraj@macOS${NC}:${BOLD}${BLUE}~${NC}$ "
    for ((i=0; i<${#cmd}; i++)); do
        printf "%s" "${cmd:$i:1}"
        sleep $delay
    done
    printf "\n"
    sleep 0.5
}

# Ensure omni is available
if ! command -v omni &> /dev/null; then
    alias omni="python3 $(pwd)/cli.py"
fi

clear
sleep 1.0

# ------------------------------------------------------------------------------
# Scene 1: Welcome & Help / Capabilities Overview
# ------------------------------------------------------------------------------
type_command "omni --help"
python3 cli.py --help | head -n 28
printf "\n${CYAN}... [6 specialist skills · 16 golden benchmarks · MCP server] ...${NC}\n"
sleep 3.0

clear
sleep 0.8

# ------------------------------------------------------------------------------
# Scene 2: Live Instant Audit (Adobe.com)
# ------------------------------------------------------------------------------
type_command "omni https://adobe.com"
python3 cli.py https://adobe.com
sleep 4.0

clear
sleep 0.8

# ------------------------------------------------------------------------------
# Scene 3: Head-to-Head Competitor Benchmark (Adobe vs Canva)
# ------------------------------------------------------------------------------
type_command "omni compare https://adobe.com https://canva.com"
python3 cli.py compare https://adobe.com https://canva.com
sleep 4.0

clear
sleep 0.8

# ------------------------------------------------------------------------------
# Scene 4: Auto-Generating AI Remediation Fix Prompt for Clipboard
# ------------------------------------------------------------------------------
type_command "omni prompt https://example.com"
python3 cli.py prompt https://example.com
sleep 3.5

clear
sleep 0.8

# ------------------------------------------------------------------------------
# Scene 5: 16 Golden Ground-Truth Evaluation Matrix
# ------------------------------------------------------------------------------
type_command "omni benchmark"
python3 cli.py benchmark
sleep 4.0

# Celebration finale banner
printf "\n${BOLD}${GREEN}✓ Live demo complete! Press Cmd+Shift+5 to stop recording.${NC}\n\n"
