# ./natbus/config.py
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class NatsConfig:
    server: str = "nats-nats-jetstream:4222"
    username: Optional[str] = None
    password: Optional[str] = None
    name: str = "natsbus-client"
    reconnect_time_wait: float = 1.0
    max_reconnect_attempts: int = 60

    # JetStream stream bootstrapping
    stream_create: bool = False
    stream_name: str = ""
    stream_subjects: Tuple[str, ...] = ()

    # PUSH consumer defaults
    queue_group: Optional[str] = None   # load-balanced delivery group
    bind: bool = True                   # bind to existing durable by default (kept for compatibility)
    manual_ack: bool = True             # handler must ack()

    # New: default PUSH consumer behavior (can be overridden per-subscribe)
    # deliver_policy: "new", "all", "last", "by_start_sequence", "by_start_time"
    deliver_policy: str = "new"
    ack_wait_s: int = 30
    max_ack_pending: int = 1024
