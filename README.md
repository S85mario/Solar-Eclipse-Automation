================================================================================
                    SOLAR ECLIPSE AUTOMATION SCRIPT
================================================================================

Professional automation script for total solar eclipse photography

Python 3.8+ | Windows | digiCamControl

================================================================================
                              TABLE OF CONTENTS
================================================================================

1.  Overview
2.  Features
3.  Requirements
4.  Installation
5.  Configuration
6.  Usage
7.  Timeline
8.  File Structure
9.  Logging
10. Troubleshooting
11. Testing
12. Best Practices
13. FAQ
14. Acknowledgments

================================================================================
                                1. OVERVIEW
================================================================================

This script automates the entire photography sequence during a total solar 
eclipse. It controls your camera via digiCamControl, executes precise HDR 
bracketing sequences, plays audio alerts at critical moments, and sends 
real-time notifications via Telegram.

Perfect for astrophotographers who want to focus on the eclipse experience 
while the script handles all camera operations with millisecond precision.

================================================================================
                               2. FEATURES
================================================================================

  Feature                | Description
  -----------------------|------------------------------------------------------
  Automated Shooting     | Complete eclipse sequence from C1 to P4
  Absolute Timing        | All actions based on exact clock time
  HDR Bracketing         | Automatic exposure sequences for corona
  Burst Mode             | Continuous shooting during diamond ring phases
  Audio Alerts           | Custom audio cues for filter changes
  Telegram Notifications | Real-time updates and remote commands
  Detailed Logging       | Every event, shot, and error recorded
  digiCamControl         | Full control via remote commands
  Auto Report            | Comprehensive statistics after the event
  Error Recovery         | Automatic reconnection attempts on camera errors

================================================================================
                             3. REQUIREMENTS
================================================================================

HARDWARE:
  - Windows PC (laptop recommended for portability)
  - Compatible camera (Canon, Nikon, Sony via digiCamControl)
  - USB cable
  - Tripod (recommended)

SOFTWARE:
  - digiCamControl (free) - https://digicamcontrol.com/
  - Python 3.8 or higher

OPTIONAL LIBRARIES:
  pip install requests   # For Telegram notifications
  pip install psutil     # For battery and disk space monitoring

================================================================================
                             4. INSTALLATION
================================================================================

STEP 1: Clone the Repository
  git clone https://github.com/S85mario/Solar-Eclipse-Automation.git
  cd solar-eclipse-automation

STEP 2: Install digiCamControl
  Download from https://digicamcontrol.com/ and install

STEP 3: Install Python Dependencies (Optional)
  pip install requests psutil

STEP 4: Prepare Audio Files (Optional)
  Create folder: C:\Eclissi\Audio\
  
  Add .wav files:
    togli_filtro.wav       - "Remove the solar filter"
    metti_filtro.wav       - "Put the solar filter back"
    mancano_20_secondi.wav - "20 seconds countdown"
    errore_connessione.wav - "Connection error"
    attenzione.wav         - "Attention"

================================================================================
                             5. CONFIGURATION
================================================================================

CONFIG_ECLIPSE.JSON

Create this file in the same folder as main.py:

{
  "hardware": {
    "marca_camera": "CANON",
    "gui_path": "C:\\Program Files (x86)\\digiCamControl\\CameraControl.exe",
    "cmd_path": "C:\\Program Files (x86)\\digiCamControl\\CameraControlRemoteCmd.exe"
  },
  "coordinate": {
    "latitudine_dms": "43°44'08.77\"N",
    "longitudine_dms": "7°55'20.04\"W"
  },
  "timing_eclisse": {
    "_data": "12 Agosto 2026",
    "c1_inizio": "19:30:00",
    "avviso_togli_filtro": "20:26:20",
    "anello_in_inizio": "20:26:50",
    "anello_in_fine": "20:27:20",
    "totalita_inizio": "20:27:25",
    "totalita_fine": "20:28:40",
    "anello_out_inizio": "20:28:50",
    "anello_out_fine": "20:29:20",
    "avviso_metti_filtro": "20:29:20",
    "post_parziale_inizio": "20:29:30",
    "p4_fine": "21:12:00"
  },
  "tempi_scatto": {
    "parziale": ["1/2000"],
    "burst": ["1/2000"],
    "corona_interna": ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15"],
    "corona_esterna": ["1/8", "1/4", "0.5", "1", "2"],
    "raffica_scatti": 5,
    "intervallo_parziale_sec": 780
  },
  "checklist_items": [
    "Camera turned on and connected?",
    "Save folder configured?",
    "PC clock synchronized?",
    "Configuration file valid?",
    "Battery sufficient?",
    "Free disk space sufficient?"
  ],
  "parametri_camera": {
    "iso_default": 200,
    "apertura_default": 8,
    "test_tempo": "1/1000"
  }
}

