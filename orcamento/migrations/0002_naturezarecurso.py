from django.db import migrations, models


def seed_naturezas(apps, schema_editor):
    NaturezaRecurso = apps.get_model('orcamento', 'NaturezaRecurso')
    NaturezaRecurso.objects.bulk_create([
        NaturezaRecurso(nome='Custeio', ordem=1, ativo=True),
        NaturezaRecurso(nome='Capital', ordem=2, ativo=True),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NaturezaRecurso',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome',  models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Natureza do Recurso',
                'verbose_name_plural': 'Naturezas do Recurso',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.RunPython(seed_naturezas, migrations.RunPython.noop),
    ]
