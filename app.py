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
    # EXIGE 100 RODADAS PARA PRECISÃO MÁXIMA
    if len(historico) < 100:
        return {
            "sugestao": "AGUARDANDO DADOS", 
            "confianca": "0%", 
            "motivo": f"Alimentando base de dados... ({len(historico)}/100)"
        }

    numeros = [h['numero'] for h in historico]
    cores = [mapear_cor(n) for n in numeros]
    ultimas = cores[-6:] 
    
    # --- ESTRATÉGIAS DE ANÁLISE ---
    
    # 1. Quebra de Sequência (Gale)
    if ultimas.count("VERMELHO") >= 4:
        sugestao, motivo = "PRETO", "Sequência de Vermelho (Estratégia de Quebra)"
    elif ultimas.count("PRETO") >= 4:
        sugestao, motivo = "VERMELHO", "Sequência de Preto (Estratégia de Quebra)"
    
    # 2. Padrão Xadrez (Alternado)
    elif ultimas[-4:] == ["VERMELHO", "PRETO", "VERMELHO", "PRETO"]:
        sugestao, motivo = "PRETO", "Padrão Xadrez detectado"
    elif ultimas[-4:] == ["PRETO", "VERMELHO", "PRETO", "VERMELHO"]:
        sugestao, motivo = "VERMELHO", "Padrão Xadrez detectado"
        
    # 3. Alerta de Branco (Frequência em 100 rodadas)
    elif "BRANCO" not in cores[-45:]:
        sugestao, motivo = "BRANCO", "Filtro de 45 rodadas sem Branco"
    
    else:
        sugestao, motivo = "AGUARDAR", "Aguardando confirmação de padrão lucrativo"

    return {
        "sugestao": sugestao,
        "confianca": "Alta" if sugestao != "AGUARDAR" else "Nula",
        "motivo": motivo,
        "horario": datetime.now().strftime("%H:%M:%S")
    }

@app.route('/')
def home():
    return "API Bot Double 100 Rodadas - Online"

@app.route('/prever', methods=['POST'])
def prever():
    data = request.get_json()
    if not data or 'historico' not in data:
        return jsonify({"erro": "Dados insuficientes"}), 400
    
    resultado = analisar_proxima_jogada(data['historico'])
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
