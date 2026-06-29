from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from apps.core.models import Simulacao, IndiceLegal
from apps.core.calculadora import calcular_cet_from_simulacao
from .models import ResultadoAuditoria, AvaliacaoEmpresa


def calcular(request, pk):
    simulacao = get_object_or_404(Simulacao, pk=pk)

    if hasattr(simulacao, 'resultado'):
        return redirect('auditoria:resultado', pk=simulacao.resultado.pk)

    if not simulacao.parcelamentos.exists():
        from django.contrib import messages
        messages.error(request, 'A simulação não possui parcelamento cadastrado.')
        return redirect('core:simulacao_nova')

    dados = calcular_cet_from_simulacao(simulacao)

    indice = IndiceLegal.objects.filter(ativo=True).order_by('taxa_maxima_permitida').first()

    resultado = ResultadoAuditoria.objects.create(
        simulacao=simulacao,
        cet_calculado=dados['cet_mensal'],
        cet_anual=dados['cet_anual'],
        acrescimo_total=dados['acrescimo_total'],
        percentual_acrescimo=dados['percentual_acrescimo'],
        status_abusividade=dados['status'],
        indice_referencia=indice,
        parecer_juridico=dados['parecer'],
    )

    if simulacao.credor:
        AvaliacaoEmpresa.objects.create(
            credor=simulacao.credor,
            cidade=simulacao.credor.cidade,
            resultado=resultado,
        )

    return redirect('auditoria:resultado', pk=resultado.pk)


def resultado(request, pk):
    resultado = get_object_or_404(
        ResultadoAuditoria.objects.select_related(
            'simulacao__credor__cidade__uf',
            'simulacao__credor__tipo',
            'indice_referencia',
        ),
        pk=pk,
    )
    parcelamentos = resultado.simulacao.parcelamentos.all()
    taxas_extras = resultado.simulacao.taxas_extras.all()

    return render(request, 'auditoria/resultado.html', {
        'resultado': resultado,
        'simulacao': resultado.simulacao,
        'parcelamentos': parcelamentos,
        'taxas_extras': taxas_extras,
    })


def mapa(request):
    avaliacoes = AvaliacaoEmpresa.objects.select_related(
        'credor', 'cidade__uf', 'resultado'
    ).order_by('-criado_em')[:50]
    return render(request, 'auditoria/mapa.html', {'avaliacoes': avaliacoes})
