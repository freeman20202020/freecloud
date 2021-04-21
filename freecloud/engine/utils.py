import logging
from engine.middleware import local


class ContextFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(ContextFilter, self).__init__(*args, **kwargs)

    def filter(self, record):
        try:
            record.random_string = getattr(local, 'random_string', "0000000000")
            record.path = getattr(local, 'path', "path")
        except Exception as e:
            print(str(e))
        return True


def get_log_object(name):
    logger = logging.getLogger(name)
    f = ContextFilter()
    logger.addFilter(f)
    return logger
