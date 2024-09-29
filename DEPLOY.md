# Deploy do server

Para fazer o deploy do server, será utilizado um container docker.
Construa-o com `docker build -t {nome} .`, no diretório raiz.

Após isso, você poderá executar o servidor utilizando `docker run -d -p 8000:8000 {nome}`
