import os
import sys
import time
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# ==============================================================================
# CONFIGURAZIONE GLOBALE
# ==============================================================================

CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
LOG_FILE = "eclipse_log.txt"

SIM_MODE = False        # Imposta su True per simulare l'intera eclissi a casa
SIM_SPEED_UP = 1.0      # Fattore di accelerazione per i test (lascia 1.0 in live)

# Orari locali dei 4 Contatti dell'Eclissi usare per test reale a casa
P1_START       = datetime_time(10, 30, 0)   
TOTALITY_START = datetime_time(10, 40, 0)   
TOTALITY_END   = datetime_time(10, 41, 45)  
P3_END         = datetime_time(10, 50, 0) 
'''
# Orari locali dei 4 Contatti dell'Eclissi in location
P1_START       = datetime_time(19, 30, 0)   
TOTALITY_START = datetime_time(20, 27, 0)   
TOTALITY_END   = datetime_time(20, 28, 45)  
P3_END         = datetime_time(21, 15, 0)   
'''
INTERVAL_INGRESS = 1080  
INTERVAL_EGRESS  = 690   

# --- PERCORSI FILE AUDIO LOCALIZZATI --- creare dei file audio ---
AUDIO_1_MIN          = r"C:\Eclissi\Audio\manca_un_minuto.wav"
AUDIO_TOGLI_FILTRO   = r"C:\Eclissi\Audio\togli_filtro.wav"
AUDIO_20_SEC         = r"C:\Eclissi\Audio\mancano_20_secondi.wav"
AUDIO_METTI_FILTRO   = r"C:\Eclissi\Audio\metti_filtro.wav"

# --- SCALETTA TEMPI PER DIAMOND RING BURST ---
SHUTTER_SPEEDS_BURST = ["1/8000", "1/4000", "1/2000", "1/1000"]

# --- SCALETTA TEMPI PER BRACKETING CORONA HDR ---
SHUTTER_SPEEDS_HDR = [
    "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", 
    "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "1/2", "1", "2", "4"
]

# ==============================================================================
# STRUMENTI DI SISTEMA (LOG, AUDIO, OROLOGIO)
# ==============================================================================

