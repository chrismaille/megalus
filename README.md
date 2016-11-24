# MegTools
Linha de comando para deploy das aplicações Megalus

### Instalação:
Use o comando `pip install meg-tools`

### Uso:

#### Config
> Uso: `meg config`

Use para configurar o ambiente de desenvolvimento local (para mais detalhes veja o repositório LI-Docker)

#### Deploy
> Uso: `meg deploy`

Use para fazer o deploy de um ambiente local na Amazon. É preciso rodar o comando na pasta-raiz de um dos repositorios clonados pelo comando `li config`

#### Debug
> Uso: `meg debug <app>`

Use para abrir a aplicação informada num TTY que permite depuracao via ipdb, pdb, etc... Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.

#### Telnet
> Uso: `meg telnet <app> <port>`

Use para abrir a aplicação informada num TTY que faz um telnet dentro do Docker para o endereco 127.0.0.1 e a porta especificada. Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.

#### Test
> Uso: `meg test <app> [--django] [--rds]`

Use para rodar os testes unitários da aplicação selecionada usando Python Unittest. Utilize as opções abaixo para configurar os testes:

* --django: Use os testes do Django ao invés de Unittest
* --rds: Use o banco de dados na Amazon (utilizado pelo Travis) ao invés do banco de dados local, para rodar os testes

#### Bash
> Uso: `meg debug <app>`

Use para abrir a aplicação informada num terminal bash (usuario root). Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.

#### Run
> Uso: `meg run <app>`

Roda a aplicação informada e suas dependências ou todas as aplicações/containers se não informar nenhuma aplicação.

#### Build
> Uso: `meg build <app> [--no-cache]`

Use para fazer a build do container da aplicação selecionada. Se nenhuma aplicação for informada, será feito a build de todos os containers:

* --no-cache: Durante a build, forçar o download de todas as livrarias/dependencias
