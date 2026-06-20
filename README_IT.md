# SolarEclipse2026 📸 🌒

Sistema di controllo ibrido automatizzato per fotocamere Canon/Nikon tramite **digiCamControl** per bracketing ad alta precisione durante l'**Eclissi Solare Totale del 12 agosto 2026**.

Questo script combina l'affidabilità a prova di bomba della CLI di digiCamControl (`CameraControlRemoteCmd.exe`) per il cambio dei parametri della fotocamera con la velocità sotto il millisecondo dei trigger HTTP del Web Server per lo scatto immediato. Ottimizzato per fotocamere astromodificate e progettato per salvare i file **rigorosamente sulla scheda SD della fotocamera**, in modo da massimizzare la velocità di svuotamento del buffer ed evitare il sovraccarico di memoria sul PC.

---

# 🚀 Funzionalità Chiave

* **Motore Ibrido:** Impostazione dei parametri tramite CLI nativa (~1s di overhead tra i lunghi intervalli) + trigger di scatto HTTP ultra-rapido (~22ms di latenza per una sincronizzazione esatta).
* **Salvataggio Forzato solo su SD:** Sovrascrive automaticamente le impostazioni predefinite della sessione di digiCamControl per imporre il salvataggio dei file direttamente sulla scheda di memoria della fotocamera (`CameraMemoryOnly`), mantenendo pulito il PC.
* **Modalità Debug Interattiva:** Permette di attivare o disattivare facilmente log dettagliati e colorati in console e le richieste URL precise all'avvio.
* **Notifiche Telegram:** Aggiornamenti in tempo reale, log degli errori e avvisi critici per i filtri inviati direttamente sul tuo telefono.
* **Ottimizzato per Astromodifica:** Mappatura dei tempi di esposizione della timeline personalizzata per sfruttare la maggiore sensibilità all'Idrogeno Alfa ($H\alpha$ a $656.3\text{ nm}$) per catturare protuberanze solari e cromosfera in modo sbalorditivo.

---

# 🛠️ Prerequisiti e Configurazione

# 1. Requisiti
* Sistema operativo Windows con digiCamControl installato.
* Python 3.x.
* Una fotocamera DSLR/Mirrorless compatibile (es. serie Canon EOS R) collegata tramite cavo USB-C ad alta velocità.

