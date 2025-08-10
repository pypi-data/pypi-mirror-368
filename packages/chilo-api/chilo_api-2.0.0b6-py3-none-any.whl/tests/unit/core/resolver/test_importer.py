import unittest

from chilo_api.core.resolver.importer import ResolverImporter


class ResolverImporterTest(unittest.TestCase):

    def test_bad_handlers_multi_dynamic_files(self):
        importer = ResolverImporter(handlers='tests/unit/mocks/rest/handlers/invalid/bad_structure/multi_dynamic')
        with self.assertRaises(RuntimeError) as context:
            importer.get_handlers_file_tree()
        self.assertIn('Cannot have two dynamic files in the same directory', str(context.exception))

    def test_bad_handlers_same_file_and_directory_names(self):
        importer = ResolverImporter(handlers='tests/unit/mocks/rest/handlers/invalid/bad_structure/same_names')
        with self.assertRaises(RuntimeError) as context:
            importer.get_handlers_file_tree()
        self.assertIn('Cannot have file and directory share same name', str(context.exception))

    def test_empty_handlers_result(self):
        importer = ResolverImporter(handlers='tests/mocks/empty_handlers')
        with self.assertRaises(RuntimeError) as context:
            importer.get_handlers_file_tree()
        self.assertIn('no files found in handler path', str(context.exception))

    def test_get_handlers_file_tree_success(self):
        importer = ResolverImporter(handlers='tests/unit/mocks/rest/handlers/valid')
        file_tree = importer.get_handlers_file_tree()
        self.assertIsNotNone(file_tree)
        self.assertIsInstance(file_tree, dict)
