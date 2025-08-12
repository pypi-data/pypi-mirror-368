from importlib.resources import files

version_str = (files(__package__) / 'VERSION').read_text().strip()
