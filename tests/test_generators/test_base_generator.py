from unittest import TestCase
from unittest.mock import mock_open, patch, Mock, MagicMock

from big_file_generator import Generator


class TestBaseGenerator(TestCase):
    def setUp(self):
        self.generator = Generator(1000, 1000)

    def test__generator__wrong_args(self):
        with self.assertRaises(ValueError):
            Generator(-1, -1)

    def test__generator__wrong_size(self):
        with self.assertRaises(ValueError):
            Generator(-1, 1000)

    def test__generator__wrong_max_line_size(self):
        with self.assertRaises(ValueError):
            Generator(1000, -1)

    def test__open__file__ok(self):
        with patch('big_file_generator.open', mock_open(read_data='bibble')) as m:
            with patch.object(self.generator, 'line_generator', return_value=True) as line_gen_mock:
                result = self.generator.generate('filename.file')
                self.assertTrue(result)
                # TODO: line_gen_mock.assert_called_with(m)

    def test__open__file__failed(self):
        # mock = Mock(side_effect=OSError)
        with patch('big_file_generator.open', Mock(side_effect=OSError)):
            with patch.object(self.generator, 'line_generator', return_value=True):
                result = self.generator.generate('filename.file')
                self.assertFalse(result)

    def test__line_generator__zero_chunk_size(self): pass
