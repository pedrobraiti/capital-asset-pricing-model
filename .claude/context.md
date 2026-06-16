# Contexto do projeto

> Camada **estável** da memória: o que o projeto é e suas características macro. Muda devagar.
> O detalhe volátil de "de onde parei" fica no `handoff.md`; as tarefas, no `todo.md`;
> as decisões com o porquê, no `decisions.md`.

**Nome:** capital-asset-pricing-model
**Descrição:** Replicação empírica e extensão out-of-sample do paper Fama & French (2004), "The Capital Asset Pricing Model: Theory and Evidence" (Journal of Economic Perspectives, 18(3):25–46).
**Stack:** Python 3.12, pandas, numpy, scipy, matplotlib. Dados: Kenneth R. French Data Library.

## Visão geral
Estudo de asset pricing que testa empiricamente o CAPM Sharpe-Lintner-Black usando os mesmos
dados (derivados de CRSP, via biblioteca do Ken French) que o paper usa. Reproduz os achados
centrais — Security Market Line "achatada", efeito valor (B/M), efeito tamanho, alfa de Jensen,
teste conjunto GRS, regressões cross-section de Fama-MacBeth, modelo de três fatores e momentum —
e estende tudo out-of-sample para depois de 2003 (até o dado mais recente, ~2025). Inclui também
um backtest tradeável "Betting Against Beta" (a estratégia implicada pela SML achatada).

Público: portfólio público profissional no GitHub. README em inglês, com resultados, gráficos e referências.

## Fase atual
Estudo concluído e publicado (v1.0). Repositório público no GitHub.

## Restrições e bloqueios de longo prazo
- Dados dependem da disponibilidade da biblioteca do Ken French (download HTTP + cache local).
- Sem CRSP individual (não é gratuito): a SML por beta usa portfólios pré-formados do French + cross-section.
- Não é recomendação de investimento; estudo acadêmico/educacional.
