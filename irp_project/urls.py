from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views


def healthz(request):
    """Healthcheck para o Docker/load balancer. Retorna 200 se a app subiu e o DB responde."""
    db_ok = True
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
    except Exception:
        db_ok = False
    payload = {'status': 'ok' if db_ok else 'degraded', 'db': db_ok}
    return JsonResponse(payload, status=200 if db_ok else 503)


urlpatterns = [
    path('healthz', healthz, name='healthz'),
    path('admin/', admin.site.urls),
    path('modulos/', core_views.selecionar_modulo, name='selecionar_modulo'),
    path('orcamento/', include('orcamento.urls')),
    path('', include('core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('senha/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/senha/ok/'
    ), name='password_change'),
    path('senha/ok/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
]

# Em produção o Nginx serve /media/; aqui só ativa no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
