#./natbus/client.py
from __future__ import annotations
import asyncio
from typing import Awaitable, Callable, Optional
from urllib.parse import urlparse

from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig, ConsumerConfig, AckPolicy
from nats.js import errors as js_err

from .config import NatsConfig
from .message import BusMessage, ReceivedMessage

Handler = Callable[[ReceivedMessage], Awaitable[None]]

r"""
NATS JetStream: publish, PUSH consumers, PULL consumers, and Ephemerals (quick guide)

Overview
--------
- Publishers only publish bytes to a subject (e.g. "ai.json.requests").
- A Stream stores messages for one or more subjects.
- A Consumer defines how clients read from a stream. Consumers can be:
  1) PUSH: the server delivers messages to your callback.
  2) PULL: your code fetches messages when it's ready.
  3) EPHEMERAL PUSH: like PUSH, but without a durable; auto-removed after inactivity.

PUSH consumer (server-driven delivery)
--------------------------------------
- The server pushes messages to your subscriber callback.
- Optional queue group (deliver_group) enables load balancing:
  - All subscribers that use the same subject + same durable + same queue group form a worker pool; each message goes to exactly one member.
  - Different queue names receive independent copies (fan-out).
- Use a durable name to retain position/ack state across restarts.

PULL consumer (client-driven fetching)
-------------------------------------
- Your code explicitly fetches batches from the consumer.
- There is no queue group concept for pull.

Ephemeral PUSH consumers (short-lived)
--------------------------------------
- No durable_name; server delivers to a per-subscriber inbox (deliver_subject).
- Optional deliver_group behaves like durable PUSH for load balancing.
- Use inactive_threshold to have the server auto-delete the consumer after it is idle and has no interested subscribers.
- Ideal for short-lived WebSocket sessions with dynamic subjects derived from a connection/session id.
- Unsubscribe from the inbox subject stops delivery immediately; the consumer is garbage-collected after the inactivity window.

Acks & durability
-----------------
- Use explicit ack (AckPolicy.EXPLICIT).
- ack() confirms processing; nak() requests redelivery; term() stops redelivery.
- Durables track delivery cursor so workers can restart without replay. Ephemerals do not keep long-term position.

Terminology
-----------
- Subject: routing key publishers send to.
- Stream: stores messages.
- Consumer: read view (durable or ephemeral).
- Deliver group: PUSH-only load-balancing group name.
- Inbox (deliver_subject): core NATS subject where JetStream pushes messages for a PUSH/ephemeral consumer.
"""



def _split_servers(s: str | list[str]) -> list[str]:
    if isinstance(s, str):
        return [p.strip() for p in s.split(",") if p.strip()]
    return [str(p).strip() for p in s if str(p).strip()]

def _normalize_servers(servers: list[str]) -> list[str]:
    if not servers:
        return ["nats://127.0.0.1:4222"]
    out: list[str] = []
    schemes: set[str] = set()
    for raw in servers:
        url = raw if "://" in raw else f"nats://{raw}"
        scheme = urlparse(url).scheme.lower()
        if scheme not in {"nats", "tls", "ws", "wss"}:
            raise ValueError(f"Unsupported NATS scheme: {scheme} in {raw}")
        schemes.add(scheme)
        out.append(url)
    if not (schemes <= {"nats", "tls"} or schemes <= {"ws", "wss"}):
        raise ValueError("Mixed WebSocket and TCP endpoints are not allowed")
    return out

def _norm_queue(q: Optional[str]) -> Optional[str]:
    if q is None:
        return None
    q = q.strip()
    return q or None


class PullSubscription:
    def __init__(self, sub):
        self._sub = sub

    async def fetch(self, batch: int = 1, timeout: Optional[float] = None, no_wait: bool = False):
        if no_wait:
            nmsgs = await self._sub.fetch_no_wait(batch)
        else:
            nmsgs = await self._sub.fetch(batch, timeout=timeout)
        out = []
        for m in nmsgs:
            out.append(ReceivedMessage(
                subject=m.subject,
                data=m.data,
                headers=dict(m.headers or {}),
                _ack=m.ack,
                _nak=m.nak,
                _term=m.term,
            ))
        return out


class EphemeralPushHandle:
    def __init__(self, sub):
        self._sub = sub
    async def close(self):
        await self._sub.unsubscribe()


