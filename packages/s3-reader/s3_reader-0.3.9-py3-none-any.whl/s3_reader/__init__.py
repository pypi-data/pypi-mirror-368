from .file import File

__all__ = ['File', '__version__']


def __getattr__(name: str) -> str:
    if name == '__version__':
        from .version import __version__

        return __version__
    msg = f'module {__name__} has no attribute {name}'
    raise AttributeError(msg)
