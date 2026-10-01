"""
ORBIT Customer Behavioral Clickstream Generator
Produces high-velocity web/mobile app telemetry: page views, feature clicks, API calls, latency, errors.
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()
Faker.seed(999)

EVENT_ACTIONS = ["page_view", "search_query", "checkout_step", "filter_apply", "export_report", "api_call"]
DEVICE_TYPES = ["desktop_macos", "desktop_windows", "mobile_ios", "mobile_android", "headless_agent"]
HTTP_STATUS_CODES = [200, 200, 200, 201, 204, 400, 403, 404, 500, 503]


def generate_customer_event(
    timestamp: datetime = None,
    seed: int = None
) -> Dict[str, Any]:
    """Generates a single customer clickstream telemetry event."""
    if seed is not None:
        random.seed(seed)
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    action = random.choice(EVENT_ACTIONS)
    latency_ms = max(5, int(random.lognormvariate(4.0, 0.6)))
    status_code = random.choice(HTTP_STATUS_CODES) if random.random() < 0.08 else 200

    return {
        "event_id": f"evt_{fake.uuid4()[:12]}",
        "timestamp": timestamp.isoformat(),
        "session_id": f"sess_{random.randint(100000, 999999)}",
        "customer_id": f"cust_{random.randint(10000, 99999)}",
        "action": action,
        "page_url": fake.uri_path(),
        "device_type": random.choice(DEVICE_TYPES),
        "ip_address": fake.ipv4(),
        "client_latency_ms": latency_ms,
        "status_code": status_code,
        "payload_bytes": random.randint(256, 16384)
    }


def generate_customer_batch(count: int = 100, base_time: datetime = None, seed: int = None) -> List[Dict[str, Any]]:
    """Generates a batch of customer clickstream events."""
    if seed is not None:
        random.seed(seed)
    if base_time is None:
        base_time = datetime.now(timezone.utc)
    return [generate_customer_event(timestamp=base_time, seed=seed + i if seed else None) for i in range(count)]
