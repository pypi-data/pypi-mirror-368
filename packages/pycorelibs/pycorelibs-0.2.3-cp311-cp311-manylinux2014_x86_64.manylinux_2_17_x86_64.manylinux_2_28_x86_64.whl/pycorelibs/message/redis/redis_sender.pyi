from _typeshed import Incomplete
from pycorelibs.message.message import MessageModel as MessageModel
from pycorelibs.message.redis.redis_queue import RedisMessageQueue as RedisMessageQueue

class MessageSender:
    queue: RedisMessageQueue
    model_class: Incomplete
    def __init__(self, queue: RedisMessageQueue, model_class=...) -> None: ...
    def send(self, text: str, priority: int = 0, **kwargs): ...
