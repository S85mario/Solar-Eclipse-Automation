##!/usr/bin/env python3
"""
Gestione timing e attese
"""

import time
import sys
from datetime import datetime, timedelta
from utils.logger import log_messaggio
from utils.helpers import watchdog_reset
from utils.constants import (
    P1_INIZIO, TOTALITA_INIZIO, TOTALITA_FINE, P4_FINE,
    WATCHDOG_INTERVAL, FATTORE_COMPRESSIONE,
    stop_requested, pause_requested, MODALITA_SIM_COMPRESSA
)
from .telegram_notifier import invia_notifica_telegram_embed, check_telegram_commands
from .config_manager import ottieni_config

def calcola_contatti_gps():
    """Mostra i contatti dell'eclisse dalla configurazione"""
    config = ottieni_config()
    lat_dms = config["coordinate"]["latitudine_dms"]
    lon_dms = config["coordinate"]["longitudine_dms"]
    print(f"\n[GEOTARGET] Coordinate caricate: {lat_dms} , {lon_dms}")
    print(f"\n📅 ORARI ECLISSE ({config['timing_eclisse']['_data']}):")
    print(f"   P1 (Inizio parziale):   {P1_INIZIO}")
    print(f"   C2 (Inizio totalità):   {TOTALITA_INIZIO}")
    print(f"   C3 (Fine totalità):     {TOTALITA_FINE}")
    print(f"   P4 (Fine parziale):     {P4_FINE}")

def attesa_con_intervallo(intervallo_sec, messaggio):
    """Attesa con controllo comandi Telegram"""
    global stop_requested, pause_requested
    
    wait_sec = intervallo_sec
    while wait_sec > 0:
        check_telegram_commands()
        
        while pause_requested and not stop_requested:
            time.sleep(1)
        if stop_requested:
            log_messaggio("🛑 STOP richiesto!", "WARN")
            import sys
            sys.exit(0)
        
        sleep_time = min(10, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        
        if wait_sec > 0:
            print(f"\r   {messaggio} tra {wait_sec//60} minuti...", end='')
    print()

def attesa_con_compressione(tempo_target, nome_fase=""):
    """Attesa con tempo compresso per simulazione"""
    global stop_requested, pause_requested
    
    now = datetime.now()
    if now >= tempo_target:
        log_messaggio(f"🎯 {nome_fase} raggiunto!")
        return
    
    wait_sec = (tempo_target - now).total_seconds()
    if wait_sec <= 0:
        return
    
    # TEMPO GIA' COMPRESSO! Non moltiplicare ulteriormente
    log_messaggio(f"⏳ Attesa {wait_sec:.1f} secondi reali fino a {nome_fase}")
    invia_notifica_telegram_embed(f"INIZIO ATTESA {nome_fase}", f"Attesa di {wait_sec:.1f} secondi", "🔵")
    
    while wait_sec > 0:
        check_telegram_commands()
        
        while pause_requested and not stop_requested:
            time.sleep(0.1)
        if stop_requested:
            log_messaggio("🛑 STOP richiesto!", "WARN")
            sys.exit(0)
        
        sleep_time = min(1, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        
        if wait_sec > 0:
            print(f"\r   Ancora {wait_sec:.1f} secondi...", end='')
    
    print()
    log_messaggio(f"🎯 {nome_fase} raggiunto!")
    invia_notifica_telegram_embed(f"{nome_fase} RAGGIUNTA", f"Inizio acquisizione", "🟢")

def attesa_fino_a(orario_target, nome_fase=""):
    """Attesa standard per orario time (non simulazione)"""
    global stop_requested, pause_requested
    
    now = datetime.now()
    target = datetime.combine(now.date(), orario_target)
    if now > target:
        target += timedelta(days=1)
    
    wait_sec = (target - now).total_seconds()
    if wait_sec <= 0:
        log_messaggio(f"⚠️ Orario {orario_target} già passato per {nome_fase}!", "WARN")
        return
    
    log_messaggio(f"⏳ Attesa {wait_sec/60:.1f} minuti fino a {nome_fase} ({orario_target})")
    invia_notifica_telegram_embed(f"INIZIO ATTESA {nome_fase}", f"Attesa di {wait_sec/60:.1f} minuti", "🔵")
    
    last_watchdog = time.time()
    while wait_sec > 0:
        check_telegram_commands()
        
        while pause_requested and not stop_requested:
            time.sleep(1)
        if stop_requested:
            log_messaggio("🛑 STOP richiesto!", "WARN")
            import sys
            sys.exit(0)
        
        sleep_time = min(WATCHDOG_INTERVAL, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        
        if time.time() - last_watchdog >= WATCHDOG_INTERVAL:
            watchdog_reset()
            last_watchdog = time.time()
        
        if wait_sec > 0:
            print(f"\r⏳ Ancora {wait_sec:.0f} sec per {nome_fase}...", end='')
    
    print()
    log_messaggio(f"🎯 Ora {nome_fase} raggiunta!")
    invia_notifica_telegram_embed(f"{nome_fase} RAGGIUNTA", f"Inizio acquisizione", "🟢")