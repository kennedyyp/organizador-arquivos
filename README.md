# Organizador de arquivos

Sabe quando a pasta Downloads fica cheia de PDF, foto, planilha e arquivo compactado, tudo misturado? Esse script separa os arquivos por tipo e coloca cada um na sua pasta, dentro de Downloads mesmo.

Foi feito em Python para usar no Debian 13. Tudo acontece no computador: seus arquivos não vão para a nuvem. Dá para rodar quando quiser ou deixar agendado uma vez por semana.

## Para começar

Instale o que precisa, baixe o projeto e crie o ambiente virtual:

```bash
sudo apt update
sudo apt install git python3 python3-venv
git clone https://github.com/kennedyyp/organizador-arquivos.git
cd organizador-arquivos
python3 -m venv .venv
```

Se você já tem o projeto, não precisa clonar de novo. Os próximos comandos devem ser executados dentro da pasta dele. Usamos o Python da `.venv` para manter o ambiente do projeto separado do sistema, sem precisar ativá-lo toda vez.

## Primeiro, veja o que ele vai fazer

```bash
.venv/bin/python organizador.py "$HOME/Downloads"
```

Esse comando só mostra a organização proposta. Nenhum arquivo é movido. Se sua pasta de downloads fica em outro lugar, troque o caminho.

Conferiu e está tudo certo? Para organizar de verdade:

```bash
.venv/bin/python organizador.py "$HOME/Downloads" --aplicar
```

Por exemplo, uma foto vai para `Downloads/Imagens` e um PDF para `Downloads/PDFs`. Os nomes são mantidos; se já existir outro igual no destino, ele acrescenta um número. Pastas, links simbólicos, arquivos ocultos e extensões desconhecidas ficam onde estão.

Espere os downloads terminarem antes de rodar. O script verifica se o arquivo está mudando, mas uma gravação pausada também pode parecer concluída. Use sem sudo e mantenha o projeto fora da pasta que vai organizar.

## Deixar rodando toda semana

O horário definido é domingo às 10h, seguindo o relógio do computador. Primeiro veja a configuração e depois instale o agendamento:

```bash
.venv/bin/python configurar_agendamento.py "$HOME/Downloads"
.venv/bin/python configurar_agendamento.py "$HOME/Downloads" --instalar
```

A partir daí, o systemd do seu usuário cuida da execução. Não precisa deixar o terminal aberto. Se o notebook estiver desligado no horário, uma execução pendente poderá acontecer quando você entrar novamente na sua sessão. Não mude a pasta do projeto de lugar depois de instalar.

Para ver quando vai rodar:

```bash
systemctl --user list-timers organizador-arquivos.timer --all
```

Se quiser conferir o que aconteceu na última execução:

```bash
journalctl --user -u organizador-arquivos.service -n 30 --no-pager
```

## Para desligar ou ligar de novo

Para parar o agendamento:

```bash
systemctl --user disable --now organizador-arquivos.timer
```

Isso impede as próximas execuções. Uma organização que já começou pode terminar, e os arquivos que foram movidos continuam nas suas pastas.

Para ligar novamente, depois de já ter instalado:

```bash
systemctl --user enable --now organizador-arquivos.timer
```

## E se eu quiser desfazer?

Quando move arquivos, o programa mostra o caminho de um registro salvo na pasta `.organizador-registros`, dentro de Downloads. Guarde esse caminho. Para ver o que seria restaurado, substitua o exemplo pelo registro da sua execução:

```bash
.venv/bin/python organizador.py --desfazer "/caminho/.organizador-registros/REGISTRO.jsonl"
```

Acrescente `--aplicar` ao mesmo comando para desfazer de verdade. Se um arquivo tiver sido modificado ou o lugar original estiver ocupado, ele será ignorado para evitar sobrescrita. As pastas vazias permanecem.

## Para remover

Primeiro desligue o agendamento e espere qualquer organização em andamento terminar. Depois, remova a configuração:

```bash
systemctl --user disable --now organizador-arquivos.timer
systemctl --user clean --what=state organizador-arquivos.timer
rm -f -- "$HOME/.config/systemd/user/organizador-arquivos.timer"
rm -f -- "$HOME/.config/systemd/user/organizador-arquivos.service"
systemctl --user daemon-reload
```

Agora você pode apagar a pasta do projeto pelo gerenciador de arquivos. Os arquivos organizados e o repositório no GitHub continuam lá. Se pretende desfazer alguma organização, faça isso antes de apagar o programa ou os registros.

Se quiser rodar os testes do projeto, eles usam arquivos fictícios em pastas temporárias:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Só um cuidado ao compartilhar resultados: os registros podem mostrar nomes e caminhos de arquivos pessoais. Não coloque esses registros nem seus documentos no GitHub.
