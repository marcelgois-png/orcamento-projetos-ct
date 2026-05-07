from django.db import migrations, models
import django.db.models.deletion


SEED = [
    # (codigo, nome, natureza_nome, ordem)
    ('449052', 'Permanente',                         'Capital',  1),
    ('339014', 'Diárias',                            'Custeio',  2),
    ('339018', 'Auxílio Financeiro ao Estudante',    'Custeio',  3),
    ('339030', 'Material de Consumo',                'Custeio',  4),
    ('339033', 'Passagens e Locomoção',              'Custeio',  5),
    ('339036', 'Estagiários',                        'Custeio',  6),
    ('339036', 'Serviços Pessoa Física',             'Custeio',  7),
    ('339039', 'Serviços Pessoa Jurídica',           'Custeio',  8),
    ('339040', 'Serviços PJ | TIC',                  'Custeio',  9),
]


def seed_rubricas(apps, schema_editor):
    Rubrica         = apps.get_model('orcamento', 'Rubrica')
    NaturezaRecurso = apps.get_model('orcamento', 'NaturezaRecurso')

    for codigo, nome, nat_nome, ordem in SEED:
        nat = NaturezaRecurso.objects.filter(nome__iexact=nat_nome).first()
        Rubrica.objects.create(
            codigo=codigo, nome=nome, natureza=nat, ordem=ordem, ativo=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0002_naturezarecurso'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rubrica',
            fields=[
                ('id',      models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo',  models.CharField(max_length=20, verbose_name='Código')),
                ('nome',    models.CharField(max_length=200, verbose_name='Nome')),
                ('natureza', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='rubricas',
                    to='orcamento.naturezarecurso',
                    verbose_name='Natureza do Recurso',
                )),
                ('ordem',   models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('ativo',   models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Rubrica',
                'verbose_name_plural': 'Rubricas',
                'ordering': ['ordem', 'codigo', 'nome'],
            },
        ),
        migrations.RunPython(seed_rubricas, migrations.RunPython.noop),
    ]
