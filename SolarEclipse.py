import subprocess
import time
from datetime import datetime, timedelta
import os
import json
import urllib.request
import urllib.parse
import sys

# ==============================================================================
# CONFIGURAZIONE GLOBALE E DEBUG COLORE (DINAMICO)
# ==============================================================================
DEBUG_MODE = False  # Viene sovrascritto dall'input iniziale dell'utente

# Codici colore ANSI per la console
CLR_RESET = "\033[0m"
CLR_DEBUG = "\033[94m"    # Blu
CLR_INFO  = "\033[96m"    # Ciano
CLR_OK    = "\033[92m"    # Verde
CLR_WARN  = "\033[93m"    # Giallo
CLR_ERR   = "\033[91m"    # Rosso
CLR_BOLD  = "\033[1m"

def log_debug(msg):
    if DEBUG_MODE:
        print(f"{CLR_DEBUG}[DEBUG] {msg}{CLR_RESET}")

# Inizializzazione supporto colori su Windows Terminal / CMD vecchio
if os.name == 'nt':
    os.system('color')

# Chiedi all'utente se attivare il Debug all'avvio
print(f"{CLR_BOLD}{CLR_INFO}=== CONFIGURAZIONE SCRIPT ==={CLR_RESET}")
scelta_debug = input("Vuoi attivare la modalità DEBUG avanzata? (s/N): ").strip().lower()
if scelta_debug == 's':
    DEBUG_MODE = True
    print(f"{CLR_DEBUG}-> Modalità DEBUG Attivata.{CLR_RESET}\n")
else:
    DEBUG_MODE = False
    print(f"{CLR_WARN}-> Modalità DEBUG Disattivata (Solo log essenziali).{CLR_RESET}\n")

# ==============================================================================
# CONFIGURAZIONE ORARI ECLISSI 12 AGOSTO 2026
# ==============================================================================
C2_TIME = datetime(2026, 6, 20, 13, 45, 10)
C3_TIME = datetime(2026, 6, 20, 13, 46, 50)
#C2_TIME = datetime(2026, 8, 12, 20, 27, 10)
#C3_TIME = datetime(2026, 8, 12, 20, 28, 50)

PATH_TO_CMD = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
PORTA_SERVER = "2727" 

BASE_URL_SLC = f"http://127.0.0.1:{PORTA_SERVER}/?slc="
BASE_URL_CMD = f"http://127.0.0.1:{PORTA_SERVER}/?CMD="
SECRETS_FILE = "secrets.json"

# ==============================================================================
# SERVIZIO NOTIFICHE TELEGRAM
# ==============================================================================
BOT_TOKEN = None
CHAT_ID = None

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
    except Exception: pass

# ==============================================================================
# INTERFACCIA CHECKLIST
# ==============================================================================
def run_startup_checklist():
    print(f"\n{CLR_BOLD}{CLR_INFO}" + "="*60)
    print("   CHECKLIST CONFIGURAZIONE CONFIGURATA - ECLISSI 2026   ")
    print("="*60 + f"{CLR_RESET}")
    checklist = [
        ("ALIMENTAZIONE", "PC a rete/Powerbank e batteria Camera 100%."),
        ("CAVO DATI USB", "Cavo USB-C alta velocità collegato."),
        ("DIGICAMCONTROL", "Software aperto, Camera rilevata, LIVE VIEW CHIUSO."),
        ("WEB SERVER", f"Enable attivo nelle impostazioni sulla porta {PORTA_SERVER}."),
        ("FUOCO MANUALE (MF)", "Obiettivo su MF e ghiera bloccata."),
        ("RIVEDILE IMMAGINI", "Image Review su OFF nei menu della mirrorless."),
        ("FILTRO SOLARE", "Filtro ND 3.8 inserito per le fasi parziali.")
    ]
    for i, (titolo, descrizione) in enumerate(checklist, 1):
        input(f"[{i}/{len(checklist)}] {CLR_WARN}📌 {titolo}:{CLR_RESET} {descrizione}\n   [INVIO per confermare...]")
    send_telegram_message("🚀 *Script Online!* Timeline caricata e checklist superata.")

