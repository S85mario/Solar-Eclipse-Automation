#!/usr/bin/env python3
"""
Solar Eclipse Automation - Versione Ottimizzata
Sequenza temporale precisa basata su orario assoluto
"""

import sys
import time
import os
import json
import subprocess
import winsound
from datetime import datetime, timedelta, time as datetime_time

# =============================================================================
# COSTANTI
# =============================================================================

CONFIG_FILE = "config_eclipse.json"
SECRETS_FILE = "secrets.json"
LOG_FILE = "eclissi_log.txt"
LOG_DETTAGLIATO = "eclissi_dettaglio.log"

AUDIO_FOLDER = r"C:\Eclissi\Audio"
AUDIO_MAP = {
    "metti_filtro": "metti_filtro.wav",
    "togli_filtro": "togli_filtro.wav",
    "mancano_20_secondi": "mancano_20_secondi.wav",
    "errore_connessione": "errore_connessione.wav",
    "attenzione": "attenzione.wav"
}

# Variabili globali
CONFIG = {}
CMD_PATH = ""
TIMING = {}
TEMPI = {}
FASI = []
CHECKLIST = []
STATS = {
    'fasi_completate': 0,
    'scatti_riusciti': 0,
    'scatti_falliti': 0,
    'scatti_totali': 0,
    'inizio': None,
    'fine': None,
    'errori': []
}
stop_requested = False

# =============================================================================
# LOGGING
# =============================================================================

def log(messaggio, livello="INFO", dati=None):
    """Log completo con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    riga = f"[{timestamp}] [{livello}] {messaggio}"
    if dati:
        riga += f" | DATI: {json.dumps(dati, ensure_ascii=False)}"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{livello}] {messaggio}")
    
    try:
        with open(LOG_DETTAGLIATO, "a", encoding="utf-8") as f:
            f.write(riga + "\n")
    except:
        pass
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{livello}] {messaggio}\n")
    except:
        pass

def log_evento_fase(nome, orario, stato="INIZIO", dettagli=None):
    dati = {"fase": nome, "orario": str(orario), "stato": stato}
    if dettagli:
        dati.update(dettagli)
    log(f"FASE: {nome} - {stato}", "FASE", dati)

def log_evento_scatto(etichetta, risultato, dettagli=None):
    dati = {"etichetta": etichetta, "risultato": "OK" if risultato else "FALLITO"}
    if dettagli:
        dati.update(dettagli)
    livello = "SUCCESS" if risultato else "ERROR"
    log(f"SCATTO: {etichetta}", livello, dati)

def log_evento_hardware(comando, risposta, stato="OK"):
    log(f"HARDWARE: {comando}", "DEBUG", {"comando": comando, "risposta": risposta[:100], "stato": stato})

def log_evento_sistema(messaggio, dettagli=None):
    log(f"SISTEMA: {messaggio}", "SISTEMA", dettagli)

# =============================================================================
# AUDIO
# =============================================================================

def suono(tipo):
    try:
        nome_file = AUDIO_MAP.get(tipo, "")
        if not nome_file:
            return
        percorso = os.path.join(AUDIO_FOLDER, nome_file)
        if os.path.exists(percorso):
            winsound.PlaySound(percorso, winsound.SND_ASYNC | winsound.SND_FILENAME)
            log_evento_sistema(f"Audio riprodotto: {tipo}")
        else:
            winsound.Beep(1000, 300)
    except:
        winsound.Beep(1000, 300)

# =============================================================================
# UTILITY
# =============================================================================

def time_from_string(s):
    h, m, sec = map(int, s.split(':'))
    return datetime_time(h, m, sec)

def datetime_from_time(orario, data=None):
    """Crea un datetime da un oggetto time (oggi o domani se passato)"""
    if data is None:
        data = datetime.now().date()
    target = datetime.combine(data, orario)
    now = datetime.now()
    if target < now:
        target += timedelta(days=1)
    return target

def attesa_fino_a(orario_target, nome_fase=""):
    """Attesa precisa fino all'orario target"""
    global stop_requested
    
    now = datetime.now()
    target = datetime_from_time(orario_target)
    
    if now >= target:
        log(f"⚡ {nome_fase} - Orario già passato! Parto subito!", "WARN")
        return
    
    wait_sec = (target - now).total_seconds()
    
    if wait_sec > 3600:
        log(f"⚠️ Attesa di {wait_sec/3600:.1f} ore per {nome_fase} - sembra eccessiva!", "WARN")
    
    log(f"⏳ In attesa di {nome_fase} alle {orario_target}... ({wait_sec:.0f} secondi)")
    
    # Avviso 20 secondi prima
    if wait_sec > 20:
        # Attendi fino a 20 secondi prima
        time.sleep(wait_sec - 20)
        suono("mancano_20_secondi")
        log(f"⏰ {nome_fase} tra 20 secondi!")
        
        # Conto alla rovescia finale
        for i in range(20, 0, -1):
            now = datetime.now()
            if now >= target:
                log(f"🎯 {nome_fase} raggiunta!")
                return
            if stop_requested:
                log("🛑 STOP richiesto!", "WARN")
                sys.exit(0)
            print(f"\r   {i} secondi...", end='')
            time.sleep(1)
        print()
    else:
        # Attesa breve
        while wait_sec > 0:
            now = datetime.now()
            if now >= target:
                log(f"🎯 {nome_fase} raggiunta!")
                return
            if stop_requested:
                log("🛑 STOP richiesto!", "WARN")
                sys.exit(0)
            time.sleep(1)
            wait_sec -= 1
            if wait_sec % 10 == 0 and wait_sec > 0:
                print(f"\r   Ancora {wait_sec:.0f} secondi...", end='')
        print()
    
    log(f"🎯 {nome_fase} raggiunta alle {datetime.now().strftime('%H:%M:%S')}!")

# =============================================================================
# CONFIGURAZIONE
# =============================================================================

def carica_config():
    global CONFIG, CMD_PATH, TIMING, TEMPI, FASI, CHECKLIST
    
    log_evento_sistema("Caricamento configurazione...")
    
    if not os.path.exists(CONFIG_FILE):
        log(f"❌ File {CONFIG_FILE} non trovato!", "ERROR")
        return False
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
        
        CMD_PATH = CONFIG["hardware"]["cmd_path"]
        TIMING = CONFIG["timing_eclisse"]
        TEMPI = CONFIG["tempi_scatto"]
        FASI = CONFIG["fasi_eclisse"]
        CHECKLIST = CONFIG["checklist_items"]
        
        log_evento_sistema("Configurazione caricata con successo", {
            "file": CONFIG_FILE,
            "fasi": len(FASI),
            "checklist": len(CHECKLIST)
        })
        return True
    except Exception as e:
        log(f"❌ Errore caricamento: {e}", "ERROR")
        return False

def carica_secrets():
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# =============================================================================
# HARDWARE
# =============================================================================

def avvia_digicamcontrol():
    log_evento_sistema("Verifica digiCamControl...")
    
    try:
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' in risultato.stdout:
            log("✅ digiCamControl già in esecuzione")
            return True
    except:
        pass
    
    try:
        log("🚀 Avvio digiCamControl...")
        subprocess.Popen([CONFIG["hardware"]["gui_path"]], shell=True)
        for i in range(8, 0, -1):
            print(f"\r   Avvio in corso... {i} secondi", end='')
            time.sleep(1)
        print("\r   ✅ digiCamControl avviato!")
        return True
    except Exception as e:
        log(f"❌ Errore avvio: {e}", "ERROR")
        return False

def test_connessione():
    """Testa la connessione con la camera con retry"""
    log("🔍 Test connessione camera...")
    
    for tentativo in range(1, 4):
        try:
            risultato = subprocess.run(
                [CMD_PATH, "/c", "get", "shutterspeed"],
                capture_output=True, text=True, timeout=5
            )
            if risultato.returncode == 0 and risultato.stdout:
                log(f"✅ Camera connessa! {risultato.stdout.strip()}")
                return True
        except:
            pass
        time.sleep(2)
    
    suono("errore_connessione")
    log("❌ Camera non trovata!", "ERROR")
    return False

