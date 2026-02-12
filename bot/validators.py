import re
from dataclasses import dataclass
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # STOP_MARKET is bonus

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{6,20}$")

class ValidationError(ValueError):
    pass

@dataclass(frozen=True)
class OrderInput:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None

def _ensure_positive(name: str, value: float) -> None:
    if value is None:
        raise ValidationError(f"{name} is required.")
    try:
        v = float(value)
    except Exception:
        raise ValidationError(f"{name} must be a number.")
    if v <= 0:
        raise ValidationError(f"{name} must be > 0.")

def validate_inputs(symbol: str, side: str, order_type: str, quantity, price=None, stop_price=None) -> OrderInput:
    symbol = (symbol or "").upper().strip()
    side = (side or "").upper().strip()
    order_type = (order_type or "").upper().strip()

    if not _SYMBOL_RE.match(symbol):
        raise ValidationError("symbol must be alphanumeric uppercase like BTCUSDT (6-20 chars).")

    if side not in VALID_SIDES:
        raise ValidationError(f"side must be one of {sorted(VALID_SIDES)}.")

    if order_type not in VALID_TYPES:
        raise ValidationError(f"type must be one of {sorted(VALID_TYPES)}.")

    _ensure_positive("quantity", quantity)
    quantity_f = float(quantity)

    price_f = None
    stop_f = None

    if order_type == "LIMIT":
        _ensure_positive("price", price)
        price_f = float(price)

    if order_type == "STOP_MARKET":
        _ensure_positive("stop-price", stop_price)
        stop_f = float(stop_price)

    return OrderInput(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity_f,
        price=price_f,
        stop_price=stop_f,
    )
