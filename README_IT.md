🎯 Panoramica

Solar Eclipse Automation Script è uno strumento professionale per catturare automaticamente foto durante un'eclissi solare totale. Gestisce sequenze HDR complesse, supporta hot-resume, telemetria hardware, compressione temporale per test e notifiche Telegram.
✨ Funzionalità
Funzionalità	Descrizione
📷 Sequenze HDR	Bracketing automatico per protuberanze, corona e anello di diamante
🔄 Hot-Resume	Riprende automaticamente dall'ultimo scatto dopo un'interruzione
📱 Notifiche Telegram	Avvisi in tempo reale e comandi remoti (/status, /stop, /pause, /resume)
⚡ Compressione temporale	Testa l'intera eclisse in pochi minuti (compressione 60x)
🔋 Monitoraggio batteria	Avvisi quando la batteria del PC è scarica (richiede psutil)
📊 Report automatico	Genera statistiche dettagliate dopo l'evento
🎮 Wizard configurazione	Guida interattiva per il setup
💾 Persistenza stato	Salva i progressi dopo ogni scatto per il recupero
📸 Sequenza scatti
Fase	Durata	Intervallo	Scatti	Tempo
Parziale (entrata)	45 min	15 min	3	1/2000
Anello diamante (entrata)	5 sec	Immediato	9	1/8000-1/2000
Corona interna	50 sec	Sequenziale	6	1/500-1/15
Corona esterna	50 sec	Sequenziale	5	1/8-2 sec
Anello diamante (uscita)	5 sec	Immediato	9	1/8000-1/2000
Parziale (uscita)	45 min	15 min	3	1/2000

Totale: ~35 scatti
🚀 Guida rapida
1. Prerequisiti
bash

# Solo Windows (per il controllo camera)
digiCamControl: https://digicamcontrol.com/

# Python 3.8 o superiore
python --version

# Librerie opzionali
pip install psutil requests

2. Installazione
bash

# Clona il repository
git clone https://github.com/tuousername/solar-eclipse-automation.git
cd solar-eclipse-automation

# Installa le dipendenze (opzionale)
pip install -r requirements.txt

3. Configurazione

Crea secrets.json per Telegram (richiesto per le notifiche):
json

{
  "telegram": {
    "bot_token": "IL_TUO_TOKEN_DEL_BOT_DA_BOTFATHER",
    "chat_id": "IL_TUO_CHAT_ID_DA_USERINFOBOT"
  }
}

Modifica config_eclipse.json per impostare la tua posizione e gli orari:
json

{
  "coordinate": {
    "latitudine_dms": "43°44'08.77\"N",
    "longitudine_dms": "7°55'20.04\"W"
  },
  "timing_eclisse": {
    "p1_inizio": "19:30:00",
    "totalita_inizio": "20:27:10",
    "totalita_fine": "20:28:50",
    "p4_fine": "21:12:00"
  }
}

4. Esecuzione
bash

python main.py

Opzioni menu:

    1 - Test veloce con compressione temporale (60x)

    2 - Modalità reale (per l'evento vero)

    3 - Wizard configurazione

    4 - Cambia fattore compressione

    5 - Esci

📱 Comandi Telegram
Comando	Azione
/status	Mostra statistiche correnti
/stop	Arresto emergenza
/pause	Pausa temporanea
/resume	Riprendi esecuzione
/help	Mostra comandi disponibili
📁 Struttura del progetto
text

solar-eclipse-automation/
├── main.py                          # Punto di ingresso
├── config_eclipse.json              # Configurazione principale
├── secrets.json                     # Credenziali (NON CONDIVIDERE!)
│
├── modules/
│   ├── config_manager.py            # Gestione configurazione
│   ├── telegram_notifier.py         # Notifiche Telegram
│   ├── hardware_manager.py          # Controllo camera
│   ├── time_manager.py              # Timing e attese
│   ├── sequence_executor.py         # Sequenze scatti
│   ├── statistics.py                # Report
│   └── ui_manager.py                # Menu e checklist
│
└── utils/
    ├── constants.py                 # Costanti globali
    ├── logger.py                    # Sistema di logging
    └── helpers.py                   # Funzioni di utilità

⚙️ Fattori di compressione temporale
Fattore	Tempo reale	Tempo simulato	Utilizzo
1x	100 min	100 min	Evento reale
30x	100 min	3.3 min	Test medio
60x	100 min	1.7 min	Test veloce
120x	100 min	50 sec	Test rapidissimo
📊 Esempio report generato
text

======================================================================
   REPORT ECLISSE SOLARE - 2026-08-12 21:15:30
======================================================================

📅 INFORMAZIONI GENERALI:
   Data eclisse: 12 Agosto 2026
   Località: 43°44'08.77"N, 7°55'20.04"W
   Camera: CANON
   Modalità: REALE

----------------------------------------------------------------------

📸 STATISTICHE SCATTI:
   Fasi completate:        6/6
   Scatti previsti:        35
   Scatti eseguiti:        35
   Scatti riusciti:        34
   Scatti falliti:         1
   Successo:               97.1%

----------------------------------------------------------------------

🔋 BATTERIA:
   Batteria inizio:        100%
   Batteria fine:          67%
   Consumo:                33%

======================================================================

🛠️ Risoluzione problemi
Problema	Soluzione
Camera non trovata	Verifica connessione USB, camera in modalità Manuale, digiCamControl aperto
Telegram non funziona	Verifica token e chat_id in secrets.json
Script si blocca	Riduci intervallo watchdog nella configurazione
Simulazione lenta	Aumenta il fattore di compressione (opzione 4)