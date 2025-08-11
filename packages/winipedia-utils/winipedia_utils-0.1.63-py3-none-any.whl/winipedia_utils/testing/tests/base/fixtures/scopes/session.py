"""Session-level test fixtures and utilities.

This module provides fixtures and test functions that operate at the session scope,
ensuring that project-wide conventions are followed and that the overall project
structure is correct. These fixtures are automatically applied to the test session
through pytest's autouse mechanism.
"""

from importlib import import_module
from pathlib import Path

from winipedia_utils.consts import _DEV_DEPENDENCIES
from winipedia_utils.git.gitignore.gitignore import _gitignore_is_correct
from winipedia_utils.git.pre_commit.config import (
    _pre_commit_config_is_correct,
)
from winipedia_utils.modules.module import to_path
from winipedia_utils.modules.package import (
    find_packages,
    get_src_package,
    walk_package,
)
from winipedia_utils.projects.poetry.config import (
    _pyproject_tool_configs_are_correct,
    get_poetry_package_name,
    laod_pyproject_toml,
)
from winipedia_utils.testing.assertions import assert_with_msg
from winipedia_utils.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_test_obj_importpath_from_obj,
)
from winipedia_utils.testing.fixtures import autouse_session_fixture
from winipedia_utils.testing.tests.base.utils.utils import (
    _conftest_content_is_correct,
)


@autouse_session_fixture
def _test_dev_dependencies_const_correct() -> None:
    """Verify that the dev dependencies in consts.py are correct.

    This fixture runs once per test session and checks that the dev dependencies
    in consts.py are correct by comparing them to the dev dependencies in
    pyproject.toml.

    Raises:
        AssertionError: If the dev dependencies in consts.py are not correct

    """
    if get_poetry_package_name() != "winipedia_utils":
        # this const is only used in winipedia_utils
        # to be able to install them with setup.py
        return
    toml_dict = laod_pyproject_toml()
    actual_dev_dependencies = (
        toml_dict.get("tool", {})
        .get("poetry", {})
        .get("group", {})
        .get("dev", {})
        .get("dependencies", {})
        .keys()
    )
    assert_with_msg(
        set(actual_dev_dependencies) == set(_DEV_DEPENDENCIES),
        "Dev dependencies in consts.py are not correct",
    )


@autouse_session_fixture
def _test_dev_dependencies_are_in_pyproject_toml() -> None:
    """Verify that the dev dependencies are installed.

    This fixture runs once per test session and checks that the dev dependencies
    are installed by trying to import them.

    Raises:
        ImportError: If a dev dependency is not installed

    """
    toml_dict = laod_pyproject_toml()
    dev_dependencies = (
        toml_dict.get("tool", {})
        .get("poetry", {})
        .get("group", {})
        .get("dev", {})
        .get("dependencies", {})
        .keys()
    )
    assert_with_msg(
        set(_DEV_DEPENDENCIES).issubset(set(dev_dependencies)),
        "Dev dependencies in consts.py are not a subset of the ones in pyproject.toml",
    )


@autouse_session_fixture
def _test_conftest_exists_and_is_correct() -> None:
    """Verify that the conftest.py file exists and has the correct content.

    This fixture runs once per test session and checks that the conftest.py file
    exists in the tests directory and contains the correct pytest_plugins configuration.

    Raises:
        AssertionError: If the conftest.py file doesn't exist or has incorrect content

    """
    conftest_path = Path(TESTS_PACKAGE_NAME, "conftest.py")
    assert_with_msg(
        conftest_path.is_file(),
        f"Expected conftest.py file at {conftest_path} but it doesn't exist",
    )

    assert_with_msg(
        _conftest_content_is_correct(conftest_path),
        "conftest.py has incorrect content",
    )


@autouse_session_fixture
def _test_pyproject_toml_is_correct() -> None:
    """Verify that the pyproject.toml file exists and has the correct content.

    This fixture runs once per test session and checks that the pyproject.toml file
    exists in the root directory and contains the correct content.

    Raises:
        AssertionError: If the pyproject.toml file doesn't exist
                        or has incorrect content

    """
    pyproject_toml_path = Path("pyproject.toml")
    assert_with_msg(
        pyproject_toml_path.is_file(),
        f"Expected pyproject.toml file at {pyproject_toml_path} but it doesn't exist",
    )
    assert_with_msg(
        _pyproject_tool_configs_are_correct(),
        "pyproject.toml has incorrect content.",
    )


