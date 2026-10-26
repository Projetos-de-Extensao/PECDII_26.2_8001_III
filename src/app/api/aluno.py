from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser


from app.models.aluno import Aluno
from app.serializers.aluno import AlunoSerializer

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAdminUser]  # Permite acesso sem autenticação