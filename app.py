import asyncio
from playwright.async_api import async_playwright
import requests
from flask import Flask, jsonify
from flask_cors import CORS
import threading

# CONFIGURAÇÕES DA SUA API NO RENDER
API_URL = "https://my-bot-new-3.onrender.com/prever"
SINAL_URL = "https://my-bot-new-3.onrender.com/prever/ultimo_sinal"
SITE_URL = "https://www.tipminer.com/br/historico/blaze/double"

app = Flask(__name__)
CORS(app)

scanner_ativo = False
cache_sinal = {"sugestao": "CONECTANDO", "confianca": "0%", "motivo": "Iniciando..."}

async def rodar_scanner():
    global scanner_ativo, cache_sinal
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(SITE_URL, wait_until="domcontentloaded")
        
        ultimo_num = None
        historico = []

        while scanner_ativo:
            try:
                el = await page.query_selector("div.cell__content.inline-flex.items-center.justify-center.rounded-md.border.font-bold > div")
                if el:
                    num = int(''.join(filter(str.isdigit, await el.inner_text())))
                    if num != ultimo_num:
                        ultimo_num = num
                        historico.append({"numero": num})
                        if len(historico) > 100: historico.pop(0)

                        # Envia para o Render
                        try:
                            requests.post(API_URL, json={"historico": historico}, timeout=5)
                            print(f"✅ Enviado: {num} (Total: {len(historico)})")
                            
                            # Busca o sinal de volta
                            res = requests.get(SINAL_URL, timeout=5)
                            if res.status_code == 200:
                                cache_sinal = res.json()
                        except: print("❌ Erro de conexão com Render")
                await asyncio.sleep(4)
            except: break
        await browser.close()

@app.route('/ligar')
def ligar():
    global scanner_ativo
    if not scanner_ativo:
        scanner_ativo = True
        threading.Thread(target=lambda: asyncio.run(rodar_scanner())).start()
    return jsonify({"status": "ok"})

@app.route('/obter_sinal_local')
def obter_sinal_local():
    return jsonify(cache_sinal)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
