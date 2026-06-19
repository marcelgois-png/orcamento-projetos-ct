from django.urls import path
from . import views

urlpatterns = [
    # Dashboard público (sem login)
    path('dashboard/', views.orcamento_dashboard, name='orcamento_dashboard'),

    # Painel interno
    path('', views.orcamento_home, name='orcamento_home'),

    # PDI — tree view unificada + formulários
    path('pdi/', views.pdi_perspectiva_list, name='pdi_perspectiva_list'),
    path('pdi/perspectivas/criar/', views.pdi_perspectiva_create, name='pdi_perspectiva_create'),
    path('pdi/perspectivas/<int:pk>/editar/', views.pdi_perspectiva_edit, name='pdi_perspectiva_edit'),
    path('pdi/perspectivas/<int:pk>/excluir/', views.pdi_perspectiva_delete, name='pdi_perspectiva_delete'),

    path('pdi/objetivos/criar/', views.pdi_objetivo_create, name='pdi_objetivo_create'),
    path('pdi/objetivos/<int:pk>/editar/', views.pdi_objetivo_edit, name='pdi_objetivo_edit'),
    path('pdi/objetivos/<int:pk>/excluir/', views.pdi_objetivo_delete, name='pdi_objetivo_delete'),

    path('pdi/indicadores/criar/', views.pdi_indicador_create, name='pdi_indicador_create'),
    path('pdi/indicadores/<int:pk>/editar/', views.pdi_indicador_edit, name='pdi_indicador_edit'),
    path('pdi/indicadores/<int:pk>/excluir/', views.pdi_indicador_delete, name='pdi_indicador_delete'),

    path('pdi/importar/', views.pdi_importar, name='pdi_importar'),
    path('pdi/modelo/', views.pdi_modelo_xlsx, name='pdi_modelo_xlsx'),

    # Recursos orçamentários
    path('recursos/', views.recurso_list, name='recurso_list'),
    path('recursos/criar/', views.recurso_create, name='recurso_create'),
    path('recursos/importar/', views.recurso_importar, name='recurso_importar'),
    path('recursos/planilha-modelo/', views.recurso_template_xlsx, name='recurso_template_xlsx'),
    path('recursos/excluir-lote/', views.recurso_excluir_lote, name='recurso_excluir_lote'),
    path('recursos/<int:pk>/editar/', views.recurso_edit, name='recurso_edit'),
    path('recursos/<int:pk>/excluir/', views.recurso_delete, name='recurso_delete'),

    # Transferências
    path('transferencias/', views.transferencia_list, name='transferencia_list'),
    path('transferencias/criar/', views.transferencia_create, name='transferencia_create'),
    path('transferencias/<int:pk>/', views.transferencia_detail, name='transferencia_detail'),
    path('transferencias/<int:pk>/editar/', views.transferencia_edit, name='transferencia_edit'),
    path('transferencias/<int:pk>/cancelar/', views.transferencia_cancelar, name='transferencia_cancelar'),

    # Registro de Preço Vigente
    path('registros-preco/', views.registro_preco_list, name='registro_preco_list'),
    path('registros-preco/sincronizar-irp/', views.registro_preco_sync_irp, name='registro_preco_sync_irp'),
    path('registros-preco/sincronizar-rp/', views.registro_preco_sync_irp, name='registro_preco_sync_rp'),
    path('registros-preco/importar/', views.registro_preco_importar, name='registro_preco_importar'),
    path('registros-preco/excluir-lote/', views.registro_preco_excluir_lote, name='registro_preco_excluir_lote'),
    path('registros-preco/planilha-modelo/', views.registro_preco_template_xlsx, name='registro_preco_template_xlsx'),

    # Despesas
    path('despesas/', views.despesa_list, name='despesa_list'),
    path('despesas/criar/', views.despesa_create, name='despesa_create'),
    path('despesas/importar/', views.despesa_importar, name='despesa_importar'),
    path('despesas/planilha-modelo/', views.despesa_template_xlsx, name='despesa_template_xlsx'),
    path('despesas/excluir-lote/', views.despesa_excluir_lote, name='despesa_excluir_lote'),
    path('despesas/<int:pk>/editar/', views.despesa_edit, name='despesa_edit'),
    path('despesas/<int:pk>/excluir/', views.despesa_delete, name='despesa_delete'),

    # Licitações do IRP (somente leitura)
    path('licitacoes/', views.licitacao_list, name='orcamento_licitacao_list'),

    # Administração do sistema — Usuários
    path('admin/usuarios/',                  views.orc_usuario_list,   name='orc_usuario_list'),
    path('admin/usuarios/criar/',            views.orc_usuario_create, name='orc_usuario_create'),
    path('admin/usuarios/<int:pk>/editar/',  views.orc_usuario_edit,   name='orc_usuario_edit'),
    path('admin/usuarios/<int:pk>/toggle/',  views.orc_usuario_toggle, name='orc_usuario_toggle'),
    path('admin/usuarios/<int:pk>/apagar/',  views.orc_usuario_apagar, name='orc_usuario_apagar'),

    # Administração do sistema — Cadastros de listas
    path('admin/cadastros/',                                          views.orc_cadastros,        name='orc_cadastros'),
    path('admin/cadastros/naturezas/criar/',                          views.orc_natureza_create,  name='orc_natureza_create'),
    path('admin/cadastros/naturezas/<int:pk>/editar/',                views.orc_natureza_edit,    name='orc_natureza_edit'),
    path('admin/cadastros/naturezas/<int:pk>/toggle/',                views.orc_natureza_toggle,  name='orc_natureza_toggle'),
    path('admin/cadastros/naturezas/<int:pk>/excluir/',               views.orc_natureza_delete,  name='orc_natureza_delete'),

    # Rubricas
    path('admin/cadastros/rubricas/criar/',                           views.orc_rubrica_create,   name='orc_rubrica_create'),
    path('admin/cadastros/rubricas/<int:pk>/editar/',                 views.orc_rubrica_edit,     name='orc_rubrica_edit'),
    path('admin/cadastros/rubricas/<int:pk>/toggle/',                 views.orc_rubrica_toggle,   name='orc_rubrica_toggle'),
    path('admin/cadastros/rubricas/<int:pk>/excluir/',                views.orc_rubrica_delete,   name='orc_rubrica_delete'),

    # Origens do Recurso
    path('admin/cadastros/origens/criar/',                            views.orc_origem_create,    name='orc_origem_create'),
    path('admin/cadastros/origens/<int:pk>/editar/',                  views.orc_origem_edit,      name='orc_origem_edit'),
    path('admin/cadastros/origens/<int:pk>/toggle/',                  views.orc_origem_toggle,    name='orc_origem_toggle'),
    path('admin/cadastros/origens/<int:pk>/excluir/',                 views.orc_origem_delete,    name='orc_origem_delete'),

    # Situações da Despesa
    path('admin/cadastros/situacoes-despesa/criar/',                  views.orc_situacao_despesa_create, name='orc_situacao_despesa_create'),
    path('admin/cadastros/situacoes-despesa/<int:pk>/editar/',        views.orc_situacao_despesa_edit,   name='orc_situacao_despesa_edit'),
    path('admin/cadastros/situacoes-despesa/<int:pk>/toggle/',        views.orc_situacao_despesa_toggle, name='orc_situacao_despesa_toggle'),
    path('admin/cadastros/situacoes-despesa/<int:pk>/excluir/',       views.orc_situacao_despesa_delete, name='orc_situacao_despesa_delete'),
]
