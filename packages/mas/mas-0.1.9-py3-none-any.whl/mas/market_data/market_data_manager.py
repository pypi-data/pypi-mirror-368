import threading
import time
import MetaTrader5 as mt5
from datetime import datetime
from mas.receive.receive_manage import ReceiveManager
from mas.connection.connection import ConnectionManager
from mas.lang.i18n_strings import get_text, MarketText


class MarketDataManager:
    def __init__(self, receiver: ReceiveManager, connection: ConnectionManager):
        """
        初始化 MarketManager 實例，設定 Tick / Bar 訂閱管理結構與執行緒安全控制，並注入資料接收器與連線管理器。

        Args:
            receiver (ReceiveManager): 用於接收 Tick 與 Bar 推播資料的接收器實例。
            connection (ConnectionManager): 用於處理 Symbol 查詢與 MT5 連線的連線管理器。

        Returns:
            None

        Initialize the MarketManager instance. Sets up tick/bar subscription containers, threading lock, 
        and receiver/connection interfaces.

        Args:
            receiver (ReceiveManager): The receiver instance that handles incoming tick and bar data.
            connection (ConnectionManager): The connection manager for handling symbol lookup and MT5 connection.

        Returns:
            None
        """
        self._tick_subscriptions = {}
        self._bar_subscriptions = {}
        self._lock = threading.Lock()
        self._running = True
        self._started = False
        self.receiver = receiver
        self.connection = connection

    def stop_all_subscriptions(self):
        """
        停止所有 Tick 與 Bar 的訂閱，並以執行緒安全方式重設訂閱狀態。

        設定 `_running` 為 False，並將所有已註冊的訂閱標記為停用狀態，
        避免背景推播任務繼續執行，並在終端輸出取消成功訊息。

        Args:
            None

        Returns:
            None

        Stop all active Tick and Bar subscriptions with thread-safe control.

        Sets `_running` to False, marks all registered subscriptions as inactive,
        and prevents background push loops from continuing. Confirmation messages will be printed.

        Args:
            None

        Returns:
            None
        """
        self._running = False

        with self._lock:
            for symbol in list(self._tick_subscriptions.keys()):
                self._tick_subscriptions[symbol] = False
            print(get_text(MarketText.TICK_ALL_STOP))
        with self._lock:
            for key in list(self._bar_subscriptions.keys()):
                self._bar_subscriptions[key] = False
            print(get_text(MarketText.BAR_ALL_STOP))

    def subscribe_ticks(self, params: dict) -> None:
        """
        訂閱指定商品的 Tick 資料，並啟動背景執行緒定時推播最新 Tick 給接收器。

        若該商品已在訂閱清單中，將忽略此次請求。
        每次推播僅在 Tick 資料有更新（time_msc 不同）時觸發，並透過 receiver.on_tick 傳送。
        本操作具執行緒安全控制，訂閱狀態將記錄於內部結構中。

        Args:
            params (dict): 訂閱參數，包含：
                - symbol (str): 必填，商品代碼。
                - interval_ms (int, optional): 推播間隔（毫秒），預設為 500。
                - flags (int, optional): Tick 模式旗標，預設為 mt5.COPY_TICKS_ALL。

        Returns:
            None

        Subscribe to Tick data for the specified symbol and start a background thread
        to push the latest Tick to the receiver at regular intervals.

        If the symbol is already subscribed, the request will be ignored.
        The push is triggered only when a new Tick is detected (based on time_msc).
        This operation is thread-safe, and the subscription status is managed internally.

        Args:
            params (dict): Subscription parameters:
                - symbol (str): Required. The symbol to subscribe.
                - interval_ms (int, optional): Push interval in milliseconds. Defaults to 500.
                - flags (int, optional): Tick retrieval mode flag. Defaults to mt5.COPY_TICKS_ALL.

        Returns:
            None
        """
        symbol = params.get("symbol")
        interval_ms = params.get("interval_ms", 500)
        flags = params.get("flags", mt5.COPY_TICKS_ALL)

        if not symbol:
            print(get_text(MarketText.TICK_NO_SYMBOL))
            return

        with self._lock:
            if symbol in self._tick_subscriptions:
                print(get_text(MarketText.TICK_ALREADY_SUBSCRIBED,symbol=symbol))
                return
            self._tick_subscriptions[symbol] = True

        def tick_worker():
            last_time_msc = None
            while self._tick_subscriptions.get(symbol, False) and self._running:
                try:
                    utc_now = datetime.utcnow()
                    ticks = mt5.copy_ticks_from(
                        self.connection.find_symbol(symbol), utc_now, 10, flags
                    )

                    if ticks is not None and len(ticks) > 0:
                        tick = ticks[-1]
                        tick_time_msc = tick['time_msc']

                        if tick_time_msc != last_time_msc:
                            last_time_msc = tick_time_msc
                            data = {
                                "symbol": symbol,
                                "time": datetime.utcfromtimestamp(tick['time']),
                                "bid": tick['bid'],
                                "ask": tick['ask'],
                                "last": tick['last'],
                                "volume": tick['volume']
                            }
                            self.receiver.on_tick(symbol, data)
                except Exception as e:
                    print(get_text(MarketText.TICK_READ_ERROR,msg=str(e)))
                time.sleep(interval_ms / 1000.0)

        thread = threading.Thread(
            target=tick_worker,
            daemon=False,
            name=f"TickThread-{symbol}"
        )
        thread.start()

        print(get_text(MarketText.TICK_SUBSCRIBED,
            symbol=symbol, interval=interval_ms))

    def unsubscribe_ticks(self, params: dict) -> None:
        """
        取消指定商品的 Tick 訂閱，並安全地更新內部訂閱狀態。

        若 symbol 未提供、或該商品尚未訂閱，則會回傳提示訊息。
        此操作具執行緒安全控制，會將對應 symbol 的訂閱Tag設為 False，以終止背景推播執行緒。

        Args:
            params (dict): 取消訂閱參數，包含：
                - symbol (str): 必填，欲取消訂閱的商品代碼。

        Returns:
            None

        Unsubscribe from the Tick feed of the specified symbol and safely update the internal subscription status.

        If the symbol is missing or not currently subscribed, a warning message will be printed.
        This operation is thread-safe and sets the corresponding subscription flag to False, effectively
        terminating the background pushing thread for that symbol.

        Args:
            params (dict): Unsubscription parameters:
                - symbol (str): Required. The symbol to unsubscribe.

        Returns:
            None
        """

        symbol = params.get("symbol")
        if not symbol:
            print(get_text(MarketText.TICK_UNSUB_NO_SYMBOL))
            return

        with self._lock:
            if symbol not in self._tick_subscriptions or not self._tick_subscriptions[symbol]:
                print(get_text(MarketText.TICK_UNSUB_NOT_EXIST,symbol=symbol))
                return
            self._tick_subscriptions[symbol] = False

        print(get_text(MarketText.TICK_UNSUB_SUCCESS,symbol=symbol))

    def subscribe_bars(self, params: dict) -> None:
        """
        訂閱指定商品與週期的 Bar（K 線）資料，並啟動背景執行緒定時推播至接收器。

        若該 symbol + timeframe 組合已存在訂閱，將忽略此次請求。
        每次推播僅在最新 Bar 資料更新時觸發，並透過 receiver.on_bar 傳送。
        支援模擬模式（backtest_toggle），並具備執行緒安全控制。

        Args:
            params (dict): 訂閱參數，包含：
                - symbol (str): 必填，商品代碼。
                - timeframe (str): 必填，時間週期（如 'M1', 'H1', 'D1'）。
                - interval_ms (int, optional): 推播間隔（毫秒），預設為 1000。
                - backtest_toggle (bool, optional): 是否為回測模式，預設 False。

        Returns:
            None

        Subscribe to Bar (candlestick) data for the specified symbol and timeframe,
        and launch a background thread to periodically push updated Bar data to the receiver.

        If the symbol-timeframe combination is already subscribed, the request will be ignored.
        The push will be triggered only when a new bar is detected.
        Supports backtesting mode (via backtest_toggle) and is thread-safe.

        Args:
            params (dict): Subscription parameters, including:
                - symbol (str): Required. Instrument symbol.
                - timeframe (str): Required. Timeframe string such as 'M1', 'H1', 'D1'.
                - interval_ms (int, optional): Push interval in milliseconds. Defaults to 1000.
                - backtest_toggle (bool, optional): Whether to use backtest mode. Defaults to False.

        Returns:
            None
        """
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")
        interval_ms = params.get("interval_ms", 1000)
        backtest_toggle = params.get("backtest_toggle", False)

        if not symbol or not timeframe:
            print(get_text(MarketText.BAR_NO_SYMBOL))
            return

        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M2": mt5.TIMEFRAME_M2,
            "M3": mt5.TIMEFRAME_M3,
            "M4": mt5.TIMEFRAME_M4,
            "M5": mt5.TIMEFRAME_M5,
            "M6": mt5.TIMEFRAME_M6,
            "M10": mt5.TIMEFRAME_M10,
            "M12": mt5.TIMEFRAME_M12,
            "M15": mt5.TIMEFRAME_M15,
            "M20": mt5.TIMEFRAME_M20,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H2": mt5.TIMEFRAME_H2,
            "H3": mt5.TIMEFRAME_H3,
            "H4": mt5.TIMEFRAME_H4,
            "H6": mt5.TIMEFRAME_H6,
            "H8": mt5.TIMEFRAME_H8,
            "H12": mt5.TIMEFRAME_H12,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }

        mt5_tf = timeframe_map.get(timeframe.upper())
        if mt5_tf is None:
            print(get_text(MarketText.BAR_UNSUPPORTED_TF,
                timeframe=timeframe))
            return

        key = f"{symbol}_{timeframe}"
        with self._lock:
            if key in self._bar_subscriptions:
                print(get_text(MarketText.BAR_ALREADY_SUBSCRIBED,key_name=key))
                return
            self._bar_subscriptions[key] = True

        def bar_worker():
            last_time = None
            while self._bar_subscriptions.get(key, False) and self._running:
                try:
                    if not backtest_toggle:
                        if not mt5.initialize():
                            print(get_text(MarketText.BAR_INIT_FAIL))
                            break

                    real_symbol = self.connection.find_symbol(symbol)
                    bars = mt5.copy_rates_from(
                        real_symbol, mt5_tf, datetime.now(), 2)

                    if bars is not None and len(bars) > 0:
                        bar = bars[-1]
                        bar_time = bar['time']
                        if bar_time != last_time:
                            last_time = bar_time
                            data = {
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "time": datetime.fromtimestamp(bar['time']),
                                "open": bar['open'],
                                "high": bar['high'],
                                "low": bar['low'],
                                "close": bar['close'],
                                "volume": bar['tick_volume']
                            }
                            self.receiver.on_bar(symbol, data)
                except Exception as e:
                    print(get_text(MarketText.BAR_SUB_ERROR,msg=str(e)))

                time.sleep(interval_ms / 1000.0)

        thread = threading.Thread(
            target=bar_worker, daemon=False, name=f"BarThread-{key}")
        thread.start()
        print(get_text(MarketText.BAR_SUBSCRIBED,
            symbol=symbol, timeframe=timeframe))

    def unsubscribe_bars(self, params: dict) -> None:
        """
        取消指定商品與時間週期的 Bar（K 線）資料訂閱，並更新內部狀態以終止推播。

        若該 symbol + timeframe 組合未曾訂閱，或已取消，將跳過處理並提示訊息。
        訂閱狀態更新採用執行緒安全設計，確保背景任務可正確終止。

        Args:
            params (dict): 取消訂閱參數，包含：
                - symbol (str): 必填，欲取消的商品代碼。
                - timeframe (str): 必填，對應時間週期（如 'M1', 'H1'）。

        Returns:
            None

        Unsubscribe from the Bar (candlestick) feed for the specified symbol and timeframe,
        and mark the internal subscription status as inactive to stop further pushing.

        If the symbol-timeframe combination is not subscribed or already unsubscribed,
        a warning message will be printed. This operation is thread-safe and ensures
        background workers can stop cleanly.

        Args:
            params (dict): Unsubscription parameters:
                - symbol (str): Required. Instrument symbol.
                - timeframe (str): Required. Timeframe such as 'M1', 'H1', etc.

        Returns:
            None
    """
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")

        if not symbol or not timeframe:
            print(get_text(MarketText.BAR_UNSUB_NO_SYMBOL))
            return

        key = f"{symbol}_{timeframe}"

        with self._lock:
            if key not in self._bar_subscriptions or not self._bar_subscriptions[key]:
                print(get_text(MarketText.BAR_UNSUB_NOT_EXIST,key_name=key))
                return
            self._bar_subscriptions[key] = False
        print(get_text(MarketText.BAR_UNSUB_SUCCESS,key_name=key))
