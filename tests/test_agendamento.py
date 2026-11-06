import tempfile
import unittest
from pathlib import Path

from configurar_agendamento import gerar_unidades, instalar


class AgendamentoTests(unittest.TestCase):
    def test_instalacao_pode_ser_repetida_e_nao_sobrescreve_personalizacao(self):
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            unidades = gerar_unidades(pasta / 'projeto', pasta / 'Downloads')
            destino = pasta / 'unidades'
            instalar(unidades, destino)
            instalar(unidades, destino)
            servico = destino / 'organizador-arquivos.service'
            servico.write_text('configuracao personalizada', encoding='utf-8')
            with self.assertRaises(ValueError):
                instalar(unidades, destino)
            self.assertEqual(servico.read_text(), 'configuracao personalizada')

    def test_link_simbolico_nao_e_usado_como_destino(self):
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            original = pasta / 'original'
            original.write_text('preservar')
            (pasta / 'organizador-arquivos.service').symlink_to(original)
            with self.assertRaises(ValueError):
                instalar(gerar_unidades(pasta, pasta / 'Downloads'), pasta)
            self.assertEqual(original.read_text(), 'preservar')
            self.assertFalse((pasta / 'organizador-arquivos.timer').exists())
