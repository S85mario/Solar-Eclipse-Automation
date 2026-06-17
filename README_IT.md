================================================================================
                    SOLAR ECLIPSE AUTOMATION SCRIPT
================================================================================

Script professionale per l'automazione della fotografia durante un'eclissi solare totale

Python 3.8+ | Windows | digiCamControl

================================================================================
                              INDICE
================================================================================

1.  Panoramica
2.  Funzionalità
3.  Requisiti
4.  Installazione
5.  Configurazione
6.  Utilizzo
7.  Sequenza Temporale
8.  Struttura File
9.  Logging
10. Risoluzione Problemi
11. Test
12. Best Practices
13. FAQ
14. Ringraziamenti

================================================================================
                            1. PANORAMICA
================================================================================

Questo script automatizza l'intera sequenza fotografica durante un'eclissi 
solare totale. Controlla la tua fotocamera tramite digiCamControl, esegue 
sequenze HDR precise, riproduce avvisi audio nei momenti critici e invia 
notifiche in tempo reale via Telegram.

Perfetto per astrofotografi che vogliono concentrarsi sull'esperienza 
dell'eclissi mentre lo script gestisce tutte le operazioni della fotocamera 
con precisione millimetrica.

================================================================================
                           2. FUNZIONALITÀ
================================================================================

  Funzionalità           | Descrizione
  -----------------------|------------------------------------------------------
  Scatto Automatico      | Sequenza completa dall'inizio alla fine dell'eclissi
  Timing Assoluto        | Tutte le azioni basate sull'orario esatto del PC
  Bracketing HDR         | Sequenze di esposizione automatiche per la corona
  Modalità Raffica       | Scatti continui durante le fasi dell'anello di diamante
  Avvisi Audio           | Segnali acustici personalizzati per il filtro solare
  Notifiche Telegram     | Aggiornamenti in tempo reale e comandi remoti
  Log Dettagliato        | Ogni evento, scatto ed errore registrato con timestamp
  Integrazione digiCam   | Controllo completo tramite comandi remoti
  Report Automatico      | Statistiche dettagliate dopo l'evento
  Recupero Errori        | Tentativi di riconnessione automatici in caso di errore

================================================================================
                             3. REQUISITI
================================================================================

HARDWARE:
  - PC Windows (portatile consigliato per la portabilità)
  - Fotocamera compatibile (Canon, Nikon, Sony tramite digiCamControl)
  - Cavo USB
  - Treppiede (consigliato)

SOFTWARE:
  - digiCamControl (gratuito) - https://digicamcontrol.com/
  - Python 3.8 o superiore

LIBRERIE OPZIONALI:
  pip install requests   # Per le notifiche Telegram
  pip install psutil     # Per il monitoraggio batteria e spazio su disco

================================================================================
                            4. INSTALLAZIONE
================================================================================

PASSO 1: Clona il Repository
  git clone https://github.com/S85mario/Solar-Eclipse-Automation.git
  cd Solar-Eclipse-Automation

PASSO 2: Installa digiCamControl
  Scarica da https://digicamcontrol.com/ e installa

PASSO 3: Installa le Dipendenze Python (Opzionale)
  pip install requests psutil

PASSO 4: Prepara i File Audio (Opzionale)
  Crea la cartella: C:\Eclissi\Audio\
  
  Aggiungi i file .wav:
    togli_filtro.wav       - "Togli il filtro solare"
    metti_filtro.wav       - "Rimetti il filtro solare"
    mancano_20_secondi.wav - "Conto alla rovescia 20 secondi"
    errore_connessione.wav - "Errore di connessione"
    attenzione.wav         - "Attenzione"

================================================================================
                            5. CONFIGURAZIONE
================================================================================

CONFIG_ECLIPSE.JSON

Crea questo file nella stessa cartella di main.py:

{
  "hardware": {
    "marca_camera": "CANON",
    "gui_path": "C:\\Program Files (x86)\\digiCamControl\\CameraControl.exe",
    "cmd_path": "C:\\Program Files (x86)\\digiCamControl\\CameraControlRemoteCmd.exe"
  },
  "coordinate": {
    "latitudine_dms": "43°44'08.77\"N",
    "longitudine_dms": "7°55'20.04\"W"
  },
  "timing_eclisse": {
    "_data": "12 Agosto 2026",
    "c1_inizio": "19:30:00",
    "avviso_togli_filtro": "20:26:20",
    "anello_in_inizio": "20:26:50",
    "anello_in_fine": "20:27:20",
    "totalita_inizio": "20:27:25",
    "totalita_fine": "20:28:40",
    "anello_out_inizio": "20:28:50",
    "anello_out_fine": "20:29:20",
    "avviso_metti_filtro": "20:29:20",
    "post_parziale_inizio": "20:29:30",
    "p4_fine": "21:12:00"
  },
  "tempi_scatto": {
    "parziale": ["1/2000"],
    "burst": ["1/2000"],
    "corona_interna": ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15"],
    "corona_esterna": ["1/8", "1/4", "0.5", "1", "2"],
    "raffica_scatti": 5,
    "intervallo_parziale_sec": 780
  },
  "checklist_items": [
    "Fotocamera accesa e connessa?",
    "Cartella di salvataggio configurata?",
    "Orologio PC sincronizzato?",
    "File di configurazione valido?",
    "Batteria sufficiente?",
    "Spazio libero su disco sufficiente?"
  ],
  "parametri_camera": {
    "iso_default": 200,
    "apertura_default": 8,
    "test_tempo": "1/1000"
  }
}

