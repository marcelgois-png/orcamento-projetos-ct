"""
Management command: normalizar_rubricas
=======================================
Detecta e corrige desalinhamentos entre o catálogo de Rubricas
(orcamento.Rubrica) e os valores armazenados como CharField nos
modelos RecursoOrcamentario e Despesa.

Problemas tratados
------------------
1. Rubrica no catálogo com nome divergente do RUBRICA_CHOICES
   (ex: 'Permanente' vs 'Material Permanente' para código 449052).
2. RecursoOrcamentario.rubrica / Despesa.rubrica armazenando a
   CHAVE do RUBRICA_CHOICES ('material_permanente') em vez da
   string de exibição ('449052 - Material Permanente').
3. RecursoOrcamentario.rubrica armazenando o str() antigo do catálogo
   ('449052 - Permanente') quando o catálogo foi corrigido.

Uso
---
    python manage.py normalizar_rubricas            # modo dry-run (só mostra)
    python manage.py normalizar_rubricas --aplicar  # aplica as correções
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import RUBRICA_CHOICES
from orcamento.models import RecursoOrcamentario, Despesa, Rubrica


# Mapa completo: chave RUBRICA_CHOICES → string de exibição
CHOICES_MAP = dict(RUBRICA_CHOICES)

# Mapa inverso: string de exibição → string de exibição (identidade) — para verificar
DISPLAY_SET = set(CHOICES_MAP.values())


def _catalog_correto():
    """
    Retorna dict {codigo: str_correta} baseado em RUBRICA_CHOICES.
    Ex: {'449052': '449052 - Material Permanente'}
    """
    result = {}
    for _key, label in RUBRICA_CHOICES:
        codigo = label.split(' - ')[0].strip()
        result[codigo] = label
    return result


def _str_correto_para(rubrica_valor, catalog_by_code):
    """
    Dado um valor armazenado (chave ou string de exibição), retorna
    a string de exibição canónica ou None se não encontrada.
    """
    # Já é uma string de exibição correcta?
    if rubrica_valor in DISPLAY_SET:
        return rubrica_valor

    # É uma chave do RUBRICA_CHOICES? (ex: 'material_permanente')
    if rubrica_valor in CHOICES_MAP:
        return CHOICES_MAP[rubrica_valor]

    # É uma string antiga do catálogo (ex: '449052 - Permanente')?
    codigo = rubrica_valor.split(' - ')[0].strip()
    if codigo in catalog_by_code:
        return catalog_by_code[codigo]

    return None  # não conseguimos mapear


class Command(BaseCommand):
    help = 'Normaliza valores de rubrica nos modelos RecursoOrcamentario e Despesa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--aplicar',
            action='store_true',
            default=False,
            help='Aplica as correcções na base de dados (por omissão é dry-run)',
        )

    def handle(self, *args, **options):
        aplicar = options['aplicar']
        catalog_by_code = _catalog_correto()

        self.stdout.write('\n=== DIAGNÓSTICO DE RUBRICAS ===\n')

        # ── 1. Catálogo de Rubricas ────────────────────────────────────────────
        self.stdout.write('\n[1] Catálogo de Rubricas vs RUBRICA_CHOICES:')
        cat_fixes = []
        for rb in Rubrica.objects.all().order_by('codigo'):
            str_atual = str(rb)
            codigo = rb.codigo.strip()
            str_correta = catalog_by_code.get(codigo)
            if str_correta and str_atual != str_correta:
                nome_correto = str_correta.split(' - ', 1)[1] if ' - ' in str_correta else str_correta
                self.stdout.write(
                    self.style.WARNING(
                        f'  DIVERGÊNCIA  codigo={codigo!r}  '
                        f'atual={str_atual!r}  correto={str_correta!r}'
                    )
                )
                cat_fixes.append((rb, nome_correto))
            else:
                self.stdout.write(f'  OK           {str_atual!r}')

        # ── 2. RecursoOrcamentario.rubrica ────────────────────────────────────
        self.stdout.write('\n[2] Valores distintos em RecursoOrcamentario.rubrica:')
        ro_fixes = []
        for val in RecursoOrcamentario.objects.values_list('rubrica', flat=True).distinct().order_by('rubrica'):
            correto = _str_correto_para(val, catalog_by_code)
            if correto and correto != val:
                count = RecursoOrcamentario.objects.filter(rubrica=val).count()
                self.stdout.write(
                    self.style.WARNING(
                        f'  DIVERGÊNCIA  {val!r} → {correto!r}  ({count} registos)'
                    )
                )
                ro_fixes.append((val, correto))
            elif correto:
                self.stdout.write(f'  OK           {val!r}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'  SEM MAPA     {val!r}  (não conseguimos mapear)')
                )

        # ── 3. Despesa.rubrica ─────────────────────────────────────────────────
        self.stdout.write('\n[3] Valores distintos em Despesa.rubrica:')
        desp_fixes = []
        for val in Despesa.objects.values_list('rubrica', flat=True).distinct().order_by('rubrica'):
            correto = _str_correto_para(val, catalog_by_code)
            if correto and correto != val:
                count = Despesa.objects.filter(rubrica=val).count()
                self.stdout.write(
                    self.style.WARNING(
                        f'  DIVERGÊNCIA  {val!r} → {correto!r}  ({count} registos)'
                    )
                )
                desp_fixes.append((val, correto))
            elif correto:
                self.stdout.write(f'  OK           {val!r}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'  SEM MAPA     {val!r}  (não conseguimos mapear)')
                )

        # ── Resumo ─────────────────────────────────────────────────────────────
        total = len(cat_fixes) + len(ro_fixes) + len(desp_fixes)
        self.stdout.write(f'\nTotal de divergências encontradas: {total}')

        if not total:
            self.stdout.write(self.style.SUCCESS('\nTudo consistente. Nenhuma correcção necessária.'))
            return

        if not aplicar:
            self.stdout.write(
                self.style.NOTICE(
                    '\nModo DRY-RUN. Para aplicar as correcções execute:\n'
                    '    python manage.py normalizar_rubricas --aplicar\n'
                )
            )
            return

        # ── Aplicar correcções ─────────────────────────────────────────────────
        self.stdout.write('\nAplicando correcções...')
        with transaction.atomic():
            for rb, nome_correto in cat_fixes:
                rb.nome = nome_correto
                rb.save(update_fields=['nome'])
                self.stdout.write(self.style.SUCCESS(f'  Catálogo actualizado: {rb.codigo} → nome={nome_correto!r}'))

            for val_antigo, val_novo in ro_fixes:
                n = RecursoOrcamentario.objects.filter(rubrica=val_antigo).update(rubrica=val_novo)
                self.stdout.write(self.style.SUCCESS(f'  RecursoOrcamentario: {n} registos  {val_antigo!r} → {val_novo!r}'))

            for val_antigo, val_novo in desp_fixes:
                n = Despesa.objects.filter(rubrica=val_antigo).update(rubrica=val_novo)
                self.stdout.write(self.style.SUCCESS(f'  Despesa: {n} registos  {val_antigo!r} → {val_novo!r}'))

        self.stdout.write(self.style.SUCCESS('\nCorrecções aplicadas com sucesso.'))
