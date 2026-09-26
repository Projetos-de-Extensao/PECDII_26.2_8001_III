---
id: prototipobaixa
title: Protótipo Baixa Fidelidade
---
## Introdução

O protótipo de baixa fidelidade é uma etapa essencial no desenvolvimento do projeto, agindo como a ponte entre a ideia abstrata e a implementação real.

Aqui estão os principais motivos que justificam a sua importância:

- Validação Rápida da Arquitetura de Informação: Permite testar a disposição dos elementos, o fluxo de telas e a hierarquia dos dados com a equipe ou clientes antes de escrever qualquer linha de código.

- Economia de Tempo e Recurso (Baixo Custo de Mudança): Alterar uma tela em formato de desenho/texto leva segundos. Descobrir que uma regra de negócio ou campo está faltando depois que o banco de dados e a API já foram codificados custa dezenas de horas de retrabalho.

- Clareza para o Back-End: Ajuda os desenvolvedores a visualizarem exatamente quais endpoints (GET, POST, PUT, DELETE), parâmetros de busca, regras de acesso (perfis) e relacionamentos no banco de dados serão necessários para sustentar a interface.

- Foco na Funcionalidade (Sem Distrações Estéticas): Por não ter cores, logotipos ou tipografia refinada, as discussões se concentram 100% nas regras de negócio, na usabilidade e na lógica do sistema, sem perder tempo com "deveria ser azul ou verde".

- Facilidade na Identificação de Falhas de Escopo: Facilita notar lacunas no fluxo — como telas esquecidas (ex: onde tratar conflito de horários ou onde cadastrar os responsáveis) — antes de avançar para etapas mais complexas.

Em resumo, ele funciona como a planta baixa de uma casa: ninguém constrói as paredes ou escolhe a pintura sem antes validar o desenho das salas e onde passam os canos.

## Metodologia

Iniciei o projeto através dos levantamentos iniciais da equipe, após discussões a ferramenta Figma foi selecionada para produzir o protótipo de baixa fidelidade com base em Wireframes de Baixa Fidelidade (Textual).

## Protótipo de baixa fidelidade

### Versão 1.0

### Tela 1: Login e Autenticação

[![Prototipo 1](../assets/Prototipo/tela1_Login_Autenticacao.png)](../assets/Prototipo/tela1_Login_Autenticacao.png)


### Tela 2: Dashboard Administrativo

[![Prototipo 2](../assets/Prototipo/tela2_Dashboard_Administrativo.png)](../assets/Prototipo/tela2_Dashboard_Administrativo.png)

### Tela 3: Gestão de Alunos

[![Prototipo 3](../assets/Prototipo/tela3_GestaoAlunos.png)](../assets/Prototipo/tela3_GestaoAlunos.png)

### Tela 4: Registro de Presença e Acompanhamento

[![Prototipo 4](../assets/Prototipo/tela4_RegistroDePresenca.png)](../assets/Prototipo/tela4_RegistroDePresenca.png)

### Tela 5: Gestão de Espaços e Ativos

[![Prototipo 5](../assets/Prototipo/tela5_GestaoEspaco_Ativos.png)](../assets/Prototipo/tela5_GestaoEspaco_Ativos.png)

### Tela 6: Agenda e Conflitos

[![Prototipo 6](../assets/Prototipo/tela6_Agenda_Conflitos.png)](../assets/Prototipo/tela6_Agenda_Conflitos.png)


Para conectar essa interface ao back-end, estas são as entidades primárias identificadas no mapa mental:

1. User / Auth: ID, Nome, Email, SenhaHash, Perfil   (ADMIN, TREINADOR, SAUDE, RESPONSAVEL, ALUNOS).
2. Aluno: ID, User_ID, Responsável_ID, DataNascimento, InformaçõesPessoais.
3. Profissional: ID, User_ID, Especialidade (FISIOTERAPEUTA, TREINADOR, NUTRICIONISTA, PSICOLOGO), HorariosDisponiveis.
4. Turma / Atividade: ID, Nome, Modalidade, Treinador_ID, Espaco_ID, DiasHorarios, CapacidadeMaxima.
5. Agendamento: ID, Profissional_ID, Aluno_ID, Espaco_ID, DataHoraInicio, DataHoraFim, Status.
6. Presença: ID, Aluno_ID, Turma_ID, Data, Status (PRESENTE, FALTA), Observacao.
7. Espaco / Ativo: ID, Nome, Capacidade, StatusAtivo, Condicao.
8. Auditoria: ID, User_ID, Acao, TabelaAfetada, Timestamp.

[clique aqui para ver o Protótipo no figma](https://www.figma.com/design/87VnCz8Xq9zmTTrBFEiL4y/prototipo-de-baixa-fidelidade?node-id=0-1&m=dev&t=LIhzbVnf63TpNRgt-1)

## Conclusão

A partir deste protótipo de baixa fidelidade, é possível extrair e validar aspectos estruturais e técnicos do sistema antes de escrever código ou criar o design final:

1- Arquitetura de Dados e Banco de Dados (Modelagem de Entidades): Revela as entidades principais (Aluno, Profissional, Turma, Agendamento, Espaço, Frequência) e como elas se relacionam (por exemplo: um aluno vinculado a um responsável, uma turma vinculada a um treinador e a um espaço).

2- Definição das APIs / Endpoints REST: Permite listar as rotas necessárias para o back-end, como rotas para buscar/filtrar alunos, registrar presenças, consultar e bloquear horários de espaços e checar conflitos de agenda.

3- Matriz de Permissões e Segurança (RBAC): Mapeia quais rotas e dados cada perfil de usuário (Admin, Treinador, Profissional de Saúde, Responsável/Aluno) pode visualizar ou alterar, facilitando a implementação de autenticação e autorização.

4- Mapeamento de Regras de Negócio Críticas: Evidencia fluxos complexos e validações necessárias, tais como detecção automática de conflito de horários, cálculo de ocupação de espaços e bloqueio de locais em manutenção.

5- Navegação e Usabilidade (Jornada do Usuário): Define o fluxo de telas e a hierarquia das informações, garantindo que o usuário consiga cumprir suas tarefas (como fazer uma chamada de presença ou agendar um atendimento) com poucos cliques.

6- Escopo e Esforço de Desenvolvimento: Facilita a estimativa de tempo e complexidade para a equipe de desenvolvimento back-end e front-end, alinhando as expectativas entre desenvolvedores e partes interessadas.

## Referências

> Tecnologias de IAs foram consultadas e serviram como um grande auxiliar no decorrer do projeto. A IA utilizada foi o Gemini.

> Ferramenta Figma. Disponível em https://www.figma.com

## Autor(es)

| Data     | Versão | Descrição                            | Autor(es)                                                                            |
| -------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| 24/09/2026 | 1.0     | Criação do Protótipo de Baixa Fidelidade               | Rodrigo Aquino de Souza
