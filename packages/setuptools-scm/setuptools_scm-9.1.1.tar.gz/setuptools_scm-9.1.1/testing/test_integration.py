from __future__ import annotations

import importlib.metadata
import logging
import os
import re
import subprocess
import sys
import textwrap

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import pytest

from packaging.version import Version

from setuptools_scm._integration import setuptools as setuptools_integration
from setuptools_scm._requirement_cls import extract_package_name

if TYPE_CHECKING:
    import setuptools

from setuptools_scm import Configuration
from setuptools_scm._integration.setuptools import _warn_on_old_setuptools
from setuptools_scm._overrides import PRETEND_KEY
from setuptools_scm._overrides import PRETEND_KEY_NAMED
from setuptools_scm._run_cmd import run

from .wd_wrapper import WorkDir

c = Configuration()


@pytest.fixture
def wd(wd: WorkDir) -> WorkDir:
    wd("git init")
    wd("git config user.email test@example.com")
    wd('git config user.name "a test"')
    wd.add_command = "git add ."
    wd.commit_command = "git commit -m test-{reason}"
    return wd


def test_pyproject_support(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")
    monkeypatch.delenv("SETUPTOOLS_SCM_DEBUG")
    pkg = tmp_path / "package"
    pkg.mkdir()
    pkg.joinpath("pyproject.toml").write_text(
        textwrap.dedent(
            """
            [tool.setuptools_scm]
            fallback_version = "12.34"
            [project]
            name = "foo"
            description = "Factory ⸻ A code generator 🏭"
            authors = [{name = "Łukasz Langa"}]
            dynamic = ["version"]
            """
        ),
        encoding="utf-8",
    )
    pkg.joinpath("setup.py").write_text(
        "__import__('setuptools').setup()", encoding="utf-8"
    )
    res = run([sys.executable, "setup.py", "--version"], pkg)
    assert res.stdout == "12.34"


PYPROJECT_FILES = {
    "setup.py": "[tool.setuptools_scm]\n",
    "setup.cfg": "[tool.setuptools_scm]\n",
    "pyproject tool.setuptools_scm": (
        "[project]\nname='setuptools_scm_example'\n[tool.setuptools_scm]"
    ),
    "pyproject.project": (
        "[project]\nname='setuptools_scm_example'\n"
        "dynamic=['version']\n[tool.setuptools_scm]"
    ),
}

SETUP_PY_PLAIN = "__import__('setuptools').setup()"
SETUP_PY_WITH_NAME = "__import__('setuptools').setup(name='setuptools_scm_example')"

SETUP_PY_FILES = {
    "setup.py": SETUP_PY_WITH_NAME,
    "setup.cfg": SETUP_PY_PLAIN,
    "pyproject tool.setuptools_scm": SETUP_PY_PLAIN,
    "pyproject.project": SETUP_PY_PLAIN,
}

SETUP_CFG_FILES = {
    "setup.py": "",
    "setup.cfg": "[metadata]\nname=setuptools_scm_example",
    "pyproject tool.setuptools_scm": "",
    "pyproject.project": "",
}

with_metadata_in = pytest.mark.parametrize(
    "metadata_in",
    ["setup.py", "setup.cfg", "pyproject tool.setuptools_scm", "pyproject.project"],
)


@with_metadata_in
def test_pyproject_support_with_git(wd: WorkDir, metadata_in: str) -> None:
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Write files first
    if metadata_in == "pyproject tool.setuptools_scm":
        wd.write(
            "pyproject.toml",
            textwrap.dedent(
                """
                [build-system]
                requires = ["setuptools>=80", "setuptools-scm>=8"]
                build-backend = "setuptools.build_meta"

                [tool.setuptools_scm]
                dist_name='setuptools_scm_example'
                """
            ),
        )
    elif metadata_in == "pyproject.project":
        wd.write(
            "pyproject.toml",
            textwrap.dedent(
                """
                [build-system]
                requires = ["setuptools>=80", "setuptools-scm>=8"]
                build-backend = "setuptools.build_meta"

                [project]
                name='setuptools_scm_example'
                dynamic=['version']
                [tool.setuptools_scm]
                """
            ),
        )
    else:
        # For "setup.py" and "setup.cfg" cases, use the PYPROJECT_FILES content
        wd.write("pyproject.toml", PYPROJECT_FILES[metadata_in])

    wd.write("setup.py", SETUP_PY_FILES[metadata_in])
    wd.write("setup.cfg", SETUP_CFG_FILES[metadata_in])

    # Now do git operations
    wd("git init")
    wd("git config user.email test@example.com")
    wd('git config user.name "a test"')
    wd("git add .")
    wd('git commit -m "initial"')
    wd("git tag v1.0.0")

    res = run([sys.executable, "setup.py", "--version"], wd.cwd)
    assert res.stdout == "1.0.0"


def test_pyproject_no_project_section_no_auto_activation(wd: WorkDir) -> None:
    """Test that setuptools_scm doesn't auto-activate when pyproject.toml has no project section."""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Create pyproject.toml with setuptools-scm in build-system.requires but no project section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=80", "setuptools-scm>=8"]
            build-backend = "setuptools.build_meta"
            """
        ),
    )

    wd.write("setup.py", "__import__('setuptools').setup(name='test_package')")

    # Now do git operations
    wd("git init")
    wd("git config user.email test@example.com")
    wd('git config user.name "a test"')
    wd("git add .")
    wd('git commit -m "initial"')
    wd("git tag v1.0.0")

    # Should not auto-activate setuptools_scm, so version should be None
    res = run([sys.executable, "setup.py", "--version"], wd.cwd)
    print(f"Version output: {res.stdout!r}")
    # The version should not be from setuptools_scm (which would be 1.0.0 from git tag)
    # but should be the default setuptools version (0.0.0)
    assert res.stdout == "0.0.0"  # Default version when no version is set


def test_pyproject_no_project_section_no_error(wd: WorkDir) -> None:
    """Test that setuptools_scm doesn't raise an error when there's no project section."""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Create pyproject.toml with setuptools-scm in build-system.requires but no project section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=80", "setuptools-scm>=8"]
            build-backend = "setuptools.build_meta"
            """
        ),
    )

    # This should NOT raise an error because there's no project section
    # setuptools_scm should simply not auto-activate
    from setuptools_scm._integration.pyproject_reading import read_pyproject

    pyproject_data = read_pyproject(wd.cwd / "pyproject.toml")
    # Should not auto-activate when no project section exists
    assert not pyproject_data.is_required or not pyproject_data.section_present