SECRETS.JSON (per Telegram)

Crea questo file per le notifiche Telegram:

{
  "telegram": {
    "bot_token": "IL_TUO_TOKEN_DEL_BOT_DA_BOTFATHER",
    "chat_id": "IL_TUO_CHAT_ID_DA_USERINFOBOT"
  }
}

Come ottenere le credenziali Telegram:
  1. Apri Telegram e cerca @BotFather
  2. Invia /newbot e segui le istruzioni
  3. Copia il token del bot
  4. Cerca @userinfobot e invia /start
  5. Copia il tuo chat ID

================================================================================
                             6. UTILIZZO
================================================================================

AVVIA LO SCRIPT:
  python main.py

COSA SUCCEDE DURANTE L'ESECUZIONE:
  1. Controlli Iniziali - Connessione camera, batteria, spazio su disco
  2. Checklist - Verifica interattiva di tutte le preparazioni
  3. Configurazione Hardware - digiCamControl si avvia e testa la connessione
  4. Attesa C1 - Lo script attende silenziosamente l'orario di inizio
  5. Esecuzione Automatica - Sequenza completa automatica
  6. Generazione Report - Riepilogo con statistiche alla fine

COMANDI TELEGRAM (se configurati):
  /status  - Mostra le statistiche attuali
  /stop    - Arresto di emergenza
  /pause   - Pausa temporanea
  /resume  - Riprendi l'esecuzione
  /help    - Mostra i comandi disponibili

================================================================================
                        7. SEQUENZA TEMPORALE
================================================================================

SEQUENZA COMPLETA DELL'ECLISSE:

  Ora       | Evento                 | Azione
  ----------|------------------------|-------------------------------------------
  19:30:00  | C1 - Inizio Parziale   | Scatti ogni 13 minuti
  20:26:20  | Avviso Filtro          | "Togli il filtro solare"
  20:26:50  | Anello Diamante IN     | Scatti a raffica per 30 secondi
  20:27:25  | Totalità (C2)          | Bracketing corona interna
  20:28:00  | Totalità (C2)          | Bracketing corona esterna
  20:28:40  | Fine Totalità          | Fine bracketing
  20:28:50  | Anello Diamante OUT    | Scatti a raffica per 30 secondi
  20:29:20  | Avviso Filtro          | "Rimetti il filtro solare"
  20:29:30  | Inizio Post-Parziale   | Scatti ogni 10 minuti
  21:12:00  | P4 - Fine Eclisse      | Completato

RIEPILOGO SCATTI:

  Fase               | Scatti | Intervallo
  -------------------|--------|---------------
  Parziale (IN)      | ~8     | 13 minuti
  Anello Diamante IN | ~15    | 30 sec raffica
  Corona Interna     | 6      | Sequenziale
  Corona Esterna     | 5      | Sequenziale
  Anello Diamante OUT| ~15    | 30 sec raffica
  Parziale (OUT)     | ~10    | 10 minuti
  -------------------|--------|---------------
  TOTALE             | ~59    |

================================================================================
                        8. STRUTTURA FILE
================================================================================

Solar-Eclipse-Automation/
├── main.py                          # Script principale
├── config_eclipse.json              # Configurazione
├── secrets.json                     # Credenziali Telegram (NON CONDIVIDERE!)
├── eclissi_log.txt                  # Log semplice
├── eclissi_dettaglio.log            # Log dettagliato con timestamp
├── report_eclisse_*.txt             # Report automatico
│
└── C:\Eclissi\Audio\                # File audio (opzionali)
    ├── togli_filtro.wav
    ├── metti_filtro.wav
    ├── mancano_20_secondi.wav
    ├── errore_connessione.wav
    └── attenzione.wav

================================================================================
                            9. LOGGING
================================================================================

DUE FILE DI LOG:

  eclissi_log.txt          Log semplice con timestamp e messaggi
  eclissi_dettaglio.log    Log dettagliato con millisecondi e dati JSON

ESEMPIO DI LOG:

  [2026-06-17 19:30:00.123] [INFO] In attesa dell'orario di inizio PRE-PARZIALE
  [2026-06-17 19:30:01.789] [SUCCESS] SCATTO: PRE-PARZIALE_1/2000_shot1
  [2026-06-17 20:26:20.000] [INFO] AVVISO: TOGLI IL FILTRO SOLARE
  [2026-06-17 20:26:50.000] [INFO] ANELLO_DIAMANTE_IN - Raffica 5 scatti
  [2026-06-17 21:12:00.000] [INFO] ECLISSE COMPLETATA!

