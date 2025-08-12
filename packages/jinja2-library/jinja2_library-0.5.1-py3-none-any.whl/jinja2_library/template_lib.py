# -*- coding: utf-8 -*-
"""
Provides support for template (engine) libraries.
A template library may provide additional functionality, like:

  * `filter`_ functions
  * `test`_ functions
  * `global`_ functions
  * `extension`_ classes (template directives, tags)

This additional functionality can then be used in templates.

.. _filter::    http://jinja.pocoo.org/docs/dev/templates/#filters
.. _test::      http://jinja.pocoo.org/docs/dev/templates/#tests
.. _global::    http://jinja.pocoo.org/docs/dev/api/#the-global-namespace
.. _extension:: http://jinja.pocoo.org/docs/dev/templates/#extensions


TEMPLATE LIBRARY EXAMPLE
--------------------------------

.. code-block:: python

    from jinja2_library import Library
    import jinja2.ext

    # -- LIBRARY:
    this_library  = Library()
    register = this_library.make_register_decorator()

    # -- LIBRARY CONTENTS:
    @register.filter
    def my_filter1(arg):
        return transform(arg)

    @register.filter(name="filter2", aliases=["my.filter2"])
    def my_filter2(arg):
        return transform(arg)

    # -- USE LIBRARY WITH JINJA:
    class LibraryExtension(jinja2.ext.Extension):
        # -- NOTE: Add this library functionality to the Jinja2 environment.
        # HINT: Simplifies its usage in Jinja2 template environment.
        def __init__(self, environment):
            super(LibraryExtension, self).__init__(environment)
            this_library.add_to_environment(environment)

.. note::

    The provided mechanism is similar to a `Django template library`_
    (``django.template.Library``). But the Library and the "register" decorator
    functionality is split up into two classes (for a cleaner, simpler design).

    .. _Django template library: https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
"""

from __future__ import absolute_import
import jinja2.ext
import six

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def make_scoped_name(scope, name):
    scoped_name = name
    if scope:
        scoped_name = "%s.%s" % (scope, name)
    return scoped_name


def remove_scope_from_name(scope, name):
    if scope:
        prefix = "%s." % scope
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def dict_assign_scoped(data, scoped_name, value):
    current_dict = data
    name_parts = scoped_name.split(".")
    last_part = name_parts[-1]

    # -- STEP: Select or create storage scope (as dict).
    for name_part in name_parts[:-1]:
        new_dict = current_dict.get(name_part, None)
        if new_dict is None:
            new_dict = current_dict[name_part] = {}
        current_dict = new_dict

    # -- STORAGE-SCOPE FOUND:
    current_dict[last_part] = value


def _ensure_environment_extensions_attribute_exists(environment):
    # -- PREVENT: Environment.extensions problem in constructor.
    _extensions = getattr(environment, "extensions", None)
    if _extensions is None:
        environment.extensions = {}


def add_library_to_environment(library, environment):
    """Add a template library (or similar) to the Jinja2 environment.

    A functional template library contains:

    * filters
    * tests
    * globals
    * extensions (extra tags; derived from: :class:`jinja2.ext.extension.Extension`)
    """
    # assert isinstance(environment, jinja2.environment.Environment)
    environment.filters.update(library.filters)
    environment.tests.update(library.tests)
    # -- SUPPORT: scoped/dotted names for globals
    # REQUIRES: Split up into multiple dicts
    for name, global_func in library.globals.items():
        if "." in name:
            dict_assign_scoped(environment.globals, name, global_func)
        else:
            environment.globals[name] = global_func

    _ensure_environment_extensions_attribute_exists(environment)
    for extension in library.extensions:
        environment.add_extension(extension)


