import subprocess
import time
from datetime import datetime, timedelta, timezone
import os
import json
import urllib.request
import urllib.parse
import sys
import email.utils

# ==============================================================================
# CONFIGURAZIONE GLOBALE, AGGIORNAMENTO E DEBUG COLORE
# ==============================================================================
DEBUG_MODE = False  
GITHUB_RAW_URL = "https://raw.githubusercontent.com/S85mario/Solar-Eclipse-Automation/main/SolarEclipse.py"

# Destinazione salvataggio foto: "1" = SD Camera | "0" = PC | "2" = Entrambi
TARGET_STORAGE = "1" 

# Codici colore ANSI per la console
CLR_RESET = "\033[0m"
CLR_DEBUG = "\033[94m"    
CLR_INFO  = "\033[96m"    
CLR_OK    = "\033[92m"    
CLR_WARN  = "\033[93m"    
CLR_ERR   = "\033[91m"    
CLR_BOLD  = "\033[1m"

def log_debug(msg):
    if DEBUG_MODE:
        print(f"{CLR_DEBUG}[DEBUG] {msg}{CLR_RESET}")

if os.name == 'nt':
    os.system('color')

# SINTESI VOCALE NATIVA WINDOWS (NON-BLOCKING)
def speach_alert(testo):
    """Fa parlare il PC in background senza bloccare il timing dello script"""
    command = f"Add-Type -AssemblyName System.Speech; $val = New-Object System.Speech.Synthesis.SpeechSynthesizer; $val.Speak('{testo}')"
    try:
        subprocess.Popen(['powershell', '-Command', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# FUNZIONE DI AGGIORNAMENTO AUTOMATICO DA GITHUB (FORZATO SENZA INPUT)
def check_for_updates():
    print(f"{CLR_BOLD}{CLR_INFO}🔄 VERIFICA AGGIORNAMENTO DA GITHUB...{CLR_RESET}")
    try:
        print(f"{CLR_INFO}Controllo della versione remota...{CLR_RESET}")
        req = urllib.request.Request(GITHUB_RAW_URL)
        with urllib.request.urlopen(req, timeout=5) as response:
            remote_code = response.read().decode('utf-8')
        
        # Legge il file locale corrente
        current_script_path = sys.argv[0]
        with open(current_script_path, 'r', encoding='utf-8') as f:
            local_code = f.read()
        
        if remote_code.strip() != local_code.strip():
            print(f"{CLR_BOLD}{CLR_WARN}⚠️ TROVATA NUOVA VERSIONE! Aggiornamento automatico in corso...{CLR_RESET}")
            
            # Scrive direttamente il nuovo codice sul file locale
            with open(current_script_path, 'w', encoding='utf-8') as f:
                f.write(remote_code)
                
            print(f"{CLR_BOLD}{CLR_OK}✅ Script aggiornato con successo! Riavvio automatico...{CLR_RESET}")
            speach_alert("Aggiornamento completato. Riavvio in corso.")
            
            # Esci con codice 5 per far ricascare il file .bat nel loop e farlo ripartire
            sys.exit(5)
        else:
            print(f"{CLR_OK}✅ Il codice è già aggiornato all'ultima versione di GitHub.{CLR_RESET}\n")
    except Exception as e:
        print(f"{CLR_ERR}❌ Impossibile verificare gli aggiornamenti: {e}{CLR_RESET}\n")

# Esegui subito il controllo aggiornamenti all'avvio
check_for_updates()

# Chiedi all'utente se attivare il Debug
print(f"{CLR_BOLD}{CLR_INFO}=== CONFIGURAZIONE DEBUG ==={CLR_RESET}")
scelta_debug = input("Vuoi attivare la modalità DEBUG avanzata? (s/N): ").strip().lower()
if scelta_debug == 's':
    DEBUG_MODE = True
    print(f"{CLR_DEBUG}-> Modalità DEBUG Attivata.{CLR_RESET}\n")
else:
    DEBUG_MODE = False
    print(f"{CLR_WARN}-> Modalità DEBUG Disattivata (Solo log essenziali).{CLR_RESET}\n")

# ==============================================================================
# CONFIGURAZIONE DINAMICA ORARI ECLISSI
# ==============================================================================
print(f"{CLR_BOLD}{CLR_INFO}=== IMPOSTAZIONE ORARI ECLISSI ==={CLR_RESET}")
print("1) Imposta Orari REALI (12 Agosto 2026)")
print("2) Imposta Orari TEST RAPIDO (Oggi - Qualche minuto nel futuro)")
print("3) Inserimento MANUALE personalizzato")
scelta_ora = input("Scegli un'opzione (1/2/3): ").strip()

now = datetime.now()

if scelta_ora == '1':
    C2_TIME = datetime(2026, 8, 12, 20, 27, 10)
    C3_TIME = datetime(2026, 8, 12, 20, 28, 50)
elif scelta_ora == '2':
    # Imposta automaticamente il test a +2 minuti da adesso per il C2 e +4 per il C3
    C2_TIME = now + timedelta(minutes=2)
    C3_TIME = now + timedelta(minutes=4)
else:
    print(f"\n{CLR_WARN}Inserisci i dati per l'orario personalizzato (Formato numerico):{CLR_RESET}")
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

print(f"\n{CLR_BOLD}{CLR_OK}⏱️ ORARI CONFIGURATI PER LA SESSIONE:{CLR_RESET}")
print(f"🔴 C2 (Inizio Totalità): {C2_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔵 C3 (Fine Totalità):   {C3_TIME.strftime('%Y-%m-%d %H:%M:%S')}\n")

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
# CONTROLLI PRE-FLIGHT (NTP CHECK & INTERFACCIA)
# ==============================================================================
def check_pc_clock_sync():
    print(f"\n{CLR_BOLD}{CLR_INFO}🌐 VERIFICA SINCRONIZZAZIONE ORA (NTP CHECK)...{CLR_RESET}")
    try:
        req = urllib.request.Request('https://www.google.com', method='HEAD')
        with urllib.request.urlopen(req, timeout=3) as response:
            date_header = response.headers.get('Date')
        if not date_header: return
        
        server_time = email.utils.parsedate_to_datetime(date_header)
        pc_time = datetime.now(timezone.utc)
        discrepanza = abs((pc_time - server_time).total_seconds())
        SOGLIA_MASSIMA = 1.0 
        
        if discrepanza > SOGLIA_MASSIMA:
            print(f"{CLR_BOLD}{CLR_ERR}❌ ERRORE CRITICO: L'orologio del PC è sballato di {discrepanza:.2f} secondi!{CLR_RESET}")
            speach_alert("Attenzione. Orologio del computer non sincronizzato.")
            scelta = input(f"{CLR_BOLD}Vuoi forzare l'avvio comunque? (y/N): {CLR_RESET}").strip().lower()
            if scelta != 'y': sys.exit()
        else:
            print(f"{CLR_OK}✅ Orologio synchronized! Discrepanza: {discrepanza:.2f} secondi.{CLR_RESET}\n")
    except Exception:
        print(f"{CLR_WARN}⚠️ Impossibile connettersi al server del tempo per il controllo orario.{CLR_RESET}")

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
        ("VISUALIZZAZIONE IMMAGINI", "Image Review su OFF nei menu della mirrorless."),
        ("FILTRO SOLARE", "Filtro ND 3.8 inserito per le fases parziali.")
    ]
    for i, (titolo, descrizione) in enumerate(checklist, 1):
        input(f"[{i}/{len(checklist)}] {CLR_WARN}📌 {titolo}:{CLR_RESET} {descrizione}\n   [INVIO per confermare...]")
    send_telegram_message("🚀 *Script Online!* Sincronizzazione completata e checklist superata.")
    speach_alert("Sistema online. Pronto per l'eclissi.")

# ==============================================================================
# FUNZIONE DI SCATTO
# ==============================================================================
def execute_camera_command(shutter, aperture, iso, label):
    shutter_clean = shutter.replace('"', '')
    val_raw = str(aperture).lower().replace('f', '').replace('/', '').replace(',', '.').strip()
    aperture_final = f"{val_raw}.0" if '.' not in val_raw else val_raw
    
    try:
        log_debug(f"Inizio sequenza per: {label}")
        
        url_iso = f"{BASE_URL_SLC}set&param1=iso&param2={iso}"
        url_aperture = f"{BASE_URL_SLC}set&param1=aperture&param2={aperture_final}"
        url_shutter = f"{BASE_URL_SLC}set&param1=shutterspeed&param2={urllib.parse.quote(shutter_clean)}"
        url_transfer = f"{BASE_URL_SLC}set&param1=transfer&param2={TARGET_STORAGE}"
        
        # Invio configurazioni
        urllib.request.urlopen(url_iso, timeout=2).read()
        time.sleep(0.05)
        urllib.request.urlopen(url_aperture, timeout=2).read()
        time.sleep(0.05)
        urllib.request.urlopen(url_shutter, timeout=2).read()
        time.sleep(0.05)
        urllib.request.urlopen(url_transfer, timeout=2).read()
        
        time.sleep(0.15)
        
        # Scatto
        url_premi = f"{BASE_URL_CMD}CaptureNoAf"
        url_rilascia = f"{BASE_URL_CMD}Release"
        
        log_debug("⬇️ Scatto avviato...")
        urllib.request.urlopen(url_premi, timeout=2).read()
        time.sleep(0.50) 
        urllib.request.urlopen(url_rilascia, timeout=2).read()
        
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"{CLR_OK}[{timestamp}] 📸 {label} -> ESEGUITO (ISO {iso} | {shutter_clean} | f/{aperture_final}){CLR_RESET}")
        send_telegram_message(f"📸 `{label}` eseguita.")
        
    except Exception as e:
        print(f"{CLR_ERR}❌ Errore critico su {label}: {e}{CLR_RESET}")