# 2. Struttura dei File
Assicurati che la cartella del tuo progetto contenga:
```text
├── SolarEclipse2026.py   # Lo script principale
└── secrets.json          # Configurazione del bot Telegram (Opzionale)

# 3. Configurazione Telegram (secrets.json)

Se desideri ricevere avvisi sul telefono in tempo reale sul campo, crea un file secrets.json:

{
  "telegram": {
    "bot_token": "IL_TUO_BOT_TOKEN_QUI",
    "chat_id": "IL_TUO_CHAT_ID_QUI"
  }
}

Fase / Evento,Tempi Relativi alla Totalità,Impostazioni (ISO | Tempo | Diaframma),Obiettivo dello Scatto
Fase Parziale C1,C2 - 58 min,ISO 100 | 1/250s | f/8.0,Tracciamento Primo Contatto
Fasi Parziali,C2 -40m / -20m / -10m / -5m,ISO 100 | 1/250s | f/8.0,Tracciamento disco solare
Anello di Diamante C2,C2 - 5 sec,ISO 400 | 1/100s | f/8.0,Fondersi con i grani di Baily
Grani di Baily C2,C2 - 2 sec,ISO 200 | 1/3200s | f/16.0,Picchi nitidi nelle valli lunari
HDR 1,C2 + 0 sec,ISO 200 | 1/4000s | f/8.0,Protuberanze (Hα)
HDR 2 & 3,C2 + 2 sec / + 4 sec,"ISO 200 | 1/1000s, 1/250s | f/8.0",Corona Interna e Media
HDR 4 & 5,C2 + 6 sec / + 8 sec,"ISO 200 | 1/60s, 1/15s | f/8.0",Corona Estesa ed Esterna
HDR 6 & 7,C2 + 10 sec / + 12 sec,"ISO 200 | 1/4s, 1.0s | f/8.0",Strutture Profonde ed Earthshine
Grani di Baily C3,C3 + 2 sec,ISO 200 | 1/3200s | f/16.0,Prep. anello di diamante Terzo Contatto
Anello di Diamante C3,C3 + 5 sec,ISO 400 | 1/100s | f/8.0,Uscita dalla Totalità
Fasi Parziali,C3 +5m fino a +30m,ISO 100 | 1/250s | f/8.0,Tracciamento finale dell'uscita

📋 Checklist di Dispiegamento sul Campo (Pre-Flight)

Quando avvii lo script, una checklist interattiva ti chiederà di confermare ogni passaggio fondamentale prima dell'attivazione:

  1  [ ] ALIMENTAZIONE: PC collegato a una rete stabile/Powerbank e batteria della fotocamera al 100%.

  2  [ ] CAVO: Cavo di tethering USB-C ad alta velocità bloccato saldamente.

  3  [ ] DIGICAMCONTROL: Software attivo, fotocamera rilevata, LIVE VIEW CHIUSO (Fondamentale per evitare lag).

  4  [ ] WEB SERVER: Web Server attivo nelle impostazioni di digiCamControl (porta predefinita 2727).

  5  [ ] FUOCO MANUALE (MF): Fuoco bloccato sull'infinito precedentemente tramite Live View, obiettivo commutato su MF e fissato con nastro.

  6  [ ] RIVEDILE IMMAGINI: "Rivedi Immagine" impostato su OFF nei menu interni della fotocamera (Fondamentale per prevenire i blocchi BUSY).

  7  [ ] FILTRO SOLARE: Filtro solare ND 3.8/5.0 fissato saldamente per le fasi parziali.

💻 Utilizzo

  1  Avvia digiCamControl e assicurati che la tua fotocamera sia completamente riconosciuta.

  2  Apri un terminale/prompt dei comandi nella directory dello script ed esegui:
    
    python SolarEclipse2026.py

  3 Selezione Debug: Lo script chiederà: Vuoi attivare la modalità DEBUG avanzata? (s/N):.

    - Premi S per i test (mostra i log completi colorati in ANSI e gli endpoint web attivi).

    - Premi Invio (No) il giorno dell'eclissi per un'esecuzione pulita e standard.

  4 Completa la checklist sullo schermo premendo INVIO a ogni passaggio.
  5 Giù le mani: Una volta avviato, NON toccare il corpo della fotocamera e non premere il pulsante Play per visualizzare l'anteprima delle immagini. Lascia che lo script gestisca il buffer.    

  ⚠️ Promemoria Critici per la Sicurezza durante la Totalità

    Rimozione del Filtro: Lo script emetterà un forte lampeggio in console e un avviso su Telegram a C2 - 4min 50s con scritto: ⚠️ RIMUOVERE FILTRO ND 3.8 ORA!. Rimuovi immediatamente il filtro solare per catturare l'Anello di Diamante e la Totalità.

    Reinserimento del Filtro: Subito dopo l'Anello di Diamante C3, lo script mostrerà l'avviso: 🚨 REINSERIRE FILTRO ND 3.8 IMMEDIATAMENTE!. Riposiziona subito il filtro solare per proteggere il sensore e le ottiche della fotocamera dalla luce solare diretta e concentrata durante le fasi parziali finali.

⚙️ Note sull'Astromodifica

Questa sequenza è fortemente ottimizzata per sensori privi del filtro IR-cut nativo o con filtro sostituito. Le rapide esposizioni a 1/4000s (HDR 1) risolveranno nativamente una quantità sbalorditiva di contrasto strutturale all'interno dei filamenti solari in idrogeno-alfa, mentre l'intero spettro mostrerà una saturazione rosa/magenta amplificata vicino al confine della corona interna. Assicurati di regolare il Bilanciamento del Bianco in post-produzione partendo dai dati RAW nativi.

Cieli sereni per il 12 agosto 2026! 🌌