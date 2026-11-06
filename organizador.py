#!/usr/bin/env python3
"""Organizador local sem dependências. Simula por padrão."""
import argparse
import json
import os
from pathlib import Path
import stat
import time
from datetime import datetime

CATEGORIAS = {
    'Imagens': 'jpg jpeg png gif webp svg bmp tiff heic avif',
    'PDFs': 'pdf',
    'Documentos': 'doc docx odt txt rtf md epub',
    'Planilhas': 'xls xlsx ods csv tsv',
    'Apresentacoes': 'ppt pptx odp',
    'Videos': 'mp4 mkv avi mov webm m4v',
    'Audios': 'mp3 wav flac ogg m4a opus',
    'Compactados': 'zip rar 7z tar gz bz2 xz zst',
    'Pacotes': 'deb rpm appimage iso',
    'Codigo': 'py js ts html css sh json yaml yml sql ipynb',
}
EXTENSOES = {ext: categoria for categoria, lista in CATEGORIAS.items()
             for ext in lista.split()}
TEMPORARIOS = {'.part', '.crdownload', '.download', '.tmp', '.swp'}


def mover_sem_sobrescrever(origem, destino):
    # Hard link + unlink evita sobrescrever um destino criado entre verificações.
    # As pastas de categoria devem estar no mesmo sistema de arquivos.
    os.link(origem, destino, follow_symlinks=False)
    try:
        origem.unlink()
    except OSError:
        destino.unlink()
        raise


def assinatura(caminho):
    info = caminho.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Não é um arquivo regular.')
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def organizar(pasta, aplicar, estabilidade=2):
    falhas = 0
    movimentos = []
    reservados = set()
    candidatos = {}
    for caminho in sorted(pasta.iterdir()):
        if (caminho.name.startswith('.') or caminho.is_symlink()
                or caminho.suffix.lower() in TEMPORARIOS
                or caminho.suffix.lower().lstrip('.') not in EXTENSOES):
            continue
        try:
            candidatos[caminho] = assinatura(caminho)
        except (OSError, ValueError):
            continue
    if candidatos:
        time.sleep(estabilidade)
    for origem, inicial in candidatos.items():
        try:
            if assinatura(origem) != inicial:
                print(f'IGNORADO: {origem.name} ainda está mudando.')
                continue
        except (OSError, ValueError):
            continue
        if (origem.name.startswith('.') or origem.is_symlink()
                or not origem.is_file() or origem.suffix.lower() in TEMPORARIOS):
            continue
        categoria = EXTENSOES.get(origem.suffix.lower().lstrip('.'), 'Outros')
        diretorio = pasta / categoria
        if diretorio.is_symlink() or (diretorio.exists() and not diretorio.is_dir()):
            print(f'IGNORADO: destino inválido: {diretorio}')
            continue
        destino = diretorio / origem.name
        contador = 1
        while destino.exists() or destino.is_symlink() or destino in reservados:
            destino = diretorio / f'{origem.stem} ({contador}){origem.suffix}'
            contador += 1
        reservados.add(destino)
        movimentos.append((origem, destino, inicial))
    if not aplicar:
        for origem, destino, inicial in movimentos:
            print(f'{origem.name} -> {destino.relative_to(pasta)}')
        print(f'\nSimulação: {len(movimentos)} arquivo(s). Nada foi alterado.')
        return 0
    if not movimentos:
        print('Nenhum arquivo para organizar.')
        return 0
    registro = pasta / '.organizador-registros'
    if registro.is_symlink():
        raise ValueError('A pasta de registros não pode ser um link simbólico.')
    registro.mkdir(exist_ok=True)
    diario = registro / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.jsonl')
    with diario.open('x', encoding='utf-8') as log:
        for origem, destino, inicial in movimentos:
            try:
                destino.parent.mkdir(exist_ok=True)
                info = origem.lstat()
                if assinatura(origem) != inicial:
                    raise ValueError('O arquivo mudou desde o planejamento.')
                # Registra a intenção antes da movimentação, inclusive em caso de interrupção.
                log.write(json.dumps({'origem': str(origem), 'destino': str(destino),
                                      'inode': info.st_ino, 'device': info.st_dev,
                                      'size': info.st_size, 'mtime_ns': info.st_mtime_ns}) + '\n')
                log.flush()
                os.fsync(log.fileno())
                mover_sem_sobrescrever(origem, destino)
                print(f'MOVIDO: {origem.name} -> {destino.relative_to(pasta)}')
            except (OSError, ValueError) as erro:
                falhas += 1
                print(f'ERRO: {origem.name}: {erro}')
    print(f'\nRegistro para desfazer: {diario}')
    return falhas


def desfazer(diario, aplicar):
    pasta = diario.parent.parent.resolve()
    if diario.parent.name != '.organizador-registros':
        raise ValueError('Use um registro dentro de .organizador-registros.')
    linhas = diario.read_text(encoding='utf-8').splitlines()
    for linha in reversed(linhas):
        item = json.loads(linha)
        origem, destino = Path(item['origem']), Path(item['destino'])
        if (origem.parent.resolve() != pasta or destino.parent.parent.resolve() != pasta
                or destino.parent.is_symlink()):
            raise ValueError('Registro contém caminhos inválidos.')
        if origem.exists() or origem.is_symlink() or not destino.exists() or destino.is_symlink():
            print(f'IGNORADO: {origem.name} (origem ocupada ou destino ausente)')
            continue
        info = destino.stat()
        if (info.st_ino, info.st_dev, info.st_size, info.st_mtime_ns) != (
                item['inode'], item['device'], item['size'], item['mtime_ns']):
            print(f'IGNORADO: {destino.name} foi alterado após a organização.')
            continue
        if aplicar:
            mover_sem_sobrescrever(destino, origem)
        print(f'{"RESTAURADO" if aplicar else "RESTAURARIA"}: {origem.name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pasta', nargs='?', type=Path, help='Pasta a organizar')
    parser.add_argument('--aplicar', action='store_true', help='Executa as movimentações')
    parser.add_argument('--desfazer', type=Path, metavar='REGISTRO', help='Desfaz um registro')
    parser.add_argument('--estabilidade', type=float, default=2, metavar='SEGUNDOS',
                        help='Intervalo de verificação de estabilidade (padrão: 2)')
    args = parser.parse_args()
    if not 0 < args.estabilidade <= 3600:
        parser.error('--estabilidade deve estar entre 0 e 3600 segundos, sem incluir zero.')
    try:
        if args.desfazer:
            desfazer(args.desfazer.expanduser().absolute(), args.aplicar)
        elif args.pasta:
            pasta = args.pasta.expanduser().resolve(strict=True)
            if not pasta.is_dir():
                parser.error('Informe uma pasta.')
            falhas = organizar(pasta, args.aplicar, args.estabilidade)
            if falhas:
                parser.exit(1, f'Execução terminou com {falhas} falha(s). Consulte os registros.\n')
        else:
            parser.error('Informe a pasta que deseja organizar.')
    except (OSError, ValueError, KeyError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
