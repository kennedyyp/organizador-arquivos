"""Prepara um timer semanal do systemd; só instala com --instalar."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

NOME = 'organizador-arquivos'
CALENDARIO = 'Sun *-*-* 10:00:00'


def argumento_systemd(valor):
    """Escapa um argumento literal de ExecStart, sem passar por shell."""
    if any(ord(c) < 32 for c in valor):
        raise ValueError('Caminhos com caracteres de controle não são suportados.')
    valor = (valor.replace('\\', '\\\\').replace('"', '\\"')
             .replace('%', '%%').replace('$', '$$'))
    return f'"{valor}"'


def gerar_unidades(projeto, pasta):
    comando = ' '.join(argumento_systemd(str(arg)) for arg in (
        projeto / '.venv/bin/python', '-u', projeto / 'organizador.py', pasta,
        '--aplicar', '--estabilidade', '5',
    ))
    servico = f'''[Unit]
Description=Organiza arquivos locais por tipo

[Service]
Type=oneshot
ExecStart={comando}
NoNewPrivileges=true
UMask=0077
TimeoutStartSec=15min
StandardOutput=journal
StandardError=journal
'''
    timer = f'''[Unit]
Description=Organizacao semanal aos domingos, 10h

[Timer]
OnCalendar={CALENDARIO}
Persistent=true
AccuracySec=1min
Unit={NOME}.service

[Install]
WantedBy=timers.target
'''
    return {f'{NOME}.service': servico, f'{NOME}.timer': timer}


def instalar(unidades, diretorio):
    # Confere todos os destinos antes de escrever qualquer arquivo.
    for nome, conteudo in unidades.items():
        destino = diretorio / nome
        if destino.is_symlink():
            raise ValueError(f'Destino é um link simbólico: {destino}')
        if destino.exists() and destino.read_text(encoding='utf-8') != conteudo:
            raise ValueError(f'Configuração existente diferente: {destino}. '
                             'Revise-a antes de substituir.')
    diretorio.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in unidades.items():
        destino = diretorio / nome
        if not destino.exists():
            with destino.open('x', encoding='utf-8') as arquivo:
                arquivo.write(conteudo)
            destino.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pasta', type=Path, help='Mesma pasta já validada na simulação')
    parser.add_argument('--instalar', action='store_true',
                        help='Grava as unidades e ativa o timer do usuário')
    args = parser.parse_args()
    try:
        if os.geteuid() == 0:
            raise ValueError('Execute como seu usuário normal, sem sudo.')
        projeto = Path(__file__).resolve().parent
        pasta = args.pasta.expanduser().resolve(strict=True)
        if not pasta.is_dir() or pasta == Path.home().resolve():
            raise ValueError('Escolha uma pasta específica, diferente da sua home.')
        if pasta == projeto or pasta in projeto.parents:
            raise ValueError('Mantenha o projeto fora da pasta organizada.')
        if not (projeto / '.venv/bin/python').is_file():
            raise ValueError('Crie primeiro o ambiente: python3 -m venv .venv')
        if sys.prefix == sys.base_prefix:
            raise ValueError('Use .venv/bin/python configurar_agendamento.py ...')
        unidades = gerar_unidades(projeto, pasta)
        diretorio = Path.home() / '.config/systemd/user'
        if not args.instalar:
            for nome, conteudo in unidades.items():
                print(f'Arquivo previsto: {diretorio / nome}\n{conteudo}')
            print('Prévia: nada foi instalado. Use --instalar para ativar.')
            return
        subprocess.run(['systemctl', '--user', 'show-environment'],
                       stdout=subprocess.DEVNULL, check=True)
        instalar(unidades, diretorio)
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', '--user', 'enable', '--now', f'{NOME}.timer'],
                       check=True)
        subprocess.run(['systemctl', '--user', 'list-timers', f'{NOME}.timer',
                        '--no-pager'], check=True)
        print('Timer ativado. Se uma execução anterior foi perdida, ela pode ocorrer agora.')
    except (OSError, ValueError, subprocess.CalledProcessError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
