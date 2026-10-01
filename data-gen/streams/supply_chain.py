"""
ORBIT Supply Chain & Logistics Stream Generator
Simulates container shipments, carrier routing, GPS coordinates, IoT temperature sensors, and transit delays.
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta, timezone
from faker import Faker

fake = Faker()
Faker.seed(777)

CARRIERS = ["Maersk Line", "DHL Global Forwarding", "FedEx Supply Chain", "Kuehne+Nagel", "MSC"]
TRANSPORT_MODES = ["air_cargo", "ocean_freight", "intermodal_rail", "dedicated_fleet"]
TRANSIT_STATUSES = ["in_transit", "customs_hold", "port_clearance", "out_for_delivery", "delivered", "exception_delayed"]


def generate_supply_chain_shipment(
    timestamp: datetime = None,
    seed: int = None
) -> Dict[str, Any]:
    """Generates an enterprise shipment and transit tracking telemetry record."""
    if seed is not None:
        random.seed(seed)
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    carrier = random.choice(CARRIERS)
    mode = random.choice(TRANSPORT_MODES)
    days_to_eta = random.randint(1, 14)
    eta = timestamp + timedelta(days=days_to_eta)
    
    # Ambient temp in Celsius (-20 for cold chain, +20 for standard)
    is_cold_chain = random.random() < 0.25
    ambient_temp = round(random.normalvariate(-18.0 if is_cold_chain else 21.0, 1.5), 1)

    return {
        "shipment_id": f"shp_{fake.uuid4()[:12]}",
        "timestamp": timestamp.isoformat(),
        "order_id": f"ord_{fake.uuid4()[:12]}",
        "carrier_name": carrier,
        "transport_mode": mode,
        "origin_hub": fake.city(),
        "destination_hub": fake.city(),
        "current_latitude": round(float(fake.latitude()), 4),
        "current_longitude": round(float(fake.longitude()), 4),
        "status": random.choice(TRANSIT_STATUSES),
        "estimated_arrival": eta.isoformat(),
        "is_cold_chain": is_cold_chain,
        "cargo_temp_celsius": ambient_temp,
        "transit_delay_hours": max(0, int(random.expovariate(0.2))) if random.random() < 0.2 else 0
    }


def generate_supply_chain_batch(count: int = 100, base_time: datetime = None, seed: int = None) -> List[Dict[str, Any]]:
    """Generates a batch of supply chain shipments."""
    if seed is not None:
        random.seed(seed)
    if base_time is None:
        base_time = datetime.now(timezone.utc)
    return [generate_supply_chain_shipment(timestamp=base_time, seed=seed + i if seed else None) for i in range(count)]
