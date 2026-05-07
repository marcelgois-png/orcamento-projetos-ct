from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_pregao_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='setor',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('centro',         'Centro'),
                    ('direcao',        'Direção de Centro'),
                    ('administrativo', 'Setor Administrativo'),
                    ('departamento',   'Departamento'),
                    ('coordenacao_g',  'Coordenação de Curso'),
                    ('coordenacao_pg', 'Programa de Pós-Graduação'),
                    ('laboratorio',    'Laboratório'),
                    ('secretaria',     'Secretaria de Departamento'),
                ],
                default='laboratorio',
                max_length=20,
                verbose_name='Tipo',
            ),
        ),
    ]
