from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_setor_tipo'),
    ]

    operations = [
        # PerfilUsuario: rename setor_lotacao → setor
        migrations.RenameField(
            model_name='perfilusuario',
            old_name='setor_lotacao',
            new_name='setor',
        ),
        # PerfilUsuario: remove setor_localizacao
        migrations.RemoveField(
            model_name='perfilusuario',
            name='setor_localizacao',
        ),
        # Resposta: rename setor_lotacao → setor
        migrations.RenameField(
            model_name='resposta',
            old_name='setor_lotacao',
            new_name='setor',
        ),
        # Resposta: remove setor_localizacao
        migrations.RemoveField(
            model_name='resposta',
            name='setor_localizacao',
        ),
    ]
