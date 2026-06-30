import subprocess
import time
from datetime import datetime, timedelta, timezone
import os
import json
import urllib.request
import urllib.parse
import sys
import email.utils
import logging  
import msvcrt   

# ==============================================================================
# CONFIGURAZIONE GLOBALE, NOTIFICHE E DEBUG COLORE
# ==============================================================================
DEBUG_MODE = False  
TARGET_STORAGE = "1" 
SECRETS_FILE = "secrets.json"
PORTA_SERVER = "2727" 
BASE_URL_SLC = f"http://127.0.0.1:{PORTA_SERVER}/?slc="
BASE_URL_CMD = f"http://127.0.0.1:{PORTA_SERVER}/?CMD="

# Variabile globale per memorizzare la discrepanza calcolata (in secondi)
DISCREPANZA_TEMPO = 0.0

# Codici colore ANSI per la console
CLR_RESET = "\033[0m"
CLR_DEBUG = "\033[94m"    
CLR_INFO  = "\033[96m"    
CLR_OK    = "\033[92m"    
CLR_WARN  = "\033[93m"    
CLR_ERR   = "\033[91m"    
CLR_BOLD  = "\033[1m"

if os.name == 'nt':
    os.system('color')

# ==============================================================================
# CONFIGURAZIONE SCATOLA NERA (LOGGING SU FILE E CONSOLE)
# ==============================================================================
logger = logging.getLogger("EclipseLogger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("eclipse_session.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s')
file_formatter.datefmt = '%Y-%m-%d %H:%M:%S'
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def log_all(livello, msg, color=""):
    clean_msg = msg.replace(CLR_BOLD, "").replace(CLR_RESET, "").replace(CLR_DEBUG, "").replace(CLR_INFO, "").replace(CLR_OK, "").replace(CLR_WARN, "").replace(CLR_ERR, "")
    
    if livello == "debug":
        logger.debug(clean_msg)
        if not DEBUG_MODE: return
    elif livello == "info": 
        logger.info(clean_msg)
    elif livello == "warn": 
        logger.warning(clean_msg)
    elif livello == "err": 
        logger.error(clean_msg)
    
    if color: print(f"{color}{msg}{CLR_RESET}")
    else: print(msg)

def speach_alert(testo):
    log_all("debug", f"[VOCALE] Sintesi vocale avviata per: '{testo}'")
    command = f"Add-Type -AssemblyName System.Speech; $val = New-Object System.Speech.Synthesis.SpeechSynthesizer; $val.Speak('{testo}')"
    try:
        subprocess.Popen(['powershell', '-Command', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log_all("err", f"[VOCALE] Errore sintesi vocale: {e}")

# ==============================================================================
# CALCOLO DELLA DISCREPANZA ORARIA (SENZA MODIFICARE L'OROLOGIO DI WINDOWS)
# ==============================================================================
def misura_discrepanza_oraria():
    """Calcola lo sfasamento tra il PC e il server di riferimento, senza richiedere permessi admin"""
    global DISCREPANZA_TEMPO
    log_all("info", "⏱️ CALCOLO DISCREPANZA: Verifica sfasamento orario con il server...", CLR_BOLD + CLR_INFO)
    try:
        url_target = "https://raw.githubusercontent.com/S85mario/Solar-Eclipse-Automation/main/SolarEclipse.py"
        req = urllib.request.Request(url_target, method='HEAD')
        
        # Prendiamo il tempo del PC prima e dopo la richiesta per compensare la latenza di rete
        t_inizio = datetime.now(timezone.utc)
        with urllib.request.urlopen(req, timeout=5) as res:
            header_date = res.headers.get('Date')
        t_fine = datetime.now(timezone.utc)
        
        if header_date:
            ora_server = email.utils.parsedate_to_datetime(header_date)
            # Stimiamo il momento esatto in cui il server ha risposto (metà del tempo di transito della richiesta)
            ora_pc_stimata = t_inizio + (t_fine - t_inizio) / 2
            
            # Calcolo della differenza in secondi (Server - PC)
            DISCREPANZA_TEMPO = (ora_server - ora_pc_stimata).total_seconds()
            
            if abs(DISCREPANZA_TEMPO) > 0.1:
                log_all("warn", f"⚠️ DISCREPANZA RILEVATA: Il PC è sfasato di {DISCREPANZA_TEMPO:+.3f} secondi rispetto al server.", CLR_BOLD + CLR_WARN)
                log_all("info", "✅ Lo script applicherà questa correzione in tempo reale su ogni timer.", CLR_OK)
            else:
                log_all("info", f"✅ Orologio PC perfetto (Discrepanza minima: {DISCREPANZA_TEMPO:+.3f}s).", CLR_OK)
        else:
            log_all("err", "❌ Impossibile estrarre i metadati temporali dal server. Discrepanza impostata a 0.", CLR_ERR)
            DISCREPANZA_TEMPO = 0.0
    except Exception as e:
        log_all("err", f"❌ Calcolo discrepanza fallito ({e}). Discrepanza impostata a 0.", CLR_ERR)
        DISCREPANZA_TEMPO = 0.0

def get_ora_corretta_ora():
    """Restituisce l'orario attuale del PC già corretto con la discrepanza calcolata"""
    return datetime.now() + timedelta(seconds=DISCREPANZA_TEMPO)

# ==============================================================================
# FUNZIONE DI AGGIORNAMENTO SU RICHIESTA VIA MENU
# ==============================================================================
def check_for_updates():
    URL_AGGIORNAMENTO = "https://raw.githubusercontent.com/S85mario/Solar-Eclipse-Automation/main/SolarEclipse.py"
    log_all("info", "🔄 VERIFICA AGGIORNAMENTI DA GITHUB IN CORSO...", CLR_BOLD + CLR_INFO)
    try:
        req = urllib.request.Request(URL_AGGIORNAMENTO)
        with urllib.request.urlopen(req, timeout=5) as response:
            remote_code = response.read().decode('utf-8')
        
        current_script_path = sys.argv[0]
        with open(current_script_path, 'r', encoding='utf-8') as f:
            local_code = f.read()
        
        if remote_code.strip() != local_code.strip():
            log_all("warn", "⚠️ TROVATA NUOVA VERSIONE! Aggiornamento automatico...", CLR_BOLD + CLR_WARN)
            with open(current_script_path, 'w', encoding='utf-8') as f:
                f.write(remote_code)
            log_all("info", "✅ Script aggiornato con successo! Riavvio in corso...", CLR_BOLD + CLR_OK)
            speach_alert("Update completato.")
            time.sleep(1.5)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            log_all("info", "✅ Il codice locale è già aggiornato all'ultima versione di GitHub.", CLR_OK)
            input("\nPremere Invio per tornare al menu...")
    except Exception as e:
        log_all("err", f"❌ Controllo aggiornamenti fallito: {e}", CLR_ERR)
        input("\nPremere Invio per tornare al menu...")

# ==============================================================================
# MENU INIZIALE E CONFIGURAZIONE DINAMICA ORARI
# ==============================================================================
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CLR_BOLD}{CLR_INFO}=== AUTOMAZIONE SCRIPT ECLISSI ==={CLR_RESET}")
    print("1) Imposta Orari REALI Ribadeo - Sole Basso (12 Agosto 2026) [+ Misura Discrepanza]")
    print("2) Imposta Orari TEST RAPIDO (Oggi - Qualche minuto nel futuro) [+ Misura Discrepanza]")
    print("3) Inserimento MANUALE personalizzato")
    print("4) 🔄 Controlla ed esegui AGGIORNAMENTO da GitHub")
    print("----------------------------------------------------------------")
    scelta_ora = input("Scegli un'opzione (1/2/3/4): ").strip()

    if scelta_ora == '1':
        misura_discrepanza_oraria() # Misura lo sfasamento prima di creare la coda
        C2_TIME = datetime(2026, 8, 12, 20, 26, 56)
        C3_TIME = datetime(2026, 8, 12, 20, 28, 45)
        break
    elif scelta_ora == '2':
        misura_discrepanza_oraria() # Misura lo sfasamento prima di creare la coda
        # Nel test rapido gli orari di C2 e C3 si basano sull'ora corretta stimata
        ora_corretta_attuale = get_ora_corretta_ora()
        C2_TIME = ora_corretta_attuale + timedelta(minutes=2)
        C3_TIME = ora_corretta_attuale + timedelta(minutes=4)
        break
    elif scelta_ora == '3':
        print(f"\n{CLR_WARN}Inserisci i dati per l'orario personalizzato:{CLR_RESET}")
        anno = int(input("Anno (es. 2026): ").strip())
        mese = int(input("Mese (1-12): ").strip())
        giorno = int(input("Giorno (1-31): ").strip())
        
        print(f"\n{CLR_INFO}-> Configurazione Contatto C2 (Inizio Totalità):{CLR_RESET}")
        ora_c2 = int(input("  Ora (0-23): ").strip())
        min_c2 = int(input("  Minuto (0-59): ").strip())
        sec_c2 = int(input("  Secondo (0-59): ").strip())
        C2_TIME = datetime(anno, mese, giorno, ora_c2, min_c2, sec_c2)
        
        print(f"\n{CLR_INFO}-> Configurazione Contatto C3 (Fine Totalità):{CLR_RESET}")
        ora_c3 = int(input("  Ora (0-23): ").strip())
        min_c3 = int(input("  Minuto (0-59): ").strip())
        sec_c3 = int(input("  Secondo (0-59): ").strip())
        C3_TIME = datetime(anno, mese, giorno, ora_c3, min_c3, sec_c3)
        break
    elif scelta_ora == '4':
        check_for_updates()
    else:
        print(f"{CLR_ERR}Opzione non valida!{CLR_RESET}")
        time.sleep(1)

log_all("info", f"⏱️ ORARI CONFIGURATI - C2: {C2_TIME.strftime('%H:%M:%S')} | C3: {C3_TIME.strftime('%H:%M:%S')}", CLR_BOLD + CLR_OK)

print(f"\n{CLR_BOLD}{CLR_INFO}=== CONFIGURAZIONE DEBUG ==={CLR_RESET}")
scelta_debug = input("Vuoi attivare la modalità DEBUG avanzata a schermo? (s/N): ").strip().lower()
if scelta_debug == 's':
    DEBUG_MODE = True
    log_all("info", "-> Modalità DEBUG Verbose Attivata.", CLR_DEBUG)
else:
    DEBUG_MODE = False
    log_all("info", "-> Modalità DEBUG Verbose Disattivata.", CLR_WARN)

BOT_TOKEN, CHAT_ID = None, None
try:
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, 'r') as f:
            config = json.load(f)
            BOT_TOKEN = config["telegram"]["bot_token"]
            CHAT_ID = config["telegram"]["chat_id"]
except Exception: pass

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        data = urllib.parse.urlencode(payload).encode('utf-8')
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=4)
        log_all("debug", f"[TELEGRAM] Messaggio inviato: {message}")
    except Exception as e:
        log_all("debug", f"[TELEGRAM] Invio fallito: {e}")