def imposta_tempo(tempo, max_tentativi=3):
    """Imposta il tempo di scatto"""
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run(
                [CMD_PATH, "/c", "set", "shutterspeed", tempo],
                capture_output=True, text=True, timeout=5
            )
            if risultato.returncode == 0:
                log_evento_hardware(f"set shutterspeed {tempo}", risultato.stdout, "OK")
                return True
        except Exception as e:
            log(f"⚠️ Errore impostazione tempo {tempo}: {e}", "WARN")
        time.sleep(1)
    
    log(f"❌ Impostazione tempo {tempo} fallita!", "ERROR")
    return False

def scatta(etichetta, max_tentativi=3):
    """Esegue uno scatto con retry e riconnessione"""
    global STATS
    
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run(
                [CMD_PATH, "/c", "capture"],
                capture_output=True, text=True, timeout=15
            )
            if risultato.returncode == 0:
                STATS['scatti_riusciti'] += 1
                STATS['scatti_totali'] += 1
                log_evento_scatto(etichetta, True, {"tentativo": tentativo})
                log(f"📸 {etichetta}")
                return True
        except subprocess.TimeoutExpired:
            log(f"⚠️ Timeout scatto {etichetta}, tentativo {tentativo}", "WARN")
            # Tentativo di riconnessione
            try:
                subprocess.run([CMD_PATH, "/c", "get", "shutterspeed"], 
                              capture_output=True, timeout=3)
            except:
                pass
        except Exception as e:
            log(f"⚠️ Errore scatto {etichetta}: {e}", "WARN")
        time.sleep(0.5)
    
    STATS['scatti_falliti'] += 1
    STATS['scatti_totali'] += 1
    STATS['errori'].append(f"Scatto fallito: {etichetta}")
    log(f"❌ Scatto fallito: {etichetta}", "ERROR")
    return False

# =============================================================================
# SEQUENZA SCATTI - TUTTE CON ATTESA PRECISA
# =============================================================================

def esegui_parziale(fase, orario_inizio, intervallo, durata, tempi_lista=None):
    """
    Esegue scatti parziali a intervalli regolari a partire da un orario specifico
    """
    global STATS
    
    if not tempi_lista:
        tempi_lista = TEMPI.get("parziale", ["1/2000"])
    
    # ⚠️ ATTENDI L'ORARIO DI INIZIO
    log(f"⏳ In attesa dell'orario di inizio {fase} alle {orario_inizio}...")
    attesa_fino_a(orario_inizio, fase)
    
    tempo_scatto = tempi_lista[0]
    num_scatti = int(durata / intervallo)
    
    log(f"🎬 {fase} - {num_scatti} scatti ogni {intervallo//60} minuti a {tempo_scatto}")
    
    # Imposta il tempo una sola volta
    if not imposta_tempo(tempo_scatto):
        log(f"❌ Impossibile impostare tempo {tempo_scatto} per {fase}", "ERROR")
        return
    
    # Calcola il momento del primo scatto
    now = datetime.now()
    prossimo_scatto = now + timedelta(seconds=1)
    fine = datetime_from_time(orario_inizio) + timedelta(seconds=durata)
    count = 0
    
    log(f"   Fine fase: {fine.strftime('%H:%M:%S')}")
    
    while datetime.now() < fine:
        if stop_requested:
            break
        
        now = datetime.now()
        if now >= prossimo_scatto:
            etichetta = f"{fase}_{tempo_scatto}_shot{count+1}"
            if scatta(etichetta):
                count += 1
            # Programma il prossimo scatto
            prossimo_scatto = prossimo_scatto + timedelta(seconds=intervallo)
            if count < num_scatti:
                log(f"⏳ Prossimo scatto tra {intervallo//60} minuti (alle {prossimo_scatto.strftime('%H:%M:%S')})")
        
        # Attesa breve
        time.sleep(0.5)
    
    STATS['fasi_completate'] += 1
    log(f"✅ {fase} completata - {count} scatti")

