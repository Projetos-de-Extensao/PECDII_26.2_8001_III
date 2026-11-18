"""Populate the local SQLite database with isolated PKZ Lab test data."""

import argparse
import os
import secrets
import sys
from datetime import timedelta
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connections, transaction
from django.db.models import Q
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

from app.Enums import StatusSessao
from app.models import (
    Administrador,
    Aluno,
    Laudo,
    Presenca,
    Responsavel,
    Sala,
    Sessao,
    Treinador,
    VinculoResponsavel,
)
from app.serializers.responsavelSerializer import ResponsavelSerializer


TAG = "demo_test_20261118"
PASSWORD = os.environ.get("PKZ_TEST_SEED_PASSWORD") or secrets.token_urlsafe(32)
GENERATED_PASSWORD = not os.environ.get("PKZ_TEST_SEED_PASSWORD")
ADMIN_USERNAME = f"{TAG}_admin"
RESPONSAVEL_USERNAME = f"{TAG}_responsavel"
ALUNO_USERNAME = f"{TAG}_aluno"
TREINADOR_1_USERNAME = f"{TAG}_treinador_1"
TREINADOR_2_USERNAME = f"{TAG}_treinador_2"
MATRICULA = "DEMO-TEST-20261118"
ROOM_NUMBERS = (9901181, 9901182)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Cria ou remove dados sintéticos de teste no SQLite local do projeto."
        )
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="remove somente os dados identificados por este script",
    )
    parser.add_argument(
        "--database",
        type=Path,
        help="arquivo SQLite existente; por padrão usa src/db.sqlite3",
    )
    return parser.parse_args()


def configure_database(database_path):
    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
        raise SystemExit("Este script só opera em banco SQLite.")

    configured_path = Path(settings.DATABASES["default"]["NAME"]).resolve()
    target_path = (database_path or configured_path).resolve()
    if target_path == configured_path:
        settings.DATABASES["default"]["NAME"] = str(target_path)
    elif not database_path:
        raise SystemExit("Informe um arquivo SQLite existente.")

    if not target_path.is_file():
        raise SystemExit(
            f"Banco não encontrado: {target_path}. "
            "O script não cria nem migra bancos automaticamente."
        )

    connections.close_all()
    settings.DATABASES["default"]["NAME"] = str(target_path)

    executor = MigrationExecutor(connections["default"])
    pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
    if pending:
        raise SystemExit(
            "Há migrações pendentes. Execute `python manage.py migrate` "
            "antes de usar este script."
        )

    return target_path


def adult_birth_date(years):
    today = timezone.localdate()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


def assert_validation_error(callback, expected_text):
    try:
        callback()
    except ValidationError as error:
        if expected_text not in str(error):
            raise RuntimeError(
                f"Validação falhou com mensagem inesperada: {error}"
            ) from error
        return
    raise RuntimeError(f"A regra deveria rejeitar: {expected_text}")


def ensure_no_seed_data():
    usernames = (
        ADMIN_USERNAME,
        RESPONSAVEL_USERNAME,
        ALUNO_USERNAME,
        TREINADOR_1_USERNAME,
        TREINADOR_2_USERNAME,
    )
    if (
        Administrador.objects.filter(username__in=usernames).exists()
        or Responsavel.objects.filter(username__in=usernames).exists()
        or Aluno.objects.filter(username__in=usernames).exists()
        or Treinador.objects.filter(username__in=usernames).exists()
        or Sala.objects.filter(numero__in=ROOM_NUMBERS).exists()
        or Aluno.objects.filter(matricula=MATRICULA).exists()
    ):
        raise SystemExit(
            "Já existem registros com os identificadores reservados pelo script. "
            "Use --cleanup para remover os dados de teste anteriores."
        )


def populate():
    ensure_no_seed_data()

    now = timezone.now()
    start = now + timedelta(days=7)
    admin = Administrador.objects.create_user(
        username=ADMIN_USERNAME,
        password=PASSWORD,
        tipoContrato="TESTE",
        first_name="Admin de teste",
    )
    trainer_1 = Treinador.objects.create_user(
        username=TREINADOR_1_USERNAME,
        password=PASSWORD,
        tipoContrato="TESTE",
        formacao="Formação demonstrativa",
        especialidade="Treino funcional",
        first_name="Profissional de teste 1",
    )
    trainer_2 = Treinador.objects.create_user(
        username=TREINADOR_2_USERNAME,
        password=PASSWORD,
        tipoContrato="TESTE",
        formacao="Formação demonstrativa",
        especialidade="Treino demonstrativo",
        first_name="Profissional de teste 2",
    )

    responsible_data = {
        "username": RESPONSAVEL_USERNAME,
        "password": PASSWORD,
        "email": f"{RESPONSAVEL_USERNAME}@example.test",
        "first_name": "Responsável de teste",
        "dataNascimento": adult_birth_date(30).isoformat(),
    }
    responsible_serializer = ResponsavelSerializer(data=responsible_data)
    responsible_serializer.is_valid(raise_exception=True)
    responsible = responsible_serializer.save()

    student = Aluno.objects.create_user(
        username=ALUNO_USERNAME,
        password=PASSWORD,
        first_name="Aluno de teste",
        matricula=MATRICULA,
        creditos=10,
    )
    VinculoResponsavel.objects.create(
        responsavel=responsible,
        aluno=student,
    )
    room_1 = Sala.objects.create(numero=ROOM_NUMBERS[0], capacidade=10)
    room_2 = Sala.objects.create(numero=ROOM_NUMBERS[1], capacidade=10)

    session_1 = Sessao.solicitar(
        profissional=trainer_1,
        sala=room_1,
        dataHora=start,
        duracao=timedelta(minutes=45),
        creditosNecessarios=2,
    )
    session_1.confirmar()
    session_2 = Sessao.solicitar(
        profissional=trainer_2,
        sala=room_2,
        dataHora=start,
        duracao=timedelta(minutes=45),
        creditosNecessarios=2,
    )
    session_2.confirmar()
    adjacent_session = Sessao.solicitar(
        profissional=trainer_1,
        sala=room_1,
        dataHora=start + timedelta(minutes=45),
        duracao=timedelta(minutes=45),
        creditosNecessarios=2,
    )
    adjacent_session.confirmar()

    assert_validation_error(
        lambda: Sessao.solicitar(
            profissional=trainer_2,
            sala=room_1,
            dataHora=start + timedelta(minutes=15),
            duracao=timedelta(minutes=45),
            creditosNecessarios=2,
        ),
        "horário conflitante",
    )
    assert_validation_error(
        lambda: Sessao.solicitar(
            profissional=trainer_1,
            sala=room_2,
            dataHora=start + timedelta(minutes=15),
            duracao=timedelta(minutes=15),
            creditosNecessarios=2,
        ),
        "horário conflitante",
    )
    assert_validation_error(
        lambda: Sessao.solicitar(
            profissional=trainer_2,
            sala=room_2,
            dataHora=now - timedelta(days=1),
            duracao=timedelta(minutes=45),
            creditosNecessarios=2,
        ),
        "futuras",
    )

    Responsavel.validarMaioridade(adult_birth_date(18))
    assert_validation_error(
        lambda: Responsavel.validarMaioridade(
            adult_birth_date(18) + timedelta(days=1)
        ),
        "18 anos completos",
    )

    responsible.inscreverDependenteEmSessao(student, session_1)
    credits_after_first_enrollment = student.creditos - session_1.creditosNecessarios
    assert_validation_error(
        lambda: responsible.inscreverDependenteEmSessao(student, session_2),
        "horário conflitante",
    )
    student.refresh_from_db()
    if student.creditos != credits_after_first_enrollment:
        raise RuntimeError("A tentativa de inscrição conflitante alterou créditos.")
    if Presenca.objects.filter(sessao=session_2, aluno=student).exists():
        raise RuntimeError("A tentativa conflitante persistiu uma inscrição.")

    return {
        "administrador": admin.username,
        "responsavel": responsible.username,
        "aluno": student.username,
        "profissionais": [trainer_1.username, trainer_2.username],
        "salas": list(ROOM_NUMBERS),
        "sessoes": [
            session_1.pk,
            session_2.pk,
            adjacent_session.pk,
        ],
        "creditos_restantes": student.creditos,
    }


def seed_sessions():
    trainer_usernames = (TREINADOR_1_USERNAME, TREINADOR_2_USERNAME)
    return Sessao.objects.filter(
        Q(sala__numero__in=ROOM_NUMBERS)
        | Q(profissional__username__in=trainer_usernames)
    )


