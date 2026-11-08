"""Sinais de silo x impedimentos e retrabalho, por sprint.

Indicadores de silo: participação nas reuniões, sprint sem ata, dependências
entre pessoas diferentes e mudanças de escopo. Testa correlação (Pearson e
Spearman) com teste de permutação, com e sem controle do tamanho da sprint.
Usa só sprints fechadas (1-9). Grava analise_silos.png.

Uso: python scripts/analise_silos.py   (requer matplotlib)
"""
import csv
import os
import random
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "dataset_limpo")
rd = lambda f: list(csv.DictReader(open(os.path.join(DATA, f), encoding="utf-8")))
tasks, atas = rd("dataset_tarefas.csv"), rd("dataset_atas.csv")
byid = {t["task_id"]: t for t in tasks}
S = list(range(1, 11))
F = list(range(1, 10))  # sprints fechadas

# ---------------------------------------------------------------- indicadores por sprint
g = {s: defaultdict(float) for s in S}
for t in tasks:
    s = int(t["sprint"]); d = g[s]
    d["n"] += 1
    d["imp"] += int(t["impedimentos"] or 0)
    d["ret"] += t["retrabalho"] == "Sim"
    d["esc"] += t["mudanca_escopo"] == "Sim"
    ds = [x for x in t["dependencias"].split(";") if x]
    d["deps"] += len(ds)
    d["cross"] += sum(byid[x]["responsavel"] != t["responsavel"] for x in ds)
ata = {int(a["sprint"]): a for a in atas}
for s in S:
    g[s]["ata"] = 1 if s in ata else 0
    g[s]["part"] = int(ata[s]["n_participantes"]) if s in ata else None
    g[s]["aus"] = (6 - g[s]["part"]) if s in ata else None

print("INDICADORES POR SPRINT")
print("sprint tarefas  part  ausentes  ata  dep_total  dep_cruzada  %cruzada  escopo  impedim  retrab")
for s in S:
    d = g[s]
    pc = d["cross"] / d["deps"] * 100 if d["deps"] else 0
    print(f"{s:>6}{d['n']:>8.0f}{d['part'] if d['part'] is not None else '-':>6}"
          f"{d['aus'] if d['aus'] is not None else '-':>10}{'sim' if d['ata'] else 'NÃO':>5}"
          f"{d['deps']:>11.0f}{d['cross']:>13.0f}{pc:>9.0f}%{d['esc']:>8.0f}{d['imp']:>9.0f}{d['ret']:>8.0f}")

# ---------------------------------------------------------------- estatística
def pearson(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x) ** 0.5; sy = sum((b - my) ** 2 for b in y) ** 0.5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")

def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r

def spearman(x, y):
    return pearson(ranks(x), ranks(y))

def perm_p(x, y, f, n=20000, seed=7):
    rnd = random.Random(seed); obs = abs(f(x, y)); yy = list(y); hit = 0
    for _ in range(n):
        rnd.shuffle(yy)
        if abs(f(x, yy)) >= obs - 1e-12:
            hit += 1
    return hit / n

def resid(v, z):
    """resíduo de v após regressão linear em z (remove a tendência de z)."""
    mz, mv = sum(z) / len(z), sum(v) / len(v)
    b = sum((a - mz) * (c - mv) for a, c in zip(z, v)) / sum((a - mz) ** 2 for a in z)
    return [c - (mv + b * (a - mz)) for a, c in zip(z, v)]

def row(name, xs, ys, ss, sizes):
    rp, rs = pearson(xs, ys), spearman(xs, ys)
    pp = perm_p(xs, ys, pearson)
    # controle do tamanho da sprint (nº de tarefas): correlação parcial
    rpart = pearson(resid(xs, sizes), resid(ys, sizes))
    ppart = perm_p(resid(xs, sizes), resid(ys, sizes), pearson)
    print(f"{name:42} n={len(xs)}  Pearson={rp:+.2f} (p={pp:.3f})  Spearman={rs:+.2f}  "
          f"parcial|tamanho={rpart:+.2f} (p={ppart:.3f})")
    return rp, pp, rpart, ppart

