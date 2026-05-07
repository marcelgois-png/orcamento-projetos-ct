from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    """
    Cria HomologacaoSetor e AprovacaoCT.

    Depende de 0007 (noop) para manter grafo linear após o 0006_remove
    auto-gerado (que já aplicou AddField(perfil_tipo) + RemoveField(is_gestor)).
    """

    dependencies = [
        ('core', '0007_data_migration_homologacao_aprovacao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Cria HomologacaoSetor
        migrations.CreateModel(
            name='HomologacaoSetor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacao', models.TextField(blank=True, verbose_name='Observação')),
                ('status', models.CharField(
                    choices=[('pendente', 'Pendente'), ('homologada', 'Homologada'), ('rejeitada', 'Rejeitada')],
                    default='pendente', max_length=20, verbose_name='Status',
                )),
                ('homologado_em', models.DateTimeField(blank=True, null=True)),
                ('homologado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='homologacoes_realizadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('irp', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='homologacoes',
                    to='core.irp',
                )),
                ('setor_raiz', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='homologacoes',
                    to='core.setor',
                )),
            ],
            options={
                'verbose_name': 'Homologação de Setor',
                'verbose_name_plural': 'Homologações de Setor',
                'ordering': ['setor_raiz__nome'],
                'unique_together': {('irp', 'setor_raiz')},
            },
        ),

        # Cria AprovacaoCT
        migrations.CreateModel(
            name='AprovacaoCT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parecer', models.TextField(blank=True, verbose_name='Parecer')),
                ('status', models.CharField(
                    choices=[('pendente', 'Pendente'), ('aprovada', 'Aprovada'), ('rejeitada', 'Rejeitada')],
                    default='pendente', max_length=20, verbose_name='Status',
                )),
                ('aprovado_em', models.DateTimeField(blank=True, null=True)),
                ('aprovado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='aprovacoes_ct',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('irp', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='aprovacao_ct',
                    to='core.irp',
                )),
            ],
            options={
                'verbose_name': 'Aprovação CT',
                'verbose_name_plural': 'Aprovações CT',
                'ordering': ['-irp__criada_em'],
            },
        ),
    ]
