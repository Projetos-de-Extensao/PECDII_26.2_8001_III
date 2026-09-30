---
id: legislacao
title: Legislação e Regras Aplicáveis
---

# Guia Jurídico de Desenvolvimento do GAAP

## Introdução

Este documento é um guia informativo para a equipe que desenvolve o backend do GAAP. Seu foco é traduzir as normas relevantes em cuidados de projeto, implementação, testes e documentação para a API de agenda e operação de treinamentos, que inclui cadastros, agendamentos, presença, relatórios de treino, autenticação, autorização e auditoria. O produto pode tratar dados de crianças e adolescentes; dados de saúde também podem surgir se um registro revelar informação clínica.

Este material é informativo, não constitui parecer jurídico e não define as bases legais ou obrigações operacionais da organização que utilizará o sistema. A equipe deve evitar decisões de produto que pressuponham permissões para tratar dados sem requisito aprovado. O MVP documentado não inclui prontuário clínico detalhado.

## 1. Normas diretamente relevantes

### 1.1 Lei Geral de Proteção de Dados Pessoais (LGPD)

Lei nº 13.709/2018 (LGPD) aplica-se ao tratamento de dados pessoais em meios digitais. No GAAP, isso inclui dados cadastrais e de contato, credenciais, vínculos entre estudantes e responsáveis, agenda, presença e registros de treino associados a uma pessoa identificada ou identificável.

Os princípios do art. 6º devem influenciar as decisões técnicas:

- **Finalidade, adequação e necessidade:** modelar e expor apenas os campos necessários às funções previstas. Não acrescentar CPF, endereço, data de nascimento completa ou outros identificadores sem requisito funcional claro.
- **Qualidade e transparência:** manter dados corretos e compreensíveis; documentar no contrato da API quais campos são coletados e para que servem. Não declarar que a equipe determinou a base legal do tratamento.
- **Segurança e prevenção:** proteger dados contra acesso indevido, alteração, perda ou divulgação, desde o desenho até a execução do sistema (arts. 46 e 49).
- **Responsabilização:** manter decisões de modelagem e segurança rastreáveis, com testes e documentação que demonstrem como as regras de acesso e proteção são aplicadas.

Dados referentes à saúde são dados pessoais sensíveis (art. 5º, II), sujeitos às hipóteses específicas do art. 11. Legítimo interesse não é hipótese geral para tratar dados sensíveis. Como prontuários clínicos estão fora do MVP, relatórios de treino não devem receber campos livres destinados a diagnósticos, tratamentos ou anotações clínicas.

A LGPD prevê direitos dos titulares, incluindo confirmação e acesso, correção, portabilidade nos termos aplicáveis, eliminação ou bloqueio nas hipóteses legais e informação sobre compartilhamentos (art. 18). A API deve permitir localizar, corrigir e exportar ou excluir registros conforme as funcionalidades aprovadas, sem codificar retenção indefinida. A eliminação pode ter exceções legais (art. 16); por isso, não apagar trilhas de auditoria automaticamente sem considerar sua finalidade e obrigação de conservação.

A lei também exige medidas de segurança (arts. 46 e 49), registro das operações de tratamento (art. 37) e comunicação de incidentes que possam acarretar risco ou dano relevante, conforme o art. 48 e a regulamentação da ANPD. A equipe deve preservar evidências técnicas necessárias e encaminhar rapidamente informações sobre incidentes aos responsáveis pela operação, sem assumir atribuições de comunicação jurídica em nome deles.

### 1.2 Crianças e adolescentes: LGPD e Estatuto da Criança e do Adolescente

O projeto prevê alunos menores de idade e vínculos com responsáveis. O ECA (Lei nº 8.069/1990) considera criança a pessoa com menos de 12 anos e adolescente aquela entre 12 e 18 anos incompletos. O art. 14 da LGPD exige que o tratamento de dados de crianças e adolescentes observe seu melhor interesse. Para dados de crianças tratados com base em consentimento, exige consentimento específico e destacado de pelo menos um dos pais ou responsável legal; a equipe não deve presumir que consentimento seja a base adequada para todos os tratamentos.

Implicações para o desenvolvimento:

- Implementar autorização por vínculo: um responsável só pode consultar ou operar dados dos estudantes associados à sua conta, e um profissional só pode acessar os atendimentos sob sua responsabilidade.
- Verificar autorização em cada endpoint e para cada objeto solicitado. Não confiar em identificadores enviados pelo cliente da API como prova de vínculo ou permissão.
- Evitar divulgar dados de menores em respostas, mensagens de erro, logs, exemplos de API, fixtures e documentação. Usar dados sintéticos em desenvolvimento e testes.
- Projetar as mensagens e contratos da API para permitir que uma interface apresente informações de tratamento em linguagem clara e apropriada, sem armazenar consentimento ou declaração de responsável por padrão, a menos que haja requisito aprovado.
- Considerar privacidade, dignidade, imagem e melhor interesse da criança e do adolescente como critérios de revisão das decisões de produto e segurança.

### 1.3 Marco Civil da Internet

A Lei nº 12.965/2014 prevê, no art. 15, guarda de registros de acesso a aplicações de internet por seis meses para provedores de aplicação constituídos como pessoa jurídica e que exerçam a atividade de forma organizada, profissional e com fins econômicos. Essa obrigação depende do enquadramento da aplicação e deve ser considerada na arquitetura de produção.

