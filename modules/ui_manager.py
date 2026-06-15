#!/usr/bin/env python3
"""
Gestione interfaccia utente (menu e checklist)
"""

import sys
import time
import json
from utils.logger import log_messaggio
from utils.helpers import emetti_suono
from utils.constants import SIM_MODE, TEST_TEMPO
from .hardware_manager import avvia_digicamcontrol_minimized, test_connessione_camera, imposta_tempo_scatto
from .config_manager import salva_configurazione, ottieni_config

def wizard_configurazione():
    """Wizard interattivo per creare config_eclipse.json"""
    print("\n" + "=" * 70)
    print("   🚀 WIZARD DI CONFIGURAZIONE ECLISSE")
    print("=" * 70)
    
    config = {
        "hardware": {
            "marca_camera": "CANON",
            "gui_path": r"C:\Program Files (x86)\digiCamControl\CameraControl.exe",
            "cmd_path": r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe",
            "sim_mode": False,
            "debug_mode": False
        },
        "coordinate": {
            "latitudine_dms": "43°44'08.77\"N",
            "longitudine_dms": "7°55'20.04\"W",
            "uso_calcolo_gps": False
        },
        "timing_eclisse": {
            "_data": "12 Agosto 2026",
            "p1_inizio": "19:30:00",
            "totalita_inizio": "20:27:10",
            "totalita_fine": "20:28:50",
            "p4_fine": "21:12:00"
        },
        "tempi_scatto": {
            "protuberanze": ["1/8000", "1/4000", "1/2000", "1/1000"],
            "corona": ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "0.5", "1", "2"],
            "burst": ["1/8000", "1/4000", "1/2000"],
            "parziale": ["1/2000"],
            "raffica_scatti": 3
        },
        "intervalli": {
            "ingresso_parziale_sec": 2700,
            "uscita_parziale_sec": 2700,
            "intervallo_parziale_sec": 900,
            "watchdog_interval_sec": 30
        },
        "fasi_eclisse": [
            {"nome": "PRE-PARZIALE (ingresso)", "tempo_riferimento": "p1_inizio", "durata_sec": 2700, "lista_tempi": "parziale", "usa_raffica": False, "intervallo_scatti": 900},
            {"nome": "ANELLO DIAMANTE (ingresso)", "tempo_riferimento": "totalita_inizio", "durata_sec": 5, "lista_tempi": "burst", "usa_raffica": True, "intervallo_scatti": 0},
            {"nome": "TOTALITA' - CORONA INTERNA", "tempo_riferimento": "totalita_inizio", "durata_sec": 50, "lista_tempi": "corona_interna", "usa_raffica": False, "intervallo_scatti": 0},
            {"nome": "TOTALITA' - CORONA ESTERNA", "tempo_riferimento": "totalita_inizio", "durata_sec": 50, "lista_tempi": "corona_esterna", "usa_raffica": False, "intervallo_scatti": 0},
            {"nome": "ANELLO DIAMANTE (uscita)", "tempo_riferimento": "totalita_fine", "durata_sec": 5, "lista_tempi": "burst", "usa_raffica": True, "intervallo_scatti": 0},
            {"nome": "POST-PARZIALE (uscita)", "tempo_riferimento": "totalita_fine", "durata_sec": 2700, "lista_tempi": "parziale", "usa_raffica": False, "intervallo_scatti": 900}
        ],
        "checklist_items": [
            "Filtro solare montato?",
            "Fuoco su MANUALE (MF) e bloccato col nastro?",
            "Camera su MANUALE (M)?",
            "ISO e Diaframma impostati manualmente? (ISO 200, f/8)",
            "Salvataggio SOLO su SD interna?",
            "Formato RAW attivo?",
            "Stabilizzatore immagine OFF?",
            "Autofocus DISATTIVATO?"
        ],
        "file_sistema": {
            "log_file": "eclissi_log.txt",
            "stato_file": "eclissi_stato.json",
            "watchdog_file": "watchdog_last.txt"
        },
        "parametri_camera": {
            "iso_default": 200,
            "apertura_default": 8,
            "test_tempo": "1/1000"
        }
    }
    
    nome_file = input("Nome file configurazione [config_eclipse.json]: ") or "config_eclipse.json"
    salva_configurazione(config, nome_file)
    print(f"\n✅ Configurazione salvata in {nome_file}")
    return nome_file

def run_checklist():
    """Checklist pre-eclisse interattiva"""
    global TEST_TEMPO
    
    # LEGGI DIRETTAMENTE LE VOCI DAL CONFIG
    config = ottieni_config()
    checklist_items = config.get("checklist_items", [])
    
    print("\n" + "=" * 70)
    print("   🔴🔴🔴 CHECKLIST PRE-ECLISSE OBBLIGATORIA 🔴🔴🔴")
    print("=" * 70)
    print("\n⚠️  LEGGI E CONFERMA OGNI VOCE ⚠️\n")
    
    if not checklist_items:
        print("   ⚠️ Nessuna voce nella checklist! Verifica il file config_eclipse.json")
        checklist_items = [
            "Filtro solare montato?",
            "Camera su MANUALE (M)?",
            "ISO e Diaframma impostati?",
            "Salvataggio su SD interna?"
        ]
    
    for i, item in enumerate(checklist_items, 1):
        input(f"   [{i}/{len(checklist_items)}] {item} [PREMI INVIO]")
    
    print("\n" + "-" * 70)
    print("   ✅ CHECKLIST COMPLETATA! ✅")
    print("=" * 70)
    
    print("\n" + "!" * 75)
    print("      CONFIGURAZIONE HARDWARE")
    print("!" * 75)
    print("  1. ACCENDI CAMERA")
    print("  2. COLLEGA USB")
    print("!" * 75)
    
    input("\n[Premi INVIO quando camera è collegata e accesa]")
    
    # Avvia digiCamControl
    if not avvia_digicamcontrol_minimized():
        print("\n⚠️ Impossibile avviare digiCamControl automaticamente")
        print("   Avvialo manualmente e premi INVIO")
        input()
    
    # Test connessione camera
    print("\n🔍 Test connessione camera...")
    for tentativo in range(1, 4):
        if test_connessione_camera():
            print("   ✅ Camera connessa!")
            break
        if tentativo < 3:
            print(f"   Tentativo {tentativo}/3 fallito, riprovo...")
            time.sleep(2)
    else:
        print("   ⚠️ Connessione incerta, continuo comunque...")
    
    # Test impostazione tempo
    print(f"\n📷 Test impostazione tempo {TEST_TEMPO}...")
    if imposta_tempo_scatto(TEST_TEMPO):
        print("   ✅ Test superato!")
    else:
        print("   ⚠️ Test fallito, ma continuo...")
    
    print("\n✅ Configurazione hardware completata!\n")