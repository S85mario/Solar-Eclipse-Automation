#!/usr/bin/env python3
"""
Gestione notifiche Telegram
"""

import requests
import threading
from datetime import datetime
from utils.logger import log_messaggio, log_debug
from utils.constants import SIM_MODE, MODALITA_SIM_COMPRESSA, stop_requested, pause_requested, stats
from .config_manager import ottieni_secrets, ottieni_config

def invia_notifica_telegram(messaggio, parse_mode=None):
    """Invia una notifica via Telegram"""
    secrets = ottieni_secrets()
    config = ottieni_config()
    
    try:
        bot_token = secrets.get("telegram", {}).get("bot_token", "")
        chat_id = secrets.get("telegram", {}).get("chat_id", "")
        
        if not bot_token or not chat_id:
            return False
        
        if MODALITA_SIM_COMPRESSA:
            prefix = "🧪 [TEST COMPRESSO]"
        elif SIM_MODE:
            prefix = "🔧 [SIMULAZIONE]"
        else:
            prefix = "📷 [REALE]"
        
        full_message = f"{prefix}\n{messaggio}"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": full_message}
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        def send():
            try:
                requests.post(url, data=data, timeout=5)
            except:
                pass
        
        threading.Thread(target=send, daemon=True).start()
        return True
    except:
        return False

def invia_notifica_telegram_embed(titolo, messaggio, colore="🟢"):
    """Invia una notifica formattata"""
    emoji_map = {"🟢": "✅", "🔴": "❌", "🟡": "⚠️", "🔵": "ℹ️", "🟣": "📸", "🟠": "🌞"}
    testo = f"""{emoji_map.get(colore, 'ℹ️')} *{titolo}*

{messaggio}

⏰ {datetime.now().strftime('%H:%M:%S')}"""
    return invia_notifica_telegram(testo.strip(), parse_mode="Markdown")

def check_telegram_commands():
    """Controlla se ci sono comandi pendenti da Telegram"""
    global stop_requested, pause_requested
    secrets = ottieni_secrets()
    config = ottieni_config()
    
    try:
        bot_token = secrets.get("telegram", {}).get("bot_token", "")
        chat_id = secrets.get("telegram", {}).get("chat_id", "")
        
        if not bot_token or not chat_id:
            return
        
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                message = update.get("message", {})
                text = message.get("text", "")
                chat = message.get("chat", {})
                chat_id_msg = str(chat.get("id", ""))
                
                if chat_id_msg == chat_id:
                    cmd = text.lower().strip()
                    
                    if cmd == "/stop":
                        stop_requested = True
                        invia_notifica_telegram("🛑 *Comando ricevuto: STOP*", parse_mode="Markdown")
                        log_messaggio("📱 Comando Telegram: STOP ricevuto")
                    
                    elif cmd == "/pause":
                        pause_requested = True
                        invia_notifica_telegram("⏸️ *Comando ricevuto: PAUSA*", parse_mode="Markdown")
                        log_messaggio("📱 Comando Telegram: PAUSA ricevuto")
                    
                    elif cmd == "/resume":
                        pause_requested = False
                        invia_notifica_telegram("▶️ *Comando ricevuto: RESUME*", parse_mode="Markdown")
                        log_messaggio("📱 Comando Telegram: RESUME ricevuto")
                    
                    elif cmd == "/status":
                        status_msg = f"""
📊 *STATO SCRIPT*

🔹 Fasi completate: {stats['fasi_completate']}/{len(config.get('fasi_eclisse', [])) if config else 0}
🔹 Scatti riusciti: {stats['scatti_riusciti']}
🔹 Scatti falliti: {stats['scatti_falliti']}
🔹 Batteria: {stats.get('batteria_inizio', 'N/D')}%
🔹 Modalità: {'SIMULAZIONE' if MODALITA_SIM_COMPRESSA or SIM_MODE else 'REALE'}"""
                        invia_notifica_telegram(status_msg, parse_mode="Markdown")
                    
                    elif cmd == "/help":
                        help_msg = """
🤖 *COMANDI DISPONIBILI*

/status - Stato attuale
/stop - Arresto emergenza
/pause - Pausa temporanea
/resume - Riprendi esecuzione
/help - Questo messaggio"""
                        invia_notifica_telegram(help_msg, parse_mode="Markdown")
                    
                    update_id = update.get("update_id")
                    if update_id:
                        requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={update_id+1}")
    except:
        pass