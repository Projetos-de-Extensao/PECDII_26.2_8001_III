---
id: dt
title: Design Thinking
---

# Design Thinking — GAAP

## 1. Capa

| Item | Informação |
|---|---|
| **Projeto** | Sistema de Gestão de Atletas de Alta Performance (GAAP) |
| **Recorte** | Backend de agenda e operação de treinamentos da PKZ Lab |
| **Período** | 2026.2 |
| **Stakeholder** | PKZ Lab |
| **Equipe** | Brenno Marques, Bernardo Chagas, Caio Magalhães, Juan Lucas Pereira e Rodrigo Aquino |
| **Data** | 21/09/2026 |

## 2. Introdução

A PKZ Lab é uma escola de treinamento esportivo que atende estudantes e possui profissionais de treino, fisioterapia, psicologia e nutrição. Atualmente, parte da operação depende de controles dispersos e marcações manuais, dificultando o controle de horários, profissionais, espaços, vagas, presença e registros de treinamento.

O projeto propõe uma API REST para centralizar essas informações e aplicar as regras de negócio do GAAP. O objetivo é desenvolver uma solução funcional, testada e documentada para autenticação, cadastros, agenda, notificações e acompanhamento das atividades.

### Público-alvo

- **Administrador:** gerencia estudantes, profissionais, serviços, espaços, ativos, disponibilidades, bloqueios e agendamentos.
- **Treinador/coach:** consulta sua agenda, registra presença e atividade realizada e produz relatórios de treino.
- **Profissional de saúde:** consulta os atendimentos relacionados aos serviços sob sua responsabilidade.
- **Estudante ou responsável:** possibilidade identificada no brainstorm, ainda pendente de validação.

### Escopo do MVP

O MVP contempla:

- autenticação e autorização por perfil;
- cadastro de estudantes, profissionais e serviços;
- gestão de ativos e espaços;
- disponibilidade e bloqueios;
- agendamentos com validação de conflitos e capacidade;
- consulta de agenda;
- registro de presença e realização da atividade;
- relatórios de treino;
- notificações por WhatsApp/e-mail;
- auditoria e documentação da API.

Pagamentos, cobrança, prontuário clínico detalhado, assinatura digital, cálculos avançados de força, aplicativo mobile, QR Code, operação offline, dashboards avançados, data warehouse, multi-tenancy, integrações públicas, PDF e upload de fotografias permanecem fora do escopo inicial.

## 3. Fases do Design Thinking

### 3.1. Empatia

O entendimento inicial foi construído com base no cenário, documento de visão, brainstorm, 5W2H, levantamento de funcionalidades, pesquisa de aplicações semelhantes e pesquisa sobre gestão de ativos e espaços.

As principais necessidades identificadas foram:

| Necessidade | Resposta esperada |
|---|---|
| Informações e marcações dispersas | Centralizar os dados em uma API. |
| Conflitos de horários, profissionais e locais | Validar conflitos automaticamente. |
| Atividades com limite de vagas | Impedir reservas acima da capacidade. |
| Operação com diferentes profissionais | Restringir acesso por perfil e serviço. |
| Acompanhamento de atividades | Registrar presença, realização e relatório de treino. |
| Uso de espaços e equipamentos | Controlar disponibilidade, bloqueios e manutenção. |
| Comunicação sobre a agenda | Enviar notificações de confirmações, cancelamentos e avisos. |

**As necessidades devem ser confirmadas com o stakeholder.**

### 3.2. Definição

**Problema central:** Como centralizar a agenda e a operação da PKZ Lab, garantindo informações confiáveis e evitando conflitos de horário, bloqueios, excesso de capacidade e acesso indevido?

**Pontos de vista:**

- O administrador precisa configurar a operação em um único lugar para reduzir inconsistências.
- O treinador precisa consultar sua agenda e registrar as atividades para acompanhar os estudantes.
- O profissional de saúde precisa acessar somente os atendimentos sob sua responsabilidade para preservar a segurança das informações.
- O estudante ou responsável pode precisar acompanhar ou solicitar agendamentos, mas esse acesso ainda precisa ser definido.

### 3.3. Ideação

