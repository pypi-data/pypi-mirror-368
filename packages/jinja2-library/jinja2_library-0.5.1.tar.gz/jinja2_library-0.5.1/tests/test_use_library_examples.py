from __future__ import absolute_import, print_function
import os.path
import sys
import pytest

try:
    # -- CASE: Python >= 3.5
    from subprocess import run
except ImportError:
    # -- CASE: Python < 3.5
    run = None

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
TOPDIR = os.path.abspath(os.path.dirname(HERE) or "..")
PYTHON = sys.executable

_ON_WINDOWS = sys.platform.startswith("win32")
_PYTHON_VERSION = sys.version_info[:2]
_CI_ON_WINDOWS_WITH_PY310 = (_ON_WINDOWS
    and ("CI" in os.environ)
    and (_PYTHON_VERSION == (3, 10))
)

# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
@pytest.mark.skipif(run is None, reason="MISSING: subprocess.run()")
@pytest.mark.skipif(_CI_ON_WINDOWS_WITH_PY310, reason="CI: Python Windows platform problem")
class TestLibraryExamples:
    EXAMPLES_EXPECTED_SCRIPT = [
        ("HELLO: Ciao Alice", "example/use_template_library_hello.py"),
        ("HELLO: Ciao Bob",   "example/use_template_library_scoped_hello.py"),
        ("HELLO_2: Ciao Charly", "example/use_template_library_hello2.py"),
    ]

    @pytest.mark.parametrize("expected, script", EXAMPLES_EXPECTED_SCRIPT)
    def test_example(self, expected, script):
        print("SCRIPT: {}".format(script))
        command = "{python} {script}".format(python=PYTHON, script=script)
        result = run(command, capture_output=True, shell=True,
                     env=dict(PYTHONPATH=TOPDIR))
        captured_output = result.stdout.decode("utf-8")
        print(captured_output)
        if result.stderr:
            captured_stderr = result.stderr.decode("utf-8").strip()
            print(captured_stderr, file=sys.stderr)
        assert expected in captured_output
        assert "AssertionError" not in captured_output
        assert result.returncode == 0
