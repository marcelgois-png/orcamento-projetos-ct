from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


TIPO_SETOR_CHOICES = [
    ('centro',         'Centro'),
    ('direcao',        'Direção de Centro'),
    ('administrativo', 'Setor Administrativo'),
    ('departamento',   'Departamento'),
    ('coordenacao_g',  'Coordenação de Curso'),
    ('coordenacao_pg', 'Pós-Graduação'),
    ('laboratorio',    'Laboratório'),
    ('secretaria',     'Secretaria de Departamento'),
]

TIPO_SETOR_BADGE = {
    'centro':         ('secondary', 'CT'),
    'direcao':        ('dark',      'DC'),
    'administrativo': ('info',      'ADM'),
    'departamento':   ('primary',   'DEPTO'),
    'coordenacao_g':  ('success',   'COORD-G'),
    'coordenacao_pg': ('warning',   'PPG'),
    'laboratorio':    ('danger',    'LAB'),
    'secretaria':     ('secondary', 'SEC'),
}

# Perfis compatíveis por tipo de setor
# gestor_irp é irrestrito (pode atuar em qualquer setor)
PERFIL_POR_TIPO_SETOR = {
    'centro':         ['admin', 'gestor_irp', 'diretor_centro'],
    'direcao':        ['admin', 'gestor_irp', 'diretor_centro'],
    'departamento':   ['admin', 'gestor_irp', 'aprovador_setor'],
    'coordenacao_g':  ['admin', 'gestor_irp', 'aprovador_setor', 'respondente'],
    'coordenacao_pg': ['admin', 'gestor_irp', 'aprovador_setor', 'respondente'],
    'administrativo': ['admin', 'gestor_irp', 'aprovador_setor', 'respondente'],
    'laboratorio':    ['admin', 'gestor_irp', 'respondente'],
    'secretaria':     ['admin', 'gestor_irp', 'respondente'],
}


