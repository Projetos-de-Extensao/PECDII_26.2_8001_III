from rest_framework import viewsets
from app.permissions.aluno import PermissaoAluno


from app.models.aluno import Aluno
from app.serializers.aluno import AlunoSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [PermissaoAluno]  # Permite acesso sem autenticação