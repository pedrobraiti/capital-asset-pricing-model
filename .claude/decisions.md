# Decisões arquiteturais/técnicas

Registro de decisões com o "porquê". Append-only — não edita entradas antigas.

## 2026-06-16 — Fonte de dados: Kenneth R. French Data Library
**Motivo:** É exatamente a fonte (derivada de CRSP/Compustat) usada no paper. Gratuita, sem API key,
URLs estáveis, cobre 1926→presente. Permite replicar fielmente os fatores (Mkt-RF, SMB, HML, RF),
momentum e os portfólios decis (size, B/M, beta, momentum) e as 25 carteiras size×B/M.
**Alternativas consideradas:** yfinance (sem fundamentals/book equity, survivorship bias, histórico curto);
CRSP individual (pago, inacessível). Ambos inviabilizariam a replicação fiel.

## 2026-06-16 — Estudo empírico de asset pricing, não "trading strategy"
**Motivo:** O paper é de testes empíricos do CAPM, não uma estratégia. O "backtest" fiel é testar o
modelo: SML achatada, alfas de Jensen, teste GRS, Fama-MacBeth, prêmios de fator. Adiciono um
backtest tradeável (Betting Against Beta) para dar o sabor de "estratégia" do projeto de referência.
**Alternativas consideradas:** inventar uma estratégia de trading desconexa do paper — rejeitado por
não ser fiel ao conteúdo do artigo.

## 2026-06-16 — Período: replicação (≤2003) + extensão out-of-sample (até ~2025)
**Motivo:** Decisão do usuário. Mostra fidelidade ao paper E contribuição própria (as anomalias
persistiram? o prêmio de valor enfraqueceu pós-2003?).
**Alternativas consideradas:** só o período do paper (sem contribuição moderna); só amostra completa
(perde a comparação direta com os números do paper).

## 2026-06-16 — Inferência: erros-padrão Newey-West e teste GRS exato
**Motivo:** Retornos têm heterocedasticidade/autocorrelação; Newey-West é padrão na literatura.
GRS (Gibbons-Ross-Shanken 1989) é o teste F exato de pequenas amostras citado no paper para a
hipótese conjunta de que todos os alfas são zero.
**Alternativas consideradas:** OLS simples (subestima SE); só t-stats individuais (não testa conjunto).
