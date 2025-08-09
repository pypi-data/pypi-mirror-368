from mas.market_data.market_data_manager import MarketDataManager
from mas.history.history_data_manager import HistoryDataManager
from mas.virtual.virtual_trade import VirtualTradeManager
from mas.trade.trade_manager import TradeManager
from mas.module.time_helper import normalize_datetime_params
from mas.clinet.client_post import ClientPost
from mas.receive.receive_manage import ReceiveManager
from mas.enum.env_setting import env_type

class DataProvider:
    """
    提供統一介面，用於處理回測與即時模式下的資料訂閱、下單與歷史資料推播邏輯。

    根據 backtest_toggle 參數，自動切換至回測模式或實盤操作。
    整合了 Market、History、Trade、Receiver、ClientPost 等多個子模組，便於調用與測試。

    A unified gateway for managing subscription, order execution, and data dispatching
    under both backtest and real-time modes. It automatically switches logic
    based on the `backtest_toggle` flag and connects internal subsystems
    like MarketManager, HistoryManager, TradeManager, Receiver, and ClientPost.
    """
    def __init__(
        self,
        market: MarketDataManager,
        history: HistoryDataManager,
        virtual_trade: VirtualTradeManager,
        trade: TradeManager,
        receiver: ReceiveManager,
        clientpost: ClientPost
    ):
        self.market = market
        self.history = history
        self.virtual_trade = virtual_trade
        self.trade = trade
        self.receiver = receiver
        self.clientpost = clientpost

    def subscribe_ticks(self, params: dict):
        """
        訂閱 Tick 資料，根據 backtest_toggle 自動切換回測或實盤。

        若為回測模式，會初始化伺服器、清除紀錄並推播歷史 Tick 資料；
        否則則訂閱實盤 Tick 並進入推播流程。

        Args:
            params (dict): 訂閱參數，需包含 symbol、from、to，並可含 backtest_toggle。

        Returns:
            None

        Subscribe to Tick data based on `backtest_toggle`.
        
        If in backtest mode, it resets server state and streams historical Tick data.
        Otherwise, it starts real-time Tick subscription.

        Args:
            params (dict): Subscription parameters including symbol, from, to, and backtest_toggle.

        Returns:
            None
        """
        params = normalize_datetime_params(params)
        backtest_toggle = params.get("backtest_toggle")
        self.receiver.set_bakctest_toggle(backtest_toggle)

        if backtest_toggle:
            if not env_type.exe.value:
                self.clientpost.check_server()
                self.clientpost.record_reset()
            self.history.get_history_ticks(params)
        else:
            self.market.subscribe_ticks(params)

    def subscribe_bars(self, params: dict):
        """
        訂閱 Bar（K 線）資料，根據 backtest_toggle 自動切換回測或實盤。

        若為回測模式，會初始化伺服器、清除紀錄並推播歷史 Bar 資料；
        否則則啟動實盤 Bar 訂閱。

        Args:
            params (dict): 訂閱參數，需包含 symbol、from、to、timeframe，並可含 backtest_toggle。

        Returns:
            None

        Subscribe to Bar (candlestick) data based on `backtest_toggle`.

        If in backtest mode, it streams historical Bar data and resets state;
        otherwise, starts real-time Bar subscription.

        Args:
            params (dict): Subscription parameters including symbol, from, to, timeframe, and backtest_toggle.

        Returns:
            None
        """
        params = normalize_datetime_params(params)
        backtest_toggle = params.get("backtest_toggle")
        self.receiver.set_bakctest_toggle(backtest_toggle)
        if backtest_toggle:
            if not env_type.exe.value:
                self.clientpost.check_server()
                self.clientpost.record_reset()
            self.history.get_history_bars(params)
        else:
            self.market.subscribe_bars(params)

    def unsubscribe_ticks(self, params: dict) -> None:
        """
        取消 Tick 訂閱，委派給 MarketManager 處理。

        Args:
            params (dict): 包含 symbol 的取消參數。

        Returns:
            None

        Unsubscribe Tick feed by delegating to MarketManager.

        Args:
            params (dict): Parameters including symbol.

        Returns:
            None
        """
        return self.market.unsubscribe_ticks(params)

    def unsubscribe_bars(self, params: dict) -> None:
        """
        取消 Bar（K 線）訂閱，委派給 MarketManager 處理。

        Args:
            params (dict): 包含 symbol 與 timeframe 的取消參數。

        Returns:
            None

        Unsubscribe Bar (candlestick) feed by delegating to MarketManager.

        Args:
            params (dict): Parameters including symbol and timeframe.

        Returns:
            None
        """
        return self.market.unsubscribe_bars(params)

    def send_order(self, params: dict) -> str:
        """
        根據模式執行下單動作：回測模式使用 VirtualTrade，下單模式使用 TradeManager。

        Args:
            params (dict): 下單參數，需包含 backtest_toggle 與下單細節（如 symbol、volume 等）。

        Returns:
            str: 回傳訂單 ID 或訊息。

        Send an order based on current execution mode.
        Uses VirtualTrade for backtest mode, or TradeManager for live trading.

        Args:
            params (dict): Order parameters including backtest_toggle and trade details.

        Returns:
            str: Order ID or response message.
        """
        backtest_toggle = params.get("backtest_toggle")
        self.receiver.set_bakctest_toggle(backtest_toggle)
        if backtest_toggle:
            return self.virtual_trade.send_order(params)
        else:
            return self.trade.send_order(params)
