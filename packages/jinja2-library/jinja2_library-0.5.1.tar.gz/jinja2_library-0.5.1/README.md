# Library for Jinja2 Template Extensions

[![CI Build Status](https://github.com/jenisys/jinja2-library/actions/workflows/test.yml/badge.svg)](https://github.com/jenisys/jinja2-library/actions/workflows/test.yml)
[![Latest Version](https://img.shields.io/pypi/v/jinja2-library.svg)](https://pypi.python.org/pypi/jinja2-library)
[![License](https://img.shields.io/pypi/l/jinja2-library.svg)](https://github.com/jenisys/jinja2-library/blob/main/LICENSE)

Provides a library functionality for [Jinja2] extensions that can be used in templates.

FEATURES:

* Provides a `library` concept for [Jinja2] extensions,
  like [filters], [tests], [globals] and [directives] (aka: `extensions`),
* Declarative approach to describe and register [Jinja2] extensions.
* Simplifies how `library` items are registered in an `Environment` (in one step).
* Supports own namespace/scope for each library.
* Supports control over registered names.

## EXAMPLE 1: Basic Example

```python
# -- FILE: example/hello.py
from jinja2_library import Library
import jinja2.ext

this_library = Library()
register = this_library.make_register_decorator()

@register.filter
def hello(value, greeting=None):
    greeting = greeting or "Hello"
    return u"{greeting} {name}".format(greeting=greeting, name=value)

class LibraryExtension(jinja2.ext.Extension):
    """Simplifies to use ``this_library`` as Jinja2 extension."""
    def __init__(self, environment):
        super(LibraryExtension, self).__init__(environment)
        this_library.add_to_environment(environment)
```

The template library can be used by using the `LibraryExtension` class in [Jinja2]:

```python
# -- FILE: use_template_library_hello.py
# USING: example.hello.LibraryExtension
from jinja2 import Environment
from assertpy import assert_that

this_extension = "example.hello.LibraryExtension"
this_template = "HELLO: {{ this.name|hello(greeting=this.greeting) }}"
this_data = dict(name="Alice", greeting="Ciao")

environment = Environment(extensions=[this_extension])
template = environment.from_string(this_template)
this_text = template.render(this=this_data)
assert_that(this_text).is_equal_to("HELLO: Ciao Alice")
```

## API

### Library class

The `Library` constructor provides the following parameter:

| Parameter | Type               | Default | Description                           |
|-----------|--------------------|---------|---------------------------------------|
| `scope`   | `Optional[string]` | `None`  | Scope/namespace for registered items. |

* The `scope` parameter allows to provide a namespace for the registered `Library` items.
* This prevents name collisions if many filters/tests/globals are used.
* Simplifies the registration of filters/tests/globals/extensions into an `Environment`.

EXAMPLE:

```python
# -- FILE: example/scoped_hello.py
from jinja2_library import Library
import jinja2.ext

this_library = Library("foo.bar")  # -- HINT: Library with scope="foo.bar".
register = this_library.make_register_decorator()

@register.filter(name="hello")
def hello_filter(value, greeting=None):
    greeting = greeting or "Hello"
    return u"{greeting} {name}".format(greeting=greeting, name=value)

class LibraryExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(LibraryExtension, self).__init__(environment)
        this_library.add_to_environment(environment)
```

Scoped library names can then be used inside a template, like:

```jinja
{#- FILE: template.jinja -#}
{#- USING: extensions=["example.scoped_hello.LibraryExtension"] -#}
HELLO: {{ this.name|foo.bar.hello(greeting="Ciao") }}
```

### Register Decorators

This Python package provides the following [decorators] (in the context of the example above):

| Register Decorator    | Description                                                         |
|:----------------------|:--------------------------------------------------------------------|
| `@register.filter`    | Register a [Jinja2 filter] function to `this_library`.              |
| `@register.test`      | Register a [Jinja2 test] predicate function to `this_library`.      |
| `@register.global_`   | Register a [Jinja2 global] function or variable to `this_library`.  |
| `@register.extension` | Register a [Jinja2 extension] class (aka: `jinja2.ext.Extension`).  |

The function [decorators] for `@register.filter/test/global_` support optional parameters.
These optional decorator parameters are:

| Parameter | Type               | Default           | Description                       |
|:----------|:-------------------|:------------------|:----------------------------------|
| `name`    | `string`           | `{function.name}` | Name of the `filter/test/global`. |
| `aliases` | `sequence<string>` | `EMPTY_SEQUENCE`  | List of alternative names.        |


Background Info
-------------------------------------------------------------------------------

Inspired by the [Django template library] approach.


History
-------------------------------------------------------------------------------

* INITIALLY CREATED AS: `simplegen.template_lib`
* REFACTORING: Extracted into own standalone package to simplify reuse
  with [Jinja2] template engine.

----

[decorators]: https://peps.python.org/pep-0318/
[Jinja2]: https://github.com/pallets/jinja/
[Jinja2 filter]: https://jinja.palletsprojects.com/en/stable/api/#custom-filters
[Jinja2 test]: https://jinja.palletsprojects.com/en/stable/api/#custom-tests
[Jinja2 global]: https://jinja.palletsprojects.com/en/stable/api/#the-global-namespace
[Jinja2 directive]: https://jinja.palletsprojects.com/en/stable/templates/#extensions
[Django template library]: https://docs.djangoproject.com/en/5.2/howto/custom-template-tags/

[filters]: https://jinja.palletsprojects.com/en/stable/api/#custom-filters
[tests]: https://jinja.palletsprojects.com/en/stable/api/#custom-tests
[globals]: https://jinja.palletsprojects.com/en/stable/api/#the-global-namespace
[directives]: https://jinja.palletsprojects.com/en/stable/templates/#extensions
