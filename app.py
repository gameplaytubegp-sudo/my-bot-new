import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def mapear_cor(numero):
    if numero == 0 or numero == 15:
        return "BRANCO"
    elif 1 <= numero <= 7:
        return "VERMELHO"
    elif 8 <= numero <= 14:
        return "PRETO"
    return "DESCONHECIDO"

def analisar_proxima_jogada(historico):
    # ATUALIZADO PARA 100 RODADAS
    if len(historico) < 100:
        return {
            "sugestao": "AGUARDANDO DADOS", 
            "confianca": "0%", 
            "motivo": f"Coletando histórico longo... ({len(historico)}/100)"
        }

    numeros = [h['numero'] for h in historico]
    cores = [mapear_cor(n) for n in numeros]
    ultimas = cores[-6:] # Analisa as últimas 6 para padrões curtos
    agora = datetime.now()
    
    # ESTRATÉGIA 1: Quebra de Sequência (Gale)
    if ultimas.count("VERMELHO") >= 4:
        sugestao, confianca, motivo = "PRETO", "Alta", "Sequência longa de Vermelho (Quebra)"
    elif ultimas.count("PRETO") >= 4:
        sugestao, confianca, motivo = "VERMELHO", "Alta", "Sequência longa de Preto (Quebra)"
    
    # ESTRATÉGIA 2: Alerta de Branco (Baseado em 100 rodadas)
    elif "BRANCO" not in cores[-40:]:
        sugestao, confianca, motivo = "BRANCO", "Estratégica", "Mais de 40 rodadas sem Branco"
    
    # ESTRATÉGIA 3: Padrão Alternado (Xadrez)
    elif ultimas[-4:] == ["VERMELHO", "PRETO", "VERMELHO", "PRETO"]:
        sugestao, confianca, motivo = "PRETO", "Média", "Padrão Xadrez detectado"
    
    else:
        sugestao, confianca, motivo = "AGUARDAR", "Baixa", "Sem padrão claro nas 100 rodadas"

    return {
        "sugestao": sugestao,
        "confianca": confianca,
        "motivo": motivo,
        "horario": agora.strftime("%H:%M:%S")
    }

@app.route('/')
def home():
    return "API do Bot Double Online (Modo 100 Rodadas)"

@app.route('/prever', methods=['POST'])
def prever():
    data = request.get_json()
    if not data or 'historico' not in data:
        return jsonify({"erro": "JSON inválido"}), 400
    return jsonify(analisar_proxima_jogada(data['historico']))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
