### Lista dos endpoints da API

### Árvore dos endpoints
```
# Tree:

advogado
    └ /
    └ token
    └ requerentes
requerente
    └ /
ai
    └ odds


```
<br><br>

#### /advogado: CRUD de advogados

Método POST:
```
type: application/json
args: 
    username: o username do advogado a ser criado
    password: a senha do advogado a ser criado
    oab: a oab do advogado a ser criado
    email: o email do advogado a ser criado
return:
    - 201 - advogado criado com sucesso
    - 400 - campos obrigatórios deixados em branco
    - 409 - já existe usuário com email/username inserido
    - 500 - erro interno do servidor
    
    json: 
    - message: mensagem de erro ou sucesso
```

---

#### /advogado/token: Autenticacao de advogados
método GET:
```
type: application/json
args:
    username: o username do advogado a ser autenticado
    password: a senha do advogado a ser autenticado
return:
    - 200 - advogado autenticado com sucesso
    - 400 - campos obrigatórios deixados em branco
    - 401 - credenciais inválidas/usuário não encontrado
    - 500 - erro interno do servidor
    
    json:
    - message: mensagem de erro ou sucesso
    - access_token: em caso de sucesso, o token de acesso do advogado
```
---
#### /advogado/requerentes
método GET:
```
type: application/json
args:
    access_token: token de acesso do advogado cujos requerentes serão consultados
return:
    - 200: consulta realizada com sucesso
    - 400: campos obrigatórios deixados em branco
    - 401: credenciais inválidas/usuário não encontrado
    - 500: erro interno do servidor

    json:
    - message: mensagem de erro ou sucesso
    - requerentes_list: lista dos objetos dos requerentes
```
---
#### /requerente
método POST:
```
type: application/json
args:
    name: nome do requerente a ser criado
    cpf_cnpj: cpf/cnpj fo requerente a ser criado
    pessoa_fisica: (boolean) se o requerente é pessoa física ou jurídica
    access_token: token de acesso do advogado que está cadastrando o requerente
return:
    - 200: cadastro realizado com sucesso
    - 400: campos obrigatórios deixados em branco
    - 401: credenciais inválidas/usuário não encontrado
    - 500: erro interno do servidor

    json:
    - message: mensagem de erro ou sucesso
```
método DELETE:
```
type: application/json
args:
    access_token: token de acesso do advogado que está deletando seu requerente
    requerente_id: ID do requerente a ser deletado
return:
    - 200: requerente deletado com sucesso
    - 400: campos obrigatórios deixados em branco
    - 401: credenciais inválidas/usuário não encontrado
    - 500: erro interno do servidor

    json:
    - message: mensagem de erro ou sucesso
```