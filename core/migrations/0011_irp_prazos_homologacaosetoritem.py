from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_perfilusuario_is_gestor_and_more'),
    ]

    operations = [
        # 1. Adiciona prazo_homologacao e prazo_aprovacao_ct à IRP
        migrations.AddField(
            model_name='irp',
            name='prazo_homologacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Prazo de Homologação'),
        ),
        migrations.AddField(
            model_name='irp',
            name='prazo_aprovacao_ct',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Prazo de Aprovação CT'),
        ),
        # 2. Renomeia label do campo prazo existente (só metadata, sem DDL)
        migrations.AlterField(
            model_name='irp',
            name='prazo',
            field=models.DateTimeField(verbose_name='Prazo de Respostas'),
        ),
        # 3. Cria HomologacaoSetorItem
        migrations.CreateModel(
            name='HomologacaoSetorItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_aprovada', models.DecimalField(
                    blank=True, decimal_places=2, max_digits=10,
                    null=True, verbose_name='Qtd. Aprovada',
                )),
                ('observacao', models.TextField(blank=True, verbose_name='Observação')),
                ('homologacao', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='itens_homologados',
                    to='core.homologacaosetor',
                )),
                ('item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='homologacoes_setor',
                    to='core.item',
                )),
            ],
            options={
                'verbose_name': 'Item Homologado',
                'verbose_name_plural': 'Itens Homologados',
                'unique_together': {('homologacao', 'item')},
            },
        ),
    ]
