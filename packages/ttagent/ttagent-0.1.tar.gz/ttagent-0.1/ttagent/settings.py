from ttutils import to_bytes
from ttutils.config import EnvConfig

CFG = EnvConfig()

DOMAIN = CFG.DOMAIN
SECRET = CFG.SECRET

SECRET_BYTES = to_bytes(int(SECRET, 32))
CLIENT_SECRET = SECRET[20:]
STREAM_URL = f'https://{DOMAIN}/bot/stream'