# ==============================================================================
# FUNZIONE DI SCATTO OTTIMIZZATA (CACHE PARAMETRI VIA DIGICAMCONTROL)
# ==============================================================================
_STATO_CAMERA_CACHE = {
    "iso": None,
    "aperture": None,
    "shutterspeed": None,
    "transfer": None
}

def execute_camera_command(shutter, aperture, iso, label):
    shutter_clean = shutter.replace('"', '')
    val_raw = str(aperture).lower().replace('f', '').replace('/', '').replace(',', '.').strip()
    aperture_final = f"{val_raw}.0" if '.' not in val_raw else val_raw
    
    try:
        log_all("debug", f"[FOTOCAMERA] Sincronizzazione parametri per: {label}")
        
        if _STATO_CAMERA_CACHE["iso"] != iso:
            url_iso = f"{BASE_URL_SLC}set&param1=iso&param2={iso}"
            urllib.request.urlopen(url_iso, timeout=2).read()
            _STATO_CAMERA_CACHE["iso"] = iso
            time.sleep(0.04)
            
        if _STATO_CAMERA_CACHE["aperture"] != aperture_final:
            url_aperture = f"{BASE_URL_SLC}set&param1=aperture&param2={aperture_final}"
            urllib.request.urlopen(url_aperture, timeout=2).read()
            _STATO_CAMERA_CACHE["aperture"] = aperture_final
            time.sleep(0.04)
            
        if _STATO_CAMERA_CACHE["shutterspeed"] != shutter_clean:
            url_shutter = f"{BASE_URL_SLC}set&param1=shutterspeed&param2={urllib.parse.quote(shutter_clean)}"
            urllib.request.urlopen(url_shutter, timeout=2).read()
            _STATO_CAMERA_CACHE["shutterspeed"] = shutter_clean
            time.sleep(0.04)
            
        if _STATO_CAMERA_CACHE["transfer"] != TARGET_STORAGE:
            url_transfer = f"{BASE_URL_SLC}set&param1=transfer&param2={TARGET_STORAGE}"
            urllib.request.urlopen(url_transfer, timeout=2).read()
            _STATO_CAMERA_CACHE["transfer"] = TARGET_STORAGE
            time.sleep(0.04)
            
        url_premi = f"{BASE_URL_CMD}CaptureNoAf"
        url_rilascia = f"{BASE_URL_CMD}Release"
        
        urllib.request.urlopen(url_premi, timeout=2).read()
        time.sleep(0.45) 
        urllib.request.urlopen(url_rilascia, timeout=2).read()
        
        log_all("info", f"📸 {label} -> ESEGUITO (ISO {iso} | {shutter_clean} | f/{aperture_final})", CLR_OK)
        send_telegram_message(f"📸 `{label}` eseguita.")
        
    except Exception as e:
        log_all("err", f"❌ Errore critico su comando camera per [{label}]: {e}", CLR_ERR)

