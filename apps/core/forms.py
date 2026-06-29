from django import forms
from django.forms import inlineformset_factory
from .models import Simulacao, Parcelamento, TaxaExtra, Credor, Pessoa


class SimulacaoForm(forms.ModelForm):
    class Meta:
        model = Simulacao
        fields = ['valor_a_vista', 'credor', 'observacao']
        widgets = {
            'valor_a_vista': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1500.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'credor': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Informações adicionais (opcional)',
            }),
        }
        labels = {
            'valor_a_vista': 'Valor à Vista (R$)',
            'credor': 'Estabelecimento / Credor',
            'observacao': 'Observação',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['credor'].required = False
        self.fields['credor'].empty_label = '— Não informado —'
        self.fields['observacao'].required = False


class ParcelamentoForm(forms.ModelForm):
    class Meta:
        model = Parcelamento
        fields = ['num_parcelas', 'valor_parcela', 'periodicidade']
        widgets = {
            'num_parcelas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 12',
                'min': '1',
            }),
            'valor_parcela': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 150.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'periodicidade': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'num_parcelas': 'Número de Parcelas',
            'valor_parcela': 'Valor da Parcela (R$)',
            'periodicidade': 'Periodicidade',
        }


class TaxaExtraForm(forms.ModelForm):
    class Meta:
        model = TaxaExtra
        fields = ['nome_taxa', 'valor']
        widgets = {
            'nome_taxa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Taxa de abertura de crédito',
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 50.00',
                'step': '0.01',
                'min': '0',
            }),
        }
        labels = {
            'nome_taxa': 'Nome do Encargo',
            'valor': 'Valor (R$)',
        }


class CredorForm(forms.ModelForm):
    class Meta:
        model = Credor
        fields = ['nome', 'cnpj_cpf', 'tipo', 'cidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do estabelecimento'}),
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ ou CPF (opcional)'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cidade': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nome': 'Nome',
            'cnpj_cpf': 'CNPJ / CPF',
            'tipo': 'Tipo de Credor',
            'cidade': 'Cidade',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cnpj_cpf'].required = False
        self.fields['cidade'].required = False
        self.fields['cidade'].empty_label = '— Selecione —'
