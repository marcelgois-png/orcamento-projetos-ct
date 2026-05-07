from django.urls import path
from . import views

urlpatterns = [
    # --- HTMX ---
    path('ajax/subsetores/', views.subsetores_ajax, name='subsetores_ajax'),

    # --- Usuário ---
    path('', views.home, name='home'),
    path('perfil/', views.perfil_editar, name='perfil_editar'),
    path('irps/', views.irp_list, name='irp_list'),
    path('irps/<int:pk>/responder/', views.irp_responder, name='irp_responder'),
    path('irps/<int:irp_pk>/item/<int:item_pk>/salvar/', views.salvar_item_htmx, name='salvar_item_htmx'),

    # --- Dashboard público ---
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Recuperação / Ativação de acesso ---
    path('recuperar-usuario/', views.recuperar_usuario, name='recuperar_usuario'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar_senha'),
    path('recuperar-senha/confirmar/<uidb64>/<token>/', views.confirmar_senha, name='confirmar_senha'),
    path('ativar-conta/<uidb64>/<token>/', views.ativar_conta, name='ativar_conta'),

    # --- Homologação (Aprovador de Setor Raiz) ---
    path('homologacoes/', views.homologacao_list, name='homologacao_list'),
    path('homologacoes/<int:irp_pk>/', views.homologar_setor, name='homologar_setor'),
    path('homologacoes/<int:irp_pk>/reabrir/', views.reabrir_homologacao, name='reabrir_homologacao'),
    path('homologacoes/<int:irp_pk>/encaminhar/', views.encaminhar_licitacao, name='encaminhar_licitacao'),


    # --- Licitação ---
    path('licitacao/', views.licitacao_list, name='licitacao_list'),
    path('licitacao/<int:irp_pk>/', views.licitacao_detalhe, name='licitacao_detalhe'),
    path('licitacao/pregao/<int:pregao_pk>/salvar/', views.licitacao_salvar_pregao, name='licitacao_salvar_pregao'),
    path('licitacao/item/<int:item_pk>/salvar/', views.licitacao_salvar_item, name='licitacao_salvar_item'),
    path('licitacao/exportar/<int:pregao_pk>/', views.licitacao_exportar_itens, name='licitacao_exportar_itens'),

    # --- Gestão ---
    path('gestao/', views.gestao_home, name='gestao_home'),

    # IRPs
    path('gestao/irps/', views.gestao_irp_list, name='gestao_irp_list'),
    path('gestao/irps/criar/', views.gestao_irp_create, name='gestao_irp_create'),
    path('gestao/irps/<int:pk>/editar/', views.gestao_irp_edit, name='gestao_irp_edit'),
    path('gestao/irps/<int:pk>/liberar/', views.gestao_irp_liberar, name='gestao_irp_liberar'),
    path('gestao/irps/<int:pk>/interromper/', views.gestao_irp_interromper, name='gestao_irp_interromper'),
    path('gestao/irps/<int:pk>/excluir/', views.gestao_irp_delete, name='gestao_irp_delete'),
    path('gestao/irps/<int:irp_pk>/resultados/', views.gestao_resultados, name='gestao_resultados'),
    path('gestao/irps/<int:irp_pk>/exportar/', views.gestao_exportar, name='gestao_exportar'),

    # Itens
    path('gestao/irps/<int:irp_pk>/itens/', views.gestao_item_list, name='gestao_item_list'),
    path('gestao/irps/<int:irp_pk>/itens/criar/', views.gestao_item_create, name='gestao_item_create'),
    path('gestao/irps/<int:irp_pk>/itens/apagar-lote/', views.gestao_item_apagar_lote, name='gestao_item_apagar_lote'),
    path('gestao/irps/<int:irp_pk>/itens/importar/', views.gestao_item_importar, name='gestao_item_importar'),
    path('gestao/irps/<int:irp_pk>/itens/importar/modelo/', views.gestao_item_template_xlsx, name='gestao_item_template_xlsx'),
    path('gestao/itens/<int:pk>/editar/', views.gestao_item_edit, name='gestao_item_edit'),
    path('gestao/itens/<int:pk>/toggle/', views.gestao_item_toggle, name='gestao_item_toggle'),
    path('gestao/itens/<int:pk>/excluir/', views.gestao_item_delete, name='gestao_item_delete'),

    # Setores
    path('gestao/setores/', views.gestao_setor_list, name='gestao_setor_list'),
    path('gestao/setores/criar/', views.gestao_setor_create, name='gestao_setor_create'),
    path('gestao/setores/apagar-lote/', views.gestao_setor_apagar_lote, name='gestao_setor_apagar_lote'),
    path('gestao/setores/<int:pk>/editar/', views.gestao_setor_edit, name='gestao_setor_edit'),
    path('gestao/setores/<int:pk>/desativar/', views.gestao_setor_delete, name='gestao_setor_delete'),
    path('gestao/setores/<int:pk>/apagar/', views.gestao_setor_apagar, name='gestao_setor_apagar'),

    # Usuários
    path('gestao/usuarios/', views.gestao_usuario_list, name='gestao_usuario_list'),
    path('gestao/usuarios/apagar-lote/', views.gestao_usuario_apagar_lote, name='gestao_usuario_apagar_lote'),
    path('gestao/usuarios/criar/', views.gestao_usuario_create, name='gestao_usuario_create'),
    path('gestao/usuarios/<int:pk>/editar/', views.gestao_usuario_edit, name='gestao_usuario_edit'),
    path('gestao/usuarios/<int:pk>/toggle-ativo/', views.gestao_usuario_toggle_ativo, name='gestao_usuario_toggle_ativo'),
    path('gestao/usuarios/<int:pk>/apagar/', views.gestao_usuario_apagar, name='gestao_usuario_apagar'),
]