# ==============================================================================
# TIMELINE DEFINITIVA VARIATA - ESTINZIONE ATMOSFERICA COMPENSATA
# ==============================================================================
script_data = """
# --- FASE PARZIALE IN INGRESSO (Filtro ND 3.8 - ISO 100) ---
TAKEPIC,C2,-,58:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -58 min (ND 3.8)
TAKEPIC,C2,-,40:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -40 min (ND 3.8)
TAKEPIC,C2,-,20:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -20 min (ND 3.8)
TAKEPIC,C2,-,10:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -10 min (ND 3.8)
TAKEPIC,C2,-,05:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -5 min (ND 3.8)
TAKEPIC,C2,-,02:00,1,1/2500,8,100,1,RAW,L,N,Parziale IN -2 min (ND 3.8)

# --- FENOMENI VELOCI IN INGRESSO (C2) ---
TAKEPIC,C2,-,00:08,1,1/2500,8,100,1,RAW,L,N,Anello di Diamante C2 (Con ND 3.8)
TAKEPIC,C2,-,00:06,1,1/2500,8,100,1,RAW,L,N,Anello di Diamante C2 (Senza Filtro)
TAKEPIC,C2,-,00:04,1,1/320,8,800,1,RAW,L,N,Anello di Diamante C2 (Esplosione)
TAKEPIC,C2,-,00:02,1,1/2500,8,100,1,RAW,L,N,Grani di Baily C2 (Perle di luce)
TAKEPIC,C2,-,00:01,1,1/2500,8,100,1,RAW,L,N,Grani di Baily C2 (Ultimo filo)

# --- TOTALITÀ (109 Secondi Disponibili - ISO 800 e f/8 FISSI) ---
# CICLO 1 HDR
TAKEPIC,C2,+,00:02,1,1/2500,8,400,1,RAW,L,N,Ciclo 1 - HDR 1 - Prominenze (ISO 400)
TAKEPIC,C2,+,00:04,1,1/1250,8,800,1,RAW,L,N,Ciclo 1 - HDR 2 - Lower Corona
TAKEPIC,C2,+,00:06,1,1/160,8,800,1,RAW,L,N,Ciclo 1 - HDR 3 - Inner Corona 0.2
TAKEPIC,C2,+,00:08,1,1/80,8,800,1,RAW,L,N,Ciclo 1 - HDR 4 - Inner Corona 0.5
TAKEPIC,C2,+,00:10,1,1/20,8,800,1,RAW,L,N,Ciclo 1 - HDR 5 - Middle Corona
TAKEPIC,C2,+,00:12,1,1/8,8,800,1,RAW,L,N,Ciclo 1 - HDR 6 - Upper Corona
TAKEPIC,C2,+,00:14,1,1/5,8,800,1,RAW,L,N,Ciclo 1 - HDR 7 - Outer Corona 3R
TAKEPIC,C2,+,00:16,1,1/2,8,800,1,RAW,L,N,Ciclo 1 - HDR 8 - Outer Corona 4R
TAKEPIC,C2,+,00:18,1,1,8,800,1,RAW,L,N,Ciclo 1 - HDR 9 - Outer Corona 8R
TAKEPIC,C2,+,00:21,1,2,8,800,1,RAW,L,N,Ciclo 1 - HDR 10 - Earthshine

# CICLO 2 HDR
TAKEPIC,C2,+,00:46,1,1/2500,8,400,1,RAW,L,N,Ciclo 2 - HDR 1 - Prominenze (ISO 400)
TAKEPIC,C2,+,00:48,1,1/1250,8,800,1,RAW,L,N,Ciclo 2 - HDR 2 - Lower Corona
TAKEPIC,C2,+,00:50,1,1/160,8,800,1,RAW,L,N,Ciclo 2 - HDR 3 - Inner Corona 0.2
TAKEPIC,C2,+,00:52,1,1/80,8,800,1,RAW,L,N,Ciclo 2 - HDR 4 - Inner Corona 0.5
TAKEPIC,C2,+,00:54,1,1/20,8,800,1,RAW,L,N,Ciclo 2 - HDR 5 - Middle Corona
TAKEPIC,C2,+,00:56,1,1/8,8,800,1,RAW,L,N,Ciclo 2 - HDR 6 - Upper Corona
TAKEPIC,C2,+,00:58,1,1/5,8,800,1,RAW,L,N,Ciclo 2 - HDR 7 - Outer Corona 3R
TAKEPIC,C2,+,01:00,1,1/2,8,800,1,RAW,L,N,Ciclo 2 - HDR 8 - Outer Corona 4R
TAKEPIC,C2,+,01:02,1,1,8,800,1,RAW,L,N,Ciclo 2 - HDR 9 - Outer Corona 8R
TAKEPIC,C2,+,01:05,1,2,8,800,1,RAW,L,N,Ciclo 2 - HDR 10 - Earthshine

# CICLO 3 HDR
TAKEPIC,C2,+,01:22,1,1/2500,8,400,1,RAW,L,N,Ciclo 3 - HDR 1 - Prominenze (ISO 400)
TAKEPIC,C2,+,01:24,1,1/1250,8,800,1,RAW,L,N,Ciclo 3 - HDR 2 - Lower Corona
TAKEPIC,C2,+,01:26,1,1/160,8,800,1,RAW,L,N,Ciclo 3 - HDR 3 - Inner Corona 0.2
TAKEPIC,C2,+,01:28,1,1/80,8,800,1,RAW,L,N,Ciclo 3 - HDR 4 - Inner Corona 0.5
TAKEPIC,C2,+,01:30,1,1/20,8,800,1,RAW,L,N,Ciclo 3 - HDR 5 - Middle Corona
TAKEPIC,C2,+,01:32,1,1/8,8,800,1,RAW,L,N,Ciclo 3 - HDR 6 - Upper Corona
TAKEPIC,C2,+,01:34,1,1/5,8,800,1,RAW,L,N,Ciclo 3 - HDR 7 - Outer Corona 3R
TAKEPIC,C2,+,01:36,1,1/2,8,800,1,RAW,L,N,Ciclo 3 - HDR 8 - Outer Corona 4R
TAKEPIC,C2,+,01:38,1,1,8,800,1,RAW,L,N,Ciclo 3 - HDR 9 - Outer Corona 8R
TAKEPIC,C2,+,01:41,1,2,8,800,1,RAW,L,N,Ciclo 3 - HDR 10 - Earthshine

# --- FENOMENI VELOCI IN USCITA (C3) ---
TAKEPIC,C3,+,00:01,1,1/2500,8,100,1,RAW,L,N,Grani di Baily C3 (Senza Filtro)
TAKEPIC,C3,+,00:02,1,1/2500,8,100,1,RAW,L,N,Grani di Baily C3 (Senza Filtro)
TAKEPIC,C3,+,00:03,1,1/2500,8,100,1,RAW,L,N,Grani di Baily C3 (Con ND 3.8)
TAKEPIC,C3,+,00:05,1,1/320,8,800,1,RAW,L,N,Anello di Diamante C3 (Flash)
TAKEPIC,C3,+,00:08,1,1/320,8,800,1,RAW,L,N,Anello di Diamante C3 (Flash finale)

# --- FASE PARZIALE IN USCITA (Filtro ND 3.8 - ISO 100) ---
TAKEPIC,C3,+,05:00,1,1/2500,8,100,1,RAW,L,N,Parziale OUT +05 min (ND 3.8)
TAKEPIC,C3,+,10:00,1,1/2500,8,100,1,RAW,L,N,Parziale OUT +10 min (ND 3.8)
TAKEPIC,C3,+,20:00,1,1/2500,8,100,1,RAW,L,N,Parziale OUT +20 min (ND 3.8)
TAKEPIC,C3,+,30:00,1,1/2500,8,100,1,RAW,L,N,Parziale OUT +30 min (ND 3.8)
"""