# ==============================================================================
# FUNZIONE DI SCATTO CON LOG DINAMICI
# ==============================================================================
def execute_camera_command(shutter, aperture, iso, label):
    shutter_clean = shutter.replace('"', '')
    val_raw = str(aperture).lower().replace('f', '').replace('/', '').replace(',', '.').strip()
    aperture_final = f"{val_raw}.0" if '.' not in val_raw else val_raw
    
    try:
        log_debug(f"Inizio sequenza per: {label}")
        
        # 1. Cambio Parametri via EXE
        log_debug(f"Esecuzione CLI -> Imposto ISO: {iso} | Shutter: {shutter_clean} | Aperture: {aperture_final}")
        subprocess.run([PATH_TO_CMD, "/c", f"set iso {iso}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([PATH_TO_CMD, "/c", f"set shutterspeed {shutter_clean}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([PATH_TO_CMD, "/c", f"set aperture {aperture_final}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. Blocco Download via Web Server (Sintassi ufficiale)
        url_folder = f"{BASE_URL_SLC}set&param1=session.folder&param2=None"
        url_download = f"{BASE_URL_SLC}set&param1=session.downloadonlyjpg&param2=false"
        
        log_debug(f"Invio blocco download -> URL cartella: {url_folder}")
        urllib.request.urlopen(url_folder, timeout=2).read()
        
        log_debug(f"Invio blocco trasferimento -> URL flag: {url_download}")
        urllib.request.urlopen(url_download, timeout=2).read()
        
        # Pausa stabilizzazione
        log_debug("Pausa di stabilizzazione elettronica (0.30s)...")
        time.sleep(0.30)
        
        # 3. Impulso di scatto finale via Web Server
        url_scatto = f"{BASE_URL_CMD}Capture"
        log_debug(f"Invio trigger scatto -> URL: {url_scatto}")
        urllib.request.urlopen(url_scatto, timeout=2).read()
        
        # Log di successo standard in verde (Sempre visibile)
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"{CLR_OK}[{timestamp}] 📸 {label} -> CONFIGURATO (ISO {iso} | {shutter_clean} | f/{aperture_final}){CLR_RESET}")
        send_telegram_message(f"📸 `{label}` scattata (Solo su SD).")
        
    except Exception as e:
        print(f"{CLR_ERR}❌ Errore critico su {label}: {e}{CLR_RESET}")

# ==============================================================================
# TIMELINE DI SCATTO AGGIORNATA
# ==============================================================================
script_data = """
TAKEPIC,C2,-,58:00,1,1/250,8,100,1,RAW,L,N,Parziale "C1" Primo Contatto -58 min
TAKEPIC,C2,-,40:00,1,1/250,8,100,1,RAW,L,N,Parziale -40 min
TAKEPIC,C2,-,20:00,1,1/250,8,100,1,RAW,L,N,Parziale -20 min
TAKEPIC,C2,-,10:00,1,1/250,8,100,1,RAW,L,N,Parziale -10 min
TAKEPIC,C2,-,05:00,1,1/250,8,100,1,RAW,L,N,Parziale -5 min
TAKEPIC,C2,-,00:05,1,1/100,8,400,3,RAW,L,N,Anello di Diamante C2
TAKEPIC,C2,-,00:02,1,1/3200,16,200,3,RAW,L,N,Grani di Baily C2
TAKEPIC,C2,+,00:00,1,1/4000,8,200,3,RAW,L,N,HDR 1 - Protuberanze
TAKEPIC,C2,+,00:02,1,1/1000,8,200,2,RAW,L,N,HDR 2 - Corona Interna
TAKEPIC,C2,+,00:04,1,1/250,8,200,2,RAW,L,N,HDR 3 - Corona Media
TAKEPIC,C2,+,00:06,1,1/60,8,200,2,RAW,L,N,HDR 4 - Corona Media Estesa
TAKEPIC,C2,+,00:08,1,1/15,8,200,2,RAW,L,N,HDR 5 - Corona Esterna
TAKEPIC,C2,+,00:10,1,1/4,8,200,2,RAW,L,N,HDR 6 - Strutture Profonde
TAKEPIC,C2,+,00:12,1,1,8,200,2,RAW,L,N,HDR 7 - Earthshine e Max Corona
TAKEPIC,C3,+,00:02,1,1/3200,16,200,3,RAW,L,N,Grani di Baily C3
TAKEPIC,C3,+,00:05,1,1/100,8,400,3,RAW,L,N,Anello di Diamond C3
TAKEPIC,C3,+,05:00,1,1/250,8,100,1,RAW,L,N,Parziale +5 min
TAKEPIC,C3,+,10:00,1,1/250,8,100,1,RAW,L,N,Parziale +10 min
TAKEPIC,C3,+,20:00,1,1/250,8,100,1,RAW,L,N,Parziale +20 min
TAKEPIC,C3,+,30:00,1,1/250,8,100,1,RAW,L,N,Parziale +30 min
"""

# ==============================================================================
# LOGICA DI CONTROLLO TEMPORALE
# ==============================================================================
cronoprogramma = []
for line in script_data.strip().split('\n'):
    parts = line.split(',')
    _, contatto, segno, offset_str, _, shutter, aperture, iso, _, _, _, _, commento = parts
    minuti, secondi = map(int, offset_str.split(':'))
    offset = timedelta(minutes=minuti, seconds=secondi)
    base_time = C2_TIME if contatto == "C2" else C3_TIME
    target_time = base_time + (offset if segno == "+" else -offset)
    cronoprogramma.append({'time': target_time, 'shutter': shutter, 'aperture': aperture, 'iso': iso, 'label': commento})

cronoprogramma.sort(key=lambda x: x['time'])
run_startup_checklist()
scatti_validi = [s for s in cronoprogramma if s['time'] > datetime.now()]

print(f"\n{CLR_BOLD}{CLR_INFO}🚀 Monitoraggio avviato. Scatti validi in coda: {len(scatti_validi)}{CLR_RESET}\n")

promemoria_rimozione_inviato = False
promemoria_inserimento_inviato = False

for scatto in scatti_validi:
    while datetime.now() < scatto['time']:
        tempo_rimanente = scatto['time'] - datetime.now()
        
        if scatto['label'] == "Anello di Diamante C2" and tempo_rimanente <= timedelta(minutes=4, seconds=50) and not promemoria_rimozione_inviato:
            msg = "⚠️ RIMUOVERE FILTRO ND 3.8 ORA!"
            print(f"\n{CLR_BOLD}{CLR_WARN}{msg}{CLR_RESET}\n")
            send_telegram_message(msg)
            promemoria_rimozione_inviato = True
        time.sleep(0.01)
        
    execute_camera_command(scatto['shutter'], scatto['aperture'], scatto['iso'], scatto['label'])
    
    if scatto['label'] == "Anello di Diamond C3" and not promemoria_inserimento_inviato:
        msg = "🚨 REINSERIRE FILTRO ND 3.8 IMMEDIATAMENTE!"
        print(f"\n{CLR_BOLD}{CLR_ERR}{msg}{CLR_RESET}\n")
        send_telegram_message(msg)
        promemoria_inserimento_inviato = True

    time.sleep(0.15)

print(f"\n{CLR_BOLD}{CLR_OK}🏁 Sequenza completata con successo!{CLR_RESET}")