"""Sharding: .shard[count=], .shard_id(), .shard_ready[], .broadcast_eval()"""
import asyncio


class ShardManager:
    def __init__(self, client_factory, *, count: int, token: str):
        self.client_factory = client_factory
        self.count = count
        self.token = token
        self.shards: dict[int, object] = {}

    def shard_id_for(self, guild_id: int) -> int:
        """Discord's standard sharding formula: (guild_id >> 22) % num_shards."""
        return (guild_id >> 22) % self.count

    async def start(self):
        for shard_id in range(self.count):
            client = self.client_factory(shard_id=shard_id, shard_count=self.count)
            self.shards[shard_id] = client
        await asyncio.gather(*(c.start(self.token) for c in self.shards.values()))

    async def broadcast_eval(self, func):
        """Runs func(shard_client) across every shard and gathers the results."""
        return await asyncio.gather(*(func(c) for c in self.shards.values()))
