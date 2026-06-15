#!/usr/bin/env python3
"""
Gestione interfaccia utente (menu e checklist)
"""

import sys
import time
import json
from utils.logger import log_messaggio
from utils.helpers import emetti_suono
from utils.constants import SIM_MODE, CHECKLIST_ITEMS, TEST_TEMPO
from .config_manager import salva_configurazione, ottieni_config
from .hardware_manager import avvia_digicamcontrol_minimized, test_connessione_camera, imposta_tempo_scatto

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
            "Fuoco su MANUALE (MF) e bloccato?",
            "Camera su MANUALE (M)?",
            "ISO 200 e f/8 impostati?",
            "Salvataggio su SD interna?",
            "Formato RAW attivo?",
            "Stabilizzatore OFF?",
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
    return nome_file

def run_checklist():
    """Checklist pre-eclisse interattiva"""
    global CHECKLIST_ITEMS, TEST_TEMPO
    
    print("\n" + "!" * 75)
    print("      SEQUENZA DI CONNESSIONE HARDWARE")
    print("!" * 75)
    if SIM_MODE:
        print("  🔧 MODALITA' SIMULAZIONE - Skip connessione")
    else:
        print("  1. ACCENDI CAMERA")
        print("  2. COLLEGA USB")
        print("  3. digiCamControl verrà avviato (attendere 15 secondi)")
    print("!" * 75)
    
    if not SIM_MODE:
        input("\n[Premi INVIO quando camera è collegata e accesa]")
        
        # Avvia digiCamControl
        if not avvia_digicamcontrol_minimized():
            print("\n⚠️ digiCamControl non si è avviato automaticamente!")
            print("   Avvialo MANUALMENTE dal desktop e premi INVIO")
            input()
        
        # Verifica che digiCamControl sia realmente in esecuzione
        print("\n🔍 Verifica che digiCamControl sia in esecuzione...")
        time.sleep(2)
        
        # Test connessione con retry
        connesso = False
        for tentativo in range(1, 4):
            print(f"\n🔌 Tentativo {tentativo}/3 di connessione...")
            if test_connessione_camera():
                connesso = True
                break
            if tentativo < 3:
                print(f"   Riprovo tra 5 secondi...")
                time.sleep(5)
        
        if not connesso:
            print("\n" + "=" * 60)
            print("❌ CONNESSIONE CAMERA FALLITA!")
            print("=" * 60)
            print("\nVerifica manualmente:")
            print("  1. digiCamControl è APERTO?")
            print("  2. La camera è ACCESA?")
            print("  3. Il cavo USB è collegato?")
            print("  4. La camera è in modalità M (Manuale)?")
            print("  5. Hai premuto 'Connect' in digiCamControl?")
            print("\n⚠️ Dopo aver verificato, premi INVIO per riprovare")
            input()
            
            # Ultimo tentativo
            print("\n📷 Ultimo tentativo di connessione...")
            if not test_connessione_camera():
                print("\n❌ Impossibile connettersi alla camera!")
                if input("Forzare continuazione? (s/n): ").lower() != 's':
                    print("❌ Inizializzazione annullata")
                    sys.exit(1)
        
        # Test cambio tempo
        print(f"\n📷 Test impostazione tempo {TEST_TEMPO}...")
        for tentativo in range(1, 4):
            if imposta_tempo_scatto(TEST_TEMPO):
                print(f"   ✅ Test superato!")
                break
            if tentativo < 3:
                print(f"   Riprovo tra 3 secondi... (tentativo {tentativo+1}/3)")
                time.sleep(3)
        else:
            print("\n⚠️ Il comando test è stato rifiutato dopo 3 tentativi!")
            print("   Verifica che la camera sia in modalità MANUALE (M)")
            if input("Forzare continuazione? (s/n): ").lower() != 's':
                print("❌ Inizializzazione annullata")
                sys.exit(1)
    
    print("\n📋 CHECKLIST PRE-ECLISSE:")
    for i, item in enumerate(CHECKLIST_ITEMS, 1):
        input(f"  [{i}/{len(CHECKLIST_ITEMS)}] {item} [INVIO] ")
    
    print("\n✅ Checklist completata!")