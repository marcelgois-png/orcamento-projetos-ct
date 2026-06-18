from django.db import migrations


# Situações padrão de execução orçamentária. Devem existir e estar ativas para
# que o registro de despesas funcione. Esta migração de dados as restaura caso
# tenham sido desativadas ou renomeadas pela tela de cadastro (ex.: "Empenhada"
# desativada, que fazia o registro falhar com "Informe uma situação válida").
CANONICAS = [
    ('empenhada', 'Empenhada', 1, True,  'bg-warning text-dark'),
    ('liquidada', 'Liquidada', 2, True,  'bg-primary'),
    ('paga',      'Paga',      3, True,  'bg-success'),
    ('cancelada', 'Cancelada', 4, False, 'bg-secondary'),
]


def reativar(apps, schema_editor):
    SituacaoDespesa = apps.get_model('orcamento', 'SituacaoDespesa')
    for chave, nome, ordem, impacta_saldo, badge in CANONICAS:
        obj = SituacaoDespesa.objects.filter(chave=chave).first()
        if obj is None:
            # Foi apagada: recria, desde que o nome canônico esteja livre
            # (o campo nome é único).
            if not SituacaoDespesa.objects.filter(nome=nome).exists():
                SituacaoDespesa.objects.create(
                    chave=chave, nome=nome, ordem=ordem,
                    ativo=True, impacta_saldo=impacta_saldo, badge=badge,
                )
            continue

        campos = []
        if not obj.ativo:
            obj.ativo = True
            campos.append('ativo')
        # Restaura o nome canônico se foi renomeado, mas só se o nome estiver
        # livre (não quebra a constraint de unicidade nem situações customizadas).
        if obj.nome != nome and not SituacaoDespesa.objects.filter(nome=nome).exclude(pk=obj.pk).exists():
            obj.nome = nome
            campos.append('nome')
        if campos:
            obj.save(update_fields=campos)


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0016_despesa_pdi_vinculos'),
    ]

    operations = [
        migrations.RunPython(reativar, migrations.RunPython.noop),
    ]
