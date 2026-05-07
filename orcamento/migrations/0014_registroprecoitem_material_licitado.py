from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0013_alter_registroprecoitem_saldo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registroprecoitem',
            name='material_licitado',
            field=models.TextField('Material Licitado', blank=True),
        ),
    ]
