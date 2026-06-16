# Handoff — de onde parei

> **Propósito:** este arquivo serve para que um chat NOVO saiba com precisão "de onde eu parei",
> de forma relativamente detalhada. É o PRIMEIRO arquivo que a próxima sessão lê.

**Última atualização:** 2026-06-16 — durante o setup inicial.

## Onde parei
Acabei de ler o paper Fama & French (2004) por inteiro (extraído para texto via pypdf), varri o
projeto de referência `volume-profile-trading` para igualar o padrão de qualidade, e confirmei a
fonte de dados (Kenneth R. French Data Library, acesso de rede testado e funcionando — dados de
192607 até 202604). Estou montando o scaffold inicial (.claude, config, git).

## Contexto mental
O paper é de TESTES EMPÍRICOS do CAPM, não uma estratégia de trading. Logo o "backtest extenso"
fiel é uma replicação empírica: SML achatada (Fig. 2), efeito valor B/M (Fig. 3), efeito tamanho,
alfa de Jensen + teste conjunto GRS, regressões Fama-MacBeth, prêmios do modelo de 3 fatores e
momentum. Estendo tudo out-of-sample pós-2003. Adiciono um backtest tradeável "Betting Against
Beta" (a estratégia implicada pela SML achatada) para dar o sabor de estratégia do projeto de ref.

Usuário escolheu: README/docs em INGLÊS; período = replicação do paper + extensão até hoje.

## Próximo passo concreto
Terminar o scaffold (README skeleton, CLAUDE.md, LICENSE — já criados config/.claude), `git init`,
commit inicial, e então construir `src/capm/data/` (loader Ken French com cache parquet).

## Em aberto / armadilhas
- A biblioteca do French NÃO tem decis pré-ordenados por beta diretamente; a SML achatada (Fig. 2)
  será construída via cross-section de muitos portfólios decis (size, B/M, momentum) + estimação de
  beta full-sample, que É o teste cross-section do paper. Verificar se existe dataset de beta deciles.
- Formato dos CSVs do French tem cabeçalho/rodapé e múltiplas seções (monthly/annual) — parsing cuidadoso.
- Datas no formato YYYYMM (mensal) e YYYY (anual). Valores em PERCENTUAL (dividir por 100).

## Como retomar rápido
- Paper em texto: `paper_text.txt` (ignorado no git) e PDF `JEP.FamaandFrench.pdf`.
- venv já criado: `& ".venv\Scripts\Activate.ps1"`.
- Projeto de referência: `C:\Users\ACS Gamer\Documents\vscode-local\trading-BaTe-Claude\volume-profile-trading`.
