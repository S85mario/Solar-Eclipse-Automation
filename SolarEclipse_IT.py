#!/usr/bin/env python3
"""
Solar Eclipse Automation Script - v4.2
Per eclissi solare totale 
Con compressione temporale configurabile e persistente
"""

import os
import sys
import time
import re
import json
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# Moduli opzionali per telemetria avanzata
try:
    import psutil
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False

# ==============================================================================
# 0. CONFIGURAZIONE SIMULAZIONE (DEFAULT)
# ==============================================================================

# Fattore di compressione temporale (verrà caricato da file se esiste)
FATTORE_COMPRESSIONE = 60

# Attesa iniziale prima dell'inizio (in secondi reali)
ATTESA_INIZIALE_SEC = 10

# Modalità debug
DEBUG_MODE = False

# File per salvare la configurazione della simulazione
COMPRESSIONE_FILE = "compressione_config.json"

# ==============================================================================
# 1. VARIABILI GLOBALI
# ==============================================================================

stats = {
    'fasi_completate': 0,
    'totale_scatti_previsti': 0,
    'totale_scatti_eseguiti': 0,
    'scatti_riusciti': 0,
    'scatti_falliti': 0,
    'inizio_eclisse': None,
    'fine_eclisse': None,
    'batteria_inizio': None,
    'batteria_fine': None,
    'errori': [],
    'tempi_scatto_utilizzati': []
}

CONFIG = None
SIM_MODE = False
MARCA_CAMERA = "CANON"
CMD_PATH = ""
GUI_PATH = ""
P1_INIZIO = None
TOTALITA_INIZIO = None
TOTALITA_FINE = None
P4_FINE = None
RAFAGA_SCATTI = 3
CHECKLIST_ITEMS = []
TEST_TEMPO = "1/1000"
LOG_FILE = "eclissi_log.txt"
STATO_FILE = "eclissi_stato.json"
WATCHDOG_FILE = "watchdog_last.txt"
WATCHDOG_INTERVAL = 30
TEMPI_HDR = []
TEMPI_BURST = []
TEMPI_CORONA_INTERNA = []
TEMPI_CORONA_ESTERNA = []
TEMPI_PROTUBERANZE = []
TEMPI_CORONA = []

P1_SIM = None
C2_SIM = None
C3_SIM = None
P4_SIM = None
MODALITA_SIM_COMPRESSA = False

# ==============================================================================
# 2. FUNZIONI PER COMPRESSIONE PERSISTENTE
# ==============================================================================

def salva_fattore_compressione():
    """Salva il fattore di compressione su file"""
    try:
        with open(COMPRESSIONE_FILE, 'w') as f:
            json.dump({"fattore": FATTORE_COMPRESSIONE}, f)
    except Exception as e:
        pass

def carica_fattore_compressione():
    """Carica il fattore di compressione da file"""
    global FATTORE_COMPRESSIONE
    try:
        if os.path.exists(COMPRESSIONE_FILE):
            with open(COMPRESSIONE_FILE, 'r') as f:
                data = json.load(f)
                FATTORE_COMPRESSIONE = data.get("fattore", 60)
    except Exception as e:
        pass

# ==============================================================================
# 3. FUNZIONI BASE
# ==============================================================================

def log_messaggio(messaggio, level="INFO"):
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
    if DEBUG_MODE:
        log_messaggio(f"[DEBUG] {messaggio}")

def emetti_suono(tipo="attenzione"):
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

def stringa_a_time(time_str):
    h, m, s = map(int, time_str.split(':'))
    return datetime_time(h, m, s)

def carica_configurazione(config_file="config_SolarEclipse_IT.json"):
    if not os.path.exists(config_file):
        log_messaggio(f"File {config_file} non trovato!", "ERROR")
        return None
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        log_messaggio(f"Configurazione caricata da {config_file}")
        return config
    except Exception as e:
        log_messaggio(f"Errore caricamento: {e}", "ERROR")
        return None

def salva_stato(fase, indice):
    try:
        stato = {
            'fase': fase,
            'indice': indice,
            'timestamp': datetime.now().isoformat(),
            'ultimo_scatto': datetime.now().strftime('%H:%M:%S')
        }
        with open(STATO_FILE, 'w') as f:
            json.dump(stato, f, indent=2)
        log_debug(f"Stato salvato: {fase} - indice {indice}")
    except Exception as e:
        log_messaggio(f"Errore salvataggio stato: {e}", "WARN")

