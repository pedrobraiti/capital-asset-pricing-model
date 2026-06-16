# TODO

Plano vivo do projeto. Tarefas e subtarefas, marcadas conforme concluídas.

## Em progresso
<nada — v1.0 publicado>

## Próximas
<vazio — estudo concluído (v1.0)>
Ideias futuras (opcional): 5x5 size×B/M heatmap de alfas; bootstrap CIs nos prêmios;
versão internacional (Fama-French Developed); 4-fator BAB stock-level.

## Concluído
- [x] Ler o paper Fama & French (2004)
- [x] Varrer projeto de referência (volume-profile-trading)
- [x] Confirmar fonte de dados (Ken French) e acesso de rede
- [x] Setup inicial do projeto
- [x] Data loader da biblioteca Ken French (download + cache, parser robusto, deciles D1..D10)
- [x] Máquina estatística (OLS Newey-West, teste GRS, Fama-MacBeth, métricas de performance)
  validada: alfa de valor +6%/yr t=3.1; GRS CAPM rejeita B/M (p=0.02), 3F não (p=0.26); SML achatada via FM
- [x] Módulos empíricos: SML achatada, valor/tamanho/momentum (sorts), prêmios de fator, painel GRS, momentum, BAB
  validados: FM slope -0.65% t=-0.16; premia t-stats batem com o paper (3.55/2.08/3.79); SMB/HML somem pós-2003; BAB alpha +2.3% t=1.9
- [x] Reporting (style + 10 charts) e pipeline (run_study.py, build_figures.py); figuras geradas em output/figures
- [x] Testes pytest (13 testes: regressão/HAC, GRS, métricas, parser de dados) — todos passando
- [x] README profissional em inglês com resultados, tabelas e 10 gráficos embutidos + referências
