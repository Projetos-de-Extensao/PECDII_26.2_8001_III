---
id: diagrama_de_casos de uso
title: Diagrama de Casos de Uso
---

## Casos de Uso

Os casos de uso descrevem as principais interações entre os usuários e o sistema de gestão do PKZ Lab, representando as funcionalidades disponíveis de acordo com os diferentes perfis de acesso. A documentação apresenta os atores envolvidos, as pré-condições, o fluxo básico, os fluxos alternativos e as pós-condições de cada caso de uso.

### Descrição:


- Acesso e Segurança
    
    - Realizar Login
    - Autenticar Usuário
    - Controle de acesso por perfil
        
- Alunos
    
    - Gerenciar Alunos
    - Consultar informações do aluno
    - Consultar histórico de presença
        
- Profissionais
    
    - Gerenciar Profissionais
    - Consultar horários e atividades associadas
        
- Turmas e Atividades
    
    - Gerenciar Turmas
    - Associar alunos e profissionais
    - Definir horários e espaços
        
- Agenda
    
    - Gerenciar Agendamentos
    - Consultar horários
    - Verificar disponibilidade e conflitos
    - Cancelar agendamentos
        
- Presença e Acompanhamento
    
    - Registrar Presença
    - Registrar Progresso do Aluno
    - Consultar Desempenho
        
- Administração
    
    - Gerenciar Alunos
    - Gerenciar Profissionais
    - Gerenciar Turmas
    - Gerenciar Agendamentos
    - Consultar Relatórios

### Realizar Login

**Atores:** Usuário, Sistema

**Pré-Condições:**

* Usuário deve estar previamente cadastrado no sistema.
* Usuário deve possuir credenciais de acesso válidas.

**Fluxo Básico:**

1. Usuário informa e-mail e senha.
2. Sistema autentica o usuário.
3. Sistema identifica o perfil de acesso.
4. Sistema disponibiliza as funcionalidades permitidas para o perfil identificado.

**Fluxos Alternativos:**

* **2a.** As credenciais informadas são inválidas.

  * **2a1.** Sistema informa que os dados de acesso são inválidos.
  * **2a2.** Usuário pode tentar realizar o login novamente.
* **3a.** Usuário não possui um perfil de acesso válido.

  * **3a1.** Sistema bloqueia o acesso às funcionalidades.

**Pós-Condições:**

* Usuário é autenticado e tem acesso às funcionalidades permitidas para seu perfil.

**Regras de Negócio:**

* **RN01.** Apenas usuários cadastrados podem acessar o sistema.
* **RN02.** O acesso às funcionalidades deve respeitar o perfil de cada usuário.
* **RN03.** Credenciais inválidas não devem permitir acesso ao sistema.

---

### Gerenciar Alunos

**Atores:** Administrador, Responsável, Sistema

**Pré-Condições:**

* Usuário deve estar autenticado.
* Usuário deve possuir permissão para consultar ou alterar informações de alunos.

**Fluxo Básico:**

1. Usuário acessa o gerenciamento de alunos.
2. Sistema apresenta os alunos disponíveis de acordo com o perfil de acesso.
3. Usuário seleciona um aluno existente ou inicia um novo cadastro.
4. Usuário informa ou altera os dados do aluno.
5. Sistema valida as informações fornecidas.
6. Sistema registra as informações.
7. Sistema confirma a operação.

**Fluxos Alternativos:**

* **5a.** Existem dados obrigatórios ausentes.

  * **5a1.** Sistema informa os dados que precisam ser preenchidos.
* **5b.** Os dados informados são inválidos.

  * **5b1.** Sistema solicita a correção das informações.
* **3a.** Usuário não possui permissão para realizar a operação.

  * **3a1.** Sistema bloqueia a operação.

**Pós-Condições:**

* Os dados do aluno são cadastrados ou atualizados conforme a operação realizada.

**Regras de Negócio:**

* **RN04.** Todo aluno deve possuir um cadastro antes de ser associado a uma turma ou agendamento.
* **RN05.** Os dados do aluno devem ser armazenados de acordo com as permissões de acesso definidas.
* **RN06.** Informações obrigatórias devem ser preenchidas antes da conclusão do cadastro.
* **RN07.** O acesso às informações do aluno deve respeitar o perfil do usuário.

---

