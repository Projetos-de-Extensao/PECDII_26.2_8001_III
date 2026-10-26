from django.urls import path, include

from app.router.aluno import router as aluno_router
from app.router.usuario import router as usuario_router

from app.api.login import login

urlpatterns = [
    path('', include(aluno_router.urls)),
    path('', include(usuario_router.urls)),
    path("login/", login, name="login"),
]