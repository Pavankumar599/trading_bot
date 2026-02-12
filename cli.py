import argparse
import json
import logging
import os
import sys
from typing import Any, Dict

from bot.client import BinanceAPIError, BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import place_order, summarize_response
from bot.validators import ValidationError, validate_inputs

log = logging.getLogger(__name__)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Place orders on Binance USDT-M Futures Testnet (MARKET, LIMIT, STOP_MARKET)."
    )
    p.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    p.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    p.add_argument("--type", required=True, dest="order_type", choices=["MARKET", "LIMIT", "STOP_MARKET"], help="Order type")
    p.add_argument("--quantity", required=True, type=float, help="Order quantity (float)")
    p.add_argument("--price", type=float, help="Required for LIMIT orders")
    p.add_argument("--stop-price", dest="stop_price", type=float, help="Required for STOP_MARKET orders (bonus)")
    p.add_argument("--base-url", default="https://testnet.binancefuture.com", help="Base URL (default: testnet)")
    p.add_argument("--log-file", default=os.path.join("logs", "bot.log"), help="Log file path")
    p.add_argument("--api-key", default=os.getenv("BINANCE_API_KEY"), help="API key (or set BINANCE_API_KEY)")
    p.add_argument("--api-secret", default=os.getenv("BINANCE_API_SECRET"), help="API secret (or set BINANCE_API_SECRET)")
    return p

def print_request_summary(args: argparse.Namespace) -> None:
    summary = {
        "symbol": args.symbol,
        "side": args.side,
        "type": args.order_type,
        "quantity": args.quantity,
        "price": args.price,
        "stopPrice": args.stop_price,
        "base_url": args.base_url,
    }
    print("Order request summary:")
    print(json.dumps(summary, indent=2))

def print_response_details(resp: Dict[str, Any]) -> None:
    print("\nOrder response details:")
    print(json.dumps(resp, indent=2))

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(args.log_file)

    # Basic credential check
    if not args.api_key or not args.api_secret:
        print("ERROR: Missing API credentials. Provide --api-key/--api-secret or set BINANCE_API_KEY/BINANCE_API_SECRET.")
        return 2

    try:
        inp = validate_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as e:
        log.error("VALIDATION ERROR: %s", e)
        print(f"ERROR: {e}")
        return 2

    client = BinanceFuturesClient(
        api_key=args.api_key,
        api_secret=args.api_secret,
        base_url=args.base_url,
    )

    print_request_summary(args)

    try:
        raw = place_order(client, inp)
        summarized = summarize_response(raw)
        print_response_details(summarized)
        print("\n✅ Success: order placed on testnet.")
        return 0
    except BinanceAPIError as e:
        log.error("API ERROR: %s", e, exc_info=True)
        print("\n❌ Failure: Binance API error.")
        # Pretty print payload if possible
        payload = e.payload
        if isinstance(payload, dict):
            print(json.dumps(payload, indent=2))
        else:
            print(str(payload))
        return 1
    except Exception as e:
        log.exception("UNEXPECTED ERROR: %s", e)
        print("\n❌ Failure: unexpected error (see logs).")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
