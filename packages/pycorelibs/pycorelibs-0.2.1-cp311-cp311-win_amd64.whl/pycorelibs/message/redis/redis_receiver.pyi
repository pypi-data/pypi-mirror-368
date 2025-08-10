from _typeshed import Incomplete
from pycorelibs.message.redis.redis_queue import RedisMessageQueue as RedisMessageQueue

class MessageReceiver:
    queue: RedisMessageQueue
    callback: Incomplete
    retry_interval: Incomplete
    def __init__(self, queue: RedisMessageQueue, callback: any, retry_interval: int = 30) -> None: ...
    async def run(self) -> None: ...
