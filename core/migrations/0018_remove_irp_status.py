from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_irp_liberada'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irp',
            name='status',
        ),
    ]
