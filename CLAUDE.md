# Instruções para o Claude neste projeto

## Memória persistente

Ao iniciar **qualquer** conversa neste projeto, antes de agir:
1. Leia `.claude/handoff.md` **PRIMEIRO** — é o ponteiro mais fresco: responde "de onde parei" com detalhe.
2. Leia `.claude/context.md` para o estado macro/estável do projeto.
3. Leia `.claude/todo.md` para saber o que está em progresso e o que vem a seguir.
4. Rode `git log --oneline -20` para ver atividade recente.
5. Se a tarefa tocar em área sensível/arquitetural, leia `.claude/decisions.md`.

### Manter o handoff vivo

O `.claude/handoff.md` é o que permite a **próxima sessão começar de onde esta parou**. Trate-o como documento vivo:
- Ao concluir qualquer passo significativo (não só no fim da sessão), atualize-o.
- Escreva com detalhe suficiente para um chat novo retomar sem reconstruir seu raciocínio.
- Atualize a data e **sobrescreva** o conteúdo antigo — reflete sempre o ESTADO ATUAL.

## Disciplina do TODO

- O `.claude/todo.md` é **mandatório** e deve sempre refletir a realidade do projeto.
- Marque `[x]` a subtarefa **no mesmo commit** em que ela é concluída.
- Subtarefas pequenas e modulares — se não cabe em um commit, quebra em menores.

## Disciplina de commits

- Sempre que uma subtarefa do TODO for **concluída**, faça um commit.
- Use **Conventional Commits**: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`, `style:`.
- Mensagens claras, no imperativo, descrevendo o **porquê** quando não óbvio.
- **Nunca** inclua `Co-Authored-By: Claude` nas mensagens de commit.
- Antes de cada commit, avalie e atualize **no mesmo commit** se necessário: `handoff.md`, `todo.md`,
  `context.md`, `decisions.md`, `README.md`, `.env.example`.

## Arquitetura

Seguir os padrões em `~/.claude/rules/BEST_PRACTICES.md` (código profissional, modular, testável).
Camadas: `data/` (ingestão+cache) → `stats/` (máquina estatística) → `empirics/` (estudos) →
`reporting/` (gráficos). Scripts em `scripts/` orquestram. Sem lookahead; betas/alfas com inferência
robusta (Newey-West, GRS).

## Reproduzir o estudo

```powershell
& ".venv\Scripts\Activate.ps1"
pip install -r requirements.txt
pytest -q
python scripts/run_study.py      # baixa (cacheia) dados do French e roda todos os testes
python scripts/build_figures.py  # gera todas as figuras em output/figures/
```
