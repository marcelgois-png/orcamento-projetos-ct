from django.db import migrations


def autorizada_para_realizada(apps, schema_editor):
    Transferencia = apps.get_model('orcamento', 'Transferencia')
    Transferencia.objects.filter(status='autorizada').update(status='realizada')


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0006_transferencia_comprovante_transferencia_link_sipac'),
    ]

    operations = [
        # 1. Converter dados existentes antes de mudar as choices
        migrations.RunPython(autorizada_para_realizada, migrations.RunPython.noop),

        # 2. Atualizar choices e default no campo status
        migrations.AlterField(
            model_name='transferencia',
            name='status',
            field=__import__('django.db.models', fromlist=['CharField']).CharField(
                choices=[('realizada', 'Realizada'), ('cancelada', 'Cancelada')],
                default='realizada',
                max_length=20,
                verbose_name='Status',
            ),
        ),
    ]