def carica_stato():
    if os.path.exists(STATO_FILE):
        try:
            with open(STATO_FILE, 'r') as f:
                stato = json.load(f)
            log_messaggio(f"Ripreso da stato: {stato.get('fase', 'inizio')}")
            return stato
        except Exception as e:
            log_messaggio(f"Errore caricamento stato: {e}", "WARN")
    return None

# ==============================================================================
# 4. FUNZIONI HARDWARE
# ==============================================================================

def controlla_telemetria():
    if HAS_TELEMETRY:
        try:
            batteria = psutil.sensors_battery()
            if batteria:
                if not batteria.power_plugged and batteria.percent < 20:
                    log_messaggio(f"⚠️ BATTERIA AL {batteria.percent}% - NON IN CARICA!", "WARN")
                    emetti_suono("attenzione")
                elif not batteria.power_plugged and batteria.percent < 10:
                    log_messaggio(f"🚨 CRITICO: BATTERIA AL {batteria.percent}%!", "ERROR")
                    emetti_suono("critico")
                return batteria.percent
        except Exception as e:
            log_debug(f"Errore telemetria: {e}")
    return None

def converti_tempo_in_secondi(stringa_tempo):
    try:
        if "/" in stringa_tempo:
            num, denom = stringa_tempo.split("/")
            return float(num) / float(denom)
        return float(stringa_tempo)
    except:
        return 0.1

def calc_pausa(tempo_scatto):
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

def imposta_tempo_scatto(tempo, max_tentativi=3):
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
        except subprocess.TimeoutExpired:
            log_messaggio(f"Timeout cambio tempo al tentativo {tentativo}", "WARN")
        except Exception as e:
            log_messaggio(f"Errore USB al tentativo {tentativo}: {e}", "WARN")
        time.sleep(0.2)
    log_messaggio(f"❌ CRITICO: Cambio tempo fallito ({tempo})!", "ERROR")
    emetti_suono("critico")
    return False

def scatta_foto(etichetta, max_tentativi=3):
    global stats
    if SIM_MODE:
        log_messaggio(f"[SIM] 📸 Scatto: {etichetta}")
        stats['scatti_riusciti'] += 1
        stats['totale_scatti_eseguiti'] += 1
        parti = etichetta.split('_')
        if len(parti) >= 2:
            stats['tempi_scatto_utilizzati'].append(parti[1])
        time.sleep(0.05)
        return True
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "capture"], 
                                      capture_output=True, text=True, timeout=10)
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                stats['scatti_riusciti'] += 1
                stats['totale_scatti_eseguiti'] += 1
                parti = etichetta.split('_')
                if len(parti) >= 2:
                    stats['tempi_scatto_utilizzati'].append(parti[1])
                return True
        except subprocess.TimeoutExpired:
            log_messaggio(f"Timeout scatto al tentativo {tentativo}", "WARN")
        except Exception as e:
            log_messaggio(f"Errore otturatore al tentativo {tentativo}: {e}", "WARN")
        time.sleep(0.2)
    log_messaggio(f"❌ CRITICO: Scatto fallito per {etichetta}!", "ERROR")
    stats['scatti_falliti'] += 1
    stats['totale_scatti_eseguiti'] += 1
    stats['errori'].append(f"Scatto fallito: {etichetta}")
    emetti_suono("critico")
    return False

def watchdog_reset():
    try:
        with open(WATCHDOG_FILE, "w") as f:
            f.write(datetime.now().isoformat())
        log_debug("Watchdog resettato")
    except Exception as e:
        log_debug(f"Errore watchdog: {e}")

# ==============================================================================
# 5. FUNZIONI DI TEMPORIZZAZIONE
# ==============================================================================

