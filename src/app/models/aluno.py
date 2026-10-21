from django.db import models

class TipoAluno(models.TextChoices):
    ALUNO_PKZ = "aluno_pkz", "Aluno PKZ"
    ALUNO_ONE_TO_ONE = "aluno_one_to_one", "Aluno One to One"

class Servicos(models.TextChoices):
    FISIOTERAPIA = "fisioterapia", "Fisioterapia"
    PSICOLOGO = "psicologo", "Psicólogo"
    NUTRICIONISTA = "nutricionista", "Nutricionista"

class Aluno(models.Model):
    tipo_aluno = models.CharField(
        max_length=20,
        choices=TipoAluno.choices,
    )
    nome = models.CharField(max_length=100)
    nascimento = models.DateField()
    categoria = models.CharField(max_length=100)
    telefone = models.CharField(max_length=11)
    observacoes = models.CharField(max_length=500)
    servicos = models.CharField(
        max_length=20,
        choices=Servicos.choices,
    )
    plano_mensal_creditos = models.IntegerField()
