---
id: diagrama_de_casos_de_uso
title: Casos de Uso — PKZ Lab
---

# Casos de Uso — PKZ Lab

## Visão geral

O sistema administra usuários e perfis, responsáveis e dependentes, profissionais, salas, sessões, inscrições, créditos, presenças e laudos. Os perfis implementados incluem **Administrador**, **Responsável** e **Profissional** (com especializações); há também o cadastro de **Aluno**. O acesso às operações depende de autenticação e permissões.

## Casos de uso

### UC01 — Autenticar usuário e gerenciar acesso

**Atores:** Usuário cadastrado; Administrador (para criação e desativação de contas).

**Pré-condições:** Conta existente e ativa para autenticação.

**Fluxo básico:**
1. O usuário informa suas credenciais no endpoint de login.
2. O sistema valida as credenciais e retorna um token de autenticação.
3. O usuário utiliza o token para acessar operações permitidas ao seu perfil.
4. O usuário pode consultar seus próprios dados (`me`), alterar a senha e encerrar a sessão (logout).

**Fluxos alternativos:**
- Credenciais inválidas ou conta sem acesso: o sistema recusa a autenticação.
- Na alteração de senha, a senha atual deve estar correta e a nova deve passar pela validação.
- Um responsável cadastrado com convite pode definir a senha por meio de UID e token válidos.
- O administrador pode desativar usuários; contas desativadas não devem autenticar.

**Pós-condições:** Usuário autenticado, senha atualizada, conta ativada ou token encerrado, conforme a operação.

**Regras de negócio:** As permissões são verificadas por operação; o convite de ativação exige token válido; a desativação preserva o registro do usuário.

---

### UC02 — Gerenciar alunos e vínculos com responsáveis

**Atores:** Administrador; Responsável (consulta do próprio cadastro e operações específicas sobre dependentes).

**Pré-condições:** Usuário autenticado e autorizado.

**Fluxo básico:**
1. O administrador cadastra um responsável informando seus dados e os de pelo menos um aluno.
2. O sistema valida os dados e cria o responsável e os alunos em uma transação.
3. O sistema vincula cada aluno ao responsável e envia convite de ativação por e-mail.
4. O administrador consulta alunos e pode atualizar informações conforme as permissões implementadas.
5. O administrador pode adicionar, remover ou transferir vínculos entre responsáveis e alunos.

**Fluxos alternativos:**
- Dados obrigatórios ausentes ou inválidos: cadastro recusado.
- Tentativa de vincular aluno que já possui responsável: operação recusada.
- Transferência ou remoção de vínculo inválido: operação recusada.
- Usuário sem permissão: acesso negado.

**Pós-condições:** Cadastro e vínculos persistidos ou modificados conforme a operação autorizada.

**Regras de negócio:** Cada aluno pode ter, no máximo, um responsável vinculado; o cadastro conjunto de responsável e alunos é atômico; o responsável não tem acesso administrativo geral aos alunos.

---

### UC03 — Gerenciar profissionais e usuários

**Atores:** Administrador; Profissional (consulta permitida).

**Pré-condições:** Administrador autenticado para cadastro; usuário autenticado para consultas autorizadas.

**Fluxo básico:**
1. O administrador inicia o cadastro de usuário.
2. Seleciona, quando aplicável, o tipo profissional: treinador, fisioterapeuta, psicólogo ou nutricionista.
3. O sistema valida os dados e cria o usuário e seu perfil especializado.
4. Usuários autenticados consultam os profissionais conforme o filtro de acesso da API.

**Fluxos alternativos:** Tipo de especialização inválido, dados incorretos ou cadastro duplicado: a operação é recusada.

**Pós-condições:** Usuário/profissional cadastrado ou informações consultadas.

**Regras de negócio:** O cadastro administrativo exige permissão de administrador; o perfil profissional identifica sua especialização. Não há caso de uso independente de cadastro de turmas no código analisado.

---

### UC04 — Gerenciar salas e sessões

**Atores:** Administrador; Profissional.

**Pré-condições:** Usuário autenticado; profissional e sala cadastrados para solicitar sessão.

**Fluxo básico:**
1. O administrador cadastra ou gerencia salas.
2. O administrador solicita uma sessão indicando o profissional; o profissional pode solicitar sessão para si mesmo.
3. O sistema valida sala, data/hora, duração, créditos necessários e regras de disponibilidade.
4. A sessão é criada com status **SOLICITADA**.
5. O administrador confirma ou rejeita a solicitação.
6. Os usuários autenticados consultam sessões, com filtros por data, profissional, sala e status.
7. O profissional responsável pode concluir uma sessão confirmada, marcando-a **REALIZADA**.

**Fluxos alternativos:**
- Dados inválidos ou conflito de disponibilidade: solicitação recusada.
- Rejeição: administrador informa motivo.
- Cancelamento: administrador ou profissional responsável informa motivo; o sistema aplica as regras de cancelamento.
- Sessão em status inadequado: confirmação, rejeição, cancelamento ou conclusão recusada.

**Pós-condições:** Sala cadastrada ou sessão criada, confirmada, rejeitada, cancelada ou realizada.

