import re
import urllib.parse

def extrair_nomes_limpos(texto):
    if not texto: return []
    lista = []
    itens = [i.strip() for i in texto.split(',') if i.strip()]
    for item in itens:
        nome = re.sub(r'\s*\(.*?\)', '', item).strip().capitalize()
        if nome and nome.lower() != 'vago':
            if nome not in lista:
                lista.append(nome)
    return lista

def atualizar_whatsapp(dia_obj):
    texto_wpp = f"*Dia {dia_obj['dia']} - {dia_obj.get('mes_ano', '')}*\n"
    texto_wpp += f"📋 *Jornada:* {dia_obj.get('config_jornada', '')}\n"
    if dia_obj.get('gerado_por'):
        texto_wpp += f"👤 *Gestor:* {dia_obj['gerado_por']}\n"
    if dia_obj.get('ronda_nome'):
        texto_wpp += f"🚨 *Ronda do Dia:* {dia_obj['ronda_nome']}\n"
    if dia_obj.get('ajuste_manual'):
        texto_wpp += f"📝 *Obs:* {dia_obj['ajuste_manual']}\n"
    texto_wpp += "\n"

    if dia_obj.get("escala_fixa"):
        texto_wpp += "📌 *ESCALA FIXA (Posto Único)*\n\n"
        for r in dia_obj["escala_fixa"]:
            texto_wpp += f"• *{r['posto']}:* {r['funcionario']}\n"
        texto_wpp += "\n"
    else:
        if dia_obj.get("t1_postos"):
            texto_wpp += f"☀️ *Turno 1 - Manhã (08:00 às 14:00)*\n"
            for r in dia_obj["t1_postos"]:
                texto_wpp += f"• *{r['posto']}:* {r['funcionario']}\n"
        if dia_obj.get("t2_postos"):
            texto_wpp += f"\n🌙 *Turno 2 - Tarde (14:00 às 20:00)*\n"
            for r in dia_obj["t2_postos"]:
                texto_wpp += f"• *{r['posto']}:* {r['funcionario']}\n"

        if dia_obj.get("pausas_15min_tarde"):
            texto_wpp += "\n⏱️ *Pausas 15 min (Tarde)*\n"
            for p in dia_obj["pausas_15min_tarde"]:
                texto_wpp += f"- {p['horario']}: {p['descricao']}\n"

        if dia_obj.get("escala_almoco"):
            texto_wpp += "\n🍽️ *Escala de Almoço / Refeição*\n"
            for a in dia_obj["escala_almoco"]:
                texto_wpp += f"- {a['horario']}: {a['descricao']}\n"

    dia_obj["link_whatsapp"] = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_wpp)}"
