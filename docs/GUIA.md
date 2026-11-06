# Organizador de arquivos

Automação local em Python para organizar arquivos no Debian 13.

## Estado do projeto

Versão com execução manual e agendamento semanal opcional, simulação por padrão
e testes automatizados. Não há monitoramento contínuo.

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

## Agendamento semanal no Debian

O timer executa aos domingos às 10h no fuso configurado no computador, com
tolerância de um minuto. Não requer bibliotecas novas nem sudo. O instalador
usa caminhos absolutos para o projeto, o Python da `.venv` e a pasta escolhida.

Na pasta do projeto, confira primeiro a prévia das unidades:

```bash
.venv/bin/python configurar_agendamento.py "$HOME/Downloads"
```

Depois de conferir a pasta e o horário, instale e ative:

```bash
.venv/bin/python configurar_agendamento.py "$HOME/Downloads" --instalar
```

São criados `organizador-arquivos.service` e `organizador-arquivos.timer` em
`~/.config/systemd/user/`. O serviço roda com seu usuário, usando `--aplicar`
e intervalo de estabilidade de 5 segundos. Não ativa organização na instalação
normal do projeto: apenas o comando com `--instalar` habilita o timer.

`Persistent=true` recupera uma execução perdida quando o gerenciador do usuário
voltar a iniciar (normalmente no login). Isso pode mover arquivos logo após
ativar um timer que já tinha execução pendente. Não liga o notebook desligado,
não garante execução sem sessão e não ativa linger. Não espere várias execuções
para cada semana perdida: elas são recuperadas em uma ativação.

Confira o próximo horário e o fuso:

```bash
timedatectl
systemctl --user list-timers organizador-arquivos.timer --all
```

Consulte o histórico e possíveis falhas:

```bash
journalctl --user -u organizador-arquivos.service -n 50 --no-pager
```

Antes da primeira execução, é normal não haver logs. Eles podem conter nomes e
caminhos pessoais: mantenha-os locais. Uma falha de movimentação resulta em saída
diferente de zero para o systemd; não há notificação nem repetição automática.

Para desativar futuras execuções (não desfaz movimentações já feitas):

```bash
systemctl --user disable --now organizador-arquivos.timer
```

Não mova a pasta do projeto depois de instalar o agendamento. Se quiser alterar
o horário, use `systemctl --user edit organizador-arquivos.timer` e adicione:

```ini
[Timer]
OnCalendar=
OnCalendar=Sun *-*-* 10:00:00
```

Substitua o dia e horário desejados. A linha vazia limpa o calendário anterior.
Depois aplique com `systemctl --user daemon-reload` e
`systemctl --user restart organizador-arquivos.timer`, e confira `list-timers`.
O instalador não substitui unidades existentes com conteúdo diferente.

Referência: [documentação oficial do systemd 257](https://www.freedesktop.org/software/systemd/man/257/systemd.timer.html).

## Cuidados de versionamento

O repositório é destinado a código e documentação. Não adicione arquivos reais de
Downloads, documentos de clientes, credenciais ou registros com caminhos pessoais.
O `.gitignore` exclui ambientes virtuais e algumas pastas locais, mas não substitui
conferir `git diff --cached` antes de cada commit.

## Publicação e instalação

Esta é uma ferramenta local: a entrega prevista é clonar o repositório, criar o
ambiente virtual e executar como usuário comum. Não precisa de servidor web,
portas abertas ou serviço de nuvem para organizar os arquivos.
