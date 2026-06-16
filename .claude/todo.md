# TODO

Plano vivo do projeto. Tarefas e subtarefas, marcadas conforme concluídas.

## Em progresso
- [ ] Módulos empíricos (SML achatada, valor, tamanho, alfas+GRS, 3 fatores, momentum, BAB)

## Próximas
- [ ] Módulos empíricos (SML achatada, valor, tamanho, alfas+GRS, 3 fatores, momentum, BAB)
- [ ] Reporting (charts) + pipeline (run_study.py)
- [ ] Testes pytest
- [ ] Rodar estudo, README profissional com resultados/gráficos, publicar no GitHub

## Concluído
- [x] Ler o paper Fama & French (2004)
- [x] Varrer projeto de referência (volume-profile-trading)
- [x] Confirmar fonte de dados (Ken French) e acesso de rede
- [x] Setup inicial do projeto
- [x] Data loader da biblioteca Ken French (download + cache, parser robusto, deciles D1..D10)
- [x] Máquina estatística (OLS Newey-West, teste GRS, Fama-MacBeth, métricas de performance)
  validada: alfa de valor +6%/yr t=3.1; GRS CAPM rejeita B/M (p=0.02), 3F não (p=0.26); SML achatada via FM
