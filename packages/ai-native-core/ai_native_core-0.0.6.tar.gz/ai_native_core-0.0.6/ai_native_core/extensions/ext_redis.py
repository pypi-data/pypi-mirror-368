import os
from typing import Any, Union

import redis
from redis.cache import CacheConfig
from redis.cluster import ClusterNode, RedisCluster
from redis.connection import Connection, SSLConnection
from redis.sentinel import Sentinel


class RedisClientWrapper:
    """
    A wrapper class for the Redis client that addresses the issue where the global
    `redis_client` variable cannot be updated when a new Redis instance is returned
    by Sentinel.

    This class allows for deferred initialization of the Redis client, enabling the
    client to be re-initialized with a new instance when necessary. This is particularly
    useful in scenarios where the Redis instance may change dynamically, such as during
    a failover in a Sentinel-managed Redis setup.

    Attributes:
        _client (redis.Redis): The actual Redis client instance. It remains None until
                               initialized with the `initialize` method.

    Methods:
        initialize(client): Initializes the Redis client if it hasn't been initialized already.
        __getattr__(item): Delegates attribute access to the Redis client, raising an error
                           if the client is not initialized.
    """

    def __init__(self):
        self._client = None

    def initialize(self, client):
        if self._client is None:
            self._client = client

    def __getattr__(self, item):
        if self._client is None:
            raise RuntimeError("Redis client is not initialized. Call init_app first.")
        return getattr(self._client, item)


redis_client = RedisClientWrapper()


def init_redis_client():
    global redis_client
    connection_class: type[Union[Connection, SSLConnection]] = Connection
    if os.getenv("REDIS_USE_SSL", "false").lower() == "true":
        connection_class = SSLConnection
    resp_protocol = int(os.getenv("REDIS_SERIALIZATION_PROTOCOL", "2"))
    if os.getenv("REDIS_ENABLE_CLIENT_SIDE_CACHE", "false").lower() == "true":
        if resp_protocol >= 3:
            clientside_cache_config = CacheConfig()
        else:
            raise ValueError("Client side cache is only supported in RESP3")
    else:
        clientside_cache_config = None

    redis_params: dict[str, Any] = {
        "username": os.getenv("REDIS_USERNAME"),
        "password": os.getenv("REDIS_PASSWORD") or None,  # Temporary fix for empty password
        "db": int(os.getenv("REDIS_DB", "0")),
        "encoding": "utf-8",
        "encoding_errors": "strict",
        "decode_responses": False,
        "protocol": resp_protocol,
        "cache_config": clientside_cache_config,
    }

    if os.getenv("REDIS_USE_SENTINEL", "false").lower() == "true":
        sentinels = os.getenv("REDIS_SENTINELS")
        assert sentinels is not None, "REDIS_SENTINELS must be set when REDIS_USE_SENTINEL is True"
        sentinel_hosts = [
            (node.split(":")[0], int(node.split(":")[1])) for node in sentinels.split(",")
        ]
        sentinel = Sentinel(
            sentinel_hosts,
            sentinel_kwargs={
                "socket_timeout": float(os.getenv("REDIS_SENTINEL_SOCKET_TIMEOUT", "0.1")),
                "username": os.getenv("REDIS_SENTINEL_USERNAME"),
                "password": os.getenv("REDIS_SENTINEL_PASSWORD"),
            },
        )
        master = sentinel.master_for(os.getenv("REDIS_SENTINEL_SERVICE_NAME"), **redis_params)
        redis_client.initialize(master)
    elif os.getenv("REDIS_USE_CLUSTERS", "false").lower() == "true":
        clusters = os.getenv("REDIS_CLUSTERS")
        assert clusters is not None, "REDIS_CLUSTERS must be set when REDIS_USE_CLUSTERS is True"
        nodes = [
            ClusterNode(host=node.split(":")[0], port=int(node.split(":")[1]))
            for node in clusters.split(",")
        ]
        redis_client.initialize(
            RedisCluster(
                startup_nodes=nodes,
                password=os.getenv("REDIS_CLUSTERS_PASSWORD"),
                protocol=resp_protocol,
                cache_config=clientside_cache_config,
            )
        )
    else:
        redis_params.update(
            {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "connection_class": connection_class,
                "protocol": resp_protocol,
                "cache_config": clientside_cache_config,
            }
        )
        pool = redis.ConnectionPool(**redis_params)
        redis_client.initialize(redis.Redis(connection_pool=pool))

    return redis_client


init_redis_client()
