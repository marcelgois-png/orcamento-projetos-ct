from datetime import date
from decimal import Decimal

from django import forms

from core.models import Setor
from .models import (
    RecursoOrcamentario, Transferencia, Despesa,
    PdiPerspectiva, PdiObjetivoEstrategico, PdiIndicador, PdiMeta,
    NaturezaRecurso, Rubrica, OrigemRecurso, RegistroPrecoItem, SituacaoDespesa,
)


def _setor_qs():
    return Setor.objects.filter(ativo=True).order_by('codigo')


def _ano_choices():
    """2021 até o ano corrente, sempre inclusivo."""
    ano_atual = date.today().year
    return [(a, str(a)) for a in range(2021, ano_atual + 1)]


def _natureza_choices():
    return [('', '— Selecione —')] + [
        (n.nome, n.nome)
        for n in NaturezaRecurso.objects.filter(ativo=True).order_by('ordem', 'nome')
    ]


def _rubrica_choices():
    return [('', '— Selecione —')] + [
        (str(r), str(r))
        for r in Rubrica.objects.filter(ativo=True).select_related('natureza').order_by('ordem', 'codigo')
    ]


def _origem_choices():
    return [('', '— Selecione —')] + [
        (o.nome, o.nome)
        for o in OrigemRecurso.objects.filter(ativo=True).order_by('ordem', 'nome')
    ]


def _rubrica_choices_por_natureza():
    """Retorna lista de choices agrupadas por natureza para uso com optgroup."""
    grupos = {}
    for r in Rubrica.objects.filter(ativo=True).select_related('natureza').order_by('ordem', 'codigo'):
        nat = r.natureza.nome if r.natureza else 'Sem natureza'
        grupos.setdefault(nat, []).append((str(r), str(r)))
    result = [('', '— Selecione —')]
    for nat, items in grupos.items():
        result.append((nat, items))  # Django suporta optgroup como (label, [(val, disp)])
    return result


def _situacao_despesa_choices(incluir=None):
    choices = [
        (s.chave, s.nome)
        for s in SituacaoDespesa.objects.filter(ativo=True).order_by('ordem', 'nome')
    ]
    if incluir and incluir not in {value for value, _label in choices}:
        obj = SituacaoDespesa.objects.filter(chave=incluir).first()
        choices.append((incluir, obj.nome if obj else str(incluir).replace('-', ' ').title()))
    if not choices:
        choices = [
            ('empenhada', 'Empenhada'),
            ('liquidada', 'Liquidada'),
            ('paga', 'Paga'),
            ('cancelada', 'Cancelada'),
        ]
    return choices


