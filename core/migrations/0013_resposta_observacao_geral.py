from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_homologacaosetoritem_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='resposta',
            name='observacao_geral',
            field=models.TextField(blank=True, verbose_name='Observações Adicionais'),
        ),
    ]