@pytest.mark.parametrize("use_scm_version", ["True", "{}", "lambda: {}"])
def test_pyproject_missing_setup_hook_works(wd: WorkDir, use_scm_version: str) -> None:
    wd.write(
        "setup.py",
        f"""__import__('setuptools').setup(
    name="example-scm-unique",
    use_scm_version={use_scm_version},
    )""",
    )
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires=["setuptools", "setuptools_scm"]
            build-backend = "setuptools.build_meta"
            [tool.setuptools_scm]
            """
        ),
    )

    res = subprocess.run(
        [sys.executable, "setup.py", "--version"],
        cwd=wd.cwd,
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    stripped = res.stdout.strip()
    assert stripped.endswith("0.1.dev0+d20090213")

    res_build = subprocess.run(
        [sys.executable, "-m", "build", "-nxw"],
        env={k: v for k, v in os.environ.items() if k != "SETUPTOOLS_SCM_DEBUG"},
        cwd=wd.cwd,
    )
    import pprint

    pprint.pprint(res_build)
    wheel: Path = next(wd.cwd.joinpath("dist").iterdir())
    assert "0.1.dev0+d20090213" in str(wheel)


def test_pretend_version(monkeypatch: pytest.MonkeyPatch, wd: WorkDir) -> None:
    monkeypatch.setenv(PRETEND_KEY, "1.0.0")

    assert wd.get_version() == "1.0.0"
    assert wd.get_version(dist_name="ignored") == "1.0.0"


@with_metadata_in
def test_pretend_version_named_pyproject_integration(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir, metadata_in: str
) -> None:
    test_pyproject_support_with_git(wd, metadata_in)
    monkeypatch.setenv(
        PRETEND_KEY_NAMED.format(name="setuptools_scm_example".upper()), "3.2.1"
    )
    res = wd([sys.executable, "setup.py", "--version"])
    assert res.endswith("3.2.1")


def test_pretend_version_named(monkeypatch: pytest.MonkeyPatch, wd: WorkDir) -> None:
    monkeypatch.setenv(PRETEND_KEY_NAMED.format(name="test".upper()), "1.0.0")
    monkeypatch.setenv(PRETEND_KEY_NAMED.format(name="test2".upper()), "2.0.0")
    assert wd.get_version(dist_name="test") == "1.0.0"
    assert wd.get_version(dist_name="test2") == "2.0.0"


def test_pretend_version_name_takes_precedence(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir
) -> None:
    monkeypatch.setenv(PRETEND_KEY_NAMED.format(name="test".upper()), "1.0.0")
    monkeypatch.setenv(PRETEND_KEY, "2.0.0")
    assert wd.get_version(dist_name="test") == "1.0.0"


def test_pretend_version_rejects_invalid_string(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir
) -> None:
    """Test that invalid pretend versions raise errors and bubble up."""
    monkeypatch.setenv(PRETEND_KEY, "dummy")
    wd.write("setup.py", SETUP_PY_PLAIN)

    # With strict validation, invalid pretend versions should raise errors
    with pytest.raises(Exception, match=r".*dummy.*"):
        wd.get_version(write_to="test.py")


def test_pretend_metadata_with_version(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir
) -> None:
    """Test pretend metadata overrides work with pretend version."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    monkeypatch.setenv(PRETEND_KEY, "1.2.3.dev4+g1337beef")
    monkeypatch.setenv(PRETEND_METADATA_KEY, '{node="g1337beef", distance=4}')

    version = wd.get_version()
    assert version == "1.2.3.dev4+g1337beef"

    # Test version file template functionality
    wd.write("setup.py", SETUP_PY_PLAIN)
    wd("mkdir -p src")
    version_file_content = """
version = '{version}'
major = {version_tuple[0]}
minor = {version_tuple[1]}
patch = {version_tuple[2]}
commit_hash = '{scm_version.short_node}'
num_commit = {scm_version.distance}
"""  # noqa: RUF027
    # Use write_to with template to create version file
    version = wd.get_version(
        write_to="src/version.py", write_to_template=version_file_content
    )

    content = (wd.cwd / "src/version.py").read_text(encoding="utf-8")
    assert "commit_hash = 'g1337beef'" in content
    assert "num_commit = 4" in content


