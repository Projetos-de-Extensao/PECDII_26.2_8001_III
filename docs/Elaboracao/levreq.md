---
id: levantamento_requisitos
title: Levantamento de Requisitos
---

# Levantamento de requisitos — GAAP

Este documento detalha os requisitos do backend de agenda e operação de
treinamentos da PKZ Lab. O escopo segue o [Documento de Visão](../Iniciacao/documento_de_visao.md)
e não inclui notificações, pagamentos, ativos, turmas ou avaliações.

## Stakeholders e perfis

- **Administrador:** gerencia cadastros, espaços, disponibilidade, bloqueios e agendamentos.
- **Responsável:** usuário vinculado a um ou mais alunos, com acesso limitado aos recursos autorizados para esse vínculo.
- **Aluno:** usuário que acessa os próprios agendamentos e registros autorizados.
- **Treinador:** consulta sua agenda, registra presença e atividade realizada e gerencia relatórios de treino.
- **Profissional de saúde:** consulta os atendimentos do serviço ao qual está vinculado e registra presença autorizada.
- **PKZ Lab:** valida regras de operação e critérios de aceite.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| F01 | Autenticar usuários com senha protegida por hash. | Alta |
| F02 | Autorizar operações conforme o perfil do usuário. | Alta |
| F03 | Cadastrar e manter estudantes. | Alta |
| F04 | Cadastrar e manter profissionais. | Alta |
| F05 | Cadastrar e manter serviços. | Alta |
| F06 | Cadastrar espaços e suas capacidades. | Alta |
| F07 | Configurar disponibilidade de profissionais e espaços. | Alta |
| F08 | Registrar bloqueios de agenda. | Alta |
| F09 | Criar agendamentos recusando conflitos, bloqueios e excesso de capacidade. | Alta |
| F10 | Consultar a agenda conforme o perfil e o serviço autorizado. | Alta |
| F11 | Registrar presença ou falta em agendamento existente. | Alta |
| F12 | Registrar a realização da atividade. | Alta |
| F13 | Criar e finalizar relatório de treino. | Alta |
| F14 | Registrar ações relevantes em auditoria. | Média |
| F15 | Documentar endpoints, parâmetros, respostas e erros. | Média |
| F16 | Consultar pendências operacionais simples. | Média |

## Requisitos não funcionais

- **RNF01 — Segurança:** senhas nunca são armazenadas em texto puro.
- **RNF02 — Autorização:** validações ocorrem no backend em toda leitura e alteração.
- **RNF03 — Dados:** o banco é relacional, normalizado e utiliza migrações.
- **RNF04 — Qualidade:** as regras RN01 a RN10 devem possuir testes automatizados.
- **RNF05 — Documentação:** a API deve possuir instruções reproduzíveis de execução.

## Regras de negócio

- **RN01:** cada usuário acessa somente operações permitidas pelo seu perfil.
- **RN02:** o profissional de saúde acessa apenas atendimentos do seu serviço.
- **RN03:** horários bloqueados não recebem agendamentos.
- **RN04:** não existem agendamentos sobrepostos para o mesmo profissional ou espaço.
- **RN05:** um agendamento não ultrapassa a capacidade do espaço.
- **RN06:** somente o administrador mantém cadastros, disponibilidades e bloqueios.
- **RN07:** presença ou falta exige agendamento existente e autorização.
- **RN08:** somente o treinador cria e finaliza relatórios de treino.
- **RN09:** senhas são protegidas por hash.
- **RN10:** ações relevantes geram registro de auditoria.

## Caso de uso prioritário: confirmar agendamento

**Atores:** Administrador ou profissional autorizado.
**Pré-condições:** usuário autenticado; profissional, serviço e espaço cadastrados.
**Fluxo:** informar horário e recursos; validar disponibilidade; validar bloqueios,
conflitos e capacidade; persistir o agendamento; registrar auditoria.
**Exceções:** retornar erro de validação sem persistir quando qualquer regra falhar.

## Rastreabilidade

Os requisitos F01–F16 correspondem às funcionalidades F01–F16 do Documento de
Visão. As regras RN01–RN10 correspondem às regras de negócio do mesmo documento.

## Versionamento

| Data | Versão | Descrição | Autor(es) |
|---|---:|---|---|
| 28/10/2026 | 1.1 | Substituição do exemplo de delivery pelo levantamento do GAAP | Brenno Marques Silva |
| 10/28/26 | 1.2 | Correções de coerência e escopo | Brenno Marques Silva |
