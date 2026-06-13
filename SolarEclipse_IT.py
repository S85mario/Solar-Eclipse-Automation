import os
import sys
import time
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# ==============================================================================
# CONFIGURAZIONE FOTOCAMERA E MARCHIO
# ==============================================================================

# Scegli il tuo marchio: "CANON", "NIKON" oppure "SONY"
CAMERA_BRAND = "CANON"  

# --- PROFILI CODIFICA TEMPI HDR PER BRAND ---
# digiCamControl interpreta la riga di comando in base al protocollo del firmware nativo.
SHUTTER_PROFILES = {
    "CANON": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "0.5",  # Notazione decimale nativa Canon
        "1"
    ],
    "NIKON": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "1/2",  # Notazione frazionaria standard Nikon
        "1"
    ],
    "SONY": [
        "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
        "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", 
        "1/2",  # Sony (via MTP/Remote) solitamente si allinea allo standard frazionario
        "1"
    ]
}

# Assegnazione dinamica della scaletta HDR in base al brand selezionato
if CAMERA_BRAND.upper() in SHUTTER_PROFILES:
    SHUTTER_SPEEDS_HDR = SHUTTER_PROFILES[CAMERA_BRAND.upper()]
else:
    print(f"[ERRORE CRITICO] Marchio '{CAMERA_BRAND}' non supportato. Uso profilo standard CANON.")
    SHUTTER_SPEEDS_HDR = SHUTTER_PROFILES["CANON"]

# ==============================================================================
# CONFIGURAZIONE GLOBALE SISTEMA
# ==============================================================================

GUI_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControl.exe"
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
LOG_FILE = "eclipse_log.txt"

SIM_MODE = False        
SIM_SPEED_UP = 1.0      

# Orari locali dei 4 Contatti dell'Eclissi
P1_START       = datetime_time(19, 30, 0)   
TOTALITY_START = datetime_time(20, 27, 0)   
TOTALITY_END   = datetime_time(20, 28, 45)  
P3_END         = datetime_time(21, 15, 0)   

INTERVAL_INGRESS = 1080  
INTERVAL_EGRESS  = 690   

# --- PERCORSI FILE AUDIO LOCALIZZATI ---
AUDIO_1_MIN          = r"C:\Eclissi\Audio\manca_un_minuto.wav"
AUDIO_TOGLI_FILTRO   = r"C:\Eclissi\Audio\togli_filtro.wav"
AUDIO_20_SEC         = r"C:\Eclissi\Audio\mancano_20_secondi.wav"
AUDIO_METTI_FILTRO   = r"C:\Eclissi\Audio\metti_filtro.wav"

# --- SCALETTA TEMPI PER DIAMOND RING BURST ---
SHUTTER_SPEEDS_BURST = ["1/8000", "1/4000", "1/2000", "1/1000"]

# ==============================================================================
# STRUMENTI DI SISTEMA (AVVIO SOFTWARE, LOG, AUDIO, OROLOGIO)
# ==============================================================================

def start_digicamcontrol():
    """Avvia automaticamente l'interfaccia grafica di digiCamControl in background"""
    if SIM_MODE:
        log_message("[SIM] Avvio automatico di digiCamControl simulato.")
        return
        
    log_message(f"Verifica stato digiCamControl per profilo {CAMERA_BRAND}...")
    if os.path.exists(GUI_PATH):
        try:
            subprocess.Popen([GUI_PATH])
            log_message("Applicazione digiCamControl lanciata con successo.")
            log_message("Attesa di 5 secondi per l'inizializzazione dell'handshake USB...")
            time.sleep(5)
        except Exception as e:
            log_message(f"Incapace di avviare digiCamControl automaticamente: {e}", level="ERROR")
    else:
        log_message(f"Eseguibile GUI non trovato al percorso specificato: {GUI_PATH}", level="ERROR")