def test_pretend_metadata_named(monkeypatch: pytest.MonkeyPatch, wd: WorkDir) -> None:
    """Test pretend metadata with named package support."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY_NAMED

    monkeypatch.setenv(
        PRETEND_KEY_NAMED.format(name="test".upper()), "1.2.3.dev5+gabcdef12"
    )
    monkeypatch.setenv(
        PRETEND_METADATA_KEY_NAMED.format(name="test".upper()),
        '{node="gabcdef12", distance=5, dirty=true}',
    )

    version = wd.get_version(dist_name="test")
    assert version == "1.2.3.dev5+gabcdef12"


def test_pretend_metadata_without_version_warns(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that pretend metadata without any base version logs a warning."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    # Only set metadata, no version - but there will be a git repo so there will be a base version
    # Let's create an empty git repo without commits to truly have no base version
    monkeypatch.setenv(PRETEND_METADATA_KEY, '{node="g1234567", distance=2}')

    with caplog.at_level(logging.WARNING):
        version = wd.get_version()
        assert version is not None

    # In this case, metadata was applied to a fallback version, so no warning about missing base


def test_pretend_metadata_with_scm_version(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that pretend metadata works with actual SCM-detected version."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    # Set up a git repo with a tag so we have a base version
    wd("git init")
    wd("git config user.name test")
    wd("git config user.email test@example.com")
    wd.write("file.txt", "content")
    wd("git add file.txt")
    wd("git commit -m 'initial'")
    wd("git tag v1.0.0")

    # Now add metadata overrides
    monkeypatch.setenv(PRETEND_METADATA_KEY, '{node="gcustom123", distance=7}')

    # Test that the metadata gets applied to the actual SCM version
    version = wd.get_version()
    # The version becomes 1.0.1.dev7+gcustom123 due to version scheme and metadata overrides
    assert "1.0.1.dev7+gcustom123" == version

    # Test version file to see if metadata was applied
    wd.write("setup.py", SETUP_PY_PLAIN)
    wd("mkdir -p src")
    version_file_content = """
version = '{version}'
commit_hash = '{scm_version.short_node}'
num_commit = {scm_version.distance}
"""  # noqa: RUF027
    version = wd.get_version(
        write_to="src/version.py", write_to_template=version_file_content
    )

    content = (wd.cwd / "src/version.py").read_text(encoding="utf-8")
    assert "commit_hash = 'gcustom123'" in content
    assert "num_commit = 7" in content


def test_pretend_metadata_type_conversion(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir
) -> None:
    """Test that pretend metadata properly uses TOML native types."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    monkeypatch.setenv(PRETEND_KEY, "2.0.0")
    monkeypatch.setenv(
        PRETEND_METADATA_KEY,
        '{distance=10, dirty=true, node="gfedcba98", branch="feature-branch"}',
    )

    version = wd.get_version()
    # The version should be formatted properly with the metadata
    assert "2.0.0" in version


