#!/usr/bin/env python3
"""
Gestione statistiche e report finale
"""

from datetime import datetime
from utils.logger import log_messaggio
from utils.constants import stats, MODALITA_SIM_COMPRESSA, FATTORE_COMPRESSIONE
from .telegram_notifier import invia_notifica_telegram_embed
from .config_manager import ottieni_config

def genera_report_finale():
    """Genera report statistico completo dell'eclisse"""
    global stats
    config = ottieni_config()
    
    print("\n" + "=" * 70)
    print("   📊 GENERAZIONE REPORT FINALE")
    print("=" * 70)
    
    durata_totale = None
    if stats['inizio_eclisse'] and stats['fine_eclisse']:
        durata_totale = (stats['fine_eclisse'] - stats['inizio_eclisse']).total_seconds() / 60
    
    if stats['totale_scatti_eseguiti'] > 0:
        percentuale_successo = (stats['scatti_riusciti'] / stats['totale_scatti_eseguiti']) * 100
    else:
        percentuale_successo = 0
    
    errori_text = "   ✅ Nessun errore rilevato"
    if stats['errori']:
        errori_lista = '\n'.join([f'   • {e[:100]}' for e in stats['errori'][:5]])
        errori_text = errori_lista
        if len(stats['errori']) > 5:
            errori_text += f'\n   ... e altri {len(stats["errori"]) - 5}'
    
    tempi_unici = list(dict.fromkeys(stats['tempi_scatto_utilizzati']))
    tempi_text = ', '.join(tempi_unici[:10])
    if len(tempi_unici) > 10:
        tempi_text += f'... e altri {len(tempi_unici) - 10}'
    
    report = f"""
{'=' * 70}
   REPORT ECLISSE SOLARE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 70}

📅 INFORMAZIONI GENERALI:
   Data eclisse: {config['timing_eclisse']['_data']}
   Località: {config['coordinate']['latitudine_dms']}, {config['coordinate']['longitudine_dms']}
   Camera: {config['hardware']['marca_camera']}
   Modalità: {'SIMULAZIONE COMPRESSA' if MODALITA_SIM_COMPRESSA else 'REALE'}
   Fattore compressione: {f'{FATTORE_COMPRESSIONE}x' if MODALITA_SIM_COMPRESSA else 'N/A'}

{'-' * 70}

⏰ TIMING ECLISSE:
   P1 (Inizio parziale):   {config['timing_eclisse']['p1_inizio']}
   C2 (Inizio totalità):   {config['timing_eclisse']['totalita_inizio']}
   C3 (Fine totalità):     {config['timing_eclisse']['totalita_fine']}
   P4 (Fine parziale):     {config['timing_eclisse']['p4_fine']}
   
   Inizio script:          {stats['inizio_eclisse'].strftime('%H:%M:%S') if stats['inizio_eclisse'] else 'N/D'}
   Fine script:            {stats['fine_eclisse'].strftime('%H:%M:%S') if stats['fine_eclisse'] else 'N/D'}
   Durata totale:          {f'{durata_totale:.1f} minuti' if durata_totale else 'N/D'}

{'-' * 70}

📸 STATISTICHE SCATTI:
   Fasi completate:        {stats['fasi_completate']}/{len(config['fasi_eclisse'])}
   Scatti previsti:        {stats['totale_scatti_previsti']}
   Scatti eseguiti:        {stats['totale_scatti_eseguiti']}
   Scatti riusciti:        {stats['scatti_riusciti']}
   Scatti falliti:         {stats['scatti_falliti']}
   Successo:               {percentuale_successo:.1f}%

{'-' * 70}

🔋 BATTERIA:
   Batteria inizio:        {stats['batteria_inizio']}%
   Batteria fine:          {stats['batteria_fine']}%
   Consumo:                {stats['batteria_inizio'] - stats['batteria_fine'] if stats['batteria_inizio'] and stats['batteria_fine'] else 'N/D'}%

{'-' * 70}

🎬 TEMPI SCATTO UTILIZZATI:
   {tempi_text}

{'-' * 70}

⚠️ ERRORI RILEVATI:
   {errori_text}

{'-' * 70}

{'=' * 70}
   Report generato automaticamente da Solar Eclipse Script v5.0
{'=' * 70}
"""
    
    report_file = f"report_eclisse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Report salvato in: {report_file}")
    print(report)
    
    invia_notifica_telegram_embed("📊 REPORT COMPLETATO", f"Report salvato in {report_file}\nSuccesso: {percentuale_successo:.1f}%", "🟢")
    
    return report_file