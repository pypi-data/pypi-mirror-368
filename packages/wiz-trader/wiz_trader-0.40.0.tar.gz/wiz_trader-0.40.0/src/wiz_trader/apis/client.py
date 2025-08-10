import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import requests

# Setup module-level logger with a default handler if none exists.
logger = logging.getLogger(__name__)
if not logger.handlers:
  handler = logging.StreamHandler()
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)

class WizzerClient:
  """
  A Python SDK for connecting to the Wizzer's REST API.

  Attributes:
    base_url (str): Base URL of the Wizzer's API server.
    token (str): JWT token for authentication.
    log_level (str): Logging level. Options: "error", "info", "debug".
    strategy_id (str): Default strategy ID to use if not provided in methods.
  """
  
  # Constants
  # Transaction types
  TRANSACTION_TYPE_BUY = "BUY"
  TRANSACTION_TYPE_SELL = "SELL"

  # Product types
  PRODUCT_CNC = "CNC"         # Cash and Carry
  PRODUCT_MIS = "MIS"         # Margin Intraday Square-off
  PRODUCT_NRML = "NRML"       # Normal / Overnight Futures and Options

  # Order types
  ORDER_TYPE_MARKET = "MARKET"
  ORDER_TYPE_LIMIT = "LIMIT"
  ORDER_TYPE_SL = "STOPLIMIT"        # Stop Loss
  ORDER_TYPE_SLM = "STOPMARKET"      # Stop Loss Market

  # Validity types
  VALIDITY_DAY = "DAY"
  VALIDITY_IOC = "IOC"        # Immediate or Cancel
  VALIDITY_GTT = "GTT"        # Good Till Triggered

  # Variety types
  VARIETY_REGULAR = "REGULAR"
  VARIETY_AMO = "AMO"         # After Market Order
  VARIETY_BO = "BO"           # Bracket Order
  VARIETY_CO = "CO"           # Cover Order

  # Exchanges
  EXCHANGE_NSE = "NSE"        # National Stock Exchange
  EXCHANGE_BSE = "BSE"        # Bombay Stock Exchange
  EXCHANGE_WZR = "WZR"        # Wizzer Exchange (for baskets)

  # Segments
  SEGMENT_NSE_CM = "NSECM"    # NSE Cash Market
  SEGMENT_BSE_CM = "BSECM"    # BSE Cash Market
  SEGMENT_NSE_FO = "NSEFO"    # NSE Futures and Options
  SEGMENT_WZREQ = "WZREQ"     # Wizzer Basket Segment
  
  # Order status constants
  ORDER_STATUS_OPEN = "OPEN"
  ORDER_STATUS_CANCELLED = "CANCELLED" 
  ORDER_STATUS_REJECTED = "REJECTED"
  ORDER_STATUS_PENDING = "PENDING"
  ORDER_STATUS_COMPLETED = "COMPLETED"

  # Trading mode constants
  TRADING_MODE_PAPER = "paper_trading"
  TRADING_MODE_ADVICES = "advices"
  TRADING_MODE_TRADING_AND_ADVICES = "trading_and_advices"
  
  # Rebalance execution policies
  REBALANCE_FULL = "full_rebalance"
  REBALANCE_ENTRY_ONLY = "entry_only"
  REBALANCE_EXIT_ONLY = "exit_only"
  
  # Add constants for option types and moneyness
  OPTION_TYPE_CE = "CE"
  OPTION_TYPE_PE = "PE"

  MONEYNESS_ATM = "ATM"
  MONEYNESS_ITM = "ITM" 
  MONEYNESS_OTM = "OTM"
  
  # Expiry preference constants
  EXPIRY_CURRENT_WEEKLY = "current_weekly"
  EXPIRY_NEAR_MONTH = "near_month"
  EXPIRY_MID_MONTH = "mid_month"
  EXPIRY_FAR_MONTH = "far_month"
  EXPIRY_FIRST_WEEKLY = "first_weekly"
  EXPIRY_SECOND_WEEKLY = "second_weekly"
  EXPIRY_THIRD_WEEKLY = "third_weekly"
  EXPIRY_FOURTH_WEEKLY = "fourth_weekly"
  EXPIRY_FIFTH_WEEKLY = "fifth_weekly"
  EXPIRY_FIRST_WEEKLY_MID_MONTH = "first_weekly_mid_month"
  EXPIRY_SECOND_WEEKLY_MID_MONTH = "second_weekly_mid_month"
  EXPIRY_THIRD_WEEKLY_MID_MONTH = "third_weekly_mid_month"
  EXPIRY_FOURTH_WEEKLY_MID_MONTH = "fourth_weekly_mid_month"
  EXPIRY_FIFTH_WEEKLY_MID_MONTH = "fifth_weekly_mid_month"
  EXPIRY_FIRST_WEEKLY_FAR_MONTH = "first_weekly_far_month"
  EXPIRY_SECOND_WEEKLY_FAR_MONTH = "second_weekly_far_month"
  EXPIRY_THIRD_WEEKLY_FAR_MONTH = "third_weekly_far_month"
  EXPIRY_FOURTH_WEEKLY_FAR_MONTH = "fourth_weekly_far_month"
  EXPIRY_FIFTH_WEEKLY_FAR_MONTH = "fifth_weekly_far_month"
  EXPIRY_FIRST_QUARTER = "first_quarter"
  EXPIRY_SECOND_QUARTER = "second_quarter"
  EXPIRY_THIRD_QUARTER = "third_quarter"
  EXPIRY_FOURTH_QUARTER = "fourth_quarter"
  EXPIRY_FIRST_HALF = "first_half_yearly"
  EXPIRY_SECOND_HALF = "second_half_yearly"
  EXPIRY_FIRST_QUARTER_PLUS_1 = "first_quarter_plus_1"
  EXPIRY_SECOND_QUARTER_PLUS_1 = "second_quarter_plus_1"
  EXPIRY_THIRD_QUARTER_PLUS_1 = "third_quarter_plus_1"
  EXPIRY_FOURTH_QUARTER_PLUS_1 = "fourth_quarter_plus_1"
  EXPIRY_FIRST_HALF_PLUS_1 = "first_half_yearly_plus_1"
  EXPIRY_SECOND_HALF_PLUS_1 = "second_half_yearly_plus_1"
  EXPIRY_FIRST_QUARTER_PLUS_2 = "first_quarter_plus_2"
  EXPIRY_SECOND_QUARTER_PLUS_2 = "second_quarter_plus_2"
  EXPIRY_THIRD_QUARTER_PLUS_2 = "third_quarter_plus_2"
  EXPIRY_FOURTH_QUARTER_PLUS_2 = "fourth_quarter_plus_2"
  EXPIRY_FIRST_HALF_PLUS_2 = "first_half_yearly_plus_2"
  EXPIRY_SECOND_HALF_PLUS_2 = "second_half_yearly_plus_2"
  EXPIRY_FIRST_QUARTER_PLUS_3 = "first_quarter_plus_3"
  EXPIRY_SECOND_QUARTER_PLUS_3 = "second_quarter_plus_3"
  EXPIRY_THIRD_QUARTER_PLUS_3 = "third_quarter_plus_3"
  EXPIRY_FOURTH_QUARTER_PLUS_3 = "fourth_quarter_plus_3"
  EXPIRY_FIRST_HALF_PLUS_3 = "first_half_yearly_plus_3"
  EXPIRY_SECOND_HALF_PLUS_3 = "second_half_yearly_plus_3"
  EXPIRY_FIRST_QUARTER_PLUS_4 = "first_quarter_plus_4"
  EXPIRY_SECOND_QUARTER_PLUS_4 = "second_quarter_plus_4"
  EXPIRY_THIRD_QUARTER_PLUS_4 = "third_quarter_plus_4"
  EXPIRY_FOURTH_QUARTER_PLUS_4 = "fourth_quarter_plus_4"
  EXPIRY_FIRST_HALF_PLUS_4 = "first_half_yearly_plus_4"
  EXPIRY_SECOND_HALF_PLUS_4 = "second_half_yearly_plus_4"
  
  # Historical data interval constants
  INTERVAL_1_MINUTE = "1m"
  INTERVAL_2_MINUTES = "2m"
  INTERVAL_3_MINUTES = "3m"
  INTERVAL_5_MINUTES = "5m"
  INTERVAL_10_MINUTES = "10m"
  INTERVAL_15_MINUTES = "15m"
  INTERVAL_30_MINUTES = "30m"
  INTERVAL_45_MINUTES = "45m"
  INTERVAL_1_HOUR = "1h"
  INTERVAL_1_DAY = "1d"
  INTERVAL_1_MONTH = "1M"
  
  # Constants for weightage schemes
  WEIGHTAGE_SCHEME_EQUI_WEIGHTED = "equi_weighted"
  WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED = "quantity_weighted"
  WEIGHTAGE_SCHEME_PRICE_WEIGHTED = "price_weighted"
  WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED = "market_cap_weighted"
  WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED = "float_adjusted_market_cap_weighted"
  WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED = "fundamental_weighted"
  WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED = "custom_weighted"
  
  # KV data type constants
  KV_TYPE_STRING = "string"
  KV_TYPE_BOOLEAN = "boolean"
  KV_TYPE_NUMBER = "number"
  KV_TYPE_ARRAY = "array"
  KV_TYPE_OBJECT = "object"

  # URIs to various API endpoints
  _routes = {
    # Order related endpoints
    "order.place": "/orders",
    "order.get": "/orders",
    "order.modify": "/orders/{order_id}",
    "order.cancel": "/orders/{order_id}",
    "order.info": "/orders/{order_id}",
    
    # Basket order endpoints
    "basket.order.place": "/orders/basket",
    "basket.order.exit": "/orders/basket/exit",
    "basket.order.modify": "/orders/basket/{order_id}",
    
    # Portfolio and position management
    "portfolio.positions": "/portfolios/positions",
    "portfolio.positions.exit.all": "/portfolios/positions/exit/all",
    "portfolio.positions.exit.strategy": "/portfolios/positions/exit/strategies/{strategy_id}",
    "portfolio.holdings": "/portfolios/holdings",
    
    # Basket management
    "basket.create": "/baskets",
    "basket.list": "/baskets",
    "basket.info": "/baskets/{basket_id}",
    "basket.instruments": "/baskets/{basket_id}/instruments",
    "basket.rebalance": "/baskets/rebalance",
    
    # Data hub endpoints
    "datahub.indices": "/datahub/indices",
    "datahub.index.components": "/datahub/index/components",
    "datahub.historical.ohlcv": "/datahub/historical/ohlcv",
    
    # Instrument & asset class endpoints
    "instrument.metrics": "/instruments/metrics",
    "instrument.option_chain": "/instruments/options/chain",
    "instrument.expiry_list": "/instruments/options/chain/expirylist",
    "instrument.future_list": "/instruments/futures/list",

    # Classification API endpoints
    "classification.types": "/datahub/classifications/types",
    "classification.values": "/datahub/classifications/{type}",
    "indices.filter": "/datahub/indices/filter",
    "instruments.filter": "/datahub/instruments/filter",
    "instruments.filter_with_index": "/datahub/indices/{id}/instruments",
    "instruments.filter_by_derivatives": "/datahub/instruments/filter-by-derivatives",
    
    # Screener API endpoints
    "screener.run": "/datahub/screener",
    "screener.fields": "/datahub/screener/metadata",
    
    # KV store endpoints
    "kv.create": "/kv/{strategy_id}/{key}",
    "kv.get": "/kv/{strategy_id}/{key}",
    "kv.update": "/kv/{strategy_id}/{key}",
    "kv.patch": "/kv/{strategy_id}/{key}",
    "kv.delete": "/kv/{strategy_id}/{key}",
    "kv.list": "/kv/{strategy_id}",
    "kv.keys": "/kv/{strategy_id}/keys",
    "kv.delete_all": "/kv/{strategy_id}/all",
    
    # Analytics API endpoints - Fundamentals
    "analytics.fundamentals.net_profit_margin": "/analytics/fundamentals/margins/netProfit",
    "analytics.fundamentals.roe": "/analytics/fundamentals/roe",
    "analytics.fundamentals.roa": "/analytics/fundamentals/roa",
    "analytics.fundamentals.ebit_margin": "/analytics/fundamentals/ebit-margin",
    "analytics.fundamentals.ocf_netprofit_ratio": "/analytics/fundamentals/ocf-netprofit-ratio",
    "analytics.fundamentals.eps_cagr": "/analytics/fundamentals/eps-cagr",
    "analytics.fundamentals.book_to_market": "/analytics/fundamentals/valuation/book-to-market",
    "analytics.fundamentals.marketcap_to_sales": "/analytics/fundamentals/valuation/marketcap-to-sales",
    "analytics.fundamentals.cash_to_marketcap": "/analytics/fundamentals/liquidity/cash-to-marketcap",
    
    # Analytics API endpoints - Valuation
    "analytics.valuation.pe_ratio": "/analytics/valuation/pe-ratio",
    "analytics.valuation.pb_ratio": "/analytics/valuation/pb-ratio",
    "analytics.valuation.ev_ebitda": "/analytics/valuation/ev-ebitda",
    "analytics.valuation.fcf_yield": "/analytics/valuation/fcf-yield",
    
    # Analytics API endpoints - Returns
    "analytics.returns.quarterly": "/analytics/returns/quarterly",
    "analytics.returns.monthly": "/analytics/returns/monthly",
    "analytics.returns.cagr": "/analytics/returns/cagr",
    
    # Analytics API endpoints - Market Data
    "analytics.marketdata.ohlcv_daily": "/analytics/marketdata/ohlcv-daily",
    "analytics.marketdata.historical_prices": "/analytics/marketdata/historical-prices",
    "analytics.marketdata.free_float_market_cap": "/analytics/marketdata/free-float-market-cap",
    "analytics.marketdata.index_ohlc_daily": "/analytics/marketdata/index-ohlc-daily",
    
    # Analytics API endpoints - Ownership
    "analytics.ownership.fii_dii": "/analytics/ownership/fii-dii",
    "analytics.ownership.fii_change": "/analytics/ownership/fii-change",
    "analytics.ownership.dii_change": "/analytics/ownership/dii-change",
    
    # Analytics API endpoints - Metrics
    "analytics.metrics.sortino_ratio": "/analytics/metrics/sortino-ratio",
    "analytics.metrics.upside_capture": "/analytics/metrics/upside-capture",
    
    # Analytics API endpoints - Macro
    "analytics.macro.risk_free_rate": "/analytics/macro/rates/risk-free",
    
    # Analytics API endpoints - Risk
    "analytics.risk.max_drawdown": "/analytics/risk/maxDrawdown",
    "analytics.risk.returns_volatility": "/analytics/risk/returnsVolatility",
    
    # Analytics API endpoints - Metadata
    "analytics.metadata.sector": "/analytics/metadata/sector",
    
    # Analytics API endpoints - Leverage
    "analytics.leverage.debt_equity_ratio": "/analytics/leverage/debtEquityRatio",
    
    # Analytics API endpoints - New Additions
    "analytics.marketdata.average_volume": "/analytics/marketdata/averageVolume",
    "analytics.index.max_drawdown": "/analytics/index/metrics/maxDrawdown",
    "analytics.instrument.drawdown_duration": "/analytics/instrument/metrics/drawdownDuration",
    "analytics.price.rolling_peak": "/analytics/price/rollingPeak",
    "analytics.price.rolling_mean": "/analytics/price/rollingMean",
    "analytics.volatility.realized": "/analytics/volatility/realized",
    "analytics.risk.beta_90d": "/analytics/risk/beta90d",
    "analytics.risk.beta_custom": "/analytics/risk/beta",
    "analytics.strategy.drawdown_max": "/analytics/strategy/drawdown/max",
    "analytics.product.drawdown_max": "/analytics/product/drawdown/max",
    "analytics.volatility.atr": "/analytics/volatility/atr",
    "analytics.returns.simple": "/analytics/returns/simple",
    
  }
  
  def __init__(
    self,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    strategy_id: Optional[str] = None,
    log_level: str = "error"  # default only errors
  ):
    # Configure logger based on log_level.
    valid_levels = {"error": logging.ERROR, "info": logging.INFO, "debug": logging.DEBUG}
    if log_level not in valid_levels:
      raise ValueError(f"log_level must be one of {list(valid_levels.keys())}")
    logger.setLevel(valid_levels[log_level])

    self.log_level = log_level
    # System env vars take precedence over .env
    self.base_url = base_url or os.environ.get("WZ__API_BASE_URL")
    self.token = token or os.environ.get("WZ__TOKEN")
    self.strategy_id = strategy_id or os.environ.get("WZ__STRATEGY_ID")
    
    if not self.token:
      raise ValueError("JWT token must be provided as an argument or in .env (WZ__TOKEN)")
    if not self.base_url:
      raise ValueError("Base URL must be provided as an argument or in .env (WZ__API_BASE_URL)")

    # Prepare the authorization header
    self.headers = {
      "Authorization": f"Bearer {self.token}",
      "Content-Type": "application/json"
    }

    logger.debug("Initialized WizzerClient with URL: %s", self.base_url)

  def _get_strategy(self, strategy: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Get strategy information, either from the provided parameter or from the default.
    
    Args:
      strategy (Optional[Dict[str, str]]): Strategy object with id, identifier, and name.
    
    Returns:
      Dict[str, str]: A strategy object with at least the id field.
        
    Raises:
      ValueError: If no strategy is provided and no default is set.
    """
    if strategy and "id" in strategy:
      return strategy
    
    if not self.strategy_id:
      raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
    
    return {"id": self.strategy_id}

  def _validate_datetime_format(self, datetime_str: str, interval: str) -> bool:
    """
    Validate datetime format based on interval type.
    
    Args:
      datetime_str (str): The datetime string to validate
      interval (str): The interval type
    
    Returns:
      bool: True if format is valid for the interval
    """
    # For daily and monthly intervals, only date is required
    if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
      try:
        datetime.strptime(datetime_str, "%Y-%m-%d")
        return True
      except ValueError:
        return False
    
    # For intraday intervals, datetime is required
    else:
      try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return True
      except ValueError:
        return False
  
  # ===== DATA HUB METHODS =====

  def get_indices(self, trading_symbol: Optional[str] = None, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of indices available on the exchange.

    Args:
      trading_symbol (Optional[str]): Filter by specific index symbol.
      exchange (Optional[str]): Filter by specific exchange (NSE, BSE).

    Returns:
      List[Dict[str, Any]]: List of index information.
    """
    params = {}
    
    if trading_symbol:
      params["tradingSymbol"] = trading_symbol
    if exchange:
      params["exchange"] = exchange

    logger.debug("Fetching indices with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.indices"], params=params)
    return response

  def get_index_components(self, trading_symbol: str, exchange: str) -> List[Dict[str, Any]]:
    """
    Get list of components (stocks) for a specific index.

    Args:
      trading_symbol (str): Index symbol (e.g., "NIFTY 50").
      exchange (str): Exchange name (NSE, BSE).

    Returns:
       List[Dict[str, Any]]: List of component stocks in the index.
    """
    params = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange
    }

    logger.debug("Fetching index components with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.index.components"], params=params)
    return response
  
  def get_historical_ohlcv(
    self, 
    instruments: List[str], 
    start_date: str, 
    end_date: str, 
    ohlcv: List[str],
    interval: str = "1d",
    continuous: bool = False
  ) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for specified instruments.

    Args:
      instruments (List[str]): List of instrument identifiers (e.g., ["NSE:SBIN:3045"]).
      start_date (str): Start date. For daily/monthly intervals: YYYY-MM-DD format.
                       For intraday intervals: YYYY-MM-DD HH:MM:SS format.
      end_date (str): End date. For daily/monthly intervals: YYYY-MM-DD format.
                     For intraday intervals: YYYY-MM-DD HH:MM:SS format.
      ohlcv (List[str]): List of OHLCV fields to retrieve. 
        Valid values: "open", "high", "low", "close", "volume", "oi" (open interest - F&O only).
      interval (str, optional): Data interval. Options:
        - Intraday: "1m", "2m", "3m", "5m", "10m", "15m", "30m", "45m", "1h"
        - Daily: "1d" (default)
        - Monthly: "1M" (last trading day of month)
        
        Use constants like client.INTERVAL_5_MINUTES, client.INTERVAL_1_DAY, etc.
      continuous (bool, optional): Only relevant for futures. If True, returns continuous data across 
        multiple contract months to form a seamless data stream. Defaults to False.

    Returns:
      List[Dict[str, Any]]: Historical data for requested instruments.
      
      Note:
      - For daily/monthly intervals, the 'date' field contains YYYY-MM-DD.
      - For intraday intervals, the 'date' field contains YYYY-MM-DD HH:MM:SS.
      - The "oi" (open interest) field is only applicable for F&O instruments
      - The "continuous" parameter is only relevant for futures instruments and allows you to get
        backdated data across multiple contract months for a seamless time series

    Raises:
      ValueError: If datetime format doesn't match the interval requirements.
    """
    # Validate datetime formats
    if not self._validate_datetime_format(start_date, interval):
      if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
        raise ValueError(f"For interval '{interval}', start_date must be in YYYY-MM-DD format")
      else:
        raise ValueError(f"For interval '{interval}', start_date must be in YYYY-MM-DD HH:MM:SS format")
    
    if not self._validate_datetime_format(end_date, interval):
      if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
        raise ValueError(f"For interval '{interval}', end_date must be in YYYY-MM-DD format")
      else:
        raise ValueError(f"For interval '{interval}', end_date must be in YYYY-MM-DD HH:MM:SS format")

    endpoint = self._routes["datahub.historical.ohlcv"]
    data = {
      "instruments": instruments,
      "startDate": start_date,
      "endDate": end_date,
      "ohlcv": ohlcv,
      "interval": interval
    }
    
    # Add continuous parameter if specified
    if continuous:
      data["continuous"] = continuous

    logger.debug("Fetching historical OHLCV with data: %s", data)
    response = self._make_request("POST", endpoint, json=data)
    return response

  # ===== ORDER MANAGEMENT METHODS =====

  def place_order(
    self,
    exchange: str,
    trading_symbol: str,
    transaction_type: str,
    quantity: int,
    order_type: str = None,
    product: str = None,
    price: float = 0,
    trigger_price: float = 0,
    disclosed_qty: int = 0,
    validity: str = None,
    variety: str = None,
    stoploss: float = 0,
    target: float = 0,
    exchange_token: Optional[int] = None,
    broker: str = None,
    strategy: Optional[Dict[str, str]] = None
  ) -> Dict[str, Any]:
    """
    Place a regular order.
    
    Args:
      exchange (str): Exchange code (e.g., "NSE", "BSE").
      trading_symbol (str): Symbol of the instrument.
      transaction_type (str): "BUY" or "SELL".
      quantity (int): Number of shares to trade.
      order_type (str, optional): Order type (e.g., "MARKET", "LIMIT"). Defaults to MARKET.
      product (str, optional): Product code (e.g., "CNC" for delivery). Defaults to CNC.
      price (float, optional): Price for limit orders. Defaults to 0.
      trigger_price (float, optional): Trigger price for stop orders. Defaults to 0.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      validity (str, optional): Order validity (e.g., "DAY", "IOC"). Defaults to DAY.
      variety (str, optional): Order variety. Defaults to REGULAR.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      segment (Optional[str], optional): Market segment. If None, determined from exchange.
      exchange_token (Optional[int], optional): Exchange token for the instrument.
      broker (str, optional): Broker code.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "exchange": exchange,
      "tradingSymbol": trading_symbol,
      "transactionType": transaction_type,
      "qty": quantity,
      "orderType": order_type,
      "product": product,
      "price": price,
      "triggerPrice": trigger_price,
      "disclosedQty": disclosed_qty,
      "validity": validity,
      "variety": variety,
      "stoploss": stoploss,
      "target": target,
      "strategy": strategy_info
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    logger.debug("Placing order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def cancel_order(self, order_id: str) -> Dict[str, Any]:
    """
    Cancel an existing order.
    
    Args:
      order_id (str): Order ID to cancel.
        
    Returns:
      Dict[str, Any]: Response with the cancelled order ID.
    """
    endpoint = self._routes["order.cancel"].format(order_id=order_id)
    
    logger.debug("Cancelling order: %s", order_id)
    return self._make_request("DELETE", endpoint)

  def get_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      page_no: int = 1,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
              Valid values: "paper_trading", "advices", "trading_and_advices".
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
              Valid values: "OPEN", "CANCELLED", "REJECTED", "PENDING", "COMPLETED".
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format. Defaults to today.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format. Defaults to today.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          page_no (int, optional): Page number for pagination. Defaults to 1.
          paginate (bool, optional): Whether to automatically fetch all pages. Defaults to False.
              
      Returns:
          List[Dict[str, Any]]: List of orders matching the filter criteria.
      """
      endpoint = self._routes["order.get"]
      
      # Build the base parameters without list items
      params = {}
      
      # Handle single parameters
      if from_date:
          params["fromDateRange"] = from_date
      
      if to_date:
          params["toDateRange"] = to_date
      
      if not paginate:
          params["pageNo"] = page_no
      
      # Validate trading modes
      if trading_modes:
          for mode in trading_modes:
              if mode not in [self.TRADING_MODE_PAPER, self.TRADING_MODE_ADVICES, self.TRADING_MODE_TRADING_AND_ADVICES]:
                  raise ValueError(f"Invalid trading mode: {mode}")
      
      # Validate order statuses
      if order_statuses:
          for status in order_statuses:
              if status not in [self.ORDER_STATUS_OPEN, self.ORDER_STATUS_CANCELLED, 
                              self.ORDER_STATUS_REJECTED, self.ORDER_STATUS_PENDING, 
                              self.ORDER_STATUS_COMPLETED]:
                  raise ValueError(f"Invalid order status: {status}")
      
      # Handle pagination with properly formatted parameters
      if paginate:
          return self._paginate_orders(endpoint, params, trading_modes, order_statuses, trading_symbols)
      else:
          logger.debug("Fetching orders with params: %s", params)
          return self._make_request_with_multi_params(
              "GET", 
              endpoint, 
              params=params,
              trading_modes=trading_modes,
              order_statuses=order_statuses, 
              trading_symbols=trading_symbols
          )

  def _make_request_with_multi_params(
      self, 
      method: str, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> Any:
      """
      Make an HTTP request with multiple parameters having the same name.
      
      Args:
          method (str): HTTP method (GET, POST, etc.)
          endpoint (str): API endpoint path.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          Any: Parsed JSON response.
      """
      url = f"{self.base_url}{endpoint}"
      
      # Start with the base parameters
      all_params = params.copy()
      
      # Create a session to manually handle parameter encoding
      session = requests.Session()
      req = requests.Request(method, url, headers=self.headers, params=all_params)
      prepped = req.prepare()
      
      # Build the URL with additional repeated parameters
      query_parts = []
      if prepped.url.find('?') >= 0:
          query_parts.append(prepped.url.split('?', 1)[1])
      
      # Add repeated parameters
      if trading_modes:
          for mode in trading_modes:
              query_parts.append(f"tradingMode={mode}")
      
      if order_statuses:
          for status in order_statuses:
              query_parts.append(f"orderStatus={status}")
      
      if trading_symbols:
          for symbol in trading_symbols:
              query_parts.append(f"tradingSymbols={symbol}")
      
      # Build the final URL
      final_url = prepped.url.split('?')[0]
      if query_parts:
          final_url += '?' + '&'.join(query_parts)
      
      try:
          logger.debug("%s request to %s", method, final_url)
          response = session.send(prepped)
          response.url = final_url
          response.raise_for_status()
          return response.json()
      except requests.RequestException as e:
          logger.error("API request failed: %s", e, exc_info=True)
          if hasattr(e.response, 'text'):
              logger.error("Response content: %s", e.response.text)
          raise

  def _paginate_orders(
      self, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> List[Dict[str, Any]]:
      """
      Internal method to handle pagination for orders API with multi-value parameters.
      
      Args:
          endpoint (str): API endpoint.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          List[Dict[str, Any]]: Combined results from all pages.
      """
      all_orders = []
      page_no = 1
      total_count = None
      page_size = 50  # API returns 50 orders per page
      
      while True:
          current_params = params.copy()
          current_params["pageNo"] = page_no
          logger.debug("Fetching orders page %d", page_no)
          
          # Build the URL with the session to get the properly formatted parameters
          session = requests.Session()
          req = requests.Request("GET", f"{self.base_url}{endpoint}", headers=self.headers, params=current_params)
          prepped = req.prepare()
          
          # Build the URL with additional repeated parameters
          query_parts = []
          if prepped.url.find('?') >= 0:
              query_parts.append(prepped.url.split('?', 1)[1])
          
          # Add repeated parameters
          if trading_modes:
              for mode in trading_modes:
                  query_parts.append(f"tradingMode={mode}")
          
          if order_statuses:
              for status in order_statuses:
                  query_parts.append(f"orderStatus={status}")
          
          if trading_symbols:
              for symbol in trading_symbols:
                  query_parts.append(f"tradingSymbols={symbol}")
          
          # Build the final URL
          final_url = prepped.url.split('?')[0]
          if query_parts:
              final_url += '?' + '&'.join(query_parts)
          
          # Make the request
          try:
              logger.debug("GET request to %s", final_url)
              prepped.url = final_url
              response = session.send(prepped)
              response.raise_for_status()
              
              # Get orders from the current page
              orders = response.json()
              all_orders.extend(orders)
              
              # Check if we need to fetch more pages
              if total_count is None and "X-Total-Count" in response.headers:
                  try:
                      total_count = int(response.headers["X-Total-Count"])
                      logger.debug("Total orders count: %d", total_count)
                  except (ValueError, TypeError):
                      logger.warning("Could not parse X-Total-Count header")
                      break
              
              # If we've fetched all orders or there are no more pages, stop
              if not orders or len(all_orders) >= total_count or total_count is None:
                  break
              
              # Move to the next page
              page_no += 1
              
          except requests.RequestException as e:
              logger.error("API request failed during pagination: %s", e, exc_info=True)
              if hasattr(e.response, 'text'):
                  logger.error("Response content: %s", e.response.text)
              raise
      
      logger.info("Fetched %d orders in total", len(all_orders))
      return all_orders

  def get_open_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get open orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of open orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_OPEN],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_completed_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get completed orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of completed orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_COMPLETED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_pending_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get pending orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of pending orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_PENDING],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_cancelled_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get cancelled orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of cancelled orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_CANCELLED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_rejected_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get rejected orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of rejected orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_REJECTED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_paper_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get paper traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of paper traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_PAPER],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_advised_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get advised orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of advised orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_live_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get live traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of live traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_TRADING_AND_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )
  
  def get_order(self, order_id: str) -> Dict[str, Any]:
    """
    Get details of a specific order by ID.
    
    Args:
      order_id (str): ID of the order to retrieve.
        
    Returns:
      Dict[str, Any]: Order details.
    """
    endpoint = self._routes["order.info"].format(order_id=order_id)
    
    logger.debug("Fetching order: %s", order_id)
    return self._make_request("GET", endpoint)
    
  def get_positions(self, position_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get portfolio positions with optional filtering by status.
    
    Args:
      position_status (Optional[str], optional): Filter positions by status.
        Valid values: "open", "closed". If None, returns all positions.
        
    Returns:
      List[Dict[str, Any]]: List of positions matching the filter criteria.
    """
    endpoint = self._routes["portfolio.positions"]
    params = {}
    
    if position_status:
      if position_status not in ["open", "closed"]:
        raise ValueError("position_status must be either 'open', 'closed', or None")
      params["positionStatus"] = position_status
    
    logger.debug("Fetching positions with status: %s", position_status or "all")
    return self._make_request("GET", endpoint, params=params)
    
  def get_open_positions(self) -> List[Dict[str, Any]]:
    """
    Get all open positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of open positions.
    """
    return self.get_positions(position_status="open")
    
  def get_closed_positions(self) -> List[Dict[str, Any]]:
    """
    Get all closed positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of closed positions.
    """
    return self.get_positions(position_status="closed")
  
  def get_holdings(self, portfolios: Optional[str] = "default") -> List[Dict[str, Any]]:
    """
    Get current holdings.
    
    Args:
      portfolios (str, optional): Portfolio name. Defaults to "default".
        
    Returns:
      List[Dict[str, Any]]: List of holdings.
    """
    endpoint = self._routes["portfolio.holdings"]
    params = {"portfolios": portfolios}
    
    logger.debug("Fetching holdings for portfolio: %s", portfolios)
    return self._make_request("GET", endpoint, params=params)
    
  # ===== BASKET MANAGEMENT METHODS =====

  def create_basket(
    self,
    name: str,
    instruments: List[Dict[str, Any]],
    weightage_scheme: str = "equi_weighted",
    capital: Optional[Dict[str, float]] = None,
    instrument_types: Optional[List[str]] = None,
    trading_symbol: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Create a new basket.
    
    Args:
      name (str): Name of the basket.
      instruments (List[Dict[str, Any]]): List of instruments with weightage and shares.
      weightage_scheme (str, optional): Weightage scheme. Defaults to "equi_weighted".
      capital (Optional[Dict[str, float]], optional): Capital allocation. Defaults to {"minValue": 0, "actualValue": 0}.
      instrument_types (Optional[List[str]], optional): Types of instruments. Defaults to ["EQLC"].
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.create"]
    
    # Set defaults
    if capital is None:
      capital = {"minValue": 0, "actualValue": 0}
        
    data = {
      "name": name,
      "weightageScheme": weightage_scheme,
      "instruments": instruments,
      "capital": capital,
      "instrumentTypes": instrument_types
    }
    
    logger.debug("Creating basket: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def get_baskets(self) -> List[Dict[str, Any]]:
    """
    Get all baskets.
    
    Returns:
      List[Dict[str, Any]]: List of baskets.
    """
    endpoint = self._routes["basket.list"]
    
    logger.debug("Fetching baskets")
    return self._make_request("GET", endpoint)
    
  def get_basket(self, basket_id: str) -> Dict[str, Any]:
    """
    Get a specific basket by ID.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.info"].format(basket_id=basket_id)
    
    logger.debug("Fetching basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def get_basket_instruments(self, basket_id: str) -> List[Dict[str, Any]]:
    """
    Get instruments in a basket.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      List[Dict[str, Any]]: List of instruments in the basket.
    """
    endpoint = self._routes["basket.instruments"].format(basket_id=basket_id)
    
    logger.debug("Fetching instruments for basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def place_basket_order(
    self,
    trading_symbol: str,
    transaction_type: str,
    quantity: float,
    price: float = 0,
    order_type: str = None,
    product: str = None,
    validity: str = None,
    exchange_token: Optional[int] = None,
    trigger_price: float = 0,
    stoploss: float = 0,
    target: float = 0,
    broker: str = "wizzer",
    variety: str = None,
    strategy: Optional[Dict[str, str]] = None,
    disclosed_qty: int = 0,
    sl_applied_level: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Place a basket order.
    
    Args:
      trading_symbol (str): Basket trading symbol (e.g., "/BASKET_NAME").
      transaction_type (str): "BUY" or "SELL".
      quantity (float): Quantity/units of the basket.
      price (float, optional): Price for limit orders. Defaults to 0.
      order_type (str, optional): Order type. Defaults to MARKET.
      product (str, optional): Product code. Defaults to CNC.
      validity (str, optional): Order validity. Defaults to DAY.
      exchange_token (Optional[int], optional): Exchange token for the basket.
      trigger_price (float, optional): Trigger price. Defaults to 0.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      broker (str, optional): Broker code. Defaults to "wizzer".
      variety (str, optional): Order variety. Defaults to REGULAR.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      sl_applied_level (Optional[str], optional): Stop loss applied level (e.g., "basket").
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": self.EXCHANGE_WZR,
      "transactionType": transaction_type,
      "qty": quantity,
      "price": price,
      "orderType": order_type,
      "product": product,
      "validity": validity,
      "triggerPrice": trigger_price,
      "stoploss": stoploss,
      "target": target,
      "broker": broker,
      "variety": variety,
      "strategy": strategy_info,
      "segment": self.SEGMENT_WZREQ,
      "disclosedQty": disclosed_qty
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    # Add stop loss level if provided
    if sl_applied_level:
      data["slAppliedLevel"] = sl_applied_level
        
    logger.debug("Placing basket order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def place_basket_exit_order(
    self,
    trading_symbol: str,
    exchange: str,
    transaction_type: str,
    quantity: float,
    exchange_token: int,
    **kwargs
  ) -> Dict[str, Any]:
    """
    Place a basket exit order.
    
    Args:
      trading_symbol (str): Basket trading symbol.
      exchange (str): Exchange code (usually "WZR" for baskets).
      transaction_type (str): "BUY" or "SELL" (usually "SELL" for exit).
      quantity (float): Quantity/units of the basket.
      exchange_token (int): Exchange token for the basket.
      **kwargs: Additional parameters for the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.exit"]
    
    # Build base data
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange,
      "transactionType": transaction_type,
      "qty": quantity,
      "exchangeToken": exchange_token,
      **kwargs
    }
    
    # Set strategy if not in kwargs
    if "strategy" not in kwargs:
      data["strategy"] = self._get_strategy(None)
        
    # Set defaults if not in kwargs
    defaults = {
      "orderType": self.ORDER_TYPE_MARKET,
      "product": self.PRODUCT_CNC, 
      "validity": self.VALIDITY_DAY,
      "disclosedQty": 0,
      "price": 0,
      "variety": self.VARIETY_REGULAR,
      "stoploss": 0,
      "broker": "wizzer",
      "triggerPrice": 0,
      "target": 0,
      "segment": self.SEGMENT_WZREQ
    }
    
    for key, value in defaults.items():
      if key not in data:
        data[key] = value
    
    logger.debug("Placing basket exit order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_basket_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing basket order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying basket order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def rebalance_basket(
        self,
        trading_symbol: str,
        instruments: List[str],
        execution_policy: str,
        order_type: str = None,
        product: str = None,
        weightage_scheme: str = None
    ) -> Dict[str, Any]:
        """
        Rebalance a basket with new instruments.
        
        Args:
          trading_symbol (str): Basket trading symbol.
          instruments (List[str]): List of instrument identifiers for the new basket composition.
          execution_policy (str): Rebalance execution policy.
              Options: REBALANCE_FULL, REBALANCE_ENTRY_ONLY, REBALANCE_EXIT_ONLY.
          order_type (str, optional): Order type to use for rebalance orders.
              Options: ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT
          product (str, optional): Product type to use for rebalance orders.
              Options: PRODUCT_CNC, PRODUCT_MIS
          weightage_scheme (str, optional): Weightage scheme for rebalancing. Options:
              WEIGHTAGE_SCHEME_EQUI_WEIGHTED, WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED, 
              WEIGHTAGE_SCHEME_PRICE_WEIGHTED, WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED,
              WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED, 
              WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED, WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED
            
        Returns:
          Dict[str, Any]: Rebalance response.
        """
        endpoint = self._routes["basket.rebalance"]
        
        # Validate execution policy
        valid_execution_policies = [self.REBALANCE_FULL, self.REBALANCE_ENTRY_ONLY, self.REBALANCE_EXIT_ONLY]
        if execution_policy not in valid_execution_policies:
            raise ValueError(f"execution_policy must be one of {valid_execution_policies}")
          
        # Validate weightage scheme if provided
        if weightage_scheme:
            valid_weightage_schemes = [
                self.WEIGHTAGE_SCHEME_EQUI_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED,
                self.WEIGHTAGE_SCHEME_PRICE_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED,
                self.WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED,
                self.WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED
            ]
            if weightage_scheme not in valid_weightage_schemes:
                raise ValueError(f"weightage_scheme must be one of {valid_weightage_schemes}")
        
        # Build the basic request payload
        data = {
            "tradingSymbol": trading_symbol,
            "instruments": instruments,
            "policies": {
                "execution": execution_policy
            }
        }
        
        # Add order policies if specified
        if order_type or product:
            order_policies = {}
            
            if order_type:
                valid_order_types = [self.ORDER_TYPE_MARKET, self.ORDER_TYPE_LIMIT]
                if order_type not in valid_order_types:
                    raise ValueError(f"order_type must be one of {valid_order_types}")
                order_policies["orderType"] = order_type
                
            if product:
                valid_products = [self.PRODUCT_CNC, self.PRODUCT_MIS, self.PRODUCT_NRML]
                if product not in valid_products:
                    raise ValueError(f"product must be one of {valid_products}")
                order_policies["product"] = product
            
            if order_policies:
                data["policies"]["orders"] = order_policies
                
        # Add weightage scheme if specified
        if weightage_scheme:
            data["policies"]["weightageScheme"] = weightage_scheme
        
        logger.debug("Rebalancing basket %s with instruments: %s, policy: %s, order settings: %s", 
                    trading_symbol, instruments, execution_policy, 
                    {"order_type": order_type, "product": product, "weightage_scheme": weightage_scheme})
        
        return self._make_request("POST", endpoint, json=data)
    
  def exit_all_positions(self) -> Dict[str, Any]:
    """
    Exit all positions across all strategies.
    
    This method sends a request to close all open positions for the user.
    
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
    """
    endpoint = self._routes["portfolio.positions.exit.all"]
    
    data = {}
    
    logger.debug("Exiting all positions")
    return self._make_request("POST", endpoint, json=data)
    
  def exit_strategy_positions(self, strategy_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Exit all positions for a specific strategy.
    
    Args:
      strategy_id (Optional[str]): ID of the strategy to exit positions for.
        If None, uses the default strategy ID.
        
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
      
    Raises:
      ValueError: If no strategy_id is provided and no default is set.
    """
    # Get strategy ID (either from parameter or default)
    if not strategy_id:
      if not self.strategy_id:
        raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
      strategy_id = self.strategy_id
      
    endpoint = self._routes["portfolio.positions.exit.strategy"].format(strategy_id=strategy_id)
    
    data = {}
    
    logger.debug("Exiting all positions for strategy: %s", strategy_id)
    return self._make_request("POST", endpoint, json=data)

  # =====INSTRUMENT & ASSET CLASS METHODS =====
  
  def get_instrument_metrics(self, identifiers: List[str]) -> List[Dict[str, Any]]:
    """
    Get detailed metrics for instruments by their identifiers.
    
    Args:
        identifiers (List[str]): List of instrument identifiers in the format
                                "EXCHANGE:SYMBOL:TOKEN" (e.g., "NSE:SBIN:3045").
        
    Returns:
        List[Dict[str, Any]]: List of instrument metrics.
    
    Example:
        >>> client.get_instrument_metrics([
        ...     "NSE:SBIN:3045", 
        ...     "NSE:RELIANCE:2885",
        ...     "NSE:NIFTY26DEC11000CE:61009"
        ... ])
    """
    endpoint = self._routes["instrument.metrics"]
    data = {
        "identifiers": identifiers
    }
    
    logger.debug("Fetching instrument metrics for identifiers: %s", identifiers)
    response = self._make_request("POST", endpoint, json=data)
    return response

  def get_option_chain(
      self,
      identifier: str,
      expiry_date: Optional[str] = None,
      expiry_preference: Optional[str] = None,
      option_type: List[str] = None,
      moneyness: List[str] = None
  ) -> Dict[str, Any]:
      """
      Get option chain for a specified instrument.
      
      Args:
          identifier (str): Instrument identifier (e.g., "NSE:SBIN:3045").
          expiry_date (str): Expiry date in YYYY-MM-DD format.
          expiry_preference (Optional[str]): Expiry category preference instead of exact date.
              Use the EXPIRY_* constants provided by the class.
          option_type (List[str]): List of option types to include. 
              Values from [OPTION_TYPE_CE, OPTION_TYPE_PE].
          moneyness (List[str]): List of moneyness types to include. 
              Values from [MONEYNESS_ATM, MONEYNESS_ITM, MONEYNESS_OTM].
      
      Returns:
          Dict[str, Any]: Option chain data including strikes.
          
      Raises:
          ValueError: If option_type or moneyness lists are empty.
      """
      endpoint = self._routes["instrument.option_chain"]
      
      # Validate option_type and moneyness parameters
      if not option_type:
          raise ValueError("At least one option type must be specified")
      if not moneyness:
          raise ValueError("At least one moneyness type must be specified")
      if not expiry_date and not expiry_preference:
        raise ValueError("Either expiry_date or expiry_preference must be provided")
      
      # Validate option_type values
      valid_option_types = [self.OPTION_TYPE_CE, self.OPTION_TYPE_PE]
      for opt_type in option_type:
          if opt_type not in valid_option_types:
              raise ValueError(f"Invalid option type: {opt_type}. Must be one of {valid_option_types}")
      
      # Validate moneyness values
      valid_moneyness = [self.MONEYNESS_ATM, self.MONEYNESS_ITM, self.MONEYNESS_OTM]
      for money in moneyness:
          if money not in valid_moneyness:
              raise ValueError(f"Invalid moneyness: {money}. Must be one of {valid_moneyness}")
      
      data = {
          "identifier": identifier,
          "optionType": option_type,
          "moneyness": moneyness
      }
      
      # Add either expiryDate or expiryPreference
      if expiry_date:
          data["expiryDate"] = expiry_date
      elif expiry_preference:
          data["expiryPreference"] = expiry_preference
      
      logger.debug("Fetching option chain with data: %s", data)
      return self._make_request("POST", endpoint, json=data)

  def get_option_expiry_list(
      self,
      identifier: str
  ) -> Dict[str, Any]:
      """
      Get a list of available expiry dates for an instrument's options.
      
      Args:
        identifier (str): Instrument identifier in the format "EXCHANGE:SYMBOL:TOKEN"
          (e.g., "NSE:SBIN:3045" or "NSE:NIFTY 50:26000").
          
      Returns:
        Dict[str, Any]: Response containing the list of available expiry dates with contract types.
        
      Example:
        ```python
        # Get expiry dates for a stock
        expiry_list = client.get_option_expiry_list("NSE:SBIN:3045")
        
        # Get expiry dates for an index
        nifty_expiry = client.get_option_expiry_list("NSE:NIFTY 50:26000")
        
        # Access the expiry dates
        for expiry in expiry_list.get('expiryList', []):
            print(f"{expiry['date']} - {expiry['contract']}")
        ```
      """
      endpoint = self._routes["instrument.expiry_list"]
      
      data = {
        "identifier": identifier
      }

      logger.debug("Fetching option expiry list for %s", identifier)
      return self._make_request("POST", endpoint, json=data)
    
  def get_futures_list(self, identifier: str) -> List[Dict[str, Any]]:
    """
    Get available futures contracts for an instrument.
    
    Args:
      identifier (str): Instrument identifier (e.g., "NSE:SBIN:3045" or "NSE:NIFTY 50:26000").
        
    Returns:
      List[Dict[str, Any]]: List of available futures contracts with expiry dates and contract types.
      
    Example:
      # Get futures for a stock
      sbin_futures = client.get_futures_list("NSE:SBIN:3045")
      for future in sbin_futures:
          print(f"{future['tradingSymbol']} - {future['expiry']} ({future['contract']})")
          
      # Get futures for an index
      nifty_futures = client.get_futures_list("NSE:NIFTY 50:26000")
    """
    endpoint = self._routes["instrument.future_list"]
    data = {"identifier": identifier}
    
    logger.debug("Fetching futures list for: %s", identifier)
    return self._make_request("POST", endpoint, json=data)


  def get_classification_types(self) -> list:
    """
    Retrieve all available classification types.
    
    Returns:
      list: A list of classification types.
    """
    endpoint = self._routes["classification.types"]
    logger.debug("Fetching classification types.")
    return self._make_request("GET", endpoint)

  def get_classifications(self, classification_type: str) -> list:
    """
    Retrieve all values for a specific classification type.
    
    Args:
      classification_type (str): The type of classification to retrieve values for.
      
    Returns:
      list: A list of classification values.
    """
    endpoint = self._routes["classification.values"].format(type=classification_type)
    logger.debug(f"Fetching classification values for type: {classification_type}")
    return self._make_request("GET", endpoint)

  def filter_indices(self, filters: Dict[str, List[str]], match_all: bool = True) -> list:
    """
    Filter indices based on multiple classification criteria.
    
    Args:
      filters (Dict[str, List[str]]): A dictionary of filters where keys are classification
                                      types and values are lists of classification values.
      match_all (bool): If True, performs an AND logic search. If False, performs an OR logic search.
      
    Returns:
      list: A list of indices that match the filter criteria.
    """
    endpoint = self._routes["indices.filter"]
    data = {
      "filters": filters,
      "matchAll": match_all
    }
    logger.debug(f"Filtering indices with filters: {filters} and match_all: {match_all}")
    return self._make_request("POST", endpoint, json=data)

  def filter_instruments(
    self,
    filters: Optional[Dict[str, List[str]]] = None,
    match_all: bool = True,
    index_identifier: Optional[str] = None
  ) -> list:
    """
    Filter instruments based on classification criteria, with an option to filter within an index.
    
    Args:
      filters (Optional[Dict[str, List[str]]]): A dictionary of filters where keys are classification
                                      types and values are lists of classification values. Can be None.
      match_all (bool): If True, performs an AND logic search. If False, performs an OR logic search.
      index_identifier (Optional[str]): If provided, filters instruments within a specific index.
      
    Returns:
      list: A list of instruments that match the filter criteria.
    """
    data = {
        "filters": filters or {},
        "matchAll": match_all
    }

    if index_identifier:
        endpoint = self._routes["instruments.filter_with_index"].format(id=index_identifier)
        logger.debug(f"Filtering instruments for index: {index_identifier} with filters: {filters} and match_all: {match_all}")
    else:
        endpoint = self._routes["instruments.filter"]
        logger.debug(f"Filtering instruments with filters: {filters} and match_all: {match_all}")
        
    return self._make_request("POST", endpoint, json=data)

  def filter_instruments_by_derivatives(
    self,
    hasOptions: Optional[bool] = None,
    hasFutures: Optional[bool] = None
  ) -> list:
    """
    Filter instruments based on the existence of derivatives (options or futures).

    Args:
      hasOptions (Optional[bool]): If True, returns instruments that have options.
      hasFutures (Optional[bool]): If True, returns instruments that have futures.
    
    Returns:
      list: A list of instruments that match the criteria.
    """
    endpoint = self._routes["instruments.filter_by_derivatives"]
    data = {}
    if hasOptions is not None:
        data["hasOptions"] = hasOptions
    if hasFutures is not None:
        data["hasFutures"] = hasFutures
    
    logger.debug(f"Filtering instruments by derivatives with payload: {data}")
    return self._make_request("POST", endpoint, json=data)

  def run_screener(
    self,
    filters: Dict[str, Any],
    sort: Optional[List[Dict[str, int]]] = None,
    limit: Optional[int] = None,
  ) -> List[Dict[str, Any]]:
    """
    Run an instrument screener with specified filters.

    Args:
      filters (Dict[str, Any]): The filter conditions for the screener.
      sort (Optional[List[Dict[str, int]]]): The sort order for the results.
      limit (Optional[int]): The maximum number of results to return.
      
    Returns:
      List[Dict[str, Any]]: A list of instruments that match the screener criteria.
    """
    endpoint = self._routes["screener.run"]
    data = {"filters": filters}
    if sort is not None:
        data["sort"] = sort
    if limit is not None:
        data["limit"] = limit
        
    logger.debug(f"Running screener with payload: {data}")
    return self._make_request("POST", endpoint, json=data)

  def get_screener_fields(self) -> List[Dict[str, Any]]:
    """
    Get the list of available fields and supported operations for the screener.

    Returns:
      List[Dict[str, Any]]: A list of available screener fields.
    """
    endpoint = self._routes["screener.fields"]
    logger.debug("Fetching screener fields.")
    return self._make_request("GET", endpoint)

  def _normalize_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
    """
    Normalize parameters for HTTP requests, converting booleans to lowercase strings.
    Preserves spaces in string values to prevent automatic URL encoding by requests library.
    
    Args:
      params (Optional[Dict[str, Any]]): Raw parameters dictionary.
      
    Returns:
      Optional[Dict[str, str]]: Normalized parameters with proper string formatting.
    """
    if not params:
      return None
    
    normalized = {}
    for key, value in params.items():
      if isinstance(value, bool):
        # Convert Python boolean to lowercase string for API compatibility
        normalized[key] = "true" if value else "false"
      elif value is not None:
        # Convert other values to strings, preserving spaces
        # This prevents requests library from automatically URL-encoding spaces to '+'
        normalized[key] = str(value)
    
    return normalized

  def _make_request(
    self,
    method: str,
    endpoint: str, 
    params: Optional[Dict[str, Any]] = None, 
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
  ) -> Any:
    """
    Make an HTTP request to the API.

    Args:
      method (str): HTTP method (GET, POST, etc.)
      endpoint (str): API endpoint path.
      params (Optional[Dict[str, Any]]): Query parameters for GET requests.
      json (Optional[Dict[str, Any]]): JSON payload for POST requests.
      headers (Optional[Dict[str, str]]): Custom headers to override the defaults.

    Returns:
      Any: Parsed JSON response.

    Raises:
      requests.RequestException: If the request fails.
    """
    import urllib.parse
    
    url = f"{self.base_url}{endpoint}"
    request_headers = headers if headers else self.headers
    
    # Normalize parameters to handle booleans correctly
    normalized_params = self._normalize_params(params)
    
    # Handle URL construction manually to encode spaces as %20 instead of +
    if normalized_params and method.upper() == 'GET':
      # Construct query string manually to control encoding
      query_parts = []
      for key, value in normalized_params.items():
        # Use urllib.parse.quote to encode values, spaces become %20 instead of +
        encoded_key = urllib.parse.quote(str(key), safe='')
        encoded_value = urllib.parse.quote(str(value), safe='')  # Properly encode all special chars
        query_parts.append(f"{encoded_key}={encoded_value}")
      
      if query_parts:
        url = f"{url}?{'&'.join(query_parts)}"
      normalized_params = None  # Don't pass params to requests since we built the URL manually
    
    try:
      logger.debug("%s request to %s", method, url)
      response = requests.request(
        method=method,
        url=url,
        headers=request_headers,
        params=normalized_params,
        json=json
      )
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
      logger.error("API request failed: %s", e, exc_info=True)
      if hasattr(e.response, 'text'):
        logger.error("Response content: %s", e.response.text)
      raise

  # ===== KV STORE METHODS =====

  def create_kv(self, key: str, value: Any, ttl: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a new key-value pair.
    
    Args:
        key (str): The key for the KV pair.
        value (Any): The value to store (any JSON-serializable type).
        ttl (Optional[int]): Time to live in seconds. If provided, the key will expire after this duration.
    
    Returns:
        Dict[str, Any]: Response containing key, value, type, ttl, createdAt, updatedAt.
        
    Example Response:
        {
            "key": "state",
            "value": {"positions": 30},
            "type": "object", 
            "ttl": 100,
            "createdAt": "2023-10-01T10:00:00Z",
            "updatedAt": "2023-10-01T10:00:00Z"
        }
    
    Raises:
        ValueError: If key is empty or invalid.
        requests.RequestException: If key already exists (409 Conflict) or API request fails.
    
    Example:
        client.create_kv(key="portfolio_state", value={"positions": 30}, ttl=3600)
    """
    if not key or not key.strip():
      raise ValueError("Key cannot be empty or whitespace")
    
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.create"].format(strategy_id=strategy_info["id"], key=key)
    
    # Build request payload
    data = {"value": value}
    if ttl is not None:
      data["ttl"] = ttl
    
    logger.debug("Creating KV pair: key=%s, type=%s, ttl=%s", key, type(value).__name__, ttl)
    return self._make_request("POST", endpoint, json=data)

  def get_kv(self, key: str) -> Dict[str, Any]:
    """
    Retrieve a key-value pair.
    
    Args:
        key (str): The key to retrieve.
    
    Returns:
        Dict[str, Any]: Response containing value, type, and optional ttl.
        
    Example Response:
        {
            "value": {"positions": 30},
            "type": "object",
            "ttl": 85
        }
    
    Raises:
        ValueError: If key is empty or invalid.
        requests.RequestException: If key not found (404) or API request fails.
    
    Example:
        data = client.get_kv("portfolio_state")
        positions = data["value"]["positions"]
    """
    if not key or not key.strip():
      raise ValueError("Key cannot be empty or whitespace")
    
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.get"].format(strategy_id=strategy_info["id"], key=key)
    
    logger.debug("Retrieving KV pair: key=%s", key)
    return self._make_request("GET", endpoint)

  def update_kv(self, key: str, value: Any, ttl: Optional[int] = None) -> Dict[str, Any]:
    """
    Update (replace) an existing key-value pair completely.
    
    Args:
        key (str): The key to update.
        value (Any): The new value to store (any JSON-serializable type).
        ttl (Optional[int]): New time to live in seconds.
    
    Returns:
        Dict[str, Any]: Response containing key, value, type, ttl, createdAt, updatedAt.
        
    Example Response:
        {
            "key": "state",
            "value": {"positions": 50, "orders": 10},
            "type": "object",
            "ttl": 200,
            "createdAt": "2023-10-01T10:00:00Z", 
            "updatedAt": "2023-10-01T10:30:00Z"
        }
    
    Raises:
        ValueError: If key is empty or invalid.
        requests.RequestException: If key not found (404) or API request fails.
    
    Example:
        client.update_kv(key="portfolio_state", value={"positions": 50}, ttl=1800)
    """
    if not key or not key.strip():
      raise ValueError("Key cannot be empty or whitespace")
    
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.update"].format(strategy_id=strategy_info["id"], key=key)
    
    # Build request payload
    data = {"value": value}
    if ttl is not None:
      data["ttl"] = ttl
    
    logger.debug("Updating KV pair: key=%s, type=%s, ttl=%s", key, type(value).__name__, ttl)
    return self._make_request("PUT", endpoint, json=data)

  def patch_kv(self, key: str, value: Optional[Any] = None, ttl: Optional[int] = None) -> Dict[str, Any]:
    """
    Partially update a key-value pair.
    
    For OBJECT types: merges the new value with existing value.
    For other types (STRING, NUMBER, BOOLEAN, ARRAY): replaces the value entirely.
    
    Args:
        key (str): The key to patch.
        value (Optional[Any]): New value or partial value to merge.
        ttl (Optional[int]): New time to live in seconds.
        
    Note: At least one of value or ttl must be provided.
    
    Returns:
        Dict[str, Any]: Response containing key, value, type, ttl, createdAt, updatedAt.
        
    Example Response (for object merge):
        {
            "key": "state", 
            "value": {"positions": 30, "orders": 5, "last_update": "2023-10-01"},  # Merged
            "type": "object",
            "ttl": 150,
            "createdAt": "2023-10-01T10:00:00Z",
            "updatedAt": "2023-10-01T10:15:00Z"
        }
    
    Raises:
        ValueError: If key is empty, invalid, or no parameters provided.
        requests.RequestException: If key not found (404) or API request fails.
    
    Example:
        # For objects - merges with existing
        client.patch_kv(key="portfolio_state", value={"last_update": "2023-10-01"})
        
        # For non-objects - replaces entirely
        client.patch_kv(key="counter", value=42)
        
        # Update only TTL
        client.patch_kv(key="session", ttl=1800)
    """
    if not key or not key.strip():
      raise ValueError("Key cannot be empty or whitespace")
    
    if value is None and ttl is None:
      raise ValueError("At least one of value or ttl must be provided")
    
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.patch"].format(strategy_id=strategy_info["id"], key=key)
    
    # Build request payload
    data = {}
    if value is not None:
      data["value"] = value
    if ttl is not None:
      data["ttl"] = ttl
    
    logger.debug("Patching KV pair: key=%s, has_value=%s, has_ttl=%s", key, value is not None, ttl is not None)
    return self._make_request("PATCH", endpoint, json=data)

  def delete_kv(self, key: str) -> Dict[str, Any]:
    """
    Delete a key-value pair.
    
    Args:
        key (str): The key to delete.
    
    Returns:
        Dict[str, Any]: Success confirmation.
        
    Example Response:
        {
            "success": True,
            "message": "Key deleted successfully"
        }
    
    Raises:
        ValueError: If key is empty or invalid.
        requests.RequestException: If key not found (404) or API request fails.
    
    Example:
        response = client.delete_kv("old_config")
        if response["success"]:
            print("Key deleted successfully")
    """
    if not key or not key.strip():
      raise ValueError("Key cannot be empty or whitespace")
    
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.delete"].format(strategy_id=strategy_info["id"], key=key)
    
    logger.debug("Deleting KV pair: key=%s", key)
    return self._make_request("DELETE", endpoint)

  def get_all_kvs(self, page_no: int = 1, paginate: bool = False) -> List[Dict[str, Any]]:
    """
    Get all key-value pairs with their complete data.
    
    Args:
        page_no (int): Page number for pagination (default: 1).
        paginate (bool): If True, automatically fetch all pages (default: False).
    
    Returns:
        List[Dict[str, Any]]: List of all KV pairs with complete data.
        
    Example Response:
        [
            {
                "key": "portfolio_state",
                "value": {"positions": 30},
                "type": "object",
                "ttl": 100,
                "createdAt": "2023-10-01T10:00:00Z",
                "updatedAt": "2023-10-01T10:00:00Z"
            },
            {
                "key": "environment",
                "value": "production",
                "type": "string", 
                "createdAt": "2023-10-01T09:00:00Z",
                "updatedAt": "2023-10-01T09:00:00Z"
            },
            {
                "key": "trade_count",
                "value": 42,
                "type": "number",
                "createdAt": "2023-10-01T08:00:00Z",
                "updatedAt": "2023-10-01T08:30:00Z"
            }
        ]
    
    Example:
        # Get first page only
        kvs = client.get_all_kvs()
        
        # Get all pages automatically
        all_kvs = client.get_all_kvs(paginate=True)
    """
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.list"].format(strategy_id=strategy_info["id"])
    
    if paginate:
      return self._paginate_kv_requests(endpoint, "get_all_kvs")
    else:
      params = {"pageNo": page_no}
      logger.debug("Fetching all KVs page %d", page_no)
      return self._make_request("GET", endpoint, params=params)

  def get_kv_keys(self, page_no: int = 1, paginate: bool = False) -> List[Dict[str, Any]]:
    """
    Get all keys with metadata (without values for memory efficiency).
    
    Args:
        page_no (int): Page number for pagination (default: 1).
        paginate (bool): If True, automatically fetch all pages (default: False).
    
    Returns:
        List[Dict[str, Any]]: List of keys with metadata (no values).
        
    Example Response:
        [
            {
                "key": "portfolio_state",
                "type": "object",
                "ttl": 100,
                "createdAt": "2023-10-01T10:00:00Z",
                "updatedAt": "2023-10-01T10:00:00Z"
            },
            {
                "key": "environment", 
                "type": "string",
                "createdAt": "2023-10-01T09:00:00Z",
                "updatedAt": "2023-10-01T09:00:00Z"
            },
            {
                "key": "trade_count",
                "type": "number",
                "createdAt": "2023-10-01T08:00:00Z",
                "updatedAt": "2023-10-01T08:30:00Z"
            }
        ]
    
    Example:
        # Get keys for first page
        keys = client.get_kv_keys()
        
        # Get all keys across all pages
        all_keys = client.get_kv_keys(paginate=True)
        
        # Check what keys exist
        for key_info in all_keys:
            print(f"Key: {key_info['key']}, Type: {key_info['type']}")
    """
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.keys"].format(strategy_id=strategy_info["id"])
    
    if paginate:
      return self._paginate_kv_requests(endpoint, "get_kv_keys")
    else:
      params = {"pageNo": page_no}
      logger.debug("Fetching KV keys page %d", page_no)
      return self._make_request("GET", endpoint, params=params)

  def _paginate_kv_requests(self, endpoint: str, operation: str) -> List[Dict[str, Any]]:
    """
    Internal method to handle pagination for KV list operations.
    
    Args:
        endpoint (str): API endpoint.
        operation (str): Operation name for logging.
        
    Returns:
        List[Dict[str, Any]]: Combined results from all pages.
    """
    all_items = []
    page_no = 1
    total_count = None
    page_size = 20  # KV API uses 20 items per page
    
    while True:
      params = {"pageNo": page_no}
      logger.debug("Fetching %s page %d", operation, page_no)
      
      try:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
          method="GET",
          url=url,
          headers=self.headers,
          params=params
        )
        response.raise_for_status()
        
        # Get items from the current page
        items = response.json()
        all_items.extend(items)
        
        # Check if we need to fetch more pages
        if total_count is None and "X-Total-Count" in response.headers:
          try:
            total_count = int(response.headers["X-Total-Count"])
            logger.debug("Total %s count: %d", operation, total_count)
          except (ValueError, TypeError):
            logger.warning("Could not parse X-Total-Count header for %s", operation)
            break
        
        # If we've fetched all items or there are no more pages, stop
        if not items or len(all_items) >= total_count or total_count is None:
          break
        
        # Move to the next page
        page_no += 1
        
      except requests.RequestException as e:
        logger.error("API request failed during %s pagination: %s", operation, e, exc_info=True)
        if hasattr(e.response, 'text'):
          logger.error("Response content: %s", e.response.text)
        raise
    
    logger.info("Fetched %d items in total for %s", len(all_items), operation)
    return all_items
  
  # Add this method to the WizzerClient class
  def delete_all_kv(self) -> Dict[str, Any]:
    """
    Delete all key-value pairs for the current strategy.
    
    This method removes all KV pairs associated with the client's strategy.
    Use with caution as this operation cannot be undone.
    
    Returns:
        Dict[str, Any]: Response containing success status, count of deleted items, and message.
        
    Example Response:
        {
            "success": True,
            "deleted": 15,
            "message": "Successfully deleted 15 key-value pairs"
        }
    
    Raises:
        requests.RequestException: If API request fails.
    
    Example:
        response = client.delete_all_kv()
        print(f"Deleted {response['deleted']} key-value pairs")
    """
    # Get strategy information
    strategy_info = self._get_strategy()
    endpoint = self._routes["kv.delete_all"].format(strategy_id=strategy_info["id"])
    
    logger.debug("Deleting all KV pairs for strategy: %s", strategy_info["id"])
    return self._make_request("DELETE", endpoint)
  
  # ===== ANALYTICS API METHODS =====
  
  # --- Fundamentals Methods ---
  
  def get_net_profit_margin(
    self, 
    symbol: str, 
    period: str = "quarterly", 
    fiscal_year: Optional[str] = None,
    quarter: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Get net profit margin for a stock.
    
    Args:
      symbol (str): Stock symbol (e.g., "INFY").
      period (str, optional): "quarterly" or "annual". Defaults to "quarterly".
      fiscal_year (str, optional): For annual reports (e.g., "2023").
      quarter (str, optional): For quarterly reports (e.g., "Q1FY24").
      
    Returns:
      Dict[str, Any]: Net profit margin data.
      
    Example Response:
      {
        "symbol": "INFY",
        "period": "quarterly",
        "quarter": "Q1FY24",
        "fiscalYear": null,
        "netProfitMargin": 16.8,
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "period": period
    })
    
    if fiscal_year:
      params["fiscalYear"] = fiscal_year
    if quarter:
      params["quarter"] = quarter
    
    logger.debug("Fetching net profit margin for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.net_profit_margin"], params=params)
  
  def get_roe(
    self, 
    symbol: str, 
    period: str = "annual", 
    consolidated: bool = True
  ) -> Dict[str, Any]:
    """
    Get Return on Equity (ROE) for a stock.
    
    Args:
      symbol (str): Stock symbol.
      period (str, optional): "quarterly" or "annual". Defaults to "annual".
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      
    Returns:
      Dict[str, Any]: ROE data.
      
    Example Response:
      {
        "symbol": "TCS",
        "period": "annual",
        "roe": 42.5,
        "unit": "%"
      }
    """
    params = {
      "symbol": symbol,
      "period": period,
      "consolidated": consolidated
    }
    
    logger.debug("Fetching ROE for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.roe"], params=params)
  
  def get_roa(
    self, 
    symbol: str, 
    period: str = "annual", 
    consolidated: bool = True
  ) -> Dict[str, Any]:
    """
    Get Return on Assets (ROA) for a stock.
    
    Args:
      symbol (str): Stock symbol.
      period (str, optional): "quarterly" or "annual". Defaults to "annual".
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      
    Returns:
      Dict[str, Any]: ROA data.
      
    Example Response:
      {
        "symbol": "WIPRO",
        "period": "annual",
        "roa": 14.3,
        "unit": "%"
      }
    """
    params = {
      "symbol": symbol,
      "period": period,
      "consolidated": consolidated
    }
    
    logger.debug("Fetching ROA for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.roa"], params=params)
  
  def get_ebit_margin(
    self, 
    symbol: str, 
    period: str = "annual", 
    consolidated: bool = True
  ) -> Dict[str, Any]:
    """
    Get EBIT margin for a stock.
    
    Args:
      symbol (str): Stock symbol.
      period (str, optional): "quarterly" or "annual". Defaults to "annual".
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      
    Returns:
      Dict[str, Any]: EBIT margin data.
      
    Example Response:
      {
        "symbol": "INFY",
        "period": "annual",
        "ebit_margin": 24.1,
        "unit": "%"
      }
    """
    params = {
      "symbol": symbol,
      "period": period,
      "consolidated": consolidated
    }
    
    logger.debug("Fetching EBIT margin for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.ebit_margin"], params=params)
  
  def get_ocf_netprofit_ratio(
    self, 
    symbol: str, 
    period: str = "annual"
  ) -> Dict[str, Any]:
    """
    Get Operating Cash Flow to Net Profit ratio.
    
    Args:
      symbol (str): Stock symbol.
      period (str, optional): "annual" or "ttm". Defaults to "annual".
      
    Returns:
      Dict[str, Any]: OCF/Net Profit ratio data.
      
    Example Response:
      {
        "symbol": "TCS",
        "period": "annual",
        "ocf_netprofit_ratio": 1.15,
        "unit": "ratio"
      }
      
    Note: Ratio > 1 indicates strong cash generation.
    """
    params = {
      "symbol": symbol,
      "period": period
    }
    
    logger.debug("Fetching OCF/Net Profit ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.ocf_netprofit_ratio"], params=params)
  
  def get_eps_cagr(
    self, 
    symbol: str, 
    start_year: int,
    end_year: int
  ) -> Dict[str, Any]:
    """
    Get EPS Compound Annual Growth Rate (CAGR).
    
    Args:
      symbol (str): Stock symbol.
      start_year (int): Starting year (e.g., 2019).
      end_year (int): Ending year (e.g., 2023).
      
    Returns:
      Dict[str, Any]: EPS CAGR data.
      
    Example Response:
      {
        "symbol": "INFY",
        "startYear": 2019,
        "endYear": 2023,
        "epsCagr": 8.5,
        "epsStart": 35.2,
        "epsEnd": 48.7,
        "years": 4,
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startYear": start_year,
      "endYear": end_year
    })
    
    logger.debug("Fetching EPS CAGR for %s from %s to %s", symbol, start_year, end_year)
    return self._make_request("GET", self._routes["analytics.fundamentals.eps_cagr"], params=params)
  
  def get_book_to_market(
    self,
    symbol: str,
    as_of: str,
    price_source: str = "avgQuarter",
    custom_price: Optional[float] = None,
    standalone: bool = False,
    currency: str = "INR"
  ) -> Dict[str, Any]:
    """
    Get book-to-market ratio for a stock.
    
    Args:
      symbol (str): Stock symbol (e.g., "NSE:INFY").
      as_of (str): Reference date (YYYY-MM-DD).
      price_source (str, optional): Price source: spot, avgQuarter, custom. Defaults to "avgQuarter".
      custom_price (float, optional): Required if price_source=custom.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      currency (str, optional): Output currency. Defaults to "INR".
      
    Returns:
      Dict[str, Any]: Book-to-market ratio data.
      
    Example Response:
      {
        "symbol": "NSE:INFY",
        "asOf": "2023-03-31",
        "bookToMarket": 0.1234,
        "bookValuePerShare": 184.50,
        "marketPricePerShare": 1495.75,
        "sourcePriceType": "avgQuarter",
        "quarterRef": "Q4FY23",
        "standalone": false,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "asOf": as_of,
      "priceSource": price_source,
      "standalone": standalone,
      "currency": currency
    })
    
    if custom_price is not None:
      params["customPrice"] = str(custom_price)
    
    logger.debug("Fetching book-to-market ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.book_to_market"], params=params)
  
  def get_marketcap_to_sales(
    self,
    symbol: str,
    as_of: str,
    price_source: str = "avgQuarter",
    custom_price: Optional[float] = None,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get market cap to sales ratio for a stock.
    
    Args:
      symbol (str): Stock symbol.
      as_of (str): Reference date (YYYY-MM-DD).
      price_source (str, optional): Price source. Defaults to "avgQuarter".
      custom_price (float, optional): Custom price if price_source=custom.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: Market cap to sales ratio data.
      
    Example Response:
      {
        "symbol": "INFY",
        "asOf": "2023-03-31",
        "marketcapToSales": 5.67,
        "marketCap": 615000,
        "sales": 108500,
        "pricePerShare": 1495.75,
        "sharesOutstanding": 4112000000,
        "revenueQuarter": "Q1",
        "standalone": false,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "asOf": as_of,
      "priceSource": price_source,
      "standalone": standalone
    })
    
    if custom_price is not None:
      params["customPrice"] = str(custom_price)
    
    logger.debug("Fetching market cap to sales ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.marketcap_to_sales"], params=params)
  
  def get_cash_to_marketcap(
    self,
    symbol: str,
    as_of: str,
    price_source: str = "avgQuarter",
    custom_price: Optional[float] = None,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get cash to market cap ratio for a stock.
    
    Args:
      symbol (str): Stock symbol.
      as_of (str): Reference date (YYYY-MM-DD).
      price_source (str, optional): Price source. Defaults to "avgQuarter".
      custom_price (float, optional): Custom price if price_source=custom.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: Cash to market cap ratio data.
      
    Example Response:
      {
        "symbol": "INFY",
        "asOf": "2023-03-31",
        "cashToMarketcap": 0.0456,
        "cashAndEquivalents": 28050,
        "marketCap": 615000,
        "pricePerShare": 1495.75,
        "sharesOutstanding": 4112000000,
        "reportingQuarter": "Q1",
        "standalone": false,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "asOf": as_of,
      "priceSource": price_source,
      "standalone": standalone
    })
    
    if custom_price is not None:
      params["customPrice"] = str(custom_price)
    
    logger.debug("Fetching cash to market cap ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.fundamentals.cash_to_marketcap"], params=params)
  
  # --- Valuation Methods ---
  
  def get_pe_ratio(
    self, 
    symbol: str, 
    date: Optional[str] = None,
    ttm: bool = False,
    consolidated: bool = True,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get Price to Earnings (P/E) ratio.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Date in "YYYY-MM-DD" format.
      ttm (bool, optional): Use trailing twelve months. Defaults to False.
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: P/E ratio data.
      
    Example Response:
      {
        "symbol": "RELIANCE",
        "date": "2025-07-31",
        "pe_ratio": 27.5,
        "price": null,
        "eps": null,
        "ttm": false,
        "consolidated": true,
        "unit": "ratio"
      }
    """
    params = {
      "symbol": symbol,
      "ttm": ttm,
      "consolidated": consolidated,
      "standalone": standalone
    }
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching P/E ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.valuation.pe_ratio"], params=params)
  
  def get_pb_ratio(
    self, 
    symbol: str, 
    date: Optional[str] = None,
    consolidated: bool = True,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get Price to Book (P/B) ratio.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Date in "YYYY-MM-DD" format.
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: P/B ratio data.
      
    Example Response:
      {
        "symbol": "HDFC",
        "date": "2025-07-31",
        "pb_ratio": 3.2,
        "price": null,
        "book_value": null,
        "consolidated": true,
        "unit": "ratio"
      }
    """
    params = {
      "symbol": symbol,
      "consolidated": consolidated,
      "standalone": standalone
    }
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching P/B ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.valuation.pb_ratio"], params=params)
  
  def get_ev_ebitda(
    self, 
    symbol: str, 
    date: Optional[str] = None,
    ttm: bool = False,
    consolidated: bool = True,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get Enterprise Value to EBITDA ratio.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Date in "YYYY-MM-DD" format.
      ttm (bool, optional): Use trailing twelve months. Defaults to False.
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: EV/EBITDA ratio data.
      
    Example Response:
      {
        "symbol": "LTI",
        "date": "2025-06-30",
        "ev_ebitda": 22.8,
        "enterprise_value": null,
        "ebitda": null,
        "ttm": false,
        "unit": "ratio"
      }
    """
    params = {
      "symbol": symbol,
      "ttm": ttm,
      "consolidated": consolidated,
      "standalone": standalone
    }
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching EV/EBITDA for %s", symbol)
    return self._make_request("GET", self._routes["analytics.valuation.ev_ebitda"], params=params)
  
  def get_fcf_yield(
    self, 
    symbol: str, 
    date: Optional[str] = None,
    ttm: bool = False,
    consolidated: bool = True,
    standalone: bool = False
  ) -> Dict[str, Any]:
    """
    Get Free Cash Flow yield.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Date in "YYYY-MM-DD" format.
      ttm (bool, optional): Use trailing twelve months. Defaults to False.
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      standalone (bool, optional): Use standalone financials. Defaults to False.
      
    Returns:
      Dict[str, Any]: FCF yield data.
      
    Example Response:
      {
        "symbol": "HDFCAMC",
        "date": "2025-06-30",
        "fcf_yield": 4.5,
        "fcf": null,
        "market_cap": null,
        "ttm": false,
        "unit": "%"
      }
    """
    params = {
      "symbol": symbol,
      "ttm": ttm,
      "consolidated": consolidated,
      "standalone": standalone
    }
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching FCF yield for %s", symbol)
    return self._make_request("GET", self._routes["analytics.valuation.fcf_yield"], params=params)
  
  # --- Returns Methods ---
  
  
  def get_quarterly_returns(
    self, 
    symbol: str, 
    start_date: str,
    end_date: str,
    adjusted: bool = True
  ) -> Dict[str, Any]:
    """
    Get quarterly returns for a stock.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      adjusted (bool, optional): Use adjusted prices. Defaults to True.
      
    Returns:
      Dict[str, Any]: Quarterly returns data.
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted
    })
    
    logger.debug("Fetching quarterly returns for %s", symbol)
    return self._make_request("GET", self._routes["analytics.returns.quarterly"], params=params)
  
  def get_monthly_returns(
    self, 
    symbol: str, 
    start_date: str,
    end_date: str,
    adjusted: bool = True
  ) -> Dict[str, Any]:
    """
    Get monthly returns for a stock.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      adjusted (bool, optional): Use adjusted prices. Defaults to True.
      
    Returns:
      Dict[str, Any]: Monthly returns data.
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted
    })
    
    logger.debug("Fetching monthly returns for %s", symbol)
    return self._make_request("GET", self._routes["analytics.returns.monthly"], params=params)
  
  # --- Market Data Methods ---
  
  def get_analytics_ohlcv_daily(
    self, 
    symbol: str, 
    start_date: str,
    end_date: str,
    adjusted: bool = True
  ) -> Dict[str, Any]:
    """
    Get daily OHLCV data from analytics API.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      adjusted (bool, optional): Use adjusted prices. Defaults to True (ignored as adjusted data not available).
      
    Returns:
      Dict[str, Any]: Daily OHLCV data.
      
    Example Response:
      {
        "data": [
          {
            "date": "2025-01-01",
            "open": 2305.0,
            "high": 2340.0,
            "low": 2290.0,
            "close": 2325.0,
            "volume": 12500000,
            "symbol": "RELIANCE"
          }
        ]
      }
      
    Note: Maximum 365 days per request.
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted
    })
    
    logger.debug("Fetching analytics OHLCV daily data for %s", symbol)
    return self._make_request("GET", self._routes["analytics.marketdata.ohlcv_daily"], params=params)
  
  def get_analytics_historical_prices(
    self, 
    symbol: str, 
    start_date: str,
    end_date: str,
    adjusted: bool = True
  ) -> Dict[str, Any]:
    """
    Get historical prices from analytics API (same as OHLCV daily).
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      adjusted (bool, optional): Use adjusted prices. Defaults to True.
      
    Returns:
      Dict[str, Any]: Historical price data.
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted
    })
    
    logger.debug("Fetching analytics historical prices for %s", symbol)
    return self._make_request("GET", self._routes["analytics.marketdata.historical_prices"], params=params)
  
  def get_free_float_market_cap(
    self, 
    symbol: str, 
    date: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Get free-float market capitalization.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Date in "YYYY-MM-DD" format. Defaults to most recent.
      
    Returns:
      Dict[str, Any]: Free-float market cap data.
      
    Example Response:
      {
        "symbol": "RELIANCE",
        "date": "2025-07-31",
        "free_float_market_cap": 1054321.89,
        "market_cap": 1234567.89,
        "promoter_holding_percent": 14.6,
        "unit": "₹ Crores"
      }
    """
    params = {"symbol": symbol}
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching free-float market cap for %s", symbol)
    return self._make_request("GET", self._routes["analytics.marketdata.free_float_market_cap"], params=params)
  
  # --- Ownership Methods ---
  
  def get_fii_dii_holdings(
    self, 
    symbol: str, 
    quarter: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Get FII and DII holdings percentages.
    
    Args:
      symbol (str): Stock symbol.
      quarter (str, optional): Quarter in "Q1FY24" format. Defaults to latest.
      
    Returns:
      Dict[str, Any]: FII and DII holdings data.
      
    Example Response:
      {
        "symbol": "RELIANCE",
        "quarter": "Q4FY23",
        "fii_percentage": 24.3,
        "dii_percentage": 18.7,
        "institutional_total": 43.0,
        "unit": "%"
      }
    """
    params = {"symbol": symbol}
    
    if quarter:
      params["quarter"] = quarter
    
    logger.debug("Fetching FII/DII holdings for %s", symbol)
    return self._make_request("GET", self._routes["analytics.ownership.fii_dii"], params=params)
  
  def get_fii_change(self, symbol: str) -> Dict[str, Any]:
    """
    Get FII holding change from previous quarter.
    
    Args:
      symbol (str): Stock symbol.
      
    Returns:
      Dict[str, Any]: FII change data.
      
    Example Response:
      {
        "symbol": "INFY",
        "quarter": "2025-03-31",
        "fii_change": 1.2,
        "current_fii": 33.5,
        "previous_fii": 32.3,
        "unit": "%"
      }
    """
    params = {"symbol": symbol}
    
    logger.debug("Fetching FII change for %s", symbol)
    return self._make_request("GET", self._routes["analytics.ownership.fii_change"], params=params)
  
  def get_dii_change(self, symbol: str) -> Dict[str, Any]:
    """
    Get DII holding change from previous quarter.
    
    Args:
      symbol (str): Stock symbol.
      
    Returns:
      Dict[str, Any]: DII change data.
      
    Example Response:
      {
        "symbol": "INFY",
        "quarter": "2025-03-31",
        "dii_change": -0.5,
        "current_dii": 15.2,
        "previous_dii": 15.7,
        "unit": "%"
      }
    """
    params = {"symbol": symbol}
    
    logger.debug("Fetching DII change for %s", symbol)
    return self._make_request("GET", self._routes["analytics.ownership.dii_change"], params=params)
  
  # --- Index Data Methods ---
  
  def get_index_ohlc_daily(
    self, 
    symbol: str, 
    start_date: str,
    end_date: str
  ) -> Dict[str, Any]:
    """
    Get daily OHLC data for an index.
    
    Args:
      symbol (str): Index symbol (e.g., "NIFTY50").
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      
    Returns:
      Dict[str, Any]: Index OHLC data.
      
    Example Response:
      {
        "data": [
          {
            "date": "2025-01-01",
            "open": 18250.0,
            "high": 18350.0,
            "low": 18200.0,
            "close": 18325.0,
            "symbol": "NIFTY50"
          }
        ]
      }
    """
    params = self._normalize_params({
      "index": symbol,
      "startDate": start_date,
      "endDate": end_date
    })
    
    logger.debug("Fetching index OHLC daily data for %s", symbol)
    return self._make_request("GET", self._routes["analytics.marketdata.index_ohlc_daily"], params=params)
  
  # --- Metrics Methods ---
  
  def get_sortino_ratio(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    rf: float = 0.065,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get Sortino ratio for a stock/strategy/index.
    
    Args:
      symbol (str): Stock/strategy/index symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      rf (float, optional): Annualized risk-free rate. Defaults to 0.065.
      interval (str, optional): Return frequency: daily, weekly, monthly. Defaults to "daily".
      
    Returns:
      Dict[str, Any]: Sortino ratio data.
      
    Example Response:
      {
        "symbol": "HDFCBANK",
        "startDate": "2024-01-01",
        "endDate": "2025-01-01",
        "interval": "daily",
        "rf": 0.065,
        "sortinoRatio": 1.8542,
        "annualizedReturn": 0.1234,
        "downsideDeviation": 0.0321,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "rf": rf,
      "interval": interval
    })
    
    logger.debug("Fetching Sortino ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.metrics.sortino_ratio"], params=params)
  
  def get_upside_capture(
    self,
    symbol: str,
    benchmark_symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get upside capture ratio for a stock/portfolio.
    
    Args:
      symbol (str): Stock/portfolio symbol.
      benchmark_symbol (str): Benchmark symbol.
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      interval (str, optional): Comparison interval. Defaults to "daily".
      
    Returns:
      Dict[str, Any]: Upside capture ratio data.
      
    Example Response:
      {
        "symbol": "ICICIBANK",
        "benchmarkSymbol": "NIFTY50",
        "startDate": "2024-01-01",
        "endDate": "2025-01-01",
        "interval": "daily",
        "upsideCaptureRatio": 112.50,
        "periodsAnalyzed": 250,
        "positiveBenchmarkPeriods": 135,
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "benchmarkSymbol": benchmark_symbol,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching upside capture ratio for %s vs %s", symbol, benchmark_symbol)
    return self._make_request("GET", self._routes["analytics.metrics.upside_capture"], params=params)
  
  # --- Macro Methods ---
  
  def get_risk_free_rate(
    self,
    start_date: str,
    end_date: str,
    tenor: str = "10Y",
    country: str = "IN",
    method: str = "average"
  ) -> Dict[str, Any]:
    """
    Get risk-free rates for various tenors and countries.
    
    Args:
      start_date (str): Start date in "YYYY-MM-DD" format.
      end_date (str): End date in "YYYY-MM-DD" format.
      tenor (str, optional): Maturity: 3M, 6M, 1Y, 5Y, 10Y. Defaults to "10Y".
      country (str, optional): Country code. Defaults to "IN".
      method (str, optional): Calculation: average, start, end, daily_series. Defaults to "average".
      
    Returns:
      Dict[str, Any]: Risk-free rate data.
      
    Example Response:
      {
        "country": "IN",
        "tenor": "10Y",
        "startDate": "2024-01-01",
        "endDate": "2024-12-31",
        "method": "average",
        "riskFreeRate": 0.0735,
        "source": "RBI/FIMMDA (Default)",
        "unit": "decimal"
      }
    """
    params = self._normalize_params({
      "startDate": start_date,
      "endDate": end_date,
      "tenor": tenor,
      "country": country,
      "method": method
    })
    
    logger.debug("Fetching risk-free rate for %s %s", country, tenor)
    return self._make_request("GET", self._routes["analytics.macro.risk_free_rate"], params=params)
  
  # --- Risk Analysis Methods ---
  
  def get_max_drawdown(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    adjusted: bool = True,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Calculate maximum drawdown for a stock over a specified period.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Analysis start date (YYYY-MM-DD).
      end_date (str): Analysis end date (YYYY-MM-DD).
      adjusted (bool, optional): Use adjusted prices. Defaults to True.
      interval (str, optional): Data frequency: daily, weekly, monthly. Defaults to "daily".
      
    Returns:
      Dict[str, Any]: Maximum drawdown data.
      
    Example Response:
      {
        "symbol": "TCS",
        "startDate": "2024-01-01",
        "endDate": "2024-12-31",
        "adjusted": true,
        "interval": "daily",
        "maxDrawdown": -0.1847,
        "peakDate": "2024-03-15",
        "troughDate": "2024-06-08",
        "peakPrice": 4250.50,
        "troughPrice": 3465.75,
        "unit": "decimal"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted,
      "interval": interval
    })
    
    logger.debug("Fetching max drawdown for %s", symbol)
    return self._make_request("GET", self._routes["analytics.risk.max_drawdown"], params=params)
  
  def get_returns_volatility(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    frequency: str = "daily",
    periods: Optional[int] = None
  ) -> Dict[str, Any]:
    """
    Calculate returns volatility using standard deviation over a specified period.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Analysis start date (YYYY-MM-DD).
      end_date (str): Analysis end date (YYYY-MM-DD).
      frequency (str, optional): Return frequency: daily, weekly, monthly. Defaults to "daily".
      periods (int, optional): Rolling window size (5-250). Auto-calculated if not provided.
      
    Returns:
      Dict[str, Any]: Volatility analysis data.
      
    Example Response:
      {
        "symbol": "INFY",
        "startDate": "2024-01-01",
        "endDate": "2024-06-30",
        "frequency": "daily",
        "volatility": 0.0243,
        "annualizedVolatility": 0.3856,
        "periods": 125,
        "unit": "decimal"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "frequency": frequency
    })
    
    if periods is not None:
      params["periods"] = str(periods)
    
    logger.debug("Fetching returns volatility for %s", symbol)
    return self._make_request("GET", self._routes["analytics.risk.returns_volatility"], params=params)
  
  # --- Metadata Methods ---
  
  def get_sector_classification(
    self,
    symbol: str
  ) -> Dict[str, Any]:
    """
    Get comprehensive sector and industry classification for a stock.
    
    Args:
      symbol (str): Stock symbol.
      
    Returns:
      Dict[str, Any]: Sector classification data.
      
    Example Response:
      {
        "symbol": "TATASTEEL",
        "sector": "Basic Materials",
        "industry": "Steel",
        "subIndustry": "Integrated Steel",
        "classification": "Industrial Metals & Mining",
        "lastUpdated": "2024-01-15"
      }
    """
    params = self._normalize_params({
      "symbol": symbol
    })
    
    logger.debug("Fetching sector classification for %s", symbol)
    return self._make_request("GET", self._routes["analytics.metadata.sector"], params=params)
  
  # --- Leverage Analysis Methods ---
  
  def get_debt_equity_ratio(
    self,
    symbol: str,
    date: Optional[str] = None,
    consolidated: bool = True
  ) -> Dict[str, Any]:
    """
    Calculate debt-to-equity ratio using most recent financial data.
    
    Args:
      symbol (str): Stock symbol.
      date (str, optional): Specific quarter-end date (YYYY-MM-DD). Latest if not provided.
      consolidated (bool, optional): Use consolidated financials. Defaults to True.
      
    Returns:
      Dict[str, Any]: Debt-to-equity ratio data.
      
    Example Response:
      {
        "symbol": "RELIANCE",
        "date": "2024-09-30",
        "deRatio": 0.3247,
        "totalDebt": 287450.25,
        "shareholderEquity": 884972.10,
        "source": "consolidated",
        "quarter": "Q2FY25",
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "consolidated": consolidated
    })
    
    if date:
      params["date"] = date
    
    logger.debug("Fetching debt-to-equity ratio for %s", symbol)
    return self._make_request("GET", self._routes["analytics.leverage.debt_equity_ratio"], params=params)
  
  def get_cagr(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    adjusted: bool = True
  ) -> Dict[str, Any]:
    """
    Calculate Compound Annual Growth Rate (CAGR) over a specified time period.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Investment start date (YYYY-MM-DD).
      end_date (str): Investment end date (YYYY-MM-DD).
      adjusted (bool, optional): Use adjusted prices. Defaults to True.
      
    Returns:
      Dict[str, Any]: CAGR calculation data.
      
    Example Response:
      {
        "symbol": "TCS",
        "startDate": "2020-01-01",
        "endDate": "2024-12-31",
        "cagr": 12.45,
        "startPrice": 2150.30,
        "endPrice": 3847.60,
        "years": 5.0,
        "adjusted": true,
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted
    })
    
    logger.debug("Fetching CAGR for %s from %s to %s", symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.returns.cagr"], params=params)

  # --- New Analytics Methods ---
  
  def get_average_traded_volume(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get average traded volume for a stock over a specified period.
    
    Args:
      symbol (str): Stock symbol (e.g., HDFCBANK, NSE:RELIANCE).
      start_date (str): Period start date (YYYY-MM-DD).
      end_date (str): Period end date (YYYY-MM-DD).
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Average volume data.
      
    Example Response:
      {
        "symbol": "HDFCBANK",
        "startDate": "2024-04-01",
        "endDate": "2024-06-30",
        "interval": "daily",
        "averageVolume": 1234567,
        "totalDays": 61,
        "unit": "shares"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching average traded volume for %s from %s to %s", symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.marketdata.average_volume"], params=params)
  
  def get_index_max_drawdown(
    self,
    index_symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get maximum drawdown for an index over a specified period.
    
    Args:
      index_symbol (str): Index symbol (e.g., NIFTY50, BANKNIFTY, SENSEX).
      start_date (str): Period start date (YYYY-MM-DD).
      end_date (str): Period end date (YYYY-MM-DD).
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Maximum drawdown data.
      
    Example Response:
      {
        "indexSymbol": "NIFTY50",
        "startDate": "2023-01-01",
        "endDate": "2024-01-01",
        "interval": "daily",
        "maxDrawdown": -15.23,
        "drawdownDate": "2023-10-26",
        "peakDate": "2023-09-19",
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "indexSymbol": index_symbol,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching index max drawdown for %s from %s to %s", index_symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.index.max_drawdown"], params=params)
  
  def get_drawdown_duration(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get drawdown duration analysis for a stock or index.
    
    Args:
      symbol (str): Stock or index symbol (e.g., INFY, NIFTY50).
      start_date (str): Start of analysis period (YYYY-MM-DD).
      end_date (str): End of analysis period (YYYY-MM-DD).
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Drawdown duration data.
      
    Example Response:
      {
        "symbol": "INFY",
        "startDate": "2022-01-01",
        "endDate": "2024-01-01",
        "interval": "daily",
        "maxDrawdownDuration": 147,
        "averageDrawdownDuration": 23.5,
        "totalDrawdowns": 12,
        "unit": "days"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching drawdown duration for %s from %s to %s", symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.instrument.drawdown_duration"], params=params)
  
  def get_rolling_peak_price(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    window: int,
    adjusted: bool = True,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get rolling peak price analysis for a stock.
    
    Args:
      symbol (str): Stock symbol (e.g., RELIANCE, NSE:TCS).
      start_date (str): Start of evaluation period (YYYY-MM-DD).
      end_date (str): End of evaluation period (YYYY-MM-DD).
      window (int): Rolling window size in days (1-252).
      adjusted (bool, optional): Adjust for corporate actions. Defaults to True.
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Rolling peak price data.
      
    Example Response:
      {
        "symbol": "NSE:TCS",
        "startDate": "2024-01-01",
        "endDate": "2024-06-30",
        "window": 20,
        "interval": "daily",
        "adjusted": true,
        "data": [
          {"date": "2024-01-01", "price": 3500.0, "rollingPeak": 3500.0},
          {"date": "2024-01-02", "price": 3520.0, "rollingPeak": 3520.0}
        ]
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "window": window,
      "adjusted": adjusted,
      "interval": interval
    })
    
    logger.debug("Fetching rolling peak price for %s from %s to %s with window %d", symbol, start_date, end_date, window)
    return self._make_request("GET", self._routes["analytics.price.rolling_peak"], params=params)
  
  def get_rolling_price_mean(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    window: int,
    adjusted: bool = True,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get rolling mean price analysis for a stock.
    
    Args:
      symbol (str): Stock symbol (e.g., HDFCBANK, NSE:WIPRO).
      start_date (str): Start of evaluation period (YYYY-MM-DD).
      end_date (str): End of evaluation period (YYYY-MM-DD).
      window (int): Rolling window size in days (1-252).
      adjusted (bool, optional): Adjust for corporate actions. Defaults to True.
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Rolling mean price data.
      
    Example Response:
      {
        "symbol": "NSE:HDFCBANK",
        "startDate": "2024-01-01",
        "endDate": "2024-06-30",
        "window": 20,
        "interval": "daily",
        "adjusted": true,
        "data": [
          {"date": "2024-01-01", "price": 1500.0, "rollingMean": 1500.0},
          {"date": "2024-01-02", "price": 1510.0, "rollingMean": 1505.0}
        ]
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "window": window,
      "adjusted": adjusted,
      "interval": interval
    })
    
    logger.debug("Fetching rolling mean price for %s from %s to %s with window %d", symbol, start_date, end_date, window)
    return self._make_request("GET", self._routes["analytics.price.rolling_mean"], params=params)
  
  def get_realized_volatility(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    adjusted: bool = True,
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get realized price volatility for a stock.
    
    Args:
      symbol (str): Stock symbol or instrument ID (e.g., NSE:ITC, BHARTIARTL).
      start_date (str): Start of volatility calculation window (YYYY-MM-DD).
      end_date (str): End of volatility calculation window (YYYY-MM-DD).
      adjusted (bool, optional): Adjust prices for corporate actions. Defaults to True.
      interval (str, optional): Time interval ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
      
    Returns:
      Dict[str, Any]: Realized volatility data.
      
    Example Response:
      {
        "symbol": "NSE:ITC",
        "startDate": "2024-01-01",
        "endDate": "2024-06-30",
        "interval": "daily",
        "adjusted": true,
        "realizedVolatility": 22.45,
        "annualizedVolatility": 35.67,
        "unit": "%"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted,
      "interval": interval
    })
    
    logger.debug("Fetching realized volatility for %s from %s to %s", symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.volatility.realized"], params=params)
  
  def get_beta_90d(
    self,
    symbol: str,
    benchmark: str = "NIFTY50"
  ) -> Dict[str, Any]:
    """
    Get 90-day CAPM Beta for a stock relative to a benchmark.
    
    Args:
      symbol (str): Stock symbol (e.g., RELIANCE, ITC).
      benchmark (str, optional): Benchmark index. Defaults to 'NIFTY50'.
      
    Returns:
      Dict[str, Any]: 90-day beta data.
      
    Example Response:
      {
        "symbol": "ITC",
        "benchmark": "NIFTY50",
        "period": "90d",
        "beta": 0.85,
        "correlation": 0.72,
        "rSquared": 0.52,
        "alpha": 0.03,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "benchmark": benchmark
    })
    
    logger.debug("Fetching 90d beta for %s vs %s", symbol, benchmark)
    return self._make_request("GET", self._routes["analytics.risk.beta_90d"], params=params)
  
  def get_beta_custom_period(
    self,
    symbol: str,
    benchmark: str,
    start_date: str,
    end_date: str
  ) -> Dict[str, Any]:
    """
    Get CAPM Beta for a stock relative to a benchmark over a custom period.
    
    Args:
      symbol (str): Stock symbol.
      benchmark (str): Benchmark index symbol.
      start_date (str): Start date (YYYY-MM-DD).
      end_date (str): End date (YYYY-MM-DD).
      
    Returns:
      Dict[str, Any]: Custom period beta data.
      
    Example Response:
      {
        "symbol": "ITC",
        "benchmark": "NIFTY50",
        "startDate": "2023-01-01",
        "endDate": "2025-01-01",
        "beta": 0.87,
        "correlation": 0.74,
        "rSquared": 0.55,
        "alpha": 0.02,
        "unit": "ratio"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "benchmark": benchmark,
      "startDate": start_date,
      "endDate": end_date
    })
    
    logger.debug("Fetching custom period beta for %s vs %s from %s to %s", symbol, benchmark, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.risk.beta_custom"], params=params)

  def get_strategy_max_drawdown(
    self, 
    strategy_id: str, 
    start_date: str, 
    end_date: str, 
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get maximum drawdown for a strategy over a specified period.
    
    Args:
      strategy_id (str): Strategy identifier.
      start_date (str): Start date (YYYY-MM-DD).
      end_date (str): End date (YYYY-MM-DD).
      interval (str): Time interval ('daily', 'weekly', 'monthly').
      
    Returns:
      Dict[str, Any]: Strategy max drawdown data.
      
    Example Response:
      {
        "strategyId": "str_01jspb8z36edjsp5pecqq0mpm3",
        "startDate": "2023-01-01",
        "endDate": "2024-12-31",
        "maxDrawdown": -0.15,
        "peakDate": "2023-06-15",
        "troughDate": "2023-09-20",
        "peakNav": 1.25,
        "troughNav": 1.06
      }
    """
    params = self._normalize_params({
      "strategyId": strategy_id,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching max drawdown for strategy %s from %s to %s", strategy_id, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.strategy.drawdown_max"], params=params)

  def get_product_max_drawdown(
    self, 
    product_id: str, 
    start_date: str, 
    end_date: str, 
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Get maximum drawdown for a product over a specified period.
    
    Args:
      product_id (str): Product identifier.
      start_date (str): Start date (YYYY-MM-DD).
      end_date (str): End date (YYYY-MM-DD).
      interval (str): Time interval ('daily', 'weekly', 'monthly').
      
    Returns:
      Dict[str, Any]: Product max drawdown data.
      
    Example Response:
      {
        "productId": "prd_01jyrg7ffkemq9hz3rkeznh9dr",
        "startDate": "2023-01-01",
        "endDate": "2024-12-31",
        "maxDrawdown": -0.12,
        "peakDate": "2023-05-10",
        "troughDate": "2023-08-15",
        "peakNav": 1.18,
        "troughNav": 1.04
      }
    """
    params = self._normalize_params({
      "productId": product_id,
      "startDate": start_date,
      "endDate": end_date,
      "interval": interval
    })
    
    logger.debug("Fetching max drawdown for product %s from %s to %s", product_id, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.product.drawdown_max"], params=params)

  def get_atr(
    self, 
    symbol: str, 
    start_date: str, 
    end_date: str, 
    window: int, 
    adjusted: bool = True, 
    interval: str = "daily"
  ) -> Dict[str, Any]:
    """
    Calculate Average True Range (ATR) for a security over a specified period.
    
    Args:
      symbol (str): Stock symbol.
      start_date (str): Start date (YYYY-MM-DD).
      end_date (str): End date (YYYY-MM-DD).
      window (int): Lookback period (e.g., 14, 20).
      adjusted (bool): Adjust for splits/dividends.
      interval (str): Time interval ('daily', 'weekly', 'intraday').
      
    Returns:
      Dict[str, Any]: ATR data.
      
    Example Response:
      {
        "symbol": "AXISBANK",
        "startDate": "2023-01-01",
        "endDate": "2024-12-31",
        "window": 14,
        "adjusted": true,
        "atr": [
          {
            "date": "2023-01-15",
            "atrValue": 25.67
          }
        ]
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "window": window,
      "adjusted": adjusted,
      "interval": interval
    })
    
    logger.debug("Fetching ATR for %s with window %d from %s to %s", symbol, window, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.volatility.atr"], params=params)

  def get_simple_return(
    self, 
    symbol: str, 
    start_date: str, 
    end_date: str, 
    adjusted: bool = True, 
    interval: str = "daily", 
    benchmark: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Calculate simple return for a security or sectoral index.
    
    Args:
      symbol (str): Stock/index symbol.
      start_date (str): Start date (YYYY-MM-DD).
      end_date (str): End date (YYYY-MM-DD).
      adjusted (bool): Adjust for corporate actions.
      interval (str): Time interval ('daily', 'weekly', 'monthly').
      benchmark (str, optional): Benchmark for relative return calculation.
      
    Returns:
      Dict[str, Any]: Simple return data.
      
    Example Response:
      {
        "symbol": "NIFTY IT",
        "startDate": "2023-01-01",
        "endDate": "2024-12-31",
        "adjusted": true,
        "totalReturn": 0.15,
        "startPrice": 1250.0,
        "endPrice": 1437.5,
        "benchmarkReturn": 0.12,
        "relativeReturn": 0.03,
        "unit": "decimal"
      }
    """
    params = self._normalize_params({
      "symbol": symbol,
      "startDate": start_date,
      "endDate": end_date,
      "adjusted": adjusted,
      "interval": interval,
      "benchmark": benchmark
    })
    
    logger.debug("Fetching simple return for %s from %s to %s", symbol, start_date, end_date)
    return self._make_request("GET", self._routes["analytics.returns.simple"], params=params)
