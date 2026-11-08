"""Gera Relatorio_Qualidade_Dados.pdf (diagnóstico dos 4 CSVs brutos).

Uso: python scripts/gerar_relatorio_qualidade.py   (requer reportlab)
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "Relatorio_Qualidade_Dados.pdf")

FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FD + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

INK = colors.HexColor("#1f2328")
MUTED = colors.HexColor("#6b7280")
ACCENT = colors.HexColor("#0f6b6b")
RED = colors.HexColor("#b91c1c")
LINE = colors.HexColor("#d9dee3")
HEAD_BG = colors.HexColor("#eef4f4")
NOTE_BG = colors.HexColor("#f6f7f9")

st = {
    "title": ParagraphStyle("title", fontName="Arial-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=4),
    "sub": ParagraphStyle("sub", fontName="Arial", fontSize=10, leading=14, textColor=MUTED, spaceAfter=14),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=14, leading=18, textColor=ACCENT, spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Arial", fontSize=9.5, leading=13.5, textColor=INK, spaceAfter=5, alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="Arial", fontSize=9.5, leading=13.5, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=3),
    "cell": ParagraphStyle("cell", fontName="Arial", fontSize=8.5, leading=11, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=INK),
    "note": ParagraphStyle("note", fontName="Arial", fontSize=9, leading=12.5, textColor=INK),
    "prompt": ParagraphStyle("prompt", fontName="Arial-Italic", fontSize=9, leading=12.5, textColor=INK),
}


def P(t, s="body"):
    return Paragraph(t, st[s])


def bullets(items):
    return [Paragraph(i, st["bullet"], bulletText="•") for i in items]


def table(rows, widths, num_cols=(), highlight_rows=()):
    data = [[Paragraph(str(c), st["cellb" if r == 0 else "cell"]) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for c in num_cols:
        style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    for r in highlight_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fdf2f2")))
    t.setStyle(TableStyle(style))
    return t


def box(flow, bg=NOTE_BG, border=ACCENT):
    t = Table([[flow]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def sprint_table(header, rows, highlight=()):
    data = [["Sprint"] + [str(i) for i in range(1, 11)]] + [[label] + vals for label, vals in rows]
    t = Table([[Paragraph(str(c), st["cellb" if (r == 0 or c_i == 0) else "cell"]) for c_i, c in enumerate(row)]
               for r, row in enumerate(data)],
              colWidths=[5 * cm] + [1.2 * cm] * 10)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for c in highlight:
        style.append(("BACKGROUND", (c, 1), (c, -1), colors.HexColor("#fdf2f2")))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "MBA em IA e Dados para Negócios · Eletiva Project Management N2 · Diagnóstico de qualidade dos dados")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


s = []
s.append(P("Diagnóstico de qualidade dos dados", "title"))
s.append(P("Projeto de migração de ERP para AWS · sprints 1 a 10 (set/2024 a jan/2025) · "
           "fonte: dataset_artefato/ (dados brutos)", "sub"))

s.append(box(P("<b>Por que este relatório existe.</b> Antes de responder às perguntas de sobrecarga e silos, "
               "os quatro arquivos foram auditados para saber em quais números é possível confiar. "
               "O resultado orienta as premissas da análise e a limpeza registrada em dataset_limpo/LIMPEZA.md.", "note")))
s.append(Spacer(1, 8))
s.append(box(P("<b>Prompt usado na ferramenta de IA:</b> \"Anexei 4 CSVs de um projeto (tarefas, time, backlog, atas). "
               "Descreva cada arquivo e liste problemas de qualidade: valores faltantes, linhas vazias, sprints sem ata, "
               "e números que não batem entre arquivos (ex.: velocity do backlog vs. story points concluídos nas tarefas). "
               "Liste as premissas que você precisa assumir.\"", "prompt"), border=MUTED))

# 1
s.append(P("1. Os quatro arquivos", "h1"))
s.append(table([
    ["Arquivo", "Linhas", "Colunas", "O que registra"],
    ["dataset_tarefas.csv", "120 tarefas", "21", "Uma linha por tarefa: tipo, responsável, story points, datas previstas e reais, status, "
     "dependências, impedimentos, mudança de escopo, retrabalho, horas e custo."],
    ["dataset_time.csv", "6 pessoas", "16", "Papel, senioridade, especialidade, capacidade semanal, % de utilização por sprint e custo/hora."],
    ["dataset_backlog.csv", "10 sprints", "10", "Resumo por sprint: itens no início, adicionados, concluídos e no fim; velocity; "
     "impedimentos; tarefas com mudança de escopo e com retrabalho."],
    ["dataset_atas.csv", "8 reuniões", "5", "Dailies e retrospectivas: sprint, tipo, data, participantes e resumo em texto."],
], [3.6, 2.1, 1.6, 9.7]))
s.append(Spacer(1, 6))
s.append(table([
    ["Pessoa", "Papel", "Pessoa", "Papel"],
    ["Ana", "Tech Lead", "Diego", "Analista de Dados"],
    ["Bruno", "Dev Backend", "Elena", "QA"],
    ["Carla", "Dev Frontend", "Felipe", "PM / Scrum Master"],
], [3, 5.5, 3, 5.5]))
s.append(Spacer(1, 4))
s.append(P("Situação das tarefas: <b>93 concluídas</b>, 21 em andamento e 6 a fazer."))

# 2
s.append(P("2. Problemas de qualidade", "h1"))
s.append(P("2.1 Valores faltantes", "h2"))
s.append(table([
    ["Arquivo", "Campo", "Linhas afetadas", "Avaliação"],
    ["tarefas", "horas_gastas e custo_real", "4 tarefas concluídas (TASK-031, 055, 085, 092)", "<b>Problema.</b> Tarefa concluída deveria ter horas; fica fora das somas de horas e custo."],
    ["tarefas", "impedimentos", "3 tarefas concluídas (TASK-023, 038, 082)", "<b>Problema.</b> Não se sabe se é zero ou falta de registro."],
    ["tarefas", "data_inicio_real", "8: as 6 \"To Do\" e 2 \"Done\" (TASK-040, 081)", "Esperado nas \"To Do\"; <b>problema</b> nas 2 concluídas."],
    ["tarefas", "data_fim_real", "21", "Esperado: tarefas não concluídas."],
    ["tarefas", "dependencias", "36", "Esperado: tarefas sem dependência."],
], [1.8, 3.2, 5.2, 6.8], highlight_rows=(1, 2)))

s.append(P("2.2 Valores incoerentes dentro do mesmo arquivo", "h2"))
s.extend(bullets([
    "<b>Datas de fim em tarefas abertas:</b> 6 tarefas \"In Progress\" têm data_fim_real preenchida "
    "(TASK-065, 066, 067, 071, 113, 114).",
    "<b>Dependência fora de ordem:</b> TASK-113 (sprint 9) depende de TASK-074, que é da sprint 10.",
    "<b>Saldo do backlog quebrado entre sprints:</b> dentro de cada sprint a conta fecha "
    "(início + adicionados - concluídos = fim), mas o fim de uma sprint não bate com o início da seguinte "
    "(sprint 1 termina com 6 itens e a 2 começa com 14; a 8 termina com 19 e a 9 começa com 24).",
]))

s.append(P("2.3 Linhas vazias, colunas sem valor e redundantes", "h2"))
s.extend(bullets([
    "<b>Ata da sprint 3</b> (Retrospectiva, 27/09/2024): sem participantes nem resumo, e com 6 campos em vez de 5.",
    "<b>Atas fora de ordem:</b> a sprint 5 aparece antes da 4.",
    "<b>Coluna constante:</b> horas_semana_disponiveis vale 40 para todos.",
    "<b>Coluna redundante:</b> custo_hora_responsavel repete o custo_hora do time em 100% das linhas.",
]))

s.append(KeepTogether([
    P("2.4 Sprints sem ata e ausências", "h2"),
    table([
        ["Sprint", "Situação das atas"],
        ["3", "Linha existe, mas está vazia."],
        ["7 e 10", "Sem ata."],
        ["1, 4, 5 e 8", "Só daily, sem retrospectiva."],
        ["2, 6 e 9", "Só retrospectiva, sem daily."],
    ], [3, 14], highlight_rows=(1, 2)),
    Spacer(1, 4),
    P("Ausências registradas: <b>Bruno e Carla</b> faltaram às dailies das sprints 5 e 8 (só 4 de 6 participantes)."),
]))

s.append(P("2.5 Números que não batem entre arquivos", "h2"))
s.append(P("<b>a) Velocity (backlog) × story points concluídos (tarefas)</b> — os arquivos apontam tendências opostas."))
s.append(sprint_table(None, [
    ("Velocity no backlog", ["28", "30", "32", "29", "27", "26", "24", "22", "20", "12"]),
    ("SP concluídos nas tarefas", ["32", "34", "48", "46", "49", "59", "66", "91", "27", "0"]),
], highlight=(8, 10)))
s.append(Spacer(1, 3))
s.append(P("O backlog diz que a entrega cai; as tarefas dizem que sobe até a sprint 8. "
           "A sprint 10 tem velocity 12 no backlog, mas nenhuma tarefa concluída."))

s.append(P("<b>b) Impedimentos</b> — possivelmente medem coisas diferentes (impedimentos únicos × ocorrências por tarefa), "
           "mas os arquivos não dizem."))
s.append(sprint_table(None, [
    ("Abertos (backlog)", ["1", "2", "3", "3", "5", "8", "10", "13", "14", "12"]),
    ("Soma por tarefa (tarefas)", ["1", "1", "4", "3", "8", "14", "18", "28", "29", "23"]),
]))
s.append(Spacer(1, 8))

s.append(KeepTogether([
    P("<b>c) Mudança de escopo e retrabalho</b> (sprints com divergência)"),
    table([
        ["Sprint", "Escopo (backlog)", "Escopo (tarefas)", "Retrabalho (backlog)", "Retrabalho (tarefas)"],
        ["3", "1", "0", "1", "1"],
        ["6", "4", "5", "2", "4"],
        ["8", "5", "5", "4", "6"],
        ["9", "4", "5", "3", "5"],
        ["10", "4", "5", "2", "1"],
    ], [2, 3.75, 3.75, 3.75, 3.75], num_cols=(1, 2, 3, 4)),
]))
s.append(Spacer(1, 6))
s.extend(bullets([
    "<b>d) Itens × tarefas:</b> o backlog registra 8 itens concluídos por sprint até a sprint 8, enquanto as tarefas "
    "concluídas variam de 8 a 14. O backlog começa com 14 itens e a sprint 1 tem 8 tarefas: não fica claro se "
    "\"item\" é o mesmo que \"tarefa\".",
    "<b>e) Utilização (time) × horas gastas (tarefas):</b> na sprint 9, Ana aparece com 128% de utilização, mas tem "
    "172 h gastas nas tarefas, o que daria 215% de uma capacidade de 80 h por sprint. Diego: 110% contra 170 h na sprint 8.",
    "<b>f) Atas × dados:</b> na retrospectiva da sprint 9, Elena diz que \"40% das tarefas\" voltaram por retrabalho; "
    "as tarefas mostram 31% (5 de 16).",
]))

# 3
s.append(P("3. Premissas adotadas", "h1"))
s.append(table([
    ["#", "Premissa", "Justificativa"],
    ["1", "Sprint de 2 semanas.", "As atas têm cerca de 14 dias de intervalo. As tarefas das sprints 1 e 2 cabem em 1 semana cada, então é preciso confirmar."],
    ["2", "Capacidade de 40 h/semana (80 h/sprint) por pessoa.", "Vem de horas_semana_disponiveis."],
    ["3", "Fonte única para entregas, escopo e retrabalho: dataset_tarefas.", "É o mais detalhado e auditável linha a linha. O backlog fica só para a evolução de itens e impedimentos abertos."],
    ["4", "Fonte para sobrecarga: dataset_time.", "A utilização é coerente com as atas (Ana: \"50+ horas por semana\", cerca de 125%). As horas das tarefas provavelmente incluem trabalho que atravessa sprints."],
    ["5", "Campo em branco = desconhecido, não zero.", "Nenhum valor foi preenchido por estimativa."],
    ["6", "Tarefa \"In Progress\" não está concluída, mesmo com data de fim.", "A data de fim é ignorada."],
    ["7", "A sprint 10 está em andamento.", "Entra na previsão, mas não nas médias de desempenho."],
    ["8", "As atas são uma amostra, não um registro completo.", "Ausência em reunião sinaliza silo, mas não prova ausência na sprint inteira."],
    ["9", "Custo = horas × custo/hora, sem encargos ou indiretos.", "A conta foi confirmada em 100% das linhas."],
], [0.7, 6.3, 10]))

# 4
s.append(KeepTogether([
    P("4. O que isso muda na análise", "h1"),
    *bullets([
        "A divergência de velocity é o achado mais importante: dependendo da fonte, o projeto parece acelerar ou desacelerar. "
        "Toda conclusão sobre ritmo de entrega precisa dizer qual fonte usou e por quê.",
        "Sobrecarga será medida pela utilização do dataset_time, confirmada pelo que as atas relatam, e não pelas horas somadas das tarefas.",
        "As limpezas aplicadas (colunas redundantes e constantes, ata vazia, datas de fim em tarefas abertas) estão em "
        "dataset_limpo/ e documentadas em dataset_limpo/LIMPEZA.md, geradas por scripts/limpar_dados.py.",
    ]),
]))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Diagnóstico de qualidade dos dados", author="Marcos Abdo")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
