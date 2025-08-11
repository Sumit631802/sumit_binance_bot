"""
CLI tool to place limit orders on USDT-M Futures.
Usage:
  python src/limit_orders.py BTCUSDT BUY 0.001 56000 --dry-run
"""

import argparse
import sys
from src.utils import valid_symbol, valid_side, valid_decimal, get_client, log_action, make_result

def place_limit_order(client, symbol, side, qty, price, time_in_force="GTC", dry_run=True):
    meta = {"symbol": symbol, "side": side, "quantity": qty, "price": price, "tif": time_in_force}
    log_action("order.attempt.limit", meta)
    if dry_run or client is None:
        log_action("order.placed.limit.mock", meta)
        return make_result(True, "Mock limit order placed", meta)

    try:
        resp = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce=time_in_force,
            quantity=qty,
            price=price
        )
        log_action("order.placed.limit", {"symbol": symbol, "resp": resp})
        return make_result(True, "Limit order placed", {"resp": resp})
    except Exception as e:
        log_action("order.error.limit", {"error": str(e)})
        return make_result(False, f"Error placing limit order: {e}")


def main(argv):
    parser = argparse.ArgumentParser(description="Place a limit order on Binance USDT-M Futures")
    parser.add_argument("symbol", type=str)
    parser.add_argument("side", type=str)
    parser.add_argument("quantity", type=str)
    parser.add_argument("price", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--testnet", action="store_true")
    args = parser.parse_args(argv)

    if not valid_symbol(args.symbol) or not valid_side(args.side) or not valid_decimal(args.quantity) or not valid_decimal(args.price):
        print("Invalid input"); return

    client = get_client(testnet=args.testnet, dry_run=args.dry_run)
    result = place_limit_order(client, args.symbol.upper(), args.side.upper(), float(args.quantity), str(args.price), dry_run=args.dry_run)
    print(result["message"])
    if not result["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
