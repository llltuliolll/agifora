"""
Motor de cálculo do Custo Efetivo Total (CET).

O CET é a taxa que iguala o valor presente de todos os pagamentos futuros
(parcelas + encargos) ao valor recebido à vista pelo consumidor.
Resolve-se via numpy_financial.irr() sobre o fluxo de caixa.
"""

from decimal import Decimal
import numpy_financial as npf


def calcular_cet(valor_a_vista: float, parcelas: list[dict], taxas_extras: float = 0.0) -> dict:
    """
    Calcula o CET de uma operação de crédito.

    Args:
        valor_a_vista: Valor do bem/serviço à vista (float).
        parcelas: Lista de dicts com chaves:
                  'num_parcelas' (int), 'valor_parcela' (float), 'periodicidade' (int em dias).
        taxas_extras: Soma dos encargos extras cobrados (TAC, seguro etc.) em R$.

    Returns:
        dict com:
            cet_mensal  – taxa em % ao mês
            cet_anual   – taxa em % ao ano
            acrescimo_total   – R$ cobrado a mais
            percentual_acrescimo – % cobrado a mais sobre o valor à vista
            fluxo_caixa – lista com o fluxo usado no cálculo
            status      – 'legal' | 'abusivo' | 'atencao'
            parecer     – texto explicativo
    """
    if not parcelas:
        raise ValueError("É necessário ao menos um parcelamento.")

    total_pago = sum(p['num_parcelas'] * p['valor_parcela'] for p in parcelas) + taxas_extras
    acrescimo = total_pago - valor_a_vista
    perc_acrescimo = (acrescimo / valor_a_vista) * 100 if valor_a_vista else 0

    fluxo = _montar_fluxo(valor_a_vista, parcelas, taxas_extras)

    try:
        taxa_periodo = npf.irr(fluxo)
        if taxa_periodo is None or taxa_periodo != taxa_periodo:
            taxa_periodo = 0.0
    except Exception:
        taxa_periodo = 0.0

    # Converte a taxa do período base (dias) para mensal (30 dias)
    periodo_base = parcelas[0]['periodicidade'] if parcelas else 30
    if periodo_base != 30:
        taxa_periodo = (1 + taxa_periodo) ** (30 / periodo_base) - 1

    cet_mensal = taxa_periodo * 100
    cet_anual = ((1 + taxa_periodo) ** 12 - 1) * 100

    status, parecer = _avaliar_legalidade(cet_mensal, cet_anual, acrescimo, perc_acrescimo)

    return {
        'cet_mensal': round(cet_mensal, 4),
        'cet_anual': round(cet_anual, 4),
        'acrescimo_total': round(acrescimo, 2),
        'percentual_acrescimo': round(perc_acrescimo, 2),
        'total_pago': round(total_pago, 2),
        'fluxo_caixa': fluxo,
        'status': status,
        'parecer': parecer,
    }


def _montar_fluxo(valor_a_vista: float, parcelas: list[dict], taxas_extras: float) -> list[float]:
    """Monta fluxo de caixa: entrada positiva no período 0, saídas negativas nos períodos seguintes."""
    fluxo = [valor_a_vista - taxas_extras]  # período 0: valor líquido recebido

    for p in parcelas:
        for _ in range(p['num_parcelas']):
            fluxo.append(-p['valor_parcela'])

    return fluxo


def _avaliar_legalidade(cet_mensal: float, cet_anual: float, acrescimo: float, perc: float) -> tuple[str, str]:
    """Avalia conformidade com a Lei de Usura (Decreto 22.626/33): teto 1% a.m. / 12% a.a."""
    TETO_MENSAL = 1.0
    TETO_ANUAL = 12.0

    if cet_mensal <= 0 and acrescimo <= 0:
        return 'legal', (
            'Nenhum acréscimo identificado. A operação está em conformidade com a legislação vigente. '
            'O valor pago a prazo é igual ao valor à vista, não havendo cobrança de juros.'
        )

    if cet_mensal > TETO_MENSAL or cet_anual > TETO_ANUAL:
        return 'abusivo', (
            f'ALERTA: Taxa de juros ABUSIVA identificada! '
            f'O CET calculado é de {cet_mensal:.4f}% ao mês ({cet_anual:.2f}% ao ano), '
            f'ultrapassando o limite legal de {TETO_MENSAL}% a.m. ({TETO_ANUAL}% a.a.) '
            f'estabelecido pelo Decreto nº 22.626/33 (Lei de Usura) para entidades não financeiras. '
            f'O acréscimo cobrado é de R$ {acrescimo:.2f} ({perc:.2f}% sobre o valor à vista). '
            f'Recomenda-se registrar ocorrência no PROCON e buscar assessoria jurídica.'
        )

    if cet_mensal > TETO_MENSAL * 0.8:
        return 'atencao', (
            f'ATENÇÃO: A taxa está próxima do limite legal. '
            f'CET de {cet_mensal:.4f}% a.m. ({cet_anual:.2f}% a.a.). '
            f'O limite da Lei de Usura é de {TETO_MENSAL}% a.m. '
            f'O acréscimo total é de R$ {acrescimo:.2f} ({perc:.2f}%).'
        )

    return 'legal', (
        f'Operação dentro dos limites legais. '
        f'CET de {cet_mensal:.4f}% ao mês ({cet_anual:.2f}% ao ano), '
        f'abaixo do teto de {TETO_MENSAL}% a.m. estabelecido pela Lei de Usura (Decreto 22.626/33). '
        f'Acréscimo total: R$ {acrescimo:.2f} ({perc:.2f}%).'
    )


def calcular_cet_from_simulacao(simulacao) -> dict:
    """Helper que recebe um objeto Simulacao do Django e extrai os dados necessários."""
    valor_av = float(simulacao.valor_a_vista)
    parcelas = [
        {
            'num_parcelas': p.num_parcelas,
            'valor_parcela': float(p.valor_parcela),
            'periodicidade': p.periodicidade,
        }
        for p in simulacao.parcelamentos.all()
    ]
    taxas = sum(float(t.valor) for t in simulacao.taxas_extras.all())
    return calcular_cet(valor_av, parcelas, taxas)
