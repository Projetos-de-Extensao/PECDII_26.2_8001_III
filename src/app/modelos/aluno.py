from django.db import models

class Aluno(models.Model):
    # tipo_aluno = models.CheckConstraint("Aluno PKZ", "Aluno One to One")
    nome_completo = models.CharField(max_length=100)
    nascimento = models.DateField()
    categoria = models.CharField(max_length=100)
    telefone = models.CharField(max_length=9)
    observacoes = models.CharField(max_length=500)
    # servicos_liberados = models.CheckConstraint("Fisioterapia", "Psicólogo", "Nutricionista")
    plano_mensal_creditos = models.IntegerField()
