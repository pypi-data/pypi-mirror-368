"""
Registry entry.
"""
import typing as t
if t.TYPE_CHECKING:
    # Ignore warning/test-coverage as it's required for type-hinting only.
    from ._registry import Registry  # type: ignore[unused-import] # pragma: no cover


class Entry:
    """
    Registry entry.
    :param defaults: keyword arguments representing default entry data.
    """
    def __init__(self, **defaults):
        self._defaults = defaults

    def __set_name__(self, owner: 'Registry', name: str):
        if not name.isupper():
            raise NameError(f'Registry entry name `{name}` must be uppercase!')
        self._key: t.Hashable = name
        self._owner: Registry = owner

    def __call__(self, **overrides) -> t.Dict[t.Hashable, t.Any]:
        result = {} if self._owner.key_field is None else {self._owner.key_field: self._key}
        result.update({**self._defaults, **overrides})
        return result

    def __repr__(self):
        return f'<Entry `{self._key}` with defaults: {self._defaults}>'
