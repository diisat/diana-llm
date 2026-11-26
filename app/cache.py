"""Bounded, expiring RAM cache for public FAQ answers only."""
import asyncio
import time
from collections import OrderedDict


class AnswerCache:
    def __init__(self, max_entries=128, ttl=86400, clock=time.monotonic):
        self.max_entries = max_entries
        self.ttl = ttl
        self.clock = clock
        self.entries = OrderedDict()
        self.pending = {}

    async def resolve(self, key, factory):
        if key is None or self.max_entries <= 0 or self.ttl <= 0:
            return await factory()
        now = self.clock()
        for old_key, (expires, _) in list(self.entries.items()):
            if expires <= now:
                del self.entries[old_key]
        if key in self.entries:
            self.entries.move_to_end(key)
            return self.entries[key][1].model_copy(deep=True)
        task = self.pending.get(key)
        if task is None:
            async def fill():
                try:
                    answer = await factory()
                    self.entries[key] = (self.clock()+self.ttl, answer.model_copy(deep=True))
                    self.entries.move_to_end(key)
                    while len(self.entries) > self.max_entries:
                        self.entries.popitem(last=False)
                    return answer
                finally:
                    self.pending.pop(key, None)
            task = asyncio.create_task(fill())
            # Retrieve exceptions even when every waiting HTTP request disconnects.
            task.add_done_callback(lambda t: None if t.cancelled() else t.exception())
            self.pending[key] = task
        return (await asyncio.shield(task)).model_copy(deep=True)
