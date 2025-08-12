# -*- coding: utf-8 -*-
"""
Test module for unit-tests of the template library module.

REQUIRE: pytest
"""

from __future__ import absolute_import, print_function
from jinja2 import Environment
from jinja2_library import Library
import pytest
import jinja2
import jinja2.ext


# ------------------------------------------------------------------------------
# TEST SUPPORT:
# ------------------------------------------------------------------------------
JINJA2_EXTENSIONS = [

]

def make_environment(extensions=None, **kwargs):
    extensions = extensions or JINJA2_EXTENSIONS
    return Environment(extensions=extensions, **kwargs)


def render_template(template_text, environment=None, **data):
    environment = Environment(extensions=JINJA2_EXTENSIONS)
    return environment.from_string(template_text).render(**data)


# ------------------------------------------------------------------------------
# TESTSUITE:
# ------------------------------------------------------------------------------
class TestRegisterToLibraryDecorator(object):
    """Test library registration decorator functions."""

    # -- CASE: @register.filter
    def test_filter__as_decorator(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        def func_filter1(value, **kwargs):
            pass

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.filters.get("func_filter1")
        assert registered_func is func_filter1
        assert len(library.filters) == 1

    def test_filter__as_decorator_call_without_params(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter()
        def func_filter2(value, **kwargs):
            pass

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.filters.get("func_filter2")
        assert registered_func is func_filter2
        assert len(library.filters) == 1

    def test_filter__as_decorator_call_with_name_key(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter(name="func_filter3_name")
        def func_filter3(value, **kwargs):
            pass

        # -- CHECK:
        registered_func = library.filters.get("func_filter3_name")
        assert registered_func is func_filter3
        assert len(library.filters) == 1

    def test_filter__as_decorator_call_with_name_arg(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter("func_filter4_name")
        def func_filter4(value, **kwargs):
            pass

        # -- CHECK:
        registered_func = library.filters.get("func_filter4_name")
        assert "func_filter4_name" in library.filters
        assert registered_func is func_filter4
        assert len(library.filters) == 1

    def test_filter__as_decorator_call_with_aliases(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter(aliases=["alias.filter5_1", "alias.filter5_2"])
        def func_filter5(value, **kwargs):
            pass

        # -- CHECK:
        assert set(library.filters.keys()) == \
               set(["func_filter5", "alias.filter5_1", "alias.filter5_2"])
        assert list(library.filters.values()) == ([func_filter5] * 3)
        assert len(library.filters) == 3

    def test_filter__can_call_registered_function(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        def func_hello(value):
            return "Hello %s" % value

        # -- CHECK:
        registered_func = library.filters.get("func_hello")
        assert registered_func is func_hello
        assert "Hello world" == registered_func("world")

    @pytest.mark.parametrize("name, aliases, error", [
        (123,       None,    AttributeError),  # CASE: name has invalid type.
        ("alice",   ["bob"], AttributeError),  # CASE: Unnamed aliases param.
    ])
    def test_filter__with_invalid_args_raises_error(self, name, aliases, error):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        # -- NOTE: Unnamed decorator params may cause problems.
        # error_class = error
        with pytest.raises(error):
            @register.filter(name, aliases)
            def func_filter6(value, **kwargs):
                pass

        # -- CHECK:
        assert len(library.filters) == 0


    # -- CASE: @register.test
    def test_test__as_decorator(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test
        def func_test1(value, **kwargs):
            return True

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.tests.get("func_test1")
        assert registered_func is func_test1
        assert len(library.tests) == 1

    def test_test__as_decorator_call_without_params(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test()
        def func_test2(value, **kwargs):
            return True

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.tests.get("func_test2")
        assert registered_func is func_test2
        assert len(library.tests) == 1

    def test_test__as_decorator_call_with_name_key(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test(name="func_test3_name")
        def func_test3(value, **kwargs):
            return True

        # -- CHECK:
        registered_func = library.tests.get("func_test3_name")
        assert registered_func is func_test3
        assert len(library.tests) == 1

    def test_test__as_decorator_call_with_name_arg(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test("func_test4_name")
        def func_test4(value, **kwargs):
            return True

        # -- CHECK:
        registered_func = library.tests.get("func_test4_name")
        assert "func_test4_name" in library.tests
        assert registered_func is func_test4
        assert len(library.tests) == 1

    def test_test__as_decorator_call_with_aliases(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test(aliases=["alias.test5_1", "alias.test5_2"])
        def func_test5(value, **kwargs):
            return True

        # -- CHECK:
        assert set(library.tests.keys()) == \
               set(["func_test5", "alias.test5_1", "alias.test5_2"])
        assert list(library.tests.values()) == ([func_test5] * 3)
        assert len(library.tests) == 3

    def test_test__can_call_registered_function(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.test
        def func_true(value):
            return bool(value)

        # -- CHECK:
        registered_func = library.tests.get("func_true")
        assert registered_func is func_true
        assert True  == registered_func(1)
        assert False == registered_func(0)

    @pytest.mark.parametrize("name, aliases, error", [
        (123,       None,    AttributeError),  # CASE: name has invalid type.
        ("alice",   ["bob"], AttributeError),  # CASE: Unnamed aliases param.
    ])
    def test_test__with_invalid_args_raises_error(self, name, aliases, error):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        # -- NOTE: Unnamed decorator params may cause problems.
        # error_class = error
        with pytest.raises(error):
            @register.test(name, aliases)
            def func_test6(value):
                return False

        # -- CHECK:
        assert len(library.tests) == 0


    # -- CASE: @register.global_
    def test_global__as_decorator(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_
        def func_global1(value, **kwargs):
            pass

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.globals.get("func_global1")
        assert registered_func is func_global1
        assert len(library.globals) == 1

    def test_global__as_decorator_call_without_params(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_()
        def func_global2(value, **kwargs):
            pass

        # -- CHECK:
        # NOTE: function.__name__ is used name if none is provided.
        registered_func = library.globals.get("func_global2")
        assert registered_func is func_global2
        assert len(library.globals) == 1

    def test_global__as_decorator_call_with_name_key(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_(name="func_global3_name")
        def func_global3(value, **kwargs):
            pass

        # -- CHECK:
        registered_func = library.globals.get("func_global3_name")
        assert registered_func is func_global3
        assert len(library.globals) == 1

    def test_global__as_decorator_call_with_name_arg(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_("func_global4_name")
        def func_global4(value, **kwargs):
            pass

        # -- CHECK:
        registered_func = library.globals.get("func_global4_name")
        assert "func_global4_name" in library.globals
        assert registered_func is func_global4
        assert len(library.globals) == 1

    def test_global__as_decorator_call_with_aliases(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_(aliases=["alias.global5_1", "alias.global5_2"])
        def func_global5(value, **kwargs):
            pass

        # -- CHECK:
        assert set(library.globals.keys()) == \
               set(["func_global5", "alias.global5_1", "alias.global5_2"])
        assert list(library.globals.values()) == ([func_global5] * 3)
        assert len(library.globals) == 3

    def test_global__can_call_registered_function(self):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.global_
        def func_hello(value):
            return "Hello %s" % value

        # -- CHECK:
        registered_func = library.globals.get("func_hello")
        assert registered_func is func_hello
        assert "Hello world" == registered_func("world")

    @pytest.mark.parametrize("name, aliases, error", [
        (123,       None,    AttributeError),  # CASE: name has invalid type.
        ("alice",   ["bob"], AttributeError),  # CASE: Unnamed aliases param.
    ])
    def test_global__with_invalid_args_raises_error(self, name, aliases, error):
        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        # -- NOTE: Unnamed decorator params may cause problems.
        # error_class = error
        with pytest.raises(error):
            @register.global_(name, aliases)
            def func_global6(value, **kwargs):
                pass

        # -- CHECK:
        assert len(library.globals) == 0

    def test_extension__with_extension_class(self):

        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.extension
        class AliceExtension(jinja2.ext.Extension):
            tags = set(["alice"])
            def parse(self, parser): pass

        # -- CHECK:
        assert library.extensions == [AliceExtension]

    def test_extension__raises_error_for_known_extension(self):

        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()

        @register.extension
        class AliceExtension(jinja2.ext.Extension):
            tags = set(["alice"])
            def parse(self, parser): pass

        # -- CHECK: Register extension again.
        with pytest.raises(AssertionError):
            register.extension(AliceExtension)


    def test_extension__with_extension_name(self):

        # -- BLUEPRINT:
        library = Library()
        register = library.make_register_decorator()
        register.extension("my_module.AliceExtension")

        # -- CHECK:
        assert library.extensions == ["my_module.AliceExtension"]

class TestLibrary(object):

    def test_add_filter__with_unscoped_library(self):
        library = Library()
        def my_filter(x):
            pass

        library.add_filter(my_filter, "my_filter")
        assert "my_filter" in library.filters
        assert library.filters["my_filter"] is my_filter

    @pytest.mark.parametrize("scope", ["foo", "foo.bar"])
    def test_add_filter__with_scoped_library(self, scope):
        library = Library(scope)
        def my_filter(x):
            pass

        unscoped_name = "my_filter"
        scoped_name = "%s.%s" % (scope, unscoped_name)
        library.add_filter(my_filter, "my_filter")
        assert scoped_name in library.filters
        assert unscoped_name not in library.filters
        assert library.filters[scoped_name] is my_filter


    def test_add_test__with_unscoped_library(self):
        library = Library()
        def my_test(value):
            return bool(value)

        library.add_test(my_test, "my_test")
        assert "my_test" in library.tests
        assert library.tests["my_test"] is my_test

    @pytest.mark.parametrize("scope", ["foo", "foo.bar"])
    def test_add_test__with_scoped_library(self, scope):
        library = Library(scope)
        def my_test(value):
            return bool(value)

        library.add_test(my_test, "my_test")
        unscoped_name = "my_test"
        scoped_name = "%s.%s" % (scope, unscoped_name)
        assert scoped_name in library.tests
        assert unscoped_name not in library.tests
        assert library.tests[scoped_name] is my_test

    def test_add_global__with_unscoped_library(self):
        library = Library()
        def my_global(value):
            return value

        library.add_global(my_global, "my_global")
        assert "my_global" in library.globals
        assert library.globals["my_global"] is my_global

    @pytest.mark.parametrize("scope", ["foo", "foo.bar"])
    def test_add_global__with_scoped_library(self, scope):
        library = Library(scope)
        def my_global(value):
            return value

        library.add_global(my_global, "my_global")

        unscoped_name = "my_global"
        scoped_name = "%s.%s" % (scope, unscoped_name)
        assert scoped_name in library.globals
        assert unscoped_name not in library.globals
        assert library.globals[scoped_name] is my_global

    def test_add_extension__by_class(self):
        import jinja2.ext
        class MyExtension(jinja2.ext.Extension): pass

        library = Library()
        library.add_extension(MyExtension)
        assert MyExtension in library.extensions

    def test_add_extension__by_scoped_name(self):
        library = Library()
        library.add_extension("jinja2.ext.i18n")
        assert "jinja2.ext.i18n" in library.extensions
