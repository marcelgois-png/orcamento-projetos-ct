import re
import unicodedata

from .models import RUBRICA_CHOICES


def _norm(value):
    text = str(value or '').strip().lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


def rubrica_catalog_labels():
    try:
        from orcamento.models import Rubrica
        labels = [
            str(r)
            for r in Rubrica.objects.filter(ativo=True).select_related('natureza').order_by('ordem', 'codigo', 'nome')
        ]
    except Exception:
        labels = []
    return labels or [label for _, label in RUBRICA_CHOICES]


def rubrica_choices(include_blank=True):
    choices = [(label, label) for label in rubrica_catalog_labels()]
    if include_blank:
        return [('', '— Selecionar —')] + choices
    return choices


def _catalog_lookup():
    lookup = {}
    for label in rubrica_catalog_labels():
        parts = label.split(' - ', 1)
        code = parts[0].strip() if parts else ''
        name = parts[1].strip() if len(parts) > 1 else label
        for alias in {label, code, name, f'{code} {name}'.strip()}:
            key = _norm(alias)
            if key:
                lookup[key] = label
    return lookup


def rubrica_normalizada(value, strict=False):
    raw = str(value or '').strip()
    if not raw:
        return ''

    lookup = _catalog_lookup()
    raw_key = _norm(raw)
    if raw_key in lookup:
        return lookup[raw_key]

    legacy_aliases = {
        'consumo': '339030 - Material de Consumo',
        'material consumo': '339030 - Material de Consumo',
        'permanente': '449052 - Material Permanente',
        'diaria': '339014 - Diárias',
        'diarias': '339014 - Diárias',
        'auxilio financeiro': '339018 - Auxílio Financeiro ao Estudante',
        'passagens': '339033 - Passagens e Locomoção',
        'locomocao': '339033 - Passagens e Locomoção',
        'estagiario': '339036 - Estagiários',
        'estagiarios': '339036 - Estagiários',
        'servico pf': '339036 - Serviços Pessoa Física',
        'servicos pessoa fisica': '339036 - Serviços Pessoa Física',
        'servico pj': '339039 - Serviços Pessoa Jurídica',
        'servicos pessoa juridica': '339039 - Serviços Pessoa Jurídica',
        'pj tic': '339040 - Serviços PJ | TIC',
        'servico pj tic': '339040 - Serviços PJ | TIC',
        'servicos pessoa juridica tic': '339040 - Serviços PJ | TIC',
    }
    alias_target = legacy_aliases.get(raw_key)
    if alias_target:
        return lookup.get(_norm(alias_target), alias_target)

    for old_key, old_label in RUBRICA_CHOICES:
        aliases = {old_key, old_label}
        if ' - ' in old_label:
            code, name = old_label.split(' - ', 1)
            aliases.update({code, name, f'{code} {name}'})
        if raw_key in {_norm(alias) for alias in aliases}:
            return lookup.get(_norm(old_label), old_label)

    code_match = re.search(r'\b\d{6}\b', raw)
    if code_match:
        label = lookup.get(_norm(code_match.group(0)))
        if label:
            return label

    if strict:
        raise ValueError(f'Rubrica "{raw}" não consta no cadastro de rubricas do módulo Orçamento.')
    return raw
