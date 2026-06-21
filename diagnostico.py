"""
Diagnóstico: abre o site do Zaffari, tenta fazer a busca, e SALVA EM ARQUIVOS
(screenshot + html + lista de campos de input encontrados) em vez de depender
de você ver a janela do navegador em tempo real.

Rodar:
    python3 diagnostico.py

Depois, abra os arquivos gerados na pasta "diagnostico/":
    - 1_pagina_inicial.png   -> como a home do site carregou
    - 2_apos_busca.png       -> como ficou depois de tentar buscar "arroz 5kg"
    - pagina_inicial.html    -> HTML completo da home (para inspecionar campos)
    - campos_input.txt       -> lista de TODOS os campos <input> encontrados na home
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

URL = "https://www.zaffari.com.br/"
TERMO = "arroz 5kg"
OUT = Path("diagnostico")
OUT.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=True: não depende de janela aparecer
        context = await browser.new_context(locale="pt-BR", timezone_id="America/Sao_Paulo")
        page = await context.new_page()

        print(f"Acessando {URL} ...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)
        await page.screenshot(path=str(OUT / "1_pagina_inicial.png"), full_page=False)
        html = await page.content()
        (OUT / "pagina_inicial.html").write_text(html, encoding="utf-8")
        print(f"Título da página: {await page.title()}")

        # Lista TODOS os inputs da página, com seus atributos, para vermos
        # qual deveria ser usado para a busca.
        inputs = await page.eval_on_selector_all(
            "input",
            "els => els.map(e => ({type: e.type, name: e.name, placeholder: e.placeholder, id: e.id, class: e.className}))"
        )
        with open(OUT / "campos_input.txt", "w", encoding="utf-8") as f:
            f.write(f"Total de campos <input> encontrados: {len(inputs)}\n\n")
            for i, inp in enumerate(inputs):
                f.write(f"[{i}] type={inp.get('type')!r} name={inp.get('name')!r} "
                        f"placeholder={inp.get('placeholder')!r} id={inp.get('id')!r} "
                        f"class={inp.get('class')!r}\n")
        print(f"Encontrei {len(inputs)} campos <input>. Veja diagnostico/campos_input.txt")

        # Tenta clicar em "aceitar cookies" por garantia
        for texto in ["Aceitar", "Aceito", "Entendi", "Permitir", "Continuar", "Concordo"]:
            try:
                btn = page.get_by_role("button", name=texto)
                if await btn.count() > 0:
                    await btn.first.click(timeout=2500)
                    print(f"Cliquei no botão de cookies: {texto}")
                    break
            except Exception:
                pass

        # Tenta a busca com o primeiro seletor mais específico que existir
        seletores_busca = [
            "input[type='search']",
            "input[placeholder*='Busca' i]",
            "input[placeholder*='Pesquis' i]",
            "input[name*='search' i]",
            "input[name*='busca' i]",
        ]
        usado = None
        for sel in seletores_busca:
            try:
                loc = page.locator(sel)
                if await loc.count() > 0:
                    usado = sel
                    print(f"Usando seletor: {sel}")
                    await loc.first.click(timeout=10000)
                    await loc.first.fill(TERMO, timeout=10000)
                    await loc.first.press("Enter", timeout=10000)
                    break
            except Exception as e:
                print(f"Seletor {sel} falhou: {e}")

        if usado is None:
            print("NENHUM seletor de busca específico funcionou.")

        await page.wait_for_timeout(5000)
        await page.screenshot(path=str(OUT / "2_apos_busca.png"), full_page=False)
        print(f"URL final: {page.url}")
        print(f"Título final: {await page.title()}")

        await browser.close()
        print("\nPronto! Veja a pasta 'diagnostico/' com os arquivos gerados.")


if __name__ == "__main__":
    asyncio.run(main())
