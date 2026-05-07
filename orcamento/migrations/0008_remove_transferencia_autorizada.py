from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0007_transferencia_status_realizada'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transferencia',
            name='autorizada_por',
        ),
        migrations.RemoveField(
            model_name='transferencia',
            name='autorizada_em',
        ),
    ]
