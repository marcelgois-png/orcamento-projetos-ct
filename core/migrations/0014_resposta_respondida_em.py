from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_resposta_observacao_geral'),
    ]

    operations = [
        migrations.AddField(
            model_name='resposta',
            name='respondida_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Respondida em'),
        ),
    ]
