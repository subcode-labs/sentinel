import pytest
from unittest.mock import patch, MagicMock
import sys
import json
import os
from sentinel_client.cli import main
from sentinel_client.exceptions import SentinelError
from sentinel_client.types import SecretPayload


@pytest.fixture
def mock_client():
    with patch("sentinel_client.cli.SentinelClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance


def test_cli_help():
    with patch.object(sys, "argv", ["sentinel-cli", "--help"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0


def test_cli_no_command():
    with patch.object(sys, "argv", ["sentinel-cli"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1


def test_get_command_success(mock_client, capsys):
    mock_client.request_secret.return_value = SecretPayload(
        value="my-secret-value", type="managed", expires_at="2024-01-01T00:00:00Z"
    )

    with patch.object(
        sys, "argv", ["sentinel-cli", "--token", "fake-token", "get", "my-resource"]
    ):
        main()

    captured = capsys.readouterr()
    assert "my-secret-value" in captured.out.strip()

    mock_client.request_secret.assert_called_once()
    args = mock_client.request_secret.call_args
    assert args.kwargs["resource_id"] == "my-resource"


def test_get_command_json_format(mock_client, capsys):
    mock_client.request_secret.return_value = SecretPayload(
        value="my-secret-value", type="managed", expires_at="2024-01-01T00:00:00Z"
    )

    with patch.object(
        sys,
        "argv",
        [
            "sentinel-cli",
            "--token",
            "fake-token",
            "get",
            "my-resource",
            "--format",
            "json",
        ],
    ):
        main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["value"] == "my-secret-value"
    assert output["type"] == "managed"


def test_get_command_env_format(mock_client, capsys):
    mock_client.request_secret.return_value = SecretPayload(
        value="my-secret-value", type="managed", expires_at="2024-01-01T00:00:00Z"
    )

    with patch.object(
        sys,
        "argv",
        [
            "sentinel-cli",
            "--token",
            "fake-token",
            "get",
            "my-resource",
            "--format",
            "env",
        ],
    ):
        main()

    captured = capsys.readouterr()
    assert "my-resource=my-secret-value" in captured.out


def test_get_command_missing_token(capsys):
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(sys, "argv", ["sentinel-cli", "get", "resource"]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == 1
            captured = capsys.readouterr()
            assert "Error: --token or SENTINEL_TOKEN is required" in captured.err


def test_get_command_error(mock_client, capsys):
    mock_client.request_secret.side_effect = SentinelError("API Error")

    with patch.object(
        sys, "argv", ["sentinel-cli", "--token", "fake-token", "get", "my-resource"]
    ):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "Sentinel Error: API Error" in captured.err


def test_resources_command_success(mock_client, capsys):
    mock_client.list_resources.return_value = ["res1", "res2"]

    with patch.object(
        sys, "argv", ["sentinel-cli", "--token", "fake-token", "resources"]
    ):
        main()

    captured = capsys.readouterr()
    assert "res1" in captured.out
    assert "res2" in captured.out


def test_resources_command_json(mock_client, capsys):
    mock_client.list_resources.return_value = ["res1", "res2"]

    with patch.object(
        sys,
        "argv",
        ["sentinel-cli", "--token", "fake-token", "resources", "--format", "json"],
    ):
        main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output == ["res1", "res2"]


def test_run_command_success(mock_client):
    mock_client.fetch_secrets.return_value = {"DB_PASS": "secret123"}

    with patch.object(
        sys,
        "argv",
        ["sentinel-cli", "--token", "fake-token", "run", "--", "python", "script.py"],
    ):
        with patch("os.execvpe") as mock_exec:
            with patch.dict(os.environ, {"EXISTING_VAR": "value"}):
                main()

                assert mock_exec.called
                args = mock_exec.call_args[0]
                assert args[0] == "python"
                assert args[1] == ["python", "script.py"]
                assert args[2]["DB_PASS"] == "secret123"
                assert args[2]["EXISTING_VAR"] == "value"


def test_run_command_no_args(capsys):
    with patch.object(sys, "argv", ["sentinel-cli", "--token", "fake-token", "run"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "Error: No command specified" in captured.err


def test_run_command_no_cmd_after_dash(capsys):
    with patch.object(
        sys, "argv", ["sentinel-cli", "--token", "fake-token", "run", "--"]
    ):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "Error: No command specified after --" in captured.err