class RecursoOrcamentarioForm(forms.ModelForm):
    class Meta:
        model = RecursoOrcamentario
        fields = ['ano_fiscal', 'setor', 'origem_recurso', 'natureza', 'rubrica',
                  'valor_orcamentario', 'observacoes']
        widgets = {
            'ano_fiscal':         forms.Select(attrs={'class': 'form-select'}),
            'setor':              forms.Select(attrs={'class': 'form-select'}),
            'origem_recurso':     forms.Select(attrs={'class': 'form-select'}),
            'natureza':           forms.Select(attrs={'class': 'form-select'}),
            'rubrica':            forms.Select(attrs={'class': 'form-select'}),
            'valor_orcamentario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['setor'].queryset  = _setor_qs()
        self.fields['setor'].empty_label = '— Selecione o setor —'

        # Origem do Recurso: dinâmica do cadastro
        self.fields['origem_recurso'] = forms.ChoiceField(
            label='Origem do Recurso',
            choices=_origem_choices(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

        # Ano fiscal: select 2021 → ano atual
        self.fields['ano_fiscal'].widget  = forms.Select(
            attrs={'class': 'form-select'},
            choices=_ano_choices(),
        )
        # Garante que o campo aceite qualquer inteiro do range (sem validação de choices do modelo)
        self.fields['ano_fiscal'] = forms.ChoiceField(
            label='Ano Fiscal',
            choices=_ano_choices(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

        # Natureza: dinâmica do cadastro
        self.fields['natureza'] = forms.ChoiceField(
            label='Natureza',
            choices=_natureza_choices(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

        # Rubrica: dinâmica do cadastro, agrupada por natureza
        self.fields['rubrica'] = forms.ChoiceField(
            label='Rubrica',
            choices=_rubrica_choices_por_natureza(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

        # Pré-selecionar ano atual em novos registros
        if not self.instance.pk:
            self.fields['ano_fiscal'].initial = str(date.today().year)

    def clean_ano_fiscal(self):
        return int(self.cleaned_data['ano_fiscal'])


class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['origem', 'destino', 'valor', 'descricao', 'link_sipac', 'comprovante', 'data']
        labels = {
            'descricao': 'Observações',
        }
        widgets = {
            'origem':      forms.Select(attrs={'class': 'form-select'}),
            'destino':     forms.Select(attrs={'class': 'form-select'}),
            'valor':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva a finalidade ou contexto da transferência…'}),
            'link_sipac':  forms.URLInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'https://sipac.ufpb.br/…',
            }),
            'comprovante': forms.FileInput(attrs={'class': 'd-none'}),
            'data':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = RecursoOrcamentario.objects.select_related('setor').order_by('ano_fiscal', 'setor__codigo')
        self.fields['origem'].queryset = qs
        self.fields['destino'].queryset = qs
        # Observações sempre obrigatório
        self.fields['descricao'].required = True
        # Link SIPAC: opcional por padrão (condicional: obrigatório só quando muda natureza no mesmo setor)
        self.fields['link_sipac'].required = False

    def clean(self):
        cleaned = super().clean()
        origem    = cleaned.get('origem')
        destino   = cleaned.get('destino')
        valor     = cleaned.get('valor')
        link_sipac = cleaned.get('link_sipac', '').strip()

        if not (origem and destino):
            return cleaned

        if origem == destino:
            self.add_error('destino', 'Origem e destino não podem ser iguais.')
            return cleaned

        if origem.origem_recurso != destino.origem_recurso:
            self.add_error(
                'destino',
                'A Origem do Recurso do destino deve ser igual à da origem '
                f'("{origem.origem_recurso}").',
            )

        mesmo_setor = (origem.setor_id == destino.setor_id)

        if mesmo_setor:
            # Mesmo setor: rubrica do destino DEVE ser diferente da origem
            if destino.rubrica == origem.rubrica:
                self.add_error(
                    'destino',
                    'Transferência no mesmo setor: a Rubrica do destino deve ser diferente da origem '
                    f'— o objetivo é remanejar entre rubricas distintas ("{origem.rubrica}").',
                )
            # Link SIPAC obrigatório apenas quando a natureza muda entre origem e destino
            if destino.natureza != origem.natureza and not link_sipac:
                self.add_error(
                    'link_sipac',
                    'O Link do Processo SIPAC é obrigatório quando há mudança de natureza (Custeio ↔ Capital).',
                )
        else:
            # Setores diferentes: natureza e rubrica devem ser iguais
            if destino.natureza != origem.natureza:
                self.add_error(
                    'destino',
                    f'Transferência entre setores: a natureza do destino deve ser '
                    f'"{origem.get_natureza_display()}" (igual à da origem).',
                )
            if destino.rubrica != origem.rubrica:
                self.add_error(
                    'destino',
                    f'Transferência entre setores: a rubrica do destino deve ser '
                    f'"{origem.rubrica}" (igual à da origem).',
                )

        if valor and valor > origem.saldo_atual:
            self.add_error('valor', f'Valor excede o saldo disponível (R$ {origem.saldo_atual:,.2f}).')

        return cleaned


class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = [
            'data_despesa', 'requisicao', 'nota_empenho', 'pregao_ref', 'pregao',
            'registro_preco_item',
            'discriminacao', 'quantidade', 'valor_unitario', 'valor_comprometido',
            'rubrica', 'setor', 'recurso', 'situacao', 'natureza', 'categoria_material',
            'perspectiva_pdi', 'objetivo_pdi', 'indicador_pdi', 'observacao',
        ]
        widgets = {
            'data_despesa':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'requisicao':         forms.TextInput(attrs={'class': 'form-control'}),
            'nota_empenho':       forms.TextInput(attrs={'class': 'form-control'}),
            'pregao_ref':         forms.TextInput(attrs={'class': 'form-control'}),
            'pregao':             forms.Select(attrs={'class': 'form-select'}),
            'registro_preco_item': forms.Select(attrs={'class': 'form-select'}),
            'discriminacao':      forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valor_unitario':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_comprometido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rubrica':            forms.Select(attrs={'class': 'form-select'}),
            'setor':              forms.Select(attrs={'class': 'form-select'}),
            'recurso':            forms.Select(attrs={'class': 'form-select'}),
            'situacao':           forms.Select(attrs={'class': 'form-select'}),
            'natureza':           forms.Select(attrs={'class': 'form-select'}),
            'categoria_material': forms.TextInput(attrs={'class': 'form-control'}),
            'perspectiva_pdi':    forms.Select(attrs={'class': 'form-select'}),
            'objetivo_pdi':       forms.Select(attrs={'class': 'form-select'}),
            'indicador_pdi':      forms.Select(attrs={'class': 'form-select'}),
            'observacao':         forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['setor'].queryset = _setor_qs()
        self.fields['setor'].empty_label = '— Selecione —'
        self.fields['recurso'].queryset = RecursoOrcamentario.objects.select_related('setor').order_by('ano_fiscal', 'setor__codigo')
        self.fields['recurso'].empty_label = '— Selecione o recurso —'
        self.fields['perspectiva_pdi'].empty_label = '— Selecione —'
        self.fields['objetivo_pdi'].empty_label = '— Selecione —'
        self.fields['indicador_pdi'].empty_label = '— Selecione —'
        self.fields['pregao'].empty_label = '— Nenhum (licitação externa) —'

        self.fields['registro_preco_item'].queryset = (
            RegistroPrecoItem.objects.select_related('registro', 'pregao_item')
            .order_by('registro__numero_pregao', 'numero_item')
        )
        self.fields['registro_preco_item'].empty_label = '— Nenhum —'

        # Natureza e Rubrica dinâmicas
        self.fields['natureza'] = forms.ChoiceField(
            label='Natureza do Recurso',
            choices=_natureza_choices(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )
        self.fields['rubrica'] = forms.ChoiceField(
            label='Rubrica',
            choices=_rubrica_choices_por_natureza(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )
        self.fields['situacao'] = forms.ChoiceField(
            label='Situação',
            choices=_situacao_despesa_choices(getattr(self.instance, 'situacao', None)),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )
        self.fields['recurso'].required = True
        self.fields['setor'].required = False
        self.fields['natureza'].required = False
        self.fields['rubrica'].required = False

        if self.instance.pk and self.instance.data_despesa:
            self.initial['data_despesa'] = self.instance.data_despesa.strftime('%Y-%m-%d')

    def clean(self):
        cleaned = super().clean()
        recurso = cleaned.get('recurso')
        valor = cleaned.get('valor_comprometido') or Decimal('0')

        if not recurso:
            self.add_error('recurso', 'Selecione o recurso que será utilizado para esta despesa.')
            return cleaned

        saldo_disponivel = recurso.saldo_atual
        if self.instance.pk and self.instance.recurso_id == recurso.pk:
            saldo_disponivel += self.instance.valor_comprometido or Decimal('0')

        if valor and valor > saldo_disponivel:
            self.add_error(
                'valor_comprometido',
                f'Valor excede o saldo disponível do recurso selecionado (R$ {saldo_disponivel:,.2f}).',
            )

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        recurso = self.cleaned_data.get('recurso')
        if recurso:
            instance.recurso = recurso
            instance.setor = recurso.setor
            instance.natureza = recurso.natureza
            instance.rubrica = recurso.rubrica
        registro_item = self.cleaned_data.get('registro_preco_item')
        if registro_item:
            instance.registro_preco_item = registro_item
            if registro_item.registro.pregao_id:
                instance.pregao = registro_item.registro.pregao
            if not instance.pregao_ref:
                instance.pregao_ref = registro_item.registro.numero_pregao
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class PdiPerspectivaForm(forms.ModelForm):
    class Meta:
        model = PdiPerspectiva
        fields = ['codigo', 'nome', 'ordem']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome':   forms.TextInput(attrs={'class': 'form-control'}),
            'ordem':  forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PdiObjetivoForm(forms.ModelForm):
    class Meta:
        model = PdiObjetivoEstrategico
        fields = ['perspectiva', 'codigo', 'nome', 'ordem']
        widgets = {
            'perspectiva': forms.Select(attrs={'class': 'form-select'}),
            'codigo':      forms.TextInput(attrs={'class': 'form-control'}),
            'nome':        forms.TextInput(attrs={'class': 'form-control'}),
            'ordem':       forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PdiIndicadorForm(forms.ModelForm):
    class Meta:
        model = PdiIndicador
        fields = ['objetivo', 'codigo', 'nome', 'unidade_medida']
        widgets = {
            'objetivo':       forms.Select(attrs={'class': 'form-select'}),
            'codigo':         forms.TextInput(attrs={'class': 'form-control'}),
            'nome':           forms.TextInput(attrs={'class': 'form-control'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}),
        }