cronoprogramma = []
for line in script_data.strip().split('\n'):
    if not line.strip() or line.strip().startswith('#'): continue
    parts = line.split(',')
    _, contatto, segno, offset_str, _, shutter, aperture, iso, _, _, _, _, commento = parts
    minuti, secondi = map(int, offset_str.split(':'))
    offset = timedelta(minutes=minuti, seconds=secondi)
    base_time = C2_TIME if contatto == "C2" else C3_TIME
    target_time = base_time + (offset if segno == "+" else -offset)
    cronoprogramma.append({'time': target_time, 'shutter': shutter, 'aperture': aperture, 'iso': iso, 'label': commento})

cronoprogramma.sort(key=lambda x: x['time'])
# Valutiamo la coda basandoci sull'ora reale stimata, non quella sfasata del PC
ora_corretta_avvio = get_ora_corretta_ora()
scatti_validi = [s for s in cronoprogramma if s['time'] > ora_corretta_avvio]
log_all("info", f"🚀 Monitoraggio avviato. Scatti validi in coda: {len(scatti_validi)}", CLR_BOLD + CLR_INFO)

for s in scatti_validi:
    log_all("debug", f"[CODA] Target: {s['time'].strftime('%H:%M:%S')} -> {s['label']}")

promemoria_rimozione_inviato = False
promemoria_inserimento_inviato = False

