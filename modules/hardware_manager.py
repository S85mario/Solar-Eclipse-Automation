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

def avvia_digicamcontrol_minimized():
    """Avvia digiCamControl con verifica effettiva dell'avvio"""
    global SIM_MODE, GUI_PATH
    
    if SIM_MODE:
        return True
    
    # Verifica se è già in esecuzione
    try:
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' in risultato.stdout:
            log_messaggio("✅ digiCamControl già in esecuzione")
            return True
    except:
        pass
    
    # Verifica che il file esista
    if not os.path.exists(GUI_PATH):
        log_messaggio(f"❌ digiCamControl non trovato in: {GUI_PATH}", "ERROR")
        return False
    
    try:
        log_messaggio(f"🚀 Avvio digiCamControl da: {GUI_PATH}")
        
        # Avvia normalmente (senza PowerShell)
        subprocess.Popen([GUI_PATH], shell=True)
        
        # Attesa per l'avvio con verifica
        log_messaggio("⏳ Attendere l'avvio di digiCamControl...")
        
        for i in range(15, 0, -1):
            print(f"\r   {i} secondi rimanenti...", end='')
            time.sleep(1)
        print("\r   ✅ Attesa completata!                     ")
        
        # Verifica che sia effettivamente partito
        time.sleep(2)
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' in risultato.stdout:
            log_messaggio("✅ digiCamControl avviato con successo")
            return True
        else:
            log_messaggio("⚠️ digiCamControl non risulta in esecuzione", "WARN")
            return False
            
    except Exception as e:
        log_messaggio(f"❌ Errore avvio digiCamControl: {e}", "ERROR")
        return False    

def test_connessione_camera():
    """Testa la connessione con la camera - con verifica processo"""
    if SIM_MODE:
        return True
    
    # Prima verifica che digiCamControl sia in esecuzione
    try:
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' not in risultato.stdout:
            log_messaggio("❌ digiCamControl NON è in esecuzione!", "ERROR")
            return False
        else:
            log_messaggio("✅ digiCamControl in esecuzione")
    except:
        pass
    
    log_messaggio("🔍 Test connessione camera...")
    
    # Prova il comando per leggere la camera
    for tentativo in range(1, 4):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "get", "shutterspeed"], 
                                     capture_output=True, text=True, timeout=5)
            if risultato.returncode == 0 and risultato.stdout:
                log_messaggio(f"✅ Camera connessa! Risposta: {risultato.stdout.strip()}")
                return True
            else:
                log_messaggio(f"   Tentativo {tentativo}: risposta vuota", "WARN")
        except subprocess.TimeoutExpired:
            log_messaggio(f"   Tentativo {tentativo}: timeout", "WARN")
        except Exception as e:
            log_messaggio(f"   Tentativo {tentativo}: {e}", "WARN")
        
        if tentativo < 3:
            time.sleep(2)
    
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
    """Cambia tempo di scatto con attesa maggiore per stabilizzazione"""
    if SIM_MODE:
        log_debug(f"[SIM] Imposto tempo: {tempo}")
        return True
    
    # Attesa extra prima del primo tentativo (per stabilizzazione)
    time.sleep(1)
    
    for tentativo in range(1, max_tentativi + 1):
        try:
            log_messaggio(f"   Tentativo {tentativo}/{max_tentativi}: impostazione tempo {tempo}...")
            
            risultato = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", tempo], 
                                      capture_output=True, text=True, timeout=10)  # Timeout aumentato
            
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                # Attesa più lunga per stabilizzazione
                durata = converti_tempo_in_secondi(tempo)
                if durata >= 0.25:
                    time.sleep(1.0 + durata)  # Aumentato da 0.15 a 1.0
                else:
                    time.sleep(1.0)  # Aumentato da 0.15 a 1.0
                log_messaggio(f"   ✅ Tempo {tempo} impostato")
                return True
            else:
                log_messaggio(f"   ⚠️ Risposta inaspettata: {risultato.stdout[:50]}")
                
        except subprocess.TimeoutExpired:
            log_messaggio(f"   ⏰ Timeout al tentativo {tentativo}", "WARN")
        except Exception as e:
            log_messaggio(f"   ❌ Errore USB al tentativo {tentativo}: {e}", "WARN")
        
        time.sleep(1.5)  # Attesa maggiore tra tentativi
        
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