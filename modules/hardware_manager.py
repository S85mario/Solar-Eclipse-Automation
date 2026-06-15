#!/usr/bin/env python3
"""
Gestione camera e digiCamControl
"""

import os
import time
import subprocess
from utils.logger import log_messaggio, log_debug
from utils.helpers import converti_tempo_in_secondi, emetti_suono
from utils.constants import SIM_MODE, stats
from .config_manager import ottieni_config

CMD_PATH = ""
GUI_PATH = ""

def init_hardware():
    """Inizializza i percorsi hardware"""
    global CMD_PATH, GUI_PATH
    config = ottieni_config()
    if config:
        CMD_PATH = config["hardware"]["cmd_path"]
        GUI_PATH = config["hardware"]["gui_path"]

def avvia_digicamcontrol():
    """Avvia digiCamControl se non è in esecuzione"""
    if SIM_MODE:
        return True
    try:
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' in risultato.stdout:
            log_messaggio("✅ digiCamControl già in esecuzione")
            return True
    except:
        pass
    try:
        log_messaggio("🚀 Avvio digiCamControl...")
        subprocess.Popen([GUI_PATH], shell=True)
        time.sleep(5)
        log_messaggio("✅ digiCamControl avviato")
        return True
    except Exception as e:
        log_messaggio(f"❌ Errore avvio digiCamControl: {e}", "ERROR")
        return False

def test_connessione_camera():
    """Testa la connessione con la camera"""
    if SIM_MODE:
        return True
    log_messaggio("🔍 Test connessione camera...")
    try:
        risultato = subprocess.run([CMD_PATH, "/c", "get", "shutterspeed"], 
                                 capture_output=True, text=True, timeout=5)
        if risultato.returncode == 0:
            log_messaggio("✅ Camera connessa!")
            return True
    except:
        pass
    log_messaggio("❌ Camera non trovata!", "ERROR")
    return False

def controlla_telemetria():
    """Monitora batteria portatile"""
    try:
        import psutil
        batteria = psutil.sensors_battery()
        if batteria:
            if not batteria.power_plugged and batteria.percent < 20:
                log_messaggio(f"⚠️ BATTERIA AL {batteria.percent}% - NON IN CARICA!", "WARN")
                emetti_suono("attenzione")
            elif not batteria.power_plugged and batteria.percent < 10:
                log_messaggio(f"🚨 CRITICO: BATTERIA AL {batteria.percent}%!", "ERROR")
                emetti_suono("critico")
            return batteria.percent
    except:
        pass
    return None

def imposta_tempo_scatto(tempo, max_tentativi=3):
    """Cambia tempo di scatto"""
    if SIM_MODE:
        log_debug(f"[SIM] Imposto tempo: {tempo}")
        return True
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", tempo], 
                                      capture_output=True, text=True, timeout=5)
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                durata = converti_tempo_in_secondi(tempo)
                if durata >= 0.25:
                    time.sleep(0.15 + durata)
                else:
                    time.sleep(0.15)
                return True
        except:
            pass
        time.sleep(0.2)
    log_messaggio(f"❌ CRITICO: Cambio tempo fallito ({tempo})!", "ERROR")
    emetti_suono("critico")
    return False

def scatta_foto_simulazione(etichetta):
    """Versione semplificata per la simulazione - sempre successo"""
    global stats
    
    log_messaggio(f"[SIM] 📸 Scatto: {etichetta}")
    stats['scatti_riusciti'] += 1
    stats['totale_scatti_eseguiti'] += 1
    
    # Estrai il tempo dall'etichetta per le statistiche
    parti = etichetta.split('_')
    for parte in parti:
        if '/' in parte or (parte.replace('.', '').replace('-', '').isdigit() and len(parte) < 10):
            if parte not in stats['tempi_scatto_utilizzati']:
                stats['tempi_scatto_utilizzati'].append(parte)
            break
    
    time.sleep(0.05)
    return True

def scatta_foto(etichetta, max_tentativi=3):
    """Esegue uno scatto"""
    global stats
    
    # MODALITA' SIMULAZIONE - SEMPRE SUCCESSO
    if SIM_MODE:
        log_messaggio(f"[SIM] 📸 Scatto: {etichetta}")
        stats['scatti_riusciti'] += 1
        stats['totale_scatti_eseguiti'] += 1
        # Estrai il tempo dall'etichetta per le statistiche
        parti = etichetta.split('_')
        for parte in parti:
            if '/' in parte or parte.replace('.', '').isdigit():
                stats['tempi_scatto_utilizzati'].append(parte)
                break
        time.sleep(0.05)
        return True
    
    # MODALITA' REALE
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "capture"], 
                                      capture_output=True, text=True, timeout=10)
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                stats['scatti_riusciti'] += 1
                stats['totale_scatti_eseguiti'] += 1
                return True
        except:
            pass
        time.sleep(0.2)
    
    log_messaggio(f"❌ CRITICO: Scatto fallito per {etichetta}!", "ERROR")
    stats['scatti_falliti'] += 1
    stats['totale_scatti_eseguiti'] += 1
    return False