class Setor(models.Model):
    codigo = models.CharField('Código SIPAC', max_length=30, unique=True)
    nome = models.CharField('Nome', max_length=255)
    sigla = models.CharField('Sigla', max_length=30, blank=True)
    pai = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='subsetores',
        verbose_name='Setor Pai'
    )
    tipo = models.CharField(
        'Tipo', max_length=20,
        choices=TIPO_SETOR_CHOICES,
        default='laboratorio',
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['codigo']

    def __str__(self):
        if self.sigla:
            return f'{self.sigla} - {self.nome}'
        return self.nome

    def nome_exibicao(self):
        """Nome curto para exibição em seletores."""
        return f'{self.codigo} - {self.nome}'

    @property
    def tipo_badge(self):
        return TIPO_SETOR_BADGE.get(self.tipo, ('secondary', self.tipo))


RUBRICA_CHOICES = [
    ('diarias',             '339014 - Diárias'),
    ('aux_financeiro',      '339018 - Auxílio Financeiro ao Estudante'),
    ('material_consumo',    '339030 - Material de Consumo'),
    ('passagens',           '339033 - Passagens e Locomoção'),
    ('estagiarios',         '339036 - Estagiários'),
    ('servico_pf',          '339036 - Serviços Pessoa Física'),
    ('servico_pj',          '339039 - Serviços Pessoa Jurídica'),
    ('servico_pj_tic',      '339040 - Serviços PJ | TIC'),
    ('material_permanente', '449052 - Material Permanente'),
]

PERFIL_TIPO_CHOICES = [
    ('admin',              'Administrador do Sistema'),
    ('gestor_irp',         'Assessor de Planejamento'),
    ('diretor_centro',     'Diretor de Centro'),
    ('aprovador_setor',    'Chefia Setorial'),
    ('respondente',        'Respondente'),
    ('gestor_financeiro',  'Gestor Financeiro'),
    ('ordenador_despesa',  'Ordenador de Despesa'),
]

PERFIL_BADGE_CSS = {
    'admin':             'badge-perfil-admin',
    'gestor_irp':        'badge-perfil-gestor',
    'diretor_centro':    'badge-perfil-diretor',
    'aprovador_setor':   'badge-perfil-aprov-setor',
    'respondente':       'badge-perfil-respondente',
    'gestor_financeiro': 'badge-perfil-financeiro',
    'ordenador_despesa': 'badge-perfil-ordenador',
}


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome_completo = models.CharField('Nome Completo', max_length=255)
    matricula = models.CharField('Matrícula', max_length=20, blank=True)
    setor = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True,
        related_name='membros',
        verbose_name='Setor'
    )
    perfil_tipo = models.CharField(
        'Perfil', max_length=20,
        choices=PERFIL_TIPO_CHOICES,
        default='respondente'
    )
    foto = models.FileField(
        'Foto', upload_to='fotos_usuarios/',
        null=True, blank=True,
        help_text='Imagem JPG, PNG ou GIF. Máximo 10 MB.'
    )

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return self.nome_completo or self.usuario.username

    # ── Propriedades de conveniência ─────────────────────────────────────────
    @property
    def is_gestor(self):
        """True para perfis com acesso à gestão do módulo IRP."""
        return self.perfil_tipo in ('admin', 'gestor_irp', 'diretor_centro')

    @property
    def is_financeiro(self):
        """True para perfis com acesso ao módulo de Execução Orçamentária."""
        return self.perfil_tipo in ('admin', 'gestor_financeiro', 'ordenador_despesa')

    @property
    def modulos_disponiveis(self):
        """Lista de módulos acessíveis para a tela de seleção."""
        modulos = []
        if self.perfil_tipo in ('admin', 'gestor_irp', 'diretor_centro',
                                'aprovador_setor', 'respondente'):
            modulos.append('irp')
        if self.perfil_tipo in ('admin', 'gestor_financeiro', 'ordenador_despesa'):
            modulos.append('orcamento')
        return modulos

    @property
    def pode_homologar(self):
        return self.perfil_tipo in ('admin', 'aprovador_setor', 'diretor_centro')


    @property
    def perfil_badge_css(self):
        return PERFIL_BADGE_CSS.get(self.perfil_tipo, '')

    def get_setor_raiz(self):
        """Retorna o setor de referência para homologação.
        DC homologa os setores de bypass (administrativo e coordenações).
        Departamento homologa seus laboratórios e secretarias.
        """
        s = self.setor
        if s is None:
            return None
        # DC homologa os setores de bypass (administrativo e coordenações)
        if s.tipo == 'direcao':
            return s
        # Departamento homologa seus laboratórios e secretarias
        if s.tipo == 'departamento':
            return s
        # Laboratórios e secretarias são homologados pelo departamento pai
        if s.tipo in ('laboratorio', 'secretaria'):
            if s.pai and s.pai.tipo == 'departamento':
                return s.pai
            return s
        # Demais (administrativo, coordenações, centro) não têm papel de homologação
        return None


