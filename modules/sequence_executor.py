#!/usr/bin/env python3
"""
Esecuzione delle sequenze di scatti
"""

import time
import sys
from datetime import datetime, timedelta
from utils.logger import log_messaggio, log_debug
from utils.helpers import calc_pausa, salva_stato, emetti_suono
from utils.constants import (
    stats, P4_FINE, MODALITA_SIM_COMPRESSA,
    RAFAGA_SCATTI, stop_requested, pause_requested,
    TEMPI_HDR, TEMPI_BURST, TEMPI_CORONA_INTERNA, TEMPI_CORONA_ESTERNA,
    TEMPI_PROTUBERANZE, TEMPI_CORONA, TEMPI_PARZIALE,
    FATTORE_COMPRESSIONE, ATTESA_INIZIALE_SEC
)
from .telegram_notifier import invia_notifica_telegram_embed, check_telegram_commands
from .hardware_manager import imposta_tempo_scatto, scatta_foto, controlla_telemetria
from .time_manager import attesa_con_intervallo, attesa_con_compressione
from .config_manager import ottieni_config

def ottieni_lista_tempi(nome_lista):
    """Restituisce la lista dei tempi in base al nome"""
    mappa_liste = {
        "hdr": TEMPI_HDR,
        "burst": TEMPI_BURST,
        "corona_interna": TEMPI_CORONA_INTERNA,
        "corona_esterna": TEMPI_CORONA_ESTERNA,
        "protuberanze": TEMPI_PROTUBERANZE,
        "corona": TEMPI_CORONA,
        "parziale": TEMPI_PARZIALE
    }
    return mappa_liste.get(nome_lista, TEMPI_HDR)

def esegui_sequenza_scatti(nome_fase, lista_tempi, indice_partenza=0, usa_raffica=True, intervallo=0):
    """Esegue la sequenza di scatti per una fase"""
    global stats, stop_requested, pause_requested
    
    # FASE CON INTERVALLO (PRE-PARZIALE o POST-PARZIALE)
    if intervallo > 0:
        config = ottieni_config()
        durata_fase = None
        for fase in config["fasi_eclisse"]:
            if fase["nome"] == nome_fase:
                durata_fase = fase["durata_sec"]
                break
        
        if durata_fase:
            num_scatti = int(durata_fase / intervallo)
            tempo = lista_tempi[0]
            
            log_messaggio(f"🎬 INIZIO {nome_fase} - {num_scatti} scatti ogni {intervallo//60} minuti")
            
            for i in range(num_scatti):
                check_telegram_commands()
                
                while pause_requested and not stop_requested:
                    time.sleep(1)
                if stop_requested:
                    log_messaggio("🛑 STOP richiesto!", "WARN")
                    sys.exit(0)
                
                etichetta = f"{nome_fase}_{tempo}_shot{i+1}"
                if imposta_tempo_scatto(tempo):
                    if scatta_foto(etichetta):
                        log_messaggio(f"📸 {etichetta} ({i+1}/{num_scatti})")
                        controlla_telemetria()
                
                if i < num_scatti - 1:
                    log_messaggio(f"⏳ Prossimo scatto tra {intervallo//60} minuti...")
                    attesa_con_intervallo(intervallo, "Prossimo scatto")
            
            log_messaggio(f"✅ COMPLETATA {nome_fase}")
            stats['fasi_completate'] += 1
            return num_scatti - 1
    
    # FASE NORMALE (totalità o burst)
    if indice_partenza >= len(lista_tempi):
        log_messaggio(f"Fase {nome_fase} già completata", "INFO")
        return len(lista_tempi) - 1
    
    log_messaggio(f"🎬 INIZIO {nome_fase} - {len(lista_tempi)-indice_partenza} esposizioni rimaste")
    
    for i, tempo in enumerate(lista_tempi[indice_partenza:], indice_partenza):
        check_telegram_commands()
        
        while pause_requested and not stop_requested:
            time.sleep(1)
        if stop_requested:
            log_messaggio("🛑 STOP richiesto!", "WARN")
            sys.exit(0)
        
        if MODALITA_SIM_COMPRESSA:
            from utils.constants import P4_SIM
            if datetime.now() > P4_SIM:
                log_messaggio(f"📅 Eclisse simulata terminata, interrompo {nome_fase}")
                return i - 1
        else:
            from utils.constants import P4_FINE
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