================================================================================
                        10. RISOLUZIONE PROBLEMI
================================================================================

PROBLEMA: Fotocamera non trovata
SOLUZIONE:
  1. Controlla la connessione USB
  2. Fotocamera in modalità Manuale (M)
  3. digiCamControl in esecuzione
  4. Premi "Connect" in digiCamControl

PROBLEMA: digiCamControl non si avvia
SOLUZIONE: Verifica il percorso in config_eclipse.json

PROBLEMA: Lo script parte immediatamente
SOLUZIONE: Controlla l'orario c1_inizio nel config - potrebbe essere già passato

PROBLEMA: L'audio non viene riprodotto
SOLUZIONE: Verifica la cartella C:\Eclissi\Audio\ e i file .wav

PROBLEMA: Telegram non funziona
SOLUZIONE: Controlla token e chat_id in secrets.json

PROBLEMA: Lo script si blocca
SOLUZIONE: Aspetta - potrebbe essere in un periodo di attesa programmato

PROBLEMA: Scatti falliti
SOLUZIONE: La fotocamera potrebbe essere andata in standby - controlla le impostazioni di risparmio energetico

TEST VELOCE FOTOCAMERA:
  "C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe" /c get shutterspeed
  Output atteso: :;response:"1/2000";

================================================================================
                            11. TEST
================================================================================

TEST VELOCE CON ORARI MODIFICATI:

Per testare senza aspettare ore, modifica config_eclipse.json:

  "c1_inizio": "20:00:00",
  "avviso_togli_filtro": "20:10:00",
  "anello_in_inizio": "20:10:30",
  "anello_in_fine": "20:11:00",
  "totalita_inizio": "20:11:05",
  "totalita_fine": "20:12:20",
  "anello_out_inizio": "20:12:30",
  "anello_out_fine": "20:13:00",
  "avviso_metti_filtro": "20:13:00",
  "post_parziale_inizio": "20:13:10",
  "p4_fine": "20:30:00"

Questo comprime l'intera sequenza in circa 30 minuti.

================================================================================
                        12. BEST PRACTICES
================================================================================

1 SETTIMANA PRIMA:
  [ ] Testa lo script con orari modificati
  [ ] Verifica le batterie della fotocamera (avere ricambi)
  [ ] Formatta le schede SD
  [ ] Fai un backup dei file di configurazione
  [ ] Controlla la qualità del cavo USB

GIORNO PRIMA:
  [ ] Carica la batteria del PC al 100%
  [ ] Prepara cavi di ricambio
  [ ] Verifica l'orientamento del filtro solare
  [ ] Blocca la messa a fuoco con nastro adesivo
  [ ] Sincronizza l'orologio del PC (usa time.windows.com)

DURANTE L'ECLISSE:
  [ ] Non toccare PC o fotocamera
  [ ] Monitora solo i log (nessuna interazione)
  [ ] Usa batteria esterna se possibile
  [ ] Mantieni la calma - lo script fa tutto

DOPO L'ECLISSE:
  [ ] Fai il backup di tutte le foto
  [ ] Salva i file di log
  [ ] Non formattare la SD fino a doppio backup completato
  [ ] Condividi i tuoi risultati!

================================================================================
                              13. FAQ
================================================================================

D: Posso usarlo con qualsiasi fotocamera?
R: Qualsiasi fotocamera supportata da digiCamControl (Canon, Nikon, Sony)

D: Cosa succede se la fotocamera si disconnette durante l'eclisse?
R: Lo script tenterà automaticamente di riconnettersi

D: Funziona senza Telegram?
R: Sì, Telegram è opzionale. Lo script funziona perfettamente anche senza.

D: Posso usare il WiFi invece dell'USB?
R: Non consigliato - l'USB è più affidabile per eventi critici.

D: Cosa succede se la batteria del PC si scarica?
R: Al riavvio, lo script riprenderà dall'ultimo stato salvato.

D: Quante foto farà?
R: Circa 59 scatti (configurabile)

D: Cosa succede se perdo l'orario di inizio?
R: Lo script rileva se C1 è passato e parte immediatamente.

D: Devo tenere aperto il prompt dei comandi?
R: Sì, lo script viene eseguito nella finestra del prompt dei comandi.

D: Posso minimizzare la finestra dello script?
R: Sì, ma non chiuderla.

================================================================================
                         14. RINGRAZIAMENTI
================================================================================

- Il team di digiCamControl per l'eccellente software di controllo fotocamera
- La comunità astrofotografica italiana per i test sul campo
- Tutti i contributori open source

================================================================================
                             SUPPORTO
================================================================================

GitHub Issues: https://github.com/S85mario/Solar-Eclipse-Automation/issues

================================================================================

                      Buona eclisse! 🌞🌑📸

             Documentazione versione 5.0 - Giugno 2026

================================================================================