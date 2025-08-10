import asyncio
import json
import os
import logging
import random
from typing import Callable, List, Optional, Any, Iterator

import websockets
from websockets.exceptions import ConnectionClosed
from websockets.protocol import State

# Setup module‐level logger with a default handler if none exists.
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class QuotesClient:
    """
    A Python SDK for connecting to the Quotes Server via WebSocket.

    Attributes:
      base_url (str): WebSocket URL of the quotes server.
      token (str): JWT token for authentication.
      log_level (str): Logging level. Options: "error", "info", "debug".
      on_tick (Callable): Callback for tick messages (type='ticks' or no type field).
      on_stats (Callable): Callback for stats/greeks messages (type='greeks').
      on_order (Callable): Callback for order events (type='order').
      on_trade (Callable): Callback for trade events (type='trade').
      on_position (Callable): Callback for position events (type='position').
      on_holding (Callable): Callback for holding events (type='holding').
      on_connect (Callable): Callback when connection is established.
      on_close (Callable): Callback when connection is closed.
      on_error (Callable): Callback for errors.
    
    Message Routing:
      - Legacy messages with type='ticks' are routed to on_tick callback
      - Legacy messages with type='greeks' are routed to on_stats callback
      - Event messages with type='order' are routed to on_order callback
      - Event messages with type='trade' are routed to on_trade callback
      - Event messages with type='position' are routed to on_position callback
      - Event messages with type='holding' are routed to on_holding callback
      - Messages without type field are routed to on_tick for backward compatibility
      - Messages are silently dropped if the appropriate handler is not registered
    
    Message Structure Support:
      - Legacy Format: {type: "ticks", ...data} or {...data} (no type)
      - New Event Format: {type: "position", data: {...actualData}} - automatically normalized
      - All handlers receive flattened message structure with type preserved at root level
    
    Event Handler Signature:
      All event handlers follow the same signature: handler(ws: QuotesClient, event_data: dict)
      
    Example:
      def on_order_event(ws, order):
          print(f"Order {order['id']}: {order['status']}")
      
      client.on_order = on_order_event
      client.connect()
    """

    ACTION_SUBSCRIBE = "subscribe"
    ACTION_UNSUBSCRIBE = "unsubscribe"
    
    # Subscription modes
    MODE_GREEKS = "greeks"
    MODE_TICKS = "ticks"
    MODE_FULL = "full"

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        log_level: str = "error",
        max_message_size: int = 10 * 1024 * 1024,
        batch_size: int = 20
    ):
        valid_levels = {"error": logging.ERROR, "info": logging.INFO, "debug": logging.DEBUG}
        if log_level not in valid_levels:
            raise ValueError(f"log_level must be one of {list(valid_levels.keys())}")
        logger.setLevel(valid_levels[log_level])

        self.log_level = log_level
        self.max_message_size = max_message_size
        self.batch_size = batch_size

        self.base_url = base_url or os.environ.get("WZ__QUOTES_BASE_URL")
        self.token = token or os.environ.get("WZ__TOKEN")
        if not self.token:
            raise ValueError("JWT token must be provided as an argument or in .env (WZ__TOKEN)")
        if not self.base_url:
            raise ValueError("Base URL must be provided as an argument or in .env (WZ__QUOTES_BASE_URL)")

        self.url = f"{self.base_url}?token={self.token}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.subscribed_instruments: set = set()
        self.subscription_modes: dict = {}  # instrument -> mode mapping
        self._running = False
        self._background_task = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        self._backoff_base = 1
        self._backoff_factor = 2
        self._backoff_max = 60

        # Callbacks are plain synchronous functions
        self.on_tick: Optional[Callable[[Any, dict], None]] = None
        self.on_stats: Optional[Callable[[Any, dict], None]] = None
        self.on_connect: Optional[Callable[[Any], None]] = None
        self.on_close: Optional[Callable[[Any, Optional[int], Optional[str]], None]] = None
        self.on_error: Optional[Callable[[Any, Exception], None]] = None
        
        # Event callbacks for account events
        self.on_order: Optional[Callable[[Any, dict], None]] = None
        self.on_trade: Optional[Callable[[Any, dict], None]] = None
        self.on_position: Optional[Callable[[Any, dict], None]] = None
        self.on_holding: Optional[Callable[[Any, dict], None]] = None

        logger.debug("Initialized QuotesClient with URL: %s", self.url)

    def _chunk_list(self, data: List[Any], chunk_size: int) -> Iterator[List[Any]]:
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def _normalize_message(self, raw_message: dict) -> dict:
        """
        Normalize message structure to handle both legacy and new formats.
        
        Legacy Format (Ticks/Greeks): {type: "ticks", ...data} or {...data} (no type)
        New Format (Events): {type: "position", data: {...actualData}}
        
        Returns: Flattened message with type preserved at root level
        """
        try:
            # Check if message has both 'type' and 'data' fields (new format)
            if 'type' in raw_message and 'data' in raw_message:
                # New format: Extract type, merge data into root level
                message_type = raw_message['type']
                data = raw_message['data']
                if isinstance(data, dict):
                    # Create flattened message with type preserved
                    normalized = {'type': message_type}
                    normalized.update(data)
                    logger.debug("Normalized new format message: type=%s", message_type)
                    return normalized
                else:
                    # Data is not a dict, keep original structure
                    logger.debug("Data field is not a dict, keeping original structure")
                    return raw_message
            else:
                # Legacy format: Use as-is (either has type only or no type)
                logger.debug("Legacy format message detected")
                return raw_message
                
        except Exception as e:
            logger.debug("Error normalizing message: %s, using original", e)
            return raw_message

    async def _connect_with_backoff(self) -> None:
        backoff = self._backoff_base

        while self._running:
            try:
                logger.info("Connecting to %s ...", self.url)
                async with websockets.connect(self.url, max_size=self.max_message_size) as websocket:
                    self.ws = websocket
                    logger.info("Connected to the quotes server.")

                    # plain sync on_connect
                    if self.on_connect:
                        try:
                            self.on_connect(self)
                        except Exception as e:
                            logger.error("Error in on_connect callback: %s", e, exc_info=True)

                    # re-subscribe on reconnect with modes
                    if self.subscribed_instruments:
                        # Group instruments by mode for efficient re-subscription
                        mode_groups = {}
                        for instrument in self.subscribed_instruments:
                            mode = self.subscription_modes.get(instrument, self.MODE_TICKS)
                            if mode not in mode_groups:
                                mode_groups[mode] = []
                            mode_groups[mode].append(instrument)
                        
                        for mode, instruments in mode_groups.items():
                            for batch in self._chunk_list(instruments, self.batch_size):
                                msg = {
                                    "action": self.ACTION_SUBSCRIBE, 
                                    "instruments": batch,
                                    "mode": mode
                                }
                                await self.ws.send(json.dumps(msg))
                                logger.info("Re-subscribed to %d instruments with mode '%s'", len(batch), mode)
                                await asyncio.sleep(0.1)

                    backoff = self._backoff_base
                    await self._handle_messages()

            except ConnectionClosed as e:
                logger.info("Disconnected: %s", e)
                if self.on_close:
                    try:
                        self.on_close(self, getattr(e, 'code', None), str(e))
                    except Exception as ex:
                        logger.error("Error in on_close callback: %s", ex, exc_info=True)

            except Exception as e:
                logger.error("Connection error: %s", e, exc_info=True)
                if self.on_error:
                    try:
                        self.on_error(self, e)
                    except Exception as ex:
                        logger.error("Error in on_error callback: %s", ex, exc_info=True)

            if not self._running:
                break

            sleep_time = min(backoff, self._backoff_max)
            logger.info("Reconnecting in %s seconds...", sleep_time)
            await asyncio.sleep(sleep_time)
            backoff = backoff * self._backoff_factor + random.uniform(0, 1)

    async def _handle_messages(self) -> None:
        try:
            async for message in self.ws:  # type: ignore
                if self.log_level == "debug" and isinstance(message, str):
                    size = len(message.encode("utf-8"))
                    if size > 1024 * 1024:
                        logger.debug("Large message: %d bytes", size)

                if isinstance(message, str):
                    for chunk in message.strip().split("\n"):
                        if not chunk:
                            continue
                        try:
                            raw_data = json.loads(chunk)
                            # Normalize message structure
                            data = self._normalize_message(raw_data)
                            # Route based on message type
                            message_type = data.get('type')
                            
                            if message_type == 'greeks':
                                if self.on_stats:
                                    try:
                                        self.on_stats(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_stats handler: %s", e)
                                else:
                                    logger.debug("Received greeks message but no on_stats handler registered")
                            elif message_type == 'ticks':
                                if self.on_tick:
                                    try:
                                        self.on_tick(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_tick handler: %s", e)
                                else:
                                    logger.debug("Received ticks message but no on_tick handler registered")
                            elif message_type == 'order':
                                if self.on_order:
                                    try:
                                        self.on_order(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_order handler: %s", e)
                                else:
                                    logger.debug("Received order event but no on_order handler registered")
                            elif message_type == 'trade':
                                if self.on_trade:
                                    try:
                                        self.on_trade(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_trade handler: %s", e)
                                else:
                                    logger.debug("Received trade event but no on_trade handler registered")
                            elif message_type == 'position':
                                if self.on_position:
                                    try:
                                        self.on_position(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_position handler: %s", e)
                                else:
                                    logger.debug("Received position event but no on_position handler registered")
                            elif message_type == 'holding':
                                if self.on_holding:
                                    try:
                                        self.on_holding(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_holding handler: %s", e)
                                else:
                                    logger.debug("Received holding event but no on_holding handler registered")
                            else:
                                # No type field - send to on_tick for backward compatibility
                                if self.on_tick:
                                    try:
                                        self.on_tick(self, data)
                                    except Exception as e:
                                        logger.debug("Error in on_tick handler: %s", e)
                                else:
                                    logger.debug("Received message without type field and no on_tick handler registered")
                        except json.JSONDecodeError as e:
                            logger.error("JSON parse error: %s", e)
                else:
                    logger.warning("Non-string message: %s", type(message))
        except ConnectionClosed:
            logger.info("Connection closed during message handling")
        except Exception as e:
            logger.error("Error processing message: %s", e, exc_info=True)
            if self.on_error:
                try:
                    self.on_error(self, e)
                except Exception:
                    pass

    # -- Async core methods (for internal use) --

    async def _subscribe_async(self, instruments: List[str], mode: str = MODE_TICKS) -> None:
        if self.ws and self.ws.state == State.OPEN:
            new = set(instruments) - self.subscribed_instruments
            if new:
                self.subscribed_instruments |= new
                # Track mode for each instrument
                for instrument in new:
                    self.subscription_modes[instrument] = mode
                
                for batch in self._chunk_list(list(new), self.batch_size):
                    logger.info("Subscribing to %d instruments with mode '%s'", len(batch), mode)
                    message = {
                        "action": self.ACTION_SUBSCRIBE,
                        "instruments": batch,
                        "mode": mode
                    }
                    print(f"Subscribing to {batch} with mode {mode}")
                    await self.ws.send(json.dumps(message))
                    await asyncio.sleep(0.1)
        else:
            self.subscribed_instruments |= set(instruments)
            # Track mode for each instrument
            for instrument in instruments:
                self.subscription_modes[instrument] = mode

    async def _unsubscribe_async(self, instruments: List[str]) -> None:
        if self.ws and self.ws.state == State.OPEN:
            to_remove = set(instruments) & self.subscribed_instruments
            if to_remove:
                self.subscribed_instruments -= to_remove
                # Remove mode tracking for unsubscribed instruments
                for instrument in to_remove:
                    self.subscription_modes.pop(instrument, None)
                
                for batch in self._chunk_list(list(to_remove), self.batch_size):
                    logger.info("Unsubscribing from %d instruments", len(batch))
                    await self.ws.send(json.dumps({
                        "action": self.ACTION_UNSUBSCRIBE,
                        "instruments": batch
                    }))
                    await asyncio.sleep(0.1)
        else:
            self.subscribed_instruments -= set(instruments)
            # Remove mode tracking for unsubscribed instruments
            for instrument in instruments:
                self.subscription_modes.pop(instrument, None)

    # -- Public wrappers for plain callback users --

    def subscribe(self, instruments: List[str], mode: str = MODE_TICKS) -> None:
        """
        Schedule subscribe onto the client’s event loop.
        """
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._subscribe_async(instruments, mode),
                self._loop
            )
        else:
            self.subscribed_instruments |= set(instruments)
            # Track mode for each instrument
            for instrument in instruments:
                self.subscription_modes[instrument] = mode

    def unsubscribe(self, instruments: List[str]) -> None:
        """
        Schedule unsubscribe onto the client’s event loop.
        """
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._unsubscribe_async(instruments),
                self._loop
            )
        else:
            self.subscribed_instruments -= set(instruments)
            # Remove mode tracking for unsubscribed instruments
            for instrument in instruments:
                self.subscription_modes.pop(instrument, None)

    def unsubscribe_all(self) -> None:
        """
        Unsubscribe from all currently subscribed instruments.
        """
        if self.subscribed_instruments:
            self.unsubscribe(list(self.subscribed_instruments))

    async def close(self) -> None:
        """
        Close the WebSocket connection.
        """
        self._running = False
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket closed.")
        if self._background_task and not self._background_task.done():
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass

    def connect(self) -> None:
        """
        Blocking connect (runs the internal asyncio loop until stop()).
        """
        self._running = True
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self._loop = loop

        try:
            loop.run_until_complete(self._connect_with_backoff())
        finally:
            if not loop.is_closed():
                tasks = asyncio.all_tasks(loop)
                for t in tasks:
                    t.cancel()
                try:
                    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                except Exception:
                    pass

    def connect_async(self) -> None:
        """
        Non-blocking connect: starts the background task.
        """
        if self._running:
            logger.warning("Client already running.")
            return
        self._running = True
        loop = asyncio.get_event_loop()
        self._loop = loop
        self._background_task = loop.create_task(self._connect_with_backoff())

    def stop(self) -> None:
        """
        Signal the client to stop and close.
        """
        self._running = False
        logger.info("Client stopping; will close soon.")
