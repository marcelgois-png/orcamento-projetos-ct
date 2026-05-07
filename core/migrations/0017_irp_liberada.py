from django.db import migrations, models


def liberar_irps_existentes(apps, schema_editor):
    """IRPs já abertas mantêm liberada=True para não quebrar o fluxo existente."""
    IRP = apps.get_model('core', 'IRP')
    IRP.objects.filter(status='aberta').update(liberada=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_item_rubrica'),
    ]

    operations = [
        migrations.AddField(
            model_name='irp',
            name='liberada',
            field=models.BooleanField(default=False, verbose_name='Liberada para respostas'),
        ),
        migrations.RunPython(liberar_irps_existentes, migrations.RunPython.noop),
    ]
