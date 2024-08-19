### Lista dos endpoints da API

### Árvore dos endpoints
```
# Tree:

user
  └ create
  └ auth

```
<br><br>

#### /user/create: Criação de advogados
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

#### /usr/auth: Autenticacao de advogados
```
type: application/json
args:
    username: o username do advogado a ser autenticado
    password: a senha do advogado a ser autenticado
return:
    - 201 - advogado autenticado com sucesso
    - 400 - campos obrigatórios deixados em branco
    - 401 - credenciais inválidas/usuário não encontrado
    - 500 - erro interno do servidor
    
    json:
    - message: mensagem de erro ou sucesso
    - access_token: em caso de sucesso, o token de acesso do advogado

```