ora_inizio_attesa = get_ora_corretta_ora()

# ==============================================================================
# MAIN LOOP DELLA TIMELINE CON BARRA DI AVANZAMENTO CORRETTA
# ==============================================================================
for idx, scatto in enumerate(scatti_validi):
    log_all("debug", f"[ATTESA] Prossimo scatto programmato: {scatto['label']} alle {scatto['time'].strftime('%H:%M:%S.%f')[:-3]}")
    
    durata_totale_attesa = (scatto['time'] - ora_inizio_attesa).total_seconds()
    if durata_totale_attesa <= 0: durata_totale_attesa = 1.0

    # Il loop controlla l'ora corretta del PC (ora_pc + discrepanza) rispetto al target dell'eclissi
    while get_ora_corretta_ora() < scatto['time']:
        adesso_corretto = get_ora_corretta_ora()
        tempo_rimanente = scatto['time'] - adesso_corretto
        sec_mancanti = tempo_rimanente.total_seconds()
        
        tempo_trascorso = (adesso_corretto - ora_inizio_attesa).total_seconds()
        percentuale = min(100.0, max(0.0, (tempo_trascorso / durata_totale_attesa) * 100))
        
        blocchi = int(percentuale / 5)
        barra_visiva = "█" * blocchi + "-" * (20 - blocchi)
        
        sys.stdout.write(f"\r{CLR_INFO}[{barra_visiva}] {percentuale:5.1f}% | Mancano: {sec_mancanti:6.1f}s | Prossimo: {scatto['label'][:30]}{CLR_RESET}")
        sys.stdout.flush()

        if "Anello di Diamante C2 (Con ND 3.8)" in scatto['label'] and tempo_rimanente <= timedelta(minutes=4, seconds=50) and not promemoria_rimozione_inviato:
            print("\n") 
            msg = "⚠️ RIMUOVERE FILTRO ND 3.8 ORA!"
            log_all("warn", msg, CLR_BOLD + CLR_WARN)
            send_telegram_message(msg)
            speach_alert("Filter.")  
            promemoria_rimozione_inviato = True
            
        if msvcrt.kbhit():
            tasto = msvcrt.getch().decode('utf-8').lower()
            if tasto == ' ': 
                print("\n")
                log_all("warn", f"⚠️ INTERVENTO UTENTE: Forzatura scatto anticipato per {scatto['label']}!", CLR_BOLD + CLR_WARN)
                break
            elif tasto == 's': 
                print("\n")
                log_all("warn", f"⏭️ INTERVENTO UTENTE: Scatto {scatto['label']} saltato manualmente.", CLR_BOLD + CLR_WARN)
                scatto = None
                break
                
        time.sleep(0.05) 
        
    print("") 
    if scatto is None: 
        ora_inizio_attesa = get_ora_corretta_ora()
        continue
        
    # ==========================================================================
    # SISTEMA VOCALE ULTRA-RAPIDO (EVITA SOVRAPPOSIZIONI AUDIO)
    # ==========================================================================
    if "Anello di Diamante C2" in scatto['label'] and "Con ND 3.8" in scatto['label']:
        speach_alert("Diamante")  
    elif "Grani di Baily C2" in scatto['label'] and "Perle di luce" in scatto['label']:
        speach_alert("Baily")
            
    elif "HDR 1" in scatto['label']:
        if "Ciclo 1" in scatto['label']: speach_alert("C 1")
        elif "Ciclo 2" in scatto['label']: speach_alert("C 2")
        elif "Ciclo 3" in scatto['label']: speach_alert("C 3")
        
    elif "HDR 10 - Earthshine" in scatto['label']:
        speach_alert("Fine Ciclo")
        
    elif "Grani di Baily C3 (Senza Filtro)" in scatto['label'] and not promemoria_inserimento_inviato:
        msg = "🚨 REINSERIRE FILTRO ND 3.8 IMMEDIATAMENTE!"
        log_all("err", msg, CLR_BOLD + CLR_ERR)
        send_telegram_message(msg)
        speach_alert("Filter Warning")
        promemoria_inserimento_inviato = True

    execute_camera_command(scatto['shutter'], scatto['aperture'], scatto['iso'], scatto['label'])
    
    ora_inizio_attesa = get_ora_corretta_ora()
    time.sleep(0.05)

log_all("info", "🏁 Sequenza completata con successo!", CLR_BOLD + CLR_OK)
speach_alert("Fine sessione")