def test_pretend_metadata_invalid_fields_filtered(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that invalid metadata fields are filtered out with a warning."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    monkeypatch.setenv(PRETEND_KEY, "1.0.0")
    monkeypatch.setenv(
        PRETEND_METADATA_KEY,
        '{node="g123456", distance=3, invalid_field="should_be_ignored", another_bad_field=42}',
    )

    with caplog.at_level(logging.WARNING):
        version = wd.get_version()
        assert version == "1.0.0"

    assert "Invalid metadata fields in pretend metadata" in caplog.text
    assert "invalid_field" in caplog.text
    assert "another_bad_field" in caplog.text


def test_pretend_metadata_date_parsing(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir
) -> None:
    """Test that TOML date values work in pretend metadata."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    monkeypatch.setenv(PRETEND_KEY, "1.5.0")
    monkeypatch.setenv(
        PRETEND_METADATA_KEY, '{node="g987654", distance=7, node_date=2024-01-15}'
    )

    version = wd.get_version()
    assert version == "1.5.0"


def test_pretend_metadata_invalid_toml_error(
    monkeypatch: pytest.MonkeyPatch, wd: WorkDir, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that invalid TOML in pretend metadata logs an error."""
    from setuptools_scm._overrides import PRETEND_METADATA_KEY

    monkeypatch.setenv(PRETEND_KEY, "1.0.0")
    monkeypatch.setenv(PRETEND_METADATA_KEY, "{invalid toml syntax here}")

    with caplog.at_level(logging.ERROR):
        version = wd.get_version()
        # Should fall back to basic pretend version
        assert version == "1.0.0"

    assert "Failed to parse pretend metadata" in caplog.text


def test_git_tag_with_local_build_data_preserved(wd: WorkDir) -> None:
    """Test that git tags containing local build data are preserved in final version."""
    wd.commit_testfile()

    # Create a git tag that includes local build data
    # This simulates a CI system that creates tags with build metadata
    wd("git tag 1.0.0+build.123")

    # The version should preserve the build metadata from the tag
    version = wd.get_version()

    # Validate it's a proper PEP 440 version
    parsed_version = Version(version)
    assert str(parsed_version) == version, (
        f"Version should parse correctly as PEP 440: {version}"
    )

    assert version == "1.0.0+build.123", (
        f"Expected build metadata preserved, got {version}"
    )

    # Validate the local part is correct
    assert parsed_version.local == "build.123", (
        f"Expected local part 'build.123', got {parsed_version.local}"
    )


def test_git_tag_with_commit_hash_preserved(wd: WorkDir) -> None:
    """Test that git tags with commit hash data are preserved."""
    wd.commit_testfile()

    # Create a git tag that includes commit hash metadata
    wd("git tag 2.0.0+sha.abcd1234")

    # The version should preserve the commit hash from the tag
    version = wd.get_version()

    # Validate it's a proper PEP 440 version
    parsed_version = Version(version)
    assert str(parsed_version) == version, (
        f"Version should parse correctly as PEP 440: {version}"
    )

    assert version == "2.0.0+sha.abcd1234"

    # Validate the local part is correct
    assert parsed_version.local == "sha.abcd1234", (
        f"Expected local part 'sha.abcd1234', got {parsed_version.local}"
    )


def test_git_tag_with_local_build_data_preserved_dirty_workdir(wd: WorkDir) -> None:
    """Test that git tags with local build data are preserved even with dirty working directory."""
    wd.commit_testfile()

    # Create a git tag that includes local build data
    wd("git tag 1.5.0+build.456")

    # Make working directory dirty
    wd.write("modified_file.txt", "some changes")

    # The version should preserve the build metadata from the tag
    # even when working directory is dirty
    version = wd.get_version()

    # Validate it's a proper PEP 440 version
    parsed_version = Version(version)
    assert str(parsed_version) == version, (
        f"Version should parse correctly as PEP 440: {version}"
    )

    assert version == "1.5.0+build.456", (
        f"Expected build metadata preserved with dirty workdir, got {version}"
    )

    # Validate the local part is correct
    assert parsed_version.local == "build.456", (
        f"Expected local part 'build.456', got {parsed_version.local}"
    )


def test_git_tag_with_local_build_data_preserved_with_distance(wd: WorkDir) -> None:
    """Test that git tags with local build data are preserved with distance."""
    wd.commit_testfile()

    # Create a git tag that includes local build data
    wd("git tag 3.0.0+ci.789")

    # Add another commit after the tag to create distance
    wd.commit_testfile("after-tag")

    # The version should use version scheme for distance but preserve original tag's build data
    version = wd.get_version()

    # Validate it's a proper PEP 440 version
    parsed_version = Version(version)
    assert str(parsed_version) == version, (
        f"Version should parse correctly as PEP 440: {version}"
    )

    # Tag local data should be preserved and combined with SCM data
    assert version.startswith("3.0.1.dev1"), (
        f"Expected dev version with distance, got {version}"
    )

    # Use regex to validate the version format with both tag build data and SCM node data
    # Expected format: 3.0.1.dev1+ci.789.g<commit_hash>
    version_pattern = r"^3\.0\.1\.dev1\+ci\.789\.g[a-f0-9]+$"
    assert re.match(version_pattern, version), (
        f"Version should match pattern {version_pattern}, got {version}"
    )

    # The original tag's local data (+ci.789) should be preserved and combined with SCM data
    assert "+ci.789" in version, f"Tag local data should be preserved, got {version}"

    # Validate the local part contains both tag and SCM node information
    assert parsed_version.local is not None, (
        f"Expected local version part, got {parsed_version.local}"
    )
    assert "ci.789" in parsed_version.local, (
        f"Expected local part to contain tag data 'ci.789', got {parsed_version.local}"
    )
    assert "g" in parsed_version.local, (
        f"Expected local part to contain SCM node data 'g...', got {parsed_version.local}"
    )

    # Note: This test verifies that local build data from tags is preserved and combined
    # with SCM data when there's distance, which is the desired behavior for issue 1019.


def testwarn_on_broken_setuptools() -> None:
    _warn_on_old_setuptools("61")
    with pytest.warns(RuntimeWarning, match="ERROR: setuptools==60"):
        _warn_on_old_setuptools("60")


@pytest.mark.issue(611)
def test_distribution_provides_extras() -> None:
    from importlib.metadata import distribution

    dist = distribution("setuptools_scm")
    pe: list[str] = dist.metadata.get_all("Provides-Extra", [])
    assert sorted(pe) == ["rich", "toml"]


@pytest.mark.issue(760)
def test_unicode_in_setup_cfg(tmp_path: Path) -> None:
    cfg = tmp_path / "setup.cfg"
    cfg.write_text(
        textwrap.dedent(
            """
            [metadata]
            name = configparser
            author = Łukasz Langa
            """
        ),
        encoding="utf-8",
    )
    from setuptools_scm._integration.setup_cfg import read_dist_name_from_setup_cfg

    name = read_dist_name_from_setup_cfg(cfg)
    assert name == "configparser"


def test_setuptools_version_keyword_ensures_regex(
    wd: WorkDir,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wd.commit_testfile("test")
    wd("git tag 1.0")
    monkeypatch.chdir(wd.cwd)

    dist = create_clean_distribution("test")
    setuptools_integration.version_keyword(
        dist, "use_scm_version", {"tag_regex": "(1.0)"}
    )
    assert dist.metadata.version == "1.0"


@pytest.mark.parametrize(
    "ep_name", ["setuptools_scm.parse_scm", "setuptools_scm.parse_scm_fallback"]
)
def test_git_archival_plugin_ignored(tmp_path: Path, ep_name: str) -> None:
    tmp_path.joinpath(".git_archival.txt").write_text("broken", encoding="utf-8")
    try:
        dist = importlib.metadata.distribution("setuptools_scm_git_archive")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("setuptools_scm_git_archive not installed")
    else:
        print(dist.metadata["Name"], dist.version)
    from setuptools_scm.discover import iter_matching_entrypoints

    found = list(iter_matching_entrypoints(tmp_path, config=c, entrypoint=ep_name))
    imports = [item.value for item in found]
    assert "setuptools_scm_git_archive:parse" not in imports


def test_pyproject_build_system_requires_setuptools_scm(wd: WorkDir) -> None:
    """Test that setuptools_scm is enabled when present in build-system.requires"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Test with setuptools_scm in build-system.requires but no [tool.setuptools_scm] section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools_scm>=8"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )
    wd.write("setup.py", "__import__('setuptools').setup()")

    res = wd([sys.executable, "setup.py", "--version"])
    assert res.endswith("0.1.dev0+d20090213")


def test_pyproject_build_system_requires_setuptools_scm_dash_variant(
    wd: WorkDir,
) -> None:
    """Test that setuptools-scm (dash variant) is also detected in build-system.requires"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Test with setuptools-scm (dash variant) in build-system.requires
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools-scm>=8"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )
    wd.write("setup.py", "__import__('setuptools').setup()")

    res = wd([sys.executable, "setup.py", "--version"])
    assert res.endswith("0.1.dev0+d20090213")


def test_pyproject_build_system_requires_with_extras(wd: WorkDir) -> None:
    """Test that setuptools_scm[toml] is detected in build-system.requires"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Test with setuptools_scm[toml] (with extras) in build-system.requires
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools_scm[toml]>=8"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )
    wd.write("setup.py", "__import__('setuptools').setup()")

    res = wd([sys.executable, "setup.py", "--version"])
    assert res.endswith("0.1.dev0+d20090213")


def test_pyproject_build_system_requires_not_present(wd: WorkDir) -> None:
    """Test that version is not set when setuptools_scm is not in build-system.requires and no [tool.setuptools_scm] section"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Test without setuptools_scm in build-system.requires and no [tool.setuptools_scm] section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "wheel"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )
    wd.write("setup.py", "__import__('setuptools').setup()")

    res = wd([sys.executable, "setup.py", "--version"])
    assert res == "0.0.0"


def test_pyproject_build_system_requires_priority_over_tool_section(
    wd: WorkDir,
) -> None:
    """Test that both build-system.requires and [tool.setuptools_scm] section work together"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Test with both setuptools_scm in build-system.requires AND [tool.setuptools_scm] section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools_scm>=8"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "test-package"
            dynamic = ["version"]

            [tool.setuptools_scm]
            # empty section, should work with build-system detection
            """
        ),
    )
    wd.write("setup.py", "__import__('setuptools').setup()")

    res = wd([sys.executable, "setup.py", "--version"])
    assert res.endswith("0.1.dev0+d20090213")


