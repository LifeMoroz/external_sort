import io
from unittest.mock import patch

from big_file_generator import ASCIIRandomGenerator
from tests.test_generators.test_base_generator import TestBaseGenerator


class TestASCIIGenerator(TestBaseGenerator):
    def setUp(self):
        self.generator = ASCIIRandomGenerator(1000, 1000)

    def test__line_generator__ok(self):
        fd = io.StringIO()
        with patch.object(self.generator, '_get_random_row', return_value='') as m:
            self.generator.line_generator(fd)
        self.assertEqual(m.call_count, 1000)

    def test__line_generator__wrong_descriptor(self):
        fd = io.StringIO()
        fd.close()
        with self.assertRaises(ValueError):
            self.generator.line_generator(fd)

    def test__line_generator__wrong_permissions(self): pass
    # TODO:
    # fd = io.StringIO()
    # fd.close()
    # with self.assertRaises(ValueError):
    #     self.generator.line_generator(fd)
