#!/usr/bin/env python3
"""
Solar Eclipse Automation Script - v5.0 (Modulare)
Punto di ingresso principale
"""

import sys
import time
from datetime import datetime

# Import moduli
from utils.constants import *
from utils.logger import log_messaggio
from utils.helpers import emetti_suono, stringa_a_time
from modules.config_manager import (
    carica_configurazione, carica_secrets, carica_fattore_compressione,
    salva_fattore_compressione, ottieni_config, ottieni_secrets
)
from modules.telegram_notifier import invia_notifica_telegram, invia_notifica_telegram_embed
from modules.hardware_manager import init_hardware, controlla_telemetria
from modules.time_manager import calcola_contatti_gps
from modules.sequence_executor import run_automazione_normale, run_simulazione_compressa
from modules.statistics import genera_report_finale
from modules.ui_manager import run_checklist, wizard_configurazione

def inizializza_variabili_globali():
    """Inizializza tutte le variabili globali dalla configurazione"""
    global P1_INIZIO, TOTALITA_INIZIO, TOTALITA_FINE, P4_FINE
    global TEMPI_HDR, TEMPI_BURST, TEMPI_CORONA_INTERNA, TEMPI_CORONA_ESTERNA
    global TEMPI_PROTUBERANZE, TEMPI_CORONA, TEMPI_PARZIALE, RAFAGA_SCATTI
    global CHECKLIST_ITEMS, TEST_TEMPO, WATCHDOG_INTERVAL
    global stats
    
    config = ottieni_config()
    
    # Timing
    P1_INIZIO = stringa_a_time(config["timing_eclisse"]["p1_inizio"])
    TOTALITA_INIZIO = stringa_a_time(config["timing_eclisse"]["totalita_inizio"])
    TOTALITA_FINE = stringa_a_time(config["timing_eclisse"]["totalita_fine"])
    P4_FINE = stringa_a_time(config["timing_eclisse"]["p4_fine"])
    
    # Aggiorna anche in constants
    from utils import constants
    constants.P1_INIZIO = P1_INIZIO
    constants.TOTALITA_INIZIO = TOTALITA_INIZIO
    constants.TOTALITA_FINE = TOTALITA_FINE
    constants.P4_FINE = P4_FINE
    
    # Tempi scatto
    TEMPI_PROTUBERANZE = config["tempi_scatto"]["protuberanze"]
    TEMPI_CORONA = config["tempi_scatto"]["corona"]
    TEMPI_BURST = config["tempi_scatto"]["burst"]
    TEMPI_PARZIALE = config["tempi_scatto"].get("parziale", ["1/2000"])
    TEMPI_HDR = TEMPI_PROTUBERANZE + TEMPI_CORONA
    TEMPI_CORONA_INTERNA = TEMPI_CORONA[:6]
    TEMPI_CORONA_ESTERNA = TEMPI_CORONA[6:]
    RAFAGA_SCATTI = config["tempi_scatto"]["raffica_scatti"]
    
    # Checklist
    CHECKLIST_ITEMS = config["checklist_items"]
    TEST_TEMPO = config["parametri_camera"]["test_tempo"]
    
    # Intervalli
    WATCHDOG_INTERVAL = config["intervalli"]["watchdog_interval_sec"]
    
    # Statistiche
    stats['totale_scatti_previsti'] = sum([
        len(f["lista_tempi"]) * (3 if f.get("usa_raffica", False) else 1) 
        for f in config["fasi_eclisse"]
        if f.get("intervallo_scatti", 0) == 0
    ])
    for f in config["fasi_eclisse"]:
        if f.get("intervallo_scatti", 0) > 0:
            stats['totale_scatti_previsti'] += int(f["durata_sec"] / f["intervallo_scatti"])

