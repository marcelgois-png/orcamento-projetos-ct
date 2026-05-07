"""
Data migration: normaliza nomes de Rubrica e valores de rubrica
em RecursoOrcamentario e Despesa para ficarem consistentes com
os labels do RUBRICA_CHOICES definidos em core/models.py.

Problema: o catálogo Rubrica pode ter sido cadastrado com nomes
ligeiramente diferentes dos labels das RUBRICA_CHOICES (ex:
'Permanente' em vez de 'Material Permanente' para 449052).
Isso fazia com que RecursoOrcamentario.rubrica armazenasse
'449052 - Permanente' (via str(rubrica)) em vez de
'449052 - Material Permanente' (via RUBRICA_CHOICES label).
"""

from django.db import migrations

# Mapa canónico: código → string de exibição correcta
# (equivalente às RUBRICA_CHOICES de core/models.py)
RUBRICA_CANONICO = {
    '339014': '339014 - Diárias',
    '339018': '339018 - Auxílio Financeiro ao Estudante',
    '339030': '339030 - Material de Consumo',
    '339033': '339033 - Passagens e Locomoção',
    '339036': '339036 - Estagiários',          # duplicado — tratado abaixo
    '339039': '339039 - Serviços Pessoa Jurídica',
    '339040': '339040 - Serviços PJ | TIC',
    '449052': '449052 - Material Permanente',
}

# Para o código 339036 há dois choices (Estagiários e Serviços PF).
# Neste caso mantemos o nome do catálogo se for um dos dois válidos.
RUBRICA_339036_VALIDOS = {
    '339036 - Estagiários',
    '339036 - Serviços Pessoa Física',
}


def normalizar(apps, schema_editor):
    Rubrica              = apps.get_model('orcamento', 'Rubrica')
    RecursoOrcamentario  = apps.get_model('orcamento', 'RecursoOrcamentario')
    Despesa              = apps.get_model('orcamento', 'Despesa')

    # ── 1. Catálogo Rubrica ───────────────────────────────────────────────────
    for rb in Rubrica.objects.all():
        codigo = rb.codigo.strip()
        str_atual = f'{codigo} - {rb.nome}'

        if codigo == '339036':
            # Aceita qualquer dos dois rótulos válidos; não altera
            if str_atual in RUBRICA_339036_VALIDOS:
                continue
            # Caso divergente: padroniza para 'Estagiários' (primeiro da lista)
            nome_correto = 'Estagiários'
        else:
            str_correta = RUBRICA_CANONICO.get(codigo)
            if not str_correta:
                continue  # código desconhecido — não mexe
            if str_atual == str_correta:
                continue  # já está certo
            nome_correto = str_correta.split(' - ', 1)[1]

        rb.nome = nome_correto
        rb.save(update_fields=['nome'])

    # ── Reconstruir mapa de strings correctas (inclui 339036 duplicado) ───────
    # Tudo que está agora no catálogo são strings correctas
    # Construímos um mapa: código → [str_correta, ...]
    catalog_map = {}  # codigo → primeira str correcta (para casos únicos)
    for rb in Rubrica.objects.all():
        codigo = rb.codigo.strip()
        catalog_map.setdefault(codigo, f'{codigo} - {rb.nome}')

    # Conjunto de todas as strings correctas (do catálogo + RUBRICA_CANONICO)
    strings_correctas = set(RUBRICA_CANONICO.values()) | set(RUBRICA_339036_VALIDOS)

    def str_correta_para(valor):
        """Retorna a string canónica para um valor armazenado, ou None."""
        if valor in strings_correctas:
            return valor  # já correcto
        # Extrai código do prefixo  ex: '449052 - Permanente' → '449052'
        codigo = valor.split(' - ')[0].strip()
        if codigo == '339036':
            # Ambíguo — não alteramos automaticamente (requer revisão manual)
            return None
        return RUBRICA_CANONICO.get(codigo)  # None se não encontrado

    # ── 2. RecursoOrcamentario.rubrica ────────────────────────────────────────
    for val in (
        RecursoOrcamentario.objects
        .values_list('rubrica', flat=True)
        .distinct()
        .order_by('rubrica')
    ):
        if not val:
            continue
        correta = str_correta_para(val)
        if correta and correta != val:
            RecursoOrcamentario.objects.filter(rubrica=val).update(rubrica=correta)

    # ── 3. Despesa.rubrica ────────────────────────────────────────────────────
    for val in (
        Despesa.objects
        .values_list('rubrica', flat=True)
        .distinct()
        .order_by('rubrica')
    ):
        if not val:
            continue
        correta = str_correta_para(val)
        if correta and correta != val:
            Despesa.objects.filter(rubrica=val).update(rubrica=correta)


def desfazer(apps, schema_editor):
    # Não revertemos: dados antigos podem ser inconsistentes e é seguro manter a versão normalizada.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0008_remove_transferencia_autorizada'),
    ]

    operations = [
        migrations.RunPython(normalizar, desfazer),
    ]