def attesa_con_compressione(tempo_target, nome_fase=""):
    now = datetime.now()
    if now >= tempo_target:
        log_messaggio(f"🎯 {nome_fase} raggiunto!")
        return
    wait_sec = (tempo_target - now).total_seconds()
    if wait_sec <= 0:
        return
    if FATTORE_COMPRESSIONE == 1:
        log_messaggio(f"⏳ Attesa {wait_sec/60:.1f} minuti fino a {nome_fase}")
    else:
        tempo_reale = wait_sec * FATTORE_COMPRESSIONE
        log_messaggio(f"⏳ Attesa {wait_sec:.1f} sec reali ({tempo_reale/60:.1f} min simulati) fino a {nome_fase}")
    while wait_sec > 0:
        sleep_time = min(1, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        if wait_sec > 0:
            if FATTORE_COMPRESSIONE == 1:
                print(f"\r   Ancora {wait_sec/60:.1f} min...", end='')
            else:
                print(f"\r   Ancora {wait_sec:.1f} sec reali...", end='')
    print()
    log_messaggio(f"🎯 {nome_fase} raggiunto!")

def attesa_fino_a(orario_target, nome_fase=""):
    now = datetime.now()
    target = datetime.combine(now.date(), orario_target)
    if now > target:
        target += timedelta(days=1)
    wait_sec = (target - now).total_seconds()
    if wait_sec <= 0:
        log_messaggio(f"⚠️ Orario {orario_target} già passato per {nome_fase}!", "WARN")
        return
    log_messaggio(f"⏳ Attesa {wait_sec/60:.1f} minuti fino a {nome_fase} ({orario_target})")
    last_watchdog = time.time()
    while wait_sec > 0:
        sleep_time = min(WATCHDOG_INTERVAL, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        if time.time() - last_watchdog >= WATCHDOG_INTERVAL:
            watchdog_reset()
            last_watchdog = time.time()
            controlla_telemetria()
        if wait_sec > 0:
            print(f"\r⏳ Ancora {wait_sec:.0f} sec per {nome_fase}...", end='')
    print()
    log_messaggio(f"🎯 Ora {nome_fase} raggiunta!")

def calcola_contatti_gps():
    lat_dms = CONFIG["coordinate"]["latitudine_dms"]
    lon_dms = CONFIG["coordinate"]["longitudine_dms"]
    print(f"\n[GEOTARGET] Coordinate caricate: {lat_dms} , {lon_dms}")
    print(f"\n📅 ORARI ECLISSE ({CONFIG['timing_eclisse']['_data']}):")
    print(f"   P1 (Inizio parziale):   {P1_INIZIO}")
    print(f"   C2 (Inizio totalità):   {TOTALITA_INIZIO}")
    print(f"   C3 (Fine totalità):     {TOTALITA_FINE}")
    print(f"   P4 (Fine parziale):     {P4_FINE}")

# ==============================================================================
# 6. INIZIALIZZAZIONE SIMULAZIONE
# ==============================================================================

def inizializza_simulazione_compressa():
    """Inizializza i timing per la simulazione compressa"""
    global P1_SIM, C2_SIM, C3_SIM, P4_SIM, MODALITA_SIM_COMPRESSA, FATTORE_COMPRESSIONE
    
    MODALITA_SIM_COMPRESSA = True
    fattore = FATTORE_COMPRESSIONE
    
    log_messaggio(f"🔧 SIMULAZIONE CON COMPRESSIONE {fattore}x")
    
    if fattore == 60:
        log_messaggio(f"   1 minuto reale = 1 ora eclisse")
    elif fattore == 120:
        log_messaggio(f"   30 secondi reali = 1 ora eclisse")
    elif fattore == 30:
        log_messaggio(f"   2 minuti reali = 1 ora eclisse")
    elif fattore == 1:
        log_messaggio(f"   Velocità reale")
    
    now = datetime.now()
    
    def calcola_tempo_simulato(ora_reale):
        target_reale = datetime(now.year, now.month, now.day,
                               ora_reale.hour, ora_reale.minute, ora_reale.second)
        if target_reale < now:
            target_reale += timedelta(days=1)
        durata_reale = (target_reale - now).total_seconds()
        durata_compressa = durata_reale / fattore
        return now + timedelta(seconds=durata_compressa)
    
    P1_SIM = calcola_tempo_simulato(P1_INIZIO)
    C2_SIM = calcola_tempo_simulato(TOTALITA_INIZIO)
    C3_SIM = calcola_tempo_simulato(TOTALITA_FINE)
    P4_SIM = calcola_tempo_simulato(P4_FINE)
    
    log_messaggio(f"\n📅 TIMING SIMULAZIONE (tempo reale):")
    log_messaggio(f"   P1: {P1_SIM.strftime('%H:%M:%S')} (reale {P1_INIZIO})")
    log_messaggio(f"   C2: {C2_SIM.strftime('%H:%M:%S')} (reale {TOTALITA_INIZIO})")
    log_messaggio(f"   C3: {C3_SIM.strftime('%H:%M:%S')} (reale {TOTALITA_FINE})")
    log_messaggio(f"   P4: {P4_SIM.strftime('%H:%M:%S')} (reale {P4_FINE})")
    
    if ATTESA_INIZIALE_SEC > 0:
        log_messaggio(f"\n⏳ Attesa iniziale di {ATTESA_INIZIALE_SEC} secondi...")
        for i in range(ATTESA_INIZIALE_SEC, 0, -1):
            print(f"\r   Partenza tra {i} secondi...", end='')
            time.sleep(1)
        print("\r   ✅ Via!                      ")

# ==============================================================================
# 7. SEQUENZA SCATTI
# ==============================================================================

def ottieni_lista_tempi(nome_lista):
    mappa_liste = {
        "hdr": TEMPI_HDR,
        "burst": TEMPI_BURST,
        "corona_interna": TEMPI_CORONA_INTERNA,
        "corona_esterna": TEMPI_CORONA_ESTERNA,
        "protuberanze": TEMPI_PROTUBERANZE,
        "corona": TEMPI_CORONA
    }
    return mappa_liste.get(nome_lista, TEMPI_HDR)

def esegui_sequenza_scatti(nome_fase, lista_tempi, indice_partenza=0, usa_raffica=True):
    global stats
    if indice_partenza >= len(lista_tempi):
        log_messaggio(f"Fase {nome_fase} già completata", "INFO")
        return len(lista_tempi) - 1
    log_messaggio(f"🎬 INIZIO {nome_fase} - {len(lista_tempi)-indice_partenza} esposizioni rimaste")
    for i, tempo in enumerate(lista_tempi[indice_partenza:], indice_partenza):
        if MODALITA_SIM_COMPRESSA:
            if datetime.now() > P4_SIM:
                log_messaggio(f"📅 Eclisse simulata terminata, interrompo {nome_fase}")
                return i - 1
        else:
            if datetime.now().time() > P4_FINE:
                log_messaggio(f"📅 Eclisse terminata, interrompo {nome_fase}")
                return i - 1
        if usa_raffica:
            for scatto in range(RAFAGA_SCATTI):
                etichetta = f"{nome_fase}_{tempo}_shot{scatto+1}"
                if imposta_tempo_scatto(tempo):
                    if scatta_foto(etichetta):
                        log_messaggio(f"📸 {etichetta}")
                        controlla_telemetria()
                    time.sleep(0.3)
        else:
            etichetta = f"{nome_fase}_{tempo}"
            if imposta_tempo_scatto(tempo):
                if scatta_foto(etichetta):
                    log_messaggio(f"📸 {etichetta}")
                    controlla_telemetria()
        salva_stato(nome_fase, i + 1)
        if i < len(lista_tempi) - 1:
            pausa = calc_pausa(tempo)
            log_debug(f"Pausa {pausa:.1f}s prima prossimo scatto")
            time.sleep(pausa)
    log_messaggio(f"✅ COMPLETATA {nome_fase}")
    stats['fasi_completate'] += 1
    return len(lista_tempi) - 1

# ==============================================================================
# 8. MOTORE AUTOMAZIONE
# ==============================================================================

def run_automazione_normale():
    global stats
    log_messaggio("🚀 MOTORE ECLISSE ATTIVO - MODALITA' REALE")
    stato = carica_stato()
    fase_ripresa = stato.get('fase') if stato else None
    indice_ripresa = stato.get('indice', 0) if stato else 0
    fasi_config = CONFIG["fasi_eclisse"]
    fasi = []
    for fase in fasi_config:
        tempo_riferimento = fase["tempo_riferimento"]
        if tempo_riferimento == "p1_inizio":
            orario = P1_INIZIO
        elif tempo_riferimento == "totalita_inizio":
            orario = TOTALITA_INIZIO
        elif tempo_riferimento == "totalita_fine":
            orario = TOTALITA_FINE
        else:
            orario = P1_INIZIO
        lista_tempi = ottieni_lista_tempi(fase["lista_tempi"])
        fasi.append((fase["nome"], orario, fase["durata_sec"], lista_tempi, fase["usa_raffica"]))
    for nome_fase, tempo_inizio, durata_sec, tempi_scatto, usa_raffica in fasi:
        if fase_ripresa and fase_ripresa != nome_fase:
            nomi_fasi = [f[0] for f in fasi]
            if fase_ripresa in nomi_fasi:
                indice_fase_corrente = nomi_fasi.index(nome_fase)
                indice_fase_ripresa = nomi_fasi.index(fase_ripresa)
                if indice_fase_corrente < indice_fase_ripresa:
                    log_messaggio(f"⏭️ Salto fase già completata: {nome_fase}")
                    continue
        if fase_ripresa == nome_fase:
            indice_partenza = indice_ripresa
            fase_ripresa = None
            log_messaggio(f"🔄 Riprendo {nome_fase} dall'indice {indice_partenza}")
        else:
            indice_partenza = 0
            attesa_fino_a(tempo_inizio, nome_fase)
        ultimo_indice = esegui_sequenza_scatti(nome_fase, tempi_scatto, indice_partenza, usa_raffica)
        if ultimo_indice >= len(tempi_scatto) - 1:
            if os.path.exists(STATO_FILE):
                os.remove(STATO_FILE)
                log_debug("Stato cancellato - fase completata")
    log_messaggio("🎉 ECLISSE COMPLETATA! 🎉")
    emetti_suono("completamento")

def run_simulazione_compressa():
    global stats
    log_messaggio("🚀 SIMULAZIONE ECLISSE CON TEMPO COMPRESSO")
    inizializza_simulazione_compressa()
    fasi = [
        ("🌑 PRE-PARZIALE (ingresso)", P1_SIM, TEMPI_HDR, True),
        ("💍 ANELLO DIAMANTE (ingresso)", C2_SIM, TEMPI_BURST, True),
        ("🌞 TOTALITA' - CORONA INTERNA", C2_SIM, TEMPI_CORONA_INTERNA, False),
        ("🌞 TOTALITA' - CORONA ESTERNA", C2_SIM, TEMPI_CORONA_ESTERNA, False),
        ("💍 ANELLO DIAMANTE (uscita)", C3_SIM, TEMPI_BURST, True),
        ("🌑 POST-PARZIALE (uscita)", C3_SIM, TEMPI_HDR, True),
    ]
    for nome_fase, tempo_inizio, lista_tempi, usa_raffica in fasi:
        if datetime.now() > P4_SIM:
            break
        attesa_con_compressione(tempo_inizio, nome_fase)
        log_messaggio(f"🎬 INIZIO {nome_fase}")
        for tempo in lista_tempi:
            if datetime.now() > P4_SIM:
                break
            if usa_raffica:
                for scatto in range(RAFAGA_SCATTI):
                    etichetta = f"[SIM] {nome_fase}_{tempo}_shot{scatto+1}"
                    if scatta_foto(etichetta):
                        log_messaggio(f"📸 {etichetta}")
                    time.sleep(0.1)
            else:
                etichetta = f"[SIM] {nome_fase}_{tempo}"
                if scatta_foto(etichetta):
                    log_messaggio(f"📸 {etichetta}")
            stats['tempi_scatto_utilizzati'].append(tempo)
            time.sleep(calc_pausa(tempo))
        log_messaggio(f"✅ COMPLETATA {nome_fase}")
        stats['fasi_completate'] += 1
    log_messaggio("🎉 SIMULAZIONE ECLISSE COMPLETATA! 🎉")
    emetti_suono("completamento")

# ==============================================================================
# 9. REPORT FINALE
# ==============================================================================

def genera_report_finale():
    global stats
    print("\n" + "=" * 70)
    print("   📊 GENERAZIONE REPORT FINALE")
    print("=" * 70)
    durata_totale = None
    if stats['inizio_eclisse'] and stats['fine_eclisse']:
        durata_totale = (stats['fine_eclisse'] - stats['inizio_eclisse']).total_seconds() / 60
    if stats['totale_scatti_eseguiti'] > 0:
        percentuale_successo = (stats['scatti_riusciti'] / stats['totale_scatti_eseguiti']) * 100
    else:
        percentuale_successo = 0
    errori_text = "   ✅ Nessun errore rilevato"
    if stats['errori']:
        errori_lista = '\n'.join([f'   • {e[:100]}' for e in stats['errori'][:5]])
        errori_text = errori_lista
        if len(stats['errori']) > 5:
            errori_text += f'\n   ... e altri {len(stats["errori"]) - 5}'
    tempi_unici = list(dict.fromkeys(stats['tempi_scatto_utilizzati']))
    tempi_text = ', '.join(tempi_unici[:10])
    if len(tempi_unici) > 10:
        tempi_text += f'... e altri {len(tempi_unici) - 10}'
    report = f"""
{'=' * 70}
   REPORT ECLISSE SOLARE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 70}

📅 INFORMAZIONI GENERALI:
   Data eclisse: {CONFIG['timing_eclisse']['_data']}
   Località: {CONFIG['coordinate']['latitudine_dms']}, {CONFIG['coordinate']['longitudine_dms']}
   Camera: {CONFIG['hardware']['marca_camera']}
   Modalità: {'SIMULAZIONE COMPRESSA' if MODALITA_SIM_COMPRESSA else 'REALE'}
   Fattore compressione: {f'{FATTORE_COMPRESSIONE}x' if MODALITA_SIM_COMPRESSA else 'N/A'}

{'-' * 70}

⏰ TIMING ECLISSE:
   P1 (Inizio parziale):   {P1_INIZIO}
   C2 (Inizio totalità):   {TOTALITA_INIZIO}
   C3 (Fine totalità):     {TOTALITA_FINE}
   P4 (Fine parziale):     {P4_FINE}
   
   Inizio script:          {stats['inizio_eclisse'].strftime('%H:%M:%S') if stats['inizio_eclisse'] else 'N/D'}
   Fine script:            {stats['fine_eclisse'].strftime('%H:%M:%S') if stats['fine_eclisse'] else 'N/D'}
   Durata totale:          {f'{durata_totale:.1f} minuti' if durata_totale else 'N/D'}

{'-' * 70}

📸 STATISTICHE SCATTI:
   Fasi completate:        {stats['fasi_completate']}/{len(CONFIG['fasi_eclisse'])}
   Scatti previsti:        {stats['totale_scatti_previsti']}
   Scatti eseguiti:        {stats['totale_scatti_eseguiti']}
   Scatti riusciti:        {stats['scatti_riusciti']}
   Scatti falliti:         {stats['scatti_falliti']}
   Successo:               {percentuale_successo:.1f}%

{'-' * 70}

🔋 BATTERIA:
   Batteria inizio:        {stats['batteria_inizio']}%
   Batteria fine:          {stats['batteria_fine']}%
   Consumo:                {stats['batteria_inizio'] - stats['batteria_fine'] if stats['batteria_inizio'] and stats['batteria_fine'] else 'N/D'}%

{'-' * 70}

🎬 TEMPI SCATTO UTILIZZATI:
   {tempi_text}

{'-' * 70}

⚠️ ERRORI RILEVATI:
   {errori_text}

{'-' * 70}

{'=' * 70}
   Report generato automaticamente da Solar Eclipse Script v4.2
{'=' * 70}
"""
    report_file = f"report_eclisse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ Report salvato in: {report_file}")
    print(report)
    return report_file

# ==============================================================================
# 10. CHECKLIST
# ==============================================================================

def avvia_digicamcontrol():
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

def verifica_camera_reale():
    """Verifica se la camera è VERAMENTE connessa e risponde"""
    if SIM_MODE:
        return True
    
    log_messaggio("🔍 Verifica camera reale...")
    
    # Salva il tempo corrente
    try:
        risultato = subprocess.run([CMD_PATH, "/c", "get", "shutterspeed"], 
                                 capture_output=True, text=True, timeout=3)
        tempo_originale = risultato.stdout.strip()
        log_messaggio(f"   Tempo attuale: {tempo_originale}")
    except:
        tempo_originale = "1/1000"
    
    # Prova a cambiare tempo
    test_tempo = "1/8000" if tempo_originale != "1/8000" else "1/4000"
    
    try:
        # Imposta nuovo tempo
        subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", test_tempo], 
                      capture_output=True, timeout=3)
        time.sleep(0.5)
        
        # Leggi per verificare
        risultato = subprocess.run([CMD_PATH, "/c", "get", "shutterspeed"], 
                                 capture_output=True, text=True, timeout=3)
        
        if test_tempo in risultato.stdout:
            log_messaggio("✅ Camera VERAMENTE connessa!")
            # Ripristina tempo originale
            subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", tempo_originale], 
                          capture_output=True, timeout=3)
            return True
        else:
            log_messaggio("❌ Camera NON connessa!", "ERROR")
            return False
            
    except Exception as e:
        log_messaggio(f"❌ Errore: camera non risponde - {e}", "ERROR")
        return False

