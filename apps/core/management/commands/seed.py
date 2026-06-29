"""
Comando: python manage.py seed
Popula o banco com dados iniciais essenciais para o funcionamento do sistema.
"""

from django.core.management.base import BaseCommand
from apps.core.models import UF, Cidade, TipoCredor, IndiceLegal, ArtigoLei


ESTADOS = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
    ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"),
    ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"),
    ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
    ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

CIDADES_MG = [
    "Muzambinho", "Guaxupé", "Alfenas", "Poços de Caldas", "Varginha",
    "Passos", "Lavras", "São Sebastião do Paraíso", "Três Pontas", "Itajubá",
]

TIPOS_CREDOR = [
    "Comércio Varejista",
    "Pessoa Física (Informal)",
    "Financeira",
    "Banco",
    "Cooperativa de Crédito",
    "Loja de Eletrodomésticos",
    "Loja de Móveis",
    "Concessionária",
    "Outro",
]

INDICES = [
    {
        "descricao": "Lei de Usura — Decreto 22.626/33",
        "taxa_maxima_permitida": 1.0000,
        "base_legal": "Decreto nº 22.626, de 7 de abril de 1933, Art. 1º",
        "ativo": True,
    },
    {
        "descricao": "Taxa Média BCB — Crédito Pessoal Não Consignado (referência)",
        "taxa_maxima_permitida": 6.7500,
        "base_legal": "Banco Central do Brasil — Nota de Crédito",
        "ativo": True,
    },
]

ARTIGOS = [
    {
        "titulo": "Art. 1º do Decreto 22.626/33 — Lei de Usura",
        "descricao_corpo": (
            "É vedado, e será punido nos termos desta lei, estipular em quaisquer contratos "
            "taxas de juros superiores ao dobro da taxa legal (doze por cento ao ano). "
            "Equipara-se à estipulação de juros excessivos a concessão, sob títulos ou pretextos "
            "diversos, como o de comissão, prêmio, desconto, despesa de registro, multa ou "
            "qualquer outro, de vantagens que, diretamente ou indiretamente, representem mais de "
            "doze por cento ao ano."
        ),
        "indice_key": 0,
    },
]


class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais (UFs, cidades, tipos de credor, índices legais)"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando seed do banco de dados...")

        # UFs
        self.stdout.write("  Criando UFs...")
        for sigla, nome in ESTADOS:
            UF.objects.get_or_create(sigla=sigla, defaults={"nome": nome})

        # Cidades de MG (exemplo)
        self.stdout.write("  Criando cidades de MG...")
        mg = UF.objects.get(sigla="MG")
        for nome in CIDADES_MG:
            Cidade.objects.get_or_create(nome=nome, uf=mg)

        # Tipos de Credor
        self.stdout.write("  Criando tipos de credor...")
        for nome in TIPOS_CREDOR:
            TipoCredor.objects.get_or_create(nome=nome)

        # Índices Legais
        self.stdout.write("  Criando índices legais...")
        indices_criados = []
        for dados in INDICES:
            obj, _ = IndiceLegal.objects.get_or_create(
                descricao=dados["descricao"],
                defaults={
                    "taxa_maxima_permitida": dados["taxa_maxima_permitida"],
                    "base_legal": dados["base_legal"],
                    "ativo": dados["ativo"],
                },
            )
            indices_criados.append(obj)

        # Artigos de Lei
        self.stdout.write("  Criando artigos de lei...")
        for art in ARTIGOS:
            ArtigoLei.objects.get_or_create(
                titulo=art["titulo"],
                defaults={
                    "descricao_corpo": art["descricao_corpo"],
                    "indice_legal": indices_criados[art["indice_key"]],
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed concluido com sucesso!"))
        self.stdout.write("  >> Acesse /admin para gerenciar os dados.")
