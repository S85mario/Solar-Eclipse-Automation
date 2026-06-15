#!/usr/bin/env python3
"""
Sistema di logging centralizzato
"""

import sys
from datetime import datetime
from .constants import LOG_FILE, DEBUG_MODE

def log_messaggio(messaggio, level="INFO"):
    """Logga messaggio su console e file"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    formattato = f"[{timestamp}] [{level}] {messaggio}"
    
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    print(formattato)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formattato + "\n")
    except:
        pass

def log_debug(messaggio):
    """Logga solo se DEBUG_MODE è attivo"""
    if DEBUG_MODE:
        log_messaggio(f"[DEBUG] {messaggio}")