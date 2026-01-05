import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) # Permite que o seu site (index.html) acesse os dados

# Cache para o site ler o último sinal gerado
ultimo_sinal_cache = {
    "sugestao": "AGUARDANDO",
    "confianca": "0%",
    "motivo": "Iniciando sistema..."
}

def mapear_cor(numero):
    if numero == 0 or numero == 15:
        return "BRANCO"
    elif 1 <= numero <= 7:
        return "VERMELHO"
    elif 8 <= numero <= 14:
        return "PRETO"
    return "DESCONHECIDO"

def analisar_proxima_jogada(historico):
    if len(historico) < 100:
        return {
            "sugestao": "AGUARDANDO DADOS", 
            "confianca": "0%", 
            "motivo": f"Coletando histórico... ({len(historico)}/100)"
        }

    numeros = [h['numero'] for h in historico]
    cores = [mapear_cor(n) for n in numeros]
    ultimas = cores[-6:]
    
    # Estratégia
    if ultimas.count("VERMELHO") >= 4:
        sugestao, motivo = "PRETO", "Quebra de Sequência Vermelha"
    elif ultimas.count("PRETO") >= 4:
        sugestao, motivo = "VERMELHO", "Quebra de Sequência Preta"
    elif "BRANCO" not in cores[-45:]:
        sugestao, motivo = "BRANCO", "Alerta de Branco (45+ rodadas)"
    else:
        return {"sugestao": "AGUARDAR", "confianca": "10%", "motivo": "Aguardando padrão claro"}

    return {
        "sugestao": sugestao,
        "confianca": "90%",
        "motivo": motivo
    }

@app.route('/')
def home():
    return "API do Bot Double Online"

@app.route('/prever', methods=['POST'])
def prever():
    global ultimo_sinal_cache
    data = request.get_json()
    if not data or 'historico' not in data:
        return jsonify({"erro": "Dados inválidos"}), 400
    
    resultado = analisar_proxima_jogada(data['historico'])
    ultimo_sinal_cache = resultado # Salva o sinal para o site ler
    return jsonify(resultado)

@app.route('/prever/ultimo_sinal', methods=['GET'])
def buscar_ultimo():
    global ultimo_sinal_cache
    return jsonify(ultimo_sinal_cache)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
