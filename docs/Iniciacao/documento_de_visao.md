# Documento de Visão — Backend GAAP (PKZ Lab)

| Item | Informação |
|------|------------|
| **Projeto** | Backend do GAAP (Gestão de Atletas de Alta Performance) — PKZ Lab |
| **Equipe** | Bernardo Chagas, Brenno Marques, Caio Magalhães, Juan Lucas Pereira e Rodrigo Aquino |
| **Versão / Data** | 2.0 — 10/11/2026 |

---

## 1. Problema

A PKZ Lab é um centro multidisciplinar de treinamento esportivo e acompanhamento integrado que oferece serviços de treinamento físico, fisioterapia, psicologia e nutrição. Antes do sistema, a operação dependia de controles dispersos em planilhas e de marcações feitas manualmente por WhatsApp, sem uma fonte única e confiável sobre agenda, capacidade de salas, saldo de créditos dos alunos, vínculo de dependentes, histórico de presença e emissão de laudos técnicos.

Consequências da operação manual:

- conflitos operacionais na alocação de sessões, profissionais e espaços físicos (salas);
- falta de controle automatizado sobre os créditos necessários para inscrição dos alunos nas sessões e sobre regras de reembolso em cancelamentos;
- ausência de fluxo formal de solicitação e aprovação administrativa de sessões;
- falta de histórico estruturado de presença, faltas e justificativas por sessão;
- despadronização na emissão de relatórios de desempenho e documentos clínicos (fisioterapia, psicologia e nutrição);
- risco de acesso indevido a informações sensíveis de alunos e documentos técnicos, dado que cada perfil de usuário possui atribuições e restrições distintas.

---

## 2. Objetivo

**Objetivo geral:** entregar, em 2026.2, uma **API REST funcional, testada e documentada**, acompanhada de um portal web integrado de operação e testes, que centralize a gestão de usuários, espaços, sessões, créditos, presenças e laudos da PKZ Lab, aplicando todas as regras de negócio no servidor.

**O sistema implementado deve:**

1. autenticar usuários via token (`TokenAuthentication`), bloquear o login direto de perfis sem acesso individual (`Aluno`), permitir alteração de senha e suportar ativação de conta por convite (`uid` e `token`) para responsáveis;
2. manter o cadastro de administradores, profissionais especializados (`Treinador`, `Fisioterapeuta`, `Psicologo` e `Nutricionista`), responsáveis e alunos (com geração automática de matrícula no padrão `MAT-XXXXXX` e controle de saldo de créditos);
3. gerenciar o vínculo formal entre responsáveis e alunos dependentes (`VinculoResponsavel`), permitindo adição, remoção e transferência de responsabilidade;
4. manter o cadastro de espaços físicos (`Sala`) com validação de numeração única e capacidade mínima;
5. gerenciar o ciclo de vida completo das sessões (`SOLICITADA`, `CONFIRMADA`, `REJEITADA`, `CANCELADA` e `REALIZADA`), exigindo aprovação ou rejeição administrativa para sessões solicitadas;
6. controlar a inscrição e o cancelamento de inscrição de dependentes em sessões confirmadas, aplicando débito automático de créditos e regras de reembolso integral (no cancelamento da sessão ou na desistência com antecedência mínima de 12 horas);
7. permitir a consulta filtrada de sessões (por data, profissional, sala e status) e o acompanhamento das inscrições dos dependentes pelo responsável;
8. registrar e consultar a lista de presença de cada sessão (`PENDENTE`, `PRESENTE`, `AUSENTE`, `JUSTIFICADO`, `DESISTENTE` e `CANCELADA`), exigindo justificativa textual quando o status for `JUSTIFICADO`;
9. permitir a emissão, consulta restrita por perfil e download em formato **PDF** de laudos e documentos técnicos (`DESEMPENHO`, `FISIOTERAPIA`, `PSICOLOGIA` e `NUTRICAO`), validando a compatibilidade entre o tipo de documento e a especialidade do profissional emissor;
10. disponibilizar documentação interativa da API via OpenAPI 3 / Swagger UI e ReDoc (`drf-spectacular`).

---

## 3. Usuários

O domínio possui a classe base `Usuario` (que estende `AbstractUser` do Django com `telefone`, `dataNascimento`, `endereco` e métodos de ativação/desativação de conta) e quatro especializações principais: **Administrador, Responsável, Aluno e Profissional**. A classe `Profissional`, por sua vez, especializa-se em **Treinador, Fisioterapeuta, Psicólogo e Nutricionista**.