# ==============================================================================
# TIMELINE DI SCATTO GENERALE (3 CICLI HDR + FASI PARZIALI)
# ==============================================================================
script_data = """
TAKEPIC,C3,-,58:00,1,1/250,8,100,1,RAW,L,N,Parziale +58 min
TAKEPIC,C3,-,40:00,1,1/250,8,100,1,RAW,L,N,Parziale +40 min
TAKEPIC,C3,-,20:00,1,1/250,8,100,1,RAW,L,N,Parziale +20 min
TAKEPIC,C3,-,10:00,1,1/250,8,100,1,RAW,L,N,Parziale +10 min
TAKEPIC,C3,-,05:00,1,1/250,8,100,1,RAW,L,N,Parziale +5 min
TAKEPIC,C3,-,01:00,1,1/250,8,100,1,RAW,L,N,Parziale +1 min
TAKEPIC,C2,-,00:10,1,1/100,8,400,1,RAW,L,N,Grani di Baily C2
TAKEPIC,C2,-,00:08,1,1/100,8,400,1,RAW,L,N,Grani di Baily C2
TAKEPIC,C2,-,00:05,1,1/3200,16,200,1,RAW,L,N,Anello di Diamante C2
TAKEPIC,C2,-,00:02,1,1/3200,16,200,1,RAW,L,N,Anello di Diamante C2

TAKEPIC,C2,+,00:00,1,1/4000,8,200,1,RAW,L,N,Ciclo 1 - HDR 1 - Protuberanze
TAKEPIC,C2,+,00:02,1,1/1000,8,200,1,RAW,L,N,Ciclo 1 - HDR 2 - Corona Interna
TAKEPIC,C2,+,00:04,1,1/250,8,200,1,RAW,L,N,Ciclo 1 - HDR 3 - Corona Media
TAKEPIC,C2,+,00:06,1,1/60,8,200,1,RAW,L,N,Ciclo 1 - HDR 4 - Corona Media Estesa
TAKEPIC,C2,+,00:08,1,1/15,8,200,1,RAW,L,N,Ciclo 1 - HDR 5 - Corona Esterna
TAKEPIC,C2,+,00:10,1,1/4,8,200,1,RAW,L,N,Ciclo 1 - HDR 6 - Strutture Profonde
TAKEPIC,C2,+,00:12,1,1,8,200,1,RAW,L,N,Ciclo 1 - HDR 7 - Earthshine

TAKEPIC,C2,+,00:25,1,1/4000,8,200,1,RAW,L,N,Ciclo 2 - HDR 1 - Protuberanze
TAKEPIC,C2,+,00:27,1,1/1000,8,200,1,RAW,L,N,Ciclo 2 - HDR 2 - Corona Interna
TAKEPIC,C2,+,00:29,1,1/250,8,200,1,RAW,L,N,Ciclo 2 - HDR 3 - Corona Media
TAKEPIC,C2,+,00:31,1,1/60,8,200,1,RAW,L,N,Ciclo 2 - HDR 4 - Corona Media Estesa
TAKEPIC,C2,+,00:33,1,1/15,8,200,1,RAW,L,N,Ciclo 2 - HDR 5 - Corona Esterna
TAKEPIC,C2,+,00:35,1,1/4,8,200,1,RAW,L,N,Ciclo 2 - HDR 6 - Strutture Profonde
TAKEPIC,C2,+,00:37,1,1,8,200,1,RAW,L,N,Ciclo 2 - HDR 7 - Earthshine

TAKEPIC,C2,+,00:50,1,1/4000,8,200,1,RAW,L,N,Ciclo 3 - HDR 1 - Protuberanze
TAKEPIC,C2,+,00:52,1,1/1000,8,200,1,RAW,L,N,Ciclo 3 - HDR 2 - Corona Interna
TAKEPIC,C2,+,00:54,1,1/250,8,200,1,RAW,L,N,Ciclo 3 - HDR 3 - Corona Media
TAKEPIC,C2,+,00:56,1,1/60,8,200,1,RAW,L,N,Ciclo 3 - HDR 4 - Corona Media Estesa
TAKEPIC,C2,+,00:58,1,1/15,8,200,1,RAW,L,N,Ciclo 3 - HDR 5 - Corona Esterna
TAKEPIC,C2,+,01:00,1,1/4,8,200,1,RAW,L,N,Ciclo 3 - HDR 6 - Strutture Profonde
TAKEPIC,C2,+,01:02,1,1,8,200,1,RAW,L,N,Ciclo 3 - HDR 7 - Earthshine

TAKEPIC,C2,+,00:10,1,1/100,8,400,1,RAW,L,N,Grani di Baily C2
TAKEPIC,C2,+,00:08,1,1/100,8,400,1,RAW,L,N,Grani di Baily C2
TAKEPIC,C2,+,00:05,1,1/3200,16,200,1,RAW,L,N,Anello di Diamante C2
TAKEPIC,C2,+,00:02,1,1/3200,16,200,1,RAW,L,N,Anello di Diamante C2

TAKEPIC,C3,+,05:00,1,1/250,8,100,1,RAW,L,N,Parziale +5 min
TAKEPIC,C3,+,10:00,1,1/250,8,100,1,RAW,L,N,Parziale +10 min
TAKEPIC,C3,+,20:00,1,1/250,8,100,1,RAW,L,N,Parziale +20 min
TAKEPIC,C3,+,30:00,1,1/250,8,100,1,RAW,L,N,Parziale +30 min
"""
# ==============================================================================
# LOGICA DI CONTROLLO TEMPORALE (MAIN FLOW)
# ==============================================================================
cronoprogramma = []
for line in script_data.strip().split('\n'):
    if not line.strip(): continue
    parts = line.split(',')
    _, contatto, segno, offset_str, _, shutter, aperture, iso, _, _, _, _, commento = parts
    minuti, secondi = map(int, offset_str.split(':'))
    offset = timedelta(minutes=minuti, seconds=secondi)
    base_time = C2_TIME if contatto == "C2" else C3_TIME
    target_time = base_time + (offset if segno == "+" else -offset)
    cronoprogramma.append({'time': target_time, 'shutter': shutter, 'aperture': aperture, 'iso': iso, 'label': commento})

