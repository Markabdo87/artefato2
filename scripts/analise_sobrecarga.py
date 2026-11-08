"""Hipótese: a sobrecarga não é do time, é de 2 pessoas no caminho crítico.

Versão 2 (revisada): compara as duas fontes de carga, usa só sprints
fechadas (1-9) nas médias e calcula a folga pelo trabalho já planejado
para a sprint 10, não pela utilização parcial dela.

Lê dataset_limpo/, imprime os cálculos e grava analise_sobrecarga.png.
Uso: python scripts/analise_sobrecarga.py   (requer matplotlib)
"""
import csv
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "dataset_limpo")
rd = lambda f: list(csv.DictReader(open(os.path.join(DATA, f), encoding="utf-8")))
team, tasks = rd("dataset_time.csv"), rd("dataset_tarefas.csv")
byid = {t["task_id"]: t for t in tasks}
S = list(range(1, 11))
FECHADAS = list(range(1, 10))  # sprint 10 em andamento: fora das médias
CAP = 80  # h por sprint = 100% (40 h/semana x 2 semanas)
DEVS = ["Ana", "Bruno", "Carla", "Diego", "Elena"]  # Felipe não tem tarefas
deps = lambda t: [d for d in t["dependencias"].split(";") if d]

util = {m["membro"]: [int(m[f"sprint_{s}_utilizacao_pct"]) for s in S] for m in team}
hg, he = defaultdict(float), defaultdict(float)
for t in tasks:
    k = (t["responsavel"], int(t["sprint"]))
    he[k] += float(t["horas_estimadas"])
    hg[k] += float(t["horas_gastas"] or 0)

# ---------------------------------------------------------------- 0. as duas fontes batem?
print("0) UTILIZAÇÃO (dataset_time) x HORAS GASTAS / 80 h (dataset_tarefas), sprints 1-9")
xs, ys = [], []
for p in DEVS:
    print(f"   {p:6} util  " + " ".join(f"{util[p][s-1]:>4}" for s in FECHADAS))
    print(f"   {'':6} horas " + " ".join(f"{hg[(p, s)]/CAP*100:>4.0f}" for s in FECHADAS))
    for s in FECHADAS:
        xs.append(util[p][s - 1]); ys.append(hg[(p, s)] / CAP * 100)
mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
r = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (
    sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
print(f"   correlação entre as fontes: r = {r:.2f}")
for s in range(6, 10):
    top_u = sorted(DEVS, key=lambda p: -util[p][s - 1])[:2]
    top_h = sorted(DEVS, key=lambda p: -hg[(p, s)])[:2]
    print(f"   sprint {s}: 2 mais carregados  util={sorted(top_u)}  horas={sorted(top_h)}")
print(f"   Ana na sprint 9: {hg[('Ana', 9)]:.0f} h em ~10 dias úteis = {hg[('Ana', 9)]/10:.0f} h/dia (implausível); "
      f"utilização 128% = {1.28*40:.0f} h/semana (bate com a ata: '50+ horas por semana')")

# ---------------------------------------------------------------- 1. utilização (sprints fechadas)
print("\n1) UTILIZAÇÃO (%) — média das sprints 6-9 (fechadas)")
for p, v in util.items():
    print(f"   {p:8} média 6-9 = {sum(v[5:9])/4:6.1f}   sprints >100% (1-9) = {sum(x > 100 for x in v[:9])}")

# ---------------------------------------------------------------- 1b. folga real para a próxima sprint
print("\n1b) FOLGA PARA REDISTRIBUIR (100% - maior entre: utilização na sprint 9 e horas já planejadas na sprint 10)")
folga_total = 0
for p in ["Bruno", "Carla", "Elena"]:
    plan10 = he[(p, 10)] / CAP * 100
    carga = max(util[p][8], plan10)
    folga = max(0, 100 - carga)
    folga_total += folga
    print(f"   {p:6} util S9 = {util[p][8]:>3}%  planejado S10 = {plan10:>4.0f}%  folga = {folga:>3.0f} pp = {folga/100*CAP:>4.0f} h")
print(f"   folga total = {folga_total:.0f} pp = {folga_total/100*CAP:.0f} h por sprint")
e10 = [t for t in tasks if t["sprint"] == "10" and t["responsavel"] == "Elena" and t["status"] == "To Do"]
print(f"   Elena tem {sum(float(t['horas_estimadas']) for t in e10):.0f} h 'To Do' na sprint 10, "
      f"todas esperando Ana/Diego: {', '.join(t['task_id'] for t in e10)}")

# ---------------------------------------------------------------- 2. dependências
open_t = [t for t in tasks if t["status"] != "Done"]
all_dep, open_dep, waiting = Counter(), Counter(), defaultdict(set)
for t in open_t:
    for d in deps(t):
        owner = byid[d]["responsavel"]
        all_dep[owner] += 1
        if byid[d]["status"] != "Done":
            open_dep[owner] += 1
            waiting[owner].add(t["task_id"])
tot_all, tot_open = sum(all_dep.values()), sum(open_dep.values())
print(f"\n2) DEPENDÊNCIAS DAS {len(open_t)} TAREFAS ABERTAS")
for p in sorted(all_dep, key=lambda p: -open_dep[p]):
    print(f"   {p:6} todas={all_dep[p]:>3}  ainda abertas={open_dep[p]:>3}  tarefas que esperam={len(waiting[p]):>3}")
ad = open_dep["Ana"] + open_dep["Diego"]
print(f"   Ana + Diego = {ad} de {tot_open} = {ad/tot_open:.0%}")

# ---------------------------------------------------------------- 3. caminho até o go-live
def ancestors(tid, seen=None):
    seen = set() if seen is None else seen
    for d in deps(byid[tid]):
        if d not in seen and byid[d]["status"] != "Done":
            seen.add(d)
            ancestors(d, seen)
    return seen

chain = ancestors("TASK-080")
sp = Counter()
for t in chain:
    sp[byid[t]["responsavel"]] += int(byid[t]["story_points"])
tot_sp = sum(sp.values())
print(f"\n3) CAMINHO ATÉ O GO-LIVE: {len(chain)} tarefas abertas, {dict(sp)} SP")
print(f"   Ana + Diego = {sp['Ana'] + sp['Diego']} de {tot_sp} SP = {(sp['Ana'] + sp['Diego'])/tot_sp:.0%}")

# ---------------------------------------------------------------- heatmap
plt.rcParams.update({"font.family": ["Helvetica", "DejaVu Sans"], "font.size": 10})
fig, ax = plt.subplots(figsize=(10, 4.4), facecolor="white")
names = list(util)
mat = [util[p] for p in names]
cmap = LinearSegmentedColormap.from_list("u", ["#eff6ff", "#93c5fd", "#fde68a", "#f97316", "#b91c1c"])
im = ax.imshow(mat, cmap=cmap, vmin=50, vmax=130, aspect="auto")
for i, row in enumerate(mat):
    for j, v in enumerate(row):
        ax.text(j, i, f"{v}", ha="center", va="center", fontsize=9,
                color="white" if v >= 100 else "#1f2328", weight="bold" if v > 100 else "normal")
ax.add_patch(Rectangle((8.5, -0.5), 1, len(names), fill=False, hatch="///", edgecolor="#6b7280", lw=0))
roles = {m["membro"]: m["papel"].split(" /")[0] for m in team}
ax.set_yticks(range(len(names)))
ax.set_yticklabels([f"{p} ({roles[p]})" + (" *" if p == "Felipe" else "") for p in names])
ax.set_xticks(range(10)); ax.set_xticklabels([str(s) for s in S[:9]] + ["10\n(em andamento)"]); ax.set_xlabel("sprint")
for sp_ in ax.spines.values(): sp_.set_visible(False)
ax.tick_params(length=0)
cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02); cb.set_label("% da capacidade (80 h/sprint)")
cb.outline.set_visible(False)
ax.set_title("Utilização por pessoa e sprint (%) — só Ana e Diego passam de 100%", loc="left", weight="bold", fontsize=12)
fig.text(0.01, 0.01, "* Felipe não tem tarefas registradas: a utilização dele não pode ser conferida com dataset_tarefas. "
         "Sprint 10 em andamento (0 de 19 tarefas concluídas).", fontsize=8, color="#6b7280")
fig.tight_layout(rect=(0, 0.04, 1, 1))
out = os.path.join(BASE, "analise_sobrecarga.png")
fig.savefig(out, dpi=160)
print("\nheatmap:", out)
