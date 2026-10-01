"""
ORBIT Banking & Financial Services (BFSI) Stream Generator
Produces realistic transaction streams with accounts, merchants, risk scores, and geolocation.
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()
Faker.seed(42)

TRANSACTION_TYPES = ["wire_transfer", "card_payment", "atm_withdrawal", "ach_transfer", "pos_debit", "crypto_ramp"]
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
CHANNELS = ["mobile_app", "web_portal", "api_gateway", "in_branch", "atm_terminal"]
MERCHANT_CATEGORIES = ["technology", "aviation", "hospitality", "luxury_retail", "groceries", "utility", "health"]


def generate_banking_transaction(
    timestamp: datetime = None,
    seed: int = None
) -> Dict[str, Any]:
    """Generates a single synthetic banking transaction event."""
    if seed is not None:
        random.seed(seed)
    
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    txn_type = random.choice(TRANSACTION_TYPES)
    base_amount = (
        random.uniform(5.0, 450.0) if txn_type in ["card_payment", "pos_debit"]
        else random.uniform(500.0, 25000.0)
    )

    return {
        "event_id": f"txn_{fake.uuid4()[:12]}",
        "timestamp": timestamp.isoformat(),
        "account_id": f"acc_{random.randint(100000, 999999)}",
        "customer_id": f"cust_{random.randint(10000, 99999)}",
        "transaction_type": txn_type,
        "amount": round(base_amount, 2),
        "currency": random.choice(CURRENCIES),
        "channel": random.choice(CHANNELS),
        "merchant_name": fake.company(),
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "risk_score": round(random.betavariate(1.5, 8.0) * 100, 1), # Skewed toward lower risk
        "is_flagged": False,
        "origin_country": fake.country_code(),
        "status": "settled" if random.random() > 0.05 else "pending"
    }


def generate_banking_batch(count: int = 100, base_time: datetime = None, seed: int = None) -> List[Dict[str, Any]]:
    """Generates a batch of banking transactions."""
    if seed is not None:
        random.seed(seed)
    if base_time is None:
        base_time = datetime.now(timezone.utc)
    
    return [generate_banking_transaction(timestamp=base_time, seed=seed + i if seed else None) for i in range(count)]
