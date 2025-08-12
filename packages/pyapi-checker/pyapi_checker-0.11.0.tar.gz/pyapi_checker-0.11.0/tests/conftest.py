"""
Copyright 2025 Palantir Technologies, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import shutil
from pathlib import Path
from subprocess import run
from typing import Any, Iterator
from unittest.mock import Mock, patch

import importlib_resources
import pytest


@pytest.fixture()
def test_lib(tmp_path: Path, request: pytest.FixtureRequest) -> Iterator[Path]:
    current_git_version: bytes = getattr(request, "param", {}).get("current_git_version", b"1.0.0-3-g0a549f3")

    project_dir = tmp_path / "test-pyapi-lib"
    shutil.copytree(str(importlib_resources.files("tests").joinpath("test-pyapi-lib")), project_dir)

    with patch("subprocess.run") as mock_run:

        def mock_different_calls(*args: Any, **kwargs: Any) -> Any:
            command = kwargs["args"]
            mock_process = Mock()

            if command[:2] == ["git", "rev-parse"]:
                mock_process.stdout = f"{project_dir.parent}\n".encode("utf-8")
                return mock_process
            elif command[:4] == ["git", "describe", "--tags", "--abbrev=0"]:
                mock_process.stdout = b"1.0.0\n"
                return mock_process
            elif command[:4] == ["git", "describe", "--tags", "--always"]:
                mock_process.stdout = current_git_version
                return mock_process
            elif command[:2] == ["git", "status"]:
                mock_process.stdout = b""
                return mock_process
            elif command[:3] == ["python3", "-m", "pip"]:
                download_dir = Path(command[-1])
                shutil.copy(
                    str(importlib_resources.files("tests").joinpath("test_pyapi_lib-1.0.0-py3-none-any.whl")),
                    download_dir,
                )
                return mock_process
            else:
                return run(*args, **kwargs)

        mock_run.side_effect = mock_different_calls

        yield project_dir
