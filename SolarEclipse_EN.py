import os
import sys
import time
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# ==============================================================================
# CAMERA CONFIGURATION & BRAND PROFILES
# ==============================================================================

# Choose your camera brand: "CANON", "NIKON", or "SONY"
CAMERA_BRAND = "CANON"  

# --- SHUTTER SPEED HDR PROFILES PER BRAND ---
# digiCamControl interprets command-line values based on native firmware protocols.
SHUTTER_PROFILES = {
    "CANON": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "0.5",  # Canon-specific decimal notation for 1/2s
        "1"
    ],
    "NIKON": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "1/2",  # Standard fractional notation for Nikon
        "1"
    ],
    "SONY": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "1/2",  # Sony standard fractional notation via MTP/PC Remote
        "1"
    ]
}

# Dynamic assignment of the HDR sequence based on the selected brand
if CAMERA_BRAND.upper() in SHUTTER_PROFILES:
    SHUTTER_SPEEDS_HDR = SHUTTER_PROFILES[CAMERA_BRAND.upper()]
else:
    print(f"[CRITICAL ERROR] Camera brand '{CAMERA_BRAND}' not supported. Defaulting to CANON profile.")
    SHUTTER_SPEEDS_HDR = SHUTTER_PROFILES["CANON"]

# ==============================================================================
# GLOBAL SYSTEM CONFIGURATION
# ==============================================================================

GUI_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControl.exe"
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
LOG_FILE = "eclipse_log.txt"

SIM_MODE = False        # Set to True to simulate the entire eclipse sequence at home
SIM_SPEED_UP = 1.0      # Speed-up factor for dry-run testing (keep 1.0 for live event)

# Local times for the 4 Eclipse Contacts
P1_START       = datetime_time(19, 30, 0)   
TOTALITY_START = datetime_time(20, 27, 0)   
TOTALITY_END   = datetime_time(20, 28, 45)  
P3_END         = datetime_time(21, 15, 0)   

INTERVAL_INGRESS = 1080  
INTERVAL_EGRESS  = 690   

# --- LOCALIZED AUDIO FILE PATHS ---
AUDIO_1_MIN          = r"C:\Eclipse\Audio\one_minute_left.wav"
AUDIO_TOGLI_FILTRO   = r"C:\Eclipse\Audio\remove_filter.wav"
AUDIO_20_SEC         = r"C:\Eclipse\Audio\20_seconds_left.wav"
AUDIO_METTI_FILTRO   = r"C:\Eclipse\Audio\replace_filter.wav"

# --- SHUTTER SPEED SEQUENCE FOR DIAMOND RING BURST ---
SHUTTER_SPEEDS_BURST = ["1/8000", "1/4000", "1/2000", "1/1000"]

# ==============================================================================
# SYSTEM UTILITIES (SOFTWARE LAUNCH, LOGGING, AUDIO, CLOCK)
# ==============================================================================

def start_digicamcontrol():
    """Automatically launches the digiCamControl GUI in the background"""
    if SIM_MODE:
        log_message("[SIM] Automated launch of digiCamControl simulated.")
        return
        
    log_message(f"Checking digiCamControl status for profile: {CAMERA_BRAND}...")
    if os.path.exists(GUI_PATH):
        try:
            subprocess.Popen([GUI_PATH])
            log_message("digiCamControl application launched successfully.")
            log_message("Waiting 5 seconds for software initialization and USB handshake...")
            time.sleep(5)
        except Exception as e:
            log_message(f"Unable to launch digiCamControl automatically: {e}", level="ERROR")
    else:
        log_message(f"GUI executable not found at specified path: {GUI_PATH}", level="ERROR")


def log_message(message, level="INFO"):
    """Writes the log to the console and appends it to the emergency text file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    
    print(formatted_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception as e:
        print(f"[LOG WRITE ERROR] Unable to write to log file: {e}")


class SimClock:
    def __init__(self, start_time_obj, speed_up=1.0, active=False):
        self.active = active
        self.speed