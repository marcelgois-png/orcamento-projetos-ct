from django.db import migrations, models


SEED = [
    'Arrecadação Própria',
    'Discricionário',
    'Projeto Aerojampa',
    'Projeto Baja',
    'Projeto Fórmula',
    'Projeto Motostudent',
    'TED',
    'Transferência Interna',
]


def seed_origens(apps, schema_editor):
    OrigemRecurso = apps.get_model('orcamento', 'OrigemRecurso')
    for i, nome in enumerate(SEED, start=1):
        OrigemRecurso.objects.create(nome=nome, ordem=i, ativo=True)


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0003_rubrica'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrigemRecurso',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome',  models.CharField(max_length=200, unique=True, verbose_name='Nome')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Origem do Recurso',
                'verbose_name_plural': 'Origens do Recurso',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.RunPython(seed_origens, migrations.RunPython.noop),
    ]
