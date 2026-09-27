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

