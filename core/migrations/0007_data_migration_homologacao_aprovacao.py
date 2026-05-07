from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_perfilusuario_is_gestor_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = []
