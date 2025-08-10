[badge--license]: https://img.shields.io/badge/©MIT-d19a04.svg?style=for-the-badge
[href--license]: https://github.com/endusol/dynamic_registry/blob/main/LICENSE

[badge--python]: https://img.shields.io/badge/Python%203.9%2B-3060bb?logo=python&style=for-the-badge&logoColor=white
[href--python]: https://www.python.org/

[badge--pypi]: https://img.shields.io/badge/DYNAMICREGISTRY-352239.svg?logo=pypi&style=for-the-badge&logoColor=white
[href--pypi]: https://pypi.org/project/dynamicregistry/

[badge--safety]: https://img.shields.io/badge/🛡%20Safety-131313?style=for-the-badge
[href--safety]: https://data.safetycli.com/packages/pypi/dynamicregistry/

[badge--codecov]: https://img.shields.io/codecov/c/github/endusol/dynamic_registry/main?logo=codecov&style=for-the-badge&logoColor=white
[href--codecov]: https://app.codecov.io/github/endusol/dynamic_registry/tree/main

[badge--gh-actions]: https://img.shields.io/badge/dynamic/json?&style=for-the-badge&logo=githubactions&logoColor=white&label=Publish%20to%20PyPi&color=131313&url=https%3A%2F%2Fapi.github.com%2Frepos%2Fendusol%2Fdynamic_registry%2Factions%2Fruns&query=%24.workflow_runs%5B0%5D.conclusion
[href--gh-actions]: https://github.com/endusol/dynamic_registry/actions/workflows/publish-pypi.yaml

[badge--gh-sponsors]: https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#ea4aaa
[href--gh-sponsors]: https://github.com/endusol/dynamic_registry/

[badge--buy-me-a-coffee]: https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black
[href--buy-me-a-coffee]: https://buymeacoffee.com/endusol

[badge--ko-fi]: https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white
[href--ko-fi]: https://ko-fi.com/endusol

# dynamic_registry

[![badge--license]][href--license]
[![badge--python]][href--python]
[![badge--pypi]][href--pypi]

[![badge--safety]][href--safety]
[![badge--codecov]][href--codecov]
[![badge--gh-actions]][href--gh-actions]


**Create registries with dynamic entries - which may be enriched with some data at runtime.**

`dynamic_registry` provides an elegant and reusable way to create registries that dynamically track and manage entries.
Useful for plugins, handlers, or any scenario requiring dynamic discovery and access to components.

---

## Would like to support?

[![badge--buy-me-a-coffee]][href--buy-me-a-coffee]
[![badge--ko-fi]][href--ko-fi]

---

## Installation

```shell
pip install dynamic-registry
```

## Basic usage

```python
from dynamic_registry import Registry, Entry


class ErrorsRegistry(metaclass=Registry):
    ERROR_404 = Entry(message='Not found!')
    ERROR_500 = Entry(message='Internal server error!')
    ERROR_501 = Entry(message='Not authorized!')


print(ErrorsRegistry.ERROR_500())
# Note, how dynamic enrichment works:
print(ErrorsRegistry.ERROR_501(user='Nigan', action='ACCESS_ALEXANDREA_SERVER', reason='User is in the blacklist!'))
print(ErrorsRegistry.ERROR_501(user='Rick', action='ACCESS_ALEXANDREA_SERVER', reason='Invalid username/password!'))
# You can even overwrite the key field and defaults defined during the class creation:
print(ErrorsRegistry.ERROR_500(message='Overwritten message!'))
print(ErrorsRegistry.ERROR_500(key='ERROR_500_OVERWRITTEN_KEY'))

for name, entry in ErrorsRegistry.entries.items():
    print(f'ENTRY: {name} ==> {entry}')
```

## Options

Optionally, you can use custom entry key/name field (default is `key`) like this:

```python
from dynamic_registry import Registry, Entry


class MyRegistry(metaclass=Registry, key_field='id'):
    ENTRY = Entry()


print(MyRegistry.ENTRY())
```

Or you can disable this behavior at all, by setting `key_field` to `None`:

```python
from dynamic_registry import Registry, Entry


class MyRegistry(metaclass=Registry, key_field=None):
    ENTRY = Entry()


print(MyRegistry.ENTRY())
```

