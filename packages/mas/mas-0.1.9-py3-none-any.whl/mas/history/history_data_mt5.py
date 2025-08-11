import MetaTrader5 as mt5
import pandas as pd
from mas.enum.env_setting import env_type
from mas.receive.receive_manage import ReceiveManager
from mas.virtual.virtual_trade import VirtualTradeManager
from mas.clinet.client_post import ClientPost
from mas.connection.connection import ConnectionManager
from mas.module import math_base as mb
from datetime import timedelta
from mas.lang.i18n_strings import get_text, HistoryText
import pytz


class HistoryData:
    def __init__(self, receiver: ReceiveManager, virtual_trade: VirtualTradeManager, connection: ConnectionManager, clientpost: ClientPost):
        """
        初始化資料流控制模組，注入接收器、虛擬交易模組、連線管理器與後端回報介面。

        Args:
            receiver (ReceiveManager): 接收推播資料的對象，需實作 on_tick / on_bar 方法。
            virtual_trade (VirtualTradeManager): 虛擬交易模組，用於模擬策略交易與績效紀錄。
            connection (ConnectionManager): 負責與 MT5 等平台溝通的連線管理器。
            clientpost (ClientPost): 對接後端伺服器的請求模組，處理資料回傳與報表產出。

        Returns:
            無

        Initialize the data flow coordinator with receiver, virtual trading, connection handler, and backend client.

        Args:
            receiver (ReceiveManager): Receiver that handles on_tick/on_bar callbacks.
            virtual_trade (VirtualTradeManager): Virtual trading module for simulating trades and tracking performance.
            connection (ConnectionManager): Connection handler for MT5 or other trading platforms.
            clientpost (ClientPost): Client module for sending data and generating reports via backend.

        Returns:
            None
        """
        self.receiver = receiver
        self.virtual_trade = virtual_trade
        self.connection = connection
        self.clientpost = clientpost

    def stream_history_ticks(self, params: dict) -> pd.DataFrame:
        """
        從 MT5 擷取指定商品的歷史 Tick 資料，支援 "all"（預設）與 "trade"模式，並自動上傳點差費用設定。

        Args:
            params (dict): 查詢參數，需包含：
                - symbol (str): 商品代碼。
                - from (datetime): 起始時間（需為時區化 datetime）。
                - to (datetime): 結束時間（需為時區化 datetime）。
                - mode (str, optional): Tick 模式，支援 "all"（預設）與 "trade"。

        Returns:
            pd.DataFrame: 擷取到的 Tick 資料，若失敗或查無資料則回傳空表。
                          欄位包含 time, bid, ask, last, volume 等。

        Retrieve historical tick data from MT5 for a given symbol and time range.
        Supports both full tick mode and trade-only mode, and automatically uploads spread fee configuration.

        Args:
            params (dict): Query parameters including:
                - symbol (str): Symbol code.
                - from (datetime): Start time (timezone-aware).
                - to (datetime): End time (timezone-aware).
                - mode (str, optional): Tick retrieval mode: "all" (default) or "trade".

        Returns:
            pd.DataFrame: Retrieved tick data. Returns an empty DataFrame if no data is found or on failure.
                          Columns include time, bid, ask, last, volume, etc.
        """
        symbol = params.get("symbol")
        date_from = params.get("from")
        date_to = params.get("to")
        mode = params.get("mode", "all").lower()

        if not all([symbol, date_from, date_to]):
            print(get_text(HistoryText.MISSING_PARAMS))
            return pd.DataFrame()

        mode_map = {
            "all": mt5.COPY_TICKS_ALL,
            "trade": mt5.COPY_TICKS_TRADE
        }
        if mode not in mode_map:
            print(get_text(HistoryText.UNSUPPORTED_MODE, mode=mode))
        tick_mode = mode_map.get(mode, mt5.COPY_TICKS_ALL)
        timezone = pytz.timezone("Etc/UTC")
        date_from = date_from.astimezone(timezone)
        date_to = date_to.astimezone(timezone)
        ticks = mt5.copy_ticks_range(self.connection.find_symbol(
            symbol), date_from, date_to, tick_mode)
        if ticks is None:
            print(get_text(HistoryText.TICK_FAIL, symbol=symbol))
            return pd.DataFrame()

        df = pd.DataFrame(ticks)
        if not df.empty:
            df["time"] = pd.to_datetime(df["time"], unit="s")

        spread_fee = mb.get_spread_fee_for_tick(df)
        if not env_type.exe.value:
            self.clientpost.set_spread_fee({
                "symbol": symbol,
                "spread_fee": spread_fee
            })
        return df

    def get_mt5_data(self, symbol, mt5_tf, date_from, date_to):
        """
        從 MT5 擷取指定商品與時間週期的歷史資料，採用分段擷取方式避免單次查詢過大。

        Args:
            symbol (str): 商品代碼。
            mt5_tf (int): MT5 時間週期常數，例如 mt5.TIMEFRAME_H1、mt5.TIMEFRAME_D1。
            date_from (datetime): 查詢起始時間。
            date_to (datetime): 查詢結束時間。

        Returns:
            pd.DataFrame: 擷取到的歷史 K 線資料（包含 open, high, low, close, volume 等），
                          若無資料則回傳空 DataFrame。

        Retrieve historical bar data from MT5 for the given symbol and timeframe,
        using chunked range queries to avoid large-range failures.

        Args:
            symbol (str): Symbol code.
            mt5_tf (int): MT5 timeframe constant, e.g., mt5.TIMEFRAME_H1 or mt5.TIMEFRAME_D1.
            date_from (datetime): Start time of the query.
            date_to (datetime): End time of the query.

        Returns:
            pd.DataFrame: A DataFrame containing the historical bar data (open, high, low, close, volume, etc.),
                          or an empty DataFrame if no data is retrieved.
        """
        chunk_days = 30
        all_data = []

        current_start = date_from
        while current_start < date_to:
            current_end = min(
                current_start + timedelta(days=chunk_days), date_to)
            try:
                rates = mt5.copy_rates_range(
                    symbol, mt5_tf, current_start, current_end)
                if rates is not None and len(rates) > 0:
                    all_data.append(pd.DataFrame(rates))
                else:
                    print(get_text(HistoryText.NO_DATA, symbol=symbol,
                          start=current_start, end=current_end))
            except Exception as e:
                print(get_text(HistoryText.COPY_FAIL, msg=str(e)))
            current_start = current_end

        if all_data:
            df_all = pd.concat(all_data, ignore_index=True)
            df_all["time"] = pd.to_datetime(df_all["time"], unit="s")
            return df_all
        else:
            return pd.DataFrame()

    def stream_history_bars(self, params: dict) -> pd.DataFrame:
        """
        從 MT5 擷取指定商品的歷史 K 線資料（Bar 資料），支援多種時間週期，並自動上傳點差費用設定。

        Args:
            params (dict): 查詢參數，需包含：
                - symbol (str): 商品代碼。
                - timeframe (str): 時間週期（如 "M1", "H1", "D1" 等）。
                - from (datetime): 查詢起始時間。
                - to (datetime): 查詢結束時間。

        Returns:
            pd.DataFrame: 擷取到的 Bar 資料（包含 open, high, low, close, volume 等），
                          若參數不齊或查無資料則回傳空表。

        Retrieve historical bar (candlestick) data for a given symbol and timeframe from MT5.
        Supports multiple timeframe levels and uploads the calculated spread fee to the backend.

        Args:
            params (dict): Query parameters. Must include:
                - symbol (str): Symbol code.
                - timeframe (str): Timeframe string such as "M1", "H1", or "D1".
                - from (datetime): Start time of the query.
                - to (datetime): End time of the query.

        Returns:
            pd.DataFrame: Retrieved bar data as a DataFrame (open, high, low, close, volume, etc.).
                          Returns an empty DataFrame if inputs are invalid or no data is found.
        """
        symbol = params.get("symbol")
        timeframe = params.get("timeframe")
        date_from = params.get("from")
        date_to = params.get("to")

        if not all([symbol, timeframe, date_from, date_to]):
            return pd.DataFrame()

        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }

        mt5_tf = timeframe_map.get(timeframe.upper())
        if mt5_tf is None:
            return pd.DataFrame()

        rates = self.get_mt5_data(self.connection.find_symbol(
            symbol), mt5_tf, date_from, date_to)

        spread_fee = mb.get_spread_fee(rates)
        if not env_type.exe.value:
            self.clientpost.set_spread_fee({
                "symbol": symbol,
                "spread_fee": spread_fee
            })
        return rates

    def get_history_ticks(self, params: dict) -> None:
        """
        推播歷史 Tick 資料至接收器與虛擬交易模組，模擬即時 Tick 資料流，最後一筆資料會通知後端結束。

        Args:
            params (dict): 查詢參數，需包含：
                - symbol (str): 商品代碼。
                - from (datetime): 起始時間。
                - to (datetime): 結束時間。
                - mode (str, optional): Tick 模式（可選 "all" 或 "trade"）。

        Returns:
            None

        Stream historical tick data to the receiver and virtual trade module, simulating real-time data replay.
        The final tick will trigger a completion notice to the backend.

        Args:
            params (dict): Query parameters. Must include:
                - symbol (str): Symbol code.
                - from (datetime): Start time.
                - to (datetime): End time.
                - mode (str, optional): Tick mode: "all" (default) or "trade".

        Returns:
            None
        """
        data_source = self.stream_history_ticks(params)
        symbol = params.get("symbol")
        if data_source.empty:
            return

        for idx, row in data_source.iterrows():
            if self.virtual_trade:
                self.virtual_trade.set_current_bar(symbol, row)

            data = {
                "symbol": symbol,
                "time": row["time"],
                "bid": row.get("bid"),
                "ask": row.get("ask"),
                "last": row.get("last"),
                "volume": row.get("volume")
            }
            is_end = idx == data_source.index[-1]
            if is_end:
                if not env_type.exe.value:
                    self.clientpost.data_is_end()

            self.receiver.on_tick(symbol, data, is_end)

    def get_history_bars(self, params: dict) -> None:
        """
        推播歷史 Bar 資料（K 線）至接收器與虛擬交易模組，模擬即時資料流，最後一筆資料會通知後端資料結束。

        Args:
            params (dict): 查詢參數，需包含：
                - symbol (str): 商品代碼。
                - from (datetime): 起始時間。
                - to (datetime): 結束時間。
                - timeframe (str): 時間週期（如 "M1", "H1", "D1" 等）。

        Returns:
            None

        Stream historical bar (candlestick) data to the receiver and virtual trade module, simulating real-time replay.
        The final bar will trigger a completion notice to the backend.

        Args:
            params (dict): Query parameters. Must include:
                - symbol (str): Symbol code.
                - from (datetime): Start time.
                - to (datetime): End time.
                - timeframe (str): Timeframe string such as "M1", "H1", "D1", etc.

        Returns:
            None
        """
        data_source = self.stream_history_bars(params)
        symbol = params.get("symbol")
        if not env_type.exe.value:
            self.clientpost.set_data(symbol, data_source)
        if data_source.empty:
            return

        for idx, row in data_source.iterrows():
            if self.virtual_trade:
                self.virtual_trade.set_current_bar(symbol, row)

            data = {
                "symbol": symbol,
                "time": row["time"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["tick_volume"] if "tick_volume" in row else row.get("volume")
            }
            is_end = idx == data_source.index[-1]
            if is_end:
                if not env_type.exe.value:
                    self.clientpost.data_is_end()
            self.receiver.on_bar(symbol, data, is_end)
