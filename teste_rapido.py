"""
Teste rápido: roda a coleta para 1-2 itens, em modo visível (navegador abre na tela),
para você conferir manualmente se o seletor está achando o produto certo antes de
rodar a lista inteira (150 itens) ou subir para o GitHub Actions.

Como rodar:
    pip install -r requirements.txt
    python -m playwright install chromium
    python teste_rapido.py

Por padrão testa só "Arroz" no Zaffari. Edite ITEM_TESTE e LOJA_TESTE abaixo
para testar outros casos.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from playwright.async_api import async_playwright
from coletor import LOJAS, coletar_item

ITEM_TESTE = {
    "item": "Arroz",
    "termo_busca": "arroz prato fino 1kg",
    "unidade_padrao": "kg",
    "coletar": "sim",
}
LOJA_TESTE = "zaffari"  # troque para "pao_de_acucar" para testar a outra loja


async def main():
    loja_cfg = LOJAS[LOJA_TESTE]
    async with async_playwright() as p:
        # headless=False: o navegador ABRE NA TELA, assim você vê o que está
        # acontecendo (se aparece captcha, pedido de CEP, bloqueio, etc.)
        browser = await p.chromium.launch(headless=True, slow_mo=300)
        context = await browser.new_context(locale="pt-BR", timezone_id="America/Sao_Paulo")
        resultado = await coletar_item(context, LOJA_TESTE, loja_cfg, ITEM_TESTE)
        print()
        print("=" * 60)
        print("RESULTADO DO TESTE")
        print("=" * 60)
        for campo, valor in resultado.__dict__.items():
            print(f"{campo}: {valor}")
        print("=" * 60)
        print("\nFechando navegador...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
