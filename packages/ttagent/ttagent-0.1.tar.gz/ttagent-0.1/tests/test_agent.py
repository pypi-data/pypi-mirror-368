import json
import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import httpx_sse
import pytest
from httpx import AsyncClient

from ttagent import Action, Post, TTAgent
from ttagent.agent import StreamExitError, StreamInterruptedError


@pytest.fixture
async def ttagent() -> TTAgent:
    mock_client = MagicMock(spec=AsyncClient)
    return TTAgent(client=mock_client, log=MagicMock(spec=logging.Logger))


async def test_TTAgent_base_handler_ok_post(ttagent):
    event_id = 'test_id'
    event = 'post'
    data: dict[str, Any] = {
        'user_id': 12,
        'chat_id': 321,
        'post_no': 23,
        'user_unique_name': 'uname',
        'text': 'text',
    }

    post = Post(
        user_id=12,
        chat_id=321,
        post_no=23,
        team_id=None,
        user_unique_name='uname',
        text='text',
        text_parsed=[],
        attachments=[],
    )

    data['signature'] = ttagent._make_signature(json.dumps(data))

    ttagent.post_handler = AsyncMock()

    await ttagent._base_handler(event_id, event, data)

    ttagent.post_handler.assert_called_once_with(post)
    ttagent.log.warning.assert_not_called()


async def test_TTAgent_base_handler_ok_action(ttagent):
    event_id = 'test_id'
    event = 'action'
    data: dict[str, Any] = {
        'user_id': 2,
        'chat_id': 321,
        'post_no': 23,
        'action': 'act',
        'user_unique_name': 'uname',
        'params': {'param1': 'value1'},
    }

    action = Action(
        user_id=2,
        chat_id=321,
        post_no=23,
        team_id=None,
        user_unique_name='uname',
        action='act',
        params={'param1': 'value1'},
    )

    data['signature'] = ttagent._make_signature(json.dumps(data))

    ttagent.action_handler = AsyncMock()

    await ttagent._base_handler(event_id, event, data)

    ttagent.action_handler.assert_called_once_with(action)
    ttagent.log.warning.assert_not_called()


async def test_TTAgent_base_handler_err_interrupt(ttagent):
    event_id = 'test_id'
    event = 'system'
    data: dict[str, Any] = {
        'action': 'interrupt',
        'reason': 'test_reason',
    }

    data['signature'] = ttagent._make_signature(json.dumps(data))

    with pytest.raises(StreamInterruptedError):
        await ttagent._base_handler(event_id, event, data)

    ttagent.log.warning.assert_not_called()


async def test_TTAgent_base_handler_err_unknown(ttagent):
    event_id = 'test_id'
    event = 'unknown'
    data: dict[str, Any] = {}

    data['signature'] = ttagent._make_signature(json.dumps(data))

    await ttagent._base_handler(event_id, event, data)

    ttagent.log.warning.assert_called()


async def test_TTAgent_base_handler_err_signature(ttagent):
    event_id = 'test_id'
    event = 'post'
    data: dict[str, Any] = {
        'user_id': 12,
        'chat_id': 321,
        'post_no': 23,
        'user_unique_name': 'uname',
        'text': 'text',
    }

    post = Post(
        user_id=12,
        chat_id=321,
        post_no=23,
        team_id=None,
        user_unique_name='uname',
        text='text',
        text_parsed=[],
        attachments=[],
    )

    data['signature'] = ttagent._make_signature(json.dumps(data)) + 'Q'

    ttagent.post_handler = AsyncMock()

    await ttagent._base_handler(event_id, event, data)

    ttagent.post_handler.assert_called_once_with(post)
    ttagent.log.warning.assert_called()


async def test_TTAgent_run_ok(ttagent):
    ttagent._retry_listener = AsyncMock()

    await ttagent.run()

    client = ttagent._retry_listener.call_args[0][0]

    assert client.headers.get('X-APIToken')
    assert client.timeout.connect > 30


async def test_TTAgent_retry_listener_ok(ttagent):
    ttagent._listener = AsyncMock()
    mock_client = MagicMock(spec=AsyncClient)

    await ttagent._retry_listener(mock_client)

    ttagent._listener.assert_called_once_with(mock_client)


async def test_TTAgent_retry_listener_err_raise(ttagent):
    ttagent._listener = AsyncMock(side_effect=KeyboardInterrupt)
    mock_client = MagicMock(spec=AsyncClient)

    with pytest.raises(KeyboardInterrupt):
        await ttagent._retry_listener(mock_client)


async def test_TTAgent_retry_listener_err_interrupt(ttagent):
    ttagent._listener = AsyncMock(side_effect=StreamInterruptedError)
    mock_client = MagicMock(spec=AsyncClient)

    with pytest.raises(StreamInterruptedError):
        await ttagent._retry_listener(mock_client)


ERRORS = (
    httpx.ConnectError('test'),
    httpx.ReadError('test'),
    httpx.CloseError('test'),
    httpx.ConnectTimeout('test'),
    httpx.ReadTimeout('test'),
    httpx.PoolTimeout('test'),
    httpx_sse.SSEError('test'),
    StreamExitError('test'),
)


@pytest.fixture(params=ERRORS, ids=(x.__class__.__name__ for x in ERRORS))
def http_error(request):
    return request.param


async def test_TTAgent_retry_listener_err_network(ttagent, http_error):
    ttagent._listener = AsyncMock(side_effect=[http_error, KeyboardInterrupt])
    mock_client = MagicMock(spec=AsyncClient)

    with pytest.raises(KeyboardInterrupt):
        await ttagent._retry_listener(mock_client)

    assert ttagent._listener.call_count == 2
    ttagent._listener.assert_called_with(mock_client)
    ttagent.log.warning.assert_called()


class AsyncContextManager:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


async def test_TTAgent_listener_ok(ttagent, monkeypatch):
    ttagent._base_handler = AsyncMock()
    ttagent._retry_counter = 1

    class TestContext(AsyncContextManager):
        async def aiter_sse(self):
            yield MagicMock(id='id', event='post', data='{}')
            yield MagicMock(side_effect=TypeError)

    monkeypatch.setattr(httpx_sse, 'aconnect_sse', MagicMock(return_value=TestContext()))

    with pytest.raises(StreamExitError):
        await ttagent._listener(MagicMock(spec=AsyncClient))

    ttagent._base_handler.assert_called_with('id', 'post', {})


async def test_TTAgent_listener_ok_exit(ttagent, monkeypatch):
    ttagent._base_handler = AsyncMock(side_effect=StreamInterruptedError('test'))
    ttagent._retry_counter = 1

    class TestContext(AsyncContextManager):
        async def aiter_sse(self):
            yield MagicMock(id='id', event='post', data='{}')

    monkeypatch.setattr(httpx_sse, 'aconnect_sse', MagicMock(return_value=TestContext()))

    await ttagent._listener(MagicMock(spec=AsyncClient))

    ttagent._base_handler.assert_called_with('id', 'post', {})


async def test_TTAgent_post_handler_ok(ttagent):
    await ttagent.post_handler(
        Post(
            user_id=1,
            chat_id=2,
            post_no=3,
            team_id=None,
            text='text',
            user_unique_name='uname',
            text_parsed=[],
            attachments=[],
        )
    )

    ttagent.log.info.assert_called()


async def test_TTAgent_action_handler_ok(ttagent):
    await ttagent.action_handler(
        Action(
            user_id=1,
            chat_id=2,
            post_no=3,
            team_id=None,
            user_unique_name='uname',
            action='act',
            params={}
        )
    )

    ttagent.log.info.assert_called()