# -----------------------------------------------------------------------------
# CLASS: Library
# -----------------------------------------------------------------------------
class Library(object):
    """Provides a template library (functionality).
    A template library provides additional functionality that can be used
    in templates, like:

    * Jinja2 filters (filter-functions)
    * Jinja2 tests (predicate-functions)
    * Jinja2 globals (global-functions)
    * extensions (tags, directives)

    The library object itself provides a bundle or modules of this extended
    functionality.

    Library Scopes
    --------------------

    The library can be assigned a :attr:`scope` that provides a namespace
    for its extensions.

    .. code:: python

        # -- FILE: jinja_ext_foo.py
        # TEMPLATE LIBRARY: foo (extension: "jinja_ext_foo:LibraryExtension")
        from jinja2_library import Library
        import jinja2.ext

        # -- TEMPLATE LIBRARY (bare bones):
        # HINT: Use Library() to use it without scope/namespace.
        this_library = Library(scope="foo")
        register = this_library.make_register_decorator()

        # -- LIBRARY CONTENTS:
        @register.filter
        def hello(arg):
            return "Hello %s" % arg

        @register.filter(name="hello2, aliases=["ciao"])
        def hello2(arg):
            return "Hello2 %s" % arg

        class LibraryExtension(jinja2.ext.Extension):
            def __init__(self, environment):
                super(LibraryExtension, self).__init__(environment)
                this_library.add_to_environment(environment)

    This scope prefix (as dotted name) must be used in a template
    to use the functional extensions of this library.

    .. code:: jinja

        # -- TEMPLATE EXAMPLE:
        {{"Alice"|foo.hello}}
        {{"Alice"|foo.hello2}}
        {{"Alice"|foo.ciao}}
    """

    def __init__(self, scope=None):
        self.scope = scope
        self.filters = {}
        self.tests = {}
        self.globals = {}
        self.extensions = []

    def make_scoped_name(self, name):
        return make_scoped_name(self.scope, name)

    def _add_to_data(self, data, func, name=None, aliases=None, aliases_scope=None):
        """Core functionality to add a filter, test or global."""
        if name is None:
            name = func.__name__
        scoped_name = self.make_scoped_name(name)
        data[scoped_name] = func
        if aliases:
            if aliases_scope is None:
                aliases_scope = self.scope
            for name in aliases:
                scoped_name = make_scoped_name(aliases_scope, name)
                data[scoped_name] = func
        return self

    def add_filter(self, func, name=None, aliases=None, aliases_scope=None):
        return self._add_to_data(self.filters, func, name=name,
                                 aliases=aliases,
                                 aliases_scope=aliases_scope)

    def add_test(self, func, name=None, aliases=None, aliases_scope=None):
        return self._add_to_data(self.tests, func, name=name,
                                 aliases=aliases,
                                 aliases_scope=aliases_scope)

    def add_global(self, func, name=None, aliases=None, aliases_scope=None):
        return self._add_to_data(self.globals, func, name=name,
                                 aliases=aliases,
                                 aliases_scope=aliases_scope)

    def add_extension(self, extension_class):
        if extension_class not in self.extensions:
            self.extensions.append(extension_class)
        return self

    def make_register_decorator(self, aliases_scope=None):
        return _RegisterToLibraryDecorator(self, aliases_scope)

    def add_to_environment(self, environment):
        add_library_to_environment(self, environment)

    # -- EXPERIMENT:
    # def make_extension_class(self, class_name=None):
    #     """Make a jinja2.ext.Extension class from this library object."""
    #     # -- HINT: Use this Library object as blueprint for Extension class.
    #     import jinja2.ext
    #     this_library = self
    #     class ExtensionClass(jinja2.ext.Extension):
    #         def __init__(self, environment):
    #             jinja2.ext.Extension.__init__(self, environment)
    #             this_library.add_to_environment(environment)
    #     ExtensionClass.__name__ = class_name or "Extension"
    #     return ExtensionClass


