VENV_DIR=".cocotb-examples"
REQ_FILE="requirements.txt"
SENTINEL="$VENV_DIR/last_install"

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'          # No Color

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}Creating virtual environment...${NC}"
  python3 -m venv "$VENV_DIR"
fi

# Activate environment
source "$VENV_DIR/bin/activate"

# Check if requirements.txt is newer than our sentinel file
if [ ! -f "$SENTINEL" ] || [ "$REQ_FILE" -nt "$SENTINEL" ]; then
  echo -e "${YELLOW}Updating dependencies...${NC}"
  pip install --upgrade pip
  pip install -r "$REQ_FILE"
  
  # Update the timestamp of the sentinel file
  touch "$SENTINEL"
  echo -e "${YELLOW}Environment is up to date.${NC}"
else
  echo -e "${YELLOW}Environment is already up to date.${NC}"
fi