results = {}
print("\nCORRELAÇÕES (sprints fechadas 1-9; p = teste de permutação, 20.000 sorteios)")
for target, lab in (("imp", "impedimentos"), ("ret", "retrabalho")):
    print(f"\n-> com {lab}")
    for key, name, subset in (
        ("cross", "dependências entre pessoas (nº)", F),
        ("pcross", "dependências entre pessoas (% do total)", F),
        ("esc", "tarefas com mudança de escopo", F),
        ("aus", "ausentes na reunião (só sprints com ata)", [s for s in F if g[s]["ata"]]),
        ("sem_ata", "sprint sem ata (0/1)", F),
        ("n", "nº de tarefas da sprint (controle)", F),
    ):
        def val(s):
            if key == "pcross":
                return g[s]["cross"] / g[s]["deps"] * 100 if g[s]["deps"] else 0
            if key == "sem_ata":
                return 1 - g[s]["ata"]
            return g[s][key]
        xs = [val(s) for s in subset]; ys = [g[s][target] for s in subset]; sz = [g[s]["n"] for s in subset]
        results[(key, target)] = row(name, xs, ys, subset, sz)

# normalizado por tarefa
print("\n-> taxas por tarefa (remove o efeito de sprints maiores)")
for target, lab in (("imp", "impedimentos/tarefa"), ("ret", "retrabalho/tarefa")):
    xs = [g[s]["cross"] / g[s]["n"] for s in F]; ys = [g[s][target] / g[s]["n"] for s in F]
    print(f"   dep. cruzadas/tarefa x {lab:20} Pearson={pearson(xs, ys):+.2f} (p={perm_p(xs, ys, pearson):.3f})")
    xs = [g[s]["esc"] / g[s]["n"] for s in F]
    print(f"   escopo/tarefa        x {lab:20} Pearson={pearson(xs, ys):+.2f} (p={perm_p(xs, ys, pearson):.3f})")

# sensibilidade: tirar uma sprint de cada vez
print("\nSENSIBILIDADE (leave-one-out, Pearson dep. cruzadas x impedimentos)")
loo = []
for out in F:
    sub = [s for s in F if s != out]
    loo.append(pearson([g[s]["cross"] for s in sub], [g[s]["imp"] for s in sub]))
print("   faixa:", f"{min(loo):+.2f} a {max(loo):+.2f}")
loo = []
for out in F:
    sub = [s for s in F if s != out]
    loo.append(pearson([g[s]["esc"] for s in sub], [g[s]["ret"] for s in sub]))
print("   escopo x retrabalho, faixa:", f"{min(loo):+.2f} a {max(loo):+.2f}")

# ---------------------------------------------------------------- gráfico
plt.rcParams.update({"font.family": ["Helvetica", "DejaVu Sans"], "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), facecolor="white")
a1.plot(S, [g[s]["imp"] for s in S], color="#dc2626", marker="o", lw=2, label="impedimentos")
a1.plot(S, [g[s]["cross"] for s in S], color="#2563eb", marker="o", lw=2, label="dependências entre pessoas")
a1.plot(S, [g[s]["esc"] for s in S], color="#ea580c", marker="o", lw=2, label="tarefas c/ mudança de escopo")
a1.plot(S, [g[s]["ret"] for s in S], color="#7c3aed", marker="o", lw=2, label="tarefas c/ retrabalho")
for s in S:
    if not g[s]["ata"]:
        a1.axvspan(s - 0.4, s + 0.4, color="#e5e7eb", zorder=0)
    elif g[s]["aus"]:
        a1.axvspan(s - 0.4, s + 0.4, color="#fee2e2", zorder=0)
a1.axvspan(9.5, 10.5, color="white", hatch="///", ec="#9ca3af", lw=0, zorder=0)
a1.set_xticks(S); a1.set_xlabel("sprint")
a1.set_title("Sinais de silo e problemas por sprint", loc="left", weight="bold")
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.text(0.01, -0.2, "cinza = sprint sem ata · rosa = reunião com 2 ausentes (Bruno e Carla) · hachurado = sprint 10 em andamento",
        transform=a1.transAxes, fontsize=8, color="#6b7280")

xs = [g[s]["n"] for s in F]; ys = [g[s]["imp"] for s in F]
a2.scatter(xs, ys, color="#dc2626", s=50, zorder=3)
for s in F:
    if s == 1:
        continue  # mesmo ponto da sprint 2
    a2.annotate("S1 e S2" if s == 2 else f"S{s}",(g[s]["n"], g[s]["imp"]), textcoords="offset points", xytext=(6, 2), fontsize=8.5)
a2.set_xlabel("nº de tarefas na sprint"); a2.set_ylabel("impedimentos")
a2.set_title("O fator escondido: tudo cresce junto com o tamanho da sprint", loc="left", weight="bold")
fig.tight_layout()
out = os.path.join(BASE, "analise_silos.png")
fig.savefig(out, dpi=160)
print("\ngráfico:", out)
