import re
import unicodedata
from decimal import Decimal, InvalidOperation

PRECO_RE = re.compile(r"R\$[\s\xa0]*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})")


def normalizar_texto(txt: str) -> str:
    txt = txt or ""
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    txt = txt.lower()
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def extrair_precos(texto: str):
    valores = []
    for m in PRECO_RE.finditer(texto or ""):
        bruto = m.group(1).replace(".", "").replace(",", ".")
        try:
            valores.append(float(Decimal(bruto)))
        except (InvalidOperation, ValueError):
            pass
    return valores


def score_match(termo_busca: str, texto_produto: str) -> float:
    termo = normalizar_texto(termo_busca)
    texto = normalizar_texto(texto_produto)
    if not termo or not texto:
        return 0.0
    tokens = [t for t in termo.split() if len(t) > 2]
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in texto)
    score = hits / len(tokens)
    # Bônus se a expressão inteira aparece no card
    if termo in texto:
        score += 0.25
    return min(score, 1.0)