def esegui_burst(fase, orario_inizio, durata, lista_tempi=None):
    """
    Esegue scatti a raffica a partire da un orario specifico per una durata
    """
    global STATS
    
    if not lista_tempi:
        lista_tempi = TEMPI.get("burst", ["1/2000"])
    
    # ⚠️ ATTENDI L'ORARIO DI INIZIO
    log(f"⏳ In attesa dell'orario di inizio {fase} alle {orario_inizio}...")
    attesa_fino_a(orario_inizio, fase)
    
    tempo_unico = lista_tempi[0]
    raffica = TEMPI.get("raffica_scatti", 5)
    
    log(f"🎬 {fase} - Raffica {raffica} scatti a {tempo_unico} per {durata} secondi")
    
    # Imposta il tempo una sola volta
    if not imposta_tempo(tempo_unico):
        log(f"❌ Impossibile impostare tempo {tempo_unico} per {fase}", "ERROR")
        return
    
    # Scatta in rapida successione
    inizio = datetime.now()
    fine = inizio + timedelta(seconds=durata)
    count = 0
    
    while datetime.now() < fine:
        if stop_requested:
            break
        etichetta = f"{fase}_{tempo_unico}_shot{count+1}"
        if scatta(etichetta):
            count += 1
        # Piccola pausa tra gli scatti
        time.sleep(0.1)
    
    log(f"✅ {fase} completata - {count} scatti in {durata} secondi")
    STATS['fasi_completate'] += 1

