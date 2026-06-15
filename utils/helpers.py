#!/usr/bin/env python3
"""
Funzioni di utilità generiche
"""

import time
import winsound
import json
import os
from datetime import datetime, time as datetime_time
from .constants import MODALITA_SIM_COMPRESSA, FATTORE_COMPRESSIONE, WATCHDOG_FILE, STATO_FILE

def stringa_a_time(time_str):
    """Converte stringa HH:MM:SS in oggetto time"""
    h, m, s = map(int, time_str.split(':'))
    return datetime_time(h, m, s)

def emetti_suono(tipo="attenzione"):
    """Emette un suono in base al tipo"""
    try:
        if tipo == "attenzione":
            winsound.Beep(2000, 1000)
        elif tipo == "critico":
            winsound.Beep(2500, 500)
        elif tipo == "completamento":
            winsound.Beep(1000, 200)
            winsound.Beep(1500, 200)
            winsound.Beep(2000, 500)
    except:
        pass

def converti_tempo_in_secondi(stringa_tempo):
    """Converte stringa tempo in secondi"""
    try:
        if "/" in stringa_tempo:
            num, denom = stringa_tempo.split("/")
            return float(num) / float(denom)
        return float(stringa_tempo)
    except:
        return 0.1

def calc_pausa(tempo_scatto):
    """Calcola pausa basata sul tempo di scatto"""
    durata = converti_tempo_in_secondi(tempo_scatto)
    
    if MODALITA_SIM_COMPRESSA and FATTORE_COMPRESSIONE > 1:
        if durata < 0.5:
            return 0.1
        elif durata < 5:
            return durata * 0.3
        else:
            return durata * 0.2
    else:
        if durata < 0.5:
            return 1.0
        elif durata < 5:
            return durata * 1.2
        else:
            return durata + 1.0

def salva_stato(fase, indice):
    """Salva lo stato corrente per hot-resume"""
    try:
        stato = {
            'fase': fase,
            'indice': indice,
            'timestamp': datetime.now().isoformat(),
            'ultimo_scatto': datetime.now().strftime('%H:%M:%S')
        }
        with open(STATO_FILE, 'w') as f:
            json.dump(stato, f, indent=2)
    except:
        pass

def carica_stato():
    """Carica lo stato precedente per resume"""
    if os.path.exists(STATO_FILE):
        try:
            with open(STATO_FILE, 'r') as f:
                stato = json.load(f)
            return stato
        except:
            pass
    return None

def watchdog_reset():
    """Reset watchdog per evitare freeze totale"""
    try:
        with open(WATCHDOG_FILE, "w") as f:
            f.write(datetime.now().isoformat())
    except:
        pass