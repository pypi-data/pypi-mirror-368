import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from ttagent import main


def test_import_agent_ok():
    main._import_agent('example.agent:MyAgent')
    main._import_agent('example.agent:agent')


def test_import_agent_err_bad_format():
    with pytest.raises(ImportError):
        main._import_agent('example.agent')


def test_import_agent_err_not_exists():
    with pytest.raises(ImportError):
        main._import_agent('example.agent:app2')


def test_run_ok(monkeypatch):
    import example.agent  # noqa PLC0415

    mock_agent, mock_asyncio_run = MagicMock(), MagicMock()
    monkeypatch.setattr(example.agent, 'agent', mock_agent)
    monkeypatch.setattr(asyncio, 'run', mock_asyncio_run)

    main.run('example.agent:agent')

    mock_agent.run.assert_called()
    mock_asyncio_run.assert_called()


def test_run_err(monkeypatch):
    import example.agent  # noqa PLC0415

    mock_agent = MagicMock(run=AsyncMock(side_effect=Exception))
    monkeypatch.setattr(example.agent, 'agent', mock_agent)

    main.run('example.agent:agent')

    mock_agent.run.assert_called()


def test_main_ok(monkeypatch):
    monkeypatch.setattr(main, 'run', MagicMock())
    monkeypatch.setattr(main.parser, 'parse_args', Mock(return_value=MagicMock(agent='test')))

    with pytest.raises(SystemExit):
        main.main()
