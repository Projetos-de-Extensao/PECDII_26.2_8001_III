from django.db import IntegrityError
from django.db import transaction
from django.test import TestCase

from app.models import Sala


class SalaTests(TestCase):
    def test_cria_sala_com_numero_e_capacidade(self):
        sala = Sala.objects.create(numero=101, capacidade=20)

        self.assertEqual(sala.numero, 101)
        self.assertEqual(sala.capacidade, 20)

    def test_numero_da_sala_deve_ser_unico(self):
        Sala.objects.create(numero=101, capacidade=20)

        with self.assertRaises(IntegrityError):
            Sala.objects.create(numero=101, capacidade=10)

    def test_capacidade_da_sala_deve_ser_maior_que_zero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Sala.objects.create(numero=102, capacidade=0)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Sala.objects.create(numero=103, capacidade=-5)
