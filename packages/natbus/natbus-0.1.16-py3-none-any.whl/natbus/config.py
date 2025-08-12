#./natbus/config.py
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
    stream_create: bool = False
    stream_name: str = ""
    stream_subjects: Tuple[str, ...] = ()
    # push consumer defaults
    queue_group: Optional[str] = None   # set to enable load-balanced delivery
    bind: bool = True                   # bind to existing durable by default
    manual_ack: bool = True             # handler must ack()
