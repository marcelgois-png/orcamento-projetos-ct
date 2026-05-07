from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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

NATUREZA_CHOICES = [
    ('custeio', 'Custeio'),
    ('capital',  'Capital'),
]


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0026_add_perfil_financeiro'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── PDI ──────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='PdiPerspectiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome',   models.CharField(max_length=200, verbose_name='Nome')),
                ('codigo', models.CharField(blank=True, max_length=20, verbose_name='Código')),
                ('ordem',  models.PositiveIntegerField(default=0, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Perspectiva PDI',
                'verbose_name_plural': 'Perspectivas PDI',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='PdiObjetivoEstrategico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome',   models.CharField(max_length=300, verbose_name='Nome')),
                ('codigo', models.CharField(blank=True, max_length=20, verbose_name='Código')),
                ('ordem',  models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('perspectiva', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='objetivos',
                    to='orcamento.pdiperspectiva',
                    verbose_name='Perspectiva',
                )),
            ],
            options={
                'verbose_name': 'Objetivo Estratégico',
                'verbose_name_plural': 'Objetivos Estratégicos',
                'ordering': ['perspectiva', 'ordem', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='PdiIndicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome',           models.CharField(max_length=300, verbose_name='Nome')),
                ('codigo',         models.CharField(blank=True, max_length=20, verbose_name='Código')),
                ('unidade_medida', models.CharField(blank=True, max_length=50, verbose_name='Unidade de Medida')),
                ('objetivo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='indicadores',
                    to='orcamento.PdiObjetivoEstrategico',
                    verbose_name='Objetivo Estratégico',
                )),
            ],
            options={
                'verbose_name': 'Indicador PDI',
                'verbose_name_plural': 'Indicadores PDI',
                'ordering': ['objetivo', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='PdiMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano',            models.PositiveIntegerField(verbose_name='Ano')),
                ('valor_previsto', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Valor Previsto')),
                ('descricao',      models.TextField(blank=True, verbose_name='Descrição')),
                ('indicador', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='metas',
                    to='orcamento.pdiindicador',
                    verbose_name='Indicador',
                )),
            ],
            options={
                'verbose_name': 'Meta PDI',
                'verbose_name_plural': 'Metas PDI',
                'ordering': ['indicador', 'ano'],
            },
        ),

        # ── RecursoOrcamentario ───────────────────────────────────────────────
        migrations.CreateModel(
            name='RecursoOrcamentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano_fiscal',         models.PositiveIntegerField(verbose_name='Ano Fiscal')),
                ('origem_recurso',     models.CharField(max_length=200, verbose_name='Origem do Recurso')),
                ('natureza',           models.CharField(choices=NATUREZA_CHOICES, max_length=10, verbose_name='Natureza do Recurso')),
                ('rubrica',            models.CharField(blank=True, choices=RUBRICA_CHOICES, max_length=30, verbose_name='Rubrica')),
                ('valor_orcamentario', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor Orçamentário (R$)')),
                ('observacoes',        models.TextField(blank=True, verbose_name='Observações')),
                ('criado_em',          models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('criado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='recursos_criados',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('setor', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='recursos_orcamentarios',
                    to='core.setor',
                    verbose_name='Setor',
                )),
            ],
            options={
                'verbose_name': 'Recurso Orçamentário',
                'verbose_name_plural': 'Recursos Orçamentários',
                'ordering': ['ano_fiscal', 'setor', 'natureza', 'rubrica'],
                'unique_together': {('ano_fiscal', 'setor', 'origem_recurso', 'natureza', 'rubrica')},
            },
        ),

        # ── Transferencia ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Transferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor',         models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor (R$)')),
                ('descricao',     models.TextField(verbose_name='Justificativa')),
                ('data',          models.DateField(verbose_name='Data')),
                ('status',        models.CharField(
                    choices=[('pendente', 'Pendente'), ('autorizada', 'Autorizada'), ('cancelada', 'Cancelada')],
                    default='pendente', max_length=20, verbose_name='Status',
                )),
                ('autorizada_em', models.DateTimeField(blank=True, null=True, verbose_name='Autorizada em')),
                ('criada_em',     models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('autorizada_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transferencias_autorizadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('criada_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transferencias_criadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('destino', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='transferencias_entrada',
                    to='orcamento.recursoorcamentario',
                    verbose_name='Destino',
                )),
                ('origem', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='transferencias_saida',
                    to='orcamento.recursoorcamentario',
                    verbose_name='Origem',
                )),
            ],
            options={
                'verbose_name': 'Transferência',
                'verbose_name_plural': 'Transferências',
                'ordering': ['-criada_em'],
            },
        ),

        # ── Despesa ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_despesa',       models.DateField(verbose_name='Data da Despesa')),
                ('requisicao',         models.CharField(blank=True, max_length=100, verbose_name='Requisição')),
                ('nota_empenho',       models.CharField(blank=True, max_length=100, verbose_name='Nota de Empenho')),
                ('pregao_ref',         models.CharField(blank=True, max_length=100, verbose_name='Pregão (externo)')),
                ('discriminacao',      models.TextField(verbose_name='Discriminação do Item')),
                ('quantidade',         models.DecimalField(decimal_places=3, max_digits=12, verbose_name='Qtde')),
                ('valor_unitario',     models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor Unitário (R$)')),
                ('valor_comprometido', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor Comprometido (R$)')),
                ('rubrica',            models.CharField(blank=True, choices=RUBRICA_CHOICES, max_length=30, verbose_name='Rubrica')),
                ('situacao',           models.CharField(
                    choices=[('empenhada', 'Empenhada'), ('liquidada', 'Liquidada'), ('paga', 'Paga'), ('cancelada', 'Cancelada')],
                    default='empenhada', max_length=20, verbose_name='Situação',
                )),
                ('observacao',         models.TextField(blank=True, verbose_name='Observação')),
                ('natureza',           models.CharField(choices=NATUREZA_CHOICES, max_length=10, verbose_name='Natureza do Recurso')),
                ('categoria_material', models.CharField(blank=True, max_length=100, verbose_name='Categoria do Material')),
                ('criada_em',          models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('atualizada_em',      models.DateTimeField(auto_now=True, verbose_name='Atualizada em')),
                ('criada_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas_criadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('indicador_pdi', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas',
                    to='orcamento.pdiindicador',
                    verbose_name='Indicador PDI',
                )),
                ('objetivo_pdi', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas',
                    to='orcamento.PdiObjetivoEstrategico',
                    verbose_name='Objetivo Estratégico PDI',
                )),
                ('perspectiva_pdi', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas',
                    to='orcamento.pdiperspectiva',
                    verbose_name='Perspectiva PDI',
                )),
                ('pregao', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas_orcamento',
                    to='core.pregao',
                    verbose_name='Licitação (IRP)',
                )),
                ('recurso', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas',
                    to='orcamento.recursoorcamentario',
                    verbose_name='Recurso Orçamentário',
                )),
                ('setor', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='despesas_orcamento',
                    to='core.setor',
                    verbose_name='Setor',
                )),
            ],
            options={
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Despesas',
                'ordering': ['-data_despesa'],
            },
        ),
    ]
