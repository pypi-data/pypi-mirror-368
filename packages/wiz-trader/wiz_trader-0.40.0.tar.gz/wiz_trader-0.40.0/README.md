# WizTrader SDK Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Authentication](#authentication)
4. [Quotes Client](#quotes-client)
    - [Initialization](#quotes-client-initialization)
    - [Connection Methods](#connection-methods)
    - [Callbacks](#callbacks)
    - [Subscribing to Instruments](#subscribing-to-instruments)
    - [Unsubscribing from Instruments](#unsubscribing-from-instruments)
    - [Account Events](#account-events)
    - [Handling WebSocket Connection](#handling-websocket-connection)
    - [Complete Examples](#quotes-client-examples)
5. [Wizzer Client](#wizzer-client)
    - [Initialization](#wizzer-client-initialization)
    - [Constants](#constants)
    - [Data Hub Methods](#data-hub-methods)
    - [Order Management](#order-management)
    - [Portfolio Management](#portfolio-management)
    - [Basket Management](#basket-management)
    - [Instrument Management](#instrument-management)
    - [Instrument Screener](#instrument-screener)
    - [Analytics API](#analytics-api)
    - [Complete Examples](#wizzer-client-examples)
6. [Common Use Cases](#common-use-cases)
7. [Error Handling](#error-handling)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

## Introduction

WizTrader is a Python SDK for connecting to the Wizzer trading platform. It provides two main client classes:

- **QuotesClient**: For real-time market data streaming via WebSockets
- **WizzerClient**: For REST API access to trading, order management, and market data, including data pipelines and classification APIs.

This documentation covers all the ways to use the SDK, with examples for each endpoint and common use cases.

## Installation

You can install the package directly from PyPI:

```bash
pip install wiz_trader
```

To install the development version from GitHub:

```bash
pip install git+https://github.com/wizzer-tech/wiz_trader.git
```

## Authentication

There are two ways to provide authentication credentials to the SDK:

1. **Direct parameter passing** (Recommended for most use cases)
2. **Environment variables** (Recommended for production deployments)

### Direct Parameter Passing

Simply provide the required parameters directly when initializing the clients:

```python
from wiz_trader import QuotesClient, WizzerClient

quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    strategy_id="str_01hxgwgfxgfrxb48bzchnve7gm",  # Optional
    log_level="info"
)
```

### Environment Variables

Set the following environment variables:

```bash
export WZ__QUOTES_BASE_URL="wss://websocket-url/quotes"
export WZ__API_BASE_URL="https://api-url.in"
export WZ__TOKEN="your-jwt-token"
export WZ__STRATEGY_ID="str_01hxgwgfxgfrxb48bzchnve7gm"  # Optional
```

Then initialize the clients without parameters:

```python
from wiz_trader import QuotesClient, WizzerClient

quotes_client = QuotesClient(log_level="info")
wizzer_client = WizzerClient(log_level="info")
```

You can also use a hybrid approach, providing some parameters directly and letting others fall back to environment variables:

```python
quotes_client = QuotesClient(log_level="debug")  # Only override log level
```

## Quotes Client

The `QuotesClient` enables you to connect to Wizzer's WebSocket server for real‑time market data using **plain synchronous** callbacks—no `async def` required.

### Quotes Client Initialization

You can initialize the `QuotesClient` in several ways:

```python
from wiz_trader import QuotesClient

# Method 1: All parameters provided directly
client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info",         # Options: "error", "info", "debug"
    max_message_size=10 * 1024 * 1024,  # Optional: default 10MB
    batch_size=20             # Optional: default 20 instruments per batch
)

# Method 2: Using environment variables
# (Requires WZ__QUOTES_BASE_URL and WZ__TOKEN set)
client = QuotesClient(log_level="info")

# Method 3: Mixed approach
client = QuotesClient(
    base_url="wss://custom-url/quotes",
    log_level="debug"         # token from WZ__TOKEN env var
)
```

### Connection Methods

#### Blocking Connection

Blocks your main thread, similar to Zerodha’s KiteTicker:

```python
client.connect()
```

#### Non‑Blocking Connection

Run alongside your own `asyncio` code:

```python
client.connect_async()
# … do other work …
client.stop()
```

### Callbacks

All callbacks are **plain `def`** functions.  Inside them you can call `subscribe(...)`, which under the hood schedules the actual async work—so you never `await` in your callbacks.

The QuotesClient routes messages based on their `type` field:
- Messages with `type: 'ticks'` are sent to the `on_tick` callback
- Messages with `type: 'greeks'` are sent to the `on_stats` callback
- Messages without a `type` field are sent to `on_tick` for backward compatibility

```python
def on_tick(ws, tick):
    print("Tick:", tick)

def on_stats(ws, stats):
    print("Stats:", stats)
    # Stats/Greek messages contain: {'type': 'greeks', 'identifier': '...', 'rho': 0.1, 'theta': 9.8, ...}

def on_connect(ws):
    print("Connected!")
    # Subscribe with different modes
    ws.subscribe(["NSE:SBIN:3045"], mode="ticks")      # Will receive tick messages
    ws.subscribe(["NSE:NIFTY25JULFUT:53216"], mode="greeks") # Will receive greek messages
    ws.subscribe(["NSE:RELIANCE:2885"], mode="full")   # Will receive both types

def on_close(ws, code, reason):
    print(f"Connection closed [{code}]: {reason}")
    ws.stop()   # to prevent auto‑reconnect

def on_error(ws, error):
    print("Error:", error)

client.on_tick    = on_tick
client.on_stats   = on_stats
client.on_connect = on_connect
client.on_close   = on_close
client.on_error   = on_error
```

### Subscribing to Instruments

Call `ws.subscribe([...])` directly; the SDK will batch large lists and send them over the socket:

```python
def on_connect(ws):
    # subscribe without await
    ws.subscribe([
        "NSE:SBIN:3045",
        "NSE:ICICIBANK:4963",
        "NSE:RELIANCE:2885",
    ])
```

### Unsubscribing from Instruments

Use the `unsubscribe` method to stop receiving real-time data for specific instruments. This helps manage bandwidth and reduces unnecessary data processing.

```python
# Unsubscribe from specific instruments
ws.unsubscribe(["NSE:SBIN:3045", "NSE:ICICIBANK:4963"])

# You can also unsubscribe from a single instrument
ws.unsubscribe(["NSE:RELIANCE:2885"])
```

**Key Features:**
- Immediately stops tick data for the specified instruments
- Reduces network bandwidth and processing overhead
- Can be called multiple times for different instrument sets
- No callback fired for unsubscribed instruments

### Account Events

The QuotesClient now supports automatic reception of account-related events (orders, trades, positions, holdings) from the quotes server. These events are automatically pushed to SDK users via dedicated callback handlers based on the event type.

#### Event Handlers

Register event handlers to receive real-time updates for your account activity:

```python
def on_order(ws, order):
    print(f"Order event: {order}")

def on_trade(ws, trade):
    print(f"Trade event: {trade}")

def on_position(ws, position):
    print(f"Position event: {position}")

def on_holding(ws, holding):
    print(f"Holding event: {holding}")

# Register event handlers
client.on_order = on_order
client.on_trade = on_trade
client.on_position = on_position
client.on_holding = on_holding
```

#### Key Features

- **Automatic Event Reception**: No explicit subscription needed - events are automatically sent based on your JWT token's account ID and strategy ID
- **Optional Handlers**: Events are silently dropped if no handler is registered - you only receive what you need
- **Message Normalization**: The SDK automatically handles different message formats and delivers clean, flattened event data to your handlers
- **Error Resilience**: Handler exceptions are caught and logged without breaking the event flow
- **Backward Compatible**: Existing tick and Greeks functionality remains unchanged

#### Event Data Structure

All event handlers receive flattened event data with the event type preserved:

```python
# Example order event data
{
    "_id": "order_01k10np7weemkv812nx55bppw5",
    "accountEntityType": "client",
    "accountId": "user_01j9brznsffphvzqn9gzyj1frw",
    "avgPrice": 72.65,
    "broker": "wizzer",
    "brokerOrderId": "dssorder_175344314711184",
    "brokerTimestamp": "2025-07-25T11:32:28.147Z",
    "cancelledQty": 0,
    "completedAt": "2025-07-25T11:32:28.147Z",
    "createdAt": "2025-07-25T11:32:27.722Z",
    "disclosedQty": 0,
    "exchange": "NSE",
    "exchangeOrderId": "dssx_1753443147",
    "exchangeToken": 11184,
    "exchangeUpdateTimestamp": "2025-07-25T11:32:28.147Z",
    "executionType": "regular",
    "filledQty": 1,
    "guid": "t0lVueivgBgcEh2k_BP",
    "instrumentType": "EQLC",
    "isDealer": false,
    "isOrderModified": false,
    "legs": [],
    "marginUsed": 0,
    "meta": {
        "dss": {"orderId": "order_01k10np7weemkv812nx55bppw5"},
        "source": "wizzer.dss",
        "wizzer": {"mode": "paper_trading"}
    },
    "orderType": "MARKET",
    "parentOrderId": "",
    "pendingQty": 1,
    "placedBy": "user_01j9brznsffphvzqn9gzyj1frw",
    "price": 0,
    "product": "CNC",
    "qty": 1,
    "remarks": "",
    "segment": "NSECM",
    "slPrice": 0,
    "slTriggerPrice": 0,
    "sqOffHoldingId": "",
    "sqOffPositionId": "",
    "status": "COMPLETED",
    "stoploss": 0,
    "stoplossOrderId": "",
    "strategy": {
        "id": "stgy_01jtn7t3erf8ss78spqy40k8en",
        "identifier": "S-608377",
        "name": "Test 1122"
    },
    "target": 0,
    "targetOrderId": "",
    "tradingSymbol": "IDFCFIRSTB",
    "transactionType": "BUY",
    "triggerId": "",
    "triggerPrice": 0,
    "updatedAt": "2025-07-25T11:32:28.254Z",
    "userId": "user_01j9brznsffphvzqn9gzyj1frw",
    "validity": "DAY",
    "variety": "REGULAR"
}

# Example trade event data
{
    "_id": "trade_01k10np8rqef793zr93ctqj0wt",
    "accountId": "user_01j9brznsffphvzqn9gzyj1frw",
    "avgPrice": 72.65,
    "broker": "wizzer",
    "brokerOrderId": "dssorder_175344314711184",
    "createdAt": "2025-07-25T11:32:28.567Z",
    "exchange": "NSE",
    "exchangeOrderId": "dssx_1753443147",
    "exchangeTimestamp": "2025-07-25T11:32:28.147Z",
    "exchangeToken": 11184,
    "isDividend": false,
    "meta": {
        "dss": {"orderId": "order_01k10np7weemkv812nx55bppw5"},
        "source": "wizzer.dss",
        "wizzer": {"mode": "paper_trading"}
    },
    "orderId": "order_01k10np7weemkv812nx55bppw5",
    "orderType": "MARKET",
    "parentOrderId": "",
    "parentTradeId": "",
    "product": "CNC",
    "qty": 1,
    "segment": "NSECM",
    "strategy": {
        "id": "stgy_01jtn7t3erf8ss78spqy40k8en",
        "identifier": "S-608377",
        "name": "Test 1122"
    },
    "tradeId": "dsstrade_50PccSfWvsCg-Cr5dQE",
    "tradingSymbol": "IDFCFIRSTB",
    "transactionType": "BUY",
    "updatedAt": "2025-07-25T11:32:28.567Z",
    "userId": "user_01j9brznsffphvzqn9gzyj1frw"
}

# Example position event data
{
    "_id": "pos_01k10np8t7e0fs63q52hacbx8m",
    "accountEntityType": "client",
    "accountId": "user_01j9brznsffphvzqn9gzyj1frw",
    "bep": 0,
    "broker": "wizzer",
    "buyAvgPrice": 72.65,
    "buyOrders": ["order_01k10np7weemkv812nx55bppw5"],
    "buyQty": 1,
    "buyTrades": ["trade_01k10np8rqef793zr93ctqj0wt"],
    "buyValue": 72.65,
    "closePrice": 0,
    "createdAt": "2025-07-25T11:32:28.614Z",
    "exchange": "NSE",
    "exchangeToken": 11184,
    "instrumentType": "EQLC",
    "lotSize": 1,
    "meta": {
        "source": "wizzer.dss",
        "wizzer": {"mode": "paper_trading"}
    },
    "netQty": 1,
    "pnlPercentage": 0,
    "product": "CNC",
    "realisedPnlToday": 0,
    "segment": "NSECM",
    "sellAvgPrice": 0,
    "sellOrders": [],
    "sellQty": 0,
    "sellTrades": [],
    "sellValue": 0,
    "slPrice": null,
    "slTriggerPrice": null,
    "status": "open",
    "stoploss": 0,
    "strategy": {
        "id": "stgy_01jtn7t3erf8ss78spqy40k8en",
        "identifier": "S-608377",
        "name": "Test 1122"
    },
    "target": 0,
    "tradingSymbol": "IDFCFIRSTB",
    "unrealisedPnlToday": 0,
    "updatedAt": "2025-07-25T11:32:28.614Z",
    "userId": "user_01j9brznsffphvzqn9gzyj1frw"
}

# Example holding event data
{
    "_id": "holding_01k10np8t7e0fs63q52hacbx8m",
    "accountEntityType": "client",
    "accountId": "user_01j9brznsffphvzqn9gzyj1frw",
    "bep": 0,
    "broker": "wizzer",
    "buyAvgPrice": 72.65,
    "buyOrders": ["order_01k10np7weemkv812nx55bppw5"],
    "buyQty": 1,
    "buyTrades": ["trade_01k10np8rqef793zr93ctqj0wt"],
    "buyValue": 72.65,
    "closePrice": 0,
    "createdAt": "2025-07-25T11:32:28.614Z",
    "exchange": "NSE",
    "exchangeToken": 11184,
    "instrumentType": "EQLC",
    "lotSize": 1,
    "meta": {
        "source": "wizzer.dss",
        "wizzer": {"mode": "paper_trading"}
    },
    "netQty": 1,
    "pnlPercentage": 0,
    "product": "CNC",
    "realisedPnlToday": 0,
    "segment": "NSECM",
    "sellAvgPrice": 0,
    "sellOrders": [],
    "sellQty": 0,
    "sellTrades": [],
    "sellValue": 0,
    "slPrice": null,
    "slTriggerPrice": null,
    "status": "open",
    "stoploss": 0,
    "strategy": {
        "id": "stgy_01jtn7t3erf8ss78spqy40k8en",
        "identifier": "S-608377",
        "name": "Test 1122"
    },
    "target": 0,
    "tradingSymbol": "IDFCFIRSTB",
    "unrealisedPnlToday": 0,
    "updatedAt": "2025-07-25T11:32:28.614Z",
    "userId": "user_01j9brznsffphvzqn9gzyj1frw"
}
```

#### Complete Event Handling Example

```python
from wiz_trader import QuotesClient

# Initialize client
client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

def on_order(ws, order):    
    # React to order status changes
    if order['status'] == ORDER_STATUS_COMPLETED:
        print(f"Order {order['_id']} completed!")
    elif order['status'] == ORDER_STATUS_REJECTED:
        print(f"Order {order['_id']} rejected: {order.get('remarks', 'Unknown')}")

def on_trade(ws, trade):
    print(f"Trade executed: {trade['qty']} x {trade['tradingSymbol']} @ {trade['avgPrice']}")

def on_position(ws, position):
    print(f"Position update: {position['tradingSymbol']} = {position['netQty']} (PnL: {position.get('unrealisedPnlToday', 0)})")

def on_holding(ws, holding):
    print(f"Holding update: {holding['tradingSymbol']} = {holding['netQty']}")

def on_connect(ws):
    print("Connected! Ready to receive events.")
    # Also subscribe to some ticks if needed
    ws.subscribe(["NSE:SBIN:3045"], mode="ticks")

# Register all handlers
client.on_order = on_order
client.on_trade = on_trade
client.on_position = on_position
client.on_holding = on_holding
client.on_connect = on_connect

# Connect and receive events
client.connect()
```

#### Event-Driven Trading Strategy Example

```python
class EventDrivenStrategy:
    def __init__(self):
        self.orders = {}
        self.positions = {}
        self.pending_orders = set()
    
    def on_order_event(self, ws, order):
        order_id = order['_id']
        self.orders[order_id] = order
        
        # Track pending orders
        if order['status'] == ORDER_STATUS_OPEN:
            self.pending_orders.add(order_id)
        elif order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        # Log order lifecycle
        print(f"Order {order_id}: {order['status']}")
        
        # React to rejections
        if order['status'] == ORDER_STATUS_REJECTED:
            print(f"Order rejected! Reason: {order.get('remarks', 'Unknown')}")
            # Implement retry logic or alternative strategy
    
    def on_position_event(self, ws, position):
        symbol = position['tradingSymbol']
        self.positions[symbol] = position
        
        # Monitor position changes
        print(f"Position {symbol}: Qty={position['netQty']}, PnL={position.get('unrealisedPnlToday', 0)}")
        
        # Implement stop-loss or take-profit logic
        pnl = position.get('unrealisedPnlToday', 0)
        if pnl < -100:  # Stop loss at -100
            print(f"Stop loss triggered for {symbol}")
            # Place exit order
        elif pnl > 200:  # Take profit at 200
            print(f"Take profit triggered for {symbol}")
            # Place exit order
    
    def on_trade_event(self, ws, trade):
        print(f"Trade executed: {trade['qty']} @ {trade['avgPrice']}")
        # Update internal trade log, calculate VWAP, etc.

# Initialize strategy
strategy = EventDrivenStrategy()

# Set up client with strategy handlers
client = QuotesClient(base_url="wss://...", token="...")
client.on_order = strategy.on_order_event
client.on_position = strategy.on_position_event
client.on_trade = strategy.on_trade_event

client.connect()
```

### Complete Examples

#### Blocking Example

```python
import logging
from wiz_trader import QuotesClient

logging.basicConfig(level=logging.INFO)

client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token"
)

def on_tick(ws, tick):
    logging.debug("Tick: %s", tick)

def on_stats(ws, stats):
    logging.debug("Stats: %s", stats)

def on_connect(ws):
    logging.info("Connected.")
    ws.subscribe(["NSE:SBIN:3045"], mode="ticks")
    ws.subscribe(["NSE:NIFTY24JUN20100CE:20100"], mode="greeks")

def on_close(ws, code, reason):
    logging.warning("Closed: %s", reason)
    ws.stop()

def on_error(ws, error):
    logging.error("Error: %s", error)

client.on_tick    = on_tick
client.on_stats   = on_stats
client.on_connect = on_connect
client.on_close   = on_close
client.on_error   = on_error

try:
    client.connect()
except KeyboardInterrupt:
    client.stop()
```

#### Non‑Blocking Example

```python
import asyncio
import logging
from wiz_trader import QuotesClient

async def main():
    logging.basicConfig(level=logging.INFO)
    client = QuotesClient(
        base_url="wss://websocket-url/quotes",
        token="your-jwt-token"
    )
    client.on_tick    = lambda ws, tick: logging.info(tick)
    client.on_connect = lambda ws: ws.subscribe(["NSE:SBIN:3045"])
    client.connect_async()

    # Your other async work here...
    await asyncio.sleep(60)
    client.stop()

asyncio.run(main())
```

#### Message Data Structures

##### Ticks structure
Messages with `type: 'ticks'` contain market data:
- `ts`: tick timestamp
- `lastTradedTs`: timestamp of the last executed trade in this instrument
- `oi`: Current open interest (for futures and options)
- `oiDayHigh`: Day's highest open interest value  
- `oiDayLow`: Day's lowest open interest value

```json
{
  "type": "ticks",
  "identifier": "NSE:RELIANCE:2885",
  "tradingSymbol": "RELIANCE",
  "exchange": "NSE",
  "segment": "NSECM",
  "exchangeToken": 2885,
  "bids": [{"volume": 1722, "price": 1295.5, "orders": 43}, ...],
  "offers": [{"volume": 0, "price": 0, "orders": 0}, ...],
  "ltp": 1295.5,
  "lastTradedQty": 10,
  "buyQty": 1722,
  "sellQty": 0,
  "volume": 10429964,
  "avgPrice": 1291.46,
  "netChange": 0,
  "ohlc": {"open": 1270, "high": 1300.9, "low": 1267, "close": 1295.5},
  "oi": 1234567,
  "oiDayHigh": 1250000,
  "oiDayLow": 1200000,
  "lastTradedTs": "2025-04-21T10:29:33Z",
  "ts": "2025-04-21T10:29:46Z"
}
```

##### Greeks structure
Messages with `type: 'greeks'` contain options Greeks data:

```json
{
  "type": "greeks",
  "identifier": "NSE:NIFTY25JULFUT:53216",
  "tradingSymbol": "NIFTY25JULFUT",
  "iv": 0.0,
  "delta": 0.0,
  "gamma": 0.0,
  "theta": 0.0,
  "vega": 0.0,
  "rho": 0.0,
  "ts": "2025-04-21T10:29:46Z"
}
```

## Wizzer Client

The `WizzerClient` provides access to Wizzer's REST APIs for trading, portfolio management, and market data.

### Wizzer Client Initialization

Initialize the client with your authentication details:

```python
from wiz_trader import WizzerClient

# Method 1: All parameters provided directly
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    strategy_id="str_01hxgwgfxgfrxb48bzchnve7gm",  # Optional: Default strategy ID
    log_level="info"  # Options: "error", "info", "debug"
)

# Method 2: Using environment variables
# (Requires WZ__API_BASE_URL and WZ__TOKEN to be set)
client = WizzerClient(log_level="info")
```

### Constants

The `WizzerClient` provides constants for various parameter values, making your code more readable and type-safe:

```python
from wiz_trader import WizzerClient

client = WizzerClient(...)

# Use constants for transaction types
client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_MARKET,
    product=client.PRODUCT_CNC
)
```

Available constants:

- Transaction types: `TRANSACTION_TYPE_BUY`, `TRANSACTION_TYPE_SELL`
- Product types: `PRODUCT_CNC`, `PRODUCT_MIS`, `PRODUCT_NRML`
- Order types: `ORDER_TYPE_MARKET`, `ORDER_TYPE_LIMIT`, `ORDER_TYPE_SL`, `ORDER_TYPE_SLM`
- Order status: `ORDER_STATUS_OPEN`, `ORDER_STATUS_CANCELLED`, `ORDER_STATUS_REJECTED`, `ORDER_STATUS_PENDING`, `ORDER_STATUS_COMPLETED`
- Validity types: `VALIDITY_DAY`, `VALIDITY_IOC`, `VALIDITY_GTT`
- Variety types: `VARIETY_REGULAR`, `VARIETY_AMO`, `VARIETY_BO`, `VARIETY_CO`
- Exchanges: `EXCHANGE_NSE`, `EXCHANGE_BSE`, `EXCHANGE_WZR`
- Segments: `SEGMENT_NSE_CM`, `SEGMENT_BSE_CM`, `SEGMENT_NSE_FO`, `SEGMENT_WZREQ`
- Instrument types: `INSTRUMENT_TYPE_EQ`, `INSTRUMENT_TYPE_EQLC`, `INSTRUMENT_TYPE_EQMCC`, `INSTRUMENT_TYPE_EQSCC`, `INSTRUMENT_TYPE_BASKET`
- - Weightage schemes: `WEIGHTAGE_SCHEME_EQUI_WEIGHTED`, `WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED`, `WEIGHTAGE_SCHEME_PRICE_WEIGHTED`, `WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED`, `WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED`, `WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED`, `WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED`

### Data Hub Methods

#### Get Indices

Fetch available indices from an exchange:

```python
# Get all indices from NSE
indices = client.get_indices(exchange="NSE")
print(f"Found {len(indices)} indices")

# Get a specific index by trading symbol
nifty_50 = client.get_indices(trading_symbol="NIFTY 50", exchange="NSE")
```

#### Get Index Components

Fetch components (stocks) in a specific index:

```python
# Get components of NIFTY 50
components = client.get_index_components(trading_symbol="NIFTY 50", exchange="NSE")
print(f"Found {len(components)} components in NIFTY 50")
for component in components[:5]:
    print(f"{component['tradingSymbol']} - {component.get('weightage', 'N/A')}%")
```

#### List Classification Types

Retrieve all available classification types.

```python
classification_types = client.get_classification_types()
# Response: ['basicIndustry', 'industry', 'macroEconomicSector', 'sector']
```

#### List Classification Values

Retrieve all values for a specific classification type.

```python
basic_industry_values = client.get_classifications("basicIndustry")
# Response: ['Aerospace & Defense', 'Agricultural Food & other Products', ...]
```

#### Filter Indices by Classifications

Filter indices based on multiple classification criteria. The `match_all` parameter controls the filter logic:
- `True`: AND logic (all filters must match)
- `False`: OR logic (any filter can match)

```python
# Example: Find indices in the 'Commodities' macro-economic sector OR 'Aerospace & Defense' industry
filters = {
    "macroEconomicSector": ["Commodities"],
    "industry": ["Aerospace & Defense"]
}
or_logic_indices = client.filter_indices(filters=filters, match_all=False)

# Example: Find indices that are in BOTH 'Housing Finance Company' and 'Financial Services'
filters = {
    "basicIndustry": ["Housing Finance Company"],
    "sector": ["Financial Services"]
}
and_logic_indices = client.filter_indices(filters=filters, match_all=True)
```

#### Filter Instruments by Classifications

Filter instruments based on classification criteria.

```python
# Example: Find instruments in the 'Technology' sector
filters = {"sector": ["Technology"]}
tech_instruments = client.filter_instruments(filters=filters, match_all=True)
```

#### Filter Instruments by Classifications and Index

Filter instruments that belong to both specific classifications and a given index.

```python
# Example: Find 'Financial Services' instruments within the 'NIFTY NEXT 50' index
filters = {
    "basicIndustry": ["Housing Finance Company"],
    "sector": ["Financial Services"]
}
filtered_instruments = client.filter_instruments(
    index_identifier="NSE:NIFTY NEXT 50:26054",
    filters=filters,
    match_all=False
)
```

#### Filter Instruments by Derivatives

Filter instruments based on whether they have associated futures or options contracts.

```python
# Find all instruments that have options
optionable_stocks = client.filter_instruments_by_derivatives(hasOptions=True)

# Find all instruments that have futures
futures_stocks = client.filter_instruments_by_derivatives(hasFutures=True)

# Find all instruments that have both options and futures
fno_stocks = client.filter_instruments_by_derivatives(hasOptions=True, hasFutures=True)

# Find all instruments that have either options or futures
all_derivative_stocks = client.filter_instruments_by_derivatives()
```

### Instrument Screener

The SDK provides a powerful instrument screener to filter and sort instruments based on a wide range of criteria using a simple and expressive Domain Specific Language (DSL).

> **📋 Comprehensive Screener Documentation**: For detailed information about all available screener fields, practical use cases, and advanced filtering examples, see **[screener.md](screener.md)**.

#### `get_screener_fields()`

This method returns a list of all available filterable fields and their supported operations.

```python
# Get all available screener fields
fields = client.get_screener_fields()
print(json.dumps(fields, indent=2))
```

#### `run_screener(filters, sort=None, limit=None, as_of=None)`

This is the main method for the instrument screener. It accepts a dictionary with a `filters` object to define the screening criteria.

**Arguments:**

*   `filters` (dict, required): An object containing the filter conditions.
*   `sort` (list, optional): A list of objects to define the sort order.
*   `limit` (int, optional): The maximum number of results to return.

#### Filter DSL (Domain Specific Language)

The `filters` object uses a simple DSL to define the screening criteria.

##### Operators

| Operator  | Description              | Example                               |
| :-------- | :----------------------- | :------------------------------------ |
| `$eq`     | Equal to                 | `{ "sector": { "$eq": "Finance" } }`  |
| `$ne`     | Not equal to             | `{ "sector": { "$ne": "Finance" } }`  |
| `$gt`     | Greater than             | `{ "roe": { "$gt": 0.15 } }`          |
| `$gte`    | Greater than or equal to | `{ "roe": { "$gte": 0.15 } }`         |
| `$lt`     | Less than                | `{ "roe": { "$lt": 0.15 } }`          |
| `$lte`    | Less than or equal to    | `{ "roe": { "$lte": 0.15 } }`         |
| `$in`     | In a list of values    | `{ "sector": { "$in": ["Information Technology", "Finance"] } }` |
| `$nin`    | Not in a list of values| `{ "sector": { "$nin": ["Information Technology", "Finance"] } }` |
| `$like`   | Like (case-sensitive)    | `{ "companyName": { "$like": "%Bank%" } }` |
| `$nlike`  | Not like (case-sensitive)| `{ "companyName": { "$nlike": "%Bank%" } }` |
| `$ilike`  | Like (case-insensitive)  | `{ "companyName": { "$ilike": "%bank%" } }` |
| `$between`| Between two values       | `{ "roe": { "$between": [0.10, 0.20] } }` |

##### Logical Operators

*   `$and`: A list of filter conditions that must all be true.
*   `$or`: A list of filter conditions where at least one must be true.

#### Screener Examples

##### Basic Filters

1.  **Find all instruments in the 'Finance' sector.**
    ```python
    client.run_screener(filters={"sector": {"$eq": "Finance"}})
    ```

2.  **Find all instruments on the 'NSE' exchange.**
    ```python
    client.run_screener(filters={"exchange": {"$eq": "NSE"}})
    ```

3.  **Find all instruments with a Return on Equity (ROE) greater than 15%.**
    ```python
    client.run_screener(filters={"roe": {"$gt": 0.15}})
    ```

##### Set and Range Operators

4.  **Find all instruments in the 'Energy' or 'Healthcare' sectors.**
    ```python
    client.run_screener(filters={"sector": {"$in": ["Energy", "Healthcare"]}})
    ```

5.  **Find instruments with a PAT Margin between 5% and 10%.**
    ```python
    client.run_screener(filters={"patMargin": {"$between": [0.05, 0.10]}})
    ```

##### Pattern Matching

6.  **Find all instruments with 'Bank' in their name (case-insensitive).**
    ```python
    client.run_screener(filters={"companyName": {"$ilike": "%bank%"}})
    ```

##### Logical Combinations

7.  **Find instruments in the 'IT' sector with a ROE greater than 20%.**
    ```python
    client.run_screener(
        filters={
            "$and": [
                {"sector": {"$eq": "Information Technology"}},
                {"roe": {"$gt": 0.20}}
            ]
        }
    )
    ```

8.  **Complex Nested Query:** Find instruments in the 'Automobile' sector that have (a ROE > 18% AND a low Debt/Equity) OR have a high Asset Turnover.
    ```python
    client.run_screener(
        filters={
            "$and": [
                {"sector": {"$eq": "Automobile"}},
                {
                    "$or": [
                        {
                            "$and": [
                                {"roe": {"$gt": 0.18}},
                                {"debtEquity": {"$lt": 0.3}}
                            ]
                        },
                        {"assetTurnover": {"$gt": 1.5}}
                    ]
                }
            ]
        }
    )
    ```

##### Sort and Limit

9.  **Find the top 10 companies by highest ROE.**
    ```python
    client.run_screener(
        filters={},
        sort=[{"roe": -1}],
        limit=10
    )
    ```

10. **Find companies in the 'Pharmaceuticals' sector, sort them by the highest PAT margin, and then by the lowest Debt-to-Equity ratio.**
    ```python
    client.run_screener(
        filters={"sector": {"$eq": "Pharmaceuticals"}},
        sort=[
            {"patMargin": -1},
            {"debtEquity": 1}
        ]
    )
    ```

#### Get Historical OHLCV Data
## Overview

The `get_historical_ohlcv` method supports multiple time intervals for historical data retrieval, from 1-minute intraday data to monthly aggregated data.

## Supported Intervals

### Intraday Intervals
- `1m` - 1 minute
- `2m` - 2 minutes  
- `3m` - 3 minutes
- `5m` - 5 minutes
- `10m` - 10 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `45m` - 45 minutes
- `1h` - 1 hour

### Daily/Monthly Intervals
- `1d` - 1 day (default)
- `1M` - 1 month (last trading day of month)

## Date Format Requirements

### For Daily and Monthly Intervals (`1d`, `1M`)
- **Format**: `YYYY-MM-DD`
- **Example**: `"2024-01-15"`

### For Intraday Intervals (all minute/hour intervals)
- **Format**: `YYYY-MM-DD HH:MM:SS`
- **Example**: `"2024-01-15 09:30:00"`

**New Features in Historical Data API:**

- **Open Interest (`oi`)**: Now supported in the `ohlcv` parameter for futures instruments
- **Continuous Data**: The `continuous` parameter (for futures only) provides seamless data across multiple contract months when your date range spans multiple months

## Using Constants

The client provides constants for all intervals:

```python
from wiz_trader import WizzerClient

client = WizzerClient(...)

# Intraday intervals
client.INTERVAL_1_MINUTE     # "1m"
client.INTERVAL_2_MINUTES    # "2m"
client.INTERVAL_3_MINUTES    # "3m"
client.INTERVAL_5_MINUTES    # "5m"
client.INTERVAL_10_MINUTES   # "10m"
client.INTERVAL_15_MINUTES   # "15m"
client.INTERVAL_30_MINUTES   # "30m"
client.INTERVAL_45_MINUTES   # "45m"
client.INTERVAL_1_HOUR       # "1h"

# Daily/Monthly intervals
client.INTERVAL_1_DAY        # "1d"
client.INTERVAL_1_MONTH      # "1M"
```

## Usage Examples

### 1. Get 5-minute intraday data

```python
# Get 5-minute candles for a trading session
intraday_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN:3045"],
    start_date="2024-01-15 09:15:00",  # Market open
    end_date="2024-01-15 15:30:00",    # Market close
    ohlcv=["open", "high", "low", "close", "volume"],
    interval=client.INTERVAL_5_MINUTES
)

# Response will have date field as: "2024-01-15 09:15:00", "2024-01-15 09:20:00", etc.
```

### 2. Get 1-minute data for scalping

```python
# Get 1-minute data for the first hour of trading
scalping_data = client.get_historical_ohlcv(
    instruments=["NSE:RELIANCE:2885", "NSE:TCS:2953"],
    start_date="2024-01-15 09:15:00",
    end_date="2024-01-15 10:15:00",
    ohlcv=["open", "high", "low", "close", "volume"],
    interval=client.INTERVAL_1_MINUTE
)
```

### 3. Get hourly data for swing trading

```python
# Get hourly data for a week
hourly_data = client.get_historical_ohlcv(
    instruments=["NSE:NIFTY 50:26000"],
    start_date="2024-01-15 09:15:00",
    end_date="2024-01-19 15:30:00",
    ohlcv=["open", "high", "low", "close", "volume"],
    interval=client.INTERVAL_1_HOUR
)
```

### 4. Get daily data (traditional)

```python
# Get daily data for a month
daily_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN:3045"],
    start_date="2024-01-01",  # Note: No time component
    end_date="2024-01-31",
    ohlcv=["open", "high", "low", "close", "volume"],
    interval=client.INTERVAL_1_DAY
)

# Response will have date field as: "2024-01-01", "2024-01-02", etc.
```

### 5. Get monthly data for long-term analysis

```python
# Get monthly data for a year
monthly_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN:3045"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    ohlcv=["close", "volume"],
    interval=client.INTERVAL_1_MONTH
)

# Get futures data with open interest
futures_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN25MAYFUT:57515"],
    start_date="2024-01-01",
    end_date="2024-03-01",
    ohlcv=["open", "high", "low", "close", "volume", "oi"],  # Include open interest
    interval="1d"
)

# Get continuous futures data across multiple contract months
continuous_futures = client.get_historical_ohlcv(
    instruments=["NSE:SBIN25MAYFUT:57515"],
    start_date="2023-01-01",
    end_date="2024-12-31",
    ohlcv=["close", "oi"],
    interval="1d",
    continuous=True  # Get seamless data across contract months
)
```

## Response Structure

The response structure remains the same, but the `date` field format varies:

### For Daily/Monthly Intervals
```json
{
  "instrument": {
    "exchange": "NSE",
    "tradingSymbol": "SBIN",
    "exchangeToken": 3045,
    "identifier": "NSE:SBIN:3045"
  },
  "data": [
    {
      "date": "2024-01-15",  // YYYY-MM-DD format
      "open": 750.0,
      "high": 765.0,
      "low": 745.0,
      "close": 760.0,
      "volume": 1000000
    }
  ]
}
```

### For Intraday Intervals
```json
{
  "instrument": {
    "exchange": "NSE",
    "tradingSymbol": "SBIN",
    "exchangeToken": 3045,
    "identifier": "NSE:SBIN:3045"
  },
  "data": [
    {
      "date": "2024-01-15 09:15:00",  // YYYY-MM-DD HH:MM:SS format
      "open": 750.0,
      "high": 752.0,
      "low": 749.0,
      "close": 751.0,
      "volume": 50000
    }
  ]
}
```

## Advanced Usage Examples

### Multiple Timeframe Analysis

```python
def get_multi_timeframe_data(symbol, date):
    """Get data across multiple timeframes for comprehensive analysis"""
    
    # 1-minute data for entry/exit precision
    minute_data = client.get_historical_ohlcv(
        instruments=[symbol],
        start_date=f"{date} 09:15:00",
        end_date=f"{date} 15:30:00",
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=client.INTERVAL_1_MINUTE
    )
    
    # 5-minute data for short-term trends
    five_min_data = client.get_historical_ohlcv(
        instruments=[symbol],
        start_date=f"{date} 09:15:00",
        end_date=f"{date} 15:30:00",
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=client.INTERVAL_5_MINUTES
    )
    
    # 15-minute data for medium-term trends
    fifteen_min_data = client.get_historical_ohlcv(
        instruments=[symbol],
        start_date=f"{date} 09:15:00",
        end_date=f"{date} 15:30:00",
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=client.INTERVAL_15_MINUTES
    )
    
    # Hourly data for major trend
    hourly_data = client.get_historical_ohlcv(
        instruments=[symbol],
        start_date=f"{date} 09:15:00",
        end_date=f"{date} 15:30:00",
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=client.INTERVAL_1_HOUR
    )
    
    return {
        "1m": minute_data,
        "5m": five_min_data,
        "15m": fifteen_min_data,
        "1h": hourly_data
    }

# Usage
multi_data = get_multi_timeframe_data("NSE:SBIN:3045", "2024-01-15")
```

### Building OHLC Candlestick Data

```python
import pandas as pd
import matplotlib.pyplot as plt
from mplfinance import plot as mpf

def plot_candlestick_chart(symbol, start_date, end_date, interval):
    """Create a candlestick chart from historical data"""
    
    # Get historical data
    data = client.get_historical_ohlcv(
        instruments=[symbol],
        start_date=start_date,
        end_date=end_date,
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=interval
    )
    
    if not data or not data[0].get('data'):
        print("No data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data[0]['data'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Rename columns for mplfinance
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # Create candlestick chart
    mpf.plot(df, type='candle', volume=True, 
             title=f'{symbol} - {interval} Chart',
             style='charles')

# Plot 5-minute chart
plot_candlestick_chart(
    "NSE:SBIN:3045", 
    "2024-01-15 09:15:00", 
    "2024-01-15 15:30:00",
    client.INTERVAL_5_MINUTES
)
```

### Backtesting with Different Intervals

```python
def backtest_strategy_multiple_intervals(symbol, start_date, end_date):
    """Backtest a strategy across different intervals"""
    
    intervals = [
        (client.INTERVAL_5_MINUTES, "5m"),
        (client.INTERVAL_15_MINUTES, "15m"),
        (client.INTERVAL_30_MINUTES, "30m"),
        (client.INTERVAL_1_HOUR, "1h")
    ]
    
    results = {}
    
    for interval_code, interval_name in intervals:
        # For intraday intervals, use datetime format
        data = client.get_historical_ohlcv(
            instruments=[symbol],
            start_date=f"{start_date} 09:15:00",
            end_date=f"{end_date} 15:30:00",
            ohlcv=["open", "high", "low", "close", "volume"],
            interval=interval_code
        )
        
        if data and data[0].get('data'):
            df = pd.DataFrame(data[0]['data'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Simple moving average crossover strategy
            df['sma_10'] = df['close'].rolling(10).mean()
            df['sma_20'] = df['close'].rolling(20).mean()
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['sma_10'] > df['sma_20'], 'signal'] = 1
            df.loc[df['sma_10'] < df['sma_20'], 'signal'] = -1
            
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['signal'].shift(1) * df['returns']
            
            # Calculate total return
            total_return = (1 + df['strategy_returns']).prod() - 1
            
            results[interval_name] = {
                'total_return': total_return,
                'num_trades': df['signal'].diff().abs().sum() / 2,
                'num_candles': len(df)
            }
    
    return results

# Compare strategy performance across intervals
performance = backtest_strategy_multiple_intervals(
    "NSE:SBIN:3045",
    "2024-01-01",
    "2024-01-31"
)

for interval, metrics in performance.items():
    print(f"{interval}: Return={metrics['total_return']:.2%}, "
          f"Trades={metrics['num_trades']:.0f}, "
          f"Candles={metrics['num_candles']}")
```

## Error Handling

```python
try:
    data = client.get_historical_ohlcv(
        instruments=["NSE:SBIN:3045"],
        start_date="2024-01-15 09:15:00",
        end_date="2024-01-15 15:30:00",
        ohlcv=["open", "high", "low", "close", "volume"],
        interval=client.INTERVAL_5_MINUTES
    )
except ValueError as e:
    print(f"Date format error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Use appropriate intervals for your strategy**:
   - Scalping: 1m, 2m, 3m
   - Day trading: 5m, 15m, 30m
   - Swing trading: 1h, 1d
   - Position trading: 1d, 1M

2. **Be mindful of data volume**:
   - 1-minute data generates a lot of candles
   - Use shorter date ranges for minute-level data

3. **Validate date formats**:
   - The client will validate formats automatically
   - Use datetime strings consistently

4. **Consider market hours**:
   - For intraday data, use market hours: 09:15:00 to 15:30:00
   - Weekend dates won't have intraday data

5. **Cache data when possible**:
   - Historical data doesn't change
   - Store frequently used datasets locally

### Order Management

#### Place Regular Order

Place a regular order for a single instrument:

```python
# Simple market order
order_response = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_MARKET,
    product=client.PRODUCT_CNC
)
print(f"Order placed successfully: {order_response.get('orderId')}")

# Limit order with price
limit_order = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_LIMIT,
    product=client.PRODUCT_CNC,
    price=650.00
)

# Order with stop loss and target
sl_order = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    product=client.PRODUCT_CNC,
    stoploss=640.00,
    target=670.00
)
```

#### Modify Order

Modify an existing order:

```python
# Modify an order's price
modified_order = client.modify_order(
    order_id="order_01jpeyxtr4fb69fx740my3115c",
    price=655.00
)

# Modify an order's quantity
modified_order = client.modify_order(
    order_id="order_01jpeyxtr4fb69fx740my3115c",
    qty=15
)
```

#### Cancel Order

Cancel an existing order:

```python
# Cancel an order
cancelled_order = client.cancel_order(order_id="order_01jpeyxtr4fb69fx740my3115c")
```

#### Get Order Details

Fetch details of a specific order:

```python
# Get order details
order_details = client.get_order(order_id="order_01jpeyxtr4fb69fx740my3115c")
print(f"Order status: {order_details.get('status')}")
```

### Portfolio Management

#### Get Positions

Fetch your current positions:

```python
# Get all positions
all_positions = client.get_positions()
print(f"Found {len(all_positions)} positions")

# Get only open positions
open_positions = client.get_open_positions()
print(f"Found {len(open_positions)} open positions")

# Get only closed positions
closed_positions = client.get_closed_positions()
print(f"Found {len(closed_positions)} closed positions")
```

#### Get Holdings

Fetch your holdings:

```python
# Get holdings
holdings = client.get_holdings()
print(f"Found {len(holdings)} holdings")

# Get holdings for a specific portfolio
portfolio_holdings = client.get_holdings(portfolios="my_portfolio")
```

#### Exit Positions

Exit all positions or positions for a specific strategy:

```python
# Exit all positions
exit_response = client.exit_all_positions()
print(f"Successfully exited {exit_response.get('success', 0)} positions")

# Exit positions for a specific strategy
strategy_exit = client.exit_strategy_positions(strategy_id="str_01jbxszcjdegz8zt3h95g8c1d9")
```

### Basket Management

#### Create Basket

Create a new basket of instruments:

```python
# Create a basic basket with two stocks
basket_response = client.create_basket(
    name="My Basket",
    instruments=[
        {
            "shares": 10,
            "weightage": 50,
            "instrument": {
                "exchange": "NSE",
                "identifier": "NSE:SBIN:3045",
                "orderIndex": 1,
                "exchangeToken": 3045,
                "tradingSymbol": "SBIN"
            }
        },
        {
            "shares": 15,
            "weightage": 50,
            "instrument": {
                "exchange": "NSE",
                "identifier": "NSE:ICICIBANK:4963",
                "orderIndex": 2,
                "exchangeToken": 4963,
                "tradingSymbol": "ICICIBANK"
            }
        }
    ],
    weightage_scheme="equi_weighted",
    capital={"minValue": 50000, "actualValue": 50000},
    instrument_types=["EQLC"]
)
basket_id = basket_response.get('id')
```

#### Get Baskets

Fetch existing baskets:

```python
# Get all baskets
baskets = client.get_baskets()
print(f"Found {len(baskets)} baskets")

# Get a specific basket by ID
basket = client.get_basket(basket_id="bk_01jpf2d57ae96bez63me7p6g9k")

# Get instruments in a basket
basket_instruments = client.get_basket_instruments(basket_id="bk_01jpf2d57ae96bez63me7p6g9k")
```

#### Place Basket Order

Place an order for an entire basket:

```python
# Place a basket order
basket_order = client.place_basket_order(
    trading_symbol="/MY_BASKET",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=1,
    price=50000.00,
    product=client.PRODUCT_CNC
)
```

#### Exit Basket Order

Exit a basket position:

```python
# Exit a basket position
exit_order = client.place_basket_exit_order(
    trading_symbol="/MY_BASKET",
    exchange=client.EXCHANGE_WZR,
    transaction_type=client.TRANSACTION_TYPE_SELL,
    quantity=1,
    exchange_token=1741872632
)
```

#### Rebalance Basket

#### Available Weightage Schemes

When creating or rebalancing baskets, you can choose from several weightage schemes:

- **`WEIGHTAGE_SCHEME_EQUI_WEIGHTED`**: Equal weightage for all instruments
- **`WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED`**: Weighted by quantity
- **`WEIGHTAGE_SCHEME_PRICE_WEIGHTED`**: Weighted by price
- **`WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED`**: Weighted by market capitalization
- **`WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED`**: Weighted by float-adjusted market cap
- **`WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED`**: Weighted by fundamental metrics
- **`WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED`**: Custom weightage scheme

Rebalance a basket with new instruments:

```python
# Rebalance a basket
rebalance_response = client.rebalance_basket(
    trading_symbol="/MY_BASKET",
    instruments=["NSE:SBIN:3045", "NSE:HDFCBANK:1333", "NSE:TCS:2953"]
)

# Full Rebalance with market cap weighting & execution of all orders at market price
client.rebalance_basket(
    trading_symbol="/MY_BASKET",
    instruments=["NSE:SBIN:3045", "NSE:HDFCBANK:1333"],
    execution_policy=client.REBALANCE_FULL,
    order_type=client.ORDER_TYPE_MARKET,
    weightage_scheme=client.WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED
)

# Entry-only rebalance with price weighting
client.rebalance_basket(
    trading_symbol="/MY_BASKET",
    instruments=["NSE:SBIN:3045", "NSE:HDFCBANK:1333"],
    execution_policy=client.REBALANCE_ENTRY_ONLY,
    weightage_scheme=client.WEIGHTAGE_SCHEME_EQUI_WEIGHTED
)
```

### Instrument Management
## Instrument Data APIs

### Get Instrument Metrics

Fetch detailed information and metrics for specific instruments:

```python
# Get metrics for a single equity instrument
equity_info = client.get_instrument_metrics(identifiers=["NSE:SBIN:3045"])
print(f"SBIN Last Price: {equity_info[0]['ltp']}")
print(f"SBIN 52-week High: {equity_info[0]['week52High']}")

# Get metrics for multiple instruments of different types
instruments_info = client.get_instrument_metrics(
    identifiers=[
        "NSE:AARTIIND:7",              # Equity
        "NSE:NIFTY26DEC11000CE:61009", # Option
        "NSE:SBIN25MAYFUT:57515"       # Future
    ]
)

# Print detailed information for each instrument
for instrument in instruments_info:
    print(f"{instrument['tradingSymbol']} ({instrument['instrumentType']}):")
    print(f"  LTP: {instrument['ltp']}")
    print(f"  Exchange: {instrument['exchange']}")
    print(f"  Segment: {instrument['segment']}")
    if instrument.get('bhavcopy'):
        print(f"  Volume: {instrument['bhavcopy']['volume']}")
        print(f"  OHLC: {instrument['bhavcopy']['open']}/{instrument['bhavcopy']['high']}/"
              f"{instrument['bhavcopy']['low']}/{instrument['bhavcopy']['close']}")
```

#### Response Structure for Instrument Metrics

The `get_instrument_metrics` method returns a list of dictionaries, each with the following structure:

```python
[
    {
        # Instrument name if available
        "name": "",
        
        # Trading symbol
        "tradingSymbol": "AARTIIND",
        
        # Exchange code
        "exchange": "NSE",
        
        # Bid price if available
        "bid": 0,
        
        # Size of total bids at best bid price
        "bidSize": 0,
        
        # Ask (offer) price
        "ask": 0,
        
        # Size of total asks at best ask price
        "askSize": 0,
        
        # Last traded price
        "ltp": 450.05,
        
        # Trading volume
        "volume": 0,
        
        # Lot size for the instrument
        "lotSize": 1,
        
        # Mid price ((bid+ask)/2)
        "mid": 0,
        
        # Market capitalization (for equities)
        "marketCap": 0,
        
        # Dividend yield percentage (for equities)
        "dividendYield": 0,
        
        # Last dividend date
        "dividendDate": "",
        
        # Daily Open-High-Low-Close values
        "ohlc": {
            "open": 0,
            "high": 0,
            "low": 0,
            "close": 0
        },
        
        # Industry classification (for equities)
        "industry": "",
        
        # Sector classification (for equities)
        "sector": "",
        
        # Relevant indicators for underlying assets (for derivatives)
        "underlyingIndicators": "",
        
        # Net change in price
        "netChange": 0,
        
        # Net change in percentage
        "netChangePercentage": 0,
        
        # Beta value (for equities)
        "beta": 0,
        
        # Liquidity rating
        "liquidityRating": 0,
        
        # Implied volatility metrics (for options)
        "iv": {
            "index": 0,
            "indexRank": 0,
            "percentile": 0,
            "change5Days": 0,
            "change30Days": 0,
            "ivHvChange30Days": 0
        },
        
        # Historical volatility metrics
        "hv": {
            "change30Days": 0,
            "change60Days": 0,
            "change90Days": 0
        },
        
        # Minimum price movement
        "tickSize": 0.05,
        
        # Previous day's trading summary
        "bhavcopy": {
            "open": 458.4,
            "high": 470.9,
            "low": 440.75,
            "close": 448.55,
            "volume": 3544523,
            "turnover": 1632822505.15,
            "totalTrades": 59999
        },
        
        # Exchange token identifier
        "exchangeToken": 7,
        
        # Market segment
        "segment": "NSECM",
        
        # Whether the instrument is actively traded
        "isTraded": false,
        
        # Complete instrument identifier
        "identifier": "NSE:AARTIIND:7",
        
        # Instrument type code
        "instrumentType": "EQLC",
        
        # Option type (for options) - CE or PE
        "optionType": "",
        
        # Expiry date (for derivatives)
        "expiry": "",
        
        # International Securities Identification Number
        "isin": "INE769A01020",
        
        # Margin requirement percentage
        "margin": 19.43,
        
        # 52-week high price
        "week52High": 765.5,
        
        # 52-week low price
        "week52Low": 344.2,
        
        # Maximum allowed trade volume
        "maxTradeVolume": 2147483647,
        
        # Price band limits
        "priceBand": {
            "high": 493.4,
            "low": 403.7,
            "creditRating": {
                "lower": 403.7,
                "higher": 493.4
            }
        }
    },
    # Additional instruments...
]
```

Note that certain fields may have zero or empty values if the data is not available from the exchange or if it's not applicable to that instrument type.

### Options Chain

#### Get Option Expiry List

Fetch available expiry dates for an instrument's options:

```python
# For a stock
expiry_list = client.get_option_expiry_list("NSE:SBIN:3045")

# For an index
nifty_expiry = client.get_option_expiry_list("NSE:NIFTY 50:26000")

# Print all available expiry dates
for expiry in expiry_list.get('expiryList', []):
    print(f"{expiry['date']} - {expiry['contract']} " +
          f"(Futures: {'Yes' if expiry['isFuturesExpiry'] else 'No'}, " +
          f"Options: {'Yes' if expiry['isOptionsExpiry'] else 'No'})")
```

#### Response Structure

The response is a JSON object with the following structure:

```json
{
  "exchange": "NSE",                // Exchange of the instrument
  "tradingSymbol": "SBIN",          // Trading symbol
  "exchangeToken": 3045,            // Exchange token
  "identifier": "NSE:SBIN:3045",    // Full identifier
  "expiryList": [                   // Array of expiry objects
    {
      "date": "2025-05-29",         // Expiry date in YYYY-MM-DD format
      "contract": "near_month",     // Contract type (see below)
      "isFuturesExpiry": true,      // Whether futures expire on this date
      "isOptionsExpiry": true       // Whether options expire on this date
    },
    // More expiry objects...
  ]
}
```

For index options like NIFTY, the response will typically include more expiry dates, including weekly options and longer-dated quarterly options.

The `expiryList` array contains objects with the following fields:
- `date`: The expiry date in YYYY-MM-DD format
- `contract`: The type of contract (e.g., "near_month", "current_weekly")
- `isFuturesExpiry`: Boolean indicating if futures expire on this date
- `isOptionsExpiry`: Boolean indicating if options expire on this date

#### Contract Types

Each expiry date is categorized with a `contract` field that indicates the type of expiry. The possible contract types are:

1. **Weekly Expiries (Thursdays/Wednesdays)**
   - `current_weekly`: The first non-expiry Thursday of the current week

2. **Monthly Expiries (last Wed/Thu of month)**
   - `near_month`: Last Wed/Thu of this month (current month)
   - `mid_month`: Last Wed/Thu of next month
   - `far_month`: Last Wed/Thu of month after next

3. **Weekly Ordinals Within Current Month**
   - `first_weekly`: 1st non-expiry Thursday of current month
   - `second_weekly`: 2nd non-expiry Thursday
   - `third_weekly`: 3rd non-expiry Thursday
   - `fourth_weekly`: 4th non-expiry Thursday
   - `fifth_weekly`: 5th non-expiry Thursday (rare)

4. **Weekly Ordinals in Mid-Month Slot (next month's week-trade dates)**
   - `first_weekly_mid_month`: 1st Thursday of next month
   - `second_weekly_mid_month`: 2nd Thursday of next month
   - `third_weekly_mid_month`: 3rd Thursday of next month
   - `fourth_weekly_mid_month`: 4th Thursday of next month
   - `fifth_weekly_mid_month`: 5th Thursday of next month (rare)

5. **Weekly Ordinals in Far-Month Slot (month-after-next)**
   - `first_weekly_far_month`: 1st Thursday of month after next
   - `second_weekly_far_month`: 2nd Thursday of month after next
   - `third_weekly_far_month`: 3rd Thursday of month after next
   - `fourth_weekly_far_month`: 4th Thursday of month after next
   - `fifth_weekly_far_month`: 5th Thursday of month after next (rare)

6. **Quarterly Expiries (last-Thu of Mar/Jun/Sep/Dec)**
   - `first_quarter`: Last Thu of March (Q1)
   - `second_quarter`: Last Thu of June (Q2)
   - `third_quarter`: Last Thu of September (Q3)
   - `fourth_quarter`: Last Thu of December (Q4)

7. **Half-Yearly Expiries**
   - `first_half_yearly`: Last Thu of June (H1)
   - `second_half_yearly`: Last Thu of December (H2)

8. **Year-Plus-N Quarterly/Half-Yearly (N = years ahead)**
   - For quarterly options in future years:
     - `first_quarter_1`: Q1 (March) of next year
     - `second_quarter_1`: Q2 (June) of next year
     - `third_quarter_1`: Q3 (September) of next year
     - `fourth_quarter_1`: Q4 (December) of next year
   - For half-yearly options in future years:
     - `first_half_yearly_1`: H1 (June) of next year
     - `second_half_yearly_1`: H2 (December) of next year
   - This pattern continues with `_2`, `_3`, and `_4` suffixes for up to 4 years ahead

9. **Special Case**
   - `none`: No matching expiry category

### Get Options Chain

The Options Chain API provides detailed information about available option contracts for a specified instrument, including strike prices, premiums, and option Greeks.

#### Constants

The SDK provides constants for option types, moneyness, and expiry preferences to make your code more readable and type-safe:

**Option Types:**
```python
client.OPTION_TYPE_CE  # Call option
client.OPTION_TYPE_PE  # Put option
```

**Moneyness Types:**
```python
client.MONEYNESS_ATM  # At-the-money
client.MONEYNESS_ITM  # In-the-money
client.MONEYNESS_OTM  # Out-of-the-money
```

**Expiry Preferences:**
```python
# Common expiry preferences
client.EXPIRY_CURRENT_WEEKLY  # Current week's expiry
client.EXPIRY_NEAR_MONTH      # Current month's expiry
client.EXPIRY_MID_MONTH       # Next month's expiry
client.EXPIRY_FAR_MONTH       # Month after next expiry

# Many more constants available for weekly, monthly, 
# quarterly, and yearly expiries
```

#### Get Option Chain

Fetch the option chain for a specific instrument using either an exact expiry date or a expiry preference:

```python
# Get ATM call options for SBIN with specific expiry date
options = client.get_option_chain(
    identifier="NSE:SBIN:3045",
    expiry_date="2025-05-30",
    option_type=[client.OPTION_TYPE_CE],  # Call options
    moneyness=[client.MONEYNESS_ATM]      # At-the-money
)
print(f"Found {len(options['strikes'])} strikes")
print(f"Current underlying price: {options['underlyingPrice']}")

# Get both call and put options with expiry preference
all_options = client.get_option_chain(
    identifier="NSE:NIFTY 50:26000",
    expiry_preference=client.EXPIRY_CURRENT_WEEKLY,  # Current week's expiry
    option_type=[client.OPTION_TYPE_CE, client.OPTION_TYPE_PE],  # Both calls and puts
    moneyness=[client.MONEYNESS_ATM, client.MONEYNESS_ITM, client.MONEYNESS_OTM]  # All moneyness types
)

# Print option chain details
print(f"Resolved expiry: {all_options['resolvedExpiry']}")
print(f"Underlying price: {all_options['underlyingPrice']}")
print(f"Future price: {all_options['futurePrice']}")

# Process options data
for strike in all_options['strikes']:
    print(f"{strike['tradingSymbol']} ({strike['moneyness']}): {strike['ltp']}")
```

#### Response Structure

The `get_option_chain` method returns a dictionary with the following structure:

```python
{
    # The actual expiry date that was resolved (may differ slightly from requested date)
    "resolvedExpiry": "2025-05-29", 
    
    # Current price of the underlying stock/index
    "underlyingPrice": 792.1,
    
    # Price of the corresponding futures contract (if applicable)
    "futurePrice": 793.35,
    
    # Array of available strike prices matching the query criteria
    "strikes": [
        {
            # The strike price of the option
            "strikePrice": 790,
            
            # Option type: "CE" (Call) or "PE" (Put)
            "optionType": "CE",
            
            # Exchange token for the option contract
            "exchangeToken": 136169,
            
            # Exchange where the option is traded
            "exchange": "NSE",
            
            # Trading symbol for the option contract
            "tradingSymbol": "SBIN25MAY790CE",
            
            # Moneyness classification: "ATM", "ITM", or "OTM"
            "moneyness": "ATM",
            
            # Expiry date of the option contract
            "expiry": "2025-05-29",
            
            # Last traded price of the option
            "ltp": 15.1,
            
            # Option Greeks and metrics (if available)
            "metrics": {
                # Option premium
                "premium": 0,
                
                # Open interest
                "oi": 0,
                
                # Implied volatility
                "iv": 0,
                
                # Delta - rate of change of option price with respect to underlying
                "delta": 0,
                
                # Gamma - rate of change of delta with respect to underlying
                "gamma": 0,
                
                # Theta - rate of change of option price with respect to time
                "theta": 0,
                
                # Vega - rate of change of option price with respect to volatility
                "vega": 0,
                
                # Rho - rate of change of option price with respect to interest rate
                "rho": 0
            }
        },
        # Additional strikes...
    ]
}
```

#### Advanced Examples

##### Finding a Straddle/Strangle

```python
def find_straddle_strangle(identifier, expiry):
    """Find and analyze straddle/strangle opportunities."""
    # Get the option chain
    option_chain = client.get_option_chain(
        identifier=identifier,
        expiry_date=expiry,
        option_type=[client.OPTION_TYPE_CE, client.OPTION_TYPE_PE],
        moneyness=[client.MONEYNESS_ATM]
    )
    
    # Find ATM call and put
    calls = [s for s in option_chain["strikes"] if s["optionType"] == "CE"]
    puts = [s for s in option_chain["strikes"] if s["optionType"] == "PE"]
    
    if not calls or not puts:
        print("Couldn't find both call and put options")
        return
    
    # For a straddle, we want the same strike price
    atm_strike = calls[0]["strikePrice"]
    atm_call = calls[0]
    atm_put = next((p for p in puts if p["strikePrice"] == atm_strike), None)
    
    if atm_call and atm_put:
        call_premium = atm_call["ltp"]
        put_premium = atm_put["ltp"]
        total_premium = call_premium + put_premium
        
        print(f"ATM Straddle Analysis for {identifier} (Expiry: {expiry})")
        print(f"Underlying Price: {option_chain['underlyingPrice']}")
        print(f"ATM Strike: {atm_strike}")
        print(f"Call Premium: {call_premium}")
        print(f"Put Premium: {put_premium}")
        print(f"Total Premium: {total_premium}")
        print(f"Breakeven Upper: {atm_strike + total_premium}")
        print(f"Breakeven Lower: {atm_strike - total_premium}")
        
        # Calculate the percentage move needed for breakeven
        pct_move = (total_premium / option_chain['underlyingPrice']) * 100
        print(f"Required % Move for Breakeven: {pct_move:.2f}%")
    
    # For a strangle, we want OTM call and put
    otm_options = client.get_option_chain(
        identifier=identifier,
        expiry_date=expiry,
        option_type=[client.OPTION_TYPE_CE, client.OPTION_TYPE_PE],
        moneyness=[client.MONEYNESS_OTM]
    )
    
    otm_calls = sorted([s for s in otm_options["strikes"] if s["optionType"] == "CE"], 
                       key=lambda x: x["strikePrice"])
    otm_puts = sorted([s for s in otm_options["strikes"] if s["optionType"] == "PE"], 
                      key=lambda x: x["strikePrice"], reverse=True)
    
    if otm_calls and otm_puts:
        otm_call = otm_calls[0]  # First OTM call
        otm_put = otm_puts[0]    # First OTM put
        
        call_premium = otm_call["ltp"]
        put_premium = otm_put["ltp"]
        total_premium = call_premium + put_premium
        
        print(f"\nOTM Strangle Analysis for {identifier} (Expiry: {expiry})")
        print(f"Call Strike: {otm_call['strikePrice']} (Premium: {call_premium})")
        print(f"Put Strike: {otm_put['strikePrice']} (Premium: {put_premium})")
        print(f"Total Premium: {total_premium}")
        print(f"Breakeven Upper: {otm_call['strikePrice'] + total_premium}")
        print(f"Breakeven Lower: {otm_put['strikePrice'] - total_premium}")
    
    return option_chain

# Example usage
find_straddle_strangle("NSE:SBIN:3045", "2025-05-30")
```

##### Option Chain Visualization

```python
def visualize_option_chain(identifier, expiry):
    """Create a visualization of the option chain."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Get the option chain
    option_chain = client.get_option_chain(
        identifier=identifier,
        expiry_date=expiry,
        option_type=[client.OPTION_TYPE_CE, client.OPTION_TYPE_PE],
        moneyness=[client.MONEYNESS_ATM, client.MONEYNESS_ITM, client.MONEYNESS_OTM]
    )
    
    # Extract data
    underlying_price = option_chain["underlyingPrice"]
    
    # Separate calls and puts
    calls = sorted([s for s in option_chain["strikes"] if s["optionType"] == "CE"], 
                  key=lambda x: x["strikePrice"])
    puts = sorted([s for s in option_chain["strikes"] if s["optionType"] == "PE"], 
                 key=lambda x: x["strikePrice"])
    
    # Extract strike prices and premiums
    call_strikes = [c["strikePrice"] for c in calls]
    call_premiums = [c["ltp"] for c in calls]
    
    put_strikes = [p["strikePrice"] for p in puts]
    put_premiums = [p["ltp"] for p in puts]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot calls and puts
    ax.plot(call_strikes, call_premiums, 'b-', marker='o', label='Calls')
    ax.plot(put_strikes, put_premiums, 'r-', marker='o', label='Puts')
    
    # Add vertical line for current price
    ax.axvline(x=underlying_price, color='g', linestyle='--', 
               label=f'Current Price ({underlying_price})')
    
    # Add labels and title
    ax.set_xlabel('Strike Price')
    ax.set_ylabel('Premium')
    ax.set_title(f'Option Chain for {identifier} (Expiry: {expiry})')
    ax.legend()
    ax.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return option_chain

# Example usage
visualize_option_chain("NSE:NIFTY 50:26000", "2025-05-30")
```

#### Get Futures List

Fetch available futures contracts for an instrument:

```python
# Get futures for an equity stock
sbin_futures = client.get_futures_list("NSE:SBIN:3045")
print(f"Found {len(sbin_futures)} futures contracts for SBIN")
for future in sbin_futures:
    print(f"{future['tradingSymbol']} - Expiry: {future['expiry']} ({future['contract']})")

# Get futures for an index
nifty_futures = client.get_futures_list("NSE:NIFTY 50:26000")
print(f"Found {len(nifty_futures)} futures contracts for NIFTY 50")
for future in nifty_futures:
    print(f"{future['tradingSymbol']} - Expiry: {future['expiry']} ({future['contract']})")
```

#### Response Structure for Futures List

The `get_futures_list` method returns a list of dictionaries, each representing a futures contract:

```python
[
    {
        # Exchange where the future is traded
        "exchange": "NSE",
        
        # Trading symbol of the futures contract
        "tradingSymbol": "SBIN25MAYFUT",
        
        # Exchange token for the futures contract
        "exchangeToken": 57515,
        
        # Complete identifier for the futures contract
        "identifier": "NSE:SBIN25MAYFUT:57515",
        
        # Expiry date in YYYY-MM-DD format
        "expiry": "2025-05-29",
        
        # Contract type (near_month, mid_month, far_month)
        "contract": "near_month"
    },
    # Additional futures contracts...
]
```

The `contract` field indicates the type of futures contract:
- **`near_month`**: Current month's futures contract
- **`mid_month`**: Next month's futures contract  
- **`far_month`**: Month after next futures contract

### Analytics API

The Analytics API provides comprehensive financial analysis and market data tools for stocks and indices. It includes fundamentals analysis, valuation metrics, returns calculation, market data, ownership analysis, metrics, and macro data.

#### Fundamentals Analysis

Get key financial metrics and ratios for stocks:

```python
# Net Profit Margin
margin = client.get_net_profit_margin("INFY", period="quarterly", quarter="Q1FY24")
print(f"Net Profit Margin: {margin['netProfitMargin']}%")

# Return on Equity (ROE)
roe = client.get_roe("TCS", period="annual", consolidated=True)
print(f"ROE: {roe['roe']}%")

# Return on Assets (ROA)
roa = client.get_roa("WIPRO", period="annual", consolidated=True)
print(f"ROA: {roa['roa']}%")

# EBIT Margin
ebit = client.get_ebit_margin("INFY", period="annual", consolidated=True)
print(f"EBIT Margin: {ebit['ebitMargin']}%")

# Operating Cash Flow to Net Profit Ratio
ocf_ratio = client.get_ocf_netprofit_ratio("TCS", period="annual")
print(f"OCF/Net Profit Ratio: {ocf_ratio['ocfNetprofitRatio']}")

# EPS CAGR (Compound Annual Growth Rate)
eps_cagr = client.get_eps_cagr("INFY", start_year=2019, end_year=2023)
print(f"EPS CAGR (2019-2023): {eps_cagr['epsCagr']}%")

# Book to Market Ratio
btm = client.get_book_to_market("NSE:INFY", as_of="2024-03-31")
print(f"Book to Market: {btm['bookToMarket']}")

# Market Cap to Sales Ratio
mts = client.get_marketcap_to_sales("RELIANCE", as_of="2024-03-31")
print(f"Market Cap to Sales: {mts['marketcapToSales']}")

# Cash to Market Cap Ratio
ctm = client.get_cash_to_marketcap("TCS", as_of="2024-03-31")
print(f"Cash to Market Cap: {ctm['cashToMarketcap']}")
```

#### Valuation Metrics

Get key valuation ratios:

```python
# Price to Earnings (P/E) Ratio
pe = client.get_pe_ratio("RELIANCE", date="2024-12-31", ttm=False, consolidated=True)
print(f"P/E Ratio: {pe['peRatio']}")

# Price to Book (P/B) Ratio
pb = client.get_pb_ratio("HDFC", date="2024-12-31", consolidated=True)
print(f"P/B Ratio: {pb['pbRatio']}")

# Enterprise Value to EBITDA
ev_ebitda = client.get_ev_ebitda("TCS", date="2024-06-30", ttm=False, consolidated=True)
print(f"EV/EBITDA: {ev_ebitda['evEbitda']}")

# Free Cash Flow Yield
fcf_yield = client.get_fcf_yield("HDFCAMC", date="2024-06-30", ttm=False, consolidated=True)
print(f"FCF Yield: {fcf_yield['fcfYield']}%")
```

#### Returns Analysis

Calculate returns over different time periods:

```python
# CAGR (Compound Annual Growth Rate)
cagr_data = client.get_cagr(
    symbol="RELIANCE",
    start_date="2020-01-01",
    end_date="2024-01-01",
    adjusted=True
)
print(f"Annual CAGR: {cagr_data['cagr']}%")
print(f"Start Price: ₹{cagr_data['startPrice']}")
print(f"End Price: ₹{cagr_data['endPrice']}")

# Quarterly Returns
quarterly_returns = client.get_quarterly_returns(
    symbol="INFY",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjusted=True
)

# Monthly Returns
monthly_returns = client.get_monthly_returns(
    symbol="TCS",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjusted=True
)
```

#### Market Data

Get historical price data and market capitalization:

```python
# Daily OHLCV Data
ohlcv_data = client.get_analytics_ohlcv_daily(
    symbol="RELIANCE",
    start_date="2024-01-01",
    end_date="2024-01-31",
    adjusted=True
)
print(f"Retrieved {len(ohlcv_data['data'])} days of data")

# Historical Prices (same as OHLCV)
historical_prices = client.get_analytics_historical_prices(
    symbol="SBIN",
    start_date="2024-01-01",
    end_date="2024-01-31",
    adjusted=True
)

# Free-Float Market Capitalization
free_float_mcap = client.get_free_float_market_cap("RELIANCE", date="2024-07-31")
print(f"Free-Float Market Cap: ₹{free_float_mcap['freeFloatMarketCap']} Crores")
print(f"Total Market Cap: ₹{free_float_mcap['marketCap']} Crores")
print(f"Promoter Holding: {free_float_mcap['promoterHoldingPercent']}%")

# Index OHLC Daily Data
index_data = client.get_index_ohlc_daily(
    symbol="NIFTY50",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(f"Retrieved {len(index_data['data'])} days of index data")
```

#### Ownership Analysis

Analyze institutional holdings and their changes:

```python
# FII and DII Holdings
fii_dii = client.get_fii_dii_holdings("RELIANCE", quarter="Q4FY23")
print(f"FII Holdings: {fii_dii['fiiPercent']}%")
print(f"DII Holdings: {fii_dii['diiPercent']}%")

# FII Change from Previous Quarter
fii_change = client.get_fii_change("INFY")
print(f"FII Change: {fii_change['fiiChange']}%")
print(f"Current FII: {fii_change['currentFii']}%")
print(f"Previous FII: {fii_change['previousFii']}%")

# DII Change from Previous Quarter
dii_change = client.get_dii_change("INFY")
print(f"DII Change: {dii_change['diiChange']}%")
print(f"Current DII: {dii_change['currentDii']}%")
print(f"Previous DII: {dii_change['previousDii']}%")
```

#### Metrics (Risk-Adjusted Performance)

Get risk-adjusted performance metrics:

```python
# Sortino Ratio
sortino = client.get_sortino_ratio(
    symbol="HDFCBANK",
    start_date="2024-01-01",
    end_date="2024-12-31",
    rf=0.065,
    interval="daily"
)
print(f"Sortino Ratio: {sortino['sortinoRatio']}")
print(f"Annualized Return: {sortino['annualizedReturn']}")
print(f"Downside Deviation: {sortino['downsideDeviation']}")

# Upside Capture Ratio
upside_capture = client.get_upside_capture(
    symbol="ICICIBANK",
    benchmark_symbol="NIFTY50",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(f"Upside Capture Ratio: {upside_capture['upsideCaptureRatio']}%")
print(f"Periods Analyzed: {upside_capture['periodsAnalyzed']}")
```

#### Macro Economic Data

Get macroeconomic indicators:

```python
# Risk-Free Rate
risk_free_rate = client.get_risk_free_rate(
    start_date="2024-01-01",
    end_date="2024-12-31",
    tenor="10Y",
    country="IN",
    method="average"
)
print(f"Risk-Free Rate (10Y): {risk_free_rate['riskFreeRate']}")
print(f"Country: {risk_free_rate['country']}")
print(f"Source: {risk_free_rate['source']}")
```

#### Risk Analysis

Get risk metrics and volatility measures:

```python
# Maximum Drawdown (Peak-to-trough decline)
max_drawdown = client.get_max_drawdown(
    symbol="RELIANCE",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(f"Maximum Drawdown: {max_drawdown['maxDrawdown']}%")
print(f"Drawdown Start Date: {max_drawdown['drawdownStartDate']}")
print(f"Drawdown End Date: {max_drawdown['drawdownEndDate']}")
print(f"Days in Drawdown: {max_drawdown['daysInDrawdown']}")

# Returns Volatility (Standard Deviation)
volatility = client.get_returns_volatility(
    symbol="NIFTY50",
    start_date="2024-01-01",
    end_date="2024-12-31",
    interval="daily"
)
print(f"Volatility (Daily): {volatility['volatility']}%")
print(f"Annualized Volatility: {volatility['annualizedVolatility']}%")
print(f"Mean Return: {volatility['meanReturn']}%")
```

#### Sector Classification

Get comprehensive sector and industry classification:

```python
# Complete Sector Classification Data
sector_data = client.get_sector_classification("RELIANCE")
print(f"Company: {sector_data['companyName']}")
print(f"Sector: {sector_data['sector']}")
print(f"Industry: {sector_data['industry']}")
print(f"Sub-Industry: {sector_data['subIndustry']}")
print(f"GICS Sector Code: {sector_data['gicsSectorCode']}")
print(f"Industry Group: {sector_data['industryGroup']}")
print(f"Market Cap Tier: {sector_data['marketCapTier']}")
```

#### Leverage Analysis

Analyze financial leverage and debt ratios:

```python
# Debt-to-Equity Ratio
debt_equity = client.get_debt_equity_ratio(
    symbol="RELIANCE",
    period="annual",
    consolidated=True
)
print(f"Debt-to-Equity Ratio: {debt_equity['debtEquityRatio']}")
print(f"Total Debt: ₹{debt_equity['totalDebt']} Crores")
print(f"Total Equity: ₹{debt_equity['totalEquity']} Crores")
print(f"Period: {debt_equity['period']}")
print(f"Data Date: {debt_equity['dataDate']}")
```

#### Advanced Returns Analysis

Calculate compound annual growth rates:

```python
# CAGR (Compound Annual Growth Rate)
cagr = client.get_cagr(
    symbol="TCS",
    start_date="2020-01-01",
    end_date="2024-01-01",
    adjusted=True
)
print(f"CAGR (4-Year): {cagr['cagr']}%")
print(f"Total Return: {cagr['totalReturn']}%")
print(f"Start Price: ₹{cagr['startPrice']}")
print(f"End Price: ₹{cagr['endPrice']}")
print(f"Years: {cagr['years']}")
```

#### Complete Analytics Example

Here's a comprehensive example that combines multiple analytics features:

```python
from wiz_trader import WizzerClient

def analyze_stock(symbol):
    client = WizzerClient(
        base_url="https://api-url.in",
        token="your-jwt-token"
    )
    
    print(f"=== Analysis for {symbol} ===\n")
    
    # Fundamentals
    print("[FUNDAMENTALS]:")
    try:
        margin = client.get_net_profit_margin(symbol)
        print(f"  Net Profit Margin: {margin.get('netProfitMargin', 'N/A')}%")
        
        roe = client.get_roe(symbol)
        print(f"  ROE: {roe.get('roe', 'N/A')}%")
        
        roa = client.get_roa(symbol)
        print(f"  ROA: {roa.get('roa', 'N/A')}%")
        
        eps_cagr = client.get_eps_cagr(symbol, start_year=2019, end_year=2023)
        print(f"  EPS CAGR (5Y): {eps_cagr.get('epsCagr', 'N/A')}%")
    except Exception as e:
        print(f"  Error fetching fundamentals: {e}")
    
    # Valuation
    print("\n[VALUATION]:")
    try:
        pe = client.get_pe_ratio(symbol)
        print(f"  P/E Ratio: {pe.get('peRatio', 'N/A')}")
        
        pb = client.get_pb_ratio(symbol)
        print(f"  P/B Ratio: {pb.get('pbRatio', 'N/A')}")
        
        ev_ebitda = client.get_ev_ebitda(symbol)
        print(f"  EV/EBITDA: {ev_ebitda.get('evEbitda', 'N/A')}")
    except Exception as e:
        print(f"  Error fetching valuation: {e}")
    
    # Returns
    print("\n📈 RETURNS:")
    try:
        cagr_data = client.get_cagr(
            symbol=symbol,
            start_date="2020-01-01",
            end_date="2024-01-01"
        )
        print(f"  4-Year CAGR: {cagr_data.get('cagr', 'N/A')}%")
        print(f"  Start Price: ₹{cagr_data.get('startPrice', 'N/A')}")
        print(f"  End Price: ₹{cagr_data.get('endPrice', 'N/A')}")
    except Exception as e:
        print(f"  Error fetching returns: {e}")
    
    # Ownership
    print("\n[OWNERSHIP]:")
    try:
        fii_dii = client.get_fii_dii_holdings(symbol)
        print(f"  FII Holdings: {fii_dii.get('fiiPercent', 'N/A')}%")
        print(f"  DII Holdings: {fii_dii.get('diiPercent', 'N/A')}%")
        
        fii_change = client.get_fii_change(symbol)
        print(f"  FII Change: {fii_change.get('fiiChange', 'N/A')}%")
    except Exception as e:
        print(f"  Error fetching ownership: {e}")
    
    # Market Cap
    print("\n[MARKET DATA]:")
    try:
        mcap = client.get_free_float_market_cap(symbol)
        print(f"  Market Cap: ₹{mcap.get('marketCap', 'N/A')} Crores")
        print(f"  Free-Float Market Cap: ₹{mcap.get('freeFloatMarketCap', 'N/A')} Crores")
        print(f"  Promoter Holding: {mcap.get('promoterHoldingPercent', 'N/A')}%")
    except Exception as e:
        print(f"  Error fetching market data: {e}")
    
    # Risk Analysis
    print("\n[RISK ANALYSIS]:")
    try:
        max_drawdown = client.get_max_drawdown(
            symbol=symbol,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        print(f"  Maximum Drawdown: {max_drawdown.get('maxDrawdown', 'N/A')}%")
        
        volatility = client.get_returns_volatility(
            symbol=symbol,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        print(f"  Returns Volatility: {volatility.get('volatility', 'N/A')}%")
    except Exception as e:
        print(f"  Error fetching risk metrics: {e}")
    
    # Sector Classification
    print("\n[SECTOR CLASSIFICATION]:")
    try:
        sector = client.get_sector_classification(symbol)
        print(f"  Sector: {sector.get('sector', 'N/A')}")
        print(f"  Industry: {sector.get('industry', 'N/A')}")
        print(f"  Market Cap Tier: {sector.get('marketCapTier', 'N/A')}")
    except Exception as e:
        print(f"  Error fetching sector data: {e}")
    
    # Leverage Analysis
    print("\n[LEVERAGE ANALYSIS]:")
    try:
        debt_equity = client.get_debt_equity_ratio(symbol)
        print(f"  Debt-to-Equity Ratio: {debt_equity.get('debtEquityRatio', 'N/A')}")
    except Exception as e:
        print(f"  Error fetching leverage metrics: {e}")

# Analyze multiple stocks
stocks = ["RELIANCE", "TCS", "INFY", "HDFC", "SBIN"]
for stock in stocks:
    analyze_stock(stock)
    print("\n" + "="*50 + "\n")
```

#### Advanced Market Data Analysis

Advanced volume and drawdown analysis:

```python
# Average Traded Volume
volume_data = client.get_average_traded_volume(
    symbol="HDFCBANK",
    start_date="2024-04-01",
    end_date="2024-06-30",
    interval="daily"
)
print(f"Average Volume: {volume_data['averageVolume']} shares")

# Index Maximum Drawdown
index_drawdown = client.get_index_max_drawdown(
    index_symbol="NIFTY50",
    start_date="2023-01-01",
    end_date="2024-01-01",
    interval="daily"
)
print(f"Max Drawdown: {index_drawdown['maxDrawdown']}%")

# Drawdown Duration Analysis
drawdown_duration = client.get_drawdown_duration(
    symbol="INFY",
    start_date="2022-01-01",
    end_date="2024-01-01",
    interval="daily"
)
print(f"Max Drawdown Duration: {drawdown_duration['maxDrawdownDuration']} days")
```

#### Technical Price Analysis

Rolling price analysis and volatility:

```python
# Rolling Peak Price Analysis
rolling_peak = client.get_rolling_peak_price(
    symbol="NSE:TCS",
    start_date="2024-01-01",
    end_date="2024-06-30",
    window=20,
    adjusted=True
)
print(f"Rolling peak data points: {len(rolling_peak['data'])}")

# Rolling Price Mean
rolling_mean = client.get_rolling_price_mean(
    symbol="HDFCBANK",
    start_date="2024-01-01",
    end_date="2024-06-30",
    window=50,
    adjusted=True
)
print(f"Rolling mean data points: {len(rolling_mean['data'])}")

# Realized Volatility
volatility = client.get_realized_volatility(
    symbol="NSE:ITC",
    start_date="2024-01-01",
    end_date="2024-06-30",
    adjusted=True
)
print(f"Realized Volatility: {volatility['realizedVolatility']}%")
print(f"Annualized Volatility: {volatility['annualizedVolatility']}%")
```

#### Advanced Risk Metrics

CAMP Beta analysis:

```python
# 90-Day Beta Analysis
beta_90d = client.get_beta_90d(
    symbol="ITC",
    benchmark="NIFTY50"
)
print(f"90-Day Beta: {beta_90d['beta']}")
print(f"Correlation: {beta_90d['correlation']}")
print(f"R-Squared: {beta_90d['rSquared']}")

# Custom Period Beta
beta_custom = client.get_beta_custom_period(
    symbol="TCS",
    benchmark="NIFTY50",
    start_date="2020-01-01",
    end_date="2024-12-31"
)
print(f"Custom Period Beta: {beta_custom['beta']}")
print(f"Alpha: {beta_custom['alpha']}")

# Strategy Max Drawdown
strategy_drawdown = client.get_strategy_max_drawdown(
    strategy_id="str_01jspb8z36edjsp5pecqq0mpm3",
    start_date="2023-01-01",
    end_date="2024-12-31",
    interval="daily"
)
print(f"Strategy Max Drawdown: {strategy_drawdown['maxDrawdown']}")
print(f"Peak Date: {strategy_drawdown['peakDate']}")

# Product Max Drawdown
product_drawdown = client.get_product_max_drawdown(
    product_id="prd_01jyrg7ffkemq9hz3rkeznh9dr",
    start_date="2023-01-01",
    end_date="2024-12-31",
    interval="monthly"
)
print(f"Product Max Drawdown: {product_drawdown['maxDrawdown']}")

# Average True Range (ATR)
atr_data = client.get_atr(
    symbol="AXISBANK",
    start_date="2023-01-01",
    end_date="2024-12-31",
    window=14,
    adjusted=True,
    interval="daily"
)
print(f"Latest ATR: {atr_data['atr'][-1]['atrValue']}")

# Simple Return
simple_return = client.get_simple_return(
    symbol="NIFTY_IT",
    start_date="2023-01-01",
    end_date="2024-12-31",
    adjusted=True,
    interval="daily",
    benchmark="NIFTY 50"
)
print(f"Total Return: {simple_return['totalReturn']}")
print(f"Relative Return: {simple_return['relativeReturn']}")
```

**Key Features:**
- **Comprehensive Coverage**: 43+ analytics endpoints covering fundamentals, valuation, returns, market data, ownership, metrics, macro data, risk analysis, sector classification, leverage analysis, and advanced technical analysis
- **Fundamentals Analysis**: 9 methods including ROE, ROA, margins, ratios, book-to-market, market cap-to-sales, and cash-to-market cap
- **Valuation Metrics**: P/E, P/B, EV/EBITDA, FCF yield with TTM and consolidated/standalone options
- **Risk-Adjusted Metrics**: Sortino ratio, upside capture ratio, maximum drawdown, and returns volatility for comprehensive risk analysis
- **Sector & Industry Analysis**: Complete GICS classification with sector, industry, sub-industry, and market cap tier data
- **Leverage Analysis**: Debt-to-equity ratios and comprehensive financial leverage metrics
- **Institutional Analysis**: Track FII/DII holdings and their quarterly changes
- **Returns Calculation**: Calculate CAGR over custom time periods with flexible date ranges
- **Macro Economic Data**: Risk-free rates for various tenors and countries
- **Index Support**: Historical OHLC data for major indices like NIFTY50, SENSEX
- **Error Handling**: Robust error handling with comprehensive parameter validation
- **Modern API Design**: Updated parameter names following camelCase convention

### Wizzer Client Examples

#### Market Data and Analysis Example

```python
from wiz_trader import WizzerClient
import pandas as pd
import matplotlib.pyplot as plt

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def analyze_index_performance(index_symbol, exchange, start_date, end_date):
    # Get index components
    components = client.get_index_components(
        trading_symbol=index_symbol,
        exchange=exchange
    )
    print(f"Found {len(components)} components in {index_symbol}")
    
    # Get the identifiers for the top 5 weighted components
    top_components = sorted(components, key=lambda x: x.get('weightage', 0), reverse=True)[:5]
    instrument_ids = [comp['identifier'] for comp in top_components]
    
    # Fetch historical data
    historical_data = client.get_historical_ohlcv(
        instruments=instrument_ids,
        start_date=start_date,
        end_date=end_date,
        ohlcv=["close"],
        interval="1d"
    )
    
    # Process and plot the data
    for instrument_data in historical_data:
        symbol = instrument_data['instrument'].split(':')[1]
        df = pd.DataFrame(instrument_data['data'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Calculate percentage change from first day
        first_close = df['close'].iloc[0]
        df['pct_change'] = ((df['close'] - first_close) / first_close) * 100
        
        plt.plot(df.index, df['pct_change'], label=symbol)
    
    plt.title(f"Performance of Top {index_symbol} Components")
    plt.xlabel("Date")
    plt.ylabel("% Change")
    plt.legend()
    plt.grid(True)
    plt.show()

# Analyze NIFTY 50 performance for Jan 2024
analyze_index_performance(
    index_symbol="NIFTY 50",
    exchange="NSE",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

#### Algorithmic Trading Example

```python
from wiz_trader import QuotesClient, WizzerClient
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMovingAverageCrossover:
    def __init__(self, symbol, exchange, token, fast_period=5, slow_period=20):
        # Trading parameters
        self.symbol = symbol
        self.exchange = exchange
        self.token = token
        self.instrument_id = f"{exchange}:{symbol}:{token}"
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # State variables
        self.prices = []
        self.position = None
        self.order_id = None
        
        # Clients
        self.quotes_client = QuotesClient(
            base_url="wss://websocket-url/quotes",
            token="your-jwt-token"
        )
        self.wizzer_client = WizzerClient(
            base_url="https://api-url.in",
            token="your-jwt-token"
        )
        
        # Set up quotes client callbacks
        self.quotes_client.on_tick = self.on_tick
        self.quotes_client.on_connect = self.on_connect
        self.quotes_client.on_error = lambda ws, error: logger.error(f"Error: {error}")
    
    def on_connect(self, ws):
        logger.info(f"Connected to quotes server")
        ws.subscribe([self.instrument_id])
    
    def on_tick(self, ws, tick):
        if "ltp" in tick:
            price = tick["ltp"]
            self.prices.append(price)
            
            # Keep only the required number of prices
            if len(self.prices) > self.slow_period:
                self.prices.pop(0)
            
            # Once we have enough data, check for signals
            if len(self.prices) >= self.slow_period:
                self.check_for_signals()
    
    def check_for_signals(self):
        # Calculate moving averages
        fast_ma = sum(self.prices[-self.fast_period:]) / self.fast_period
        slow_ma = sum(self.prices) / self.slow_period
        
        current_price = self.prices[-1]
        
        logger.info(f"Price: {current_price}, Fast MA: {fast_ma:.2f}, Slow MA: {slow_ma:.2f}")
        
        # Generate signals
        if fast_ma > slow_ma and self.position != "long":
            # Buy signal
            logger.info("BUY SIGNAL")
            self.enter_position("long", current_price)
        
        elif fast_ma < slow_ma and self.position == "long":
            # Sell signal
            logger.info("SELL SIGNAL")
            self.exit_position(current_price)
    
    def enter_position(self, position_type, price):
        if position_type == "long":
            # Place a buy order
            try:
                order_response = self.wizzer_client.place_order(
                    exchange=self.exchange,
                    trading_symbol=self.symbol,
                    transaction_type=self.wizzer_client.TRANSACTION_TYPE_BUY,
                    quantity=10,  # Fixed quantity for simplicity
                    order_type=self.wizzer_client.ORDER_TYPE_MARKET,
                    product=self.wizzer_client.PRODUCT_CNC
                )
                self.order_id = order_response.get("orderId")
                self.position = "long"
                logger.info(f"Entered LONG position at {price}, Order ID: {self.order_id}")
            except Exception as e:
                logger.error(f"Error entering position: {e}")
    
    def exit_position(self, price):
        if self.position == "long":
            # Place a sell order
            try:
                order_response = self.wizzer_client.place_order(
                    exchange=self.exchange,
                    trading_symbol=self.symbol,
                    transaction_type=self.wizzer_client.TRANSACTION_TYPE_SELL,
                    quantity=10,  # Fixed quantity for simplicity
                    order_type=self.wizzer_client.ORDER_TYPE_MARKET,
                    product=self.wizzer_client.PRODUCT_CNC
                )
                logger.info(f"Exited LONG position at {price}, Order ID: {order_response.get('orderId')}")
                self.position = None
                self.order_id = None
            except Exception as e:
                logger.error(f"Error exiting position: {e}")
    
    def run(self):
        try:
            logger.info("Starting the strategy...")
            self.quotes_client.connect()
        except KeyboardInterrupt:
            logger.info("Strategy interrupted by user")
            if self.position:
                logger.info("Closing position before exit")
                self.exit_position(self.prices[-1] if self.prices else 0)
            self.quotes_client.stop()

# Run the strategy
strategy = SimpleMovingAverageCrossover(
    symbol="SBIN",
    exchange="NSE",
    token=3045,
    fast_period=5,
    slow_period=20
)
strategy.run()
```

#### Basket Management Example

```python
from wiz_trader import WizzerClient
import json

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def create_and_trade_basket():
    # Create a sector-based basket
    banking_basket = client.create_basket(
        name="Banking Basket",
        instruments=[
            {
                "shares": 20,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:SBIN:3045",
                    "orderIndex": 1,
                    "exchangeToken": 3045,
                    "tradingSymbol": "SBIN"
                }
            },
            {
                "shares": 15,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:ICICIBANK:4963",
                    "orderIndex": 2,
                    "exchangeToken": 4963,
                    "tradingSymbol": "ICICIBANK"
                }
            },
            {
                "shares": 15,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:HDFCBANK:1333",
                    "orderIndex": 3,
                    "exchangeToken": 1333,
                    "tradingSymbol": "HDFCBANK"
                }
            },
            {
                "shares": 30,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:BANKBARODA:2263",
                    "orderIndex": 4,
                    "exchangeToken": 2263,
                    "tradingSymbol": "BANKBARODA"
                }
            }
        ],
        weightage_scheme="equi_weighted",
        capital={"minValue": 100000, "actualValue": 100000},
        instrument_types=["EQLC"]
    )
    
    basket_id = banking_basket.get('id')
    basket_symbol = banking_basket.get('tradingSymbol')
    exchange_token = banking_basket.get('basketInstrument', {}).get('exchangeToken')
    
    print(f"Created basket: {basket_symbol} (ID: {basket_id})")
    
    # Place a buy order for the basket
    try:
        order_response = client.place_basket_order(
            trading_symbol=basket_symbol,
            transaction_type=client.TRANSACTION_TYPE_BUY,
            quantity=1,  # Buy one unit of the basket
            price=100000.00,
            product=client.PRODUCT_CNC
        )
        print(f"Placed basket buy order: {order_response.get('orderId')}")
        
        # After some time, exit the basket
        # (This would normally be based on some strategy or time delay)
        exit_response = client.place_basket_exit_order(
            trading_symbol=basket_symbol,
            exchange=client.EXCHANGE_WZR,
            transaction_type=client.TRANSACTION_TYPE_SELL,
            quantity=1,
            exchange_token=exchange_token
        )
        print(f"Placed basket exit order: {exit_response.get('orderId')}")
        
    except Exception as e:
        print(f"Error during basket trading: {e}")

# Rebalance the basket (e.g., to adjust weightages or change stocks)
    try:
        rebalance_response = client.rebalance_basket(
            trading_symbol=basket_symbol,
            instruments=[
                "NSE:SBIN:3045",
                "NSE:HDFCBANK:1333",
                "NSE:ICICIBANK:4963",
                "NSE:AXISBANK:5900"  # Replacing BANKBARODA with AXISBANK
            ]
        )
        print(f"Rebalanced basket successfully")
    except Exception as e:
        print(f"Error during basket rebalancing: {e}")

# Run the basket trading example
create_and_trade_basket()
```

## Common Use Cases

### Backtesting with Historical Data

```python
from wiz_trader import WizzerClient
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def backtest_simple_strategy(symbol, exchange, token, start_date, end_date, 
                             fast_period=10, slow_period=30):
    # Get historical data
    instrument_id = f"{exchange}:{symbol}:{token}"
    data = client.get_historical_ohlcv(
        instruments=[instrument_id],
        start_date=start_date,
        end_date=end_date,
        ohlcv=["open", "high", "low", "close", "volume"],
        interval="1d"
    )
    
    if not data or not data[0].get('data'):
        print("No data available for the specified period")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data[0]['data'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Calculate moving averages
    df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_period).mean()
    
    # Generate signals
    df['signal'] = 0
    df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1  # Buy signal
    df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1  # Sell signal
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    # Calculate cumulative returns
    df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
    df['strategy_cumulative_returns'] = (1 + df['strategy_returns']).cumprod() - 1
    
    # Calculate statistics
    total_days = len(df)
    winning_days = len(df[df['strategy_returns'] > 0])
    win_rate = winning_days / total_days if total_days > 0 else 0
    
    strategy_return = df['strategy_cumulative_returns'].iloc[-1]
    buy_hold_return = df['cumulative_returns'].iloc[-1]
    
    print(f"Backtest Results for {symbol} ({start_date} to {end_date}):")
    print(f"Strategy Return: {strategy_return:.2%}")
    print(f"Buy & Hold Return: {buy_hold_return:.2%}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Total Trades: {df['signal'].diff().abs().sum() / 2:.0f}")
    
    return df

# Run a backtest
result_df = backtest_simple_strategy(
    symbol="SBIN",
    exchange="NSE",
    token=3045,
    start_date="2023-01-01",
    end_date="2023-12-31",
    fast_period=10,
    slow_period=30
)

# Plot the results 
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))

# Plot prices and moving averages
plt.subplot(2, 1, 1)
plt.plot(result_df.index, result_df['close'], label='Close Price')
plt.plot(result_df.index, result_df['fast_ma'], label=f'Fast MA ({10} days)')
plt.plot(result_df.index, result_df['slow_ma'], label=f'Slow MA ({30} days)')
plt.title('Price and Moving Averages')
plt.legend()
plt.grid(True)

# Plot cumulative returns
plt.subplot(2, 1, 2)
plt.plot(result_df.index, result_df['cumulative_returns'], label='Buy & Hold')
plt.plot(result_df.index, result_df['strategy_cumulative_returns'], label='Strategy')
plt.title('Cumulative Returns')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
```

### Real-time Portfolio Monitoring

```python
from wiz_trader import QuotesClient, WizzerClient
import pandas as pd
import time
from datetime import datetime

# Initialize clients
quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="info"
)

class PortfolioMonitor:
    def __init__(self):
        self.portfolio = {}
        self.last_update_time = None
        self.update_interval = 60  # seconds
        
    def on_tick(self, ws, tick):
        """Process incoming market data"""
        if 'instrument' in tick and 'ltp' in tick:
            instrument = tick['instrument']
            ltp = tick['ltp']
            
            if instrument in self.portfolio:
                # Update the current price
                self.portfolio[instrument]['current_price'] = ltp
                
                # Calculate P&L
                avg_price = self.portfolio[instrument]['avg_price']
                qty = self.portfolio[instrument]['qty']
                
                if qty > 0:  # Long position
                    pnl = (ltp - avg_price) * qty
                    pnl_percent = ((ltp / avg_price) - 1) * 100
                else:  # Short position
                    pnl = (avg_price - ltp) * abs(qty)
                    pnl_percent = ((avg_price / ltp) - 1) * 100
                
                self.portfolio[instrument]['pnl'] = pnl
                self.portfolio[instrument]['pnl_percent'] = pnl_percent
                
                # Display portfolio if update interval has passed
                current_time = time.time()
                if (self.last_update_time is None or 
                    current_time - self.last_update_time > self.update_interval):
                    self.display_portfolio()
                    self.last_update_time = current_time
    
    def on_connect(self, ws):
        """Handle connection to quotes server"""
        print(f"Connected to quotes server at {datetime.now()}")
        # Fetch holdings and subscribe to them
        self.fetch_holdings()
    
    def fetch_holdings(self):
        """Fetch holdings from the API and update portfolio"""
        try:
            holdings = wizzer_client.get_holdings()
            
            # Extract holding information and update portfolio
            instruments_to_subscribe = []
            for holding in holdings:
                if holding.get('qty', 0) > 0:
                    instrument = holding.get('identifier', '')
                    if instrument:
                        self.portfolio[instrument] = {
                            'symbol': holding.get('tradingSymbol', ''),
                            'exchange': holding.get('exchange', ''),
                            'qty': holding.get('qty', 0),
                            'avg_price': holding.get('avgPrice', 0),
                            'invested_value': holding.get('investedValue', 0),
                            'current_price': 0,
                            'pnl': 0,
                            'pnl_percent': 0
                        }
                        instruments_to_subscribe.append(instrument)
            
            # Subscribe to these instruments for real-time updates
            if instruments_to_subscribe:
                quotes_client.subscribe(instruments_to_subscribe)
                print(f"Subscribed to {len(instruments_to_subscribe)} instruments")
            else:
                print("No holdings found to monitor")
        
        except Exception as e:
            print(f"Error fetching holdings: {e}")
    
    def display_portfolio(self):
        """Display the current portfolio status"""
        if not self.portfolio:
            print("Portfolio is empty")
            return
        
        print("\n" + "="*80)
        print(f"Portfolio Status as of {datetime.now()}")
        print("="*80)
        
        # Create a pandas DataFrame for nicer display
        df = pd.DataFrame.from_dict(self.portfolio, orient='index')
        df['pnl'] = df['pnl'].round(2)
        df['pnl_percent'] = df['pnl_percent'].round(2)
        
        # Sort by P&L
        df = df.sort_values('pnl', ascending=False)
        
        print(df[['symbol', 'qty', 'avg_price', 'current_price', 'pnl', 'pnl_percent']])
        
        # Calculate total values
        total_invested = df['invested_value'].sum()
        total_current = (df['current_price'] * df['qty']).sum()
        total_pnl = df['pnl'].sum()
        total_pnl_percent = ((total_current / total_invested) - 1) * 100 if total_invested > 0 else 0
        
        print("-"*80)
        print(f"Total Invested: ₹{total_invested:.2f}")
        print(f"Total Current Value: ₹{total_current:.2f}")
        print(f"Total P&L: ₹{total_pnl:.2f} ({total_pnl_percent:.2f}%)")
        print("="*80 + "\n")

# Create and run the portfolio monitor
monitor = PortfolioMonitor()

# Set up callbacks
quotes_client.on_tick = monitor.on_tick
quotes_client.on_connect = monitor.on_connect
quotes_client.on_error = lambda ws, error: print(f"Error: {error}")

# Start monitoring (blocking call)
try:
    quotes_client.connect()
except KeyboardInterrupt:
    print("\nPortfolio monitoring stopped by user")
    quotes_client.stop()
```

### Multi-Strategy Trading

```python
from wiz_trader import QuotesClient, WizzerClient
import pandas as pd
import threading
import time
from datetime import datetime
import numpy as np

# Initialize API clients
quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="info"
)

class TradingStrategy:
    """Base class for trading strategies"""
    def __init__(self, name, symbols):
        self.name = name
        self.symbols = symbols
        self.active = False
        self.positions = {}
        self.prices = {}
        
    def on_tick(self, tick):
        """Process tick data - should be implemented by subclasses"""
        pass
    
    def start(self):
        """Start the strategy"""
        self.active = True
        print(f"Strategy {self.name} started at {datetime.now()}")
    
    def stop(self):
        """Stop the strategy"""
        self.active = False
        print(f"Strategy {self.name} stopped at {datetime.now()}")
        
        # Close any open positions
        self.close_all_positions()
    
    def close_all_positions(self):
        """Close all open positions"""
        for symbol, position in list(self.positions.items()):
            if position != 0:
                try:
                    self.execute_order(
                        symbol=symbol.split(':')[1],
                        exchange=symbol.split(':')[0],
                        transaction_type="SELL" if position > 0 else "BUY",
                        quantity=abs(position)
                    )
                    print(f"Closed position for {symbol}: {position} units")
                    self.positions[symbol] = 0
                except Exception as e:
                    print(f"Error closing position for {symbol}: {e}")
    
    def execute_order(self, symbol, exchange, transaction_type, quantity):
        """Execute an order through the API"""
        try:
            response = wizzer_client.place_order(
                exchange=exchange,
                trading_symbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                order_type=wizzer_client.ORDER_TYPE_MARKET,
                product=wizzer_client.PRODUCT_CNC
            )
            print(f"Order executed: {exchange}:{symbol} {transaction_type} {quantity} units")
            return response.get('orderId')
        except Exception as e:
            print(f"Order execution error: {e}")
            return None

class MovingAverageCrossover(TradingStrategy):
    """Moving Average Crossover Strategy"""
    def __init__(self, name, symbols, fast_period=10, slow_period=30):
        super().__init__(name, symbols)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.price_history = {s: [] for s in symbols}
    
    def on_tick(self, tick):
        if not self.active:
            return
            
        instrument = tick.get('instrument')
        ltp = tick.get('ltp')
        
        if instrument in self.symbols and ltp is not None:
            # Store the current price
            self.prices[instrument] = ltp
            
            # Add to price history
            self.price_history[instrument].append(ltp)
            
            # Keep only enough prices for the slow MA
            if len(self.price_history[instrument]) > self.slow_period:
                self.price_history[instrument].pop(0)
            
            # Check for trading signals if we have enough data
            if len(self.price_history[instrument]) >= self.slow_period:
                self.check_signals(instrument)
    
    def check_signals(self, instrument):
        prices = self.price_history[instrument]
        
        # Calculate moving averages
        fast_ma = sum(prices[-self.fast_period:]) / self.fast_period
        slow_ma = sum(prices) / self.slow_period
        
        # Get current position and price
        current_position = self.positions.get(instrument, 0)
        current_price = self.prices[instrument]
        
        # Generate signals
        if fast_ma > slow_ma and current_position <= 0:
            # Buy signal
            quantity = 10  # Fixed quantity for simplicity
            
            # Close any short position first
            if current_position < 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="BUY",
                    quantity=abs(current_position)
                )
                self.positions[instrument] = 0
            
            # Enter long position
            self.execute_order(
                symbol=instrument.split(':')[1],
                exchange=instrument.split(':')[0],
                transaction_type="BUY",
                quantity=quantity
            )
            self.positions[instrument] = quantity
            
            print(f"{self.name}: BUY {quantity} units of {instrument} at {current_price}")
            
        elif fast_ma < slow_ma and current_position >= 0:
            # Sell signal
            
            # Close any long position
            if current_position > 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="SELL",
                    quantity=current_position
                )
                self.positions[instrument] = 0
                
                print(f"{self.name}: SELL {current_position} units of {instrument} at {current_price}")
            
            # Option: Enter short position (if allowed)
            # quantity = 10  # Fixed quantity for simplicity
            # self.execute_order(
            #     symbol=instrument.split(':')[1],
            #     exchange=instrument.split(':')[0],
            #     transaction_type="SELL",
            #     quantity=quantity
            # )
            # self.positions[instrument] = -quantity
            # print(f"{self.name}: SHORT {quantity} units of {instrument} at {current_price}")

class BollingerBands(TradingStrategy):
    """Bollinger Bands Strategy"""
    def __init__(self, name, symbols, period=20, std_dev=2):
        super().__init__(name, symbols)
        self.period = period
        self.std_dev = std_dev
        self.price_history = {s: [] for s in symbols}
    
    def on_tick(self, tick):
        if not self.active:
            return
            
        instrument = tick.get('instrument')
        ltp = tick.get('ltp')
        
        if instrument in self.symbols and ltp is not None:
            # Store the current price
            self.prices[instrument] = ltp
            
            # Add to price history
            self.price_history[instrument].append(ltp)
            
            # Keep only enough prices for the calculation
            if len(self.price_history[instrument]) > self.period:
                self.price_history[instrument].pop(0)
            
            # Check for trading signals if we have enough data
            if len(self.price_history[instrument]) >= self.period:
                self.check_signals(instrument)
    
    def check_signals(self, instrument):
        prices = self.price_history[instrument]
        
        # Calculate Bollinger Bands
        sma = sum(prices) / len(prices)
        std = np.std(prices)
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        # Get current position and price
        current_position = self.positions.get(instrument, 0)
        current_price = self.prices[instrument]
        
        # Generate signals
        if current_price < lower_band and current_position <= 0:
            # Buy signal (price below lower band)
            quantity = 10  # Fixed quantity for simplicity
            
            # Close any short position first
            if current_position < 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="BUY",
                    quantity=abs(current_position)
                )
                self.positions[instrument] = 0
            
            # Enter long position
            self.execute_order(
                symbol=instrument.split(':')[1],
                exchange=instrument.split(':')[0],
                transaction_type="BUY",
                quantity=quantity
            )
            self.positions[instrument] = quantity
            
            print(f"{self.name}: BUY {quantity} units of {instrument} at {current_price} (below lower band {lower_band:.2f})")
            
        elif current_price > upper_band and current_position >= 0:
            # Sell signal (price above upper band)
            
            # Close any long position
            if current_position > 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="SELL",
                    quantity=current_position
                )
                self.positions[instrument] = 0
                
                print(f"{self.name}: SELL {current_position} units of {instrument} at {current_price} (above upper band {upper_band:.2f})")

class MultiStrategyManager:
    """Manages multiple trading strategies"""
    def __init__(self, quotes_client):
        self.quotes_client = quotes_client
        self.strategies = {}
        
    def add_strategy(self, strategy):
        """Add a strategy to the manager"""
        self.strategies[strategy.name] = strategy
        
        # Subscribe to all strategy symbols
        for symbol in strategy.symbols:
            if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                print(f"Warning: Symbol {symbol} does not include exchange prefix")
        
    def on_tick(self, ws, tick):
        """Process ticks and distribute to strategies"""
        for strategy in self.strategies.values():
            strategy.on_tick(tick)
    
    def on_connect(self, ws):
        """Handle connection to quotes server"""
        print(f"Connected to quotes server at {datetime.now()}")
        
        # Collect all symbols from all strategies
        all_symbols = set()
        for strategy in self.strategies.values():
            all_symbols.update(strategy.symbols)
        
        # Subscribe to all symbols
        if all_symbols:
            ws.subscribe(list(all_symbols))
            print(f"Subscribed to {len(all_symbols)} symbols")
    
    def start_all(self):
        """Start all strategies"""
        for strategy in self.strategies.values():
            strategy.start()
    
    def stop_all(self):
        """Stop all strategies"""
        for strategy in self.strategies.values():
            strategy.stop()
    
    def start_strategy(self, name):
        """Start a specific strategy"""
        if name in self.strategies:
            self.strategies[name].start()
        else:
            print(f"Strategy {name} not found")
    
    def stop_strategy(self, name):
        """Stop a specific strategy"""
        if name in self.strategies:
            self.strategies[name].stop()
        else:
            print(f"Strategy {name} not found")
    
    def run(self):
        """Run the strategy manager"""
        # Set up callbacks
        self.quotes_client.on_tick = self.on_tick
        self.quotes_client.on_connect = self.on_connect
        self.quotes_client.on_error = lambda ws, error: print(f"Error: {error}")
        
        # Start all strategies
        self.start_all()
        
        # Start the quotes client (blocking call)
        try:
            self.quotes_client.connect()
        except KeyboardInterrupt:
            print("\nMulti-strategy manager stopped by user")
            self.stop_all()
            self.quotes_client.stop()

# Create strategies
ma_strategy = MovingAverageCrossover(
    name="MA Crossover",
    symbols=["NSE:SBIN:3045", "NSE:ICICIBANK:4963"],
    fast_period=10,
    slow_period=30
)

bb_strategy = BollingerBands(
    name="Bollinger Bands",
    symbols=["NSE:RELIANCE:2885", "NSE:TCS:2953"],
    period=20,
    std_dev=2
)

# Create and run the multi-strategy manager
manager = MultiStrategyManager(quotes_client)
manager.add_strategy(ma_strategy)
manager.add_strategy(bb_strategy)
manager.run()
```

## Error Handling

The SDK provides several mechanisms for handling errors:

### Exception Handling

All API calls can throw exceptions, which should be caught and handled:

```python
try:
    order_response = client.place_order(
        exchange=client.EXCHANGE_NSE,
        trading_symbol="SBIN",
        transaction_type=client.TRANSACTION_TYPE_BUY,
        quantity=10,
        order_type=client.ORDER_TYPE_MARKET,
        product=client.PRODUCT_CNC
    )
    print(f"Order placed successfully: {order_response.get('orderId')}")
except Exception as e:
    print(f"Error placing order: {e}")
```

### Callback Error Handling

For the WebSocket client, errors are also sent via the `on_error` callback:

```python
def on_error(ws, error):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {error}")
    
    # You could implement reconnection logic or alerting here
    if isinstance(error, ConnectionRefusedError):
        print("Connection refused. Check server status.")
    elif isinstance(error, TimeoutError):
        print("Connection timed out. Check network.")

quotes_client.on_error = on_error
```

### Logging

Both clients support different log levels:

```python
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="debug"  # Options: "error", "info", "debug"
)
```

The logs can help diagnose issues during development and production.

## Troubleshooting

### Common Issues

#### Authentication Issues

If you're facing authentication errors:

1. Check that your token is valid and not expired
2. Ensure you're using the correct base_url for production or development
3. Verify environment variables if you're using them

Example of token validation:
```python
def is_token_valid(token):
    """Basic validation of JWT token format"""
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    # Check if the token is expired
    import base64
    import json
    import time
    
    try:
        # Decode the payload
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
        decoded = base64.b64decode(payload)
        data = json.loads(decoded)
        
        # Check expiration
        if 'exp' in data:
            return data['exp'] > time.time()
        return True
    except Exception:
        return False

# Check if token is valid
if not is_token_valid(token):
    print("Token is invalid or expired. Please get a new token.")
```

#### WebSocket Connection Issues

If you're having trouble connecting to the WebSocket server:

1. Check network connectivity and firewall settings
2. Verify the WebSocket URL is correct
3. Check if the server supports SSL/TLS if using 'wss://' protocol
4. Try with a smaller `max_message_size` to rule out size limitations

#### Order Placement Failures

If orders are not being placed successfully:

1. Check the error message from the API response
2. Verify that you're using the correct exchange, symbol, and token
3. Ensure you have sufficient funds/holdings for the trade
4. Check that market hours are active for the segment you're trading

## API Reference

For a complete list of all available methods and parameters, refer to the class docstrings within the SDK.

```python
# Example of getting detailed help on a method
help(WizzerClient.place_order)
```

### Environment Variables

All supported environment variables:

- `WZ__QUOTES_BASE_URL`: WebSocket URL for the quotes server
- `WZ__API_BASE_URL`: Base URL for the Wizzer's REST API
- `WZ__TOKEN`: JWT token for authentication
- `WZ__STRATEGY_ID`: Default strategy ID to use if not provided in methods

### Full Method List

#### QuotesClient
- `__init__(base_url, token, log_level, max_message_size, batch_size)`
- `connect()` - Connect in blocking mode
- `connect_async()` - Connect in non-blocking mode
- `stop()` - Stop the WebSocket connection
- `subscribe(instruments)` - Subscribe to instruments
- `unsubscribe(instruments)` - Unsubscribe from instruments

#### WizzerClient
- `__init__(base_url, token, strategy_id, log_level)`
- `get_indices(trading_symbol, exchange)`
- `get_index_components(trading_symbol, exchange)`
- `get_historical_ohlcv(instruments, start_date, end_date, ohlcv, interval)`
- `place_order(exchange, trading_symbol, transaction_type, quantity, ...)`
- `modify_order(order_id, **params)`
- `cancel_order(order_id)`
- `get_order(order_id)`
- `get_positions(position_status)`
- `get_open_positions()`
- `get_closed_positions()`
- `get_holdings(portfolios)`
- `create_basket(name, instruments, weightage_scheme, capital, instrument_types)`
- `get_baskets()`
- `get_basket(basket_id)`
- `get_basket_instruments(basket_id)`
- `place_basket_order(trading_symbol, transaction_type, quantity, ...)`
- `place_basket_exit_order(trading_symbol, exchange, transaction_type, quantity, exchange_token, **kwargs)`
- `modify_basket_order(order_id, **params)`
- `rebalance_basket(trading_symbol, instruments)`
- `exit_all_positions()`
- `exit_strategy_positions(strategy_id)`

# Indian Industry Classification Table

| MacroSector | Sector | Industry | BasicIndustries |
|-------------|---------|----------|-----------------|
| Commodities | Chemicals | Chemicals & Petrochemicals | Commodity Chemicals |
|  |  |  | Specialty Chemicals |
|  |  |  | Carbon Black |
|  |  |  | Dyes And Pigments |
|  |  |  | Explosives |
|  |  |  | Petrochemicals |
|  |  |  | Printing Inks |
|  |  |  | Trading - Chemicals |
|  |  |  | Industrial Gases |
|  |  | Fertilizers & Agrochemicals | Fertilizers |
|  |  |  | Pesticides & Agrochemicals |
|  | Construction Materials | Cement & Cement Products | Cement & Cement Products |
|  |  | Other Construction Materials | Other Construction Materials |
|  | Metals & Mining | Ferrous Metals | Ferro & Silica Manganese |
|  |  |  | Pig Iron |
|  |  |  | Sponge Iron |
|  |  |  | Iron & Steel |
|  |  | Non - Ferrous Metals | Aluminium |
|  |  |  | Copper |
|  |  |  | Zinc |
|  |  |  | Precious Metals |
|  |  | Diversified Metals | Diversified Metals |
|  |  | Minerals & Mining | Industrial Minerals |
|  |  | Metals & Minerals Trading | Trading - Metals |
|  |  |  | Trading - Minerals |
|  | Forest Materials | Paper, Forest & Jute Products | Paper & Paper Products |
|  |  |  | Forest Products |
|  |  |  | Jute & Jute Products |
| Consumer Discretionary | Automobile and Auto Components | Automobiles | Passenger Cars & Utility Vehicles |
|  |  |  | 2/3 Wheelers |
|  |  |  | Auto Dealer |
|  |  | Auto Components | Auto Components & Equipments |
|  |  |  | Tyres & Rubber Products |
|  |  |  | Trading - Auto Components |
|  | Consumer Durables | Consumer Durables | Cycles |
|  |  |  | Consumer Electronics |
|  |  |  | Furniture, Home Furnishing |
|  |  |  | Ceramics |
|  |  |  | Granites & Marbles |
|  |  |  | Gems, Jewellery And Watches |
|  |  |  | Glass - Consumer |
|  |  |  | Household Appliances |
|  |  |  | Houseware |
|  |  |  | Leather And Leather Products |
|  |  |  | Leisure Products |
|  |  |  | Plastic Products - Consumer |
|  |  |  | Plywood Boards/Laminates |
|  |  |  | Sanitary Ware |
|  |  |  | Paints |
|  |  |  | Diversified consumer products |
|  |  |  | Footwear |
|  | Textiles | Textiles & Apparels | Garments & Apparels |
|  |  |  | Other Textile Products |
|  |  |  | Trading - Textile Products |
|  | Media,Entertainment & Publication | Media | Advertising & Media Agencies |
|  |  |  | Electronic Media |
|  |  |  | Web based media and service |
|  |  |  | Print Media |
|  |  | Entertainment | Film Production,Distribution & Exhibition |
|  |  |  | Digital Entertainment |
|  |  |  | Media & Entertainment |
|  |  |  | TV Broadcasting & Software Production |
|  |  | Printing & Publication | Printing & Publication |
|  | Realty | Realty | Residential,Commercial Projects |
|  |  |  | Real Estate related services |
|  |  |  | Real Estate Investment Trusts(REITs) |
|  | Consumer Services | Leisure Services | Hotels & Resorts |
|  |  |  | Restaurants |
|  |  |  | Amusement Parks/Other Recreation |
|  |  |  | Wellness |
|  |  |  | Tour, Travel Related Services |
|  |  | Other Consumer Services | Education |
|  |  |  | E-Learning |
|  |  |  | Food Storage Facilities |
|  |  |  | Other Consumer Services |
|  |  | Retailing | Speciality Retail  |
|  |  |  | Pharmacy Retail |
|  |  |  | Diversified Retail |
|  |  |  | E-Retail/ ECommerce |
|  |  |  | Internet & Catalogue Retail |
|  |  |  | Distributors |
| Energy | Oil, Gas & Consumable Fuels | Gas | Gas Transmission/Marketing |
|  |  |  | LPG/CNG/PNG/LNG Supplier |
|  |  |  | Trading - Gas |
|  |  | Oil | Oil Exploration & Production |
|  |  |  | Offshore Support Solution Drilling |
|  |  |  | Oil Storage & Transportation |
|  |  |  | Oil Equipment & Services |
|  |  | Petroleum Products | Refineries & Marketing |
|  |  |  | Lubricants |
|  |  | Consumable Fuels | Coal |
|  |  |  | Trading - Coal |
| Fast Moving Consumer Goods | Fast Moving Consumer Goods | Agricultural Food & other Products | Edible Oil |
|  |  |  | Sugar |
|  |  |  | Tea & Coffee |
|  |  |  | Other Agricultural Products |
|  |  |  | Other Beverages |
|  |  | Beverages | Breweries & Distilleries |
|  |  | Cigarettes & Tobacco Products | Cigarettes & Tobacco Products |
|  |  | Food Products | Animal Feed |
|  |  |  | Dairy Products |
|  |  |  | Other Food Products |
|  |  |  | Packaged Foods |
|  |  |  | Seafood |
|  |  |  | Meat Products including Poultry |
|  |  | Personal Products | Personal Care |
|  |  | Household Products | Household Products |
|  |  |  | Stationary |
|  |  | Diversified FMCG | Diversified FMCG |
| Financial Services | Financial Services | Finance | Financial Institution |
|  |  |  | Housing Finance Company |
|  |  |  | Investment Company |
|  |  |  | Non Banking Financial Company (NBFC) |
|  |  |  | Other Financial Services |
|  |  |  | Holding Company |
|  |  |  | Microfinance Institutions |
|  |  |  | Securitisation |
|  |  | Banks | Public Sector Bank |
|  |  |  | Private Sector Bank |
|  |  |  | Other Bank |
|  |  | Capital Markets | Asset Management Company |
|  |  |  | Depositories,Clearing Houses and Other Intermediaries |
|  |  |  | Financial Products Distributor |
|  |  |  | Ratings |
|  |  |  | Exchange and Data Platform |
|  |  |  | Stockbroking & Allied |
|  |  |  | Other Capital Market related Services |
|  |  | Insurance | General Insurance |
|  |  |  | Life Insurance |
|  |  |  | Other Insurance Companies |
|  |  |  | Insurance Distributors |
|  |  | Financial Technology (Fintech) | Financial Technology (Fintech) |
| Healthcare | Healthcare | Pharmaceuticals & Biotechnology | Pharmaceuticals |
|  |  |  | Biotechnology |
|  |  | Healthcare Equipment & Supplies | Medical Equipment & Supplies |
|  |  | Healthcare Services | Hospital |
|  |  |  | Healthcare Service Provider |
|  |  |  | Healthcare Research, Analytics & Technology |
| Industrials | Construction | Construction | Civil Construction |
|  | Capital Goods | Aerospace & Defense | Aerospace & Defense |
|  |  | Agricultural,Commercial & Construction Vehicles | Tractors |
|  |  |  | Commercial Vehicles |
|  |  |  | Construction Vehicles |
|  |  |  | Dealers-Commercial Vehicles, Tractors, Construction Vehicles |
|  |  | Electrical Equipment | Heavy Electrical Equipment |
|  |  |  | Other Electrical Equipment |
|  |  | Industrial Manufacturing | Railway Wagons |
|  |  |  | Ship Building & Allied Services |
|  |  |  | Industrial Products |
|  |  | Industrial Products | Cables - Electricals |
|  |  |  | Castings & Forgings |
|  |  |  | Packaging |
|  |  |  | Plastic Products - Industrial |
|  |  |  | Rubber |
|  |  |  | Other Industrial Products |
|  |  |  | Glass - Industrial |
|  |  |  | Aluminium, Copper & Zinc Products |
|  |  |  | Iron & Steel Products |
|  |  |  | Abrasives & Bearings |
|  |  |  | Compressors,Pumps & Diesel Engines |
|  |  |  | Electrodes & Refractories |
| Information Technology | Information Technology | IT - Software | Computers - Software & Consulting |
|  |  |  | Software Products |
|  |  | IT - Services | IT Enabled Services |
|  |  | IT - Hardware | Computers Hardware & Equipments |
| Services | Services | Engineering Services | Dredging |
|  |  | Transport Services | Airline |
|  |  |  | Logistics Solution Provider |
|  |  |  | Railways |
|  |  |  | Road Transport |
|  |  |  | Shipping |
|  |  |  | Transport Related Services |
|  |  | Transport Infrastructure | Airport & Airport services |
|  |  |  | Port & Port services |
|  |  |  | Road Assets-Toll, Annuity, HybridAnnuity |
|  |  | Commercial Services & Supplies | Trading & Distributors |
|  |  |  | Consulting Services |
|  |  |  | Data Processing Services |
|  |  |  | Diversified Commercial Services |
|  |  |  | Business Process Outsourcing (BPO)/ Knowledge Process Outsourcing (KPO) |
|  |  | Public Services | Urban Local Bodies |
|  |  |  | Development Authority |
| Telecommunication | Telecommunication | Telecom - Services | Telecom - Cellular & Fixed line services |
|  |  |  | Telecom - Infrastructure |
|  |  |  | Other Telecom Services |
|  |  | Telecom - Equipment & Accessories | Telecom - Equipment & Accessories |
| Utilities | Power | Power | Power Generation |
|  |  |  | Integrated Power Utilities |
|  |  |  | Power Trading |
|  |  |  | Power - Transmission |
|  |  |  | Power Distribution |
|  | Utilities | Other Utilities | Water Supply & Management |
|  |  |  | Waste Management |
|  |  |  | Emergency Services |
|  |  |  | Multi Utilities |
|  |  |  | Other Utilities |
| Diversified | Diversified | Diversified | Diversified |


## Available Screener Fields

### Instrument Properties

| Field | Description | Data Type | Supported Operations |
|--- |--- |--- |--- |
| `exchange` | Stock exchange where the instrument is traded | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `tradingSymbol` | Trading symbol of the instrument | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `macroEconomicSector` | Macro economic sector classification | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `sector` | Sector classification | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `industry` | Industry classification | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `basicIndustry` | Basic industry classification | String | `$eq`, `$ne`, `$in`, `$nin`, `$like`, `$nlike`, `$ilike` |
| `indices` | List of indices the instrument belongs to | Array(String) | `$in`, `$nin` |
| `issuedSize` | Total issued shares (listed shares count) | UInt64 | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `marketCap` | Logarithm of Market Capitalization | Nullable(Float64) | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Financial Data

| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `reportDate` | Date of the financial report | Date | - | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `latestReportDate_daily` | Date of the latest financial report (daily derived) | Date | - | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `companyName` | Company name | String | - | `$eq`, `$ne`, `$like`, `$nlike`, `$ilike` |
| `period` | Financial reporting period (Q1, Q2, Q3, Q4, FY) | String | - | `$eq`, `$ne`, `$in`, `$nin` |
| `filingDate` | Date when the report was filed | Date | - | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `natureOfReport` | Type of financial report (Annual, Quarterly, etc.) | String | - | `$eq`, `$ne`, `$in`, `$nin` |
| `auditedUnaudited` | Audited or Unaudited status of the financial report | String | - | `$eq`, `$ne`, `$in`, `$nin` |

## Banking-Specific Metrics

### Interest Income & Expense
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `interestEarnedQuarterly` | Interest Earned - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `interestEarnedAnnual` | Interest Earned - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `interestExpenseQuarterly` | Interest Expense - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `interestExpenseAnnual` | Interest Expense - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### NPA & Asset Quality
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `grossNpaRatioQuarterly` | Gross NPA Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `grossNpaRatioAnnual` | Gross NPA Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netNpaRatioQuarterly` | Net NPA Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netNpaRatioAnnual` | Net NPA Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `gnpaPct` | Gross Non-Performing Assets Percentage | Float | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Capital Adequacy
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `cet1RatioQuarterly` | CET1 Capital Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cet1RatioAnnual` | CET1 Capital Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `tier1CapitalRatioQuarterly` | Tier 1 Capital Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `tier1CapitalRatioAnnual` | Tier 1 Capital Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalCapitalRatioQuarterly` | Total Capital Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalCapitalRatioAnnual` | Total Capital Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Banking Assets & Liabilities
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `advancesQuarterly` | Advances - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `advancesAnnual` | Advances - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `depositsQuarterly` | Deposits - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `depositsAnnual` | Deposits - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `investmentsQuarterly` | Investments - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `investmentsAnnual` | Investments - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashBankBalanceQuarterly` | Cash and Bank Balance - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashBankBalanceAnnual` | Cash and Bank Balance - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Balance Sheet Items

### Fixed Assets
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `ppeQuarterly` | Property, Plant & Equipment - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ppeAnnual` | Property, Plant & Equipment - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `goodwillQuarterly` | Goodwill - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `goodwillAnnual` | Goodwill - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `intangibleAssetsQuarterly` | Intangible Assets - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `intangibleAssetsAnnual` | Intangible Assets - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cwipQuarterly` | Capital Work in Progress - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cwipAnnual` | Capital Work in Progress - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `intangiblesUnderDevQuarterly` | Intangibles Under Development - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `intangiblesUnderDevAnnual` | Intangibles Under Development - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `investmentPropertyQuarterly` | Investment Property - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `investmentPropertyAnnual` | Investment Property - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Current Assets
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `inventoriesQuarterly` | Inventories - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `inventoriesAnnual` | Inventories - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `tradeReceivablesQuarterly` | Trade Receivables - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `tradeReceivablesAnnual` | Trade Receivables - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherReceivablesQuarterly` | Other Receivables - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherReceivablesAnnual` | Other Receivables - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashEquivalentsQuarterly` | Cash and Cash Equivalents - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashEquivalentsAnnual` | Cash and Cash Equivalents - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Total Assets & Equity
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `bookValue` | Book Value | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `shareholderEquity` | Shareholder Equity | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalAssetsQuarterly` | Total Assets - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalAssetsAnnual` | Total Assets - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalEquityQuarterly` | Total Equity - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalEquityAnnual` | Total Equity - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `equityShareCapitalQuarterly` | Equity Share Capital - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `equityShareCapitalAnnual` | Equity Share Capital - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalLiabilitiesQuarterly` | Total Liabilities - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalLiabilitiesAnnual` | Total Liabilities - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Debt & Cash
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `totalDebt` | Total Debt | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netCash` | Net Cash (Cash - Total Debt) | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Income Statement Items

### Revenue & Income
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `revenue` | Total Revenue | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `revenueOperationsQuarterly` | Revenue from Operations - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `revenueOperationsAnnual` | Revenue from Operations - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherIncomeQuarterly` | Other Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherIncomeAnnual` | Other Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalIncomeQuarterly` | Total Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalIncomeAnnual` | Total Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dividendIncomeQuarterly` | Dividend Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dividendIncomeAnnual` | Dividend Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Expenses
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `materialCostQuarterly` | Material Cost - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `materialCostAnnual` | Material Cost - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `employeeExpenseQuarterly` | Employee Expenses - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `employeeExpenseAnnual` | Employee Expenses - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `financeCostsQuarterly` | Finance Costs - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `financeCostsAnnual` | Finance Costs - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `depreciationAmortisationQuarterly` | Depreciation & Amortisation - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `depreciationAmortisationAnnual` | Depreciation & Amortisation - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherExpensesQuarterly` | Other Expenses - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherExpensesAnnual` | Other Expenses - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalExpensesQuarterly` | Total Expenses - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `totalExpensesAnnual` | Total Expenses - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Profit & Loss
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `profitBeforeTaxQuarterly` | Profit Before Tax - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `profitBeforeTaxAnnual` | Profit Before Tax - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentTaxQuarterly` | Current Tax - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentTaxAnnual` | Current Tax - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `deferredTaxQuarterly` | Deferred Tax - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `deferredTaxAnnual` | Deferred Tax - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `taxExpenseQuarterly` | Tax Expense - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `taxExpenseAnnual` | Tax Expense - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netIncome` | Net Income | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netProfitQuarterly` | Net Profit - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netProfitAnnual` | Net Profit - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Cash Flow Statement

### Operating Activities
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `operatingCashFlowQuarterly` | Operating Cash Flow - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `operatingCashFlowAnnual` | Operating Cash Flow - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netOperatingCashQuarterly` | Net Operating Cash - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netOperatingCashAnnual` | Net Operating Cash - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Investing Activities
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `investingCashFlowQuarterly` | Investing Cash Flow - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `investingCashFlowAnnual` | Investing Cash Flow - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ppePurchasesQuarterly` | PPE Purchases - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ppePurchasesAnnual` | PPE Purchases - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ppeSaleProceedsQuarterly` | PPE Sale Proceeds - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ppeSaleProceedsAnnual` | PPE Sale Proceeds - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `purchaseInvestmentsQuarterly` | Purchase of Investments - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `purchaseInvestmentsAnnual` | Purchase of Investments - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `saleInvestmentsQuarterly` | Sale of Investments - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `saleInvestmentsAnnual` | Sale of Investments - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Financing Activities
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `financingCashFlowQuarterly` | Financing Cash Flow - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `financingCashFlowAnnual` | Financing Cash Flow - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `borrowingProceedsQuarterly` | Borrowing Proceeds - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `borrowingProceedsAnnual` | Borrowing Proceeds - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `borrowingRepaymentsQuarterly` | Borrowing Repayments - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `borrowingRepaymentsAnnual` | Borrowing Repayments - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dividendsPaidQuarterly` | Dividends Paid - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dividendsPaidAnnual` | Dividends Paid - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `shareIssueProceedsQuarterly` | Share Issue Proceeds - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `shareIssueProceedsAnnual` | Share Issue Proceeds - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `shareBuybackQuarterly` | Share Buyback - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `shareBuybackAnnual` | Share Buyback - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Net Cash Changes
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `freeCashFlow` | Free Cash Flow | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netCashChangeQuarterly` | Net Cash Change - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netCashChangeAnnual` | Net Cash Change - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashCashflowStmtQuarterly` | Cash from Cashflow Statement - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `cashCashflowStmtAnnual` | Cash from Cashflow Statement - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## NBFC-Specific Metrics

### Revenue & Income
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `feesCommissionIncomeQuarterly` | Fees & Commission Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `feesCommissionIncomeAnnual` | Fees & Commission Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `fairValueGainsQuarterly` | Fair Value Gains - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `fairValueGainsAnnual` | Fair Value Gains - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `rentalIncomeQuarterly` | Rental Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `rentalIncomeAnnual` | Rental Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Expenses
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `feesCommissionExpenseQuarterly` | Fees & Commission Expense - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `feesCommissionExpenseAnnual` | Fees & Commission Expense - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `fairValueLossesQuarterly` | Fair Value Losses - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `fairValueLossesAnnual` | Fair Value Losses - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `impairmentFinancialInstrumentsQuarterly` | Impairment of Financial Instruments - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `impairmentFinancialInstrumentsAnnual` | Impairment of Financial Instruments - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### NBFC Assets
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `loansQuarterly` | Loans - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `loansAnnual` | Loans - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherFinancialAssetsQuarterly` | Other Financial Assets - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `otherFinancialAssetsAnnual` | Other Financial Assets - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Insurance-Specific Metrics

### Premium Income
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `grossPremiumIncomeQuarterly` | Gross Premium Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `grossPremiumIncomeAnnual` | Gross Premium Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netPremiumIncomeQuarterly` | Net Premium Income - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `netPremiumIncomeAnnual` | Net Premium Income - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Insurance Ratios
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `solvencyRatioQuarterly` | Solvency Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `solvencyRatioAnnual` | Solvency Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `expensesOfManagementRatioQuarterly` | Expenses of Management Ratio - quarterly | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `expensesOfManagementRatioAnnual` | Expenses of Management Ratio - annual | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Financial Ratios



### Leverage Ratios
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `debtEquityRatioQuarterly` | Debt to Equity Ratio - quarterly | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `debtEquityRatioAnnual` | Debt to Equity Ratio - annual | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `debtServiceRatioQuarterly` | Debt Service Ratio - quarterly | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `debtServiceRatioAnnual` | Debt Service Ratio - annual | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `interestCoverageRatioQuarterly` | Interest Coverage Ratio - quarterly | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `interestCoverageRatioAnnual` | Interest Coverage Ratio - annual | Float64 | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Valuation Ratios
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `peRatio` | Price to Earnings Ratio | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `pbRatio` | Price to Book Ratio | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `evEbitda` | Enterprise Value to EBITDA | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `fcfYield` | Free Cash Flow Yield | Float | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Profitability Ratios
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `basicEpsQuarterly` | Basic EPS - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `basicEpsAnnual` | Basic EPS - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dilutedEpsQuarterly` | Diluted EPS - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `dilutedEpsAnnual` | Diluted EPS - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `roe` | Return on Equity | Nullable(Float32) | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `roa` | Return on Assets | Nullable(Float32) | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ebitda` | Earnings Before Interest, Taxes, Depreciation, and Amortization | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ebitMargin` | Earnings Before Interest and Taxes Margin | Nullable(Float32) | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `EPS` | Earnings Per Share | Nullable(Float64) | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `epsCagr` | EPS Compounded Annual Growth Rate | Float | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Efficiency Ratios
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `assetTurnover` | Asset Turnover Ratio | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentRatio` | Current Ratio | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ocfNPRatio` | Operating Cash Flow to Net Profit Ratio | Nullable(Float64) | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `ocfPat` | Operating Cash Flow to PAT Ratio | Float | ratio | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Shareholding Patterns

#### Current Holdings
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `currentFiiHoldings` | Current FII holdings percentage (latest quarter) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentDiiHoldings` | Current DII holdings percentage (latest quarter) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentPromoterHoldings` | Current Promoter holdings percentage (latest quarter) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `currentInstitutionalHoldings` | Current total institutional holdings percentage (latest quarter) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `freeFloatPercentage` | Free float percentage (latest quarter) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `freeFloatMarketCap` | Free-float market capitalization (latest trading day) | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

#### Quarter-on-Quarter Changes
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `qoqInstitutionalChange` | Quarter-on-quarter change in institutional holdings (%) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `qoqFiiChange` | Quarter-on-quarter change in FII holdings (%) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `qoqDiiChange` | Quarter-on-quarter change in DII holdings (%) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `qoqPromoterChange` | Quarter-on-quarter change in Promoter holdings (%) | Float64 | % | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

## Segment Analysis

### Segment Financial Data
| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `segmentRevenueQuarterly` | Segment Revenue - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentRevenueAnnual` | Segment Revenue - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentProfitBeforeTaxQuarterly` | Segment Profit Before Tax - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentProfitBeforeTaxAnnual` | Segment Profit Before Tax - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentAssetsQuarterly` | Segment Assets - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentAssetsAnnual` | Segment Assets - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentLiabilitiesQuarterly` | Segment Liabilities - quarterly | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `segmentLiabilitiesAnnual` | Segment Liabilities - annual | Float64 | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Historical Market Data

| Field | Description | Data Type | Unit | Supported Operations |
|--- |--- |--- |--- |--- |
| `hmdOpen` | Opening price of the trading session | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdHigh` | Highest price during the trading session | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdLow` | Lowest price during the trading session | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdClose` | Closing price of the trading session | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdLtp` | Last Traded Price | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdPrevClose` | Previous day closing price | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdVolume` | Trading volume (number of shares traded) | UInt64 | shares | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdTurnover` | Trading turnover (total value of shares traded) | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdTotalTrades` | Total number of trades executed | UInt64 | count | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdPriceBandLower` | Lower price band limit | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdPriceBandUpper` | Upper price band limit | Float | currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `hmdDate` | Trading date | Date | - | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |
| `MarketCap` | Logarithm of Market Capitalization | Float64 | log_currency | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$between` |

### Supported Operations

- **Comparison**: `$eq` (equal), `$ne` (not equal), `$gt` (greater than), `$gte` (greater than or equal), `$lt` (less than), `$lte` (less than or equal)
- **Range**: `$between` (between two values)
- **Array**: `$in` (in array), `$nin` (not in array)
- **Pattern**: `$like` (case-sensitive pattern), `$nlike` (case-sensitive not pattern), `$ilike` (case-insensitive pattern)
- **Logical**: `$and` (all conditions must be true), `$or` (at least one condition must be true)

### Example Usage

```python
# Get all available screener fields
fields = client.get_screener_fields()
print(json.dumps(fields, indent=2))

# Screen for high ROE companies in Finance sector
results = client.run_screener(
    filters={
        "$and": [
            {"sector": {"$eq": "Finance"}},
            {"roe": {"$gt": 0.15}}
        ]
    },
    sort=[{"roe": -1}],
    limit=10
)
```

## KV Store Integration

The WizzerClient includes comprehensive Key-Value (KV) store functionality for persistent data management. This feature allows you to store configuration data, state information, user preferences, and other persistent data associated with your trading strategies.

### Supported Data Types

The KV store supports all JSON-serializable data types:

- **STRING**: Text values (`"production"`, `"user123"`)
- **NUMBER**: Integer and float values (`42`, `150.25`)
- **BOOLEAN**: True/false values (`True`, `False`)
- **ARRAY**: Lists of values (`["AAPL", "GOOGL", "MSFT"]`)
- **OBJECT**: Dictionaries/objects (`{"positions": 30, "cash": 50000}`)

### Available Constants

```python
client.KV_TYPE_STRING   # "string"
client.KV_TYPE_NUMBER   # "number" 
client.KV_TYPE_BOOLEAN  # "boolean"
client.KV_TYPE_ARRAY    # "array"
client.KV_TYPE_OBJECT   # "object"
```

### Core CRUD Operations

#### Create Key-Value Pair

```python
# Store different data types
client.create_kv("environment", "production")
client.create_kv("trade_count", 42)
client.create_kv("is_active", True)
client.create_kv("symbols", ["AAPL", "GOOGL", "MSFT"])

# Store complex configuration with TTL (expires in 1 hour)
config = {
    "risk_level": "medium",
    "max_positions": 10,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.15
}
client.create_kv("strategy_config", config, ttl=3600)
```

#### Retrieve Key-Value Pair

```python
# Get a single KV pair
data = client.get_kv("strategy_config")
print(data["value"])          # The stored object
print(data["type"])           # "object"
print(data["ttl"])            # Remaining time to live (if set)

# Access nested values
risk_level = data["value"]["risk_level"]  # "medium"
```

#### Update Key-Value Pair (Complete Replacement)

```python
# Complete replacement of existing key
new_config = {"risk_level": "high", "max_positions": 5}
client.update_kv("strategy_config", new_config, ttl=1800)
```

#### Patch Key-Value Pair (Partial Update)

```python
# For objects - merges with existing data
client.patch_kv("strategy_config", {"last_updated": "2024-01-15"})

# For non-objects - replaces entirely  
client.patch_kv("trade_count", 50)

# Update only TTL
client.patch_kv("strategy_config", ttl=7200)
```

#### Delete Key-Value Pair

```python
response = client.delete_kv("old_config")
if response["success"]:
    print("Key deleted successfully")
```

### List Operations

#### Get All KV Pairs (with values)

```python
# Get first page (20 items)
kvs = client.get_all_kvs(page_no=1)

# Get all pages automatically
all_kvs = client.get_all_kvs(paginate=True)

for kv in all_kvs:
    print(f"Key: {kv['key']}")
    print(f"Type: {kv['type']}")
    print(f"Value: {kv['value']}")
```

#### Get Keys Only (memory efficient)

```python
# Get all keys without values (faster for large datasets)
keys = client.get_kv_keys(paginate=True)

for key_info in keys:
    print(f"Key: {key_info['key']}, Type: {key_info['type']}")
    if 'ttl' in key_info:
        print(f"  TTL: {key_info['ttl']} seconds remaining")
```

### Advanced Usage Examples

#### Strategy Configuration Management

```python
# Store strategy parameters
params = {
    "moving_average_period": 20,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "position_size": 0.02
}
client.create_kv("strategy_params", params)

# Update specific parameters using patch (merges with existing)
client.patch_kv("strategy_params", {"moving_average_period": 50})
```

#### State Persistence

```python
# Save current portfolio state
portfolio_state = {
    "cash_balance": 50000,
    "open_positions": 5,
    "daily_pnl": 1250.75,
    "last_updated": "2024-01-15T15:30:00Z"
}
client.create_kv("portfolio_state", portfolio_state, ttl=3600)

# Update state periodically
client.patch_kv("portfolio_state", {
    "daily_pnl": 1500.25,
    "last_updated": "2024-01-15T16:00:00Z"
})
```

#### Feature Flags

```python
# Enable/disable features dynamically
features = {
    "advanced_charts": True,
    "paper_trading": True,
    "options_trading": False,
    "algo_trading": True
}
client.create_kv("feature_flags", features)

# Toggle a feature
client.patch_kv("feature_flags", {"options_trading": True})
```

#### Data Caching with TTL

```python
# Cache market data with short TTL (5 minutes)
market_status = {
    "nse_open": True,
    "bse_open": True,
    "last_checked": "2024-01-15T09:15:00Z"
}
client.create_kv("market_status", market_status, ttl=300)
```

### Object Merge Behavior

For OBJECT type data, the `patch_kv` method performs intelligent merging:

```python
# Initial object
client.create_kv("user_prefs", {
    "theme": "dark",
    "notifications": True,
    "language": "en"
})

# Patch merges new fields with existing ones
client.patch_kv("user_prefs", {
    "notifications": False,  # Updates existing field
    "timezone": "UTC"        # Adds new field
})

# Result: {"theme": "dark", "notifications": False, "language": "en", "timezone": "UTC"}
```

### Delete All KV Pairs

The `delete_all_kv` method allows you to remove all key-value pairs for a strategy at once:

```python
# Delete all KV pairs for the current strategy
response = client.delete_all_kv()
print(f"Deleted {response['deleted']} key-value pairs")

# Example response:
# {
#     "success": True,
#     "deleted": 15,
#     "message": "Successfully deleted 15 key-value pairs"
# }

# Common usage - reset strategy state before reinitialization
def reset_strategy_state():
    """Reset all persistent state for the strategy."""
    # Clear all existing KV pairs
    result = client.delete_all_kv()
    print(f"Cleared {result['deleted']} KV pairs")
    
    # Reinitialize with default configuration
    client.create_kv("config", {
        "mode": "production",
        "risk_percentage": 0.02,
        "max_positions": 10
    })
    client.create_kv("state", {
        "initialized": True,
        "start_time": datetime.now().isoformat()
    })
    print("Strategy state reset successfully")

# Use with caution - this operation cannot be undone!
```