@autouse_session_fixture
def _test_pre_commit_config_yaml_is_correct() -> None:
    """Verify that the pre-commit yaml is correctly defining winipedia utils hook.

    Checks that the yaml starts with the winipedia utils hook.
    """
    pre_commit_config = Path(".pre-commit-config.yaml")

    assert_with_msg(
        pre_commit_config.is_file(),
        f"Expected {pre_commit_config} to exist but it doesn't.",
    )
    assert_with_msg(
        _pre_commit_config_is_correct(),
        "Pre commit config is not correct.",
    )


@autouse_session_fixture
def _test_gitignore_is_correct() -> None:
    """Verify that the .gitignore file exists and has the correct content.

    This fixture runs once per test session and checks that the .gitignore file
    exists in the root directory and contains the correct content.

    Raises:
        AssertionError: If the .gitignore file doesn't exist
                        or has incorrect content

    """
    gitignore_path = Path(".gitignore")
    assert_with_msg(
        gitignore_path.is_file(),
        f"Expected {gitignore_path} to exist but it doesn't.",
    )
    assert_with_msg(
        _gitignore_is_correct(),
        "Gitignore is not correct.",
    )


@autouse_session_fixture
def _test_no_namespace_packages() -> None:
    """Verify that there are no namespace packages in the project.

    This fixture runs once per test session and checks that all packages in the
    project are regular packages with __init__.py files, not namespace packages.

    Raises:
        AssertionError: If any namespace packages are found

    """
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)

    any_namespace_packages = set(namespace_packages) - set(packages)
    assert_with_msg(
        not any_namespace_packages,
        f"Found namespace packages: {any_namespace_packages}. "
        f"All packages should have __init__.py files.",
    )


@autouse_session_fixture
def _test_all_src_code_in_one_package() -> None:
    """Verify that all source code is in a single package.

    This fixture runs once per test session and checks that there is only one
    source package besides the tests package.

    Raises:
        AssertionError: If there are multiple source packages

    """
    packages = find_packages(depth=0)
    src_package = get_src_package().__name__
    expected_packages = {TESTS_PACKAGE_NAME, src_package}
    assert_with_msg(
        set(packages) == expected_packages,
        f"Expected only packages {expected_packages}, but found {packages}",
    )


@autouse_session_fixture
def _test_src_package_correctly_named() -> None:
    """Verify that the source package is correctly named.

    This fixture runs once per test session and checks that the source package
    is correctly named after the project.

    Raises:
        AssertionError: If the source package is not correctly named

    """
    src_package = get_src_package().__name__
    assert_with_msg(
        src_package == get_poetry_package_name(),
        f"Expected source package to be named {get_poetry_package_name()}, "
        f"but it is named {src_package}",
    )


@autouse_session_fixture
def _test_py_typed_exists() -> None:
    """Verify that the py.typed file exists in the source package.

    This fixture runs once per test session and checks that the py.typed file
    exists in the source package.

    Raises:
        AssertionError: If the py.typed file doesn't exist

    """
    src_package = get_src_package()
    py_typed_path = to_path(src_package.__name__, is_package=True) / "py.typed"
    assert_with_msg(
        py_typed_path.exists(),
        f"Expected py.typed file to exist at {py_typed_path}",
    )


@autouse_session_fixture
def _test_project_structure_mirrored() -> None:
    """Verify that the project structure is mirrored in tests.

    This fixture runs once per test session and checks that for every package and
    module in the source package, there is a corresponding test package and module.

    Raises:
        AssertionError: If any package or module doesn't have a corresponding test

    """
    src_package = get_src_package()

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    for package, modules in walk_package(src_package):
        test_package_name = make_test_obj_importpath_from_obj(package)
        test_package = import_module(test_package_name)
        assert_with_msg(
            bool(test_package),
            f"Expected test package {test_package_name} to be a module",
        )

        for module in modules:
            test_module_name = make_test_obj_importpath_from_obj(module)
            test_module = import_module(test_module_name)
            assert_with_msg(
                bool(test_module),
                f"Expected test module {test_module_name} to be a module",
            )


@autouse_session_fixture
def _test_no_unitest_package_usage() -> None:
    """Verify that the unittest package is not used in the project.

    This fixture runs once per test session and checks that the unittest package
    is not used in the project.

    Raises:
        AssertionError: If the unittest package is used

    """
    for path in Path().rglob("*.py"):
        if path == to_path(__name__, is_package=False):
            continue
        assert_with_msg(
            "unittest" not in path.read_text(encoding="utf-8"),
            f"Found unittest usage in {path}. Use pytest instead.",
        )
