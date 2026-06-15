📖 Solar Eclipse Automation Script

https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/python-3.8+-blue.svg
https://img.shields.io/badge/platform-Windows%2520%257C%2520Linux%2520%257C%2520Mac-lightgrey.svg

    Automated photography script for total solar eclipses | Script di automazione fotografica per eclissi solari totali

📑 Table of Contents | Indice

    English Version

    Versione Italiana
🎯 Overview

Solar Eclipse Automation Script is a professional tool for automatically capturing photos during a total solar eclipse. It manages complex HDR sequences, supports hot-resume, hardware telemetry, time compression for testing, and Telegram notifications.
✨ Features
Feature	Description
📷 HDR Sequences	Automatic exposure bracketing for prominences, corona, and diamond ring
🔄 Hot-Resume	Automatically resumes from the last captured shot after interruption
📱 Telegram Notifications	Real-time alerts and remote commands (/status, /stop, /pause, /resume)
⚡ Time Compression	Test the entire eclipse in minutes (60x compression)
🔋 Battery Monitoring	Alerts when laptop battery is low (requires psutil)
📊 Auto Report	Generates detailed statistics after the event
🎮 Wizard Configuration	Interactive setup guide
💾 State Persistence	Saves progress every shot for crash recovery
📸 Shooting Sequence
Phase	Duration	Interval	Shots	Shutter Speed
Partial (In)	45 min	15 min	3	1/2000
Diamond Ring (In)	5 sec	Immediate	9	1/8000-1/2000
Inner Corona	50 sec	Sequential	6	1/500-1/15
Outer Corona	50 sec	Sequential	5	1/8-2 sec
Diamond Ring (Out)	5 sec	Immediate	9	1/8000-1/2000
Partial (Out)	45 min	15 min	3	1/2000

Total: ~35 shots
🚀 Quick Start
1. Prerequisites
bash

# Windows only (for camera control)
digiCamControl: https://digicamcontrol.com/

# Python 3.8 or higher
python --version

# Optional libraries
pip install psutil requests

2. Installation
bash

# Clone the repository
git clone https://github.com/yourusername/solar-eclipse-automation.git
cd solar-eclipse-automation

# Install dependencies (optional)
pip install -r requirements.txt

3. Configuration

Create secrets.json for Telegram (required for notifications):
json

{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
    "chat_id": "YOUR_CHAT_ID_FROM_USERINFOBOT"
  }
}

Edit config_eclipse.json to set your location and eclipse times:
json

{
  "coordinate": {
    "latitudine_dms": "43°44'08.77\"N",
    "longitudine_dms": "7°55'20.04\"W"
  },
  "timing_eclisse": {
    "p1_inizio": "19:30:00",
    "totalita_inizio": "20:27:10",
    "totalita_fine": "20:28:50",
    "p4_fine": "21:12:00"
  }
}

4. Run
bash

python main.py

Menu Options:

    1 - Quick test with time compression (60x)

    2 - Real mode (for the actual event)

    3 - Configuration wizard

    4 - Change compression factor

    5 - Exit

📱 Telegram Commands
Command	Action
/status	Show current statistics
/stop	Emergency stop
/pause	Temporary pause
/resume	Resume execution
/help	Show available commands

⚙️ Time Compression Factors
Factor	Real Time	Simulated Time	Use Case
1x	100 min	100 min	Actual event
30x	100 min	3.3 min	Medium test
60x	100 min	1.7 min	Quick test
120x	100 min	50 sec	Very fast test
📊 Sample Report Output
text

======================================================================
   REPORT ECLISSE SOLARE - 2026-08-12 21:15:30
======================================================================

📅 INFORMAZIONI GENERALI:
   Data eclisse: 12 Agosto 2026
   Località: 43°44'08.77"N, 7°55'20.04"W
   Camera: CANON
   Modalità: REALE

----------------------------------------------------------------------

📸 STATISTICHE SCATTI:
   Fasi completate:        6/6
   Scatti previsti:        35
   Scatti eseguiti:        35
   Scatti riusciti:        34
   Scatti falliti:         1
   Successo:               97.1%

----------------------------------------------------------------------

🔋 BATTERIA:
   Batteria inizio:        100%
   Batteria fine:          67%
   Consumo:                33%

======================================================================

🛠️ Troubleshooting
Issue	Solution
Camera not found	Check USB connection, camera in Manual mode, digiCamControl running
Telegram not working	Verify token and chat_id in secrets.json
Script freezes	Reduce watchdog interval in config
Simulation too slow	Increase compression factor (option 4)