class _RegisterToLibraryDecorator(object):
    """Provides decorator functions to register filters, tests, globals and
    extensions (tags) to a library.

    Objects of this class are normally created by the library to which it
    registers to.

    .. code-block:: python

        from jinja2_library import Library
        this_library = Library()
        register = this_library.make_register_decorator()

        @register.filter
        def my_filter1(value, *args, **kwargs): pass

        @register.filter(name="hello", aliases=["hello2"])
        def my_filter2(value, *args): pass

        @register.filter("hello")
        def my_filter3(value, *args): pass

        # -- ALTERNATIVE:
        def my_filter4(value, *args): pass
        register.filter(my_filter4, name="filter4")
    """
    def __init__(self, lib, aliases_scope=None):
        self._lib = lib
        self.aliases_scope = aliases_scope

    # -- REGISTRATION CORE FUNCTIONALITY:
    def _register_filter(self, func, name=None, aliases=None):
        self._lib.add_filter(func, name, aliases, self.aliases_scope)
        return func

    def _register_test(self, func, name=None, aliases=None):
        self._lib.add_test(func, name, aliases, self.aliases_scope)
        return func

    def _register_global(self, func, name=None, aliases=None):
        self._lib.add_global(func, name, aliases, self.aliases_scope)
        return func

    # -- DECORATOR FUNCTIONS:
    def filter(self, func=None, name=None, aliases=None):
        """Decorator to register a Jinja2 filter (function) to the library.
        If no name is provided, the function-name is used as name.
        Note that aliases (sequence-of-names) allow to register the function
        with additional names.

        :param func:  Function to use as filter function.
        :param name:  Use function-name if None (as string).
        :param aliases: Optional, use for additional names (list-of-strings)
        :return: Decorator or registered function.
        """
        # self._lib.add_filter(name, func)
        if isinstance(func, six.string_types) and name is None:
            # -- CORRECT LAZINESS: @register.filter("name")
            name = func
            func = None

        if func is None:
            # CASE: @register.filter()
            # CASE: @register.filter("name", aliases=...)
            # CASE: @register.filter(name="name", aliases=...)
            def decorator(func):
                return self._register_filter(func, name, aliases)
            return decorator
        elif callable(func):
            # CASE: @register.filter
            return self._register_filter(func, name, aliases)
        else:
            message = "Unsupported args: func=%r, name=%r" % (func, name)
            raise AttributeError(message)

    def test(self, func=None, name=None, aliases=None):
        """Decorator to register a Jinja2 test (function) to the library."""
        if isinstance(func, six.string_types) and name is None:
            # -- CORRECT LAZINESS: @register.test("name")
            name = func
            func = None

        if func is None:
            # CASE: @register.test()
            # CASE: @register.test("name", aliases=...)
            # CASE: @register.test(name="name", aliases=...)
            def decorator(func):
                return self._register_test(func, name, aliases)
            return decorator
        elif callable(func):
            # CASE: @register.test
            return self._register_test(func, name, aliases)
        else:
            message = "Unsupported args: func=%r, name=%r" % (func, name)
            raise AttributeError(message)

    def global_(self, func=None, name=None, aliases=None):
        """Decorator to register a Jinja2 global (function) to the library."""
        if isinstance(func, six.string_types) and name is None:
            # CORRECT LAZINESS: @register.global_("name")
            name = func
            func = None

        if func is None:
            # CASE: @register.global_()
            # CASE: @register.global_("name", aliases=...)
            # CASE: @register.global_(name="name", aliases=...)
            def decorator(func):
                return self._register_global(func, name, aliases)
            return decorator
        elif callable(func):
            # CASE: @register.global_
            return self._register_global(func, name, aliases)
        else:
            message = "Unsupported args: func=%r, name=%r" % (func, name)
            raise AttributeError(message)

    def extension(self, extension_class):
        """Decorator to register a Jinja2 extension class (tag) to the library."""
        assert isinstance(extension_class, six.string_types) or \
               issubclass(extension_class, jinja2.ext.Extension), type(extension_class)
        assert extension_class not in self._lib.extensions
        self._lib.add_extension(extension_class)
        return extension_class
