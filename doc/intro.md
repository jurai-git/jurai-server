# Documentação do projeto

## Introdução e estrutura básica

Como apontado no [readme](../README.md), este server é escrito em python, utilizando Flask, SqlAlchemy e MySQL.

### Estrutura
Aqui está uma estrutura básica do projeto:

```
.
├── app
│  ├── config.py
│  ├── __init__.py
│  └── main
│     ├── controller
│     │   └── __init__.py
│     ├── extensions.py
│     ├── __init__.py
│     ├── model
│     │   └── __init__.py
│     └── service
│         └── __init__.py
│
└── models

```

Como podemos ver, o projeto tem 4 componentes principais: 
- app/main/model - pasta que guarda os modelos ORM do projeto
- app/main/service - pasta que guarda os serviços do projeto
- app/main/controller - pasta que guarda os controladores do flask do projeto (juntamente com os endpoints)
- models - pasta que guarda os modelos de IA do projeto

Além disso, cada diretório contém um arquivo `__init__.py`, que serve para declarar pacotes do python, e para inicializar ditos pacotes.

### Fluxo lógico

O programa é iniciado no arquivo `app/__init__.py`. Este arquivo é responsável pela inicialização básica do flask:
- A criação do `app`
- A inicialização do banco de dados
- A inicialização de extensões
- A inicialização de serviços
- O registro do blueprint inicial

Todas essas estapas estão completamente contidas no arquivo init, com exceção da inicialização de extensões, que é feita no arquivo `app/main/extensions.py`.

Nessa inicialização, o programa criar a blueprint raiz do projeto, localizada em `app/main/__init__.py`. 
Essa blueprint raiz é a responsável por configurar todas as outras blueprints, loalizadas nos controllers.

