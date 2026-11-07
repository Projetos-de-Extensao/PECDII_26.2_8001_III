from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

# Import your views here.
from app.views.usuarioView import UsuarioView
from app.views.salaView import SalaView
from app.views.administradorView import AdministradorView
from app.views.responsavelView import ResponsavelView
from app.views.loginView import LoginView
from app.views.logoutView import LogoutView
from app.views.alunoView import AlunoView
from app.views.profissionalView import ProfissionalView


router = DefaultRouter()

router.register(r'usuarios', UsuarioView, basename='usuario')
router.register(r'salas', SalaView, basename='sala')


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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/logout/", LogoutView.as_view(), name="logout"),
]