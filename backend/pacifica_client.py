"""Thin wrapper around Pacifica's public API endpoints."""

import requests
from dataclasses import dataclass


BASE_URL = "https://api.pacifica.fi/api/v1"


@dataclass
class MarketInfo:
    symbol: str
    max_leverage: int
    tick_size: float
    lot_size: float
    min_order_size: float
    max_order_size: float
    funding_rate: float
    next_funding_rate: float
    instrument_type: str
    base_asset: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "max_leverage": self.max_leverage,
            "tick_size": self.tick_size,
            "lot_size": self.lot_size,
            "min_order_size": self.min_order_size,
            "max_order_size": self.max_order_size,
            "funding_rate": self.funding_rate,
            "next_funding_rate": self.next_funding_rate,
            "instrument_type": self.instrument_type,
            "base_asset": self.base_asset,
        }


@dataclass
class MarketData:
    symbol: str
    mark: float
    oracle: float
    mid: float
    funding: float
    next_funding: float
    open_interest: float
    volume_24h: float
    yesterday_price: float

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "mark": self.mark,
            "oracle": self.oracle,
            "mid": self.mid,
            "funding": self.funding,
            "next_funding": self.next_funding,
            "open_interest": self.open_interest,
            "volume_24h": self.volume_24h,
            "yesterday_price": self.yesterday_price,
        }


@dataclass
class FundingRecord:
    oracle_price: float
    bid_impact_price: float
    ask_impact_price: float
    funding_rate: float
    next_funding_rate: float
    created_at: int  # unix ms


@dataclass
class OrderBookLevel:
    price: float
    amount: float
    count: int


@dataclass
class OrderBook:
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: int

    @property
    def bid_depth_usd(self) -> float:
        return sum(l.price * l.amount for l in self.bids)

    @property
    def ask_depth_usd(self) -> float:
        return sum(l.price * l.amount for l in self.asks)


class PacificaClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def _get(self, path: str, params: dict = None) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", True):
            raise RuntimeError(f"API error: {data.get('error', 'unknown')}")
        return data

    def get_markets(self) -> list[MarketInfo]:
        """GET /info — market specs for all pairs."""
        data = self._get("/info")
        markets = []
        for m in data["data"]:
            markets.append(MarketInfo(
                symbol=m["symbol"],
                max_leverage=int(m["max_leverage"]),
                tick_size=float(m["tick_size"]),
                lot_size=float(m["lot_size"]),
                min_order_size=float(m["min_order_size"]),
                max_order_size=float(m["max_order_size"]),
                funding_rate=float(m["funding_rate"]),
                next_funding_rate=float(m["next_funding_rate"]),
                instrument_type=m.get("instrument_type", "perpetual"),
                base_asset=m.get("base_asset", m["symbol"]),
            ))
        return markets

    def get_market_data(self) -> list[MarketData]:
        """GET /info/prices — live prices, OI, funding for all markets."""
        data = self._get("/info/prices")
        markets = []
        for m in data["data"]:
            markets.append(MarketData(
                symbol=m["symbol"],
                mark=float(m["mark"]),
                oracle=float(m["oracle"]),
                mid=float(m["mid"]),
                funding=float(m["funding"]),
                next_funding=float(m["next_funding"]),
                open_interest=float(m["open_interest"]),
                volume_24h=float(m["volume_24h"]),
                yesterday_price=float(m["yesterday_price"]),
            ))
        return markets

    def get_funding_history(self, symbol: str, limit: int = 4000) -> list[FundingRecord]:
        """GET /funding_rate/history — paginated funding rate history."""
        records = []
        cursor = None
        remaining = limit

        while remaining > 0:
            params = {"symbol": symbol, "limit": min(remaining, 4000)}
            if cursor:
                params["cursor"] = cursor

            data = self._get("/funding_rate/history", params=params)

            for r in data["data"]:
                records.append(FundingRecord(
                    oracle_price=float(r["oracle_price"]),
                    bid_impact_price=float(r["bid_impact_price"]),
                    ask_impact_price=float(r["ask_impact_price"]),
                    funding_rate=float(r["funding_rate"]),
                    next_funding_rate=float(r["next_funding_rate"]),
                    created_at=int(r["created_at"]),
                ))

            remaining -= len(data["data"])

            if not data.get("has_more", False):
                break
            cursor = data.get("next_cursor")

        return records

    def get_orderbook(self, symbol: str, agg_level: int = 100) -> OrderBook:
        """GET /book — orderbook depth."""
        data = self._get("/book", params={"symbol": symbol, "agg_level": agg_level})
        book_data = data["data"]

        bids = [
            OrderBookLevel(price=float(l["p"]), amount=float(l["a"]), count=int(l["n"]))
            for l in book_data["l"][0]  # l[0] = bids
        ]
        asks = [
            OrderBookLevel(price=float(l["p"]), amount=float(l["a"]), count=int(l["n"]))
            for l in book_data["l"][1]  # l[1] = asks
        ]

        return OrderBook(
            symbol=book_data["s"],
            bids=bids,
            asks=asks,
            timestamp=int(book_data["t"]),
        )

    def get_combined_market_info(self) -> list[dict]:
        """Merge /info and /info/prices into a single list for the frontend."""
        specs = {m.symbol: m for m in self.get_markets()}
        prices = {m.symbol: m for m in self.get_market_data()}

        combined = []
        for symbol in specs:
            spec = specs[symbol]
            price = prices.get(symbol)
            if not price:
                continue
            combined.append({
                **spec.to_dict(),
                **price.to_dict(),
            })

        # Sort by OI descending
        combined.sort(key=lambda x: x["open_interest"], reverse=True)
        return combined


if __name__ == "__main__":
    client = PacificaClient()

    print("=== Markets ===")
    markets = client.get_combined_market_info()
    for m in markets[:10]:
        print(f"  {m['symbol']:12s} Lev: {m['max_leverage']:3d}x  OI: ${m['open_interest']:>14,.2f}  Mark: {m['mark']}")

    print(f"\nTotal markets: {len(markets)}")

    print("\n=== BTC Orderbook ===")
    book = client.get_orderbook("BTC")
    print(f"  Bid depth: ${book.bid_depth_usd:,.0f}")
    print(f"  Ask depth: ${book.ask_depth_usd:,.0f}")
    for b in book.bids[:3]:
        print(f"  Bid: ${b.price:,.0f} x {b.amount} ({b.count} orders)")

    print("\n=== BTC Funding History (last 5) ===")
    history = client.get_funding_history("BTC", limit=5)
    for h in history:
        print(f"  Rate: {h.funding_rate:+.8f}  Oracle: ${h.oracle_price:,.2f}")
