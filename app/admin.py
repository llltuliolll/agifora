from django.contrib import admin
from .models import (
    UF, Cidade, Pessoa, TipoCredor, Credor, Simulacao,
    Parcelamento, TaxaExtra, IndiceLegal, ResultadoAuditoria,
    ArtigoLei, AvaliacaoDaEmpresa
)

@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome')
    search_fields = ('sigla', 'nome')

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf')
    list_filter = ('uf',)
    search_fields = ('nome',)

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'data_nasc', 'cidade')
    search_fields = ('nome', 'cpf', 'email')
    list_filter = ('cidade',)

@admin.register(TipoCredor)
class TipoCredorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'permite_cpf', 'permite_cnpj')
    search_fields = ('nome',)

@admin.register(Credor)
class CredorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj_cpf', 'tipo_credor', 'cidade')
    search_fields = ('nome', 'cnpj_cpf')
    list_filter = ('tipo_credor', 'cidade')

@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pessoa', 'credor', 'data_consulta', 'valor_a_vista')
    list_filter = ('data_consulta', 'credor')
    search_fields = ('pessoa__nome', 'credor__nome')

@admin.register(Parcelamento)
class ParcelamentoAdmin(admin.ModelAdmin):
    list_display = ('simulacao', 'num_parcelas', 'valor_parcela', 'periodicidade')
    search_fields = ('simulacao__pessoa__nome',)

@admin.register(TaxaExtra)
class TaxaExtraAdmin(admin.ModelAdmin):
    list_display = ('nome_taxa', 'valor', 'simulacao')
    search_fields = ('nome_taxa', 'simulacao__pessoa__nome')

@admin.register(IndiceLegal)
class IndiceLegalAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'taxa_maxima_permitida', 'base_legal')
    search_fields = ('descricao', 'base_legal')

@admin.register(ResultadoAuditoria)
class ResultadoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('simulacao', 'cet_calculado', 'status_abusividade')
    list_filter = ('status_abusividade',)
    search_fields = ('simulacao__pessoa__nome',)

@admin.register(ArtigoLei)
class ArtigoLeiAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'indice_legal')
    search_fields = ('titulo', 'descricao_corpo')
    list_filter = ('indice_legal',)

@admin.register(AvaliacaoDaEmpresa)
class AvaliacaoDaEmpresaAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'cidade', 'resultado_da_auditoria')
    search_fields = ('cnpj',)
    list_filter = ('cidade',)