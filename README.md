# Monitor de Preços — Zaffari e Pão de Açúcar

Projeto para coletar semanalmente preços de itens associados à inflação de alimentos e produtos de mercado, salvando uma série histórica por loja.

## ⚠️ Antes de automatizar no GitHub: teste local primeiro

**Este robô ainda não foi testado contra os sites reais.** Antes de subir para o GitHub Actions, rode o teste rápido no seu computador — é rápido e evita descobrir problemas só depois de uma semana de execuções silenciosamente erradas.

```bash
pip install -r requirements.txt
python -m playwright install chromium
python teste_rapido.py
```

Isso abre um navegador **visível** (não headless) buscando "Arroz" no Zaffari, e mostra o resultado encontrado. Confira:

- O navegador conseguiu abrir o site normalmente, ou apareceu captcha / bloqueio / pedido de localização?
- O produto encontrado (`produto_encontrado`) é realmente arroz, ou é outra coisa com "R$" no texto?
- O preço (`preco`) faz sentido?
- O `status` veio `ok` ou `revisar_match`?

Troque `LOJA_TESTE = "zaffari"` para `"pao_de_acucar"` no arquivo `teste_rapido.py` e rode de novo para testar a outra loja.

### Por que isso importa especialmente para o GitHub Actions

Sites grandes de varejo costumam ter proteção contra automação (ex. Cloudflare) que analisa o IP de origem, entre outros sinais. IPs de provedores de nuvem — como os usados pelo GitHub Actions — são mais propensos a cair em bloqueios ou desafios (captcha) do que uma conexão doméstica normal. **Isso quer dizer que o robô pode funcionar no seu computador e falhar no GitHub Actions.** Não há como garantir de antemão; o jeito de saber é rodar o workflow manualmente uma vez (`workflow_dispatch`) e checar os resultados antes de confiar na automação semanal.

Se isso acontecer, o caminho mais simples (sem precisar de serviços pagos de proxy) é manter a coleta rodando no seu próprio computador (ou um Raspberry Pi / mini PC sempre ligado em casa) via uma tarefa agendada do Windows/Linux, em vez do GitHub Actions. O GitHub Actions é ótimo quando funciona, mas depende do site não bloquear datacenter — o que está fora do seu controle.

## Estrutura

- `data/itens_monitorados.csv`: lista de itens, termo de busca e unidade padrão.
- `src/coletor.py`: robô de coleta com Playwright.
- `src/normalizacao.py`: funções de extração de preço e correspondência de texto.
- `teste_rapido.py`: testa 1 item, em modo visível, antes de rodar tudo.
- `saidas/historico_precos_long.csv`: histórico em formato longo, criado após a primeira execução.
- `monitor_precos_zaffari_pao_de_acucar.xlsx`: planilha-base, com abas `Zaffari` e `Pao_de_Acucar` (52 semanas pré-criadas), `Itens_monitorados`, `Configuracao` e `Resumo`.
- `.github/workflows/coleta_semanal.yml`: automação semanal no GitHub Actions.

## Como rodar a lista completa no computador

```bash
pip install -r requirements.txt
python -m playwright install chromium
CAMINHO_EXCEL="monitor_precos_zaffari_pao_de_acucar.xlsx" python src/coletor.py
```

No Windows PowerShell:

```powershell
pip install -r requirements.txt
python -m playwright install chromium
$env:CAMINHO_EXCEL="monitor_precos_zaffari_pao_de_acucar.xlsx"
python src/coletor.py
```

Isso roda os 150 itens nas duas lojas (pode levar bastante tempo, há uma pausa de ~2s entre buscas para não sobrecarregar os sites).

## Como funciona

1. O robô lê `data/itens_monitorados.csv`.
2. Pesquisa cada item no Zaffari e no Pão de Açúcar (itens com `coletar = não` são pulados, mas registrados como `nao_coletado`).
3. Extrai cards de produto que contenham preço em `R$`.
4. Escolhe o melhor candidato por compatibilidade do texto com o termo de busca.
5. Se o card tiver **mais de um preço** (ex. combo, "de X por Y"), marca `revisar_match` em vez de simplesmente assumir o menor valor — confira manualmente esses casos.
6. Salva o resultado em `saidas/historico_precos_long.csv` (sempre, mesmo sem planilha configurada).
7. Se `CAMINHO_EXCEL` estiver definido, atualiza as abas `Zaffari` e `Pao_de_Acucar` da planilha-base, **preenchendo a linha de "Semana" cuja data já bate com hoje** (a planilha já vem com 52 semanas pré-criadas; o robô não cria linhas novas).
8. Também recria a aba `Coletas_Detalhadas` para auditoria completa.

## Atenção importante

Sites de supermercado mudam layout com frequência, podem exigir localização, login, cookies ou confirmação de loja. Por isso, a primeira execução precisa ser conferida manualmente. Os resultados com status `revisar_match`, `nao_encontrado` ou `erro`/`erro_timeout` devem ser revisados antes de uso em relatório.

Por padrão, itens alcoólicos da lista ficam marcados como `coletar = não` no CSV. Eles permanecem na estrutura da planilha apenas para preservar a lista original, mas não são coletados automaticamente.

## Formato recomendado para análise

A base longa é a mais segura para conferência:

| data_coleta | loja | item | produto_encontrado | preco | status | qtd_precos_no_card |
|---|---|---|---|---:|---|---:|

A planilha larga, com datas nas linhas e itens nas colunas, é atualizada para uso final e visualização.

## Subindo para o GitHub Actions

Depois de testar localmente e confiar no resultado:

1. Crie um repositório no GitHub (ex. `monitor-precos-mercado`).
2. Suba todos os arquivos desta pasta (mantendo a estrutura: `src/`, `data/`, `.github/workflows/`, e a planilha na raiz).
3. Na aba **Actions** do repositório, abra o workflow **"Coleta semanal de preços"**.
4. Use **Run workflow** para testar manualmente uma vez antes de confiar no agendamento automático.
5. Confira o resultado: baixe o artefato de log (`erros_ultima_coleta.json`) e veja se a planilha foi atualizada corretamente no commit gerado pelo bot.
6. Se funcionar bem, ele passa a rodar automaticamente toda segunda-feira às 9h (horário de Brasília).

O workflow já está configurado para comitar os resultados (`historico_precos_long.csv` e a planilha) de volta no repositório automaticamente após cada execução.