@pytest.mark.parametrize("base_name", ["setuptools_scm", "setuptools-scm"])
@pytest.mark.parametrize(
    "requirements",
    ["", ">=8", "[toml]>=7", "~=9.0", "[rich,toml]>=8"],
    ids=["empty", "version", "extras", "fuzzy", "multiple-extras"],
)
def test_extract_package_name(base_name: str, requirements: str) -> None:
    """Test the _extract_package_name helper function"""
    assert extract_package_name(f"{base_name}{requirements}") == "setuptools-scm"


def test_build_requires_integration_with_config_reading(wd: WorkDir) -> None:
    """Test that Configuration.from_file handles build-system.requires automatically"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    from setuptools_scm._config import Configuration

    # Test: pyproject.toml with setuptools_scm in build-system.requires but no tool section
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools_scm>=8"]

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )

    # This should NOT raise an error because setuptools_scm is in build-system.requires
    config = Configuration.from_file(
        name=wd.cwd.joinpath("pyproject.toml"), dist_name="test-package"
    )
    assert config.dist_name == "test-package"

    # Test: pyproject.toml with setuptools-scm (dash variant) in build-system.requires
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=64", "setuptools-scm>=8"]

            [project]
            name = "test-package"
            dynamic = ["version"]
            """
        ),
    )

    # This should also NOT raise an error
    config = Configuration.from_file(
        name=wd.cwd.joinpath("pyproject.toml"), dist_name="test-package"
    )
    assert config.dist_name == "test-package"


