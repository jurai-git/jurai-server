# jurai-server

## Sobre o repositório

Este repositório contém o código fonte para o servidor do JurAI.
O servidor é escrito em Python, utilizando Flask como framework backend, e Flask SqlAlchemy + MySQL como banco de dados.

Para conhecer mais sobre a estrutura do projeto e como você pode contribuir para ele com código, veja as [docs](docs) do projeto.

### Quickstart

Para rapiadmente configurar o servidor com algumas configurações básicas, e tê-lo funcionando no modo de desenvolvimento em seu localhost, você poderá seguir os passos a seguir:

#### 1 - Configurar o ambiente

Para configurar o ambiente, entre na raiz do projeto, e execute:

Crie o venv: `python -m venv venv`

Ative o venv: `source venv/bin/activate`

E, finalmente, instale os pacotes necessários: 
`pip install -r requirements.txt`.

#### 2 - Configurar o banco de dados

Para configurar as informações de banco de dados, você deverá criar um arquivo `.env` no diertório /app.
Este arquivo deverá seguir o seguinte modelo:

```
# file: /app/.env
SECRET_KEY = "dev"

MYSQL_HOST = '111.222.333.4'
MYSQL_USER = 'user'
MYSQL_PASSWORD = 'pwd'
MYSQL_DB = 'database_schema'
```
Troque as informações do banco de dados de acordo com o seu banco. Você não poderá ter uma tabela chamada `advogado` em seu banco, pois uma tabela de mesmo nome será criada pelo código.

#### 3 - Executar o server

Após fazer essas configurações básicas, você poderá executar o servidor.
Para fazer isso, basta executar:

`flask run`
