# MEXC API SDK

An unofficial, fully-typed async Python SDK for the MEXC cryptocurrency exchange, with Trading SDK compatibility.

## Installation

```bash
pip install mexc-trading-sdk
```

## Features

- Fully async (with `httpx`)
- Type-annotated (with `TypedDict`, `Literal`, etc.) and validated (with `pydantic`)
- [Trading SDK](https://github.com/tribulnation/sdk) compatibility layer
- Easy context-managed usage (with `async with`)
- Comprehensive spot trading, market data, and wallet endpoints

## Usage

```python
from mexc import MEXC  # Main async client

API_KEY = "your_api_key" # aka "access key"
API_SECRET = "your_api_secret" # aka "secret key"

async with MEXC(API_KEY, API_SECRET) as client:
  r = await client.place_order('BTCUSDT', {
    'price': '100000',
    'quantity': '0.001',
    'type': 'LIMIT',
    'side': 'BUY',
  })
```

> Get your API keys from the [MEXC dashboard](https://www.mexc.com/user/openapi).

Or, you can use public methods:

```python
from mexc.api.spot import MarketData

async with MarketData() as client:
  candles = await client.candles('BTCUSDT', interval='15m')
```

## Trading SDK Compatibility

This SDK includes a compatibility layer with the [Trading SDK](https://github.com/tribulnation/sdk).

> Note: For Trading SDK compatibility, use `from mexc.sdk import MEXC`, not `from mexc import MEXC`.

```python
import trading_sdk as tdk
from mexc.sdk import MEXC

async def micro_strategy(client: tdk.Trading):
    while True:
        await client.place_order('BTCUSDT', {
            'quantity': '1',
            'type': 'MARKET',
            'side': 'BUY',
        })
        await asyncio.sleep(3600*24)

async with MEXC(API_KEY, API_SECRET) as client:
    await micro_strategy(client)
```

## Supported APIs

The SDK covers the following MEXC endpoints:

### Spot

#### Trading
- [`place_order`](mexc/src/mexc/api/spot/trading/place_order.py)
- [`query_order`](mexc/src/mexc/api/spot/trading/query_order.py)
- [`query_all_orders`](mexc/src/mexc/api/spot/trading/query_all_orders.py)
- [`cancel_order`](mexc/src/mexc/api/spot/trading/cancel_order.py)
- [`cancel_all_orders`](mexc/src/mexc/api/spot/trading/cancel_all_orders.py)

#### User Data
- [`account`](mexc/src/mexc/api/spot/user_data/account.py) (balances)
- [`my_trades`](mexc/src/mexc/api/spot/user_data/my_trades.py)

#### Market Data
- [`time`](mexc/src/mexc/api/spot/market_data/time.py) (server time)
- [`depth`](mexc/src/mexc/api/spot/market_data/depth.py) (order book)
- [`candles`](mexc/src/mexc/api/spot/market_data/candles.py) (klines)
- [`trades`](mexc/src/mexc/api/spot/market_data/trades.py) (recent trades)
- [`agg_trades`](mexc/src/mexc/api/spot/market_data/agg_trades.py)

### Wallet
- [`currency_info`](mexc/src/mexc/api/wallet/currency_info.py) (withdrawal methods)
- [`deposit_addresses`](mexc/src/mexc/api/wallet/deposit_addresses.py) (deposit methods)
- [`withdraw`](mexc/src/mexc/api/wallet/withdraw.py)
- [`cancel_withdraw`](mexc/src/mexc/api/wallet/cancel_withdraw.py)
