from django.contrib import admin
from .models import UF, Cidade, Pessoa, TipoCredor, Credor, IndiceLegal, ArtigoLei, Simulacao, Parcelamento, TaxaExtra


@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome']
    search_fields = ['sigla', 'nome']


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'uf']
    list_filter = ['uf']
    search_fields = ['nome']


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'email', 'cidade']
    search_fields = ['nome', 'cpf', 'email']


@admin.register(TipoCredor)
class TipoCredorAdmin(admin.ModelAdmin):
    list_display = ['nome']


@admin.register(Credor)
class CredorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cidade', 'cnpj_cpf']
    list_filter = ['tipo', 'cidade__uf']
    search_fields = ['nome', 'cnpj_cpf']


@admin.register(IndiceLegal)
class IndiceLegalAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'taxa_maxima_permitida', 'base_legal', 'ativo']
    list_filter = ['ativo']


@admin.register(ArtigoLei)
class ArtigoLeiAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'indice_legal']
    search_fields = ['titulo']


class ParcelamentoInline(admin.TabularInline):
    model = Parcelamento
    extra = 0


class TaxaExtraInline(admin.TabularInline):
    model = TaxaExtra
    extra = 0


@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'pessoa', 'credor', 'valor_a_vista', 'data_consulta']
    list_filter = ['data_consulta']
    search_fields = ['pessoa__nome', 'credor__nome']
    inlines = [ParcelamentoInline, TaxaExtraInline]
    readonly_fields = ['data_consulta']
