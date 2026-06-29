from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class UF(models.Model):
    sigla = models.CharField(max_length=2, unique=True)
    nome = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'UF'
        verbose_name_plural = 'UFs'
        ordering = ['sigla']

    def __str__(self):
        return f'{self.sigla} – {self.nome}'


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    uf = models.ForeignKey(UF, on_delete=models.PROTECT, related_name='cidades')

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['nome']
        unique_together = ['nome', 'uf']

    def __str__(self):
        return f'{self.nome}/{self.uf.sigla}'


class Pessoa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pessoa', null=True, blank=True)
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    data_nasc = models.DateField(null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='pessoas')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TipoCredor(models.Model):
    nome = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = 'Tipo de Credor'
        verbose_name_plural = 'Tipos de Credor'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Credor(models.Model):
    nome = models.CharField(max_length=150)
    cnpj_cpf = models.CharField(max_length=18, blank=True)
    tipo = models.ForeignKey(TipoCredor, on_delete=models.PROTECT, related_name='credores')
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='credores')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Credor / Estabelecimento'
        verbose_name_plural = 'Credores / Estabelecimentos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class IndiceLegal(models.Model):
    descricao = models.CharField(max_length=200)
    taxa_maxima_permitida = models.DecimalField(
        max_digits=8, decimal_places=4,
        help_text='Taxa máxima em % ao mês. Ex: 1.0000 para 1% a.m.'
    )
    base_legal = models.CharField(max_length=200)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Índice Legal'
        verbose_name_plural = 'Índices Legais'
        ordering = ['descricao']

    def __str__(self):
        return f'{self.descricao} ({self.taxa_maxima_permitida}% a.m.)'


class ArtigoLei(models.Model):
    titulo = models.CharField(max_length=200)
    descricao_corpo = models.TextField()
    indice_legal = models.ForeignKey(IndiceLegal, on_delete=models.SET_NULL, null=True, blank=True, related_name='artigos')

    class Meta:
        verbose_name = 'Artigo de Lei'
        verbose_name_plural = 'Artigos de Lei'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class Simulacao(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True, blank=True, related_name='simulacoes')
    credor = models.ForeignKey(Credor, on_delete=models.SET_NULL, null=True, blank=True, related_name='simulacoes')
    data_consulta = models.DateTimeField(auto_now_add=True)
    valor_a_vista = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Valor do produto/serviço à vista'
    )
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Simulação'
        verbose_name_plural = 'Simulações'
        ordering = ['-data_consulta']

    def __str__(self):
        return f'Simulação #{self.pk} – {self.data_consulta.strftime("%d/%m/%Y %H:%M")}'

    @property
    def valor_total_parcelado(self):
        total = sum(
            p.num_parcelas * p.valor_parcela for p in self.parcelamentos.all()
        )
        extras = sum(t.valor for t in self.taxas_extras.all())
        return total + extras


class Parcelamento(models.Model):
    PERIODICIDADE_CHOICES = [
        (30, 'Mensal (30 dias)'),
        (15, 'Quinzenal (15 dias)'),
        (7, 'Semanal (7 dias)'),
        (1, 'Diário'),
    ]

    simulacao = models.ForeignKey(Simulacao, on_delete=models.CASCADE, related_name='parcelamentos')
    num_parcelas = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    periodicidade = models.IntegerField(choices=PERIODICIDADE_CHOICES, default=30, help_text='Intervalo em dias')

    class Meta:
        verbose_name = 'Parcelamento'
        verbose_name_plural = 'Parcelamentos'

    def __str__(self):
        return f'{self.num_parcelas}x de R$ {self.valor_parcela}'

    @property
    def valor_total(self):
        return self.num_parcelas * self.valor_parcela


class TaxaExtra(models.Model):
    simulacao = models.ForeignKey(Simulacao, on_delete=models.CASCADE, related_name='taxas_extras')
    nome_taxa = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Taxa Extra'
        verbose_name_plural = 'Taxas Extras'

    def __str__(self):
        return f'{self.nome_taxa}: R$ {self.valor}'
