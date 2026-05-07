from django.db import migrations, models
from django.utils import timezone


def efetivar_transferencias_pendentes(apps, schema_editor):
    Transferencia = apps.get_model('orcamento', 'Transferencia')
    for transferencia in Transferencia.objects.filter(status='pendente'):
        transferencia.status = 'autorizada'
        if not transferencia.autorizada_por_id:
            transferencia.autorizada_por_id = transferencia.criada_por_id
        if not transferencia.autorizada_em:
            transferencia.autorizada_em = transferencia.criada_em or timezone.now()
        transferencia.save(update_fields=['status', 'autorizada_por', 'autorizada_em'])


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0004_origemrecurso'),
    ]

    operations = [
        migrations.RunPython(efetivar_transferencias_pendentes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='transferencia',
            name='status',
            field=models.CharField(
                choices=[('autorizada', 'Registrada'), ('cancelada', 'Cancelada')],
                default='autorizada',
                max_length=20,
                verbose_name='Status',
            ),
        ),
    ]
