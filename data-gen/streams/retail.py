"""
ORBIT Retail Orders & Inventory Stream Generator
Simulates omnichannel retail orders, cart items, fulfillment warehouse inventory levels, and stockouts.
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()
Faker.seed(1337)

PRODUCT_CATEGORIES = [
    "Enterprise Servers", "Networking Racks", "Cloud Workstations", 
    "IoT Edge Nodes", "Quantum Accelerators", "Industrial Sensors"
]

WAREHOUSE_HUBS = [
    {"hub_id": "WH-US-EAST", "location": "New York, USA"},
    {"hub_id": "WH-US-WEST", "location": "San Jose, USA"},
    {"hub_id": "WH-EU-CENTRAL", "location": "Frankfurt, Germany"},
    {"hub_id": "WH-AP-SOUTH", "location": "Mumbai, India"},
    {"hub_id": "WH-AP-EAST", "location": "Tokyo, Japan"}
]


def generate_retail_order(
    timestamp: datetime = None,
    seed: int = None
) -> Dict[str, Any]:
    """Generates an enterprise retail / procurement order event."""
    if seed is not None:
        random.seed(seed)
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    warehouse = random.choice(WAREHOUSE_HUBS)
    items_count = random.randint(1, 12)
    unit_price = round(random.uniform(120.0, 4800.0), 2)
    discount_pct = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20]), 2)
    total_amount = round(items_count * unit_price * (1.0 - discount_pct), 2)

    return {
        "order_id": f"ord_{fake.uuid4()[:12]}",
        "timestamp": timestamp.isoformat(),
        "customer_id": f"cust_{random.randint(10000, 99999)}",
        "warehouse_id": warehouse["hub_id"],
        "product_category": random.choice(PRODUCT_CATEGORIES),
        "sku": f"SKU-{random.randint(1000, 9999)}-{fake.lexify(text='???').upper()}",
        "quantity": items_count,
        "unit_price": unit_price,
        "discount_applied": discount_pct,
        "total_amount": total_amount,
        "payment_method": random.choice(["corporate_net30", "procure_card", "wire", "escrow"]),
        "order_status": random.choice(["confirmed", "allocated", "awaiting_fulfillment"]),
        "inventory_remaining": random.randint(5, 500)
    }


def generate_retail_batch(count: int = 100, base_time: datetime = None, seed: int = None) -> List[Dict[str, Any]]:
    """Generates a batch of retail orders."""
    if seed is not None:
        random.seed(seed)
    if base_time is None:
        base_time = datetime.now(timezone.utc)
    return [generate_retail_order(timestamp=base_time, seed=seed + i if seed else None) for i in range(count)]
