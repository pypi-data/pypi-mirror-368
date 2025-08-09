from logging.config import dictConfig

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)-8s [pid#%(process)d] %(asctime)s %(name)s '
                '%(filename)s:%(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
        }
    },
})