def log_message(message, level="INFO"):
    """Scrive il log a schermo e contemporaneamente sul file di testo d'emergenza"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    
    print(formatted_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception as e:
        print(f"[ERRORE SCRITTURA LOG] Impossibile scrivere su file: {e}")


class SimClock:
    def __init__(self, start_time_obj, speed_up=1.0, active=False):
        self.active = active
        self.speed_up = speed_up
        self.real_start = time.time()
        today = datetime.now().date()
        anchor_dt = datetime.combine(today, start_time_obj)
        self.sim_start_dt = anchor_dt - timedelta(minutes=1)
        
    def get_now(self):
        if not self.active:
            return datetime.now()
        elapsed_real = time.time() - self.real_start
        elapsed_sim = elapsed_real * self.speed_up
        return self.sim_start_dt + timedelta(seconds=elapsed_sim)


def play_alert(file_path):
    if SIM_MODE:
        log_message(f"[SIM - AUDIO] Riproduzione: {os.path.basename(file_path)}")
        return
    try:
        winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        log_message(f"Impossibile riprodurre file audio {os.path.basename(file_path)}: {e}", level="ERROR")


def set_shutter_speed(shutter_speed):
    """Cambia il tempo di scatto sulla fotocamera usando la sintassi corretta per il brand"""
    if SIM_MODE:
        return True
    try:
        result = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", shutter_speed], capture_output=True, text=True)
        if "error" in result.stdout.lower() or result.returncode != 0:
            log_message(f"Errore hardware [{CAMERA_BRAND}] nel cambio tempo a {shutter_speed}: {result.stdout.strip()}", level="ERROR")
            return False
        time.sleep(0.15)  
        return True
    except Exception as e:
        log_message(f"Fallimento critico subprocess su set shutterspeed: {e}", level="ERROR")
        return False


def capture_image(phase_name):
    """Invia il comando di scatto puro"""
    if SIM_MODE:
        log_message(f"[SIM] Scatto eseguito: {phase_name}")
        return True
    try:
        result = subprocess.run([CMD_PATH, "/c", "capture"], capture_output=True, text=True)
        if "error" in result.stdout.lower() or result.returncode != 0:
            log_message(f"Errore hardware [{CAMERA_BRAND}] durante lo scatto {phase_name}: {result.stdout.strip()}", level="ERROR")
            return False
        log_message(f"Scatto completato con successo: {phase_name}")
        return True
    except Exception as e:
        log_message(f"Fallimento critico subprocess su capture: {e}", level="ERROR")
        return False


def run_preflight_checklist():
    # ----------------------------------------------------------------------
    # STEP DI CONNESSIONE OBBLIGATORI (ANTI-BLOCCO USB)
    # ----------------------------------------------------------------------
    print("\n" + "!" * 75)
    print("      ATTENZIONE: PROCEDURA DI CONNESSIONE HARDWARE OBBLIGATORIA")
    print("!" * 75)
    print(f"  FOTOCAMERA SELEZIONATA: Profilo {CAMERA_BRAND}")
    print("  1. ACCENDI LA FOTOCAMERA (assicurati che sia in modalità 'M').")
    print("  2. COLLEGA IL CAVO USB al computer solo dopo averla accesa.")
    print("  3. SE DA ERRORE DI CONNESSIONE:")
    print("     -> Rimuovi la batteria della fotocamera, reinseriscila e ripeti.")
    print("!" * 75)
    input("\nHai eseguito la sequenza corretta? [Premi INVIO per confermare ed andare avanti] ")
    print("\n" + "=" * 70)
    print("                CHECKLIST DI SICUREZZA PRE-ECLISSI")
    print("=" * 70)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- NUOVA SESSIONE DI SCATTO ({CAMERA_BRAND}): {datetime.now()} ---\n")
        print("[ OK ] File di log d'emergenza inizializzato correttamente.")
    except Exception as e:
        print(f"[FALLITO] Impossibile creare il file di log: {e}. Esco per sicurezza.")
        sys.exit(1)

    print("[... ] Avvio del test audio. Dovresti sentire un segnale acustico...")
    if not SIM_MODE:
        try:
            winsound.Beep(1000, 400)
        except:
            print("[AVVISO] Altoparlanti non disponibili o disattivati.")
    else:
        print("[ OK ] Test audio simulato superato.")

    if not SIM_MODE:
        print(f"[... ] Verifica comunicazione USB con fotocamera {CAMERA_BRAND}...")
        test_speed = "1/2000"
        try:
            result = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", test_speed], capture_output=True, text=True)
            if "error" in result.stdout.lower() or result.returncode != 0:
                print(f"\n[ERRORE CRITICO] La fotocamera {CAMERA_BRAND} ha rifiutato il comando di test! Risposta: {result.stdout.strip()}")
                print("Verifica la sequenza di accensione o la compatibilità del driver in digiCamControl.")
                confirm = input("Vuoi forzare l'avvio dello script comunque? (s/n): ")
                if confirm.lower() != 's':
                    sys.exit(1)
            else:
                print(f"[ OK ] Comunicazione USB stabilita. Tempo impostato a {test_speed} con successo.")
        except Exception as e:
            print(f"[ERRORE] Impossibile eseguire CameraControlRemoteCmd.exe: {e}")
            sys.exit(1)
            
    checklist_items = [
        "Filtro Solare inserito saldamente sull'obiettivo?",
        "Messa a fuoco impostata su MANUALE (MF) e bloccata sulle stelle/sole?",
        "La ghiera di scatto della fotocamera è fisicamente su 'M' (Manuale)?",
        "Alimentazione PC e fotocamera collegate (Powerbank/Batterie cariche)?",
        f"La macchina [{CAMERA_BRAND}] è impostata per salvare le foto *SOLO SU SCHEDA SD* interna?"
    ]
    
    print("\nConferma i seguenti punti fisici premendo INVIO:")
    for i, item in enumerate(checklist_items, 1):
        input(f"  [{i}/{len(checklist_items)}] {item} [Premi INVIO per confermare] ")
        
    print(f"\n[ SUCCESS ] Checklist completata per {CAMERA_BRAND}. Avvio dell'automation engine tra 3 secondi...\n")
    time.sleep(3)

# ==============================================================================
# LOGICA DI AUTOMAZIONE PRINCIPALE
# ==============================================================================

def run_eclipse_automation():
    today = datetime.now().date()
    dt_c1 = datetime.combine(today, P1_START)
    dt_c2 = datetime.combine(today, TOTALITY_START)
    dt_c3 = datetime.combine(today, TOTALITY_END)
    dt_c4 = datetime.combine(today, P3_END)
    
    clock = SimClock(P1_START, speed_up=SIM_SPEED_UP, active=SIM_MODE)
    
    log_message(f"ENGINE ECLISSI ATTIVO [PROFILO: {CAMERA_BRAND}]")
    
    last_ingress_shot = dt_c1
    last_egress_shot = None
    ingress_captured_count = 0
    egress_captured_count = 0
    
    alert_1m_done = False
    alert_12s_done = False
    alert_20s_done = False
    alert_c3_done = False
    c2_burst_done = False
    c3_burst_done = False
    
    hdr_index = 0
    hdr_shot_count = 0
    hdr_sequence_done = False
    
    last_countdown_update = 0
    
    while True:
        now = clock.get_now()
        timestamp_str = now.strftime('%H:%M:%S')
        
        time.sleep(0.05 if SIM_MODE else 0.1)
        
        current_epoch = time.time()
        if current_epoch - last_countdown_update >= 1.0:
            last_countdown_update = current_epoch
            if now < dt_c1:
                diff = dt_c1 - now
                sys.stdout.write(f"\r[{timestamp_str}] In attesa del Contatto C1: -{str(diff).split('.')[0]} ")
            elif now < dt_c2 and not c2_burst_done:
                diff = dt_c2 - now
                sys.stdout.write(f"\r[{timestamp_str}] Fase Parziale (Ingresso) | Tempo a C2: -{str(diff).split('.')[0]} ")
            elif now < dt_c3 and not c3_burst_done:
                diff = dt_c3 - now
                status_hdr = "In attesa" if hdr_sequence_done else f"Progresso {hdr_index}/{len(SHUTTER_SPEEDS_HDR)}"
                sys.stdout.write(f"\r[{timestamp_str}] TOTALITÀ ({CAMERA_BRAND}) | HDR: {status_hdr} | Fine C3 tra: {str(diff).split('.')[0]} ")
            elif now < dt_c4:
                diff = dt_c4 - now
                sys.stdout.write(f"\r[{timestamp_str}] Fase Parziale (Uscita) | Fine Eclissi C4 tra: {str(diff).split('.')[0]} ")
            sys.stdout.flush()

        if now < dt_c1:
            continue
            
        # ----------------------------------------------------------------------
        # FASE 2: ECLISSI PARZIALE INGRESSO (C1 -> C2)
        # ----------------------------------------------------------------------
        elif dt_c1 <= now < dt_c2:
            time_to_c2 = (dt_c2 - now).total_seconds()
            
            if time_to_c2 <= 60:
                if time_to_c2 <= 60 and not alert_1m_done:
                    log_message("T-60s a C2: Riproduzione avviso vocale.")
                    play_alert(AUDIO_1_MIN)
                    alert_1m_done = True
                    
                if time_to_c2 <= 12 and not alert_12s_done:
                    log_message("T-12s: RIMOZIONE FILTRO SOLARE ORA!")
                    play_alert(AUDIO_TOGLI_FILTRO)
                    alert_12s_done = True
                    
                if time_to_c2 <= 4 and not c2_burst_done:
                    log_message("INIZIO SEQUENZA BURST C2 (Diamond Ring & Baily's Beads)")
                    for speed in SHUTTER_SPEEDS_BURST:
                        if set_shutter_speed(speed):
                            for shot in range(1, 6):
                                capture_image(f"Diamond_Ring_Ingresso_{speed.replace('/', '_')}_S{shot}")
                    c2_burst_done = True
            else:
                if (now - last_ingress_shot).total_seconds() >= INTERVAL_INGRESS or ingress_captured_count == 0:
                    log_message(f"Scatto automatico Parziale Ingresso #{ingress_captured_count + 1}")
                    capture_image("Parziale_Ingresso")
                    last_ingress_shot = now
                    ingress_captured_count += 1
                    
        # ----------------------------------------------------------------------
        # FASE 3: TOTALITÀ CORE (C2 -> C3)
        # ----------------------------------------------------------------------
        elif dt_c2 <= now < dt_c3:
            time_to_c3 = (dt_c3 - now).total_seconds()
            
            if time_to_c3 <= 20 and not alert_20s_done:
                log_message("T-20s a C3: Avviso fine totalità imminente.")
                play_alert(AUDIO_20_SEC)
                alert_20s_done = True
                
            if time_to_c3 <= 2 and not c3_burst_done:
                log_message("INIZIO SEQUENZA BURST C3 (Diamond Ring Uscita)")
                for speed in SHUTTER_SPEEDS_BURST:
                    if set_shutter_speed(speed):
                        for shot in range(1, 6):
                            capture_image(f"Diamond_Ring_Uscita_{speed.replace('/', '_')}_S{shot}")
                c3_burst_done = True
            
            if time_to_c3 > 2 and not hdr_sequence_done:
                current_shutter = SHUTTER_SPEEDS_HDR[hdr_index]
                
                if hdr_shot_count == 0:
                    set_shutter_speed(current_shutter)
                
                shot_num = hdr_shot_count + 1
                clean_shutter_name = current_shutter.replace('/', '_').replace('.', '_')
                capture_image(f"Corona_Totale_HDR_{clean_shutter_name}_S{shot_num}")
                
                hdr_shot_count += 1
                if hdr_shot_count >= 2:
                    hdr_shot_count = 0  
                    hdr_index += 1      
                    
                    if hdr_index >= len(SHUTTER_SPEEDS_HDR):
                        log_message("FINE SEQUENZA BRACKETING CORONA HDR. Tutti i tempi eseguiti doppi. Macchina in stand-by.")
                        hdr_sequence_done = True
                
        # ----------------------------------------------------------------------
        # FASE 4: ECLISSI PARZIALE USCITA (C3 -> C4)
        # ----------------------------------------------------------------------
        elif dt_c3 <= now <= dt_c4:
            if not alert_c3_done:
                log_message("C3 Superato: RIPRISTINARE IL FILTRO SOLARE IMMEDIATAMENTE!")
                play_alert(AUDIO_METTI_FILTRO)
                alert_c3_done = True
                last_egress_shot = now
                
            if (now - last_egress_shot).total_seconds() >= INTERVAL_EGRESS or egress_captured_count == 0:
                log_message(f"Scatto automatico Parziale Uscita #{egress_captured_count + 1}")
                capture_image("Parziale_Uscita")
                last_egress_shot = now
                egress_captured_count += 1
                
        else:
            log_message("Contatto C4 superato. Fine dell'eclissi. Automazione terminata.")
            break

if __name__ == "__main__":
    start_digicamcontrol()
    run_preflight_checklist()
    run_eclipse_automation()