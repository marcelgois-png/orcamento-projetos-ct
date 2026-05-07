from django.db import migrations, models


def seed_situacoes(apps, schema_editor):
    SituacaoDespesa = apps.get_model('orcamento', 'SituacaoDespesa')
    dados = [
        ('empenhada', 'Empenhada', 1, True, 'bg-warning text-dark'),
        ('liquidada', 'Liquidada', 2, True, 'bg-primary'),
        ('paga', 'Paga', 3, True, 'bg-success'),
        ('cancelada', 'Cancelada', 4, False, 'bg-secondary'),
    ]
    for chave, nome, ordem, impacta_saldo, badge in dados:
        SituacaoDespesa.objects.update_or_create(
            chave=chave,
            defaults={
                'nome': nome,
                'ordem': ordem,
                'ativo': True,
                'impacta_saldo': impacta_saldo,
                'badge': badge,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0014_registroprecoitem_material_licitado'),
    ]

    operations = [
        migrations.CreateModel(
            name='SituacaoDespesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('chave', models.SlugField(blank=True, max_length=50, unique=True, verbose_name='Chave')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('impacta_saldo', models.BooleanField(default=True, verbose_name='Deduz do saldo')),
                ('badge', models.CharField(blank=True, default='bg-secondary', max_length=40, verbose_name='Classe visual')),
            ],
            options={
                'verbose_name': 'Situação da Despesa',
                'verbose_name_plural': 'Situações da Despesa',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.AlterField(
            model_name='despesa',
            name='situacao',
            field=models.CharField(default='empenhada', max_length=50, verbose_name='Situação'),
        ),
        migrations.RunPython(seed_situacoes, migrations.RunPython.noop),
    ]