O brainstorm levantou ideias de cadastro de alunos e profissionais, agenda, controle de turmas, capacidade, espaços, ativos, presença, relatórios, cancelamentos, reagendamentos, notificações, avaliações, créditos e pagamentos.

As ideias foram priorizadas por contribuição ao problema, viabilidade no período acadêmico, segurança, consistência dos dados e possibilidade de teste. Para o MVP, foram selecionadas:

1. autenticação, autorização e cadastros básicos;
2. gestão de espaços, ativos, disponibilidades e bloqueios;
3. agendamento e consulta de agenda;
4. validação de conflitos e capacidade;
5. presença, atividade realizada e relatório de treino;
6. notificações;
7. auditoria e documentação.

Créditos, pagamentos, avaliações e acesso direto de responsáveis continuam como possibilidades dependentes de validação.

### 3.4. Prototipagem

**Ainda não foi feita.** A equipe ainda não desenvolveu um protótipo alinhado aos fluxos do GAAP. Essa etapa deverá representar, no mínimo, autenticação, cadastros, configuração de disponibilidade, agendamento, consulta de agenda, notificações, registro de presença e relatório de treino.

### 3.5. Teste

**Ainda não foi feito.** Não há registro de testes com usuários ou feedback formal da PKZ Lab.

Após a definição dos fluxos, deverão ser validados com o stakeholder:

- perfis e permissões;
- conflitos, capacidade, disponibilidade e bloqueios;
- notificações e seus eventos;
- uso de espaços e ativos;
- presença, relatórios e auditoria;
- proteção de dados pessoais e sensíveis.

Os testes técnicos deverão cobrir as regras de negócio, autorização, persistência, notificações e tratamento de erros.

## 4. Conclusão

O Design Thinking organizou o problema da PKZ Lab e direcionou o projeto para um MVP de backend focado em agenda e operação. A solução deverá centralizar os dados, controlar os recursos envolvidos nos agendamentos, reduzir conflitos, permitir o acompanhamento das atividades e comunicar eventos relevantes por notificações.

Os próximos passos são validar o escopo com o stakeholder, detalhar casos de uso e critérios de aceitação, definir os contratos da API, desenvolver o protótipo, implementar o MVP e realizar os testes.

## 5. Checklist para conversar com o stakeholder

- [ ] Confirmar os perfis de usuário e suas permissões.
- [ ] Confirmar se estudantes ou responsáveis terão acesso ao sistema.
- [ ] Confirmar quem pode criar, cancelar e reagendar agendamentos.
- [ ] Definir prazo mínimo e regras para cancelamento e reagendamento.
- [ ] Confirmar quais serviços, atividades e profissionais farão parte do MVP.
- [ ] Definir como funciona a capacidade de cada atividade e espaço.
- [ ] Confirmar quais espaços e ativos precisam ser cadastrados.
- [ ] Definir como bloqueios, manutenção e indisponibilidade serão registrados.
- [ ] Confirmar quais eventos gerarão notificações.
- [ ] Definir os canais de notificação: WhatsApp, e-mail ou ambos.
- [ ] Definir quem receberá cada notificação e em que momento.
- [ ] Confirmar quais dados pessoais e sensíveis serão armazenados.
- [ ] Definir regras de acesso a dados de saúde e relatórios.
- [ ] Validar os critérios de aceite do MVP.
- [ ] Confirmar os fluxos que deverão ser prototipados e testados.

## 6. Referências e artefatos relacionados

- [Cenário do projeto](Cenario.md)
- [Descrição do projeto](Pesquisa/descricao_projeto.md)
- [Funcionalidades previstas](Pesquisa/funcionalidades_previstas.md)
- [Brainstorm](Brainstorm.md)
- [5W2H](5w2h.md)
- [Pesquisa de aplicações semelhantes](Pesquisa/apps_semelhantes.md)
- [Pesquisa sobre gestão de ativos e espaços](Pesquisa/gestao_ativos_e_espacos.md)

## Versionamento

| Data | Versão | Descrição | Autor(es) |
|---|---:|---|---|
| 21/09/2026 | 1.1 | Inclusão de notificações, remoção da prototipagem desenvolvida, síntese do documento e checklist do stakeholder | Brenno Marques |
