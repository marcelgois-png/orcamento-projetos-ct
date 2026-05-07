from django.contrib import admin
from .models import (
    PdiPerspectiva, PdiObjetivoEstrategico, PdiIndicador, PdiMeta,
    RecursoOrcamentario, Transferencia, Despesa,
    SituacaoDespesa,
)


@admin.register(PdiPerspectiva)
class PdiPerspectivaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'ordem']
    search_fields = ['nome', 'codigo']


@admin.register(PdiObjetivoEstrategico)
class PdiObjetivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'perspectiva', 'ordem']
    list_filter = ['perspectiva']
    search_fields = ['nome', 'codigo']


@admin.register(PdiIndicador)
class PdiIndicadorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'objetivo', 'unidade_medida']
    list_filter = ['objetivo__perspectiva']
    search_fields = ['nome', 'codigo']


@admin.register(RecursoOrcamentario)
class RecursoOrcamentarioAdmin(admin.ModelAdmin):
    list_display = ['ano_fiscal', 'setor', 'origem_recurso', 'natureza', 'rubrica', 'valor_orcamentario']
    list_filter = ['ano_fiscal', 'natureza', 'rubrica']
    search_fields = ['origem_recurso', 'setor__nome']
    raw_id_fields = ['setor']


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ['data', 'origem', 'destino', 'valor', 'status']
    list_filter = ['status']


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ['data_despesa', 'discriminacao', 'setor', 'valor_comprometido', 'situacao', 'nota_empenho']
    list_filter = ['situacao', 'natureza', 'rubrica']
    search_fields = ['discriminacao', 'nota_empenho', 'requisicao']
    raw_id_fields = ['setor', 'recurso']


@admin.register(SituacaoDespesa)
class SituacaoDespesaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'chave', 'ordem', 'ativo', 'impacta_saldo', 'badge']
    list_filter = ['ativo', 'impacta_saldo']
    search_fields = ['nome', 'chave']
