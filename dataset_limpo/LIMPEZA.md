# Limpeza dos dados

Origem: `dataset_artefato/` (dados brutos, mantidos sem alteração).
Resultado: `dataset_limpo/`, gerado por `scripts/limpar_dados.py`.

## O que foi retirado

| Arquivo | Retirado | Motivo |
|---|---|---|
| dataset_tarefas | coluna `custo_hora_responsavel` | Cópia exata de `custo_hora` do dataset_time (120 de 120 linhas iguais). |
| dataset_tarefas | `data_fim_real` de 6 tarefas em andamento (TASK-065, 066, 067, 071, 113, 114) | Tarefa com status "In Progress" não tem data de fim real; o valor distorceria o cálculo de atraso. |
| dataset_time | coluna `horas_semana_disponiveis` | Valor constante (40 h para todos); não diferencia ninguém. A capacidade de 40 h/semana fica registrada aqui. |
| dataset_backlog | colunas `velocity_pontos`, `tarefas_com_mudanca_escopo`, `tarefas_com_retrabalho` | Repetem o que dataset_tarefas registra tarefa a tarefa e contradizem esses valores (ex.: velocity 22 vs. 91 story points concluídos na sprint 8). Fonte única adotada: dataset_tarefas. |
| dataset_atas | ata da Retrospectiva da sprint 3 (2024-09-27) | Linha vazia: sem participantes nem resumo, e com uma coluna a mais. |

## O que foi ajustado

- **dataset_time:** utilização convertida de texto (`75%`) para número (`75`); colunas renomeadas para `sprint_N_utilizacao_pct`.
- **dataset_atas:** linhas ordenadas por sprint (a 5 vinha antes da 4); colunas novas `n_participantes` e `ausentes`, calculadas a partir de `participantes`, para medir silos.

## O que foi mantido de propósito (não é ruído)

- **4 tarefas concluídas sem `horas_gastas` e `custo_real`** (TASK-031, 055, 085, 092): continuam valendo para story points, status e dependências. Ficam fora só das somas de horas e custo. Os valores não foram inventados.
- **3 tarefas concluídas sem `impedimentos`** (TASK-023, 038, 082) e **2 sem `data_inicio_real`** (TASK-040, 081): campo em branco = informação desconhecida, não zero.
- **Felipe sem tarefas:** é o PM; aparece no dataset_time e nas atas.
- **`custo_estimado` e `custo_real`:** são horas × custo/hora, mas mostram o impacto financeiro direto.

## Limitações que continuam nos dados

- Não há ata das sprints 3, 7 e 10.
- No backlog, os itens no fim de uma sprint não batem com o início da seguinte (ex.: 6 → 14 da sprint 1 para a 2).
- A utilização do dataset_time não bate com as horas gastas nas tarefas (Ana: 128% vs. 172 h na sprint 9).
- TASK-113 (sprint 9) depende de TASK-074, que é da sprint 10.
- A ata da sprint 9 cita 40% de retrabalho; as tarefas mostram 31% (5 de 16).
