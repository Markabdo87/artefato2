"""Previsão da data de go-live com as duas fontes (tarefas e backlog).

Tarefas: story points abertos (sprints 9-10) / velocidade recente em SP.
Backlog: itens restantes / itens concluídos por sprint (unidade própria).
Sprint = 14 dias. Go-live planejado: TASK-080, fim previsto 2025-01-06.
Grava previsao_golive.png.

Uso: python scripts/previsao_golive.py   (requer matplotlib)
"""
import csv
import os
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: list(csv.DictReader(open(os.path.join(BASE, p), encoding="utf-8")))
tasks = rd("dataset_limpo/dataset_tarefas.csv")
backlog = rd("dataset_artefato/dataset_backlog.csv")  # bruto: tem a velocity original
byid = {t["task_id"]: t for t in tasks}

SPRINT = 14
INICIO_S10 = date(2024, 12, 23)
PLANO = date.fromisoformat(byid["TASK-080"]["data_fim_prevista"])

done_sp = {s: sum(int(t["story_points"]) for t in tasks if int(t["sprint"]) == s and t["status"] == "Done")
           for s in range(1, 11)}
abertas = [t for t in tasks if t["status"] != "Done"]
open_sp = sum(int(t["story_points"]) for t in abertas)
h_est = sum(float(t["horas_estimadas"]) for t in abertas)
h_gasto = sum(float(t["horas_gastas"] or 0) for t in abertas)

print(f"Go-live planejado (TASK-080): {PLANO}")
print(f"Trabalho aberto: {len(abertas)} tarefas, {open_sp} SP "
      f"(sprint 9: {sum(int(t['story_points']) for t in abertas if t['sprint']=='9')}, "
      f"sprint 10: {sum(int(t['story_points']) for t in abertas if t['sprint']=='10')})")
print(f"Horas já gastas nas tarefas abertas: {h_gasto:.0f} de {h_est:.0f} estimadas ({h_gasto/h_est:.0%}), "
      f"com 0 SP entregue nelas")

def fim(sp, vel, inicio=INICIO_S10):
    sprints = sp / vel
    return sprints, inicio + timedelta(days=round(sprints * SPRINT))

def drift(d):
    dias = (d - PLANO).days
    return f"+{dias} dias (~{dias/7:.0f} semanas)"

# ---------------------------------------------------------------- fonte 1: tarefas
print("\nFONTE 1 — dataset_tarefas (SP concluídos por sprint):", [done_sp[s] for s in range(1, 10)])
cen = {
    "Otimista (média S6-8)": sum(done_sp[s] for s in (6, 7, 8)) / 3,
    "Realista (média S7-9)": sum(done_sp[s] for s in (7, 8, 9)) / 3,
    "Pessimista (sprint 9)": done_sp[9],
}
res_t = {}
for nome, v in cen.items():
    n, d = fim(open_sp, v)
    res_t[nome] = (v, n, d)
    print(f"  {nome:24} {v:5.1f} SP/sprint -> {n:4.1f} sprints -> {d}  drift {drift(d)}")

# ---------------------------------------------------------------- fonte 2: backlog
vel_b = [int(b["velocity_pontos"]) for b in backlog]
print("\nFONTE 2 — dataset_backlog (velocity):", vel_b)
vb = sum(vel_b[6:9]) / 3
n, d = fim(open_sp, vb)
print(f"  velocity do backlog aplicada aos SP das tarefas (mistura unidades): {vb:.0f}/sprint -> {n:.1f} sprints -> {d}  drift {drift(d)}")
res_b_naive = (vb, n, d)

restantes = int(backlog[-1]["itens_fim_sprint"])
concl = [int(b["itens_concluidos"]) for b in backlog[7:10]]
adic = [int(b["itens_adicionados"]) for b in backlog[7:10]]
taxa, entrada = sum(concl) / 3, sum(adic) / 3
fim_s10 = PLANO  # backlog já traz a sprint 10 fechada
n1, d1 = fim(restantes, taxa, fim_s10)
print(f"  na unidade do próprio backlog: {restantes} itens após a S10, {taxa:.1f} concluídos/sprint (S8-10)")
print(f"    escopo congelado:  {n1:.1f} sprints -> {d1}  drift {drift(d1)}")
liq = taxa - entrada
n2, d2 = fim(restantes, liq, fim_s10)
print(f"    escopo entrando como em S8-10 ({entrada:.1f} itens/sprint): queima líquida {liq:.1f}/sprint -> "
      f"{n2:.0f} sprints -> {d2}")
res_b = (n1, d1)

# ---------------------------------------------------------------- opções do PM
print("\nOPÇÕES LEVADAS AO SPONSOR (velocidade realista)")
vr = cen["Realista (média S7-9)"]
cam = {"TASK-080"}
def anc(tid):
    for x in [d for d in byid[tid]["dependencias"].split(";") if d]:
        if byid[x]["status"] != "Done" and x not in cam:
            cam.add(x); anc(x)
anc("TASK-080")
sp_cam = sum(int(byid[t]["story_points"]) for t in cam)
print(f"  caminho crítico até o go-live (inclui TASK-080): {len(cam)} tarefas, {sp_cam} SP")
for nome, prazo in (("Manter prazo, cortar escopo", PLANO), ("+2 semanas", PLANO + timedelta(14)),
                    ("+4 semanas", PLANO + timedelta(28))):
    sprints = (prazo - INICIO_S10).days / SPRINT
    cap = sprints * vr
    corte = max(0, open_sp - cap)
    print(f"  {nome:28} até {prazo}: {sprints:.0f} sprint(s) = {cap:.0f} SP de capacidade -> "
          f"cortar {corte:.0f} SP ({corte/open_sp:.0%})  | caminho crítico cabe? {'sim' if cap >= sp_cam else 'NÃO'}")

# ---------------------------------------------------------------- gráfico
plt.rcParams.update({"font.family": ["Helvetica", "DejaVu Sans"], "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(11, 4.8), facecolor="white")
cores = {"Otimista (média S6-8)": "#16a34a", "Realista (média S7-9)": "#2563eb", "Pessimista (sprint 9)": "#dc2626"}
for nome, (v, n, d) in res_t.items():
    xs = [INICIO_S10, d]; ys = [open_sp, 0]
    ax.plot(xs, ys, color=cores[nome], lw=2.2, label=f"{nome}: {d.strftime('%d/%m/%Y')}")
    ax.scatter([d], [0], color=cores[nome], zorder=3)
ax.plot([INICIO_S10, res_b[1]], [open_sp, 0], color="#9ca3af", lw=1.8, ls="--",
        label=f"Backlog (contado em itens, escala ajustada), escopo congelado: {res_b[1].strftime('%d/%m/%Y')}")
for nome, prazo, c in (("plano", PLANO, "#111827"), ("+2 sem.", PLANO + timedelta(14), "#6b7280"),
                       ("+4 sem.", PLANO + timedelta(28), "#6b7280")):
    ax.axvline(prazo, color=c, lw=1, ls=":")
    ax.text(prazo, open_sp * 1.02, nome, ha="center", fontsize=8.5, color=c)
ax.set_ylabel("story points em aberto"); ax.set_ylim(0, open_sp * 1.1)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.set_title(f"Previsão de go-live: {open_sp} SP em aberto a partir da sprint 10 (23/12)", loc="left", weight="bold")
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
fig.tight_layout()
out = os.path.join(BASE, "previsao_golive.png")
fig.savefig(out, dpi=160)
print("\ngráfico:", out)