**Regras de negócio:** Apenas administrador confirma/rejeita solicitações; profissional só solicita sessão para si; apenas o profissional responsável conclui a sessão; cancelamento de sessão pode gerar reembolso integral aos inscritos elegíveis.

---

### UC05 — Inscrever e cancelar inscrição de dependente

**Atores:** Responsável.

**Pré-condições:** Responsável autenticado; aluno vinculado ao responsável; sessão existente e confirmada; créditos suficientes.

**Fluxo básico:**
1. O responsável consulta as sessões disponíveis.
2. Seleciona um dependente vinculado e uma sessão.
3. O sistema valida o vínculo, o estado da sessão, a disponibilidade e os créditos.
4. O sistema registra a inscrição e desconta os créditos necessários.
5. O responsável consulta as inscrições dos dependentes no endpoint de agendamentos.

**Fluxos alternativos:**
- Aluno sem vínculo, inscrição duplicada, conflito de horário, sessão iniciada ou créditos insuficientes: inscrição recusada.
- O responsável solicita cancelamento e informa motivo.
- O sistema altera o status da inscrição sem excluir o registro e aplica a política de reembolso.

**Pós-condições:** Inscrição registrada ou cancelada; saldo de créditos atualizado quando cabível.

**Regras de negócio:** Créditos são descontados na inscrição. Cancelamento pelo responsável com pelo menos 12 horas de antecedência dá reembolso integral; com menos de 12 horas não há reembolso. Cancelamento da sessão por administrador ou profissional responsável prevê reembolso integral das inscrições elegíveis.

---

### UC06 — Registrar presença e concluir sessão

**Atores:** Profissional responsável; Administrador (registro de presença).

**Pré-condições:** Sessão e aluno existentes; registro de inscrição correspondente; ator autorizado.

**Fluxo básico:**
1. O profissional responsável ou administrador acessa os registros da sessão.
2. Consulta os alunos inscritos e seus estados de presença.
3. Registra presença, ausência ou justificativa de um aluno.
4. O sistema atualiza o registro de presença.
5. O profissional responsável conclui a sessão confirmada.

**Fluxos alternativos:** Registro inexistente, status inválido ou usuário não autorizado: operação recusada.

**Pós-condições:** Presenças atualizadas; sessão marcada como realizada quando concluída.

**Regras de negócio:** O registro está associado a um par aluno–sessão; não se cria uma segunda inscrição para registrar presença; a conclusão da sessão é exclusiva do profissional responsável.

---

### UC07 — Registrar acompanhamento por laudo

**Atores:** Profissional.

**Pré-condições:** Profissional autenticado; aluno e sessão existentes; sessão atribuída ao profissional.

**Fluxo básico:**
1. O profissional seleciona a sessão e o aluno.
2. Informa os dados do documento de acompanhamento.
3. O sistema valida o laudo e a relação com a sessão.
4. O sistema grava o documento vinculado ao profissional, ao aluno e à sessão.
5. O documento pode ser consultado ou baixado em PDF conforme as permissões.

**Fluxos alternativos:** Sessão pertencente a outro profissional, dados inválidos ou acesso sem permissão: operação recusada.

**Pós-condições:** Laudo armazenado e disponível aos perfis autorizados.

**Regras de negócio:** Somente profissionais emitem laudos; a API implementa consulta e criação, sem edição/exclusão por seus métodos HTTP expostos.

---

### UC08 — Consultar informações do aluno e histórico

**Atores:** Administrador; Responsável; Aluno; Profissional (para consultas autorizadas de documentos).

**Pré-condições:** Usuário autenticado e permissão para o recurso solicitado.

**Fluxo básico:**
1. O usuário acessa os recursos de consulta.
2. O sistema restringe os registros segundo o perfil.
3. O administrador consulta os alunos; o responsável consulta seus dependentes e inscrições; o aluno consulta seu próprio cadastro.
4. Profissionais e responsáveis consultam laudos nos limites de acesso definidos na API.
5. O usuário visualiza os dados disponíveis.

**Fluxos alternativos:** Registro inexistente ou fora do escopo do usuário: consulta negada ou lista vazia.

**Pós-condições:** Informações consultadas sem alteração de dados.

**Regras de negócio:** O responsável só consulta dados de dependentes vinculados; a consulta de laudos é filtrada pelo perfil. Não foi identificado um painel agregado de desempenho com métricas calculadas; o acompanhamento disponível é baseado em inscrições/presenças e laudos.

---

### UC09 — Gerenciar créditos de alunos

**Atores:** Administrador.

**Pré-condições:** Administrador autenticado; aluno cadastrado.

**Fluxo básico:**
1. O administrador seleciona um aluno.
2. Informa uma quantidade inteira positiva ou negativa de créditos.
3. O sistema valida a quantidade e o saldo resultante.
4. Atualiza o saldo do aluno e confirma a operação.

**Fluxos alternativos:** Quantidade zero, não inteira ou débito superior ao saldo: operação recusada.

**Pós-condições:** Saldo atualizado.

**Regras de negócio:** O saldo não pode ficar negativo; a inscrição e o cancelamento também podem alterar créditos automaticamente.

---
