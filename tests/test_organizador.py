import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import organizador


class OrganizadorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = Path(self.temp.name)
        self.saida = contextlib.redirect_stdout(io.StringIO())
        self.saida.__enter__()
        self.addCleanup(self.saida.__exit__, None, None, None)

    def arquivo(self, nome, conteudo=b'dados'):
        caminho = self.pasta / nome
        caminho.write_bytes(conteudo)
        return caminho

    def organizar(self, aplicar):
        with patch('organizador.time.sleep'):
            organizador.organizar(self.pasta, aplicar)

    def test_simulacao_nao_altera_arquivos(self):
        self.arquivo('foto.png')
        self.organizar(False)
        self.assertEqual([p.name for p in self.pasta.iterdir()], ['foto.png'])

    def test_colisao_preserva_ambos_e_desfazer_restaura(self):
        self.arquivo('foto.png', b'nova')
        (self.pasta / 'Imagens').mkdir()
        self.arquivo('Imagens/foto.png', b'antiga')
        self.organizar(True)
        self.assertEqual((self.pasta / 'Imagens/foto.png').read_bytes(), b'antiga')
        self.assertEqual((self.pasta / 'Imagens/foto (1).png').read_bytes(), b'nova')
        diario = next((self.pasta / '.organizador-registros').iterdir())
        organizador.desfazer(diario, True)
        self.assertEqual((self.pasta / 'foto.png').read_bytes(), b'nova')

    def test_ignora_desconhecidos_temporarios_ocultos_e_subpastas(self):
        for nome in ['desconhecido.xyz', 'baixando.part', '.oculto.pdf']:
            self.arquivo(nome)
        (self.pasta / 'projeto').mkdir()
        self.arquivo('projeto/manual.pdf')
        (self.pasta / 'atalho.pdf').symlink_to(self.pasta / 'projeto/manual.pdf')
        self.organizar(True)
        self.assertFalse((self.pasta / 'PDFs').exists())
        self.assertTrue((self.pasta / 'atalho.pdf').is_symlink())
        self.assertTrue((self.pasta / 'projeto/manual.pdf').exists())
        self.assertTrue((self.pasta / 'desconhecido.xyz').exists())

    def test_arquivo_mudando_nao_e_movido(self):
        arquivo = self.arquivo('relatorio.pdf')
        with patch('organizador.time.sleep', side_effect=lambda _: arquivo.write_bytes(b'novo conteudo')):
            organizador.organizar(self.pasta, True)
        self.assertTrue(arquivo.exists())
        self.assertFalse((self.pasta / 'PDFs').exists())

    def test_destino_simbolico_nao_recebe_arquivos(self):
        (self.pasta / 'outra').mkdir()
        (self.pasta / 'PDFs').symlink_to(self.pasta / 'outra', target_is_directory=True)
        self.arquivo('relatorio.pdf')
        self.organizar(True)
        self.assertTrue((self.pasta / 'relatorio.pdf').exists())
        self.assertEqual(list((self.pasta / 'outra').iterdir()), [])

    def test_desfazer_preserva_arquivo_modificado(self):
        self.arquivo('relatorio.pdf')
        self.organizar(True)
        diario = next((self.pasta / '.organizador-registros').iterdir())
        destino = self.pasta / 'PDFs/relatorio.pdf'
        destino.write_bytes(b'modificado depois')
        organizador.desfazer(diario, True)
        self.assertFalse((self.pasta / 'relatorio.pdf').exists())
        self.assertEqual(destino.read_bytes(), b'modificado depois')

    def test_desfazer_nao_sobrescreve_origem_ocupada(self):
        self.arquivo('relatorio.pdf')
        self.organizar(True)
        diario = next((self.pasta / '.organizador-registros').iterdir())
        self.arquivo('relatorio.pdf', b'outro')
        organizador.desfazer(diario, True)
        self.assertEqual((self.pasta / 'relatorio.pdf').read_bytes(), b'outro')
        self.assertTrue((self.pasta / 'PDFs/relatorio.pdf').exists())


if __name__ == '__main__':
    unittest.main()
