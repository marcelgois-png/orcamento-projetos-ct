from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils.text import slugify

from core.models import Setor, RUBRICA_CHOICES
from core.models import Pregao, PregaoItem


NATUREZA_CHOICES = [
    ('custeio', 'Custeio'),
    ('capital',  'Capital'),
]


# ── Cadastros de Listas ───────────────────────────────────────────────────────

class NaturezaRecurso(models.Model):
    nome  = models.CharField('Nome', max_length=100, unique=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Natureza do Recurso'
        verbose_name_plural = 'Naturezas do Recurso'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Rubrica(models.Model):
    codigo   = models.CharField('Código', max_length=20)
    nome     = models.CharField('Nome', max_length=200)
    natureza = models.ForeignKey(
        NaturezaRecurso, verbose_name='Natureza do Recurso',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rubricas',
    )
    ordem = models.PositiveIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Rubrica'
        verbose_name_plural = 'Rubricas'
        ordering = ['ordem', 'codigo', 'nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}'

    @property
    def label_completo(self):
        return f'{self.codigo} - {self.nome}'


class OrigemRecurso(models.Model):
    nome  = models.CharField('Nome', max_length=200, unique=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Origem do Recurso'
        verbose_name_plural = 'Origens do Recurso'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


# ── PDI ──────────────────────────────────────────────────────────────────────

class SituacaoDespesa(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)
    chave = models.SlugField('Chave', max_length=50, unique=True, blank=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)
    impacta_saldo = models.BooleanField('Deduz do saldo', default=True)
    badge = models.CharField('Classe visual', max_length=40, default='bg-secondary', blank=True)

    class Meta:
        verbose_name = 'Situação da Despesa'
        verbose_name_plural = 'Situações da Despesa'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.chave:
            base = slugify(self.nome)[:45] or 'situacao'
            chave = base
            i = 2
            while SituacaoDespesa.objects.filter(chave=chave).exclude(pk=self.pk).exists():
                sufixo = f'-{i}'
                chave = f'{base[:50 - len(sufixo)]}{sufixo}'
                i += 1
            self.chave = chave
        super().save(*args, **kwargs)

    @classmethod
    def chaves_sem_impacto(cls):
        chaves = list(cls.objects.filter(impacta_saldo=False).values_list('chave', flat=True))
        return chaves or ['cancelada']

    @classmethod
    def chaves_ativas(cls):
        chaves = list(cls.objects.filter(ativo=True).values_list('chave', flat=True))
        return chaves or ['empenhada', 'liquidada', 'paga', 'cancelada']

    @classmethod
    def label_for(cls, chave):
        if not chave:
            return ''
        obj = cls.objects.filter(chave=chave).only('nome').first()
        return obj.nome if obj else str(chave).replace('_', ' ').replace('-', ' ').title()

    @classmethod
    def badge_for(cls, chave):
        obj = cls.objects.filter(chave=chave).only('badge').first()
        return obj.badge if obj and obj.badge else 'bg-secondary'


class PdiPerspectiva(models.Model):
    nome   = models.CharField('Nome', max_length=200)
    codigo = models.CharField('Código', max_length=20, blank=True)
    ordem  = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Perspectiva PDI'
        verbose_name_plural = 'Perspectivas PDI'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}' if self.codigo else self.nome


class PdiObjetivoEstrategico(models.Model):
    perspectiva = models.ForeignKey(
        PdiPerspectiva, on_delete=models.CASCADE,
        related_name='objetivos', verbose_name='Perspectiva'
    )
    nome   = models.CharField('Nome', max_length=300)
    codigo = models.CharField('Código', max_length=20, blank=True)
    ordem  = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Objetivo Estratégico'
        verbose_name_plural = 'Objetivos Estratégicos'
        ordering = ['perspectiva', 'ordem', 'nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}' if self.codigo else self.nome


class PdiIndicador(models.Model):
    objetivo       = models.ForeignKey(
        PdiObjetivoEstrategico, on_delete=models.CASCADE,
        related_name='indicadores', verbose_name='Objetivo Estratégico'
    )
    nome           = models.CharField('Nome', max_length=300)
    codigo         = models.CharField('Código', max_length=20, blank=True)
    unidade_medida = models.CharField('Unidade de Medida', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Indicador PDI'
        verbose_name_plural = 'Indicadores PDI'
        ordering = ['objetivo', 'nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}' if self.codigo else self.nome


class PdiMeta(models.Model):
    indicador      = models.ForeignKey(
        PdiIndicador, on_delete=models.CASCADE,
        related_name='metas', verbose_name='Indicador'
    )
    ano            = models.PositiveIntegerField('Ano')
    valor_previsto = models.DecimalField('Valor Previsto', max_digits=12, decimal_places=2, null=True, blank=True)
    descricao      = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Meta PDI'
        verbose_name_plural = 'Metas PDI'
        ordering = ['indicador', 'ano']

    def __str__(self):
        return f'{self.indicador} / {self.ano}'


# ── Recurso Orçamentário ──────────────────────────────────────────────────────

class RecursoOrcamentario(models.Model):
    ano_fiscal        = models.PositiveIntegerField('Ano Fiscal')
    setor             = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True,
        related_name='recursos_orcamentarios', verbose_name='Setor'
    )
    origem_recurso    = models.CharField('Origem do Recurso', max_length=200)
    natureza          = models.CharField('Natureza do Recurso', max_length=100)
    rubrica           = models.CharField('Rubrica', max_length=120, blank=True)
    valor_orcamentario = models.DecimalField('Valor Orçamentário (R$)', max_digits=12, decimal_places=2)
    observacoes       = models.TextField('Observações', blank=True)
    criado_por        = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recursos_criados'
    )
    criado_em         = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Recurso Orçamentário'
        verbose_name_plural = 'Recursos Orçamentários'
        ordering = ['ano_fiscal', 'setor', 'natureza', 'rubrica']
        unique_together = [('ano_fiscal', 'setor', 'origem_recurso', 'natureza', 'rubrica')]

    def __str__(self):
        setor_str = str(self.setor) if self.setor else 'Sem setor'
        return f'{self.ano_fiscal} | {setor_str} | {self.origem_recurso} | {self.natureza}'

    @property
    def saldo_atual(self):
        entradas = self.transferencias_entrada.filter(
            status='realizada').aggregate(t=Sum('valor'))['t'] or 0
        saidas = self.transferencias_saida.filter(
            status='realizada').aggregate(t=Sum('valor'))['t'] or 0
        despesas = self.despesas.exclude(
            situacao__in=SituacaoDespesa.chaves_sem_impacto()).aggregate(t=Sum('valor_comprometido'))['t'] or 0
        return self.valor_orcamentario + entradas - saidas - despesas


# ── Transferência ─────────────────────────────────────────────────────────────

class Transferencia(models.Model):
    STATUS_CHOICES = [
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    origem        = models.ForeignKey(
        RecursoOrcamentario, on_delete=models.CASCADE,
        related_name='transferencias_saida', verbose_name='Origem'
    )
    destino       = models.ForeignKey(
        RecursoOrcamentario, on_delete=models.CASCADE,
        related_name='transferencias_entrada', verbose_name='Destino'
    )
    valor         = models.DecimalField('Valor (R$)', max_digits=12, decimal_places=2)
    descricao     = models.TextField('Justificativa')
    link_sipac    = models.URLField('Link do Processo SIPAC', max_length=500, blank=True)
    comprovante   = models.FileField(
        'Comprovante de Autorização',
        upload_to='transferencias/comprovantes/',
        blank=True, null=True,
    )
    data          = models.DateField('Data')
    status        = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='realizada')
    criada_por    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transferencias_criadas'
    )
    criada_em      = models.DateTimeField('Criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'Transferência'
        verbose_name_plural = 'Transferências'
        ordering = ['-criada_em']

    def __str__(self):
        return f'Transf. {self.origem} → {self.destino} (R$ {self.valor})'


# ── Despesa ───────────────────────────────────────────────────────────────────

class RegistroPrecoVigente(models.Model):
    ORIGEM_CHOICES = [
        ('rp', 'Módulo IRP'),
        ('sipac', 'SIPAC'),
    ]

    origem = models.CharField('Origem', max_length=20, choices=ORIGEM_CHOICES)
    pregao = models.ForeignKey(
        Pregao, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='registros_preco_orcamento', verbose_name='Pregão IRP'
    )
    numero_pregao = models.CharField('Pregão', max_length=80)
    processo_sipac = models.CharField('Processo SIPAC', max_length=80, blank=True)
    link_sipac = models.URLField('Link SIPAC', max_length=500, blank=True)
    objeto = models.TextField('Objeto', blank=True)
    data_homologacao = models.DateField('Data de Homologação', null=True, blank=True)
    validade = models.DateField('Validade', null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='registros_preco_importados'
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Registro de Preço Vigente'
        verbose_name_plural = 'Registros de Preço Vigentes'
        ordering = ['origem', 'numero_pregao']

    def __str__(self):
        return f'{self.numero_pregao} ({self.get_origem_display()})'

    @property
    def situacao_vigencia(self):
        from django.utils import timezone
        if not self.validade:
            return 'sem_validade'
        hoje = timezone.localdate()
        if self.validade < hoje:
            return 'vencido'
        if (self.validade - hoje).days <= 30:
            return 'a_vencer'
        return 'vigente'


class RegistroPrecoItem(models.Model):
    registro = models.ForeignKey(
        RegistroPrecoVigente, on_delete=models.CASCADE,
        related_name='itens', verbose_name='Registro de Preço'
    )
    pregao_item = models.OneToOneField(
        PregaoItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='registro_preco_orcamento', verbose_name='Item IRP'
    )
    chave_importacao = models.CharField('Chave de Importação', max_length=100, unique=True)
    numero_item = models.CharField('Item', max_length=50)
    material_licitado = models.TextField('Material Licitado', blank=True)
    material = models.TextField('Material')
    rubrica = models.CharField('Rubrica', max_length=120, blank=True)
    unidade = models.CharField('Unidade', max_length=60, blank=True)
    quantidade_empenhada = models.DecimalField('Qtd. Emp.', max_digits=12, decimal_places=3, null=True, blank=True)
    marca = models.CharField('Marca', max_length=160, blank=True)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2, null=True, blank=True)
    saldo = models.DecimalField('Saldo UFPB', max_digits=12, decimal_places=3, null=True, blank=True)
    saldo_unidade = models.CharField('Saldo Unidade', max_length=60, blank=True)
    validade = models.DateField('Validade', null=True, blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Item de Registro de Preço'
        verbose_name_plural = 'Itens de Registro de Preço'
        ordering = ['registro__numero_pregao', 'numero_item']

    def __str__(self):
        return f'{self.registro.numero_pregao} | Item {self.numero_item}'

    @property
    def validade_efetiva(self):
        return self.validade or self.registro.validade

    @property
    def situacao_vigencia(self):
        from django.utils import timezone
        validade = self.validade_efetiva
        if not validade:
            return 'sem_validade'
        hoje = timezone.localdate()
        if validade < hoje:
            return 'vencido'
        if (validade - hoje).days <= 30:
            return 'a_vencer'
        return 'vigente'


class Despesa(models.Model):
    data_despesa      = models.DateField('Data da Despesa')
    requisicao        = models.CharField('Requisição', max_length=100, blank=True)
    nota_empenho      = models.CharField('Nota de Empenho', max_length=100, blank=True)
    pregao_ref        = models.CharField('Pregão (externo)', max_length=100, blank=True)
    pregao            = models.ForeignKey(
        Pregao, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas_orcamento', verbose_name='Licitação (IRP)'
    )
    registro_preco_item = models.ForeignKey(
        RegistroPrecoItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas', verbose_name='Registro de Preço Vigente'
    )
    discriminacao     = models.TextField('Discriminação do Item')
    quantidade        = models.DecimalField('Qtde', max_digits=12, decimal_places=3)
    valor_unitario    = models.DecimalField('Valor Unitário (R$)', max_digits=12, decimal_places=2)
    valor_comprometido = models.DecimalField('Valor Comprometido (R$)', max_digits=12, decimal_places=2)
    rubrica           = models.CharField('Rubrica', max_length=120, blank=True)
    setor             = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas_orcamento', verbose_name='Setor'
    )
    recurso           = models.ForeignKey(
        RecursoOrcamentario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas', verbose_name='Recurso Orçamentário'
    )
    situacao          = models.CharField('Situação', max_length=50, default='empenhada')
    observacao        = models.TextField('Observação', blank=True)
    natureza          = models.CharField('Natureza do Recurso', max_length=100)
    categoria_material = models.CharField('Categoria do Material', max_length=100, blank=True)

    perspectiva_pdi   = models.ForeignKey(
        PdiPerspectiva, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas', verbose_name='Perspectiva PDI'
    )
    objetivo_pdi      = models.ForeignKey(
        PdiObjetivoEstrategico, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas', verbose_name='Objetivo Estratégico PDI'
    )
    indicador_pdi     = models.ForeignKey(
        PdiIndicador, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas', verbose_name='Indicador PDI'
    )
    pdi_vinculos      = models.JSONField('Vínculos PDI', default=list, blank=True)

    criada_por        = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despesas_criadas'
    )
    criada_em         = models.DateTimeField('Criada em', auto_now_add=True)
    atualizada_em     = models.DateTimeField('Atualizada em', auto_now=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa']

    def __str__(self):
        return f'{self.data_despesa} | {self.discriminacao[:60]}'

    def get_situacao_display(self):
        return SituacaoDespesa.label_for(self.situacao)

    @property
    def situacao_badge_class(self):
        return SituacaoDespesa.badge_for(self.situacao)
