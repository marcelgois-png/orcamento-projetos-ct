from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_resposta_respondida_em'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pregao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(blank=True, max_length=50, verbose_name='Pregão Eletrônico')),
                ('link_acompanhamento', models.URLField(blank=True, max_length=500, verbose_name='Link de Acompanhamento')),
                ('status', models.CharField(choices=[('em_licitacao', 'Em licitação'), ('homologado', 'Homologado')], default='em_licitacao', max_length=20, verbose_name='Status do Pregão')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('irp', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pregao', to='core.irp')),
            ],
            options={
                'verbose_name': 'Pregão',
                'verbose_name_plural': 'Pregões',
                'ordering': ['-irp__criada_em'],
            },
        ),
        migrations.CreateModel(
            name='PregaoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('situacao', models.CharField(choices=[('em_licitacao', 'Em licitação'), ('licitado', 'Licitado'), ('nao_licitado', 'Não Licitado')], default='em_licitacao', max_length=20, verbose_name='Situação na Licitação')),
                ('preco_licitado', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Licitado')),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pregao_item', to='core.item')),
                ('pregao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_pregao', to='core.pregao')),
            ],
            options={
                'verbose_name': 'Item do Pregão',
                'verbose_name_plural': 'Itens do Pregão',
                'unique_together': {('pregao', 'item')},
            },
        ),
    ]
