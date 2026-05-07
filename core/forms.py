import datetime

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone as tz

from .models import (Setor, PerfilUsuario, IRP, Item,
                     TIPO_SETOR_CHOICES, PERFIL_POR_TIPO_SETOR, PERFIL_TIPO_CHOICES)
from .rubricas import rubrica_choices


def _setor_qs():
    """Todos os setores ativos (pai + filhos) — usado para validação de FK."""
    return Setor.objects.filter(ativo=True).order_by('nome')


def _setor_pai_qs():
    """Apenas setores raiz (sem pai) — para o primeiro select da cascata."""
    return Setor.objects.filter(ativo=True, pai=None).order_by('nome')


class IRPForm(forms.ModelForm):
    # Override with DateField so the browser shows only a date picker (no time).
    # The clean() method converts each date to a timezone-aware datetime at 23:59:59.
    prazo = forms.DateField(
        label='Prazo de Respostas',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
    )
    prazo_homologacao = forms.DateField(
        label='Prazo de Homologação',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
    )

    class Meta:
        model = IRP
        fields = ['titulo', 'descricao', 'prazo', 'prazo_homologacao']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prazo_homologacao'].required = True
        inst = self.instance
        if inst.pk:
            # Pre-populate with the date portion of the stored datetime
            for campo in ('prazo', 'prazo_homologacao'):
                val = getattr(inst, campo, None)
                if val:
                    # 'type=date' requires ISO format (YYYY-MM-DD) to show correctly in browsers
                    self.initial[campo] = val.strftime('%Y-%m-%d')

    def clean(self):
        cleaned = super().clean()
        prazo_d    = cleaned.get('prazo')           # date object from DateField
        prazo_hom_d = cleaned.get('prazo_homologacao')

        # Validate ordering (compare dates — must have at least 1 day difference)
        today = tz.now().date()

        if prazo_d and prazo_d <= today:
            self.add_error(
                'prazo',
                'O prazo de respostas deve ser, no mínimo, para amanhã.'
            )

        if prazo_d and prazo_hom_d and prazo_hom_d <= prazo_d:
            self.add_error(
                'prazo_homologacao',
                f'O prazo de homologação deve ser posterior ao prazo de respostas (mínimo: {(prazo_d + datetime.timedelta(days=1)).strftime("%d/%m/%Y")}).'
            )

        # Convert date → timezone-aware datetime at end of day (23:59:59)
        def _fim_do_dia(d):
            return tz.make_aware(datetime.datetime.combine(d, datetime.time(23, 59, 59)))

        if prazo_d and 'prazo' not in self.errors:
            cleaned['prazo'] = _fim_do_dia(prazo_d)
        if prazo_hom_d and 'prazo_homologacao' not in self.errors:
            cleaned['prazo_homologacao'] = _fim_do_dia(prazo_hom_d)

        return cleaned


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['numero', 'unidade', 'rubrica', 'numero_dfd', 'codigo_catmat', 'descricao', 'preco_estimado', 'quantidade_total']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: UN, KG, CX, PCT'}),
            'rubrica': forms.Select(attrs={'class': 'form-select'}),
            'numero_dfd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 774/2024'}),
            'codigo_catmat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 233708'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0,00'}),
            'quantidade_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'placeholder': 'opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rubrica'].required = False
        self.fields['rubrica'].choices = rubrica_choices()


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['codigo', 'nome', 'sigla', 'tipo', 'pai', 'ativo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 11.01.17.03'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: DEM'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'pai': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].choices = [('', '— Selecionar tipo —')] + TIPO_SETOR_CHOICES
        self.fields['pai'].queryset = Setor.objects.all().order_by('nome')
        self.fields['pai'].label = 'Setor Pai'
        self.fields['pai'].empty_label = '--- Nenhum (setor raiz) ---'
        self.fields['pai'].required = False


class PerfilForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )

    class Meta:
        model = PerfilUsuario
        fields = ['nome_completo', 'matricula', 'setor']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self._usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        self.fields['setor'].queryset = _setor_qs()
        if self._usuario:
            self.fields['email'].initial = self._usuario.email

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if commit:
            perfil.save()
            if self._usuario and 'email' in self.cleaned_data:
                self._usuario.email = self.cleaned_data['email']
                self._usuario.save(update_fields=['email'])
        return perfil


class UsuarioForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=255, label='Nome Completo',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    matricula = forms.CharField(
        max_length=20, required=False, label='Matrícula',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    foto = forms.FileField(
        required=False, label='Foto do Usuário',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'input-foto'}),
        help_text='JPG, PNG ou GIF · Máximo 10 MB'
    )
    setor = forms.ModelChoiceField(
        queryset=None, label='Setor do Servidor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    perfil_tipo = forms.ChoiceField(
        choices=[('', '— Selecione o perfil —')] + [
            ('admin',           'Administrador do Sistema'),
            ('gestor_irp',      'Gestor de IRP'),
            ('aprovador_setor', 'Aprovador de Setor Raiz'),
            ('respondente',     'Respondente'),
        ],
        label='Perfil de Acesso',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False, label='Senha',
        help_text='Deixe em branco para não alterar (ao editar).'
    )
    senha2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False, label='Confirmar senha',
        help_text='Repita a senha para confirmação.'
    )
    email2 = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,  # enforced in clean() for new users
        label='Confirmar e-mail',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'E-mail',
        }
        # Force email required at model-form level
        required_fields = ['email']

    def __init__(self, *args, **kwargs):
        self._perfil = kwargs.pop('perfil', None)
        super().__init__(*args, **kwargs)
        self.fields['setor'].queryset = _setor_qs()
        # email is always required
        self.fields['email'].required = True
        # perfil_tipo is always required
        self.fields['perfil_tipo'].required = True
        # email2 required when creating a new user
        if not self.instance.pk:
            self.fields['email2'].required = True
            self.fields['email2'].label = 'Confirmar e-mail *'
        if self._perfil:
            self.fields['nome_completo'].initial = self._perfil.nome_completo
            self.fields['matricula'].initial = self._perfil.matricula
            self.fields['setor'].initial = self._perfil.setor
            self.fields['perfil_tipo'].initial = self._perfil.perfil_tipo

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto and hasattr(foto, 'size'):
            if foto.size > 10 * 1024 * 1024:
                raise forms.ValidationError('A foto não pode ultrapassar 10 MB.')
            ext = foto.name.rsplit('.', 1)[-1].lower() if '.' in foto.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
                raise forms.ValidationError('Formato inválido. Use JPG, PNG, GIF ou WebP.')
        return foto

    def clean_senha(self):
        # A senha não é mais obrigatória para novos usuários (definida via link de e-mail)
        return self.cleaned_data.get('senha')

    def clean_perfil_tipo(self):
        perfil_tipo = self.cleaned_data.get('perfil_tipo')
        if not perfil_tipo:
            raise forms.ValidationError('Selecione um perfil de acesso.')
        return perfil_tipo

    def clean(self):
        cleaned = super().clean()

        # E-mail obrigatório sempre
        email = cleaned.get('email', '').strip()
        if not email:
            self.add_error('email', 'O e-mail é obrigatório.')

        # E-mail de confirmação: obrigatório na criação, opcional na edição
        email2 = cleaned.get('email2', '').strip()
        if not self.instance.pk and not email2:
            self.add_error('email2', 'Confirme o e-mail.')
        elif email and email2 and email.lower() != email2.lower():
            self.add_error('email2', 'Os endereços de e-mail não coincidem.')

        # Validate password confirmation
        senha = cleaned.get('senha', '')
        senha2 = cleaned.get('senha2', '')
        if senha and senha != senha2:
            self.add_error('senha2', 'As senhas não coincidem.')

        setor = cleaned.get('setor')
        perfil_tipo = cleaned.get('perfil_tipo')
        if setor and perfil_tipo:
            allowed = PERFIL_POR_TIPO_SETOR.get(setor.tipo, [])
            if perfil_tipo not in allowed:
                perfil_label = dict(PERFIL_TIPO_CHOICES).get(perfil_tipo, perfil_tipo)
                self.add_error(None,
                    f'O perfil "{perfil_label}" não é compatível com o tipo de setor '
                    f'"{setor.get_tipo_display()}". '
                    f'Perfis disponíveis: {", ".join(dict(PERFIL_TIPO_CHOICES).get(p, p) for p in allowed)}.'
                )
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        senha = self.cleaned_data.get('senha')

        if not user.pk:
            # Novos usuários começam inativos e com senha inutilizável até ativação
            user.is_active = False
            user.set_unusable_password()
        
        if senha:
            user.set_password(senha)
            # Se o gestor definir uma senha manualmente (caso os campos estejam visíveis), 
            # talvez queira que o usuário já comece ativo? 
            # Mas seguindo o requisito, vamos manter inativo até confirmação por e-mail.

        if commit:
            user.save()
            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.nome_completo = self.cleaned_data['nome_completo']
            perfil.matricula = self.cleaned_data.get('matricula', '')
            perfil.setor = self.cleaned_data.get('setor')
            perfil.perfil_tipo = self.cleaned_data.get('perfil_tipo', 'respondente')
            foto = self.cleaned_data.get('foto')
            if foto:
                perfil.foto = foto
            perfil.save()
        return user


class ItemImportForm(forms.Form):
    arquivo = forms.FileField(
        label='Arquivo',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.csv,.txt'}),
        help_text='Planilha Excel (.xlsx) ou CSV (;) com as colunas da IRP.'
    )
