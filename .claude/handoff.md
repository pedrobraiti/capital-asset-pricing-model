# Handoff — de onde parei

> **Propósito:** este arquivo serve para que um chat NOVO saiba com precisão "de onde eu parei".
> É o PRIMEIRO arquivo que a próxima sessão lê.

**Última atualização:** 2026-06-16 — v1.1 (efeito-publicação + internacional) concluída.

## Onde parei
Projeto PUBLICADO e ampliado para v1.1: https://github.com/pedrobraiti/capital-asset-pricing-model
(branch `main`). Além da replicação v1.0, adicionei dois estudos a pedido do usuário:
(1) efeito-publicação estilo McLean-Pontiff (empirics/publication_effect.py) e (2) evidência
internacional por região (empirics/international.py + french.regional_factors). 12 figuras, 15 testes
pytest passando. Pipeline roda em segundos. v1.1 commitada e pushada (commit 90c7af4). Entregue.

## Contexto mental
Replicação empírica fiel do Fama & French (2004) + extensão out-of-sample pós-2003. Resultados-chave
(todos reproduzem o paper): SML achatada (FM slope -0.65% t=-0.16 vs CAPM +5.65%); alfa de valor
+8.2%/yr (t=2.9); GRS rejeita CAPM em quase tudo, FF3 salva size/value mas quebra em momentum;
prêmios 1927-2003 batem com o paper (t-stats 3.55/2.08/3.79); SMB e HML SOMEM pós-2003 (achado
próprio mais interessante); BAB com alpha +2.3%/yr e beta ~0. Dados do Ken French (cache local).

## Próximo passo concreto
Se ainda não publicado: `gh repo create capital-asset-pricing-model --public --source=. --remote=origin --push`.
Confirmar que as figuras renderizam no README do GitHub (caminhos relativos output/figures/*.png).

## Em aberto / armadilhas
- Cache em data/cache é git-ignored (reproduzível). Figuras e tabelas em output/ SÃO versionadas
  (necessário para o README renderizar no GitHub). paper_text.txt é git-ignored.
- Pequenas diferenças nos pontos dos prêmios vs paper são revisões de dados CRSP desde 2004 (t-stats batem).
- Parser do French: cuidado com normalização de newline no Windows (já resolvido em french._raw_text).

## Como retomar rápido
- venv: `& ".venv\Scripts\Activate.ps1"`. `pytest -q` deve dar 13 passing.
- Resultados: output/RESULTS.md e output/tables/*.csv. Figuras: output/figures/.
- Paper: JEP.FamaandFrench.pdf (e paper_text.txt extraído, git-ignored).
