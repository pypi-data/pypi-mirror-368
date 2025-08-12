from __future__ import absolute_import, print_function

import jinja2
from jinja2 import Environment
from jinja2_library import add_library_to_environment, Library
import pytest


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
# TEST SUITE:
# ------------------------------------------------------------------------------
class TestLibraryUsage(object):
    """Ensure that the library functionality can be used in templates."""

    @staticmethod
    def make_template_with_library(template_text, library):
        """Helper function to simplify tests."""
        environment = make_environment()
        add_library_to_environment(library, environment)
        template = environment.from_string(template_text)
        return template


    def test_use_filter(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """{{"Alice"|hello}}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Alice")
        assert output == "Hello Alice"

    def test_use_filter__with_call_args(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """{{"Bob"|hello(greeting="Ciao")}}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Bob")
        assert output == "Ciao Bob"

    @pytest.mark.parametrize("scope", ["foo", "foo.bar"])
    def test_use_filter__with_scoped_library(self, scope):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library(scope)
        register = library.make_register_decorator()

        @register.filter
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """{{"Charly"|%s.hello}}""" % scope
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Charly")
        assert output == "Hello Charly"
        assert scope in template_text

    @pytest.mark.skipif(not hasattr(jinja2, "pass_context"), reason="FOR: jinja2 >= 3.0")
    def test_use_filter__with_jinja2__pass_context_decorator(self):
        """Ensure that jinja2 filter decorators can be used."""
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        @jinja2.pass_context
        def hello(context, value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """{{"Dominik"|hello(greeting="Bonjour")}}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Dominik")
        assert output == "Bonjour Dominik"

    @pytest.mark.skipif(not hasattr(jinja2, "contextfilter"), reason="FOR: jinja2 < 3.0")
    def test_use_filter__with_jinja2__pass_context_decorator(self):
        """Ensure that jinja2 filter decorators can be used."""
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.filter
        @jinja2.contextfilter
        def hello(context, value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """{{"Dominik"|hello(greeting="Bonjour")}}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Dominik")
        assert output == "Bonjour Dominik"

    def test_use_test(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.test
        def even(value):
            return (value % 2) == 0
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST: {{ 10 is even }}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render()
        assert output == "TEST: True"

    def test_use_test__with_call_args(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.test
        def even2(value1, value2):
            return ((value1 + value2) % 2) == 0
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST2: {{ 11 is even2(2) }}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render()
        assert output == "TEST2: False"

    @pytest.mark.parametrize("scope", ["foo", "foo.baz"])
    def test_use_test__with_scoped_library_raises_error(self, scope):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library(scope)
        register = library.make_register_decorator()

        @register.test
        def even3(value):
            return (value % 2) == 0
        # -- LIBRARY MODULE END

        # -- STEP: Use template with library
        template_text = """TEST3: {{ 10 is %s.even3 }}""" % scope
        template = self.make_template_with_library(template_text, library)
        output = template.render()
        assert output == "TEST3: True"
        assert scope in template_text

    def test_use_global(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.global_
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST: {{ hello(name) }}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Alice")
        assert output == "TEST: Hello Alice"

    def test_use_global__with_call_args(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.global_
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST: {{ hello(name, greeting="Bonjour") }}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Bob")
        assert output == "TEST: Bonjour Bob"

    @pytest.mark.parametrize("scope", ["foo", "foo.baz"])
    def test_use_global__with_scoped_library_raises_error(self, scope):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library(scope)
        register = library.make_register_decorator()

        @register.global_
        def hello(value, greeting=None):
            greeting = greeting or "Hello"
            return "{greeting} {name}".format(greeting=greeting, name=value)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST: {{ %s.hello(name) }}""" % scope
        template = self.make_template_with_library(template_text, library)
        output = template.render(name="Charly")
        assert output == "TEST: Hello Charly"
        assert scope in template_text

    def test_use_extension(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        register = library.make_register_decorator()

        @register.extension
        class HelloExtension(jinja2.ext.Extension):
            tags = set(["hello"])

            def parse(self, parser):
                lineno = next(parser.stream).lineno
                body = parser.parse_statements(["name:endhello"],
                                               drop_needle=True)
                return jinja2.nodes.CallBlock(
                    self.call_method("_hello"), [], [], body).set_lineno(lineno)
                # -- RETURN: nodes.CallBlock/Call that is executed later-on.

            def _hello(self, caller):
                captured_text = caller()
                return "HELLO {0}".format(captured_text)
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        template_text = """TEST: {% hello -%} {{ name2 }} {%- endhello %}"""
        template = self.make_template_with_library(template_text, library)
        output = template.render(name2="Alice")
        assert output == "TEST: HELLO Alice"

    def test_use_extension__registered_by_name(self):
        # -- LIBRARY MODULE BEGIN -----------------------------------
        library = Library()
        library.add_extension("example.hello2.LibraryExtension")
        # -- LIBRARY MODULE END -------------------------------------

        # -- STEP: Use template with library
        this_template = """TEST: {% hello -%} {{ name2 }} {%- endhello %}"""
        template = self.make_template_with_library(this_template, library)
        output = template.render(name2="Bob")
        assert output == "TEST: HELLO Bob"
