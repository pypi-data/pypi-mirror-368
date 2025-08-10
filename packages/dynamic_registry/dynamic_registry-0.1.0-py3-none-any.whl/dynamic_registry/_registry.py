"""
Registry type (metaclass).
"""
import typing as t
from ._entry import Entry


class Registry(type):
    """
    Registry metaclass.
    """
    def __new__(mcs, name, bases, namespace, *, key_field='key'):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._key_field = key_field
        return cls

    @property
    def key_field(cls) -> t.Hashable:
        """
        Field ``key_field``. The field used in all the registry entries to represent unique key/name of the entry.
        """
        return cls._key_field

    @property
    def entries(cls) -> t.Dict[str, 'Entry']:
        """
        All the entries as a dictionary.
        """
        return {key: value for key, value in cls.__dict__.items() if isinstance(value, Entry)}

    def __repr__(cls):
        entries_names = ', '.join(sorted(f'`{_}`' for _ in cls.entries))
        return f'<Registry `{cls.__name__}` with entries: {entries_names}>'