def run_checklist():
    global CHECKLIST_ITEMS, TEST_TEMPO
    
    print("\n" + "!" * 75)
    print("      SEQUENZA DI CONNESSIONE HARDWARE")
    print("!" * 75)
    
    if SIM_MODE:
        print("  🔧 MODALITA' SIMULAZIONE - Skip connessione")
    else:
        print("  1. ACCENDI CAMERA")
        print("  2. COLLEGA USB")
        print("  3. AVVIA digiCamControl (se non parte da solo)")
    print("!" * 75)
    
    if not SIM_MODE:
        input("\n[Premi INVIO quando camera è collegata e accesa]")
        
        # Avvia digiCamControl se necessario
        if not avvia_digicamcontrol():
            print("\n⚠️ digiCamControl non trovato!")
            print("   Avvialo manualmente e premi INVIO")
            input()
        
        # Test camera REALE
        if not verifica_camera_reale():
            print("\n❌ Camera non rilevata!")
            print("   Verifica:")
            print("   1. La camera è ACCESA?")
            print("   2. Il cavo USB è collegato?")
            print("   3. digiCamControl è aperto?")
            print("   4. La camera è in modalità M (Manuale)?")
            
            if input("\nForzare continuazione? (s/n): ").lower() != 's':
                print("❌ Inizializzazione annullata")
                sys.exit(1)
        
        # Test impostazione tempo
        if not imposta_tempo_scatto(TEST_TEMPO):
            print("\n⚠️ Impossibile impostare il tempo di scatto!")
            print("   Verifica che la camera sia in modalità MANUALE (M)")
            if input("Forzare continuazione? (s/n): ").lower() != 's':
                print("❌ Inizializzazione annullata")
                sys.exit(1)
    
    print("\n📋 CHECKLIST PRE-ECLISSE:")
    for i, item in enumerate(CHECKLIST_ITEMS, 1):
        input(f"  [{i}/{len(CHECKLIST_ITEMS)}] {item} [INVIO] ")
    
    print("\n✅ Checklist completata!")

