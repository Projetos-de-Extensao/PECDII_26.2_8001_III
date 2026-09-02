---
id: pesquisa_ativos_e_espacos
title: Gestão de Ativos e Espaços
---

# Gestão de Ativos e Espaços

> Pesquisa sobre gestão de ativos e gestão de espaços e como esses conceitos podem ser aplicados ao projeto **PKZ Lab**, que integra atividades esportivas e atendimentos especializados voltados ao público infantil.

## 1. O que é gestão de ativos?

A **gestão de ativos** (*Asset Management*) consiste em administrar os bens de uma organização durante seu ciclo de vida, buscando garantir que eles estejam disponíveis, em boas condições e contribuam para os objetivos da organização. Envolve aspectos como:

- Utilização
- Desempenho
- Manutenção
- Riscos
- Substituição dos ativos

No contexto de *Facilities Management*, a gestão de ativos está relacionada à manutenção de espaços, infraestrutura e recursos para garantir que estejam seguros, disponíveis e operacionais. A IBM, por exemplo, inclui entre as atividades de gestão de instalações a preservação de ativos e o planejamento dos espaços.

Para a PKZ Lab, os ativos podem incluir tanto recursos diretamente relacionados ao esporte quanto equipamentos utilizados nos atendimentos especializados.

### Exemplos de ativos

**Esportivos:**

- Bolas
- Redes
- Traves
- Tabelas
- Equipamentos de academia
- Colchonetes e tatames

**Atendimento e saúde:**

- Equipamentos de fisioterapia
- Macas
- Materiais para avaliação física
- Equipamentos de avaliação
- Computadores e equipamentos utilizados pelos profissionais

Dessa forma, a gestão de ativos permite saber quais recursos existem, onde estão, qual é seu estado e se estão disponíveis para utilização.

## 2. Gestão de espaços

A **gestão de espaços** consiste em organizar e acompanhar os ambientes físicos disponíveis em uma organização. Entre as informações normalmente relevantes estão:

- Localização
- Capacidade
- Ocupação
- Disponibilidade
- Finalidade de cada espaço

No caso da PKZ Lab, isso pode envolver diferentes tipos de ambientes:

- Quadras
- Campos
- Academias
- Salas de treinamento
- Salas de fisioterapia
- Consultórios
- Salas destinadas a acompanhamento psicológico.
- Outros ambientes de atendimento

Assim, um espaço não precisa necessariamente ser esportivo. Uma sala utilizada por um fisioterapeuta também é um recurso que precisa ser administrado pelo sistema.

## 3. Relação entre espaços e atividades

Um dos pontos mais importantes para a PKZ Lab é relacionar o tipo de atividade ao espaço adequado.

| Atividade | Espaço |
|---|---|
| Treino de futebol | Campo |
| Aula de basquete | Quadra |
| Treinamento funcional | Academia |
| Fisioterapia | Sala de fisioterapia |
| Atendimento psicológico | Consultório/sala adequada |

Isso permite que o sistema saiba quais espaços podem ser utilizados para cada tipo de atividade.

Também evita que um usuário tente realizar uma atividade em um ambiente inadequado ou que dois atendimentos utilizem simultaneamente o mesmo espaço.

## 4. Gestão da disponibilidade

A gestão de espaços está diretamente relacionada ao agendamento.

O sistema deve ser capaz de determinar se determinado espaço está disponível em um horário específico, considerando reservas existentes, horários de funcionamento, manutenção e possíveis bloqueios.

**Exemplo 1 — Sala de Fisioterapia:**
A sala está disponível das 8h às 18h. Um atendimento é marcado das 14h às 15h. Nesse período, a sala não deve ser disponibilizada para outro atendimento.

**Exemplo 2 — Quadra:**
A Quadra 01 está reservada para uma aula de basquete das 16h às 17h. Outro usuário não pode realizar uma reserva para a mesma quadra nesse intervalo.

Sistemas de gestão de espaços utilizam justamente informações de capacidade, ocupação e disponibilidade para administrar reservas e evitar conflitos.

## 5. Ativos associados aos espaços

Os ativos podem ser relacionados aos espaços onde são utilizados.

| Espaço | Ativos associados |
|---|---|
| Sala de Fisioterapia | Maca, equipamentos de fisioterapia, materiais de avaliação |
| Academia | Esteiras, bicicletas, aparelhos de musculação |
| Quadra | Traves, redes, tabelas, equipamentos esportivos |

Essa relação permite identificar onde determinado ativo está localizado e quais recursos estão disponíveis em determinado ambiente.

Também facilita a manutenção. Caso um equipamento esteja quebrado ou em manutenção, seu status pode ser alterado sem necessariamente tornar todo o espaço indisponível.

## 6. Manutenção e interdição

A gestão de ativos e espaços também está relacionada à manutenção.

Um equipamento pode precisar de manutenção preventiva ou corretiva, enquanto um espaço inteiro pode precisar ser temporariamente interditado.

