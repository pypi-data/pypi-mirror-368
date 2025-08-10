def find_version() -> str:
    import importlib.metadata
    try:
        return importlib.metadata.version('sides')
    except importlib.metadata.PackageNotFoundError:
        try:
            import pathlib, tomllib
            root = pathlib.Path(__file__).parents[2]
            pyproject_path = root / 'pyproject.toml'
            pyproject_toml = pyproject_path.read_text()
            pyproject = tomllib.loads(pyproject_toml)
            return pyproject['project']['version']
        except:
            return '0.0.0+unknown'


if __name__ == '__main__':
    print(find_version())
