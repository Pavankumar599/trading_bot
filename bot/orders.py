import logging
from typing import Any, Dict

from .client import BinanceFuturesClient
from .validators import OrderInput

log = logging.getLogger(__name__)

def build_order_params(inp: OrderInput) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": inp.symbol,
        "side": inp.side,
        "type": inp.order_type,
        "quantity": inp.quantity,
        # You can add 'newClientOrderId' here if desired
    }

    if inp.order_type == "LIMIT":
        params["price"] = inp.price
        params["timeInForce"] = "GTC"

    if inp.order_type == "STOP_MARKET":
        params["stopPrice"] = inp.stop_price
        # Optional: you can set workingType / priceProtect
        # params["workingType"] = "CONTRACT_PRICE"

    return params

def place_order(client: BinanceFuturesClient, inp: OrderInput) -> Dict[str, Any]:
    params = build_order_params(inp)
    return client.create_order(**params)

def summarize_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    # Common fields for futures create order response
    return {
        "orderId": resp.get("orderId"),
        "status": resp.get("status"),
        "executedQty": resp.get("executedQty"),
        "avgPrice": resp.get("avgPrice") or resp.get("avgFillPrice"),
        "clientOrderId": resp.get("clientOrderId"),
        "symbol": resp.get("symbol"),
        "side": resp.get("side"),
        "type": resp.get("type"),
        "price": resp.get("price"),
    }