cronoprogramma.sort(key=lambda x: x['time'])

# Avvio controlli iniziali
run_startup_checklist()
check_pc_clock_sync()

scatti_validi = [s for s in cronoprogramma if s['time'] > datetime.now()]
print(f"\n{CLR_BOLD}{CLR_INFO}🚀 Monitoraggio avviato. Scatti validi in coda: {len(scatti_validi)}{CLR_RESET}\n")

promemoria_rimozione_inviato = False
promemoria_inserimento_inviato = False

for scatto in scatti_validi:
    # Ciclo di attesa preciso al millisecondo per lo scatto corrente
    while datetime.now() < scatto['time']:
        tempo_rimanente = scatto['time'] - datetime.now()
        
        # ALLARME FILTRO INGRESSO TOTALITÀ (A -4 minuti e 50 secondi dal C2)
        if scatto['label'] == "Anello di Diamante C2" and tempo_rimanente <= timedelta(minutes=4, seconds=50) and not promemoria_rimozione_inviato:
            msg = "⚠️ RIMUOVERE FILTRO ND 3.8 ORA!"
            print(f"\n{CLR_BOLD}{CLR_WARN}{msg}{CLR_RESET}\n")
            send_telegram_message(msg)
            speach_alert("Attenzione! Rimuovere il filtro solare adesso. Ripeto. Rimuovere il filtro solare immediatamente.")
            promemoria_rimozione_inviato = True
            
        time.sleep(0.01)
    
    # ==========================================================================
    # REGISTRO DEGLI ANNUNCI VOCALI (TEXT-TO-SPEECH)
    # ==========================================================================
    if scatto['label'] == "Anello di Diamante C2":
        speach_alert("Anello di diamante. Inizio della totalità.")
        
    elif scatto['label'] == "Grani di Baily C2":
        speach_alert("Grani di Baily in ingresso.")
        
    elif "HDR 1" in scatto['label']:
        nome_ciclo = scatto['label'].split(" - ")[0]
        speach_alert(f"Avvio {nome_ciclo} della corona.")
        
    elif scatto['label'] == "Grani di Baily C3":
        speach_alert("Grani di Baily in uscita.")
        
    elif scatto['label'] == "Anello di Diamond C3":
        speach_alert("Anello di diamante in uscita. Fine della totalità.")
        
    elif scatto['label'] == "Parziale +5 min":
        speach_alert("Esecuzione scatto parzialità. Più cinque minuti dal terzo contatto.")
        
    elif scatto['label'] == "Parziale +10 min":
        speach_alert("Esecuzione scatto parzialità. Più dieci minuti dal terzo contatto.")

    # Esecuzione fisica del comando sulla fotocamera
    execute_camera_command(scatto['shutter'], scatto['aperture'], scatto['iso'], scatto['label'])
    
    # ALLARME FILTRO USCITA TOTALITÀ (Subito dopo lo scatto C3)
    if scatto['label'] == "Anello di Diamond C3" and not promemoria_inserimento_inviato:
        msg = "🚨 REINSERIRE FILTRO ND 3.8 IMMEDIATAMENTE!"
        print(f"\n{CLR_BOLD}{CLR_ERR}{msg}{CLR_RESET}\n")
        send_telegram_message(msg)
        speach_alert("Pericolo! Reinserire il filtro solare immediatamente! Coprire l'obiettivo!")
        promemoria_inserimento_inviato = True

    # Piccolo cooldown per non intasare il loop di controllo
    time.sleep(0.15)

print(f"\n{CLR_BOLD}{CLR_OK}🏁 Sequenza completata con successo!{CLR_RESET}")
speach_alert("Tutti gli scatti in programma sono stati eseguiti. Sequenza completata con successo.")