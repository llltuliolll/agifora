from django.db import models
from apps.core.models import Simulacao, Credor, Cidade, IndiceLegal


class ResultadoAuditoria(models.Model):
    STATUS_CHOICES = [
        ('legal', 'Legal'),
        ('abusivo', 'Abusivo'),
        ('atencao', 'Atenção'),
    ]

    simulacao = models.OneToOneField(Simulacao, on_delete=models.CASCADE, related_name='resultado')
    cet_calculado = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text='CET em % ao mês calculado pelo sistema'
    )
    cet_anual = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text='CET em % ao ano'
    )
    taxa_nominal_mensal = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    acrescimo_total = models.DecimalField(max_digits=12, decimal_places=2)
    percentual_acrescimo = models.DecimalField(max_digits=8, decimal_places=2)
    status_abusividade = models.CharField(max_length=10, choices=STATUS_CHOICES)
    indice_referencia = models.ForeignKey(
        IndiceLegal, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='Índice legal usado como teto para a comparação'
    )
    parecer_juridico = models.TextField()
    gerado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resultado da Auditoria'
        verbose_name_plural = 'Resultados das Auditorias'
        ordering = ['-gerado_em']

    def __str__(self):
        return f'Auditoria #{self.pk} – {self.get_status_abusividade_display()}'

    @property
    def status_badge_class(self):
        return {
            'legal': 'badge-legal',
            'abusivo': 'badge-abusivo',
            'atencao': 'badge-atencao',
        }.get(self.status_abusividade, 'badge-secondary')

    @property
    def status_icon(self):
        return {
            'legal': 'check-circle',
            'abusivo': 'x-circle',
            'atencao': 'alert-triangle',
        }.get(self.status_abusividade, 'info')


class AvaliacaoEmpresa(models.Model):
    credor = models.ForeignKey(Credor, on_delete=models.CASCADE, related_name='avaliacoes')
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='avaliacoes')
    resultado = models.ForeignKey(ResultadoAuditoria, on_delete=models.CASCADE, related_name='avaliacoes')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação de Empresa'
        verbose_name_plural = 'Avaliações de Empresas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.credor.nome} – {self.resultado.get_status_abusividade_display()}'
