import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Q

from .models import Simulacao, Parcelamento, TaxaExtra, Credor, IndiceLegal
from .forms import SimulacaoForm, ParcelamentoForm, TaxaExtraForm, CredorForm
from .calculadora import calcular_cet_from_simulacao
from apps.auditoria.models import ResultadoAuditoria, AvaliacaoEmpresa


def home(request):
    stats = {
        'total_simulacoes': Simulacao.objects.count(),
        'abusivas': ResultadoAuditoria.objects.filter(status_abusividade='abusivo').count(),
        'legais': ResultadoAuditoria.objects.filter(status_abusividade='legal').count(),
        'credores': Credor.objects.count(),
    }
    recentes = ResultadoAuditoria.objects.select_related(
        'simulacao__credor'
    ).order_by('-gerado_em')[:5]
    return render(request, 'core/home.html', {'stats': stats, 'recentes': recentes})


def simulacao_nova(request):
    sim_form = SimulacaoForm(request.POST or None)
    parc_form = ParcelamentoForm(request.POST or None)
    taxa_form = TaxaExtraForm(request.POST or None)

    if request.method == 'POST':
        if sim_form.is_valid() and parc_form.is_valid():
            simulacao = sim_form.save(commit=False)
            if request.user.is_authenticated and hasattr(request.user, 'pessoa'):
                simulacao.pessoa = request.user.pessoa
            simulacao.save()

            parcelamento = parc_form.save(commit=False)
            parcelamento.simulacao = simulacao
            parcelamento.save()

            # Taxas extras adicionadas via JS (campo hidden JSON)
            taxas_json = request.POST.get('taxas_json', '[]')
            try:
                taxas_lista = json.loads(taxas_json)
                for taxa in taxas_lista:
                    if taxa.get('nome_taxa') and taxa.get('valor'):
                        TaxaExtra.objects.create(
                            simulacao=simulacao,
                            nome_taxa=taxa['nome_taxa'],
                            valor=float(taxa['valor']),
                        )
            except (json.JSONDecodeError, ValueError):
                pass

            return redirect('auditoria:calcular', pk=simulacao.pk)

        messages.error(request, 'Corrija os erros abaixo antes de continuar.')

    indices = IndiceLegal.objects.filter(ativo=True)
    return render(request, 'core/simulacao_nova.html', {
        'sim_form': sim_form,
        'parc_form': parc_form,
        'taxa_form': taxa_form,
        'indices': indices,
    })


def historico(request):
    qs = ResultadoAuditoria.objects.select_related(
        'simulacao__credor', 'simulacao__credor__cidade'
    ).order_by('-gerado_em')

    status_filter = request.GET.get('status')
    if status_filter in ('legal', 'abusivo', 'atencao'):
        qs = qs.filter(status_abusividade=status_filter)

    busca = request.GET.get('q', '').strip()
    if busca:
        qs = qs.filter(
            Q(simulacao__credor__nome__icontains=busca) |
            Q(simulacao__observacao__icontains=busca)
        )

    return render(request, 'core/historico.html', {
        'resultados': qs,
        'status_filter': status_filter,
        'busca': busca,
    })


def credores_lista(request):
    credores = Credor.objects.select_related('tipo', 'cidade').annotate(
        total_simulacoes=Count('simulacoes'),
        total_abusivas=Count('simulacoes__resultado', filter=Q(simulacoes__resultado__status_abusividade='abusivo')),
    ).order_by('nome')

    busca = request.GET.get('q', '').strip()
    if busca:
        credores = credores.filter(nome__icontains=busca)

    return render(request, 'core/credores_lista.html', {'credores': credores, 'busca': busca})


def credor_novo(request):
    form = CredorForm(request.POST or None)
    if form.is_valid():
        credor = form.save()
        messages.success(request, f'Estabelecimento "{credor.nome}" cadastrado com sucesso.')
        return redirect('core:credores_lista')
    return render(request, 'core/credor_form.html', {'form': form, 'titulo': 'Novo Estabelecimento'})


def credor_editar(request, pk):
    credor = get_object_or_404(Credor, pk=pk)
    form = CredorForm(request.POST or None, instance=credor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Estabelecimento atualizado.')
        return redirect('core:credores_lista')
    return render(request, 'core/credor_form.html', {'form': form, 'titulo': 'Editar Estabelecimento', 'credor': credor})


def credor_detalhe(request, pk):
    credor = get_object_or_404(Credor, pk=pk)
    resultados = ResultadoAuditoria.objects.filter(
        simulacao__credor=credor
    ).select_related('simulacao').order_by('-gerado_em')
    return render(request, 'core/credor_detalhe.html', {'credor': credor, 'resultados': resultados})


def sobre(request):
    return render(request, 'core/sobre.html')
