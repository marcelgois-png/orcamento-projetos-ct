from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_pregao_data_homologacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='perfil_tipo',
            field=models.CharField(
                choices=[
                    ('admin',            'Administrador do Sistema'),
                    ('gestor_irp',       'Gestor de IRP'),
                    ('diretor_centro',   'Diretor do Centro'),
                    ('aprovador_setor',  'Aprovador de Setor Raiz'),
                    ('respondente',      'Respondente'),
                    ('gestor_financeiro', 'Gestor Financeiro'),
                    ('ordenador_despesa', 'Ordenador de Despesa'),
                ],
                default='respondente',
                max_length=20,
                verbose_name='Perfil',
            ),
        ),
    ]