def run_automazione_normale():
    """Esecuzione normale (tempo reale)"""
    global stats
    
    from utils.helpers import carica_stato
    from utils.constants import P1_INIZIO, TOTALITA_INIZIO, TOTALITA_FINE, P4_FINE
    from .time_manager import attesa_fino_a
    
    log_messaggio("🚀 MOTORE ECLISSE ATTIVO - MODALITA' REALE")
    invia_notifica_telegram_embed("🚀 SCRIPT AVVIATO", "Modalità REALE", "🟢")
    
    stato = carica_stato()
    fase_ripresa = stato.get('fase') if stato else None
    indice_ripresa = stato.get('indice', 0) if stato else 0
    
    config = ottieni_config()
    fasi_config = config["fasi_eclisse"]
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
        intervallo = fase.get("intervallo_scatti", 0)
        
        fasi.append((
            fase["nome"],
            orario,
            fase["durata_sec"],
            lista_tempi,
            fase["usa_raffica"],
            intervallo
        ))
    
    for nome_fase, tempo_inizio, durata_sec, tempi_scatto, usa_raffica, intervallo in fasi:
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
        
        ultimo_indice = esegui_sequenza_scatti(nome_fase, tempi_scatto, indice_partenza, usa_raffica, intervallo)
        
        if ultimo_indice >= len(tempi_scatto) - 1:
            import os
            from utils.constants import STATO_FILE
            if os.path.exists(STATO_FILE):
                os.remove(STATO_FILE)
    
    log_messaggio("🎉 ECLISSE COMPLETATA! 🎉")
    emetti_suono("completamento")

