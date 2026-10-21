from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from app.models.aluno import Aluno
from app.serializers.aluno import AlunoSerializer

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer