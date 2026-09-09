---
id: pesquisa_descricao_projeto
title: Descrição do Projeto
---


# Sistema de Agendamento e Gerenciamento para a PKZ Lab


## Capa


**Tema:** Desenvolvimento de um Sistema de Agendamento e Gerenciamento (GAAP) para a PKZ Lab


**Período:** 2026.2


**Stakeholder:** PKZ Lab




---


## 1. Contexto


O projeto consiste no desenvolvimento de um recorte inicial do **GAAP (Gestão de Atletas de Alta Performance)**, sistema destinado a uma escola de treinamento esportivo que atende estudantes e conta com profissionais responsáveis por atividades de **treino, fisioterapia, psicologia e nutrição**.


Atualmente, parte da operação depende de controles dispersos, dificultando a obtenção de informações confiáveis sobre **agenda, disponibilidade, capacidade, comparecimento e registros de treinamento**.


Diante desse cenário, o projeto propõe o desenvolvimento de uma **API REST para o backend do GAAP**, com foco inicial na organização da agenda e no apoio à operação de treinamentos. O sistema deverá centralizar as principais informações operacionais e aplicar regras de validação para evitar conflitos de horários, utilização de horários bloqueados e agendamentos acima da capacidade disponível.


O projeto será desenvolvido como um produto acadêmico em um período de quatro meses, utilizando modelagem orientada a objetos, banco de dados relacional, ORM, UML, testes automatizados e práticas de desenvolvimento colaborativo com Git e GitHub.


---


## 2. Objetivo


O objetivo principal é desenvolver uma **API funcional, testada e documentada** para apoiar o gerenciamento da agenda e das atividades relacionadas aos atletas de alta performance.


O sistema deverá permitir:


* autenticação e autorização dos usuários;
* controle de acesso de acordo com o perfil do usuário;
* cadastro e manutenção de estudantes;
* cadastro e manutenção de profissionais;
* cadastro e gerenciamento de serviços;
* configuração de disponibilidade e bloqueios;
* criação e gerenciamento de agendamentos;
* consulta de agendas;
* registro de presença ou ausência;
* registro de realização das atividades;
* criação e finalização de relatórios de treino;
* disponibilização de informações básicas para acompanhamento da operação;
* registro de ações relevantes para auditoria;
* documentação dos endpoints da API.


Além da implementação das funcionalidades, o projeto deverá possuir testes automatizados, documentação técnica e modelos UML e de banco de dados compatíveis com a solução desenvolvida.


---


## 3. Público e perfis de acesso


O sistema terá três perfis principais de usuários.


### Administrador


Responsável pela configuração e manutenção da operação do sistema.


Entre suas atividades estão:


* cadastrar e gerenciar estudantes;
* cadastrar e gerenciar profissionais;
* cadastrar e gerenciar serviços;
* configurar horários de disponibilidade;
* cadastrar bloqueios de agenda;
* administrar os agendamentos;
* consultar informações pendentes.


### Treinador / Coach


Responsável pelo acompanhamento dos estudantes dentro das atividades sob sua responsabilidade.


Entre suas atividades estão:


* consultar sua agenda;
* registrar presença ou ausência;
* registrar a realização da atividade;
* criar relatórios de treino;
* finalizar relatórios de treino.


### Profissional de Saúde


Profissional responsável pelos serviços de **fisioterapia, psicologia ou nutrição**, conforme sua atribuição.


Esse usuário deverá:


* consultar sua agenda;
* visualizar somente os atendimentos relacionados aos serviços aos quais está vinculado;
* acessar os agendamentos sob sua responsabilidade.


O controle de acesso deverá impedir que um usuário utilize funcionalidades ou consulte informações que não estejam relacionadas ao seu perfil.


---


## 4. Escopo do projeto


O escopo corresponde ao **backend inicial do GAAP**, desenvolvido por meio de uma API REST.


A solução deverá contemplar os principais recursos necessários para o funcionamento da agenda e para o acompanhamento básico das atividades.


### 4.1 Autenticação e autorização


O sistema deverá possuir mecanismos para autenticação dos usuários e controle de acesso conforme seus perfis.


As informações de autenticação deverão ser armazenadas de maneira segura, não sendo permitido o armazenamento de senhas em texto puro.


### 4.2 Cadastros básicos


A API deverá fornecer recursos para gerenciamento das informações fundamentais da operação, incluindo:


* estudantes;
* profissionais;
* serviços.


Esses cadastros servirão como base para a configuração da agenda e para a realização dos agendamentos.


### 4.3 Disponibilidade e bloqueios


O administrador deverá conseguir configurar períodos de disponibilidade e registrar bloqueios de agenda.


Essas informações deverão ser consideradas pelo sistema no momento da realização de um agendamento.


### 4.4 Agendamento


O sistema deverá permitir a criação de agendamentos respeitando as regras definidas para a operação.


Um agendamento não deverá ser confirmado quando:


* houver conflito de horário;
* o horário estiver bloqueado;
* a capacidade disponível for excedida.


Essas validações deverão ocorrer no backend.


### 4.5 Consulta de agenda


Os usuários autorizados deverão conseguir consultar os agendamentos relacionados às suas responsabilidades.


A agenda deverá considerar as regras de autorização, evitando que profissionais tenham acesso indevido a informações de outros usuários.


### 4.6 Presença e ausência


O treinador ou profissional autorizado deverá registrar o comparecimento ou a ausência do estudante em uma atividade agendada.


### 4.7 Registro de atividade realizada


O sistema deverá permitir o registro de que a atividade ou sessão prevista no agendamento foi efetivamente realizada.


### 4.8 Relatório de treino


O treinador deverá poder criar e finalizar um relatório relacionado à atividade de treinamento realizada.


O sistema deverá controlar o processo de criação e finalização desse relatório.


### 4.9 Auditoria


A solução deverá manter registros de ações relevantes realizadas no sistema, permitindo acompanhar eventos importantes da operação.


### 4.10 Documentação da API


Os endpoints desenvolvidos deverão ser documentados, permitindo compreender os recursos disponíveis, seus parâmetros, respostas e regras de utilização.


---


## 5. Regras de funcionamento


A API deverá aplicar as regras necessárias para garantir a consistência dos agendamentos e o controle adequado de acesso.


Entre as principais regras estão:


* um usuário somente poderá acessar funcionalidades permitidas ao seu perfil;
* profissionais de saúde deverão visualizar apenas os atendimentos relacionados aos serviços sob sua responsabilidade;
* horários bloqueados não poderão receber novos agendamentos;
* não poderão existir agendamentos conflitantes;
* um agendamento não poderá ultrapassar a capacidade disponível;
* operações realizadas sobre os dados deverão respeitar as permissões definidas para cada perfil;
* informações de autenticação deverão ser armazenadas de forma segura.


As regras específicas do negócio que ainda não estiverem definidas no cenário deverão ser validadas com o cliente antes de serem consideradas requisitos definitivos.


---


## 6. Análise da solução


O principal problema identificado está relacionado à dispersão das informações utilizadas na operação da escola de treinamento.


A ausência de uma fonte confiável e centralizada pode dificultar:


* o controle da agenda;
* a identificação de horários disponíveis;
* o controle da capacidade;
* o acompanhamento da presença dos estudantes;
* o registro das atividades realizadas;
* a elaboração e manutenção dos relatórios de treino.


A proposta do GAAP busca centralizar essas operações em uma API, permitindo que diferentes funcionalidades utilizem uma mesma base de dados e as mesmas regras de negócio.


A solução também estabelece diferentes níveis de acesso, permitindo que administradores, treinadores e profissionais de saúde utilizem o sistema de acordo com suas responsabilidades.


---


## 7. Tecnologias e abordagem


O desenvolvimento do projeto deverá utilizar uma abordagem orientada a objetos e um banco de dados relacional.


Entre os principais elementos técnicos previstos estão:


* modelagem orientada a objetos;
* banco de dados relacional normalizado;
* ORM;
* API REST;
* autenticação e autorização;
* validação de dados;
* tratamento de erros;
* testes automatizados;
* documentação de endpoints;
* UML;
* Git e GitHub para versionamento e colaboração.