SECRETS.JSON (for Telegram)

Create this file for Telegram notifications:

{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
    "chat_id": "YOUR_CHAT_ID_FROM_USERINFOBOT"
  }
}

How to get Telegram credentials:
  1. Open Telegram and search for @BotFather
  2. Send /newbot and follow instructions
  3. Copy your bot token
  4. Search for @userinfobot and send /start
  5. Copy your chat ID

================================================================================
                               6. USAGE
================================================================================

START THE SCRIPT:
  python main.py

WHAT HAPPENS DURING EXECUTION:
  1. Initial Checks - Camera connection, battery, disk space
  2. Checklist - Interactive verification of all preparations
  3. Hardware Setup - digiCamControl starts and tests connection
  4. Wait for C1 - Script waits silently until the start time
  5. Auto Execution - Complete sequence runs automatically
  6. Report Generation - Summary with statistics at the end

TELEGRAM COMMANDS (if configured):
  /status  - Show current statistics
  /stop    - Emergency stop
  /pause   - Temporary pause
  /resume  - Resume execution
  /help    - Show available commands

================================================================================
                            7. TIMELINE
================================================================================

COMPLETE ECLIPSE SEQUENCE:

  Time      | Event                 | Action
  ----------|-----------------------|-------------------------------------------
  19:30:00  | C1 - Partial Start    | Shots every 13 minutes
  20:26:20  | Filter Alert          | "Remove the solar filter"
  20:26:50  | Diamond Ring IN       | Burst shots for 30 seconds
  20:27:25  | Totality (C2)         | Inner corona bracketing
  20:28:00  | Totality (C2)         | Outer corona bracketing
  20:28:40  | Totality End          | End bracketing
  20:28:50  | Diamond Ring OUT      | Burst shots for 30 seconds
  20:29:20  | Filter Alert          | "Put the solar filter back"
  20:29:30  | Post-Partial Start    | Shots every 10 minutes
  21:12:00  | P4 - Eclipse End      | Complete

SHOT COUNT SUMMARY:

  Phase            | Shots | Interval
  -----------------|-------|---------------
  Partial (In)     | ~8    | 13 minutes
  Diamond Ring IN  | ~15   | 30 sec burst
  Inner Corona     | 6     | Sequential
  Outer Corona     | 5     | Sequential
  Diamond Ring OUT | ~15   | 30 sec burst
  Partial (Out)    | ~10   | 10 minutes
  -----------------|-------|---------------
  TOTAL            | ~59   |

================================================================================
                          8. FILE STRUCTURE
================================================================================

solar-eclipse-automation/
├── main.py                          # Main script
├── config_eclipse.json              # Configuration
├── secrets.json                     # Telegram credentials (DO NOT SHARE!)
├── eclissi_log.txt                  # Simple log
├── eclissi_dettaglio.log            # Detailed log with timestamps
├── report_eclisse_*.txt             # Auto-generated report
│
└── C:\Eclissi\Audio\                # Audio files (optional)
    ├── togli_filtro.wav
    ├── metti_filtro.wav
    ├── mancano_20_secondi.wav
    ├── errore_connessione.wav
    └── attenzione.wav

================================================================================
                              9. LOGGING
================================================================================

TWO LOG FILES:

  eclissi_log.txt          Simple log with timestamps and messages
  eclissi_dettaglio.log    Detailed log with milliseconds and JSON data

