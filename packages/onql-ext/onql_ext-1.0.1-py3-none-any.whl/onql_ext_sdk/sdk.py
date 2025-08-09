import asyncio
import json
import uuid
import nats
from typing import Dict, Callable, Any, Optional

class SDK:
    """
    A class-based SDK for ONQL extensions using NATS for communication.
    Use `SDK.create(keyword)` to get a connected, ready-to-use instance.
    """
    # The __init__ is now internal. Users should use SDK.create().
    def __init__(self, keyword: str, nats_url: str):
        self.keyword = keyword
        self.nats_url = nats_url
        self.connection: Optional[nats.NATS] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}

    @classmethod
    async def create(cls, keyword: str, nats_url: str = "nats://localhost:4222"):
        """Creates, connects, and returns a ready-to-use SDK instance."""
        sdk_instance = cls(keyword, nats_url)
        sdk_instance.connection = await nats.connect(sdk_instance.nats_url)
        # General subscription to handle responses to our requests
        await sdk_instance.connection.subscribe(f"{sdk_instance.keyword}.listen", cb=sdk_instance._handle_message)
        return sdk_instance

    async def _handle_message(self, msg):
        """Internal callback to route incoming NATS messages."""
        try:
            data = json.loads(msg.data.decode())
            if data.get("type") == "response":
                rid = data.get("rid")
                if rid in self.pending_requests:
                    future = self.pending_requests.pop(rid)
                    if not future.done():
                        future.set_result(data)
        except (json.JSONDecodeError, KeyError):
            pass

    def on_request(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers a callback to handle incoming requests."""
        if not self.connection:
            raise ConnectionError("SDK is not connected.")

        async def handler(msg):
            try:
                data = json.loads(msg.data.decode())
                if data.get("type") == "request":
                    asyncio.create_task(callback(data))
            except (json.JSONDecodeError, KeyError):
                pass
        
        asyncio.create_task(self.connection.subscribe(f"{self.keyword}.listen", cb=handler))

    async def request(self, target: str, payload: Any, timeout: int = 30) -> Dict[str, Any]:
        """Sends a request to a target extension and waits for a response."""
        if not self.connection:
            raise ConnectionError("SDK is not connected.")

        rid = str(uuid.uuid4())
        req = {"id": self.keyword, "rid": rid, "target": target, "payload": payload, "type": "request"}
        future = asyncio.Future()
        self.pending_requests[rid] = future
        await self.connection.publish(f"{self.keyword}.send", json.dumps(req).encode())
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.pending_requests.pop(rid, None)
            return {"type": "timeout", "rid": rid, "error": f"Request to '{target}' timed out."}

    async def response(self, req_data: Dict[str, Any], data: Any):
        """Sends a response back to a requester."""
        if not self.connection:
            raise ConnectionError("SDK is not connected.")

        res = {"id": self.keyword, "target": req_data["id"], "rid": req_data["rid"], "payload": req_data["payload"], "data": data, "type": "response"}
        await self.connection.publish(f"{self.keyword}.send", json.dumps(res).encode())

    async def close(self):
        """Gracefully closes the NATS connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.drain()
            self.connection = None
            print(f"Connection closed for '{self.keyword}'.")
        