O banco de dados deverá utilizar **chaves primárias, chaves estrangeiras, restrições de unicidade e índices** adequados às consultas realizadas pela agenda.


---


## 8. Segurança e proteção de dados


Como o sistema poderá trabalhar com dados pessoais de estudantes e profissionais, a segurança deverá ser considerada desde a modelagem até a implementação.


Entre as medidas previstas estão:


* autenticação de usuários;
* autorização baseada em perfil;
* armazenamento seguro de senhas por meio de hash;
* validação das informações recebidas pela API;
* restrição de acesso a recursos conforme as responsabilidades do usuário;
* tratamento adequado de erros;
* proteção contra acesso indevido aos dados.


A **Lei Geral de Proteção de Dados Pessoais (LGPD)** deverá ser considerada nas decisões relacionadas ao tratamento e armazenamento de dados pessoais.


Como o GAAP possui serviços de fisioterapia, psicologia e nutrição, eventuais informações relacionadas à saúde deverão receber tratamento compatível com as exigências aplicáveis aos dados pessoais sensíveis.


Entretanto, o cenário estabelece que **registros clínicos detalhados estão fora do escopo do recorte inicial**, portanto o projeto acadêmico não deverá implementar um prontuário clínico completo.


---


## 9. Itens fora do escopo


Para manter o foco no backend da agenda e da operação de treinamento, os seguintes recursos não fazem parte do recorte inicial:


* pagamentos;
* gateway de pagamento;
* cobrança recorrente;
* controle financeiro;
* prontuário clínico detalhado;
* assinatura digital de documentos clínicos;
* cálculos avançados de força por sexo ou idade;
* aplicativo mobile;
* integração com QR Code;
* integração com WhatsApp;
* envio de notificações por e-mail;
* funcionamento offline;
* dashboards avançados;
* data warehouse;
* suporte a múltiplos clientes por meio de arquitetura multi-tenant;
* integrações públicas externas;
* geração de arquivos PDF;
* upload de fotografias.


Esses recursos poderão ser considerados futuramente, mas não devem fazer parte do MVP definido para este projeto.


---


## 10. Oportunidade


A principal oportunidade identificada está na **centralização das informações da operação esportiva em uma única API**, permitindo que os diferentes perfis utilizem os mesmos dados e regras de negócio.


A aplicação de validações automáticas para conflitos, bloqueios e capacidade pode reduzir inconsistências nos agendamentos, enquanto o controle de presença e os relatórios de treino fornecem uma base organizada para o acompanhamento das atividades.


A arquitetura também poderá servir como base para futuras extensões do sistema, sem que essas funcionalidades precisem ser implementadas no recorte atual.


---


## 11. Evoluções futuras


Embora estejam fora do escopo do MVP, o cenário prevê possibilidades de evolução do sistema, como:


* controle de créditos e pagamentos;
* lista de espera;
* notificações de vencimento e lembretes;
* perfil unificado do estudante;
* avaliação física;
* dashboards e recursos de BI;
* webhooks;
* aplicativo mobile.


Essas funcionalidades não serão tratadas como requisitos do sistema atual, mas podem ser consideradas extensões futuras.


---


## 12. Conclusão


O projeto propõe o desenvolvimento de um **backend para o Sistema de Gestão de Atletas de Alta Performance (GAAP)**, com foco na organização da agenda e no suporte às atividades de treinamento.


A solução deverá centralizar os cadastros básicos, a disponibilidade, os bloqueios, os agendamentos, a consulta de agenda, o controle de presença, o registro das atividades e os relatórios de treino, utilizando autenticação, autorização e validações para garantir o funcionamento adequado da operação.


O recorte foi definido de maneira a concentrar o esforço do projeto acadêmico nas funcionalidades essenciais do backend, mantendo fora do MVP recursos financeiros, clínicos avançados, mobile, integrações externas e análises avançadas.


Dessa forma, o GAAP inicial deverá fornecer uma base funcional, testada e documentada para apoiar a operação da escola de treinamento e possibilitar futuras evoluções do sistema.