**Manutenção de ativo (parcial):**
Uma esteira da academia apresenta defeito → o equipamento é marcado como indisponível, mas a academia continua funcionando.

**Manutenção de espaço (total):**
A sala de fisioterapia passa por manutenção → a sala fica indisponível durante determinado período e novos atendimentos não podem ser agendados para ela.

Isso cria uma relação direta entre:

```
Ativo → Espaço → Manutenção → Disponibilidade → Agendamento
```

Esse tipo de integração é especialmente importante em uma organização que reúne atividades esportivas e atendimentos especializados.

## 7. Particularidade da PKZ Lab: público infantil

O fato de a PKZ Lab ser voltada para crianças também é relevante para a gestão dos espaços.

Além dos espaços esportivos, podem existir ambientes destinados a avaliações, acompanhamento e atendimento profissional.

Isso significa que o sistema pode precisar lidar com diferentes categorias de utilização:

**Atividades esportivas** → treinos, aulas e práticas esportivas.

**Atendimentos especializados** → fisioterapia, avaliação e, caso confirmado, psicologia.

A literatura sobre medicina esportiva pediátrica mostra que a integração entre diferentes profissionais pode ser relevante no atendimento de jovens atletas. Pesquisas discutem, por exemplo, a integração da psicologia aos serviços de medicina esportiva pediátrica e a colaboração entre profissionais para atender necessidades físicas e psicológicas dos jovens.

Isso reforça que, no contexto da PKZ Lab, espaços e ativos não precisam estar relacionados exclusivamente ao treinamento esportivo.

## 8. Gestão integrada dos recursos

Considerando o funcionamento da PKZ Lab, pode ser interessante pensar nos recursos em conjunto:

```
Criança → atividade/atendimento → profissional → espaço → equipamentos → horário
```

Por exemplo, para uma sessão de fisioterapia, o sistema poderia precisar verificar:

- se o fisioterapeuta está disponível;
- se a sala está disponível;
- se os equipamentos necessários estão disponíveis;
- se o horário está dentro do funcionamento da unidade;
- se não existe outro atendimento utilizando os mesmos recursos.

Para um treino esportivo, a lógica seria semelhante:

- professor disponível;
- quadra/campo disponível;
- capacidade adequada;
- equipamentos necessários disponíveis.

Essa abordagem aproxima a gestão de ativos e espaços daquilo que o grupo está pesquisando sobre agendamento multidisciplinar.

## 9. Benefícios para a PKZ Lab

Uma gestão integrada de ativos e espaços poderia trazer:

- **Maior organização**: permite centralizar informações sobre ambientes e equipamentos.
- **Redução de conflitos**: evita que um espaço ou recurso seja reservado simultaneamente.
- **Melhor utilização dos espaços**: facilita identificar horários disponíveis e ambientes subutilizados.
- **Controle de manutenção**: permite identificar equipamentos ou ambientes indisponíveis.
- **Integração entre esporte e atendimento**: possibilita administrar no mesmo sistema espaços esportivos e espaços destinados aos profissionais de saúde.
- **Melhor planejamento**: facilita saber quais recursos estão disponíveis antes de realizar uma reserva.

## 10. O que pode ser aproveitado no projeto PKZ Lab?

A pesquisa sugere algumas funcionalidades que podem ser avaliadas como requisitos do sistema:

| Área | Possível funcionalidade |
|---|---|
| Espaços | Cadastro dos ambientes |
| Espaços | Informações de capacidade e finalidade |
| Espaços | Controle de disponibilidade |
| Espaços | Bloqueio temporário |
| Ativos | Cadastro de equipamentos |
| Ativos | Associação do ativo a um espaço |
| Ativos | Controle do estado do equipamento |
| Manutenção | Registro de manutenção |
| Manutenção | Indisponibilização de ativos/espaços |
| Agendamento | Reserva de espaços |
| Agendamento | Verificação de conflitos |
| Profissionais | Associação de profissionais aos espaços/atividades |

> **Importante:** essas são possibilidades identificadas na pesquisa, não necessariamente requisitos já definidos da PKZ Lab. O cliente ainda precisa decidir quais realmente fazem parte do escopo.
>

## Fontes principais

- **IBM — Facilities Management**: conceito de gestão de instalações, preservação de ativos, espaços e infraestrutura.
- **PubMed — The Role of Psychologists in Sport Medicine Practice**: integração de psicologia e medicina esportiva pediátrica.
- **PubMed — Integrating Psychological Care into Pediatric Sports Medicine (2026)**: modelos de integração entre psicologia e medicina esportiva pediátrica.
- **PubMed — Interdisciplinary Return to Play Management for Pediatric Concussion**: colaboração interdisciplinar envolvendo fisioterapeutas e outros profissionais no acompanhamento de atletas jovens.
- **PubMed — Pediatric Physical Therapy Management (2026)**: destaca planos de cuidado colaborativos e encaminhamento para outros profissionais no atendimento pediátrico.
