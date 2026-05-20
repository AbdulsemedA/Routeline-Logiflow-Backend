from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def emit_socket_event(event_name, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global",
        {
            "type": "socket_event",
            "event": event_name,
            "data": data
        }
    )

def emit_driver_move(driver_id, location):
    emit_socket_event("driver:move", {"driverId": driver_id, "location": location})

def emit_delivery_status(delivery_id, status, note=None):
    emit_socket_event("delivery:status", {"deliveryId": delivery_id, "status": status, "note": note})