| Perfil | Especialização / Registro | Pode | Não pode |
|--------|---------------------------|------|----------|
| **Administrador** | `Administrador` (`tipoContrato`) | Cadastrar usuários, profissionais e responsáveis (com dependentes e envio de convite de ativação); desativar usuários; gerenciar saldo de créditos de alunos; cadastrar, editar e remover salas; solicitar, aprovar (`confirmar`), desaprovar (`rejeitar`) e cancelar sessões; registrar e listar presenças; consultar todos os alunos, responsáveis, sessões e laudos | Emitir laudos técnicos ou concluir sessões (`realizar`) em nome de profissionais |
| **Responsável** | `Responsavel` (vínculo via `VinculoResponsavel`) | Ativar sua conta via link de convite (`uid`/`token`); consultar e atualizar dados cadastrais permitidos de seus dependentes (`first_name`, `last_name`, `telefone`, `endereco`, `dataNascimento`); inscrever dependentes em sessões confirmadas; cancelar inscrições informando motivo; consultar agendamentos/inscrições e baixar laudos (inclusive em PDF) exclusivos de seus dependentes | Acessar dados, agendamentos ou laudos de alunos não vinculados a ele; solicitar ou moderar sessões; alterar matrícula ou saldo de créditos |
| **Aluno** | `Aluno` (`matricula`, `responsavel`, `creditos`) | Representa o atleta/paciente atendido nas sessões, titular da matrícula, do saldo de créditos, das presenças e dos laudos; possui suporte no modelo para emancipação/autonomia (`assumirTutoria`) | Realizar login direto na plataforma (`LoginView` bloqueia autenticação individual de `Aluno`, cujas contas recebem `set_unusable_password()` no cadastro) |
| **Treinador** | `Treinador` (`especialidade`) | Solicitar sessões para si mesmo; cancelar e concluir (`realizar`) suas próprias sessões; listar e registrar presenças (`PRESENTE`, `AUSENTE`, `JUSTIFICADO`) em suas sessões; emitir e exportar em PDF o **Relatório de Desempenho** (`DESEMPENHO`) de alunos inscritos em suas sessões | Aprovar ou rejeitar sessões; gerenciar salas, usuários ou créditos; emitir documentos exclusivos da área de saúde (`FISIOTERAPIA`, `PSICOLOGIA`, `NUTRICAO`) |
| **Profissional de Saúde** | `Fisioterapeuta` (`CREFITO`), `Psicologo` (`CRP`), `Nutricionista` (`CRN`) | Solicitar sessões para si mesmo; cancelar e concluir (`realizar`) suas próprias sessões; listar e registrar presenças em suas sessões; emitir e exportar em PDF laudos compatíveis com seu conselho profissional (`FISIOTERAPIA`, `PSICOLOGIA` ou `NUTRICAO`) | Executar funções administrativas; emitir ou consultar laudos de outros profissionais; emitir documentos fora de sua especialidade |

---

## 4. Escopo

### 4.1 Dentro do MVP (Implementado no Código)

