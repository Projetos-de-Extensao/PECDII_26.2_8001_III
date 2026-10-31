from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

# Import your views here.
from app.views.usuarioView import UsuarioView
from app.views.salaView import SalaView


router = DefaultRouter()

router.register(r'usuarios', UsuarioView, basename='usuario')
router.register(r'salas', SalaView, basename='sala')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
]