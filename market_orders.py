"""
CLI tool to place market orders on USDT-M Futures.
Usage:
  python src/market_orders.py BTCUSDT BUY 0.001 --dry-run
"""

import argparse
import sys
from src.utils import valid_symbol, valid_side, valid_decimal, get_client, log_action, make_result

def place_market_order(client, symbol, side, qty, dry_run=True):
    meta = {"symbol": symbol, "side": side, "quantity": qty}
    log_action("order.attempt.market", meta)
    if dry_run or client is None:
        log_action("order.placed.market.mock", meta)
        return make_result(True, "Mock market order placed", meta)

    try:
        # Using python-binance client if available
        resp = client.futures_create_order(symbol=symbol,
                                           side=side,
                                           type="MARKET",
                                           quantity=qty)
        log_action("order.placed.market", {"symbol": symbol, "resp": resp})
        return make_result(True, "Market order placed", {"resp": resp})
    except Exception as e:
        log_action("order.error.market", {"error": str(e)})
        return make_result(False, f"Error placing market order: {e}")


def main(argv):
    parser = argparse.ArgumentParser(description="Place a market order on Binance USDT-M Futures")
    parser.add_argument("symbol", type=str, help="Symbol, e.g. BTCUSDT")
    parser.add_argument("side", type=str, help="BUY or SELL")
    parser.add_argument("quantity", type=str, help="Quantity (float)")
    parser.add_argument("--dry-run", action="store_true", help="Do not send orders (default)")
    parser.add_argument("--testnet", action="store_true", help="Use testnet endpoints (if client supported)")
    args = parser.parse_args(argv)

    if not valid_symbol(args.symbol):
        print("Invalid symbol"); return
    if not valid_side(args.side):
        print("Invalid side"); return
    if not valid_decimal(args.quantity):
        print("Invalid quantity"); return

    client = get_client(testnet=args.testnet, dry_run=args.dry_run)
    result = place_market_order(client, args.symbol.upper(), args.side.upper(), float(args.quantity), dry_run=args.dry_run)
    print(result["message"])
    if not result["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
