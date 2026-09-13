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
    local delay=0.04
    printf "${BOLD}${GREEN}[shaswatraj@Sh ~ %% ${NC}"
    for ((i=0; i<${#cmd}; i++)); do
        printf "%s" "${cmd:$i:1}"
        sleep $delay
    done
    printf "\n"
    sleep 0.6
}

# Ensure omni is available
if ! command -v omni &> /dev/null; then
    alias omni="python3 $(pwd)/cli.py"
fi

clear
sleep 1.0

# ------------------------------------------------------------------------------
# Scene 1: Starting with 'omni' interactive mode (matching screenshot)
# ------------------------------------------------------------------------------
type_command "omni"
python3 -c "from cli import print_banner, _c, BOLD, CYAN, GREEN; print_banner(); print(_c(BOLD, 'Welcome to OmniAudit-GEO! Choose an action or paste any URL directly:\n')); print(f'  {_c(CYAN, \"[1]\")} 🚀 Run Master Website Audit\n  {_c(CYAN, \"[2]\")} ⚔️  Competitor Head-to-Head Benchmark (Compare 2 sites)\n  {_c(CYAN, \"[3]\")} 📊 Run 16 Golden Benchmarks (Accuracy Suite)\n  {_c(CYAN, \"[4]\")} 🤖 Generate AI Remediation Fix Prompt (Claude / Cursor)\n  {_c(CYAN, \"[5]\")} 🔬 Run Specialist Skill Audit\n  {_c(CYAN, \"[6]\")} 🌐 Launch Web Dashboard & REST API (http://localhost:8000)\n  {_c(CYAN, \"[7]\")} 📖 Browse Documentation Catalog\n  {_c(CYAN, \"[8]\")} 🚪 Exit\n')"
sleep 2.0
printf "${BOLD}${GREEN}Select an option [1-8] or enter URL [default: 1]: ${NC}"
target="https://adobe.com"
for ((i=0; i<${#target}; i++)); do
    printf "%s" "${target:$i:1}"
    sleep 0.04
done
printf "\n"
sleep 0.8

clear
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
