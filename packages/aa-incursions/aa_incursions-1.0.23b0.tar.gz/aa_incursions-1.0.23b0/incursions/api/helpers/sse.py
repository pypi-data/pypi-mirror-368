import json
import struct

import base62
import msgpack
import requests
from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_encrypt
from nacl.utils import random as nacl_random
from pydantic import BaseModel

from django.utils.timezone import now


class SSEClient:
    def __init__(self, url: str, secret: str) -> None:
        self.url = url
        self.key = bytes.fromhex(secret) if isinstance(secret, str) else secret
        self.VERSION_BYTE = b'\xBA'

    def branca_encode(self, payload: bytes, timestamp: int | None = None) -> str:
        if len(self.key) != 32:
            raise ValueError("SSE_SECRET must be a hex-encoded 32-byte key")

        ts_bytes = struct.pack(">I", int(timestamp or now().timestamp()))
        nonce = nacl_random(24)
        header = self.VERSION_BYTE + ts_bytes + nonce

        ciphertext = crypto_aead_xchacha20poly1305_ietf_encrypt(payload, header, nonce, self.key)
        token = header + ciphertext
        return base62.encodebytes(token)

    def events_url(self, topics: list[str]) -> str:
        request_payload = {"topics": topics}
        payload: bytes = msgpack.packb(request_payload, use_bin_type=True)
        token = self.branca_encode(payload)
        return f"{self.url}/events?token={token}"

    def submit(self, events: list["SSEEvent"]) -> requests.Response:
        submission = {"events": [event.to_dict() for event in events]}
        payload: bytes = msgpack.packb(submission, use_bin_type=True)
        encoded = self.branca_encode(payload)
        return requests.post(f"{self.url}/submit", data=encoded)


class SSEEvent:
    def __init__(self, topic: str, event: str, data: str) -> None:
        self.topic = topic
        self.event = event
        self.data = data

    @classmethod
    def new(cls, topic: str, event: str, data: str) -> "SSEEvent":
        return cls(topic, event, data)

    @classmethod
    def new_json(cls, topic: str, event: str, data: BaseModel | dict) -> "SSEEvent":
        encoded = json.dumps(data)
        return cls(topic, event, encoded)

    def to_dict(self) -> dict:
        return {"topic": self.topic, "event": self.event, "data": self.data}
