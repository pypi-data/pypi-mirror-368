from mas.history.history_data_mt5 import HistoryData
# from mas.history.history_data_db import HistoryData


class HistoryDataManager:
    """
    歷史資料管理器，提供 Tick 與 Bar 資料的查詢與推播介面。

    此類別為 HistoryData 的代理，對外統一提供簡化的歷史資料操作入口，
    可取得歷史 Tick / Bar 資料，或將其推播至 receiver 進行模擬或回測。

    History data manager class that provides a unified interface for querying and streaming
    historical tick and bar data. It acts as a proxy to the internal HistoryData module.

    Args:
        receiver: 資料接收器，需實作 on_tick/on_bar。
        virtual_trade: 虛擬交易模組。
        connection: 平台連線管理器。
        clientpost: 與後端溝通的資料推送模組。
    """
    def __init__(self, receiver, virtual_trade, connection, clientpost):
        self.manager = HistoryData(
            receiver, virtual_trade, connection, clientpost)

    def stream_history_ticks(self, params: dict):
        """
        取得歷史 Tick 資料，格式為 pandas DataFrame。

        Args:
            params (dict): 查詢參數，需包含 symbol, from, to，可選 mode。

        Returns:
            pd.DataFrame: Tick 資料表格。

        Retrieve historical tick data as a pandas DataFrame.

        Args:
            params (dict): Query parameters including symbol, from, to, optional mode.

        Returns:
            pd.DataFrame: Tick data.
        """
        return self.manager.stream_history_ticks(params)

    def stream_history_bars(self, params: dict):
        """
        取得歷史 Bar 資料（K 線），格式為 pandas DataFrame。

        Args:
            params (dict): 查詢參數，需包含 symbol, from, to, timeframe。

        Returns:
            pd.DataFrame: Bar 資料表格。

        Retrieve historical bar (candlestick) data as a pandas DataFrame.

        Args:
            params (dict): Query parameters including symbol, from, to, timeframe.

        Returns:
            pd.DataFrame: Bar data.
        """
        return self.manager.stream_history_bars(params)

    def get_history_ticks(self, params: dict):
        """
        推播歷史 Tick 資料至 receiver 與虛擬交易模組，模擬即時資料流，最後一筆會通知後端結束。

        Args:
            params (dict): 查詢參數，需包含 symbol, from, to，可選 mode。

        Returns:
            None

        Stream historical tick data to the receiver and virtual trade module,
        simulating real-time replay. The final tick triggers completion notice.

        Args:
            params (dict): Query parameters including symbol, from, to, optional mode.

        Returns:
            None
        """
        return self.manager.get_history_ticks(params)

    def get_history_bars(self, params: dict):
        """
        推播歷史 Bar 資料至 receiver 與虛擬交易模組，模擬即時資料流，最後一筆會通知後端結束。

        Args:
            params (dict): 查詢參數，需包含 symbol, from, to, timeframe。

        Returns:
            None

        Stream historical bar (candlestick) data to the receiver and virtual trade module,
        simulating real-time replay. The final bar triggers completion notice.

        Args:
            params (dict): Query parameters including symbol, from, to, timeframe.

        Returns:
            None
        """
        return self.manager.get_history_bars(params)
