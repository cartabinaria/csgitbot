from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, create_autospec, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.endpoints import github
from src.endpoints.oauth import OAuthCallbackResponse
from src.my_types import Author


def fake_auth():
    return OAuthCallbackResponse(
        access_token="unused-test-token",
        username="test-user",
        email="test-user@example.invalid",
    )


class UploadFilesTests(unittest.TestCase):
    def test_upload_files_to_root_and_nested_directory(self):
        app = FastAPI()
        app.include_router(github.router, prefix="/api")
        app.dependency_overrides[github.decode_token] = fake_auth
        author = Author(name="test-user", email="test-user@example.invalid")
        branch_name = "test-user/root-upload"

        for path in (".", "./", "materials/notes"):
            with self.subTest(path=path), TemporaryDirectory() as directory:
                repos = Path(directory) / "repos"
                repository = repos / "example"
                repository.mkdir(parents=True)
                repo = create_autospec(github.repomanager.LocalRepo, instance=True)
                repo.is_initialized.return_value = True
                manager = SimpleNamespace(
                    check_path_exists=Mock(return_value=True),
                    LocalRepo=Mock(return_value=repo),
                    create_branch_name=Mock(return_value=branch_name),
                )

                with (
                    patch.object(github, "REPOS_PATH", str(repos)),
                    patch.object(github, "repomanager", manager),
                    patch("socket.socket.connect", side_effect=AssertionError("Unexpected network access")),
                    TestClient(app) as client,
                ):
                    response = client.post(
                        "/api/uploadfiles/",
                        data={"repository": "example", "path": path},
                        files=[
                            ("files", ("notes.txt", b"root upload\n", "text/plain")),
                            ("files", ("sample.bin", b"\x00\xff\x01", "application/octet-stream")),
                        ],
                    )

                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json(), {
                    "detail": "2 files uploaded successfully",
                    "branch_name": branch_name,
                })
                self.assertEqual((repository / path / "notes.txt").read_bytes(), b"root upload\n")
                self.assertEqual((repository / path / "sample.bin").read_bytes(), b"\x00\xff\x01")
                manager.check_path_exists.assert_called_once_with(str(repository))
                manager.LocalRepo.assert_called_once_with(str(repository))
                manager.create_branch_name.assert_called_once_with(author)
                repo.commit_files.assert_called_once()
                files_to_commit, commit_author = repo.commit_files.call_args.args
                self.assertEqual([Path(file) for file in files_to_commit], [
                    Path(path) / "notes.txt", Path(path) / "sample.bin",
                ])
                self.assertEqual(commit_author, author)
                repo.pull.assert_called_once_with()
                repo.create_branch.assert_called_once_with(branch_name)
                repo.move_to_branch.assert_called_once_with(branch_name)
                repo.push.assert_called_once_with()
                repo.move_to_default.assert_called_once_with()
