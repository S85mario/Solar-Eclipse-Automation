#!/usr/bin/env python3
"""
Gestione centralizzata delle configurazioni
"""

import os
import json
from utils.logger import log_messaggio, log_debug
from utils.constants import (
    CONFIG_FILE, SECRETS_FILE, COMPRESSIONE_FILE,
    FATTORE_COMPRESSIONE, CONFIG, secrets
)

def carica_configurazione():
    """Carica la configurazione principale"""
    global CONFIG
    if not os.path.exists(CONFIG_FILE):
        log_messaggio(f"File {CONFIG_FILE} non trovato!", "ERROR")
        return None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
        log_messaggio(f"Configurazione caricata da {CONFIG_FILE}")
        return CONFIG
    except Exception as e:
        log_messaggio(f"Errore caricamento: {e}", "ERROR")
        return None

def carica_secrets():
    """Carica le credenziali da file separato"""
    global secrets
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
                secrets = json.load(f)
            log_debug("Credenziali caricate")
            return True
        except Exception as e:
            log_messaggio(f"Errore caricamento secrets: {e}", "WARN")
            return False
    return False

def carica_fattore_compressione():
    """Carica il fattore di compressione da file"""
    global FATTORE_COMPRESSIONE
    try:
        if os.path.exists(COMPRESSIONE_FILE):
            with open(COMPRESSIONE_FILE, 'r') as f:
                data = json.load(f)
                FATTORE_COMPRESSIONE = data.get("fattore", 60)
    except:
        pass

def salva_fattore_compressione():
    """Salva il fattore di compressione su file"""
    global FATTORE_COMPRESSIONE
    try:
        with open(COMPRESSIONE_FILE, 'w') as f:
            json.dump({"fattore": FATTORE_COMPRESSIONE}, f)
    except:
        pass

def salva_configurazione(config_data, filename=CONFIG_FILE):
    """Salva una configurazione su file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        log_messaggio(f"Configurazione salvata in {filename}")
        return True
    except Exception as e:
        log_messaggio(f"Errore salvataggio: {e}", "ERROR")
        return False

def ottieni_config():
    """Restituisce la configurazione corrente"""
    return CONFIG

def ottieni_secrets():
    """Restituisce i secrets correnti"""
    return secrets