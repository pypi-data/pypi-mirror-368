import asyncio
import base64
import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx
import httpx_sse
from ttclient import TTClient

from .abc import Action, Post
from .settings import CLIENT_SECRET, DOMAIN, SECRET_BYTES, STREAM_URL


class StreamInterruptedError(Exception):
    '''
        Вызывается, когда пришла команда от сервера на прерывание.
        Клиент не должен повторять попытки подключения. Причины прерывания:
        - клиент не успевает обрабатывать сообщения и очередь на сервере переполнена,
        - подключился другой клиент для того же бота.
    '''
    pass


class StreamExitError(httpx_sse.SSEError):
    '''
        Вызывается при корректном завершении SSE подключения.
        Требует от клиента переподключения для продолжения работы.
        Как правило связан с перезапуском сервера.
    '''
    pass


@dataclass()
class TTAgent:
    log: logging.Logger = field(default_factory=lambda: logging.getLogger('ttagent'))
    # для кастомизации клиента
    client: TTClient = field(default_factory=lambda: TTClient(CLIENT_SECRET, DOMAIN))
    # для кастомизации http подключения (в т.ч. заголовков авториазции)
    http_options: dict[str, Any] = field(default_factory=lambda: {'timeout': 60})
    http_headers: dict[str, Any] = field(default_factory=lambda: {'User-Agent': 'TTAgent'})
    _retry_counter: int = 0

    async def run(self) -> None:
        ''' Подключаемся к потоку и начинаем обработку данных '''
        # секрет не должен попадать в логи вместе с датаклассом
        headers = {'X-APIToken': CLIENT_SECRET} | self.http_headers

        async with httpx.AsyncClient(headers=headers, **self.http_options) as client:
            await self._retry_listener(client)

    # Сетевой уровень
    async def _listener(self, client: httpx.AsyncClient) -> None:
        ''' Основной цикл получения данных от сервера '''
        async with httpx_sse.aconnect_sse(client, 'GET', STREAM_URL) as event_source:
            self.log.info('Connection established')
            self._retry_counter = 0

            async for sse in event_source.aiter_sse():
                try:
                    await self._base_handler(sse.id, sse.event, json.loads(sse.data))
                except StreamInterruptedError as exc:
                    self.log.warning('Stream interrupted: %s', exc.args[0])
                    return  # перерываем работу по команде сервера
                except Exception as exc:  # игнорируем любые ошибки, чтоб не прерывать работу
                    self.log.exception(exc)

        raise StreamExitError('Connection closed gracefully')

    async def _retry_listener(self, client: httpx.AsyncClient) -> None:
        ''' Запускает обработку потока с обвязкой для обработки ошибок и переподключения '''
        self.log.info('Try to connect to stream at %s', STREAM_URL)

        try:
            await self._listener(client)
        except (httpx.NetworkError, httpx.TimeoutException, httpx_sse.SSEError) as exc:
            self.log.exception(exc)

            self._retry_counter += 1
            retry_after = self._retry_counter ** 2 if self._retry_counter < 18 else 300  # noqa PLR2004
            # постепенно увеличиваем время ожидания с каждой попыткой до 300 сек

            self.log.warning('Connection lost. Retry after %s seconds', retry_after)
            await asyncio.sleep(retry_after)
            await self._retry_listener(client)

    # Прикладной уровень
    async def _base_handler(self, event_id: str | None, event: str, data: dict[str, Any]) -> None:
        '''
            Обработка данных события и проверка подписи.
            Маршрутизация по обработчикам разных типов событий.
        '''
        actual_signature = data.pop('signature')
        expected_signatutre = self._make_signature(json.dumps(data))

        if actual_signature != expected_signatutre:
            self.log.warning('Signature check failed: actual - %s, expected - %s',
                actual_signature, expected_signatutre)

        match event, data:
            case 'system', {'action': 'interrupt', 'reason': reason}:
                raise StreamInterruptedError(reason)
            case 'post', dict(data):
                await self.post_handler(self._make_post(data))
            case 'action', dict(data):
                await self.action_handler(self._make_action(data))
            case _:
                self.log.warning('Unexpected %s data: %s', event, str(data))

    def _make_signature(self, data: str) -> str:
        return str(base64.b64encode(
            hmac.new(
                SECRET_BYTES,
                bytes(data, 'utf8'),
                digestmod=hashlib.sha256
            ).digest()
        ), 'utf8')

    def _make_post(self, data: dict[str, Any]) -> Post:
        return Post(
            user_id=data['user_id'],
            user_unique_name=data['user_unique_name'],
            chat_id=data['chat_id'],
            post_no=data['post_no'],
            team_id=data.get('organization_id'),
            text=data['text'],
            text_parsed=data.get('text_parsed', []),
            attachments=data.get('attachments', []),
            reply_no=data.get('reply_no'),
            reply_text=data.get('reply_text'),
            file_guid=data.get('file_guid'),
            file_name=data.get('file_name'),
        )

    def _make_action(self, data: dict[str, Any]) -> Action:
        return Action(
            user_id=data['user_id'],
            user_unique_name=data['user_unique_name'],
            chat_id=data['chat_id'],
            post_no=data['post_no'],
            team_id=data.get('organization_id'),
            action=data['action'],
            params=data['params'],
        )

    async def post_handler(self, post: Post) -> None:
        ''' Обработка поста, отправленного боту '''
        self.log.info('Get post: %s', str(post))

    async def action_handler(self, action: Action) -> None:
        ''' Обработка экшена '''
        self.log.info('Get action: %s', str(action))
