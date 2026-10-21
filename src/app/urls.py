from django.urls import path, include

from app.router.aluno import router as aluno_router
from app.router.usuario import router as usuario_router

urlpatterns = [
    path('', include(aluno_router.urls)),
    path('', include(usuario_router.urls)),
]