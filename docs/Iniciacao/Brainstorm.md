---
id: brainstorm
title: Brainstorm
---

## Metodologia

A equipe se reuniu para debater ideias gerais sobre o projeto na sala 208 do IBMEC (Barra). A reunião ocorreu no intervalo da aula de projeto CDIA2 e estendeu-se até o final do intervalo. O aluno Brenno Marques atuou como moderador, direcionando a equipe com questões pré-elaboradas, e o aluno Rodrigo Aquino foi responsável por transcrever as respostas para o documento.

## Brainstorm

## Versão 1.1

## Perguntas (respondidas pelos membros do grupo) e Ideias dos membros

### 1. Qual o objetivo principal da aplicação?
- **Brenno**: Agendar reuniões e atividades
- **Brenno**: Visualizar agendamentos
- **Juan**: Centralizar as informações de agendamentos

---

### 2. Quem vai utilizar?
- **Brenno**: Alunos e analistas
- **Juan**: Treinadores e Profissionais de saúde
- **Bernardo**: Administradores
- **Rodrigo**: Pais/Responsáveis dos alunos

---

### 3. Como é o processo de agendamento?
- **Brenno**: Verificação de disponibilidade do local
- **Bernardo**: Verificação de disponibilidade dos profissionais
- **Rodrigo**: Capacidade do local para as atividades em grupo
- **Caio**: Verificação de horários sobrepostos

---

### 4. Quais informações devem ser protegidas?
- **Brenno**: CPF
- **Rodrigo**: Dados médicos e Dados financeiros
- **Caio**: Dados sensíveis

---

### 5. Reagendamento e Cancelamento
- **Juan**: Tempo mínimo
- **Bernardo**: Notificar incluídos
- **Rodrigo**: Multas? (Deverá ser consultada nas regras de negócio com o PO)

---

### 6. Painel administrativo
- **Brenno**: Adicionar locais, atividades, unidades, etc.
- **Brenno**: Cadastrar alunos e professores
- **Juan**: Condições de ativos
- **Rodrigo**: Remover locais, atividades, unidades, etc.

---

### 7. O que notificar?
- **Brenno**: Novas atividades disponíveis
- **Bernardo**: Fatura de pagamento
- **Juan**: Imprevisto com profissionais (ex: cancelamento de aulas)
- **Rodrigo**: Imprevistos gerais, eventos, confirmação das ações (agendamento e cancelamento)

---

### 8. Área de avaliações
- **Brenno**: Feedback dos alunos sobre os professores e atividades
- **Juan**: Avaliação dos alunos (quanto a desempenho e evolução)

---

### 9. Regras de negócio
- **Brenno**: Agendamento baseado em créditos, disponibilidade, só responsáveis podem agendar, apenas os administradores podem criar atividades e cadastrar alunos e professores
- **Brenno**: Crianças devem possuir um responsável
- **Juan**: Visualizar apenas o próprio histórico, registros de falta
- **Rodrigo**: Conflito de horários e locais

---

## Requisitos Elicitados e Priorizados

### Legenda de Prioridade
- **Alta (Must Have)**: Essencial para o funcionamento básico do sistema.
- **Média (Should Have)**: Importante, mas o sistema funciona sem isso numa primeira versão.
- **Baixa (Could Have)**: Recursos adicionais que agregam valor, mas não são prioritários.

| ID | Tipo | Descrição | Prioridade | Rastreabilidade (Origem) |
|---|---|---|---|---|
| BS01 | RF | O sistema deve permitir que alunos, responsáveis e analistas agendem e visualizem reuniões e atividades. | Alta | P1, P2 |
| BS02 | RF | O sistema deve permitir que apenas os administradores cadastrem e gerenciem (adicionar/remover) locais, atividades, unidades, alunos e professores. | Alta | P6, P9 |
| BS03 | RF | O sistema deve verificar automaticamente a disponibilidade de locais e profissionais antes de confirmar um agendamento. | Alta | P3 |
| BS04 | RF | O sistema deve validar a capacidade máxima do local para atividades em grupo. | Alta | P3 |
| BS05 | RF | O sistema deve impedir agendamentos em horários sobrepostos ou com conflito de local/profissional. | Alta | P3, P9 |
| BS06 | RF | O sistema deve permitir vinculação de dependentes (crianças) aos seus respectivos responsáveis. | Alta | P9 |
| BS07 | RF | O sistema deve restringir a realização de agendamentos para menores de idade apenas aos seus responsáveis cadastrados. | Alta | P9 |
| BS08 | RF | O sistema deve permitir que o usuário visualize apenas o seu próprio histórico de agendamentos e registros de falta. | Média | P9 |
| BS09 | RF | O sistema deve permitir reagendamento e cancelamento respeitando um tempo mínimo configurável de antecedência. | Média | P5 |
| BS010 | RF | O sistema deve disponibilizar um módulo para que alunos avaliem professores e atividades (feedback). | Baixa | P8 |
| BS011 | RF | O sistema deve permitir que treinadores e profissionais de saúde registrem avaliações de desempenho e evolução dos alunos. | Baixa | P8 |
| BS012 | RNF | O sistema deve garantir a proteção e criptografia de dados sensíveis (CPF, dados médicos). | Alta | P4 |
| BS013 | RNF | O sistema deve controlar o status de condição (ativo/inativo) para usuários, locais e atividades. | Média | P6 |

---

## Itens Fora de Escopo / Pendentes (Aguardando Definição do PO)

Conforme orientação, os seguintes tópicos levantados durante a sessão de brainstorm foram classificados como **Fora do Escopo Inicial** ou **Pendentes de Validação com o Product Owner (PO)**:

1. **Gestão de Créditos**: O modelo de agendamento baseado no consumo de créditos fica pendente de definição de regras pelo PO.
2. **Dados Financeiros e Faturas**: A gestão de faturas, cobranças e dados de pagamento não será tratada nesta fase inicial do sistema.
3. **Módulo de Notificações**: O envio de notificações (confirmações, cancelamentos, alertas de imprevistos e faturas) foi postergado para uma release futura.
4. **Política de Multas**: A aplicação de multas por cancelamento tardio depende de alinhamento prévio com as regras de negócio do PO.

---

## Conclusão

Através da aplicação da técnica de brainstorm e da subsequente estruturação dos dados, foi possível elicitar, priorizar e rastrear os primeiros requisitos do projeto, estabelecendo limites claros de escopo para as próximas etapas de desenvolvimento.

## Referências Bibliográficas

> BARBOSA, S. D. J; DA SILVA, B. S. Interação humano-computador. Elsevier, 2010.

## Autor(es)

| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 14/09/2026 | 1.0 | Criação do documento | Brenno Marques, Rodrigo Aquino, Bernardo Chagas, Juan Lucas Pereira, Caio Magalhães |
| 27/10/2026 | 1.1 | Refatoração de requisitos, priorização, rastreabilidade e delimitação de escopo | Brenno Marques, Rodrigo Aquino, Bernardo Chagas, Juan Lucas Pereira, Caio Magalhães |