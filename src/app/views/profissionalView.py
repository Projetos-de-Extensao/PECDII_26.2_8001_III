from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from app.models import Administrador, Profissional, Responsavel
from app.serializers import ProfissionalSerializer
from app.serializers.profissionalSerializer import ProfissionalPublicSerializer


class ProfissionalView(ReadOnlyModelViewSet):
    """Permite consultar profissionais cadastrados."""

    def get_queryset(self):
        """Lista profissionais e permite filtrar por especialização."""
        usuario = self.request.user
        if not (
            Administrador.objects.filter(pk=usuario.pk).exists()
            or Profissional.objects.filter(pk=usuario.pk).exists()
            or Responsavel.objects.filter(pk=usuario.pk).exists()
        ):
            return Profissional.objects.none()

        queryset = Profissional.objects.all()
        tipo = self.request.query_params.get("tipo")

        especializacoes = {
            "treinador": "treinador",
            "fisioterapeuta": "fisioterapeuta",
            "psicologo": "psicologo",
            "nutricionista": "nutricionista",
        }

        if tipo in especializacoes:
            queryset = queryset.filter(
                **{f"{especializacoes[tipo]}__isnull": False}
            )
        elif tipo:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"tipo": "Especialização inválida."})

        return queryset

    def get_serializer_class(self):
        if Administrador.objects.filter(pk=self.request.user.pk).exists():
            return ProfissionalSerializer
        return ProfissionalPublicSerializer

    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticated]