from django.db import models
from django.contrib.auth.models import AbstractUser
from nbformat import ValidationError

#Implementa a classe Usuario, que herda da classe de usuario do Django
class Usuario(AbstractUser):
    # HERDADO DE AbstractUser
    #
    # ATRIBUTOS:
    # id: integer
    # password: string (hash da senha)
    # last_login: datetime
    # is_superuser: boolean
    # username: string
    # first_name: string
    # last_name: string
    # email: string
    # is_staff: boolean
    # is_active: boolean
    # date_joined: datetime
    # groups: ManyToMany[Group]
    # user_permissions: ManyToMany[Permission]
    #
    # MÉTODOS:
    # get_full_name()
    # get_short_name()
    # email_user(subject, message)
    # set_password(raw_password)
    # check_password(raw_password)
    # has_usable_password()
    # get_username()
    # get_all_permissions()
    # get_user_permissions()
    # get_group_permissions()
    # has_perm(perm)
    # has_perms(perm_list)
    # has_module_perms(app_label)

    telefone = models.CharField(max_length=15, blank=True)
    dataNascimento = models.DateField(blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True)

    def ativar(self):
        """
        Ativa o usuário, permitindo que ele faça login no sistema.

        Este método define o atributo 'is_active' como True,
        indicando que o usuário está ativo e pode acessar o sistema.
        """
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active"])
        else:
            raise ValidationError("O usuário já está ativo.")

    def desativar(self):
        """
        Desativa o usuário, impedindo que ele faça login no sistema.

        Este método define o atributo 'is_active' como False,
        indicando que o usuário está inativo e não pode acessar o sistema.
        """
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])
        else:
            raise ValidationError("O usuário já está desativado.")
