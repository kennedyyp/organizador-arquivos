# Organizador de arquivos

Automação local em Python para organizar arquivos no Debian 13.

## Estado do projeto

Estrutura inicial de versionamento. A implementação será adicionada após a
configuração do repositório e a definição das regras de organização.

## Objetivo

Organizar arquivos soltos da pasta de Downloads por tipo, com simulação,
proteção contra sobrescrita e registro de movimentações para desfazer.
Sem upload de arquivos ou backup em nuvem.

## Tecnologias

- Python 3.13: integração com arquivos e diretórios pela biblioteca padrão.
- `venv`: ambiente de dependências separado dos pacotes do Debian.
- Git: histórico local de alterações.
- GitHub: hospedagem do código e colaboração.

## Preparar o ambiente no Debian 13

```bash
sudo apt update
sudo apt install git gh python3 python3-venv
```

Depois de clonar este repositório e entrar nele:

```bash
python3 -m venv .venv
.venv/bin/python -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
```

A última linha deve ser `True`. Não há dependências externas para instalar neste estágio.
O programa ainda não está implementado neste repositório.

## Cuidados de versionamento

O repositório é destinado a código e documentação. Não adicione arquivos reais de
Downloads, documentos de clientes, credenciais ou registros com caminhos pessoais.
O `.gitignore` exclui ambientes virtuais e algumas pastas locais, mas não substitui
conferir `git diff --cached` antes de cada commit.

## Publicação e instalação

Esta é uma ferramenta local: a entrega prevista é clonar o repositório, criar o
ambiente virtual e executar como usuário comum. Não precisa de servidor web,
portas abertas ou serviço de nuvem para organizar os arquivos.
