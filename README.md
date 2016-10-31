# LI-AWS-Deploy
Linha de comando para deploy das aplicações LI

### Instalação:
Use o comando `pip install li-aws-deploy`

### Uso:

#### Config
> Uso: `li config`
Use para configurar o ambiente de desenvolvimento local (para mais detalhes veja o repositório LI-Docker)

#### Deploy
> Uso: `li deploy`
Use para fazer o deploy de um ambiente local na Amazon. É preciso rodar o comando na pasta-raiz de um dos repositorios clonados pelo comando `li config`

#### Debug
> Uso: `li debug <app>`
Use para abrir a aplicação informada num TTY que permite depuracao via ipdb, pdb, etc... Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.

#### Telnet
> Uso: `li telnet <app> <port>`
Use para abrir a aplicação informada num TTY que faz um telnet dentro do Docker para o endereco 127.0.0.1 e a porta especificada. Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.

#### Test
> Uso: `li test <app> [--django] [--rds]`
Use para rodar os testes unitários da aplicação selecionada usando Python Unittest. Utilize as opções abaixo para configurar os testes:
--django: Use os testes do Django ao invés de Unittest
--rds: Use o banco de dados na Amazon (utilizado pelo Travis) ao invés do banco de dados local, para rodar os testes

#### Bash
> Uso: `li debug <app>`
Use para abrir a aplicação informada num terminal bash (usuario root). Se não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.