def run_simulazione_compressa():
    """Esegue la simulazione completa con tempo compresso"""
    global stats, MODALITA_SIM_COMPRESSA, SIM_MODE
    
    from utils.constants import P1_INIZIO, TOTALITA_INIZIO, TOTALITA_FINE, P4_FINE
    from modules.hardware_manager import scatta_foto_simulazione
    
    # Assicura che siamo in modalità simulazione
    SIM_MODE = True
    MODALITA_SIM_COMPRESSA = True
    
    log_messaggio("🚀 SIMULAZIONE ECLISSE CON TEMPO COMPRESSO")
    invia_notifica_telegram_embed("🧪 SIMULAZIONE AVVIATA", f"Compressione {FATTORE_COMPRESSIONE}x", "🟢")
    
    fattore = FATTORE_COMPRESSIONE
    log_messaggio(f"🔧 SIMULAZIONE CON COMPRESSIONE {fattore}x")
    log_messaggio(f"   {fattore} secondi reali = 1 minuto di eclisse")
    
    # Calcola i timing simulati
    now = datetime.now()
    
    def time_to_seconds(t):
        return t.hour * 3600 + t.minute * 60 + t.second
    
    def secondi_da_p1(ora_reale):
        p1_sec = time_to_seconds(P1_INIZIO)
        evento_sec = time_to_seconds(ora_reale)
        return evento_sec - p1_sec
    
    # P1 inizia dopo ATTESA_INIZIALE_SEC secondi
    tempo_p1 = now + timedelta(seconds=ATTESA_INIZIALE_SEC)
    tempo_c2 = tempo_p1 + timedelta(seconds=secondi_da_p1(TOTALITA_INIZIO) / fattore)
    tempo_c3 = tempo_p1 + timedelta(seconds=secondi_da_p1(TOTALITA_FINE) / fattore)
    tempo_p4 = tempo_p1 + timedelta(seconds=secondi_da_p1(P4_FINE) / fattore)
    
    log_messaggio(f"\n📅 TIMING SIMULAZIONE:")
    log_messaggio(f"   P1: tra {ATTESA_INIZIALE_SEC} secondi")
    log_messaggio(f"   C2: tra {(tempo_c2 - now).total_seconds():.1f} secondi")
    log_messaggio(f"   C3: tra {(tempo_c3 - now).total_seconds():.1f} secondi")
    log_messaggio(f"   P4: tra {(tempo_p4 - now).total_seconds():.1f} secondi")
    
    # Attesa iniziale
    log_messaggio(f"\n⏳ Attesa iniziale di {ATTESA_INIZIALE_SEC} secondi...")
    for i in range(ATTESA_INIZIALE_SEC, 0, -1):
        print(f"\r   Partenza tra {i} secondi...", end='')
        time.sleep(1)
    print("\r   ✅ Via!                      ")
    
    # Intervallo per scatti parziali (15 minuti reali = 900/fattore secondi simulati)
    intervallo_parziale_sim = max(1, int(900 / fattore))
    log_messaggio(f"\n📸 Intervallo tra scatti parziali: {intervallo_parziale_sim} secondi reali")
    
    # Tempo per le fasi parziali
    tempo_parziale = "1/2000"
    log_messaggio(f"   Tempo scatto per fasi parziali: {tempo_parziale}")
    
    # === PRE-PARZIALE (ingresso) ===
    attesa_fase = (tempo_p1 - datetime.now()).total_seconds()
    if attesa_fase > 0:
        log_messaggio(f"\n⏳ Attesa {attesa_fase:.1f} secondi per PRE-PARZIALE...")
        time.sleep(attesa_fase)
    
    log_messaggio(f"\n🎬 INIZIO PRE-PARZIALE (ingresso)")
    for i in range(3):
        etichetta = f"PRE-PARZIALE_{tempo_parziale}_shot{i+1}"
        scatta_foto_simulazione(etichetta)
        log_messaggio(f"📸 {etichetta} ({i+1}/3)")
        
        if i < 2:
            log_messaggio(f"⏳ Prossimo scatto tra {intervallo_parziale_sim} secondi...")
            time.sleep(intervallo_parziale_sim)
    
    log_messaggio(f"✅ COMPLETATA PRE-PARZIALE (ingresso)")
    stats['fasi_completate'] += 1
    
    # === ANELLO DIAMANTE (ingresso) ===
    attesa_c2 = (tempo_c2 - datetime.now()).total_seconds()
    if attesa_c2 > 0:
        log_messaggio(f"\n⏳ Attesa {attesa_c2:.1f} secondi per ANELLO DIAMANTE...")
        time.sleep(attesa_c2)
    
    log_messaggio(f"\n🎬 INIZIO ANELLO DIAMANTE (ingresso)")
    for tempo in TEMPI_BURST:
        for scatto in range(RAFAGA_SCATTI):
            etichetta = f"ANELLO_DIAMANTE_IN_{tempo}_shot{scatto+1}"
            scatta_foto_simulazione(etichetta)
            log_messaggio(f"📸 {etichetta}")
            time.sleep(0.1)
    log_messaggio(f"✅ COMPLETATA ANELLO DIAMANTE (ingresso)")
    stats['fasi_completate'] += 1
    
    # === TOTALITA' - CORONA INTERNA ===
    log_messaggio(f"\n🎬 INIZIO TOTALITA' - CORONA INTERNA")
    for tempo in TEMPI_CORONA_INTERNA:
        etichetta = f"TOTALITA_INTERNA_{tempo}"
        scatta_foto_simulazione(etichetta)
        log_messaggio(f"📸 {etichetta}")
        time.sleep(calc_pausa(tempo) / 10)
    log_messaggio(f"✅ COMPLETATA TOTALITA' - CORONA INTERNA")
    stats['fasi_completate'] += 1
    
    # === TOTALITA' - CORONA ESTERNA ===
    log_messaggio(f"\n🎬 INIZIO TOTALITA' - CORONA ESTERNA")
    for tempo in TEMPI_CORONA_ESTERNA:
        etichetta = f"TOTALITA_ESTERNA_{tempo}"
        scatta_foto_simulazione(etichetta)
        log_messaggio(f"📸 {etichetta}")
        time.sleep(calc_pausa(tempo) / 10)
    log_messaggio(f"✅ COMPLETATA TOTALITA' - CORONA ESTERNA")
    stats['fasi_completate'] += 1
    
    # === ANELLO DIAMANTE (uscita) ===
    attesa_c3 = (tempo_c3 - datetime.now()).total_seconds()
    if attesa_c3 > 0:
        log_messaggio(f"\n⏳ Attesa {attesa_c3:.1f} secondi per ANELLO DIAMANTE (uscita)...")
        time.sleep(attesa_c3)
    
    log_messaggio(f"\n🎬 INIZIO ANELLO DIAMANTE (uscita)")
    for tempo in TEMPI_BURST:
        for scatto in range(RAFAGA_SCATTI):
            etichetta = f"ANELLO_DIAMANTE_OUT_{tempo}_shot{scatto+1}"
            scatta_foto_simulazione(etichetta)
            log_messaggio(f"📸 {etichetta}")
            time.sleep(0.1)
    log_messaggio(f"✅ COMPLETATA ANELLO DIAMANTE (uscita)")
    stats['fasi_completate'] += 1
    
    # === POST-PARZIALE (uscita) ===
    attesa_post = (tempo_p4 - datetime.now()).total_seconds()
    if attesa_post > 0:
        log_messaggio(f"\n⏳ Attesa {attesa_post:.1f} secondi per POST-PARZIALE...")
        time.sleep(attesa_post)
    
    log_messaggio(f"\n🎬 INIZIO POST-PARZIALE (uscita)")
    for i in range(3):
        etichetta = f"POST-PARZIALE_{tempo_parziale}_shot{i+1}"
        scatta_foto_simulazione(etichetta)
        log_messaggio(f"📸 {etichetta} ({i+1}/3)")
        
        if i < 2:
            log_messaggio(f"⏳ Prossimo scatto tra {intervallo_parziale_sim} secondi...")
            time.sleep(intervallo_parziale_sim)
    
    log_messaggio(f"✅ COMPLETATA POST-PARZIALE (uscita)")
    stats['fasi_completate'] += 1
    
    log_messaggio("\n🎉 SIMULAZIONE ECLISSE COMPLETATA! 🎉")
    emetti_suono("completamento")
    invia_notifica_telegram_embed("🎉 SIMULAZIONE COMPLETATA", "Test completato con successo!", "🟢")
    
    # Report finale statistiche
    log_messaggio(f"\n📊 STATISTICHE SIMULAZIONE:")
    log_messaggio(f"   Fasi completate: {stats['fasi_completate']}/6")
    log_messaggio(f"   Scatti totali: {stats['totale_scatti_eseguiti']}")
    log_messaggio(f"   Scatti riusciti: {stats['scatti_riusciti']}")