class IRP(models.Model):
    titulo = models.CharField('Título', max_length=255)
    descricao = models.TextField('Descrição / Instruções', blank=True)
    prazo = models.DateTimeField('Prazo de Respostas')
    prazo_homologacao = models.DateTimeField('Prazo de Homologação', null=True, blank=True)
    criada_em = models.DateTimeField('Criada em', auto_now_add=True)
    atualizada_em = models.DateTimeField('Atualizada em', auto_now=True)
    criada_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='irps_criadas'
    )
    liberada = models.BooleanField('Liberada para respostas', default=False)

    class Meta:
        verbose_name = 'IRP'
        verbose_name_plural = 'IRPs'
        ordering = ['-criada_em']

    def __str__(self):
        return self.titulo

    @property
    def esta_aberta(self):
        return self.liberada and self.prazo > timezone.now()

    @property
    def fase_atual(self):
        """Retorna a fase atual da IRP.
        Fluxo: em_cadastro → respostas → homologacao → encerrada.
        """
        if not self.liberada:
            return 'em_cadastro'
        agora = timezone.now()
        if self.prazo > agora:
            return 'respostas'


        respostas = self.respostas.filter(respondida_em__isnull=False).select_related('setor', 'setor__pai')

        setores_raiz_exigidos = set()
        needs_dc_hom = False

        for r in respostas:
            s = r.setor
            if not s:
                continue
            if s.tipo in ('laboratorio', 'secretaria'):
                if s.pai and s.pai.tipo == 'departamento':
                    setores_raiz_exigidos.add(s.pai_id)
                else:
                    setores_raiz_exigidos.add(s.id)
            elif s.tipo in ('administrativo', 'coordenacao_g', 'coordenacao_pg'):
                needs_dc_hom = True

        if needs_dc_hom:
            dc = Setor.objects.filter(tipo='direcao').first()
            if dc:
                setores_raiz_exigidos.add(dc.id)

        # Se não há respostas que exijam homologação:
        if not setores_raiz_exigidos:
            # Se ainda estamos no prazo de homologação (mesmo sem respostas), mantemos em 'homologacao'
            if self.prazo_homologacao and self.prazo_homologacao > agora:
                return 'homologacao'
            return 'encerrada'

        # Busca homologações já salvas (homologada ou rejeitada)
        homologacoes_salvas = self.homologacoes.filter(
            setor_raiz_id__in=setores_raiz_exigidos,
            status__in=['homologada', 'rejeitada']
        ).values_list('setor_raiz_id', flat=True)

        # Se todos os setores exigidos já homologaram
        if set(homologacoes_salvas) == setores_raiz_exigidos:
            return 'encerrada'

        # Se o prazo de homologação venceu, também consideramos encerrada (mesmo se pendente)
        if self.prazo_homologacao and agora > self.prazo_homologacao:
             return 'encerrada'

        return 'homologacao'

    @property
    def total_itens(self):
        return self.itens.count()

    # itens_ativos e total_respostas: suportam tanto @property quanto annotation ORM.
    # O setter permite que Django aplique .annotate() sem AttributeError.
    @property
    def itens_ativos(self):
        return getattr(self, '_itens_ativos', None) if hasattr(self, '_itens_ativos') else self.itens.filter(ativo=True).count()

    @itens_ativos.setter
    def itens_ativos(self, value):
        self._itens_ativos = value

    @property
    def total_respostas(self):
        return getattr(self, '_total_respostas', None) if hasattr(self, '_total_respostas') else self.respostas.filter(respondida_em__isnull=False).count()

    @total_respostas.setter
    def total_respostas(self, value):
        self._total_respostas = value


class Item(models.Model):
    RUBRICA_CHOICES = RUBRICA_CHOICES  # definido no nível do módulo

    irp = models.ForeignKey(IRP, on_delete=models.CASCADE, related_name='itens')
    numero = models.PositiveIntegerField('Nº')
    unidade = models.CharField('Unidade', max_length=50)
    rubrica = models.CharField('Rubrica', max_length=120, choices=RUBRICA_CHOICES, blank=True)
    numero_dfd = models.CharField('N° DFD', max_length=50, blank=True, default='')
    codigo_catmat = models.CharField('Código CATMAT', max_length=20, blank=True, default='')
    descricao = models.TextField('Descrição do Material')
    preco_estimado = models.DecimalField('Valor de Referência (R$)', max_digits=12, decimal_places=2)
    quantidade_total = models.DecimalField('Quant. Total', max_digits=12, decimal_places=3, null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['numero']
        unique_together = ['irp', 'numero']

    def __str__(self):
        return f'Item {self.numero} - {self.descricao[:60]}'


class Resposta(models.Model):
    irp = models.ForeignKey(IRP, on_delete=models.CASCADE, related_name='respostas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respostas')
    setor = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True,
        related_name='respostas_setor',
        verbose_name='Setor'
    )
    respondida_em = models.DateTimeField('Respondida em', null=True, blank=True)
    atualizada_em = models.DateTimeField('Última atualização', auto_now=True)
    observacao_geral = models.TextField('Observações Adicionais', blank=True)

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'
        unique_together = ['irp', 'usuario']

    def __str__(self):
        return f'{self.usuario} → {self.irp}'

    @property
    def total_valor(self):
        total = sum(
            (ri.quantidade or 0) * ri.item.preco_estimado
            for ri in self.itens_resposta.select_related('item').all()
            if ri.quantidade
        )
        return total

    @property
    def total_itens_intencionados(self):
        return self.itens_resposta.filter(quantidade__gt=0).count()

    @property
    def foi_editada(self):
        """Retorna True se a resposta foi editada após a submissão inicial."""
        if not self.respondida_em:
            return False
        # Consideramos editada se a última atualização for pelo menos 2 segundos após a inicial
        return (self.atualizada_em - self.respondida_em).total_seconds() > 2


