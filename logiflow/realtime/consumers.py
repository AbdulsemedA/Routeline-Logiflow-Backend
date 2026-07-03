import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GlobalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"[GlobalConsumer] Incoming connection: {self.channel_name}")
        await self.channel_layer.group_add("global", self.channel_name)
        await self.accept()
        print(f"[GlobalConsumer] Connection accepted!")

    async def disconnect(self, close_code):
        print(f"[GlobalConsumer] Disconnected! Code: {close_code}")
        await self.channel_layer.group_discard("global", self.channel_name)

    async def socket_event(self, event):
        await self.send(text_data=json.dumps({
            "event": event["event"],
            "data": event.get("data", {})
        }))
