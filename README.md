# Organizador de arquivos

Organiza os arquivos soltos de Downloads em pastas como Imagens, PDFs e Documentos.
Funciona localmente no Debian 13, sem enviar seus arquivos para a internet.

## 1. Instalar

```bash
sudo apt update
sudo apt install git python3 python3-venv
git clone https://github.com/kennedyyp/organizador-arquivos.git
cd organizador-arquivos
python3 -m venv .venv
```

Se já instalou, apenas entre na pasta do projeto. Execute os comandos Python
abaixo nessa pasta, sem sudo. Troque `$HOME/Downloads` se sua pasta for outra.

## 2. Organizar manualmente

Veja o que seria movido, sem alterar nada:

```bash
.venv/bin/python organizador.py "$HOME/Downloads"
```

Depois de conferir, mova os arquivos:

```bash
.venv/bin/python organizador.py "$HOME/Downloads" --aplicar
```

O programa preserva nomes, evita sobrescrever arquivos e não percorre subpastas.
Desconhecidos, ocultos e temporários são ignorados. Aguarde downloads terminarem
antes de executar; a verificação de estabilidade não garante que terminaram.

## 3. Ativar uma vez por semana

Domingo às 10h, no horário do computador. Confira a prévia e depois ative:

```bash
.venv/bin/python configurar_agendamento.py "$HOME/Downloads"
.venv/bin/python configurar_agendamento.py "$HOME/Downloads" --instalar
```

O agendamento move arquivos automaticamente. Se perder o horário enquanto o
notebook estiver desligado, uma execução pendente poderá ocorrer ao entrar
novamente na sua sessão. Mantenha a pasta do projeto no mesmo lugar.

Confira a próxima execução e os registros:

```bash
systemctl --user list-timers organizador-arquivos.timer --all
journalctl --user -u organizador-arquivos.service -n 30 --no-pager
```

## 4. Desativar e reativar

Desative futuras execuções (uma execução já iniciada pode terminar):

```bash
systemctl --user disable --now organizador-arquivos.timer
```

Para reativar depois de instalado:

```bash
systemctl --user enable --now organizador-arquivos.timer
```

## 5. Desfazer uma organização

Cada execução que move arquivos mostra o caminho do registro. Substitua o
exemplo pelo caminho exibido e confira a simulação:

```bash
.venv/bin/python organizador.py --desfazer "/caminho/.organizador-registros/REGISTRO.jsonl"
```

Acrescente `--aplicar` para restaurar. Arquivos modificados ou com o caminho
original ocupado são ignorados. Desativar o timer não desfaz movimentações.

## 6. Remover o agendamento e o programa

Desative o timer e aguarde qualquer organização em andamento terminar.
Depois remova somente a configuração deste projeto:

```bash
systemctl --user disable --now organizador-arquivos.timer
systemctl --user clean --what=state organizador-arquivos.timer
rm -f -- "$HOME/.config/systemd/user/organizador-arquivos.timer"
rm -f -- "$HOME/.config/systemd/user/organizador-arquivos.service"
systemctl --user daemon-reload
```

Depois disso, você pode apagar a pasta do projeto pelo gerenciador de arquivos.
Isso não apaga o repositório no GitHub, os arquivos organizados nem os registros
em Downloads. Se quiser desfazer, faça isso antes de apagar o programa e os registros.

## Mais informações

Não envie documentos pessoais ou registros de movimentações ao GitHub.
Instalação detalhada, testes e mudança de horário: [guia completo](docs/GUIA.md).