class RespostaItem(models.Model):
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE, related_name='itens_resposta')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='respostas_item')
    quantidade = models.DecimalField(
        'Quantidade', max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Item da Resposta'
        verbose_name_plural = 'Itens da Resposta'
        unique_together = ['resposta', 'item']

    def __str__(self):
        return f'{self.resposta} - Item {self.item.numero}'

    @property
    def valor_total(self):
        if self.quantidade:
            return self.quantidade * self.item.preco_estimado
        return None


# ---------------------------------------------------------------------------
# Homologação por Setor Raiz
# ---------------------------------------------------------------------------

class HomologacaoSetor(models.Model):
    STATUS_CHOICES = [
        ('pendente',    'Pendente'),
        ('homologada',  'Homologada'),
        ('rejeitada',   'Rejeitada'),
    ]
    irp = models.ForeignKey(
        IRP, on_delete=models.CASCADE, related_name='homologacoes'
    )
    setor_raiz = models.ForeignKey(
        Setor, on_delete=models.CASCADE, related_name='homologacoes'
    )
    homologado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='homologacoes_realizadas'
    )
    homologado_em = models.DateTimeField(null=True, blank=True)
    observacao = models.TextField('Observação', blank=True)
    status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES, default='pendente'
    )

    class Meta:
        verbose_name = 'Homologação de Setor'
        verbose_name_plural = 'Homologações de Setor'
        unique_together = ['irp', 'setor_raiz']
        ordering = ['setor_raiz__nome']

    def __str__(self):
        return f'{self.irp} | {self.setor_raiz} [{self.status}]'




# ---------------------------------------------------------------------------
# Ajuste item a item na Homologação de Setor
# ---------------------------------------------------------------------------

class HomologacaoSetorItem(models.Model):
    homologacao = models.ForeignKey(
        HomologacaoSetor, on_delete=models.CASCADE,
        related_name='itens_homologados'
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        related_name='homologacoes_setor'
    )
    quantidade_aprovada = models.DecimalField(
        'Qtd. Aprovada', max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Item Homologado'
        verbose_name_plural = 'Itens Homologados'
        unique_together = ['homologacao', 'item']

    def __str__(self):
        return f'{self.homologacao} – Item {self.item.numero}'


# ---------------------------------------------------------------------------
# Pregão (Licitação)
# ---------------------------------------------------------------------------

class Pregao(models.Model):
    STATUS_CHOICES = [
        ('em_preparacao', 'Em preparação'),
        ('em_licitacao',  'Em licitação'),
        ('homologado',    'Homologado'),
    ]
    irp = models.OneToOneField(
        IRP, on_delete=models.CASCADE, related_name='pregao'
    )
    numero = models.CharField('Pregão Eletrônico', max_length=50, blank=True)
    link_acompanhamento = models.URLField('Link de Acompanhamento', max_length=500, blank=True)
    data_publicacao = models.DateField('Data da Publicação', null=True, blank=True)
    status = models.CharField(
        'Status do Pregão', max_length=20,
        choices=STATUS_CHOICES, default='em_preparacao'
    )
    data_homologacao = models.DateField('Data da Homologação', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pregão'
        verbose_name_plural = 'Pregões'
        ordering = ['-irp__criada_em']

    def __str__(self):
        return f'Pregão {self.numero or "s/n"} – {self.irp}'


class PregaoItem(models.Model):
    SITUACAO_CHOICES = [
        ('em_preparacao', 'Em preparação'),
        ('em_licitacao',  'Em licitação'),
        ('licitado',      'Licitado'),
        ('nao_licitado',  'Não Licitado'),
    ]
    pregao = models.ForeignKey(
        Pregao, on_delete=models.CASCADE, related_name='itens_pregao'
    )
    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name='pregao_item'
    )
    situacao = models.CharField(
        'Situação na Licitação', max_length=20,
        choices=SITUACAO_CHOICES, default='em_licitacao'
    )
    preco_licitado = models.DecimalField(
        'Preço Licitado', max_digits=12, decimal_places=2,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Item do Pregão'
        verbose_name_plural = 'Itens do Pregão'
        unique_together = ['pregao', 'item']

    def __str__(self):
        return f'Item {self.item.numero} – {self.pregao}'
