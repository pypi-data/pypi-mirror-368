from dataclasses import dataclass
from typing import Literal

EventType = Literal['system', 'post', 'action']


@dataclass
class Post:
    # пользователь, отправивший пост
    user_id: int
    user_unique_name: str
    # координаты поста
    chat_id: int
    post_no: int
    team_id: int | None
    # данные поста
    text: str
    text_parsed: list[dict]
    attachments: list[str]
    reply_no: int | None = None
    reply_text: str | None = None
    file_name: str | None = None
    file_guid: str | None = None


@dataclass
class Action:
    # пользователь, отправивший запрос
    user_id: int
    user_unique_name: str
    # координаты поста
    chat_id: int
    post_no: int
    team_id: int | None
    # данные запроса
    action: str
    params: dict