| ID | Funcionalidade | Módulo / Endpoint Principal |
|----|----------------|-----------------------------|
| **F01** | Autenticação via Token, logout, consulta de perfil logado (`/api/me/`), alteração de senha e ativação de conta por convite (`uid`/`token`) | `LoginView`, `LogoutView`, `MeView`, `UsuarioView` |
| **F02** | Controle de acesso e autorização baseada em perfil (`IsAdministrador`, `IsResponsavel`, `IsAuthenticated` e validações de vínculo) | `permissions/`, `views/` |
| **F03** | Cadastro de alunos com geração automática de matrícula (`MAT-XXXXXX`) e atualização parcial de dados cadastrais pelo responsável | `AlunoView`, `AdministradorView`, `AlunoSerializer` |
| **F04** | Cadastro e listagem de profissionais com filtro por especialidade (`treinador`, `fisioterapeuta`, `psicologo`, `nutricionista`) e validação de registro profissional | `ProfissionalView`, `AdministradorView`, `CadastroProfissionalSerializer` |
| **F05** | Cadastro de responsáveis em lote com seus dependentes e disparo de convite de ativação por e-mail, além de adição, remoção e transferência de dependentes | `ResponsavelView`, `AdministradorView`, `VinculoResponsavel` |
| **F06** | Gestão de créditos de alunos (adição e remoção administrativa de saldo com trava contra saldo negativo) | `AdministradorView.gerenciar_creditos` |
| **F07** | Cadastro e gerenciamento de salas físicas com número único e validação de capacidade mínima ($\ge 1$) | `SalaView`, `AdministradorView.cadastrar_sala`, `Sala` |
| **F08** | Solicitação de sessões por profissionais ou administradores com definição de sala, data/hora, duração e créditos necessários | `SessaoView.create`, `Sessao.solicitar`, `Profissional.solicitarSessao` |
| **F09** | Moderação administrativa de sessões: aprovação (`SOLICITADA` $\rightarrow$ `CONFIRMADA`) e rejeição motivada (`SOLICITADA` $\rightarrow$ `REJEITADA`) | `AdministradorView`, `SessaoView.confirmar`, `SessaoView.rejeitar` |
| **F10** | Cancelamento de sessões antes do início com estorno automático e integral dos créditos aos alunos inscritos e atualização do status das presenças para `CANCELADA` | `SessaoView.cancelar`, `Sessao.cancelar` |
| **F11** | Conclusão de sessões confirmadas (`CONFIRMADA` $\rightarrow$ `REALIZADA`) pelo profissional responsável | `SessaoView.realizar` |
| **F12** | Consulta de agenda de sessões com filtros combináveis por data (`AAAA-MM-DD`), profissional, sala e status, além de consulta de agendamentos por responsável | `SessaoView.get_queryset`, `ResponsavelView.agendamentos` |
| **F13** | Inscrição de dependentes em sessões confirmadas (com desconto transacional de créditos) e cancelamento de inscrição (com reembolso de créditos se realizado com $\ge 12\text{h}$ de antecedência) | `ResponsavelView.inscrever_dependente`, `ResponsavelView.cancelar_inscricao`, `Sessao.inscreverAluno`, `Sessao.removerAluno` |
| **F14** | Registro e listagem de presença por sessão (`PRESENTE`, `AUSENTE`, `JUSTIFICADO`) pelo profissional responsável ou administrador | `SessaoView.registrar_presenca`, `SessaoView.listar_presencas`, `Presenca` |
| **F15** | Emissão e consulta de laudos e documentos estruturados em JSON (`DESEMPENHO`, `FISIOTERAPIA`, `PSICOLOGIA`, `NUTRICAO`) com validação de campos obrigatórios por especialidade | `LaudoView`, `LaudoSerializer`, `Laudo` |
| **F16** | Geração e download dinâmico de laudos em arquivo **PDF** (`/api/laudos/{id}/pdf/`) via `ReportLab` | `LaudoView.baixar_pdf` |
| **F17** | Documentação automatizada da API (Schema OpenAPI, Swagger UI em `/api/docs/` e ReDoc em `/api/redoc/`) | `drf-spectacular`, `project/urls.py` |
| **F18** | Interfaces web integradas para operação do portal (`/portal/`) e bancada de testes da API (`/teste-api/`) | `templates/portal.html`, `templates/teste_api.html` |

### 4.2 Regras de Negócio Implementadas

- **RN01 — Isolamento por Perfil:** Cada usuário só executa operações e visualiza registros compatíveis com seu perfil (`Administrador`, `Profissional`, `Responsavel`). Alunos não realizam login direto na plataforma.
- **RN02 — Desativação Lógica de Contas:** A desativação de um usuário (`desativarUsuario`) preserva o histórico no banco de dados e altera apenas `is_active = False`, bloqueando imediatamente sua autenticação.
- **RN03 — Unicidade de Responsável por Aluno:** Cada aluno pode estar vinculado a, no máximo, um `Responsavel` ativo por vez (`OneToOneField` em `VinculoResponsavel`), sendo permitida a transferência formal de responsabilidade (`transferirResponsabilidade`).
- **RN04 — Ciclo de Vida e Moderação de Sessões:** Toda sessão nasce com status `SOLICITADA`. Apenas administradores podem aprová-la (`CONFIRMADA`) ou desaprová-la mediante justificativa obrigatória (`REJEITADA`). Apenas o profissional responsável pode marcá-la como `REALIZADA` após estar `CONFIRMADA`.
- **RN05 — Elegibilidade de Inscrição e Créditos:** Um aluno só pode ser inscrito em sessões com status `CONFIRMADA` que ainda não tenham iniciado (`dataHora > agora`), desde que não possua inscrição ativa na mesma sessão e disponha de saldo de `creditos >= creditosNecessarios`.
- **RN06 — Política de Cancelamento e Reembolso de Créditos:**
  - Caso o responsável cancele a inscrição do dependente antes do início da sessão com **12 horas ou mais de antecedência**, os créditos são integralmente devolvidos ao aluno e a inscrição passa para `DESISTENTE`. Com menos de 12 horas, a inscrição passa para `DESISTENTE` sem estorno de créditos.
  - Caso a própria sessão seja cancelada pelo profissional ou administrador antes de seu início, todos os alunos com presença `PENDENTE` têm seus créditos reembolsados integralmente de forma atômica e o status da presença atualizado para `CANCELADA`.