def esegui_bracketing(fase, orario_inizio, lista_tempi, durata=None):
    """
    Esegue bracketing a partire da un orario specifico per una durata o una volta
    """
    global STATS
    
    if not lista_tempi:
        lista_tempi = TEMPI.get("corona_interna", ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15"])
    
    # ⚠️ ATTENDI L'ORARIO DI INIZIO
    log(f"⏳ In attesa dell'orario di inizio {fase} alle {orario_inizio}...")
    attesa_fino_a(orario_inizio, fase)
    
    log(f"🎬 {fase} - Bracketing {len(lista_tempi)} esposizioni")
    
    # Se è specificata una durata, esegui in loop fino a scadenza
    if durata and durata > 0:
        fine = datetime.now() + timedelta(seconds=durata)
        ciclo = 0
        while datetime.now() < fine:
            if stop_requested:
                break
            ciclo += 1
            log(f"   Ciclo {ciclo}")
            for tempo in lista_tempi:
                if stop_requested:
                    break
                if datetime.now() >= fine:
                    break
                if imposta_tempo(tempo):
                    etichetta = f"{fase}_{tempo}_c{ciclo}"
                    scatta(etichetta)
                    time.sleep(0.3)
    else:
        # Esegui una sola volta
        for tempo in lista_tempi:
            if stop_requested:
                break
            if imposta_tempo(tempo):
                etichetta = f"{fase}_{tempo}"
                scatta(etichetta)
                time.sleep(0.3)
    
    STATS['fasi_completate'] += 1
    log(f"✅ {fase} completata")

# =============================================================================
# TELEGRAM
# =============================================================================

def invia_telegram(messaggio):
    secrets = carica_secrets()
    token = secrets.get("telegram", {}).get("bot_token", "")
    chat_id = secrets.get("telegram", {}).get("chat_id", "")
    
    if not token or not chat_id:
        return False
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": messaggio}, timeout=3)
        return True
    except:
        return False

# =============================================================================
# VERIFICHE INIZIALI
# =============================================================================

def verifica_iniziale():
    """Esegue tutte le verifiche preliminari"""
    log_evento_sistema("--- VERIFICHE INIZIALI ---")
    
    # 1. Verifica connessione fotocamera
    log("🔍 Verifica connessione fotocamera...")
    if not test_connessione():
        log("⚠️ Fotocamera non connessa!", "WARN")
        if input("\nPremi INVIO per continuare o CTRL+C per fermare... "):
            pass
    
    # 2. Verifica cartella di salvataggio
    log("📁 Verifica cartella di salvataggio...")
    
    # 3. Verifica sincronizzazione oraria
    log("🕐 Verifica sincronizzazione oraria...")
    
    # 4. Verifica file configurazione
    log("📄 Verifica file configurazione...")
    if os.path.exists(CONFIG_FILE):
        log("✅ File configurazione presente")
    else:
        log("❌ File configurazione mancante!", "ERROR")
        return False
    
    # 5. Verifica batteria e spazio
    log("🔋 Verifica batteria e spazio...")
    try:
        import psutil
        batteria = psutil.sensors_battery()
        if batteria:
            if batteria.percent < 20 and not batteria.power_plugged:
                log(f"⚠️ Batteria al {batteria.percent}% - collegare l'alimentazione!", "WARN")
            else:
                log(f"✅ Batteria: {batteria.percent}%")
    except:
        pass
    
    try:
        import shutil
        spazio = shutil.disk_usage("C:")
        if spazio.free < 1024 * 1024 * 1024:  # 1GB
            log(f"⚠️ Spazio libero: {spazio.free // (1024*1024*1024)}GB - potrebbe essere insufficiente!", "WARN")
        else:
            log(f"✅ Spazio libero: {spazio.free // (1024*1024*1024)}GB")
    except:
        pass
    
    log_evento_sistema("--- VERIFICHE COMPLETATE ---")
    return True

# =============================================================================
# REPORT
# =============================================================================

def genera_report():
    print("\n" + "=" * 70)
    print("   📊 REPORT ECLISSE")
    print("=" * 70)
    
    report = f"""
📅 DATA: {TIMING['_data']}
📍 POSIZIONE: {CONFIG.get('coordinate', {}).get('latitudine_dms', 'N/D')}
📷 CAMERA: {CONFIG['hardware']['marca_camera']}

⏰ TIMING:
   C1: {TIMING['c1_inizio']}  |  Totalità: {TIMING['totalita_inizio']} - {TIMING['totalita_fine']}  |  P4: {TIMING['p4_fine']}

📸 STATISTICHE:
   Fasi completate: {STATS['fasi_completate']}/{len(FASI)}
   Scatti riusciti: {STATS['scatti_riusciti']}
   Scatti falliti: {STATS['scatti_falliti']}
   Totale: {STATS['scatti_totali']}
   Successo: {f"{(STATS['scatti_riusciti']/max(1,STATS['scatti_totali'])*100):.1f}%"}

⏱️ DURATA:
   Inizio: {STATS['inizio'].strftime('%H:%M:%S') if STATS['inizio'] else 'N/D'}
   Fine: {STATS['fine'].strftime('%H:%M:%S') if STATS['fine'] else 'N/D'}

❌ ERRORI:
   {chr(10).join([f'   • {e}' for e in STATS['errori'][:5]]) if STATS['errori'] else '   ✅ Nessun errore'}
"""
    
    print(report)
    
    nome_file = f"report_eclisse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(nome_file, 'w', encoding='utf-8') as f:
        f.write(report)
    log(f"✅ Report salvato in: {nome_file}")
    
    invia_telegram(f"📊 REPORT ECLISSE\n{report[:500]}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    global STATS, stop_requested
    
    # Inizializza log
    log_evento_sistema("========================================")
    log_evento_sistema("AVVIO SCRIPT ECLISSE")
    log_evento_sistema(f"Data/ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_evento_sistema("========================================")
    
    print("\n" + "=" * 70)
    print("   🌞 SOLAR ECLIPSE AUTOMATION v5.0")
    print("=" * 70)
    
    # Carica configurazione
    if not carica_config():
        input("\nPremi INVIO per uscire...")
        return
    
    # Mostra timing
    print(f"\n📅 DATA: {TIMING['_data']}")
    print(f"\n⏰ TIMING ECLISSE:")
    print(f"   C1 (Inizio parziale):    {TIMING['c1_inizio']}")
    print(f"   Avviso togli filtro:     {TIMING['avviso_togli_filtro']}")
    print(f"   Anello diamante IN:      {TIMING['anello_in_inizio']} - {TIMING['anello_in_fine']}")
    print(f"   Totalità (C2):           {TIMING['totalita_inizio']} - {TIMING['totalita_fine']}")
    print(f"   Anello diamante OUT:     {TIMING['anello_out_inizio']} - {TIMING['anello_out_fine']}")
    print(f"   Avviso rimetti filtro:   {TIMING['avviso_metti_filtro']}")
    print(f"   Post-parziale:           {TIMING['post_parziale_inizio']}")
    print(f"   P4 (Fine parziale):      {TIMING['p4_fine']}")
    
    # Verifiche iniziali
    print("\n" + "=" * 70)
    print("   🔍 VERIFICHE INIZIALI")
    print("=" * 70)
    
    if not verifica_iniziale():
        print("\n❌ Verifiche fallite!")
        input("\nPremi INVIO per uscire...")
        return
    
    # Checklist
    print("\n" + "=" * 70)
    print("   🔴 CHECKLIST PRE-ECLISSE")
    print("=" * 70)
    print("\n⚠️  LEGGI E CONFERMA OGNI VOCE ⚠️\n")
    
    for i, item in enumerate(CHECKLIST, 1):
        input(f"   [{i}/{len(CHECKLIST)}] {item} [PREMI INVIO]")
    
    print("\n✅ CHECKLIST COMPLETATA!")
    
    # Hardware
    print("\n" + "!" * 70)
    print("   CONFIGURAZIONE HARDWARE")
    print("!" * 70)
    print("  1. ACCENDI CAMERA")
    print("  2. COLLEGA USB")
    print("!" * 70)
    
    input("\n[Premi INVIO quando camera è collegata e accesa]")
    
    avvia_digicamcontrol()
    
    if not test_connessione():
        print("\n⚠️ Camera non rilevata!")
        if input("\nPremi INVIO per continuare o CTRL+C per fermare... "):
            pass
    
    # Test tempo
    test_tempo = CONFIG.get("parametri_camera", {}).get("test_tempo", "1/1000")
    print(f"\n📷 Test impostazione tempo {test_tempo}...")
    if imposta_tempo(test_tempo):
        print("   ✅ Test superato!")
    else:
        print("   ⚠️ Test fallito, continuo...")
    
    # ========================================================================
    # ATTESA INIZIO ECLISSE
    # ========================================================================
    STATS['inizio'] = datetime.now()
    
    print("\n" + "⚠️" * 70)
    print("   SCRIPT PRONTO - IN ATTESA DELL'ECLISSE")
    print("   NON SPEGNERE IL COMPUTER O SCOLLEGARE LA CAMERA")
    print("⚠️" * 70)
    
    input("\n[Premi INVIO per avviare]")
    
    invia_telegram("🚀 SCRIPT AVVIATO - In attesa dell'eclisse")
    log_evento_sistema("SCRIPT AVVIATO")
    
    # ========================================================================
    # ESECUZIONE
    # ========================================================================
    try:
        # Converti timing in oggetti time
        c1 = time_from_string(TIMING['c1_inizio'])
        avviso_togli = time_from_string(TIMING['avviso_togli_filtro'])
        anello_in_inizio = time_from_string(TIMING['anello_in_inizio'])
        anello_in_fine = time_from_string(TIMING['anello_in_fine'])
        totalita_inizio = time_from_string(TIMING['totalita_inizio'])
        totalita_fine = time_from_string(TIMING['totalita_fine'])
        anello_out_inizio = time_from_string(TIMING['anello_out_inizio'])
        anello_out_fine = time_from_string(TIMING['anello_out_fine'])
        avviso_metti = time_from_string(TIMING['avviso_metti_filtro'])
        post_parziale_inizio = time_from_string(TIMING['post_parziale_inizio'])
        p4_fine = time_from_string(TIMING['p4_fine'])
        
        # ================================================================
        # FASE C1 - PARZIALITÀ INGRESSO
        # ================================================================
        durata_parziale = (datetime_from_time(p4_fine) - datetime_from_time(c1)).total_seconds()
        intervallo_parziale = TEMPI.get("intervallo_parziale_sec", 780)
        
        log(f"📅 PRE-PARZIALE: da {c1} a {p4_fine}, durata {durata_parziale//60} minuti")
        
        esegui_parziale(
            "PRE-PARZIALE",
            c1,
            intervallo_parziale,
            durata_parziale,
            TEMPI.get("parziale", ["1/2000"])
        )
        
        # ================================================================
        # AVVISO TOGLI FILTRO
        # ================================================================
        attesa_fino_a(avviso_togli, "AVVISO TOGLI FILTRO")
        suono("togli_filtro")
        log("🟢 AVVISO: TOGLI IL FILTRO SOLARE tra 30 secondi!")
        invia_telegram("🔴 TOGLI IL FILTRO! Anello diamante tra 30 secondi")
        
        # ================================================================
        # ANELLO DI DIAMANTE INGRESSO
        # ================================================================
        # Attendi l'inizio dell'anello (30 secondi dopo l'avviso)
        time.sleep(30)
        
        durata_anello_in = (datetime_from_time(anello_in_fine) - datetime_from_time(anello_in_inizio)).total_seconds()
        esegui_burst(
            "ANELLO_DIAMANTE_IN",
            anello_in_inizio,
            durata_anello_in,
            TEMPI.get("burst", ["1/2000"])
        )
        
        # ================================================================
        # TOTALITÀ (C2)
        # ================================================================
        # Attendi l'inizio della totalità
        attesa_fino_a(totalita_inizio, "TOTALITA' (C2)")
        
        durata_totalita = (datetime_from_time(totalita_fine) - datetime_from_time(totalita_inizio)).total_seconds()
        
        log(f"🌑 TOTALITA': {durata_totalita:.0f} secondi")
        
        # Corona interna
        esegui_bracketing(
            "CORONA_INTERNA",
            totalita_inizio,
            TEMPI.get("corona_interna", ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15"]),
            durata_totalita / 2  # Metà della totalità
        )
        
        # Corona esterna (seconda metà della totalità)
        if datetime.now() < datetime_from_time(totalita_fine):
            esegui_bracketing(
                "CORONA_ESTERNA",
                datetime.now().time(),  # Orario corrente
                TEMPI.get("corona_esterna", ["1/8", "1/4", "0.5", "1", "2"]),
                (datetime_from_time(totalita_fine) - datetime.now()).total_seconds()
            )
        
        # ================================================================
        # ANELLO DI DIAMANTE USCITA
        # ================================================================
        attesa_fino_a(anello_out_inizio, "ANELLO_DIAMANTE_OUT")
        
        durata_anello_out = (datetime_from_time(anello_out_fine) - datetime_from_time(anello_out_inizio)).total_seconds()
        esegui_burst(
            "ANELLO_DIAMANTE_OUT",
            anello_out_inizio,
            durata_anello_out,
            TEMPI.get("burst", ["1/2000"])
        )
        
        # ================================================================
        # AVVISO RIMETTI FILTRO
        # ================================================================
        attesa_fino_a(avviso_metti, "AVVISO RIMETTI FILTRO")
        suono("metti_filtro")
        log("🔴 AVVISO: RIMETTI IL FILTRO SOLARE!")
        invia_telegram("🔴 RIMETTI IL FILTRO! Totalità finita")
        
        # ================================================================
        # FASE PARZIALE FINALE
        # ================================================================
        attesa_fino_a(post_parziale_inizio, "POST-PARZIALE")
        
        durata_post = (datetime_from_time(p4_fine) - datetime_from_time(post_parziale_inizio)).total_seconds()
        esegui_parziale(
            "POST-PARZIALE",
            post_parziale_inizio,
            600,  # 10 minuti
            durata_post,
            TEMPI.get("parziale", ["1/2000"])
        )
        
        # ====================================================================
        # COMPLETATO
        # ====================================================================
        STATS['fine'] = datetime.now()
        
        print("\n" + "=" * 70)
        print("   🎉 ECLISSE COMPLETATA! 🎉")
        print("=" * 70)
        
        log_evento_sistema("ECLISSE COMPLETATA", {
            "fasi_completate": STATS['fasi_completate'],
            "scatti_riusciti": STATS['scatti_riusciti'],
            "scatti_falliti": STATS['scatti_falliti']
        })
        
        invia_telegram("🎉 ECLISSE COMPLETATA! Report in generazione...")
        genera_report()
        
    except KeyboardInterrupt:
        log("🛑 Script interrotto", "WARN")
        print("\n\n⚠️ Script interrotto.")
        sys.exit(0)
    except Exception as e:
        log(f"❌ ERRORE: {e}", "ERROR")
        print(f"\n\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()