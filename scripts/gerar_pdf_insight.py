"""Gera Insight_Principal.pdf (insight em uma frase, 2 alternativas e comparação).

Uso: python scripts/gerar_pdf_insight.py   (requer reportlab)
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "Insight_Principal.pdf")

FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FD + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

INK, MUTED = colors.HexColor("#1f2328"), colors.HexColor("#6b7280")
ACCENT, LINE = colors.HexColor("#0f6b6b"), colors.HexColor("#d9dee3")
HEAD_BG, NOTE_BG = colors.HexColor("#eef4f4"), colors.HexColor("#f6f7f9")
GOOD_BG = colors.HexColor("#ecfdf3")

st = {
    "title": ParagraphStyle("t", fontName="Arial-Bold", fontSize=18, leading=22, textColor=INK, spaceAfter=2),
    "sub": ParagraphStyle("s", fontName="Arial", fontSize=10, leading=14, textColor=MUTED, spaceAfter=8),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=14, leading=18, textColor=ACCENT, spaceBefore=9, spaceAfter=5),
    "body": ParagraphStyle("b", fontName="Arial", fontSize=9, leading=12.5, textColor=INK, spaceAfter=5),
    "quote": ParagraphStyle("q", fontName="Arial-Bold", fontSize=12, leading=16, textColor=INK),
    "quote2": ParagraphStyle("q2", fontName="Arial", fontSize=10, leading=13.5, textColor=INK),
    "label": ParagraphStyle("l", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=ACCENT, spaceAfter=3),
    "cell": ParagraphStyle("c", fontName="Arial", fontSize=8.5, leading=11, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="Arial-Bold", fontSize=8.5, leading=11.5, textColor=INK),
    "small": ParagraphStyle("sm", fontName="Arial", fontSize=8.5, leading=12, textColor=MUTED),
}
P = lambda t, s="body": Paragraph(t, st[s])


def box(flows, bg=NOTE_BG, border=ACCENT, width=17):
    t = Table([[flows]], colWidths=[width * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def table(rows, widths, shade_col=None):
    data = [[Paragraph(str(c), st["cellb" if r == 0 or i == 0 else "cell"]) for i, c in enumerate(row)]
            for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths])
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if shade_col is not None:
        style.append(("BACKGROUND", (shade_col, 1), (shade_col, -1), GOOD_BG))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8); canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "MBA em IA e Dados para Negócios · Eletiva Project Management N2 · Insight principal")
    canvas.drawString(2 * cm, 0.8 * cm, "Fontes: dataset_limpo/ · scripts/analise_sobrecarga.py, "
                      "analise_silos.py e previsao_golive.py")
    canvas.restoreState()


s = [
    P("Insight principal", "title"),
    P("Projeto de migração de ERP para AWS · síntese das análises de sobrecarga, silos e previsão de go-live", "sub"),
    box([P("INSIGHT", "label"),
         P("O go-live atrasa cerca de 4 semanas (de 06/01 para 03/02) porque 78% do que trava a entrega está "
           "com as duas únicas pessoas acima de 100% de utilização, e o resto do time só tem 18 horas de folga "
           "por sprint para ajudar.", "quote")]),
    Spacer(1, 8),
    table([
        ["Número", "De onde vem"],
        ["+4 semanas (03/02/2025)", "Previsão realista: 186 SP em aberto ÷ 61 SP por sprint (média das sprints 7 a 9)."],
        ["78%", "25 das 32 dependências que ainda bloqueiam tarefas abertas são de Ana ou Diego; "
                "57 dos 73 SP do caminho até o go-live também."],
        ["Acima de 100%", "Ana: 115% a 130% desde a sprint 6. Diego: 100% a 110% desde a sprint 7. "
                          "Ninguém mais passa de 100%."],
        ["18 horas", "Folga real só do Bruno (22 pontos percentuais). Carla e Elena já têm a sprint 10 "
                     "planejada acima de 100%."],
    ], [4, 13]),

    P("Duas alternativas", "h1"),
    box([P("ALTERNATIVA 1 · ESCOPO", "label"),
         P("Tarefas que mudaram de escopo têm 45% mais impedimentos, e 11 das 27 mudanças caíram na Tech Lead, "
           "que já estava acima de 120%: o que trava o projeto é o escopo entrando fora do processo, "
           "não o isolamento entre pessoas.", "quote2")], border=MUTED),
    Spacer(1, 6),
    box([P("ALTERNATIVA 2 · TEMPO DE REAÇÃO", "label"),
         P("O time alertou a sobrecarga 77 dias antes da primeira decisão do PM; nesse intervalo os impedimentos "
           "dobraram e a Tech Lead passou de 100% para 128%.", "quote2")], border=MUTED),

    P("Qual é mais acionável", "h1"),
    table([
        ["Critério", "Principal", "Alt. 1 (escopo)", "Alt. 2 (reação)"],
        ["Diz o que fazer na próxima sprint",
         "<b>Sim:</b> tirar de Ana e Diego o que não é crítico, usar a folga do Bruno, cortar escopo fora do caminho crítico",
         "Sim: criar uma porta única de entrada de escopo", "Não: explica o passado"],
        ["Diz quem e quanto", "<b>Sim:</b> Ana e Diego, 78%, 18 horas de folga", "Em parte: Ana, 11 mudanças", "Não"],
        ["Impacto na data do go-live", "<b>Direto</b> (03/02)", "Indireto: evita novos atrasos", "Nenhum"],
        ["Está sob controle do PM", "Em parte: o corte de escopo depende do sponsor", "<b>Totalmente</b>", "—"],
    ], [3.8, 5.2, 4.3, 3.7], shade_col=1),
    Spacer(1, 8),
    P("<b>A principal é a mais acionável.</b> Ela entrega ao sponsor uma data, um gargalo com nome e um limite de "
      "capacidade. Disso saem as três decisões imediatas: realocar tarefas, cortar o que está fora do caminho crítico "
      "e confirmar 03/02. A alternativa 1 é a melhor segunda ação, porque ataca a causa e impede que o problema volte, "
      "mas não salva a data atual. A alternativa 2 é diagnóstico: serve como contexto (por que chegamos aqui) e para "
      "justificar uma regra de escalada, não como insight central."),
    P("<b>No relatório:</b> a principal entra como insight e a alternativa 1 justifica a segunda ação de mitigação; "
      "o barema de slides pede exatamente 2 ações, e cada uma sai de um dos dois insights."),
]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.4 * cm,
                        bottomMargin=1.7 * cm, title="Insight principal", author="Marcos Abdo")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