def cleanup():
    usernames = (
        ADMIN_USERNAME,
        RESPONSAVEL_USERNAME,
        ALUNO_USERNAME,
        TREINADOR_1_USERNAME,
        TREINADOR_2_USERNAME,
    )
    responsible = Responsavel.objects.filter(
        username=RESPONSAVEL_USERNAME
    ).first()
    student = Aluno.objects.filter(username=ALUNO_USERNAME).first()
    trainers = Treinador.objects.filter(
        username__in=(TREINADOR_1_USERNAME, TREINADOR_2_USERNAME)
    )
    rooms = list(Sala.objects.filter(numero__in=ROOM_NUMBERS))
    sessions = seed_sessions()

    fixture_users_exist = (
        Administrador.objects.filter(username=ADMIN_USERNAME).exists()
        or responsible is not None
        or student is not None
        or trainers.exists()
    )
    if not fixture_users_exist:
        if rooms or sessions.exists():
            raise SystemExit(
                "Limpeza cancelada: há registros com identificadores "
                "reservados, mas não foi possível confirmar que foram "
                "criados por este script."
            )
        return ()

    if (
        not Administrador.objects.filter(username=ADMIN_USERNAME).exists()
        or responsible is None
        or student is None
        or trainers.count() != 2
        or len(rooms) != len(ROOM_NUMBERS)
        or any(room.capacidade != 10 for room in rooms)
        or student.matricula != MATRICULA
        or student.creditos != 8
        or sessions.count() != 3
        or Presenca.objects.filter(sessao__in=sessions).count() != 1
    ):
        raise SystemExit(
            "Limpeza cancelada: o conjunto de dados não corresponde "
            "à população original. Nenhum registro foi removido."
        )

    if responsible and responsible.dependentes.exclude(
        aluno__username=ALUNO_USERNAME
    ).exists():
        raise SystemExit(
            "Limpeza cancelada: o responsável de teste tem dependentes "
            "fora do conjunto criado pelo script."
        )
    if student:
        link = VinculoResponsavel.objects.filter(aluno=student).first()
        if link and link.responsavel_id != getattr(responsible, "pk", None):
            raise SystemExit(
                "Limpeza cancelada: o aluno de teste está vinculado a "
                "outro responsável."
            )
        if Presenca.objects.filter(aluno=student).exclude(
            sessao__in=sessions
        ).exists():
            raise SystemExit(
                "Limpeza cancelada: o aluno de teste possui inscrições "
                "em sessões fora do conjunto criado pelo script."
            )

    if Presenca.objects.filter(sessao__in=sessions).exclude(
        aluno__username=ALUNO_USERNAME
    ).exists():
        raise SystemExit(
            "Limpeza cancelada: há alunos externos inscritos nas sessões "
            "de teste."
        )
    if Laudo.objects.filter(
        Q(sessao__in=sessions)
        | Q(aluno__username=ALUNO_USERNAME)
        | Q(profissional__in=trainers)
    ).exists():
        raise SystemExit(
            "Limpeza cancelada: foram encontrados laudos relacionados "
            "aos dados de teste."
        )
    if sessions.exclude(
        sala__numero__in=ROOM_NUMBERS,
        profissional__username__in=(TREINADOR_1_USERNAME, TREINADOR_2_USERNAME),
    ).exists():
        raise SystemExit(
            "Limpeza cancelada: uma sala ou profissional de teste está "
            "associado a sessões externas."
        )

    with transaction.atomic():
        Presenca.objects.filter(sessao__in=sessions).delete()
        sessions.delete()
        VinculoResponsavel.objects.filter(
            aluno__username=ALUNO_USERNAME,
            responsavel__username=RESPONSAVEL_USERNAME,
        ).delete()

        Treinador.objects.filter(
            username__in=(TREINADOR_1_USERNAME, TREINADOR_2_USERNAME)
        ).delete()
        Aluno.objects.filter(username=ALUNO_USERNAME).delete()
        Responsavel.objects.filter(username=RESPONSAVEL_USERNAME).delete()
        Administrador.objects.filter(username=ADMIN_USERNAME).delete()
        Sala.objects.filter(numero__in=ROOM_NUMBERS).delete()

    return usernames


def main():
    args = parse_args()
    database_path = configure_database(args.database)

    if args.cleanup:
        with transaction.atomic():
            removed_usernames = cleanup()
        print(f"Dados de teste removidos de: {database_path}")
        print("Contas verificadas: " + ", ".join(removed_usernames))
        return

    with transaction.atomic():
        result = populate()
    print(f"Dados criados e regras verificadas em: {database_path}")
    for key, value in result.items():
        print(f"{key}: {value}")
    if GENERATED_PASSWORD and sys.stdout.isatty():
        print(f"Senha local de teste: {PASSWORD}")


if __name__ == "__main__":
    main()
