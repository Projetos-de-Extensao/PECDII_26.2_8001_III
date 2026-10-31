from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

# Import your views here.
from app.views.usuarioView import UsuarioView


router = DefaultRouter()

router.register(
    r'usuarios',
    UsuarioView,
    basename='usuario'
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
]