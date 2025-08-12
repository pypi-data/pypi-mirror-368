import unittest
from unittest import mock

from chilo_api.cli.openapi.file_writer import OpenAPIFileWriter


def mock_open(*args, **kwargs):
    return mock.mock_open(read_data='bar')(*args, **kwargs)


class OpenAPIFileWriterTest(unittest.TestCase):

    def setUp(self):
        self.writer = OpenAPIFileWriter()

    @mock.patch('builtins.open', mock_open)
    def test_write_openapi(self):
        self.writer.write_openapi({'test': True}, 'tests/outputs/file_writer', ['json', 'yml'])
