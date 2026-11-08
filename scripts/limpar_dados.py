"""Limpeza dos 4 CSVs do artefato de Project Management N2.

Lê dataset_artefato/ (dados brutos, que não são alterados) e grava
dataset_limpo/ com apenas os dados que contribuem para a análise.
Cada regra aplicada está descrita em dataset_limpo/LIMPEZA.md.

Uso: python3 scripts/limpar_dados.py   (a partir da pasta "Artefato Módulo 2")
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "dataset_artefato")
OUT = os.path.join(BASE, "dataset_limpo")
os.makedirs(OUT, exist_ok=True)


def read(name):
    with open(os.path.join(RAW, name), encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} linhas, {len(header)} colunas")


# ---------------------------------------------------------------- time
raw = read("dataset_time.csv")
hdr, rows = raw[0], raw[1:]
drop = {"horas_semana_disponiveis"}  # constante (40 para todos)
keep = [i for i, c in enumerate(hdr) if c not in drop]
new_hdr = [hdr[i].replace("_utilizacao", "_utilizacao_pct") for i in keep]
new_rows = [[r[i].rstrip("%").strip() for i in keep] for r in rows]
write("dataset_time.csv", new_hdr, new_rows)

# ---------------------------------------------------------------- tarefas
raw = read("dataset_tarefas.csv")
hdr, rows = raw[0], raw[1:]
ix = {c: i for i, c in enumerate(hdr)}
drop = {"custo_hora_responsavel"}  # cópia exata de custo_hora em dataset_time
keep = [i for i, c in enumerate(hdr) if c not in drop]
cleared = []
for r in rows:
    # tarefa não concluída não pode ter data de fim real
    if r[ix["status"]] != "Done" and r[ix["data_fim_real"]]:
        cleared.append(r[ix["task_id"]])
        r[ix["data_fim_real"]] = ""
write("dataset_tarefas.csv", [hdr[i] for i in keep], [[r[i] for i in keep] for r in rows])
print("  data_fim_real apagada em:", ", ".join(cleared))

# ---------------------------------------------------------------- backlog
raw = read("dataset_backlog.csv")
hdr, rows = raw[0], raw[1:]
# duplicam (e contradizem) o que dataset_tarefas registra tarefa a tarefa
drop = {"velocity_pontos", "tarefas_com_mudanca_escopo", "tarefas_com_retrabalho"}
keep = [i for i, c in enumerate(hdr) if c not in drop]
write("dataset_backlog.csv", [hdr[i] for i in keep], [[r[i] for i in keep] for r in rows])

# ---------------------------------------------------------------- atas
raw = read("dataset_atas.csv")
hdr, rows = raw[0], raw[1:]
time_todo = [r[0] for r in read("dataset_time.csv")[1:]]
out = []
for r in rows:
    r = r[:5]  # descarta coluna extra (linha da sprint 3 tinha 6 campos)
    if not r[3].strip() and not r[4].strip():
        print(f"  ata removida (vazia): sprint {r[0]} {r[1]} {r[2]}")
        continue
    presentes = [p.strip() for p in r[3].split(",") if p.strip()]
    ausentes = [m for m in time_todo if m not in presentes]
    out.append([r[0], r[1], r[2], len(presentes), r[3], "; ".join(ausentes), r[4]])
out.sort(key=lambda r: (int(r[0]), r[2]))
write("dataset_atas.csv",
      ["sprint", "tipo_reuniao", "data", "n_participantes", "participantes", "ausentes", "resumo"], out)