def main():
    """Punto di ingresso principale"""
    global FATTORE_COMPRESSIONE, SIM_MODE, MODALITA_SIM_COMPRESSA, stats
    
    # Carica configurazioni
    carica_fattore_compressione()
    carica_secrets()
    
    config = carica_configurazione()
    if config is None:
        print("\n❌ Nessun file di configurazione trovato!")
        print("   Esegui il wizard per crearne uno.")
        sys.exit(1)
    
    init_hardware()
    inizializza_variabili_globali()
    
    print("\n" + "☀️" * 50)
    print("      SOLAR ECLIPSE AUTOMATION SCRIPT v5.0")
    print("      Versione Modulare")
    print("☀️" * 50)
    
    # Test Telegram
    if ottieni_secrets().get("telegram", {}).get("bot_token"):
        invia_notifica_telegram("🤖 *Bot Telegram attivo*", parse_mode="Markdown")
        print("✅ Telegram: Bot connesso")
    
    # Menu principale
    while True:
        print(f"\n⚙️ Fattore compressione attuale: {FATTORE_COMPRESSIONE}x")
        print("\nOpzioni disponibili:")
        print("   [1] Avvia simulazione con compressione (test veloce)")
        print("   [2] Avvia modalità reale (usa per l'evento vero)")
        print("   [3] Wizard configurazione (crea nuovo file config)")
        print("   [4] Cambia fattore compressione")
        print("   [5] Esci")
        
        scelta = input("\nSeleziona opzione (1-5): ")
        
        if scelta == "3":
            wizard_configurazione()
            print("\n✅ Configurazione creata. Riavvia lo script.")
            input("Premi INVIO per continuare...")
            continue
        elif scelta == "4":
            nuovo = input(f"\nInserisci nuovo fattore (attuale {FATTORE_COMPRESSIONE}): ")
            if nuovo.isdigit():
                FATTORE_COMPRESSIONE = int(nuovo)
                salva_fattore_compressione()
                print(f"✅ Fattore cambiato a {FATTORE_COMPRESSIONE}x")
            else:
                print("❌ Valore non valido")
            input("\nPremi INVIO per continuare...")
            continue
        elif scelta == "5":
            invia_notifica_telegram("👋 Script terminato")
            print("Arrivederci!")
            sys.exit(0)
        break
    
    # ============================================================
    # IMPOSTAZIONE MODALITÀ
    # ============================================================
    if scelta == "1":
        MODALITA_SIM_COMPRESSA = True
        SIM_MODE = True
        print(f"\n🔧 AVVIO SIMULAZIONE CON COMPRESSIONE {FATTORE_COMPRESSIONE}x")
    else:
        MODALITA_SIM_COMPRESSA = False
        SIM_MODE = config["hardware"]["sim_mode"]
        if SIM_MODE:
            print("\n🔧 AVVIO SIMULAZIONE BASE")
        else:
            print("\n📷 AVVIO MODALITA' REALE")
    
    # Aggiorna costanti globali
    from utils import constants
    constants.SIM_MODE = SIM_MODE
    constants.MODALITA_SIM_COMPRESSA = MODALITA_SIM_COMPRESSA
    
    # Inizializza statistiche
    stats['inizio_eclisse'] = datetime.now()
    
    # Telemetria iniziale
    batteria = controlla_telemetria()
    if batteria:
        stats['batteria_inizio'] = batteria
    
    # Mostra info configurazione
    print(f"\n📋 Configurazione:")
    print(f"   Camera: {config['hardware']['marca_camera']}")
    print(f"   Modalità: {'SIMULAZIONE COMPRESSA' if MODALITA_SIM_COMPRESSA else 'REALE'}")
    if MODALITA_SIM_COMPRESSA:
        print(f"   Compressione: {FATTORE_COMPRESSIONE}x")
    elif SIM_MODE:
        print(f"   Simulazione base attiva")
    print(f"   Scatti previsti: {stats['totale_scatti_previsti']}")
    
    calcola_contatti_gps()
    
    # ============================================================
    # CHECKLIST - Solo in modalità reale (non simulazione)
    # ============================================================
    if not MODALITA_SIM_COMPRESSA and not SIM_MODE:
        print("\n" + "=" * 70)
        print("   📋 ESECUZIONE CHECKLIST PRE-ECLISSE")
        print("=" * 70)
        print(f"\n[DEBUG] CHECKLIST_ITEMS contiene {len(CHECKLIST_ITEMS)} voci:")
        for i, item in enumerate(CHECKLIST_ITEMS, 1):
            print(f"   {i}. {item}")
        print()
        run_checklist()
    else:
        print("\n🔧 Modalità simulazione attiva - Checklist saltata")
    
    # ============================================================
    # ATTESA FINALE E AVVIO
    # ============================================================
    print("\n" + "⚠️" * 40)
    if MODALITA_SIM_COMPRESSA:
        print("      AVVIO SIMULAZIONE COMPRESSA")
    elif SIM_MODE:
        print("      AVVIO SIMULAZIONE BASE")
    else:
        print("      SCRIPT PRONTO - IN ATTESA DELL'ECLISSE")
        print("      NON SPEGNERE IL COMPUTER O SCOLLEGARE LA CAMERA")
    print("⚠️" * 40)
    
    # Attesa solo in modalità reale (non simulazione)
    if not MODALITA_SIM_COMPRESSA and not SIM_MODE:
        input("\n[Premi INVIO per avviare l'acquisizione]")
    
    # ============================================================
    # ESECUZIONE PRINCIPALE
    # ============================================================
    try:
        if MODALITA_SIM_COMPRESSA:
            run_simulazione_compressa()
        else:
            run_automazione_normale()
        
        stats['fine_eclisse'] = datetime.now()
        
        batteria_fine = controlla_telemetria()
        if batteria_fine:
            stats['batteria_fine'] = batteria_fine
        
        genera_report_finale()
        
    except KeyboardInterrupt:
        log_messaggio("🚨 SCRIPT INTERROTTO", "WARN")
        invia_notifica_telegram("⚠️ Script interrotto manualmente")
        print("\n\n⚠️ Script interrotto.")
        sys.exit(0)
    except Exception as e:
        log_messaggio(f"❌ ERRORE: {e}", "ERROR")
        invia_notifica_telegram(f"❌ ERRORE CRITICO: {e}")
        stats['errori'].append(str(e))
        print(f"\n\n❌ Errore fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()