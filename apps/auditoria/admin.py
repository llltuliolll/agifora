from django.contrib import admin
from .models import ResultadoAuditoria, AvaliacaoEmpresa


@admin.register(ResultadoAuditoria)
class ResultadoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'simulacao', 'cet_calculado', 'cet_anual', 'status_abusividade', 'gerado_em']
    list_filter = ['status_abusividade', 'gerado_em']
    readonly_fields = ['gerado_em']
    search_fields = ['simulacao__credor__nome']


@admin.register(AvaliacaoEmpresa)
class AvaliacaoEmpresaAdmin(admin.ModelAdmin):
    list_display = ['credor', 'cidade', 'resultado', 'criado_em']
    list_filter = ['resultado__status_abusividade']
    readonly_fields = ['criado_em']
