from django.contrib import admin
from .models import (Setor, PerfilUsuario, IRP, Item, Resposta, RespostaItem,
                     HomologacaoSetor)


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'sigla', 'pai', 'ativo']
    list_filter = ['ativo', 'pai']
    search_fields = ['codigo', 'nome', 'sigla']
    list_editable = ['ativo']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'usuario', 'matricula', 'setor', 'perfil_tipo']
    list_filter = ['perfil_tipo', 'setor']
    search_fields = ['nome_completo', 'matricula', 'usuario__username']
    raw_id_fields = ['usuario']


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fields = ['numero', 'descricao', 'unidade', 'preco_estimado']


@admin.register(IRP)
class IRPAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'prazo', 'liberada', 'total_itens', 'total_respostas', 'criada_em']
    list_filter = ['liberada']
    search_fields = ['titulo']
    inlines = [ItemInline]
    readonly_fields = ['criada_em', 'atualizada_em', 'criada_por']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criada_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['irp', 'numero', 'descricao', 'unidade', 'preco_estimado']
    list_filter = ['irp']
    search_fields = ['descricao']


class RespostaItemInline(admin.TabularInline):
    model = RespostaItem
    extra = 0
    fields = ['item', 'quantidade', 'observacao']
    raw_id_fields = ['item']


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'irp', 'setor', 'atualizada_em']
    list_filter = ['irp', 'setor']
    search_fields = ['usuario__username', 'usuario__perfil__nome_completo']
    inlines = [RespostaItemInline]
    readonly_fields = ['atualizada_em']


@admin.register(HomologacaoSetor)
class HomologacaoSetorAdmin(admin.ModelAdmin):
    list_display = ['irp', 'setor_raiz', 'status', 'homologado_por', 'homologado_em']
    list_filter = ['status', 'irp']


