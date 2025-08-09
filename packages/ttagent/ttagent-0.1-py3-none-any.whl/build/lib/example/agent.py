from ttagent import Action, Post, TTAgent

from . import log_config  # noqa


class MyAgent(TTAgent):
    async def post_handler(self, post: Post) -> None:
        self.log.info('Get post %s', str(post))

    async def action_handler(self, action: Action) -> None:
        self.log.info('Get action %s', str(action))


agent = MyAgent()
