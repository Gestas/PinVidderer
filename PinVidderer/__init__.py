from pathlib import Path

_package_root = Path(__file__).parent.resolve()


def get_abs_path(path):
    _p = _package_root.joinpath(path)
    return _p.resolve()