Registros de acesso à aplicação não são o mesmo que a auditoria de ações de negócio. Não aplicar automaticamente o prazo de seis meses a todos os logs: registrar apenas o necessário, proteger os registros contra acesso e alteração indevidos e evitar incluir senhas, tokens ou conteúdo pessoal desnecessário.

## 2. Propriedade intelectual e dependências

A Lei nº 9.609/1998 protege programas de computador; a Lei nº 9.610/1998 disciplina direitos autorais. A equipe deve:

- Usar bibliotecas, frameworks, imagens, diagramas e materiais de terceiros de acordo com suas licenças e condições de atribuição.
- Registrar as dependências e suas licenças no repositório; não copiar código ou conteúdo de aplicações analisadas sem autorização.
- Não publicar dados reais, segredos, credenciais, especificações confidenciais do cliente ou conteúdo que identifique estudantes.

## 3. Regras técnicas para implementação e testes

As medidas abaixo são salvaguardas de engenharia derivadas dos princípios legais e dos requisitos de segurança do projeto. A lei não determina uma tecnologia específica; a equipe deve escolher controles adequados à arquitetura e comprovar seu funcionamento por testes.

1. Armazenar senhas somente com hash apropriado para senhas; nunca em texto puro ou em logs.
2. Aplicar autorização no backend em toda operação, não apenas na interface. Validar o perfil e o vínculo com o recurso solicitado em cada leitura e alteração.
3. Manter os acessos de profissionais de saúde restritos aos serviços e atendimentos que lhes foram atribuídos. Acesso administrativo amplo deve ser limitado a pessoas autorizadas.
4. Coletar campos pessoais mínimos, validar entradas e evitar dados sensíveis em parâmetros de URL, mensagens de erro e registros de auditoria.
5. Manter auditoria de ações relevantes com usuário, ação, recurso e instante, sem gravar senhas, tokens, conteúdo clínico ou payloads completos desnecessários. Proteger os registros contra alteração por usuários comuns.
6. Usar canal criptografado em produção, guardar segredos fora do código-fonte, restringir acesso ao banco e às cópias de segurança e testar o procedimento de restauração.
7. Definir dados sintéticos para desenvolvimento e testes. Não usar dados reais de alunos em ambientes acadêmicos ou repositórios.
8. Tratar a exclusão e a correção de dados de forma consistente entre registros relacionados, respeitando obrigações de retenção e mantendo apenas a trilha de auditoria necessária.
9. Separar ambientes de desenvolvimento, teste e produção; limitar dados e credenciais por ambiente e nunca incluir segredos no repositório.
10. Preparar registros técnicos e procedimento interno para detectar, conter e investigar incidentes. Não inserir dados pessoais em rastreamento de erros ou alertas sem necessidade.
11. Testar autorização positiva e negativa para cada perfil, incluindo tentativas de consultar ou alterar registros de outro aluno, responsável ou profissional.
12. Testar correção, exclusão e exportação dos dados nas rotas aplicáveis, verificando relações, cópias e auditoria, sem ignorar eventuais obrigações de retenção.

## 4. Revisão jurídica no fluxo de desenvolvimento

- Antes de adicionar um novo campo pessoal, identificar sua finalidade no requisito e verificar se é realmente necessário.
- Antes de criar um novo tipo de registro, avaliar se ele pode revelar dado sensível ou dado de menor e aplicar autorização e proteção compatíveis.
- Revisar qualquer alteração de endpoint que amplie quem pode consultar, exportar, alterar ou excluir informações.
- Revisar logs, mensagens de erro, documentação, dados de exemplo e relatórios para impedir exposição acidental de dados pessoais.
- Registrar decisões de segurança e privacidade nas issues e pull requests relacionadas; incluir testes de acesso e proteção como critérios de aceite.
- Quando um requisito não esclarecer finalidade, campos, acesso ou retenção, não inferir permissões amplas nem coletar mais dados. Registrar a lacuna e manter a implementação limitada ao que está especificado.

## Conclusão

Para a equipe de desenvolvimento, os deveres mais diretamente traduzidos em código são minimizar dados, proteger dados pessoais e sensíveis, aplicar autorização por perfil e vínculo, evitar dados reais em ambientes de desenvolvimento, permitir operações compatíveis com os direitos dos titulares e testar esses controles. O ECA reforça que dados de crianças e adolescentes exigem consideração especial do melhor interesse. O Marco Civil pode acrescentar requisitos específicos para registros de acesso à aplicação, conforme o enquadramento legal do serviço.

## Referências oficiais

> [Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais (LGPD)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).

> [Lei nº 8.069/1990 — Estatuto da Criança e do Adolescente (texto compilado)](https://www.planalto.gov.br/ccivil_03/leis/L8069compilado.htm).

> [Lei nº 12.965/2014 — Marco Civil da Internet](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm).

> [Lei nº 9.609/1998 — proteção da propriedade intelectual de programa de computador](https://www.planalto.gov.br/ccivil_03/leis/l9609.htm).

> [Lei nº 9.610/1998 — direitos autorais](https://www.planalto.gov.br/ccivil_03/leis/l9610.htm).

> [ANPD — Resolução CD/ANPD nº 15, de 24 de abril de 2024 (comunicação de incidentes de segurança)](https://www.gov.br/anpd/pt-br/assuntos/legislacao/regulamentacoes-anpd/resolucao-cd-anpd-no-15-de-24-de-abril-de-2024).

## Versionamento

| Data | Versão | Descrição | Autor |
|---|---:|---|---|
| 29/09/2026 | 1.0 | Elaboração do levantamento de leis e regras aplicáveis ao escopo do GAAP | Bernardo Chagas |
