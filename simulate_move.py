import os
import sys
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from logiflow.deliveries.models import Delivery
from logiflow.realtime.emitters import emit_driver_move

print('Script starts!')

d = Delivery.objects.filter(id='aa8aa82b-30b3-4368-80a3-8eb7f2506cc4').first()
if not d:
    print('No delivery found!')
    sys.exit(1)

driver = d.assigned_driver
if not driver:
    print('No assigned driver')
    sys.exit(1)

print(f"Simulating movement for Driver [{driver.id}]")

if getattr(driver, 'current_location', None):
    # current_location is a GEOSGeometry Point (lng, lat)
    start_lat = driver.current_location.y
    start_lng = driver.current_location.x
else:
    start_lat = 40.7128
    start_lng = -74.0060

for i in range(200): # run for 100 seconds
    new_lat = start_lat + (i * 0.0005)
    new_lng = start_lng + (i * 0.0005)
    print(f"Emitting move: lat={new_lat}, lng={new_lng}", flush=True)
    emit_driver_move(str(driver.id), {"lat": new_lat, "lng": new_lng})
    time.sleep(0.5)

print("Simulation complete.", flush=True)
