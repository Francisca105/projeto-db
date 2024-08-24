# Projeto de Bases de Dados 2023/2024

## Resumo

Este projeto foi desenvolvido no âmbito da cadeira de Bases de Dados do Instituto Superior Técnico e consiste na criação de um modelo de dados para uma empresa de prestação de cuidados de saúde. O projeto foi dividido em duas entregas principais, que envolveram a modelação Entidade-Associação, conversão para um modelo relacional, e a implementação de consultas utilizando Álgebra Relacional e SQL.

## Entrega 1: Modelação Entidade-Associação e Conversão para Modelo Relacional

### 1. Modelação Entidade-Associação

Nesta primeira fase, foi criado um modelo Entidade-Associação que representa os requisitos de informação da aplicação. O domínio do problema envolvia a gestão de clínicas, profissionais de saúde (médicos e enfermeiros), pacientes, consultas, e receitas médicas.

#### Principais Entidades e Relações

* **Clínica**: Identificada pelo nome, com morada e telefone.
* **Profissional de Saúde**: Inclui médicos e enfermeiros, identificados pelo NIF, com atributos adicionais como nome, morada, telefone e IBAN. Médicos possuem uma especialidade.
* **Paciente**: Identificado pelo número do SNS, com atributos como nome, NIF, data de nascimento, morada e telefone.
* **Consulta**: Associação entre paciente, médico, e clínica, com registo de sintomas e, eventualmente, receitas médicas.

### 2. Conversão E-A–Relacional

O modelo Entidade-Associação foi convertido para um modelo relacional seguindo a notação aprendida nas aulas. Foram identificadas restrições de integridade que completam o modelo, assegurando que apenas situações válidas são representadas na base de dados.

#### Modelo Relacional

* Tabelas para cada entidade (e.g., **Clinica**, **Medico**, **Paciente**).
* Relações com chaves estrangeiras para garantir a integridade referencial.
* Restrições adicionais como `unique` e `FK` foram definidas conforme necessário.

## Entrega 2: Álgebra Relacional & SQL

### 1. Consultas em Álgebra Relacional

Nesta fase, foram formuladas consultas para responder a interrogações específicas sobre o esquema relacional.

### 2. Consultas em SQL

As consultas foram também implementadas em SQL, abrangendo questões como a obtenção de pacientes que consultaram médicos de todas as especialidades e identificação de médicos com pacientes mais fiéis.

## Estrutura do Projeto

* **Diagrama Entidade-Associação**: `modelo_EA.drawio`
* **Modelo Relacional**: `modelo_relacional.sql`
* **Consultas em SQL**: `consultas.sql`
* **Relatório**: `relatorio_entrega1.pdf`, `relatorio_entrega2.pdf`

## Conclusão

O projeto proporcionou uma compreensão aprofundada dos processos de modelação de dados e da aplicação prática da Álgebra Relacional e SQL para a manipulação de bases de dados.