- **RN07 — Validação de Registro de Presença:** A chamada só pode ser registrada em sessões `CONFIRMADA` ou `REALIZADA`, exclusivamente pelo profissional responsável pela sessão ou por um administrador. O status `JUSTIFICADO` exige obrigatoriamente o preenchimento do campo `justificativa` (validado na aplicação e por `CheckConstraint` no banco).
- **RN08 — Compatibilidade Especialidade x Laudo:** Somente o profissional responsável pela sessão pode emitir laudos para alunos efetivamente inscritos nela (excluídos status `CANCELADA` e `DESISTENTE`), respeitando o vínculo estrito de especialidade:
  - `Treinador` $\rightarrow$ `DESEMPENHO` (campos obrigatórios: `desempenhoFisico`, `evolucao`, `recomendacoes`);
  - `Fisioterapeuta` $\rightarrow$ `FISIOTERAPIA` (campos obrigatórios: `avaliacaoFuncional`, `evolucao`, `recomendacoes`);
  - `Psicologo` $\rightarrow$ `PSICOLOGIA` (campos obrigatórios: `finalidade`, `procedimentos`, `analise`, `conclusao`);
  - `Nutricionista` $\rightarrow$ `NUTRICAO` (campos obrigatórios: `avaliacaoNutricional`, `evolucao`, `orientacoes`).
- **RN09 — Sigilo de Laudos:** Administradores consultam todos os laudos; profissionais consultam apenas os laudos que emitiram; responsáveis consultam e exportam em PDF apenas os laudos pertencentes aos seus dependentes vinculados.
- **RN10 — Proteção de Credenciais:** Senhas nunca são armazenadas ou retornadas em texto puro (`write_only=True`), passando pelos validadores nativos do Django e hashing seguro.

### 4.3 Fora do Escopo Atual (Backlog Futuro)

- Integração com gateways externos de pagamento financeiro para compra avulsa de créditos.
- Notificações via WhatsApp ou push mobile (atualmente o envio de convite utiliza o backend de e-mail do Django).
- Controle individual de ativos/equipamentos móveis (bolas, macas, aparelhos) e ordens de manutenção.
- Aplicativo mobile nativo (iOS/Android) e leitura de QR Code presencial.
- Assinatura digital com certificado ICP-Brasil nos PDFs gerados.

### 4.4 Evoluções e Ajustes em relação à Versão 1.0

1. **Entregas adicionais incorporadas ao escopo implementado:**
   - Geração dinâmica de **PDF** para laudos e relatórios (`ReportLab`);
   - Sistema completo de **créditos por aluno** com débito e estorno transacional;
   - **Portal Web** (`/portal/`) e interface de **Teste da API** (`/teste-api/`) integrados ao backend;
   - Fluxo de **ativação de conta por token/convite** para responsáveis recém-cadastrados.

---

## 5. Restrições

| Tipo | Restrição |
|------|-----------|
| **Prazo** | Um semestre letivo (2026.2), estruturado nas fases de Iniciação, Elaboração, Construção e Transição (RUP/UP) |
| **Custo** | Sem despesa financeira direta; utilização de ferramentas open-source e infraestrutura acadêmica |
| **Tecnologia** | Python 3.14, Django 6.1.2, Django REST Framework (DRF), `drf-spectacular` (OpenAPI 3), `ReportLab` (geração de PDF) e banco relacional SQLite3 com ORM, migrações e constraints de integridade |
| **Ferramentas** | Git, GitHub (Issues, Projects, Actions/Workflows e Codespaces), MkDocs Material para documentação e Visual Studio Code |
| **Fluxo de trabalho** | Branch `main` protegida; desenvolvimento orientado a issues e pull requests com revisão da equipe |
| **Segurança e LGPD** | Autenticação por Token; senhas com hash; restrição de acesso por perfil e vínculo familiar (`VinculoResponsavel`); dados clínicos e laudos restritos ao profissional emissor, ao responsável legal e à administração |
| **Qualidade** | Suíte de testes automatizados (`src/app/tests/`) cobrindo modelos, permissões, autenticação, fluxo de créditos, presenças, sessões, salas, usuários, profissionais, responsáveis e laudos |

---

## Versionamento

| Data | Versão | Descrição | Autor |
|------|-------:|-----------|-------|
| 27/10/2026 | 1.0 | Criação do Documento de Visão | Caio Magalhães |
| 10/11/2026 | 2.0 | Atualização completa do Documento de Visão alinhada ao código-fonte implementado | Caio Magalhães |
