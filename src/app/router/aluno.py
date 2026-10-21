from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.api.aluno import AlunoViewSet

router = DefaultRouter()
router.register(r'alunos', AlunoViewSet, basename='aluno')

urlpatterns = [
    path('', include(router.urls))
]