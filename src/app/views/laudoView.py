from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from io import BytesIO
from xml.sax.saxutils import escape

from django.http import FileResponse
from rest_framework.decorators import action

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)

from app.models import Laudo, Profissional, Administrador, Responsavel
from app.models.responsavelModel import VinculoResponsavel
from app.serializers.laudoSerializer import LaudoSerializer


class LaudoView(ModelViewSet):
    """Permite emitir e consultar documentos profissionais."""

    serializer_class = LaudoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        """Retorna apenas documentos acessíveis ao usuário."""
        usuario = self.request.user

        queryset = Laudo.objects.select_related(
            "aluno", "sessao", "profissional"
        )

        if Administrador.objects.filter(pk=usuario.pk).exists():
            return queryset

        if Profissional.objects.filter(pk=usuario.pk).exists():
            return queryset.filter(profissional_id=usuario.pk)

        if Responsavel.objects.filter(pk=usuario.pk).exists():
            alunos = VinculoResponsavel.objects.filter(
                responsavel_id=usuario.pk
            ).values_list("aluno_id", flat=True)

            return queryset.filter(aluno_id__in=alunos)

        return queryset.none()

    def create(self, request, *args, **kwargs):
        """Emite um documento para uma sessão do profissional."""
        if not Profissional.objects.filter(pk=request.user.pk).exists():
            raise PermissionDenied(
                "Apenas profissionais podem emitir documentos."
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sessao = serializer.validated_data["sessao"]

        if sessao.profissional_id != request.user.pk:
            raise PermissionDenied(
                "Você só pode emitir documentos das suas sessões."
            )

        profissional = Profissional.objects.get(pk=request.user.pk)
        serializer.save(profissional=profissional)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


    @action(detail=True, methods=["get"], url_path="pdf")
    def baixar_pdf(self, request, pk=None):
        """Gera o PDF de um documento autorizado para consulta."""
        laudo = self.get_object()

        buffer = BytesIO()
        documento = SimpleDocTemplate(buffer)
        estilos = getSampleStyleSheet()
        elementos = []

        titulo = estilos["Title"]
        titulo.alignment = TA_CENTER

        tipo = laudo.get_tipoDocumento_display() if laudo.tipoDocumento else "Documento"

        elementos.append(Paragraph("PKZ LAB", titulo))
        elementos.append(Paragraph(escape(tipo), estilos["Heading2"]))
        elementos.append(Spacer(1, 15))
        elementos.append(HRFlowable(width="100%", color=colors.grey))
        elementos.append(Spacer(1, 15))

        dados = [
            ("Aluno", str(laudo.aluno)),
            ("Profissional", str(laudo.profissional)),
            ("Sessão", str(laudo.sessao_id)),
            ("Data de emissão", laudo.dataGeracao.strftime("%d/%m/%Y")),
        ]

        for campo, valor in dados:
            elementos.append(
                Paragraph(
                    f"<b>{campo}:</b> {escape(valor)}",
                    estilos["Normal"]
                )
            )
            elementos.append(Spacer(1, 8))

        elementos.append(Spacer(1, 15))

        for campo, valor in (laudo.conteudo or {}).items():
            elementos.append(
                Paragraph(escape(str(campo)), estilos["Heading3"])
            )
            elementos.append(
                Paragraph(
                    escape(str(valor)).replace("\n", "<br/>"),
                    estilos["Normal"]
                )
            )
            elementos.append(Spacer(1, 12))

        documento.build(elementos)
        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"laudo_{laudo.pk}.pdf",
            content_type="application/pdf",
        )