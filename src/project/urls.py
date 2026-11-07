from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Import your views here.
from app.views.usuarioView import UsuarioView
from app.views.salaView import SalaView
from app.views.administradorView import AdministradorView
from app.views.responsavelView import ResponsavelView
from app.views.loginView import LoginView
from app.views.logoutView import LogoutView
from app.views.alunoView import AlunoView
from app.views.profissionalView import ProfissionalView
from app.views.sessaoView import SessaoView
from app.views.meView import MeView
from app.views.laudoView import LaudoView


router = DefaultRouter()

router.register(
    r'usuarios', 
    UsuarioView, 
    basename='usuario'
)

router.register(
    r'salas',
    SalaView,
    basename='sala'
)


router.register(
    r'administradores',
    AdministradorView,
    basename='administrador'
)

router.register(
    r'responsaveis',
    ResponsavelView,
    basename='responsavel'
)

router.register(
    r'alunos',
    AlunoView,
    basename='aluno'
)

router.register(
    r'profissionais',
    ProfissionalView,
    basename='profissional'
)

router.register(
    r'sessoes',
    SessaoView,
    basename='sessao'
)

router.register(
    r'laudos',
    LaudoView,
    basename='laudo'
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(), name='redoc'),

    path(
        "teste-api/",
        TemplateView.as_view(template_name="teste_api.html"),
        name="teste-api",
    ),

    path(
        "portal/",
        TemplateView.as_view(template_name="portal.html"),
        name="portal",
    ),
    path("api/me/", MeView.as_view(), name="me"),

]