class NatsBus:
    def __init__(self, cfg: NatsConfig):
        self.cfg = cfg
        self._nc: Optional[NATS] = None
        self._js = None
        self._subs: list = []
        # Idempotency map to avoid duplicate core-NATS subscriptions to the same deliver subject
        self._push_keys: dict[tuple[str, Optional[str], Handler], object] = {}

    @property
    def nc(self) -> NATS:
        if not self._nc:
            raise RuntimeError("not connected")
        return self._nc

    async def _ensure_push_consumer(
        self, stream: str, subject: str, durable: str, queue: Optional[str]
    ) -> str:
        queue = _norm_queue(queue)
        try:
            info = await self._js.consumer_info(stream, durable)
            cfg = info.config
            if not getattr(cfg, "deliver_subject", None):
                raise RuntimeError(
                    f"Existing consumer '{durable}' is a PULL consumer; cannot bind as PUSH."
                )
            actual_q = getattr(cfg, "deliver_group", None) or None
            if actual_q != queue:
                raise RuntimeError(
                    f"Existing consumer '{durable}' deliver_group='{actual_q or '(none)'}' "
                    f"differs from requested queue='{queue or '(none)'}'."
                )
            if cfg.filter_subject and cfg.filter_subject != subject:
                raise RuntimeError(
                    f"Existing consumer '{durable}' filter_subject='{cfg.filter_subject}' "
                    f"differs from requested '{subject}'."
                )
            return cfg.deliver_subject
        except js_err.NotFoundError:
            deliver_subject = self._nc.new_inbox()
            await self._js.add_consumer(
                stream,
                ConsumerConfig(
                    durable_name=durable,
                    filter_subject=subject,
                    ack_policy=AckPolicy.EXPLICIT,
                    deliver_subject=deliver_subject,
                    deliver_group=queue,
                ),
            )
            return deliver_subject

    async def _ensure_pull_consumer(self, stream: str, subject: str, durable: str) -> None:
        try:
            info = await self._js.consumer_info(stream, durable)
            cfg = info.config
            if getattr(cfg, "deliver_subject", None):
                raise RuntimeError(
                    f"Existing consumer '{durable}' is PUSH (has deliver_subject); cannot bind as PULL."
                )
            if cfg.filter_subject and cfg.filter_subject != subject:
                raise RuntimeError(
                    f"Existing consumer '{durable}' filter_subject='{cfg.filter_subject}' "
                    f"differs from requested '{subject}'."
                )
            return
        except js_err.NotFoundError:
            pass

        await self._js.add_consumer(
            stream,
            ConsumerConfig(
                durable_name=durable,
                filter_subject=subject,
                ack_policy=AckPolicy.EXPLICIT,
            ),
        )

    async def connect(self) -> None:
        raw = _split_servers(self.cfg.server)
        urls = _normalize_servers(raw)
        servers_arg = urls[0] if len(urls) == 1 else urls

        self._nc = NATS()
        await self._nc.connect(
            servers=servers_arg,
            user=self.cfg.username,
            password=self.cfg.password,
            name=self.cfg.name,
            reconnect_time_wait=self.cfg.reconnect_time_wait,
            max_reconnect_attempts=self.cfg.max_reconnect_attempts,
        )
        self._js = self._nc.jetstream()

        if self.cfg.stream_create and self.cfg.stream_name and self.cfg.stream_subjects:
            try:
                await self._js.add_stream(
                    StreamConfig(
                        name=self.cfg.stream_name,
                        subjects=list(self.cfg.stream_subjects),
                    )
                )
            except Exception:
                pass

    async def close(self) -> None:
        if self._nc:
            try:
                await self._nc.drain()
            finally:
                await self._nc.close()
        self._nc = None
        self._js = None
        self._subs.clear()
        self._push_keys.clear()

    async def publish(self, msg: BusMessage) -> None:
        if not self._js:
            raise RuntimeError("JetStream not initialized; call connect() first")
        await self._js.publish(msg.subject, msg.data, headers=msg.headers)

    async def publish_json(self, subject: str, obj, *, sender: Optional[str] = None,
                           correlation_id: Optional[str] = None, headers: Optional[dict[str, str]] = None) -> None:
        msg = BusMessage.from_json(subject, obj, sender=sender, correlation_id=correlation_id, headers=headers)
        await self.publish(msg)

    async def publish_bytes(self, subject: str, data: bytes, *, sender: Optional[str] = None,
                            correlation_id: Optional[str] = None, headers: Optional[dict[str, str]] = None,
                            content_type: str = "application/octet-stream") -> None:
        msg = BusMessage.from_bytes(subject, data, sender=sender, correlation_id=correlation_id,
                                    headers=headers, content_type=content_type)
        await self.publish(msg)

    async def push_subscribe(
        self,
        subject: str,
        handler: Handler,
        *,
        durable: Optional[str] = None,
        queue: Optional[str] = None,
        manual_ack: Optional[bool] = None,
    ) -> None:
        if not self._js:
            raise RuntimeError("JetStream not initialized; call connect() first")

        if manual_ack is None:
            manual_ack = self.cfg.manual_ack
        if queue is None:
            queue = self.cfg.queue_group
        queue = _norm_queue(queue)

        if not self.cfg.stream_name or not durable:
            raise ValueError("stream_name and durable are required for PUSH consumers")

        deliver_subject = await self._ensure_push_consumer(
            self.cfg.stream_name, subject, durable, queue
        )

        key = (deliver_subject, queue, handler)
        if key in self._push_keys:
            return

        async def _cb(nats_msg):
            async def _ack():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"+ACK")
                elif hasattr(nats_msg, "ack"):
                    await nats_msg.ack()

            async def _nak():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"-NAK")
                elif hasattr(nats_msg, "nak"):
                    await nats_msg.nak()

            async def _term():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"+TERM")
                elif hasattr(nats_msg, "term"):
                    await nats_msg.term()

            rm = ReceivedMessage(
                subject=subject,
                data=nats_msg.data,
                headers=dict(nats_msg.headers or {}),
                _ack=_ack,
                _nak=_nak,
                _term=_term,
            )
            await handler(rm)

        if queue:
            sub = await self._nc.subscribe(deliver_subject, queue=queue, cb=_cb)
        else:
            sub = await self._nc.subscribe(deliver_subject, cb=_cb)

        self._subs.append(sub)
        self._push_keys[key] = sub

    async def subscribe(self, subject: str, handler: Handler, *,
                        durable: Optional[str] = None, queue: Optional[str] = None,
                        manual_ack: Optional[bool] = None, bind: Optional[bool] = None) -> None:
        await self.push_subscribe(
            subject, handler, durable=durable, queue=queue, manual_ack=manual_ack
        )

    async def pull_subscribe(
        self,
        subject: str,
        *,
        durable: str,
        stream: Optional[str] = None,
    ) -> PullSubscription:
        if not self._js:
            raise RuntimeError("JetStream not initialized; call connect() first")

        stream_name = stream or self.cfg.stream_name or ""
        if not stream_name:
            raise ValueError("stream name required for pull_subscribe (set cfg.stream_name or pass stream=)")

        await self._ensure_pull_consumer(stream_name, subject, durable)

        try:
            sub = await self._js.pull_subscribe(
                subject,
                durable=durable,
                stream=stream_name,
            )
        except js_err.Error as e:
            raise RuntimeError(
                f"JetStream pull_subscribe failed: stream={stream_name} subject={subject} "
                f"durable={durable} err={e}"
            )
        return PullSubscription(sub)

    async def ephemeral_push_subscribe(
        self,
        subject: str,
        handler: Handler,
        *,
        inactive_seconds: int = 120,
        queue: Optional[str] = None,
    ) -> EphemeralPushHandle:
        if not self._js:
            raise RuntimeError("JetStream not initialized; call connect() first")
        if not self.cfg.stream_name:
            raise ValueError("cfg.stream_name required for ephemeral_push_subscribe")

        deliver_subject = self._nc.new_inbox()

        await self._js.add_consumer(
            self.cfg.stream_name,
            ConsumerConfig(
                filter_subject=subject,
                ack_policy=AckPolicy.EXPLICIT,
                deliver_subject=deliver_subject,
                deliver_group=queue,
                inactive_threshold=inactive_seconds,
            ),
        )

        async def _cb(nats_msg):
            async def _ack():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"+ACK")
                elif hasattr(nats_msg, "ack"):
                    await nats_msg.ack()

            async def _nak():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"-NAK")
                elif hasattr(nats_msg, "nak"):
                    await nats_msg.nak()

            async def _term():
                reply = getattr(nats_msg, "reply", None)
                if reply:
                    await self._nc.publish(reply, b"+TERM")
                elif hasattr(nats_msg, "term"):
                    await nats_msg.term()

            rm = ReceivedMessage(
                subject=subject,
                data=nats_msg.data,
                headers=dict(nats_msg.headers or {}),
                _ack=_ack,
                _nak=_nak,
                _term=_term,
            )
            await handler(rm)

        sub = await self._nc.subscribe(deliver_subject, queue=queue, cb=_cb) if queue \
              else await self._nc.subscribe(deliver_subject, cb=_cb)
        return EphemeralPushHandle(sub)
