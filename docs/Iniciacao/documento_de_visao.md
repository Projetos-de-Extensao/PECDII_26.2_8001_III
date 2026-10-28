# Documento de Visão — Backend GAAP (PKZ Lab)
 
| Item | Informação |
|------|------------|
| **Projeto** | Backend do GAAP (Gestão de Atletas de Alta Performance) |
| **Equipe** | Bernardo Chagas, Brenno Marques, Caio Magalhães, Juan Lucas Pereira e Rodrigo Aquino |
| **Versão / Data** | 1.0 — 27/10/2026 |
 
---
 
## 1. Problema
 
A PKZ Lab é uma escola de treinamento esportivo com serviços de treino, fisioterapia, psicologia e nutrição. Hoje a operação depende de controles dispersos e de marcações feitas manualmente por WhatsApp. Não existe uma fonte única e confiável sobre agenda, vagas, presença e relatórios de treino.
 
Consequências:
 
- conflitos de horário entre sessões, profissionais e espaços;
- atividades com mais estudantes do que o limite de vagas;
- dificuldade para saber quais horários estão livres;
- falta de histórico organizado de presença e de atividades realizadas;
- risco de acesso indevido a informações, pois cada profissional tem uma função diferente.
---
 
## 2. Objetivo
 
**Objetivo geral:** entregar, em 2026.2, uma **API REST funcional, testada e documentada** que centralize a agenda e a operação de treinamento da PKZ Lab e aplique as regras de negócio no servidor.
 
**A API deve:**
 
1. autenticar usuários e autorizar o acesso por perfil;
2. manter os cadastros de estudantes, profissionais, serviços e espaços;
3. configurar disponibilidades e bloqueios;
4. criar agendamentos recusando conflito de horário, horário bloqueado e excesso de capacidade;
5. permitir a consulta de agenda conforme o perfil;
6. registrar presença ou falta e a realização da atividade;
7. permitir criar e finalizar relatórios de treino;
8. registrar em auditoria as ações relevantes;
9. ter todos os endpoints documentados.
---
 
## 3. Usuários
 
O domínio possui os perfis de usuário **Administrador, Responsável, Aluno,
Treinador e Profissional de saúde**. Administrador, Responsável, Aluno e
Profissional são especializações de `Usuario`; Treinador e as especialidades
de saúde são especializações de Profissional.
 
| Perfil | Pode | Não pode |
|--------|------|----------|
| **Administrador** | Gerenciar estudantes, profissionais, serviços e espaços; configurar disponibilidades e bloqueios; administrar agendamentos; consultar pendências | — |
| **Responsável** | Acessar os recursos permitidos para acompanhar alunos sob sua responsabilidade e realizar ações autorizadas | Acessar dados ou operações fora de seus vínculos |
| **Aluno** | Acessar os recursos permitidos para acompanhar seus próprios agendamentos e registros | Acessar dados de outros alunos ou funções administrativas |
| **Treinador** | Consultar a agenda sob sua responsabilidade; registrar presença ou falta; registrar a atividade realizada; criar e finalizar relatórios de treino | Executar funções administrativas; ver agendas de outros profissionais |
| **Profissional de saúde** (fisioterapia, psicologia ou nutrição) | Consultar a agenda e os atendimentos do serviço ao qual está vinculado | Ver atendimentos de outros serviços; executar funções administrativas |

As permissões efetivas de Aluno e Responsável devem respeitar seus vínculos
com os alunos e as regras de autorização do backend.
 
---
 
## 4. Escopo
 
### 4.1 Dentro do MVP
 
| ID | Funcionalidade |
|----|----------------|
| F01 | Autenticação, com senhas protegidas por hash |
| F02 | Autorização por perfil |
| F03 | Cadastro de estudantes |
| F04 | Cadastro de profissionais |
| F05 | Cadastro de serviços |
| F06 | Cadastro de espaços, com capacidade |
| F07 | Disponibilidade de profissionais e espaços |
| F08 | Bloqueios de agenda |
| F09 | Agendamento com validação de conflito, bloqueio e capacidade |
| F10 | Consulta de agenda por perfil |
| F11 | Registro de presença e falta |
| F12 | Registro de atividade realizada |
| F13 | Relatório de treino (criar e finalizar) |
| F14 | Auditoria de ações relevantes |
| F15 | Documentação da API |
| F16 | Consulta simples de pendências (administrador) |
 
### 4.2 Regras de negócio do MVP
 
- **RN01** — Cada usuário só acessa o que o seu perfil permite.
- **RN02** — O profissional de saúde só vê atendimentos do seu serviço.
- **RN03** — Horário bloqueado não recebe agendamentos.
- **RN04** — Não pode haver agendamentos sobrepostos para o mesmo profissional ou espaço.
- **RN05** — Um agendamento não pode ultrapassar a capacidade.
- **RN06** — Só o administrador cadastra estudantes, profissionais, serviços, espaços, disponibilidades e bloqueios.
- **RN07** — Presença ou falta só é registrada em agendamento existente, por treinador ou profissional autorizado.
- **RN08** — Só o treinador cria e finaliza relatórios de treino.
- **RN09** — Senhas nunca são guardadas em texto puro.
- **RN10** — Ações relevantes geram registro de auditoria.
As validações RN03, RN04 e RN05 ocorrem no backend.
 
### 4.3 Fora do MVP
 
- Notificações (WhatsApp, e-mail, confirmações, avisos, faturas).
- Prontuário clínico detalhado e assinatura digital.
- Aplicativo mobile, QR Code e operação offline.
- Dashboards avançados, BI e data warehouse.
- Multi-tenancy e integrações públicas.
- Geração de PDF e upload de fotografias.
- Avaliações de professores e de desempenho dos estudantes.
### 4.4 Pendente de validação com a PKZ Lab
 
- Permissões detalhadas de Alunos e Responsáveis e vínculo de menores com responsáveis.
- Cancelamento e reagendamento (quem pode e prazo mínimo).
- Gestão de ativos e equipamentos.
- Controle de turmas.
---
 
## 5. Restrições
 
| Tipo | Restrição |
|------|-----------|
| **Prazo** | Um semestre (2026.2), em fases RUP/UP |
| **Custo** | Sem despesa financeira; o custo é o tempo da equipe |
| **Tecnologia** | Python e Django; banco de dados relacional normalizado com ORM e migrações; API REST |
| **Ferramentas** | Git, GitHub (Issues, Projects e pull requests) e Visual Studio Code |
| **Fluxo de trabalho** | `main` protegida; um branch por issue; todo código entra por pull request revisado por pelo menos um integrante |
| **Segurança e LGPD** | Senhas com hash; validação dos dados recebidos; dados sensíveis (CPF e dados médicos) protegidos; informações de saúde tratadas como dados pessoais sensíveis; sem prontuário clínico |
| **Qualidade** | Testes automatizados cobrindo as regras RN01 a RN10, executados em integração contínua |
| **Artefatos** | Diagramas de casos de uso, classes, sequência (confirmar agendamento e finalizar relatório) e entidade-relacionamento, versionados no repositório |
| **Entrega** | Somente backend: sem interface gráfica, sem app mobile |
 
---
 
 
## Versionamento
 
| Data | Versão | Descrição | Autor |
|------|-------:|-----------|-------|
| 27/10/2026 | 1.0 | Criação do Documento de Visão | Caio Magalhães |
