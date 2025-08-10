import importlib
import inspect
from pathlib import Path

from .composer import Composer
from .composer_repository import ComposerRepository


def scan(package):
    package_path = Path(package.__file__).parent
    package_name = package.__name__

    def walk_modules(path, prefix):
        for item in path.iterdir():
            if item.is_dir():
                yield from walk_modules(item, f"{prefix}.{item.name}")
            elif item.suffix == '.py' and item.name != '__init__.py':
                modname = f"{prefix}.{item.stem}"
                try:
                    mod = importlib.import_module(modname)
                    yield mod
                except Exception:
                    pass

    # Add the package module itself
    try:
        mod = importlib.import_module(package_name)
        yield_mods = [mod]
    except Exception as e:
        print(f"Error importing {package_name}: {e}")
        yield_mods = []

    # Add all submodules
    yield_mods += list(walk_modules(package_path, package_name))

    for mod in yield_mods:
        for name, obj in inspect.getmembers(mod):
            if isinstance(obj, Composer):
                ComposerRepository.add_composer(obj)
