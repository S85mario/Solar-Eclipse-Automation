#!/usr/bin/env python3
"""
Costanti globali condivise tra tutti i moduli
"""

import os
from datetime import datetime, timedelta, time as datetime_time

# File di configurazione
CONFIG_FILE = "config_eclipse.json"
SECRETS_FILE = "secrets.json"
COMPRESSIONE_FILE = "compressione_config.json"

# File di sistema
LOG_FILE = "eclissi_log.txt"
STATO_FILE = "eclissi_stato.json"
WATCHDOG_FILE = "watchdog_last.txt"

# Variabili globali (verranno inizializzate all'avvio)
FATTORE_COMPRESSIONE = 60
ATTESA_INIZIALE_SEC = 10
SIM_MODE = False
MODALITA_SIM_COMPRESSA = False
DEBUG_MODE = False
WATCHDOG_INTERVAL = 30

# Timer globali
P1_INIZIO = None
TOTALITA_INIZIO = None
TOTALITA_FINE = None
P4_FINE = None

# Timing per simulazione
P1_SIM = None
C2_SIM = None
C3_SIM = None
P4_SIM = None

# Liste tempi scatto
TEMPI_HDR = []
TEMPI_BURST = []
TEMPI_CORONA_INTERNA = []
TEMPI_CORONA_ESTERNA = []
TEMPI_PROTUBERANZE = []
TEMPI_CORONA = []
TEMPI_PARZIALE = []
RAFAGA_SCATTI = 3
TEST_TEMPO = "1/1000"
CHECKLIST_ITEMS = []

# Statistiche globali
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

# Comandi remoti
stop_requested = False
pause_requested = False

# Configurazione globale
CONFIG = None
secrets = {}