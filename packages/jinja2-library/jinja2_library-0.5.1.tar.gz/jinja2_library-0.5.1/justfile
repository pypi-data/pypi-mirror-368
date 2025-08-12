# =============================================================================
# justfile: A makefile like build script -- Command Runner
# =============================================================================
# REQUIRES: cargo install just
# REQUIRES: uv tool install rust-just
# PLATFORMS: macOS, Linux, Windows, ...
# USAGE:
#   just --list
#   just <TARGET>
#   just <TARGET> <PARAM_VALUE1> ...
#
# SEE ALSO:
#   * https://github.com/casey/just
# =============================================================================

# -- OPTION: Load environment-variables from "$HERE/.env" file (if exists)
set dotenv-load
set export := true

# -----------------------------------------------------------------------------
# CONFIG:
# -----------------------------------------------------------------------------
HERE := justfile_directory()
MARKER_DIR := HERE
PYTHON_DEFAULT := if os() == "windows" { "python" } else { "python3" }
PYTHON := env_var_or_default("PYTHON", PYTHON_DEFAULT)
PIP := "uv pip"
PIP_INSTALL_OPTIONS := env_var_or_default("PIP_INSTALL_OPTIONS", "--quiet")

PYTEST_OPTIONS   := env_var_or_default("PYTEST_OPTIONS", "")

RMTREE := "rm -rf"
REMOVE := "rm"

# -----------------------------------------------------------------------------
# BUILD RECIPES / TARGETS:
# -----------------------------------------------------------------------------
# DEFAULT-TARGET: Ensure that packages are installed and runs tests.
default: init  test

init: (_ensure-install-packages "all")

# PART=all, testing, ...
install-packages PART="all":
    @echo "INSTALL-PACKAGES: {{PART}} ..."
    {{PIP}} install {{PIP_INSTALL_OPTIONS}} -r py.requirements/{{PART}}.txt
    @touch "{{MARKER_DIR}}/.done.install-packages.{{PART}}"

# ENSURE: Python packages are installed.
_ensure-install-packages PART="all":
    #!/usr/bin/env python3
    from subprocess import run
    from os import path
    if not path.exists("{{MARKER_DIR}}/.done.install-packages.{{PART}}"):
        run("just install-packages {{PART}}", shell=True)

# Run tests.
test *TESTS: (_ensure-install-packages "testing")
    {{PYTHON}} -m pytest {{PYTEST_OPTIONS}} {{TESTS}}

# Determine test coverage by running the tests.
coverage:
    coverage run -m pytest
    coverage combine
    coverage report
    coverage html

# -- PREPARED: lcov support
# coverage lcov
# genhtml build/coverage.lcov --output-directory build/coverage.lcov.html --ignore-errors inconsistent

# Run tox for one Python variant
tox *ARGS: (_ensure-install-packages "use_py27")
    tox {{ARGS}}


# Cleanup most parts (but leave PRECIOUS parts).
cleanup:
    - {{RMTREE}} build
    - {{RMTREE}} dist
    - {{RMTREE}} *.egg-info
    - {{RMTREE}} .pytest_cache
    - {{RMTREE}} .ruff_cache
    - {{REMOVE}} .coverage
    - {{REMOVE}} .done.*

# Cleanup everything.
cleanup-all: cleanup
    - {{RMTREE}} .tox
    - {{RMTREE}} .venv*
    - {{REMOVE}} .python-version
    - {{REMOVE}} uv.lock