# ==============================================================================
# 11. WIZARD CONFIGURAZIONE
# ==============================================================================

def wizard_configurazione():
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
            "raffica_scatti": 3
        },
        "intervalli": {
            "ingresso_parziale_sec": 1080,
            "uscita_parziale_sec": 690,
            "watchdog_interval_sec": 30
        },
        "fasi_eclisse": [
            {"nome": "PRE-PARZIALE (ingresso)", "tempo_riferimento": "p1_inizio", "durata_sec": 1080, "lista_tempi": "hdr", "usa_raffica": True},
            {"nome": "ANELLO DIAMANTE (ingresso)", "tempo_riferimento": "totalita_inizio", "durata_sec": 5, "lista_tempi": "burst", "usa_raffica": True},
            {"nome": "TOTALITA' - CORONA INTERNA", "tempo_riferimento": "totalita_inizio", "durata_sec": 50, "lista_tempi": "corona_interna", "usa_raffica": False},
            {"nome": "TOTALITA' - CORONA ESTERNA", "tempo_riferimento": "totalita_inizio", "durata_sec": 50, "lista_tempi": "corona_esterna", "usa_raffica": False},
            {"nome": "ANELLO DIAMANTE (uscita)", "tempo_riferimento": "totalita_fine", "durata_sec": 5, "lista_tempi": "burst", "usa_raffica": True},
            {"nome": "POST-PARZIALE (uscita)", "tempo_riferimento": "totalita_fine", "durata_sec": 690, "lista_tempi": "hdr", "usa_raffica": True}
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
    with open(nome_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Configurazione salvata in {nome_file}")
    return nome_file

# ==============================================================================
# 12. MAIN
# ==============================================================================

def main():
    global CONFIG, SIM_MODE, CMD_PATH, GUI_PATH
    global P1_INIZIO, TOTALITA_INIZIO, TOTALITA_FINE, P4_FINE
    global TEMPI_HDR, TEMPI_BURST, TEMPI_CORONA_INTERNA, TEMPI_CORONA_ESTERNA
    global TEMPI_PROTUBERANZE, TEMPI_CORONA, RAFAGA_SCATTI, CHECKLIST_ITEMS, TEST_TEMPO
    global LOG_FILE, STATO_FILE, WATCHDOG_FILE, WATCHDOG_INTERVAL
    global stats, MODALITA_SIM_COMPRESSA, FATTORE_COMPRESSIONE
    
    # Carica il fattore di compressione salvato
    carica_fattore_compressione()
    
    print("\n" + "☀️" * 50)
    print("      SOLAR ECLIPSE AUTOMATION SCRIPT v4.2")
    print("      Con compressione temporale configurabile")
    print("☀️" * 50)
    
    while True:  # Loop per tornare al menu dopo le operazioni
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
            print("\n✅ Configurazione creata. Torna al menu principale.")
            input("Premi INVIO per continuare...")
            continue
        
        elif scelta == "4":
            print(f"\n🔧 Fattore compressione attuale: {FATTORE_COMPRESSIONE}x")
            print("   Valori consigliati:")
            print("      1  = velocità reale (per evento vero)")
            print("      30 = 2 minuti reali = 1 ora eclisse")
            print("      60 = 1 minuto reale = 1 ora eclisse (default)")
            print("      120 = 30 secondi reali = 1 ora eclisse")
            print("      300 = 12 secondi reali = 1 ora eclisse (super veloce)")
            
            nuovo = input(f"\nInserisci nuovo fattore (1-1000): ")
            if nuovo.isdigit():
                vecchio = FATTORE_COMPRESSIONE
                FATTORE_COMPRESSIONE = int(nuovo)
                salva_fattore_compressione()
                print(f"✅ Fattore cambiato da {vecchio}x a {FATTORE_COMPRESSIONE}x")
                print("   Il nuovo valore verrà usato nella prossima simulazione.")
            else:
                print("❌ Valore non valido")
            
            input("\nPremi INVIO per continuare...")
            continue
        
        elif scelta == "5":
            print("Arrivederci!")
            sys.exit(0)
        
        # Opzione 1 o 2: avvia la simulazione/realtà
        break
    
    # Carica configurazione
    CONFIG = carica_configurazione()
    if CONFIG is None:
        print("\n❌ Nessun file di configurazione trovato!")
        print("   Esegui l'opzione 3 per crearne uno.")
        sys.exit(1)
    
    # Imposta modalità
    if scelta == "1":
        MODALITA_SIM_COMPRESSA = True
        SIM_MODE = True
        print(f"\n🔧 AVVIO SIMULAZIONE CON COMPRESSIONE {FATTORE_COMPRESSIONE}x")
    else:
        MODALITA_SIM_COMPRESSA = False
        SIM_MODE = CONFIG["hardware"]["sim_mode"]
        print("\n📷 AVVIO MODALITA' REALE")
    
    # Estrai configurazione
    MARCA_CAMERA = CONFIG["hardware"]["marca_camera"]
    CMD_PATH = CONFIG["hardware"]["cmd_path"]
    GUI_PATH = CONFIG["hardware"]["gui_path"]
    
    P1_INIZIO = stringa_a_time(CONFIG["timing_eclisse"]["p1_inizio"])
    TOTALITA_INIZIO = stringa_a_time(CONFIG["timing_eclisse"]["totalita_inizio"])
    TOTALITA_FINE = stringa_a_time(CONFIG["timing_eclisse"]["totalita_fine"])
    P4_FINE = stringa_a_time(CONFIG["timing_eclisse"]["p4_fine"])
    
    TEMPI_PROTUBERANZE = CONFIG["tempi_scatto"]["protuberanze"]
    TEMPI_CORONA = CONFIG["tempi_scatto"]["corona"]
    TEMPI_BURST = CONFIG["tempi_scatto"]["burst"]
    TEMPI_HDR = TEMPI_PROTUBERANZE + TEMPI_CORONA
    TEMPI_CORONA_INTERNA = TEMPI_CORONA[:6]
    TEMPI_CORONA_ESTERNA = TEMPI_CORONA[6:]
    RAFAGA_SCATTI = CONFIG["tempi_scatto"]["raffica_scatti"]
    
    CHECKLIST_ITEMS = CONFIG["checklist_items"]
    TEST_TEMPO = CONFIG["parametri_camera"]["test_tempo"]
    
    LOG_FILE = CONFIG["file_sistema"]["log_file"]
    STATO_FILE = CONFIG["file_sistema"]["stato_file"]
    WATCHDOG_FILE = CONFIG["file_sistema"]["watchdog_file"]
    WATCHDOG_INTERVAL = CONFIG["intervalli"]["watchdog_interval_sec"]
    
    # Inizializza statistiche
    stats['inizio_eclisse'] = datetime.now()
    stats['totale_scatti_previsti'] = sum([len(f["lista_tempi"]) * (3 if f["usa_raffica"] else 1) 
                                            for f in CONFIG["fasi_eclisse"]])
    
    # Telemetria iniziale
    batteria = controlla_telemetria()
    if batteria:
        stats['batteria_inizio'] = batteria
    
    # Mostra info
    print(f"\n📋 Configurazione:")
    print(f"   Camera: {MARCA_CAMERA}")
    print(f"   Modalità: {'SIMULAZIONE COMPRESSA' if MODALITA_SIM_COMPRESSA else 'REALE'}")
    if MODALITA_SIM_COMPRESSA:
        print(f"   Compressione: {FATTORE_COMPRESSIONE}x")
    print(f"   Scatti previsti: {stats['totale_scatti_previsti']}")
    
    calcola_contatti_gps()
    
    if not MODALITA_SIM_COMPRESSA:
        run_checklist()
    
    print("\n" + "⚠️" * 40)
    if MODALITA_SIM_COMPRESSA:
        print("      AVVIO SIMULAZIONE COMPRESSA")
    else:
        print("      SCRIPT PRONTO - IN ATTESA DELL'ECLISSE")
        print("      NON SPEGNERE IL COMPUTER O SCOLLEGARE LA CAMERA")
    print("⚠️" * 40)
    
    if not MODALITA_SIM_COMPRESSA and not SIM_MODE:
        input("\n[Premi INVIO per avviare]")
    
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
        print("\n\n⚠️ Script interrotto.")
        sys.exit(0)
    except Exception as e:
        log_messaggio(f"❌ ERRORE: {e}", "ERROR")
        stats['errori'].append(str(e))
        print(f"\n\n❌ Errore fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()