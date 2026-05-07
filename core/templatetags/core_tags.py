from django import template

register = template.Library()


@register.filter
def brl(value):
    """Formata valor como moeda brasileira: R$ 1.234,56"""
    if value is None:
        return 'R$ 0,00'
    try:
        v = float(value)
        # Format with 2 decimal places and thousands separator
        formatted = f'{v:,.2f}'          # "1,234.56"
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')  # "1.234,56"
        return f'R$ {formatted}'
    except (ValueError, TypeError):
        return 'R$ 0,00'


@register.filter
def numero_br(value):
    """Formata número com separador decimal brasileiro: 1.234,56"""
    if value is None:
        return '0'
    try:
        v = float(value)
        if v == int(v):
            return f'{int(v):,}'.replace(',', '.')
        formatted = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (ValueError, TypeError):
        return str(value)


@register.filter
def get_item(dictionary, key):
    """Acessa dicionário com chave variável no template."""
    return dictionary.get(key)


@register.filter
def dict_get(dictionary, key):
    """Alias para get_item — acessa dicionário aninhado com chave variável."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def primeiro_nome(value):
    """Retorna apenas o primeiro nome de um nome completo."""
    if not value:
        return value
    return str(value).split()[0]


@register.filter
def nome_curto(value):
    """Retorna o primeiro e o último nome de um nome completo."""
    if not value:
        return value
    partes = str(value).split()
    if len(partes) <= 2:
        return value
    return f"{partes[0]} {partes[-1]}"
