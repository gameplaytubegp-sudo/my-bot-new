import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÕES DE MAPEAMENTO ---
def mapear_cor(numero):
    if numero == 0 or numero == 15:
        return "BRANCO"
    elif 1 <= numero <= 7:
        return "VERMELHO"
    elif 8 <= numero <= 14:
        return "PRETO"
    return "DESCONHECIDO"

# --- LÓGICA DE ANÁLISE ---
def analisar_proxima_jogada(historico):
    if len(historico) < 3:
        return {"sugestao": "AGUARDAR", "confianca": "Nula", "motivo": "Poucos dados"}

    # Extrai números e cores
    numeros = [h['numero'] for h in historico]
    cores = [mapear_cor(n) for n in numeros]
    
    ultimas = cores[-5:] # Analisa as últimas 5 saídas
    agora = datetime.now()
    
    # Exemplo de Padrão: Quebra de Sequência (Gale)
    if ultimas.count("VERMELHO") >= 3:
        sugestao = "PRETO"
        confianca = "Alta"
        motivo = "Sequência de Vermelho detectada"
    elif ultimas.count("PRETO") >= 3:
        sugestao = "VERMELHO"
        confianca = "Alta"
        motivo = "Sequência de Preto detectada"
    # Exemplo de Padrão: Alerta de Branco por tempo (minuto 0 ou 5)
    elif agora.minute % 5 == 0 and "BRANCO" not in cores[-10:]:
        sugestao = "BRANCO"
        confianca = "Estratégica"
        motivo = "Janela de Minuto Pagador"
    else:
        sugestao = "AGUARDAR"
        confianca = "Baixa"
        motivo = "Sem padrão claro no momento"

    return {
        "sugestao": sugestao,
        "confianca": confianca,
        "motivo": motivo,
        "horario_analise": agora.strftime("%H:%M:%S")
    }

# --- ROTAS DA API ---
@app.route('/')
def home():
    return "API do Bot Double está Online!"

@app.route('/prever', methods=['POST'])
def prever():
    data = request.get_json()
    if not data or 'historico' not in data:
        return jsonify({"erro": "Envie o historico no formato JSON"}), 400
    
    resultado = analisar_proxima_jogada(data['historico'])
    return jsonify(resultado)

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

