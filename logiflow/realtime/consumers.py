import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GlobalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("global", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("global", self.channel_name)

    async def socket_event(self, event):
        await self.send(text_data=json.dumps({
            "event": event["event"],
            "data": event.get("data", {})
        }))