LOG EXAMPLE:

  [2026-06-17 19:30:00.123] [INFO] In attesa dell'orario di inizio PRE-PARZIALE
  [2026-06-17 19:30:01.789] [SUCCESS] SCATTO: PRE-PARZIALE_1/2000_shot1
  [2026-06-17 20:26:20.000] [INFO] AVVISO: TOGLI IL FILTRO SOLARE
  [2026-06-17 20:26:50.000] [INFO] ANELLO_DIAMANTE_IN - Raffica 5 scatti
  [2026-06-17 21:12:00.000] [INFO] ECLISSE COMPLETATA!

================================================================================
                          10. TROUBLESHOOTING
================================================================================

PROBLEM: Camera not found
SOLUTION:
  1. Check USB connection
  2. Camera in Manual (M) mode
  3. digiCamControl running
  4. Press "Connect" in digiCamControl

PROBLEM: digiCamControl not starting
SOLUTION: Verify path in config_eclipse.json

PROBLEM: Script starts immediately
SOLUTION: Check c1_inizio time in config - may already be passed

PROBLEM: Audio not playing
SOLUTION: Verify folder C:\Eclissi\Audio\ and .wav files exist

PROBLEM: Telegram not working
SOLUTION: Check token and chat_id in secrets.json

PROBLEM: Script freezes
SOLUTION: Wait - it may be in a scheduled wait period

PROBLEM: Failed shots
SOLUTION: Camera may have gone to sleep - check power settings

QUICK CAMERA TEST:
  "C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe" /c get shutterspeed
  Expected output: :;response:"1/2000";

================================================================================
                             11. TESTING
================================================================================

QUICK TEST WITH MODIFIED TIMES:

For testing without waiting hours, modify config_eclipse.json:

  "c1_inizio": "20:00:00",
  "avviso_togli_filtro": "20:10:00",
  "anello_in_inizio": "20:10:30",
  "anello_in_fine": "20:11:00",
  "totalita_inizio": "20:11:05",
  "totalita_fine": "20:12:20",
  "anello_out_inizio": "20:12:30",
  "anello_out_fine": "20:13:00",
  "avviso_metti_filtro": "20:13:00",
  "post_parziale_inizio": "20:13:10",
  "p4_fine": "20:30:00"

This compresses the entire sequence to ~30 minutes.

================================================================================
                          12. BEST PRACTICES
================================================================================

1 WEEK BEFORE:
  [ ] Test the script with modified times
  [ ] Verify camera batteries (have spares)
  [ ] Format SD cards
  [ ] Backup configuration files
  [ ] Check USB cable quality

DAY BEFORE:
  [ ] Charge PC battery to 100%
  [ ] Prepare spare cables
  [ ] Verify solar filter orientation
  [ ] Lock focus with tape
  [ ] Synchronize PC clock (use time.windows.com)

DURING ECLIPSE:
  [ ] Do not touch PC or camera
  [ ] Monitor logs only (no interaction)
  [ ] Use external battery if possible
  [ ] Stay calm - script does everything

AFTER ECLIPSE:
  [ ] Backup all photos
  [ ] Save log files
  [ ] Don't format SD until double backup complete
  [ ] Share your results!

================================================================================
                              13. FAQ
================================================================================

Q: Can I use this with any camera?
A: Any camera supported by digiCamControl (Canon, Nikon, Sony)

Q: What if the camera disconnects during the eclipse?
A: The script will automatically attempt to reconnect

Q: Does this work without Telegram?
A: Yes, Telegram is optional. The script works fully without it.

Q: Can I use WiFi instead of USB?
A: Not recommended - USB is more reliable for critical events.

Q: What if the PC battery dies?
A: On restart, the script will resume from the last saved state.

Q: How many photos will it take?
A: Approximately 59 shots (configurable)

Q: What if I miss the start time?
A: The script detects if C1 is passed and starts immediately.

Q: Do I need to keep the command prompt open?
A: Yes, the script runs in the command prompt window.

Q: Can I minimize the script window?
A: Yes, but don't close it.

================================================================================
                          14. ACKNOWLEDGMENTS
================================================================================

- digiCamControl team for the excellent camera control software
- Italian astrophotography community for field testing
- All open source contributors

================================================================================
                             SUPPORT
================================================================================

GitHub Issues: https://github.com/S85mario/solar-eclipse-automation/issues

================================================================================

                         Happy eclipse! 🌞🌑📸

                Documentation version 5.0 - June 2026

================================================================================