from chilo_api.cli.importer import CLIImporter  # pragma: no cover


def run(*_, **kwargs):  # pragma: no cover
    importer = CLIImporter()
    api = importer.get_api_module(kwargs['api'])
    return api.route