def test_improved_error_message_mentions_both_config_options(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that the error message mentions both configuration options"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Create pyproject.toml without setuptools_scm configuration
    wd.write(
        "pyproject.toml",
        textwrap.dedent(
            """
            [project]
            name = "test-package"

            [build-system]
            requires = ["setuptools>=64"]
            """
        ),
    )

    from setuptools_scm._config import Configuration

    with pytest.raises(LookupError) as exc_info:
        Configuration.from_file(
            name=wd.cwd.joinpath("pyproject.toml"),
            dist_name="test-package",
            missing_file_ok=False,
        )

    error_msg = str(exc_info.value)
    # Check that the error message mentions both configuration options
    assert "tool.setuptools_scm" in error_msg
    assert "build-system" in error_msg
    assert "requires" in error_msg


# Helper function for creating and managing distribution objects
def create_clean_distribution(name: str) -> setuptools.Distribution:
    """Create a clean distribution object without any setuptools_scm effects.

    This function creates a new setuptools Distribution and ensures it's completely
    clean from any previous setuptools_scm version inference effects, including:
    - Clearing any existing version
    - Removing the _setuptools_scm_version_set_by_infer flag
    """
    import setuptools

    dist = setuptools.Distribution({"name": name})

    # Clean all setuptools_scm effects
    dist.metadata.version = None
    if hasattr(dist, "_setuptools_scm_version_set_by_infer"):
        delattr(dist, "_setuptools_scm_version_set_by_infer")

    return dist


def version_keyword_default(dist: setuptools.Distribution) -> None:
    """Helper to call version_keyword with default config and return the result."""

    setuptools_integration.version_keyword(dist, "use_scm_version", True)


def version_keyword_calver(dist: setuptools.Distribution) -> None:
    """Helper to call version_keyword with calver-by-date scheme and return the result."""

    setuptools_integration.version_keyword(
        dist, "use_scm_version", {"version_scheme": "calver-by-date"}
    )


# Test cases: (first_func, second_func, expected_final_version)
# We use a controlled date to make calver deterministic
TEST_CASES = [
    # Real-world scenarios: infer_version and version_keyword can be called in either order
    (setuptools_integration.infer_version, version_keyword_default, "1.0.1.dev1"),
    (
        setuptools_integration.infer_version,
        version_keyword_calver,
        "9.2.13.0.dev1",
    ),  # calver should win but doesn't
    (version_keyword_default, setuptools_integration.infer_version, "1.0.1.dev1"),
    (version_keyword_calver, setuptools_integration.infer_version, "9.2.13.0.dev1"),
]


@pytest.mark.issue("https://github.com/pypa/setuptools_scm/issues/1022")
@pytest.mark.filterwarnings("ignore:version of .* already set:UserWarning")
@pytest.mark.filterwarnings(
    "ignore:.* does not correspond to a valid versioning date.*:UserWarning"
)
@pytest.mark.parametrize(
    ("first_integration", "second_integration", "expected_final_version"),
    TEST_CASES,
)
def test_integration_function_call_order(
    wd: WorkDir,
    monkeypatch: pytest.MonkeyPatch,
    first_integration: Any,
    second_integration: Any,
    expected_final_version: str,
) -> None:
    """Test that integration functions can be called in any order.

    version_keyword should always win when it specifies configuration, but currently doesn't.
    Some tests will fail, showing the bug.
    """
    # Set up controlled environment for deterministic versions
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234567890")  # 2009-02-13T23:31:30+00:00
    # Override node_date to get consistent calver versions
    monkeypatch.setenv("SETUPTOOLS_SCM_PRETEND_METADATA", "{node_date=2009-02-13}")

    # Set up a git repository with a tag and known commit hash
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    wd.commit_testfile("test2")  # Add another commit to get distance
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file
    pyproject_content = f"""
[build-system]
requires = ["setuptools", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "test-pkg-{first_integration.__name__}-{second_integration.__name__}"
dynamic = ["version"]

[tool.setuptools_scm]
local_scheme = "no-local-version"
"""
    wd.write("pyproject.toml", pyproject_content)

    dist = create_clean_distribution(
        f"test-pkg-{first_integration.__name__}-{second_integration.__name__}"
    )

    # Call both integration functions in order
    first_integration(dist)
    second_integration(dist)

    # Get the final version directly from the distribution
    final_version = dist.metadata.version

    # Assert the final version matches expectation
    # Some tests will fail here, demonstrating the bug where version_keyword doesn't override
    assert final_version == expected_final_version, (
        f"Expected version '{expected_final_version}' but got '{final_version}'"
    )


def test_infer_version_with_build_requires_no_tool_section(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that infer_version works when setuptools-scm is in build_requires but no [tool.setuptools_scm] section"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Set up a git repository with a tag
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools_scm in build-system.requires but NO [tool.setuptools_scm] section
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools_scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-infer-version"
dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.setuptools import infer_version

    # Create clean distribution
    dist = create_clean_distribution("test-package-infer-version")

    # Call infer_version - this should work because setuptools_scm is in build-system.requires
    infer_version(dist)

    # Verify that version was set
    assert dist.metadata.version is not None
    assert dist.metadata.version == "1.0.0"

    # Verify that the marker was set
    assert getattr(dist, "_setuptools_scm_version_set_by_infer", False) is True


def test_infer_version_with_build_requires_dash_variant_no_tool_section(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that infer_version works when setuptools-scm (dash variant) is in build_requires but no [tool.setuptools_scm] section"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Set up a git repository with a tag
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools-scm (dash variant) in build-system.requires but NO [tool.setuptools_scm] section
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-infer-version-dash"
dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.setuptools import infer_version

    # Create clean distribution
    dist = create_clean_distribution("test-package-infer-version-dash")

    # Call infer_version - this should work because setuptools-scm is in build-system.requires
    infer_version(dist)

    # Verify that version was set
    assert dist.metadata.version is not None
    assert dist.metadata.version == "1.0.0"

    # Verify that the marker was set
    assert getattr(dist, "_setuptools_scm_version_set_by_infer", False) is True


def test_infer_version_without_build_requires_no_tool_section_silently_returns(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that infer_version silently returns when setuptools-scm is NOT in build_requires and no [tool.setuptools_scm] section"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Set up a git repository with a tag
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file WITHOUT setuptools_scm in build-system.requires and NO [tool.setuptools_scm] section
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-no-scm"
dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.setuptools import infer_version

    # Create clean distribution
    dist = create_clean_distribution("test-package-no-scm")

    infer_version(dist)
    assert dist.metadata.version is None


def test_version_keyword_no_scm_dependency_works(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Set up a git repository with a tag
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file WITHOUT setuptools_scm in build-system.requires
    # and WITHOUT [tool.setuptools_scm] section
    pyproject_content = """
[build-system]
requires = ["setuptools>=80"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-no-scm"
dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    import setuptools

    from setuptools_scm._integration.setuptools import version_keyword

    # Create distribution
    dist = setuptools.Distribution({"name": "test-package-no-scm"})

    version_keyword(dist, "use_scm_version", True)
    assert dist.metadata.version == "1.0.0"


def test_verify_dynamic_version_when_required_missing_dynamic(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that verification fails when setuptools-scm is in build-system.requires but dynamic=['version'] is missing"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Change to the test directory
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools-scm in build-system.requires but NO dynamic=['version']
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-missing-dynamic"
# Missing: dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.pyproject_reading import read_pyproject

    # This should raise a ValueError because dynamic=['version'] is missing
    with pytest.raises(
        ValueError, match="dynamic=\\['version'\\] is not set in \\[project\\]"
    ):
        read_pyproject(Path("pyproject.toml"), missing_section_ok=True)


def test_verify_dynamic_version_when_required_with_tool_section(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that verification passes when setuptools-scm is in build-system.requires and [tool.setuptools_scm] section exists"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Change to the test directory
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools-scm in build-system.requires and [tool.setuptools_scm] section
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-with-tool-section"
# Missing: dynamic = ["version"]

[tool.setuptools_scm]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.pyproject_reading import read_pyproject

    # This should not raise an error because [tool.setuptools_scm] section exists
    pyproject_data = read_pyproject(Path("pyproject.toml"), missing_section_ok=True)
    assert pyproject_data.is_required is True
    assert pyproject_data.section_present is True


def test_verify_dynamic_version_when_required_with_dynamic(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that verification passes when setuptools-scm is in build-system.requires and dynamic=['version'] is set"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Change to the test directory
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools-scm in build-system.requires and dynamic=['version']
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-with-dynamic"
dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.pyproject_reading import read_pyproject

    # This should not raise an error because dynamic=['version'] is set
    pyproject_data = read_pyproject(Path("pyproject.toml"), missing_section_ok=True)
    assert pyproject_data.is_required is True
    assert pyproject_data.section_present is False


def test_infer_version_logs_debug_when_missing_dynamic_version(
    wd: WorkDir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that infer_version logs debug info when setuptools-scm is in build-system.requires but dynamic=['version'] is missing"""
    if sys.version_info < (3, 11):
        pytest.importorskip("tomli")

    # Set up a git repository with a tag
    wd.commit_testfile("test")
    wd("git tag 1.0.0")
    monkeypatch.chdir(wd.cwd)

    # Create a pyproject.toml file with setuptools-scm in build-system.requires but NO dynamic=['version']
    pyproject_content = """
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "test-package-missing-dynamic"
# Missing: dynamic = ["version"]
"""
    wd.write("pyproject.toml", pyproject_content)

    from setuptools_scm._integration.setuptools import infer_version

    # Create clean distribution
    dist = create_clean_distribution("test-package-missing-dynamic")

    # This should not raise an error, but should log debug info about the configuration issue
    infer_version(dist)

    # Verify that version was not set due to configuration issue
    assert dist.metadata.version is None


@pytest.mark.issue("xmlsec-regression")
def test_xmlsec_download_regression(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that pip download works for xmlsec package without causing setuptools_scm regression.

    This test ensures that downloading and building xmlsec from source doesn't fail
    due to setuptools_scm issues when using --no-build-isolation.
    """
    # Set up environment with setuptools_scm debug enabled
    monkeypatch.setenv("SETUPTOOLS_SCM_DEBUG", "1")
    monkeypatch.setenv("COLUMNS", "150")

    # Run pip download command with no-binary and no-build-isolation
    try:
        subprocess.run(
            [
                *(sys.executable, "-m", "pip", "download"),
                *("--no-binary", "xmlsec"),
                "--no-build-isolation",
                "-v",
                "xmlsec==1.3.16",
            ],
            cwd=tmp_path,
            text=True,
            timeout=300,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"pip download failed: {e}", pytrace=False)

    # The success of the subprocess.run call above means the regression is fixed.
    # pip download succeeded without setuptools_scm causing version conflicts.
