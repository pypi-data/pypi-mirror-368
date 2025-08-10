"""
Registry framework for declarative reusable data storage.

Usage example::

    from dynamic_registry import Registry, Entry

    class HttpErrors(metaclass=Registry):
        ERROR_500 = Entry(message='Internal Server Error!')
        ERROR_501 = Entry(message='Not Authorized!')
        ERROR_404 = Entry(message='Not Found!')

    # Iterating through all entries:
    for key, entry in HttpErrors.entries.items():
        print(f'{key} ==> {entry}')

    # Accessing an entry:
    print(HttpErrors.ERROR_501())

    # Overriding/adding fields at runtime:
    print(HttpErrors.ERROR_501(user='some-user-name', action='ACCESS_TO_ADMIN_PANEL'))

Notes:

- Entry names must be uppercase. ``__set_name__`` enforces this.
- Runtime overrides do not modify the original entry, but return a new dict with merged fields.
"""
from ._entry import Entry
from ._registry import Registry
