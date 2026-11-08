"""Gera Acoes_Proxima_Sprint.pdf (2 ações de PM para a sprint 11 e autocrítica).

Uso: python scripts/gerar_pdf_acoes.py   (requer reportlab)
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "Acoes_Proxima_Sprint.pdf")

FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FD + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

INK, MUTED = colors.HexColor("#1f2328"), colors.HexColor("#6b7280")
ACCENT, LINE = colors.HexColor("#0f6b6b"), colors.HexColor("#d9dee3")
HEAD_BG, NOTE_BG = colors.HexColor("#eef4f4"), colors.HexColor("#f6f7f9")
WARN, WARN_BG = colors.HexColor("#b45309"), colors.HexColor("#fff7ed")

st = {
    "title": ParagraphStyle("t", fontName="Arial-Bold", fontSize=19, leading=23, textColor=INK, spaceAfter=3),
    "sub": ParagraphStyle("s", fontName="Arial", fontSize=10, leading=14, textColor=MUTED, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=13.5, leading=17, textColor=ACCENT, spaceBefore=12, spaceAfter=6),
    "body": ParagraphStyle("b", fontName="Arial", fontSize=9.3, leading=13, textColor=INK, spaceAfter=4),
    "bullet": ParagraphStyle("bl", fontName="Arial", fontSize=9, leading=12.5, textColor=INK, leftIndent=11, bulletIndent=1, spaceAfter=2),
    "cell": ParagraphStyle("c", fontName="Arial", fontSize=8.8, leading=12, textColor=INK),
    "key": ParagraphStyle("k", fontName="Arial-Bold", fontSize=8.8, leading=12, textColor=ACCENT),
    "cellb": ParagraphStyle("cb", fontName="Arial-Bold", fontSize=8.8, leading=12, textColor=INK),
    "label": ParagraphStyle("l", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=WARN, spaceAfter=2),
}
P = lambda t, s="body": Paragraph(t, st[s])


def bullets(items, style="bullet"):
    return [Paragraph(i, st[style], bulletText="•") for i in items]


def card(rows):
    data = [[P(k, "key"), v if not isinstance(v, str) else P(v, "cell")] for k, v in rows]
    t = Table(data, colWidths=[3.2 * cm, 13.8 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HEAD_BG), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, ACCENT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def box(flows, bg=NOTE_BG, border=ACCENT):
    t = Table([[flows]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8); canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, "MBA em IA e Dados para Negócios · Eletiva Project Management N2 · Ações para a sprint 11")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


s = [
    P("Ações para a próxima sprint", "title"),
    P("Projeto de migração de ERP para AWS · decisão de PM para a sprint 11 (a partir de 07/01/2025)", "sub"),
    box([P("<b>Insight que orienta a decisão:</b> o go-live atrasa cerca de 4 semanas (de 06/01 para 03/02) porque 78% "
           "do que trava a entrega está com as duas únicas pessoas acima de 100% de utilização (Ana e Diego), e o resto "
           "do time só tem 18 horas de folga por sprint para ajudar.")]),
    Spacer(1, 6),
    box([P("UM AJUSTE NO PONTO DE PARTIDA", "label"),
         P("Dos três candidatos a ajudar, só o <b>Bruno</b> tem folga real (cerca de 18 h). A sprint 10 da <b>Carla</b> já está "
           "planejada em 105%, e a da <b>Elena</b> em 130%. A folga da Carla precisa ser <i>criada</i>, adiando tarefas de "
           "prioridade média. A Elena não tem folga: ela precisa ser <i>protegida</i>, ou vira o próximo gargalo.")],
        bg=WARN_BG, border=WARN),

    P("Ação 1 · Liberar o caminho crítico", "h1"),
    P("Ana e Diego trabalham só no que leva ao go-live."),
    card([
        ("O quê", [
            *bullets([
                "<b>Ana</b> fica só com o caminho crítico (TASK-065, 073, 078) e a 119 (multi-moeda, crítica). "
                "A <b>TASK-114</b> (log de auditoria das aprovações) <b>passa para o Bruno</b>, que já está no módulo de "
                "aprovações (TASK-102). As <b>TASK-071 e 099</b> (refatoração do XML e automação da reconciliação, 16 SP, "
                "não bloqueiam o go-live) <b>ficam para depois do go-live</b>.",
                "<b>Diego</b> fica com 066 e 074 (caminho crítico), 077 e 117 (críticas). A <b>TASK-103</b> (parametrizações "
                "fiscais, 8 SP) vai para o sponsor decidir: se não for exigência fiscal no go-live, fica para depois.",
                "<b>Carla</b> adia a 116 (documentação) e a 105 (notificações por e-mail), de prioridade média. Isso libera "
                "cerca de 12 h, que ela usa para <b>executar roteiros de UAT com a Elena</b> (TASK-076).",
                "<b>Elena</b> começa o <b>UAT em partes</b>: testa a 065 e a 066 assim que cada uma ficar pronta.",
            ], "cell" if False else "bullet")]),
        ("Quem", "<b>Felipe</b> decide no planejamento, junto com <b>Ana</b>. <b>Bruno</b> assume a 114. <b>Carla</b> apoia o "
                 "UAT. O <b>sponsor</b> decide sobre a 103."),
        ("Prazo", "Primeiro dia da sprint 11 (07/01). Revisão no meio da sprint (13/01)."),
        ("Métrica de sucesso", "Ana e Diego <b>≤ 100%</b> de utilização na sprint 11 (hoje 125% e 105%). <b>065, 066, 073 e 074 "
                               "concluídas</b> até o fim da sprint 11. <b>UAT fase 2 (076) iniciado</b> até 13/01. Nenhuma "
                               "tarefa nova atribuída a Ana ou Diego."),
        ("Trade-off", "<b>24 a 32 SP ficam para depois do go-live</b>: reconciliação automática, refatoração do XML, "
                      "documentação, notificações e talvez as parametrizações fiscais. O financeiro faz <b>reconciliação "
                      "manual</b> nas primeiras semanas."),
        ("Risco", "A passagem de contexto para o Bruno custa horas da Ana no curto prazo. Adiar a 103 pode gerar <b>risco "
                  "fiscal</b>. A Ana pode resistir a largar tarefas que já começou."),
    ]),

    P("Ação 2 · Porta única de escopo com gatilho de escalada", "h1"),
    card([
        ("O quê", [
            *bullets([
                "<b>Todo pedido de mudança</b> (diretoria, diretor financeiro, time) passa pelo Felipe por <b>um único canal</b> "
                "e entra no backlog com impacto estimado. Nada entra na sprint sem <b>trocar por algo de mesmo tamanho</b>.",
                "<b>Triagem semanal</b> com o sponsor.",
                "<b>Gatilho objetivo:</b> quem passar de 100% de utilização, ou tarefa do caminho crítico atrasada mais de "
                "2 dias, leva a escalada ao sponsor em até 48 h.",
                "<b>Toda ata</b> passa a registrar ação, dono e prazo.",
            ])]),
        ("Quem", "<b>Felipe</b> é o dono. O <b>sponsor</b> aprova e comunica a regra à diretoria. <b>Carla</b> redireciona ao "
                 "Felipe os pedidos que receber direto."),
        ("Prazo", "Regra comunicada ao sponsor e ao diretor financeiro até 08/01 (2º dia da sprint 11). Primeira triagem em 10/01."),
        ("Métrica de sucesso", "<b>0 mudanças de escopo não aprovadas</b> na sprint 11 (hoje 5 por sprint, nas sprints 6 a 10). "
                               "Itens adicionados ao backlog <b>≤ 1 por sprint</b> (hoje 5). Como tarefas com mudança de "
                               "escopo têm 45% mais impedimentos, o total de impedimentos deve cair."),
        ("Trade-off", "A diretoria perde a agilidade de pedir direto. Pedidos urgentes esperam a triagem. O Felipe, já em 90%, "
                      "ganha trabalho de gestão."),
        ("Risco", "O diretor financeiro contornar a regra, como já fez. O congelamento anunciado na sprint 9 <b>não apareceu nos "
                  "dados da sprint 10</b>. Sem o sponsor sustentando a regra publicamente, ela repete o mesmo fracasso."),
    ]),

    KeepTogether([
        P("Críticas às próprias propostas", "h1"),
        *bullets([
            "<b>A folga redistribuída é pequena.</b> As 18 h do Bruno cobrem basicamente a TASK-114. O alívio real de Ana e "
            "Diego vem de <b>adiar escopo</b>, não de redistribuir. A ação 1 é mais \"cortar\" do que \"realocar\", e isso "
            "precisa ficar claro para o sponsor.",
            "<b>As estimativas não ajudam.</b> As tarefas do caminho crítico já estouraram (065: 74 h gastas de 52; 066: 70 h "
            "de 52) e nenhuma está pronta. Mesmo com as duas ações, 03/02 pode não ser cumprido. <b>Correção:</b> se 065 e 066 "
            "não estiverem concluídas em 13/01, levar ao sponsor o cenário de março.",
            "<b>Passar tarefa no meio do caminho atrasa no curto prazo.</b> Quem chega precisa de contexto, e quem passa precisa "
            "explicar. Para reduzir esse custo, a TASK-114 vai para o Bruno porque ele já está no mesmo módulo.",
            "<b>A Elena continua como próximo gargalo.</b> Ela tem cerca de 84 h a fazer. UAT em partes e a ajuda da Carla "
            "aliviam, mas desenvolvedora testando a própria interface é risco de qualidade, e a 120 (LGPD) não pode ser adiada.",
            "<b>A ação 2 depende de quem já falhou.</b> O Felipe levou 77 dias para reagir e está em 90%. Sem apoio explícito do "
            "sponsor, mais governança pode não mudar nada. Vale definir que o <b>sponsor</b> conduz a primeira triagem.",
            "<b>Nenhuma das ações ataca o retrabalho.</b> O retrabalho (31% na sprint 9) não vem de escopo nem de dependências. "
            "Uma terceira ação seria critério de pronto e revisão de código antes do QA; fica como próximo passo.",
            "<b>A base de dados é frágil.</b> A utilização do dataset_time é declarada, não medida, e as atas têm lacunas. As "
            "metas de \"≤ 100%\" dependem de que essa medição continue sendo feita.",
        ]),
    ]),
    Spacer(1, 6),
    box([P("<b>Síntese:</b> a ação 1 protege a data e a ação 2 protege o projeto de repetir o problema. Juntas, sustentam "
           "03/02, desde que haja um <b>ponto de revisão em 13/01</b>, com o cenário de março já preparado.")]),
]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm,
                        bottomMargin=1.9 * cm, title="Ações para a próxima sprint", author="Marcos Abdo")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
