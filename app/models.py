from django.db import models

class UF(models.Model):
    sigla = models.CharField(max_length=2, unique=True, help_text="Ex: MG, SP")
    nome = models.CharField(max_length=100, help_text="Ex: Minas Gerais")

    def __str__(self):
        return self.sigla


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    uf = models.ForeignKey(UF, on_delete=models.CASCADE, related_name='cidades')

    def __str__(self):
        return f"{self.nome} - {self.uf.sigla}"


class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    data_nasc = models.DateField()
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome


class TipoCredor(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Comércio, Pessoa Física")
    permite_cpf = models.BooleanField(default=False, verbose_name="Exige CPF?")
    permite_cnpj = models.BooleanField(default=False, verbose_name="Exige CNPJ?")

    def __str__(self):
        return self.nome


class Credor(models.Model):
    nome = models.CharField(max_length=150)
    cnpj_cpf = models.CharField(max_length=18, unique=True, verbose_name="CNPJ ou CPF")
    tipo_credor = models.ForeignKey(TipoCredor, on_delete=models.PROTECT)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome


class Simulacao(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='simulacoes')
    credor = models.ForeignKey(Credor, on_delete=models.CASCADE, related_name='simulacoes')
    data_consulta = models.DateField(auto_now_add=True)
    valor_a_vista = models.DecimalField(max_digits=12, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Simulação: {self.pessoa.nome} -> {self.credor.nome}"


class Parcelamento(models.Model):
    simulacao = models.ForeignKey(Simulacao, on_delete=models.CASCADE, related_name='parcelamentos')
    num_parcelas = models.PositiveIntegerField(verbose_name="Número de Parcelas")
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2)
    periodicidade = models.PositiveIntegerField(help_text="Periodicidade em dias (ex: 30 para mensal)")

    def __str__(self):
        return f"{self.num_parcelas}x de R$ {self.valor_parcela}"


class TaxaExtra(models.Model):
    simulacao = models.ForeignKey(Simulacao, on_delete=models.CASCADE, related_name='taxas_extras')
    nome_taxa = models.CharField(max_length=100, help_text="Ex: TAC, Seguro")
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.nome_taxa} - R$ {self.valor}"


class IndiceLegal(models.Model):
    descricao = models.CharField(max_length=200, help_text="Ex: Lei de Usura")
    taxa_maxima_permitida = models.DecimalField(max_digits=6, decimal_places=4, help_text="Taxa em % (Ex: 1.0 para 1%)")
    base_legal = models.CharField(max_length=250)

    def __str__(self):
        return self.descricao


class ResultadoAuditoria(models.Model):
    simulacao = models.OneToOneField(Simulacao, on_delete=models.CASCADE, related_name='resultado_auditoria')
    cet_calculado = models.DecimalField(max_digits=6, decimal_places=4, verbose_name="CET Calculado (Taxa Real)")
    status_abusividade = models.CharField(max_length=100, help_text="Ex: Abusivo, Dentro da Lei")
    parecer_juridico = models.TextField()

    def __str__(self):
        return f"Auditoria da Simulação #{self.simulacao.id}"


class ArtigoLei(models.Model):
    titulo = models.CharField(max_length=150, help_text="Ex: Art. 1º do Decreto 22.626/33")
    descricao_corpo = models.TextField()
    indice_legal = models.ForeignKey(IndiceLegal, on_delete=models.CASCADE, related_name='artigos')

    def __str__(self):
        return self.titulo


class AvaliacaoDaEmpresa(models.Model):
    cnpj = models.CharField(max_length=18)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    resultado_da_auditoria = models.ForeignKey(ResultadoAuditoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"Avaliação CNPJ {self.cnpj} - {self.cidade.nome}"