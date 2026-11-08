"""Gera Relatorio_Final_PM_N2.pdf — relatório analítico do artefato (barema N2).

Estrutura pelos 4 movimentos do guia: pergunta, análise com IA, insight e decisão.
Usa as figuras geradas por analise_sobrecarga.py, analise_silos.py e previsao_golive.py.

Uso: python scripts/gerar_relatorio_final.py   (requer reportlab)
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "Relatorio_Final_PM_N2.pdf")
REPO = "github.com/Markabdo87/artefato2"

FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FD + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

INK, MUTED = colors.HexColor("#1f2328"), colors.HexColor("#6b7280")
ACCENT, LINE = colors.HexColor("#0f6b6b"), colors.HexColor("#d9dee3")
HEAD_BG, NOTE_BG = colors.HexColor("#eef4f4"), colors.HexColor("#f6f7f9")
WARN, WARN_BG = colors.HexColor("#b45309"), colors.HexColor("#fff7ed")
GOOD_BG = colors.HexColor("#ecfdf3")

st = {
    "kicker": ParagraphStyle("k", fontName="Arial-Bold", fontSize=9, leading=12, textColor=ACCENT, spaceAfter=4),
    "title": ParagraphStyle("t", fontName="Arial-Bold", fontSize=21, leading=26, textColor=INK, spaceAfter=6),
    "sub": ParagraphStyle("s", fontName="Arial", fontSize=10.5, leading=15, textColor=MUTED, spaceAfter=2),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=14.5, leading=18, textColor=ACCENT, spaceBefore=14, spaceAfter=7),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=9, spaceAfter=4),
    "body": ParagraphStyle("b", fontName="Arial", fontSize=9.6, leading=13.8, textColor=INK, spaceAfter=5),
    "bullet": ParagraphStyle("bl", fontName="Arial", fontSize=9.4, leading=13.2, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=3),
    "cell": ParagraphStyle("c", fontName="Arial", fontSize=8.5, leading=11.4, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="Arial-Bold", fontSize=8.5, leading=11.4, textColor=INK),
    "celli": ParagraphStyle("ci", fontName="Arial-Italic", fontSize=8.5, leading=11.4, textColor=INK),
    "key": ParagraphStyle("ky", fontName="Arial-Bold", fontSize=8.8, leading=12, textColor=ACCENT),
    "quote": ParagraphStyle("q", fontName="Arial-Bold", fontSize=12.5, leading=17, textColor=INK),
    "label": ParagraphStyle("l", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=ACCENT, spaceAfter=3),
    "labelw": ParagraphStyle("lw", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=WARN, spaceAfter=3),
    "cap": ParagraphStyle("cap", fontName="Arial", fontSize=8.5, leading=12, textColor=MUTED, spaceBefore=3, spaceAfter=8),
    "prompt": ParagraphStyle("p", fontName="Arial-Italic", fontSize=9, leading=12.5, textColor=INK),
}
P = lambda t, s="body": Paragraph(t, st[s])


def bullets(items, style="bullet"):
    return [Paragraph(i, st[style], bulletText="•") for i in items]


def box(flows, bg=NOTE_BG, border=ACCENT):
    t = Table([[flows]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def table(rows, widths, first_bold=True, shade_rows=(), shade_col=None):
    data = []
    for r, row in enumerate(rows):
        line = []
        for i, c in enumerate(row):
            if not isinstance(c, str):
                line.append(c); continue
            style = "cellb" if r == 0 or (first_bold and i == 0) else "cell"
            line.append(Paragraph(c, st[style]))
        data.append(line)
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for r in shade_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), GOOD_BG))
    if shade_col is not None:
        style.append(("BACKGROUND", (shade_col, 1), (shade_col, -1), GOOD_BG))
    t.setStyle(TableStyle(style))
    return t


def card(rows):
    data = [[P(k, "key"), v if not isinstance(v, str) else P(v, "cell")] for k, v in rows]
    t = Table(data, colWidths=[3 * cm, 14 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HEAD_BG), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, ACCENT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def figure(name, caption, width_cm=17):
    path = os.path.join(BASE, name)
    w, h = ImageReader(path).getSize()
    img = Image(path, width=width_cm * cm, height=width_cm * cm * h / w)
    return KeepTogether([img, P(caption, "cap")])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8); canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "MBA em IA e Dados para Negócios · Eletiva Project Management N2 · Marcos Abdo")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


s = []

# ============================================================== capa / resumo
s += [
    P("ARTEFATO DE ELETIVA · PROJECT MANAGEMENT · NÍVEL 2", "kicker"),
    P("Sobrecarga concentrada e escopo sem porta: por que o go-live vai atrasar e o que fazer na próxima sprint", "title"),
    P("Relatório analítico com uso de IA sobre os dados de um projeto de migração de ERP para AWS "
      "(10 sprints, set/2024 a jan/2025, time de 6 pessoas, 120 tarefas)", "sub"),
    P(f"Autor: Marcos Abdo · MBA em IA e Dados para Negócios · Evidências (dados, scripts e figuras): {REPO}", "sub"),
    Spacer(1, 10),
    box([P("RESUMO EXECUTIVO", "label"),
         *bullets([
             "<b>Pergunta:</b> a sobrecarga é do time ou de pessoas específicas no caminho crítico? E por que os alertas do "
             "time não viraram decisão a tempo?",
             "<b>Achado:</b> só Ana (Tech Lead) e Diego (Dados) passam de 100% de utilização, e 78% do que bloqueia o go-live "
             "depende deles. O resto do time tem apenas 18 h de folga real por sprint. O time alertou a sobrecarga 77 dias "
             "antes da primeira decisão do PM, e o escopo continuou entrando por fora do processo.",
             "<b>Insight:</b> o go-live atrasa cerca de 4 semanas (de 06/01 para 03/02) porque 78% do que trava a entrega está "
             "com as duas únicas pessoas acima de 100% de utilização, e o resto do time só tem 18 horas de folga por sprint "
             "para ajudar.",
             "<b>Decisão:</b> na sprint 11, (1) liberar o caminho crítico, tirando de Ana e Diego tudo o que não leva ao "
             "go-live e adiando de 24 a 32 SP, e (2) criar uma porta única de escopo com gatilho objetivo de escalada. "
             "Nova data: 03/02/2025, com ponto de revisão em 13/01.",
         ])]),
]

# ============================================================== 1. contexto
s += [
    P("1. Contexto e dados", "h1"),
    P("O mini-case descreve um projeto com cronograma atrasado, um líder que suspeita de sobrecarga sem ter dados para "
      "provar e riscos de comunicação (silos) maiores depois da mudança para o trabalho remoto. Foram usados quatro "
      "arquivos:"),
    table([
        ["Arquivo", "Conteúdo", "Uso na análise"],
        ["dataset_tarefas", "120 tarefas: responsável, story points, datas, status, dependências, impedimentos, escopo, "
                            "retrabalho, horas e custo", "Entregas, dependências, caminho crítico, previsão"],
        ["dataset_time", "6 pessoas: papel, senioridade e % de utilização por sprint", "Fonte da sobrecarga"],
        ["dataset_backlog", "10 sprints: itens, velocity, impedimentos", "Entrada de escopo e segunda fonte de velocidade"],
        ["dataset_atas", "Dailies e retrospectivas com resumo do que foi dito", "Sinais qualitativos e tempo de reação"],
    ], [3.2, 8.3, 5.5]),
    Spacer(1, 6),
    P("<b>Qualidade dos dados.</b> Antes da análise, os arquivos foram auditados (detalhes em "
      "Relatorio_Qualidade_Dados.pdf). Os pontos que mudam a leitura:"),
    *bullets([
        "A <b>velocity do backlog cai</b> (28 → 20) enquanto os <b>story points concluídos nas tarefas sobem</b> (32 → 91 até "
        "a sprint 8): as fontes apontam tendências opostas.",
        "A <b>utilização do time não bate com as horas das tarefas</b>: Ana teria 172 h na sprint 9, o equivalente a 17 h por "
        "dia útil.",
        "Faltam atas das sprints 3, 7 e 10; há tarefas abertas com data de fim e tarefas concluídas sem horas.",
    ]),
    P("A limpeza (dataset_limpo/, documentada em LIMPEZA.md) removeu colunas redundantes ou constantes, a ata vazia e datas "
      "de fim em tarefas abertas, sem preencher valores por estimativa. <b>Premissas principais:</b> sprint de 2 semanas, "
      "capacidade de 80 h por pessoa por sprint, dataset_tarefas como fonte de entregas e dataset_time como fonte de "
      "carga, sprint 10 tratada como em andamento."),
]

# ============================================================== 2. perguntas
s += [
    P("2. Perguntas", "h1"),
    P("As perguntas foram escritas antes de abrir os dados, cada uma com uma hipótese que pode ser refutada e ligada a "
      "uma decisão concreta do PM."),
    table([
        ["#", "Pergunta", "Hipótese (não trivial)", "Decisão que ela informa"],
        ["P1", "A sobrecarga está espalhada pelo time ou concentrada nas pessoas de quem o go-live depende? Quanto da "
               "folga do resto do time poderia aliviar esse gargalo?",
         "A sobrecarga não é do time: é de 2 pessoas que estão no caminho crítico.",
         "Redistribuir trabalho ou cortar escopo; quanto e de quem."],
        ["P2", "Quanto tempo passou entre o primeiro sinal de risco nas atas e a reação do PM? Escopo vindo de fora do "
               "processo e reuniões incompletas (silos) explicam o aumento de impedimentos e retrabalho?",
         "O problema não foi falta de alerta, e sim falta de mecanismo que transformasse alerta em decisão.",
         "Que regra de governança impede que isso se repita."],
        ["P3", "Com o trabalho que falta (186 SP abertos) e o ritmo recente, quando o go-live acontece de verdade?",
         "Nenhuma das opções levadas ao sponsor se sustenta sem corte de escopo.",
         "Qual data e qual opção recomendar ao sponsor."],
    ], [0.8, 6.2, 5, 5]),
    Spacer(1, 4),
    P("<b>Por que não são triviais:</b> \"o time está sobrecarregado?\" teria resposta óbvia (sim, a média chega a 98%). "
      "A pergunta útil é <i>quem</i> está acima da capacidade e se essas pessoas são as que travam a entrega, porque "
      "isso muda a decisão: redistribuir resolve um problema espalhado, mas não um gargalo concentrado."),
]

# ============================================================== 3. análise com IA
s += [
    P("3. Análise com IA: rastro de prompts, ajustes e descobertas", "h1"),
    P("Ferramenta: <b>Claude (Anthropic), via Claude Code</b>, com execução de código Python sobre os CSVs. Cada análise "
      "virou um script reprodutível, publicado no repositório junto com as figuras. A tabela abaixo resume os prompts, o "
      "que a IA devolveu e onde o resultado foi questionado ou corrigido."),
    table([
        ["#", "Prompt (resumo)", "O que a IA encontrou", "O que questionei / ajustei"],
        ["1", "Descreva os 4 CSVs e liste problemas de qualidade e números que não batem entre arquivos. Liste as premissas.",
         "Velocity do backlog e SP das tarefas com tendências opostas; utilização ≠ horas; atas faltando; 6 tarefas "
         "abertas com data de fim.",
         "Escolhi uma <b>fonte única por métrica</b> (tarefas para entregas, time para carga) e limpei os dados sem "
         "inventar valores."],
        ["2", "Hipótese: a sobrecarga é de 2 pessoas no caminho crítico. Heatmap pessoa × sprint e dependências abertas "
              "por pessoa.",
         "Só Ana e Diego passam de 100%. 25 de 32 dependências abertas (78%) e 57 de 73 SP do caminho até o go-live "
         "estão com eles. Folga calculada: 62 h.",
         "A primeira resposta tratou a hipótese como confirmada sem checar a fonte nem a sprint em andamento."],
        ["3", "Revise: a utilização bate com as horas? Felipe sem tarefas é carga real? A sprint 10 distorce algo?",
         "Fontes concordam na ordem (r = 0,87; mesmas 2 pessoas no topo) mas não no nível (17 h/dia é implausível). "
         "Felipe não é verificável.",
         "<b>Folga caiu de 62 h para 18 h</b>: a Elena parecia livre (70%), mas tem 84 h \"To Do\" presas atrás de Ana e "
         "Diego. Ela vira o próximo gargalo."],
        ["4", "Cruze, sprint a sprint, números e atas: sinal, quem falou, o PM reagiu? Quanto tempo até a reação?",
         "Primeiro alerta na sprint 4 (07/10), pedido explícito na sprint 6 (08/11), primeira decisão na sprint 9 (23/12).",
         "Defini o critério de \"reação concreta\" (ação + dono + prazo) e marquei que \"não reagiu\" = \"sem registro\"."],
        ["5", "Analise sinais de silo e sua correlação com impedimentos e retrabalho. Com 10 sprints, é confiável?",
         "Correlações por sprint muito altas: dependências entre pessoas × impedimentos r = 0,97; escopo r = 0,91.",
         "<b>Derrubei o resultado:</b> o tamanho da sprint explica r = 0,96 sozinho. No teste tarefa a tarefa, só "
         "<b>escopo → impedimentos</b> sobrevive (2,05 vs. 1,41 por tarefa, p = 0,015)."],
        ["6", "Projete o go-live com as duas fontes, 3 cenários e drift; compare com as opções levadas ao sponsor.",
         "Realista 03/02 (+4 semanas); faixa de 28/01 a 29/03. Backlog: 08/03 com escopo congelado, quase 1 ano sem "
         "congelar.",
         "Recusei dividir SP por velocity do backlog (unidades diferentes) e testei se o caminho crítico cabe em cada "
         "opção."],
        ["7", "Resuma em um insight de uma frase, com 2 alternativas, e diga qual é mais acionável.",
         "Três versões: gargalo, escopo, tempo de reação.",
         "Escolhi a que dá data, nome e limite de capacidade; as outras viraram justificativa da 2ª ação e contexto."],
        ["8", "Proponha 2 ações com o quê, quem, prazo, métrica, trade-off e risco; depois critique-as.",
         "Duas ações para a sprint 11 e sete críticas.",
         "Corrigi a premissa do pedido: só o Bruno tem folga; a da Carla precisa ser criada e a Elena protegida."],
    ], [0.6, 4.5, 6, 5.9]),
    Spacer(1, 6),
    box([P("ONDE A IA ERROU E COMO FOI CORRIGIDA", "labelw"),
         *bullets([
             "<b>Correlação espúria:</b> r = 0,97 parecia provar que silos causam impedimentos. Controlando o tamanho da "
             "sprint e testando tarefa a tarefa, a relação desaparece para dependências e ausências.",
             "<b>Folga superestimada:</b> a utilização parcial da sprint 10 escondia 84 h de trabalho da Elena. Corrigida "
             "usando o maior valor entre a utilização da sprint 9 e as horas planejadas da sprint 10.",
             "<b>Unidades misturadas:</b> aplicar a velocity do backlog aos story points das tarefas daria 20/04/2025, uma "
             "data sem sentido. A previsão do backlog foi refeita na unidade dele (itens).",
         ])], bg=WARN_BG, border=WARN),
]

# ============================================================== 4. resultados
s += [
    P("4. Resultados", "h1"),
    P("P1 · A sobrecarga é de duas pessoas, e elas estão no caminho crítico", "h2"),
    figure("analise_sobrecarga.png", "Figura 1 · Utilização por pessoa e sprint (dataset_time). Só Ana e Diego passam de "
                                     "100%. Sprint 10 em andamento (hachurada); Felipe sem tarefas para conferir a carga."),
    table([
        ["Pessoa", "Utilização média S6–9", "Dependências abertas que esperam por ela", "SP no caminho até o go-live"],
        ["Ana (Tech Lead)", "123%", "14", "31"],
        ["Diego (Dados)", "103%", "11", "26"],
        ["Elena (QA)", "90%", "5", "16"],
        ["Carla / Bruno", "82% / 77%", "2 / 0", "0 / 3 (o próprio go-live)"],
    ], [3.6, 3.8, 5.6, 4], shade_rows=(1, 2)),
    Spacer(1, 4),
    P("<b>Leitura:</b> a hipótese se confirma, com duas ressalvas. A média do time também subiu (63% → 98% na sprint 8), "
      "então há pouca folga para redistribuir: só o Bruno tem cerca de 18 h. E a Elena é o próximo gargalo, com 84 h de "
      "testes que só começam quando Ana e Diego terminarem."),

    P("P2 · O time alertou cedo; faltou mecanismo para decidir", "h2"),
    table([
        ["Risco", "Primeiro alerta na ata", "Reação concreta", "Tempo"],
        ["Sobrecarga (Ana e Diego)", "Sprint 4 (07/10); pedido explícito de ajuda na sprint 6 (08/11)",
         "Sprint 9 (23/12): escopo congelado e 3 cenários ao sponsor", "<b>77 dias</b> (45 desde o pedido explícito)"],
        ["Escopo", "Sprint 2 (layout indefinido); sprint 6 (4 pedidos)", "Sprint 9: congelamento, que não aparece na "
                                                                         "sprint 10 (5 tarefas com mudança)", "101 dias"],
        ["Qualidade e retrabalho", "Sprint 4 (duplicação, performance)", "Nenhuma registrada", "—"],
        ["Silos (ausências)", "Sprint 5 (daily com 4 de 6)", "Nenhuma; repete na sprint 8", "—"],
    ], [3.5, 5, 5.3, 3.2]),
    Spacer(1, 4),
    P("Enquanto o PM não reagia (sprints 6 a 9), os impedimentos dobraram (14 → 29) e a utilização da Ana subiu de 115% "
      "para 128%. A primeira reação (sprint 5) pediu que Ana e Diego \"priorizassem os bloqueios\", concentrando ainda "
      "mais trabalho em quem já estava no limite. A hipótese mais forte para a demora: o esforço extra manteve as entregas "
      "subindo (49 → 91 SP entre as sprints 5 e 8), então o indicador que o PM via mostrava sucesso."),
    figure("analise_silos.png", "Figura 2 · Sinais de silo e problemas por sprint (esquerda) e o fator escondido: "
                                "impedimentos crescem junto com o tamanho da sprint (direita)."),
    P("<b>Silos:</b> por sprint, as correlações parecem fortíssimas, mas somem quando se controla o tamanho da sprint. "
      "Tarefa a tarefa, nas sprints 6 a 9, só uma relação se sustenta: <b>tarefas com mudança de escopo têm 45% mais "
      "impedimentos</b> (p = 0,015). Depender de outra pessoa não gera mais impedimentos do que depender de si mesma "
      "(p = 0,23), e o retrabalho não se liga a nenhum sinal de silo. Das 27 mudanças de escopo, 11 caíram na Ana."),

    KeepTogether([
        P("P3 · O go-live vai para 03/02, e manter 06/01 é inviável", "h2"),
        figure("previsao_golive.png", "Figura 3 · Queima dos 186 SP em aberto a partir de 23/12 em três cenários "
                                      "(tarefas) e na unidade do backlog (itens, com escopo congelado)."),
    ]),
    table([
        ["Cenário", "Velocidade", "Go-live", "Drift"],
        ["Otimista (média S6–8)", "72 SP/sprint", "28/01/2025", "+22 dias"],
        ["<b>Realista (média S7–9)</b>", "61 SP/sprint", "<b>03/02/2025</b>", "<b>+28 dias (~4 semanas)</b>"],
        ["Pessimista (sprint 9)", "27 SP/sprint", "29/03/2025", "+82 dias"],
        ["Backlog, escopo congelado", "6 itens/sprint", "08/03/2025", "+61 dias"],
    ], [5, 3.5, 4, 4.5], shade_rows=(2,)),
    Spacer(1, 4),
    P("<b>Por que as fontes divergem:</b> o backlog mede avanço sobre o escopo planejado; as tarefas medem todo o trabalho "
      "feito, incluindo bugs, débito técnico e pedidos que entraram no meio da sprint. O time trabalhou mais, mas avançou "
      "menos no que foi combinado. Só o backlog mostra que, com 5 itens entrando por sprint para 6 saindo, nenhuma data "
      "se sustenta sem congelar o escopo. Alerta adicional: as tarefas abertas já consumiram 82% das horas estimadas sem "
      "entregar nenhum story point."),
    table([
        ["Opção levada ao sponsor", "Capacidade (61 SP/sprint)", "É preciso cortar", "Caminho crítico (76 SP) cabe?"],
        ["Manter 06/01 e cortar escopo", "61 SP", "125 SP (67%)", "<b>Não</b>"],
        ["+2 semanas (20/01)", "123 SP", "63 SP (34%)", "Sim"],
        ["+4 semanas (03/02)", "184 SP", "2 SP (1%), sem folga", "Sim"],
    ], [5, 4, 4, 4]),
]

# ============================================================== 5. insight
s += [
    P("5. Insight", "h1"),
    box([P("INSIGHT", "label"),
         P("O go-live atrasa cerca de 4 semanas (de 06/01 para 03/02) porque 78% do que trava a entrega está com as duas "
           "únicas pessoas acima de 100% de utilização, e o resto do time só tem 18 horas de folga por sprint para ajudar.",
           "quote")]),
    Spacer(1, 4),
    P("Foram consideradas duas alternativas: uma centrada no escopo (\"tarefas que mudaram de escopo têm 45% mais "
      "impedimentos, e 11 das 27 mudanças caíram na Tech Lead\") e outra no tempo de reação (\"o time alertou a sobrecarga "
      "77 dias antes da primeira decisão do PM\"). A escolhida é a mais acionável porque dá ao sponsor uma data, um "
      "gargalo com nome e um limite de capacidade. A alternativa de escopo justifica a segunda ação; a de tempo de reação "
      "é o contexto de por que o projeto chegou aqui."),
]

# ============================================================== 6. decisão
s += [
    P("6. Decisão do PM para a sprint 11", "h1"),
    P("<b>Ajuste no ponto de partida:</b> dos três candidatos a ajudar, só o Bruno tem folga real (cerca de 18 h). A sprint "
      "10 da Carla já está planejada em 105% e a da Elena em 130%. A folga da Carla precisa ser criada, adiando tarefas de "
      "prioridade média; a Elena precisa ser protegida."),
    P("Ação 1 · Liberar o caminho crítico", "h2"),
    card([
        ("O quê", [*bullets([
            "<b>Ana</b> fica só com o caminho crítico (TASK-065, 073, 078) e a 119. A <b>TASK-114</b> passa para o "
            "<b>Bruno</b>, que já está no módulo de aprovações. As <b>TASK-071 e 099</b> (16 SP) ficam para depois do go-live.",
            "<b>Diego</b> fica com 066, 074, 077 e 117. A <b>TASK-103</b> (parametrizações fiscais, 8 SP) vai para o sponsor "
            "decidir se é exigência fiscal no go-live.",
            "<b>Carla</b> adia a 116 e a 105 (prioridade média) e usa as cerca de 12 h liberadas para executar roteiros de "
            "UAT com a Elena.",
            "<b>Elena</b> começa o UAT em partes, testando 065 e 066 assim que cada uma ficar pronta.",
        ])]),
        ("Quem", "Felipe decide no planejamento com a Ana; Bruno assume a 114; Carla apoia o UAT; o sponsor decide a 103."),
        ("Prazo", "07/01 (início da sprint 11), com revisão em 13/01."),
        ("Métrica", "Ana e Diego ≤ 100% na sprint 11 (hoje 125% e 105%); 065, 066, 073 e 074 concluídas até o fim da sprint; "
                    "UAT fase 2 iniciado até 13/01."),
        ("Trade-off", "24 a 32 SP ficam para depois do go-live; o financeiro faz reconciliação manual nas primeiras semanas."),
        ("Risco", "Custo de passagem de contexto; risco fiscal se a 103 for adiada; resistência da Ana a largar tarefas."),
    ]),
    P("Ação 2 · Porta única de escopo com gatilho de escalada", "h2"),
    card([
        ("O quê", [*bullets([
            "Todo pedido de mudança passa pelo Felipe por um único canal e entra no backlog com impacto estimado; nada "
            "entra na sprint sem trocar por algo de mesmo tamanho. Triagem semanal com o sponsor.",
            "Gatilho objetivo: utilização acima de 100% ou tarefa do caminho crítico atrasada mais de 2 dias leva a escalada "
            "ao sponsor em até 48 h.",
            "Toda ata registra ação, dono e prazo.",
        ])]),
        ("Quem", "Felipe é o dono; o sponsor aprova e comunica a regra à diretoria; Carla redireciona os pedidos que receber."),
        ("Prazo", "Regra comunicada até 08/01; primeira triagem em 10/01, conduzida pelo sponsor."),
        ("Métrica", "0 mudanças de escopo não aprovadas na sprint 11 (hoje 5 por sprint); itens adicionados ao backlog ≤ 1 "
                    "por sprint (hoje 5); queda dos impedimentos."),
        ("Trade-off", "A diretoria perde agilidade; pedidos urgentes esperam a triagem; o Felipe ganha trabalho de gestão."),
        ("Risco", "A regra ser contornada, como o congelamento da sprint 9, que não apareceu nos dados da sprint 10."),
    ]),
    P("Impacto, próximos passos e riscos da decisão", "h2"),
    *bullets([
        "<b>Impacto esperado:</b> o go-live sai de \"sem data\" para 03/02/2025, com o caminho crítico protegido e o escopo "
        "sob controle. A recomendação ao sponsor é a opção \"+4 semanas\", combinada com corte fora do caminho crítico "
        "para criar de 15% a 20% de folga.",
        "<b>Ponto de revisão (13/01):</b> se 065 e 066 não estiverem concluídas, levar ao sponsor o cenário de março; se a "
        "sprint 11 entregar menos de 50 SP, a data passa para março.",
        "<b>Limites da decisão:</b> as tarefas do caminho crítico já estouraram as estimativas (065: 74 h de 52), então "
        "03/02 não tem margem. A ação 2 depende do apoio explícito do sponsor. A Elena continua sendo o próximo gargalo.",
        "<b>Lacuna assumida:</b> nenhuma das ações ataca o retrabalho (31% na sprint 9), que não se liga a escopo nem a "
        "silos. O próximo passo é um critério de pronto mais rígido e revisão de código antes do QA.",
    ]),
]

# ============================================================== 7. limitações
s += [
    P("7. Limitações", "h1"),
    *bullets([
        "A utilização do dataset_time é declarada, não medida; foi escolhida como fonte de carga porque bate com as atas "
        "(Ana: \"50+ horas por semana\") e com a ordem das horas das tarefas.",
        "Com 9 sprints fechadas, correlações por sprint não são confiáveis; as conclusões sobre silos se apoiam no teste "
        "tarefa a tarefa.",
        "As atas são uma amostra: \"o PM não reagiu\" significa \"não há registro de reação\".",
        "A previsão assume velocidade estável e não modela a sequência do caminho crítico (Ana → Elena → Ana → go-live), que "
        "pode atrasar mesmo com capacidade sobrando.",
    ]),
    Spacer(1, 6),
    P(f"<b>Evidências:</b> todos os dados, scripts e figuras estão em {REPO}: dataset_artefato/ (bruto), dataset_limpo/ "
      "(limpo, com LIMPEZA.md), scripts/ (limpeza, sobrecarga, silos, previsão e geração dos PDFs) e os PDFs de apoio "
      "(Relatorio_Qualidade_Dados, Insight_Principal, Acoes_Proxima_Sprint).", "cap"),
]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.7 * cm,
                        bottomMargin=1.9 * cm, title="Relatório analítico · Project Management N2", author="Marcos Abdo")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
