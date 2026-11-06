# Organizador de arquivos

Automação local em Python para organizar arquivos no Debian 13.

## Estado do projeto

Primeira versão de execução manual, com simulação por padrão e testes automatizados.
Ainda não há agendamento ou monitoramento contínuo.

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

## Executar e testar

Primeiro rode os testes com arquivos fictícios em diretórios temporários:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Informe explicitamente a pasta a organizar. Por exemplo, se a sua pasta de
Downloads estiver em `$HOME/Downloads`, simule:

```bash
.venv/bin/python organizador.py "$HOME/Downloads"
```

Confira os destinos mostrados. Para executar as movimentações:

```bash
.venv/bin/python organizador.py "$HOME/Downloads" --aplicar
```

Use o caminho real da sua pasta: ele pode ser diferente conforme sua configuração
XDG. O script não detecta esse caminho automaticamente nesta versão.
Mantenha o projeto fora da pasta organizada e execute como usuário comum, sem sudo.

## Regras de organização

- Categorias: Imagens, PDFs, Documentos, Planilhas, Apresentacoes, Videos, Audios,
  Compactados, Pacotes e Codigo. O mapeamento de extensões está em `CATEGORIAS`.
- Apenas arquivos soltos; não percorre subpastas nem move links simbólicos.
- Preserva nomes e acrescenta um número em caso de colisão.
- Arquivos desconhecidos, ocultos e temporários permanecem onde estão.
- Compara identidade, tamanho e modificação dos arquivos em duas verificações,
  separadas por 2 segundos. Ajuste com `--estabilidade 5`, por exemplo.
- A estabilidade é uma heurística: uma gravação pausada pode parecer concluída.
  Prefira executar após terminar downloads e gravações.
- As categorias devem estar no mesmo sistema de arquivos da origem e suportar
  hard links. Destinos existentes nunca são sobrescritos. Um erro por arquivo
  é exibido no terminal e as demais movimentações continuam.
- Não remove duplicatas, converte formatos ou apaga arquivos por idade.

## Desfazer uma execução

O programa imprime o caminho do registro em `.organizador-registros` dentro da
pasta organizada. Substitua o exemplo abaixo pelo caminho impresso:

```bash
.venv/bin/python organizador.py --desfazer "/caminho/.organizador-registros/REGISTRO.jsonl"
```

O comando acima simula a restauração. Acrescente `--aplicar` para executá-la.
Arquivos alterados desde a movimentação e origens ocupadas são ignorados.
Pastas vazias e registros são mantidos. Os registros contêm caminhos locais:
não os publique no GitHub. Não execute duas instâncias simultâneas nem edite
manualmente os registros.

## Cuidados de versionamento

O repositório é destinado a código e documentação. Não adicione arquivos reais de
Downloads, documentos de clientes, credenciais ou registros com caminhos pessoais.
O `.gitignore` exclui ambientes virtuais e algumas pastas locais, mas não substitui
conferir `git diff --cached` antes de cada commit.

## Publicação e instalação

Esta é uma ferramenta local: a entrega prevista é clonar o repositório, criar o
ambiente virtual e executar como usuário comum. Não precisa de servidor web,
portas abertas ou serviço de nuvem para organizar os arquivos.
