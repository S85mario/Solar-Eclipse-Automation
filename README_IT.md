Uno script Python automatizzato progettato per gestire sequenze di bracketing in alta gamma dinamica (HDR) durante le eclissi solari. Automatizza le impostazioni della fotocamera (Tempo di scatto, Diaframma, ISO) gestendo tempistiche precise calcolate rispetto ai punti di contatto C2 (Inizio Totalità) e C3 (Fine Totalità).

Lo script si interfaccia direttamente con la CLI di digiCamControl per garantire comunicazioni stabili ed evitare colli di bottiglia durante le repentine variazioni di parametri (es. Anello di Diamante e Grani di Baily).
Caratteristiche

    ⏱️ Sincronizzazione Astronomica: Automatizza la sequenza di scatto basandosi su scostamenti temporali esatti rispetto a C2 e C3.

    📷 Controllo Diaframma Stabilizzato: Forzatura della sintassi nativa (f/X.0) e pause hardware dedicate per evitare blocchi elettronici sulle lenti.

    🤖 Integrazione Telegram: Invio di log in tempo reale, conferme di scatto e notifiche di errore direttamente su un canale o bot Telegram.

    ⚙️ Timeline Personalizzabile: Struttura flessibile basata su stringhe standard TAKEPIC per modificare rapidamente la raffica HDR.

Prerequisiti

    Sistema Operativo: Windows 10 / 11

    Python: 3.x

    Software: digiCamControl installato nel percorso predefinito (C:\\Program Files (x86)\\digiCamControl\\).

    Setup Camera: Corpo macchina impostato su Manuale (M), obiettivo su Fuoco Manuale (MF) e finestra di Live View chiusa nell'interfaccia di digiCamControl.

Configurazione

    Credenziali Telegram: Crea un file chiamato secrets.json nella stessa cartella dello script:
    JSON

    {
        "telegram": {
            "bot_token": "IL_TUO_BOT_TOKEN",
            "chat_id": "IL_TUO_CHAT_ID"
        }
    }

    Orari dell'Eclissi: Modifica le variabili C2_TIME e C3_TIME inserendo gli orari astronomici precisi calcolati per le coordinate geografiche della tua postazione.