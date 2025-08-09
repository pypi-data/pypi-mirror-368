# TTAgent

Утилита для создания чат бота на базе SSE протокола.
Переподключается при сетевых сбоях или временного отключения сервера.
Для работы с АПИ, в т.ч. ответных постов, используется клиентская библиотека `ttclient`
(устанавливается как зависимость).


## INSTALL

Достаточно установить библиотеку ttagent

```
$ pip install ttagent
```


## CODE

Create `agent.py`

```python
from ttagent import Action, Post, TTAgent


class MyAgent(TTAgent):
    async def post_handler(self, post: Post) -> None:
        ''' Called when bot mentioned in post '''
        post.user_id            # int, who send post
        post.user_unique_name   # str, who send post
        post.chat_id    # int, in what chat
        post.post_no    # int, post number
        post.team_id    # int | None, if chat from team
        post.text       # str, post text
        post.text_parsed    # list[dict], parsed post text
        post.attachments    # list[str], guids of attached files
        post.reply_no       # int, if post has reply to other post (number)
        post.reply_text     # str, if post has reply to other post (text)
        post.file_name      # str, if post is file filename here
        post.file_guid      # str, if post is file guid here

    async def action_handler(self, action: Action) -> None:
        ''' Called when user clicks on bot action link or button '''
        action.action   # str, action name
        action.params   # dict, params of action
        action.user_id          # int, who send post
        action.user_unique_name   # str, who send post
        action.chat_id    # int, in what chat
        action.post_no    # int, post number
        action.team_id    # int | None, if chat from team
```


## RUN

`SECRET` given when bot created

`DOMAIN` of server hostname

```
SECRET=<...> API_HOST=<hostname> ttagent example.agent:MyAgent
```