def log_message(message, level="INFO"):
    """Scrive il log a schermo e contemporaneamente sul file di testo d'emergenza"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    # Pulisce la riga del countdown prima di stampare un log fisso
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
    """Cambia il tempo di scatto sulla mirrorless usando la sintassi corretta"""
    if SIM_MODE:
        return True
    try:
        result = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", shutter_speed], capture_output=True, text=True)
        if "error" in result.stdout.lower() or result.returncode != 0:
            log_message(f"Errore hardware nel cambio tempo a {shutter_speed}: {result.stdout.strip()}", level="ERROR")
            return False
        time.sleep(0.15)  # Delay di sincronizzazione firmware
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
            log_message(f"Errore hardware durante lo scatto {phase_name}: {result.stdout.strip()}", level="ERROR")
            return False
        log_message(f"Scatto completato con successo: {phase_name}")
        return True
    except Exception as e:
        log_message(f"Fallimento critico subprocess su capture: {e}", level="ERROR")
        return False

# ==============================================================================
# VOCE 1: PRE-FLIGHT CHECKLIST (CONTROLLI INIZIALI MANDATORI)
# ==============================================================================

def run_preflight_checklist():
    print("=" * 70)
    print("                CHECKLIST DI SICUREZZA PRE-ECLISSI")
    print("=" * 70)
    
    # 1. Test di inizializzazione file di Log
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- NUOVA SESSIONE DI SCATTO: {datetime.now()} ---\n")
        print("[ OK ] File di log d'emergenza inizializzato correttamente.")
    except Exception as e:
        print(f"[FALLITO] Impossibile creare il file di log: {e}. Esco per sicurezza.")
        sys.exit(1)

    # 2. Test Audio hardware
    print("[... ] Avvio del test audio. Dovresti sentire un segnale acustico...")
    if not SIM_MODE:
        try:
            winsound.Beep(1000, 400)
        except:
            print("[AVVISO] Altoparlanti non disponibili o disattivati.")
    else:
        print("[ OK ] Test audio simulato superato.")

    # 3. Test di connessione USB reale con la Mirrorless
    if not SIM_MODE:
        print("[... ] Verifica comunicazione USB con la fotocamera...")
        test_speed = "1/2000"
        try:
            result = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", test_speed], capture_output=True, text=True)
            if "error" in result.stdout.lower() or result.returncode != 0:
                print(f"\n[ERRORE CRITICO] La mirrorless ha rifiutato il comando di test! Risposta: {result.stdout.strip()}")
                print("Verifica che la fotocamera sia accesa, su modalità 'M' e che il software digiCamControl sia aperto.")
                confirm = input("Vuoi forzare l'avvio dello script comunque? (s/n): ")
                if confirm.lower() != 's':
                    sys.exit(1)
            else:
                print(f"[ OK ] Comunicazione USB stabilita. Tempo impostato a {test_speed} con successo.")
        except Exception as e:
            print(f"[ERRORE] Impossibile eseguire CameraControlRemoteCmd.exe: {e}")
            sys.exit(1)
            
    # 4. Checklist Manuale per il fotografo
    checklist_items = [
        "Filtro Solare inserito saldamente sull'obiettivo?",
        "Messa a fuoco impostata su MANUALE (MF) e bloccata sulle stelle/sole?",
        "La ghiera di scatto della fotocamera è fisicamente su 'M' (Manuale)?",
        "Alimentazione PC e fotocamera collegate (Powerbank/Batterie cariche)?",
        "La mirrorless è impostata per salvare le foto *SOLO SU SCHEDA SD* interna?"
    ]
    
    print("\nConferma i seguenti punti fisici premendo INVIO:")
    for i, item in enumerate(checklist_items, 1):
        input(f"  [{i}/{len(checklist_items)}] {item} [Premi INVIO per confermare] ")
        
    print("\n[ SUCCESS ] Checklist completata. Avvio dell'automation engine tra 3 secondi...\n")
    time.sleep(3)

# ==============================================================================
# LOGICA DI AUTOMAZIONE PRINCIPALE CON COUNTDOWN DINAMICO (VOCE 2 E 3)
# ==============================================================================

def run_eclipse_automation():
    today = datetime.now().date()
    dt_c1 = datetime.combine(today, P1_START)
    dt_c2 = datetime.combine(today, TOTALITY_START)
    dt_c3 = datetime.combine(today, TOTALITY_END)
    dt_c4 = datetime.combine(today, P3_END)
    
    clock = SimClock(P1_START, speed_up=SIM_SPEED_UP, active=SIM_MODE)
    
    log_message("ENGINE ECLISSI ATTIVO - AGGIORNATO CON REQUISITI DI LIVE FIELD")
    
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
    last_countdown_update = 0
    
    while True:
        now = clock.get_now()
        timestamp_str = now.strftime('%H:%M:%S')
        
        # Intervallo del ciclo principale leggero
        time.sleep(0.05 if SIM_MODE else 0.1)
        
        # --- SEZIONE DEL COUNTDOWN DINAMICO IN TEMPO REALE (VOCE 2) ---
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
                sys.stdout.write(f"\r[{timestamp_str}] TOTALITÀ IN CORSO | Fine della totalità C3 tra: {str(diff).split('.')[0]} ")
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
                    
                # BURST C2 (Anello di Diamante Ingresso)
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
                
            # BURST C3 (Anello di Diamante Uscita)
            if time_to_c3 <= 2 and not c3_burst_done:
                log_message("INIZIO SEQUENZA BURST C3 (Diamond Ring Uscita)")
                for speed in SHUTTER_SPEEDS_BURST:
                    if set_shutter_speed(speed):
                        for shot in range(1, 6):
                            capture_image(f"Diamond_Ring_Uscita_{speed.replace('/', '_')}_S{shot}")
                c3_burst_done = True
            
            # Sequenza Bracketing Corona HDR Continua
            if time_to_c3 > 2:
                current_shutter = SHUTTER_SPEEDS_HDR[hdr_index]
                if set_shutter_speed(current_shutter):
                    capture_image("Corona_Totale_HDR")
                hdr_index = (hdr_index + 1) % len(SHUTTER_SPEEDS_HDR)
                
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
    # Avvia prima i controlli fisici e hardware, poi l'automazione temporizzata
    run_preflight_checklist()
    run_eclipse_automation()
